"""Composed grounded ACE strategies, with policies and examples separated.

The new query contracts leave archived ACE prompts untouched. Offline
adaptation starts from already-paid generated training transitions. It
re-verifies their evidence, reflects, verifies one correction, curates and
audits it. Immutable successor states are returned; drivers alone persist.
"""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Any, cast

import yaml
import delphyne as dp
from delphyne.stdlib.policies import search_policy
from delphyne.stdlib.streams import SpendingDeclined, spend_on
from delphyne.stdlib.queries import SelectedExample, ExampleSelector

import ace.ace_grounded as ag
import runtime.pytanque_utils as pt
import runtime.skills as sk
from ace.ace_evidence import import_signature, unknown_identifier
from runtime.model_registry import ApiType, OmphalosReasoningEffort, make_model
from prove_agentic import ReadSkill, SearchRocq
from prove_ace import _ace_examples  # pyright: ignore[reportPrivateUsage]
from runtime.stall import stalled, view_of_feedback
from runtime.tool_budget import ToolLimits, clip_utf8


@search_policy
def grounded_search[P, T](
    tree: dp.Tree[dp.Branch | dp.Compute | dp.Fail, P, T],
    env: dp.PolicyEnv,
    policy: P,
) -> dp.StreamGen[T]:
    """DFS with resource admission for Compute, under the parent budget."""
    node = tree.node
    if isinstance(node, dp.Success):
        yield dp.Solution(node.success)
    elif isinstance(node, dp.Compute):
        query = node.query.attached.query
        args = cast(dict[str, Any], getattr(query, "args"))
        limits = args.get("limits", {})
        seconds = (
            float(cast(dict[str, Any], limits).get("seconds", 60))
            if isinstance(limits, dict)
            else 60.0
        )

        def perform() -> tuple[str, dp.Budget]:
            answer = node.run_computation_with_cache(cache=env.cache)
            raw: Any = yaml.safe_load(answer)
            elapsed = (
                float(cast(dict[str, Any], raw).get("elapsed", 0))
                if isinstance(raw, dict)
                else 0.0
            )
            return answer, dp.Budget({"rocq_seconds": elapsed})

        answer = yield from spend_on(
            perform, dp.Budget({"rocq_seconds": seconds})
        )
        if isinstance(answer, SpendingDeclined):
            return
        parsed = node.query.attached.parse_answer(dp.Answer(None, answer))
        assert not isinstance(parsed, dp.ParseError)
        yield from grounded_search()(tree.child(parsed), env, policy)
    elif isinstance(node, dp.Branch):
        yield from node.cands.stream(env, policy).bind(
            lambda candidate: grounded_search()(
                tree.child(candidate.tracked), env, policy
            )
        )
    else:
        return


@dataclass
class InspectProofState(dp.AbstractTool[str]):
    """Inspect a verified prefix with bounded output. Use start=4, 8, ...
    for omitted goals. Optional command: Search, Check, About or Locate.
    Supply complete Rocq sentences in tactics and command.
    """

    tactics: str
    command: str = ""
    start: int = 0


@dataclass
class ProposeProofScriptGrounded(
    dp.Query[
        dp.Response[
            str | dp.WrappedParseError,
            ReadSkill | SearchRocq | InspectProofState,
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

    def parser(
        self,
    ) -> dp.Parser[
        dp.Response[
            str | dp.WrappedParseError,
            ReadSkill | SearchRocq | InspectProofState,
        ]
    ]:
        return dp.last_code_block.wrap_errors.response_with(
            ReadSkill | SearchRocq | InspectProofState
        )

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        tools = self.parser().settings.tools
        return tools.tool_types if tools else []


@dataclass
class ResolveProofReference(ProposeProofScriptGrounded):
    """Choose a reference whose availability and type match this state."""


@dataclass
class ChooseProofBridge(ProposeProofScriptGrounded):
    """Choose a cast, normal-form or side-condition bridge, then verify."""


@dataclass
class ChooseProofStructure(ProposeProofScriptGrounded):
    """Choose an invariant, case split or structural opener, then verify."""


@dp.strategy
def prove_theorem_grounded(
    problem_file: str,
    theorem_name: str,
    playbook: str = "",
    claims: tuple[ag.AdviceClaim, ...] = (),
    turn_budget: int = 64,
    limits: ToolLimits = ToolLimits(),
    verifier_seconds: float = 300,
    focused: bool = True,
    restart: bool = True,
    admission: bool = True,
) -> dp.Strategy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, str]:
    spec = pt.parse_problem(problem_file, show_definitions=True)
    environment = import_signature(problem_file)
    prefix: list[dp.AnswerPrefixElement] = []
    feedbacks: list[ag.Checked] = []
    spent = 0.0
    repair_used = restart_used = False
    repair_attempted = False
    action = "propose a proof"
    for _ in range(turn_budget):
        if spent >= verifier_seconds:
            yield from dp.fail(label="verifier_budget_exhausted")
        last = feedbacks[-1] if feedbacks else None
        selected: tuple[ag.AdviceClaim, ...] = ()
        if (
            admission
            and last is not None
            and last.outcome in ("rejected", "incomplete")
        ):
            selected = ag.select_advice(claims, last.feedback, environment)
        views = [
            v
            for f in feedbacks
            if (v := view_of_feedback(f.feedback)) is not None
        ]
        if restart and (
            stalled(views, "seenstate", 4)
            or (repair_attempted and not restart_used)
        ):
            if not repair_used:
                repair_used = True
                action = "repair only the suffix after the verified prefix"
                feedbacks = feedbacks[-1:]
            elif not restart_used:
                restart_used = True
                action = (
                    "choose a different structural plan; prior plan stalled"
                )
                # Keep a bounded state summary but discard stale dialogue.
                prefix = [
                    dp.FeedbackMessage("feedback", "restart", action, last)
                ]
                feedbacks = []
                last = None
            else:
                yield from dp.fail(label="repair_and_restart_exhausted")
        query_class = ProposeProofScriptGrounded
        if (
            focused
            and last is not None
            and last.outcome in ("rejected", "incomplete")
        ):
            query_class = {
                "reference": ResolveProofReference,
                "bridge": ChooseProofBridge,
                "structure": ChooseProofStructure,
            }[ag.decision_kind(last.feedback)]
        lesson = "\n\n".join(c.render() for c in selected)
        # No free-form advice enters the validated-admission arm. The old
        # artifact is retained only for an explicit admission ablation.
        rendered = "" if admission else playbook
        query = query_class(
            spec=spec,
            available_skills=sk.list_skills(),
            turn_budget=turn_budget,
            prefix=tuple(prefix),
            playbook=rendered,
            decision=action,
            verified_prefix="\n".join(last.feedback.proof_so_far)
            if last
            else "",
            lesson=lesson,
        )
        response = yield from dp.branch(query.using(dp.ambient_pp))
        prefix.append(dp.OracleMessage("oracle", response.answer))
        call_limits = replace(
            limits, seconds=min(limits.seconds, verifier_seconds - spent)
        )
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                if isinstance(call, ReadSkill):
                    result = clip_utf8(
                        sk.read_skill(call.skill_name), limits.view_bytes
                    )
                else:
                    if spent >= verifier_seconds:
                        yield from dp.fail(label="verifier_budget_exhausted")
                    call_limits = replace(
                        limits,
                        seconds=min(limits.seconds, verifier_seconds - spent),
                    )
                    if isinstance(call, SearchRocq):
                        tactics = (
                            "\n".join(last.feedback.proof_so_far)
                            if last
                            else ""
                        )
                        command, start = call.command, 0
                    else:
                        tactics, command, start = (
                            call.tactics,
                            call.command,
                            call.start,
                        )
                    inspected = yield from dp.compute(ag.inspect_proof_state)(
                        problem_file,
                        theorem_name,
                        tactics,
                        command,
                        start,
                        call_limits,
                    )
                    spent += inspected.elapsed
                    result = inspected.text
                prefix.append(
                    dp.ToolResult(
                        "tool", response.answer.tool_calls[i], result
                    )
                )
            continue
        proposed = response.parsed.final
        if isinstance(proposed, dp.WrappedParseError):
            prefix.append(
                dp.FeedbackMessage("feedback", "parse", str(proposed.error))
            )
            continue
        checked = yield from dp.compute(ag.checked_proof)(
            problem_file,
            theorem_name,
            pt.split_into_tactics(proposed),
            call_limits,
        )
        spent += checked.elapsed
        if checked.feedback.success:
            return "\n".join(checked.feedback.proof_so_far)
        if repair_used and not restart_used:
            repair_attempted = True
        feedbacks.append(checked)
        prefix.append(
            dp.FeedbackMessage("feedback", checked.outcome, meta=checked)
        )
    yield from dp.fail(label="turn_budget_exhausted")
    return ""  # unreachable success; Fail has no outgoing policy branch


def grounded_examples() -> ExampleSelector:
    legacy = _ace_examples()

    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        own = env.examples.examples_for(query.query_name())
        if own:
            return [
                SelectedExample(example=e, index=i, similarity=None)
                for i, e in enumerate(own[:2])
            ]
        return [
            SelectedExample(example=e, index=i, similarity=None)
            for i, e in enumerate(legacy(env, query))
        ]

    return ExampleSelector(select)


@dp.ensure_compatible(prove_theorem_grounded)
def prove_theorem_grounded_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = "medium",
    convert_user_feedback_to_tool: bool = True,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        model_name,
        for_tool_calls=True,
        api=api,
        reasoning_effort=reasoning_effort,
        convert_user_feedback_to_tool=convert_user_feedback_to_tool,
    )
    return grounded_search() & dp.few_shot(
        model,
        temperature=temperature,
        max_requests=1,
        select_examples=grounded_examples(),
        tag_user_feedback_messages=True,
    )


@dataclass
class GroundedReflection:
    failed_step: str
    explanation: str
    applicability: str
    correction: tuple[str, ...]
    references: tuple[str, ...]
    abstain: bool = False


@dataclass
class ReflectGroundedTransition(dp.Query[GroundedReflection]):
    evidence: ag.TrainingTransition
    verified_solution: tuple[str, ...]
    feedback: ag.Checked
    __parser__ = dp.last_code_block.yaml


@dataclass
class AdmissionChoice:
    keep: bool
    reason: str
    condition: str = ""


@dataclass
class CurateGroundedClaim(dp.Query[AdmissionChoice]):
    reflection: GroundedReflection
    verdict: ag.ClaimVerdict
    __parser__ = dp.last_code_block.yaml


@dataclass
class AuditGroundedClaim(dp.Query[AdmissionChoice]):
    verdict: ag.ClaimVerdict
    condition: str
    __parser__ = dp.last_code_block.yaml


@dp.strategy
def adapt_grounded_transition(
    evidence: ag.TrainingTransition,
    state: ag.AdaptationState = ag.AdaptationState(),
    limits: ToolLimits = ToolLimits(),
) -> dp.Strategy[
    dp.Branch | dp.Compute | dp.Fail, dp.IPDict, ag.AdaptationState
]:
    ag.assert_training_transition(evidence)
    # Verify the supplied current-problem solution, not just its cache tag.
    solution: tuple[str, ...] = ()
    if evidence.verified_solution:
        checked_solution = yield from dp.compute(ag.checked_proof)(
            evidence.problem_file,
            evidence.theorem_name,
            list(evidence.verified_solution),
            limits,
            assisted=False,
        )
        if checked_solution.feedback.success:
            solution = evidence.verified_solution
    failed = yield from dp.compute(ag.checked_proof)(
        evidence.problem_file,
        evidence.theorem_name,
        [*evidence.prefix, evidence.failed_action],
        limits,
        assisted=False,
    )
    reflection = yield from dp.branch(
        ReflectGroundedTransition(evidence, solution, failed).using(
            _reflector_policy
        )
    )
    if reflection.abstain or failed.outcome in (
        "accepted",
        "resource_exhausted",
        "unknown",
    ):
        return replace(state, step=state.step + 1)
    corrected = replace(evidence, correction=reflection.correction)
    kind = ag.decision_kind(failed.feedback)
    claim = ag.AdviceClaim(
        id=f"grounded-{evidence.source_sha256[:10]}-{state.step}",
        kind=kind,
        condition=reflection.applicability,
        references=reflection.references,
        action=reflection.correction,
        evidence=corrected,
        environment=import_signature(evidence.problem_file),
        trigger_name=unknown_identifier(evidence.error) or "",
    )
    verified = yield from dp.compute(ag.validate_claim)(claim, limits)
    if verified.status != "verified":
        return state.admit((verified,))
    curation = yield from dp.branch(
        CurateGroundedClaim(reflection, verified).using(_curator_policy)
    )
    if not curation.keep:
        return state.admit(
            (replace(verified, status="rejected", reason=curation.reason),)
        )
    audit = yield from dp.branch(
        AuditGroundedClaim(
            verified, curation.condition or claim.condition
        ).using(_auditor_policy)
    )
    if not audit.keep:
        return state.admit(
            (replace(verified, status="rejected", reason=audit.reason),)
        )
    # Editorial conditions may narrow guidance; the checked action is immutable.
    claim = replace(
        claim,
        condition=audit.condition or curation.condition or claim.condition,
    )
    return state.admit((replace(verified, claim=claim),))


@dp.strategy
def adapt_grounded_batch(
    transitions: tuple[ag.TrainingTransition, ...],
    state: ag.AdaptationState = ag.AdaptationState(),
) -> dp.Strategy[dp.Branch, dp.IPDict, ag.AdaptationState]:
    # Each episode sees the batch-start snapshot. Only verified additions
    # are merged into the successor, which the caller may persist once.
    successor = state
    for evidence in transitions:
        result = yield from dp.branch(
            adapt_grounded_transition(evidence, state).using(
                adapt_grounded_policy
            )
        )
        successor = successor.admit(result.decisions[len(state.decisions) :])
    return successor


@dp.strategy
def _adaptation_iteration(
    batches: tuple[tuple[ag.TrainingTransition, ...], ...],
    previous: tuple[int, ag.AdaptationState] | None,
) -> dp.Strategy[
    dp.Branch | dp.Fail,
    dp.IPDict,
    tuple[ag.AdaptationState, tuple[int, ag.AdaptationState]],
]:
    index, state = previous or (0, ag.AdaptationState())
    if index >= len(batches):
        yield from dp.fail(label="adaptation_complete")
    successor = yield from dp.branch(
        adapt_grounded_batch(batches[index], state).using(_iteration_policy)
    )
    return successor, (index + 1, successor)


@dp.strategy
def adapt_grounded(
    batches: tuple[tuple[ag.TrainingTransition, ...], ...],
) -> dp.Strategy[dp.Branch, dp.IPDict, ag.AdaptationState]:
    return (
        yield from dp.branch(
            dp.iterate(
                lambda previous: _adaptation_iteration(
                    batches, previous
                ).using(_iteration_policy)
            )
        )
    )


def adapt_grounded_policy(
    policy: dp.IPDict,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.IPDict]:
    return grounded_search() & policy


def grounded_training_policy(
    model_name: str = "gpt-5.6-luna",
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.IPDict]:
    model = make_model(model_name, api="responses", reasoning_effort="medium")
    pp = dp.few_shot(model, max_requests=1, tag_user_feedback_messages=True)
    return grounded_search() & {"reflector": pp, "curator": pp, "auditor": pp}


def _reflector_policy(policy: dp.IPDict) -> dp.PromptingPolicy:
    return cast(dp.PromptingPolicy, policy["reflector"])


def _curator_policy(policy: dp.IPDict) -> dp.PromptingPolicy:
    return cast(dp.PromptingPolicy, policy["curator"])


def _auditor_policy(policy: dp.IPDict) -> dp.PromptingPolicy:
    return cast(dp.PromptingPolicy, policy["auditor"])


def _iteration_policy(
    policy: dp.IPDict,
) -> dp.Policy[dp.Branch | dp.Fail | dp.Skippable, dp.IPDict]:
    return dp.dfs() & policy
