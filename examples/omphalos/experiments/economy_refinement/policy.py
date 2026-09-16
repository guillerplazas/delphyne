"""Independent presentation and session controls over the frozen policy.

Neither wrapper changes parsing, tools, verification, playbook contents,
demonstrations or allowances. Both off delegates to the exact reference.
"""

from copy import copy
from dataclasses import fields, replace
from pathlib import Path
from typing import Any, cast, override

import delphyne as dp
from delphyne.stdlib.environments import TemplatesManager
from delphyne.stdlib.policies import prompting_policy

from prove_economy import economy_proof_policy, visible_chars
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

from .rendering import compact_query
from .window import RefinedWindow


class EconomyTemplates(TemplatesManager):
    def __init__(self, original: TemplatesManager, compact: bool) -> None:
        super().__init__(
            [Path(__file__).parent / "templates", *original.prompt_folders],
            original.data_manager,
        )
        self.original = original
        self.compact = compact

    @override
    def prompt(
        self,
        *,
        query_name: str,
        prompt_kind: str,
        template_args: dict[str, Any],
        default_template: str | None = None,
    ) -> str:
        grounded = isinstance(
            template_args.get("query"), ProposeProofScriptGrounded
        )
        if self.compact and grounded and prompt_kind == "system":
            return super().prompt(
                query_name="EconomyCompact",
                prompt_kind="system",
                template_args=dict(template_args),
            )
        return self.original.prompt(
            query_name=query_name,
            prompt_kind=prompt_kind,
            template_args=dict(template_args),
            default_template=default_template,
        )


def identity(query: ProposeProofScriptGrounded) -> ProposeProofScriptGrounded:
    return query


@prompting_policy
def refinement_prompt[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    normal: dp.PromptingPolicy,
    model: CampaignResponsesModel,
    window: RefinedWindow | None,
    compact: bool,
) -> dp.StreamGen[T]:
    if not isinstance(query.query, ProposeProofScriptGrounded):
        raise TypeError("Economy controls require grounded proof queries")
    render = compact_query if compact else identity
    transformed, reset = (
        window.apply(query.query, render)
        if window is not None
        else (render(query.query), False)
    )
    if reset:
        if model.reasoning_cache is not None:
            model.reasoning_cache.cache.dict.clear()
        model.reasoning_allowance = 0
    if compact:
        record(
            "compact_presentation",
            "rendered",
            raw_chars=visible_chars(query.query.prefix),
            visible_chars=visible_chars(transformed.prefix),
        )
    local = copy(env)
    local.templates = EconomyTemplates(env.templates, compact)
    attached = replace(query, query=cast(Any, transformed))
    yield from normal(attached, local)


def refined_economy_policy(
    snapshot_directory: str,
    pause_file: str,
    reset: bool = False,
    compact: bool = False,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    if not reset and not compact:
        return economy_proof_policy(snapshot_directory, pause_file)
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Refinement requires campaign accounting")
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
    prompting = refinement_prompt(
        recorded_prompt(normal, model, snapshot_directory),
        model,
        RefinedWindow() if reset else None,
        compact,
    )
    limits = dict(price=0.10, num_requests=64, rocq_seconds=300)
    return (
        dp.with_budget(dp.BudgetLimit(limits))
        @ admission_observer(limits)
        @ (grounded_search() & prompting)
    )
