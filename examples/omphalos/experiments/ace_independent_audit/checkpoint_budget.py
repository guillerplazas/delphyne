"""Describe already completed controller replays at the user's hold.

This module consumes saved certificates only. It cannot dispatch a replay,
an experiment, or an API call. Only full forty-problem replicates contribute
comparisons; every completed frozen cell remains in the inventory.
"""

from collections import defaultdict
from typing import Any

from .analysis import metrics, paired
from .common import CAMPAIGN, REPORT, allowed, read, save
from .families import mapping


def run(original: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [
        r
        for r in original
        if r["batch"] not in ("source", "author_pilot")
        and not r["arm"].startswith("online_")
    ]
    groups: dict[tuple[str, str, int, float], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    scenarios: list[dict[str, Any]] = []
    for row in eligible:
        certificate = read(
            CAMPAIGN / "budget_replay" / (row["cell"] + ".json")
        )
        expected_hashes: dict[str, Any] = {
            "result.yaml": row["result_sha"],
            "cache.yaml": row["cache_sha"],
        }
        if row.get("terminal_failure"):
            expected_hashes["exception.txt"] = row["exception_sha"]
        if certificate["hashes"] != expected_hashes:
            raise ValueError("Budget certificate differs from completed cell")
        if {r["cap"] for r in certificate["rows"]} != {0.05, 0.075, 0.09}:
            raise ValueError("Incomplete budget replay certificate")
        for replay in certificate["rows"]:
            if replay["paid_calls"] != 0:
                raise ValueError("Offline budget replay made a paid call")
            transformed = dict(
                row,
                solved=replay["solved"],
                costs=dict(price=replay["spent_budget"].get("price", 0)),
                counts=dict(
                    requests=replay.get(
                        "attempted_requests",
                        replay["spent_budget"].get("num_requests", 0),
                    )
                ),
                turns=[],
            )
            groups[
                row["stage"], row["arm"], row["seed"], replay["cap"]
            ].append(transformed)
            scenarios.append(replay)
        groups[row["stage"], row["arm"], row["seed"], 0.10].append(row)
    complete: dict[tuple[str, str, int, float], list[dict[str, Any]]] = {}
    for key, rows in groups.items():
        names = {t for t, (stage, _) in allowed().items() if stage == key[0]}
        if len(rows) == 40 and {r["theorem"] for r in rows} == names:
            complete[key] = rows
    comparisons: dict[str, Any] = {}
    within_controls: dict[str, Any] = {}
    for (stage, arm, seed, cap), rows in complete.items():
        label = f"{stage}/{arm}/replicate{seed}/cap{cap:g}"
        baseline = "B0" if arm.startswith("B") else "A0"
        if arm in ("A0", "B0"):
            full = complete[stage, arm, seed, 0.10]
            if cap < 0.10:
                within_controls[label] = dict(
                    theorem=paired(full, rows),
                    family=paired(full, rows, mapping()),
                )
        else:
            reference = complete.get((stage, baseline, seed, cap))
            if reference is not None:
                comparisons[label] = dict(
                    baseline=baseline,
                    theorem=paired(reference, rows),
                    family=paired(reference, rows, mapping()),
                )
    keys = (
        "n",
        "theorems",
        "solves",
        "coverage",
        "cost",
        "cost_per_solve",
        "failed_cost",
        "requests",
        "max_cell_cost",
    )
    result = dict(
        completed_frozen_cells=len(eligible),
        completed_replay_scenarios=len(scenarios),
        registered_frozen_cells=1520,
        registered_replay_scenarios=4560,
        paid_calls=0,
        complete_replicates={
            f"{stage}/{arm}/replicate{seed}/cap{cap:g}": {
                k: v for k, v in metrics(rows).items() if k in keys
            }
            for (stage, arm, seed, cap), rows in complete.items()
        },
        same_cap_comparisons=comparisons,
        lower_budget_controls_vs_full_budget=within_controls,
        interpretation="Conditional on the recorded responses, verifier results and cache behavior; these are controller replays, not new model samples. A saving from lowering both methods' budget must not be attributed to ACE. Only complete forty-problem replicates are compared; registered two-replicate panels remain unfinished.",
    )
    save(REPORT / "checkpoint_budget_results.json", result)
    save(REPORT / "checkpoint_budget_cells.json", scenarios)
    return result
