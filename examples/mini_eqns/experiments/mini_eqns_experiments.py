"""
Mini Equations Experiments

Shared utilities for running experiments on trigonometric equation proofs.
Based on the structure from find_invariants/experiments/code2inv_experiments.py
"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import delphyne as dp
import delphyne.stdlib.commands as cmd
from delphyne.stdlib.experiments.experiment_launcher import (
    Experiment,
    ExperimentFun,
)


# Load benchmark equations
BENCHMARKS_FOLDER = Path(__file__).parent.parent / "benchmark"
EQUATIONS_FILE = BENCHMARKS_FOLDER / "some_htps.txt"


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
MODULES = ["baseline_interactive", "checker"]
DEMO_FILES = ["baseline_interactive"]  # String names, not Path objects


def make_experiment[C](
    experiment: ExperimentFun[C],
    configs: Sequence[C],
    output_dir: str,
    exp_file: str,
) -> Experiment[C]:
    """
    Create an experiment with the given configuration.

    Args:
        experiment: The experiment function to run
        configs: List of configurations to test
        output_dir: Output directory name
        exp_file: The experiment file path (__file__)
    """
    workspace_root = Path(exp_file).parent.parent  # .../examples/mini_eqns
    exp_name = Path(exp_file).stem
    context = dp.CommandExecutionContext(
        modules=MODULES,
        demo_files=DEMO_FILES,
    ).with_root(workspace_root)

    # Define a naming function for configurations
    def config_naming(cfg: object, _id: object) -> str:
        """Generate a descriptive name for each configuration."""
        try:
            bench_name = getattr(cfg, "bench_name", "unknown")
            model_name = getattr(cfg, "model_name", "unknown")
            temperature = getattr(cfg, "temperature", 0.0)
            max_feedback = getattr(cfg, "max_feedback_cycles", 0)
            seed = getattr(cfg, "seed", 0)
            # Format temperature nicely
            temp_str = str(temperature).rstrip("0").rstrip(".") if temperature else "0"
            return f"{bench_name}_{model_name}_T{temp_str}_FC{max_feedback}_S{seed}"
        except Exception:
            return str(_id)

    return Experiment(
        experiment=experiment,
        context=context,
        configs=configs,
        name=exp_name,
        output_dir=workspace_root / "experiments" / output_dir / exp_name,
        config_naming=config_naming,
    )


#####
##### Baseline Interactive Experiment
#####


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


def baseline_experiment(config: BaselineConfig) -> cmd.RunStrategyArgs:
    """
    Run the baseline interactive proof strategy on a benchmark equation.

    Args:
        config: The experiment configuration

    Returns:
        RunStrategyArgs for the experiment
    """
    budget: dict[str, float] = {}
    if config.max_dollar_budget is not None:
        budget[dp.DOLLAR_PRICE] = config.max_dollar_budget

    lhs, rhs = BENCHS[config.bench_name]

    return cmd.RunStrategyArgs(
        strategy="prove_equality_interactive",
        args={"equality": [lhs, rhs]},
        policy="prove_equality_interactive_policy",
        policy_args={
            "model_name": config.model_name,
            "temperature": config.temperature,
            "max_feedback_cycles": config.max_feedback_cycles,
            "loop": config.loop,
        },
        num_generated=1,
        budget=budget,
    )