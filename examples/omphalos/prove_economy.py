"""Opt-in proof economics controls; shared by both agent harnesses.

The reference policy is the v2 proof policy, with explicit budget parameters.
One session reset preserves complete interaction groups and the last checked
proposal. It never changes the proof state or grants new search resources.
"""

from dataclasses import dataclass, fields, replace
from typing import Any, cast

import delphyne as dp
from delphyne.stdlib.policies import prompting_policy

from ace.ace_grounded import Checked
from prove_grounded import (
    ProposeProofScriptGrounded,
    grounded_examples,
    grounded_search,
)
from runtime.admission_events import record
from runtime.campaign_budget import CampaignResponsesModel
from runtime.campaign_pause import PauseAwareProofModel
from runtime.model_registry import make_model
from runtime.replay_admission import admission_observer, recorded_prompt


def interaction_groups(
    prefix: dp.AnswerPrefix,
) -> list[list[dp.AnswerPrefixElement]]:
    groups: list[list[dp.AnswerPrefixElement]] = []
    for item in prefix:
        if isinstance(item, dp.OracleMessage) or not groups:
            groups.append([])
        groups[-1].append(item)
    return groups


def visible_chars(prefix: dp.AnswerPrefix) -> int:
    total = 0
    for item in prefix:
        if isinstance(item, dp.OracleMessage):
            total += len(str(item.answer.content))
            total += sum(len(str(c)) for c in item.answer.tool_calls)
        elif isinstance(item, dp.ToolResult):
            total += len(str(item.result))
        else:
            total += (
                len(item.meta.view)
                if isinstance(item.meta, Checked)
                else len(str(item))
            )
    return total


@dataclass
class SessionWindow:
    """Drop old context once; later calls cannot resurrect discarded groups."""

    min_groups: int = 8
    threshold_chars: int = 24000
    cut: int | None = None
    retained: tuple[int, ...] = ()

    def apply(
        self, query: ProposeProofScriptGrounded
    ) -> tuple[ProposeProofScriptGrounded, bool]:
        groups = interaction_groups(query.prefix)
        reset = False
        before = visible_chars(query.prefix)
        if (
            self.cut is None
            and len(groups) >= self.min_groups
            and before >= self.threshold_chars
        ):
            required = set(range(max(0, len(groups) - 2), len(groups)))
            checked = next(
                (
                    i
                    for i in reversed(range(len(groups)))
                    if any(
                        isinstance(m, dp.FeedbackMessage)
                        and isinstance(m.meta, Checked)
                        for m in groups[i]
                    )
                ),
                None,
            )
            if checked is not None:
                required.add(checked)
            self.cut = len(groups)
            self.retained = tuple(sorted(required))
            reset = True
        if self.cut is None:
            return query, False
        if len(groups) < self.cut:
            raise ValueError("Session window requires append-only history")
        prefix = tuple(
            m
            for i, group in enumerate(groups)
            if i >= self.cut or i in self.retained
            for m in group
        )
        result = replace(query, prefix=prefix)
        if reset:
            record(
                "economy_session",
                "reset",
                groups=len(groups),
                kept_groups=len(self.retained),
                before_chars=before,
                after_chars=visible_chars(prefix),
                verified_prefix_chars=len(query.verified_prefix),
            )
        return result, reset


@prompting_policy
def session_prompt[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    normal: dp.PromptingPolicy,
    model: CampaignResponsesModel,
    window: SessionWindow,
) -> dp.StreamGen[T]:
    if not isinstance(query.query, ProposeProofScriptGrounded):
        raise TypeError("Session control only supports grounded proof queries")
    transformed, reset = window.apply(query.query)
    if reset:
        # A new session carries explicit proof evidence, not opaque reasoning
        # from the discarded conversation. Replay executes the same reset.
        if model.reasoning_cache is not None:
            model.reasoning_cache.cache.dict.clear()
        model.reasoning_allowance = 0
    attached = replace(query, query=cast(Any, transformed))
    yield from normal(attached, env)


def economy_proof_policy(
    snapshot_directory: str,
    pause_file: str,
    dollar_cap: float = 0.10,
    split_session: bool = False,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    if dollar_cap not in (0.10, 0.20):
        raise ValueError("Unregistered dollar cap")
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Proof economics requires campaign accounting")
    values = {
        f.name: getattr(original, f.name) for f in fields(original) if f.init
    }
    values.update(output_limit=32768, halt_on_billing_issue=True)
    model = PauseAwareProofModel(
        **values, pause_file=pause_file, continuation=False
    )
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=grounded_examples(),
        tag_user_feedback_messages=True,
    )
    prompting = recorded_prompt(normal, model, snapshot_directory)
    if split_session:
        prompting = session_prompt(prompting, model, SessionWindow())
    limits = dict(price=dollar_cap, num_requests=64, rocq_seconds=300)
    return (
        dp.with_budget(dp.BudgetLimit(limits))
        @ admission_observer(limits)
        @ (grounded_search() & prompting)
    )
