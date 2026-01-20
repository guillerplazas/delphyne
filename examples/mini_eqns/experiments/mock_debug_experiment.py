#!/usr/bin/env python3
"""
Mock Debug Experiment - Minimal experiment to debug framework issues.

Uses only 11 equations from other_htps.txt with simple config:
- Single model (gpt-4o-mini)
- Single seed (0)
- Low feedback cycles (2)
- No budget limit (to isolate variables)

To run:
    python experiments/mock_debug_experiment.py run --max_workers=1

To check status:
    python experiments/mock_debug_experiment.py status

To list all configurations:
    python experiments/mock_debug_experiment.py list
"""

from dataclasses import dataclass
from pathlib import Path

import delphyne as dp

# Use the simpler benchmark file (11 equations only)
BENCHMARKS_FOLDER = Path(__file__).parent.parent / "benchmark"
EQUATIONS_FILE = BENCHMARKS_FOLDER / "some_htps.txt"


def load_equations() -> dict[str, tuple[str, str]]:
    """
    Load equations from other_htps.txt benchmark file.
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


BENCHS = load_equations()


@dataclass
class MockConfig:
    """Configuration for mock debug experiment."""

    bench_name: str
    model_name: str
    seed: int
    max_feedback_cycles: int = 5
    temperature: float = 1.0

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        """Instantiate the configuration into a run_strategy command."""
        lhs, rhs = BENCHS[self.bench_name]

        return dp.RunStrategyArgs(
            strategy="prove_equality_interactive",
            args={"equality": [lhs, rhs]},
            policy="prove_equality_interactive_policy",
            policy_args={
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_feedback_cycles": self.max_feedback_cycles,
                "loop": False,  # No loop for debugging
            },
            num_generated=1,
            budget={},  # No budget limit to isolate variables
        )


# Minimal config: 11 equations × 1 model × 1 seed = 11 configs
configs = [
    MockConfig(
        bench_name=bench_name,
        model_name="gpt-4o",
        seed=0,
    )
    for bench_name in list(BENCHS.keys())
]


if __name__ == "__main__":
    print(f"Mock Debug Experiment: {len(configs)} configurations")
    print(f"Equations loaded from: {EQUATIONS_FILE}")
    print(f"Equation IDs: {list(BENCHS.keys())}")

    dp.Experiment(
        config_class=MockConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/output/{dp.path_stem(__file__)}",
    ).run_cli()
