"""A matched generic control for the distinct training coverage candidate.

Training selected ordinary ACE on cost/solve and the 8192-output-token arm
on coverage. The primary controller therefore equals the ordinary baseline,
so its matched non-ACE panel and incumbent-book panel are duplicates. Use
one of those unused optional comparison slots for exactly 40 validationX
problems x two replicates with the coverage candidate's controller and an
empty book. This isolates generic headroom from the playbook, within the
same $25 ceiling and four-panel total. No new seed or validation-led tuning.

Register after training selection but BEFORE any validation cell exists.
Run only after the original benchmark completes; all $8 liability must fit.
Both harnesses: python -m experiments.ace_sanitized_headroom register|run.
"""

from dataclasses import asdict
from pathlib import Path
import random
import sys

from experiments.ace_sanitized import campaign as c
from experiments.ace_sanitized.control import Controls
from experiments.ace_sanitized.workflow import panel, verify_freeze


def register() -> None:
    c.verify()
    if (c.OUTPUT / "validation").exists():
        raise ValueError("Register before opening any validation run")
    frozen = verify_freeze()
    ordinary = asdict(Controls())
    primary = frozen["treatments"][frozen["primary"]]
    coverage = frozen["treatments"][frozen["coverage"]]
    if primary["controls"] != ordinary or primary["book"] != "incumbent":
        raise ValueError(
            "This amendment requires both redundant primary controls"
        )
    if coverage["controls"] == ordinary:
        raise ValueError("No distinct coverage controller to match")
    c.save(
        "headroom_protocol.json",
        dict(
            protocol=__doc__,
            cells=80,
            cap=0.10,
            worst_case_dollars=8.0,
            controls=coverage["controls"],
            book="empty",
            arm="agentic_coverage",
            primary_unchanged=True,
            new_seeds=False,
            ceiling=c.CEILING,
            source_sha256=c.sha(Path(__file__)),
            freeze_sha256=c.sha(c.CAMPAIGN / "freeze.json"),
        ),
    )


def run() -> None:
    c.verify()
    p = c.read("headroom_protocol.json")
    if p["source_sha256"] != c.sha(Path(__file__)):
        raise ValueError("Headroom protocol implementation drift")
    if p["freeze_sha256"] != c.sha(c.CAMPAIGN / "freeze.json"):
        raise ValueError("Training selection drift")
    finished = c.read("benchmark_finished.json")
    labels = {label for label, _ in finished["panels"]}
    if "ace_coverage" not in labels:
        c.save(
            "headroom_finished.json",
            dict(
                completed=False,
                reason="Coverage candidate panel was not funded",
            ),
        )
        return
    jobs = panel(p["arm"], dict(controls=p["controls"], book="empty"))
    random.Random(20260917).shuffle(jobs)
    completed = c.launch("matched_headroom", jobs)
    c.save(
        "headroom_finished.json",
        dict(
            completed=completed,
            cells=80 if completed else 0,
            reason="complete"
            if completed
            else "Entire $8 liability does not fit",
            accounting=c.accounting(),
        ),
    )


if __name__ == "__main__":
    if sys.argv[1:] == ["register"]:
        register()
    elif sys.argv[1:] == ["run"]:
        run()
    else:
        raise SystemExit("register | run")
