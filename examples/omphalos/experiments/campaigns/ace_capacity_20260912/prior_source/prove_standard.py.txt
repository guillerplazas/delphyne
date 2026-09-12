"""
Standard baseline for Rocq theorem proving in miniF2F.

Single-stage Hilbert-style loop: an LLM proposes a full proof script,
pytanque verifies it, the verifier's feedback (failing tactic, error,
remaining goals) is fed back, and the LLM revises until success or the
feedback budget is exhausted. The LLM has *one* action available
(propose a complete proof body); there are no tool calls. The agentic
counterpart lives in `prove_agentic.py`.

`ProofScript` is reused by `prove_agentic.py`; the agentic side has
its own automation-assisted verifier (`check_proof_assisted`).
"""

from dataclasses import dataclass
from typing import Never

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy

import runtime.pytanque_utils as pt
from runtime.model_registry import ApiType, OmphalosReasoningEffort, make_model

# fmt: off


type ProofScript = str
"""
Raw body of the proof: a fenced code block of Rocq tactics.
Parsed into a list of tactics inside `pt.split_into_tactics`.
"""


#####
##### Strategy
#####


@strategy
def prove_theorem_standard(
    problem_file: str,
    theorem_name: str,
) -> Strategy[Branch, dp.PromptingPolicy, ProofScript]:
    spec = pt.parse_problem(problem_file)
    script = yield from dp.interact(
        step=lambda prefix, _:
            ProposeProofScript(spec, prefix).using(dp.ambient_pp),
        process=lambda s, _:
            check_proof(problem_file, theorem_name, s).using(dp.just_compute),
    )
    return script


@dataclass
class ProposeProofScript(
    dp.Query[dp.Response[ProofScript | dp.WrappedParseError, Never]]
):
    spec: pt.ProblemSpec
    prefix: dp.AnswerPrefix = ()

    # `wrap_errors` turns a malformed reply (no code block) into
    # feedback for the next turn instead of killing the run.
    __parser__ = dp.last_code_block.wrap_errors.response


@strategy
def check_proof(
    problem_file: str,
    theorem_name: str,
    script: ProofScript,
) -> Strategy[Compute, object, ProofScript | dp.Error]:
    tactics = yield from dp.compute(pt.split_into_tactics)(script)
    feedback = yield from dp.compute(pt.check)(problem_file, theorem_name, tactics)
    if feedback.success:
        return script
    # `pt.check` appends a synthetic `Qed.`: a script whose tactics all
    # applied but left goals open fails exactly there. Surface that as
    # "incomplete" so the feedback template can show the verified
    # prefix + remaining goals instead of framing it as an error.
    if feedback.failing_tactic == "Qed." and feedback.remaining_goals:
        return dp.Error(label="incomplete", meta=feedback)
    return dp.Error(label="feedback", meta=feedback)


#####
##### Policy
#####


@dp.ensure_compatible(prove_theorem_standard)
def prove_theorem_standard_policy(
    model_name: str,
    temperature: float | None = None,
    max_feedback_cycles: int = 3,
    loop: bool = False,
    api: ApiType = "chat_completions",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    use_reasoning_cache: bool = True,
    convert_user_feedback_to_tool: bool = True,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    """
    Policy for the standard baseline.

    `api="responses"` routes requests through the OpenAI Responses API.
    On paper this baseline is where the reasoning cache should pay most:
    75-85% of its cost is output tokens and ~70-85% of those are
    reasoning, all of which Chat Completions makes the model re-derive
    on every feedback cycle because it does not return reasoning items.

    In practice it is where the cache *loses*, and the two flags below
    exist so the reason can be measured rather than argued:

    - `use_reasoning_cache` is what resends earlier reasoning items. It
      is the suspected cause of this baseline's input tokens rising 3.7x
      per turn under Responses (2,763 -> 10,202) while output falls.
      Turning it off isolates the API switch on its own.
    - `convert_user_feedback_to_tool` re-frames verifier feedback as a
      tool result so the KV cache can survive a user turn. It only
      matters when the reasoning cache is on.

    Both default to `True`, which is what `make_model` already did, so
    every archived run keeps replaying byte-identically.

    `tag_user_feedback_messages` is gated on the API rather than always
    set. The flag marks verifier feedback so the Responses model can
    present it as a tool result, but it is part of the hashed
    `LLMRequest`, so setting it unconditionally would invalidate every
    archived cache and make the frozen benchmark runs unreplayable.
    """
    model = make_model(
        model_name,
        api=api,
        reasoning_effort=reasoning_effort,
        use_reasoning_cache=use_reasoning_cache,
        convert_user_feedback_to_tool=convert_user_feedback_to_tool,
    )
    sp = dfs(max_depth=max_feedback_cycles + 1)
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(
        model,
        temperature=temperature,
        max_requests=1,
        tag_user_feedback_messages=(api == "responses"),
    )
    return sp & pp
