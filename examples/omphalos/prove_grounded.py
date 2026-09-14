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
import ace.ace_applicability as aa
from ace.ace_applicability import RepairExample as SyntaxExample
import runtime.pytanque_utils as pt
import runtime.skills as sk
import runtime.admission_events as events
from ace.ace_evidence import import_signature, unknown_identifier
from runtime.model_registry import ApiType, OmphalosReasoningEffort, make_model
from prove_agentic import ReadSkill, SearchRocq
from prove_ace import _ace_examples  # pyright: ignore[reportPrivateUsage]
from runtime.stall import stalled, view_of_feedback
from runtime.tool_budget import ToolLimits, clip_utf8
from runtime.grounded_control import DecisionControl
from ace import rocq_snippets as rs


@search_policy
def grounded_search[P, T](
    tree: dp.Tree[dp.Branch | dp.Compute | dp.Fail, P, T],
    env: dp.PolicyEnv,
    policy: P,
    typed_limits: bool = False,
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
            limits.seconds
            if typed_limits and isinstance(limits, ToolLimits)
            else (
                float(cast(dict[str, Any], limits).get("seconds", 60))
                if isinstance(limits, dict)
                else 60.0
            )
        )

        def perform() -> tuple[str, dp.Budget]:
            before = events.compute_invocations
            answer = node.run_computation_with_cache(cache=env.cache)
            raw: Any = yaml.safe_load(answer)
            elapsed = (
                float(cast(dict[str, Any], raw).get("elapsed", 0))
                if isinstance(raw, dict)
                else 0.0
            )
            if typed_limits:
                events.record(
                    "compute",
                    "settled",
                    elapsed=elapsed,
                    estimate_seconds=seconds,
                    cached=events.compute_invocations == before,
                )
            return answer, dp.Budget({"rocq_seconds": elapsed})

        answer = yield from spend_on(
            perform, dp.Budget({"rocq_seconds": seconds})
        )
        if isinstance(answer, SpendingDeclined):
            return
        parsed = node.query.attached.parse_answer(dp.Answer(None, answer))
        assert not isinstance(parsed, dp.ParseError)
        yield from grounded_search(typed_limits=typed_limits)(
            tree.child(parsed), env, policy
        )
    elif isinstance(node, dp.Branch):
        yield from node.cands.stream(env, policy).bind(
            lambda candidate: grounded_search(typed_limits=typed_limits)(
                tree.child(candidate.tracked), env, policy
            )
        )
    else:
        if typed_limits:
            events.record("stop", str(node.error.label))
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
    control: DecisionControl | None = None
    snippet_checks: bool = False
    snippet_contexts: tuple[rs.SnippetContext, ...] = ()

    @property
    def snippet_catalog(self) -> str:
        return rs.context_catalog(self.snippet_contexts)

    def parser(
        self,
    ) -> dp.Parser[
        dp.Response[
            str | dp.WrappedParseError,
            ReadSkill | SearchRocq | InspectProofState,
        ]
    ]:
        if not self.snippet_checks:
            return dp.last_code_block.wrap_errors.response_with(
                ReadSkill | SearchRocq | InspectProofState
            )
        parser: dp.Parser[
            dp.Response[
                str | dp.WrappedParseError,
                ReadSkill
                | SearchRocq
                | InspectProofState
                | rs.CheckRocqSnippet,
            ]
        ] = dp.last_code_block.wrap_errors.response_with(
            ReadSkill | SearchRocq | InspectProofState | rs.CheckRocqSnippet
        )
        # The optional tool is handled by the same strategy. Keeping the
        # legacy query's generic type preserves existing subclasses.
        return cast(Any, parser)

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


@dataclass
class ProposeProofScriptGroundedSnippets(ProposeProofScriptGrounded):
    """Versioned flagship tool interface; legacy templates stay untouched."""


@dataclass
class ResolveProofReferenceSnippets(ResolveProofReference):
    """Context-bound reference decisions."""


@dataclass
class ChooseProofBridgeSnippets(ChooseProofBridge):
    """Context-bound bridge decisions."""


@dataclass
class ChooseProofStructureSnippets(ChooseProofStructure):
    """Context-bound structural decisions."""


def _last_feedback(checks: Sequence[ag.Checked]) -> ag.Checked | None:
    return checks[-1] if checks else None


def _no_branch_metadata(_: Any) -> None:
    return None


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
    polished: bool = False,
    resource_recovery: bool = False,
    matched_advice: bool = False,
    output_recovery: bool = False,
    syntax_mode: str = "",
    syntax_bank: tuple["SyntaxExample", ...] = (),
    continuation: bool = False,
    checked_repair: bool = False,
    verified_recovery: bool = False,
    bounded_exploration: bool = False,
    exploration_v2: bool = False,
    compact_history: bool = False,
    feedback_version: int = 1,
    prompt_turn_budget: int | None = None,
    snippet_tools: bool = False,
) -> dp.Strategy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, str]:
    if feedback_version not in (1, 2):
        raise ValueError("Unknown goal feedback version")
    spec = pt.parse_problem(problem_file, show_definitions=True)
    environment = import_signature(problem_file)
    prefix: list[dp.AnswerPrefixElement] = []
    feedbacks: list[ag.Checked] = []
    spent = 0.0
    repair_used = restart_used = False
    repair_attempted = False
    action = "propose a proof"
    recovery_state: tuple[str, ...] | None = None
    syntax_seen: set[tuple[str, ...]] = set()
    audited: set[tuple[str, ...]] = set()
    useful_prefix: tuple[str, ...] | None = None
    exploration_used = False
    snippet_contexts: dict[str, rs.SnippetContext] = {}
    snippet_receipts: dict[tuple[str, str], rs.SnippetReceipt] = {}
    snippet_probes = 0
    if snippet_tools:
        initial = rs.context_for(problem_file, theorem_name)
        snippet_contexts[initial.identifier] = initial
    for _ in range(turn_budget):
        if spent >= verifier_seconds:
            yield from dp.fail(label="verifier_budget_exhausted")
        last = _last_feedback(feedbacks)
        if (
            (bounded_exploration or exploration_v2)
            and not exploration_used
            and last is not None
        ):
            logical = [
                v
                for f in feedbacks
                if f.outcome in ("rejected", "incomplete")
                if (v := view_of_feedback(f.feedback)) is not None
            ]
            if last.outcome in ("rejected", "incomplete") and stalled(
                logical, "seenstate", 2 if exploration_v2 else 4
            ):
                from prove_coverage import exploration_space

                if exploration_v2:
                    from prove_coverage_cycle import exploration_space_v2

                    exploration_space = exploration_space_v2
                exploration_used = True
                explored = yield from dp.branch(
                    exploration_space(
                        problem_file, theorem_name, last, playbook, limits
                    )
                )
                if explored is not None:
                    spent += explored.elapsed
                    if explored.checked.feedback.success:
                        return "\n".join(
                            explored.checked.feedback.proof_so_far
                        )
                    last = explored.checked
                    feedbacks.append(last)
                    # A real proposal/result pair keeps Responses feedback
                    # translation valid after replacing stale dialogue.
                    prefix = [
                        dp.OracleMessage(
                            "oracle",
                            dp.Answer(
                                None, f"```rocq\n{explored.script}\n```"
                            ),
                        ),
                        dp.FeedbackMessage(
                            "feedback", last.outcome, meta=last
                        ),
                    ]
        if checked_repair and last is not None:
            from prove_continuation import checked_syntax

            state = aa.RepairState(
                problem_file,
                theorem_name,
                tuple(last.feedback.proof_so_far),
                last.feedback.failing_tactic or "",
                last.feedback.error_message or "",
                last.outcome,
                tuple(last.feedback.remaining_goals),
                environment,
            )
            key = (*state.prefix, state.failed_action)
            if aa.eligible(state) and key not in syntax_seen:
                syntax_seen.add(key)
                repaired: ag.Checked = yield from dp.compute(checked_syntax)(
                    state,
                    {
                        "seconds": min(
                            limits.seconds, verifier_seconds - spent
                        ),
                        "rpc_calls": limits.rpc_calls,
                        "view_bytes": limits.view_bytes,
                    },
                )
                spent += repaired.elapsed
                if repaired.feedback.success:
                    return "\n".join(repaired.feedback.proof_so_far)
                pattern, correction = aa.syntax_form(state.failed_action)
                decision = aa.RepairDecision(
                    "repair", pattern, correction, "local check"
                )
                if aa.executed(state, decision, repaired):
                    feedbacks.append(repaired)
                    last = _last_feedback(feedbacks)
                    # The checked correction is a proposal/result pair, as
                    # required by Responses feedback-to-tool translation.
                    prefix.extend(
                        [
                            dp.OracleMessage(
                                "oracle",
                                dp.Answer(
                                    None,
                                    "```rocq\n"
                                    + "\n".join(repaired.feedback.proof_so_far)
                                    + "\n```",
                                ),
                            ),
                            dp.FeedbackMessage(
                                "feedback", repaired.outcome, meta=repaired
                            ),
                        ]
                    )
                else:
                    prefix.append(
                        dp.OracleMessage(
                            "oracle",
                            dp.Answer(
                                None,
                                "```rocq\n"
                                + "\n".join((*state.prefix, correction))
                                + "\n```",
                            ),
                        )
                    )
                    prefix.append(
                        dp.FeedbackMessage(
                            "feedback",
                            "checked_repair_declined",
                            "Canonical syntax candidate was not established; keep the prior verified prefix. "
                            + (
                                repaired.feedback.error_message
                                or repaired.outcome
                            ),
                        )
                    )
        if spent >= verifier_seconds:
            yield from dp.fail(label="verifier_budget_exhausted")
        if verified_recovery and last is not None:
            from prove_continuation import progress_evidence

            current = tuple(last.feedback.proof_so_far)
            if (
                useful_prefix is not None
                and current[: len(useful_prefix)] != useful_prefix
            ):
                useful_prefix = None
            if (
                current not in audited
                and len(feedbacks) >= 2
                and ag.recent_progress(feedbacks[-2:])
            ):
                audited.add(current)
                before = _last_feedback(feedbacks[:-1])
                assert before is not None
                state = aa.RepairState(
                    problem_file,
                    theorem_name,
                    tuple(before.feedback.proof_so_far),
                    before.feedback.failing_tactic or "",
                    before.feedback.error_message or "",
                    before.outcome,
                    tuple(before.feedback.remaining_goals),
                    environment,
                )
                # Audit evidence, not a goal-count proxy, authorizes recovery.
                evidence = yield from dp.compute(progress_evidence)(
                    state,
                    last,
                    {"seconds": min(10.0, verifier_seconds - spent)},
                )
                spent += evidence.elapsed
                if evidence.useful:
                    useful_prefix = current
        if spent >= verifier_seconds:
            yield from dp.fail(label="verifier_budget_exhausted")
        recovery_reason = ""
        if polished and last is not None and recovery_state is not None:
            state = tuple(last.feedback.proof_so_far) + tuple(
                last.feedback.remaining_goals
            )
            if state == recovery_state:
                yield from dp.fail(label="recovery_no_progress")
            recovery_state = None
        selected: tuple[ag.AdviceClaim, ...] = ()
        if (
            admission
            and last is not None
            and last.outcome in ("rejected", "incomplete")
        ):
            selected = (
                ag.select_matched_advice(claims, last.feedback, environment)
                if matched_advice
                else ag.select_advice(claims, last.feedback, environment)
            )
        if (
            polished
            and matched_advice
            and last is not None
            and last.outcome in ("rejected", "incomplete")
        ):
            selected = ag.select_matched_advice(
                claims, last.feedback, environment
            )
        views = [
            v
            for f in feedbacks
            if not polished or f.outcome in ("rejected", "incomplete")
            if (v := view_of_feedback(f.feedback)) is not None
        ]
        if polished and resource_recovery and last is not None:
            if last.outcome in ("unknown", "resource_exhausted"):
                recovery_reason = "resource"
                action = "use a cheaper computation or representation at the verified prefix; the previous attempt has no logical verdict"
            elif stalled(views, "seenstate", 4):
                recovery_reason = "stagnation"
                action = "repair only the suffix after the verified prefix; close the outstanding goals with a different tactic"
            if recovery_reason:
                recovery_state = tuple(last.feedback.proof_so_far) + tuple(
                    last.feedback.remaining_goals
                )
                # Responses converts verifier feedback into a tool result.
                # Keep its immediately preceding proof proposal as well.
                prefix = prefix[-2:]
        if restart and (
            stalled(views, "seenstate", 4)
            or (repair_attempted and not restart_used)
        ):
            if not repair_used:
                repair_used = True
                action = "repair only the suffix after the verified prefix"
                del feedbacks[:-1]
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
        if snippet_tools:
            query_class = {
                ProposeProofScriptGrounded: ProposeProofScriptGroundedSnippets,
                ResolveProofReference: ResolveProofReferenceSnippets,
                ChooseProofBridge: ChooseProofBridgeSnippets,
                ChooseProofStructure: ChooseProofStructureSnippets,
            }[query_class]
        if snippet_tools and last is not None:
            current = rs.context_for(
                problem_file, theorem_name, tuple(last.feedback.proof_so_far)
            )
            snippet_contexts[current.identifier] = current
        query = query_class(
            spec=spec,
            available_skills=sk.list_skills(),
            turn_budget=turn_budget
            if prompt_turn_budget is None
            else prompt_turn_budget,
            prefix=tuple(prefix),
            playbook=rendered,
            decision=action,
            verified_prefix="\n".join(last.feedback.proof_so_far)
            if last
            else "",
            lesson=lesson,
            control=DecisionControl(
                min(limits.seconds, verifier_seconds - spent),
                recovery_reason,
                output_recovery
                and not recovery_reason
                and ag.recent_progress(feedbacks[-4:]),
                matched_advice,
            )
            if polished
            else None,
            snippet_checks=snippet_tools and snippet_probes < 4,
            snippet_contexts=tuple(snippet_contexts.values())[-6:],
        )
        if compact_history:
            from prove_coverage_cycle import compact_query

            query = compact_query(query)
        syntax_state = None
        syntax_correction = ""
        syntax_query: (
            dp.AbstractQuery[
                dp.Response[Any, ReadSkill | SearchRocq | InspectProofState]
            ]
            | None
        ) = None
        if syntax_mode:
            from prove_applicability import DecideSyntaxRepair

            if syntax_mode not in ("F", "A"):
                raise ValueError("syntax_mode must be F or A")
            if last is not None:
                state = aa.RepairState(
                    problem_file,
                    theorem_name,
                    tuple(last.feedback.proof_so_far),
                    last.feedback.failing_tactic or "",
                    last.feedback.error_message or "",
                    last.outcome,
                    tuple(last.feedback.remaining_goals),
                    environment,
                )
                key = (*state.prefix, state.failed_action)
                if aa.eligible(state) and key not in syntax_seen:
                    syntax_state = state
                    ids = aa.select_ids(state, syntax_bank, syntax_mode)
                    syntax_query = DecideSyntaxRepair(
                        state,
                        sk.list_skills(),
                        syntax_mode,
                        ids,
                        tuple(prefix),
                        rendered,
                    )
        continuation_query = None
        if continuation and last is not None:
            from prove_continuation import (
                continuation_query as make_continuation,
            )

            if verified_recovery:
                # No new verifier preflight treatment: the checker itself
                # reserves its work exactly as in the incumbent.
                query.control = DecisionControl(
                    0.0, may_downshift=useful_prefix is not None
                )
            continuation_query = make_continuation(query)
        response: dp.Response[Any, ReadSkill | SearchRocq | InspectProofState]
        if syntax_state is not None and syntax_query is not None:
            response = cast(
                dp.Response[Any, ReadSkill | SearchRocq | InspectProofState],
                (
                    yield from dp.branch(
                        syntax_query.using(dp.ambient_pp),
                        meta=_no_branch_metadata,
                    )
                ),
            )
        elif continuation_query is not None:
            response = yield from dp.branch(
                continuation_query.using(dp.ambient_pp)
            )
        else:
            response = yield from dp.branch(query.using(dp.ambient_pp))
        prefix.append(dp.OracleMessage("oracle", response.answer))
        call_limits = replace(
            limits, seconds=min(limits.seconds, verifier_seconds - spent)
        )
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                if isinstance(call, rs.CheckRocqSnippet):
                    key = (call.context_id, call.snippet)
                    if spent >= verifier_seconds:
                        yield from dp.fail(label="verifier_budget_exhausted")
                    if not snippet_tools or snippet_probes >= 4:
                        result = "Snippet probe allowance exhausted; submit a proof."
                    elif call.context_id not in snippet_contexts:
                        result = "Unknown context_id; use a supplied context."
                    elif key in snippet_receipts:
                        result = snippet_receipts[key].render(
                            limits.view_bytes
                        )
                        events.record(
                            "snippet",
                            "reused",
                            receipt=snippet_receipts[key].identifier,
                        )
                    else:
                        receipt = yield from dp.compute(rs.check_snippet)(
                            snippet_contexts[call.context_id],
                            call.snippet,
                            dict(
                                seconds=min(
                                    limits.seconds, verifier_seconds - spent
                                ),
                                rpc_calls=limits.rpc_calls,
                                view_bytes=limits.view_bytes,
                            ),
                        )
                        spent += receipt.elapsed
                        snippet_receipts[key] = receipt
                        if receipt.status == "completed":
                            return "\n".join(
                                receipt.checked.feedback.proof_so_far
                            )
                        if receipt.executable:
                            successor = receipt.successor()
                            snippet_contexts[successor.identifier] = successor
                        result = receipt.render(limits.view_bytes)
                    if snippet_tools and snippet_probes < 4:
                        # Repetitions and invalid handles still consume the
                        # interaction allowance, but no additional Rocq work.
                        snippet_probes += 1
                elif isinstance(call, ReadSkill):
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
                    inspect_function = ag.inspect_proof_state
                    if feedback_version == 2:
                        from ace.ace_goal_visibility import (
                            inspect_proof_state_v2,
                        )

                        inspect_function = inspect_proof_state_v2
                    inspected = yield from dp.compute(inspect_function)(
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
        if syntax_state is not None:
            syntax_seen.add((*syntax_state.prefix, syntax_state.failed_action))
            if not isinstance(proposed, aa.RepairDecision):
                yield from dp.fail(label="syntax_parse_failure")
                return ""
            if proposed.decision == "abstain":
                prefix.append(
                    dp.FeedbackMessage(
                        "feedback",
                        "syntax_abstained",
                        "Continue with an ordinary proof decision.",
                    )
                )
                continue
            if not aa.supported_decision(syntax_state, proposed):
                prefix.append(
                    dp.FeedbackMessage(
                        "feedback",
                        "syntax_rejected",
                        "Correction is outside the registered syntax-only grammar.",
                    )
                )
                continue
            syntax_correction = proposed.correction
            proposed = "\n".join((*syntax_state.prefix, proposed.correction))
        if isinstance(proposed, dp.WrappedParseError):
            prefix.append(
                dp.FeedbackMessage("feedback", "parse", str(proposed.error))
            )
            continue
        if continuation_query is not None:
            from prove_continuation import ProofContinuation, assemble

            assert isinstance(proposed, ProofContinuation)
            try:
                proposed = "\n".join(
                    assemble(
                        proposed, last.feedback.proof_so_far if last else []
                    )
                )
            except ValueError as exc:
                prefix.append(
                    dp.FeedbackMessage("feedback", "parse", str(exc))
                )
                continue
        assert isinstance(proposed, str)
        if syntax_state is not None:
            checked = yield from dp.compute(aa.checked_application)(
                syntax_state,
                syntax_correction,
                call_limits,
            )
        else:
            check_function = ag.checked_proof
            if feedback_version == 2:
                from ace.ace_goal_visibility import checked_proof_v2

                check_function = checked_proof_v2
            checked = yield from dp.compute(check_function)(
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
        if (
            isinstance(query, ProposeProofScriptGrounded)
            and query.control
            and query.control.matched_advice
            and type(query) is not ProposeProofScriptGrounded
        ):
            own = env.examples.examples_for("WorkedProofTransition")
            matches = [
                SelectedExample(example=e, index=i, similarity=None)
                for i, e in enumerate(own)
                if isinstance(e.query, WorkedProofTransition)
                and query.lesson.startswith(f"[{e.query.claim_id}]")
            ][:1]
            events.record(
                "example",
                "selected" if matches else "abstained",
                query=query.query_name(),
                count=len(matches),
            )
            return matches
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
    polished: bool = False,
    output_limit: int = 32768,
    dollar_limit: float = 0.10,
    verifier_seconds: float = 300,
    turn_budget: int = 64,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        model_name,
        for_tool_calls=True,
        api=api,
        reasoning_effort=reasoning_effort,
        convert_user_feedback_to_tool=convert_user_feedback_to_tool,
    )
    from runtime.campaign_budget import CampaignResponsesModel
    from runtime.grounded_control import (
        controlled_prompt,
        observe_budget,
        limited_prompt,
    )

    if isinstance(model, CampaignResponsesModel):
        model.output_limit = output_limit
    normal = dp.few_shot(
        model,
        temperature=temperature,
        max_requests=1,
        select_examples=grounded_examples(),
        tag_user_feedback_messages=True,
    )
    if not polished:
        return grounded_search() & normal
    if not isinstance(model, CampaignResponsesModel):
        raise ValueError("polished paid policy requires campaign accounting")
    reduced = limited_prompt(model, grounded_examples(), temperature)
    budgets = {
        "price": dollar_limit,
        "rocq_seconds": verifier_seconds,
        "num_requests": turn_budget,
        "recoveries": 1,
    }
    return (
        dp.with_budget(dp.BudgetLimit(budgets))
        @ observe_budget(budgets)
        @ (
            grounded_search(typed_limits=True)
            & controlled_prompt(normal, reduced)
        )
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
class WorkedProofTransition(dp.Query[str]):
    claim_id: str
    evidence: ag.TrainingTransition
    __parser__ = dp.last_code_block


@dp.strategy
def verify_worked_transition(
    claim: ag.AdviceClaim,
) -> dp.Strategy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, bool]:
    """Navigation check tying a demonstration answer to live Rocq evidence."""
    answer = yield from dp.branch(
        WorkedProofTransition(claim.id, claim.evidence).using(dp.ambient_pp)
    )
    action = tuple(pt.split_into_tactics(answer))
    checked = yield from dp.compute(ag.validate_claim)(
        replace(
            claim,
            action=action,
            evidence=replace(claim.evidence, correction=action),
        ),
        ToolLimits(seconds=10),
    )
    if checked.status != "verified":
        yield from dp.fail(label="demonstration_not_verified")
    return True


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


@dataclass
class ReflectGroundedTransitionJSON(ReflectGroundedTransition):
    __parser__ = dp.structured


@dataclass
class CurateGroundedClaimJSON(CurateGroundedClaim):
    __parser__ = dp.structured


@dataclass
class AuditGroundedClaimJSON(AuditGroundedClaim):
    __parser__ = dp.structured


@dp.strategy
def adapt_grounded_transition(
    evidence: ag.TrainingTransition,
    state: ag.AdaptationState = ag.AdaptationState(),
    limits: ToolLimits = ToolLimits(),
    structured: bool = False,
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
        (
            ReflectGroundedTransitionJSON
            if structured
            else ReflectGroundedTransition
        )(evidence, solution, failed).using(_reflector_policy)
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
        (CurateGroundedClaimJSON if structured else CurateGroundedClaim)(
            reflection, verified
        ).using(_curator_policy)
    )
    if not curation.keep:
        return state.admit(
            (replace(verified, status="rejected", reason=curation.reason),)
        )
    audit = yield from dp.branch(
        (AuditGroundedClaimJSON if structured else AuditGroundedClaim)(
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
