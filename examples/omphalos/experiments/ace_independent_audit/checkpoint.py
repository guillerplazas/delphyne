"""User-requested dispatch hold: certify finished work without a final verdict.

No new experiment or API call is launched. Every active batch must have
returned before this snapshot is written. Main-study finalizers remain
strictly separate and continue to require their complete registered panels.
"""

from collections import defaultdict
import fcntl
import json
from typing import Any

from . import campaign as c
from .analysis import metrics, paired
from .certification import chronology, learning_scope, receipt_audit
from .common import CAMPAIGN, OUTPUT, REPORT, allowed, read, save, sha
from .completion import require_closed
from .economics import ledger_rows, paid
from .families import mapping
from .fresh import receipts, solver_rows
from .mechanisms import aggregate, characterize, contributions
from .reporting import ARM_NAMES
from .study_certification import batches


def assert_quiet() -> None:
    if not (CAMPAIGN / "HOLD_NEW_BATCHES.json").exists():
        raise ValueError("No user-requested dispatch hold is recorded")
    for path in OUTPUT.glob("*/.launch.lock"):
        with path.open("r") as stream:
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ValueError(
                    "Batch still executing: " + path.parent.name
                ) from exc
    if any(r["status"] != "settled" for r in ledger_rows()):
        raise ValueError("Some dispatched request has not settled")


def run() -> None:
    assert_quiet()
    ledger = receipts()
    rows: list[dict[str, Any]] = []
    closed: list[str] = []
    pending: list[str] = []
    proof_hashes: set[tuple[str, str]] = set()
    source_contract: dict[str, str] | None = None
    replayed = 0
    terminal_replayed = 0
    for batch in batches():
        try:
            require_closed(batch)
        except (ValueError, FileNotFoundError):
            if not (
                CAMPAIGN / "terminal_failures" / (batch + ".json")
            ).exists():
                pending.append(batch)
                continue
            from .terminal_failure import assert_closed

            assert_closed(batch)
        current = solver_rows(batch, ledger, allow_terminal_failures=True)
        jobs = {
            c.name(job, None): job
            for job in (
                c.Job(**value)
                for value in read(CAMPAIGN / "batches" / (batch + ".json"))
            )
        }
        certificate = read(CAMPAIGN / "verification" / (batch + ".json"))
        replays = {r["cell"]: r for r in certificate["replays"]}
        terminal = {
            r["cell"]: r for r in certificate.get("terminal_failures", [])
        }
        if replays.keys() | terminal.keys() != {r["cell"] for r in current}:
            raise ValueError("Closed-batch replay denominator differs")
        if not all(r["passed"] for r in certificate["kernel"]):
            raise ValueError("Returned proof failed independent compilation")
        compiled_cells = {
            cell for proof in certificate["kernel"] for cell in proof["cells"]
        }
        if compiled_cells != {r["cell"] for r in current if r["solved"]}:
            raise ValueError("Independent proof-check denominator differs")
        for proof in certificate["kernel"]:
            proof_hashes.add((proof["source_sha"], proof["compiler_sha"]))
        for row in current:
            job = jobs[row["cell"]]
            if row["cell"] in terminal:
                failure = terminal[row["cell"]]
                if not all(
                    r["passed"] and r["paid_calls"] == 0
                    for r in failure["replays"]
                ):
                    raise ValueError("Terminal replay was not certified")
                if failure["hashes"] != {
                    "result.yaml": None,
                    "cache.yaml": row["cache_sha"],
                    "exception.txt": row["exception_sha"],
                }:
                    raise ValueError("Terminal replay hashes differ")
                terminal_replayed += 1
            else:
                replay = replays[row["cell"]]
                if not replay["passed"] or replay["paid_calls"] != 0:
                    raise ValueError("Exact replay was not certified")
                if replay["hashes"] != {
                    "result.yaml": row["result_sha"],
                    "cache.yaml": row["cache_sha"],
                }:
                    raise ValueError("Completed replay hashes differ")
                replayed += 1
            if set(row["models"]) != {"gpt-5.6-luna"} or row["tools"] != [
                "ReadSkill",
                "SearchRocq",
            ]:
                raise ValueError("Benchmark solver contract differs")
            if not job.assisted and row["counts"].get("auto_finished", 0):
                raise ValueError("Plain solver received automatic completion")
            if job.output_tokens != 32768:
                raise ValueError("Unexpected solver output allowance")
            if not row.get("terminal_failure") and (
                abs(
                    row["spent_budget"].get("price", 0) - row["costs"]["price"]
                )
                > 1e-9
            ):
                raise ValueError("Controller and reconstructed bill disagree")
            if job.book_file:
                path = CAMPAIGN / job.book_file
                if sha(path) != job.book_sha:
                    raise ValueError("Paid playbook identity changed")
                book = read(path)
                if any(
                    allowed().get(t, (None,))[0] != "train"
                    for t in book.get("training_theorems", [])
                ):
                    raise ValueError("Book declares non-training evidence")
                if batch.startswith("online-"):
                    order = int(batch.split("-")[1][1:])
                    step = int(batch.split("-")[2][1:])
                    sequence = read(CAMPAIGN / "online_protocol.json")[
                        "independent_orders"
                    ][order]
                    if book["training_theorems"] != sequence[:step]:
                        raise ValueError("Online book has an invalid prefix")
                    if step:
                        prior = read(
                            CAMPAIGN
                            / "online_events"
                            / f"online-o{order}-s{step - 1:02d}.json"
                        )["after"][job.arm.removeprefix("online_")]
                        if book["playbook"] != prior:
                            raise ValueError("Online book skipped an update")
        if batch not in ("source", "author_pilot"):
            contract = read(CAMPAIGN / "batch_sources" / (batch + ".json"))
            if source_contract is None:
                source_contract = contract
            elif source_contract != contract:
                raise ValueError(
                    "Solver code differs across completed main batches"
                )
            from .common import ROOT

            if any(
                sha(ROOT / path) != digest for path, digest in contract.items()
            ):
                raise ValueError("A measured solver source has changed")
        rows.extend(current)
        closed.append(batch)
    if len({r["cell"] for r in rows}) != len(rows):
        raise ValueError("A checkpoint cell was counted twice")
    billing = paid(ledger_rows())
    solver_billing = paid([r for r in ledger_rows() if r["stage"] == "solver"])
    if (
        abs(sum(r["costs"]["price"] for r in rows) - solver_billing["cost"])
        > 1e-8
    ):
        raise ValueError("Some solver spending is absent from completed cells")
    if (
        sum(r["counts"].get("requests", 0) for r in rows)
        != solver_billing["requests"]
    ):
        raise ValueError("Some solver call is absent from completed cells")
    grouped: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(
        list
    )
    for row in rows:
        if row["arm"] in ARM_NAMES:
            grouped[row["stage"], row["arm"], row["seed"]].append(row)
    complete: dict[tuple[str, str, int], list[dict[str, Any]]] = {}
    for key, rr in grouped.items():
        names = {t for t, (stage, _) in allowed().items() if stage == key[0]}
        if len(rr) == 40 and {r["theorem"] for r in rr} == names:
            complete[key] = rr
    comparisons: dict[str, Any] = {}
    for (stage, arm, seed), rr in complete.items():
        baseline = (
            "B0" if arm.removeprefix("online_").startswith("B") else "A0"
        )
        base = complete.get((stage, baseline, seed))
        if arm not in ("A0", "B0") and base is not None:
            comparisons[f"{stage}/{arm}/replicate{seed}"] = dict(
                baseline=baseline,
                theorem=paired(base, rr),
                family=paired(base, rr, mapping()),
            )
    chronology_data = chronology(final=False)
    online_economics: dict[str, Any] = {}
    for order in (0, 1):
        steps = [e for e in chronology_data["events"] if e["order"] == order]
        if len(steps) != 40:
            continue
        for arm in ("A2", "B1", "B2"):
            inference = metrics(complete["train", "online_" + arm, order])
            control = "B0" if arm.startswith("B") else "A0"
            baseline = metrics(complete["train", control, order])
            learning = paid(
                [
                    r
                    for r in ledger_rows()
                    if r["cell"].startswith(f"online-o{order}-")
                    and f"__{arm}__" in r["cell"]
                ]
            )
            online_economics[f"order{order}/{arm}"] = dict(
                learning=learning,
                inference=inference,
                baseline=baseline,
                operational_cost=inference["cost"] + learning["cost"],
                note="All forty scores and all forty subsequent updates, including the final update. One completed order only; these learning fees are part of the study total, not an additional bill.",
            )
    result = dict(
        user_hold=read(CAMPAIGN / "HOLD_NEW_BATCHES.json"),
        completed_solver_cells=len(rows),
        registered_solver_cells=2044,
        pending_solver_cells=2044 - len(rows),
        main_completed=sum(
            r["arm"] not in ("R1", "O1")
            and r["batch"] not in ("source", "author_pilot")
            for r in rows
        ),
        main_registered=1520,
        closed_batches=closed,
        pending_batches=pending,
        replayed_cells=replayed,
        terminal_failure_cells=terminal_replayed,
        terminal_prefix_and_rejection_replays=terminal_replayed,
        unique_compiled_proofs=len(proof_hashes),
        solved_cells=sum(r["solved"] for r in rows),
        all_solver_receipts_reconciled=True,
        main_source_contract=source_contract,
        overall_bill=billing,
        stages={
            s: paid([r for r in ledger_rows() if r["stage"] == s])
            for s in sorted({r["stage"] for r in ledger_rows()})
        },
        complete_replicates={
            f"{stage}/{arm}/replicate{seed}": metrics(rr)
            for (stage, arm, seed), rr in complete.items()
        },
        completed_replicate_comparisons=comparisons,
        complete_online_operating_costs=online_economics,
        limitations="User-requested checkpoint, not a final study verdict. Only full forty-problem replicates are compared here; partial replicate outcomes remain in the completed-cell inventory and all spending. The registered two-replicate main comparison is unfinished. No pending attempt is counted as a failure or a success.",
    )
    save(REPORT / "checkpoint_results.json", result)
    save(REPORT / "checkpoint_chronology.json", chronology_data)
    compact = [
        dict(
            {
                k: v
                for k, v in r.items()
                if k not in ("checks", "config", "value", "turns")
            },
            trace_summary=characterize(r),
        )
        for r in rows
    ]
    save(REPORT / "checkpoint_cells.json", compact)
    indexed = {r["cell"]: r for r in compact}
    mechanism_groups = {
        key: [indexed[r["cell"]] for r in values]
        for key, values in complete.items()
    }
    mechanism_pairs: dict[str, Any] = {}
    for label, comparison in comparisons.items():
        stage, arm, replicate = label.split("/")
        seed = int(replicate.removeprefix("replicate"))
        mechanism_pairs[label] = contributions(
            mechanism_groups[stage, comparison["baseline"], seed],
            mechanism_groups[stage, arm, seed],
        )
    save(
        REPORT / "checkpoint_mechanisms.json",
        dict(
            complete_replicates={
                f"{stage}/{arm}/replicate{seed}": aggregate(values)
                for (stage, arm, seed), values in mechanism_groups.items()
            },
            comparisons=mechanism_pairs,
            interpretation="Observable cost contributions on full individual replicates, not bullet-level causal attribution or the pooled study verdict.",
        ),
    )
    receipt_audit(REPORT / "checkpoint_receipt_certification.json")
    learning_scope(REPORT / "checkpoint_learning_scope.json")
    from .checkpoint_budget import run as budget_snapshot

    budget_snapshot(rows)
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k
                not in (
                    "main_source_contract",
                    "closed_batches",
                    "pending_batches",
                    "completed_replicate_comparisons",
                    "user_hold",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
