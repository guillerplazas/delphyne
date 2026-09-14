"""Audit the one known zero-charge HTTP 400; preserve failed proof setup.

This campaign-specific migration cannot discharge an unknown charge, change
money, or disable the ledger's global guard. The original receipt and source
exception remain preserved. One of four allowed request retries is used.
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

import json
import shutil
import time

from experiments import snippet_experiment as c

RECEIPT = "29f2101c9e6b441cae9ac3d307ed7821"


def main() -> None:
    acct = c.accounting()
    if acct["unresolved"] or acct["billing_issues"] != [RECEIPT]:
        raise ValueError("Unexpected billing condition; refuse repair")
    tests = c.CAMPAIGN / "tests_transport_repair.log"
    if "31 passed" not in tests.read_text():
        raise ValueError("Full scoped regression checks must pass first")
    training = c.OUTPUT / "training"
    failures = list(training.rglob("exception.txt"))
    rejected = [p for p in failures if "Error code: 400" in p.read_text()]
    if len(failures) != 20 or len(rejected) != 1:
        raise ValueError("Unexpected failed setup panel")
    exception = rejected[0]
    if (
        "No tool output found for function call call_2."
        not in exception.read_text()
    ):
        raise ValueError("Unknown request rejection")
    for path in set(failures) - set(rejected):
        if (
            "Tool messages must appear in the same order as tool calls"
            not in path.read_text()
        ):
            raise ValueError("Unexpected local failure")
    canonical = exception.parent.name
    ledger = c.Ledger(c.LEDGER)
    with ledger.connect() as db:
        row = db.execute(
            "SELECT * FROM receipts WHERE id=?", (RECEIPT,)
        ).fetchone()
        columns = [r[1] for r in db.execute("PRAGMA table_info(receipts)")]
        original = dict(zip(columns, row))
    if (
        original["status"] != "settled"
        or original["charged"] != 0
        or json.loads(original["usage"]) != {"exception": "BadRequestError"}
    ):
        raise ValueError(
            "Only this previously settled zero-charge rejection is eligible"
        )
    archive = c.CAMPAIGN / "setup_failure_02"
    archive.mkdir(exist_ok=False)
    shutil.move(str(training), archive / "training")
    c.save(
        "transport_repair.json",
        dict(
            reason="Few-shot demonstrations left unanswered tool calls; proof reference factory also overwrote the logical receipt name",
            failed_proof_denominator=20,
            failed_proof_solves=0,
            locally_rejected=19,
            provider_rejected=1,
            successful_generations=0,
            zero_charge=0,
            request_retries_used=1,
            request_retry_limit=4,
            original_receipt=original,
            canonical_cell=canonical,
            exception_file=str(
                (
                    archive / "training" / exception.relative_to(training)
                ).relative_to(c.ROOT)
            ),
            test_log_sha256=c.sha(tests),
            interpretation="Failed proof panel is preserved in full. Corrected execution uses the same problem/seed cells, budgets and gates; no successful model outcome is replaced.",
            amendment="Demonstrations now include every tool output and separately Rocq-checked final proofs; all 60 rendered proof requests have matching call/output pairs. Receipt namespace is restored after reference construction.",
        ),
    )
    with ledger.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        assert (
            db.execute(
                "SELECT * FROM receipts WHERE id=?", (RECEIPT,)
            ).fetchone()
            == row
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS reconciliations (receipt TEXT PRIMARY KEY, created REAL, original TEXT, evidence TEXT)"
        )
        db.execute(
            "INSERT INTO reconciliations VALUES (?,?,?,?)",
            (
                RECEIPT,
                time.time(),
                json.dumps(original, sort_keys=True),
                str(c.CAMPAIGN / "transport_repair.json"),
            ),
        )
        usage = dict(
            reconciled_exception="BadRequestError",
            reconciliation="transport_repair.json: exact HTTP 400, already settled at zero; original retained in reconciliations table",
        )
        db.execute(
            "UPDATE receipts SET cell=?,usage=? WHERE id=?",
            (canonical, json.dumps(usage, sort_keys=True), RECEIPT),
        )
    # Preserve the preceding source seal; never overwrite its hashes.
    previous = c.CAMPAIGN / "seals/before_proof_transport_fix.json"
    (c.CAMPAIGN / "seal.json").rename(previous)
    c.seal()
    c.verify()
    print(
        "Audited one known HTTP 400 at unchanged $0; global ledger protection remains active"
    )


if __name__ == "__main__":
    main()
