"""
Draft-and-repair proof strategy.

Phase 1: A strong model drafts a COMPLETE proof, directly in the
checker's YAML format (the same format used by all other strategies in
this example — there is no intermediate "plan" language).

Phase 2: The draft is replayed one step at a time against the checker.
Steps that verify are accepted without any LLM call. When a step fails,
a cheap model is asked to repair just that step, given the draft, the
verified proof so far, and the checker's error message.

The verified proof is always renumbered sequentially (1, 2, ...) and a
draft-id-to-verified-id map translates step references, so a repaired
step can never invalidate the verified prefix.
"""

from dataclasses import dataclass
from typing import Never, assert_never

import delphyne as dp
from delphyne import Branch, Compute, Fail, IPDict, Strategy, dfs, strategy
from delphyne.stdlib.search.interactive import InteractStats

import checker as ch

type StepVerifyResult = (
    ch.Proof | ch.Step
)  # ch.Proof = complete; ch.Step = valid but incomplete


# ── Shared Helpers ────────────────────────────────────────────────────────────


def _model(
    model_name: str,
    reasoning_effort: dp.ReasoningEffort | None,
) -> dp.OpenAICompatibleModel:
    options: dp.RequestOptions | None = None
    if reasoning_effort is not None:
        options = {"reasoning_effort": reasoning_effort}
    return dp.standard_model(model_name, options)


def _remap_justification(
    justification: ch.Justification,
    id_map: dict[ch.StepId, ch.StepId],
) -> ch.Justification | None:
    """
    Translate the step references of a draft justification into
    verified-proof ids. Returns None if the justification references a
    draft step that has no verified counterpart yet (e.g. a forward
    reference).
    """
    match justification:
        case ch.Rule():
            return justification
        case ch.Sym(step):
            if (mapped := id_map.get(step)) is None:
                return None
            return ch.Sym(mapped)
        case ch.RewritePrev(step):
            if (mapped := id_map.get(step)) is None:
                return None
            return ch.RewritePrev(mapped)
        case ch.Trans(steps):
            mapped_steps: list[ch.StepId] = []
            for s in steps:
                if (m := id_map.get(s)) is None:
                    return None
                mapped_steps.append(m)
            return ch.Trans(mapped_steps)


def _overlapping_vars_hint(rule_vars: dict[str, ch.Term]) -> str | None:
    """
    Detect rule variable substitutions that corrupt under the checker's
    sequential (NOT simultaneous) substitution semantics. For example,
    `{x: "y", y: "-y"}` first turns `cos(x + y)` into `cos(y + y)` and
    then into `cos(-y + -y)` — not into `cos(y + -y)` as intended.
    """
    pairs = list(rule_vars.items())
    for i, (var, value) in enumerate(pairs):
        try:
            introduced = {str(s) for s in ch.parse_term(value).free_symbols}
        except ch.TermParseError:
            continue  # Let the checker report the syntax error.
        for later_var, later_value in pairs[i + 1 :]:
            if later_var in introduced and later_value != later_var:
                return (
                    f"vars substitution is sequential, so '{var}' → "
                    f"\"{value}\" first introduces '{later_var}', which "
                    f'is then rewritten to "{later_value}", corrupting '
                    f"the result. Put the negative sign on the variable "
                    f"being replaced instead (e.g. use "
                    f'{{{var}: "-{later_var}", {later_var}: '
                    f'"{later_var}"}} to obtain a difference).'
                )
    return None


def _validate_draft(draft: ch.Proof, max_total_steps: int) -> str | None:
    """
    Typed, structural validation of a draft proof. Semantic errors are
    deliberately not rejected here: they are repaired step by step in
    phase 2.
    """
    if not draft:
        return "The proof is empty. Write a complete YAML proof."
    if len(draft) > max_total_steps:
        return (
            f"The proof has {len(draft)} steps, which exceeds the "
            f"maximum of {max_total_steps}. Find a shorter proof."
        )
    for step_id, (_, justification) in draft.items():
        if isinstance(justification, ch.Rule):
            if justification.rule not in ch.TRIG_RULES:
                return (
                    f"Step {step_id} uses unsupported rule "
                    f"'{justification.rule}'. Only use: "
                    + ", ".join(sorted(ch.TRIG_RULES))
                )
            if (
                hint := _overlapping_vars_hint(justification.vars)
            ) is not None:
                return f"Step {step_id}: {hint}"
        if isinstance(justification, ch.Trans):
            if len(justification.trans) < 2:
                return (
                    f"Step {step_id}: trans must chain at least 2 "
                    f"steps. Use {{step: ...}} or {{sym: ...}} for a "
                    f"single reference."
                )
    return None


# ── Phase 1: Proof Draft ──────────────────────────────────────────────────────


@dataclass
class GenerateProofDraft(dp.Query[dp.Response[ch.Proof, Never]]):
    """Draft a complete machine-checkable proof in the checker's format."""

    equality: ch.Eq
    prefix: dp.AnswerPrefix = ()

    __parser__ = dp.last_code_block.yaml_as(ch.Proof).response

    def globals(self) -> dict[str, object]:
        return {"rules": ch.TRIG_RULES}


@dataclass
class CheckedDraft:
    """A structurally valid draft, with the result of a full check."""

    proof: ch.Proof
    complete: bool


@strategy
def check_draft(
    equality: ch.Eq, draft: ch.Proof, max_total_steps: int
) -> Strategy[Compute, object, CheckedDraft | dp.Error]:
    """
    Reject structurally invalid drafts (unknown rules, single-step
    trans, too long) and check whether the draft already proves the
    equality. A draft that fails the check only semantically is still
    accepted: phase 2 repairs it.
    """
    error = _validate_draft(draft, max_total_steps)
    if error is not None:
        return dp.Error(label="draft_feedback", meta=error)
    draft = dict(sorted(draft.items()))
    check_error = yield from dp.compute(ch.check)(
        equality, draft, ch.TRIG_RULES
    )
    return CheckedDraft(draft, complete=check_error is None)


@strategy
def generate_draft(
    equality: ch.Eq, max_total_steps: int
) -> Strategy[Branch, IPDict, CheckedDraft]:
    """
    Produce a draft proof, retrying on parse errors and structural
    rejections.
    """
    return (
        yield from dp.interact(
            step=lambda prefix, _: GenerateProofDraft(equality, prefix).using(
                ...
            ),
            process=lambda draft, _: check_draft(
                equality, draft, max_total_steps
            ).using(dp.just_compute),
        )
    )


# ── Phase 2: Verified Replay with Repair ──────────────────────────────────────


@dataclass
class RepairProofStep(dp.Query[dp.Response[ch.Proof, Never]]):
    """Ask the LLM for exactly ONE step, given the draft, the verified
    proof so far, and the error that made the draft step fail."""

    equality: ch.Eq
    draft: ch.Proof
    verified_proof: ch.Proof
    step_id: ch.StepId
    failed_step: ch.Step | None  # None: draft exhausted, extend the proof
    error: str
    prefix: dp.AnswerPrefix = ()

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
    justification = new_step[1]
    if isinstance(justification, ch.Rule):
        if (hint := _overlapping_vars_hint(justification.vars)) is not None:
            return dp.Error(
                label="step_feedback",
                meta=f"Error at step {new_step_id}: {hint}",
            )
    candidate = {**partial_proof, new_step_id: new_step}
    error = yield from dp.compute(ch.check)(equality, candidate, ch.TRIG_RULES)

    if error is None:
        return candidate  # Complete proof!

    if error.step == new_step_id:
        return dp.Error(label="step_feedback", meta=str(error))

    # error.step is None or < new_step_id → step itself is valid, proof not done yet
    return new_step


@strategy
def repair_step(
    equality: ch.Eq,
    draft: ch.Proof,
    verified_proof: ch.Proof,
    step_id: ch.StepId,
    failed_step: ch.Step | None,
    error: str,
) -> Strategy[Branch, IPDict, StepVerifyResult]:
    """Uses dp.interact to propose and validate a single repaired step."""

    def process(raw_proof: ch.Proof, stats: InteractStats):
        if len(raw_proof) != 1:
            hint = ""
            if stats.num_rejected >= 1:
                hint = " Back up and propose a smaller local rewrite."
            return dp.const_space(
                dp.Error(
                    label="step_feedback",
                    meta=f"Expected exactly 1 step, got {len(raw_proof)}. "
                    f"Write only step {step_id}.{hint}",
                )
            )
        # Normalize: ignore whatever key the LLM used, always use step_id
        _, new_step = next(iter(raw_proof.items()))
        return verify_new_step(
            equality, verified_proof, step_id, new_step
        ).using(dp.just_compute)

    return (
        yield from dp.interact(
            step=lambda prefix, _: RepairProofStep(
                equality,
                draft,
                verified_proof,
                step_id,
                failed_step,
                error,
                prefix,
            ).using(...),
            process=process,
        )
    )


@strategy
def prove_step_by_step(
    equality: ch.Eq,
    max_total_steps: int = 24,
) -> Strategy[Branch | Fail, IPDict, ch.Proof]:
    """
    Two-phase strategy: draft a complete proof, then replay it one step
    at a time. Draft steps that verify are accepted without any LLM
    call; failing steps are repaired by a (cheaper) model. If the draft
    runs out before the proof is complete, the repair model extends it.
    """
    # Phase 1: draft a complete proof in the checker's own format.
    draft = yield from generate_draft(equality, max_total_steps).inline()
    if draft.complete:
        return draft.proof

    # Phase 2: verified replay. `verified` is always renumbered
    # sequentially (keys 1..k-1) and fully checker-verified; `id_map`
    # translates draft step ids to verified ids.
    verified: ch.Proof = {}
    id_map: dict[ch.StepId, ch.StepId] = {}
    draft_items = sorted(draft.proof.items())
    cursor = 0

    for k in range(1, max_total_steps + 1):
        consuming_draft = cursor < len(draft_items)
        failed_step: ch.Step | None = None

        if consuming_draft:
            draft_id, (draft_eq, draft_just) = draft_items[cursor]
            remapped = _remap_justification(draft_just, id_map)
            if remapped is not None:
                # Free check: replay the draft step (zero LLM calls).
                candidate_step: ch.Step = (draft_eq, remapped)
                outcome = yield from dp.run(
                    verify_new_step(
                        equality, verified, k, candidate_step
                    ).using(dp.just_compute)
                )
                if isinstance(outcome, dict):
                    return outcome  # Draft step completes the proof.
                if not isinstance(outcome, dp.Error):
                    verified = {**verified, k: outcome}
                    id_map[draft_id] = k
                    cursor += 1
                    continue
                failed_step = candidate_step
                error = str(outcome.meta)
            else:
                failed_step = (draft_eq, draft_just)
                error = (
                    f"Draft step {draft_id} references a step that has "
                    f"no verified counterpart. Rewrite it against the "
                    f"verified proof."
                )
        else:
            # Extension mode: the draft is exhausted but the proof is
            # not complete yet.
            error = (
                "The draft is exhausted but the proof does not end "
                "with the target equality yet."
            )

        result = yield from repair_step(
            equality,
            draft.proof,
            verified,
            k,
            failed_step,
            error,
        ).inline()

        if isinstance(result, dict):
            return result  # Complete proof returned by verify_new_step.

        # result is ch.Step (tuple): valid step, proof not yet complete.
        verified = {**verified, k: result}
        if consuming_draft:
            # The repaired step plays the failed draft step's role.
            id_map[draft_items[cursor][0]] = k
            cursor += 1

    assert_never(
        (
            yield from dp.fail(
                message=f"Could not complete proof in {max_total_steps} steps."
            )
        )
    )


def prove_step_by_step_policy(
    draft_model_name: str = "gpt-5.4",
    repair_model_name: str = "gpt-5.4",
    draft_reasoning_effort: dp.ReasoningEffort | None = "medium",
    repair_reasoning_effort: dp.ReasoningEffort | None = "low",
    num_completions: int = 5,
    max_repair_cycles_per_step: int = 4,
    max_total_steps: int = 30,
    max_draft_feedback_cycles: int = 2,
    loop: bool = False,
):
    """
    Policy for the draft-and-repair strategy.

    Args:
        draft_model_name: Model used to draft the complete proof
        repair_model_name: Model used to repair failing proof steps
        draft_reasoning_effort: Reasoning effort for the draft model
        repair_reasoning_effort: Reasoning effort for the repair model
        num_completions: Number of repair candidates per request
        max_repair_cycles_per_step: Max feedback rounds per repaired step
        max_total_steps: Maximum number of validated proof steps to keep
        max_draft_feedback_cycles: Number of times an invalid draft may be retried
        loop: Whether to loop the search
    """
    total_rounds = (max_draft_feedback_cycles + 1) + max_total_steps * (
        max_repair_cycles_per_step + 1
    )
    request_limit = dp.BudgetLimit({dp.NUM_REQUESTS: total_rounds})
    sp = dp.with_budget(request_limit) @ dfs(max_depth=total_rounds)
    if loop:
        sp = dp.loop() @ sp

    draft_pp = dp.few_shot(
        _model(draft_model_name, draft_reasoning_effort),
        max_requests=1,
    )
    repair_pp = dp.few_shot(
        _model(repair_model_name, repair_reasoning_effort),
        num_completions=num_completions,
        max_requests=1,
    )
    return sp & {
        "GenerateProofDraft": draft_pp,
        "RepairProofStep": repair_pp,
    }


def prove_step_by_step_escalation_policy(
    draft_model_name: str = "gpt-5.4",
    cheap_draft_model_name: str = "gpt-5.4",
    cheap_draft_effort: dp.ReasoningEffort = "low",
    cheap_repair_model_name: str = "gpt-5.4-mini",
    cheap_repair_effort: dp.ReasoningEffort = "medium",
    cheap_num_completions: int = 2,
    cheap_request_limit: int = 6,
    cheap_dollar_limit: float = 0.04,
    strong_draft_effort: dp.ReasoningEffort = "medium",
    strong_repair_model_name: str = "gpt-5.4",
    num_completions: int = 5,
    max_repair_cycles_per_step: int = 4,
    max_total_steps: int = 30,
    max_draft_feedback_cycles: int = 2,
    loop: bool = True,
):
    """
    Budget-administering policy for the draft-and-repair strategy.

    Runs the strategy under a *cheap* configuration first (low-effort
    draft, small repair model, bounded retry loop, capped both at
    `cheap_request_limit` LLM requests and `cheap_dollar_limit`
    dollars). Only if the cheap tier yields no proof is the *strong*
    configuration tried (higher-effort draft, strong repair model,
    restart loop).

    The ladder economics rely on the cheap tier being generous with
    cheap tokens and the escalation being rare: an extra small-model
    repair round costs around a cent, while every problem the cheap
    tier solves avoids a strong-model draft that costs a nickel. The
    dollar cap matters because reasoning-token usage is heavy-tailed:
    it cuts off the occasional run-away reasoning chain that a pure
    request cap would let through.

    Args:
        draft_model_name: Model drafting proofs in the strong tier
        cheap_draft_model_name: Model drafting proofs in the cheap tier
        cheap_draft_effort: Draft reasoning effort in the cheap tier
        cheap_repair_model_name: Repair model in the cheap tier
        cheap_repair_effort: Repair reasoning effort in the cheap tier
        cheap_num_completions: Repair candidates per request in the
            cheap tier (each candidate pays its own reasoning tokens,
            so this is kept small)
        cheap_request_limit: LLM request budget of the cheap tier
        cheap_dollar_limit: Dollar budget of the cheap tier
        strong_draft_effort: Draft reasoning effort in the strong tier
        strong_repair_model_name: Repair model in the strong tier
        num_completions: Number of repair candidates per request
        max_repair_cycles_per_step: Max feedback rounds per repaired step
        max_total_steps: Maximum number of validated proof steps to keep
        max_draft_feedback_cycles: Number of times an invalid draft may be retried
        loop: Whether to loop the search in the strong tier
    """
    cheap_budget = dp.BudgetLimit(
        {
            dp.NUM_REQUESTS: cheap_request_limit,
            dp.DOLLAR_PRICE: cheap_dollar_limit,
        }
    )
    cheap = dp.with_budget(cheap_budget) @ prove_step_by_step_policy(
        draft_model_name=cheap_draft_model_name,
        repair_model_name=cheap_repair_model_name,
        draft_reasoning_effort=cheap_draft_effort,
        repair_reasoning_effort=cheap_repair_effort,
        num_completions=cheap_num_completions,
        max_repair_cycles_per_step=max_repair_cycles_per_step,
        max_total_steps=max_total_steps,
        max_draft_feedback_cycles=max_draft_feedback_cycles,
        loop=True,
    )
    strong = prove_step_by_step_policy(
        draft_model_name=draft_model_name,
        repair_model_name=strong_repair_model_name,
        draft_reasoning_effort=strong_draft_effort,
        repair_reasoning_effort="low",
        num_completions=num_completions,
        max_repair_cycles_per_step=max_repair_cycles_per_step,
        max_total_steps=max_total_steps,
        max_draft_feedback_cycles=max_draft_feedback_cycles,
        loop=loop,
    )
    return cheap.or_else(strong)
