"""Reconcile the seven completed validation arms before S1 and O1 finish.

This makes no model calls and never scores an incomplete arm. Later main
finalization still requires every registered attempt. Paired exclusions of
terminal-failure theorems are sensitivity analyses, never replacements for
the original eighty-cell denominators.
"""

from collections import defaultdict
import json
from typing import Any

from .analysis import metrics, paired
from .common import CAMPAIGN, REPORT, partition, read, save
from .families import mapping
from .fresh import receipts, solver_rows
from .mechanisms import aggregate, characterize, contributions


def run() -> None:
    batches = [f"core_frozen-part{i:02d}" for i in range(5)]
    batches += ["core_pilot_book-part00", "core_pilot_book-part01"]
    ledger = receipts()
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    expected = {
        (name, seed) for name in partition("validation") for seed in (0, 1)
    }
    certificates: dict[str, Any] = {}
    for batch in batches:
        terminal = CAMPAIGN / "terminal_failures" / (batch + ".json")
        verification = CAMPAIGN / "verification" / (batch + ".json")
        certificates[batch] = read(
            terminal if terminal.exists() else verification
        )
        for row in solver_rows(
            batch, ledger, allow_terminal_failures=terminal.exists()
        ):
            if row["stage"] == "validation":
                row["trace_summary"] = characterize(row)
                groups[row["arm"]].append(row)
    if set(groups) != {"A0", "A1", "A2", "B0", "B1", "B2", "P1"}:
        raise ValueError("Validation arm set changed")
    for arm, rows in groups.items():
        if (
            len(rows) != 80
            or {(r["theorem"], r["seed"]) for r in rows} != expected
        ):
            raise ValueError("Incomplete validation comparison: " + arm)
    comparisons: dict[str, Any] = {}
    pairs = [("A0", arm) for arm in ("A1", "A2", "P1")]
    pairs += [("B0", arm) for arm in ("B1", "B2")]
    pairs += [("A0", "B0"), ("A2", "P1"), ("B1", "B2")]
    for base, arm in pairs:
        before, after = groups[base], groups[arm]
        failures = {
            r["theorem"] for r in before + after if r.get("terminal_failure")
        }
        item = dict(
            theorem=paired(before, after),
            family=paired(before, after, mapping()),
            mechanisms=contributions(before, after),
        )
        if failures:
            item["terminal_theorem_exclusion"] = dict(
                excluded_theorems=sorted(failures),
                theorem=paired(
                    [r for r in before if r["theorem"] not in failures],
                    [r for r in after if r["theorem"] not in failures],
                ),
                interpretation="Descriptive sensitivity only; the headline retains all eighty attempts and their actual bills.",
            )
        comparisons[f"{arm}_vs_{base}"] = item
    result = dict(
        scope="Seven complete 80-cell validationX panels; S1 and O1 excluded until their registered panels finish.",
        paid_calls=0,
        metrics={arm: metrics(rows) for arm, rows in groups.items()},
        mechanisms={arm: aggregate(rows) for arm, rows in groups.items()},
        replicates={
            f"{arm}/seed{seed}": metrics(
                [r for r in rows if r["seed"] == seed]
            )
            for arm, rows in groups.items()
            for seed in (0, 1)
        },
        comparisons=comparisons,
        certificates=certificates,
    )
    save(REPORT / "validation_diagnosis.json", result)
    print(
        json.dumps(
            dict(
                metrics=result["metrics"],
                comparisons={k: v["theorem"] for k, v in comparisons.items()},
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
