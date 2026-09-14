"""Offline, development-only exports of the registered snippet campaign.

No selection, API calls, new Rocq runs or changes to frozen measurements.
Both harnesses: python -m tools.reports.snippet_results
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from collections import defaultdict
from dataclasses import asdict
import csv
import gzip
import io
import json
from pathlib import Path
from typing import Any

import yaml

from experiments import snippet_experiment as c
from experiments.resource_completion_experiment import token_summary
from ace.ace_grounded import failure_category


def table(name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    stream = io.StringIO()
    writer = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path = c.CAMPAIGN / name
    if path.exists():
        assert path.read_text() == stream.getvalue(), "Frozen export drift"
    else:
        path.write_text(stream.getvalue())


def cache_tokens(path: Path) -> dict[str, int]:
    total = dict(input=0, cached=0, output=0)
    entries: list[dict[str, Any]] = yaml.load(
        path.read_text(), Loader=yaml.CSafeLoader
    )
    for entry in entries:
        if entry["input"]["request"]["options"].get("model") == "__compute__":
            continue
        output: dict[str, Any] = entry.get("output") or {}
        usage: dict[str, Any] = output.get("budget", {}).get("values", {})
        for key, field in (
            ("input", "input_tokens"),
            ("cached", "cached_input_tokens"),
            ("output", "output_tokens"),
        ):
            total[key] += int(usage.get(field, 0))
    return total


def main() -> None:
    c.verify()
    acct = c.accounting()
    assert c.read("final_accounting.json") == acct
    grouped_events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in c.events():
        grouped_events[event.get("cell", "")].append(event)
    cells: list[dict[str, Any]] = []
    requests: list[dict[str, Any]] = []
    writers: list[dict[str, Any]] = []
    snippet_receipts: list[dict[str, Any]] = []
    book = (
        c.Playbook.load(c.CAMPAIGN / "book.yaml").render_prompt()
        if (c.CAMPAIGN / "book.yaml").exists()
        else ""
    )
    manifest_cells: set[str] = set()
    for path in sorted((c.CAMPAIGN / "manifests").glob("*.json")):
        key = path.stem
        assert c.read(f"replays/{key}.json")["passed"]
        for cfg in c.configs(key):
            cell = c.name(cfg, None)
            assert cell not in manifest_cells
            manifest_cells.add(cell)
            result = c.cell_result(cfg)
            cost = acct["costs"].get(cell, 0.0)
            tokens = acct["tokens"].get(cell, {})
            token_cost = token_summary([tokens])["dated_tariff_cost"]
            assert abs(cost - token_cost) < 1e-8
            cache = c.directory(cfg) / "cache.yaml"
            if cache.exists():
                assert cache_tokens(cache) == dict(
                    input=tokens.get("input", 0),
                    cached=tokens.get("cached", 0),
                    output=tokens.get("output", 0),
                ), cell
                entries: list[dict[str, Any]] = yaml.load(
                    cache.read_text(), Loader=yaml.CSafeLoader
                )
                for entry in entries:
                    request = entry["input"]["request"]
                    if request["options"].get("model") != "__compute__":
                        continue
                    call = yaml.safe_load(request["chat"][-1]["content"])
                    if call.get("fun") != "check_snippet":
                        continue
                    checked = yaml.safe_load(
                        entry["output"]["outputs"][0]["content"]
                    )
                    feedback = checked["checked"]["feedback"]
                    snippet_receipts.append(
                        dict(
                            cell=cell,
                            call=call,
                            receipt=checked,
                            error_category=failure_category(
                                feedback.get("error_message") or ""
                            ),
                        )
                    )
            events = grouped_events[cell]
            checks = [e for e in events if e["kind"] == "snippet"]
            invoked = [
                e
                for e in events
                if e["kind"] == "model" and e["decision"] == "invoked"
            ]
            advertised = book_requests = 0
            snippet_calls: list[str] = []
            for snapshot in (c.CAMPAIGN / "transport" / cell).glob(
                "*.json.gz"
            ):
                raw = json.loads(gzip.decompress(snapshot.read_bytes()))
                for output in raw["response"]["outputs"]:
                    for call in output.get("tool_calls", []):
                        if call["name"] == "CheckRocqSnippet":
                            snippet_calls.append(
                                json.dumps(call["args"], sort_keys=True)
                            )
                request: dict[str, Any] = raw["request"]["request"]
                tool_schemas: list[dict[str, Any]] = request["tools"] or []
                advertised += any(
                    t["name"] == "CheckRocqSnippet" for t in tool_schemas
                )
                book_requests += bool(book) and any(
                    book in (m.get("content") or "") for m in request["chat"]
                )
            if cfg.arm == "B":
                assert book_requests > 0, (
                    "B book never reached a dispatched request"
                )
            cells.append(
                dict(
                    cell=cell,
                    theorem=cfg.bench_name,
                    stage=cfg.stage,
                    arm=cfg.arm,
                    seed=cfg.seed,
                    success=bool(result and result["success"]),
                    qualified_solve=bool(
                        cfg.stage != "writing"
                        and result
                        and result["success"]
                        and cost <= cfg.dollar_cap + 1e-12
                    ),
                    platform_failed=result is None,
                    cost=cost,
                    input_tokens=tokens.get("input", 0),
                    cached_input_tokens=tokens.get("cached", 0),
                    output_tokens=tokens.get("output", 0),
                    model_requests=len(invoked),
                    tool_advertised_requests=advertised,
                    real_snippet_checks=sum(
                        e.get("rpc_calls", 0) > 0 for e in checks
                    ),
                    snippet_rejected=sum(
                        e["decision"] == "rejected" for e in checks
                    ),
                    snippet_open=sum(
                        e["decision"] == "executed_open" for e in checks
                    ),
                    snippet_completed=sum(
                        e["decision"] == "completed" for e in checks
                    ),
                    snippet_resource_exhausted=sum(
                        e["decision"] == "resource_exhausted" for e in checks
                    ),
                    snippet_unknown=sum(
                        e["decision"] == "unknown" for e in checks
                    ),
                    snippet_reused=len(snippet_calls)
                    - len(set(snippet_calls)),
                    snippet_requests=len(snippet_calls),
                    actual_book_requests=book_requests
                    if cfg.arm == "B"
                    else 0,
                    source=str(c.directory(cfg).relative_to(c.ROOT)),
                )
            )
            settled = {
                e["receipt"]: e
                for e in events
                if e["kind"] == "model" and e["decision"] == "settled"
            }
            for i, event in enumerate(invoked, 1):
                response = settled[event["receipt"]]
                requests.append(
                    dict(
                        cell=cell,
                        request=i,
                        receipt=event["receipt"],
                        output_limit=event["output_limit"],
                        reserved_bound=event["estimate_dollars"],
                        charged=response["dollars"],
                        truncated=response["truncated"],
                        rejected=False,
                    )
                )
            if cfg.stage == "writing":
                product = c.product(cfg)
                writers.append(
                    dict(
                        cell=cell,
                        role=cfg.role,
                        complete=product is not None,
                        retained=list(product.answer.retained_receipts)
                        if product
                        else [],
                        dropped=list(product.answer.dropped_receipts)
                        if product
                        else [],
                        operations=len(product.delta.operations)
                        if product
                        else 0,
                        receipts=[asdict(r) for r in product.receipts]
                        if product
                        else [],
                    )
                )
    repair = c.read("transport_repair.json")
    receipt = repair["original_receipt"]
    requests.append(
        dict(
            cell=repair["canonical_cell"],
            request=0,
            receipt=receipt["id"],
            output_limit=32768,
            reserved_bound=receipt["reserved"],
            charged=0.0,
            truncated=False,
            rejected=True,
        )
    )
    with (c.CAMPAIGN / "receipts.csv").open() as stream:
        receipts = list(csv.DictReader(stream))
    assert (
        len(requests) == len(receipts) == len({r["receipt"] for r in requests})
    )
    assert {r["receipt"] for r in requests} == {r["id"] for r in receipts}
    assert abs(sum(r["cost"] for r in cells) - acct["new_total"]) < 1e-8
    assert abs(sum(r["charged"] for r in requests) - acct["new_total"]) < 1e-8
    summaries: dict[str, Any] = {}
    for group in sorted(
        {
            r["stage"] + "/" + (r["arm"] if r["stage"] != "writing" else "all")
            for r in cells
        }
    ):
        stage, arm = group.split("/")
        rows = [
            r
            for r in cells
            if r["stage"] == stage and (arm == "all" or r["arm"] == arm)
        ]
        solved = sum(r["qualified_solve"] for r in rows)
        total = sum(r["cost"] for r in rows)
        summaries[group] = dict(
            cells=len(rows),
            solved=solved,
            cost=total,
            cost_per_qualified_solve=total / solved if solved else None,
            platform_failed=sum(r["platform_failed"] for r in rows),
            tool_exposed_cells=sum(r["real_snippet_checks"] > 0 for r in rows),
            tool_totals={
                k: sum(r[k] for r in rows)
                for k in rows[0]
                if k.startswith("snippet_")
                or k
                in (
                    "real_snippet_checks",
                    "tool_advertised_requests",
                    "model_requests",
                )
            },
            pricing=token_summary(
                [acct["tokens"].get(r["cell"], {}) for r in rows]
            ),
        )
    reference_tokens: dict[str, Any] = {}
    for stage, refs in c.read("references.json").items():
        tokens = {
            r["theorem"]: cache_tokens(
                c.ROOT / r["source"] / "configs" / r["name"] / "cache.yaml"
            )
            for r in refs
        }
        reference_tokens[stage] = dict(
            cells=tokens, pricing=token_summary(list(tokens.values()))
        )
    table("cells.csv", cells)
    table("requests.csv", requests)
    c.save("mechanism_summary.json", summaries)
    c.save("writer_provenance.json", writers)
    c.save("snippet_receipts.json", snippet_receipts)
    c.save("reference_tokens.json", reference_tokens)
    c.save(
        "export_verification.json",
        dict(
            complete=True,
            cells=len(cells),
            model_requests=len(requests),
            new_spending=acct["new_total"],
            cumulative=acct["cumulative"],
            unknown_charges=acct["unresolved"],
            platform_failures=sum(r["platform_failed"] for r in cells),
            setup_failure_jobs=44,
            setup_failure_proof_denominator=40,
            setup_failure_proof_solves=0,
            setup_failure_charge=0,
            setup_failure_record="setup_failure_01/RESULTS.md",
            paid_retries=0,
            zero_charge_request_retries=1,
            all_required_panels_replayed=True,
            receipts_and_tokens_reconcile=True,
            repeated_request_count_source="Unique transport snapshots; strategy reused events can recur during tree reconstruction",
            source_seal_verified=True,
            reference_replay="60 observed-request replays; historical terminal admission not reconstructed",
        ),
    )
    paths = [
        *c.OUTPUT.rglob("result.yaml"),
        *c.OUTPUT.rglob("cache.yaml"),
        *(c.CAMPAIGN / "transport").rglob("*.json.gz"),
        c.CAMPAIGN / "events.jsonl",
        c.CAMPAIGN / "receipts.csv",
    ]
    c.save(
        "output_inventory.json",
        {str(p.relative_to(c.ROOT)): c.sha(p) for p in sorted(paths)},
    )
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
