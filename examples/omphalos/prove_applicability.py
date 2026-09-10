"""Opt-in syntax decisions and executable demonstrations (both harnesses)."""

from dataclasses import dataclass, replace
from collections.abc import Sequence
from typing import Any

import delphyne as dp
from delphyne.stdlib.queries import ExampleSelector, SelectedExample
from delphyne.stdlib.policies import prompting_policy

import ace.ace_applicability as aa
import ace.ace_grounded as ag
import prove_grounded as pg
import runtime.pytanque_utils as pt
import runtime.skills as sk
from prove_agentic import ReadSkill, SearchRocq
from runtime.admission_events import record
from runtime.model_registry import make_model, OmphalosReasoningEffort
from runtime.tool_budget import ToolLimits, clip_utf8


@dataclass
class DecideSyntaxRepair(
    dp.Query[
        dp.Response[
            aa.RepairDecision, ReadSkill | SearchRocq | pg.InspectProofState
        ]
    ]
):
    state: aa.RepairState
    available_skills: dict[str, str]
    mode: aa.Mode = "Q"
    example_ids: tuple[str, ...] = ()
    prefix: dp.AnswerPrefix = ()
    playbook: str = ""
    demonstration: bool = False

    __parser__ = dp.structured.response


@dataclass(frozen=True)
class RepairResult:
    decision: aa.RepairDecision
    checked: ag.Checked | None
    executed: bool
    requests: int
    elapsed: float
    status: str


@dp.strategy
def repair_episode(
    state: aa.RepairState,
    mode: aa.Mode,
    bank: tuple[aa.RepairExample, ...] = (),
    playbook: str = "",
    request_limit: int = 4,
    limits: ToolLimits = ToolLimits(),
) -> dp.Strategy[
    dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, RepairResult
]:
    """Fresh local episode: one proposal, no logical or serialization retry."""
    ids = aa.select_ids(state, bank, mode)
    abstain = aa.RepairDecision(
        "abstain",
        aa.syntax_form(state.failed_action)[0],
        "",
        "No supported correction",
    )
    # Reconstruct a minimal valid proposal/feedback pair, not a claimed replay
    # of historical dialogue, reasoning cache, or monetary admission state.
    initial = ag.Checked(
        pt.Feedback(
            False,
            len(state.prefix),
            state.failed_action,
            state.error,
            remaining_goals=list(state.goals),
            proof_so_far=list(state.prefix),
        ),
        state.outcome,
        0,
        0,
        "",
    )
    initial = replace(
        initial,
        view=ag.feedback_view(
            initial.feedback, initial.outcome, limits.view_bytes
        ),
    )
    prefix: list[dp.AnswerPrefixElement] = [
        dp.OracleMessage(
            "oracle",
            dp.Answer(
                None,
                "```rocq\n"
                + "\n".join((*state.prefix, state.failed_action))
                + "\n```",
            ),
        ),
        dp.FeedbackMessage("feedback", state.outcome, meta=initial),
    ]
    spent = 0.0
    for turn in range(request_limit):
        query: dp.AbstractQuery[Any]
        if mode == "R":
            query_type = {
                "reference": pg.ResolveProofReference,
                "bridge": pg.ChooseProofBridge,
                "structure": pg.ChooseProofStructure,
            }[ag.decision_kind(initial.feedback)]
            query = query_type(
                spec=pt.parse_problem(
                    state.problem_file, show_definitions=True
                ),
                available_skills=sk.list_skills(),
                prefix=tuple(prefix),
                playbook=playbook,
                turn_budget=request_limit,
                verified_prefix="\n".join(state.prefix),
            )
        else:
            query = DecideSyntaxRepair(
                state, sk.list_skills(), mode, ids, tuple(prefix), playbook
            )
        response = yield from dp.branch(query.using(dp.ambient_pp))
        prefix.append(dp.OracleMessage("oracle", response.answer))
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                if isinstance(call, ReadSkill):
                    text = clip_utf8(
                        sk.read_skill(call.skill_name), limits.view_bytes
                    )
                else:
                    if spent >= 300:
                        return RepairResult(
                            abstain,
                            None,
                            False,
                            turn + 1,
                            spent,
                            "verifier_budget_exhausted",
                        )
                    tactics = (
                        "\n".join(state.prefix)
                        if isinstance(call, SearchRocq)
                        else call.tactics
                    )
                    start = 0 if isinstance(call, SearchRocq) else call.start
                    inspected = yield from dp.compute(ag.inspect_proof_state)(
                        state.problem_file,
                        state.theorem_name,
                        tactics,
                        call.command,
                        start,
                        replace(
                            limits, seconds=min(limits.seconds, 300 - spent)
                        ),
                    )
                    spent += inspected.elapsed
                    text = inspected.text
                prefix.append(
                    dp.ToolResult("tool", response.answer.tool_calls[i], text)
                )
            continue
        value = response.parsed.final
        if isinstance(value, dp.WrappedParseError):
            return RepairResult(
                abstain, None, False, turn + 1, spent, "parse_failure"
            )
        if mode == "R":
            assert isinstance(value, str)
            tactics = pt.split_into_tactics(value)
            if tactics[: len(state.prefix)] != list(state.prefix):
                return RepairResult(
                    abstain, None, False, turn + 1, spent, "changed_prefix"
                )
            suffix = tactics[len(state.prefix) :]
            # R is unconstrained at generation. The same syntax-only rubric
            # scores its first proposal; extra search is not a local repair.
            answer = aa.RepairDecision(
                "repair",
                aa.syntax_form(state.failed_action)[0],
                "\n".join(suffix),
                "ordinary continuation",
            )
        else:
            assert isinstance(value, aa.RepairDecision)
            answer = value
        if answer.decision == "abstain":
            return RepairResult(
                answer, None, False, turn + 1, spent, "abstained"
            )
        call_limits = replace(limits, seconds=min(limits.seconds, 300 - spent))
        if mode == "R":
            checked = yield from dp.compute(ag.checked_proof)(
                state.problem_file,
                state.theorem_name,
                [*state.prefix, *pt.split_into_tactics(answer.correction)],
                call_limits,
                assisted=False,
            )
            _, canonical = aa.syntax_form(state.failed_action)
            expected = [*state.prefix, *pt.split_into_tactics(canonical)]
            admitted = checked.feedback.success or (
                aa.eligible(state)
                and checked.outcome in ("accepted", "incomplete", "rejected")
                and aa.syntax_tokens(
                    "\n".join(checked.feedback.proof_so_far[: len(expected)])
                )
                == aa.syntax_tokens("\n".join(expected))
            )
        else:
            checked = yield from dp.compute(aa.check_repair)(
                state, answer, call_limits
            )
            admitted = aa.executed(state, answer, checked)
        return RepairResult(
            answer,
            checked,
            admitted,
            turn + 1,
            spent + checked.elapsed,
            "proposed",
        )
    return RepairResult(
        abstain, None, False, request_limit, spent, "request_limit"
    )


def syntax_examples() -> ExampleSelector:
    legacy = pg.grounded_examples()

    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        if not isinstance(query, DecideSyntaxRepair):
            return [
                SelectedExample(example=e, index=i, similarity=None)
                for i, e in enumerate(legacy(env, query))
            ]
        own = env.examples.examples_for("DecideSyntaxRepair")
        return [
            SelectedExample(example=e, index=i, similarity=None)
            for i, e in enumerate(own)
            if isinstance(e.query, DecideSyntaxRepair)
            and e.query.example_ids
            and e.query.example_ids[0] in query.example_ids
        ]

    return ExampleSelector(select)


@prompting_policy
def observe_syntax[T](
    query: dp.AttachedQuery[T], env: dp.PolicyEnv, normal: dp.PromptingPolicy
) -> dp.StreamGen[T]:
    for message in normal(query, env):
        if isinstance(message, dp.Solution) and isinstance(
            query.query, DecideSyntaxRepair
        ):
            record(
                "syntax_query",
                "answered",
                mode=query.query.mode,
                ids=query.query.example_ids,
                pattern=aa.syntax_form(query.query.state.failed_action)[0],
            )
        yield message


def applicability_policy(
    model_name: str = "gpt-5.6-luna",
    reasoning_effort: OmphalosReasoningEffort = "medium",
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        model_name,
        api="responses",
        reasoning_effort=reasoning_effort,
        for_tool_calls=True,
        convert_user_feedback_to_tool=True,
    )
    return pg.grounded_search() & observe_syntax(
        dp.few_shot(
            model,
            max_requests=1,
            select_examples=syntax_examples(),
            tag_user_feedback_messages=True,
        )
    )


@dp.strategy
def verify_syntax_demo(
    state: aa.RepairState, example_id: str, expected: bool
) -> dp.Strategy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, bool]:
    response = yield from dp.branch(
        DecideSyntaxRepair(
            state, {}, "Q", (example_id,), demonstration=True
        ).using(dp.ambient_pp)
    )
    if isinstance(response.parsed, dp.ToolRequests):
        yield from dp.fail(label="demo_requires_decision")
        return False
    answer = response.parsed.final
    if expected:
        checked = yield from dp.compute(aa.check_repair)(
            state, answer, ToolLimits(seconds=10)
        )
        if not aa.executed(state, answer, checked):
            yield from dp.fail(label="demo_not_verified")
    elif answer.decision != "abstain":
        yield from dp.fail(label="demo_requires_abstention")
    return True
