"""Policy adapter for the registered ACE capacity follow-up.

The underlying strategy, examples, model options, and Delphyne budget
semantics are unchanged. Request transport state and terminal admissions
are recorded outside rendered prompts. Both agent harnesses use this module.
"""

import delphyne as dp
from copy import copy
from pathlib import Path
from delphyne.stdlib.models import LLMCache, load_request_cache
from delphyne.stdlib.policies import search_policy
from prove_grounded import (
    grounded_examples,
    grounded_search,
    prove_theorem_grounded,
)
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import make_model
from runtime.replay_admission import (
    PrefixCache,
    PrefixGuard,
    admission_observer,
    recorded_model,
    recorded_prompt,
)


@search_policy
def capacity_search[P, T](
    tree: dp.Tree[dp.Branch | dp.Compute | dp.Fail, P, T],
    env: dp.PolicyEnv,
    policy: P,
    prefix_cache: str = "",
) -> dp.StreamGen[T]:
    if not prefix_cache:
        yield from grounded_search()(tree, env, policy)
        return
    if env.cache is None:
        raise ValueError("Continuation needs an output request cache")
    with load_request_cache(Path(prefix_cache), mode="replay") as source:
        required = dict(source.cache.dict)
    local = copy(env)
    env.cache.cache.dict.update(required)
    guard = PrefixGuard(set(required))
    local.cache = LLMCache(
        PrefixCache(env.cache.cache.dict, "read_write", guard)
    )
    local.cache.num_seen = env.cache.num_seen
    yield from grounded_search()(tree, local, policy)
    if guard.remaining:
        raise ValueError(
            "Continuation stopped before replaying its full prefix"
        )


@dp.ensure_compatible(prove_theorem_grounded)
def prove_capacity_policy(
    model_name: str,
    snapshot_directory: str,
    dollar_limit: float,
    verifier_seconds: float = 300,
    turn_budget: int = 64,
    prefix_cache: str = "",
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        model_name,
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(model, CampaignResponsesModel):
        raise ValueError("Capacity experiments require campaign accounting")
    model = recorded_model(model)
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=grounded_examples(),
        tag_user_feedback_messages=True,
    )
    limits = dict(
        price=dollar_limit,
        rocq_seconds=verifier_seconds,
        num_requests=turn_budget,
    )
    return admission_observer(limits) @ (
        capacity_search(prefix_cache)
        & recorded_prompt(normal, model, snapshot_directory)
    )


def capacity_role_policy(
    model_name: str,
    snapshot_directory: str,
    dollar_limit: float,
    temperature: float | None = None,
    api: str = "responses",
    reasoning_effort: str = "medium",
    max_requests: int = 3,
) -> dp.Policy[dp.Branch, dp.PromptingPolicy]:
    if api != "responses" or reasoning_effort != "medium" or max_requests != 3:
        raise ValueError("Unregistered creation policy")
    original = make_model(
        model_name, api="responses", reasoning_effort="medium"
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Creation probes require campaign accounting")
    model = recorded_model(original)
    normal = dp.few_shot(
        model,
        temperature=temperature,
        max_requests=3,
        tag_user_feedback_messages=True,
    )
    return admission_observer(dict(price=dollar_limit, num_requests=3)) @ (
        dp.dfs() & recorded_prompt(normal, model, snapshot_directory)
    )
