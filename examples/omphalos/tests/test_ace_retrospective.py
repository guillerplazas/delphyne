"""Reporting regressions: closed inputs, denominators, and outcome anchors."""

from pathlib import Path
import math

import pytest

from tools.reports.ace_retrospective import (
    allowed,
    cumulative,
    field,
    header,
    qualification,
)


@pytest.mark.parametrize(
    "path",
    [
        "benchmarks/testX.txt",
        "experiments/output/x_test_agentic/experiment.yaml",
        "experiments/campaigns/coverage_20260911/RESULTS.md",
        "experiments/campaigns/ace_review_20260908/final_report.json",
        "experiments/campaigns/coverage_20260911/test_report.json",
    ],
)
def test_closed_or_mixed_inputs_rejected_before_open(path: str) -> None:
    with pytest.raises(PermissionError):
        allowed(path)


def test_cumulative_spending_keeps_unsolved_and_platform_failed_cost() -> None:
    rows = [
        {"theorem": "a", "cost": 0.01, "solved": True, "failed": False},
        {"theorem": "b", "cost": 0.03, "solved": False, "failed": False},
        {"theorem": "c", "cost": 0.02, "solved": False, "failed": True},
    ]
    points = cumulative(rows, ["a", "b", "c"], 0.1)
    assert math.isclose(points[-1]["spend"], 0.06)
    assert [p["solves"] for p in points] == [0, 1, 1, 1]


def test_cumulative_missing_cell_refuses_a_curve() -> None:
    with pytest.raises(ValueError, match="complete unique panel"):
        cumulative([], ["missing"], 0.1)


def test_threshold_does_not_credit_success_above_cost_limit() -> None:
    rows = [
        {"cost": 0.02, "solved": True, "failed": False},
        {"cost": 0.12, "solved": True, "failed": False},
        {"cost": 0.01, "solved": False, "failed": True},
    ]
    assert qualification(rows, [0, 0.1, 0.2]) == [
        {"threshold": 0, "solves": 0},
        {"threshold": 0.1, "solves": 1},
        {"threshold": 0.2, "solves": 2},
    ]


def test_result_reader_ignores_embedded_old_outcome(tmp_path: Path) -> None:
    result = tmp_path / "result.yaml"
    result.write_text(
        "command:\n  args:\n    success: true\n    description: "
        + "x" * 150_000
        + "\noutcome:\n  result:\n    success: false\n"
        + "    spent_budget:\n      input_tokens: 25\n"
    )
    outcome = header(result)
    assert field(outcome, "success") == "false"
    assert field(outcome, "input_tokens") == "25"
