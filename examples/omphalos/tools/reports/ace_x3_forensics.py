"""Offline decomposition of the historical X3 result, using permitted cells.

Both harnesses: python -m tools.reports.ace_x3_forensics.
No paid requests. Original census and sealed experiment exports stay intact.
The explicit legacy ledger mapping repairs a gap in the census's root-name
lookup without opening unrelated receipt rows or rerunning the whole census.
"""

from collections import defaultdict
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any

import yaml

from experiments.ace_thesis import campaign as c
from experiments.ace_thesis.artifact import fingerprint
from experiments.ace_sanitized.scope import partition
from runtime.model_registry import price_tokens
from tools.reports.ace_thesis import export_csv

HISTORY = "audit/retrospective/a37ab9343885ea57/comparisons.json"
FRESH = "analysis/8a0e952bec9d71f5"
LEDGERS = {
    "a": "ace_attribution_20260912",
    "b": "ace_polish_20260909",
    "b_seed1": "ace_polish_20260909",
}


def raw(path: Path) -> Any:
    return yaml.load(path.read_text(), Loader=yaml.CSafeLoader)


def first_request(directory: Path) -> dict[str, Any]:
    return next(
        e["input"]["request"]
        for e in raw(directory / "cache.yaml")
        if e["input"]["request"]["options"].get("model") != "__compute__"
    )


def billing(ledger: Path, cell: str) -> list[dict[str, Any]]:
    with sqlite3.connect(f"file:{ledger}?mode=ro", uri=True) as db:
        rows = db.execute(
            "SELECT id,model,created,charged,status,usage,stage FROM receipts WHERE cell=? ORDER BY created,id",
            (cell,),
        ).fetchall()
    if not rows:
        raise ValueError("Missing exact-cell receipts: " + cell)
    result: list[dict[str, Any]] = []
    for ident, model, created, charged, status, encoded, stage in rows:
        usage = json.loads(encoded)
        day = datetime.fromtimestamp(created, timezone.utc).date()
        inp, out = usage["input_tokens"], usage["output_tokens"]
        cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
        cost = price_tokens(model, inp, cached, out, on=day)
        if status != "settled" or abs(cost - charged) > 1e-9:
            raise ValueError("Unresolved or mispriced receipt")
        result.append(
            dict(
                ledger=str(ledger.relative_to(c.ROOT)),
                cell=cell,
                receipt=ident,
                date=day.isoformat(),
                stage=stage,
                charged=charged,
                uncached=price_tokens(model, inp, 0, out, on=day),
                input=inp,
                cached=cached,
                output=out,
            )
        )
    return result


def total(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {
        field: sum(r[field] for r in rows)
        for field in ("cost", "uncached", "input", "cached", "output")
    }
    result.update(
        cells=len(rows),
        solved=sum(r["solved"] for r in rows),
        cached_fraction=result["cached"] / result["input"],
        cache_discount=result["uncached"] - result["cost"],
    )
    return result


def decomposition(a: dict[str, Any], b: dict[str, Any]) -> dict[str, float]:
    net = a["cost"] - b["cost"]
    base = a["uncached"] - b["uncached"]
    discount = b["cache_discount"] - a["cache_discount"]
    if abs(net - base - discount) > 1e-9:
        raise ValueError("Cost decomposition does not reconcile")
    return dict(
        net_saving=net,
        uncached_volume_component=base,
        cache_discount_component=discount,
        saving_percent=100 * net / a["cost"],
        uncached_saving_percent=100 * base / a["uncached"],
    )


def main() -> None:
    allowed = partition("validation")
    historical = c.read(HISTORY)[0]
    if historical["label"] != "attribution_X3":
        raise ValueError("Unexpected historical reference")
    records: dict[str, dict[str, dict[str, Any]]] = {}
    receipts: list[dict[str, Any]] = []
    for arm, campaign in LEDGERS.items():
        records[arm] = {}
        ledger = c.ROOT / "experiments/campaigns" / campaign / "ledger.sqlite3"
        paths = historical["source_paths_" + arm.removesuffix("_seed1")]
        if arm == "b_seed1":
            paths = [p.removesuffix("__seed0") + "__seed1" for p in paths]
        for path in paths:
            if not any("/" + name + "__" in path for name in allowed):
                raise ValueError("Source path outside validation allowlist")
            row = c.read("audit/cells/" + fingerprint(path) + ".json")
            if row["theorem"] not in allowed:
                raise ValueError("Unauthorized theorem")
            if arm == "b_seed1":
                prior = records["b"][row["theorem"]]
                if (
                    row["book_sha256"] != prior["book_sha256"]
                    or row["comparator"] != prior["comparator"]
                ):
                    raise ValueError("Alternate X3 replicate has changed")
            directory = c.ROOT / path
            for name, value in row["hashes"].items():
                if c.sha(directory / name) != value:
                    raise ValueError("Historical raw evidence changed")
            paid = billing(ledger, directory.name)
            receipts.extend(paid)
            cost = sum(r["charged"] for r in paid)
            if abs(cost - row["cache_cost_current_tariff"]) > 1e-9:
                raise ValueError("Legacy ledger/cache difference")
            for field in ("input", "cached", "output"):
                if sum(r[field] for r in paid) != row["tokens"][field]:
                    raise ValueError("Legacy ledger/cache token difference")
            records[arm][row["theorem"]] = dict(
                cost=cost,
                uncached=sum(r["uncached"] for r in paid),
                **row["tokens"],
                solved=row["solved"],
                requests=len(paid),
                directory=directory,
                book_sha256=row["book_sha256"],
                comparator=row["comparator"],
            )
        if set(records[arm]) != set(allowed):
            raise ValueError("Incomplete historical panel")
    with (c.CAMPAIGN / FRESH / "cells.csv").open() as stream:
        fresh = [
            r for r in csv.DictReader(stream) if r["stage"] == "validation"
        ]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in fresh:
        grouped[row["arm"]].append(
            dict(
                **{
                    k: float(row[k])
                    for k in ("cost", "input", "cached", "output")
                },
                uncached=float(row["uncached_cost"]),
                solved=row["solved"] == "True",
            )
        )
    comparisons: list[dict[str, Any]] = []
    parity: list[dict[str, Any]] = []
    jobs = {(j.arm, j.theorem, j.seed): j for j in c.jobs("validation")}
    for theorem in sorted(allowed):
        a, b = records["a"][theorem], records["b"][theorem]
        row: dict[str, Any] = dict(theorem=theorem)
        for label, value in (
            ("old_nonace", a),
            ("old_x3", b),
            ("old_x3_seed1", records["b_seed1"][theorem]),
        ):
            row[label + "_source"] = str(
                value["directory"].relative_to(c.ROOT)
            )
            row.update(
                {
                    label + "_" + k: v
                    for k, v in value.items()
                    if k not in {"directory", "comparator"}
                }
            )
        row["old_saving"] = a["cost"] - b["cost"]
        for arm in ("nonace_ordinary", "nonace_matched", "ace_historical"):
            cells = [
                r for r in fresh if r["arm"] == arm and r["theorem"] == theorem
            ]
            if len(cells) != 2:
                raise ValueError("Missing fresh replicate")
            row[arm + "_solves"] = sum(r["solved"] == "True" for r in cells)
            row[arm + "_mean_cost"] = sum(float(r["cost"]) for r in cells) / 2
            old = a if arm.startswith("nonace") else b
            new = c.directory(jobs[arm, theorem, 0])
            before, after = first_request(old["directory"]), first_request(new)
            parity.append(
                dict(
                    theorem=theorem,
                    arm=arm,
                    identical_chat=before["chat"] == after["chat"],
                    identical_tools=before["tools"] == after["tools"],
                    old_options=before["options"],
                    new_options=after["options"],
                    old_request_sha256=fingerprint(before),
                    new_request_sha256=fingerprint(after),
                )
            )
        comparisons.append(row)
    old_totals = {a: total(list(r.values())) for a, r in records.items()}
    fresh_totals = {a: total(r) for a, r in grouped.items()}
    ranked = sorted(comparisons, key=lambda r: r["old_saving"], reverse=True)
    net = old_totals["a"]["cost"] - old_totals["b"]["cost"]
    result = dict(
        historical=old_totals,
        fresh=fresh_totals,
        historical_decomposition=decomposition(
            old_totals["a"], old_totals["b"]
        ),
        fresh_matched_decomposition=decomposition(
            fresh_totals["nonace_matched"], fresh_totals["ace_historical"]
        ),
        alternate_x3_sensitivity=dict(
            decomposition=decomposition(
                old_totals["a"], old_totals["b_seed1"]
            ),
            same_playbook_and_observed_configuration=True,
            limitation="Reuses the original non-ACE seed-0 control; no matching second non-ACE replicate. Not a second independently controlled comparison.",
        ),
        top_two_share_of_net_saving=sum(r["old_saving"] for r in ranked[:2])
        / net,
        ledger_mapping=LEDGERS,
        legacy_receipts=len(receipts),
        all_receipts_settled_and_repriced=True,
        historical_cache_and_ledger_agree=True,
        request_comparisons=len(parity),
        identical_initial_chats=sum(r["identical_chat"] for r in parity),
        identical_initial_tools=sum(r["identical_tools"] for r in parity),
        history_sha256=c.sha(c.CAMPAIGN / HISTORY),
        fresh_cells_sha256=c.sha(c.CAMPAIGN / FRESH / "cells.csv"),
        source_sha256=c.sha(Path(__file__)),
        limitation="Price decomposition fixes observed paths; it is not a causal cache ablation. Initial request parity is not equality of adaptive continuations. No paid reruns or protected-data access.",
    )
    destination = (
        c.CAMPAIGN / "audit/x3_forensics" / c.sha(Path(__file__))[:16]
    )
    destination.mkdir(parents=True, exist_ok=True)
    export_csv(destination / "by_theorem.csv", ranked)
    export_csv(destination / "legacy_receipts.csv", receipts)
    (destination / "requests.json").write_text(
        json.dumps(parity, indent=2) + "\n"
    )
    (destination / "results.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    (destination / "reporting_source.py").write_text(
        Path(__file__).read_text()
    )
    print(
        json.dumps(
            dict(
                directory=str(destination.relative_to(c.ROOT)), results=result
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
