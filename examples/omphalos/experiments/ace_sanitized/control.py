"""Independent, opt-in proof policies over the frozen grounded strategy."""

from copy import copy
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any, cast, override

import delphyne as dp
from delphyne.stdlib.environments import TemplatesManager
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.policies import prompting_policy

from ace.ace_grounded import Checked
from experiments.economy_refinement.window import RefinedWindow
from prove_economy import economy_proof_policy, interaction_groups
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

from .views import bounded_query


@dataclass(frozen=True)
class Controls:
    output_tokens: int = 32768
    drop: bool = False
    concise: bool = False
    views: bool = False
    stop_repeated: bool = False

    def __post_init__(self) -> None:
        if self.output_tokens not in (8192, 32768):
            raise ValueError("Unregistered generation allowance")


TOOL_DESCRIPTIONS = {
    "ReadSkill": (
        "Read one reference named in the skills index. Unknown names return "
        "an error. Use it for tactics, proof patterns or compiler errors."
    ),
    "SearchRocq": (
        "Run a complete Rocq Search, SearchPattern, Check, Print, About or "
        "Locate command, ending in a period, at the current checked state. "
        "Use real types and definitions instead of guessing names. Narrow "
        "the command if the result is empty or truncated."
    ),
    "InspectProofState": (
        "Inspect goals after tactics; optionally run an introspection "
        "command there. Supply complete Rocq sentences. Use start=4,8,... "
        "to page omitted goals."
    ),
}


@dataclass(kw_only=True)
class DocumentationModel(PauseAwareProofModel):
    @override
    def add_model_defaults(self, req: LLMRequest) -> LLMRequest:
        req = super().add_model_defaults(req)
        return replace(
            req,
            tools=tuple(
                replace(
                    tool,
                    description=TOOL_DESCRIPTIONS[tool.name],
                    schema={
                        **tool.schema,
                        **(
                            {"description": TOOL_DESCRIPTIONS[tool.name]}
                            if "description" in tool.schema
                            else {}
                        ),
                    },
                )
                if tool.name in TOOL_DESCRIPTIONS
                else tool
                for tool in req.tools
            ),
        )


class ProofTemplates(TemplatesManager):
    def __init__(self, original: TemplatesManager) -> None:
        super().__init__(
            [Path(__file__).parent / "templates", *original.prompt_folders],
            original.data_manager,
        )
        self.original = original

    @override
    def prompt(
        self,
        *,
        query_name: str,
        prompt_kind: str,
        template_args: dict[str, Any],
        default_template: str | None = None,
    ) -> str:
        query = template_args.get("query")
        if isinstance(query, ProposeProofScriptGrounded) and (
            prompt_kind == "system"
        ):
            return super().prompt(
                query_name="SanitizedConcise",
                prompt_kind="system",
                template_args=dict(template_args),
            )
        return self.original.prompt(
            query_name=query_name,
            prompt_kind=prompt_kind,
            template_args=dict(template_args),
            default_template=default_template,
        )


def repeated_failure(prefix: dp.AnswerPrefix, count: int = 4) -> bool:
    """Four identical checked failures, without new tool evidence."""
    previous: tuple[Any, ...] | None = None
    seen_tools: set[tuple[str, str]] = set()
    run = 0
    for group in interaction_groups(prefix):
        for item in group:
            if isinstance(item, dp.ToolResult):
                evidence = (str(item.call), str(item.result))
                if evidence not in seen_tools:
                    previous, run = None, 0
                    seen_tools.add(evidence)
            elif isinstance(item, dp.FeedbackMessage) and isinstance(
                item.meta, Checked
            ):
                checked = item.meta
                if checked.outcome not in ("rejected", "incomplete"):
                    previous, run = None, 0
                    continue
                fb = checked.feedback
                proposal = next(
                    (
                        str(m.answer.content)
                        for m in group
                        if isinstance(m, dp.OracleMessage)
                    ),
                    "",
                )
                key = (
                    proposal,
                    tuple(fb.proof_so_far),
                    tuple(fb.remaining_goals),
                    fb.failing_tactic,
                    fb.error_message,
                    checked.outcome,
                )
                run = run + 1 if key == previous else 1
                previous = key
    return run >= count


@prompting_policy
def controlled_prompt[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    normal: dp.PromptingPolicy,
    model: CampaignResponsesModel,
    controls: Controls,
    window: RefinedWindow | None,
) -> dp.StreamGen[T]:
    if not isinstance(query.query, ProposeProofScriptGrounded):
        raise TypeError("Proof controls require grounded queries")
    if controls.stop_repeated and repeated_failure(query.query.prefix):
        record("sanitized_stop", "repeated_checked_failure")
        return
    # Decide the cut on raw evidence. Rendering cannot delay the drop.
    transformed, reset = (
        window.apply(query.query, lambda q: q)
        if window is not None
        else (query.query, False)
    )
    if reset:
        if model.reasoning_cache is not None:
            model.reasoning_cache.cache.dict.clear()
        model.reasoning_allowance = 0
    if controls.views:
        transformed = bounded_query(transformed)
    local = copy(env)
    if controls.concise:
        local.templates = ProofTemplates(env.templates)
    attached = replace(query, query=cast(Any, transformed))
    yield from normal(attached, local)


def sanitized_proof_policy(
    snapshot_directory: str,
    pause_file: str,
    controls: Controls = Controls(),
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    if controls == Controls():
        return economy_proof_policy(snapshot_directory, pause_file)
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Campaign accounting is required")
    values = {
        f.name: getattr(original, f.name) for f in fields(original) if f.init
    }
    values.update(
        output_limit=controls.output_tokens, halt_on_billing_issue=True
    )
    model_type = (
        DocumentationModel if controls.concise else PauseAwareProofModel
    )
    model = model_type(**values, pause_file=pause_file, continuation=False)
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=grounded_examples(),
        tag_user_feedback_messages=True,
    )
    prompting = controlled_prompt(
        recorded_prompt(normal, model, snapshot_directory),
        model,
        controls,
        RefinedWindow(max_resets=1) if controls.drop else None,
    )
    limits = dict(price=0.10, num_requests=64, rocq_seconds=300)
    return (
        dp.with_budget(dp.BudgetLimit(limits))
        @ admission_observer(limits)
        @ (grounded_search() & prompting)
    )
