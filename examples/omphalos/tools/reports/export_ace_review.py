"""Export the completed ACE review's billing and operational evidence.

Run after continue_ace_review.py finishes, from either harness. Reads a
consistent SQLite transaction and exception classifications, never proof
trajectories. Refuses incomplete billing or a changed frozen export.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import csv
import hashlib
import io
import json
import sqlite3
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = OMPHALOS_ROOT
CAMPAIGN = ROOT / "experiments/campaigns/ace_review_20260908"


def write_frozen(path: Path, content: str) -> None:
    if path.exists():
        if path.read_text() != content:
            raise ValueError(f"refusing to change frozen export: {path}")
        return
    with path.open("x", newline="") as out:
        out.write(content)


def exception_class(text: str) -> str:
    for marker, label in (
        ("CampaignExhausted", "admission"),
        ("OPENAI_API_KEY", "credential"),
        ("AuthenticationError", "authentication"),
        ("string_above_max_length", "input_string_limit"),
        ("context_length_exceeded", "context_limit"),
        ("APITimeoutError", "timeout"),
        ("APIConnectionError", "connection"),
        ("InternalServerError", "server"),
        ("RateLimitError", "rate_limit"),
        ("BadRequestError", "other_bad_request"),
    ):
        if marker in text:
            return label
    return "other"


def main() -> None:
    final = json.loads((CAMPAIGN / "final_report.json").read_text())
    with sqlite3.connect(
        (CAMPAIGN / "ledger.sqlite3").as_uri() + "?mode=ro", uri=True
    ) as db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN")
        rows = [
            dict(row)
            for row in db.execute("SELECT * FROM receipts ORDER BY created,id")
        ]
        ceiling, allocations = json.loads(
            db.execute("SELECT config FROM settings").fetchone()[0]
        )
        original = json.loads(
            db.execute("SELECT config FROM allocation_origin").fetchone()[0]
        )
        transfers = [
            dict(row)
            for row in db.execute("SELECT * FROM transfers ORDER BY created")
        ]
    if not rows or any(row["status"] == "in_flight" for row in rows):
        raise ValueError("billing is incomplete")
    liability = sum(float(row["charged"]) for row in rows)
    if (
        abs(liability - final["ledger"]["liability"]) > 1e-8
        or liability > ceiling + 1e-8
        or allocations != final["ledger"]["allocations"]
        or transfers != final["ledger"]["transfers"]
    ):
        raise ValueError("billing does not match the frozen final report")

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream, fieldnames=list(rows[0]), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    content = stream.getvalue()

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        # Adaptation cell names identify generator, reflector, curator,
        # and embedding roles. Evaluation receipts remain grouped by phase.
        role = next(
            (
                name
                for name in ("generator", "reflector", "curator", "embedding")
                if name in str(row["cell"])
            ),
            "other",
        )
        label = (
            f"adaptation/{role}"
            if row["stage"] == "adaptation"
            else row["stage"]
        )
        groups[label].append(row)
    diagnostics: dict[str, Any] = {}
    for label, members in sorted(groups.items()):
        usage = [json.loads(row["usage"] or "{}") for row in members]
        inputs = [int(u["input_tokens"]) for u in usage if "input_tokens" in u]
        diagnostics[label] = dict(
            attempts=len(members),
            status_counts=dict(Counter(row["status"] for row in members)),
            liability=sum(float(row["charged"]) for row in members),
            receipted_charges=sum(
                float(row["charged"])
                for row in members
                if row["status"] == "settled"
            ),
            exceptions=dict(
                Counter(u["exception"] for u in usage if "exception" in u)
            ),
            median_input_tokens=statistics.median(inputs) if inputs else None,
            maximum_input_tokens=max(inputs) if inputs else None,
            maximum_output_tokens=max(
                (int(u.get("output_tokens", 0)) for u in usage), default=0
            ),
        )
    exceptions: list[dict[str, Any]] = []
    for phase in ("calibration", "development", "confirmation", "terra"):
        run = ROOT / f"experiments/output/ace_review_{phase}/configs"
        for path in sorted(run.glob("*/exception.txt*")):
            if path.is_file():
                raw = path.read_bytes()
                exceptions.append(
                    dict(
                        file=str(path.relative_to(ROOT)),
                        sha256=hashlib.sha256(raw).hexdigest(),
                        phase=phase,
                        category=exception_class(raw.decode()),
                    )
                )
    summary = dict(
        receipts_file="receipts.csv",
        receipts_sha256=hashlib.sha256(content.encode()).hexdigest(),
        receipt_count=len(rows),
        ceiling=ceiling,
        liability=liability,
        original_allocation=original,
        allocations=allocations,
        transfers=transfers,
        groups=diagnostics,
        exception_files=exceptions,
        exception_note="One original or preserved top-level exception per failed cell attempt; initial credential failures are included. These counts differ from HTTP attempt counts. No proof trajectories were read.",
    )
    write_frozen(CAMPAIGN / "receipts.csv", content)
    write_frozen(
        CAMPAIGN / "operational_audit.json",
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
    )
    print(json.dumps(dict(receipts=len(rows), liability=liability), indent=2))


if __name__ == "__main__":
    main()
