"""
Mini Equations Experiments

Shared utilities for running experiments on trigonometric equation proofs.
Based on the structure from find_invariants/experiments/code2inv_experiments.py
"""

from dataclasses import dataclass
from pathlib import Path

import delphyne as dp


# Load benchmark equations
BENCHMARKS_FOLDER = Path(__file__).parent.parent / "benchmark"
EQUATIONS_FILE = BENCHMARKS_FOLDER / "other_htps.txt"


def load_all_equations() -> dict[str, tuple[str, str]]:
    """
    Load all equations from the benchmark file.
    Returns a dict mapping equation ID (001, 002, ...) to (lhs, rhs) tuple.
    """
    equations: list[tuple[str, str]] = []

    with open(EQUATIONS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Remove inline comments
            if "#" in line:
                line = line.split("#")[0].strip()
            # Parse equation
            if "=" in line:
                lhs, rhs = line.split("=", 1)
                equations.append((lhs.strip(), rhs.strip()))

    # Create numbered dictionary
    ret: dict[str, tuple[str, str]] = {}
    for i, (lhs, rhs) in enumerate(equations, start=1):
        ret[f"{i:03d}"] = (lhs, rhs)
    return ret


BENCHS = load_all_equations()


@dataclass
class BaselineConfig:
    """Configuration for baseline interactive proof experiments."""
    bench_name: str
    model_name: str
    temperature: float
    max_feedback_cycles: int
    seed: int
    loop: bool = False
    max_dollar_budget: float | None = 0.2

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        """
        Instantiate the configuration into a run_strategy command.
        """
        budget: dict[str, float] = {}
        if self.max_dollar_budget is not None:
            budget[dp.DOLLAR_PRICE] = self.max_dollar_budget

        lhs, rhs = BENCHS[self.bench_name]

        return dp.RunStrategyArgs(
            strategy="prove_equality_interactive",
            args={"equality": [lhs, rhs]},
            policy="prove_equality_interactive_policy",
            policy_args={
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_feedback_cycles": self.max_feedback_cycles,
                "loop": self.loop,
            },
            num_generated=1,
            budget=budget,
        )