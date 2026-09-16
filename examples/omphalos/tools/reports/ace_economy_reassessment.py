"""Reassess the three completed validationX campaigns after clarification.

Guille's "quality" means code and implementation quality, not a requirement
to preserve solve counts in every replicate. This is a retrospective
interpretation amendment, not a new preregistration or statistical test.
Keep coverage, cost and uncertainty separate; do not mutate frozen reports.

Both harnesses: python -m tools.reports.ace_economy_reassessment.
Only six explicit validation-only exports are read. No model, experiment,
partition loader, cache, ledger or mixed-scope verifier is imported.
"""

import csv
import hashlib
import io
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGNS = ROOT / "experiments/campaigns"
SOURCES = {
    "main": ("ace_economy_20260916", "analysis/results.json", 400),
    "budget": ("ace_economy_budget_20260916", "results.json", 80),
    "session": ("ace_economy_session_20260916", "results.json", 320),
}
DESTINATION = CAMPAIGNS / "ace_economy_20260916/reassessment/results.json"


def load_source(label: str) -> tuple[dict[str, Any], dict[str, str]]:
    """Reject unknown sources before opening anything; bind exact exports."""
    if label not in SOURCES:
        raise ValueError("Only the three registered validationX sources")
    campaign, filename, count = SOURCES[label]
    directory = CAMPAIGNS / campaign
    cells_path = directory / "cells.csv"
    cells_bytes = cells_path.read_bytes()
    cells = list(csv.DictReader(io.StringIO(cells_bytes.decode())))
    if len(cells) != count or any(
        not row["cell"].startswith("validation__")
        or row.get("stage", "validation") != "validation"
        for row in cells
    ):
        raise ValueError("Expected complete validationX exports only")
    report_path = directory / filename
    report_bytes = report_path.read_bytes()
    data: dict[str, Any] = json.loads(report_bytes)
    if label != "budget" and data.get("authorized_partition") != "validationX":
        raise ValueError("Report must declare validationX")
    return data, {
        str(path.relative_to(ROOT)): hashlib.sha256(value).hexdigest()
        for path, value in (
            (cells_path, cells_bytes),
            (report_path, report_bytes),
        )
    }


def assess(pair: dict[str, Any]) -> dict[str, Any]:
    """Report economic effects without using solve counts as a veto."""
    if not pair["complete"] or pair["cells"] != 80 or pair["families"] != 40:
        raise ValueError(
            "A complete 80-cell, 40-family comparison is required"
        )
    solved_a, solved_b = int(pair["solved_a"]), int(pair["solved_b"])
    if not all(0 <= count <= 80 for count in (solved_a, solved_b)):
        raise ValueError("Solve counts must fit the complete denominator")
    cost_a, cost_b = float(pair["cost_a"]), float(pair["cost_b"])
    if not all(math.isfinite(cost) for cost in (cost_a, cost_b)):
        raise ValueError("Costs must be finite")
    if cost_a <= 0 or cost_b < 0:
        raise ValueError("A positive reference cost is required")
    ratio = cost_b / cost_a
    cps_a = cost_a / solved_a if solved_a else None
    cps_b = cost_b / solved_b if solved_b else None
    return {
        "cells": 80,
        "families": 40,
        "proofs_reference": solved_a,
        "proofs_candidate": solved_b,
        "proof_count_change": solved_b - solved_a,
        "cost_reference": cost_a,
        "cost_candidate": cost_b,
        "cost_change_percent": 100 * (ratio - 1),
        "inference_saving_percent": 100 * (1 - ratio),
        "observed_ten_percent_saving": ratio <= 0.90,
        "cost_per_solve_reference": cps_a,
        "cost_per_solve_candidate": cps_b,
        "cost_per_solve_change_percent": (
            100 * (cps_b / cps_a - 1)
            if cps_a is not None and cps_b is not None
            else None
        ),
        "cost_ratio_ci90": pair["cost_ratio_ci90"],
        "cost_p_two_sided": pair["cost_p_two_sided"],
        "coverage_p_two_sided": pair["p_two_sided"],
        "nominal_cost_saving_supported": ratio < 1
        and pair["cost_p_two_sided"] < 0.10,
        "ten_percent_saving_supported_by_ci90": (
            pair["cost_ratio_ci90"][1] <= 0.90
        ),
        "per_replicate_coverage_is_a_gate": False,
        "legacy_only": {
            key: pair[key]
            for key in (
                "observed_ten_percent_target",
                "observed_target",
                "practical_interest",
                "verdict",
            )
            if key in pair
        },
    }


def main() -> None:
    loaded = {label: load_source(label) for label in SOURCES}
    main_data, budget_data, session_data = (
        loaded[label][0] for label in ("main", "budget", "session")
    )
    pairs = main_data["paired"]
    comparisons: dict[str, dict[str, Any]] = {}
    for key, pair in pairs.items():
        comparisons[key.removeprefix("validation/")] = assess(pair)
    for arm, passed in main_data["practical_interest"].items():
        comparisons[f"ace_vs_{arm}"]["legacy_only"]["practical_interest"] = (
            passed
        )
    comparisons["matched_20_cent_ace"] = assess(budget_data["validation"])
    comparisons["matched_reset_ace"] = assess(
        session_data["primary_ace_with_reset"]
    )
    comparisons["non_ace_reset"] = assess(
        session_data["secondary_non_ace_reset_effect"]
    )
    interpretations = {
        "agentic_vs_ace": "1.47% observed saving; below the 10% target.",
        "matched_20_cent_ace": (
            "0.34% observed saving; below the 10% target."
        ),
        "matched_reset_ace": (
            "Observed 10% inference target achieved; promising result, "
            "with unchanged pooled coverage and uncertain generalization."
        ),
        "ace_vs_session": (
            "Promising efficiency improvement: more proofs and lower "
            "cost per solve; leading advisor intervention."
        ),
        "ace_vs_views": (
            "Promising efficiency improvement: more proofs and lower "
            "cost per solve; retain as an additional candidate."
        ),
        "ace_vs_budget": (
            "Useful coverage-cost trade-off: more proofs at substantially "
            "higher total cost and cost per solve; not an economy win."
        ),
        "non_ace_reset": (
            "Positive observed coverage-cost trade-off: more proofs, "
            "with higher total cost and cost per solve."
        ),
    }
    for key, interpretation in interpretations.items():
        comparisons[key]["current_interpretation"] = interpretation
    report = {
        "authority": "Guille's 2026-09-16 quality clarification",
        "authorized_partition": "validationX",
        "retrospective_amendment": True,
        "quality_means": "code and implementation quality",
        "coverage_role": "reported outcome; no automatic per-replicate veto",
        "statistics_role": (
            "Unchanged uncertainty; practical promise is separate from "
            "statistical support. Advisor tests remain exploratory."
        ),
        "frozen_measurements_and_gates_modified": False,
        "source_sha256": {
            key: value
            for _, hashes in loaded.values()
            for key, value in hashes.items()
        },
        "comparisons": comparisons,
        "preferred_development_intervention": "session",
        "additional_promising_intervention": "views",
        "default_promoted": False,
        "new_paid_calls": 0,
        "combined_spend": round(float(session_data["combined_spend"]), 8),
        "combined_ceiling": 50,
    }
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Reassessed {len(comparisons)} comparisons; no paid calls.")


if __name__ == "__main__":
    main()
