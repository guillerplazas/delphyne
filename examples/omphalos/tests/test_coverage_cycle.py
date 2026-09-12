"""Development-only regression suite: no eager partition imports."""

from dataclasses import replace
from typing import Any
from unittest.mock import patch
import json

import delphyne as dp
from delphyne.stdlib.execution_contexts import load_execution_context
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.policies import prompting_policy
from delphyne.stdlib.queries import create_prompt
from delphyne.stdlib.streams import SpendingDeclined, spend_on
import pytest

import ace.ace_grounded as ag
import prove_coverage as pc
import prove_grounded as pg
import runtime.pytanque_utils as pt
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits
from experiments.coverage_cycle_experiment import context, BANK, partition
import prove_coverage_cycle as cc

DEMOS = "demos/coverage.demo.yaml"


def original() -> ag.Checked:
    return ag.Checked(
        pt.Feedback(
            False,
            failing_tactic="fail.",
            error_message="failed",
            proof_so_far=["intros."],
            remaining_goals=["H : True |- True"],
        ),
        "rejected",
        0.1,
        1,
        "failed at True",
    )


def env() -> dp.PolicyEnv:
    return context().policy_env()


def test_usable_requires_checked_complete_scope() -> None:
    o = original()
    assert not pc.usable(o, replace(o, outcome="unknown"))
    assert not pc.usable(o, replace(o, outcome="resource_exhausted"))
    assert not pc.usable(o, replace(o, outcome="incomplete"))
    changed = replace(
        o,
        outcome="incomplete",
        feedback=replace(
            o.feedback,
            failing_tactic="Qed.",
            proof_so_far=["intros.", "idtac."],
        ),
    )
    assert pc.usable(o, changed)
    assert not changed.feedback.success
    assert not pc.usable(changed, changed)


@pytest.mark.parametrize(
    "cap,price,expected",
    [
        (0, 0.01, 0),
        (0.011, 0.01, 1),
        (0.021, 0.01, 2),
        (0.025, 0.01, 2),
        (0.025, 0.001, 6),
    ],
)
def test_nested_budget_and_nofail(
    cap: float, price: float, expected: int
) -> None:
    calls: list[str] = []

    @prompting_policy
    def paid[T](
        query: dp.AttachedQuery[T], env: dp.PolicyEnv
    ) -> dp.StreamGen[T]:
        def invoke() -> tuple[bool, dp.Budget]:
            assert isinstance(query.query, pc.ExploreProof)
            calls.append(query.query.mode)
            return True, dp.Budget({"price": price, "num_requests": 1})

        decision = yield from spend_on(
            invoke, dp.Budget({"price": price, "num_requests": 1})
        )
        if not isinstance(decision, SpendingDeclined):
            parsed = query.parse_answer(
                dp.Answer(
                    None, dp.Structured({"mode": "suffix", "script": "fail."})
                )
            )
            assert not isinstance(parsed, dp.ParseError)
            yield dp.Solution(parsed)

    @dp.strategy
    def wrapper() -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Any]:
        return (
            yield from dp.branch(
                pc.exploration_space(
                    "miniF2F/valid/mathd_algebra/mathd_algebra_190.v",
                    "mathd_algebra_190",
                    original(),
                    "",
                    ToolLimits(seconds=1),
                )
            )
        )

    # A real training file makes query parsing independent of path guesses.
    TRAINX_PROBLEMS = {n: (p, n) for n, p in partition("training").items()}

    file = next(iter(TRAINX_PROBLEMS.values()))[0]

    def rejected(*args: Any, **kwargs: Any) -> ag.Checked:
        return original()

    with (
        patch.object(pt, "parse_problem", return_value=pt.parse_problem(file)),
        patch.object(ag, "checked_proof", new=rejected),
    ):
        values, spent = (
            wrapper()
            .run_toplevel(env(), pg.grounded_search() & paid())
            .collect(
                budget=dp.BudgetLimit(
                    {"price": cap, "num_requests": 64, "rocq_seconds": 300}
                )
            )
        )
    assert len(values) == 1 and values[0].tracked.value is None
    assert len(calls) == expected
    assert spent["num_requests"] == expected
    assert abs(spent["price"] - expected * price) < 1e-10
    if expected == 6:
        assert calls == ["suffix"] * 3 + ["replace"] * 3


def test_exploration_response_rendering() -> None:
    TRAINX_PROBLEMS = {n: (p, n) for n, p in partition("training").items()}

    spec = pt.parse_problem(next(iter(TRAINX_PROBLEMS.values()))[0], True)
    for mode in ("suffix", "replace"):
        q = pc.ExploreProof(
            spec,
            {},
            mode=mode,
            verified_prefix="intros.",
            decision="failed state",
        )
        chat = create_prompt(
            q, (), {}, None, env().templates, tag_user_feedback_messages=True
        )
        translate_chat_for_responses(
            LLMRequest(chat=chat, options={}), None, True
        )
        parsed = q.parse_answer(
            dp.Answer(None, dp.Structured({"mode": mode, "script": "lia."}))
        )
        assert not isinstance(parsed, dp.ParseError)


def test_disabled_strategy_query_parity() -> None:
    TRAINX_PROBLEMS = {n: (p, n) for n, p in partition("training").items()}

    theorem, (file, _) = next(iter(TRAINX_PROBLEMS.items()))
    seen: list[dict[str, Any]] = []
    from dataclasses import asdict

    def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        assert isinstance(q, pg.ProposeProofScriptGrounded)
        seen.append(asdict(q))
        return [dp.Answer(None, "```rocq\nintros.\n```")]

    success = ag.Checked(
        pt.Feedback(True, proof_so_far=["intros."]),
        "accepted",
        0.01,
        1,
        "done",
    )

    def accepted(*args: Any, **kwargs: Any) -> ag.Checked:
        return success

    with patch.object(ag, "checked_proof", new=accepted):
        variants: list[dict[str, Any]] = [{}, {"bounded_exploration": False}]
        for kwargs in variants:
            pg.prove_theorem_grounded(
                file, theorem, admission=False, restart=False, **kwargs
            ).run_toplevel(
                env(), pg.grounded_search() & fixed_oracle(oracle)
            ).collect()
    assert seen[0] == seen[1]


def test_live_demo_navigation_and_family_exclusion() -> None:
    if not (ROOT / DEMOS).exists():
        pytest.skip("demonstrations not built yet")
    from delphyne.scripts.demonstrations import check_demo_file

    for demo in (
        DEMOS,
        "demos/exploration.demo.yaml",
        "demos/coverage_cycle.demo.yaml",
    ):
        result = check_demo_file(ROOT / demo, context("D2"), ROOT)
        assert not result.errors, result.errors
    bank = json.loads((ROOT / BANK).read_text())
    policy = cc.relevant_examples(BANK)
    e = context("D2").policy_env()
    for row in bank["examples"]:
        for example in e.examples.examples_for(row["query"]):
            q = example.query
            assert isinstance(q, pg.ProposeProofScriptGrounded)
            chosen = policy(e, q)
            assert all(
                pc.family(x.query.spec.theorem_name, bank["families"])
                != pc.family(q.spec.theorem_name, bank["families"])
                for x in chosen
                if isinstance(x.query, pg.ProposeProofScriptGrounded)
            )
    base = load_execution_context(ROOT).policy_env()
    assert not base.examples.examples_for("ChooseProofBridge")
    assert not base.examples.examples_for("ChooseProofStructure")


def test_stall_exploration_reenters_main_with_valid_feedback() -> None:
    TRAINX_PROBLEMS = {n: (p, n) for n, p in partition("training").items()}

    theorem, (file, _) = next(iter(TRAINX_PROBLEMS.items()))
    modes: list[str] = []
    calls: list[list[str]] = []
    o = original()
    changed = replace(
        o,
        outcome="incomplete",
        feedback=replace(
            o.feedback,
            failing_tactic="Qed.",
            proof_so_far=["intros.", "idtac."],
        ),
    )

    def check(
        file: str,
        theorem: str,
        tactics: list[str],
        limits: ToolLimits,
        assisted: bool = True,
    ) -> ag.Checked:
        calls.append(tactics)
        if not assisted:
            return changed
        if len(calls) > 5:
            return ag.Checked(
                pt.Feedback(True, proof_so_far=["intros.", "exact I."]),
                "accepted",
                0.1,
                1,
                "done",
            )
        return o

    def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        chat = create_prompt(
            q, (), {}, None, env().templates, tag_user_feedback_messages=True
        )
        translate_chat_for_responses(
            LLMRequest(chat=chat, options={}), None, True
        )
        if isinstance(q, pc.ExploreProof):
            modes.append(q.mode)
            return [
                dp.Answer(
                    None, dp.Structured(dict(mode=q.mode, script="idtac."))
                )
            ]
        return [dp.Answer(None, "```rocq\nintros.\n```")]

    with patch.object(ag, "checked_proof", new=check):
        values, _ = (
            pg.prove_theorem_grounded(
                file,
                theorem,
                admission=False,
                restart=False,
                bounded_exploration=True,
            )
            .run_toplevel(env(), pg.grounded_search() & fixed_oracle(oracle))
            .collect(budget=dp.BudgetLimit({"rocq_seconds": 300}))
        )
    assert values and modes == ["suffix"]
    assert len(calls) == 7


def test_protected_paths_and_manifest() -> None:
    from runtime.development_only import forbidden
    from experiments.coverage_cycle_experiment import configs

    assert forbidden("benchmarks/testX.txt")
    assert forbidden("experiments/output/coverage_20260911/test/D/cache.yaml")
    assert not forbidden("benchmarks/trainX.txt")
    with pytest.raises(PermissionError):
        # Hook rejects before the OS opens anything; no protected data read.
        (ROOT / "benchmarks/testX.txt").open()
    with pytest.raises(ValueError):
        partition("test")
    assert (
        sum(
            len(configs(s, a))
            for s in ("training", "validation")
            for a in ("D2", "E2", "S", "H")
        )
        == 320
    )


@pytest.mark.parametrize(
    "operation,action,goals,expected",
    [
        ("numeral_coercion", "change (INR 49 = 49).", "|- INR 49 = 49", True),
        ("numeral_coercion", "nra.", "n : nat\n|- INR n >= 0", False),
        ("recurrence_coercion", "nra.", "n : nat\n|- INR n >= 0", False),
        ("sqrt_side_condition", "apply sqrt_pos.", "|- 0 <= sqrt x", True),
        ("sqrt_side_condition", "apply H.", "|- f (sqrt x) = 2", False),
        ("trig_identity", "rewrite H.", "|- cos x ^ 2 + sin x ^ 2 = 1", True),
        ("sum_unfold", "simpl sum_f.", "|- sum_f f n = n", True),
    ],
)
def test_operation_relevance(
    operation: str, action: str, goals: str, expected: bool
) -> None:
    assert cc.operation_matches(operation, action, "", goals, "") is expected


def test_final_submission_has_no_tools_and_strict_json() -> None:
    spec = pt.parse_problem(next(iter(partition("training").values())), True)
    q = cc.SubmitExploration(spec, {}, mode="suffix")
    assert q.query_settings(None).tools is None
    assert not q.advertised_tools()
    assert q.query_settings(None).structured_output is not None
    assert isinstance(
        q.parse_answer(dp.Answer(None, "not json")), dp.ParseError
    )
    assert not isinstance(
        q.parse_answer(
            dp.Answer(
                None, dp.Structured({"mode": "suffix", "script": "lia."})
            )
        ),
        dp.ParseError,
    )
    chat = create_prompt(q, (), {}, None, env().templates, True)
    translate_chat_for_responses(LLMRequest(chat=chat, options={}), None, True)


def test_v2_final_turn_and_fallback() -> None:
    specfile = next(iter(partition("training").values()))
    seen: list[tuple[str, bool]] = []

    def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        assert isinstance(q, pc.ExploreProof)
        seen.append((q.mode, q.query_settings(None).tools is None))
        return [
            dp.Answer(None, dp.Structured({"mode": q.mode, "script": "fail."}))
        ]

    def reject(*args: Any, **kwargs: Any) -> ag.Checked:
        return original()

    with patch.object(ag, "checked_proof", new=reject):
        values, _ = (
            cc.explore_stall_v2(
                specfile,
                PathName(specfile),
                original(),
                "",
                ToolLimits(seconds=1),
            )
            .run_toplevel(env(), pc.exploration_policy(fixed_oracle(oracle)))
            .collect(
                budget=dp.BudgetLimit(
                    {"price": 0.025, "num_requests": 6, "rocq_seconds": 120}
                )
            )
        )
    assert values and values[0].tracked.value is None
    assert seen == [
        (m, final)
        for m in ("suffix", "replace")
        for final in (False, False, True)
    ]


def PathName(file: str) -> str:
    from pathlib import Path

    return Path(file).stem


def test_compaction_preserves_state_and_recent_rounds() -> None:
    spec = pt.parse_problem(next(iter(partition("training").values())), True)
    prefix: list[dp.AnswerPrefixElement] = []
    for _ in range(5):
        prefix.extend(
            [
                dp.OracleMessage(
                    "oracle",
                    dp.Answer(None, "```rocq\n" + "idtac.\n" * 3000 + "```"),
                ),
                dp.FeedbackMessage("feedback", "rejected", meta=original()),
            ]
        )
    q = pg.ProposeProofScriptGrounded(
        spec, {}, prefix=tuple(prefix), verified_prefix="intros."
    )
    shorter = cc.compact_query(q)
    assert (
        shorter.spec == q.spec and shorter.verified_prefix == q.verified_prefix
    )
    assert shorter.prefix == q.prefix[-4:]
    assert cc.prompt_chars(shorter) < cc.prompt_chars(q)
    assert q.prefix == tuple(prefix)
    chat = create_prompt(shorter, (), {}, None, env().templates, True)
    translate_chat_for_responses(LLMRequest(chat=chat, options={}), None, True)
    assert cc.compact_query(replace(q, prefix=()), 1000000).prefix == ()


def test_checked_syntax_rejects_unsupported_and_deduplicates() -> None:
    import ace.ace_applicability as aa

    state = aa.RepairState(
        "unused", "unused", (), "norm_num.", "Syntax error", "rejected", (), ""
    )
    assert not aa.eligible(state)
    assert aa.syntax_form("set x := 3.")[1] == "set (x := 3)."
    assert aa.syntax_form("nra [H].")[1] == "nra."
