"""Budget composition and grounded-example regressions; no API calls."""

from dataclasses import asdict, replace
from pathlib import Path
from typing import Any
from unittest.mock import patch
from tempfile import TemporaryDirectory

import delphyne as dp
import yaml
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.queries import create_prompt
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.policies import prompting_policy
from delphyne.stdlib.streams import SpendingDeclined, spend_on

import ace.ace_grounded as ag
import prove_grounded as pg
import runtime.pytanque_utils as pt
from runtime.grounded_control import DecisionControl, controlled_prompt
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits


def environment() -> dp.PolicyEnv:
    return dp.PolicyEnv(
        object_loader=dp.ObjectLoader.trivial(),
        prompt_dirs=(),
        demonstration_files=(),
        data_dirs=(),
    )


def short(limits: ToolLimits) -> ag.Inspection:
    return ag.Inspection("checked", 2, 1, "incomplete")


@dp.strategy
def short_operation() -> dp.Strategy[dp.Compute, object, ag.Inspection]:
    return (yield from dp.compute(short)(ToolLimits(seconds=7)))


def test_typed_admission() -> None:
    for typed, cap, admitted in (
        (True, 7, True),
        (True, 6, False),
        (False, 7, False),
    ):
        values, spent = (
            short_operation()
            .run_toplevel(
                environment(), pg.grounded_search(typed_limits=typed) & None
            )
            .collect(budget=dp.BudgetLimit({"rocq_seconds": cap}))
        )
        assert bool(values) == admitted
        assert spent["rocq_seconds"] == (2 if admitted else 0)


CALLS: list[str] = []


@prompting_policy
def priced[T](
    query: dp.AttachedQuery[T], env: dp.PolicyEnv, cost: float, label: str
) -> dp.StreamGen[T]:
    def invoke() -> tuple[bool, dp.Budget]:
        CALLS.append(label)
        return True, dp.Budget({"price": cost})

    answer = yield from spend_on(invoke, dp.Budget({"price": cost}))
    if not isinstance(answer, SpendingDeclined):
        yield from fixed_oracle(
            lambda _: [dp.Answer(None, "```rocq\nlia.\n```")]
        )(query, env)


@dp.strategy
def decision(
    control: DecisionControl,
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Any]:
    file = next(
        s
        for s in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if s and not s.startswith("#")
    )
    return (
        yield from dp.branch(
            pg.ProposeProofScriptGrounded(
                pt.parse_problem(file, True), {}, control=control
            ).using(dp.ambient_pp)
        )
    )


def test_preflight_and_downshift() -> None:
    pp = controlled_prompt(priced(0.10, "normal"), priced(0.01, "reduced"))
    for seconds, recoveries, expected in (
        (0, 1, []),
        (7, 0, []),
        (7, 1, ["reduced"]),
    ):
        CALLS.clear()
        values, spent = (
            decision(DecisionControl(7, may_downshift=True))
            .run_toplevel(environment(), dp.dfs() & pp)
            .collect(
                budget=dp.BudgetLimit(
                    {
                        "price": 0.05,
                        "rocq_seconds": seconds,
                        "recoveries": recoveries,
                    }
                )
            )
        )
        assert CALLS == expected and bool(values) == bool(expected)
        assert spent["rocq_seconds"] == 0
        assert spent["recoveries"] == (1 if expected else 0)


def test_recovery_shares_allowance() -> None:
    CALLS.clear()
    # A resource recovery uses the same unit needed for a monetary downshift.
    values, spent = (
        decision(DecisionControl(7, "resource", True))
        .run_toplevel(
            environment(),
            dp.dfs()
            & controlled_prompt(
                priced(0.10, "normal"), priced(0.01, "reduced")
            ),
        )
        .collect(
            budget=dp.BudgetLimit(
                {"price": 0.05, "rocq_seconds": 7, "recoveries": 1}
            )
        )
    )
    assert not values and not CALLS and spent["recoveries"] == 1


def test_downshift_does_not_mutate_parent_model() -> None:
    from runtime.campaign_budget import CampaignResponsesModel
    from runtime.grounded_control import limited_prompt
    from runtime.model_registry import pricing_for

    model = CampaignResponsesModel(
        options={"model": "gpt-5.6-luna"},
        pricing=pricing_for("gpt-5.6-luna"),
        use_reasoning_cache=True,
        convert_user_feedback_to_tool=True,
        ledger_file="unused",
        stage="unused",
    )
    model.reasoning_allowance = 100

    def fake_few_shot(
        reduced: CampaignResponsesModel, **kwargs: Any
    ) -> dp.PromptingPolicy:
        assert reduced is not model
        assert reduced.output_limit == 4096 and model.output_limit == 32768
        assert reduced.reasoning_cache is model.reasoning_cache
        assert reduced.reasoning_allowance == 100
        reduced.reasoning_allowance = 120
        return fixed_oracle(lambda _: [dp.Answer(None, "```rocq\nlia.\n```")])

    with patch("runtime.grounded_control.dp.few_shot", fake_few_shot):
        stream = decision(DecisionControl(7)).run_toplevel(
            environment(),
            dp.dfs() & limited_prompt(model, pg.grounded_examples()),
        )
        # Inspect while suspended at the solution, not only after exhaustion.
        for message in stream:
            if isinstance(message, dp.Solution):
                assert model.output_limit == 32768
                assert model.reasoning_allowance == 120
                break
        else:
            raise AssertionError("no solution")


def test_match_abstention_and_progress() -> None:
    e = ag.TrainingTransition(
        "unused",
        "unused",
        "cell",
        "sha",
        (),
        "ring.",
        "not convertible",
        ("x : R",),
        ("reflexivity.",),
    )
    claim = ag.AdviceClaim(
        "x", "structure", "local", (), e.correction, e, "env"
    )
    fb = pt.Feedback(False, 0, "ring.", "not convertible", ["x : R"])
    assert not ag.select_matched_advice((claim,), fb, "env")
    claim = replace(claim, symbols=("R",))
    assert ag.select_matched_advice((claim,), fb, "env") == (claim,)
    assert not ag.select_matched_advice(
        (claim,), replace(fb, error_message="Syntax error"), "env"
    )
    assert not ag.select_matched_advice((claim,), fb, "other-env")
    checks = [ag.Checked(fb, "rejected", 1, 1, "")]
    assert not ag.recent_progress(checks * 4)
    checks.append(
        ag.Checked(replace(fb, proof_so_far=["intros."]), "rejected", 1, 1, "")
    )
    assert ag.recent_progress(checks)
    assert not ag.recent_progress(
        [replace(c, outcome="unknown") for c in checks]
    )


def test_structured_contract() -> None:
    file = next(
        s
        for s in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if s and not s.startswith("#")
    )
    e = ag.TrainingTransition(
        file,
        Path(file).stem,
        "cell",
        "sha",
        (),
        "bad.",
        "syntax: bad",
        (),
        ("lia.",),
    )
    fb = ag.Checked(
        pt.Feedback(False, 0, "bad.", "syntax: bad"), "rejected", 0, 0, ""
    )
    q = pg.ReflectGroundedTransitionJSON(e, (), fb)
    reflection = pg.GroundedReflection(
        "bad.",
        "Contains colon: and newline\nplus quotes",
        "local",
        ("lia.",),
        (),
    )
    assert (
        q.parse_answer(dp.Answer(None, dp.Structured(asdict(reflection))))
        == reflection
    )
    assert isinstance(
        q.parse_answer(dp.Answer(None, "explanation: bad: yaml")),
        dp.ParseError,
    )


def test_recovery_stops_unchanged_goals() -> None:
    file = next(
        s
        for s in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if s and not s.startswith("#")
    )
    queries: list[pg.ProposeProofScriptGrounded] = []

    def oracle(q: dp.AbstractQuery[Any]) -> list[dp.Answer]:
        assert isinstance(q, pg.ProposeProofScriptGrounded)
        queries.append(q)
        return [dp.Answer(None, "```rocq\nlia.\n```")]

    fb = pt.Feedback(False, 0, "lia.", "Cannot find witness", ["|- n = 0"])
    pp = controlled_prompt(fixed_oracle(oracle), fixed_oracle(oracle))
    with patch.object(pt, "check", return_value=fb):
        values, spent = (
            pg.prove_theorem_grounded(
                file,
                Path(file).stem,
                polished=True,
                resource_recovery=True,
                restart=False,
            )
            .run_toplevel(
                environment(), pg.grounded_search(typed_limits=True) & pp
            )
            .collect(
                budget=dp.BudgetLimit(
                    {"num_requests": 64, "rocq_seconds": 300, "recoveries": 1}
                )
            )
        )
    assert not values and len(queries) < 10 and spent["recoveries"] == 1
    assert len(queries[-1].prefix) == 2
    assert_responses_prefix(queries[-1])


def test_receipts_cannot_disappear() -> None:
    from tools.reports import ace_polish_report as report
    from tools.analysis.cell_records import CellRecord

    row = CellRecord(
        "missing__candidate-r64__gpt-5.6-luna__seed0",
        "missing",
        "0",
        "candidate-r64",
        "gpt-5.6-luna",
        {},
        "done",
        True,
        100,
        0,
        20,
        1,
        0.001,
        False,
    )
    with (
        patch.object(report, "cells_of_run", return_value=iter([row])),
        patch.object(report, "charged_cells", return_value={}),
    ):
        try:
            report.observations("training")
        except ValueError as exc:
            assert "missing receipts" in str(exc)
        else:
            raise AssertionError(
                "missing billing evidence was silently treated as free"
            )


def test_large_command_arguments_do_not_hide_success() -> None:
    from tools.analysis.cell_records import _result_head, _field  # pyright: ignore[reportPrivateUsage]

    with TemporaryDirectory() as directory:
        path = Path(directory) / "result.yaml"
        path.write_text(
            "command: run_strategy\nargs:\n  success: false\n  evidence: "
            + "x" * 150000
            + "\noutcome:\n  result:\n    success: true\n    spent_budget:\n      price: 0.01\n"
        )
        head = _result_head(path)
        assert head.startswith("outcome:")
        assert _field(head, "success") == "true"


def assert_responses_prefix(query: pg.ProposeProofScriptGrounded) -> None:
    """Exercise real rendering/translation, which a fixed oracle bypasses."""
    config = yaml.safe_load((ROOT / "delphyne.yaml").read_text())
    env = dp.PolicyEnv(
        object_loader=dp.ObjectLoader.trivial(),
        prompt_dirs=tuple(ROOT / p for p in config["prompt_dirs"]),
        demonstration_files=(),
        data_dirs=(),
    )
    chat = create_prompt(
        query, (), {}, None, env.templates, tag_user_feedback_messages=True
    )
    translated, _ = translate_chat_for_responses(
        LLMRequest(chat=chat, options={}), None, True
    )
    assert translated


if __name__ == "__main__":
    for key, fn in list(globals().items()):
        if key.startswith("test_"):
            fn()
            print("ok", key)
