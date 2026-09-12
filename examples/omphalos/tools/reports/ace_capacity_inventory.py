"""Verify explicit experiment records, reconcile receipts and hash artifacts."""

# ruff: noqa: E402
from runtime.development_only import install

install()

from collections import Counter
import csv
import json
from pathlib import Path
import sqlite3
from typing import Any

from experiments.ace import ace_capacity_experiment as c


SOURCE_FILES = (
    "runtime/replay_admission.py",
    "ace/ace_goal_visibility.py",
    "ace/ace_verified_snippets.py",
    "prove_grounded.py",
    "prove_capacity.py",
    "experiments/ace/ace_capacity_experiment.py",
    "tests/test_ace_capacity.py",
    "tools/reports/ace_capacity_preflight.py",
    "tools/reports/ace_capacity_report.py",
    "tools/reports/ace_capacity_replay.py",
    "tools/reports/ace_capacity_quality.py",
    "tools/reports/ace_capacity_synthesis.py",
    "tools/reports/ace_capacity_plots.py",
    "tools/reports/ace_capacity_inventory.py",
)


def hashes(paths: list[Path]) -> dict[str, Any]:
    return {
        str(p.relative_to(c.ROOT)): dict(
            sha256=c.old.digest(p), bytes=p.stat().st_size
        )
        for p in sorted(set(paths))
        if p.is_file()
    }


def main() -> None:
    c.verify()
    records: dict[str, Any] = {}
    raw_files: list[Path] = []
    for path in sorted((c.CAMPAIGN / "batches").glob("*.json")):
        if path.name.endswith(".complete.json"):
            continue
        batch = json.loads(path.read_text())
        completed = json.loads(path.with_suffix(".complete.json").read_text())
        for raw in batch["configs"]:
            cls = c.RoleConfig if batch["kind"] == "role" else c.ProofConfig
            cfg = cls(**raw)
            directory = c.ROOT / batch["output"] / "configs" / cfg.identifier()
            state = c.ol.ground_truth(directory)
            assert state == completed[cfg.identifier()] and state in (
                "done",
                "failed",
            )
            records[cfg.identifier()] = dict(
                status=state,
                group=Path(batch["output"]).name,
                directory=str(directory.relative_to(c.ROOT)),
            )
            raw_files.extend(p for p in directory.iterdir() if p.is_file())
    assert len(records) == 373
    assert Counter(r["status"] for r in records.values()) == {
        "done": 372,
        "failed": 1,
    }
    with sqlite3.connect(c.CAMPAIGN / "prior_ledger.sqlite3") as db:
        before = db.execute("SELECT * FROM receipts ORDER BY id").fetchall()
    with sqlite3.connect(c.LEDGER) as db:
        all_rows = db.execute("SELECT * FROM receipts ORDER BY id").fetchall()
        current = {r[0]: r for r in all_rows}
        assert all(current[r[0]] == r for r in before)
        cursor = db.execute(
            "SELECT * FROM receipts WHERE stage LIKE 'capacity-%' ORDER BY created,id"
        )
        with (c.CAMPAIGN / "receipts.csv").open("w") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow([d[0] for d in cursor.description])
            writer.writerows(cursor)
        stage_counts = dict(
            db.execute(
                "SELECT stage,COUNT(*) FROM receipts WHERE stage LIKE 'capacity-%' GROUP BY stage"
            )
        )
    accounting = (
        c.accounting()
    )  # Reprices every receipt from dated token rates.
    assert accounting["unresolved"] == 0 and accounting["total_spend"] <= 75
    assert abs(accounting["new_spend"] - 23.25562298) < 1e-8
    parity = {
        g: c.read(f"admission_parity_{g}.json")
        for g in ("cross", "creation", "mechanisms", "headroom1", "headroom2")
    }
    assert sum(len(v["items"]) for v in parity.values()) == 373
    assert all(v["all_equal"] for v in parity.values())
    raw_files.extend(
        [
            c.CAMPAIGN / "events.jsonl",
            c.CAMPAIGN / "prior_ledger.sqlite3",
            c.LEDGER,
        ]
    )
    raw_files.extend((c.CAMPAIGN / "replay_events").glob("*.jsonl"))
    transport = hashes(list((c.CAMPAIGN / "transport").rglob("*.gz")))
    c.save(
        "raw_inventory.json",
        dict(
            records=records,
            files=hashes(raw_files),
            transport=transport,
            storage="Raw caches and transport snapshots remain local; preserve every named file for exact replay.",
        ),
    )
    c.save(
        "verification.json",
        dict(
            sealed_files=len(c.read("seal.json")),
            references=176,
            records=dict(Counter(r["status"] for r in records.values())),
            record_groups=dict(Counter(r["group"] for r in records.values())),
            replay_complete_records=372,
            replay_failed_prefixes=1,
            exact_admission_sequences=373,
            carried_observations=35,
            prior_receipts_unchanged=len(before),
            combined_receipts=len(all_rows),
            new_receipts_by_stage=stage_counts,
            receipts_repriced=True,
            unresolved_receipts=0,
            accounting=accounting,
            scoped_tests=49,
            scoped_tests_log="tests_preflight.log",
            scoped_pyright="1.1.406: zero errors; typecheck_completed.log",
            root_pyright="17 pre-existing find_invariants/why3py errors; root_typecheck_pinned.log",
            ruff_log="ruff_completed.log",
            symlink_check="agents_completed.log",
            closure_disclosures=[
                "closure_correction.json",
                "closure_maintenance_note.json",
            ],
            source=hashes([c.ROOT / p for p in SOURCE_FILES]),
            raw_inventory_sha256=c.old.digest(
                c.CAMPAIGN / "raw_inventory.json"
            ),
            note="No new closed-set evaluation; numerical analysis restricted to explicit development manifests. This is not a zero-exposure claim.",
        ),
    )
    reviewable = [
        p
        for p in c.CAMPAIGN.iterdir()
        if p.is_file()
        and p.suffix
        in (
            ".json",
            ".md",
            ".png",
            ".pdf",
            ".csv",
            ".sh",
            ".log",
            ".yaml",
            ".exit",
        )
        and p.name != "artifact_inventory.json"
    ]
    reviewable.extend((c.CAMPAIGN / "prior_source").rglob("*.txt"))
    c.save("artifact_inventory.json", hashes(reviewable))
    print(
        json.dumps(
            dict(
                records=len(records),
                raw_files=len(raw_files),
                transport_files=len(transport),
                prior_receipts=len(before),
                new_receipts=accounting["requests"],
                total_spend=accounting["total_spend"],
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
