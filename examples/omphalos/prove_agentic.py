"""
Agentic baseline for Rocq theorem proving in miniF2F.

Same outer loop as `prove_standard.py` (an LLM proposes a proof script,
pytanque verifies it, the verifier's feedback is fed back for revision),
but the LLM has *exploration* tools available alongside proposing:

  - `ReadSkill(skill_name=...)` loads a curated Rocq skill markdown
    file from `rocq_skills_data/` into the chat history.
  - `SearchRocq(command=...)` runs a Rocq introspection command
    (`Search ...`, `Check ...`, `Print ...`, `About ...`,
    `SearchPattern ...`) against the problem's initial proof state via
    pytanque, and returns the formatted feedback.
  - `TryTactic(tactics=...)` previews the effect of a tactic prefix on
    the theorem's initial proof state, returning the resulting goals or
    the failing tactic + Rocq error. Pytanque's `client.run` is
    functional — the original state stays valid — so this is a true
    preview, not a commit.

Two toolsets are exposed behind the `toolset` strategy argument:

  - `"full"` — all three tools.
  - `"lean"` — `ReadSkill` + `SearchRocq` only. Structural exploration
    happens through *partial proposals* instead: `check_proof` reports
    the verified prefix and the remaining goals whenever a script
    applies cleanly without closing the goal, so a proposal doubles as
    a preview (and wins outright if it happens to close the goal).

Budgeting: every assistant turn (tool round or proposal) costs one LLM
request. The policy deliberately leaves search depth unbounded by
default (`max_turns=None`) so that the *request budget* (`num_requests`
at the experiment level) is the binding constraint — tool calls and
proposals draw from one pool, and exploring does not eat a separate,
scarcer "feedback cycle" allowance. `turn_budget` mirrors that request
budget into the system prompt so the model knows what it is spending.

Reuses `ProofScript` and `check_proof` verbatim from `prove_standard`.
"""

from dataclasses import dataclass
from typing import Literal

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy

import pytanque_utils as pt
import skills as sk
from prove_standard import ProofScript, check_proof

# fmt: off


type Toolset = Literal["full", "lean"]
"""
Which exploration tools the LLM is offered: `"full"` advertises
`ReadSkill`, `SearchRocq` and `TryTactic`; `"lean"` drops `TryTactic`
(partial proposals cover structural exploration instead).
"""


#####
##### Tools
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


@dataclass
class TryTactic(dp.AbstractTool[str]):
    """
    Preview the effect of applying a tactic (or short tactic prefix) to
    the theorem's *initial* proof state, WITHOUT committing. Useful for
    comparing several structural openers (`induction n.` vs
    `destruct n.`) before drafting a full script.

    Pass `tactics` as a Rocq proof body — one or more tactics, each
    terminated with `.`. The tool replays them in order from the
    theorem's initial state and returns:

      - the resulting goal(s) if every tactic succeeded;
      - "PROOF FINISHED" plus the closing tactics if the prefix
        actually closes the goal (then emit them verbatim as your
        final proof);
      - the failing tactic + Rocq error if any step fails, along with
        the prefix that did succeed.

    The pytanque session is fresh per call — there is NO shared state
    between invocations, so include any prerequisite tactics (e.g.
    `intros n.`) in every preview. Note that *proposing* a partial
    script returns the same information through the verifier, and a
    proposal that closes the goal finishes the job on the spot — so
    prefer a proposal unless you specifically want to compare
    alternatives before committing to one.
    """
    tactics: str


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
def _try_tactic_handler(
    problem_file: str, theorem_name: str, tactics: str,
) -> Strategy[Compute, object, str]:
    """Wraps pt.try_tactic so the TryTactic handler returns a StrategyInstance."""
    text = yield from dp.compute(pt.try_tactic)(problem_file, theorem_name, tactics)
    return text


@strategy
def prove_theorem_agentic(
    problem_file: str,
    theorem_name: str,
    toolset: Toolset = "lean",
    turn_budget: int = 16,
) -> Strategy[Branch, dp.PromptingPolicy, ProofScript]:
    spec = pt.parse_problem(problem_file)
    available = sk.list_skills()
    script = yield from dp.interact(
        step=lambda prefix, _:
            ProposeProofScriptAgentic(
                spec, available, toolset, turn_budget, prefix
            ).using(dp.ambient_pp),
        process=lambda s, _:
            check_proof(problem_file, theorem_name, s).using(dp.just_compute),
        tools={
            ReadSkill: lambda call:
                _read_skill_handler(call.skill_name).using(dp.just_compute),
            SearchRocq: lambda call:
                _search_rocq_handler(problem_file, theorem_name, call.command)
                  .using(dp.just_compute),
            # Never advertised under the "lean" toolset (see the
            # query's `parser` method), so the handler is just unused
            # dead weight there.
            TryTactic: lambda call:
                _try_tactic_handler(problem_file, theorem_name, call.tactics)
                  .using(dp.just_compute),
        },
    )
    return script


@dataclass
class ProposeProofScriptAgentic(
    dp.Query[dp.Response[ProofScript, ReadSkill | SearchRocq | TryTactic]]
):
    spec: pt.ProblemSpec
    available_skills: dict[str, str]
    toolset: Toolset
    turn_budget: int
    prefix: dp.AnswerPrefix

    def parser(self) -> dp.Parser[
        dp.Response[ProofScript, ReadSkill | SearchRocq | TryTactic]
    ]:
        # The advertised toolset depends on the query instance, hence
        # a `parser` method instead of a `__parser__` class attribute.
        if self.toolset == "lean":
            return dp.last_code_block.response_with(ReadSkill | SearchRocq)
        return dp.last_code_block.response_with(
            ReadSkill | SearchRocq | TryTactic
        )


#####
##### Policy
#####


def prove_theorem_agentic_policy(
    model_name: str,
    temperature: float | None = None,
    max_turns: int | None = None,
    loop: bool = False,
):
    """
    Policy for the agentic baseline.

    `max_turns` bounds the number of assistant turns (tool rounds +
    proposals) via dfs depth. The default `None` leaves depth unbounded
    so that the request budget (`num_requests` passed at the experiment
    level) is the binding constraint instead — this keeps tool calls
    from eating into a separate, scarcer proposal allowance.
    """
    model = dp.standard_model(model_name)
    sp = dfs(max_depth=max_turns)
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(model, temperature=temperature, max_requests=1)
    return sp & pp
