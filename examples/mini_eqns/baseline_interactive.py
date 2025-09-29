"""
Interactive baseline: conversational agent that produces a proof and is
then provided opportunities to fix errors from the checker using the
`interact` pattern.
"""

from dataclasses import dataclass
from typing import Never

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy

import checker as ch


@dataclass
class ProveEqualityInteractive(dp.Query[dp.Response[ch.Proof, Never]]):
    """
    Query for proving trigonometric equalities interactively.
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
    # Run the checker on the target equality and the proposed proof
    feedback = yield from dp.compute(ch.check)(equality, proof, ch.TRIG_RULES)

    # If feedback is None, the proof is correct
    if feedback is None:
        return proof

    # Proof is incorrect – return feedback for the LLM
    return dp.Error(label="feedback", meta=str(feedback))


@strategy
def prove_equality_interactive(
    equality: ch.Eq
) -> Strategy[Branch, dp.PromptingPolicy, ch.Proof]:
    """
    Interactive strategy to prove a trigonometric equality.
    Queries the LLM iteratively, using checker feedback to refine the proof.
    Returns a ch.Proof on success.
    """
    # Use dp.interact to manage the LLM interaction with feedback loop
    result_proof = yield from dp.interact(
        step=lambda prefix, _:
            ProveEqualityInteractive(equality, prefix).using(dp.ambient_pp),
        process=lambda proof, _:
            check_equality(equality, proof).using(dp.just_compute)
    )

    return result_proof


def prove_equality_interactive_policy(
    model_name: str = "gpt-4o-mini",
    temperature: float | None = None,
    max_feedback_cycles: int = 3,
    loop: bool = False,
):
    """
    Policy for the interactive proof strategy.

    Args:
        model_name: Name of the model to use
        temperature: Temperature for sampling
        max_feedback_cycles: Maximum number of feedback rounds
        loop: Whether to loop the search
    """
    model = dp.standard_model(model_name)

    # `interact` branches twice per feedback cycle
    sp = dfs(max_depth=2*(max_feedback_cycles+1))
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(model, temperature=temperature, max_requests=1)
    return sp & pp