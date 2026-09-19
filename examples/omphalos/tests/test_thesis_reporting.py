"""Guard the thesis endpoints against incomplete or selective accounting."""

from math import isclose
from pathlib import Path
from typing import Any

import pytest

from tools.reports import ace_thesis as report
from tools.reports import ace_thesis_retrospective as retrospective


@pytest.fixture
def panel(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    names = {f"problem_{i}": f"unused_{i}.v" for i in range(10)}

    def partition(_: str) -> dict[str, str]:
        return names

    def families(_: str) -> dict[str, str]:
        return {name: name for name in names}

    monkeypatch.setattr(report, "partition", partition)
    monkeypatch.setattr(report, "families", families)
    return [
        dict(
            stage="validation",
            arm=arm,
            theorem=theorem,
            replicate=seed,
            solved=index < 5,
            failed=False,
            cost=0.05,
            uncached_cost=0.12,
        )
        for arm in ("baseline", "ace")
        for index, theorem in enumerate(names)
        for seed in (0, 1)
    ]


def test_coverage_goal_is_percentage_points_not_relative_percent(
    panel: list[dict[str, Any]],
) -> None:
    panel[30]["solved"] = True
    result = report.comparison(panel, "baseline", "ace")
    assert (result["solved_a"], result["solved_b"]) == (10, 11)
    assert isclose(result["coverage_change_points"], 5)
    assert not result["coverage_target_observed"]
    panel[31]["solved"] = True
    assert report.comparison(panel, "baseline", "ace")[
        "coverage_target_observed"
    ]


def test_saving_requires_pooled_coverage_and_counts_failed_spend(
    panel: list[dict[str, Any]],
) -> None:
    for row in panel[20:]:
        row["cost"] = 0.04
    panel[-1]["failed"] = True
    result = report.comparison(panel, "baseline", "ace")
    assert isclose(result["cost_b"], 0.8)
    assert result["failed_b"] == 1
    assert result["cost_target_observed"]
    # A seed regression is allowed when a paired seed gains a proof.
    panel[20]["solved"] = False
    panel[31]["solved"] = True
    assert report.comparison(panel, "baseline", "ace")["cost_target_observed"]
    panel[31]["solved"] = False
    assert not report.comparison(panel, "baseline", "ace")[
        "cost_target_observed"
    ]


def test_missing_and_duplicate_cells_forbid_comparison(
    panel: list[dict[str, Any]],
) -> None:
    with pytest.raises(ValueError, match="Incomplete expected"):
        report.comparison(panel[:-1], "baseline", "ace")
    with pytest.raises(ValueError, match="Duplicate"):
        report.comparison(panel + [panel[-1]], "baseline", "ace")


def test_uncached_prices_do_not_revoke_actual_qualified_proofs(
    panel: list[dict[str, Any]],
) -> None:
    result = report.comparison(panel, "baseline", "ace", "uncached_cost")
    assert result["solved_a"] == result["solved_b"] == 10
    assert isclose(result["cost_a"], 2.4)


def test_failure_sensitivity_removes_the_same_pair_from_both_arms(
    panel: list[dict[str, Any]],
) -> None:
    panel[-1]["failed"] = True
    primary = report.comparison(panel, "baseline", "ace")
    sensitivity = report.comparison(
        panel, "baseline", "ace", exclude={("problem_9", "1")}
    )
    assert primary["cells"] == 20 and primary["failed_b"] == 1
    assert sensitivity["cells"] == 19 and sensitivity["failed_b"] == 0
    assert isclose(sensitivity["cost_a"], 0.95)
    assert isclose(sensitivity["cost_b"], 0.95)
    with pytest.raises(ValueError, match="unregistered"):
        report.comparison(panel, "baseline", "ace", exclude={("missing", "1")})


def test_historical_raw_solves_keep_their_original_budget_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def partition(_: str) -> dict[str, str]:
        return {"problem": "unused.v"}

    def canonical(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return rows

    monkeypatch.setattr(retrospective, "partition", partition)
    monkeypatch.setattr(retrospective, "canonical", canonical)
    row: dict[str, Any] = dict(
        campaign="fixture",
        partition="validation",
        path="fixture/configs/problem__ace__seed0",
        theorem="problem",
        seed="0",
        status="done",
        solved=True,
        qualified=False,
        cost=0.2,
        administrative_censoring=False,
        unknown_charge=False,
        cost_source="dated billing receipts",
        book_sha256="book",
        comparator=dict(
            strategy="prove_theorem_grounded",
            models=["fixture-model"],
            budget=dict(price=1.0),
        ),
    )
    panel = retrospective.panels([row])[0]
    assert panel["solved"] == 0
    assert panel["raw_completed_solves"] == 1
    assert panel["solved_at_original_price_budget"] == 1
    row["comparator"]["budget"]["price"] = 0.0
    assert (
        retrospective.panels([row])[0]["solved_at_original_price_budget"] == 0
    )


def test_final_export_rejects_stale_proof_and_replay_certificates(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(report.c, "CAMPAIGN", tmp_path)
    report.c.save("batches/fixture.json", {})
    report.c.save(
        "kernel_checks.json",
        dict(
            passed=True,
            results=[dict(passed=True, proof_sha256="proof", cells=["cell"])],
        ),
    )
    report.c.save(
        "replays/fixture.json",
        dict(
            passed=True,
            paid_calls=0,
            result_hashes=dict(cell="result"),
        ),
    )
    rows: list[dict[str, Any]] = [
        dict(
            cell="cell",
            proof_sha256="proof",
            result_sha256="result",
        )
    ]
    assert report.verified_exports(rows)["passed"]
    rows[0]["proof_sha256"] = "changed"
    with pytest.raises(ValueError, match="Proof certificate drift"):
        report.verified_exports(rows)
    rows[0]["proof_sha256"] = "proof"
    rows[0]["result_sha256"] = "changed"
    with pytest.raises(ValueError, match="Replay certificate drift"):
        report.verified_exports(rows)
