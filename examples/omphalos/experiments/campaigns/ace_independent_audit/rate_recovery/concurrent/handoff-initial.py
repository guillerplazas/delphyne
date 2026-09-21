"""Drain the old batch, then continue the original queue with shared TPM.

Both harnesses: python -m experiments.ace_independent_audit.concurrent_handoff
The next batch's standard launch lock prevents the old runner advancing. It
finishes all current cells and certificates, then exits at its existing
already-running guard. No process signal, paid cancellation or replay occurs.
"""

import fcntl
import json
from pathlib import Path
import time
from unittest.mock import patch

from experiments.common.omphalos_launch import launch_lock, parse_holder

from . import concurrent_rate as rate
from . import rate_recovery as old
from .common import CAMPAIGN, OUTPUT, now, read, save, sha
from .completion import require_closed
from .economics import ledger_rows


def process_identity(pid: int) -> tuple[str, str] | None:
    """PID plus kernel start time avoid waiting on a recycled PID."""
    try:
        path = Path("/proc") / str(pid)
        command = (path / "cmdline").read_bytes().replace(b"\0", b" ")
        fields = (path / "stat").read_text().rsplit(")", 1)[1].split()
        if fields[0] == "Z":
            return None
        return command.decode(), fields[19]
    except FileNotFoundError:
        return None


def check_ready() -> None:
    require_closed(old.BATCH)
    preparation = read(old.FOLDER / "preparation.json")
    for identity in preparation["interrupted"]:
        if not read(old.FOLDER / "certificates" / (identity + ".json"))[
            "passed"
        ]:
            raise ValueError("Missing continuation certificate")
    if {r["status"] for r in ledger_rows()} - {"settled", "bounded_charge"}:
        raise ValueError("An unresolved request prevents handoff")
    if any((OUTPUT / b / "experiment.yaml").exists() for b in old.FOLLOWING):
        raise ValueError("A following batch has already started")
    if (CAMPAIGN / "PAUSED").exists():
        raise ValueError("An unresolved pause prevents handoff")


def seed_recent_usage() -> None:
    """Do not treat the preceding dispatcher's last minute as free capacity."""
    gate = rate.Gate(rate.FOLDER)
    with gate.state() as state:
        if state["entries"] or state["waiting"]:
            raise ValueError("The concurrent scheduler has already been used")
        for receipt in ledger_rows():
            if receipt["created"] <= time.time() - rate.WINDOW_SECONDS:
                continue
            if receipt["status"] != "settled":
                raise ValueError("A recent request is not settled")
            usage = receipt["usage"]
            if "input_tokens" not in usage:
                continue
            state["entries"][receipt["id"]] = dict(
                active=False,
                started=receipt["created"],
                tokens=max(
                    32768, usage["input_tokens"] + usage["output_tokens"]
                ),
                cell=receipt["cell"],
                inherited=True,
            )
        gate.event(event="inherited_window", entries=state["entries"])


def run() -> None:
    rate.FOLDER.mkdir(parents=True, exist_ok=True)
    with (rate.FOLDER / "driver.lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        holder = parse_holder(
            (OUTPUT / old.BATCH / ".launch.lock").read_text()
        )
        pid = int(holder["pid"])
        identity = process_identity(pid)
        if (
            identity is None
            or "ace_independent_audit.rate_recovery run" not in identity[0]
        ):
            raise ValueError("Expected the original rate recovery process")
        if not old.running(old.BATCH):
            raise ValueError("The original batch is no longer active")
        # Load the already installed tokenizer before accepting ownership
        # of the next batch. No paid request depends on downloading it.
        rate.estimate_payload([], 0, 32768)
        old.check_sources(old.BATCH)
        if (
            sha(Path(old.__file__))
            != read(old.FOLDER / (old.BATCH + "-start.json"))["source_sha"]
        ):
            raise ValueError("The running recovery source changed")
        with launch_lock(OUTPUT / old.FOLLOWING[0]):
            if any(
                (OUTPUT / b / "experiment.yaml").exists()
                for b in old.FOLLOWING
            ):
                raise ValueError(
                    "Handoff requires unstarted following batches"
                )
            save(
                rate.FOLDER / "amendment.json",
                dict(
                    at=now(),
                    authorization="adapt it so that it is a it less conservative",
                    original_pid=pid,
                    original_process=identity,
                    original_source_sha=sha(Path(old.__file__)),
                    scheduler_sha=sha(Path(rate.__file__)),
                    driver_sha=sha(Path(__file__)),
                    finishing_batch=old.BATCH,
                    remaining_batches=old.FOLLOWING,
                    remaining_cells=sum(
                        len(old.jobs(b)) for b in old.FOLLOWING
                    ),
                    workers=old.WORKERS,
                    simultaneous_http=rate.MAX_IN_FLIGHT,
                    token_target=rate.TOKENS_PER_MINUTE,
                    provider_reported_tpm=500000,
                    docs="https://developers.openai.com/api/docs/guides/rate-limits",
                    note="Resource-only change at a completed batch boundary; model, prompts, tools, budgets, output limits, attempts and receipt accounting unchanged. Preserve actual timing/cache charges; no counterfactual bill.",
                ),
            )
            print(json.dumps(dict(at=now(), draining=old.BATCH)), flush=True)
            while process_identity(pid) == identity:
                if (CAMPAIGN / "PAUSED").exists():
                    raise ValueError("Preserve the new pause before handoff")
                time.sleep(10)
            check_ready()
            seed_recent_usage()
            save(
                rate.FOLDER / "handoff.json",
                dict(
                    at=now(),
                    original_process_exited=True,
                    completed_cells=len(old.jobs(old.BATCH)),
                    continued_cells_certified=87,
                    canceled_requests=0,
                    replacement_attempts=0,
                    source_sha=sha(Path(rate.__file__)),
                ),
            )
        print(
            json.dumps(dict(at=now(), concurrent_queue_started=True)),
            flush=True,
        )
        with patch.object(old, "paced_transport", rate.paced_transport):
            for batch in old.FOLLOWING:
                old.run_batch(batch, continuation=False)


if __name__ == "__main__":
    run()
