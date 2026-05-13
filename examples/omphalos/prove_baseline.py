"""
A conversational agent baseline for Rocq theorem proving in miniF2F.

Mirrors `examples/find_invariants/baseline.py`: an LLM proposes a full
proof script, pytanque verifies it, the verifier's feedback (failing
tactic, error, remaining goals) is fed back, and the LLM revises until
success or the feedback budget is exhausted.
"""

from dataclasses import dataclass
from typing import Never

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy

import pytanque_utils as pt

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
def prove_theorem_interactive(
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
class ProposeProofScript(dp.Query[dp.Response[ProofScript, Never]]):
    spec: pt.ProblemSpec
    prefix: dp.AnswerPrefix

    __parser__ = dp.last_code_block.response


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
    return dp.Error(label="feedback", meta=feedback)


#####
##### Policy
#####


def prove_theorem_interactive_policy(
    model_name: str,
    temperature: float | None = None,
    max_feedback_cycles: int = 3,
    loop: bool = False,
):
    model = dp.standard_model(model_name)
    sp = dfs(max_depth=max_feedback_cycles + 1)
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(model, temperature=temperature, max_requests=1)
    return sp & pp
