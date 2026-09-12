"""Version-2 policy for the existing opt-in continuation strategies.

No paid v2 run is included in ace_mechanisms_20260910. Import this policy
from either harness; use the same strategy arguments as S/C/R and the same
campaign ledger. The frozen v1 policy and measured results are unchanged.
"""

import delphyne as dp
import prove_grounded as pg
from prove_continuation import examples
from runtime.campaign_budget import CampaignResponsesModel
from runtime.continuation_output import ContinuationResponsesModel
from runtime.grounded_control import (
    controlled_prompt,
    limited_prompt,
    observe_budget,
)
from runtime.model_registry import OmphalosReasoningEffort, make_model


def continuation_policy_v2(
    model_name: str = "gpt-5.6-luna",
    reasoning_effort: OmphalosReasoningEffort = "medium",
    recovery: bool = False,
    turn_budget: int = 64,
    typed_limits: bool = False,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        model_name,
        api="responses",
        reasoning_effort=reasoning_effort,
        for_tool_calls=True,
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(model, CampaignResponsesModel):
        raise ValueError("Version-2 continuation requires campaign accounting")
    model = ContinuationResponsesModel.from_model(model)
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=examples(),
        tag_user_feedback_messages=True,
    )
    budgets = {
        "price": 0.10,
        "rocq_seconds": 300.0,
        "num_requests": float(turn_budget),
    }
    if not recovery:
        return observe_budget(budgets) @ (
            pg.grounded_search(typed_limits=typed_limits) & normal
        )
    budgets["recoveries"] = 1.0
    return (
        dp.with_budget(dp.BudgetLimit(budgets))
        @ observe_budget(budgets)
        @ (
            pg.grounded_search(typed_limits=typed_limits)
            & controlled_prompt(normal, limited_prompt(model, examples()))
        )
    )
