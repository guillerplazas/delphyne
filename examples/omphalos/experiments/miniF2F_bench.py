"""
miniF2F-Rocq benchmark loader + experiment-config dataclasses.

Two configs live here:

- `StandardConfig` — the standard baseline (single-stage Hilbert,
  no tool calls). Driven by `prove_standard.py`.
- `AgenticConfig` — the agentic baseline (exploration tools +
  automation-assisted verification). Driven by `prove_agentic.py`.

Mirrors `examples/find_invariants/experiments/code2inv_experiments.py`.
"""

# pyright: strict

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import delphyne as dp

# The experiment scripts live in `experiments/`; the partition files
# and the miniF2F tree live one directory up.
_OMPHALOS_DIR = Path(__file__).resolve().parent.parent


def _parse_theorem_name(v_path: Path) -> str:
    """Best-effort: theorem name == filename stem in miniF2F-Rocq."""
    return v_path.stem


def load_partition(filename: str) -> Mapping[str, tuple[str, str]]:
    """
    Return `{theorem_name: (problem_file_relpath, theorem_name)}` for
    every line in a partition file. Paths are kept relative to the
    omphalos workspace root so the experiment is reproducible from any
    cwd.
    """
    problems: dict[str, tuple[str, str]] = {}
    partition_file = _OMPHALOS_DIR / filename
    for raw in partition_file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        abs_path = _OMPHALOS_DIR / line
        if not abs_path.exists():
            raise FileNotFoundError(f"{filename} entry missing: {abs_path}")
        thm = _parse_theorem_name(abs_path)
        problems[thm] = (line, thm)
    return problems


TRAIN_PROBLEMS: Mapping[str, tuple[str, str]] = load_partition(
    "benchmarks/train.txt"
)
"""Train: the curated 20-problem development partition (in-sample)."""

VALIDATION_PROBLEMS: Mapping[str, tuple[str, str]] = load_partition(
    "benchmarks/validation.txt"
)
"""
Validation: the tuning partition. Held out of development, but one
round of infrastructure fixes was mined from its failure traces, so it
is partly in-sample.
"""

TEST_PROBLEMS: Mapping[str, tuple[str, str]] = load_partition(
    "benchmarks/test.txt"
)
"""Test: fully out-of-sample; never used for any iteration."""

assert (
    not set(TRAIN_PROBLEMS) & set(VALIDATION_PROBLEMS)
    and not set(TRAIN_PROBLEMS) & set(TEST_PROBLEMS)
    and not set(VALIDATION_PROBLEMS) & set(TEST_PROBLEMS)
), "the benchmark partitions must be pairwise disjoint"

# Demonstration problems must never appear in any benchmark partition
# (otherwise the few-shot examples would leak solutions).
_DEMO_PROBLEMS = (
    "algebra_binomnegdiscrineq_10alt28asqp1",
    "induction_sum_odd",
    "mathd_numbertheory_136",  # probing few-shot (TryTactics workflow)
)
assert not any(
    p in s
    for p in _DEMO_PROBLEMS
    for s in (TRAIN_PROBLEMS, VALIDATION_PROBLEMS, TEST_PROBLEMS)
), "demonstration problems must not overlap with any benchmark partition"

# All problems any config may reference, keyed by theorem name.
ALL_PROBLEMS: Mapping[str, tuple[str, str]] = {
    **TRAIN_PROBLEMS,
    **VALIDATION_PROBLEMS,
    **TEST_PROBLEMS,
}


FRONTIER_MODELS: tuple[str, ...] = (
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
)
"""
The gpt-5.6 family, priciest first (see
`model_registry.OMPHALOS_PRICING`). The train experiments sweep all
three to map the cost/performance frontier; validation and test run
only the canonical model chosen from it (rule: best agentic
pass-rate-per-dollar on train, ties to the cheaper tier — see
`experiments/frontier_report.py`). Model selection is a tuning
decision, which is why it is made on train and never on test.
"""

CANONICAL_MODEL = "gpt-5.6-terra"
"""
The model every partition sweep in this file's experiments runs.

It stays gpt-5.6-terra because sixteen scripts read this constant and
their output directories are a frozen record: repointing it would send
luna configs into terra's directories and silently invalidate them.

**For new work the best known configuration is different**, measured
2026-08-13: `gpt-5.6-luna` with `toolset="lean"`,
`reasoning_effort="medium"` and `LUNA_DOLLAR_CAP`. On test it solves
16/20 for $0.288 against terra's 16/20 for $1.852 — paired per problem
they are *zero discordant*, i.e. the same sixteen solved and the same
four missed, differing only in price. It lives in
`experiments/luna_*_experiment.py`, which name the model explicitly
rather than through this constant, precisely so that the frozen sweeps
and the current recommendation cannot drift into each other.
"""

PER_PROBLEM_DOLLAR_CAP = 0.30
"""
Per-problem spend limit for the agentic baseline, as a *controlled*
variable rather than a runaway guard.

Derived on train alone (`tools/budget_ablation.py`): $0.30 is the
smallest round cap that leaves train at 20/20, because train's most
expensive success costs $0.299. Applied unchanged to the other
partitions it holds the solve count everywhere while cutting spend by
23% on validation and 41% on test ($0.318 -> $0.186 per solve) -- the
agentic baseline spends ~80% of its test budget on the six problems it
never solves, and a failed search costs up to 26x an average success
because context grows with every turn.

Note that the *request* budget cannot deliver this. Calibrated by the
same rule on the same data it comes out at 32, i.e. no saving at all:
late requests cost several times what early ones do, so a request count
is a poor proxy for spend. Picking the right budget *metric* mattered
more here than picking the right value for it.

`AgenticConfig.max_dollar_budget` still defaults to the historical
non-binding 2.0 on purpose: `Experiment` keys its stored per-config
state on the config's field values, so changing the default would
orphan every frozen run under `experiments/output`. New sweeps pass
this constant explicitly.
"""


LUNA_DOLLAR_CAP = 0.05
"""
The same rule as `PER_PROBLEM_DOLLAR_CAP`, re-derived for gpt-5.6-luna:
the smallest round cap that costs train no solves. Train's most
expensive luna success is $0.046 (`imo_1964_p1_1`), so $0.05 is it.

It is 6x tighter than terra's $0.30 for the obvious reason — luna's
tokens are 10x cheaper — and that is the point. A cap is denominated in
dollars, so it means something different for every model and after
every price change; carrying terra's number over would have left luna
effectively uncapped. See HINTS #8 and the 2026-08-13 entry, where a
price cut was measured silently loosening a fixed cap.
"""


@dataclass
class StandardConfig:
    bench_name: str
    model_name: str
    temperature: float | None
    max_feedback_cycles: int
    seed: int
    loop: bool = False
    # Safety net only, deliberately non-binding at every gpt-5.6 tier
    # (worst observed standard problem is well under this even at sol
    # rates): the feedback-cycle budget is the controlled variable.
    max_dollar_budget: float | None = 0.5

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        problem_file, theorem_name = ALL_PROBLEMS[self.bench_name]
        budget: dict[str, float] = {}
        if self.max_dollar_budget is not None:
            budget[dp.DOLLAR_PRICE] = self.max_dollar_budget
        policy_args: dict[str, Any] = {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_feedback_cycles": self.max_feedback_cycles,
            "loop": self.loop,
        }
        return dp.RunStrategyArgs(
            strategy="prove_theorem_standard",
            args={
                "problem_file": problem_file,
                "theorem_name": theorem_name,
            },
            policy="prove_theorem_standard_policy",
            policy_args=policy_args,
            budget=budget,
        )


@dataclass
class AgenticConfig:
    """
    Configuration for the agentic baseline.

    Extra knobs compared to `StandardConfig`:

    - `toolset`: `"rich"` (ReadSkill + InspectAt + TryAutomation;
      canonical), `"probing"` (rich + TryTactics candidate probing),
      or `"lean"` (ReadSkill + SearchRocq; partial proposals cover
      structural exploration).
    - `num_requests`: the *total* request budget — LLM proposal
      attempts and tool calls draw from this one pool. It is the
      binding constraint and is also surfaced to the model as the
      `turn_budget` of the proposal query.
    - `max_turns`: optional dfs depth cap on assistant turns. `None`
      (the default) leaves depth unbounded so only `num_requests` and
      `max_dollar_budget` bind.
    """

    bench_name: str
    model_name: str
    temperature: float | None
    toolset: str
    num_requests: int
    seed: int
    max_turns: int | None = None
    loop: bool = False
    # Safety net only, deliberately non-binding at every gpt-5.6 tier:
    # `num_requests` is the controlled budget variable, and a binding
    # dollar cap would handicap the expensive tiers in the frontier
    # comparison. Sized ~3x the worst per-problem spend at sol rates.
    max_dollar_budget: float | None = 2.0

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        problem_file, theorem_name = ALL_PROBLEMS[self.bench_name]
        budget: dict[str, float] = {dp.NUM_REQUESTS: float(self.num_requests)}
        if self.max_dollar_budget is not None:
            budget[dp.DOLLAR_PRICE] = self.max_dollar_budget
        policy_args: dict[str, Any] = {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_turns": self.max_turns,
            "loop": self.loop,
        }
        return dp.RunStrategyArgs(
            strategy="prove_theorem_agentic",
            args={
                "problem_file": problem_file,
                "theorem_name": theorem_name,
                "toolset": self.toolset,
                "turn_budget": self.num_requests,
            },
            policy="prove_theorem_agentic_policy",
            policy_args=policy_args,
            budget=budget,
        )


@dataclass
class ResponsesAgenticConfig(AgenticConfig):
    """
    Agentic baseline reached through the OpenAI Responses API.

    A separate dataclass rather than two more fields on `AgenticConfig`,
    because `Experiment` keys its stored per-config state on the
    config's field values (`_config_unique_repr`): adding a field, even
    with a default, changes every existing key and orphans all ten
    frozen runs under `experiments/output`.

    What it buys is the one thing Chat Completions cannot do for this
    baseline — **tools and reasoning at the same time**. Every archived
    agentic run was measured with reasoning switched off, because that
    is the price gpt-5.6 charges for function tools on Chat Completions.
    `reasoning_effort` is therefore the variable of interest here, and
    `api` exists mostly so the `"none"` arm can serve as a control that
    isolates the API change from the reasoning change.

    `convert_user_feedback_to_tool` is the second knob: it decides
    whether the verifier's feedback reaches the model as a tool result
    (keeping the reasoning cache alive across cycles) or as a plain user
    message (which invalidates it). It is a field so the feature can be
    ablated rather than assumed.
    """

    api: str = "responses"
    reasoning_effort: str | None = None
    convert_user_feedback_to_tool: bool = True

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        args = super().instantiate(context)
        args.policy_args["api"] = self.api
        args.policy_args["reasoning_effort"] = self.reasoning_effort
        args.policy_args["convert_user_feedback_to_tool"] = (
            self.convert_user_feedback_to_tool
        )
        return args


@dataclass
class ResponsesStandardConfig(StandardConfig):
    """
    Standard baseline reached through the OpenAI Responses API.

    Separate from `StandardConfig` for the same state-stability reason
    as `ResponsesAgenticConfig`.

    On paper this is where the reasoning cache should pay most, for a
    reason that has nothing to do with tools: **75-85% of this
    baseline's cost is output tokens, and 70-85% of those are reasoning
    tokens**. Chat Completions never returns reasoning items, so every
    feedback cycle makes the model re-derive its entire chain of thought
    from scratch. The Responses API can hand that state back instead.

    In practice it loses, and `use_reasoning_cache` /
    `convert_user_feedback_to_tool` are fields rather than defaults so
    that *why* can be measured. Resending reasoning items is what
    inflates input; the feedback conversion only matters once the cache
    is on. Together with `api` they give the four arms of the API
    comparison — see `experiments/baseline_api_experiment.py`.
    """

    api: str = "responses"
    reasoning_effort: str | None = None
    use_reasoning_cache: bool = True
    convert_user_feedback_to_tool: bool = True

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        args = super().instantiate(context)
        args.policy_args["api"] = self.api
        args.policy_args["reasoning_effort"] = self.reasoning_effort
        args.policy_args["use_reasoning_cache"] = self.use_reasoning_cache
        args.policy_args["convert_user_feedback_to_tool"] = (
            self.convert_user_feedback_to_tool
        )
        return args
