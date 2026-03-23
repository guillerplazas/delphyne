"""
Sketch-guided step-by-step proof strategy.

Phase 1: A larger model generates a verifier-compatible proof sketch.
Phase 2: A smaller model proposes ONE proof step at a time, with the
sketch visible as context.

Each step is verified immediately. The sketch is also validated before
use so that unsupported proof moves do not poison the full run.
"""

from dataclasses import dataclass, field
import re
from typing import Never

import delphyne as dp
from delphyne import Branch, Compute, IPDict, Strategy, dfs, strategy
from delphyne.stdlib.search.interactive import InteractStats

import checker as ch

type StepVerifyResult = ch.Proof | ch.Step  # ch.Proof = complete; ch.Step = valid but incomplete


SKETCH_ALLOWED_MOVES = ("rule:", "sym", "step", "trans")
SKETCH_BANNED_PHRASES = {
    "difference of squares": (
        "Do not use unsupported algebraic macro-rules like difference of "
        "squares. Only use rule:<name>, sym, step, and trans."
    ),
    "difference_of_squares": (
        "Do not invent rule names such as difference_of_squares."
    ),
    "a2_minus_b2": "Do not invent rule names such as a2_minus_b2.",
    "half-angle": (
        "Do not rely on half-angle identities unless they are derived step by step."
    ),
    "product-to-sum": "Do not rely on product-to-sum identities in the sketch.",
    "sum-to-product": "Do not rely on sum-to-product identities in the sketch.",
    "(a-b)(a+b)": "Do not cite unsupported algebraic macros like (A-B)(A+B).",
}
SKETCH_RULE_RE = re.compile(r"rule:([A-Za-z_][A-Za-z0-9_]*)")


# ── Shared Helpers ────────────────────────────────────────────────────────────


def _model_options(reasoning_effort: str | None) -> dict[str, object] | None:
    if reasoning_effort is None:
        return None
    return {"reasoning_effort": reasoning_effort}



def _validate_sketch(sketch: str) -> str | None:
    stripped = sketch.strip()
    if not stripped:
        return (
            "The sketch was empty. Write a short numbered plan using only "
            "rule:<name>, sym, step, and trans."
        )

    lowered = stripped.lower()
    for phrase, message in SKETCH_BANNED_PHRASES.items():
        if phrase in lowered:
            return message

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    for i, line in enumerate(lines, start=1):
        if not re.match(r"^\d+\.", line):
            return (
                f"Sketch line {i} must start with a numbered item like "
                f"'1. rule:sin_add ...'."
            )
        if not any(token in line for token in SKETCH_ALLOWED_MOVES):
            return (
                f"Sketch line {i} must describe an allowed move using only "
                f"rule:<name>, sym, step, or trans."
            )
        for rule_name in SKETCH_RULE_RE.findall(line):
            if rule_name not in ch.TRIG_RULES:
                return (
                    f"The sketch uses unsupported rule '{rule_name}'. Only use: "
                    + ", ".join(sorted(ch.TRIG_RULES))
                )
    return None


def _get_sketch_line(sketch: str, step_number: int) -> str | None:
    """Returns the step_number-th non-empty sketch line (1-indexed), or None."""
    lines = [l.strip() for l in sketch.strip().splitlines() if l.strip()]
    if 1 <= step_number <= len(lines):
        return lines[step_number - 1]
    return None


# ── Phase 1: Proof Sketch ─────────────────────────────────────────────────────


@dataclass
class GenerateProofSketch(dp.Query[dp.Response[str, Never]]):
    """Generate a verifier-compatible proof plan using only supported moves."""

    equality: ch.Eq
    prefix: dp.AnswerPrefix = field(default_factory=list)

    __parser__ = dp.last_code_block.response

    def globals(self) -> dict[str, object]:
        return {"rules": ch.TRIG_RULES}


@strategy
def check_sketch(sketch: str) -> Strategy[Compute, object, str | dp.Error]:
    """
    Reject sketches that cite unsupported rules or proof moves.
    """
    error = _validate_sketch(sketch)
    if error is not None:
        return dp.Error(label="sketch_feedback", meta=error)
        yield
    return sketch
    yield


# ── Phase 2: Step-by-Step with Sketch Context ─────────────────────────────────


@dataclass
class ProposeNextStep(dp.Query[dp.Response[ch.Proof, Never]]):
    """Ask the LLM for exactly ONE new step, given sketch + partial proof as context."""

    equality: ch.Eq
    sketch: str
    partial_proof: ch.Proof
    current_sketch_line: str | None = None
    prefix: dp.AnswerPrefix = field(default_factory=list)

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


@strategy
def generate_validated_sketch(
    equality: ch.Eq,
) -> Strategy[Branch, IPDict, str]:
    """
    Produce a proof sketch and reject it once if it cites unsupported moves.
    """
    return (yield from dp.interact(
        step=lambda prefix, _: GenerateProofSketch(equality, prefix).using(...),
        process=lambda sketch, _: check_sketch(sketch).using(dp.just_compute),
    ))



@strategy
def prove_one_step(
    equality: ch.Eq,
    sketch: str,
    partial_proof: ch.Proof,
    current_sketch_line: str | None = None,
) -> Strategy[Branch, IPDict, StepVerifyResult]:
    """Uses dp.interact to propose and validate a single new step."""
    new_step_id = (max(partial_proof.keys()) + 1) if partial_proof else 1

    def process(raw_proof: ch.Proof, stats: InteractStats):
        if len(raw_proof) != 1:
            hint = ""
            if stats.num_rejected >= 1:
                hint = " Back up and propose a smaller local rewrite."
            return dp.const_space(dp.Error(
                label="step_feedback",
                meta=f"Expected exactly 1 step, got {len(raw_proof)}. "
                     f"Write only step {new_step_id}.{hint}"
            ))
        # Normalize: ignore whatever key the LLM used, always use new_step_id
        _, new_step = next(iter(raw_proof.items()))
        return verify_new_step(
            equality, partial_proof, new_step_id, new_step
        ).using(dp.just_compute)

    return (yield from dp.interact(
        step=lambda prefix, _: ProposeNextStep(
            equality, sketch, partial_proof, current_sketch_line, prefix
        ).using(...),
        process=process,
    ))


@strategy
def prove_step_by_step(
    equality: ch.Eq,
    max_steps: int = 20,
) -> Strategy[Branch, IPDict, ch.Proof]:
    """
    Two-phase strategy: generate a proof sketch, then build the proof one step at a time.
    Each step is verified immediately. Succeeds when a step completes the proof.
    """
    # Phase 1: generate a verifier-compatible proof roadmap.
    sketch = yield from generate_validated_sketch(equality).inline()

    # Phase 2: incremental step generation guided by the sketch
    partial_proof: ch.Proof = {}

    for _ in range(max_steps):
        step_number = (max(partial_proof.keys()) + 1) if partial_proof else 1
        current_sketch_line = _get_sketch_line(sketch, step_number)
        result = yield from prove_one_step(equality, sketch, partial_proof, current_sketch_line).inline()

        if isinstance(result, dict):
            return result  # Complete proof returned by verify_new_step

        # result is ch.Step (tuple): valid step, proof not yet complete
        new_step_id = (max(partial_proof.keys()) + 1) if partial_proof else 1
        partial_proof = {**partial_proof, new_step_id: result}

    yield from dp.fail(message=f"Could not complete proof in {max_steps} steps.")



def prove_step_by_step_policy(
    sketch_model_name: str = "gpt-5.4",
    step_model_name: str = "gpt-5.4-mini",
    sketch_reasoning_effort: str | None = "high",
    step_reasoning_effort: str | None = "low",
    num_completions: int = 2,
    max_feedback_cycles_per_step: int = 2,
    max_steps: int = 20,
    max_sketch_feedback_cycles: int = 1,
    loop: bool = False,
):
    """
    Policy for step-by-step strategy.

    Args:
        sketch_model_name: Model used to generate the global sketch
        step_model_name: Model used to propose local proof steps
        sketch_reasoning_effort: Reasoning effort for the sketch model
        step_reasoning_effort: Reasoning effort for the step model
        num_completions: Number of step candidates per request
        max_feedback_cycles_per_step: Max feedback rounds per step
        max_steps: Maximum number of validated proof steps to keep
        max_sketch_feedback_cycles: Number of times an invalid sketch may be retried
        loop: Whether to loop the search
    """
    total_rounds = (
        (max_sketch_feedback_cycles + 1)
        + max_steps * (max_feedback_cycles_per_step + 1)
    )
    request_limit = dp.BudgetLimit({dp.NUM_REQUESTS: total_rounds})
    sp = dp.with_budget(request_limit) @ dfs(max_depth=total_rounds)
    if loop:
        sp = dp.loop() @ sp

    sketch_pp = dp.few_shot(
        dp.standard_model(
            sketch_model_name,
            _model_options(sketch_reasoning_effort),
        ),
        max_requests=1,
    )
    step_pp = dp.few_shot(
        dp.standard_model(
            step_model_name,
            _model_options(step_reasoning_effort),
        ),
        num_completions=num_completions,
        max_requests=1,
    )
    return sp & {
        "GenerateProofSketch": sketch_pp,
        "ProposeNextStep": step_pp,
    }
