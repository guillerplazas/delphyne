"""Export dated receipts and bind local validation archives by SHA-256.

Both harnesses: python -m tools.analysis.export_economy_receipts --campaign
main (or budget). This is offline and only enumerates registered validation
cells. It never imports the eager X loader or invokes a mixed-scope verifier.
Large caches/transport snapshots stay local; compact exports are reviewable.
"""

import argparse
import csv
from datetime import datetime, timezone
import json
from typing import Any

from experiments import ace_economy_experiment as original
from experiments import ace_economy_validation as main_campaign
from runtime.campaign_budget import Ledger
from runtime.model_registry import price_tokens


def export(module: Any, batches: tuple[str, ...]) -> None:
    module.verify()
    account = module.accounting()
    if account["unresolved"] or account["billing_issues"]:
        raise ValueError("All billing must settle before export")
    jobs = [job for batch in batches for job in module.configs(batch)]
    cells = {module.name(job, None): job for job in jobs}
    if len(cells) != len(jobs) or any(
        job.stage != "validation" for job in jobs
    ):
        raise ValueError("Only unique registered validation cells")
    with Ledger(module.CAMPAIGN / "ledger.sqlite3").connect() as db:
        raw = db.execute(
            "SELECT id,cell,model,created,status,charged,usage FROM receipts ORDER BY created,id"
        ).fetchall()
    receipts: list[dict[str, Any]] = []
    for ident, cell, model, created, status, charged, encoded in raw:
        if cell not in cells or status != "settled":
            raise ValueError("Unexpected or unsettled receipt")
        usage = json.loads(encoded)
        inp, out = usage["input_tokens"], usage["output_tokens"]
        cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
        stamp = datetime.fromtimestamp(created, timezone.utc)
        repriced = price_tokens(model, inp, cached, out, on=stamp.date())
        if abs(charged - repriced) > 1e-8:
            raise ValueError("Dated receipt cost mismatch")
        receipts.append(
            dict(
                receipt=ident,
                cell=cell,
                model=model,
                created_utc=stamp.isoformat(),
                status=status,
                input=inp,
                cached=cached,
                output=out,
                reasoning=usage.get("output_tokens_details", {}).get(
                    "reasoning_tokens", 0
                ),
                charged=charged,
                repriced=repriced,
            )
        )
    if abs(sum(v["repriced"] for v in receipts) - account["total"]) > 1e-8:
        raise ValueError("Export does not reconcile to ledger")
    destination = module.CAMPAIGN / "analysis"
    destination.mkdir(exist_ok=True)
    with (destination / "receipts.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(receipts[0]))
        writer.writeheader()
        writer.writerows(receipts)
    archives: dict[str, Any] = {}
    for ident, job in cells.items():
        module.cell_result(job)
        folder = module.directory(job)
        files = [
            folder / filename
            for filename in ("result.yaml", "cache.yaml")
            if (folder / filename).exists()
        ]
        files.extend((module.CAMPAIGN / "transport" / ident).glob("*.json.gz"))
        archives[ident] = {
            str(p.relative_to(original.ROOT)): original.sha(p)
            for p in sorted(files)
        }
    module.save(
        "analysis/archives.json",
        dict(
            authorized_partition="validationX",
            cells=archives,
            paid_calls=0,
            receipt_rows=len(receipts),
            total_cost=account["total"],
            receipts_sha256=original.sha(destination / "receipts.csv"),
        ),
    )
    print(
        json.dumps(
            dict(
                cells=len(cells), receipts=len(receipts), cost=account["total"]
            )
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--campaign", choices=("main", "budget"), required=True
    )
    args = parser.parse_args()
    if args.campaign == "main":
        export(main_campaign, main_campaign.BATCHES)
    else:
        from experiments import (
            ace_economy_budget_experiment as budget_campaign,
        )

        export(budget_campaign, ("validation",))
