"""Continue after the completed handoff's unpaid initialization failure.

The stdlib treats an existing lock-only directory as initialized. Create its
ordinary empty ExperimentState through the existing serializer, guarded by
zero receipts and no execution artifacts. No framework source is changed.
Both harnesses run this module after the retained handoff certificate.
"""

import fcntl
import json
from pathlib import Path
import sys
from unittest.mock import patch

from delphyne.stdlib.experiments import experiment_launcher as el
from experiments.common.omphalos_launch import OmphalosExperiment, launch_lock

from . import concurrent_rate as rate
from . import rate_recovery as old
from .common import CAMPAIGN, OUTPUT, now, read, save, sha
from .completion import require_closed
from .economics import ledger_rows


def initialize_lock_only(batch: str) -> None:
    directory = OUTPUT / batch
    jobs = old.jobs(batch)
    if any(r["cell"] in jobs for r in ledger_rows()):
        raise ValueError(
            "The intended batch already has paid/rejected requests"
        )
    if {p.name for p in directory.iterdir()} != {".launch.lock"}:
        raise ValueError("Expected only the handoff's launch lock")
    with launch_lock(directory):
        experiment = OmphalosExperiment(
            config_class=old.c.Job,
            configs=list(jobs.values()),
            context=old.c.context(),
            output_dir=str(directory),
            config_naming=old.c.name,
            attempts=1,
            wait_for_slots=True,
        )
        experiment._save_state(el.ExperimentState[old.c.Job](None, None, {}))  # pyright: ignore[reportPrivateUsage]
        experiment.load()
        if experiment.get_status() != dict(todo=len(jobs), done=0, failed=0):
            raise ValueError("Initialized batch differs from its registration")


def run() -> None:
    with (rate.FOLDER / "driver.lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        handoff = read(rate.FOLDER / "handoff.json")
        if (
            not handoff["original_process_exited"]
            or handoff["canceled_requests"] != 0
            or sha(Path(rate.__file__)) != handoff["source_sha"]
        ):
            raise ValueError("The handoff or scheduler source changed")
        require_closed(old.BATCH)
        first, *following = old.FOLLOWING
        old.check_sources(first)
        if (CAMPAIGN / "PAUSED").exists():
            raise ValueError("Preserve the active pause")
        initialize_lock_only(first)
        save(
            rate.FOLDER / "queue_start.json",
            dict(
                at=now(),
                driver_sha=sha(Path(__file__)),
                scheduler_sha=sha(Path(rate.__file__)),
                handoff_sha=sha(rate.FOLDER / "handoff.json"),
                original_start_sha=sha(old.FOLDER / (first + "-start.json")),
                registered_cells=sum(len(old.jobs(b)) for b in old.FOLLOWING),
                model_api_calls_before_initialization=0,
                note="Initialize the lock-only directory with the ordinary serializer; retain the original start record and run the original cells exactly once.",
            ),
        )
        argv = ["concurrent_queue", "run", "--max_workers=4", "--wait"]
        with rate.paced_transport(), patch.object(sys, "argv", argv):
            old.c.run_batch(first)
        require_closed(first)
        old.certify_batch(first)
        with patch.object(old, "paced_transport", rate.paced_transport):
            for batch in following:
                old.run_batch(batch, continuation=False)
        print(
            json.dumps(dict(at=now(), original_queue_complete=True)),
            flush=True,
        )


if __name__ == "__main__":
    run()
