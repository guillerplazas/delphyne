"""Resume the registered frozen batches after the user's API continuation.

Both harnesses run ``python -m experiments.ace_independent_audit.resumption``.
The immutable resumption record changes dispatch order and worker allocation
only. It adds no cells, changes no treatment, and never resumes R1's retained
terminal failure. Online order zero runs through its existing entry point.
"""

import fcntl
import subprocess

from .common import CAMPAIGN, OUTPUT, read
from .completion import require_closed
from .workflow import launch


def running(batch: str) -> bool:
    """Inspect the existing launch lock without starting another launcher."""
    lock = OUTPUT / batch / ".launch.lock"
    if not lock.exists():
        return False
    with lock.open() as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
    return False


def finish(batch: str) -> None:
    """Keep returned context failures; certify them instead of relaunching."""
    try:
        require_closed(batch)
    except ValueError:
        from .terminal_failure import assert_closed, run as audit_terminal

        certificate = CAMPAIGN / "terminal_failures" / (batch + ".json")
        if certificate.exists():
            assert_closed(batch)
        else:
            # This rejects unknown failures, incomplete workers and billing.
            audit_terminal(batch)


def run() -> None:
    plan = read(CAMPAIGN / "resumption.json")
    overlap = read(CAMPAIGN / "resumption_overlap_amendment.json")
    deferred: list[str] = []
    for batch in plan["frozen_batches"]:
        if batch == overlap["batch"] and running(batch):
            deferred.append(batch)
            print(dict(batch=batch, already_running=True), flush=True)
            continue
        if (OUTPUT / batch / "experiment.yaml").exists():
            # A returned failure requires investigation, never replacement.
            finish(batch)
            print(dict(batch=batch, already_complete=True), flush=True)
            continue
        completed_online = sum(
            (
                CAMPAIGN
                / "online_events"
                / f"online-o{order}-s{step:02d}.json"
            ).exists()
            for order in (0, 1)
            for step in range(40)
        )
        workers = 16 if completed_online == 80 else 11
        if running(overlap["batch"]):
            workers = min(workers, 16 - overlap["workers"])
        try:
            launch(batch, workers=workers)
        except subprocess.CalledProcessError:
            # A nonzero launcher status is not an instruction to replace
            # attempts. Only completed, auditable outcomes may proceed.
            finish(batch)
        else:
            finish(batch)
        print(dict(batch=batch, completed=True, workers=workers), flush=True)
    for batch in deferred:
        with (OUTPUT / batch / ".launch.lock").open() as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH)
        finish(batch)
        print(dict(batch=batch, overlap_complete=True), flush=True)


if __name__ == "__main__":
    run()
