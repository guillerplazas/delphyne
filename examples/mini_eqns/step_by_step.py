"""
Sketch-guided step-by-step proof strategy.

Phase 1: One LLM call generates an informal proof sketch (which rules to apply, in what order).
Phase 2: LLM is asked for ONE proof step at a time, with the sketch visible as context.
Each step is verified immediately; the sketch keeps generation focused and directed.
"""

from dataclasses import dataclass
from typing import Never

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy
from delphyne.stdlib.search.interactive import InteractStats

import checker as ch

type StepVerifyResult = ch.Proof | ch.Step  # ch.Proof = complete; ch.Step = valid but incomplete


# ── Phase 1: Proof Sketch ─────────────────────────────────────────────────────

@dataclass
class GenerateProofSketch(dp.Query[str]):
    """Generate an informal proof plan: which rules to apply, in what order."""
    equality: ch.Eq

    __parser__ = dp.last_code_block

    def globals(self) -> dict[str, object]:
        return {"rules": ch.TRIG_RULES}


# ── Phase 2: Step-by-Step with Sketch Context ─────────────────────────────────

@dataclass
class ProposeNextStep(dp.Query[dp.Response[ch.Proof, Never]]):
    """Ask the LLM for exactly ONE new step, given sketch + partial proof as context."""
    equality: ch.Eq
    sketch: str
    partial_proof: ch.Proof
    prefix: dp.AnswerPrefix

    __parser__ = dp.last_code_block.yaml_as(ch.Proof).response

    def globals(self) -> dict[str, object]:
        return {"rules": ch.TRIG_RULES}


@strategy
def verify_new_step(
    equality: ch.Eq,
    partial_proof: ch.Proof,
    new_step_id: ch.StepId,
    new_step: ch.Step,
) -> Strategy[Compute, object, StepVerifyResult | dp.Error]:
    """
    Validates a single proposed step in context of the partial proof.

    Returns:
    - ch.Proof  → step completes the proof (full valid proof returned)
    - ch.Step   → step is valid but proof not complete (continue outer loop)
    - dp.Error  → this step is wrong (interact will retry with feedback)
    """
    candidate = {**partial_proof, new_step_id: new_step}
    error = yield from dp.compute(ch.check)(equality, candidate, ch.TRIG_RULES)

    if error is None:
        return candidate  # Complete proof!

    if error.step == new_step_id:
        return dp.Error(label="step_feedback", meta=str(error))

    # error.step is None or < new_step_id → step itself is valid, proof not done yet
    return new_step


def prove_one_step(
    equality: ch.Eq,
    sketch: str,
    partial_proof: ch.Proof,
) -> Strategy[Branch, dp.PromptingPolicy, StepVerifyResult]:
    """Uses dp.interact to propose and validate a single new step."""
    new_step_id = (max(partial_proof.keys()) + 1) if partial_proof else 1

    def process(raw_proof: ch.Proof, _stats: InteractStats):
        if len(raw_proof) != 1:
            return dp.const_space(dp.Error(
                label="step_feedback",
                meta=f"Expected exactly 1 step, got {len(raw_proof)}. "
                     f"Write only step {new_step_id}."
            ))
        # Normalize: ignore whatever key the LLM used, always use new_step_id
        _, new_step = next(iter(raw_proof.items()))
        return verify_new_step(
            equality, partial_proof, new_step_id, new_step
        ).using(dp.just_compute)

    return (yield from dp.interact(
        step=lambda prefix, _: ProposeNextStep(
            equality, sketch, partial_proof, prefix
        ).using(dp.ambient_pp),
        process=process,
    ))


@strategy
def prove_step_by_step(
    equality: ch.Eq,
    max_steps: int = 20,
) -> Strategy[Branch, dp.PromptingPolicy, ch.Proof]:
    """
    Two-phase strategy: generate a proof sketch, then build the proof one step at a time.
    Each step is verified immediately. Succeeds when a step completes the proof.
    """
    # Phase 1: one LLM call to generate the informal proof roadmap
    sketch = yield from dp.branch(
        GenerateProofSketch(equality).using(dp.ambient_pp)
    )

    # Phase 2: incremental step generation guided by the sketch
    partial_proof: ch.Proof = {}

    for _ in range(max_steps):
        result = yield from prove_one_step(equality, sketch, partial_proof)

        if isinstance(result, dict):
            return result  # Complete proof returned by verify_new_step

        # result is ch.Step (tuple): valid step, proof not yet complete
        new_step_id = (max(partial_proof.keys()) + 1) if partial_proof else 1
        partial_proof = {**partial_proof, new_step_id: result}

    yield from dp.fail(message=f"Could not complete proof in {max_steps} steps.")


def prove_step_by_step_policy(
    model_name: str = "gpt-5-mini-2025-08-07",
    temperature: float | None = None,
    max_feedback_cycles_per_step: int = 2,
    loop: bool = False,
    reasoning_effort: str | None = None,
):
    """
    Policy for step-by-step strategy.

    Args:
        model_name: Name of the model to use
        temperature: Temperature for sampling
        max_feedback_cycles_per_step: Max feedback rounds per step (3 total tries)
        loop: Whether to loop the search
        reasoning_effort: Optional reasoning effort level (e.g. "low", "medium", "high")
    """
    options: dict[str, object] = {}
    if reasoning_effort is not None:
        options["reasoning_effort"] = reasoning_effort
    model = dp.standard_model(model_name, options or None)
    sp = dfs(max_depth=2 * (max_feedback_cycles_per_step + 1))
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(model, temperature=temperature, max_requests=1)
    return sp & pp
