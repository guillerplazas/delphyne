"""Frozen serving after one adaptive Generator/Reflector/Curator curriculum.

O1 uses the assisted online curriculum's first preselected order, never the
best of its two outcomes. Its book is frozen after all forty updates and
then scored on both development partitions. Existing A0, A2 and P1 cells
supply the comparisons; no baseline cells or seeds are added.
"""

from dataclasses import replace
import json
import subprocess
from typing import Any

from . import campaign as c
from .analysis import metrics, paired
from .common import CAMPAIGN, OUTPUT, REPORT, now, read, save, sha
from .completion import require_closed
from .economics import ledger_rows, paid
from .families import mapping
from .fresh import receipts, solver_rows
from .mechanisms import characterize
from .workflow import book, save_book, launch


def register() -> None:
    path = CAMPAIGN / "adaptive_frozen_protocol.json"
    if path.exists():
        return
    save(
        path,
        dict(
            registered_at=now(),
            arm="O1",
            cells=160,
            curriculum_order=0,
            source_arm="online_A2",
            scope="Forty trainX and forty validationX problems, two replicates each",
            control="Existing A0, A2 and P1 cells; no fresh controls or seeds",
            preparation="One forty-problem adaptive trainX curriculum from empty context, same Luna Generator and Sol-medium Reflector/Curator. The book changes only after each training score. Freeze the book after the fortieth update; no additional terminal audits.",
            estimand="Offline serving of an adaptively trained book versus ordinary non-ACE. Contrasts with A2/P1 are whole preparation recipes: source trajectories, order and audit steps differ, so this is not a single-factor Generator adaptation ablation.",
            motivation="Paper-style offline preparation lets the Generator consume the evolving book during training. Fixed-source A2 isolates author effects but does not test that recipe; online pre-update scores measure a different use case from subsequent frozen serving.",
            selection="Order0 chosen before either curriculum finishes, without comparing their final performance or book contents",
            decision="Report all-attempt cost, coverage and cost per solve, with clustered90% intervals; practical cost target>=10% with at most2 fewer solves per40 on average. No per-replicate veto or default promotion.",
            accounting="Required preparation is this curriculum's forty online_A2 Generator traces plus its eighty reflection/curation outputs and actual retries. Reused controls, other online variants and the other order are study costs, not recipe costs.",
        ),
    )


def prepare() -> None:
    register()
    online = read(CAMPAIGN / "online_protocol.json")
    names = online["independent_orders"][0]
    for step, theorem in enumerate(names):
        batch = f"online-o0-s{step:02d}"
        event = read(CAMPAIGN / "online_events" / (batch + ".json"))
        if event["theorem"] != theorem:
            raise ValueError("Adaptive curriculum order changed")
        for suffix in ("", "-reflect", "-curate"):
            require_closed(batch + suffix)
    final_event = read(CAMPAIGN / "online_events/online-o0-s39.json")
    pb = book(final_event["after"]["A2"])
    filename = "books/O1_adaptive_frozen.json"
    save_book(
        CAMPAIGN / filename,
        pb,
        dict(
            training_theorems=names,
            curriculum_order=0,
            author=online["author"],
            final_event_sha=sha(CAMPAIGN / "online_events/online-o0-s39.json"),
            preparation="One adaptive curriculum; final online_A2 book frozen after40 updates",
        ),
    )
    jobs = [
        replace(j, robust=True)
        for stage in ("train", "validation")
        for j in c.ordered_jobs(stage, [("O1", True, filename)])
    ]
    c.register("adaptive_frozen", jobs)
    path = CAMPAIGN / "adaptive_frozen_at.json"
    if not path.exists():
        save(
            path,
            dict(at=now(), book_sha=sha(CAMPAIGN / filename), cells=len(jobs)),
        )
    print(
        json.dumps(
            dict(
                prepared=True,
                cells=len(jobs),
                bullets=len(pb.bullets),
                characters=len(pb.render_prompt()),
            )
        )
    )


def run() -> None:
    from .resumption import finish

    batch = "adaptive_frozen"
    if (OUTPUT / batch / "experiment.yaml").exists():
        finish(batch)
        print("O1 is already complete, including any audited failure.")
        return
    try:
        launch(batch, workers=16)
    except subprocess.CalledProcessError:
        finish(batch)
    else:
        finish(batch)


def assess() -> None:
    rows = solver_rows(
        "adaptive_frozen",
        receipts(),
        allow_terminal_failures=(
            CAMPAIGN / "terminal_failures/adaptive_frozen.json"
        ).exists(),
    )
    if len(rows) != 160:
        raise ValueError("Adaptive-frozen denominator changed")
    core = read(REPORT / "fresh_cells.json")
    comparisons: dict[str, Any] = {}
    summary: dict[str, Any] = {}
    for stage in ("train", "validation"):
        current = [r for r in rows if r["stage"] == stage]
        summary[stage] = metrics(current)
        for arm in ("A0", "A2", "P1"):
            base = [r for r in core if r["stage"] == stage and r["arm"] == arm]
            comparisons[f"{stage}/{arm}"] = dict(
                theorem=paired(base, current),
                family=paired(base, current, mapping()),
            )
    ledger = ledger_rows()
    names = read(CAMPAIGN / "online_protocol.json")["independent_orders"][0]
    cells = {f"train__online_A2__{theorem}__seed0" for theorem in names}
    sources = paid([r for r in ledger if r["cell"] in cells])
    authors = paid(
        [
            r
            for r in ledger
            if r["cell"].startswith("online-o0-") and "__A2__" in r["cell"]
        ]
    )
    save(
        REPORT / "adaptive_frozen_results.json",
        dict(
            metrics=summary,
            comparisons=comparisons,
            preparation=dict(
                source=sources,
                authors=authors,
                total_cost=sources["cost"] + authors["cost"],
            ),
            protocol=read(CAMPAIGN / "adaptive_frozen_protocol.json"),
        ),
    )
    save(
        REPORT / "adaptive_frozen_cells.json",
        [
            dict(
                {
                    k: v
                    for k, v in row.items()
                    if k not in ("checks", "config", "value", "turns")
                },
                trace_summary=characterize(row),
            )
            for row in rows
        ],
    )
    print(json.dumps(dict(cells=160, metrics=summary)))


if __name__ == "__main__":
    import sys

    actions = {
        "register": register,
        "prepare": prepare,
        "run": run,
        "assess": assess,
    }
    if len(sys.argv) != 2 or sys.argv[1] not in actions:
        raise SystemExit("Use register, prepare, run, or assess")
    actions[sys.argv[1]]()
