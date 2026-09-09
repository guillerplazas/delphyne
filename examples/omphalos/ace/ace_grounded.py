"""Typed, state-checked ACE evidence and bounded verifier computations.

Only training transitions may create claims. An admitted claim is a worked
transition in a named environment, not a universally valid tactic theorem.
The rendered executable guidance is derived from the checked action, never
from unchecked explanatory prose. Persistence belongs to experiment drivers.
"""

from runtime.paths import OMPHALOS_ROOT

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
import re
from typing import Literal

import runtime.pytanque_utils as pt
import runtime.rocq_server as rocq_server
from ace.ace_evidence import (
    checkable_references,
    grounding_verdict,
    import_signature,
    locate_command,
    unknown_identifier,
)
from runtime.tool_budget import (
    OperationExhausted,
    ToolLimits,
    clip_utf8,
    operation,
)

Outcome = Literal[
    "accepted", "rejected", "incomplete", "resource_exhausted", "unknown"
]
DecisionKind = Literal["reference", "bridge", "structure"]
Admission = Literal["verified", "rejected", "unavailable"]
ROOT = OMPHALOS_ROOT
_RESOURCE = re.compile(
    r"timeout|timed out|deadline|stack overflow|out of memory|memory limit|"
    r"reply exceeded|too large|operation .*allowance|operation budget",
    re.I,
)
_UNKNOWN = re.compile(
    r"transport failure|connection|server.*died|no response|failed to start|"
    r"session poisoned|broken pipe|EOF|unavailable",
    re.I,
)
_UNSAFE = re.compile(
    r"\b(?:admit|Admitted|Axiom|Axioms|Parameter|Parameters|Abort)\b|"
    r"\bUnset\s+(?:Guard|Positivity|Universe)\b",
)


def outcome_of(feedback: pt.Feedback) -> Outcome:
    if feedback.success:
        return "accepted"
    message = feedback.error_message or ""
    if _RESOURCE.search(message):
        return "resource_exhausted"
    if _UNKNOWN.search(message) or feedback.failing_index is None:
        return "unknown"
    if feedback.failing_tactic == "Qed." and (
        feedback.remaining_goals or "incomplete" in message.lower()
    ):
        return "incomplete"
    return "rejected"


@dataclass(frozen=True)
class Checked:
    feedback: pt.Feedback
    outcome: Outcome
    elapsed: float
    rpc_calls: int
    view: str


def feedback_view(feedback: pt.Feedback, outcome: Outcome, limit: int) -> str:
    # Raw goals remain in feedback, including on successful local repairs.
    text = json.dumps(
        {
            "outcome": outcome,
            "failing_tactic": feedback.failing_tactic,
            "error": feedback.error_message,
            "verified_prefix": feedback.proof_so_far,
            "total_goals": len(feedback.remaining_goals),
            "goals": feedback.remaining_goals[:4],
            "automation": (feedback.probe or [])[:4],
            "inspection": "InspectProofState(tactics=verified prefix, start=4)",
        },
        ensure_ascii=False,
    )
    return clip_utf8(text, limit)


def checked_proof(
    problem_file: str,
    theorem_name: str,
    tactics: list[str],
    limits: ToolLimits = ToolLimits(),
    assisted: bool = True,
) -> Checked:
    if _UNSAFE.search("\n".join(tactics)):
        fb = pt.Feedback(
            success=False,
            failing_index=0,
            failing_tactic="unsafe command",
            error_message="Proof obligations may not be bypassed.",
        )
        return Checked(
            fb,
            "rejected",
            0,
            0,
            feedback_view(fb, "rejected", limits.view_bytes),
        )
    with operation(limits) as op:
        try:
            fb = pt.check(
                problem_file, theorem_name, tactics, probe_automation=assisted
            )
        except Exception as exc:
            fb = pt.Feedback(
                success=False,
                error_message=f"{type(exc).__name__}: {exc}",
                proof_so_far=list(op.prefix),
                remaining_goals=list(op.goals),
            )
        outcome = outcome_of(fb)
        if op.exhausted and not fb.success:
            outcome = "resource_exhausted"
            fb = replace(fb, error_message=op.exhausted)
        view = feedback_view(fb, outcome, limits.view_bytes)
        return Checked(fb, outcome, op.elapsed, op.calls, view)


@dataclass(frozen=True)
class Inspection:
    text: str
    elapsed: float
    rpc_calls: int
    outcome: Outcome


def inspect_proof_state(
    problem_file: str,
    theorem_name: str,
    tactics: str,
    command: str = "",
    start: int = 0,
    limits: ToolLimits = ToolLimits(),
) -> Inspection:
    if start < 0:
        raise ValueError("goal offset must be nonnegative")
    if command and not re.match(
        r"^(?:Search|SearchPattern|Check|About|Print|Locate)\b",
        command.strip(),
    ):
        return Inspection("Use an introspection command.", 0, 0, "rejected")
    with operation(limits) as op:
        try:
            # Use the same functional replay machinery as InspectAt, but
            # paginate the raw goals before rendering them.
            file = str((ROOT / problem_file).resolve())
            augmented = rocq_server.augmented_path(
                file, pt.DEFAULT_EXTRA_IMPORTS
            )
            with rocq_server.MANAGER.session(augmented) as client:
                replay = pt._open_and_replay(  # pyright: ignore[reportPrivateUsage]
                    client,
                    augmented,
                    theorem_name,
                    pt.split_into_tactics(tactics),
                    stop_when_finished=False,
                    timeout=pt.PROOF_TACTIC_TIMEOUT,
                )
                if replay.start_error or replay.failing_index is not None:
                    text = (
                        replay.start_error
                        or replay.error_message
                        or "Replay failed"
                    )
                    result: Outcome = (
                        "unknown" if replay.start_error else "rejected"
                    )
                else:
                    assert replay.state is not None
                    goals = pt._safe_goals(client, replay.state)  # pyright: ignore[reportPrivateUsage]
                    op.goals = list(goals)
                    output = ""
                    if command:
                        after = client.run(
                            replay.state,
                            command,
                            timeout=pt.PROOF_TACTIC_TIMEOUT,
                        )
                        output = str(after.feedback)
                    text = json.dumps(
                        {
                            "output": output,
                            "start": start,
                            "total_goals": len(goals),
                            "goals": goals[start : start + 4],
                            "next": start + 4
                            if start + 4 < len(goals)
                            else None,
                        },
                        ensure_ascii=False,
                    )
                    result = "accepted"
        except Exception as exc:
            text = f"{type(exc).__name__}: {exc}"
            result = (
                "resource_exhausted"
                if isinstance(exc, OperationExhausted)
                or _RESOURCE.search(text)
                else "unknown"
            )
        if op.exhausted:
            text, result = op.exhausted, "resource_exhausted"
        return Inspection(
            clip_utf8(text, limits.view_bytes), op.elapsed, op.calls, result
        )


@dataclass(frozen=True)
class TrainingTransition:
    problem_file: str
    theorem_name: str
    source_cell: str
    source_sha256: str
    prefix: tuple[str, ...]
    failed_action: str
    error: str
    goals: tuple[str, ...]
    correction: tuple[str, ...]
    verified_solution: tuple[str, ...] = ()


def assert_training_transition(evidence: TrainingTransition) -> None:
    allowed = {
        Path(line.strip()).stem: (ROOT / line.strip()).resolve()
        for line in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    if (
        allowed.get(evidence.theorem_name)
        != (ROOT / evidence.problem_file).resolve()
    ):
        raise ValueError(
            "adaptation accepts exact trainX theorem/file pairs only"
        )


@dataclass(frozen=True)
class AdviceClaim:
    id: str
    kind: DecisionKind
    condition: str
    references: tuple[str, ...]
    action: tuple[str, ...]
    evidence: TrainingTransition
    environment: str
    trigger_name: str = ""
    symbols: tuple[str, ...] = ()

    def render(self) -> str:
        return (
            f"[{self.id}] Decision: {self.kind}; observed unavailable name: {self.trigger_name or 'none'}.\n"
            f"Verified local example: {' '.join(self.action)}\n"
            "Check its hypotheses against the current state; this example "
            "is not a general proof recipe."
        )


@dataclass(frozen=True)
class ClaimVerdict:
    claim: AdviceClaim
    status: Admission
    reason: str
    elapsed: float
    rpc_calls: int
    before_goals: tuple[str, ...] = ()
    after_goals: tuple[str, ...] = ()


def validate_claim(
    claim: AdviceClaim, limits: ToolLimits = ToolLimits()
) -> ClaimVerdict:
    e = claim.evidence
    assert_training_transition(e)
    training = {
        Path(line.strip()).stem
        for line in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    if e.theorem_name not in training:
        raise ValueError("advice admission accepts trainX evidence only")
    if (
        claim.action != e.correction
        or not claim.action
        or _UNSAFE.search(" ".join(claim.action))
    ):
        return ClaimVerdict(
            claim,
            "rejected",
            "action differs from supporting transition",
            0,
            0,
        )
    if import_signature(ROOT / e.problem_file) != claim.environment:
        return ClaimVerdict(claim, "unavailable", "environment changed", 0, 0)
    with operation(limits) as op:
        before: tuple[str, ...] = ()
        after: tuple[str, ...] = ()
        status: Admission = "unavailable"
        reason = "no verified application"
        try:
            initial = pt.check(e.problem_file, e.theorem_name, list(e.prefix))
            before = tuple(initial.remaining_goals)
            if (
                initial.success
                or initial.failing_tactic != "Qed."
                or tuple(initial.proof_so_far) != e.prefix
            ):
                reason = (
                    "supporting prefix did not reach the recorded open state"
                )
            else:
                missing: list[str] = []
                for ref in checkable_references(claim.references):
                    located = pt.inspect_at(
                        e.problem_file,
                        e.theorem_name,
                        "\n".join(e.prefix),
                        locate_command(ref),
                    )
                    if grounding_verdict(located) != "grounded":
                        missing.append(ref)
                if missing:
                    status, reason = (
                        "rejected",
                        "unavailable references: " + ", ".join(missing),
                    )
                else:
                    extended = [*e.prefix, *claim.action]
                    final = pt.check(e.problem_file, e.theorem_name, extended)
                    after = tuple(final.remaining_goals)
                    if final.success or (
                        outcome_of(final) == "incomplete"
                        and final.proof_so_far == extended
                        and before != after
                    ):
                        status, reason = (
                            "verified",
                            "accepted application changes the supporting state",
                        )
                    elif outcome_of(final) in ("rejected", "incomplete"):
                        status, reason = (
                            "rejected",
                            "application rejected or did not change goals",
                        )
                    else:
                        reason = "verification evidence unavailable"
        except Exception as exc:
            reason = f"{type(exc).__name__}: {exc}"
        if op.exhausted:
            status, reason = "unavailable", op.exhausted
        return ClaimVerdict(
            claim, status, reason, op.elapsed, op.calls, before, after
        )


def decision_kind(feedback: pt.Feedback) -> DecisionKind:
    if unknown_identifier(feedback.error_message or ""):
        return "reference"
    if re.search(
        r"unif|type|rewrite|ring|witness|expected",
        feedback.error_message or "",
        re.I,
    ):
        return "bridge"
    return "structure"


def select_advice(
    claims: tuple[AdviceClaim, ...],
    feedback: pt.Feedback,
    environment: str,
    limit: int = 3,
) -> tuple[AdviceClaim, ...]:
    kind = decision_kind(feedback)
    name = unknown_identifier(feedback.error_message or "")
    goals = "\n".join(feedback.remaining_goals)
    selected = [
        c
        for c in claims
        if c.environment == environment
        and c.kind == kind
        and (not c.trigger_name or c.trigger_name == name)
        and all(s in goals for s in c.symbols)
    ]
    return tuple(sorted(selected, key=lambda c: c.id)[:limit])


@dataclass(frozen=True)
class AdaptationState:
    claims: tuple[AdviceClaim, ...] = ()
    decisions: tuple[ClaimVerdict, ...] = ()
    step: int = 0

    def admit(self, verdicts: tuple[ClaimVerdict, ...]) -> "AdaptationState":
        admitted = {c.id: c for c in self.claims}
        for v in verdicts:
            if v.status == "verified":
                admitted[v.claim.id] = v.claim
        return AdaptationState(
            tuple(admitted.values()),
            (*self.decisions, *verdicts),
            self.step + 1,
        )

    def sha256(self) -> str:
        return hashlib.sha256(
            json.dumps(asdict(self), sort_keys=True).encode()
        ).hexdigest()
