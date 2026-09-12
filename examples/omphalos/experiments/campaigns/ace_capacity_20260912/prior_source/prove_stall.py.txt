"""
The agentic prover with a stall rule: a third budget mechanism.

`prove_theorem_agentic_stall` is `prove_agentic.prove_theorem_agentic`
with one difference: before each proposal request, `step` reads the
verifier verdicts the conversation prefix already carries
(`stall.views_of_prefix`) and, when `stall.stalled(views, rule, k)`
holds, returns a strategy that fails instead of the next query. A
failing `step` yields no candidate, so `dfs` ends the search with no
solution and the cell records what it spent (see `runtime/stall.py` for the
rules and why the decision lives in `step` and not in `process`: the
prefix is rebuilt from recorded actions on replay, nested `process`
bodies are not re-run).

With `stall_rule=""` the strategy is the agentic baseline's, prompt for
prompt: same query class, same templates, same verifier
(`commands/prove_one_stall.exec.yaml` replays the luna smoke's cache
under `cache_mode: replay` to prove it). The request and dollar caps
still apply on top.
"""

# pyright: strict

from typing import Any, cast

import delphyne as dp
from delphyne import Branch, Strategy, dfs, strategy
from delphyne.stdlib.nodes import Fail

import runtime.pytanque_utils as pt
import runtime.skills as sk
from runtime.model_registry import ApiType, OmphalosReasoningEffort, make_model
from prove_agentic import (
    InspectAt,
    ProposeProofScriptAgentic,
    ReadSkill,
    SearchRocq,
    Toolset,
    TryAutomation,
    TryTactics,
    _inspect_at_handler,  # pyright: ignore[reportPrivateUsage]
    _matching_toolset_examples,  # pyright: ignore[reportPrivateUsage]
    _read_skill_handler,  # pyright: ignore[reportPrivateUsage]
    _search_rocq_handler,  # pyright: ignore[reportPrivateUsage]
    _try_automation_handler,  # pyright: ignore[reportPrivateUsage]
    _try_tactics_handler,  # pyright: ignore[reportPrivateUsage]
    check_proof_assisted,
)
from prove_standard import ProofScript
from runtime.stall import Rule, stalled, views_of_prefix


@strategy
def _stall(rejections: int, rule: str, k: int) -> Strategy[Fail, object, Any]:
    """The step that ends the search: no candidate, no request."""
    yield from dp.fail(
        label="stalled",
        message=(
            f"stall rule {rule} k={k} fired after {rejections} rejected"
            " proposals"
        ),
    )
    raise AssertionError("unreachable")


def _fail_policy(_: dp.PromptingPolicy) -> dp.Policy[Fail, object]:
    return cast(dp.Policy[Fail, object], dfs() & cast(object, None))


@strategy
def prove_theorem_agentic_stall(
    problem_file: str,
    theorem_name: str,
    toolset: Toolset = "core",
    turn_budget: int = 32,
    stall_rule: str = "",
    stall_k: int = 0,
    show_definitions: bool = False,
    goal_caps: pt.GoalCaps | None = None,
) -> Strategy[Branch, dp.PromptingPolicy, ProofScript]:
    """
    `prove_theorem_agentic` plus the stall rule described in `runtime/stall.py`.

    `stall_rule` is one of `stall.RULES` (empty = off) and `stall_k`
    the run length; both are strategy arguments, hence part of every
    cell's recorded identity.
    """
    spec = pt.parse_problem(problem_file, show_definitions)
    available = sk.list_skills()
    rule = cast(Rule, stall_rule) if stall_rule else None

    def step(prefix: dp.AnswerPrefix, _: Any) -> Any:
        if rule is not None:
            views = views_of_prefix(prefix)
            if stalled(views, rule, stall_k):
                return _stall(len(views), rule, stall_k).using(_fail_policy)
        return ProposeProofScriptAgentic(
            spec, available, toolset, turn_budget, prefix
        ).using(dp.ambient_pp)

    script = yield from dp.interact(
        step=step,
        process=lambda s, _: check_proof_assisted(
            problem_file, theorem_name, s, goal_caps
        ).using(dp.just_compute),
        tools={
            ReadSkill: lambda call: _read_skill_handler(call.skill_name).using(
                dp.just_compute
            ),
            SearchRocq: lambda call: _search_rocq_handler(
                problem_file, theorem_name, call.command
            ).using(dp.just_compute),
            InspectAt: lambda call: _inspect_at_handler(
                problem_file, theorem_name, call.tactics, call.command
            ).using(dp.just_compute),
            TryAutomation: lambda call: _try_automation_handler(
                problem_file, theorem_name, call.tactics
            ).using(dp.just_compute),
            TryTactics: lambda call: _try_tactics_handler(
                problem_file,
                theorem_name,
                call.tactics,
                call.candidates,
            ).using(dp.just_compute),
        },
    )
    return script


@dp.ensure_compatible(prove_theorem_agentic_stall)
def prove_theorem_agentic_stall_policy(
    model_name: str,
    temperature: float | None = None,
    max_turns: int | None = None,
    loop: bool = False,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    convert_user_feedback_to_tool: bool = True,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    """`prove_agentic.prove_theorem_agentic_policy`, verbatim (the
    Responses default, like the ACE policies: no chat archive)."""
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
