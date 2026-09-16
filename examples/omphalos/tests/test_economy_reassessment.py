"""Guard the user's clarified objective and the offline source boundary."""

import math
from pathlib import Path
from typing import Any

import pytest

from tools.reports import ace_economy_reassessment as report


def comparison() -> dict[str, Any]:
    return dict(
        complete=True,
        cells=80,
        families=40,
        solved_a=50,
        solved_b=50,
        cost_a=2.0,
        cost_b=1.78,
        cost_ratio_ci90=[0.79, 1.01],
        cost_p_two_sided=0.136,
        p_two_sided=1.0,
        observed_ten_percent_target=False,
        practical_interest=False,
        per_seed=[
            dict(solved_a=24, solved_b=25),
            dict(solved_a=26, solved_b=25),
        ],
    )


def test_replication_variation_does_not_veto_observed_savings() -> None:
    pair = comparison()
    value = report.assess(pair)
    assert value["observed_ten_percent_saving"]
    assert not value["nominal_cost_saving_supported"]
    assert not value["ten_percent_saving_supported_by_ci90"]
    assert not value["legacy_only"]["observed_ten_percent_target"]
    assert not pair["practical_interest"]  # The original is not relabeled.


def test_coverage_loss_is_reported_separately_from_the_cost_target() -> None:
    pair = comparison()
    pair["solved_b"] = 45
    value = report.assess(pair)
    assert value["observed_ten_percent_saving"]
    assert value["proof_count_change"] == -5
    assert math.isclose(value["cost_per_solve_candidate"], 1.78 / 45)


def test_cost_per_solve_remains_undefined_without_a_proof() -> None:
    pair = comparison()
    pair["solved_b"] = 0
    value = report.assess(pair)
    assert value["cost_per_solve_candidate"] is None
    assert value["cost_per_solve_change_percent"] is None


@pytest.mark.parametrize("key,value", [("complete", False), ("cells", 79)])
def test_missing_cells_cannot_produce_a_reassessment(
    key: str, value: object
) -> None:
    pair = comparison()
    pair[key] = value
    with pytest.raises(ValueError, match="complete"):
        report.assess(pair)


@pytest.mark.parametrize("cost", [float("nan"), float("inf"), -1.0])
def test_invalid_costs_are_rejected(cost: float) -> None:
    pair = comparison()
    pair["cost_b"] = cost
    with pytest.raises(ValueError):
        report.assess(pair)


@pytest.mark.parametrize("source", ["test", "testX", "train", "../main"])
def test_unknown_source_is_rejected_before_reading(
    source: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_: object) -> bytes:
        raise AssertionError("An unknown source must never be opened")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError, match="registered validationX"):
        report.load_source(source)
