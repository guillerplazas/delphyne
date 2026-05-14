"""
miniF2F-Rocq benchmark loader + experiment-config dataclasses.

Two configs live here:

- `StandardConfig` — the standard baseline (single-stage Hilbert,
  no tool calls). Driven by `prove_standard.py`.
- `AgenticConfig` — the agentic baseline (LLM may call `ReadSkill`
  before / between proof attempts). Driven by `prove_agentic.py`.

Mirrors `examples/find_invariants/experiments/code2inv_experiments.py`.
"""

# pyright: strict

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import delphyne as dp

# The experiment scripts live in `experiments/`; the dev subset and the
# miniF2F tree live one directory up.
_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
_DEV_SUBSET_FILE = _OMPHALOS_DIR / "dev_subset.txt"


def _parse_theorem_name(v_path: Path) -> str:
    """Best-effort: theorem name == filename stem in miniF2F-Rocq."""
    return v_path.stem


def load_dev_subset() -> Mapping[str, tuple[str, str]]:
    """
    Return `{theorem_name: (problem_file_relpath, theorem_name)}` for
    every line in `dev_subset.txt`. Paths are kept relative to the
    omphalos workspace root so the experiment is reproducible from any
    cwd.
    """
    problems: dict[str, tuple[str, str]] = {}
    for raw in _DEV_SUBSET_FILE.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        abs_path = _OMPHALOS_DIR / line
        if not abs_path.exists():
            raise FileNotFoundError(f"dev_subset entry missing: {abs_path}")
        thm = _parse_theorem_name(abs_path)
        problems[thm] = (line, thm)
    return problems


PROBLEMS: Mapping[str, tuple[str, str]] = load_dev_subset()


@dataclass
class StandardConfig:
    bench_name: str
    model_name: str
    temperature: float | None
    max_feedback_cycles: int
    seed: int
    loop: bool = False
    max_dollar_budget: float | None = 0.2

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        problem_file, theorem_name = PROBLEMS[self.bench_name]
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

    Extra knob: `num_requests` is the *total* request budget — covers
    both LLM proposal attempts and tool calls combined.
    """

    bench_name: str
    model_name: str
    temperature: float | None
    max_feedback_cycles: int
    num_requests: int
    seed: int
    loop: bool = False
    max_dollar_budget: float | None = 0.4

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        problem_file, theorem_name = PROBLEMS[self.bench_name]
        budget: dict[str, float] = {dp.NUM_REQUESTS: float(self.num_requests)}
        if self.max_dollar_budget is not None:
            budget[dp.DOLLAR_PRICE] = self.max_dollar_budget
        policy_args: dict[str, Any] = {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_feedback_cycles": self.max_feedback_cycles,
            "loop": self.loop,
        }
        return dp.RunStrategyArgs(
            strategy="prove_theorem_agentic",
            args={
                "problem_file": problem_file,
                "theorem_name": theorem_name,
            },
            policy="prove_theorem_agentic_policy",
            policy_args=policy_args,
            budget=budget,
        )
