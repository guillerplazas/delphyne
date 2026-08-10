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
Winner of the 2026-07-21 train frontier: 20/20 agentic at $0.056/solve
(sol: 19/20 at $0.081; luna: 15/20 at $0.126). See PROGRESS.md.
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
