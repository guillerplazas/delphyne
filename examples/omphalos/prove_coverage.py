"""Fixed-book coverage improvements using Delphyne examples and sub-search.

D changes example selection only. E adds one nested, shared-budget search.
Neither mechanism trains ACE or changes the incumbent policy's defaults.
Both agent harnesses use the same queries, demonstrations and Python CLI.
"""

from collections.abc import Sequence
from dataclasses import dataclass, replace
import json
import re
from typing import Any, Literal

import delphyne as dp
from delphyne.stdlib.policies import prompting_policy
from delphyne.stdlib.queries import ExampleSelector, SelectedExample

import ace.ace_grounded as ag
import prove_grounded as pg
from prove_agentic import ReadSkill, SearchRocq
from prove_continuation import ContinueVerifiedProof, assemble
import runtime.pytanque_utils as pt
import runtime.skills as sk
from runtime.admission_events import record
from runtime.campaign_budget import CampaignResponsesModel
from runtime.continuation_output import ContinuationResponsesModel
from runtime.grounded_control import observe_budget
from runtime.model_registry import OmphalosReasoningEffort, make_model
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits


@dataclass
class ExploreProof(ContinueVerifiedProof):
    """A short bounded search; mode fixes the permitted proof edit."""

    mode: Literal["suffix", "replace"] = "suffix"


@dataclass(frozen=True)
class ExplorationResult:
    checked: ag.Checked
    script: str
    elapsed: float


def usable(original: ag.Checked, checked: ag.Checked) -> bool:
    """A checked state change is usable, not necessarily mathematical progress."""
    if checked.feedback.success:
        return True
    return (
        checked.outcome == "incomplete"
        and checked.feedback.failing_tactic in (None, "", "Qed.")
        and bool(checked.feedback.proof_so_far)
        and (
            checked.feedback.proof_so_far != original.feedback.proof_so_far
            or checked.feedback.remaining_goals
            != original.feedback.remaining_goals
        )
    )


@dp.strategy
def explore_attempt(
    problem_file: str,
    theorem_name: str,
    original: ag.Checked,
    playbook: str,
    limits: ToolLimits,
    mode: Literal["suffix", "replace"],
    final_submission: bool = False,
) -> dp.Strategy[
    dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, ExplorationResult
]:
    prefix: list[dp.AnswerPrefixElement] = []
    elapsed = 0.0
    state_prefix = original.feedback.proof_so_far if mode == "suffix" else []
    for turn in range(3):
        query_type = ExploreProof
        if final_submission and turn == 2:
            from prove_coverage_cycle import SubmitExploration

            query_type = SubmitExploration
        response = yield from dp.branch(
            query_type(
                spec=pt.parse_problem(problem_file, show_definitions=True),
                available_skills={}
                if final_submission and turn == 2
                else sk.list_skills(),
                turn_budget=3 - turn if final_submission else 3,
                prefix=tuple(prefix),
                playbook=playbook,
                verified_prefix="\n".join(state_prefix),
                decision=original.view,
                mode=mode,
            ).using(dp.ambient_pp)
        )
        prefix.append(dp.OracleMessage("oracle", response.answer))
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                if isinstance(call, ReadSkill):
                    text = yield from dp.compute(sk.read_skill)(
                        call.skill_name
                    )
                else:
                    tactics = (
                        "\n".join(state_prefix)
                        if isinstance(call, SearchRocq)
                        else call.tactics
                    )
                    command = call.command
                    start = (
                        call.start
                        if isinstance(call, pg.InspectProofState)
                        else 0
                    )
                    inspected = yield from dp.compute(ag.inspect_proof_state)(
                        problem_file,
                        theorem_name,
                        tactics,
                        command,
                        start,
                        limits,
                    )
                    elapsed += inspected.elapsed
                    text = inspected.text
                prefix.append(
                    dp.ToolResult("tool", response.answer.tool_calls[i], text)
                )
            continue
        edit = response.parsed.final
        if edit.mode != mode:
            prefix.append(
                dp.FeedbackMessage("feedback", "mode", f"Return mode={mode}.")
            )
            continue
        try:
            tactics = assemble(edit, state_prefix)
        except ValueError as exc:
            prefix.append(dp.FeedbackMessage("feedback", "parse", str(exc)))
            continue
        checked = yield from dp.compute(ag.checked_proof)(
            problem_file, theorem_name, tactics, limits, assisted=False
        )
        elapsed += checked.elapsed
        if usable(original, checked):
            return ExplorationResult(checked, "\n".join(tactics), elapsed)
        prefix.append(
            dp.FeedbackMessage("feedback", checked.outcome, meta=checked)
        )
    yield from dp.fail(label="exploration_no_usable_state")
    return ExplorationResult(original, "", elapsed)


def attempt_policy(
    pp: dp.PromptingPolicy,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    return (
        dp.with_budget(dp.BudgetLimit({"num_requests": 3}))
        @ pg.grounded_search(typed_limits=True)
    ) & pp


@dp.strategy
def explore_stall(
    problem_file: str,
    theorem_name: str,
    original: ag.Checked,
    playbook: str,
    limits: ToolLimits,
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, ExplorationResult | None]:
    for mode in ("suffix", "replace"):
        result = yield from dp.branch(
            dp.nofail(
                explore_attempt(
                    problem_file,
                    theorem_name,
                    original,
                    playbook,
                    limits,
                    mode,
                ).using(attempt_policy),
                default=None,
            )
        )
        if result is not None:
            return result
    return None


def exploration_policy(
    pp: dp.PromptingPolicy,
) -> dp.Policy[dp.Branch, dp.PromptingPolicy]:
    return (
        dp.with_budget(
            dp.BudgetLimit(
                {"price": 0.025, "num_requests": 6, "rocq_seconds": 120}
            )
        )
        @ dp.dfs()
    ) & pp


def exploration_space(
    problem_file: str,
    theorem_name: str,
    original: ag.Checked,
    playbook: str,
    limits: ToolLimits,
) -> dp.Opaque[dp.PromptingPolicy, ExplorationResult | None]:
    return dp.nofail(
        explore_stall(
            problem_file, theorem_name, original, playbook, limits
        ).using(exploration_policy),
        default=None,
    )


def family(name: str, families: dict[str, str]) -> str:
    return families.get(name, name)


def symbols(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z_][A-Za-z_0-9']*", text))


def coverage_examples(bank_file: str) -> ExampleSelector:
    fallback = pg.grounded_examples()
    bank: dict[str, Any] = json.loads((ROOT / bank_file).read_text())

    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        if type(query) not in (pg.ChooseProofBridge, pg.ChooseProofStructure):
            return [
                SelectedExample(example=e, index=i, similarity=None)
                for i, e in enumerate(fallback(env, query))
            ]
        assert isinstance(query, pg.ProposeProofScriptGrounded)
        text = query.spec.theorem_statement + "\n" + query.spec.definitions
        for msg in query.prefix:
            if isinstance(msg, dp.FeedbackMessage) and isinstance(
                msg.meta, ag.Checked
            ):
                text += "\n" + "\n".join(msg.meta.feedback.remaining_goals)
        present = symbols(text)
        candidates: list[tuple[int, str, str]] = []
        for row in bank["examples"]:
            if row["query"] != query.query_name():
                continue
            if family(row["theorem"], bank["families"]) == family(
                query.spec.theorem_name, bank["families"]
            ):
                continue
            required = set(row["match_symbols"])
            if not required or not required <= present:
                continue
            candidates.append((-len(required), row["id"], row["theorem"]))
        selected = min(candidates) if candidates else None
        if selected:
            for i, e in enumerate(
                env.examples.examples_for(query.query_name())
            ):
                if (
                    isinstance(e.query, pg.ProposeProofScriptGrounded)
                    and e.query.spec.theorem_name == selected[2]
                ):
                    record(
                        "coverage_example",
                        "selected",
                        example=selected[1],
                        query=query.query_name(),
                    )
                    return [
                        SelectedExample(example=e, index=i, similarity=None)
                    ]
        record("coverage_example", "fallback", query=query.query_name())
        # New query buckets must not leak back through the legacy selector.
        # The bank's examples are omitted explicitly on no-match/same-family.
        from prove_ace import _ace_examples  # pyright: ignore[reportPrivateUsage]

        return [
            SelectedExample(example=e, index=i, similarity=None)
            for i, e in enumerate(_ace_examples()(env, query))
        ]

    return ExampleSelector(select)


@prompting_policy
def routed_prompt[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    normal: dp.PromptingPolicy,
    short: dp.PromptingPolicy,
) -> dp.StreamGen[T]:
    if isinstance(query.query, ExploreProof):
        record("exploration", "query", mode=query.query.mode)
        yield from short(query, env)
    else:
        yield from normal(query, env)


def coverage_policy(
    model_name: str = "gpt-5.6-luna",
    reasoning_effort: OmphalosReasoningEffort = "medium",
    bank_file: str = "",
    example_selector: ExampleSelector | None = None,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        model_name,
        api="responses",
        reasoning_effort=reasoning_effort,
        for_tool_calls=True,
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(model, CampaignResponsesModel):
        raise ValueError("Coverage experiment requires campaign accounting")
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=example_selector
        or (
            coverage_examples(bank_file)
            if bank_file
            else pg.grounded_examples()
        ),
        tag_user_feedback_messages=True,
    )
    short_model = ContinuationResponsesModel.from_model(
        replace(model, output_limit=4096)
    )
    short = dp.few_shot(
        short_model,
        max_requests=1,
        select_examples=ExampleSelector(lambda _env, _q: []),
        tag_user_feedback_messages=True,
    )
    return observe_budget(
        {"price": 0.10, "num_requests": 64, "rocq_seconds": 300}
    ) @ (pg.grounded_search() & routed_prompt(normal, short))


@dataclass(frozen=True)
class AuthoredDemo:
    script: str
    explanation: str


@dataclass
class AuthorCoverageDemo(dp.Query[AuthoredDemo]):
    spec: pt.ProblemSpec
    prefix: tuple[str, ...]
    failed_action: str
    error: str
    goals: tuple[str, ...]
    verified_correction: tuple[str, ...]
    __parser__ = dp.structured


@dp.strategy
def author_coverage_demo(
    source: ag.TrainingTransition,
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, AuthoredDemo]:
    return (
        yield from dp.branch(
            AuthorCoverageDemo(
                pt.parse_problem(source.problem_file, show_definitions=True),
                source.prefix,
                source.failed_action,
                source.error,
                source.goals,
                source.correction,
            ).using(dp.ambient_pp)
        )
    )


def author_policy() -> dp.Policy[dp.Branch, dp.PromptingPolicy]:
    model = make_model(
        "gpt-5.6-sol", api="responses", reasoning_effort="medium"
    )
    if not isinstance(model, CampaignResponsesModel):
        raise ValueError("Demo authoring requires its separate ledger")
    model = ContinuationResponsesModel.from_model(
        replace(model, output_limit=8192)
    )
    return dp.dfs() & dp.few_shot(
        model,
        max_requests=1,
        select_examples=ExampleSelector(lambda _e, _q: []),
    )


@dp.strategy
def demonstrate_coverage(
    query_kind: Literal["bridge", "structure"],
    problem_file: str,
    theorem_name: str,
    original: ag.Checked,
) -> dp.Strategy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, bool]:
    cls = (
        pg.ChooseProofBridge
        if query_kind == "bridge"
        else pg.ChooseProofStructure
    )
    response = yield from dp.branch(
        cls(
            pt.parse_problem(problem_file, show_definitions=True),
            {},
            verified_prefix="\n".join(original.feedback.proof_so_far),
            decision="propose a proof",
            lesson=original.view,
        ).using(dp.ambient_pp)
    )
    if isinstance(response.parsed, dp.ToolRequests) or isinstance(
        response.parsed.final, dp.WrappedParseError
    ):
        yield from dp.fail(label="expected_proof")
        return False
    checked = yield from dp.compute(ag.checked_proof)(
        problem_file,
        theorem_name,
        pt.split_into_tactics(response.parsed.final),
        ToolLimits(seconds=30),
        assisted=False,
    )
    if not usable(original, checked):
        yield from dp.fail(label="demonstration_not_executable")
    return True
