"""Reconcile one timeout conservatively within the existing API authorization.

Preparation never unpauses dispatch, changes a receipt, or retries a model.
Application records and verifies the user's already granted continuation.
It does not invent a new user reply to the unnecessary per-receipt question.
It preserves the full reservation, labels it bounded rather than settled,
and leaves the ordinary guard active for every subsequent unknown request.
The unknown actual invoice amount must remain an interval in final analyses.
"""

import argparse
import gzip
import json
import sqlite3
from typing import Any

from runtime.campaign_budget import Ledger

from . import campaign as c
from .accounting import reserve
from .audit import cell
from .common import CAMPAIGN, OUTPUT, REPORT, now, read, save, sha
from .economics import ledger_rows
from .resumption import running
from .terminal_failure import hashes, replay_failure

BATCH = "core_frozen-part05"
CELL = "train__B1__mathd_algebra_185__seed0"
RECEIPT = "97e9d18f8d88406d8cd7fe33983f3339"
FOLDER = CAMPAIGN / "billing_recovery"


def prepare() -> dict[str, Any]:
    """Certify the lost request and its unchanged, finite reserved liability."""
    target = FOLDER / "bounded_timeout_preparation.json"
    directory = OUTPUT / BATCH / "configs" / CELL
    if target.exists():
        prior = read(target)
        response = CAMPAIGN / "responses" / CELL / (RECEIPT + ".json.gz")
        if (
            prior["certificate"]["hashes"] != hashes(directory)
            or prior["evidence_sha"] != sha(response)
            or prior["normal_certificate_sha"]
            != sha(REPORT / "returned_part05_certification.json")
        ):
            raise ValueError("Timeout evidence changed")
        return prior
    if running(BATCH):
        raise ValueError("Wait until the launched batch returns")
    all_receipts = ledger_rows()
    unresolved = [r for r in all_receipts if r["status"] != "settled"]
    if len(unresolved) != 1 or unresolved[0]["id"] != RECEIPT:
        raise ValueError("This preparation covers exactly one known timeout")
    receipt = unresolved[0]
    if (
        receipt["status"] != "unknown_charge"
        or receipt["charged"] != receipt["reserved"]
    ):
        raise ValueError("The original reservation is not fully retained")
    path = CAMPAIGN / "responses" / CELL / (RECEIPT + ".json.gz")
    with gzip.open(path, "rt") as stream:
        raw = json.load(stream)
    exception = raw.get("exception", {})
    if (
        exception.get("type") != "APITimeoutError"
        or exception.get("rejected") is not False
    ):
        raise ValueError("The saved transport failure changed")
    from datetime import datetime

    bound = reserve(
        raw["payload"]["model"],
        raw["input_bound"],
        raw["payload"]["max_output_tokens"],
        datetime.fromisoformat(raw["started"]).date(),
    )
    if bound != receipt["reserved"]:
        raise ValueError("The conservative request bound changed")
    receipts = sorted(
        [r for r in all_receipts if r["cell"] == CELL],
        key=lambda r: r["created"],
    )
    observed = cell((str(directory), "mathd_algebra_185"))
    known = sum(r["charged"] for r in receipts[:-1])
    if (
        receipts[-1]["id"] != RECEIPT
        or observed["counts"]["requests"] != len(receipts) - 1
        or not observed["exact_cost"]
        or abs(observed["costs"]["price"] - known) > 1e-9
        or known >= 0.05
    ):
        raise ValueError("Saved prefix or lower-budget applicability changed")
    job = next(
        c.Job(**v)
        for v in read(CAMPAIGN / "batches" / (BATCH + ".json"))
        if c.name(c.Job(**v), None) == CELL
    )
    replayed = [
        replay_failure(BATCH, job, raw, cap)
        for cap in (0.10, 0.05, 0.075, 0.09)
    ]
    certificate = dict(
        cell=CELL,
        batch=BATCH,
        hashes=hashes(directory),
        failure="provider_api_timeout_with_bounded_charge",
        solved=False,
        cost=known + bound,
        cost_interval=[known, known + bound],
        known_prefix_cost=known,
        unknown_charge_interval=[0.0, bound],
        unknown_receipt=RECEIPT,
        successful_api_responses=len(receipts) - 1,
        attempted_api_requests=len(receipts),
        rejected_zero_charge=0,
        receipts=[r["id"] for r in receipts],
        exception=exception,
        replays=[
            dict(
                cap=r["cap"],
                exact_terminal_request=True,
                paid_calls=0,
                passed=r["passed"],
            )
            for r in replayed
        ],
        interpretation="The client timed out after23 paid responses. Its24th request has no returned output or known invoice. Retain the failed outcome and full reserved liability, with the actual total bill in the stated interval. The reservation is not a measured charge. All four controllers reach the exact same saved request; no replacement draw or invented response.",
    )
    normal = read(REPORT / "returned_part05_certification.json")
    if (
        normal["normal_completed_cells"] != 99
        or normal["budget_scenarios"] != 297
    ):
        raise ValueError("The other99 outcomes are not fully certified")
    proposal = dict(
        prepared_at=now(),
        receipt_before=receipt,
        evidence_sha=sha(path),
        certificate=certificate,
        normal_certificate_sha=sha(
            REPORT / "returned_part05_certification.json"
        ),
        action="On explicit approval only, transition this single receipt from unknown_charge to bounded_charge without changing charged/reserved. Keep the original evidence, full liability and interval. Clear only the associated pause after checking no other unresolved receipts exist. Complete the originally registered520 unlaunched attempts; never retry this failed cell.",
        scope="No change to models, prompts, tools, proof acceptance, books, samples, spending capacity, or guard treatment of any later unknown request.",
        analysis_requirement="Every final cost involving this cell must expose its invoice interval. Do not call bounded_charge settled or exact. Practical targets must survive the adverse endpoint of the interval.",
        permission="Prepared, not approved or applied.",
    )
    save(target, proposal)
    return proposal


def apply(authorization: str) -> None:
    """Retain full liability and use the recorded authorization for this scope."""
    source = CAMPAIGN / "resumption.json"
    if (
        not authorization.strip()
        or authorization != read(source)["authorization"]
    ):
        raise ValueError("The recorded user continuation is required")
    proposal = prepare()
    pause = CAMPAIGN / "PAUSED"
    if (
        not pause.exists()
        or read(pause).get("reason") != "Unresolved request billing"
    ):
        raise ValueError("Unexpected pause state")
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    approval_file = FOLDER / "bounded_timeout_approval.json"
    if approval_file.exists():
        if read(approval_file)["user_authorization"] != authorization:
            raise ValueError("An existing authorization has different text")
    else:
        save(
            approval_file,
            dict(
                applied_authorization_at=now(),
                user_authorization=authorization,
                source_record="resumption.json",
                source_sha=sha(source),
                basis="The existing explicit API continuation covers the original remaining attempts. This routine reconciliation retains the entire reserved liability, does not increase scope or spending capacity, and never replaces the failed attempt. The earlier per-receipt permission question was unnecessary; no subsequent user approval is claimed.",
                proposal_sha=sha(FOLDER / "bounded_timeout_preparation.json"),
                receipt=RECEIPT,
            ),
        )
    with ledger.connect() as db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN IMMEDIATE")
        rows = [
            dict(r)
            for r in db.execute(
                "SELECT * FROM receipts WHERE status != 'settled'"
            )
        ]
        if len(rows) != 1 or rows[0]["id"] != RECEIPT:
            raise ValueError("Another billing issue still prevents dispatch")
        actual = dict(rows[0])
        if actual["status"] == "bounded_charge":
            actual["status"] = "unknown_charge"
        if actual != proposal["receipt_before"]:
            raise ValueError("The reviewed receipt changed")
        db.execute(
            "UPDATE receipts SET status='bounded_charge' WHERE id=?",
            (RECEIPT,),
        )
    certificate = dict(
        proposal["certificate"], liability_approval_sha=sha(approval_file)
    )
    save(CAMPAIGN / "terminal_failures" / (CELL + ".json"), certificate)
    save(
        CAMPAIGN / "budget_replay" / (CELL + ".json"),
        dict(
            hashes=certificate["hashes"],
            batch=BATCH,
            rows=[
                dict(
                    cell=CELL,
                    arm="B1",
                    stage="train",
                    theorem="mathd_algebra_185",
                    seed=0,
                    cap=r["cap"],
                    solved=False,
                    spent_budget=dict(
                        price=certificate["cost"],
                        num_requests=certificate["successful_api_responses"],
                    ),
                    cost_interval=certificate["cost_interval"],
                    attempted_requests=certificate["attempted_api_requests"],
                    paid_calls=0,
                    terminal_failure=certificate["failure"],
                )
                for r in certificate["replays"]
                if r["cap"] < 0.10
            ],
        ),
    )
    # Complete the full batch certificate before releasing its pause.
    from .terminal_failure import run

    run(BATCH)
    save(FOLDER / "original_pause.json", read(pause))
    pause.unlink()
    print(
        json.dumps(
            dict(
                applied=True,
                retained_reservation=certificate["unknown_charge_interval"][1],
                actual_charge_still_unknown=True,
                failed_attempt_retried=False,
            )
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "apply"))
    parser.add_argument("--use-recorded-continuation", action="store_true")
    args = parser.parse_args()
    if args.action == "prepare":
        proposal = prepare()
        print(
            json.dumps(
                {
                    k: v
                    for k, v in proposal.items()
                    if k not in ("receipt_before", "certificate")
                },
                indent=2,
            )
        )
    else:
        if not args.use_recorded_continuation:
            raise ValueError(
                "Explicitly select the existing continuation record"
            )
        apply(read(CAMPAIGN / "resumption.json")["authorization"])


if __name__ == "__main__":
    main()
