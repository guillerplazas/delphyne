"""Independent descriptive census and paired, clustered uncertainty."""

from collections import defaultdict
import csv
import json
import re
from typing import Any, cast

import numpy as np

from .common import CAMPAIGN, REPORT, digest, save
from .cost_bounds import interval, total_interval


def historical() -> list[dict[str, Any]]:
    with (REPORT / "raw_cells.jsonl").open() as stream:
        return [json.loads(line) for line in stream]


def normalized(value: Any, theorem: str) -> Any:
    if isinstance(value, dict):
        return {
            k: normalized(v, theorem)
            for k, v in cast(dict[str, Any], value).items()
            if k
            not in {
                "cell",
                "snapshot_directory",
                "evidence_directory",
                "pause_file",
                "input_file",
                "evidence_file",
                "prefix_cache",
                "expected_next",
            }
        }
    if isinstance(value, list):
        return [normalized(v, theorem) for v in cast(list[Any], value)]
    if isinstance(value, str):
        return value.replace(theorem, "<theorem>")
    return value


def metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    costs = [r["costs"].get("price", 0) for r in rows]
    solved = sum(r["solved"] for r in rows)
    total = sum(costs)
    result: dict[str, Any] = dict(
        n=len(rows),
        theorems=len({r["theorem"] for r in rows}),
        solves=solved,
        coverage=solved / len(rows) if rows else None,
        cost=total,
        cost_per_solve=total / solved if solved else None,
        failed_cost=sum(c for c, r in zip(costs, rows) if not r["solved"]),
        requests=sum(r["counts"].get("requests", 0) for r in rows),
        auto_finished=sum(r["counts"].get("auto_finished", 0) for r in rows),
        missing_usage=sum(not r["exact_cost"] for r in rows),
        max_cell_cost=max(costs, default=0),
        input_cost=sum(r["costs"].get("input_cost", 0) for r in rows),
        output_cost=sum(r["costs"].get("output_cost", 0) for r in rows),
        large_context_requests=sum(
            t["input"] > 272000 for r in rows for t in r["turns"]
        ),
    )
    lower, upper = total_interval(rows)
    if lower != upper:
        failed = total_interval([r for r in rows if not r["solved"]])
        result.update(
            cost_interval=[lower, upper],
            cost_per_solve_interval=[lower / solved, upper / solved]
            if solved
            else None,
            failed_cost_interval=list(failed),
            bounded_cost_cells=sum(
                interval(r)[0] != interval(r)[1] for r in rows
            ),
            unknown_charge_upper=upper - lower,
            cost_is_exact=False,
            billing_note="Cost fields use retained upper liability. The actual invoice is within cost_interval; input/output components cover only observed usage.",
        )
    return result


def paired(
    base: list[dict[str, Any]],
    arm: list[dict[str, Any]],
    families: dict[str, str] | None = None,
) -> dict[str, Any]:
    def index(
        rows: list[dict[str, Any]],
    ) -> dict[tuple[str, int], dict[str, Any]]:
        result: dict[tuple[str, int], dict[str, Any]] = {}
        for r in rows:
            key = (r["theorem"], r["seed"])
            if key in result:
                raise ValueError("Duplicate comparison cell")
            result[key] = r
        return result

    b, a = index(base), index(arm)
    if b.keys() != a.keys():
        return dict(
            complete=False,
            baseline_cells=len(b),
            arm_cells=len(a),
            missing_baseline=sorted(a.keys() - b.keys()),
            missing_arm=sorted(b.keys() - a.keys()),
        )
    groups: dict[str, list[float]] = defaultdict(
        lambda: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    )
    for key in b:
        br, ar = b[key], a[key]
        group = (families or {}).get(key[0], key[0])
        g = groups[group]
        for i, v in enumerate(
            [
                br["costs"].get("price", 0),
                ar["costs"].get("price", 0),
                float(br["solved"]),
                float(ar["solved"]),
                1.0,
                interval(br)[0],
                interval(ar)[0],
            ]
        ):
            g[i] += v
    mat = np.array(list(groups.values()))
    rng = np.random.default_rng(20260919)
    samples = mat[rng.integers(0, len(mat), size=(10000, len(mat)))].sum(
        axis=1
    )
    savings = 1 - samples[:, 1] / samples[:, 0]
    coverage = (samples[:, 3] - samples[:, 2]) / samples[:, 4]
    totals = mat.sum(axis=0)
    difference = totals[1] - totals[0]
    groupdiff = mat[:, 1] - mat[:, 0]
    # Monte Carlo paired sign flips at the chosen cluster level.
    signs = rng.choice([-1.0, 1.0], size=(50000, len(mat)))
    permuted = np.abs(signs @ groupdiff)
    observed = abs(difference)
    # The observed difference subtracts two panel sums; a permuted value
    # sums cluster differences. Equal statistics can therefore differ by
    # floating-point roundoff. Include ties within a tolerance far below
    # the tariff's smallest monetary increment, rather than dropping the
    # all-favorable permutations of a sparse budget comparison.
    extreme = (permuted >= observed) | np.isclose(
        permuted, observed, rtol=1e-12, atol=1e-12
    )
    p = (1 + int(np.sum(extreme))) / 50001
    loo: list[float] = []
    for row in mat:
        left = totals - row
        loo.append(float(1 - left[1] / left[0]))
    result: dict[str, Any] = dict(
        complete=True,
        n=int(totals[4]),
        clusters=len(mat),
        baseline_cost=float(totals[0]),
        arm_cost=float(totals[1]),
        baseline_solves=int(totals[2]),
        arm_solves=int(totals[3]),
        saving=1 - float(totals[1] / totals[0]),
        saving_ci90=[
            float(cast(Any, np.quantile(savings, q))) for q in (0.05, 0.95)
        ],
        coverage_delta=float((totals[3] - totals[2]) / totals[4]),
        coverage_delta_ci90=[
            float(cast(Any, np.quantile(coverage, q))) for q in (0.05, 0.95)
        ],
        cost_difference=float(difference),
        two_sided_sign_flip_p=p,
        leave_one_cluster_out_saving=[min(loo), max(loo)],
        practical_target=bool(
            totals[1] <= 0.9 * totals[0]
            and totals[3] >= totals[2] - 0.05 * totals[4]
        ),
    )
    if any(interval(r)[0] != interval(r)[1] for r in base + arm):
        worst = 1 - float(totals[1] / totals[5])
        best = 1 - float(totals[6] / totals[0])
        worst_samples = 1 - samples[:, 1] / samples[:, 5]
        best_samples = 1 - samples[:, 6] / samples[:, 0]
        left_out = [totals - row for row in mat]
        result.update(
            baseline_cost_interval=[float(totals[5]), float(totals[0])],
            arm_cost_interval=[float(totals[6]), float(totals[1])],
            saving_interval=[worst, best],
            cost_difference_interval=[
                float(totals[6] - totals[0]),
                float(totals[1] - totals[5]),
            ],
            saving_ci90=[
                float(cast(Any, np.quantile(worst_samples, 0.05))),
                float(cast(Any, np.quantile(best_samples, 0.95))),
            ],
            leave_one_cluster_out_saving=[
                min(float(1 - left[1] / left[5]) for left in left_out),
                max(float(1 - left[6] / left[0]) for left in left_out),
            ],
            two_sided_sign_flip_p=None,
            practical_target=bool(
                totals[1] <= 0.9 * totals[5]
                and totals[3] >= totals[2] - 0.05 * totals[4]
            ),
            cost_is_exact=False,
            billing_note="Scalar costs and saving use upper liabilities, not exact invoices. saving_interval covers every permitted bill; the 90% interval envelopes clustered bootstrap endpoint intervals. No exact cost p-value is reported. The practical target uses the adverse billing endpoint.",
        )
    return result


def summarize() -> None:
    rows = historical()
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for r in rows:
        leaf = r["path"].rsplit("/", 1)[-1]
        label = re.sub(
            r"seed[_-]?\d+", "seed*", leaf.replace(r["theorem"], "{theorem}")
        )
        config_hash = digest(normalized(r["config"], r["theorem"]))
        groups[(r["campaign"], r["stage"], label, config_hash)].append(r)
    table: list[dict[str, Any]] = []
    for (campaign, stage, label, identity), rr in sorted(groups.items()):
        table.append(
            dict(
                campaign=campaign,
                stage=stage,
                label=label,
                identity=identity,
                strategy=rr[0]["config"]["strategy"],
                policy=rr[0]["config"]["policy"],
                models=";".join(sorted({m for r in rr for m in r["models"]})),
                **metrics(rr),
            )
        )
    with (REPORT / "all_variants.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    original = [r for r in rows if r["campaign"] == "x_validation_agentic"]
    comparisons: list[dict[str, Any]] = []
    candidates: list[tuple[float, int, int, list[dict[str, Any]]]] = []
    for key, rr in groups.items():
        if key[1] != "validation" or not key[0].startswith("ace_x_validation"):
            continue
        verdict = paired(original, rr)
        comparisons.append(
            dict(campaign=key[0], label=key[2], identity=key[3], **verdict)
        )
        if (
            verdict.get("complete")
            and metrics(rr)["solves"] >= metrics(original)["solves"] - 4
        ):
            candidates.append(
                (
                    metrics(rr)["cost"],
                    -metrics(rr)["solves"],
                    len(rr[0]["config"]["strategy_args"].get("playbook", "")),
                    rr,
                )
            )
    save(REPORT / "historical_original_comparisons.json", comparisons)
    selected = min(candidates, key=lambda c: c[:3])[3]
    first = selected[0]
    save(
        CAMPAIGN / "books/A1_historical.json",
        dict(
            text=first["config"]["strategy_args"]["playbook"],
            render_version=first["config"]["strategy_args"]["render_version"],
            source_campaign=first["campaign"],
            source_cell=first["path"],
            source_result_sha=first["result_sha"],
            metrics=metrics(selected),
            selection="Complete original-loop 80-cell panels, within 4 solves of baseline; minimum all-attempt cost, then coverage, then size. Historical selection only; fresh test required.",
        ),
    )
    print(
        json.dumps(
            dict(
                groups=len(table),
                selected=first["campaign"],
                metrics=metrics(selected),
            )
        )
    )
