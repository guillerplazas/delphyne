"""The registered 1200-cell frozen and prequential development benchmark.

Frozen books precede validation. Online scores precede learning from the
current trajectory. Each online order starts with three empty books; the
ordinary controls never receive learned context or an additional tool.
"""

from dataclasses import asdict, replace
import json
import random
import subprocess
import sys
from typing import Any

from pydantic import TypeAdapter

from ace.ace_playbook import Playbook, AddOp, BulletTag, merge
from experiments.ace_sanitized.scope import partition
from experiments.common import omphalos_launch as ol

from . import campaign as c
from .audit import cell
from .common import CAMPAIGN, OUTPUT, ROOT, read, save, sha, now
from .teacher import TeacherJob, teacher_name
from .workflow import (
    RoleJob,
    book,
    save_book,
    launch,
    evidence_for,
    role_job,
    register_roles,
    result,
)

ARMS = {
    "A0": (True, ""),
    "A1": (True, "books/A1_historical.json"),
    "A2": (True, "books/A2_frozen.json"),
    "B0": (False, ""),
    "B1": (False, "books/B1_frozen.json"),
    "B2": (False, "books/B2_frozen.json"),
}


def prepare_online() -> None:
    orders: list[list[str]] = []
    for seed in (0, 1):
        names = list(partition("train"))
        random.Random(20260919 + seed).shuffle(names)
        orders.append(names)
    save(
        CAMPAIGN / "online_protocol.json",
        dict(
            arms=ARMS,
            frozen_cells=960,
            online_cells=240,
            independent_orders=orders,
            allocation="800 frozen ACE/control cells plus 400 online-track cells (160 frozen train controls +240 online ACE); total1200",
            core_solver="robust typed-transport feedback; original Luna medium, core tools, same prompts and budgets",
            online="Empty reset for each order. Five arms solve current problem; immutable scores saved before three learning updates. Training-only B2 completion sees only its already scored current trajectory.",
            learning="Same selected author, v3 parser, 2 calls per role, deterministic ADD merge,6000 token estimate cap, no dedup helpful increment. Online costs include all learning calls.",
            author=read(CAMPAIGN / "author_selection.json")["selected"],
            target="At least10% less all-attempt inference spending; at most2 fewer solves per40 averaged over replicates. Report full frontier and clustered90% intervals.",
            scope="trainX and validationX only; reused development data, no untouched generalization claim",
        ),
    )


def prepare() -> None:
    prepare_online()
    frozen = {
        arm: sha(CAMPAIGN / filename)
        for arm, (_, filename) in ARMS.items()
        if filename
    }
    save(
        CAMPAIGN / "core_protocol.json",
        dict(**read(CAMPAIGN / "online_protocol.json"), book_hashes=frozen),
    )
    jobs = c.ordered_jobs(
        "validation", [(a, *config) for a, config in ARMS.items()]
    )
    jobs += c.ordered_jobs(
        "train",
        [(a, *config) for a, config in ARMS.items() if a not in ("A0", "B0")],
    )
    jobs = [replace(j, robust=True) for j in jobs]
    if len(jobs) != 800:
        raise ValueError("Frozen core allocation changed")
    c.register("core_frozen", jobs)
    # A timestamp is a separate write-once event, so resumption stays stable.
    if not (CAMPAIGN / "core_frozen_at.json").exists():
        save(CAMPAIGN / "core_frozen_at.json", dict(at=now(), hashes=frozen))
    print(json.dumps(dict(frozen_batch=800, online_track=400, total=1200)))


def prepare_scaling() -> None:
    """One author-only follow-up; the core A0/A2 cells supply controls."""
    filename = "books/S1_frozen.json"
    jobs = [
        replace(job, robust=True)
        for stage in ("train", "validation")
        for job in c.ordered_jobs(stage, [("S1", True, filename)])
    ]
    if len(jobs) != 160:
        raise ValueError("Scaling follow-up allocation changed")
    c.register("core_scaling", jobs)
    save(
        CAMPAIGN / "scaling_protocol.json",
        dict(
            cells=160,
            book_sha=sha(CAMPAIGN / filename),
            factor="Luna-medium learning roles instead of selected Sol-medium; identical40 source trajectories, order, merge, refinement and Luna solver",
            controls="Core A0 and A2; no new controls or seeds",
            reason=read(CAMPAIGN / "full_learning_protocol.json")[
                "scaling_followup"
            ],
        ),
    )


def run_teacher_batch(batch: str) -> None:
    from .completion import install

    install()
    c.activate()
    jobs = [
        TeacherJob(**j)
        for j in read(CAMPAIGN / "online_teacher_batches" / f"{batch}.json")
    ]
    ctx = c.context()
    ctx = replace(
        ctx,
        modules=[*ctx.modules, "experiments.ace_independent_audit.teacher"],
    )
    save(
        CAMPAIGN / "online_teacher_sources" / f"{batch}.json",
        {
            "teacher.py": sha(
                ROOT / "experiments/ace_independent_audit/teacher.py"
            )
        },
    )
    ol.OmphalosExperiment(
        config_class=TeacherJob,
        configs=jobs,
        context=ctx,
        output_dir=str((OUTPUT / batch).relative_to(ROOT)),
        config_naming=teacher_name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def teach(
    batch: str, theorem: str, evidence_path: str
) -> list[dict[str, Any]]:
    job = TeacherJob(theorem, evidence_path, sha(CAMPAIGN / evidence_path))
    save(CAMPAIGN / "online_teacher_batches" / f"{batch}.json", [asdict(job)])
    command = [
        sys.executable,
        "-m",
        "experiments.ace_independent_audit",
        "run-online-teacher",
        batch,
        "run",
        "--max_workers=1",
        "--wait",
    ]
    path = CAMPAIGN / "logs" / f"{batch}.log"
    path.parent.mkdir(exist_ok=True)
    with path.open("a") as stream:
        subprocess.run(
            command,
            cwd=ROOT,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
        )
    values = result(batch, teacher_name(job, None))["values"]
    if len(values) != 1:
        raise ValueError("Missing online teacher receipt")
    return values[0]


def online(order: int) -> None:
    if order not in (0, 1):
        raise ValueError("Only the two registered orders are allowed")
    protocol = read(CAMPAIGN / "online_protocol.json")
    _, model, effort = protocol["author"]
    books = {arm: Playbook() for arm in ("A2", "B1", "B2")}
    for step, theorem in enumerate(protocol["independent_orders"][order]):
        batch = f"online-o{order}-s{step:02d}"
        event_file = CAMPAIGN / "online_events" / f"{batch}.json"
        if event_file.exists():
            event = read(event_file)
            if event["theorem"] != theorem:
                raise ValueError("Online chronology mismatch")
            books = {a: book(v) for a, v in event["after"].items()}
            continue
        filenames: dict[str, str] = {}
        for arm, pb in books.items():
            filename = f"books/{batch}__{arm}_before.json"
            save_book(
                CAMPAIGN / filename,
                pb,
                dict(
                    order=order,
                    step=step,
                    training_theorems=protocol["independent_orders"][order][
                        :step
                    ],
                ),
            )
            filenames[arm] = filename
        names = ["A0", "A2", "B0", "B1", "B2"]
        if order == 1:
            names.reverse()
        names = names[step % 5 :] + names[: step % 5]
        jobs = [
            c.Job(
                "train",
                arm if arm in ("A0", "B0") else "online_" + arm,
                theorem,
                order,
                filenames.get(arm, ""),
                sha(CAMPAIGN / filenames[arm]) if arm in filenames else "",
                assisted=arm.startswith("A"),
                robust=True,
            )
            for arm in names
        ]
        c.register(batch, jobs)
        launch(batch, workers=5)
        scores: list[dict[str, Any]] = []
        for job in jobs:
            row = cell(
                (str(OUTPUT / batch / "configs" / c.name(job, None)), theorem)
            )
            if row["status"] != "result":
                raise ValueError("Unresolved online platform failure")
            scores.append(
                dict(
                    arm=job.arm,
                    solved=row["solved"],
                    cost=row["costs"],
                    counts=row["counts"],
                    result_sha=row["result_sha"],
                    cache_sha=row["cache_sha"],
                    book_sha=job.book_sha,
                )
            )
        score_path = CAMPAIGN / "online_scores" / f"{batch}.json"
        save(
            score_path,
            dict(theorem=theorem, order=order, step=step, scores=scores),
        )
        encoded: dict[str, str] = {}
        for job in jobs:
            if not job.arm.startswith("online_"):
                continue
            arm = job.arm.removeprefix("online_")
            evidence = evidence_for(batch, job, version=2)
            path = f"evidence/{batch}__{arm}.json"
            save(CAMPAIGN / path, evidence)
            if arm == "B2":
                evidence["training_only_completion"] = teach(
                    batch + "-teacher", theorem, path
                )
                save(
                    CAMPAIGN / "evidence" / f"{batch}__B2_teacher.json",
                    evidence,
                )
            encoded[arm] = json.dumps(evidence, sort_keys=True)
        reflect_jobs = [
            role_job(
                f"{batch}__{arm}__reflect",
                "reflect_v3",
                dict(evidence=encoded[arm], playbook=pb.render_markdown()),
                model,
                effort,
            )
            for arm, pb in books.items()
        ]
        register_roles(batch + "-reflect", reflect_jobs)
        launch(batch + "-reflect", roles=True, workers=3)
        reflections: dict[str, Any] = {}
        curate_jobs: list[RoleJob] = []
        for arm, job in zip(books, reflect_jobs, strict=True):
            values = result(batch + "-reflect", job.cell)["values"]
            reflections[arm] = (
                values[0]
                if values
                else dict(
                    diagnosis="No parseable reflection; use original evidence",
                    bullet_tags=[],
                )
            )
            curate_jobs.append(
                role_job(
                    f"{batch}__{arm}__curate",
                    "curate_v3",
                    dict(
                        evidence=encoded[arm],
                        reflection=json.dumps(reflections[arm]),
                        playbook=books[arm].render_markdown(),
                    ),
                    model,
                    effort,
                )
            )
        register_roles(batch + "-curate", curate_jobs)
        launch(batch + "-curate", roles=True, workers=3)
        updates: dict[str, Any] = {}
        for arm, job in zip(books, curate_jobs, strict=True):
            values = result(batch + "-curate", job.cell)["values"]
            delta = (
                values[0]
                if values
                else dict(operations=[], reasoning="Unparseable curation")
            )
            outcome = merge(
                books[arm],
                TypeAdapter(list[AddOp]).validate_python(delta["operations"]),
                TypeAdapter(list[BulletTag]).validate_python(
                    reflections[arm]["bullet_tags"]
                ),
                max_tokens=6000,
                dedup_counts_helpful=False,
            )
            updates[arm] = dict(
                reflection=reflections[arm], delta=delta, merge=asdict(outcome)
            )
            books[arm] = outcome.playbook
        save(
            event_file,
            dict(
                theorem=theorem,
                score_sha=sha(score_path),
                before={a: sha(CAMPAIGN / f) for a, f in filenames.items()},
                updates=updates,
                after={a: asdict(pb) for a, pb in books.items()},
            ),
        )
        print(
            json.dumps(dict(order=order, completed=step + 1, total=40)),
            flush=True,
        )
    for arm, pb in books.items():
        save_book(
            CAMPAIGN / "books" / f"online-o{order}__{arm}_final.json",
            pb,
            dict(
                order=order,
                training_theorems=protocol["independent_orders"][order],
            ),
        )
