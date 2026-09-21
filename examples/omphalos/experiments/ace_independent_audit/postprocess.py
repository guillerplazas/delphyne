"""Run the existing offline finalizers when every registered batch closes.

This worker never launches solver or author experiments. It supports both
harnesses and can wait in tmux alongside the already active paid dispatcher.
Numerical finalization does not mark the investigator's narrative reports as
finished. Failures retain their evidence and stop this worker without retrying
or replacing any model response.
"""

import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time

from .common import CAMPAIGN, REPORT, now, read, save, sha
from .completion import require_closed
from .economics import ledger_rows
from .study_certification import batches

STEPS = (
    ("verification", "run-completed"),
    ("budget_replay", "run-completed"),
    ("fresh",),
    ("rule_repairs", "assess"),
    ("adaptive_frozen", "assess"),
    ("mechanisms",),
    ("economics", "finalize"),
    ("certification", "finalize"),
    ("study_certification",),
    ("rate_diagnosis",),
    ("budget_replay", "finalize"),
    ("tables",),
    ("figures", "final"),
)


def pending() -> list[str]:
    result: list[str] = []
    for batch in batches():
        try:
            require_closed(batch)
        except (ValueError, FileNotFoundError, BlockingIOError):
            certificate = CAMPAIGN / "terminal_failures" / (batch + ".json")
            if not certificate.exists():
                result.append(batch)
                continue
            from .terminal_failure import assert_closed

            assert_closed(batch)
    preparation = read(CAMPAIGN / "rate_recovery/preparation.json")
    if any(
        not (
            CAMPAIGN / "rate_recovery/certificates" / (identity + ".json")
        ).exists()
        for identity in preparation["interrupted"]
    ):
        result.append("rate-continuation-certificates")
    states = {r["status"] for r in ledger_rows()}
    if states - {"settled", "bounded_charge"}:
        result.append("unsettled-receipts")
    return result


def run() -> None:
    lock = CAMPAIGN / "postprocess.lock"
    with lock.open("a") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        destination = REPORT / "numerical_finalization.json"
        if destination.exists():
            prior = read(destination)
            for name, expected in prior["final_artifacts"].items():
                if sha(REPORT / name) != expected:
                    raise ValueError("A finalized numerical artifact changed")
            print(
                "Numerical finalization already completed; no work repeated."
            )
            return
        while True:
            if (CAMPAIGN / "PAUSED").exists():
                raise ValueError("Dispatch is paused; preserve the incident")
            remaining = pending()
            if not remaining:
                break
            print(json.dumps(dict(at=now(), awaiting=remaining)), flush=True)
            time.sleep(60)
        finished: list[list[str]] = []
        for module, *args in STEPS:
            command = [
                sys.executable,
                "-m",
                "experiments.ace_independent_audit." + module,
                *args,
            ]
            print(json.dumps(dict(at=now(), command=command)), flush=True)
            subprocess.run(command, check=True)
            finished.append([module, *args])
        names = (
            "study_certification.json",
            "receipt_certification.json",
            "fresh_results.json",
            "rule_repair_results.json",
            "adaptive_frozen_results.json",
            "final_economics.json",
            "budget_replay_results.json",
            "serving_results.csv",
            "budget_frontier.json",
            "rate_diagnosis.json",
        )
        save(
            destination,
            dict(
                at=now(),
                driver_sha=sha(Path(__file__)),
                completed_steps=finished,
                final_artifacts={name: sha(REPORT / name) for name in names},
                paid_calls=0,
                note="Numerical finalization complete. Narrative synthesis and review are tracked separately; this certificate does not label the old checkpoint reports as final.",
            ),
        )
        print("Registered numerical finalizers completed.", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["check"]:
        print(json.dumps(dict(awaiting=pending()), indent=2))
    elif sys.argv[1:] == ["run"]:
        run()
    else:
        raise SystemExit("Use check or run")
