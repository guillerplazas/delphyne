"""
Agentic baseline for Rocq theorem proving in miniF2F.

Same outer loop as `prove_standard.py` (an LLM proposes a proof script,
pytanque verifies it, the verifier's feedback is fed back for revision),
but the LLM has *exploration* actions available alongside proposing:

  - `ReadSkill(skill_name=...)` loads a curated Rocq skill markdown
    file from `rocq_skills_data/` into the chat history.
  - `SearchRocq(command=...)` runs a Rocq introspection command
    (`Search ...`, `Check ...`, `Print ...`, `About ...`,
    `SearchPattern ...`) against the problem's initial proof state via
    pytanque, and returns the formatted feedback.

The LLM allocates its request budget across these actions and proof
proposals at its own discretion. `ReadSkill` is for textbook-level
reference content; `SearchRocq` is for problem-specific lemma /
definition discovery (i.e. answers "does the lemma I want to cite
actually exist under this name?" before the agent commits to a tactic).

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


@dataclass
class SearchRocq(dp.AbstractTool[str]):
    """
    Query Rocq's interactive REPL for introspection information about
    the current problem's context. Use this BEFORE proposing a proof,
    or AFTER a failed attempt where a lemma name was wrong, to discover
    real lemma names / types / definitions instead of guessing.

    Pass `command` as a full Rocq command terminated with a period.
    Examples:
      command="Search (_ + _ <= _ + _)."   # find lemmas matching a shape
      command="SearchPattern (_ * _)."     # narrower structural search
      command="Check Rabs_pos."            # show a lemma's statement
      command="Print Rsqr."                # show a definition's body
      command="About lia."                 # short summary of a tactic

    The output is whatever Rocq prints to its feedback channel. Long
    outputs are truncated; refine your query if you hit the truncation
    marker. Syntax errors come back as an error message that you can
    correct on your next turn.
    """
    command: str


#####
##### Strategy
#####


@strategy
def _read_skill_handler(name: str) -> Strategy[Compute, object, str]:
    """Trivial @strategy wrapper so the tool handler returns a StrategyInstance."""
    text = yield from dp.compute(sk.read_skill)(name)
    return text


@strategy
def _search_rocq_handler(
    problem_file: str, theorem_name: str, command: str,
) -> Strategy[Compute, object, str]:
    """Wraps pt.query so the SearchRocq handler returns a StrategyInstance."""
    text = yield from dp.compute(pt.query)(problem_file, theorem_name, command)
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
            SearchRocq: lambda call:
                _search_rocq_handler(problem_file, theorem_name, call.command)
                  .using(dp.just_compute),
        },
    )
    return script


@dataclass
class ProposeProofScriptAgentic(
    dp.Query[dp.Response[ProofScript, ReadSkill | SearchRocq]]
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
