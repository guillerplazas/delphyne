"""Reconstruct two observed trace mechanisms from completed allowed cells.

Both harnesses: ``python -m experiments.ace_independent_audit.trace_dossiers``.
No new model calls or replacement attempts are made. Proof compilation reuses
the independent, source-hashed certificates. A matching rule is provenance
evidence, not by itself proof that the rule caused a solver improvement.
"""

from datetime import datetime
import gzip
import json
from typing import Any

from .audit import cell, load_yaml
from .common import CAMPAIGN, OUTPUT, REPORT, allowed, digest, read, save, sha
from .completion import require_closed
from .economics import ledger_rows
from .terminal_failure import assert_closed
from .verification import compile_one


def completed_row(batch: str, identity: str, theorem: str) -> dict[str, Any]:
    if batch == "rule_repairs":
        assert_closed(batch)
    else:
        require_closed(batch)
    directory = OUTPUT / batch / "configs" / identity
    row = cell((str(directory), theorem))
    receipts = [r for r in ledger_rows() if r["cell"] == identity]
    if (
        not row["exact_cost"]
        or any(r["status"] != "settled" for r in receipts)
        or len(receipts) != row["counts"]["requests"]
        or abs(sum(r["charged"] for r in receipts) - row["costs"]["price"])
        > 1e-9
    ):
        raise ValueError("Dossier source has unreconciled billing")
    return row


def prime_reuse() -> None:
    theorem = "amc12_2000_p6"
    if allowed()[theorem][0] != "train":
        raise ValueError("Expected a familiar trainX problem")
    event_file = CAMPAIGN / "learning_events/full_A2__sol_medium__35.json"
    event = read(event_file)
    evidence_file = (
        CAMPAIGN / "evidence" / f"source_assisted_v2__{theorem}.json"
    )
    if (
        event["theorem"] != theorem
        or event["evidence_hash"] != digest(read(evidence_file))
        or "rocq-00051" not in event["merge"]["added"]
    ):
        raise ValueError("Rule origin differs from the recorded source")
    books = [
        read(CAMPAIGN / "books" / name)
        for name in ("A2_frozen.json", "R1_verified_rules.json")
    ]
    rules = [
        next(b for b in book["playbook"]["bullets"] if b["id"] == "rocq-00051")
        for book in books
    ]
    if rules[0] != rules[1]:
        raise ValueError("The prime rule was changed by the repair")
    online = read(CAMPAIGN / "online_protocol.json")
    jobs = [("source", "source_assisted", 0)]
    for seed in (0, 1):
        step = online["independent_orders"][seed].index(theorem)
        jobs.extend(
            [
                (f"online-o{seed}-s{step:02d}", "A0", seed),
                ("rule_repairs", "R1", seed),
            ]
        )
    traces: list[dict[str, Any]] = []
    for batch, arm, seed in jobs:
        identity = f"train__{arm}__{theorem}__seed{seed}"
        row = completed_row(batch, identity, theorem)
        values = row["value"]
        if len(values) > 1 or any(not isinstance(v, str) for v in values):
            raise ValueError("Expected at most one returned proof string")
        proof: str | None = values[0] if values else None
        certificate = (
            compile_one((allowed()[theorem][1], theorem, proof))
            if proof is not None
            else None
        )
        if certificate is not None and not certificate["passed"]:
            raise ValueError("The returned proof did not compile")
        traces.append(
            dict(
                cell=identity,
                batch=batch,
                solved=row["solved"],
                counts=row["counts"],
                costs=row["costs"],
                proof=proof,
                kernel=certificate,
                result_sha=row["result_sha"],
                cache_sha=row["cache_sha"],
            )
        )
    save(
        REPORT / "r1_prime_dossier.json",
        dict(
            theorem=theorem,
            partition="trainX",
            rule=rules[0],
            rule_origin=dict(
                event=str(event_file.relative_to(CAMPAIGN)),
                event_sha=sha(event_file),
                evidence_sha=sha(evidence_file),
                evidence_content_digest=event["evidence_hash"],
                source_theorem=theorem,
            ),
            traces=traces,
            interpretation="The largest R1 cost contribution is familiar-problem reuse. The matching bounded-prime rule was learned from this same theorem and is unchanged between A2 and R1. The fast returned proofs follow its candidate-exclusion pattern. This establishes provenance and observed behavior, not a causal estimate of the three manual repairs or generalization to unseen problems.",
        ),
    )


def goal_flood_completion() -> None:
    theorem = "amc12a_2020_p21"
    identity = f"validation__P1__{theorem}__seed0"
    batch = "core_pilot_book-part00"
    row = completed_row(batch, identity, theorem)
    receipts = sorted(
        (r for r in ledger_rows() if r["cell"] == identity),
        key=lambda r: r["created"],
    )
    gaps = [
        dict(
            after_request=i + 1,
            before_next_request_seconds=b["created"] - a["created"],
        )
        for i, (a, b) in enumerate(zip(receipts, receipts[1:]))
    ]
    state = load_yaml(OUTPUT / batch / "experiment.yaml")["configs"][identity]
    elapsed = (
        datetime.fromisoformat(str(state["end_time"]))
        - datetime.fromisoformat(str(state["start_time"]))
    ).total_seconds()
    checks = [
        dict(
            cache_index=check["index"],
            error=check["feedback"].get("error_message"),
            remaining_goals=len(check["feedback"].get("remaining_goals", [])),
            serialized_feedback_characters=len(json.dumps(check["feedback"])),
        )
        for check in row["checks"]
    ]
    if len(receipts) != 29 or max(c["remaining_goals"] for c in checks) != 192:
        raise ValueError("The observed completed trajectory changed")
    save(
        REPORT / "goal_flood_completion.json",
        dict(
            cell=identity,
            result_sha=row["result_sha"],
            cache_sha=row["cache_sha"],
            solved=row["solved"],
            costs=row["costs"],
            counts=row["counts"],
            elapsed_worker_seconds=elapsed,
            inter_request_gaps=gaps,
            checks=checks,
            probe_sha=sha(REPORT / "goal_flood_probe.json"),
            duplicate_witness_certificate_sha=sha(
                REPORT / "goal_flood_witness_certification.json"
            ),
            interpretation="The worker returned unsolved after about35minutes, at$0.10250013. The interval after request14 is976.69seconds, followed later by four roughly3-minute gaps. Inter-request intervals include API response and local processing time; they are not isolated CPU timers. The saved 192-goal check returned ordinary wrong-bullet feedback, not a session-limit exception. A separate zero-API probe reproduces those192goals in1.52seconds with automatic probing disabled. The exact proposed witness is independently proved to contain duplicates. Earlier live commentary attributing about30minutes to one check overstated its duration; no evidence establishes that the1800-second session supervisor fired on this check.",
        ),
    )


def goal_flood_timing() -> None:
    completed = read(REPORT / "goal_flood_completion.json")
    identity = completed["cell"]
    receipts = sorted(
        (r for r in ledger_rows() if r["cell"] == identity),
        key=lambda r: r["created"],
    )
    rows: list[dict[str, Any]] = []
    for i, receipt in enumerate(receipts):
        path = CAMPAIGN / "responses" / identity / (receipt["id"] + ".json.gz")
        with gzip.open(path, "rt") as stream:
            raw = json.load(stream)
        started = datetime.fromisoformat(raw["started"]).timestamp()
        finished = datetime.fromisoformat(raw["finished"]).timestamp()
        rows.append(
            dict(
                request=i + 1,
                response_sha=sha(path),
                api_elapsed_seconds=finished - started,
                after_response_to_next_dispatch_seconds=(
                    receipts[i + 1]["created"] - finished
                    if i + 1 < len(receipts)
                    else None
                ),
                input_tokens=raw["response"]["usage"]["input_tokens"],
                cost=receipt["charged"],
            )
        )
    api_seconds = sum(r["api_elapsed_seconds"] for r in rows)
    save(
        REPORT / "goal_flood_timing.json",
        dict(
            cell=identity,
            requests=rows,
            worker_elapsed_seconds=completed["elapsed_worker_seconds"],
            api_elapsed_seconds=api_seconds,
            outside_api_seconds=completed["elapsed_worker_seconds"]
            - api_seconds,
            interpretation="API intervals come from persisted transport start/finish timestamps. Outside-API time includes proof execution, feedback generation, serialization and local bookkeeping; it is not an isolated CPU measurement. The exact response14 has192open goals in its subsequent saved check. No timing estimate changes its unsolved benchmark outcome or cost.",
        ),
    )


if __name__ == "__main__":
    prime_reuse()
    goal_flood_completion()
    goal_flood_timing()
    print(json.dumps(dict(dossiers=3, paid_calls=0)))
