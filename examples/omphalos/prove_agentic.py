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
  - `InspectAt(tactics=..., command=...)` replays a tactic prefix
    (without committing) and runs an introspection command *at the
    resulting state* — so `Search` sees the hypotheses (including
    induction hypotheses) of the actual stuck subgoal. With an empty
    `command` it just reports the goals after the prefix; with empty
    `tactics` it inspects the initial state (subsuming `SearchRocq`).
  - `TryAutomation(tactics=...)` replays a prefix, then tries a battery
    of cheap closing tactics (`lia`, `nra`, `ring`, ...) on *each*
    remaining subgoal and reports which subgoal closes with what. One
    request buys dozens of Rocq attempts.
  - `TryTactics(tactics=..., candidates=[...])` replays a prefix, then
    evaluates up to 20 *model-chosen* candidate tactics independently
    against that same held state, in one call and without committing
    anything — the model-directed generalization of `TryAutomation`
    for comparing structural moves (openers, rewrites, asserts).

Three toolsets are exposed behind the `toolset` strategy argument:

  - `"core"` — `ReadSkill` + `SearchRocq`. Structural exploration
    happens through *partial proposals*: `check_proof` reports the
    verified prefix and the remaining goals whenever a script applies
    cleanly without closing the goal, so a proposal doubles as a
    preview (and wins outright if it happens to close the goal).
  - `"rich"` — `ReadSkill` + `InspectAt` + `TryAutomation`
    (`InspectAt` with an empty prefix subsumes `SearchRocq`, so the
    latter is not advertised separately).
  - `"probing"` — `"rich"` + `TryTactics` (candidate probing).

Budgeting: every assistant turn (tool round or proposal) costs one LLM
request. The policy deliberately leaves search depth unbounded by
default (`max_turns=None`) so that the *request budget* (`num_requests`
at the experiment level) is the binding constraint — tool calls and
proposals draw from one pool, and exploring does not eat a separate,
scarcer "feedback cycle" allowance. `turn_budget` mirrors that request
budget into the system prompt so the model knows what it is spending.

Verification on the agentic side is *automation-assisted*
(`check_proof_assisted`): when a proposal fails or leaves goals open,
the verifier probes each remaining goal with `pt.AUTOMATION_BATTERY`
and reports the closers in the feedback — and if every remaining goal
closes, it finishes the proof itself. The standard baseline keeps the
plain `check_proof`.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy
from delphyne.stdlib.queries import SelectedExample

import pytanque_utils as pt
import skills as sk
from model_registry import ApiType, OmphalosReasoningEffort, make_model
from prove_standard import ProofScript

# fmt: off


type Toolset = Literal["core", "rich", "probing"]
"""
Which exploration tools the LLM is offered: `"core"` advertises
`ReadSkill` + `SearchRocq`; `"rich"` advertises `ReadSkill` +
`InspectAt` + `TryAutomation` (state-level introspection and
automation probing); `"probing"` extends `"rich"` with `TryTactics`
(model-chosen candidate probing at a held state).
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
class InspectAt(dp.AbstractTool[str]):
    """
    Replay a tactic prefix from the theorem's initial proof state
    (WITHOUT committing — every call starts from scratch), then run an
    optional Rocq introspection command at the resulting state.

    This is the precise way to work on a stuck subgoal: after
    `intros ... induction ...`, the hypotheses of that subgoal
    (including the induction hypothesis) are in scope, so
    `Search (...)` matches lemmas relevant to where you actually are,
    not to the pristine initial goal.

    Arguments:
    - `tactics`: tactic prefix to replay, each tactic ending with `.`.
      Empty string = inspect the initial state.
    - `command`: introspection command (`Search ...`, `Check ...`,
      `Print ...`, `About ...`, `SearchPattern ...`) to run at the
      resulting state. Empty string = just report the goals there.

    Returns the command output plus the goals at that state, or
    `PROOF FINISHED` if the prefix closes the goal (then submit it!),
    or the failing tactic + Rocq error if the prefix breaks.
    """
    tactics: str
    command: str = ""


@dataclass
class TryAutomation(dp.AbstractTool[str]):
    """
    Replay a tactic prefix from the theorem's initial proof state
    (WITHOUT committing), then try a battery of cheap closing tactics
    (`assumption`, `reflexivity`, `easy`, `lia`, `nia`, `lra`, `nra`,
    `ring`, `field`, `congruence`, `auto with arith/zarith`, and
    `simpl`/`intuition` combinations) on EACH remaining subgoal
    separately. The same battery is what the verifier uses to finish
    your proposals, so a goal reported as closing here will also close
    when you submit the prefix.

    Returns, per subgoal, either `CLOSED by <tactic>` or the subgoal
    that no battery tactic closes. If everything closes, the report
    includes a ready-to-submit script. One call costs one request but
    buys dozens of Rocq attempts — ideal right after choosing a
    structural opener (`induction ...`, `destruct ...`, asserts) to
    learn which cases are routine and which need real work.

    Pass `tactics` as the prefix to replay (each tactic ending with
    `.`); an empty string probes the initial goal directly.
    """
    tactics: str


@dataclass
class TryTactics(dp.AbstractTool[str]):
    """
    Replay a tactic prefix from the theorem's initial proof state
    (WITHOUT committing), then evaluate up to 20 candidate tactics YOU
    choose, each independently against that same held state, in ONE
    call. Use it to compare *structural* moves — alternative openers,
    competing rewrites, bridging asserts, different witnesses — before
    spending a proposal on one.

    Arguments:
    - `tactics`: prefix to replay, each sentence ending with `.`.
      Empty string = probe the initial state.
    - `candidates`: candidate tactics (max 20). A candidate may be a
      short sequence (`"intros n. induction n."`) and acts on the
      WHOLE proof state, so goal selectors (`"2: lia."`) are legal.

    Returns one block per candidate: the Rocq error, `PROOF FINISHED`,
    or the goal-count change plus the first resulting goal.

    Discipline (one call costs one request, same as a proposal):
    - BATCH: send 6-15 varied candidates per call. Several calls with
      2-3 candidates each waste requests; never re-probe the same
      prefix with a small variation of a failed batch — vary more, or
      extend the prefix with a winner and probe deeper.
    - Real names first: if candidates depend on stdlib lemma names,
      discover them with `InspectAt` + `Search` before probing;
      guessed names are the top cause of all-fail reports.
    - Don't probe bare closers (`lia.`, `nra.`, ...): the verifier and
      `TryAutomation` already try the closing battery for free.
    """
    tactics: str
    candidates: list[str]


#####
##### Strategy
#####


@strategy
def check_proof_assisted(
    problem_file: str,
    theorem_name: str,
    script: ProofScript,
    goal_caps: pt.GoalCaps | None = None,
) -> Strategy[Compute, object, ProofScript | dp.Error]:
    """
    Automation-assisted variant of `prove_standard.check_proof`: when
    the script fails or leaves goals open, the verifier probes each
    remaining goal with `pt.AUTOMATION_BATTERY` (probe results are
    rendered into the feedback), and if every goal closes it finishes
    the proof itself and succeeds with the assembled script.

    `goal_caps` (the pre-registered runaway-goal treatment, see
    `pt.GoalCaps`) is forwarded to the verifier only when set: the
    compute request of every archived cell keeps its exact arguments,
    hence its cache key.
    """
    tactics = yield from dp.compute(pt.split_into_tactics)(script)
    if goal_caps is None:
        feedback = yield from dp.compute(pt.check_assisted)(
            problem_file, theorem_name, tactics
        )
    else:
        feedback = yield from dp.compute(pt.check_assisted)(
            problem_file, theorem_name, tactics, goal_caps=goal_caps
        )
    if feedback.success:
        if feedback.auto_finished:
            return "\n".join(feedback.proof_so_far)
        return script
    if feedback.failing_tactic == "Qed." and feedback.remaining_goals:
        return dp.Error(label="incomplete", meta=feedback)
    return dp.Error(label="feedback", meta=feedback)


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
def _inspect_at_handler(
    problem_file: str, theorem_name: str, tactics: str, command: str,
) -> Strategy[Compute, object, str]:
    """Wraps pt.inspect_at so the InspectAt handler returns a StrategyInstance."""
    text = yield from dp.compute(pt.inspect_at)(
        problem_file, theorem_name, tactics, command
    )
    return text


@strategy
def _try_automation_handler(
    problem_file: str, theorem_name: str, tactics: str,
) -> Strategy[Compute, object, str]:
    """Wraps pt.try_automation so the TryAutomation handler returns a StrategyInstance."""
    text = yield from dp.compute(pt.try_automation)(
        problem_file, theorem_name, tactics
    )
    return text


@strategy
def _try_tactics_handler(
    problem_file: str, theorem_name: str,
    tactics: str, candidates: list[str],
) -> Strategy[Compute, object, str]:
    """Wraps pt.try_tactics so the TryTactics handler returns a StrategyInstance."""
    text = yield from dp.compute(pt.try_tactics)(
        problem_file, theorem_name, tactics, candidates
    )
    return text


@strategy
def prove_theorem_agentic(
    problem_file: str,
    theorem_name: str,
    toolset: Toolset = "rich",
    turn_budget: int = 16,
    show_definitions: bool = False,
    goal_caps: pt.GoalCaps | None = None,
) -> Strategy[Branch, dp.PromptingPolicy, ProofScript]:
    # `goal_caps` is the runaway-goal treatment (`pt.GoalCaps`): off by
    # default, and never part of a compute request unless set.
    # `show_definitions` renders the problem file's pre-theorem
    # declarations (`Definition`/`Fixpoint`/`Notation`/...) in their own
    # prompt section. It defaults to False so every archived run keeps
    # its exact prompt (and therefore its cache); see
    # `pytanque_utils._preamble_definitions` for why the omission
    # matters. New pipelines (`experiments/minif2f_x.py`) turn it on.
    spec = pt.parse_problem(problem_file, show_definitions)
    available = sk.list_skills()
    script = yield from dp.interact(
        step=lambda prefix, _:
            ProposeProofScriptAgentic(
                spec, available, toolset, turn_budget, prefix
            ).using(dp.ambient_pp),
        process=lambda s, _:
            check_proof_assisted(problem_file, theorem_name, s, goal_caps)
              .using(dp.just_compute),
        # Only the tools advertised by the query's `parser` (which
        # depends on `toolset`) can ever be called; the rest of this
        # mapping is dead weight for the non-matching toolset.
        tools={
            ReadSkill: lambda call:
                _read_skill_handler(call.skill_name).using(dp.just_compute),
            SearchRocq: lambda call:
                _search_rocq_handler(problem_file, theorem_name, call.command)
                  .using(dp.just_compute),
            InspectAt: lambda call:
                _inspect_at_handler(
                    problem_file, theorem_name, call.tactics, call.command
                ).using(dp.just_compute),
            TryAutomation: lambda call:
                _try_automation_handler(
                    problem_file, theorem_name, call.tactics
                ).using(dp.just_compute),
            TryTactics: lambda call:
                _try_tactics_handler(
                    problem_file, theorem_name,
                    call.tactics, call.candidates,
                ).using(dp.just_compute),
        },
    )
    return script


@dataclass
class ProposeProofScriptAgentic(
    dp.Query[
        dp.Response[
            ProofScript | dp.WrappedParseError,
            ReadSkill | SearchRocq | InspectAt | TryAutomation
            | TryTactics,
        ]
    ]
):
    spec: pt.ProblemSpec
    available_skills: dict[str, str]
    toolset: Toolset
    turn_budget: int
    prefix: dp.AnswerPrefix = ()

    def parser(self) -> dp.Parser[
        dp.Response[
            ProofScript | dp.WrappedParseError,
            ReadSkill | SearchRocq | InspectAt | TryAutomation
            | TryTactics,
        ]
    ]:
        # The advertised toolset depends on the query instance, hence
        # a `parser` method instead of a `__parser__` class attribute.
        # `wrap_errors` is essential: without it, a single malformed
        # reply (no code block) raises instead of becoming feedback,
        # killing the whole run on the spot.
        parser = dp.last_code_block.wrap_errors
        if self.toolset == "core":
            return parser.response_with(ReadSkill | SearchRocq)
        if self.toolset == "probing":
            return parser.response_with(
                ReadSkill | InspectAt | TryAutomation | TryTactics
            )
        return parser.response_with(ReadSkill | InspectAt | TryAutomation)

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        """
        Tool classes advertised to the LLM, derived from the parser so
        there is a single source of truth. The system prompt template
        iterates over this to render one section per available tool
        (from its docstring), adapting automatically to the toolset.
        """
        tools = self.parser().settings.tools
        return tools.tool_types if tools is not None else []


#####
##### Policy
#####


def _matching_toolset_examples() -> dp.ExampleSelector:
    """
    Example selector for the agentic proposal query.

    Toolset-neutral examples (empty `prefix` — plain proposal
    demonstrations) are kept for every toolset; tool-workflow examples
    (non-empty `prefix`, which renders as real tool-call/tool-result
    messages) are kept only when their pinned `toolset` matches the
    input query's. This lets `"probing"` carry a TryTactics workflow
    example without perturbing the `"rich"`/`"core"` prompts (which
    must stay byte-identical to their frozen benchmark runs).
    """
    def select(
        env: dp.PolicyEnv,
        query: dp.AbstractQuery[Any],
        examples: Sequence[SelectedExample],
    ) -> Sequence[SelectedExample]:
        kept: list[SelectedExample] = []
        for ex in examples:
            exq = ex.example.query
            if not isinstance(exq, ProposeProofScriptAgentic):
                kept.append(ex)
            elif not exq.prefix:
                kept.append(ex)
            elif (
                isinstance(query, ProposeProofScriptAgentic)
                and exq.toolset == query.toolset
            ):
                kept.append(ex)
        return kept

    return dp.all_examples.filter(select)


@dp.ensure_compatible(prove_theorem_agentic)
def prove_theorem_agentic_policy(
    model_name: str,
    temperature: float | None = None,
    max_turns: int | None = None,
    loop: bool = False,
    api: ApiType = "chat_completions",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    convert_user_feedback_to_tool: bool = True,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    """
    Policy for the agentic baseline.

    `max_turns` bounds the number of assistant turns (tool rounds +
    proposals) via dfs depth. The default `None` leaves depth unbounded
    so that the request budget (`num_requests` passed at the experiment
    level) is the binding constraint instead — this keeps tool calls
    from eating into a separate, scarcer proposal allowance.

    `api="responses"` is the only way to give this policy a reasoning
    model. On Chat Completions the gpt-5.6 family rejects function tools
    unless reasoning is switched off entirely, so every archived agentic
    number was measured with `reasoning_effort="none"` — the baseline
    has never been evaluated with reasoning on, against a standard
    baseline that always had it. See `model_registry.make_model`.

    `convert_user_feedback_to_tool` is exposed so the feature can be
    ablated: it is what keeps the reasoning cache alive across
    verification rounds, and it is the part of the Responses migration
    most likely to change behaviour, since the model then sees verifier
    feedback as a tool result rather than as a user message.

    `tag_user_feedback_messages` is gated on the API rather than always
    set: the flag is part of the hashed `LLMRequest`, so setting it
    unconditionally would invalidate every archived cache and make the
    frozen benchmark runs unreplayable.
    """
    model = make_model(
        model_name,
        for_tool_calls=True,
        api=api,
        reasoning_effort=reasoning_effort,
        convert_user_feedback_to_tool=convert_user_feedback_to_tool,
    )
    sp = dfs(max_depth=max_turns)
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(
        model,
        temperature=temperature,
        max_requests=1,
        select_examples=_matching_toolset_examples(),
        tag_user_feedback_messages=(api == "responses"),
    )
    return sp & pp
