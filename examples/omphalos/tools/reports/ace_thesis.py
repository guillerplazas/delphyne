"""All-attempt measurements and descriptive target tests for the sealed study.

Both harnesses: python -m tools.reports.ace_thesis. Reporting does not dispatch
requests. A reporting-source hash binds each export, independently of the
prospectively sealed experiment code. Missing/censored cells forbid export.
"""

from collections import defaultdict
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any

from experiments.ace_thesis import campaign as c
from experiments.ace_thesis.artifact import fingerprint
from experiments.ace_thesis.design import families
from experiments.ace_sanitized.scope import partition
from runtime.model_registry import price_tokens
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)


def receipts() -> list[dict[str, Any]]:
    with c.Ledger(c.CAMPAIGN / "ledger.sqlite3").connect() as db:
        raw = db.execute(
            "SELECT id,stage,cell,model,created,charged,status,usage FROM receipts ORDER BY created,id"
        ).fetchall()
    result: list[dict[str, Any]] = []
    for ident, stage, cell, model, created, charged, status, encoded in raw:
        usage = json.loads(encoded or "{}")
        inp, out = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
        day = datetime.fromtimestamp(created, timezone.utc)
        repriced = price_tokens(model, inp, cached, out, on=day.date())
        if (
            status != "settled"
            or charged is None
            or abs(charged - repriced) > 1e-8
        ):
            raise ValueError("Unsettled or mismatched receipt")
        result.append(
            dict(
                receipt=ident,
                stage=stage,
                cell=cell,
                model=model,
                created_utc=day.isoformat(),
                charged=charged,
                repriced=repriced,
                input=inp,
                cached=cached,
                output=out,
                reasoning=usage.get("output_tokens_details", {}).get(
                    "reasoning_tokens", 0
                ),
                uncached_cost=price_tokens(model, inp, 0, out, on=day.date()),
                exception=usage.get(
                    "exception", usage.get("reconciled_exception")
                ),
                response_id=usage.get("response_id"),
                provider_model=usage.get("model"),
            )
        )
    return result


def collect(billing: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_cell: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in billing:
        by_cell[row["cell"]].append(row)
    result: list[dict[str, Any]] = []
    for job in c.all_jobs():
        value = c.cell_result(job)
        paid = by_cell.pop(c.name(job, None), [])
        cost = sum(p["repriced"] for p in paid)
        data = c.read(job.input_file)
        result.append(
            dict(
                cell=c.name(job, None),
                stage=job.stage,
                arm=job.arm,
                role=job.role,
                theorem=job.theorem,
                replicate=job.seed,
                failed=value is None,
                solved=bool(
                    value and value["success"] and cost <= job.cap + 1e-12
                ),
                cost=cost,
                uncached_cost=sum(p["uncached_cost"] for p in paid),
                receipts=len(paid),
                requests=(value or {})
                .get("spent_budget", {})
                .get("num_requests"),
                input=sum(p["input"] for p in paid),
                cached=sum(p["cached"] for p in paid),
                output=sum(p["output"] for p in paid),
                artifact_sha256=data.get("artifact_sha256"),
                input_sha256=job.input_sha256,
                result_sha256=c.sha(c.directory(job) / "result.yaml")
                if value
                else None,
                proof_sha256=fingerprint(value["values"][0])
                if job.role == "proof" and value and value["success"]
                else None,
                cache_sha256=c.sha(c.directory(job) / "cache.yaml")
                if (c.directory(job) / "cache.yaml").exists()
                else None,
            )
        )
    if by_cell:
        raise ValueError("Receipts outside registered cells")
    return result


def totals(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row["role"] != "proof":
            continue
        key = row["stage"] + "/" + row["arm"]
        item = output.setdefault(
            key,
            dict(
                cells=0,
                solved=0,
                failed=0,
                cost=0.0,
                uncached_cost=0.0,
                input=0,
                cached=0,
                output=0,
            ),
        )
        for field in item:
            item[field] += 1 if field == "cells" else row[field]
    for item in output.values():
        item["coverage_percent"] = 100 * item["solved"] / item["cells"]
        item["cost_per_solve"] = (
            item["cost"] / item["solved"] if item["solved"] else None
        )
    return output


def comparison(
    rows: list[dict[str, Any]],
    left: str,
    right: str,
    cost_field: str = "cost",
    *,
    exclude: set[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    excluded = exclude or set()
    registered = {(t, str(s)) for t in partition("validation") for s in (0, 1)}
    if not excluded <= registered:
        raise ValueError("Sensitivity mask contains an unregistered cell")

    def observations(arm: str) -> dict[tuple[str, str], Observation]:
        chosen = [
            r
            for r in rows
            if r["stage"] == "validation"
            and r["arm"] == arm
            and (r["theorem"], str(r["replicate"])) not in excluded
        ]
        result = {
            (r["theorem"], str(r["replicate"])): Observation(
                r["solved"], r[cost_field], r["failed"]
            )
            for r in chosen
        }
        if len(chosen) != len(result):
            raise ValueError("Duplicate theorem/replicate")
        return result

    a, b = observations(left), observations(right)
    expected = sorted(registered - excluded)
    family = families("validation")
    # Uncached sensitivity changes price only; never retroactively revoke
    # proofs with a hypothetical cap that did not govern their search.
    cap = 0.1 if cost_field == "cost" else float("inf")
    result = compare(a, b, expected, families=family, cap_a=cap, cap_b=cap)
    if not result["complete"]:
        raise ValueError("Incomplete expected validation panel")
    result.pop("verdict")
    saving = 100 * (1 - result["cost_ratio"])
    points = 100 * result["effect"]
    result.update(
        left=left,
        right=right,
        cost_field=cost_field,
        excluded_cells=sorted(excluded),
        coverage_change_points=points,
        budget_reduction_percent=saving,
        budget_reduction_ci90=[
            100 * (1 - v) for v in reversed(result["cost_ratio_ci90"])
        ],
        cost_p_two_sided=cost_cluster_p(a, b, expected, family),
        coverage_target_observed=points >= 10 - 1e-9,
        cost_target_observed=saving >= 10 - 1e-9
        and result["solved_b"] >= result["solved_a"],
        coverage_threshold_ci90=100 * result["effect_ci90"][0] >= 10,
        cost_threshold_ci90=result["cost_ratio_ci90"][1] <= 0.9,
        limitation="Point-estimate targets are distinct from population guarantees; validationX is reused development data.",
    )
    return result


def export_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as out:
        writer = csv.DictWriter(
            out, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def verified_exports(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Refuse a final claim from missing or obsolete verification records."""
    kernel = c.read("kernel_checks.json")
    if not kernel["passed"] or not all(r["passed"] for r in kernel["results"]):
        raise ValueError("Independent proof verification failed")
    checked = {
        cell: result["proof_sha256"]
        for result in kernel["results"]
        for cell in result["cells"]
    }
    expected = {
        r["cell"]: r["proof_sha256"] for r in rows if r["proof_sha256"]
    }
    if checked != expected:
        raise ValueError("Proof certificate drift")
    replayed: dict[str, str] = {}
    hashes: dict[str, str] = {}
    for batch in sorted((c.CAMPAIGN / "batches").glob("*.json")):
        path = f"replays/{batch.stem}.json"
        certificate = c.read(path)
        if not certificate["passed"] or certificate["paid_calls"] != 0:
            raise ValueError("Exact replay did not pass without paid calls")
        replayed.update(certificate["result_hashes"])
        hashes[path] = c.sha(c.CAMPAIGN / path)
    expected = {
        r["cell"]: r["result_sha256"] for r in rows if r["result_sha256"]
    }
    if replayed != expected:
        raise ValueError("Replay certificate drift")
    return dict(
        passed=True,
        kernel_sha256=c.sha(c.CAMPAIGN / "kernel_checks.json"),
        replay_sha256=hashes,
    )


def main() -> None:
    c.verify()
    billing = receipts()
    rows = collect(billing)
    verification = (
        verified_exports(rows)
        if (c.CAMPAIGN / "finished.json").exists()
        else dict(passed=False, reason="Development stage; benchmark pending")
    )
    summary = totals(rows)
    for key, item in summary.items():
        stage, arm = key.split("/")
        cells = [r for r in rows if r["stage"] == stage and r["arm"] == arm]
        item["distinct_solved"] = len(
            {r["theorem"] for r in cells if r["solved"]}
        )
        item["replicates"] = {
            str(seed): dict(
                cells=sum(r["replicate"] == seed for r in cells),
                solved=sum(
                    r["replicate"] == seed and r["solved"] for r in cells
                ),
                cost=sum(r["cost"] for r in cells if r["replicate"] == seed),
            )
            for seed in (0, 1)
        }
    source_hash = c.sha(Path(__file__))
    destination = c.CAMPAIGN / "analysis" / source_hash[:16]
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "reporting_source.py").write_text(
        Path(__file__).read_text()
    )
    export_csv(destination / "cells.csv", rows)
    export_csv(destination / "receipts.csv", billing)
    pairs: list[dict[str, Any]] = []
    historical_pairs: list[dict[str, Any]] = []
    learning_cost = sum(r["cost"] for r in rows if r["stage"] == "learning")
    development_cost = sum(
        r["cost"] for r in rows if r["stage"] in ("round1", "round2")
    )
    if (c.CAMPAIGN / "finished.json").exists():
        aliases = c.read("panel_aliases.json")
        selected = aliases.get("ace_selected", "ace_selected")
        validation_rows = [r for r in rows if r["stage"] == "validation"]
        failure_mask = {
            (r["theorem"], str(r["replicate"]))
            for r in validation_rows
            if r["failed"]
        }
        by_theorem: list[dict[str, Any]] = []
        for theorem in sorted(partition("validation")):
            record: dict[str, Any] = dict(theorem=theorem)
            for arm in sorted({r["arm"] for r in validation_rows}):
                cells = [
                    r
                    for r in validation_rows
                    if r["theorem"] == theorem and r["arm"] == arm
                ]
                if len(cells) != 2:
                    raise ValueError(
                        "Expected two recorded replicates per arm"
                    )
                record[arm + "_solved"] = sum(r["solved"] for r in cells)
                record[arm + "_cost"] = sum(r["cost"] for r in cells)
                record[arm + "_failed"] = sum(r["failed"] for r in cells)
            by_theorem.append(record)
        export_csv(destination / "validation_by_theorem.csv", by_theorem)
        for baseline in (
            "nonace_ordinary",
            "nonace_matched",
            "ace_historical",
        ):
            baseline = aliases.get(baseline, baseline)
            if baseline == selected:
                continue
            pair = comparison(rows, baseline, selected)
            saving_per_attempt = (pair["cost_a"] - pair["cost_b"]) / pair[
                "cells"
            ]
            pair["incremental_role_learning_break_even_attempts"] = (
                math.ceil(learning_cost / saving_per_attempt)
                if saving_per_attempt > 0
                else None
            )
            pair["new_development_and_learning_break_even_attempts"] = (
                math.ceil(
                    (development_cost + learning_cost) / saving_per_attempt
                )
                if saving_per_attempt > 0
                else None
            )
            pair["uncached_sensitivity"] = comparison(
                rows, baseline, selected, "uncached_cost"
            )
            if failure_mask:
                pair["platform_failure_sensitivity"] = comparison(
                    rows, baseline, selected, exclude=failure_mask
                )
            pairs.append(pair)
        historical = aliases.get("ace_historical", "ace_historical")
        for baseline in ("nonace_ordinary", "nonace_matched"):
            pair = comparison(rows, baseline, historical)
            pair["interpretation"] = (
                "Secondary registered historical-treatment contrast; does not "
                "replace training selection or the selected-artifact endpoint."
            )
            pair["uncached_sensitivity"] = comparison(
                rows, baseline, historical, "uncached_cost"
            )
            if failure_mask:
                pair["platform_failure_sensitivity"] = comparison(
                    rows, baseline, historical, exclude=failure_mask
                )
            historical_pairs.append(pair)
    result = dict(
        totals=summary,
        comparisons=pairs,
        verification=verification,
        historical_comparisons=historical_pairs,
        accounting=c.accounting(),
        new_learning_roles_cost=learning_cost,
        new_development_proofs_cost=development_cost,
        new_preparation_cost=learning_cost + development_cost,
        source_sha256=source_hash,
        historical_preparation="Reused books/examples are sunk preparation, not free; see provenance appendix.",
        kernel_certificate="kernel_checks.json",
        replay_certificates="replays/",
        archive_recovery=[
            "operations/round1_recovered.json",
            "operations/validation_recovered.json",
        ],
        protected_data_read=False,
    )
    (destination / "results.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(
        json.dumps(
            dict(
                analysis=str(destination.relative_to(c.ROOT)),
                totals=summary,
                comparisons=pairs,
            )
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
