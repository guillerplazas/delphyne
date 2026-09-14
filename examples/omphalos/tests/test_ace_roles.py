"""New ACE contracts, real Rocq handoff and complete wire translation."""

# ruff: noqa: E402
from runtime.ace_roles_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict, replace
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.scripts.demonstrations import check_demo_file
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest, Schema
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.queries import create_prompt
from delphyne.utils.typing import pydantic_load
import pytest
import yaml

from ace.role_contracts import (
    ReflectedLesson,
    TrainingEvent,
    WriterChoices,
    compile_choices,
    lesson_draft,
    resolve,
)
from ace.rocq_snippets import check_snippet
from experiments import ace_roles_experiment as c
from prove_ace_roles import (
    WriteACEChoices,
    ReflectACEEvidence,
    RoleResponsesModel,
    role_examples,
    write_ace_choices,
    validate_inputs,
)
from prove_grounded import grounded_search
from prove_writer_drafts import reduction_input
from runtime.model_registry import pricing_for
from tests.test_continuation_output import response


def fixture() -> tuple[WriteACEChoices, WriterChoices]:
    raw = yaml.safe_load((c.ROOT / "demos/ace_roles.demo.yaml").read_text())[0]
    return pydantic_load(WriteACEChoices, raw["args"]), pydantic_load(
        WriterChoices, raw["answers"][0]["answer"]
    )


@pytest.mark.parametrize(
    "alias", ["r0", "r01", "r-1", "r100", "d1", "r", "r1x"]
)
def test_unknown_aliases_rejected(alias: str) -> None:
    with pytest.raises(ValueError):
        resolve(alias, "r", [1, 2])


def test_compilation_derives_receipt_bookkeeping_and_binds_source() -> None:
    q, answer = fixture()
    advice, delta = compile_choices(
        q.role, answer, q.drafts, q.receipts, q.contexts
    )
    assert advice.retained_receipts == (q.receipts[0].identifier,)
    assert q.receipts[0].snippet in delta.operations[0].content
    for invalid in (
        replace(answer, decisions=()),
        replace(answer, decisions=answer.decisions * 2),
    ):
        with pytest.raises(ValueError):
            compile_choices(q.role, invalid, q.drafts, q.receipts, q.contexts)
    changed = replace(
        q.receipts[0],
        context=replace(q.receipts[0].context, source="wrong-source"),
    )
    with pytest.raises(ValueError, match="actual source"):
        compile_choices(q.role, answer, q.drafts, (changed,), q.contexts)
    with pytest.raises(ValueError, match="exact source"):
        validate_inputs(q.contexts, q.drafts, (changed,))


def test_failed_receipt_cannot_be_retained_and_abstention_needs_reason() -> (
    None
):
    q, answer = fixture()
    rejected = check_snippet(
        q.contexts[0],
        "have bad : True := I.",
        dict(seconds=60, rpc_calls=512, view_bytes=8192),
    )
    assert not rejected.executable
    with pytest.raises(ValueError, match="successful"):
        compile_choices(q.role, answer, q.drafts, (rejected,), q.contexts)
    drop = replace(
        answer.decisions[0],
        action="drop",
        reason="Already covered by the book",
        section="",
        explanation="",
        receipts=(),
    )
    advice, delta = compile_choices(
        q.role,
        replace(answer, decisions=(drop,)),
        q.drafts,
        (rejected,),
        q.contexts,
    )
    assert not delta.operations and not advice.retained_receipts
    with pytest.raises(ValueError, match="reason"):
        compile_choices(
            q.role,
            replace(answer, decisions=(replace(drop, reason=""),)),
            q.drafts,
            (rejected,),
            q.contexts,
        )


def test_real_repair_and_reducer_reuse_without_second_probe() -> None:
    q, answer = fixture()
    queries: list[WriteACEChoices] = []

    def oracle(query: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(query, WriteACEChoices)
        queries.append(query)
        if not query.receipts:
            yield dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "CheckAdviceSnippet",
                        dict(context="c1", snippet=q.receipts[0].snippet),
                    ),
                ),
            )
        else:
            yield dp.Answer(None, dp.Structured(asdict(answer)))

    policy = grounded_search() & fixed_oracle(oracle)
    with patch.object(
        c.CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("HTTP forbidden"),
    ):
        vals, spent = (
            write_ace_choices("curator", "", "", (q.contexts[0],), q.drafts)
            .run_toplevel(c.context().policy_env(), policy)
            .collect()
        )
        assert len(vals) == 1 and spent["rocq_seconds"] > 0
        product = vals[0].tracked.value
        args = reduction_input([product], (q.contexts[0],), "")
        vals, spent = (
            write_ace_choices(**args)
            .run_toplevel(c.context().policy_env(), policy)
            .collect()
        )
        assert len(vals) == 1 and spent["rocq_seconds"] == 0
        assert len(queries) == 3
        assert vals[0].tracked.value.checked.delta == product.checked.delta


def test_role_recording_preserves_corrected_final_message_parser() -> None:
    model = RoleResponsesModel(
        options={"model": "gpt-5.6-luna"},
        pricing=pricing_for("gpt-5.6-luna"),
        ledger_file="unused",
        stage="offline",
        use_reasoning_cache=True,
        convert_user_feedback_to_tool=True,
    )
    req = LLMRequest(
        chat=(), options={}, structured_output=Schema("choices", None, {})
    )
    out, log = model._parse_response(  # pyright: ignore[reportPrivateUsage]
        response('{"old":true}', '{"new":true}'), req
    )  # pyright: ignore[reportPrivateUsage]
    assert out and out.content == dp.Structured(dict(new=True))
    assert any(r.message == "continuation_final_message_v2" for r in log)
    bad, _ = model._parse_response(response("{}", "broken"), req)  # pyright: ignore[reportPrivateUsage]
    assert bad is None


def test_reflection_requires_bound_event_and_real_prerequisites() -> None:
    src = c.read("terminal_fixture.json")
    events = tuple(pydantic_load(TrainingEvent, e) for e in src["events"])
    lesson = ReflectedLesson(
        "",
        "e1",
        "accepted nia witness",
        "completion",
        "exact accepted prefix",
        "nia.",
        "",
    )
    assert (
        lesson_draft(lesson, events)[0].context_id
        == events[0].context.identifier
    )
    with pytest.raises(ValueError):
        lesson_draft(replace(lesson, event="e99"), events)
    with pytest.raises(ValueError):
        lesson_draft(replace(lesson, preconditions=""), events)
    assert not lesson_draft(
        replace(
            lesson, proposed_code="", abstain_reason="Existing book covers it"
        ),
        events,
    )


def test_demonstrations_and_all_initial_pilot_requests_translate() -> None:
    ctx = c.context()
    feedback = check_demo_file(
        c.ROOT / "demos/ace_roles.demo.yaml", ctx, c.ROOT
    )
    assert not feedback.errors, feedback.errors
    env = ctx.policy_env()
    selected = 0
    for batch in c.read("candidate_packets.json")["batches"]:
        for row in batch:
            from ace.rocq_snippets import SnippetContext
            from prove_writer_drafts import UnverifiedSnippetDraft

            context = pydantic_load(SnippetContext, row["context"])
            draft = UnverifiedSnippetDraft(
                row["draft_id"],
                context.identifier,
                row["proposed_code"],
                row["purpose"],
                row["source"],
            )
            for role in ("curator", "reducer"):
                q = WriteACEChoices(role, "", "", (context,), (draft,))
                examples = role_examples()(env, q)
                selected += len(examples)
                chat = create_prompt(
                    q, tuple(examples), {}, None, env.templates
                )
                wire, _ = translate_chat_for_responses(
                    LLMRequest(chat=chat, options={}), None, True
                )
                calls = [
                    r.get("call_id")
                    for r in wire
                    if r.get("type") == "function_call"
                ]
                outputs = [
                    r.get("call_id")
                    for r in wire
                    if r.get("type") == "function_call_output"
                ]
                assert calls == outputs
                if context.theorem_name == "mathd_algebra_28":
                    assert not examples
    assert selected == 14
    for n in c.REFLECT_SOURCES:
        args = c.reflection_args(n, True, n == "amc12_2000_p6")
        problem = args.pop("problem_file")
        from runtime.pytanque_utils import parse_problem

        q = pydantic_load(
            ReflectACEEvidence,
            dict(spec=asdict(parse_problem(problem)), **args),
        )
        examples = role_examples()(env, q)
        if n == "amc12_2000_p6":
            assert not examples
        chat = create_prompt(q, tuple(examples), {}, None, env.templates)
        translate_chat_for_responses(
            LLMRequest(chat=chat, options={}), None, True
        )


def test_campaign_counts_and_boundary_rejections() -> None:
    assert abs(sum(c.ALLOCATIONS.values()) - 40) < 1e-8
    assert len(c.SOURCES) == len(c.REFLECT_SOURCES) == 8
    assert len(c.partition("training")) == len(c.partition("validation")) == 40
    for path in (
        c.ROOT / "memory/MEMORY.md",
        c.ROOT / "benchmarks/testX.txt",
        c.ROOT / "experiments/campaigns/ace_review_20260908/README.md",
    ):
        with pytest.raises(PermissionError):
            path.read_text()
    with pytest.raises(PermissionError):
        (c.OLD / "forbidden_write.json").write_text("{}")


def test_failed_curator_handoff_preserves_original_drafts(
    tmp_path: Path,
) -> None:
    q, _ = fixture()
    cfg = c.Config(
        "writer_pilot", "candidate", "curator", "fixture", "unused", "unused"
    )
    args = dict(
        role="curator",
        evidence="",
        playbook="",
        contexts=[asdict(q.contexts[0])],
        drafts=[asdict(d) for d in q.drafts],
        receipts=[],
    )
    with (
        patch.object(c, "writer_product", return_value=None),
        patch.object(c, "read", return_value=args),
    ):
        result = c.handoff([cfg], [args], "")
    assert result["drafts"] == json.loads(json.dumps(args["drafts"]))
    assert "failed_curator" in result["evidence"]


def test_actual_role_policy_and_exact_transport_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from delphyne.stdlib.commands.run_strategy import run_strategy
    from delphyne.stdlib.models import LLMOutput, LLMResponse
    from delphyne.stdlib.tasks import run_command

    q, answer = fixture()
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_LEDGER", str(tmp_path / "unused"))
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_STAGE", "writer_pilot")
    monkeypatch.setenv("OPENAI_API_KEY", "offline")
    monkeypatch.delenv("OMPHALOS_ADMISSION_EVENTS", raising=False)
    args = dp.RunStrategyArgs(
        strategy="write_ace_choices",
        args=dict(
            role="curator",
            evidence="",
            playbook="",
            contexts=[asdict(q.contexts[0])],
            drafts=[asdict(d) for d in q.drafts],
        ),
        policy="ace_roles_policy",
        policy_args=dict(
            snapshot_directory=str(tmp_path / "transport"),
            mode="writer",
            dollar_cap=0.2,
        ),
        budget=dict(price=0.2, num_requests=4, rocq_seconds=180),
        cache_file=str(tmp_path / "cache.yaml"),
        cache_mode="create",
        export_raw_trace=False,
        export_browsable_trace=False,
        export_log=False,
    )
    calls: list[LLMRequest] = []

    def dispatch(model: RoleResponsesModel, req: LLMRequest) -> LLMResponse:
        calls.append(req)
        model.reasoning_allowance += 100
        out = (
            LLMOutput(
                "",
                tool_calls=[
                    dp.ToolCall(
                        "CheckAdviceSnippet",
                        dict(context="c1", snippet=q.receipts[0].snippet),
                    )
                ],
            )
            if len(calls) == 1
            else LLMOutput(dp.Structured(asdict(answer)))
        )
        return LLMResponse(
            [out],
            dp.Budget(
                dict(
                    price=0.001,
                    num_requests=1,
                    num_completions=1,
                    output_tokens=100,
                )
            ),
            [],
            "gpt-5.6-luna",
            {},
        )

    ctx = replace(c.context(), cache_root=Path("/"))
    with patch.object(
        RoleResponsesModel,
        "_send_final_request",
        autospec=True,
        side_effect=dispatch,
    ):
        live = run_command(run_strategy, args, ctx=ctx, add_header=False)
    assert live.result and live.result.success, live.diagnostics
    assert len(calls) == 2 and all(r.structured_output for r in calls)
    args.cache_mode = "replay"
    with patch.object(
        c.CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("HTTP forbidden"),
    ):
        replay = run_command(run_strategy, args, ctx=ctx, add_header=False)
    assert replay.result and replay.result.success, replay.diagnostics
    assert replay.result.spent_budget == live.result.spent_budget
    assert replay.result.values == live.result.values
