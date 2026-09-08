"""Continue the registered review after its three initial tmux launches.

Every paid cell still runs through OmphalosExperiment and the $50 ledger.
This orders campaign stages; it does not supervise or kill worker pools.
Run from either harness, in tmux after sourcing the server environment.
Decision files are written only for complete panels. Stops on admission
exhaustion; a recorded capacity transfer can then permit a resume.
"""

# pyright: strict

import fcntl
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import omphalos_launch as ol  # noqa: E402
from ace_review_experiment import (  # noqa: E402
    CAMPAIGN,
    activate_budget,
    campaign_profile,
    experiment,
    name,
)
from ace_review_report import calibration, final_report, selection  # noqa: E402
from campaign_budget import CampaignExhausted  # noqa: E402


def wait_session(session: str) -> None:
    while (
        subprocess.run(
            ["tmux", "has-session", "-t", session], capture_output=True
        ).returncode
        == 0
    ):
        time.sleep(15)


def run_phase(phase: str, requests: int = 32, arm: str = "all") -> None:
    print(f"Starting {phase}/{arm}, requests={requests}", flush=True)
    activate_budget(phase)
    exp = experiment(phase, requests, arm)
    exp.load()
    assert exp.configs is not None
    names = {name(c, None) for c in exp.configs}
    # A resumed coordinator must not grant extra retries to a cell that
    # already had its two additional attempts. The pre-HTTP credential
    # incident is excluded from this count.
    for _ in range(3):
        retryable: set[str] = set()
        for cell in names:
            directory = exp.absolute_output_dir / "configs" / cell
            if ol.ground_truth(directory) != "failed":
                continue
            text = (directory / "exception.txt").read_text()
            if "CampaignExhausted" in text:
                retryable.add(cell)
                continue
            previous = [
                p
                for p in directory.glob("exception.txt.bak-*")
                if not any(
                    marker in p.read_text()
                    for marker in ("OPENAI_API_KEY", "CampaignExhausted")
                )
            ]
            if len(previous) < 2:
                retryable.add(cell)
        if retryable:
            exp.retry_failed(names=retryable)
        exp.resume(max_workers=campaign_profile().workers, log_progress=False)
        failed = [
            cell
            for cell in names
            if ol.ground_truth(exp.absolute_output_dir / "configs" / cell)
            == "failed"
        ]
        if any(
            "CampaignExhausted"
            in (
                exp.absolute_output_dir / "configs" / cell / "exception.txt"
            ).read_text()
            for cell in failed
        ):
            raise CampaignExhausted(f"{phase}: allocation exhausted")
        if not failed:
            break
    for cell in names:
        directory = exp.absolute_output_dir / "configs" / cell
        if ol.ground_truth(directory) == "todo":
            raise RuntimeError(f"incomplete: {cell}")
        exc = directory / "exception.txt"
        if exc.exists() and "CampaignExhausted" in exc.read_text():
            raise CampaignExhausted(f"{phase}: allocation exhausted")
    print(f"Finished {phase}/{arm}", flush=True)


def main() -> None:
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    with (CAMPAIGN / ".coordinator.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        wait_session("ace-review-calibration")
        if not (CAMPAIGN / "calibration.json").exists():
            run_phase("calibration")
            decision = calibration()
        else:
            decision = json.loads((CAMPAIGN / "calibration.json").read_text())
        requests = int(decision["requests"])
        if not (CAMPAIGN / "selection.json").exists():
            run_phase("development", requests, "baseline")
            run_phase("development", requests, "x3")
            for seed in (0, 1):
                wait_session(f"ace-review-repair{seed}")
                artifact = (
                    ROOT
                    / f"experiments/playbooks/ace_review_repair_s{seed}.yaml"
                )
                if not artifact.exists():
                    raise RuntimeError(
                        f"training has not frozen {artifact.name}"
                    )
                run_phase("development", requests, f"repair{seed}")
            selection()
        run_phase("confirmation", requests)
        run_phase("terra", 32)
        final_report()
        print("Registered ACE campaign complete.", flush=True)


if __name__ == "__main__":
    main()
