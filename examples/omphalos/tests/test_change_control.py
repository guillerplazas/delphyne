"""Change-control budgets, continuation parity, and accounting; no API."""

from dataclasses import asdict
from typing import Any, Literal
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.execution_contexts import load_execution_context
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.queries import create_prompt
from delphyne.utils.typing import pydantic_load

import ace.ace_applicability as aa
import ace.ace_grounded as ag
import prove_applicability as pa
import prove_change_control as pc
import prove_grounded as pg
import runtime.pytanque_utils as pt
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits
from tools.reports.ace_applicability_report import read
from tools.reports.change_control_report import holm, primary_gate


def fixture() -> tuple[aa.RepairState, tuple[aa.RepairExample, ...]]:
    raw = read("artifact.json")
    return (
        pydantic_load(aa.RepairState, raw["states"][2]["state"]),
        pydantic_load(tuple[aa.RepairExample, ...], raw["bank"]),
    )


def test_reuse_checked_result_and_matched_continuation() -> None:
    state, bank = fixture()
    correction = aa.syntax_form(state.failed_action)[1]
    decision = aa.RepairDecision("repair", "change", correction, "supported")
    queries: list[dp.AbstractQuery[Any]] = []
    computations: list[list[str]] = []
    env = load_execution_context(ROOT).policy_env()
    ordinary_prompts: list[Any] = []

    def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        queries.append(q)
        if isinstance(q, pa.DecideSyntaxRepair):
            return [dp.Answer(None, dp.Structured(asdict(decision)))]
        assert isinstance(q, pg.ProposeProofScriptGrounded)
        chat = create_prompt(
            q, (), {}, None, env.templates, tag_user_feedback_messages=True
        )
        translate_chat_for_responses(
            LLMRequest(chat=chat, options={}), None, True
        )
        ordinary_prompts.append(q.verified_prefix)
        script = "\n".join((*state.prefix, correction, "rewrite IH.", "lia."))
        return [dp.Answer(None, f"```rocq\n{script}\n```")]

    def check(
        file: str,
        theorem: str,
        tactics: list[str],
        limits: ToolLimits,
        assisted: bool = True,
    ) -> ag.Checked:
        assert not assisted
        computations.append(tactics)
        return ag.Checked(
            pt.Feedback(
                False,
                len(tactics),
                "Qed.",
                "incomplete proof",
                list(state.goals),
                tactics,
            ),
            "incomplete",
            0.2,
            1,
            "checked",
        )

    cases: tuple[tuple[Literal["F", "C"], int], ...] = (("F", 2), ("C", 1))
    for arm, count in cases:
        queries.clear()
        computations.clear()
        with (
            patch.object(aa, "checked_proof", new=check),
            patch.object(ag, "checked_proof", new=check),
        ):
            values, spent = (
                pc.change_episode(state, arm, bank, "")
                .run_toplevel(
                    env,
                    pg.grounded_search(typed_limits=True)
                    & fixed_oracle(oracle),
                )
                .collect(
                    budget=dp.BudgetLimit(
                        {"rocq_seconds": 300, "num_requests": 4}
                    )
                )
            )
        assert len(values) == 1
        assert len(queries) == count
        assert len(computations) == 2  # candidate once, continuation once
        assert abs(spent["rocq_seconds"] - 0.4) < 1e-9  # checkpoint is free
        assert values[0].tracked.value.repair.executed
    assert ordinary_prompts[0] == ordinary_prompts[1]


def test_terra_stops_at_decision_and_tools_are_bounded() -> None:
    state, bank = fixture()
    env = load_execution_context(ROOT).policy_env()
    queries: list[dp.AbstractQuery[Any]] = []

    def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        queries.append(q)
        assert isinstance(q, pa.DecideSyntaxRepair)
        return [
            dp.Answer(
                None,
                dp.Structured(
                    asdict(
                        aa.RepairDecision(
                            "abstain", "change", "", "unsupported"
                        )
                    )
                ),
            )
        ]

    values, _ = (
        pc.change_episode(state, "F", bank, "", diagnostic_only=True)
        .run_toplevel(
            env, pg.grounded_search(typed_limits=True) & fixed_oracle(oracle)
        )
        .collect()
    )
    assert len(queries) == 1 and values[0].tracked.value.continuation is None
    queries.clear()

    def tools(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        queries.append(q)
        return [
            dp.Answer(
                None,
                "",
                tool_calls=(dp.ToolCall("ReadSkill", {"skill_name": "mock"}),),
            )
        ]

    with patch.object(pa.sk, "read_skill", return_value="mock"):
        values, _ = (
            pc.change_episode(state, "F", bank, "")
            .run_toplevel(
                env,
                pg.grounded_search(typed_limits=True) & fixed_oracle(tools),
            )
            .collect()
        )
    assert len(queries) == 4
    assert values[0].tracked.value.continuation is None


def test_no_query_after_compute_declined() -> None:
    state, bank = fixture()
    env = load_execution_context(ROOT).policy_env()
    with patch.object(aa, "checked_proof") as check:
        values, _ = (
            pc.change_episode(state, "C", bank, "")
            .run_toplevel(
                env,
                pg.grounded_search(typed_limits=True)
                & fixed_oracle(lambda _: []),
            )
            .collect(budget=dp.BudgetLimit({"rocq_seconds": 59}))
        )
    assert not values and not check.called


def test_progress_and_safety_guards() -> None:
    from ace.change_progress import audit_progress

    state, _ = fixture()
    for suffix in (["shelve."], ["Focus 2."], ["- exact I."]):
        checked = ag.Checked(
            pt.Feedback(False, proof_so_far=[*state.prefix, *suffix]),
            "incomplete",
            0,
            0,
            "",
        )
        assert not audit_progress(state, checked).useful
    from dataclasses import replace

    unsupported = replace(state, failed_action="change True. exact I.")
    with patch.object(aa, "checked_proof") as kernel:
        assert pc.check_change(unsupported, ToolLimits()).outcome == "rejected"
    assert not kernel.called


def test_practical_gate_and_holm() -> None:
    from tools.reports.change_control_report import PANEL

    rows: list[dict[str, Any]] = []
    for arm in ("F", "C"):
        for key in PANEL:
            rows.append(
                {
                    "state_id": key,
                    "bench": key.rsplit("-", 1)[0],
                    "arm": arm,
                    "cost": 0.01 if arm == "F" else 0.008,
                    "decision_correct": True,
                    "useful": key in (PANEL[1], PANEL[5]),
                }
            )
    assert primary_gate(rows, True)
    assert not primary_gate(rows, False)
    rows[-1]["useful"] = False
    assert not primary_gate(rows, True)
    assert holm([0.01, 0.04, 0.2]) == [0.03, 0.08, 0.2]


def test_registered_configs_and_locks() -> None:
    from experiments.ace.change_control_experiment import (
        configs,
        authorize,
        name,
    )

    for stage in ("primary", "terra"):
        cs = configs(stage)
        assert len(cs) == len({name(c, None) for c in cs}) == 12
        assert {c.seed for c in cs} == {0}
        for c in cs:
            args = c.instantiate(None)
            assert args.budget and args.budget["num_requests"] == 4
            assert args.policy_args["reasoning_effort"] == c.reasoning_effort
            assert args.budget["price"] == (1.0 if stage == "terra" else 0.1)
        if stage == "terra":
            assert {c.reasoning_effort for c in cs} == {"low", "medium"}
    for stage in ("full", "validation"):
        try:
            authorize(stage)
        except ValueError:
            pass
        else:
            raise AssertionError("unapproved expansion")


if __name__ == "__main__":
    for key, fn in list(globals().items()):
        if key.startswith("test_"):
            fn()
            print("ok", key)
