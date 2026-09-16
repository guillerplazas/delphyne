"""Economic judgments, full denominators and factorial arithmetic."""

from typing import Any

import pytest

from experiments.economy_refinement import report as r


def test_cost_saving_is_reported_even_when_coverage_decreases() -> None:
    value: dict[str, Any] = dict(
        complete=True,
        cost_ratio=0.85,
        solved_a=50,
        solved_b=49,
        cost_a=2,
        cost_b=1.7,
        cost_p_two_sided=0.3,
        p_two_sided=0.5,
    )
    result = r.assessment(value)
    assert result["ten_percent_saving"]
    assert result["proof_count_change"] == -1
    assert result["coverage_cost_tradeoff"]
    assert not result["cost_difference_supported"]
    value["complete"] = False
    with pytest.raises(ValueError, match="Missing"):
        r.assessment(value)


def test_frontier_does_not_force_non_ace_to_reset() -> None:
    values: dict[str, Any] = dict(
        agentic=dict(cost=1.0, qualified=50),
        agentic_reset=dict(cost=1.2, qualified=50),
        ace=dict(cost=1.1, qualified=52),
        ace_reset=dict(cost=1.0, qualified=51),
    )
    assert r.frontier(values, ace=False) == ["agentic"]
    assert r.frontier(values, ace=True) == ["ace", "ace_reset"]
    assert r.frontier(values) == ["ace", "ace_reset"]


def test_total_cost_and_denominator_include_platform_failures() -> None:
    rows: list[dict[str, Any]] = [
        dict(
            arm="agentic",
            qualified=not failed,
            failed=failed,
            cost=cost,
            input=100,
            cached=50,
            output=20,
            uncached_cost=cost,
            requests=1,
            resets=0,
            seed=seed,
        )
        for seed, failed, cost in ((0, False, 0.02), (1, True, 0.03))
    ]
    total = r.totals(rows)["agentic"]
    assert total["cells"] == 2 and total["qualified"] == 1
    assert total["failed"] == 1
    assert total["cost"] == total["cost_per_solve"] == 0.05
    assert total["per_seed"]["1"]["qualified"] == 0


def test_interaction_detects_overlapping_savings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def families(_: str) -> dict[str, str]:
        return {"one": "one", "two": "two"}

    monkeypatch.setattr(r.reference.original, "families", families)
    rows: list[dict[str, Any]] = []
    costs = {
        (False, False): 2.0,
        (True, False): 1.5,
        (False, True): 1.0,
        (True, True): 0.75,
    }
    for theorem in ("one", "two"):
        for seed in (0, 1):
            for ace in (False, True):
                for (reset, compact), cost in costs.items():
                    rows.append(
                        dict(
                            arm=r.arm(ace, reset, compact),
                            theorem=theorem,
                            seed=seed,
                            cost=cost,
                            qualified=True,
                        )
                    )
    values = r.interactions(rows)
    for label in ("ace", "agentic"):
        assert values[label]["cost"] == 0.25
        assert values[label]["cost_ci90"] == [0.25, 0.25]
        assert values[label]["coverage"] == 0
        assert values[label]["coverage_p_two_sided"] == 1
