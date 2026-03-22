"""
Guided interactive strategy: generates multiple proof candidates per LLM call
and uses enhanced prompts with explicit proof patterns to help smaller models
decompose problems.
"""

from dataclasses import dataclass
from typing import Never

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy

import checker as ch


@dataclass
class ProveEqualityGuided(dp.Query[dp.Response[ch.Proof, Never]]):
    """
    Query for proving trigonometric equalities with guided prompts.
    Returns a Response to enable feedback loops.
    """
    equality: ch.Eq
    prefix: dp.AnswerPrefix

    __parser__ = dp.last_code_block.yaml_as(ch.Proof).response

    def globals(self) -> dict[str, object]:
        """Provide the trig rules to the prompt template."""
        return {"rules": ch.TRIG_RULES}


@strategy
def check_equality(
    equality: ch.Eq, proof: ch.Proof
) -> Strategy[Compute, object, ch.Proof | dp.Error]:
    """
    Compute strategy to check a proposed proof.
    Returns the proof if correct, or feedback as Error if incorrect.
    """
    feedback = yield from dp.compute(ch.check)(equality, proof, ch.TRIG_RULES)

    if feedback is None:
        return proof

    return dp.Error(label="feedback", meta=str(feedback))


@strategy
def prove_equality_guided(
    equality: ch.Eq
) -> Strategy[Branch, dp.PromptingPolicy, ch.Proof]:
    """
    Guided interactive strategy to prove a trigonometric equality.
    Generates multiple candidates per LLM call and uses enhanced prompts
    with explicit proof patterns.
    """
    result_proof = yield from dp.interact(
        step=lambda prefix, _:
            ProveEqualityGuided(equality, prefix).using(dp.ambient_pp),
        process=lambda proof, _:
            check_equality(equality, proof).using(dp.just_compute)
    )

    return result_proof


def prove_equality_guided_policy(
    model_name: str = "gpt-5-mini-2025-08-07",
    temperature: float | None = None,
    num_completions: int = 8,
    max_feedback_cycles: int = 3,
    loop: bool = True,
    reasoning_effort: str | None = None,
):
    """
    Policy for the guided proof strategy.

    Args:
        model_name: Name of the model to use
        temperature: Optional sampling temperature; use None for reasoning-model defaults
        num_completions: Number of proof candidates per LLM call
        max_feedback_cycles: Maximum number of feedback rounds
        loop: Whether to loop the search
        reasoning_effort: Optional reasoning effort level (e.g. "low", "medium", "high")
    """
    options: dict[str, object] = {}
    if reasoning_effort is not None:
        options["reasoning_effort"] = reasoning_effort
    model = dp.standard_model(model_name, options or None)

    # `interact` branches twice per feedback cycle
    sp = dfs(max_depth=2*(max_feedback_cycles+1))
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(
        model,
        temperature=temperature,
        num_completions=num_completions,
        max_requests=1,
    )
    return sp & pp
