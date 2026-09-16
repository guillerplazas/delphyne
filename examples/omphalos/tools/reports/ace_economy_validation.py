"""Offline validation-only economics report after the scope correction.

Use explicit registered validation batches, never the retired mixed-scope
report/verifier. Statistical primitives retain the preregistered tests.
Both harnesses: python -m tools.reports.ace_economy_validation.
"""

import csv
from datetime import date
import json
from typing import Any

from experiments import ace_economy_validation as c
from runtime.model_registry import price_tokens
from tools.reports.ace_economy_results import candidate_interest, paired


def cells() -> list[dict[str, Any]]:
    ledger = c.accounting()
    if ledger["unresolved"] or ledger["billing_issues"]:
        raise ValueError("Unresolved billing prevents an economic verdict")
    rows: list[dict[str, Any]] = []
    for batch in c.BATCHES:
        for config in c.configs(batch):
            result = c.cell_result(config)
            ident = c.name(config, None)
            cost = ledger["costs"].get(ident, 0.0)
            tokens = ledger["tokens"].get(
                ident, dict(input=0, cached=0, output=0)
            )
            rows.append(
                dict(
                    cell=ident,
                    stage="validation",
                    arm=config.arm,
                    theorem=config.bench_name,
                    seed=config.seed,
                    cap=config.cap,
                    solved=bool(result and result["success"]),
                    qualified=bool(
                        result
                        and result["success"]
                        and cost <= config.cap + 1e-12
                    ),
                    failed=result is None,
                    cost=cost,
                    requests=result["spent_budget"].get("num_requests", 0)
                    if result
                    else 0,
                    rocq_seconds=result["spent_budget"].get("rocq_seconds", 0)
                    if result
                    else 0,
                    **tokens,
                    uncached_cost=price_tokens(
                        "gpt-5.6-luna",
                        tokens["input"],
                        0,
                        tokens["output"],
                        on=date(2026, 9, 16),
                    ),
                )
            )
    identifiers = {r["cell"] for r in rows}
    if len(rows) != 400 or len(identifiers) != 400:
        raise ValueError("Exactly 400 unique validation cells required")
    if set(ledger["costs"]) - identifiers:
        raise ValueError("A receipt is outside the registered panel")
    if abs(sum(r["cost"] for r in rows) - ledger["total"]) > 1e-8:
        raise ValueError("Cell costs do not reconcile to receipts")
    return rows


def report() -> dict[str, Any]:
    c.verify()
    rows = cells()
    ledger = c.accounting()
    totals: dict[str, Any] = {}
    comparisons: dict[str, Any] = {}
    interests: dict[str, Any] = {}
    for arm in ("agentic", "ace", "budget", "session", "views"):
        subset = [r for r in rows if r["arm"] == arm]
        total: dict[str, Any] = {
            key: sum(r[key] for r in subset)
            for key in (
                "cost",
                "uncached_cost",
                "input",
                "cached",
                "output",
                "requests",
                "rocq_seconds",
                "qualified",
                "failed",
            )
        }
        total["cells"] = len(subset)
        total["cost_per_solve"] = (
            total["cost"] / total["qualified"] if total["qualified"] else None
        )
        total["cache_fraction"] = total["cached"] / total["input"]
        totals[f"validation/{arm}"] = total
        if arm == "agentic":
            continue
        reference = "agentic" if arm == "ace" else "ace"
        result = paired(rows, "validation", arm, reference)
        seeds = [
            paired(rows, "validation", arm, reference, seed=s) for s in (0, 1)
        ]
        if not result["complete"] or any(not v["complete"] for v in seeds):
            raise ValueError("Missing required matched cells")
        result["per_seed"] = seeds
        result["observed_ten_percent_target"] = result[
            "observed_ten_percent_target"
        ] and all(v["solved_b"] >= v["solved_a"] for v in seeds)
        comparisons[f"validation/{reference}_vs_{arm}"] = result
        if arm != "ace":
            interests[arm] = candidate_interest(result, seeds)
    eligible = [arm for arm, interested in interests.items() if interested]
    preferred = min(
        eligible,
        key=lambda arm: (
            -totals[f"validation/{arm}"]["qualified"],
            totals[f"validation/{arm}"]["cost"],
        ),
        default=None,
    )
    result = dict(
        totals=totals,
        paired=comparisons,
        practical_interest=interests,
        preferred_development_intervention=preferred,
        no_further_dispatch=True,
        default_promoted=False,
        authorized_partition="validationX",
        spend=ledger["total"],
        receipts=ledger["receipts"],
        unresolved=ledger["unresolved"],
        billing_issues=ledger["billing_issues"],
        preparation_lower_bound=1.36785368,
        statistical_caution="Repeatedly reused validation data; advisor comparisons exploratory, p-values unadjusted across three interventions. Equal observed coverage does not establish noninferiority. Held-out confirmation revoked by user.",
    )
    destination = c.CAMPAIGN / "analysis"
    destination.mkdir(exist_ok=True)
    for filename, value in (
        ("results.json", result),
        ("accounting.json", ledger),
    ):
        (destination / filename).write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n"
        )
    with (c.CAMPAIGN / "cells.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return result


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
