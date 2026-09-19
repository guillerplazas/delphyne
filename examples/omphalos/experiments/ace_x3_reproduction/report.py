"""Complete-matrix reporting, with independent units and cost definitions."""

from collections import Counter, defaultdict
import gzip
import json
from typing import Any, cast

import numpy as np

from experiments.ace_sanitized.scope import partition
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from tools.reports.ace_thesis import export_csv
from runtime.campaign_budget import Ledger

from . import campaign as c
from .audit import aggregate, receipts
from .diagnostics import (
    admission_tails,
    exercise_evidence,
    input_stability,
    terminations,
)


def comparisons(
    rows: list[dict[str, Any]],
    pairs: list[tuple[str, str]],
    replicates: tuple[str, ...] = ("0", "1"),
) -> dict[str, Any]:
    groups: dict[str, dict[tuple[str, str], Observation]] = defaultdict(dict)
    for row in rows:
        key = row["theorem"], str(row["seed"])
        if key in groups[row["label"]]:
            raise ValueError("Duplicate paired cell")
        groups[row["label"]][key] = Observation(
            row["solved"], row["corrected"], row.get("failed", False)
        )
    expected = [(n, s) for n in partition("validation") for s in replicates]
    families = c.read("protocol.json")["families"]
    output: dict[str, Any] = {}
    for a, b in pairs:
        qualified = compare(groups[a], groups[b], expected, families=families)
        if not qualified["complete"]:
            raise ValueError("Incomplete paired comparison")
        raw = compare(
            groups[a],
            groups[b],
            expected,
            families=families,
            cap_a=float("inf"),
            cap_b=float("inf"),
        )
        # The shared helper's historical 5pp verdict is inapplicable here.
        qualified.pop("verdict")
        raw.pop("verdict")
        savings = 1 - qualified["cost_ratio"]
        output[a + "__vs__" + b] = dict(
            qualified=qualified,
            raw=raw,
            cost_p=cost_cluster_p(groups[a], groups[b], expected, families),
            saving_percent=100 * savings,
            descriptive_ten_percent_cost_target=savings >= 0.1 - 1e-12
            and qualified["solved_b"] >= qualified["solved_a"],
            descriptive_ten_point_coverage_target=qualified["effect"]
            >= 0.1 - 1e-12,
        )
    return output


def interaction(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cells = {(r["theorem"], str(r["seed"]), r["label"]): r for r in rows}
    family_values: dict[str, list[float]] = defaultdict(
        lambda: [0.0, 0.0, 0.0]
    )
    for theorem, family in c.read("protocol.json")["families"].items():
        for seed in ("0", "1"):
            delta_cost = delta_solve = 0.0
            for arm, sign in (
                ("x3_8192", 1),
                ("none_8192", -1),
                ("x3_32768", -1),
                ("none_32768", 1),
            ):
                row = cells[theorem, seed, arm]
                delta_cost += sign * row["corrected"]
                delta_solve += sign * int(
                    row["solved"] and row["corrected"] <= 0.1 + 1e-12
                )
            family_values[family][0] += delta_cost
            family_values[family][1] += delta_solve
            family_values[family][2] += 1
    values = np.asarray(list(family_values.values()))
    rng = np.random.default_rng(20260918)
    samples = values[
        rng.integers(0, len(values), size=(10000, len(values)))
    ].sum(axis=1)
    return dict(
        definition="(X3 - empty) at 8192 minus (X3 - empty) at 32768",
        dollars_per_attempt=float(values[:, 0].sum() / values[:, 2].sum()),
        dollars_ci90=cast(
            Any, np.quantile(samples[:, 0] / samples[:, 2], [0.05, 0.95])
        ).tolist(),
        coverage_points=float(100 * values[:, 1].sum() / values[:, 2].sum()),
        coverage_points_ci90=cast(
            Any,
            (100 * np.quantile(samples[:, 1] / samples[:, 2], [0.05, 0.95])),
        ).tolist(),
        families=len(values),
        bootstrap_samples=10000,
    )


def fresh_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cells: list[dict[str, Any]] = []
    paid: list[dict[str, Any]] = []
    for job in c.jobs():
        result = c.cell_result(job)  # Refuses any administrative censoring.
        rows = receipts(c.CAMPAIGN / "ledger.sqlite3", c.name(job, None))
        if any(r["assumptions"] for r in rows if r["corrected"]):
            raise ValueError("Fresh billing metadata missing")
        folder = c.directory(job)
        cells.append(
            dict(
                label=job.arm,
                theorem=job.theorem,
                seed=str(job.seed),
                cell=c.name(job, None),
                path=str(folder.relative_to(c.ROOT)),
                solved=bool(result and result["success"]),
                failed=result is None,
                requests=len(rows),
                hashes={
                    n: c.sha(folder / n)
                    for n in ("cache.yaml", "result.yaml")
                    if (folder / n).exists()
                },
                **{
                    k: sum(r[k] for r in rows)
                    for k in (
                        "legacy",
                        "corrected",
                        "input",
                        "cached",
                        "written",
                        "output",
                        "no_cache_fixed_trace",
                        "write_premium",
                    )
                },
            )
        )
        if (
            result
            and abs(
                result["spent_budget"]["price"]
                - sum(r["legacy"] for r in rows)
            )
            > 1e-9
        ):
            raise ValueError("Controller/receipt reconciliation failure")
        for row in rows:
            path = (
                c.CAMPAIGN
                / "responses"
                / c.name(job, None)
                / (row["id"] + ".json.gz")
            )
            with gzip.open(path, "rt") as stream:
                evidence = json.load(stream)
            if row["corrected"]:
                response = evidence["response"]
                if response["id"] != row["usage"]["response_id"] or response[
                    "usage"
                ] != {k: row["usage"][k] for k in response["usage"]}:
                    raise ValueError("Provider response/receipt mismatch")
            paid.append(
                dict(
                    **row,
                    label=job.arm,
                    theorem=job.theorem,
                    seed=str(job.seed),
                    evidence_sha256=c.sha(path),
                )
            )
    if len({r["id"] for r in paid}) != len(paid):
        raise ValueError("Duplicate fresh receipt")
    summary = Ledger(c.CAMPAIGN / "ledger.sqlite3").summary()
    if abs(sum(r["corrected"] for r in paid) - summary["liability"]) > 1e-9:
        raise ValueError("Unaccounted campaign liability")
    return cells, paid


def cache_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for arm in c.ARMS:
        selected = [r for r in rows if r["label"] == arm]
        reasons: Counter[str] = Counter()
        for row in selected:
            diagnostic = row["usage"].get("prompt_cache_diagnostics")
            reasons[
                "absent"
                if diagnostic is None
                else diagnostic.get("reason")
                or diagnostic.get("type", "unavailable")
            ] += 1
        output[arm] = dict(
            diagnostics=dict(reasons),
            status=dict(
                Counter(r["usage"].get("status", "rejected") for r in selected)
            ),
            tiers=dict(
                Counter(
                    r["usage"].get("service_tier", "rejected")
                    for r in selected
                )
            ),
            model_ids=sorted(
                {r["usage"].get("model", r["model"]) for r in selected}
            ),
            cached_fraction=sum(r["cached"] for r in selected)
            / sum(r["input"] for r in selected),
        )
    return output


def historical_gap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Dollar identity per 40 attempts; deliberately not causal allocation."""
    old = {
        (r["theorem"], r["label"]): r
        for r in c.read("audit/cells.json")
        if r["label"] in ("historical_none", "historical_x3_seed0")
    }
    per_theorem: list[dict[str, Any]] = []
    for theorem in partition("validation"):
        record: dict[str, Any] = dict(theorem=theorem)
        record["historical_saving"] = (
            old[theorem, "historical_none"]["corrected"]
            - old[theorem, "historical_x3_seed0"]["corrected"]
        )
        for arm in c.ARMS:
            values = [
                r["corrected"]
                for r in rows
                if r["theorem"] == theorem and r["label"] == arm
            ]
            if len(values) != 2:
                raise ValueError("Gap decomposition requires two replicates")
            record[arm + "_mean_cost"] = sum(values) / 2
        for cap in (32768, 8192):
            record[f"new_saving_{cap}"] = (
                record[f"none_{cap}_mean_cost"] - record[f"x3_{cap}_mean_cost"]
            )
        record["loss_of_historical_saving"] = (
            record["historical_saving"] - record["new_saving_32768"]
        )
        per_theorem.append(record)
    per_theorem.sort(
        key=lambda r: r["loss_of_historical_saving"], reverse=True
    )
    old_saving = sum(r["historical_saving"] for r in per_theorem)
    new_saving = sum(r["new_saving_32768"] for r in per_theorem)
    gap = old_saving - new_saving
    # Independent dollar identity, not a causal attribution to cache warmth.
    old_volume = sum(
        r["no_cache_fixed_trace"]
        * (1 if r["label"] == "historical_none" else -1)
        for r in old.values()
    )
    new_volume = sum(
        r["no_cache_fixed_trace"]
        * (1 if r["label"] == "none_32768" else -1)
        / 2
        for r in rows
        if r["label"] in ("none_32768", "x3_32768")
    )
    c.save(
        "analysis/gap_accounting.json",
        dict(
            units="Dollars per 40 attempts",
            historical=dict(
                saving=old_saving,
                fixed_trace_volume=old_volume,
                net_cache_advantage=old_saving - old_volume,
            ),
            fresh_32768=dict(
                saving=new_saving,
                fixed_trace_volume=new_volume,
                net_cache_advantage=new_saving - new_volume,
            ),
            loss_of_saving=dict(
                total=gap,
                volume_difference=old_volume - new_volume,
                cache_difference=gap - (old_volume - new_volume),
            ),
            limitation="Accounting identity on observed traces. Not a randomized no-cache experiment or causal allocation of provider warmth, model drift and search variation.",
        ),
    )
    export_csv(c.CAMPAIGN / "analysis/gap_by_theorem.csv", per_theorem)
    return dict(
        historical_net_saving_per_40=old_saving,
        new_32768_net_saving_per_40=new_saving,
        remaining_gap_per_40=gap,
        by_theorem=per_theorem,
        limitation="Exact descriptive identity at the same recorded output cap, normalizing two new replicates to 40 attempts. The remaining temporal/sample/cache gap is not causally allocated. A negative gap means the new saving is larger.",
    )


def secondary_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Joint cost/solve uncertainty; never substitutes the registered target."""
    output: dict[str, Any] = {}
    mapping = c.read("protocol.json")["families"]
    for cap in (32768, 8192):
        values: dict[str, list[float]] = defaultdict(lambda: [0.0] * 4)
        for row in rows:
            if row["label"] not in (f"none_{cap}", f"x3_{cap}"):
                continue
            index = int(row["label"].startswith("x3_"))
            family = values[mapping[row["theorem"]]]
            family[index] += row["corrected"]
            family[index + 2] += int(
                row["solved"] and row["corrected"] <= 0.1 + 1e-12
            )
        matrix = np.asarray(list(values.values()))
        total = matrix.sum(axis=0)
        rng = np.random.default_rng(20260918)
        samples = matrix[
            rng.integers(0, len(matrix), size=(10000, len(matrix)))
        ].sum(axis=1)
        if np.any(samples[:, 2:] == 0):
            raise ValueError("Undefined bootstrap cost per solve")
        ratios = (
            samples[:, 1] * samples[:, 2] / (samples[:, 0] * samples[:, 3])
        )
        output[str(cap)] = dict(
            empty_dollars_per_solve=float(total[0] / total[2]),
            x3_dollars_per_solve=float(total[1] / total[3]),
            reduction_percent=float(
                100 * (1 - total[1] * total[2] / (total[0] * total[3]))
            ),
            reduction_percent_ci90=cast(
                Any, 100 * np.quantile(1 - ratios, [0.05, 0.95])
            ).tolist(),
            families=len(matrix),
        )
    return dict(
        cost_per_qualified_solve=output,
        limitation="Secondary descriptive metric with joint family bootstrap uncertainty. Includes costs of unsuccessful attempts. A reduction in cost per solve is not the registered 10% reduction in total spend on the same panel, and does not measure the budget needed for equal coverage.",
    )


def report() -> None:
    c.verify_seal()
    for filename in ("verification/replay.json", "verification/kernel.json"):
        if not c.read(filename)["passed"]:
            raise ValueError("Verification incomplete")
    cells, paid = fresh_records()
    grouped = {
        arm: aggregate([r for r in cells if r["label"] == arm])
        for arm in c.ARMS
    }
    pairs = [
        ("none_32768", "x3_32768"),
        ("none_8192", "x3_8192"),
        ("none_32768", "none_8192"),
        ("x3_32768", "x3_8192"),
    ]
    results = dict(
        complete=True,
        groups=grouped,
        comparisons=comparisons(cells, pairs),
        interaction=interaction(cells),
        historical_gap=historical_gap(cells),
        cache=cache_summary(paid),
        replicates={
            arm: {
                str(s): aggregate(
                    [
                        r
                        for r in cells
                        if r["label"] == arm and r["seed"] == str(s)
                    ]
                )
                for s in (0, 1)
            }
            for arm in c.ARMS
        },
        total_cost=sum(r["corrected"] for r in cells),
        cumulative_thesis_cost=c.read("prior_accounting.json")["corrected"]
        + sum(r["corrected"] for r in cells),
        limitations=[
            "Reused validationX development benchmark, not held-out confirmation",
            "Provider model alias is not an immutable backend identity",
            "Cache diagnostics are observational, not a randomized caching intervention",
            "Two replicates per theorem, clustered uncertainty over 40 theorems",
        ],
    )
    c.save("analysis/results.json", results)
    c.save("analysis/cells.json", cells)
    c.save("analysis/receipts.json", paid)
    c.save("analysis/secondary_metrics.json", secondary_metrics(cells))
    c.save("analysis/input_stability.json", input_stability(cells))
    c.save("analysis/termination.json", terminations(cells))
    c.save(
        "analysis/admission_tails_v2.json",
        admission_tails(c.CAMPAIGN / "events.jsonl", cells),
    )
    export_csv(c.CAMPAIGN / "analysis/cells.csv", cells)
    export_csv(
        c.CAMPAIGN / "analysis/receipts.csv",
        [{k: v for k, v in r.items() if k != "usage"} for r in paid],
    )
    for theorem in partition("validation"):
        old = c.read("audit/exercises/" + theorem + ".json")
        current = [
            exercise_evidence(r) for r in cells if r["theorem"] == theorem
        ]
        c.save("analysis/exercises/" + theorem + ".json", [*old, *current])
        lines = [
            f"# {theorem}",
            "",
            "All registered attempts, including failures. Costs include cache writes.",
            "",
            "| Panel | Replicate | Solved | Cost | Requests | Last checked failure |",
            "|---|---:|---:|---:|---:|---|",
        ]
        for row in [*old, *current]:
            last = row["terminal_check"]
            error = (
                "—"
                if row["solved"] or not last
                else (
                    last["feedback"].get("error_message") or last["category"]
                )
            )
            error = str(error).replace("\n", " ").replace("|", "\\|")[:180]
            lines.append(
                f"| {row['label']} | {row['seed']} | {int(row['solved'])} | ${row['corrected']:.6f} | {row['requests']} | {error} |"
            )
        lines += [
            "",
            f"Full checks, failing tactics, accepted prefixes, returned proofs, request hashes, usage and source paths are in the [compressed JSON dossier]({theorem}.json.gz). Controller stops are recorded separately in `../termination.json` (compressed in the review export when large).",
            "",
        ]
        (c.CAMPAIGN / "analysis/exercises" / (theorem + ".md")).write_text(
            "\n".join(lines)
        )
    print(json.dumps(results, indent=2))
