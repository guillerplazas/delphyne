"""Final receipt, source-seal and dispatched-book inventory; no HTTP."""

# ruff: noqa: E402
from runtime.ace_learning_scope import install

install()

import csv
import gzip
import json
import math
from typing import Any

from experiments import ace_learning_experiment as c
from runtime.campaign_budget import Ledger
from tools.reports.ace_learning_results import write


def audit() -> None:
    c.verify()
    old = json.loads((c.PRIOR / "seal.json").read_text())
    if any(c.sha(c.ROOT / p) != h for p, h in old["files"].items()):
        raise ValueError("Historical source changed")
    exposures: list[dict[str, Any]] = []
    paths = set(c.OUTPUT.rglob("result.yaml")) | set(
        c.OUTPUT.rglob("cache.yaml")
    )
    paths.update(
        (
            c.CAMPAIGN / "events.jsonl",
            c.PRIOR / "events.jsonl",
            c.CAMPAIGN / "receipts.csv",
        )
    )
    for control in c.read("compatibility.json")["reference_cells"]:
        result = c.ROOT / control["path"]
        paths.update((result, result.with_name("cache.yaml")))
    for j in c.all_configs():
        if j.role != "proof":
            continue
        book = c.read(j.input_file)["playbook"].strip()
        folder = c.CAMPAIGN / "transport" / c.name(j, None)
        snapshots = sorted(folder.glob("*.json.gz"))
        hits: list[str] = []
        for p in snapshots:
            paths.add(p)
            raw = json.loads(gzip.decompress(p.read_bytes()))
            request = raw["request"]["request"]
            if any(book in str(m.get("content", "")) for m in request["chat"]):
                hits.append(str(p.relative_to(c.ROOT)))
        if snapshots and not hits:
            raise ValueError("Book missing from dispatched query snapshots")
        exposures.append(
            dict(
                cell=c.name(j, None),
                snapshots=len(snapshots),
                exact_book_exposures=len(hits),
                example=hits[0] if hits else None,
                explanation="Logical request captured at model dispatch, including the context represented through Responses continuation. Demonstrates exposure, not use or causal benefit.",
            )
        )
    with Ledger(c.CAMPAIGN / "ledger.sqlite3").connect() as db:
        cursor = db.execute("SELECT * FROM receipts ORDER BY created,id")
        with (c.CAMPAIGN / "receipts.csv").open("w") as out:
            writer = csv.writer(out)
            writer.writerow([d[0] for d in cursor.description])
            writer.writerows(cursor.fetchall())
    write("analysis/dispatched_books.json", exposures)
    economics: dict[str, Any] = c.read("analysis/economics.json")
    metrics: dict[str, Any] = c.read("analysis/metrics.json")
    comparisons: dict[str, Any] = {}
    for key, m in metrics.items():
        if not m["complete"]:
            continue
        arm = key.split("/")[1]
        preparation = economics["totals"]["preparation"][arm]
        old_preparation = economics["totals"]["original_preparation_cost"]
        saving = (m["cost_a"] - m["cost_b"]) / m["cells"]
        comparisons[key] = dict(
            inference_cost_per_solve_v2=m["cost_per_qualified_solve_a"],
            inference_cost_per_solve_candidate=m["cost_per_qualified_solve_b"],
            preparation_plus_panel_v2=old_preparation + m["cost_a"],
            preparation_plus_panel_candidate=preparation + m["cost_b"],
            preparation_plus_panel_per_solve_v2=(old_preparation + m["cost_a"])
            / m["solved_a"]
            if m["solved_a"]
            else None,
            preparation_plus_panel_per_solve_candidate=(
                preparation + m["cost_b"]
            )
            / m["solved_b"]
            if m["solved_b"]
            else None,
            amortize_new_preparation_against_available_v2_cells=math.ceil(
                preparation / saving
            )
            if saving > 0
            else None,
            amortize_incremental_preparation_cells=math.ceil(
                max(0, preparation - old_preparation) / saving
            )
            if saving > 0
            else None,
            caution="Descriptive extrapolation, not a deployment forecast. Historical source collection and benchmark/pilot research are separate sunk resources. CPU costs are not API charges.",
        )
    economics["comparisons"] = comparisons
    economics["totals"]["pilot_research_charges"] = c.stage_used("pilots")
    economics["totals"]["proof_benchmark_research_charges"] = c.stage_used(
        "training"
    ) + c.stage_used("validation")
    write("analysis/economics.json", economics)
    write(
        "analysis/raw_inventory.json",
        dict(
            files={
                str(p.relative_to(c.ROOT)): dict(
                    bytes=p.stat().st_size, sha256=c.sha(p)
                )
                for p in sorted(paths)
            },
            note="Large immutable raw caches/transport remain in the local archive, not duplicated into the lean Git evidence bundle.",
        ),
    )
    write(
        "analysis/final_integrity.json",
        dict(
            passed=True,
            old_sealed_files=len(old["files"]),
            new_sealed_files=len(c.read("seal.json")["files"]),
            new_accounting=c.accounting(),
            proof_exposure_cells=len(exposures),
            inventory_files=len(paths),
            no_defaults_changed=True,
        ),
    )
    print("Integrity and exposure passed:", len(exposures), "proof cells")


if __name__ == "__main__":
    audit()
