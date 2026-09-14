"""Offline exports of the sealed campaign's registered results.

Written after the initial panels were collected. It neither selects arms
nor changes metrics/gates. Both harnesses can run this module without HTTP.
"""

# ruff: noqa: E402 -- guard before experiment imports
from runtime.completion_scope import install

install()

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

from experiments.resource_completion_experiment import (
    ARMS,
    CAMPAIGN,
    OUTPUT,
    ROOT,
    accounting,
    read,
    save,
    verify,
)


def table(name: str, rows: list[dict[str, Any]]) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path = CAMPAIGN / name
    if path.exists():
        assert path.read_text() == buf.getvalue(), "Immutable export drift"
    else:
        path.write_text(buf.getvalue())


def main() -> None:
    verify()
    acct = accounting()
    assert not acct["unresolved"] and not acct["billing_issues"]
    assert read("final_accounting.json") == acct
    cells: list[dict[str, Any]] = []
    requests: list[dict[str, Any]] = []
    summaries: dict[str, Any] = {}
    events = [
        json.loads(s)
        for s in (CAMPAIGN / "events.jsonl").read_text().splitlines()
    ]
    for stage in ("training", "validation"):
        refs = {r["theorem"]: r for r in read("references.json")[stage]}
        for arm in ARMS:
            key = f"{stage}_{arm}"
            diags = read(f"diagnostics/{key}.json")
            assert len(diags) == 40 and read(f"replays/{key}.json")["passed"]
            for cell, d in sorted(diags.items()):
                theorem = cell.split("__")[0]
                o, exposure = d["observation"], d["exposure"]
                cells.append(
                    dict(
                        cell=cell,
                        theorem=theorem,
                        stage=stage,
                        arm=arm,
                        seed=0,
                        solved=o["solved"],
                        failed=o["failed"],
                        cost=o["cost"],
                        reference_solved=refs[theorem]["solved"],
                        reference_cost=refs[theorem]["cost"],
                        exposed=exposure[arm],
                        model_requests=len(exposure["paid_dispatches"]),
                        proof_checks=len(d["cache"]["checks"]),
                        input_tokens=d["tokens"].get("input", 0),
                        cached_input_tokens=d["tokens"].get("cached", 0),
                        output_tokens=d["tokens"].get("output", 0),
                        source=d["source"],
                    )
                )
                for index, req in enumerate(exposure["paid_dispatches"], 1):
                    requests.append(
                        dict(
                            cell=cell,
                            request=index,
                            receipt=req["receipt"],
                            output_limit=req["output_limit"],
                            structured=req["structured"],
                            shadow_32768_denied=req["shadow_denied"],
                            proof_checked=req["proof_checked"],
                            truncated=req.get("truncated", False),
                        )
                    )
            arm_cells = [
                r for r in cells if r["stage"] == stage and r["arm"] == arm
            ]
            arm_requests = [
                r for r in requests if f"__{stage}-{arm}__" in r["cell"]
            ]
            summaries[key] = dict(
                report=read(f"reports/{key}.json"),
                gains=[
                    r["theorem"]
                    for r in arm_cells
                    if r["solved"] and not r["reference_solved"]
                ],
                losses=[
                    r["theorem"]
                    for r in arm_cells
                    if not r["solved"] and r["reference_solved"]
                ],
                gains_with_exposure=[
                    r["theorem"]
                    for r in arm_cells
                    if r["solved"]
                    and not r["reference_solved"]
                    and r["exposed"]
                ],
                shadow_denied_requests=sum(
                    r["shadow_32768_denied"] for r in arm_requests
                ),
                shadow_denied_with_proof_check=sum(
                    r["shadow_32768_denied"] and r["proof_checked"]
                    for r in arm_requests
                ),
                truncated=sum(r["truncated"] for r in arm_requests),
                repaired_final_messages=sum(
                    e["kind"] == "completion_response"
                    and e.get("corrected_final_message", False)
                    for e in events
                    if f"__{stage}-{arm}__" in e.get("cell", "")
                ),
            )
    assert len(cells) == 160 and len(requests) == acct["receipts"]
    assert len({r["receipt"] for r in requests}) == len(requests)
    assert abs(sum(r["cost"] for r in cells) - acct["total"]) < 1e-8
    assert not read("selection.json")["winner"], (
        "Extend the export explicitly for follow-up"
    )
    table("cells.csv", cells)
    table("requests.csv", requests)
    save("mechanism_summary.json", summaries)
    paths = [
        *OUTPUT.rglob("cache.yaml"),
        *OUTPUT.rglob("result.yaml"),
        *(CAMPAIGN / "transport").rglob("*.json.gz"),
        CAMPAIGN / "events.jsonl",
        CAMPAIGN / "receipts_final.csv",
    ]
    save(
        "output_inventory.json",
        {
            str(p.relative_to(ROOT)): hashlib.sha256(
                p.read_bytes()
            ).hexdigest()
            for p in sorted(paths)
        },
    )
    save(
        "export_verification.json",
        dict(
            cells=len(cells),
            requests=len(requests),
            all_receipts_unique=True,
            all_panels_replayed=True,
            all_source_seals_verified=True,
            total=acct["total"],
            remaining=30 - acct["total"],
            platform_failures=sum(r["failed"] for r in cells),
            source=str(Path(__file__).relative_to(ROOT)),
        ),
    )


if __name__ == "__main__":
    main()
