"""One checked change versus fixed demos; shared by both agent harnesses.

The optional Terra episodes stop after applicability. No runtime witness,
new prover tool, adaptive bank, recovery allowance, or full-problem reset.
"""

from dataclasses import dataclass, replace
from typing import Literal
import re

import delphyne as dp

import ace.ace_applicability as aa
import ace.ace_grounded as ag
import prove_applicability as pa
import prove_grounded as pg
import runtime.pytanque_utils as pt
from runtime.admission_events import record
from runtime.model_registry import OmphalosReasoningEffort, make_model
from runtime.tool_budget import ToolLimits
from runtime.grounded_control import observe_budget


@dataclass(frozen=True)
class ChangeEpisodeResult:
    repair: pa.RepairResult
    continuation: pa.RepairResult | None
    elapsed: float


def check_change(state: aa.RepairState, limits: ToolLimits) -> ag.Checked:
    pattern, correction = aa.syntax_form(state.failed_action)
    # Do not extend the historical grammar to multi-sentence scripts.
    if (
        pattern != "change"
        or len(pt.split_into_tactics(correction)) != 1
        or len(pt.split_into_tactics(state.failed_action)) != 1
        or re.search(r"\.(?:\s|$)", state.failed_action.rstrip()[:-1])
        or "(*" in state.failed_action
    ):
        correction = ""
    answer = aa.RepairDecision("repair", pattern, correction, "local check")
    return aa.check_repair(state, answer, limits)


@dataclass(frozen=True)
class RepairCheckpoint:
    repair: pa.RepairResult
    elapsed: float = 0.0


def checkpoint_repair(
    result: pa.RepairResult, limits: dict[str, float]
) -> RepairCheckpoint:
    """Persist the phase even if the next model request is declined.

    This Compute does no verifier work; its rocq_seconds reservation is zero.
    Recording happens only on actual computation, not strategy speculation.
    """
    assert limits == {"seconds": 0.0}
    record(
        "change_phase",
        "repair_complete",
        requests=result.requests,
        executed=result.executed,
        status=result.status,
    )
    return RepairCheckpoint(result)


@dp.strategy
def change_episode(
    state: aa.RepairState,
    arm: Literal["F", "C"],
    bank: tuple[aa.RepairExample, ...],
    playbook: str,
    diagnostic_only: bool = False,
    request_limit: int = 4,
    limits: ToolLimits = ToolLimits(),
) -> dp.Strategy[
    dp.Branch | dp.Compute | dp.Fail,
    dp.PromptingPolicy,
    ChangeEpisodeResult,
]:
    if arm == "F":
        repair = yield from pa.repair_episode(
            state, "F", bank, playbook, request_limit, limits
        ).inline()
    else:
        checked = yield from dp.compute(check_change)(state, limits)
        pattern, correction = aa.syntax_form(state.failed_action)
        answer = aa.RepairDecision(
            "repair", pattern, correction, "single checked canonical candidate"
        )
        ran = aa.executed(state, answer, checked)
        if not ran:
            answer = replace(
                answer,
                decision="abstain",
                correction="",
                reason=f"Candidate not established: {checked.outcome}",
            )
        repair = pa.RepairResult(
            answer, checked, ran, 0, checked.elapsed, "checked_control"
        )
    yield from dp.compute(checkpoint_repair)(repair, {"seconds": 0.0})
    if diagnostic_only or repair.requests >= request_limit:
        return ChangeEpisodeResult(repair, None, repair.elapsed)
    remaining = 300.0 - repair.elapsed
    if remaining <= 0:
        return ChangeEpisodeResult(repair, None, repair.elapsed)
    # Reconstruct the same minimal proposal/feedback pair for both arms.
    # On a refused candidate, discard any partially executed focus prefix.
    current = state
    if repair.checked is not None:
        checked = repair.checked
        current = replace(
            state,
            prefix=tuple(checked.feedback.proof_so_far)
            if repair.executed
            else state.prefix,
            failed_action=(checked.feedback.failing_tactic or "")
            if repair.executed
            else state.failed_action,
            error=checked.feedback.error_message or "",
            outcome=checked.outcome,
            goals=tuple(checked.feedback.remaining_goals)
            if repair.executed
            else state.goals,
        )
    continuation = yield from pa.repair_episode(
        current,
        "R",
        (),
        playbook,
        request_limit - repair.requests,
        replace(limits, seconds=min(limits.seconds, remaining)),
    ).inline()
    return ChangeEpisodeResult(
        repair, continuation, repair.elapsed + continuation.elapsed
    )


def change_control_policy(
    model_name: str = "gpt-5.6-luna",
    reasoning_effort: OmphalosReasoningEffort = "medium",
    dollar_limit: float = 0.10,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        model_name,
        api="responses",
        reasoning_effort=reasoning_effort,
        for_tool_calls=True,
        convert_user_feedback_to_tool=True,
    )
    normal = pa.observe_syntax(
        dp.few_shot(
            model,
            max_requests=1,
            select_examples=pa.syntax_examples(),
            tag_user_feedback_messages=True,
        )
    )

    return observe_budget(
        {"price": dollar_limit, "rocq_seconds": 300.0, "num_requests": 4.0}
    ) @ (pg.grounded_search(typed_limits=True) & normal)
