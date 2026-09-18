"""Bounded learning from frozen trainX evidence, without rebuilding v2."""

from copy import deepcopy
from dataclasses import asdict
import json
from typing import Any, cast

from delphyne.utils.typing import pydantic_load

from ace.ace_playbook import Playbook
from ace.learning_contracts import observe_local_progress
from ace.role_revision import (
    ReflectionProduct,
    WriterProduct,
    apply_product,
    reduction_input,
)
from ace.rocq_snippets import SnippetContext, check_snippet, context_for
from runtime.ace_role_journal import RoleJournal

from . import campaign as c
from .scope import partition


def source(theorem: str) -> dict[str, Any]:
    if theorem not in partition("train"):
        raise ValueError("Only trainX can supply adaptation evidence")
    path = c.LEARNING / "sources" / f"{theorem}.json"
    data = json.loads(path.read_text())
    if data["problem_file"] != partition("train")[theorem]:
        raise ValueError("Training source mismatch")
    return data


def _negative_cases(base: dict[str, Any]) -> list[dict[str, Any]]:
    """Synthetic proposals against actual, unmodified checked receipts."""
    duplicate = deepcopy(base)
    target = next(
        rule
        for rule in json.loads(base["rules"])
        if rule["alias"] == base["target"]
    )
    duplicate["action"] = "add"
    duplicate["proposed_rule"] = target["content"]
    wrong = deepcopy(base)
    wrong["action"] = "add"
    wrong["proposed_rule"] = (
        "The hypothesis Hscope_not_in_context : False is already proved "
        "in the recorded context; close the goal by exact Hscope_not_in_context."
    )
    ctx = pydantic_load(SnippetContext, base["receipts"][0]["context"])
    receipt = check_snippet(
        ctx,
        "assert (Hscope_false : False).",
        dict(seconds=10, rpc_calls=128, view_bytes=8192),
    )
    observation = observe_local_progress(
        receipt, dict(seconds=10, rpc_calls=128, view_bytes=8192)
    )
    opened = deepcopy(base)
    opened.update(
        action="add",
        proposed_rule=(
            "Opening assert (Hscope_false : False) establishes False as "
            "a proved local fact, immediately usable to close any goal."
        ),
        receipts=[asdict(receipt)],
        source_events=[],
        observations=[asdict(observation)],
    )
    power_ctx = context_for(
        partition("train")["amc12a_2016_p2"], "amc12a_2016_p2"
    )
    power_receipt = check_snippet(
        power_ctx,
        "pose proof Nat.pow_inj_r as Hscope_pow.",
        dict(seconds=10, rpc_calls=128, view_bytes=8192),
    )
    if not power_receipt.executable or not receipt.executable:
        raise ValueError("Negative review fixtures require executed evidence")
    power = deepcopy(base)
    power.update(
        action="add",
        proposed_rule=(
            "For every positive natural base a, equality a^b = a^c "
            "implies b=c by Nat.pow_inj_r; positivity alone suffices."
        ),
        receipts=[asdict(power_receipt)],
        source_events=[],
        observations=[
            asdict(
                observe_local_progress(
                    power_receipt,
                    dict(seconds=10, rpc_calls=128, view_bytes=8192),
                )
            )
        ],
    )
    return [
        dict(
            case="negative_duplicate",
            query=duplicate,
            expected_support="supported",
            allowed_relations=["example", "duplicate"],
        ),
        *[
            dict(
                case=label,
                query=query,
                expected_support="not_supported",
                allowed_relations=["unsupported"],
            )
            for label, query in (
                ("negative_context", wrong),
                ("negative_assertion", opened),
                ("negative_premise", power),
            )
        ],
    ]


def prepare_pilots() -> None:
    if (c.CAMPAIGN / "role_registration.json").exists():
        return
    registration = json.loads(
        (c.LEARNING / "pilot_registration.json").read_text()
    )
    rows: list[dict[str, Any]] = []
    base: dict[str, Any] | None = None
    for old in registration["cases"]:
        role = old["role"]
        if role not in ("schema", "review"):
            continue
        raw = json.loads((c.LEARNING / old["input"]).read_text())
        query = raw["query"]
        if role == "review" and old["case"] == "batch3_review0":
            base = query
        for variant in ("control", "candidate"):
            args = deepcopy(raw)
            if role == "schema":
                # Both sides now ask for an actual terminal decision.
                args["query"].update(
                    allow_tools=False, strict_actions=variant == "candidate"
                )
            job = c.make_job(
                "learning",
                role + "_" + variant,
                role,
                old["case"],
                dict(
                    args=args,
                    guidance=role == "review" and variant == "candidate",
                ),
            )
            rows.append(
                dict(
                    job=asdict(job),
                    case=old["case"],
                    role=role,
                    variant=variant,
                    expected_support=old.get("expected_support"),
                    allowed_relations=old.get("allowed_relations", []),
                    originally_valid=old.get("originally_valid"),
                    source_file=str(
                        (c.LEARNING / old["input"]).relative_to(c.ROOT)
                    ),
                    source_sha256=c.sha(c.LEARNING / old["input"]),
                )
            )
    assert base is not None
    negatives = _negative_cases(base)
    for negative in negatives:
        for variant in ("control", "candidate"):
            job = c.make_job(
                "learning",
                "review_" + variant,
                "review",
                negative["case"],
                dict(
                    args=dict(query=negative["query"]),
                    guidance=variant == "candidate",
                ),
            )
            rows.append(
                dict(
                    job=asdict(job),
                    role="review",
                    variant=variant,
                    **{k: v for k, v in negative.items() if k != "query"},
                    synthetic_proposal=True,
                )
            )
    c.save(
        "role_registration.json",
        dict(
            cases=rows,
            cells=len(rows),
            schema_cells=24,
            review_cells=40,
            prospective_rule=(
                "Schema: improve aggregate valid finals with no newly "
                "unsupported accepted plan. Review: improve scored support/novelty "
                "or retain accuracy while correcting a diagnosed case; all three "
                "unsupported-scope fixtures must abstain. Unknown positives are "
                "unscored. Outcomes are exploratory, not universal correctness."
            ),
        ),
    )
    # Input hashes are sealed before dispatch; registration binds labels.
    c.save(
        "role_inputs.json",
        {row["job"]["input_file"]: row["job"]["input_sha256"] for row in rows},
    )


def pilots() -> None:
    rows = c.read("role_registration.json")["cases"]
    selected = [c.Job(**r["job"]) for r in rows]
    for i in range(0, len(selected), 8):
        if not c.launch(f"roles_{i // 8:02d}", selected[i : i + 8]):
            raise ValueError("Incomplete role panel; no role verdict")


def assess_pilots() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for row in c.read("role_registration.json")["cases"]:
        job = c.Job(**row["job"])
        result = c.cell_result(job)
        value = cast(
            dict[str, Any] | None,
            result["values"][0] if result and result["values"] else None,
        )
        if row["role"] == "schema":
            scored = True
            correct = bool(value and value.get("plan") is not None)
        else:
            scored = bool(row["allowed_relations"])
            verdict = value or {}
            support = verdict.get("support")
            relation = verdict.get("relation")
            correct = bool(
                value
                and (
                    support in ("unsupported", "unknown")
                    if row["expected_support"] == "not_supported"
                    else support == row["expected_support"]
                    and relation in row["allowed_relations"]
                )
            )
        rows.append(
            dict(
                cell=c.name(job, None),
                role=row["role"],
                variant=row["variant"],
                case=row["case"],
                scored=scored,
                correct=correct,
                value=value,
            )
        )
    totals = {
        f"{role}_{variant}": sum(
            r["correct"] and r["scored"]
            for r in rows
            if r["role"] == role and r["variant"] == variant
        )
        for role in ("schema", "review")
        for variant in ("control", "candidate")
    }
    safety = c.read("role_safety_review.json")
    if safety["registration_sha256"] != c.sha(
        c.CAMPAIGN / "role_registration.json"
    ):
        raise ValueError(
            "Safety review does not match the registered fixtures"
        )
    schema = (
        totals["schema_candidate"] > totals["schema_control"]
        and safety["no_new_unsupported_schema_plans"]
    )
    review = (
        totals["review_candidate"] >= totals["review_control"]
        and (
            totals["review_candidate"] > totals["review_control"]
            or safety["diagnosed_review_case_corrected"]
        )
        and all(
            r["correct"]
            for r in rows
            if r["variant"] == "candidate"
            and r["case"]
            in ("negative_context", "negative_assertion", "negative_premise")
        )
    )
    result = dict(
        rows=rows,
        totals=totals,
        strict_actions=schema,
        evidence_review=True,
        guidance=review,
    )
    c.save("role_decisions.json", result)
    return result


def product(job: c.Job) -> ReflectionProduct | WriterProduct | None:
    raw = c.cell_result(job)
    if raw and raw["success"] and len(raw["values"]) == 1:
        return pydantic_load(
            ReflectionProduct if job.role == "reflector" else WriterProduct,
            raw["values"][0],
        )
    checkpoint = RoleJournal(
        c.CAMPAIGN / "transport" / c.name(job, None) / "checkpoints"
    ).latest()
    return checkpoint.product if checkpoint else None


def writer_input(
    originals: tuple[ReflectionProduct, ...],
    products: tuple[WriterProduct, ...],
    book: Playbook,
    role: str,
    decisions: dict[str, Any],
) -> dict[str, Any]:
    reduced = reduction_input(products, originals, book)
    theorems = {ctx.theorem_name for ctx in reduced["contexts"]}
    return dict(
        role=role,
        book=asdict(book),
        evidence=reduced["evidence"],
        contexts=[asdict(x) for x in reduced["contexts"]],
        drafts=[asdict(x) for x in reduced["drafts"]],
        receipts=[asdict(x) for x in reduced["receipts"]],
        source_events=[
            e for n in sorted(theorems) for e in source(n)["events"]
        ],
        strict_actions=decisions["strict_actions"],
        evidence_review=decisions["evidence_review"],
        targeted_demos=True,
    )


def adapt() -> None:
    decisions = c.read("role_decisions.json")
    book = Playbook.load(c.REFERENCE / "book.yaml")
    order = json.loads((c.REVISION / "protocol.json").read_text())["order"]
    if set(order) != set(partition("train")):
        raise ValueError("Adaptation sources must be exactly trainX")
    for i in range(0, len(order), 4):
        batch = order[i : i + 4]
        reflectors: list[c.Job] = []
        for theorem in batch:
            data = source(theorem)
            reflectors.append(
                c.make_job(
                    "learning",
                    "adapt",
                    "reflector",
                    theorem,
                    dict(
                        guidance=decisions["guidance"],
                        args=dict(
                            problem_file=data["problem_file"],
                            playbook=data["generator_book"],
                            trajectory=data["trajectory"],
                            terminal=data["terminal"],
                            events=data["events"],
                            current_book=book.render_prompt(),
                        ),
                    ),
                )
            )
        if not c.launch(f"adapt_{i // 4:02d}_reflect", reflectors):
            raise ValueError(
                "Incomplete adaptation: reflection block does not fit"
            )
        originals = tuple(
            p
            for job in reflectors
            if isinstance(p := product(job), ReflectionProduct) and p.drafts
        )
        writers = [
            c.make_job(
                "learning",
                "adapt",
                "curator",
                p.contexts[0].theorem_name,
                dict(
                    guidance=decisions["guidance"],
                    args=writer_input((p,), (), book, "curator", decisions),
                ),
            )
            for p in originals
        ]
        # Small blocks preserve the learning allocation rather than reserving
        # a full forty-role worst case against a small actual-cost ceiling.
        for j, writer in enumerate(writers):
            if not c.launch(f"adapt_{i // 4:02d}_curate{j}", [writer]):
                raise ValueError("Incomplete adaptation: curator does not fit")
        if not originals:
            continue
        products = [product(job) for job in writers]
        written = tuple(p for p in products if isinstance(p, WriterProduct))
        reducer = c.make_job(
            "learning",
            "adapt",
            "reducer",
            f"batch{i // 4:02d}",
            dict(
                guidance=decisions["guidance"],
                args=writer_input(
                    originals, written, book, "reducer", decisions
                ),
            ),
        )
        if not c.launch(f"adapt_{i // 4:02d}_reduce", [reducer]):
            raise ValueError("Incomplete adaptation: reducer does not fit")
        reduced = product(reducer)
        if isinstance(reduced, WriterProduct) and reduced.status == "complete":
            revision = apply_product(book, reduced)
            c.save(f"revisions/{i // 4:02d}.json", asdict(revision))
            book = revision.after
        else:
            c.save(
                f"revisions/{i // 4:02d}.json",
                dict(
                    status="no_complete_reducer",
                    before=book.sha256(),
                    after=book.sha256(),
                ),
            )
    # A newly generated artifact, never an in-place repair of the reference.
    path = c.CAMPAIGN / "book.yaml"
    if path.exists():
        if Playbook.load(path) != book:
            raise ValueError("Learned book changed")
    else:
        book.save(path)
    c.save(
        "learning_finished.json",
        dict(
            book_sha256=book.sha256(),
            source_count=len(order),
            reference_sha256=Playbook.load(c.REFERENCE / "book.yaml").sha256(),
            accounting=c.accounting(),
            default_promoted=False,
        ),
    )
