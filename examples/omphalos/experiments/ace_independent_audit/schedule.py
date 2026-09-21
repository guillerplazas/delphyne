"""Finite core scheduling alongside the two sequential online curricula.

This changes dispatch concurrency, never cells, prompts, books or budgets.
Six workers leave ten of the registered sixteen Rocq slots for online work.
After both curricula finish, later batches may use all sixteen slots.
"""

from dataclasses import asdict

from . import campaign as c, core, pilot_book_followup
from .common import CAMPAIGN, read, save
from .completion import require_closed
from .workflow import launch


def prepare() -> None:
    core.prepare()
    core.prepare_scaling()
    pilot_book_followup.prepare()
    batches: list[dict[str, object]] = []
    for parent in ("core_frozen", "core_scaling", "core_pilot_book"):
        jobs = [
            c.Job(**v) for v in read(CAMPAIGN / "batches" / f"{parent}.json")
        ]
        for start in range(0, len(jobs), 100):
            batch = parent + f"-part{start // 100:02d}"
            selected = jobs[start : start + 100]
            c.register(batch, selected)
            batches.append(
                dict(batch=batch, parent=parent, cells=len(selected))
            )
        combined = [
            item
            for b in batches
            if b["parent"] == parent
            for item in read(CAMPAIGN / "batches" / f"{b['batch']}.json")
        ]
        if combined != [asdict(j) for j in jobs]:
            raise ValueError("Scheduling changed the registered cells")
    save(
        CAMPAIGN / "core_schedule.json",
        dict(
            batches=batches,
            cells=1120,
            note="800 remaining core cells plus160 author-ablation and160 short-book follow-up cells; 400 core online-track cells run separately. Scientific core total1200, with320 separately registered follow-up cells.",
            concurrency="6 workers until all80 online update events exist, then16 for subsequent batches; never interrupt an active batch to resize",
        ),
    )


def run() -> None:
    schedule = read(CAMPAIGN / "core_schedule.json")
    for entry in schedule["batches"]:
        batch = entry["batch"]
        completed_online = sum(
            (
                CAMPAIGN
                / "online_events"
                / f"online-o{order}-s{step:02d}.json"
            ).exists()
            for order in (0, 1)
            for step in range(40)
        )
        workers = 16 if completed_online == 80 else 6
        launch(batch, workers=workers)
        require_closed(batch)
        print(dict(batch=batch, completed=True, workers=workers), flush=True)


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["run"]:
        run()
    else:
        raise SystemExit("Use prepare or run")
