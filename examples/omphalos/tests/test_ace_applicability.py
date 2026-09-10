"""Applicability, abstention, execution budgets and campaign locks; no API."""

from dataclasses import asdict, replace
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.execution_contexts import load_execution_context
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.policies import prompting_policy
from delphyne.stdlib.queries import create_prompt
from delphyne.stdlib.streams import SpendingDeclined, spend_on
from delphyne.utils.typing import pydantic_load
import tiktoken

import ace.ace_applicability as aa
import ace.ace_grounded as ag
import prove_applicability as pa
import prove_grounded as pg
import runtime.pytanque_utils as pt
from tools.reports.ace_applicability_report import read, stage_a_gate
from runtime.paths import OMPHALOS_ROOT as ROOT


def fixtures() -> tuple[tuple[aa.RepairExample, ...], list[dict[str, Any]]]:
    data = read("artifact.json")
    return pydantic_load(tuple[aa.RepairExample, ...], data["bank"]), data[
        "states"
    ]


def test_preserve_semantics_and_abstain() -> None:
    bank, _ = fixtures()
    e = bank[0]
    assert aa.supported_decision(e.state, e.answer)
    assert aa.supported_decision(
        e.state,
        replace(
            e.answer,
            correction=e.answer.correction.replace("change (", "change( "),
        ),
    )
    assert aa.syntax_tokens("n r a.") != aa.syntax_tokens("nra.")
    assert aa.syntax_tokens('"a b"') != aa.syntax_tokens('"ab"')
    for correction in (
        "admit.",
        "assert (H : False).",
        "clear Hmod.",
        "change (True) in Hmod.",
    ):
        assert not aa.supported_decision(
            e.state, replace(e.answer, correction=correction)
        )
    assert not aa.eligible(replace(e.state, outcome="unknown"))
    assert not aa.eligible(replace(e.state, error="Not convertible."))
    assert (
        aa.select_ids(replace(e.state, failed_action="rewrite H."), bank, "A")
        == ()
    )
    assert len(aa.select_ids(e.state, bank, "F")) == 5
    assert len(aa.select_ids(e.state, bank, "A")) == 2
    assert aa.select_ids(e.state, bank, "Q") == ()
    for outcome in ("unknown", "resource_exhausted", "rejected"):
        checked = ag.Checked(
            pt.Feedback(False, proof_so_far=list(e.state.prefix)),
            outcome,
            1,
            1,
            "",
        )
        assert not aa.executed(e.state, e.answer, checked)


def test_structured_contract_and_prompt_bank() -> None:
    bank, _ = fixtures()
    env = load_execution_context(ROOT).policy_env()
    q = pa.DecideSyntaxRepair(
        bank[0].state, {}, "F", tuple(e.id for e in bank)
    )
    answer = dp.Answer(None, dp.Structured(asdict(bank[0].answer)))
    parsed = q.parse_answer(answer)
    assert not isinstance(parsed, dp.ParseError)
    assert isinstance(
        q.parse_answer(dp.Answer(None, "not structured")), dp.ParseError
    )
    examples = pa.syntax_examples()(env, q)
    assert len(examples) == 5
    chat = create_prompt(q, examples, {}, None, env.templates)
    empty = create_prompt(q, [], {}, None, env.templates)
    # Include serialization overhead in this conservative token guard.
    enc = tiktoken.get_encoding("o200k_base")
    assert len(enc.encode(str(chat))) - len(enc.encode(str(empty))) <= 2048
    converted, _ = translate_chat_for_responses(
        LLMRequest(chat=chat, options={}), None, True
    )
    assert converted
    # A structured answer followed by feedback also needs its assistant turn.
    q = replace(
        q,
        prefix=(
            dp.OracleMessage("oracle", answer),
            dp.FeedbackMessage(
                "feedback", "syntax_abstained", "Continue normally."
            ),
        ),
    )
    chat = create_prompt(
        q, (), {}, None, env.templates, tag_user_feedback_messages=True
    )
    converted, _ = translate_chat_for_responses(
        LLMRequest(chat=chat, options={}), None, True
    )
    assert converted


@prompting_policy
def metered(
    query: dp.AttachedQuery[Any], env: dp.PolicyEnv, answer: dp.Answer
) -> dp.StreamGen[Any]:
    admitted = yield from spend_on(
        lambda: (True, dp.Budget({"price": 0.01})),
        dp.Budget({"price": 0.01}),
    )
    if not isinstance(admitted, SpendingDeclined):
        yield from fixed_oracle(lambda _: [answer])(query, env)


def test_no_extra_requests_or_parse_retries() -> None:
    bank, _ = fixtures()
    env = load_execution_context(ROOT).policy_env()
    query_count: list[pa.DecideSyntaxRepair] = []
    answer = dp.Answer(
        None,
        "",
        tool_calls=(dp.ToolCall("ReadSkill", {"skill_name": "mock"}),),
    )
    pp = metered(answer)
    with patch.object(pa.sk, "read_skill", return_value="mock skill"):
        values, spent = (
            pa.repair_episode(bank[0].state, "A", bank)
            .run_toplevel(env, pg.grounded_search() & pp)
            .collect(
                budget=dp.BudgetLimit(
                    {"num_requests": 5, "price": 0.1, "rocq_seconds": 300}
                )
            )
        )
    assert len(values) == 1 and values[0].tracked.value.requests == 4
    assert (
        values[0].tracked.value.status == "request_limit"
        and spent["num_requests"] == 4
    )
    assert spent["price"] == 0.04

    def malformed(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        assert isinstance(q, pa.DecideSyntaxRepair)
        query_count.append(q)
        return [dp.Answer(None, "broken structured output")]

    values, _ = (
        pa.repair_episode(bank[0].state, "A", bank)
        .run_toplevel(env, pg.grounded_search() & fixed_oracle(malformed))
        .collect()
    )
    assert not values and len(query_count) == 1


def test_full_strategy_preserves_default_and_counts_abstention_turn() -> None:
    bank, _ = fixtures()
    e = bank[0]
    received: list[dp.AbstractQuery[Any]] = []
    failure = pt.Feedback(
        False,
        len(e.state.prefix),
        e.state.failed_action,
        e.state.error,
        list(e.state.goals),
        list(e.state.prefix),
    )
    checked = ag.Checked(failure, "rejected", 1, 1, "")
    checked = replace(
        checked, view=ag.feedback_view(failure, "rejected", 8192)
    )

    def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        received.append(q)
        if isinstance(q, pa.DecideSyntaxRepair):
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
        return [dp.Answer(None, "```rocq\nbad.\n```")]

    env = load_execution_context(ROOT).policy_env()
    for mode, expected in (("", False), ("A", True)):
        received.clear()
        with patch.object(pt, "check", return_value=failure):
            values, _ = (
                pg.prove_theorem_grounded(
                    e.state.problem_file,
                    e.state.theorem_name,
                    turn_budget=3,
                    admission=False,
                    restart=False,
                    syntax_mode=mode,
                    syntax_bank=bank,
                )
                .run_toplevel(env, pg.grounded_search() & fixed_oracle(oracle))
                .collect()
            )
        assert not values and len(received) == 3
        assert (
            any(isinstance(q, pa.DecideSyntaxRepair) for q in received)
            == expected
        )
        if expected:
            assert isinstance(received[-1], pg.ProposeProofScriptGrounded)
            q = received[-1]
            chat = create_prompt(
                q, (), {}, None, env.templates, tag_user_feedback_messages=True
            )
            converted, _ = translate_chat_for_responses(
                LLMRequest(chat=chat, options={}), None, True
            )
            assert converted


def test_screen_does_not_expand_on_incidental_wins() -> None:
    _, states = fixtures()
    families = read("registration.json")["families"]
    rows = [
        {
            "arm": arm,
            "bench": s["state"]["theorem_name"],
            "state_id": s["id"],
            "positive": s["positive"],
            "executed": s["positive"],
            "explicit_abstention": not s["positive"],
            "useful": False,
            "cost": 0.01,
            "missing": False,
            "censored": False,
            "platform_failed": False,
        }
        for arm in ("R", "Q", "F", "A")
        for s in states
    ]
    assert not stage_a_gate(rows, families)["go"]
    # Cost saving alone cannot substitute for two useful families.
    for row in rows:
        if row["arm"] == "A":
            row["cost"] = 0.001
    assert not stage_a_gate(rows, families)["go"]
    for row in rows:
        if row["arm"] in ("F", "A") and row["state_id"] in (
            "amc12a_2002_p13-35",
            "amc12a_2003_p1-9",
        ):
            row["useful"] = True
    assert stage_a_gate(rows, families)["go"]
    rows[0]["censored"] = True
    assert not stage_a_gate(rows, families)["go"]


def test_stage_locks_and_exact_cells() -> None:
    import experiments.ace.ace_applicability_experiment as ex

    assert len(ex.configs("a")) == 48
    assert len(ex.configs("b")) == 24
    assert len(ex.configs("validation")) == 160
    assert all(c.max_dollar_budget == 0.10 for c in ex.configs("b"))
    assert len({ex.name(c, None) for c in ex.configs("a")}) == 48

    def denied(f: str) -> dict[str, Any]:
        return (
            {"execution_hashes": {}} if f == "sealed.json" else {"go": False}
        )

    def missing_approval(f: str) -> dict[str, Any]:
        if f == "sealed.json":
            return {"execution_hashes": {}}
        return {"go": True} if f.startswith("report_") else {}

    with patch.object(ex, "read", side_effect=denied):
        try:
            ex.authorize("b")
        except ValueError:
            pass
        else:
            raise AssertionError("failed screen allowed paid expansion")
    with patch.object(ex, "read", side_effect=missing_approval):
        try:
            ex.authorize("validation")
        except (ValueError, FileNotFoundError):
            pass
        else:
            raise AssertionError("validation ran without separate approval")


if __name__ == "__main__":
    for key, fn in list(globals().items()):
        if key.startswith("test_"):
            fn()
            print("ok", key)
