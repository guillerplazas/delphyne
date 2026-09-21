"""Audit a returned context-limit failure without replacing its attempt.

The paid solver is unchanged. A local copy of the cache must replay every
preceding response and reach exactly the persisted rejected request. HTTP
is forbidden; that request is replaced by a sentinel exception, not a new
model answer. The failed cell remains unsolved with all incurred charges.
"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import redirect_stdout
from dataclasses import replace
import fcntl
import gzip
import io
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.tasks import run_command
from pydantic import TypeAdapter

from runtime.campaign_budget import CampaignResponsesModel

from . import campaign as c
from .audit import cell, load_yaml
from .common import CAMPAIGN, OUTPUT, allowed, read, save, sha
from .completion import ground_truth
from .economics import ledger_rows
from .transport import AuditModel


class ObservedRejection(Exception):
    """The exact saved terminal request was reached without HTTP."""


def hashes(directory: Path) -> dict[str, Any]:
    return {
        "cache.yaml": sha(directory / "cache.yaml"),
        "exception.txt": sha(directory / "exception.txt"),
        "result.yaml": None,
    }


def replay_failure(
    batch: str, job: c.Job, rejected: dict[str, Any], cap: float
) -> dict[str, Any]:
    c.activate()
    import os

    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
        CAMPAIGN / "terminal_replay_events.jsonl"
    )
    directory = OUTPUT / batch / "configs" / c.name(job, None)
    original_hashes = hashes(directory)
    observed: list[dict[str, Any]] = []

    def reject(_model: AuditModel, request: LLMRequest) -> None:
        encoded = TypeAdapter(LLMRequest).dump_python(request, mode="json")
        if encoded != rejected["request"]:
            raise AssertionError("An unexpected request missed the cache")
        observed.append(encoded)
        raise ObservedRejection

    with tempfile.TemporaryDirectory(
        prefix="terminal-replay-", dir=CAMPAIGN
    ) as tmp:
        copied = Path(tmp) / "cache.yaml"
        shutil.copyfile(directory / "cache.yaml", copied)
        args = job.instantiate(None)
        args.budget = dict(price=cap, num_requests=32)
        args.cache_file = str(copied)
        args.cache_mode = "read_write"
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(AuditModel, "_send_final_request", reject),
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("HTTP forbidden"),
            ),
            patch(
                "openai.OpenAI", side_effect=AssertionError("HTTP forbidden")
            ),
            redirect_stdout(io.StringIO()),
        ):
            try:
                run_command(
                    run_strategy,
                    args,
                    ctx=replace(c.context(), cache_root=Path("/")),
                    add_header=False,
                )
            except ObservedRejection:
                pass
            else:
                raise ValueError("Expected the saved terminal rejection")
    if len(observed) != 1 or hashes(directory) != original_hashes:
        raise ValueError("Terminal replay changed or omitted evidence")
    return dict(
        cap=cap, exact_rejected_request=True, paid_calls=0, passed=True
    )


def certify(batch: str, job: c.Job) -> dict[str, Any]:
    identity = c.name(job, None)
    directory = OUTPUT / batch / "configs" / identity
    destination = CAMPAIGN / "terminal_failures" / (identity + ".json")
    if destination.exists():
        prior = read(destination)
        if prior["hashes"] != hashes(directory):
            raise ValueError("Terminal evidence changed")
        return prior
    if (directory / "result.yaml").exists():
        raise ValueError(
            "Unexpected partial result needs separate reconciliation"
        )
    row = cell((str(directory), job.theorem))
    receipts = sorted(
        [r for r in ledger_rows() if r["cell"] == identity],
        key=lambda r: r["created"],
    )
    if not receipts or any(r["status"] != "settled" for r in receipts):
        raise ValueError("Terminal billing is not settled")
    raw: list[dict[str, Any]] = []
    for receipt in receipts:
        with gzip.open(
            CAMPAIGN / "responses" / identity / (receipt["id"] + ".json.gz"),
            "rt",
        ) as stream:
            raw.append(json.load(stream))
    rejected = raw[-1]
    if (
        any("exception" in r for r in raw[:-1])
        or rejected.get("exception", {}).get("type") != "BadRequestError"
        or not rejected["exception"]["rejected"]
        or "context_length_exceeded" not in rejected["exception"]["message"]
        or receipts[-1]["charged"] != 0
        or row["counts"]["requests"] != len(receipts) - 1
        or not row["exact_cost"]
        or abs(row["costs"]["price"] - sum(r["charged"] for r in receipts))
        > 1e-9
    ):
        raise ValueError("Unrecognized terminal failure or unreconciled cost")
    replays = [
        replay_failure(batch, job, rejected, cap)
        for cap in (0.10, 0.05, 0.075, 0.09)
    ]
    certificate = dict(
        cell=identity,
        batch=batch,
        hashes=hashes(directory),
        failure="provider_context_length_exceeded",
        solved=False,
        cost=row["costs"]["price"],
        successful_api_responses=len(receipts) - 1,
        attempted_api_requests=len(receipts),
        rejected_zero_charge=1,
        receipts=[r["id"] for r in receipts],
        last_successful_input_tokens=raw[-2]["response"]["usage"][
            "input_tokens"
        ],
        rejected_serialized_input_bound=rejected["input_bound"],
        exception=rejected["exception"],
        replays=replays,
        interpretation="Terminal failed attempt, retained in the denominator. The final 400 has zero charge; every preceding paid response remains charged. The input bound is not a provider token count. Exact cached-prefix and rejected-request replay uses no HTTP. No replacement attempt or paid-source edit.",
    )
    save(destination, certificate)
    save(
        CAMPAIGN / "budget_replay" / (identity + ".json"),
        dict(
            hashes=certificate["hashes"],
            batch=batch,
            rows=[
                dict(
                    cell=identity,
                    arm=job.arm,
                    stage=job.stage,
                    theorem=job.theorem,
                    seed=job.seed,
                    cap=rr["cap"],
                    solved=False,
                    spent_budget=dict(
                        price=certificate["cost"],
                        num_requests=len(receipts) - 1,
                    ),
                    attempted_requests=len(receipts),
                    paid_calls=0,
                    terminal_failure=certificate["failure"],
                )
                for rr in replays
                if rr["cap"] < 0.10
            ],
        ),
    )
    return certificate


def assert_closed(batch: str) -> None:
    directory = OUTPUT / batch
    with (directory / ".launch.lock").open() as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
        state = load_yaml(directory / "experiment.yaml")
        for identity, info in state["configs"].items():
            if not info.get("end_time") or info.get("interruption_time"):
                raise ValueError("Worker did not return normally")
            folder = directory / "configs" / identity
            if info["status"] == "done" and ground_truth(folder) == "done":
                continue
            certificate = read(
                CAMPAIGN / "terminal_failures" / (identity + ".json")
            )
            if info["status"] != "failed" or certificate["hashes"] != hashes(
                folder
            ):
                raise ValueError("Uncertified terminal worker")


def completed_result(batch: str, identity: str) -> dict[str, Any]:
    directory = OUTPUT / batch / "configs" / identity
    if ground_truth(directory) != "done":
        raise ValueError("Normal replay requires a completed worker receipt")
    return load_yaml(directory / "result.yaml")["outcome"]["result"]


def normal_replay(item: tuple[str, c.Job]) -> dict[str, Any]:
    from .verification import replay_one

    with patch(
        "experiments.ace_independent_audit.verification.result",
        completed_result,
    ):
        return replay_one(item)


def normal_budget(item: tuple[str, dict[str, Any]]) -> list[dict[str, Any]]:
    from .budget_replay import replay_cell

    with patch(
        "experiments.ace_independent_audit.budget_replay.result",
        completed_result,
    ):
        return replay_cell(item)


def run(batch: str) -> None:
    from .verification import compile_one

    jobs = [c.Job(**j) for j in read(CAMPAIGN / "batches" / (batch + ".json"))]
    state = load_yaml(OUTPUT / batch / "experiment.yaml")["configs"]
    failures = [
        certify(batch, j)
        for j in jobs
        if state[c.name(j, None)]["status"] == "failed"
    ]
    assert_closed(batch)
    normal = [j for j in jobs if state[c.name(j, None)]["status"] == "done"]
    with ProcessPoolExecutor(max_workers=8) as pool:
        replays = list(pool.map(normal_replay, [(batch, j) for j in normal]))
    proofs: dict[tuple[str, str, str], list[str]] = {}
    for job in normal:
        identity = c.name(job, None)
        for proof in completed_result(batch, identity)["values"]:
            key = (allowed()[job.theorem][1], job.theorem, str(proof))
            proofs.setdefault(key, []).append(identity)
    with ThreadPoolExecutor(max_workers=8) as pool:
        kernels = [
            dict(result, cells=proofs[key])
            for key, result in zip(
                proofs, pool.map(compile_one, proofs), strict=True
            )
        ]
    if not all(k["passed"] for k in kernels):
        raise ValueError("A returned proof failed independent compilation")
    save(
        CAMPAIGN / "verification" / (batch + ".json"),
        dict(
            replays=replays,
            kernel=kernels,
            terminal_failures=failures,
        ),
    )
    from dataclasses import asdict

    with ProcessPoolExecutor(max_workers=8) as pool:
        budget = list(
            pool.map(normal_budget, [(batch, asdict(j)) for j in normal])
        )
    save(
        CAMPAIGN / "terminal_failures" / (batch + ".json"),
        dict(
            batch=batch,
            attempts=len(jobs),
            normal_completions=len(normal),
            failures=failures,
            normal_replays=len(replays),
            budget_scenarios=sum(map(len, budget)) + 3 * len(failures),
            source_state_sha=sha(OUTPUT / batch / "experiment.yaml"),
            paid_calls=0,
        ),
    )
    print(
        json.dumps(
            dict(
                batch=batch,
                returned_attempts=len(jobs),
                normal=len(normal),
                terminal_failures=len(failures),
                paid_calls=0,
            )
        )
    )


if __name__ == "__main__":
    import sys

    registered = {
        "rule_repairs",
        "adaptive_frozen",
        *[
            r["batch"]
            for r in read(CAMPAIGN / "core_schedule.json")["batches"]
        ],
    }
    if len(sys.argv) != 2 or sys.argv[1] not in registered:
        raise SystemExit(
            "Supply a registered frozen batch with a returned failure"
        )
    run(sys.argv[1])
