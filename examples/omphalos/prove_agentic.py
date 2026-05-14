"""
Agentic baseline for Rocq theorem proving in miniF2F.

Same outer loop as `prove_standard.py` (an LLM proposes a proof script,
pytanque verifies it, the verifier's feedback is fed back for revision),
but the LLM now has a second action: it can call the `ReadSkill` tool
to load a curated Rocq skill markdown file from `rocq_skills_data/`.
Each tool call appends the skill content to the conversation history
before the LLM's next move.

This is the difference that earns the "agentic" label: the LLM chooses
between two actions (propose a proof / lookup a skill) and allocates its
request budget across them at its own discretion. Skill content is
loaded on demand instead of baked into the system prompt.

Reuses `ProofScript` and `check_proof` verbatim from `prove_standard`.
"""

from dataclasses import dataclass

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy

import pytanque_utils as pt
import skills as sk
from prove_standard import ProofScript, check_proof

# fmt: off


#####
##### Tool
#####


@dataclass
class ReadSkill(dp.AbstractTool[str]):
    """
    Load a Rocq skill reference and append its full content to this
    conversation. Use this before (or between) proof attempts when you
    need detailed tactic guidance, stdlib lemma cheatsheets, error
    explanations, or proof templates.

    The set of legal `skill_name` values is shown to you as a table in
    the system prompt; calling with any other name returns an error
    message.
    """
    skill_name: str


#####
##### Strategy
#####


@strategy
def _read_skill_handler(name: str) -> Strategy[Compute, object, str]:
    """Trivial @strategy wrapper so the tool handler returns a StrategyInstance."""
    text = yield from dp.compute(sk.read_skill)(name)
    return text


@strategy
def prove_theorem_agentic(
    problem_file: str,
    theorem_name: str,
) -> Strategy[Branch, dp.PromptingPolicy, ProofScript]:
    spec = pt.parse_problem(problem_file)
    available = sk.list_skills()
    script = yield from dp.interact(
        step=lambda prefix, _:
            ProposeProofScriptAgentic(spec, available, prefix).using(dp.ambient_pp),
        process=lambda s, _:
            check_proof(problem_file, theorem_name, s).using(dp.just_compute),
        tools={
            ReadSkill: lambda call:
                _read_skill_handler(call.skill_name).using(dp.just_compute),
        },
    )
    return script


@dataclass
class ProposeProofScriptAgentic(
    dp.Query[dp.Response[ProofScript, ReadSkill]]
):
    spec: pt.ProblemSpec
    available_skills: dict[str, str]
    prefix: dp.AnswerPrefix

    __parser__ = dp.last_code_block.response


#####
##### Policy
#####


def prove_theorem_agentic_policy(
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
