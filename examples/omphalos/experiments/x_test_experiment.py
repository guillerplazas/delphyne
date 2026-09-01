"""
Canonical luna configuration on testX — the baseline's one look at the
clean partition.

Pre-registered before running:

- Configuration and cap exactly as `x_validation_experiment.py`.
- One seed, deliberately: extra seeds would be extra looks at the
  partition whose value is that each arm sees it once. Variance is
  characterised on trainX and validationX.
- testX is looked at by exactly three arms — this baseline, ACE offline,
  and the one online ACE variant selected on validationX — and its
  failures are never read to change a prompt, playbook or policy.
- Expected spend ≈ $0.5–1.2; stop and investigate above $2.

Usage:
    python experiments/x_test_experiment.py run --max_workers=4
"""

# pyright: strict

import minif2f_x as x
import omphalos_launch as ol

import delphyne as dp

SEEDS = (0,)

configs = [
    x.x_config(name, seed, max_dollar_budget=x.X_DOLLAR_CAP)
    for seed in SEEDS
    for name in x.TESTX_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=x.XAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/x_test_agentic",
        config_naming=x.x_config_name,
    ).run_cli()
