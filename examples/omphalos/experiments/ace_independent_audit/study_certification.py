"""Final denominator, solver-contract, replay and proof reconciliation."""

from concurrent.futures import ThreadPoolExecutor
import json
from typing import Any

from . import campaign as c
from .audit import load_yaml
from .common import CAMPAIGN, OUTPUT, REPORT, ROOT, allowed, read, save, sha
from .completion import require_closed
from .economics import ledger_rows, paid
from .cost_bounds import total_interval
from .fresh import receipts, solver_rows
from .verification import compile_one


def batches() -> list[str]:
    return [
        "source",
        "author_pilot",
        *[
            entry["batch"]
            for entry in read(CAMPAIGN / "core_schedule.json")["batches"]
        ],
        *[
            f"online-o{order}-s{step:02d}"
            for order in (0, 1)
            for step in range(40)
        ],
        "rule_repairs",
        "adaptive_frozen",
    ]


def contracts(names: list[str]) -> dict[str, Any]:
    reference: dict[str, str] | None = None
    hashes: dict[str, str] = {}
    count = 0
    for batch in names:
        if batch in ("source", "author_pilot"):
            continue
        recorded = read(CAMPAIGN / "batch_sources" / (batch + ".json"))
        if reference is None:
            reference = recorded
        elif recorded != reference:
            raise ValueError(
                "Paid final-study solver code differs between batches: "
                + batch
            )
        for filename, expected in recorded.items():
            if sha(ROOT / filename) != expected:
                raise ValueError("Paid solver source changed: " + filename)
            hashes[filename] = expected
        count += 1
    if count != 94:
        raise ValueError("Final-study batch denominator changed")
    return dict(batches=count, matched_source_hashes=hashes, passed=True)


def run() -> None:
    names = batches()
    ledger = receipts()
    rows = [
        *solver_rows("source", ledger),
        *solver_rows("author_pilot", ledger),
        *read(REPORT / "fresh_cells.json"),
        *read(REPORT / "rule_repair_cells.json"),
        *read(REPORT / "adaptive_frozen_cells.json"),
    ]
    if len(rows) != 2044 or len({r["cell"] for r in rows}) != 2044:
        raise ValueError(
            "Expected exactly 2044 unique registered solver cells"
        )
    indexed = {r["cell"]: r for r in rows}
    proof_cells: dict[tuple[str, str, str], list[str]] = {}
    compared: set[str] = set()
    summaries: list[dict[str, Any]] = []
    terminal_cells: set[str] = set()
    for batch in names:
        try:
            require_closed(batch)
        except ValueError:
            from .terminal_failure import assert_closed

            assert_closed(batch)
        jobs = [
            c.Job(**v) for v in read(CAMPAIGN / "batches" / (batch + ".json"))
        ]
        verification = read(CAMPAIGN / "verification" / (batch + ".json"))
        replays = {r["cell"]: r for r in verification["replays"]}
        failures = {
            r["cell"]: r for r in verification.get("terminal_failures", [])
        }
        expected = {c.name(j, None) for j in jobs}
        if replays.keys() | failures.keys() != expected:
            raise ValueError("Exact-replay denominator differs: " + batch)
        if compared & expected:
            raise ValueError("A solver cell appears in two execution batches")
        compared.update(expected)
        for job in jobs:
            identity = c.name(job, None)
            row = indexed[identity]
            directory = OUTPUT / batch / "configs" / identity
            if identity in failures:
                from .terminal_failure import hashes as failure_hashes

                failure = failures[identity]
                if failure_hashes(directory) != failure["hashes"] or failure[
                    "hashes"
                ] != {
                    "result.yaml": None,
                    "cache.yaml": row["cache_sha"],
                    "exception.txt": row["exception_sha"],
                }:
                    raise ValueError("Terminal evidence changed")
                if not all(
                    r["passed"] and r["paid_calls"] == 0
                    for r in failure["replays"]
                ):
                    raise ValueError("Terminal request replay did not pass")
                terminal_cells.add(identity)
            else:
                replay = replays[identity]
                hashes = {
                    n: sha(directory / n)
                    for n in ("result.yaml", "cache.yaml")
                }
                if hashes != replay["hashes"] or hashes != {
                    "result.yaml": row["result_sha"],
                    "cache.yaml": row["cache_sha"],
                }:
                    raise ValueError(
                        "Certification inputs changed: " + identity
                    )
                if not replay["passed"] or replay["paid_calls"] != 0:
                    raise ValueError("Replay did not pass without HTTP")
            if row["tools"] != ["ReadSkill", "SearchRocq"] or set(
                row["models"]
            ) != {"gpt-5.6-luna"}:
                raise ValueError(
                    "Unexpected model/tool capability: " + identity
                )
            if not job.assisted and row["counts"].get("auto_finished", 0):
                raise ValueError(
                    "Plain benchmark received automatic completion"
                )
            if job.output_tokens != 32768:
                raise ValueError("Unexpected output allowance")
            if identity not in failures and (
                abs(
                    row["spent_budget"].get("price", 0) - row["costs"]["price"]
                )
                > 1e-9
            ):
                raise ValueError(
                    "Controller and audited tariff disagree: " + identity
                )
            if job.book_file:
                if sha(CAMPAIGN / job.book_file) != job.book_sha:
                    raise ValueError("Book identity changed: " + identity)
                pb = read(CAMPAIGN / job.book_file)
                if "training_theorems" in pb and any(
                    allowed().get(t, (None,))[0] != "train"
                    for t in pb["training_theorems"]
                ):
                    raise ValueError("Book declares non-training evidence")
            values: list[Any] = (
                []
                if identity in failures
                else load_yaml(directory / "result.yaml")["outcome"]["result"][
                    "values"
                ]
            )
            if bool(values) != row["solved"]:
                raise ValueError("Reported proof outcome changed")
            for value in values:
                if not isinstance(value, str):
                    raise ValueError(
                        "Benchmark returned something other than a proof script"
                    )
                key = (allowed()[job.theorem][1], job.theorem, value)
                proof_cells.setdefault(key, []).append(identity)
        summaries.append(
            dict(
                batch=batch,
                cells=len(jobs),
                replayed=len(replays),
                terminal_failures=len(failures),
            )
        )
    if compared != indexed.keys():
        raise ValueError("Final certification omitted or added a solver cell")
    with ThreadPoolExecutor(max_workers=8) as pool:
        kernels = [
            dict(result, cells=proof_cells[key])
            for key, result in zip(
                proof_cells, pool.map(compile_one, proof_cells), strict=True
            )
        ]
    if not all(k["passed"] for k in kernels):
        raise ValueError("A returned proof failed independent compilation")
    solver_bill = paid([r for r in ledger_rows() if r["stage"] == "solver"])
    costs = sum(r["costs"]["price"] for r in rows)
    if abs(costs - solver_bill["cost"]) > 1e-8:
        raise ValueError(
            "Registered solver cells do not reconcile to all solver receipts"
        )
    if any(
        abs(a - b) > 1e-8
        for a, b in zip(
            total_interval(rows),
            solver_bill.get("cost_interval", [costs, costs]),
            strict=True,
        )
    ):
        raise ValueError("Solver invoice intervals do not reconcile")
    expected_requests = sum(r["counts"].get("requests", 0) for r in rows)
    if expected_requests != solver_bill["requests"]:
        raise ValueError(
            "Some paid solver request is absent from the registered cells"
        )
    frozen = read(CAMPAIGN / "adaptive_frozen_at.json")
    from datetime import datetime

    first_serving = min(
        r["created"] for r in ledger_rows() if "__O1__" in r["cell"]
    )
    if first_serving < datetime.fromisoformat(frozen["at"]).timestamp():
        raise ValueError("Adaptive serving began before the book was frozen")
    result = dict(
        passed=True,
        solver_cells=len(rows),
        batches=summaries,
        exact_replays=len(rows) - len(terminal_cells),
        terminal_prefix_and_request_replays=len(terminal_cells),
        terminal_prefix_and_rejection_replays=sum(
            r.get("terminal_failure") == "provider_context_length_exceeded"
            for r in rows
        ),
        terminal_failure_cells=sorted(terminal_cells),
        unique_proofs=len(kernels),
        proved_cells=sum(r["solved"] for r in rows),
        independent_kernel_checks=kernels,
        solver_bill=solver_bill,
        billing_certification="All returned usage is exact; any explicitly approved bounded timeout is listed in solver_bill with its full retained liability. Certification of the interval does not claim an exact invoice for the lost response.",
        contracts=contracts(names),
        scope="Only trainX/validationX. Luna is every benchmark solver; exactly ReadSkill and SearchRocq are offered. Plain cells receive no automatic completion. Every paid solver receipt belongs to one registered cell.",
        supplements="Core+author/short-book follow-ups1520, rule repairs80, adaptive-frozen160, source80, author pilot204. Model-free budget replays do not inflate this denominator.",
    )
    save(REPORT / "study_certification.json", result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "passed",
                    "solver_cells",
                    "exact_replays",
                    "unique_proofs",
                    "proved_cells",
                    "solver_bill",
                )
            }
        )
    )


if __name__ == "__main__":
    run()
