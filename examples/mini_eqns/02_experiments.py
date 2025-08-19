""" code2inv-experiments.py

Sets up the experiments - 
1. loads the equations from the text file
    builds context


"""

"""
mini_eqns Experiments
=====================

A faithful rewrite of the Code2Inv experiment harness, but for the
trigonometric-identity dataset in examples/mini_eqns/benchmark/htps.txt.

Three things are different:

  • The dataset loader:   eqn_dataset.load_equations()
  • The strategy:         comes from baseline_strategy.py
  • Config objects:       tuned for LLM model / temperature / budget knobs
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import checker as ch
import delphyne as dp
import delphyne.stdlib.commands as cmd
from delphyne.stdlib.experiments import experiment_launcher as exp



# --------------------------------------------------------------------------
#  Repo-local helpers
# --------------------------------------------------------------------------
ROOT            = Path(__file__).resolve().parent            # examples/mini_eqns
BENCHMARK_TXT   = ROOT / "benchmark" / "htps.txt"

import sys
sys.path.append(str(ROOT))           # so we can import local modules
import _01_datapre                   # loader we wrote earlier
import baseline_strategy as bs       # your existing baseline_strategy.py

# --------------------------------------------------------------------------
#  Paths / modules for Delphyne context
# --------------------------------------------------------------------------
OUTPUT_DIR      = ROOT / "output"

STRATEGY_DIRS   = [ROOT]                         # where baseline_strategy.py lives
MODULES         = ["baseline_strategy"]          # modules to import into context
PROMPT_DIRS     = [ROOT / "prompts"]             # if you have prompt templates
DEMO_FILES      = [ROOT/"baseline.demo.yaml"]                             # add *.demo.yaml here if needed



demo_ctx = dp.DemoExecutionContext(STRATEGY_DIRS, MODULES)
context  = dp.CommandExecutionContext(
    demo_ctx,
    DEMO_FILES,
    PROMPT_DIRS,
    data_dirs           = [],
    result_refresh_period = None,
    status_refresh_period = None,
)

# --------------------------------------------------------------------------
#  Load all equations once
# --------------------------------------------------------------------------
all_eqs: list[ch.Eq] = _01_datapre .load_equations(BENCHMARK_TXT)
eq_dict                      = {f"eq{idx:02d}": eq for idx, eq in enumerate(all_eqs, 1)}
# key = friendly name ("eq01", …)  value = (lhs, rhs)

# ───────────────────────────────────────────────────────────────────────────
#  1.  Single-model “baseline” policy  (closest to Code2Inv basic policy)
# ───────────────────────────────────────────────────────────────────────────

@dataclass
class BaselineCfg:
    eq_name:          str      # key into eq_dict
    model_name:       str
    temperature:      float
    max_requests:     int
    seed:             int = 0  # not used but stored for reproducibility



def baseline_experiment(cache_dir: Path | None, cfg: BaselineCfg) -> cmd.RunStrategyArgs:
    # 1) Convert tuple[str,str]  → checker Eq object expected by baseline_strategy
    lhs, rhs = eq_dict[cfg.eq_name]
    eq_obj: ch.Eq = (lhs, rhs) #if not hasattr(ch, "parse_eq") else ch.parse_eq(f"{lhs} = {rhs}")

    # 2) Build prompting policy
    policy = bs.ask_gpt_iteratively(cfg.model_name)
    #llm = dp.openai_model(cfg.model_name)
    #policy = dp.few_shot(llm, iterative_mode=True, temperature=cfg.temperature)
    if cache_dir is not None:
        llm = dp.openai_model(cfg.model_name)
        policy = dp.few_shot(llm, iterative_mode=True, temperature=cfg.temperature, cache_dir=cache_dir,)

    # 3) Build the strategy using whatever factory the baseline file exposes
    if hasattr(bs, "make_strategy"):
        strategy = bs.make_strategy(eq_obj)             # type: ignore[arg-type]
    elif hasattr(bs, "baseline_strategy"):
        strategy = bs.baseline_strategy(eq_obj)         # type: ignore[arg-type]
    else:
        raise AttributeError("baseline_strategy.py must export make_strategy() or baseline_strategy()")

    # 4) Wrap as RunStrategyArgs for Delphyne’s stdlib runner
    return cmd.RunStrategyArgs(   # type: ignore
        strategy       = strategy,
        policy         = policy,                 # pass the object directly
        num_generated  = 1,
        budget         = {dp.NUM_REQUESTS: cfg.max_requests},
    )

def make_eqn_baseline_experiment(name: str, cfgs: Sequence[BaselineCfg]) -> exp.Experiment:
    return exp.Experiment(
        name          = name,
        dir           = OUTPUT_DIR / name,
        context       = context,
        experiment    = baseline_experiment,
        config_type   = BaselineCfg,
        configs       = cfgs,
        config_naming = lambda c, uid: f"{c.eq_name}_{c.model_name}_{uid}",
    )

# --------------------------------------------------------------------------
#  CLI helper  (identical to run_app from Code2Inv file)
# --------------------------------------------------------------------------
def run_app(experiment_obj: exp.Experiment[Any]) -> None:
    parser = argparse.ArgumentParser(description="Run mini_eqns experiment")
    # worker / export flags
    parser.add_argument("--jobs",          "-j", type=int, default=2)
    parser.add_argument("--cache-requests",        action="store_true",  default=True)
    parser.add_argument("--export-log",            action="store_true",  default=True)
    parser.add_argument("--export-raw-trace",      action="store_true",  default=False)
    parser.add_argument("--export-browsable-trace",action="store_true",  default=False)
    parser.add_argument("--cache-only",            action="store_true")
    parser.add_argument("--minimal-output",        action="store_true")
    parser.add_argument("--retry-errors",          action="store_true")
    args = parser.parse_args()

    # resolve combined flags
    if args.cache_only:
        experiment_obj.cache_requests       = True
        experiment_obj.export_log           = False
        experiment_obj.export_raw_trace     = False
        experiment_obj.export_browsable_trace = False
    elif args.minimal_output:
        experiment_obj.cache_requests       = False
        experiment_obj.export_log           = False
        experiment_obj.export_raw_trace     = False
        experiment_obj.export_browsable_trace = False
    else:
        experiment_obj.cache_requests       = args.cache_requests
        experiment_obj.export_log           = args.export_log
        experiment_obj.export_raw_trace     = args.export_raw_trace
        experiment_obj.export_browsable_trace = args.export_browsable_trace

    experiment_obj.load()
    if args.retry_errors:
        experiment_obj.mark_errors_as_todos()
    experiment_obj.resume(max_workers=args.jobs)

# --------------------------------------------------------------------------
#  Convenience entry-points
# --------------------------------------------------------------------------
if __name__ == "__main__":
    # Example: build configs that sweep temperature for all equations
    cfgs = [
        BaselineCfg(eq_name=name,
                    model_name="gpt-4o-mini",
                    temperature=temp,
                    max_requests=20,
                    seed=0)
        for name in eq_dict.keys()
        for temp in (0.0, 0.2, 0.5)
    ]
    exp_obj = make_eqn_baseline_experiment("baseline_temp_sweep", cfgs)
    run_app(exp_obj)
