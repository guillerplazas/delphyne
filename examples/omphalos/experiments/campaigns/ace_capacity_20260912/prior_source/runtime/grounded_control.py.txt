"""Opt-in bounded ACE controls built on Delphyne spending streams.

The observer never authorizes spending: parent ``with_budget`` transformers
make every decision. Each proof is sequential, so a zero-cost verifier
preflight immediately before a model call cannot race another computation.
"""

from dataclasses import dataclass, replace
from typing import Any, cast

import delphyne as dp
from delphyne.core.streams import Barrier, Spent
from delphyne.stdlib.policies import prompting_policy
from delphyne.stdlib.streams import (
    SpendingDeclined,
    Stream,
    spend_on,
    stream_transformer,
)
from runtime.campaign_budget import CampaignResponsesModel
from delphyne.stdlib.queries import ExampleSelector

from runtime.admission_events import record


@dataclass(frozen=True)
class DecisionControl:
    verification_seconds: float
    recovery: str = ""
    may_downshift: bool = False
    matched_advice: bool = False


@prompting_policy
def limited_prompt[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    model: CampaignResponsesModel,
    examples: ExampleSelector,
    temperature: float | None = None,
) -> dp.StreamGen[T]:
    # A yielded solution can suspend this generator throughout an entire
    # descendant search. Never temporarily mutate the parent's output cap.
    limited = replace(model, output_limit=4096)
    limited.reasoning_cache = model.reasoning_cache
    limited.reasoning_allowance = model.reasoning_allowance
    policy = dp.few_shot(
        limited,
        temperature=temperature,
        max_requests=1,
        select_examples=examples,
        tag_user_feedback_messages=True,
    )
    for message in policy(query, env):
        model.reasoning_allowance = max(
            model.reasoning_allowance, limited.reasoning_allowance
        )
        yield message


def claim_recovery(reason: str) -> dp.StreamContext[bool]:
    result = yield from spend_on(
        lambda: (True, dp.Budget({"recoveries": 1})),
        dp.Budget({"recoveries": 1}),
    )
    if isinstance(result, SpendingDeclined):
        record("recovery", "declined", reason=reason)
        return False
    record("recovery", "admitted", reason=reason)
    return True


@prompting_policy
def controlled_prompt[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    normal: dp.PromptingPolicy,
    reduced: dp.PromptingPolicy,
) -> dp.StreamGen[T]:
    control = cast(
        DecisionControl | None, getattr(query.query, "control", None)
    )
    if control is None:
        yield from normal(query, env)
        return
    # No verifier time is consumed by this preflight. The actual Compute
    # reserves and settles its own time later; there is no double debit.
    preflight = yield from spend_on(
        lambda: (True, dp.Budget.zero()),
        dp.Budget({"rocq_seconds": control.verification_seconds}),
    )
    if isinstance(preflight, SpendingDeclined):
        record("stop", "verifier_preflight")
        return
    if control.recovery and not (yield from claim_recovery(control.recovery)):
        return
    generated = False
    declined = False
    for message in normal(query, env):
        yield message
        if isinstance(message, dp.Solution):
            generated = True
        elif isinstance(message, Barrier):
            declined |= not message.allow and message.budget["price"] > 0
    if not generated and declined and control.may_downshift:
        if (yield from claim_recovery("output_downshift")):
            yield from reduced(query, env)


@stream_transformer
def observe_budget[T](
    stream: Stream[T], env: dp.PolicyEnv, limits: dict[str, float]
) -> dp.StreamGen[T]:
    """Record the final parent decision, including pending reservations."""
    spent = dp.Budget.zero()
    pending: dict[Any, dp.Budget] = {}
    for message in stream:
        yield message
        if isinstance(message, Barrier):
            reserved = sum(pending.values(), start=dp.Budget.zero())
            remaining = {
                key: cap - spent[key] - reserved[key]
                for key, cap in limits.items()
            }
            record(
                "admission",
                "admitted" if message.allow else "declined",
                estimate=dict(message.budget.values),
                remaining=remaining,
                limiting=[
                    key
                    for key, value in remaining.items()
                    if message.budget[key] > value + 1e-12
                ],
            )
            pending[message.id] = (
                message.budget if message.allow else dp.Budget.zero()
            )
        elif isinstance(message, Spent):
            spent += message.budget
            pending.pop(message.barrier_id)
