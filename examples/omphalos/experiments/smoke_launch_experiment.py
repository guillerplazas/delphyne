"""
Smoke launch for the launch layer: four cheap canonical cells, real
API calls (~$0.05 in total), into `experiments/output/_smoke_launch`.

Purpose: exercise `OmphalosExperiment` end to end — lock, slots,
supervised attempt, per-worker limits, status rebuild — including the
chaos drill of `kill -9`-ing a pool worker mid-run and watching the
attempt fail, the group get killed, completed cells stay done and the
retry finish the rest. Problems are trainX cells the baseline solves
cheaply on both seeds, so the run is short.

Usage:
    python experiments/smoke_launch_experiment.py run --max_workers=2
    python experiments/smoke_launch_experiment.py status
"""

# pyright: strict

import minif2f_x as x
import omphalos_launch as ol

import delphyne as dp

PROBLEMS = (
    "mathd_algebra_190",
    "mathd_numbertheory_284",
    "amc12a_2013_p8",
    "mathd_algebra_141",
)

configs = [
    x.x_config(name, 0, max_dollar_budget=x.X_DOLLAR_CAP)
    for name in PROBLEMS
    if name in x.ALL_X_PROBLEMS
]


if __name__ == "__main__":
    assert len(configs) >= 2, "smoke problems must be X-partition problems"
    ol.OmphalosExperiment(
        config_class=x.XAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/_smoke_launch",
        config_naming=x.x_config_name,
    ).run_cli()
