"""One incremental learning pass from the selected round-1 train panel.

Twelve reflectors ($.05 each), up to twelve curators ($.20), three reducers
($.20): <=$3.60 nominal, within the separate $4 learning allocation.
Existing role strategy, evidence review and Compute budgeting are reused.
Partial role journals remain evidence; only complete reviewed reducer
products change a book. No semantic claim is inferred from execution alone.
"""

from dataclasses import asdict
from copy import deepcopy
from typing import Any

from delphyne.utils.typing import pydantic_load

from ace.ace_playbook import Playbook
from ace.role_revision import (
    ReflectionProduct,
    WriterProduct,
    apply_product,
    reduction_input,
)
from runtime.ace_role_journal import RoleJournal

from . import campaign as c
from .artifact import ContextArtifact, checked_example
from .evidence import learning_source
from .workflow import artifact, store_artifact


def product(job: c.Job) -> ReflectionProduct | WriterProduct | None:
    raw = c.cell_result(job)
    if raw and raw["values"]:
        return pydantic_load(
            ReflectionProduct if job.role == "reflector" else WriterProduct,
            raw["values"][0],
        )
    checkpoint = RoleJournal(
        c.CAMPAIGN / "transport" / c.name(job, None) / "checkpoints"
    ).latest()
    return checkpoint.product if checkpoint else None


def writer_args(
    originals: tuple[ReflectionProduct, ...],
    products: tuple[WriterProduct, ...],
    book: Playbook,
    role: str,
) -> dict[str, Any]:
    data = reduction_input(products, originals, book)
    theorems = sorted({ctx.theorem_name for ctx in data["contexts"]})
    return dict(
        role=role,
        book=asdict(book),
        evidence=data["evidence"],
        contexts=[asdict(x) for x in data["contexts"]],
        drafts=[asdict(x) for x in data["drafts"]],
        receipts=[asdict(x) for x in data["receipts"]],
        source_events=[
            e for n in theorems for e in c.read(f"sources/{n}.json")["events"]
        ],
        strict_actions=False,
        evidence_review=True,
        targeted_demos=True,
    )


def adapt() -> None:
    selected = c.read("round1_selection.json")["selected"]
    prior = artifact(selected)
    book = deepcopy(prior.book)
    examples = {e.identifier: e for e in prior.examples}
    # Carry the independently checked syntax repair into any newly authored
    # revision, even if training selects the unmodified historical artifact.
    for rule in book.bullets:
        if rule.id == "rocq-00015":
            rule.content = rule.content.replace(
                "change INR 2 <= INR c", "change (INR 2 <= INR c)"
            )
    c.save(
        "learning_start.json",
        dict(before=asdict(prior.book), after=asdict(book)),
    )
    order = c.read("protocol.json")["train"]
    sources = {
        j.theorem: j
        for j in c.jobs("round1")
        if j.arm == selected and j.seed == 0
    }
    for block in range(3):
        reflectors: list[c.Job] = []
        for theorem in order[4 * block : 4 * block + 4]:
            job = sources[theorem]
            if c.cell_result(job) is None:
                c.save(
                    f"sources/{theorem}.json",
                    dict(platform_failed=True, events=[]),
                )
                continue
            path = f"sources/{theorem}.json"
            if not (c.CAMPAIGN / path).exists():
                c.save(
                    path,
                    learning_source(
                        c.directory(job),
                        theorem,
                        c.read(job.input_file)["args"]["playbook"],
                    ),
                )
            data = c.read(path)
            reflectors.append(
                c.make_job(
                    "learning",
                    "adapt",
                    "reflector",
                    theorem,
                    dict(
                        args=dict(
                            problem_file=data["problem_file"],
                            playbook=data["generator_book"],
                            trajectory=data["trajectory"],
                            terminal=data["terminal"],
                            events=data["events"],
                            current_book=book.render_prompt(),
                        )
                    ),
                )
            )
        c.launch(f"learn_{block}_reflect", reflectors)
        originals = tuple(
            p
            for j in reflectors
            if isinstance(p := product(j), ReflectionProduct) and p.drafts
        )
        curators = [
            c.make_job(
                "learning",
                "adapt",
                "curator",
                p.contexts[0].theorem_name,
                dict(args=writer_args((p,), (), book, "curator")),
            )
            for p in originals
        ]
        c.launch(f"learn_{block}_curate", curators)
        if not originals:
            c.save(
                f"revisions/{block}.json",
                dict(
                    status="no_drafts",
                    before=book.sha256(),
                    after=book.sha256(),
                ),
            )
            continue
        written: list[WriterProduct] = []
        for job in curators:
            output = product(job)
            if isinstance(output, WriterProduct):
                written.append(output)
        products = tuple(written)
        reducer = c.make_job(
            "learning",
            "adapt",
            "reducer",
            f"block{block}",
            dict(args=writer_args(originals, products, book, "reducer")),
        )
        c.launch(f"learn_{block}_reduce", [reducer])
        reduced = product(reducer)
        if (
            not isinstance(reduced, WriterProduct)
            or reduced.status != "complete"
        ):
            c.save(
                f"revisions/{block}.json",
                dict(
                    status="no_complete_reducer",
                    before=book.sha256(),
                    after=book.sha256(),
                ),
            )
            continue
        revision = apply_product(book, reduced)
        c.save(f"revisions/{block}.json", asdict(revision))
        book = revision.after
        bank = {r.identifier: r for r in reduced.receipts}
        for edit in revision.edits:
            for ident in edit.receipts:
                # Fresh CPU-only verification; never silently treat an open
                # local receipt as a theorem-completion certificate.
                e = checked_example(
                    edit.target_id, bank[ident], f"revisions/{block}.json"
                )
                examples[e.identifier] = e
    known = {b.id for b in book.bullets}
    current = ContextArtifact(
        book,
        tuple(e for e in examples.values() if e.rule_id in known),
        (*prior.lineage, prior.sha256()),
    )
    store_artifact("round2", current)
    c.save(
        "learning_finished.json",
        dict(
            before=prior.sha256(),
            after=current.sha256(),
            examples=len(current.examples),
            accounting=c.accounting(),
        ),
    )
