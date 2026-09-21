"""Compact review bundle and hash inventory of retained local evidence.

This inventories only the new campaign and the explicitly scoped historical
census. It never walks other campaign trees or closed benchmark partitions.
"""

import csv
import json
from pathlib import Path
import sqlite3
from typing import Any

from .common import CAMPAIGN, OUTPUT, REPORT, ROOT, allowed, read, save, sha
from .economics import ledger_rows, paid
from .reporting import inputs
from .study_certification import batches


def record(path: Path) -> dict[str, Any]:
    return dict(
        path=str(path.relative_to(ROOT)),
        bytes=path.stat().st_size,
        sha256=sha(path),
    )


def compact_inventory(*, checkpoint: bool = False) -> list[Path]:
    package = ROOT / "experiments/ace_independent_audit"
    files = [
        *package.glob("*.py"),
        *package.glob("*.lua"),
        *package.glob("*.sh"),
        package / "README.md",
        *package.glob("templates/*.jinja"),
    ]
    excluded = {
        "artifact_manifest.json",
        "review_files.json",
        "raw_cells.jsonl",
        "exception_cells.jsonl",
        "ace_paper.txt",
        "typecheck_project.json",
    }
    if checkpoint:
        excluded.update(
            {
                "checkpoint_artifact_manifest.json",
                "checkpoint_review_files.json",
            }
        )
    files += [
        p
        for p in REPORT.iterdir()
        if p.is_file()
        and p.suffix in (".md", ".json", ".csv", ".pdf", ".jsonl")
        and p.name not in excluded
    ]
    files += [
        p
        for p in (REPORT / "figures").iterdir()
        if p.suffix in (".md", ".png", ".svg", ".pdf")
    ]
    files += list(CAMPAIGN.glob("*.json"))
    files += list((CAMPAIGN / "batch_sources").glob("*.json"))
    files += list((CAMPAIGN / "batches").glob("*.json"))
    files += list((CAMPAIGN / "terminal_failures").glob("*.json"))
    files += list((CAMPAIGN / "dispatch_history").glob("*.json"))
    files += list((CAMPAIGN / "quota_recovery").glob("*.json"))
    files += list((CAMPAIGN / "rate_recovery").glob("*.json"))
    files += list((CAMPAIGN / "rate_recovery/concurrent").glob("*.json"))
    files += list((CAMPAIGN / "rate_recovery/concurrent").glob("*.py"))
    files += list((CAMPAIGN / "rate_recovery/certificates").glob("*.json"))
    files += list((CAMPAIGN / "rate_recovery/cells").glob("*/*.json"))
    files += [
        p
        for name in (
            "bounded_timeout_preparation.json",
            "bounded_timeout_approval.json",
            "original_pause.json",
            "authorization_clarification.json",
            "applied_analysis_check.json",
        )
        if (p := CAMPAIGN / "billing_recovery" / name).exists()
    ]
    for name in (
        "checkpoint_review_snapshot.tar.gz",
        "credit_checkpoint_reports.tar.gz",
    ):
        snapshot = REPORT / name
        if snapshot.exists():
            files.append(snapshot)
    for name in (
        "A1_historical.json",
        "A2_frozen.json",
        "S1_frozen.json",
        "B1_frozen.json",
        "B2_frozen.json",
        "R1_verified_rules.json",
        "O1_adaptive_frozen.json",
    ):
        path = CAMPAIGN / "books" / name
        if not checkpoint or path.exists():
            files.append(path)
    for prefix in ("ladder", "ladder_v2"):
        for model in ("luna", "terra", "sol", "astra"):
            for effort in ("medium", "high"):
                files.append(
                    CAMPAIGN / "books" / f"{prefix}__{model}_{effort}.json"
                )
    files += [
        ROOT / filename
        for filename in (
            "runtime/model_registry.py",
            "pyrightconfig.json",
            "experiments/ace/ace_attribution_experiment.py",
            "tests/test_ace_driver.py",
        )
    ]
    return sorted(set(files))


def raw_inventory(
    *,
    completed_batches: list[str] | None = None,
    ledger_name: str = "ledger_final.sqlite3",
    index_name: str = "raw_artifact_hashes.jsonl",
) -> dict[str, Any]:
    target = REPORT / index_name
    total = 0
    counts: dict[str, int] = {}
    seen: set[Path] = set()
    with target.open("w") as stream:

        def add(path: Path, category: str) -> None:
            nonlocal total
            if path in seen:
                return
            seen.add(path)
            value = dict(record(path), category=category)
            stream.write(json.dumps(value, sort_keys=True) + "\n")
            total += value["bytes"]
            counts[category] = counts.get(category, 0) + 1

        # The census itself contains per-cell historical result/cache hashes.
        # Do not rediscover any old archive paths here.
        for name in ("raw_cells.jsonl", "exception_cells.jsonl"):
            add(REPORT / name, "scoped_historical_census")
        for _, problem in allowed().values():
            add(ROOT / problem, "allowed_statement")
        for batch in (
            batches() if completed_batches is None else completed_batches
        ):
            for job in read(CAMPAIGN / "batches" / (batch + ".json")):
                identity = (
                    f"{job['stage']}__{job['arm']}__{job['theorem']}"
                    f"__seed{job['seed']}"
                )
                filenames = ("cache.yaml", "result.yaml")
                if (
                    CAMPAIGN / "terminal_failures" / (identity + ".json")
                ).exists():
                    filenames = ("cache.yaml", "exception.txt")
                elif job.get("robust", False):
                    filenames += ("completed.json",)
                for name in filenames:
                    add(OUTPUT / batch / "configs" / identity / name, "solver")
        # Include author/teacher execution caches and launcher completion
        # state as well. This is only the newly scoped campaign tree.
        for path in sorted(OUTPUT.rglob("*")):
            if path.is_file() and path.suffix in (
                ".json",
                ".yaml",
                ".yml",
                ".txt",
            ):
                add(path, "execution_auxiliary")
        for folder in (
            "responses",
            "transport",
            "role_inputs",
            "role_sources",
            "role_batches",
            "learning_events",
            "online_events",
            "online_scores",
            "evidence",
            "verification",
            "verification_returned",
            "budget_replay",
            "books",
            "kernel",
            "rule_probes",
            "learning_cache",
            "terminal_failures",
            "billing_recovery",
            "provider_retrieval",
            "quota_recovery",
            "rate_recovery",
        ):
            for path in sorted((CAMPAIGN / folder).rglob("*")):
                if path.is_file() and path.suffix in (
                    ".json",
                    ".jsonl",
                    ".gz",
                    ".v",
                    ".yaml",
                    ".txt",
                ):
                    add(path, folder)
        for path in sorted((CAMPAIGN / "incidents").rglob("*")):
            if path.is_file() and path.suffix in (
                ".json",
                ".yaml",
                ".txt",
                ".log",
                ".md",
            ):
                add(path, "preserved_incidents")
        add(ROOT / "papers/2510.04618v3.pdf", "reference_paper")
        add(CAMPAIGN / ledger_name, "accounted_ledger_snapshot")
    return dict(
        files=len(seen), bytes=total, categories=counts, index=record(target)
    )


def checkpoint() -> None:
    from .checkpoint import assert_quiet

    assert_quiet()
    results = read(REPORT / "checkpoint_results.json")
    if not read(REPORT / "checkpoint_receipt_certification.json")["passed"]:
        raise ValueError("Checkpoint receipt certification is missing")
    for filename in ("long_report.md", "short_report.md"):
        if not (REPORT / filename).exists():
            raise ValueError("The checkpoint reports have not been assembled")
    rows = ledger_rows()
    backup = CAMPAIGN / "ledger_checkpoint.sqlite3"
    if not backup.exists():
        with (
            sqlite3.connect(
                f"file:{CAMPAIGN / 'ledger.sqlite3'}?mode=ro", uri=True
            ) as original,
            sqlite3.connect(backup) as copy,
        ):
            original.backup(copy)
    with (REPORT / "checkpoint_settled_receipts.csv").open(
        "w", newline=""
    ) as stream:
        keys = ("id", "cell", "stage", "model", "created", "charged", "status")
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows({k: r[k] for k in keys} for r in rows)
    raw = raw_inventory(
        completed_batches=results["closed_batches"],
        ledger_name="ledger_checkpoint.sqlite3",
        index_name="checkpoint_raw_artifact_hashes.jsonl",
    )
    files = compact_inventory(checkpoint=True)
    records = [record(path) for path in files]
    save(
        REPORT / "checkpoint_artifact_manifest.json",
        dict(
            review_files=records,
            review_bytes=sum(r["bytes"] for r in records),
            local_raw_evidence=raw,
            completed_solver_cells=results["completed_solver_cells"],
            registered_solver_cells=results["registered_solver_cells"],
            note="User-requested checkpoint. Every launched batch finished; remaining batches are held, not failed. The compact review bundle is staged; the large raw corpus and settled ledger snapshot remain local under the recorded paths and hashes. This is not the full-study certification. No closed partition is included or read.",
        ),
    )
    save(
        REPORT / "checkpoint_review_files.json",
        [
            str(p.relative_to(ROOT))
            for p in files
            + [
                REPORT / "checkpoint_artifact_manifest.json",
                REPORT / "checkpoint_review_files.json",
            ]
        ],
    )
    print(
        json.dumps(
            dict(
                review_files=len(files) + 2,
                review_bytes=sum(r["bytes"] for r in records),
                raw_files=raw["files"],
                raw_bytes=raw["bytes"],
                checkpoint=True,
            )
        )
    )


def run() -> None:
    inputs()
    if not read(REPORT / "receipt_certification.json")["passed"]:
        raise ValueError("Receipt certification is missing")
    if read(REPORT / "budget_replay_results.json")["scenarios"] != 4560:
        raise ValueError("Budget experiment is incomplete")
    for filename in ("long_report.md", "short_report.md"):
        if not (REPORT / filename).exists():
            raise ValueError("The final reports have not been assembled")
    rows = ledger_rows()
    accounting = paid(rows)
    backup = CAMPAIGN / "ledger_final.sqlite3"
    if not backup.exists():
        with (
            sqlite3.connect(
                f"file:{CAMPAIGN / 'ledger.sqlite3'}?mode=ro", uri=True
            ) as original,
            sqlite3.connect(backup) as copy,
        ):
            original.backup(copy)
    with (REPORT / "accounted_receipts.csv").open("w", newline="") as stream:
        keys = (
            "id",
            "cell",
            "stage",
            "model",
            "created",
            "charged",
            "reserved",
            "status",
        )
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows({k: r[k] for k in keys} for r in rows)
    raw = raw_inventory()
    files = compact_inventory()
    records = [record(path) for path in files]
    save(
        REPORT / "artifact_manifest.json",
        dict(
            review_files=records,
            review_bytes=sum(r["bytes"] for r in records),
            local_raw_evidence=raw,
            receipt_accounting=accounting,
            ledger_csv_note="The status column distinguishes exact settled charges from an explicitly approved bounded liability. A bounded row's charged column retains the reservation for capacity accounting, not an exact invoice.",
            note="The compact review bundle is staged without the multi-gigabyte raw cache/response corpus. That corpus remains locally available under the recorded paths and hashes. Historical individual result/cache hashes are inside the independently scoped raw census. No closed partition is included or read by this inventory.",
        ),
    )
    save(
        REPORT / "review_files.json",
        [
            str(p.relative_to(ROOT))
            for p in files
            + [REPORT / "artifact_manifest.json", REPORT / "review_files.json"]
        ],
    )
    print(
        json.dumps(
            dict(
                review_files=len(files) + 2,
                review_bytes=sum(r["bytes"] for r in records),
                raw_files=raw["files"],
                raw_bytes=raw["bytes"],
            )
        )
    )


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["checkpoint"]:
        checkpoint()
    elif not sys.argv[1:]:
        run()
    else:
        raise SystemExit("Use no argument for final bundle, or checkpoint")
