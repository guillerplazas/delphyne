"""Capacity protocol, exact replay, and training-only verifier regressions."""

# ruff: noqa: E402 -- guard installation precedes experiment imports

from runtime.development_only import install

install()

from dataclasses import replace
import json
from pathlib import Path
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib import openai_api as oa
from delphyne.stdlib.models import (
    AssistantMessage,
    CachedRequest,
    LLMCache,
    LLMOutput,
    LLMRequest,
    LLMResponse,
    SystemMessage,
    UserMessage,
)
from delphyne.utils.caching import Cache
import pytest

from ace import ace_goal_visibility as visibility
from ace import ace_grounded as ag
from ace.ace_verified_snippets import SnippetWitness, preserve_verified_snippet
from experiments.ace import ace_capacity_experiment as c
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import pricing_for
from runtime.replay_admission import (
    PrefixGuard,
    RecordedCache,
    admission_observer,
    transport_state,
)
from runtime.tool_budget import ToolLimits
from runtime import pytanque_utils as pt


def model() -> CampaignResponsesModel:
    return CampaignResponsesModel(
        options={"model": c.old.LUNA, "reasoning_effort": "medium"},
        pricing=pricing_for(c.old.LUNA),
        use_reasoning_cache=True,
        convert_user_feedback_to_tool=True,
        ledger_file="unused",
        stage="unused",
        estimate_dollars=True,
    )


def fake_response(
    m: CampaignResponsesModel, request: LLMRequest, content: str = "answer"
) -> LLMResponse:
    assert m.reasoning_cache is not None
    m.reasoning_cache.cache.dict[
        oa.ReasoningCacheKey(request, content, ())
    ] = [oa.ReasoningMessage(f"rs_{m.reasoning_allowance}", ["summary"], None)]
    m.reasoning_allowance += 73
    return LLMResponse(
        [LLMOutput(content)],
        dp.Budget(
            {
                "price": 0.001,
                "output_tokens": 73,
                "num_requests": 1,
                "num_completions": 1,
            }
        ),
        [],
        c.old.LUNA,
        dict(input_tokens=100, output_tokens=73),
    )


def test_exact_transport_replay_and_next_estimate(tmp_path: Path) -> None:
    live = model()
    req = LLMRequest(
        chat=(SystemMessage("system"), UserMessage("question")), options={}
    )
    raw = Cache[CachedRequest, LLMResponse]({}, "create")
    cache = LLMCache(RecordedCache(raw.dict, raw.mode, live, tmp_path))
    with patch.object(
        CampaignResponsesModel,
        "_send_final_request",
        autospec=True,
        side_effect=fake_response,
    ) as send:
        response = live.send_request(req, cache)
        next_req = replace(
            req,
            chat=(
                *req.chat,
                AssistantMessage(dp.Answer(None, "answer")),
                UserMessage("next"),
            ),
        )
        expected = live.estimate_budget(next_req)
        expected_state = transport_state(live)
        assert send.call_count == 1
    replay = model()
    replay_cache = LLMCache(
        RecordedCache(raw.dict, "replay", replay, tmp_path)
    )
    with patch.object(
        CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("HTTP forbidden"),
    ):
        assert replay.send_request(req, replay_cache) == response
        assert transport_state(replay) == expected_state
        assert replay.estimate_budget(next_req) == expected
    # A sidecar also recovers a settled response lost before cache flush.
    recovered = model()
    recovery_cache = LLMCache(RecordedCache({}, "create", recovered, tmp_path))
    with patch.object(
        CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("repayment forbidden"),
    ):
        recovered_response = recovered.send_request(req, recovery_cache)
        assert (
            recovered_response.outputs[0].content
            == response.outputs[0].content
        )
        assert recovered_response.budget == response.budget
    assert recovered.reasoning_allowance == 73


def test_snapshot_absence_and_state_drift_fail_closed(tmp_path: Path) -> None:
    m = model()
    req = m.add_model_defaults(
        LLMRequest(chat=(SystemMessage("s"),), options={})
    )
    key = CachedRequest(req, 1)
    old = {key: LLMResponse([LLMOutput("old")])}
    cache = RecordedCache(old, "replay", m, tmp_path)
    with pytest.raises(ValueError, match="snapshot"):
        cache(lambda _: pytest.fail("HTTP"))(key)
    created = RecordedCache({}, "create", m, tmp_path)
    created(lambda r: fake_response(m, r.request))(key)
    with pytest.raises(ValueError, match="state diverged"):
        created(lambda _: pytest.fail("HTTP"))(key)


def test_prefix_guard_rejects_early_divergence() -> None:
    a = CachedRequest(LLMRequest(chat=(SystemMessage("a"),), options={}), 1)
    b = CachedRequest(LLMRequest(chat=(SystemMessage("b"),), options={}), 1)
    guard = PrefixGuard({a})
    with pytest.raises(ValueError, match="diverged"):
        guard.consume(b)
    guard.consume(a)
    guard.consume(b)


def test_terminal_admission_is_exported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from delphyne.stdlib.streams import Stream, spend_on, SpendingDeclined

    path = tmp_path / "events.jsonl"
    monkeypatch.setenv("OMPHALOS_ADMISSION_EVENTS", str(path))

    def run() -> dp.StreamGen[int]:
        first = yield from spend_on(
            lambda: (1, dp.Budget({"price": 0.03})), dp.Budget({"price": 0.04})
        )
        assert first == 1

        def forbidden() -> tuple[int, dp.Budget]:
            raise AssertionError("declined call executed")

        second = yield from spend_on(
            forbidden,
            dp.Budget({"price": 0.08}),
        )
        assert isinstance(second, SpendingDeclined)

    limits = {"price": 0.1}
    env = dp.PolicyEnv(object_loader=dp.ObjectLoader.trivial())
    stream = admission_observer(limits)(Stream(run), env)
    stream.collect(budget=dp.BudgetLimit(limits))
    events = [json.loads(line) for line in path.read_text().splitlines()]
    declined = [
        e for e in events if e["kind"] == "admission_v2" and not e["admitted"]
    ]
    assert len(declined) == 1
    assert declined[0]["limiting"] == ["price"]
    assert abs(declined[0]["remaining"]["price"] - 0.07) < 1e-12
    assert events[-1]["kind"] == "terminal_v2"
    assert events[-1]["pending"] == 0


def test_feedback_only_changes_empty_incomplete_qed() -> None:
    feedback = pt.Feedback(
        False,
        failing_index=1,
        failing_tactic="Qed.",
        error_message="Attempt to save an incomplete proof",
        remaining_goals=[],
        proof_so_far=["intros."],
    )
    original = ag.Checked(
        feedback,
        "incomplete",
        1,
        2,
        ag.feedback_view(feedback, "incomplete", 8192),
    )
    shown = ag.Inspection('{"Show.":"2 unfocused goals"}', 2, 3, "accepted")
    with (
        patch.object(ag, "checked_proof", return_value=original),
        patch.object(visibility, "inspect_obligations", return_value=shown),
    ):
        fixed = visibility.checked_proof_v2("unused", "unused", [])
        assert (
            not fixed.feedback.success and fixed.feedback.remaining_goals == []
        )
        assert fixed.elapsed == 3 and fixed.rpc_calls == 5
        assert "unfocused goals" in fixed.view
        ordinary = replace(
            original, feedback=replace(feedback, remaining_goals=["g"])
        )
        with patch.object(ag, "checked_proof", return_value=ordinary):
            assert (
                visibility.checked_proof_v2("unused", "unused", []) is ordinary
            )
    rejected = visibility.inspect_proof_state_v2(
        "unused", "unused", "", "Show. Abort."
    )
    assert rejected.outcome == "rejected"


def test_registered_counts_and_isolation() -> None:
    assert len(c.read("planned_cross.json")) == 64
    assert len(c.read("planned_creation.json")) == 200
    configs = [c.ProofConfig(**r) for r in c.read("planned_mechanisms.json")]
    assert len(configs) == 80 and {v.seed for v in configs} == {0}
    for m in (c.old.LUNA, c.old.TERRA):
        values = {
            p: next(
                x
                for x in configs
                if x.model == m and x.profile == p and x.theorem == c.PANEL[0]
            ).instantiate(None)
            for p in c.PROFILES
        }
        assert values["A"].args | {"feedback_version": 2} == values["C"].args
        assert values["B"].args | {"feedback_version": 2} == values["D"].args
        assert (
            values["D"].args | {"playbook": values["E"].args["playbook"]}
            == values["E"].args
        )
    assert abs(sum(c.ALLOCATIONS.values()) - c.REMAINING) < 1e-12


def test_live_source_snippet_and_obligation_witnesses() -> None:
    witness = SnippetWitness(**c.read("snippet_witness.json"))
    raw = c.read("snippet_verification.json")["candidate"]
    verdict = preserve_verified_snippet(witness, raw)
    assert verdict.source_check.feedback.success
    assert not verdict.candidate_check.feedback.success
    assert verdict.retained == witness.template
    # Actual recorded TRAIN state, not a validation-derived demonstration.
    diags = c.old.read("complete_diagnostics.json")
    row = diags["training/luna-none/mathd_numbertheory_48"]
    check = next(
        x
        for x in row["checks"]
        if x["category"] == "incomplete-proof" and not x["remaining_goals"]
    )
    prefix = check["verified_prefix"]
    result = visibility.inspect_obligations(
        c.old.partition("training")["mathd_numbertheory_48"],
        "mathd_numbertheory_48",
        "\n".join(prefix),
        ToolLimits(),
    )
    assert result.outcome == "accepted", result.text
    assert "goal" in result.text.lower()
    assert result.rpc_calls <= 512 and len(result.text.encode()) <= 8192


def test_live_continuation_replays_prefix_without_repayment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real policy + Rocq + caches, with HTTP replaced by two fixed responses."""
    from delphyne.stdlib.commands.run_strategy import run_strategy
    from delphyne.stdlib.tasks import run_command
    import shutil

    monkeypatch.setenv("OMPHALOS_CAMPAIGN_LEDGER", "unused")
    monkeypatch.setenv("OPENAI_API_KEY", "offline-test")
    monkeypatch.setenv(
        "OMPHALOS_ADMISSION_EVENTS", str(tmp_path / "events.jsonl")
    )
    cfg = c.ProofConfig(
        "mathd_algebra_28", "training", c.old.LUNA, "none", "C", 2
    )
    args = cfg.instantiate(None)
    args.policy_args["snapshot_directory"] = str(tmp_path / "base_state")
    args.policy_args["turn_budget"] = 1
    args.budget["num_requests"] = 1
    args.cache_file = str(tmp_path / "base_cache.yaml")
    args.cache_mode = "create"
    args.export_raw_trace = args.export_log = args.export_browsable_trace = (
        False
    )
    ctx = replace(c.context(), cache_root=Path("/"))
    proof = c.old.read("quality_probe_have.json")["probes"][
        "assert_equivalent"
    ]["script"]
    calls: list[LLMRequest] = []

    def answer(m: CampaignResponsesModel, request: LLMRequest) -> LLMResponse:
        calls.append(request)
        code = "intros." if len(calls) == 1 else proof
        return fake_response(m, request, f"```rocq\n{code}\n```")

    with patch.object(
        CampaignResponsesModel,
        "_send_final_request",
        autospec=True,
        side_effect=answer,
    ):
        baseline = run_command(run_strategy, args, ctx=ctx, add_header=False)
        assert baseline.result is not None, baseline.diagnostics
        assert not baseline.result.success and len(calls) == 1
        shutil.copytree(tmp_path / "base_state", tmp_path / "extended_state")
        extended = replace(
            args,
            budget=args.budget | {"num_requests": 2},
            policy_args=args.policy_args
            | dict(
                turn_budget=2,
                snapshot_directory=str(tmp_path / "extended_state"),
                prefix_cache=str(tmp_path / "base_cache.yaml"),
            ),
            cache_file=str(tmp_path / "extended_cache.yaml"),
        )
        continuation = run_command(
            run_strategy, extended, ctx=ctx, add_header=False
        )
        assert continuation.result is not None, continuation.diagnostics
        assert continuation.result.success, continuation.diagnostics
        assert len(calls) == 2, "The first response was paid twice"
    replay = replace(
        extended,
        cache_mode="replay",
        policy_args=extended.policy_args | {"prefix_cache": ""},
    )
    with patch.object(
        CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("HTTP forbidden"),
    ):
        repeated = run_command(run_strategy, replay, ctx=ctx, add_header=False)
        assert repeated.result is not None, repeated.diagnostics
        assert repeated.result.success
        assert repeated.result.spent_budget == continuation.result.spent_budget
