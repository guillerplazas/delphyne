"""ACE learning v3: narrow actions and observations, without changing v2.

Execution observations describe one source context. They never establish
the semantic novelty or general validity of a proposed playbook rule.
"""

from dataclasses import dataclass
import re
from typing import Any, ClassVar, Literal

from pydantic import ConfigDict

from ace.role_contracts import TrainingEvent
from ace.role_revision import BookPlan, EditIntent, NoveltyVerdict
from ace.rocq_snippets import SnippetReceipt, context_for
from runtime import pytanque_utils as pt, rocq_server as rs
from runtime.admission_events import computation_started
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits, clip_utf8, operation


class StrictAction:
    __pydantic_config__: ClassVar[ConfigDict] = ConfigDict(extra="forbid")


@dataclass(frozen=True)
class AddRule(StrictAction):
    draft: str
    action: Literal["add"]
    closest_rule: str
    section: str
    content: str
    reason: str
    receipts: tuple[str, ...]


@dataclass(frozen=True)
class UpdateRule(StrictAction):
    draft: str
    action: Literal["update"]
    closest_rule: str
    section: str
    content: str
    reason: str
    receipts: tuple[str, ...]
    failure_receipt: str


@dataclass(frozen=True)
class AttachExample(StrictAction):
    draft: str
    action: Literal["example"]
    closest_rule: str
    reason: str
    receipts: tuple[str, ...]


@dataclass(frozen=True)
class DropDraft(StrictAction):
    draft: str
    action: Literal["drop"]
    reason: str


type LearningAction = AddRule | UpdateRule | AttachExample | DropDraft


@dataclass(frozen=True)
class LearningPlan(StrictAction):
    reasoning: str
    decisions: tuple[LearningAction, ...]

    def legacy(self) -> BookPlan:
        """Explicitly adapt valid v3 actions; never discard illegal fields."""
        return BookPlan(
            self.reasoning,
            tuple(
                EditIntent(
                    draft=d.draft,
                    action=d.action,
                    closest_rule=""
                    if isinstance(d, DropDraft)
                    else d.closest_rule,
                    section=d.section
                    if isinstance(d, (AddRule, UpdateRule))
                    else "",
                    content=d.content
                    if isinstance(d, (AddRule, UpdateRule))
                    else "",
                    reason=d.reason,
                    receipts=() if isinstance(d, DropDraft) else d.receipts,
                    failure_receipt=d.failure_receipt
                    if isinstance(d, UpdateRule)
                    else "",
                )
                for d in self.decisions
            ),
        )


def learning_plan(plan: BookPlan) -> LearningPlan:
    """Translate a validated historical plan for demonstrations, not parsing."""
    actions: list[LearningAction] = []
    for d in plan.decisions:
        if d.action == "drop":
            actions.append(DropDraft(d.draft, "drop", d.reason))
        elif d.action == "example":
            actions.append(
                AttachExample(
                    d.draft, "example", d.closest_rule, d.reason, d.receipts
                )
            )
        elif d.action == "update":
            actions.append(
                UpdateRule(
                    d.draft,
                    "update",
                    d.closest_rule,
                    d.section,
                    d.content,
                    d.reason,
                    d.receipts,
                    d.failure_receipt,
                )
            )
        else:
            actions.append(
                AddRule(
                    d.draft,
                    "add",
                    d.closest_rule,
                    d.section,
                    d.content,
                    d.reason,
                    d.receipts,
                )
            )
    return LearningPlan(plan.reasoning, tuple(actions))


@dataclass(frozen=True)
class LearningVerdict(StrictAction):
    support: Literal["supported", "unsupported", "unknown"]
    relation: Literal[
        "new_operation", "correction", "example", "duplicate", "unsupported"
    ]
    closest_rule: str
    reason: str

    def legacy(self) -> NoveltyVerdict:
        return NoveltyVerdict(
            self.relation if self.support == "supported" else "unsupported",
            self.closest_rule,
            f"Evidence support: {self.support}. {self.reason}",
        )


@dataclass(frozen=True)
class ObligationSnapshot:
    focused_goals: tuple[str, ...]
    existential_names: tuple[str, ...]
    existential_text: str
    complete_view: bool


@dataclass(frozen=True)
class LocalObservation:
    receipt: str
    outcome: Literal[
        "completed",
        "original_obligation_closed",
        "obligations_open",
        "unknown",
        "not_executed",
    ]
    before: ObligationSnapshot | None
    after: ObligationSnapshot | None
    discharged: tuple[str, ...]
    introduced: tuple[str, ...]
    reason: str
    elapsed: float = 0.0
    rpc_calls: int = 0


_EVARS = re.compile(r"Existential\s+\d+\s*=\s*(\?[^\s:]+)")
_POSTPONE = re.compile(
    r"\b(?:shelve|shelve_unifiable|give_up|admit|Admitted|Abort|evar|instantiate|existential|Grab)\b"
)


def _snapshot(client: Any, state: Any, limit: int) -> ObligationSnapshot:
    goals = tuple(pt._safe_goals(client, state))  # pyright: ignore[reportPrivateUsage]
    result = client.run(state, "Show Existentials.")
    raw = "\n".join(str(text) for _, text in result.feedback)
    names = tuple(_EVARS.findall(raw))
    complete = (
        len(raw.encode()) <= limit
        and not any(g.startswith("<") for g in goals)
        and (bool(names) or not goals and "Existential" not in raw)
    )
    return ObligationSnapshot(goals, names, clip_utf8(raw, limit), complete)


def observe_local_progress(
    receipt: SnippetReceipt, limits: dict[str, float | int]
) -> LocalObservation:
    """Replay one verified fragment; all RPCs share one bounded Compute."""
    computation_started("observe_local_progress")
    if not receipt.executable:
        return LocalObservation(
            receipt.identifier,
            "not_executed",
            None,
            None,
            (),
            (),
            "Receipt does not establish execution",
        )
    ctx = receipt.context
    if (
        context_for(ctx.problem_file, ctx.theorem_name, ctx.prefix, ctx.source)
        != ctx
    ):
        raise ValueError("Local observation source/environment drift")
    if receipt.checked.feedback.proof_so_far != [*ctx.prefix, receipt.snippet]:
        raise ValueError("Receipt does not certify the exact complete snippet")
    bounds = ToolLimits(**limits)  # type: ignore[arg-type]
    before: ObligationSnapshot | None = None
    after: ObligationSnapshot | None = None
    with operation(bounds) as op:
        try:
            file = rs.augmented_path(
                str(ROOT / ctx.problem_file), pt.DEFAULT_EXTRA_IMPORTS
            )
            with rs.MANAGER.session(file) as client:
                replay = pt._open_and_replay(  # pyright: ignore[reportPrivateUsage]
                    client,
                    file,
                    ctx.theorem_name,
                    list(ctx.prefix),
                    stop_when_finished=False,
                    timeout=pt.PROOF_TACTIC_TIMEOUT,
                )
                if replay.state is None or replay.failing_index is not None:
                    raise ValueError("Source prefix did not replay")
                before = _snapshot(client, replay.state, bounds.view_bytes)
                current = pt._run_guarded(  # pyright: ignore[reportPrivateUsage]
                    client,
                    replay.state,
                    receipt.snippet,
                    pt.PROOF_TACTIC_TIMEOUT,
                )
                # A full proof is certified by its original unassisted check.
                if receipt.status == "completed":
                    return LocalObservation(
                        receipt.identifier,
                        "completed",
                        before,
                        None,
                        (),
                        (),
                        "Exact complete snippet and kernel-accepted theorem",
                        op.elapsed,
                        op.calls,
                    )
                after = _snapshot(client, current, bounds.view_bytes)
                old, new = (
                    set(before.existential_names),
                    set(after.existential_names),
                )
                closed, introduced = (
                    tuple(sorted(old - new)),
                    tuple(sorted(new - old)),
                )
                outcome: Literal[
                    "original_obligation_closed", "obligations_open", "unknown"
                ] = "obligations_open"
                reason = "Original or newly introduced obligations remain; execution alone is not their proof"
                if (
                    not before.complete_view
                    or not after.complete_view
                    or _POSTPONE.search(receipt.snippet)
                ):
                    outcome, reason = (
                        "unknown",
                        "Incomplete observation or explicit existential/postponement manipulation",
                    )
                elif closed and not introduced:
                    outcome, reason = (
                        "original_obligation_closed",
                        "An original existential was discharged without introducing another; enclosing obligations are listed separately",
                    )
                return LocalObservation(
                    receipt.identifier,
                    outcome,
                    before,
                    after,
                    closed,
                    introduced,
                    reason,
                    op.elapsed,
                    op.calls,
                )
        except Exception as exc:
            return LocalObservation(
                receipt.identifier,
                "unknown",
                before,
                after,
                (),
                (),
                f"Observation unavailable: {exc}",
                op.elapsed,
                op.calls,
            )


def source_events_for(
    contexts: set[str], events: tuple[TrainingEvent, ...]
) -> tuple[TrainingEvent, ...]:
    selected = tuple(e for e in events if e.context.identifier in contexts)
    if len({(e.context.identifier, e.identifier) for e in selected}) != len(
        selected
    ):
        raise ValueError("Duplicate source-event evidence")
    return selected


def operation_tags(text: str) -> frozenset[str]:
    patterns = {
        "focus": r"bullet|focus|No such goal|\{",
        "reference": r"not found|unknown|ring_nf|No such hypothesis",
        "arguments": r"expected.*type|Unable to unify|premise|argument|Rmult_pos_pos",
        "square": r"Rsqr|Rle_0_sqr|\^\s*2|sqrt",
        "cast": r"INR|%nat|cast|convertib",
        "rewrite": r"rewrite|no subterm|normaliz|sin_2a",
        "arithmetic": r"lia|nia|nra|lra|inequal|power|exponent",
    }
    return frozenset(
        k for k, p in patterns.items() if re.search(p, text, re.I | re.S)
    )
