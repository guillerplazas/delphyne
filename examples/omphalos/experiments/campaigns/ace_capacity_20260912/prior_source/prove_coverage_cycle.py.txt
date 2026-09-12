"""Four isolated, opt-in coverage treatments; no partition imports.

Both harnesses use experiments.coverage_cycle_experiment. The incumbent
playbook and deployment budgets are shared; no ACE learning is added.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
import json
import re
from typing import Any

import delphyne as dp
from delphyne.stdlib.queries import (
    ExampleSelector,
    SelectedExample,
    create_prompt,
)
import ace.ace_grounded as ag
import prove_grounded as pg
import prove_coverage as pc
import runtime.pytanque_utils as pt
from runtime.admission_events import record
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits
from runtime.model_registry import OmphalosReasoningEffort


@dataclass
class SubmitExploration(pc.ExploreProof):
    """Last branch request: a structured proof edit, never another tool turn."""

    def query_settings(self, mode: dp.AnswerMode) -> dp.QuerySettings:
        return replace(super().query_settings(mode), tools=None)

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        return []


@dp.strategy
def explore_stall_v2(
    problem_file: str,
    theorem_name: str,
    original: ag.Checked,
    playbook: str,
    limits: ToolLimits,
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, pc.ExplorationResult | None]:
    record("exploration_v2", "triggered")
    for mode in ("suffix", "replace"):
        result = yield from dp.branch(
            dp.nofail(
                pc.explore_attempt(
                    problem_file,
                    theorem_name,
                    original,
                    playbook,
                    limits,
                    mode,
                    final_submission=True,
                ).using(pc.attempt_policy),
                default=None,
            )
        )
        if result is not None:
            record(
                "exploration_v2",
                "usable",
                mode=mode,
                solved=result.checked.feedback.success,
            )
            return result
    record("exploration_v2", "exhausted")
    return None


def exploration_space_v2(
    problem_file: str,
    theorem_name: str,
    original: ag.Checked,
    playbook: str,
    limits: ToolLimits,
) -> dp.Opaque[dp.PromptingPolicy, pc.ExplorationResult | None]:
    return dp.nofail(
        explore_stall_v2(
            problem_file, theorem_name, original, playbook, limits
        ).using(pc.exploration_policy),
        default=None,
    )


def operation_matches(
    operation: str, action: str, error: str, goals: str, definitions: str
) -> bool:
    """Conservative operation predicates, not statement-wide symbol overlap."""
    text = action + "\n" + goals
    if operation == "sum_unfold":
        return "sum_f" in text and bool(
            re.search(r"\b(simpl|cbn|unfold|rewrite|change|sum_f)\b", action)
        )
    if operation == "product_induction":
        return bool(re.search(r"\b(sum_n|prod_n)\b", goals)) and bool(
            re.search(r"\b(induction|prod_n|sum_n)\b", action)
        )
    if operation == "numeral_coercion":
        return bool(re.search(r"\bINR\s*\(?\s*(?:S\s*)?\d+", text))
    if operation == "recurrence_coercion":
        return (
            "INR" in goals
            and "Fixpoint" in definitions
            and bool(re.search(r"\b(induction|rewrite|change)\b", action))
            and bool(re.search(r"\bS\s+\w+", goals))
        )
    if operation == "trig_identity":
        return (
            bool(re.search(r"\b(cos|sin)\b", goals))
            and bool(re.search(r"\^\s*2|Rsqr", goals))
            and bool(re.search(r"\b(rewrite|nra|ring|field)\b", action))
        )
    if operation == "sqrt_side_condition":
        return (
            "sqrt" in goals
            and bool(
                re.search(
                    r"(?:0\s*(?:<=|<)|(?:<=|<)\s*0|sqrt[^\n]*\^\s*2|Rsqr\s*\(?sqrt)",
                    goals,
                )
            )
            and bool(
                re.search(r"\b(rewrite|apply|nra|positivity|assert)\b", action)
            )
        )
    return False


def relevant_examples(bank_file: str) -> ExampleSelector:
    bank = json.loads((ROOT / bank_file).read_text())
    fallback = pg.grounded_examples()

    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        from prove_ace import _ace_examples  # pyright: ignore[reportPrivateUsage]

        if type(query) not in (pg.ChooseProofBridge, pg.ChooseProofStructure):
            return [
                SelectedExample(example=e, index=i, similarity=None)
                for i, e in enumerate(fallback(env, query))
            ]
        assert isinstance(query, pg.ProposeProofScriptGrounded)
        latest = next(
            (
                m.meta
                for m in reversed(query.prefix)
                if isinstance(m, dp.FeedbackMessage)
                and isinstance(m.meta, ag.Checked)
            ),
            None,
        )
        candidates: list[tuple[int, int, str, int, Any]] = []
        if latest:
            fb = latest.feedback
            for row in bank["examples"]:
                if row["query"] != query.query_name() or bank["families"].get(
                    row["theorem"], row["theorem"]
                ) == bank["families"].get(
                    query.spec.theorem_name, query.spec.theorem_name
                ):
                    continue
                if not operation_matches(
                    row["operation"],
                    fb.failing_tactic or "",
                    fb.error_message or "",
                    "\n".join(fb.remaining_goals),
                    query.spec.definitions,
                ):
                    continue
                for i, e in enumerate(
                    env.examples.examples_for(query.query_name())
                ):
                    if (
                        isinstance(e.query, pg.ProposeProofScriptGrounded)
                        and e.query.spec.theorem_name == row["theorem"]
                    ):
                        candidates.append(
                            (
                                -row["specificity"],
                                len(str(e.answer)),
                                row["id"],
                                i,
                                e,
                            )
                        )
        if candidates:
            _, _, ident, i, example = min(candidates, key=lambda x: x[:3])
            record("relevant_example", "selected", example=ident)
            return [SelectedExample(example=example, index=i, similarity=None)]
        record("relevant_example", "fallback")
        return [
            SelectedExample(example=e, index=i, similarity=None)
            for i, e in enumerate(_ace_examples()(env, query))
        ]

    return ExampleSelector(select)


@lru_cache(maxsize=1)
def rendering_env() -> dp.PolicyEnv:
    return dp.workspace_execution_context(__file__).policy_env()


def prompt_chars(query: pg.ProposeProofScriptGrounded) -> int:
    env = rendering_env()
    examples = pg.grounded_examples()(env, query)
    chat = create_prompt(query, examples, {}, None, env.templates, True)
    return len(
        json.dumps([asdict(m) for m in chat], ensure_ascii=False, default=str)
    )


def compact_query(
    query: pg.ProposeProofScriptGrounded, threshold: int = 24000
) -> pg.ProposeProofScriptGrounded:
    before = prompt_chars(query)
    if before <= threshold:
        return query
    groups: list[list[dp.AnswerPrefixElement]] = []
    for item in query.prefix:
        if isinstance(item, dp.OracleMessage) or not groups:
            groups.append([])
        groups[-1].append(item)
    mandatory = set(range(max(0, len(groups) - 2), len(groups)))
    last_checked = next(
        (
            i
            for i in reversed(range(len(groups)))
            if any(
                isinstance(m, dp.FeedbackMessage)
                and isinstance(m.meta, ag.Checked)
                for m in groups[i]
            )
        ),
        None,
    )
    if last_checked is not None:
        mandatory.add(last_checked)
    removed: set[int] = set()
    result = query
    after = before
    for i in range(len(groups)):
        if i in mandatory:
            continue
        removed.add(i)
        result = replace(
            query,
            prefix=tuple(
                m
                for j, group in enumerate(groups)
                if j not in removed
                for m in group
            ),
        )
        after = prompt_chars(result)
        if after <= threshold:
            break
    record(
        "history",
        "compacted" if removed else "mandatory_overflow",
        before=before,
        after=after,
        removed_rounds=len(removed),
        overflow=after > threshold,
    )
    return result


def cycle_policy(
    model_name: str = "gpt-5.6-luna",
    reasoning_effort: OmphalosReasoningEffort = "medium",
    bank_file: str = "",
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    return pc.coverage_policy(
        model_name,
        reasoning_effort,
        example_selector=relevant_examples(bank_file) if bank_file else None,
    )


@dp.strategy
def demonstrate_submission(
    problem_file: str,
    theorem_name: str,
    original: ag.Checked,
    playbook: str,
    limits: ToolLimits,
) -> dp.Strategy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, bool]:
    response = yield from dp.branch(
        SubmitExploration(
            pt.parse_problem(problem_file, True),
            {},
            mode="suffix",
            verified_prefix="\n".join(original.feedback.proof_so_far),
            decision=original.view,
            playbook=playbook,
            turn_budget=1,
        ).using(dp.ambient_pp)
    )
    if isinstance(response.parsed, dp.ToolRequests):
        yield from dp.fail(label="final_submission_requested_tools")
        return False
    from prove_continuation import assemble

    checked = yield from dp.compute(ag.checked_proof)(
        problem_file,
        theorem_name,
        assemble(response.parsed.final, original.feedback.proof_so_far),
        limits,
        assisted=False,
    )
    if not pc.usable(original, checked):
        yield from dp.fail(label="submission_not_usable")
    return True
