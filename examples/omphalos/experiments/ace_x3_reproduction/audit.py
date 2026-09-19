"""Read-only reconstruction from explicitly permitted cells and receipts."""

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import sqlite3
from typing import Any

import openai

from experiments.ace_sanitized.scope import partition
from experiments.ace_thesis import campaign as old
from runtime.replay_admission import fingerprint
from tools.reports.ace_x3_forensics import HISTORY, LEDGERS, raw
from tools.reports.ace_thesis import export_csv

from . import campaign as c
from .accounting import price


def receipts(ledger: Path, cell: str) -> list[dict[str, Any]]:
    with sqlite3.connect(f"file:{ledger}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute(
            "SELECT * FROM receipts WHERE cell=? ORDER BY created,id", (cell,)
        ).fetchall()
    answer: list[dict[str, Any]] = []
    for row in rows:
        row = dict(row)
        usage = json.loads(row.pop("usage"))
        if row["status"] != "settled":
            raise ValueError("Unresolved receipt: " + row["id"])
        assumptions: list[str] = []
        rejected_zero = (
            usage.get("http_status") == 400
            and usage.get("input_tokens") == usage.get("output_tokens") == 0
            and usage.get("reconciled_exception") == "BadRequestError"
        )
        if "input_tokens" not in usage or rejected_zero:
            if row["charged"] != 0 or not (
                "exception" in usage or usage.get("rejected") or rejected_zero
            ):
                raise ValueError("Missing billing usage")
            costs = dict.fromkeys(
                (
                    "input",
                    "cached",
                    "written",
                    "output",
                    "ordinary",
                    "legacy",
                    "corrected",
                    "no_cache_fixed_trace",
                    "write_premium",
                ),
                0,
            )
        else:
            if "service_tier" not in usage:
                assumptions.append(
                    "Standard tier assumed: absent in original ledger"
                )
            if "endpoint" not in usage:
                assumptions.append(
                    "Nonregional endpoint assumed: absent in original ledger"
                )
            costs = price(
                usage,
                model=usage.get("model", row["model"]),
                on=datetime.fromtimestamp(row["created"], timezone.utc).date(),
                tier=usage.get("service_tier", "default"),
                regional="endpoint" in usage
                and usage["endpoint"] != "https://api.openai.com/v1/",
            ).as_dict()
        recorded_formula = (
            "corrected"
            if ledger == c.CAMPAIGN / "ledger.sqlite3"
            else "legacy"
        )
        if abs(costs[recorded_formula] - row["charged"]) > 1e-9:
            raise ValueError("Ledger/formula mismatch: " + row["id"])
        answer.append(
            dict(
                **row,
                **costs,
                assumptions=assumptions,
                usage=usage,
                ledger=str(ledger.relative_to(c.ROOT)),
            )
        )
    return answer


def prior_accounting() -> dict[str, Any]:
    rows = [
        r
        for j in old.all_jobs()
        for r in receipts(old.CAMPAIGN / "ledger.sqlite3", old.name(j, None))
    ]
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate prior receipt")
    with sqlite3.connect(
        f"file:{old.CAMPAIGN / 'ledger.sqlite3'}?mode=ro", uri=True
    ) as db:
        count = db.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
    if count != len(rows):
        raise ValueError("Prior authorization includes unaccounted receipts")
    return dict(
        receipts=len(rows),
        **{
            k: sum(r[k] for r in rows)
            for k in ("legacy", "corrected", "written", "write_premium")
        },
        unresolved=0,
        assumption="Standard nonregional tariff where original transport omitted metadata; not invoice verification",
        ledger_sha256=c.sha(old.CAMPAIGN / "ledger.sqlite3"),
    )


def historical_cells() -> list[dict[str, Any]]:
    allowed = partition("validation")
    comparison = old.read(HISTORY)[0]
    if comparison["label"] != "attribution_X3":
        raise ValueError("Historical comparison changed")
    result: list[dict[str, Any]] = []
    for arm, ledger_name in LEDGERS.items():
        paths = comparison["source_paths_" + arm.removesuffix("_seed1")]
        if arm == "b_seed1":
            paths = [p.removesuffix("__seed0") + "__seed1" for p in paths]
        seen: set[str] = set()
        for relative in paths:
            if not any("/" + n + "__" in relative for n in allowed):
                raise ValueError("Cell outside validation allowlist")
            record = old.read("audit/cells/" + fingerprint(relative) + ".json")
            if record["theorem"] not in allowed or record["theorem"] in seen:
                raise ValueError("Unauthorized or duplicate cell")
            seen.add(record["theorem"])
            folder = c.ROOT / relative
            for name, expected in record["hashes"].items():
                if c.sha(folder / name) != expected:
                    raise ValueError("Archive bytes changed")
            result.append(
                dict(
                    label={
                        "a": "historical_none",
                        "b": "historical_x3_seed0",
                        "b_seed1": "historical_x3_seed1",
                    }[arm],
                    path=relative,
                    theorem=record["theorem"],
                    seed=record["seed"],
                    ledger=str(
                        c.ROOT
                        / "experiments/campaigns"
                        / ledger_name
                        / "ledger.sqlite3"
                    ),
                    cell=folder.name,
                    record=record,
                )
            )
        if seen != set(allowed):
            raise ValueError("Incomplete historical panel")
    return result


def fresh_cells() -> list[dict[str, Any]]:
    return [
        dict(
            label="previous_" + j.arm,
            path=str(old.directory(j).relative_to(c.ROOT)),
            theorem=j.theorem,
            seed=str(j.seed),
            ledger=str(old.CAMPAIGN / "ledger.sqlite3"),
            cell=old.name(j, None),
        )
        for j in old.jobs("validation")
    ]


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return dict(
        cells=len(rows),
        solved=sum(r["solved"] for r in rows),
        qualified=sum(
            r["solved"] and r["corrected"] <= 0.1 + 1e-9 for r in rows
        ),
        **{
            k: sum(r[k] for r in rows)
            for k in (
                "legacy",
                "corrected",
                "input",
                "cached",
                "written",
                "output",
                "requests",
                "no_cache_fixed_trace",
                "write_premium",
            )
        },
    )


def audit() -> None:
    selected = historical_cells() + fresh_cells()
    cells: list[dict[str, Any]] = []
    paid: list[dict[str, Any]] = []
    for item in selected:
        folder = c.ROOT / item["path"]
        rows = receipts(Path(item["ledger"]), item["cell"])
        cache = raw(folder / "cache.yaml")
        llm = [
            r
            for r in cache
            if r["input"]["request"]["options"].get("model") != "__compute__"
        ]
        cache_legacy = sum(
            r["output"].get("budget", {}).get("values", {}).get("price", 0)
            for r in llm
        )
        if abs(cache_legacy - sum(r["legacy"] for r in rows)) > 1e-9:
            raise ValueError("Paid/cache discrepancy: " + item["path"])
        result_path = folder / "result.yaml"
        result = (
            raw(result_path).get("outcome", {}).get("result")
            if result_path.exists()
            else None
        )
        row = dict(
            label=item["label"],
            theorem=item["theorem"],
            seed=item["seed"],
            path=item["path"],
            cell=item["cell"],
            solved=bool(result and result["success"]),
            requests=len(rows),
            failed=result is None,
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
        cells.append(row)
        paid.extend(
            dict(
                **r,
                label=item["label"],
                theorem=item["theorem"],
                seed=item["seed"],
            )
            for r in rows
        )
    if len({(r["ledger"], r["id"]) for r in paid}) != len(paid):
        raise ValueError("Double-counted historical receipt")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in cells:
        groups[row["label"]].append(row)
    result = dict(
        groups={label: aggregate(rows) for label, rows in groups.items()},
        prior=prior_accounting(),
        cells=len(cells),
        receipts=len(paid),
        limitations="Original ledgers omit service tier and endpoint. Reconstructed Standard/nonregional tariff; GET retrieval may resolve tier. Cache repricing holds observed traces fixed and is not a no-cache experiment.",
    )
    c.save("audit/accounting.json", result)
    c.save("audit/cells.json", cells)
    c.save("audit/receipts.json", paid)
    export_csv(c.CAMPAIGN / "audit/cells.csv", cells)
    export_csv(
        c.CAMPAIGN / "audit/receipts.csv",
        [{k: v for k, v in r.items() if k != "usage"} for r in paid],
    )
    print(json.dumps(result, indent=2))


def retrieve() -> None:
    """GET only the 1,410 historical response IDs; never create a response."""
    entries = [
        r
        for r in c.read("audit/receipts.json")
        if r["label"].startswith("historical_")
    ]
    destination = c.CAMPAIGN / "retrieved"
    destination.mkdir(parents=True, exist_ok=True)

    def one(row: dict[str, Any]) -> dict[str, Any]:
        ident = row["usage"]["response_id"]
        path = destination / (row["id"] + ".json.gz")
        if path.exists():
            with gzip.open(path, "rt") as stream:
                return json.load(stream)
        value: dict[str, Any] = dict(
            receipt=row["id"], response_id=ident, cell=row["cell"]
        )
        try:
            with openai.OpenAI(max_retries=0, timeout=30) as client:
                response = client.responses.retrieve(ident)
                value.update(
                    retrieved=True,
                    response=response.to_dict(),
                    endpoint=str(client.base_url),
                )
        except Exception as exc:
            value.update(
                retrieved=False,
                exception=type(exc).__name__,
                status=getattr(exc, "status_code", None),
            )
        with gzip.open(path, "xt") as stream:
            json.dump(value, stream, sort_keys=True)
        return value

    with ThreadPoolExecutor(max_workers=8) as pool:
        values = list(pool.map(one, entries))
    c.save(
        "audit/retrieval.json",
        dict(
            cells=120,
            requests=len(values),
            new_inference_requests=0,
            retrieved=sum(v["retrieved"] for v in values),
            errors=dict(
                Counter(
                    v.get("exception") for v in values if not v["retrieved"]
                )
            ),
            tiers=dict(
                Counter(
                    v["response"].get("service_tier")
                    for v in values
                    if v["retrieved"]
                )
            ),
            models=dict(
                Counter(
                    v["response"].get("model")
                    for v in values
                    if v["retrieved"]
                )
            ),
            files_sha256={
                p.name: c.sha(p) for p in sorted(destination.glob("*.json.gz"))
            },
        ),
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in c.read("audit/retrieval.json").items()
                if k != "files_sha256"
            }
        )
    )


def other_retrospectives() -> None:
    """Correct the other published comparisons without conflating books."""
    from .report import comparisons

    results: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    for comparison in old.read(HISTORY)[1:]:
        paired: list[dict[str, Any]] = []
        try:
            for arm in ("a", "b"):
                for relative in comparison["source_paths_" + arm]:
                    if not any(
                        "__" + n + "__" in relative
                        for n in partition("validation")
                    ):
                        raise ValueError("Retrospective source outside scope")
                    record = old.read(
                        "audit/cells/" + fingerprint(relative) + ".json"
                    )
                    if record["theorem"] not in partition("validation"):
                        raise ValueError("Retrospective theorem outside scope")
                    folder = c.ROOT / relative
                    for name, digest in record["hashes"].items():
                        if c.sha(folder / name) != digest:
                            raise ValueError("Historical source drift")
                    ledger = (
                        c.ROOT
                        / "experiments/campaigns"
                        / record["campaign"]
                        / "ledger.sqlite3"
                    )
                    paid = receipts(ledger, folder.name)
                    if not paid:
                        raise ValueError("No exact-cell billing evidence")
                    paired.append(
                        dict(
                            label=arm,
                            theorem=record["theorem"],
                            seed=str(record["seed"]),
                            path=relative,
                            book_sha256=record["book_sha256"],
                            solved=record["solved"],
                            failed=record["status"] == "failed",
                            corrected=sum(r["corrected"] for r in paid),
                            legacy=sum(r["legacy"] for r in paid),
                            receipts=len(paid),
                        )
                    )
            result = comparisons(paired, [("a", "b")])["a__vs__b"]
            results.append(
                dict(
                    label=comparison["label"],
                    **result,
                    book_sha256=sorted(
                        {r["book_sha256"] for r in paired if r["label"] == "b"}
                    ),
                    status="reconstructed",
                    metadata_assumption="Standard nonregional tariff; historical ledger omits metadata",
                )
            )
            cells.extend(
                dict(**r, comparison=comparison["label"]) for r in paired
            )
        except ValueError as exc:
            results.append(
                dict(
                    label=comparison["label"],
                    status="unresolved",
                    reason=str(exc),
                )
            )
    c.save(
        "audit/other_retrospectives.json",
        dict(
            results=results,
            cells=cells,
            limitation="Different ACE book or history controls; these are not replications of original X3. Retrospective comparisons share cells and are not independent experiments.",
        ),
    )
    print(
        json.dumps(
            [
                {
                    k: r[k]
                    for k in ("label", "status", "saving_percent", "reason")
                    if k in r
                }
                for r in results
            ]
        )
    )
