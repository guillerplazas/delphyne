"""Numeric cost/coverage assessment, independent of implementation judgment.

Both harnesses: python -m experiments.economy_refinement.report pilot
or final. Validation outcomes never change the frozen treatments. The
complete-panel flag describes the registered 640-cell benchmark, separately
from any complete matched subset stopped administratively between blocks.
"""

import argparse
from collections import Counter, defaultdict
from datetime import date
import csv
import gzip
import json
from pathlib import Path
import re
from typing import Any

import numpy as np

from experiments import ace_economy_refinement_experiment as c
from experiments import ace_economy_validation as reference
from runtime.model_registry import price_tokens
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
    exact_cluster_p,
)


def arm(ace: bool, reset: bool, compact: bool) -> str:
    return (
        ("ace" if ace else "agentic")
        + ("_reset" if reset else "")
        + ("_compact" if compact else "")
    )


def totals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for label in sorted({r["arm"] for r in rows}):
        selected = [r for r in rows if r["arm"] == label]
        total: dict[str, Any] = {
            key: sum(r[key] for r in selected)
            for key in (
                "qualified",
                "failed",
                "cost",
                "input",
                "cached",
                "output",
                "uncached_cost",
                "requests",
                "resets",
            )
        }
        total.update(
            cells=len(selected),
            cost_per_solve=total["cost"] / total["qualified"]
            if total["qualified"]
            else None,
            cache_fraction=total["cached"] / total["input"]
            if total["input"]
            else None,
            cells_with_reset=sum(bool(r["resets"]) for r in selected),
            per_seed={
                str(seed): dict(
                    cells=sum(r["seed"] == seed for r in selected),
                    qualified=sum(
                        r["qualified"] for r in selected if r["seed"] == seed
                    ),
                    cost=sum(r["cost"] for r in selected if r["seed"] == seed),
                )
                for seed in sorted({r["seed"] for r in selected})
            },
        )
        result[label] = total
    return result


def frontier(values: dict[str, Any], *, ace: bool | None = None) -> list[str]:
    labels = [
        label
        for label in values
        if ace is None or label.startswith("ace" if ace else "agentic")
    ]
    return sorted(
        label
        for label in labels
        if not any(
            values[other]["cost"] <= values[label]["cost"]
            and values[other]["qualified"] >= values[label]["qualified"]
            and (
                values[other]["cost"] < values[label]["cost"]
                or values[other]["qualified"] > values[label]["qualified"]
            )
            for other in labels
            if other != label
        )
    )


def assessment(pair: dict[str, Any]) -> dict[str, Any]:
    """Practical savings and coverage are independent; no replicate veto."""
    if not pair["complete"]:
        raise ValueError("Missing matched cells prevent assessment")
    ratio = pair["cost_ratio"]
    gain = pair["solved_b"] - pair["solved_a"]
    return dict(
        cost_change_percent=100 * (ratio - 1) if ratio is not None else None,
        proof_count_change=gain,
        ten_percent_saving=ratio is not None and ratio <= 0.90,
        lower_cost=ratio is not None and ratio < 1,
        higher_coverage=gain > 0,
        coverage_cost_tradeoff=(gain < 0 and ratio is not None and ratio < 1)
        or (gain > 0 and ratio is not None and ratio > 1),
        cost_difference_supported=pair["cost_p_two_sided"] < 0.10,
        coverage_difference_supported=pair["p_two_sided"] < 0.10,
        cost_per_solve_a=pair["cost_a"] / pair["solved_a"]
        if pair["solved_a"]
        else None,
        cost_per_solve_b=pair["cost_b"] / pair["solved_b"]
        if pair["solved_b"]
        else None,
    )


def collect(batches: list[str]) -> list[dict[str, Any]]:
    account = c.accounting()
    if account["unresolved"] or account["billing_issues"]:
        raise ValueError("Wait for billing to settle before reporting")
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for line in (c.CAMPAIGN / "events.jsonl").open():
        event = json.loads(line)
        if (
            event.get("kind") == "refined_session"
            and event.get("decision") == "reset"
        ):
            counts[event["cell"]]["resets"] += 1
        if (
            event.get("kind") == "transport"
            and event.get("decision") == "saved"
        ):
            counts[event["cell"]]["requests"] += 1
    rows: list[dict[str, Any]] = []
    for batch in batches:
        if not (c.CAMPAIGN / f"batches/{batch}.json").exists():
            raise ValueError("Incomplete batch: " + batch)
        for job in c.configs(batch):
            result = c.cell_result(job)
            ident = c.name(job, None)
            cost = account["costs"].get(ident, 0)
            tokens = account["tokens"].get(
                ident, dict(input=0, cached=0, output=0)
            )
            solved = bool(result and result["success"])
            rows.append(
                dict(
                    cell=ident,
                    batch=batch,
                    stage=job.stage,
                    arm=job.arm,
                    theorem=job.bench_name,
                    seed=job.seed,
                    solved=solved,
                    qualified=solved and cost <= c.CAP + 1e-12,
                    failed=result is None,
                    cost=cost,
                    **tokens,
                    requests=counts[ident]["requests"],
                    resets=counts[ident]["resets"],
                    uncached_cost=price_tokens(
                        "gpt-5.6-luna",
                        tokens["input"],
                        0,
                        tokens["output"],
                        on=date(2026, 9, 16),
                    ),
                )
            )
    return rows


def pairs(rows: list[dict[str, Any]], pilot: bool) -> dict[str, Any]:
    observations: dict[str, dict[tuple[str, str], Observation]] = defaultdict(
        dict
    )
    for row in rows:
        key = row["theorem"], str(row["seed"])
        if key in observations[row["arm"]]:
            raise ValueError("Duplicate arm/problem/seed")
        observations[row["arm"]][key] = Observation(
            row["solved"], row["cost"], row["failed"]
        )
    expected = sorted(
        {key for value in observations.values() for key in value}
    )
    families = (
        {n: n for n, _ in expected}
        if pilot
        else reference.original.families("validation")
    )
    result: dict[str, Any] = {}

    def pair(a: str, b: str) -> None:
        left, right = observations[a], observations[b]
        value = compare(
            left, right, expected, families=families, cap_a=c.CAP, cap_b=c.CAP
        )
        if not value["complete"]:
            raise ValueError("Incomplete matched comparison")
        value.pop(
            "verdict"
        )  # Legacy 5-point solve gate is not this objective.
        value.update(
            reference=a,
            candidate=b,
            cost_p_two_sided=cost_cluster_p(left, right, expected, families),
        )
        value["assessment"] = assessment(value)
        result[f"{a} -> {b}"] = value

    settings = [(False, False), (True, False), (False, True)]
    if not pilot:
        settings.append((True, True))
    for reset, compact in settings:
        pair(arm(False, reset, compact), arm(True, reset, compact))
    for ace in (False, True):
        for reset, compact in settings[1:]:
            pair(arm(ace, False, False), arm(ace, reset, compact))
        if not pilot:
            pair(arm(ace, False, True), arm(ace, True, True))
            pair(arm(ace, True, False), arm(ace, True, True))
    if not pilot:
        # Include every ACE-vs-non-ACE comparison: forcing equal reset settings
        # can handicap the stronger non-ACE comparator. Frontier selection is
        # descriptive on this reused validation panel, not a causal estimate.
        for ra, pa in settings:
            for rb, pb in settings:
                pair(arm(False, ra, pa), arm(True, rb, pb))
    return result


def interactions(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Within-agent reset x compact difference-in-differences, clustered."""
    families = reference.original.families("validation")
    indexed = {(r["arm"], r["theorem"], r["seed"]): r for r in rows}
    cells = sorted({(r["theorem"], r["seed"]) for r in rows})
    result: dict[str, Any] = {}
    for ace in (False, True):
        grouped: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
        for theorem, seed in cells:
            values = [
                indexed[(arm(ace, r, p), theorem, seed)]
                for r, p in (
                    (False, False),
                    (True, False),
                    (False, True),
                    (True, True),
                )
            ]
            group = grouped[families[theorem]]
            for i, metric in enumerate(("cost", "qualified")):
                group[i] += (
                    values[3][metric]
                    - values[1][metric]
                    - values[2][metric]
                    + values[0][metric]
                )
            group[2] += 1
        array = np.array(list(grouped.values()), dtype=float)
        rng = np.random.default_rng(20260917)
        samples = array[
            rng.integers(0, len(array), size=(10000, len(array)))
        ].sum(axis=1)
        intervals = np.quantile(
            samples[:, :2] / samples[:, 2, None], [0.05, 0.95], axis=0
        )
        result["ace" if ace else "agentic"] = dict(
            definition="combined - reset - compact + baseline; per cell",
            cost=float(array[:, 0].sum() / len(cells)),
            cost_ci90=[float(x) for x in intervals[:, 0]],
            coverage=float(array[:, 1].sum() / len(cells)),
            coverage_ci90=[float(x) for x in intervals[:, 1]],
            coverage_p_two_sided=exact_cluster_p(
                [int(x) for x in array[:, 1]]
            ),
            interpretation="Negative cost indicates additional saving beyond additive effects; positive coverage indicates additional coverage.",
        )
    return result


def pilot_audit() -> dict[str, Any]:
    """Inspect all pilot requests; verify reset transport state and failures."""
    jobs = c.configs("pilot")
    by_id = {c.name(j, None): j for j in jobs}
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for line in (c.CAMPAIGN / "events.jsonl").open():
        event = json.loads(line)
        if event.get("cell") in by_id:
            events[event["cell"]].append(event)
    records: list[dict[str, Any]] = []
    for ident, job in by_id.items():
        initial_state: str | None = None
        reset_pending = False
        error_counts: Counter[str] = Counter()
        checks = 0
        first_system_chars: int | None = None
        for event in events[ident]:
            if (
                event.get("kind") == "refined_session"
                and event.get("decision") == "reset"
            ):
                if not job.reset:
                    raise ValueError("Reset in an unregistered arm")
                if event["before_chars"] - event["after_chars"] < 8192:
                    raise ValueError("Reset failed its savings bound")
                reset_pending = True
            if (
                event.get("kind") != "transport"
                or event.get("decision") != "saved"
            ):
                continue
            path = (
                c.CAMPAIGN
                / "transport"
                / ident
                / (event["request"] + ".json.gz")
            )
            saved = json.loads(gzip.decompress(path.read_bytes()))
            if initial_state is None:
                initial_state = saved["before"]
            if reset_pending:
                if saved["before"] != initial_state:
                    raise ValueError(
                        "Opaque reasoning survived a session drop"
                    )
                checks += 1
                reset_pending = False
            chat = saved["request"]["request"]["chat"]
            if first_system_chars is None:
                first_system_chars = len(chat[0]["content"])
            # Examine the newest feedback, not copies resent in every request.
            instance: int | None = None
            for index, message in enumerate(chat):
                if message.get("role") == "user" and not message.get(
                    "is_feedback", False
                ):
                    instance = index
            if instance is None:
                raise ValueError("Request has no problem instance")
            feedback = next(
                (
                    m.get("content", "")
                    for m in reversed(chat[instance + 1 :])
                    if m.get("is_feedback")
                ),
                "",
            )
            if feedback:
                text = str(feedback).lower()
                for label, pattern in (
                    (
                        "unknown_name",
                        r"reference .*not found|unknown.*reference|not a declared",
                    ),
                    ("syntax", r"syntax error|lexer|illegal application"),
                    (
                        "unclosed_goal",
                        r"incomplete|cannot find witness|unable to unify",
                    ),
                    (
                        "resource",
                        r"timeout|timed out|resource_exhausted|deadline",
                    ),
                    (
                        "transport",
                        r"transport failure|server.*died|connection",
                    ),
                ):
                    if re.search(pattern, text):
                        error_counts[label] += 1
        records.append(
            dict(
                cell=ident,
                first_system_chars=first_system_chars,
                reset_transport_checks=checks,
                reset_without_next_paid_call=reset_pending,
                feedback_request_flags=dict(error_counts),
            )
        )
    return dict(
        cells=records,
        interpretation="Flags count requests observing newest feedback, not unique failures. Diagnostics guide code review; no problem-specific mathematical recipe or book change.",
    )


def report(pilot: bool) -> dict[str, Any]:
    c.verify()
    batches = (
        ["pilot"]
        if pilot
        else [
            b
            for b in c.FINAL_BATCHES
            if (c.CAMPAIGN / f"batches/{b}.json").exists()
        ]
    )
    if not batches:
        raise ValueError("No completed blocks")
    rows = collect(batches)
    account = c.accounting()
    total = totals(rows)
    complete = pilot or len(batches) == len(c.FINAL_BATCHES)
    result: dict[str, Any] = dict(
        stage="trainX pilot" if pilot else "validationX benchmark",
        complete_registered_panel=complete,
        expected_cells=24 if pilot else 640,
        observed_cells=len(rows),
        matched_theorems=len({r["theorem"] for r in rows}),
        totals=total,
        comparisons=pairs(rows, pilot),
        frontiers=dict(
            ace=frontier(total, ace=True),
            agentic=frontier(total, ace=False),
            combined=frontier(total),
        ),
        new_spend=account["total"],
        prior_spend=sum(c.prior_costs().values()),
        combined_spend=account["total"] + sum(c.prior_costs().values()),
        default_promoted=False,
        uncertainty="Reused development partitions; repeated seeds are clustered by theorem family. Exploratory comparisons are not multiplicity-adjusted. Frontier selection and uncached repricing are descriptive, not new experiments. No equivalence claim follows from equal counts.",
        report_source_sha256=c.sha(Path(__file__)),
    )
    if pilot:
        result["implementation_audit"] = pilot_audit()
    else:
        if not (c.CAMPAIGN / "benchmark_finished.json").exists():
            raise ValueError(
                "Wait for benchmark completion or administrative stop"
            )
        expected_ids = {
            c.name(j, None) for b in ["pilot", *batches] for j in c.configs(b)
        }
        if set(account["costs"]) - expected_ids:
            raise ValueError("Unaccounted receipts outside completed cells")
        if (
            abs(
                sum(r["cost"] for r in rows)
                + sum(r["cost"] for r in collect(["pilot"]))
                - account["total"]
            )
            > 1e-8
        ):
            raise ValueError("Cell costs do not reconcile")
        result["interactions"] = interactions(rows)
    filename = "pilot_numbers" if pilot else "results"
    c.save(f"{filename}.json", result)
    with (c.CAMPAIGN / f"{filename}_cells.csv").open("w") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    print(
        json.dumps(
            dict(
                complete=complete,
                cells=len(rows),
                totals=total,
                spend=account["total"],
            ),
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("pilot", "final"))
    args = parser.parse_args()
    report(args.stage == "pilot")
