"""
Canonical luna configuration on validationX — the control arm every
X-partition experiment (ACE offline/online, ablations, two-tier
policies) is paired against on the selection partition.

Pre-registered before running:

- Configuration: canonical luna + `show_definitions=True`, exactly as
  `x_train_experiment.py`; cap = `minif2f_x.X_DOLLAR_CAP`, derived on
  trainX (`make x-cap`) and confirmed in `PROGRESS.md` before this run.
- Two seeds, so that later arms are paired on 80 cells and the noise
  floor (identical configs disagree on 1–3 of 20 cells) is measured on
  this partition rather than assumed.
- Readout: solves and per-cell price; the offline cap curve
  (`tools/analysis/budget_ablation.py`) and the error taxonomy
  (`tools/analysis/failure_analysis.py`) are produced for it like for every arm.
- Expected spend ≈ $1–2.5; stop and investigate above $4.

Usage:
    python -m experiments.baselines.x_validation_experiment run --max_workers=4
"""

# pyright: strict

import experiments.common.minif2f_x as x
import experiments.common.omphalos_launch as ol

import delphyne as dp

SEEDS = (0, 1)

configs = [
    x.x_config(name, seed, max_dollar_budget=x.X_DOLLAR_CAP)
    for seed in SEEDS
    for name in x.VALIDATIONX_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=x.XAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/x_validation_agentic",
        config_naming=x.x_config_name,
    ).run_cli()
