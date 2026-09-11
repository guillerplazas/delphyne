"""Opt-in proof edits and checked repairs; shared by both agent harnesses.

The policy uses the incumbent search and prompting machinery. Recovery alone
adds a one-unit budget; no polished controls or playbook changes are implied.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import delphyne as dp
from delphyne.stdlib.queries import ExampleSelector, SelectedExample

import ace.ace_applicability as aa
import ace.ace_grounded as ag
from ace.change_progress import ProgressAudit, audit_progress
import prove_grounded as pg
from prove_agentic import ReadSkill, SearchRocq
import runtime.pytanque_utils as pt
from runtime.admission_events import record
from runtime.grounded_control import (
    DecisionControl,
    controlled_prompt,
    limited_prompt,
    observe_budget,
)
from runtime.model_registry import OmphalosReasoningEffort, make_model
from runtime.tool_budget import ToolLimits


@dataclass(frozen=True)
class ProofContinuation:
    mode: Literal["suffix", "replace"]
    script: str


@dataclass
class ContinueVerifiedProof(
    dp.Query[
        dp.Response[
            ProofContinuation,
            ReadSkill | SearchRocq | pg.InspectProofState,
        ]
    ]
):
    spec: pt.ProblemSpec
    available_skills: dict[str, str]
    toolset: str = "core"
    turn_budget: int = 64
    prefix: dp.AnswerPrefix = ()
    playbook: str = ""
    render_version: int = 3
    decision: str = "propose a proof"
    verified_prefix: str = ""
    lesson: str = ""
    control: DecisionControl | None = None

    __parser__ = dp.structured.response

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        return [ReadSkill, SearchRocq, pg.InspectProofState]


def continuation_query(
    q: pg.ProposeProofScriptGrounded,
) -> ContinueVerifiedProof:
    return ContinueVerifiedProof(
        spec=q.spec,
        available_skills=q.available_skills,
        toolset=q.toolset,
        turn_budget=q.turn_budget,
        prefix=q.prefix,
        playbook=q.playbook,
        render_version=q.render_version,
        decision=f"{q.decision}; {q.query_name()}",
        verified_prefix=q.verified_prefix,
        lesson=q.lesson,
        control=q.control,
    )


def assemble(edit: ProofContinuation, prefix: Sequence[str]) -> list[str]:
    tactics = pt.split_into_tactics(edit.script)
    if not tactics:
        raise ValueError("Empty proof continuation")
    if edit.mode == "suffix":
        return [*prefix, *tactics]
    if edit.mode == "replace":
        return tactics
    raise ValueError("Unknown continuation mode")


@dp.strategy
def demonstrate_continuation(
    spec: pt.ProblemSpec, prefix: tuple[str, ...], expected: tuple[str, ...]
) -> dp.Strategy[dp.Branch | dp.Fail, dp.PromptingPolicy, list[str]]:
    """Executable response-contract examples; not selected as paid advice."""
    response = yield from dp.branch(
        ContinueVerifiedProof(
            spec, {}, verified_prefix="\n".join(prefix)
        ).using(dp.ambient_pp)
    )
    if isinstance(response.parsed, dp.ToolRequests):
        yield from dp.fail(label="expected_final_edit")
        return []
    result = assemble(response.parsed.final, prefix)
    if result != list(expected):
        yield from dp.fail(label="incorrect_assembly")
    return result


def checked_syntax(
    state: aa.RepairState, limits: dict[str, Any]
) -> ag.Checked:
    """One finite candidate, with unassisted verification and no model call.

    A dictionary exposes the precise reservation to the incumbent search.
    The historical grammar and all failed candidates remain unchanged.
    """
    pattern, correction = aa.syntax_form(state.failed_action)
    answer = aa.RepairDecision("repair", pattern, correction, "local check")
    checked = aa.check_repair(state, answer, ToolLimits(**limits))
    record(
        "checked_syntax",
        "accepted"
        if aa.executed(state, answer, checked) or checked.feedback.success
        else "declined",
        pattern=pattern,
        correction=correction,
        outcome=checked.outcome,
        original_prefix=list(state.prefix),
        verified_prefix=checked.feedback.proof_so_far,
    )
    return checked


def progress_evidence(
    state: aa.RepairState, checked: ag.Checked, limits: dict[str, Any]
) -> ProgressAudit:
    audit = audit_progress(state, checked, ToolLimits(**limits))
    record(
        "verified_progress",
        "useful" if audit.useful else "unestablished",
        reason=audit.reason,
        outcome=audit.outcome,
        prefix=checked.feedback.proof_so_far,
    )
    return audit


def examples() -> ExampleSelector:
    legacy = pg.grounded_examples()

    def select(
        env: dp.PolicyEnv, q: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        # Legacy demonstrations return full scripts, not typed edits. Protocol
        # demonstrations are tested separately and do not add training advice.
        if isinstance(q, ContinueVerifiedProof):
            return []
        from prove_applicability import DecideSyntaxRepair, syntax_examples

        if isinstance(q, DecideSyntaxRepair):
            chosen = syntax_examples()(env, q)
        else:
            chosen = legacy(env, q)
        return [
            SelectedExample(example=e, index=i, similarity=None)
            for i, e in enumerate(chosen)
        ]

    return ExampleSelector(select)


def continuation_policy(
    model_name: str = "gpt-5.6-luna",
    reasoning_effort: OmphalosReasoningEffort = "medium",
    recovery: bool = False,
    turn_budget: int = 64,
    typed_limits: bool = False,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        model_name,
        api="responses",
        reasoning_effort=reasoning_effort,
        for_tool_calls=True,
        convert_user_feedback_to_tool=True,
    )
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=examples(),
        tag_user_feedback_messages=True,
    )
    budgets = {
        "price": 0.10,
        "rocq_seconds": 300.0,
        "num_requests": float(turn_budget),
    }
    if not recovery:
        return observe_budget(budgets) @ (
            pg.grounded_search(typed_limits=typed_limits) & normal
        )
    from runtime.campaign_budget import CampaignResponsesModel

    if not isinstance(model, CampaignResponsesModel):
        raise ValueError("Recovery requires campaign accounting")
    budgets["recoveries"] = 1.0
    return (
        dp.with_budget(dp.BudgetLimit(budgets))
        @ observe_budget(budgets)
        @ (
            pg.grounded_search(typed_limits=typed_limits)
            & controlled_prompt(normal, limited_prompt(model, examples()))
        )
    )
