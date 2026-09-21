"""Certify the credit-exhausted checkpoint without inventing final outcomes.

All scope comes from this study's registered development-only manifests.
Previously compiled/replayed evidence is revalidated by hashes, and every
persisted provider response is independently repriced. No API call is made.
This is separate from the immutable initial checkpoint and full finalizers.
"""

import json
from typing import Any

from . import campaign as c
from .audit import load_yaml
from .certification import receipt_audit
from .common import CAMPAIGN, OUTPUT, REPORT, ROOT, digest, read, save, sha
from .economics import ledger_rows
from .quota_recovery import BATCH, CELL, FOLDER, REASON, prepare
from .resumption import running
from .study_certification import batches


def run() -> dict[str, Any]:
    proposal = prepare()
    if (
        not (CAMPAIGN / "PAUSED").exists()
        or read(CAMPAIGN / "PAUSED")["reason"] != REASON
    ):
        raise ValueError("This snapshot is only for the recorded credit pause")
    names = batches()
    if any(running(name) for name in names):
        raise ValueError("A worker is still running")
    receipts = ledger_rows()
    receipt_digest = digest(sorted(receipts, key=lambda r: r["id"]))
    destination = REPORT / "quota_checkpoint_inventory.json"
    if destination.exists():
        result = read(destination)
        if result["receipt_rows_digest"] != receipt_digest:
            raise ValueError(
                "This checkpoint is historical; do not overwrite it"
            )
        return result
    normal: set[str] = set()
    terminal: set[str] = set()
    pending: set[str] = set()
    expected_all: set[str] = set()
    proved: set[str] = set()
    proof_keys: set[tuple[str, str]] = set()
    certificates: list[dict[str, str]] = []
    for batch in names:
        jobs = [
            c.Job(**j) for j in read(CAMPAIGN / "batches" / (batch + ".json"))
        ]
        expected = {c.name(j, None) for j in jobs}
        if expected_all & expected:
            raise ValueError("Registered solver identity appears twice")
        expected_all.update(expected)
        certificate = (
            REPORT / "returned_part06_certification.json"
            if batch == BATCH
            else CAMPAIGN / "verification" / (batch + ".json")
        )
        if not certificate.exists():
            for identity in expected:
                directory = OUTPUT / batch / "configs" / identity
                if any(
                    (directory / filename).exists()
                    for filename in (
                        "result.yaml",
                        "exception.txt",
                        "completed.json",
                    )
                ):
                    raise ValueError(
                        "An unclassified trajectory has execution evidence"
                    )
            pending.update(expected)
            continue
        recorded = read(certificate)
        replays = {r["cell"]: r for r in recorded["replays"]}
        failures = {
            r["cell"]: r for r in recorded.get("terminal_failures", [])
        }
        censored: set[str] = {CELL} if batch == BATCH else set()
        if replays.keys() | failures.keys() | censored != expected:
            raise ValueError(
                "Checkpoint replay coverage differs from its manifest"
            )
        normal.update(replays)
        terminal.update(failures)
        for identity, replay in replays.items():
            directory = OUTPUT / batch / "configs" / identity
            if (
                not replay["passed"]
                or replay["paid_calls"] != 0
                or any(
                    sha(directory / filename) != value
                    for filename, value in replay["hashes"].items()
                )
            ):
                raise ValueError(
                    "A normal replay's preserved evidence changed"
                )
            values = load_yaml(directory / "result.yaml")["outcome"]["result"][
                "values"
            ]
            if values:
                proved.add(identity)
        for identity, failure in failures.items():
            directory = OUTPUT / batch / "configs" / identity
            if (directory / "result.yaml").exists() or any(
                sha(directory / filename) != failure["hashes"][filename]
                for filename in ("cache.yaml", "exception.txt")
            ):
                raise ValueError(
                    "A terminal prefix's preserved evidence changed"
                )
            if not all(
                r["passed"] and r["paid_calls"] == 0
                for r in failure["replays"]
            ):
                raise ValueError("A terminal prefix is not replay-certified")
        compiled: set[str] = set()
        for proof in recorded["kernel"]:
            if not proof["passed"]:
                raise ValueError("An independently compiled proof failed")
            compiled.update(proof["cells"])
            proof_keys.add((proof["source_sha"], proof["compiler_sha"]))
        if compiled != proved & expected:
            raise ValueError(
                "Compiled proof coverage differs from returned outcomes"
            )
        certificates.append(
            dict(path=str(certificate.relative_to(ROOT)), sha=sha(certificate))
        )
    if len(
        expected_all
    ) != 2044 or expected_all != normal | terminal | pending | {CELL}:
        raise ValueError(
            "The complete registered denominator does not reconcile"
        )
    audit = receipt_audit(
        REPORT / "quota_checkpoint_receipt_certification.json"
    )
    if digest(sorted(ledger_rows(), key=lambda r: r["id"])) != receipt_digest:
        raise ValueError("The ledger changed while certifying the checkpoint")
    result = dict(
        registered_solver_attempts=len(expected_all),
        completed_solver_attempts=len(normal) + len(terminal),
        normal_exact_replays=len(normal),
        terminal_prefix_replays=len(terminal),
        administratively_censored=[CELL],
        preserved_prefix_cost=proposal["prefix_cost"],
        unlaunched_solver_attempts=len(pending),
        unique_benchmark_proofs=len(proof_keys),
        proved_cells=len(proved),
        budget_cells=sum(
            1 for _ in (CAMPAIGN / "budget_replay").glob("*.json")
        ),
        receipt_rows_digest=receipt_digest,
        receipt_certification_sha=sha(
            REPORT / "quota_checkpoint_receipt_certification.json"
        ),
        quota_preparation_sha=sha(FOLDER / "preparation.json"),
        total_research_cost_interval=audit["paid_cost_interval"],
        certificates=certificates,
        paid_calls=0,
        note="Complete outcomes only. Account-credit interruption remains incomplete, with its paid prefix and zero-charge rejection retained. No imputation, replacement sample, new model call or final-study verdict. Manual repair and parser-probe proofs are excluded from benchmark proof counts.",
    )
    save(destination, result)
    print(json.dumps({k: v for k, v in result.items() if k != "certificates"}))
    return result


if __name__ == "__main__":
    run()
