#!/usr/bin/env python3
"""
Mini Eqns Experiments (Baseline)

This file mirrors the structure used in `examples/find_invariants/experiments`.
It defines a small experiment harness and a simple grid of configs that you can
run with:

python experiments/baseline_experiment_simple.py run --max_workers=1

Tip: if you change the grid (models, temperatures, etc.), run:
  python experiments/baseline_experiment_simple.py clean_index
before running again to drop stale configurations from the persistent state.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
import uuid

import delphyne as dp
import delphyne.stdlib.commands as cmd
from delphyne.stdlib.experiments.experiment_launcher import (
    Experiment,
    ExperimentFun,
)

# -------------------------------------------------------
# Benchmark loading (similar spirit to code2inv.py)
# -------------------------------------------------------

MINI_EQNS_FOLDER = Path(__file__).parent.parent  # .../examples/mini_eqns
BENCHMARK_FILE = MINI_EQNS_FOLDER / "benchmark" / "htps.txt"


def _parse_eq_line(line: str) -> tuple[str, str] | None:
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    s = s.split("#", 1)[0].strip()
    s = s.replace("*1", "").strip()
    if "=" not in s:
        return None
    lhs, rhs = s.split("=", 1)
    return lhs.strip(), rhs.strip()


def load_all_equations() -> dict[str, tuple[str, str]]:
    """Load all equations as a dict mapping a stable name (001, 002, ...) to (lhs, rhs)."""
    pairs: list[tuple[str, str]] = []
    for line in BENCHMARK_FILE.read_text().splitlines():
        pr = _parse_eq_line(line)
        if pr is not None:
            pairs.append(pr)
    ret: dict[str, tuple[str, str]] = {}
    for i, (lhs, rhs) in enumerate(pairs, start=1):
        ret[f"{i:03d}"] = (lhs, rhs)
    return ret


BENCHS = load_all_equations()

# Modules and demo files required by the strategy/policy
MODULES = ["baseline_strategy_new", "checker"]
DEMO_FILES = [Path("baseline.demo.yaml")]  # relative to workspace root


# -------------------------------------------------------
# Experiment scaffolding (same API as code2inv_experiments.py)
# -------------------------------------------------------

def make_experiment[C](
    experiment: ExperimentFun[C],
    configs: Sequence[C],
    output_dir: str,
    exp_file: str,
) -> Experiment[C]:
    workspace_root = Path(exp_file).parent.parent  # .../examples/mini_eqns
    exp_name = Path(exp_file).stem
    context = dp.CommandExecutionContext(
        modules=MODULES,
        demo_files=DEMO_FILES,
    ).with_root(workspace_root)

    def _name(cfg: object, _id: uuid.UUID) -> str:  # deterministic names
        try:
            bench_name = getattr(cfg, "bench_name")
            model_name = getattr(cfg, "model_name")
            temperature = getattr(cfg, "temperature")
            mfc = getattr(cfg, "max_feedback_cycles")
            t = (
                str(temperature).rstrip("0").rstrip(".")
                if "." in str(temperature)
                else str(temperature)
            )
            return f"{bench_name}_{model_name}_T{t}_FC{mfc}"
        except Exception:
            return str(_id)

    return Experiment(
        experiment=experiment,
        context=context,
        configs=configs,
        name=exp_name,
        output_dir=workspace_root / "experiments" / output_dir / exp_name,
        config_naming=_name,
    )


# -------------------------------------------------------
# Baseline Experiment (adapted to mini-eqns baseline_strategy_new.py)
# -------------------------------------------------------

@dataclass
class BaselineConfig:
    bench_name: str
    model_name: str
    temperature: float
    max_feedback_cycles: int
    loop: bool = True
    max_dollar_budget: float | None = 0.2


def baseline_experiment(config: BaselineConfig):
    budget: dict[str, float] = {}
    if config.max_dollar_budget is not None:
        budget[dp.DOLLAR_PRICE] = config.max_dollar_budget
    lhs, rhs = BENCHS[config.bench_name]
    return cmd.RunStrategyArgs(
        strategy="prove_equality_interactive",
        args={"equality": [lhs, rhs]},  # expected Eq tuple
        policy="prove_equality_interactive_policy",
        policy_args={
            "model_name": config.model_name,  # must be a StandardModelName literal
            "temperature": config.temperature,
            "max_feedback_cycles": config.max_feedback_cycles,
            "loop": config.loop,
        },
        num_generated=1,
        budget=budget,
    )


# -------------------------------------------------------
# Default grid (keep ONLY allowed model literals)
# -------------------------------------------------------

# Allowed StandardModelName literals include: 'gpt-4o', 'gpt-4o-mini', 'o3', 'o4-mini', etc.
#SMALL = ["gpt-4o", "gpt-4o-mini"]

configs = [
    BaselineConfig(
        bench_name=bench_name,
        model_name="gpt-4o-mini",
        temperature=1.0,
        max_feedback_cycles=3,
        loop=True,
        max_dollar_budget=0.2,
    )
    for bench_name in BENCHS
]


if __name__ == "__main__":
    make_experiment(baseline_experiment, configs, "output", __file__).run_cli()
