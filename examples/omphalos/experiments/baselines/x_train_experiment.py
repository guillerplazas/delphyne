"""
Canonical luna configuration on trainX, under a loose cap — the
baseline that every X-partition arm is paired against, and the sweep
the X dollar cap is derived from.

Pre-registered before running:

- Configuration: `gpt-5.6-luna`, `core`, `reasoning_effort="medium"`,
  Responses API, 32 requests, `show_definitions=True` — the canonical
  configuration plus the definitions fix, which is on from the first
  X-partition run so that it is never an A/B here (its effect was
  measured separately: `experiments/ablations/defs_experiment.py`).
- Cap: `X_LOOSE_CAP` ($0.10), deliberately loose so `tools/
  budget_ablation.py` can read the shipping cap off the recorded
  per-request prices afterwards (`make x-cap`): the smallest round cap
  that costs trainX no solves becomes `minif2f_x.X_DOLLAR_CAP`.
- Two seeds. `seed` does not seed the provider — sampling is
  nondeterministic regardless — it distinguishes independent repeats,
  and two of them per problem are what put a noise floor under every
  later pairing on this partition.
- Primary readout: solves per cell and the per-cell price distribution
  (median solved cell, dearest solved cell). No comparison is made
  here; this run defines the baseline.
- Expected spend: 80 cells at ≤ $0.10, most far below; ≈ $1.5–3.
  Stop and investigate above $5.

Usage:
    python -m experiments.baselines.x_train_experiment run --max_workers=4
"""

# pyright: strict

import experiments.common.minif2f_x as x
import experiments.common.omphalos_launch as ol

import delphyne as dp

SEEDS = (0, 1)

configs = [
    x.x_config(name, seed, max_dollar_budget=x.X_LOOSE_CAP)
    for seed in SEEDS
    for name in x.TRAINX_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=x.XAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/x_train_agentic",
        config_naming=x.x_config_name,
    ).run_cli()
