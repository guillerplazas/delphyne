"""Proof-edit, repair, progress and campaign regressions; no paid calls."""

from dataclasses import replace
from typing import Any
from unittest.mock import patch

import pytest
import delphyne as dp
from delphyne.stdlib.execution_contexts import load_execution_context
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.queries import create_prompt
from delphyne.utils.typing import pydantic_load

import ace.ace_applicability as aa
import ace.ace_grounded as ag
import prove_grounded as pg
import prove_change_control as pc
import prove_continuation as ct
import runtime.pytanque_utils as pt
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits
from runtime.grounded_control import claim_recovery
from delphyne.stdlib.streams import stream_transformer, Stream
from tools.reports.change_control_report import read
from experiments.ace.ace_mechanisms_experiment import select


def state_at(index: int = 1) -> aa.RepairState:
    return pydantic_load(
        aa.RepairState, read("artifact.json")["states"][index]["state"]
    )


def test_edit_contract() -> None:
    prefix = ["intros x."]
    assert ct.assemble(ct.ProofContinuation("suffix", "exact H."), prefix) == [
        *prefix,
        "exact H.",
    ]
    assert ct.assemble(
        ct.ProofContinuation("replace", "intros.\nlia."), prefix
    ) == ["intros.", "lia."]
    assert prefix == ["intros x."]
    with pytest.raises(ValueError):
        ct.assemble(ct.ProofContinuation("suffix", ""), prefix)
    q = ct.ContinueVerifiedProof(pt.parse_problem(state_at().problem_file), {})
    assert isinstance(
        q.parse_answer(
            dp.Answer(None, dp.Structured(dict(mode="guess", script="lia.")))
        ),
        dp.ParseError,
    )


@pytest.mark.parametrize("accepted", [False, True])
def test_full_repair_once_and_rendering(accepted: bool) -> None:
    state = state_at()
    prefix = list(state.prefix)
    correction = aa.syntax_form(state.failed_action)[1]
    failed = ag.Checked(
        pt.Feedback(
            False,
            failing_tactic=state.failed_action,
            error_message=state.error,
            proof_so_far=prefix,
            remaining_goals=list(state.goals),
        ),
        "rejected",
        0.1,
        1,
        "Syntax error",
    )
    repaired = ag.Checked(
        pt.Feedback(
            False,
            failing_tactic="Qed.",
            error_message="unfinished" if accepted else "not convertible",
            proof_so_far=[*prefix, correction] if accepted else prefix,
            remaining_goals=list(state.goals),
        ),
        "incomplete" if accepted else "rejected",
        0.2,
        1,
        "checked",
    )
    final = ag.Checked(
        pt.Feedback(True, proof_so_far=[*prefix, correction, "lia."]),
        "accepted",
        0.1,
        1,
        "done",
    )
    env = load_execution_context(ROOT).policy_env()
    queries: list[dp.AbstractQuery[Any]] = []

    def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        queries.append(q)
        chat = create_prompt(
            q, (), {}, None, env.templates, tag_user_feedback_messages=True
        )
        translate_chat_for_responses(
            LLMRequest(chat=chat, options={}), None, True
        )
        if isinstance(q, ct.ContinueVerifiedProof):
            assert q.verified_prefix == "\n".join(
                repaired.feedback.proof_so_far
            )
            return [
                dp.Answer(
                    None, dp.Structured(dict(mode="suffix", script="lia."))
                )
            ]
        return [dp.Answer(None, "```rocq\nintros.\n```")]

    checked_calls: list[list[str]] = []
    repair_calls: list[aa.RepairState] = []

    def ordinary(
        file: str,
        theorem: str,
        tactics: list[str],
        limits: ToolLimits,
        assisted: bool = True,
    ) -> ag.Checked:
        checked_calls.append(tactics)
        return failed if len(checked_calls) == 1 else final

    def checked(state: aa.RepairState, limits: dict[str, Any]) -> ag.Checked:
        repair_calls.append(state)
        return repaired

    with (
        patch.object(ag, "checked_proof", new=ordinary),
        patch.object(ct, "checked_syntax", new=checked),
    ):
        values, spent = (
            pg.prove_theorem_grounded(
                state.problem_file,
                state.theorem_name,
                admission=False,
                restart=False,
                continuation=True,
                checked_repair=True,
            )
            .run_toplevel(env, pg.grounded_search() & fixed_oracle(oracle))
            .collect()
        )
    assert len(values) == 1 and len(queries) == 2
    assert len(checked_calls) == 2 and len(repair_calls) == 1
    assert abs(spent["rocq_seconds"] - 0.4) < 1e-8


def test_local_suffix_and_replacement() -> None:
    state = state_at()
    env = load_execution_context(ROOT).policy_env()
    for mode in ("suffix", "replace"):
        checked_calls: list[list[str]] = []

        def check(
            file: str,
            theorem: str,
            tactics: list[str],
            limits: ToolLimits,
            assisted: bool = True,
        ) -> ag.Checked:
            checked_calls.append(tactics)
            return ag.Checked(
                pt.Feedback(
                    False,
                    proof_so_far=tactics,
                    remaining_goals=list(state.goals),
                ),
                "incomplete",
                0.1,
                1,
                "checked",
            )

        def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
            assert isinstance(q, ct.ContinueVerifiedProof)
            return [
                dp.Answer(None, dp.Structured(dict(mode=mode, script="lia.")))
            ]

        with (
            patch.object(aa, "checked_proof", new=check),
            patch.object(ag, "checked_proof", new=check),
        ):
            values, _ = (
                pc.change_episode(state, "C", (), "", continuation=True)
                .run_toplevel(
                    env,
                    pg.grounded_search(typed_limits=True)
                    & fixed_oracle(oracle),
                )
                .collect()
            )
        assert values
        assert checked_calls[-1] == (
            [*checked_calls[0], "lia."] if mode == "suffix" else ["lia."]
        )


def test_progress_rejects_hidden_or_incidental_work() -> None:
    state = state_at()
    for suffix in (
        ["shelve."],
        ["assert (Hdummy : True).", "{ exact I."],
        ["- exact I."],
    ):
        checked = ag.Checked(
            pt.Feedback(False, proof_so_far=[*state.prefix, *suffix]),
            "incomplete",
            0.0,
            0,
            "",
        )
        assert not ct.progress_evidence(
            state, checked, {"seconds": 10.0}
        ).useful
    unavailable = ag.Checked(pt.Feedback(False), "unknown", 0.0, 0, "")
    assert not ct.progress_evidence(
        state, unavailable, {"seconds": 10.0}
    ).useful


def test_single_shared_recovery() -> None:
    @stream_transformer
    def twice[T](stream: Stream[T], env: dp.PolicyEnv) -> dp.StreamGen[T]:
        first = yield from claim_recovery("test")
        second = yield from claim_recovery("test")
        assert first and not second
        yield from stream

    env = load_execution_context(ROOT).policy_env()
    stream: dp.Stream[int] = dp.Stream(lambda: iter(()))
    _, spent = twice()(stream, env).collect(
        budget=dp.BudgetLimit({"recoveries": 1})
    )
    assert spent["recoveries"] == 1


def test_attainable_selection_and_tradeoff() -> None:
    def m(n: int, c: float) -> dict[str, Any]:
        return dict(cells=40, solves=n, cost=c, cost_per_solve=c / n)

    metrics = {a: m(26, 1.0) for a in ("S", "C", "R", "E")}
    metrics["reference"] = m(28, 1.0)
    metrics["C"] = m(29, 1.0)
    assert select(metrics) == ("C", "practical improvement")
    metrics["C"] = m(28, 0.99)
    assert select(metrics)[0] == "C"
    metrics["C"] = m(27, 0.80)
    assert select(metrics) == ("C", "exploratory coverage trade-off")
    metrics["C"] = m(26, 0.80)
    assert select(metrics)[0] is None


def test_live_canonical_repairs() -> None:
    for i, row in enumerate(read("artifact.json")["states"]):
        state = state_at(i)
        checked = ct.checked_syntax(state, {"seconds": 10.0})
        pattern, correction = aa.syntax_form(state.failed_action)
        answer = aa.RepairDecision("repair", pattern, correction, "test")
        assert (
            aa.executed(state, answer, checked) or checked.feedback.success
        ) == row["positive"]
    state = state_at(1)
    _, change = aa.syntax_form(state.failed_action)
    checked = ag.checked_proof(
        state.problem_file,
        state.theorem_name,
        [*state.prefix, change, "rewrite IH.", "lia."],
        ToolLimits(seconds=10),
        assisted=False,
    )
    assert ct.progress_evidence(state, checked, {"seconds": 10.0}).useful
    # Existing finite set/nra candidates, checked on the same real context.
    for action in ("set marker := n.", "nra [IH]."):
        s = replace(
            state,
            failed_action=action,
            error="Syntax error",
            outcome="rejected",
        )
        result = ct.checked_syntax(s, {"seconds": 10.0})
        assert result.outcome != "unknown"
        if action.startswith("set"):
            assert result.feedback.proof_so_far[-1] == "set (marker := n)."


def test_executable_protocol_demonstrations() -> None:
    from delphyne.scripts.demonstrations import check_demo_file

    context = load_execution_context(ROOT)
    result = check_demo_file(
        ROOT / "demos/continuation_protocol.demo.yaml", context, ROOT
    )
    assert not result.errors, result.errors
