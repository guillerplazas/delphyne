"""Full trainX trace learning and source-linked terminal refinement.

The fixed-source design isolates teacher evidence for B1/B2. Generator
adaptation during the curriculum is tested separately by the online track.
"""

from dataclasses import asdict
import json
import random
from typing import Any

from pydantic import TypeAdapter

from ace.ace_playbook import AuditDecision, apply_audit
from experiments.ace_sanitized.scope import partition

from .common import CAMPAIGN, read, save, sha
from .workflow import (
    grow,
    book,
    save_book,
    role_job,
    register_roles,
    launch,
    result,
)

SOURCES = {
    "A2": "source_assisted_v2",
    "B1": "source_plain_v2",
    "B2": "teacher_plain_v2",
    "S1": "source_assisted_v2",
}


def prepare() -> None:
    selection = read(CAMPAIGN / "author_selection.json")
    names = list(partition("train"))
    random.Random(20260921).shuffle(names)
    save(
        CAMPAIGN / "full_learning_protocol.json",
        dict(
            author=selection["selected"],
            authors={
                arm: (
                    ["luna_medium", "gpt-5.6-luna", "medium"]
                    if arm == "S1"
                    else selection["selected"]
                )
                for arm in SOURCES
            },
            order=names,
            arms=SOURCES,
            source_hashes={
                arm: {
                    t: sha(CAMPAIGN / "evidence" / f"{prefix}__{t}.json")
                    for t in names
                }
                for arm, prefix in SOURCES.items()
            },
            calls="4 arms x 40 trajectories x 2 roles =320 role outputs, max640 requests; five terminal source-batch auditors per arm, max2 requests each",
            generator="Frozen Luna source trajectories; B1/B2 share identical plain trajectories",
            initialization="Empty books independently; identical merge/cap/work allowances",
            parser="Outer YAML v3; old valid parsed values unchanged; no changes to archived pilot",
            refinement="Five source batches of eight trajectories; explicit keep/drop/rewrite deltas applied sequentially, no monolithic replacement. Every check retained. Missing evidence in one batch cannot justify deletion.",
            scope="trainX only. Online curriculum separately tests Generator/book interaction.",
            scaling_followup="S1 repeats A2's entire training/refinement with Luna-medium instead of the selected Sol-medium author. Final completed pilot:Sol11/12 at$0.113950 versusLuna10/12 at$0.156320. Evaluate160 frozen train/validation cells against the already registered A2/A0 core controls; no replacement of core selection or extra baseline replicates.",
        ),
    )


def run(arm: str) -> None:
    if arm not in SOURCES:
        raise ValueError("Unknown full learning arm")
    protocol = read(CAMPAIGN / "full_learning_protocol.json")
    tag, model, effort = protocol["authors"][arm]
    names = protocol["order"]
    prefix = SOURCES[arm]
    for theorem in names:
        if (
            sha(CAMPAIGN / "evidence" / f"{prefix}__{theorem}.json")
            != protocol["source_hashes"][arm][theorem]
        ):
            raise ValueError("Training evidence drift")
    label = "full_" + arm
    grow(label, [(tag, model, effort)], names, prefix, parser_version=3)
    raw = read(CAMPAIGN / "books" / f"{label}__{tag}.json")
    pb = book(raw["playbook"])
    evidence: list[dict[str, Any]] = []
    for step, theorem in enumerate(names):
        event = read(
            CAMPAIGN / "learning_events" / f"{label}__{tag}__{step:02d}.json"
        )
        source = read(CAMPAIGN / "evidence" / f"{prefix}__{theorem}.json")
        evidence.append(
            dict(
                theorem=theorem,
                reflection=event["reflection"],
                delta=event["delta"],
                added=event["merge"]["added"],
                deduped=event["merge"]["deduped"],
                source_file=f"evidence/{prefix}__{theorem}.json",
                source_sha=sha(
                    CAMPAIGN / "evidence" / f"{prefix}__{theorem}.json"
                ),
                solved=source["solved"],
                returned=source["returned"],
                checks=source["checks"],
                training_completion=source.get("training_only_completion", []),
            )
        )
    batches: list[str] = []
    for index in range(5):
        cell = f"{label}__{tag}__terminal_refine_{index}"
        job = role_job(
            cell,
            "refine_v3",
            dict(
                evidence=json.dumps(
                    dict(
                        scope="One of five source batches. Lack of evidence in this batch is not evidence against a bullet. Repair claims contradicted by these traces, and remove clear duplicates. Preserve unrelated rules.",
                        trajectories=evidence[8 * index : 8 * (index + 1)],
                    ),
                    sort_keys=True,
                ),
                playbook=pb.render_markdown(),
            ),
            model,
            effort,
        )
        batch = label + f"-terminal-refine-{index}"
        batches.append(batch)
        register_roles(batch, [job])
        launch(batch, roles=True)
        values = result(batch, cell)["values"]
        decisions = (
            TypeAdapter(list[AuditDecision]).validate_python(
                values[0]["decisions"]
            )
            if values
            else []
        )
        refined = apply_audit(pb, decisions, [], max_tokens=6000)
        save(
            CAMPAIGN / "learning_events" / f"{cell}.json",
            dict(
                role_output=values,
                applied=asdict(refined),
                input_book=asdict(pb),
            ),
        )
        pb = refined.playbook
    save_book(
        CAMPAIGN / "books" / f"{arm}_frozen.json",
        pb,
        dict(
            training_theorems=names,
            author=protocol["authors"][arm],
            source=prefix,
            unrefined_book=f"books/{label}__{tag}.json",
            refinement_batches=batches,
        ),
    )
    print(
        json.dumps(
            dict(
                arm=arm,
                bullets=len(pb.bullets),
                chars=len(pb.render_prompt()),
            )
        )
    )
