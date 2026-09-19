"""Both harnesses: build compact review exports without changing raw evidence.

Run after `verify` and `report`: python -m experiments.ace_x3_reproduction.review.
Only this campaign's explicit development-data artifacts are visited.
"""

import gzip
import json
from pathlib import Path
from typing import Any

from . import campaign as c


def compressed(path: Path) -> Path:
    destination = path.with_suffix(path.suffix + ".gz")
    data = gzip.compress(path.read_bytes(), mtime=0)
    if destination.exists() and destination.read_bytes() != data:
        raise ValueError("Compressed evidence changed: " + str(path))
    destination.write_bytes(data)
    if gzip.decompress(data) != path.read_bytes():
        raise ValueError("Compression changed evidence")
    return destination


def record(path: Path) -> dict[str, Any]:
    return dict(
        path=str(path.relative_to(c.ROOT)),
        bytes=path.stat().st_size,
        sha256=c.sha(path),
    )


def main() -> None:
    c.verify_seal()
    if not all(
        c.read(name)["passed"]
        for name in ("verification/replay.json", "verification/kernel.json")
    ):
        raise ValueError("Verification incomplete")
    if len(list((c.CAMPAIGN / "analysis/exercises").glob("*.md"))) != 40:
        raise ValueError("Incomplete exercise dossiers")
    raw: list[Path] = [
        c.CAMPAIGN / n for n in ("ledger.sqlite3", "events.jsonl")
    ]
    for directory in (
        "responses",
        "transport",
        "retrieved",
        "historical_transport",
    ):
        raw.extend((c.CAMPAIGN / directory).rglob("*.json.gz"))
    for job in c.jobs():
        raw.extend(c.directory(job) / n for n in ("cache.yaml", "result.yaml"))
    raw.extend((c.CAMPAIGN / "kernel").glob("*.v"))
    raw.extend((c.CAMPAIGN / "kernel").glob("*.json"))
    c.save("raw_archive_manifest.json", [record(p) for p in sorted(raw)])
    deliver = [
        c.CAMPAIGN / n
        for n in (
            "README.md",
            "book.json",
            "prior_accounting.json",
            "runtime.json",
            "protocol.json",
            "manifest.json",
            "seal.json",
            "environment.json",
            "preflight.json",
            "root_pyright.log",
            "quality.json",
            "verification/replay.json",
            "verification/kernel.json",
            "audit/accounting.json",
            "audit/cells.json",
            "audit/cells.csv",
            "audit/receipts.json",
            "audit/receipts.csv",
            "audit/retrieval.json",
            "audit/corrected_comparisons.json",
            "audit/other_retrospectives.json",
            "audit/source_history_verified.json",
            "audit/source_reflog.json",
            "audit/provider_output_validation.json",
            "audit/historical_replay_v2.json",
            "audit/historical_kernel.json",
            "audit/encrypted_retrieval_probe.json",
            "audit/x3_census_v2.json",
            "audit/input_stability_v2.json",
            "audit/admission_tails_v2.json",
            "analysis/results.json",
            "analysis/cells.json",
            "analysis/cells.csv",
            "analysis/receipts.json",
            "analysis/receipts.csv",
            "analysis/secondary_metrics.json",
            "analysis/input_stability.json",
            "analysis/admission_tails_v2.json",
            "analysis/termination.json",
            "analysis/gap_by_theorem.csv",
            "analysis/gap_accounting.json",
            "raw_archive_manifest.json",
        )
    ]
    deliver.extend((c.CAMPAIGN / "audit/source").rglob("*.py"))
    deliver.extend((c.CAMPAIGN / "audit/source").rglob("*.diff"))
    deliver.extend((c.CAMPAIGN / "analysis/figures").glob("*.*"))
    deliver.extend((c.CAMPAIGN / "analysis/exercises").glob("*.md"))
    for path in (c.CAMPAIGN / "analysis/exercises").glob("*.json"):
        deliver.append(compressed(path))
    deliver = [
        compressed(p)
        if p.suffix in (".json", ".csv") and p.stat().st_size > 250_000
        else p
        for p in deliver
    ]
    deliver.extend(Path(__file__).parent.glob("*.py"))
    deliver.extend(
        c.ROOT / n
        for n in (
            "tests/test_x3_reproduction.py",
            "docs/ace_x3_reproduction_study.md",
        )
    )
    c.save(
        "review_manifest.json",
        dict(
            files=[record(p) for p in sorted(deliver)],
            raw_archive="raw_archive_manifest.json.gz",
            limitation="Hashes are integrity checks, not backups. Keep original paid caches, SQLite ledger, events, provider responses and transport snapshots for replay. Compressed exports preserve exact original bytes.",
        ),
    )
    print(
        json.dumps(
            dict(
                files=len(deliver),
                bytes=sum(p.stat().st_size for p in deliver),
            )
        )
    )


if __name__ == "__main__":
    main()
