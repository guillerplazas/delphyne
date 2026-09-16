"""Quality, scope, context pairing and exact paid-reference parity, offline."""

from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from delphyne.utils.typing import pydantic_load
import pytest
import yaml

from ace.ace_grounded import Checked
from experiments import ace_economy_experiment as c
from prove_economy import SessionWindow, interaction_groups
from prove_grounded import ProposeProofScriptGrounded
from runtime import pytanque_utils as pt
from runtime.campaign_budget import CampaignResponsesModel
from tools.reports.ace_economy_results import candidate_interest, paired


def query() -> ProposeProofScriptGrounded:
    file = next(iter(c.partition("validation").values()))
    return ProposeProofScriptGrounded(pt.parse_problem(file, True), {})


def test_window_keeps_tool_pairs_checked_evidence_and_new_history() -> None:
    feedback = Checked(
        pt.Feedback(
            False, proof_so_far=["intros n."], remaining_goals=["n = n"]
        ),
        "incomplete",
        0,
        0,
        "goal n = n",
    )
    groups: list[list[dp.AnswerPrefixElement]] = []
    for i in range(8):
        if i == 2:
            groups.append(
                [
                    dp.OracleMessage(
                        "oracle", dp.Answer(None, "```rocq\nintros n.\n```")
                    ),
                    dp.FeedbackMessage(
                        "feedback", "incomplete", meta=feedback
                    ),
                ]
            )
        else:
            call = dp.ToolCall(
                "SearchRocq", {"command": "Check Nat.add_comm."}
            )
            groups.append(
                [
                    dp.OracleMessage("oracle", dp.Answer(None, "", (call,))),
                    dp.ToolResult("tool", call, "result " + str(i)),
                ]
            )
    original = replace(
        query(),
        prefix=tuple(m for g in groups for m in g),
        verified_prefix="intros n.",
    )
    window = SessionWindow(threshold_chars=1)
    result, reset = window.apply(original)
    assert reset and window.retained == (2, 6, 7)
    assert interaction_groups(result.prefix) == [groups[i] for i in (2, 6, 7)]
    assert result.verified_prefix == original.verified_prefix
    assert result.spec == original.spec
    new = [
        dp.OracleMessage(
            "oracle", dp.Answer(None, "```rocq\nreflexivity.\n```")
        ),
        dp.FeedbackMessage("feedback", "new"),
    ]
    next_query = replace(original, prefix=(*original.prefix, *new))
    again, reset = window.apply(next_query)
    assert not reset
    assert interaction_groups(again.prefix) == [
        groups[i] for i in (2, 6, 7)
    ] + [new]


def test_session_off_or_below_threshold_is_identical() -> None:
    original = query()
    result, reset = SessionWindow().apply(original)
    assert result is original and not reset


@pytest.mark.parametrize(
    "stage",
    ["training", "trainX", "challenge", "validationX", "testX", "../test"],
)
def test_unregistered_partition_rejected(stage: str) -> None:
    with pytest.raises(ValueError):
        c.partition(stage)


def test_quality_loss_cannot_win_on_savings() -> None:
    result: dict[str, Any] = dict(
        complete=True,
        solved_a=50,
        solved_b=52,
        observed_ten_percent_target=True,
        cost_per_solve_a=0.03,
        cost_per_solve_b=0.02,
    )
    seeds = [
        dict(complete=True, solved_a=25, solved_b=24),
        dict(complete=True, solved_a=25, solved_b=28),
    ]
    assert not candidate_interest(result, seeds)
    seeds[0]["solved_b"] = 25
    assert candidate_interest(result, seeds)


def test_missing_problem_cannot_produce_verdict() -> None:
    result = paired([], "validation", "ace", "agentic")
    assert not result["complete"] and len(result["missing_b"]) == 80


def test_reference_policy_exactly_replays_paid_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = (
        c.ROOT / "experiments/output/ace_revision_20260913/validation/configs"
    )
    paths = sorted(root.glob("validation__candidate__*__seed0"))[:3]
    assert len(paths) == 3
    monkeypatch.setenv(
        "OMPHALOS_CAMPAIGN_LEDGER", str(c.PRIOR / "ledger.sqlite3")
    )
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_STAGE", "validation")
    monkeypatch.setenv("OMPHALOS_ESTIMATE_DOLLARS", "1")
    monkeypatch.delenv("OMPHALOS_ADMISSION_EVENTS", raising=False)
    for folder in paths:
        raw = yaml.safe_load((folder / "result.yaml").read_text())
        args = pydantic_load(dp.RunStrategyArgs, raw["args"])
        args.policy = "economy_proof_policy"
        args.cache_mode, args.cache_file = "replay", str(folder / "cache.yaml")
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("No HTTP in parity check"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(c.context(), cache_root=Path("/")),
                add_header=False,
            )
        expected = raw["outcome"]["result"]
        assert out.result is not None
        assert out.result.success == expected["success"]
        assert out.result.spent_budget == expected["spent_budget"]
        assert (
            json.loads(json.dumps(list(out.result.values)))
            == expected["values"]
        )
