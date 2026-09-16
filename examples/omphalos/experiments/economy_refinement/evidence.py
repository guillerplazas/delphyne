"""Offline campaign evidence: chronological audit, HTTP-blocked replay/export.

Both harnesses use `python -m experiments.economy_refinement.evidence`.
Only explicit registered trainX/validationX cells are opened. Reporting
code is separate from the frozen runtime; outputs bind it by source hash.
"""

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import datetime, timezone
import csv
import gzip
import io
import json
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command

from experiments import ace_economy_refinement_experiment as c
from experiments import ace_economy_session_experiment as session
from experiments import ace_economy_validation as reference
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.model_registry import price_tokens
from tools.analysis.replay_economy import own_receipts


def replay(batch: str) -> None:
    jobs = c.configs(batch)
    c.verify()
    if not (c.CAMPAIGN / f"batches/{batch}.json").exists():
        raise ValueError("Only completed batches can be replayed")
    destination = f"replays/{batch}.json"
    if (c.CAMPAIGN / destination).exists():
        saved = c.read(destination)
        if not saved["passed"] or saved["paid_calls"]:
            raise ValueError("Invalid replay certificate")
        if set(saved["result_hashes"]) != {c.name(j, None) for j in jobs}:
            raise ValueError("Replay cells changed")
        for job in jobs:
            path = c.directory(job) / "result.yaml"
            if c.sha(path) != saved["result_hashes"][c.name(job, None)]:
                raise ValueError("Measured result changed after replay")
        return
    before = own_receipts(c.CAMPAIGN)
    checks: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    for job in jobs:
        original = c.cell_result(job)
        ident = c.name(job, None)
        hashes[ident] = c.sha(c.directory(job) / "result.yaml")
        if original is None:
            checks.append(dict(cell=ident, platform_failed=True))
            continue
        c.activate(events=False)
        args = job.instantiate(None)
        args.cache_mode = "replay"
        args.cache_file = str(c.directory(job) / "cache.yaml")
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Replay forbids HTTP"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(c.context(), cache_root=Path("/")),
                add_header=False,
            )
        if (
            out.result is None
            or out.result.success != original["success"]
            or out.result.spent_budget != original["spent_budget"]
            or json.loads(json.dumps(list(out.result.values)))
            != original["values"]
        ):
            raise ValueError("Exact replay mismatch: " + ident)
        checks.append(dict(cell=ident, passed=True))
    if own_receipts(c.CAMPAIGN) != before:
        raise ValueError("Replay created a paid receipt")
    c.verify()
    c.save(
        destination,
        dict(passed=True, paid_calls=0, result_hashes=hashes, cells=checks),
    )
    print(
        json.dumps(dict(batch=batch, replayed=len(checks), paid_calls=0)),
        flush=True,
    )


def export() -> None:
    c.verify()
    account = c.accounting()
    if account["unresolved"] or account["billing_issues"]:
        raise ValueError("All billing must settle")
    batches = [
        b for b in c.BATCHES if (c.CAMPAIGN / f"batches/{b}.json").exists()
    ]
    jobs = [j for batch in batches for j in c.configs(batch)]
    cells = {c.name(j, None): j for j in jobs}
    if len(cells) != len(jobs):
        raise ValueError("Duplicate cell identity")
    with Ledger(c.CAMPAIGN / "ledger.sqlite3").connect() as db:
        rows = db.execute(
            "SELECT id,cell,model,created,status,charged,usage FROM receipts ORDER BY created,id"
        ).fetchall()
    receipts: list[dict[str, Any]] = []
    for ident, cell, model, created, status, charged, encoded in rows:
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
    if abs(sum(r["repriced"] for r in receipts) - account["total"]) > 1e-8:
        raise ValueError("Receipt export does not reconcile")
    destination = c.CAMPAIGN / "analysis"
    destination.mkdir(exist_ok=True)
    with (destination / "receipts.csv").open("w") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(receipts[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(receipts)
    archives: dict[str, Any] = {}
    outcomes: dict[str, Any] = {}
    for ident, job in cells.items():
        result = c.cell_result(job)
        outcomes[ident] = dict(
            success=bool(result and result["success"]),
            platform_failed=result is None,
            cost=account["costs"].get(ident, 0),
            values=result["values"] if result else [],
            spent_budget=result["spent_budget"] if result else None,
        )
        files = [
            c.directory(job) / filename
            for filename in ("result.yaml", "cache.yaml")
            if (c.directory(job) / filename).exists()
        ]
        files.extend((c.CAMPAIGN / "transport" / ident).glob("*.json.gz"))
        archives[ident] = {
            str(p.relative_to(c.ROOT)): c.sha(p) for p in sorted(files)
        }
    c.save(
        "analysis/archives.json",
        dict(
            authorized_partitions=["trainX", "validationX"],
            cells=archives,
            paid_calls=0,
            receipt_rows=len(receipts),
            total_cost=account["total"],
            receipts_sha256=c.sha(destination / "receipts.csv"),
            evidence_code_sha256=c.sha(Path(__file__)),
        ),
    )
    c.save("analysis/outcomes.json", outcomes)
    print(
        json.dumps(
            dict(
                cells=len(cells), receipts=len(receipts), cost=account["total"]
            )
        )
    )


def old_audit() -> None:
    """Audit first/last rendered requests, chronologically, in 400 old cells.

    This is a mechanism audit, not a token-cost estimator. Last requests
    need not contain all earlier history in a session-reset treatment.
    """
    session.verify()
    rows: list[dict[str, Any]] = []
    for module, batches in (
        (reference, ("baseline", "session", "views")),
        (session, ("validation",)),
    ):
        jobs = [j for b in batches for j in module.configs(b)]
        ids = {module.name(j, None) for j in jobs}
        requests: dict[str, list[str]] = defaultdict(list)
        for line in (module.CAMPAIGN / "events.jsonl").open():
            event = json.loads(line)
            if (
                event.get("cell") in ids
                and event.get("kind") == "transport"
                and event.get("decision") == "saved"
            ):
                requests[event["cell"]].append(event["request"])
        for job in jobs:
            ident = module.name(job, None)
            ordered = requests[ident]
            if not ordered:
                raise ValueError("Missing chronological transport events")
            loaded: list[dict[str, Any]] = []
            for key in (ordered[0], ordered[-1]):
                path = module.CAMPAIGN / "transport" / ident / f"{key}.json.gz"
                loaded.append(json.loads(gzip.decompress(path.read_bytes())))
            chat = loaded[-1]["request"]["request"]["chat"]
            goals: Counter[str] = Counter()
            queries: Counter[str] = Counter()
            clipped = prefix_chars = 0
            outcomes: Counter[str] = Counter()
            for msg in chat:
                if "call" in msg:
                    queries[json.dumps(msg["call"], sort_keys=True)] += 1
                text = msg.get("result", msg.get("content", ""))
                if not isinstance(text, str):
                    continue
                clipped += int("[view truncated;" in text)
                try:
                    data = json.loads(text)
                except ValueError:
                    continue
                if not isinstance(data, dict):
                    continue
                data = cast(dict[str, Any], data)
                goals.update(data.get("goals", []))
                prefix_chars += (
                    len(json.dumps(data.get("verified_prefix", [])))
                    if "verified_prefix" in data
                    else 0
                )
                if "outcome" in data:
                    outcomes[data["outcome"]] += 1
            rows.append(
                dict(
                    cell=ident,
                    arm=job.arm,
                    requests=len(ordered),
                    first_input=loaded[0]["response"]["budget"]["values"][
                        "input_tokens"
                    ],
                    last_input=loaded[-1]["response"]["budget"]["values"][
                        "input_tokens"
                    ],
                    duplicate_goal_chars=sum(
                        len(g) * (n - 1) for g, n in goals.items()
                    ),
                    repeated_tool_queries=sum(n - 1 for n in queries.values()),
                    clipped_messages=clipped,
                    verified_prefix_chars=prefix_chars,
                    observed_outcomes=dict(outcomes),
                )
            )
    totals: dict[str, Any] = {}
    for arm in sorted({r["arm"] for r in rows}):
        selected = [r for r in rows if r["arm"] == arm]
        totals[arm] = dict(
            cells=len(selected),
            **{
                key: sum(r[key] for r in selected)
                for key in (
                    "requests",
                    "duplicate_goal_chars",
                    "repeated_tool_queries",
                    "clipped_messages",
                    "verified_prefix_chars",
                )
            },
        )
    c.save(
        "failure_audit.json",
        dict(
            source_scope="400 prior validation-only cells, first/last requests in event order",
            interpretation="Repeated query text can be legitimate at changed proof states; these are mechanism counts, not bug labels. Final requests in reset arms omit dropped history.",
            findings=[
                "Old JSON feedback places full proof prefix before current goals; byte clipping can hide goals.",
                "Full goal states and checked proof prefixes recur in visible history.",
                "One-shot reset permits later history regrowth; the refined drop permits two bounded resets.",
                "A smaller per-message cap can induce more requests; total charged cost and coverage are primary.",
                "No handoff, memory or extra tool is introduced; playbook remains frozen.",
            ],
            totals=totals,
            cells=rows,
            evidence_code_sha256=c.sha(Path(__file__)),
        ),
    )
    print(json.dumps(totals, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("replay", "export", "audit-old"))
    parser.add_argument("batches", nargs="*")
    args = parser.parse_args()
    if args.action == "replay":
        for batch in args.batches:
            replay(batch)
    elif args.action == "export":
        export()
    else:
        old_audit()


if __name__ == "__main__":
    main()
