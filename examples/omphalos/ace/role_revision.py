"""Versioned ACE edits: preserve evidence, judge novelty, update locally.

The September 13 v1 measurement contracts remain unchanged. This module
separates source examples from prompt rules and adds optimistic concurrency
checks to small, evidence-backed changes. It makes no semantic-proof claim
for a model's novelty judgment.
"""

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import re
from typing import Any, Literal

from ace.ace_playbook import (
    AddOp,
    AuditDecision,
    Playbook,
    SECTIONS,
    apply_audit,
)
from ace.role_contracts import TrainingEvent, resolve
from ace.rocq_snippets import SnippetContext, SnippetReceipt
from prove_writer_drafts import (
    DraftAdvice,
    DraftDecision,
    UnverifiedSnippetDraft,
    validate_decisions,
)


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass(frozen=True)
class LocalRepair:
    event: str
    diagnosis: str
    operation: str
    preconditions: str
    code: str


def bind_repair(
    repair: LocalRepair, events: tuple[TrainingEvent, ...]
) -> UnverifiedSnippetDraft:
    event = next((e for e in events if e.identifier == repair.event), None)
    if event is None:
        raise ValueError("event must name one supplied training event")
    for field in ("diagnosis", "operation", "preconditions", "code"):
        if not getattr(repair, field).strip():
            raise ValueError(f"{field} must be nonempty for a local repair")
    return UnverifiedSnippetDraft(
        "repair-" + fingerprint(event.context.identifier + repair.code)[:24],
        event.context.identifier,
        repair.code,
        repair.operation
        + ": "
        + repair.diagnosis
        + "; "
        + repair.preconditions,
        event.context.source,
        event.error,
        event.goals,
    )


@dataclass(frozen=True)
class ReflectionFinish:
    action: Literal["done", "abstain"]
    reason: str


def validate_finish(
    finish: ReflectionFinish, drafts: tuple[UnverifiedSnippetDraft, ...]
) -> None:
    if not finish.reason.strip():
        raise ValueError("reason must explain the final disposition")
    if finish.action == "done" and not drafts:
        raise ValueError("SubmitLocalRepair first, or choose action=abstain")
    if finish.action == "abstain" and drafts:
        raise ValueError(
            "Submitted local repairs already exist: choose action=done. "
            "Use reason for uncertainty; their code remains unverified."
        )


@dataclass(frozen=True)
class ReflectionProduct:
    status: Literal["complete", "partial"]
    drafts: tuple[UnverifiedSnippetDraft, ...]
    contexts: tuple[SnippetContext, ...]
    diagnostics: tuple[str, ...]
    finish: ReflectionFinish | None = None


@dataclass(frozen=True)
class EditIntent:
    draft: str
    action: Literal["add", "update", "example", "drop"]
    closest_rule: str
    section: str
    content: str
    reason: str
    receipts: tuple[str, ...]
    failure_receipt: str = ""


@dataclass(frozen=True)
class BookPlan:
    reasoning: str
    decisions: tuple[EditIntent, ...]


@dataclass(frozen=True)
class NoveltyVerdict:
    relation: Literal[
        "new_operation", "correction", "example", "duplicate", "unsupported"
    ]
    closest_rule: str
    reason: str


@dataclass(frozen=True)
class BookEdit:
    action: Literal["add", "update", "example"]
    target_id: str
    before_sha256: str
    section: str
    content: str
    receipts: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class EditReview:
    draft: str
    verdict: NoveltyVerdict | None
    error: str = ""


@dataclass(frozen=True)
class WriterProduct:
    role: Literal["curator", "reducer"]
    status: Literal["complete", "partial"]
    base_sha256: str
    drafts: tuple[UnverifiedSnippetDraft, ...]
    contexts: tuple[SnippetContext, ...]
    receipts: tuple[SnippetReceipt, ...]
    plan: BookPlan | None
    edits: tuple[BookEdit, ...]
    diagnostics: tuple[str, ...]
    reviews: tuple[EditReview, ...] = ()


def validate_rule(section: str, content: str) -> None:
    if not content.strip() or len(content) > 700:
        raise ValueError("Prompt rule must contain 1 to 700 characters")
    if "\n" in content or "```" in content:
        raise ValueError(
            "Keep one compact rule; store proof examples separately"
        )
    if section not in SECTIONS:
        raise ValueError("Use a supplied playbook section")


def nearest_rules(
    book: Playbook, text: str, limit: int = 5
) -> list[dict[str, str]]:
    """Transparent lexical retrieval, not a semantic acceptance test."""
    terms = set(re.findall(r"[A-Za-z][A-Za-z0-9_.]+", text.lower()))
    ranked: list[tuple[float, int]] = []
    for i, b in enumerate(book.bullets):
        other = set(re.findall(r"[A-Za-z][A-Za-z0-9_.]+", b.content.lower()))
        ranked.append((len(terms & other) / max(1, len(terms | other)), i))
    return [
        dict(
            alias=f"b{i + 1}",
            id=book.bullets[i].id,
            content=book.bullets[i].content,
        )
        for _, i in sorted(ranked, key=lambda r: (-r[0], r[1]))[:limit]
    ]


def validate_plan(
    plan: BookPlan,
    book: Playbook,
    drafts: tuple[UnverifiedSnippetDraft, ...],
    receipts: tuple[SnippetReceipt, ...],
    contexts: tuple[SnippetContext, ...],
) -> None:
    decisions: list[DraftDecision] = []
    kept: list[str] = []
    updates = [d.closest_rule for d in plan.decisions if d.action == "update"]
    if len(set(updates)) != len(updates):
        raise ValueError("Conflicting updates to one rule; reduce them first")
    for d in plan.decisions:
        source = resolve(d.draft, "d", drafts)
        if not d.reason.strip():
            raise ValueError("Each decision needs a reason")
        if d.action == "drop":
            if d.receipts or d.failure_receipt or d.content or d.section:
                raise ValueError(
                    "drop requires empty evidence/content/section"
                )
            ids: tuple[str, ...] = ()
        else:
            ids = tuple(
                resolve(r, "r", receipts).identifier for r in d.receipts
            )
            if book.bullets:
                resolve(d.closest_rule, "b", book.bullets)
            elif d.closest_rule or d.action != "add":
                raise ValueError(
                    "An empty book permits only an untargeted add"
                )
            if d.action in ("add", "update"):
                validate_rule(d.section, d.content)
            elif d.content or d.section:
                raise ValueError(
                    "An example attaches evidence without adding prompt text"
                )
            if d.action == "update":
                if (
                    d.section
                    != resolve(d.closest_rule, "b", book.bullets).section
                ):
                    raise ValueError(
                        "An update preserves its existing section"
                    )
                bad = resolve(d.failure_receipt, "r", receipts)
                good = [resolve(r, "r", receipts) for r in d.receipts]
                if bad.status != "rejected" or not any(
                    r.executable
                    and r.context.identifier == bad.context.identifier
                    for r in good
                ):
                    raise ValueError(
                        "An update needs rejected and repaired snippets in the same context"
                    )
            elif d.failure_receipt:
                raise ValueError("failure_receipt is only for an update")
            kept.extend(ids)
        decisions.append(
            DraftDecision(
                source.draft_id,
                "drop" if d.action == "drop" else "retain",
                d.reason,
                ids,
            )
        )
    if sum(d.action != "drop" for d in plan.decisions) > 3:
        raise ValueError("At most three retained decisions per batch")
    validate_decisions(
        DraftAdvice(
            plan.reasoning,
            (),
            tuple(dict.fromkeys(kept)),
            (),
            tuple(decisions),
        ),
        drafts,
        receipts,
        contexts,
    )


def approve_edit(
    intent: EditIntent,
    verdict: NoveltyVerdict,
    book: Playbook,
    receipts: tuple[SnippetReceipt, ...],
) -> BookEdit | None:
    """A separate judgment can veto an add or keep only its example."""
    if not verdict.reason.strip():
        raise ValueError("Novelty judgment needs an explicit reason")
    if verdict.relation == "unsupported":
        return None
    target = (
        resolve(verdict.closest_rule, "b", book.bullets)
        if book.bullets
        else None
    )
    if not book.bullets and verdict.closest_rule:
        raise ValueError("No existing rule is available")
    ids = tuple(resolve(r, "r", receipts).identifier for r in intent.receipts)
    if not ids or any(
        not resolve(r, "r", receipts).executable for r in intent.receipts
    ):
        raise ValueError("Only executed source receipts support an edit")
    action: Literal["add", "update", "example"]
    if verdict.relation in ("duplicate", "example") and target is not None:
        action = "example"
    elif verdict.relation == "new_operation" and intent.action == "add":
        action = "add"
    elif (
        verdict.relation == "correction"
        and intent.action == "update"
        and verdict.closest_rule == intent.closest_rule
    ):
        action = "update"
    else:
        return None
    return BookEdit(
        action,
        target.id if target and action != "add" else "",
        fingerprint(target.content) if target and action != "add" else "",
        intent.section if action != "example" else "",
        intent.content if action != "example" else "",
        ids,
        verdict.reason,
    )


def apply_edits(
    book: Playbook,
    base_sha256: str,
    edits: tuple[BookEdit, ...],
    *,
    max_tokens: int = 4000,
) -> tuple[Playbook, tuple[BookEdit, ...]]:
    """Atomic, default-keep application; evidence stays outside the prompt."""
    if book.sha256() != base_sha256:
        raise ValueError("Stale book revision; recompute the edit plan")
    current = book
    updated: set[str] = set()
    applied: list[BookEdit] = []
    for edit in edits:
        by_id = {b.id: b for b in current.bullets}
        if edit.action == "update" and edit.target_id in updated:
            raise ValueError(
                "Conflicting updates to one rule; reduce them first"
            )
        if not edit.receipts or not edit.reason.strip():
            raise ValueError("Each edit requires evidence and a reason")
        if edit.action in ("add", "update"):
            validate_rule(edit.section, edit.content)
        elif edit.content or edit.section:
            raise ValueError("Examples cannot insert prompt content")
        if edit.action != "add":
            target = by_id.get(edit.target_id)
            if (
                target is None
                or fingerprint(target.content) != edit.before_sha256
            ):
                raise ValueError("Stale target rule")
        if edit.action == "update":
            updated.add(edit.target_id)
            if edit.section != by_id[edit.target_id].section:
                raise ValueError("An update preserves its existing section")
            decision = (
                AuditDecision(
                    edit.target_id, "rewrite", edit.reason, edit.content
                ),
            )
            outcome = apply_audit(current, decision, (), max_tokens=max_tokens)
        elif edit.action == "add":
            # A deterministic backstop also catches duplicate adds in a batch.
            normalized = " ".join(edit.content.split()).casefold()
            duplicate = next(
                (
                    b
                    for b in current.bullets
                    if " ".join(b.content.split()).casefold() == normalized
                ),
                None,
            )
            if duplicate is not None:
                applied.append(
                    replace(
                        edit,
                        action="example",
                        target_id=duplicate.id,
                        before_sha256=fingerprint(duplicate.content),
                        section="",
                        content="",
                    )
                )
                continue
            outcome = apply_audit(
                current,
                (),
                (AddOp("ADD", edit.section, edit.content),),
                max_tokens=max_tokens,
            )
            if not outcome.refused:
                assigned = outcome.added[0]
                if edit.target_id and edit.target_id != assigned:
                    raise ValueError("Added rule identity drift")
                edit = replace(edit, target_id=assigned)
        else:
            applied.append(edit)
            continue
        if outcome.refused:
            raise ValueError(
                "Whole edit batch exceeds prompt budget; original book retained"
            )
        current = outcome.playbook
        applied.append(edit)
    if current.token_estimate() > max_tokens:
        raise ValueError(
            "Whole edit batch exceeds prompt budget; original book retained"
        )
    return current, tuple(applied)


@dataclass(frozen=True)
class BookRevision:
    """A self-contained revision; only ``after.render_prompt()`` is injected.

    The old book, drafts, reviews and complete receipt bank remain available
    for audit and example lookup without being repeated in generator prompts.
    """

    before: Playbook
    after: Playbook
    edits: tuple[BookEdit, ...]
    writer: WriterProduct


def apply_product(
    book: Playbook, product: WriterProduct, *, max_tokens: int = 4000
) -> BookRevision:
    """Validate the complete review trail before committing any book change."""
    if (
        product.role != "reducer"
        or product.status != "complete"
        or product.plan is None
    ):
        raise ValueError("A complete reviewed reducer product is required")
    if product.base_sha256 != book.sha256():
        raise ValueError("Stale book revision")
    validate_plan(
        product.plan, book, product.drafts, product.receipts, product.contexts
    )
    kept = tuple(d for d in product.plan.decisions if d.action != "drop")
    if tuple(r.draft for r in product.reviews) != tuple(d.draft for d in kept):
        raise ValueError(
            "Exactly one ordered review per retained decision is required"
        )
    current = book
    expected: list[BookEdit] = []
    for decision, review in zip(kept, product.reviews):
        if review.error or review.verdict is None:
            raise ValueError("A failed review cannot authorize an edit")
        edit = approve_edit(
            decision, review.verdict, current, product.receipts
        )
        if edit is not None:
            current, bound = apply_edits(
                current, current.sha256(), (edit,), max_tokens=max_tokens
            )
            expected.extend(bound)
    if tuple(expected) != product.edits:
        raise ValueError("Edits disagree with the independent review trail")
    after, applied = apply_edits(
        book, product.base_sha256, product.edits, max_tokens=max_tokens
    )
    if after.sha256() != current.sha256():
        raise ValueError("Sequential review and atomic application disagree")
    return BookRevision(book, after, applied, product)


def rule_examples(
    revision: BookRevision, rule_id: str
) -> tuple[SnippetReceipt, ...]:
    """Fetch exact source examples for this revision, including folded adds."""
    if rule_id not in {b.id for b in revision.after.bullets}:
        raise ValueError("Unknown rule in this revision")
    ids = dict.fromkeys(
        rid
        for e in revision.edits
        if e.target_id == rule_id
        for rid in e.receipts
    )
    receipts = {r.identifier: r for r in revision.writer.receipts}
    return tuple(receipts[rid] for rid in ids)


def reduction_input(
    products: tuple[WriterProduct, ...],
    originals: tuple[ReflectionProduct, ...],
    book: Playbook,
) -> dict[str, Any]:
    """Preserve local repairs and checked receipts even after invalid finals."""
    contexts = {
        c.identifier: c for p in (*originals, *products) for c in p.contexts
    }
    drafts = {d.draft_id: d for p in (*originals, *products) for d in p.drafts}
    receipts = {r.identifier: r for p in products for r in p.receipts}
    for r in receipts.values():
        contexts[r.context.identifier] = r.context
    needed = {d.context_id for d in drafts.values()} | {
        r.context.identifier for r in receipts.values()
    }
    for r in receipts.values():
        if r.executable:
            successor = r.successor()
            contexts[successor.identifier] = successor
            needed.add(successor.identifier)
    return dict(
        role="reducer",
        book=book,
        evidence=json.dumps(
            [
                dict(
                    role=p.role,
                    status=p.status,
                    base_sha256=p.base_sha256,
                    plan=asdict(p.plan) if p.plan else None,
                    diagnostics=p.diagnostics,
                )
                for p in products
            ]
        ),
        contexts=tuple(c for key, c in contexts.items() if key in needed),
        drafts=tuple(drafts.values()),
        receipts=tuple(receipts.values()),
    )
