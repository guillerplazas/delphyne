"""Small model-facing decisions compiled into the existing ACE contracts.

Aliases are local presentation references, never certificates. Persistent
products retain immutable source/context/receipt identities.
"""

from dataclasses import dataclass
from typing import Literal, Sequence, TypeVar

from ace.rocq_snippets import SnippetContext, SnippetReceipt
from prove_snippets import SnippetAddition
from prove_writer_drafts import (
    DraftAdvice,
    DraftDecision,
    UnverifiedSnippetDraft,
    validate_decisions,
)
from prove_writer_receipts import compile_receipt_advice
from prove_ace import CurationDelta

T = TypeVar("T")


def resolve(alias: str, prefix: str, values: Sequence[T]) -> T:
    if not alias.startswith(prefix):
        raise ValueError(f"Use a supplied {prefix} alias")
    suffix = alias[len(prefix) :]
    if not suffix.isdecimal() or str(int(suffix)) != suffix:
        raise ValueError("Malformed local alias")
    index = int(suffix) - 1
    if not 0 <= index < len(values):
        raise ValueError("Unknown local alias: " + alias)
    return values[index]


@dataclass(frozen=True)
class WriterChoice:
    draft: str
    action: Literal["retain", "drop"]
    reason: str
    section: str
    explanation: str
    receipts: tuple[str, ...]


@dataclass(frozen=True)
class WriterChoices:
    reasoning: str
    decisions: tuple[WriterChoice, ...]


def compile_choices(
    role: Literal["curator", "reducer"],
    answer: WriterChoices,
    drafts: tuple[UnverifiedSnippetDraft, ...],
    receipts: tuple[SnippetReceipt, ...],
    contexts: tuple[SnippetContext, ...],
) -> tuple[DraftAdvice, CurationDelta]:
    decisions: list[DraftDecision] = []
    ops: list[SnippetAddition] = []
    retained: list[str] = []
    for choice in answer.decisions:
        draft = resolve(choice.draft, "d", drafts)
        if choice.action == "drop":
            if choice.receipts or choice.section or choice.explanation:
                raise ValueError(
                    "Dropped drafts need empty section/explanation/receipts"
                )
            ids: tuple[str, ...] = ()
        else:
            rs = tuple(resolve(a, "r", receipts) for a in choice.receipts)
            if not rs or any(not r.executable for r in rs):
                raise ValueError("Retain only successful checked receipts")
            ids = tuple(r.identifier for r in rs)
            ops.append(
                SnippetAddition(choice.section, choice.explanation, ids)
            )
            retained.extend(ids)
        decisions.append(
            DraftDecision(draft.draft_id, choice.action, choice.reason, ids)
        )
    # A receipt may support multiple related decisions; retain it only once.
    kept = tuple(dict.fromkeys(retained))
    advice = DraftAdvice(
        answer.reasoning,
        tuple(ops),
        kept,
        tuple(
            r.identifier
            for r in receipts
            if r.executable and r.identifier not in kept
        ),
        tuple(decisions),
    )
    delta = compile_receipt_advice(role, advice, receipts)
    validate_decisions(advice, drafts, receipts, contexts)
    return advice, delta


@dataclass(frozen=True)
class TrainingEvent:
    identifier: str
    context: SnippetContext
    submitted: str
    status: str
    error: str
    goals: tuple[str, ...]


@dataclass(frozen=True)
class ReflectedLesson:
    reasoning: str
    event: str
    diagnosis: str
    operation: str
    preconditions: str
    proposed_code: str
    abstain_reason: str


def lesson_draft(
    lesson: ReflectedLesson,
    events: tuple[TrainingEvent, ...],
) -> tuple[UnverifiedSnippetDraft, ...]:
    if not lesson.proposed_code.strip():
        if not lesson.abstain_reason.strip():
            raise ValueError("Abstention requires an evidence-based reason")
        return ()
    event = next((e for e in events if e.identifier == lesson.event), None)
    if event is None or lesson.abstain_reason.strip():
        raise ValueError("A proposed draft needs exactly one supplied event")
    if not lesson.operation.strip() or not lesson.preconditions.strip():
        raise ValueError("Specify the operation and source prerequisites")
    return (
        UnverifiedSnippetDraft(
            "lesson-" + event.context.theorem_name,
            event.context.identifier,
            lesson.proposed_code,
            lesson.operation
            + ": "
            + lesson.diagnosis
            + " Preconditions: "
            + lesson.preconditions,
            event.context.source,
            event.error,
            event.goals,
        ),
    )
