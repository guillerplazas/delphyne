"""
Canonical luna configuration on ladonX — the control arm every Ladon
arm is paired against (`ladon/README.md`).

Pre-registered before running:

- Configuration and cap exactly as `x_validation_experiment.py`:
  canonical luna + `show_definitions=True`, `minif2f_x.X_DOLLAR_CAP`.
- Two seeds, so that Ladon arms are paired on 80 cells and the noise
  floor (identical configs disagree on 1–3 of 20 cells) is measured on
  this partition rather than assumed.
- Frozen once run: Ladon's guard refuses any change to this file or to
  its output directory. A change of the canonical configuration means
  a new baseline directory, never an edit of this one.
- Expected spend ≈ $1–2.5; stop and investigate above $4.

Ladon's preflight launches this itself when the directory is not
complete; it can also be run by hand:

    python -m experiments.ladon.x_ladon_experiment run --max_workers=4 --wait
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict


import experiments.common.omphalos_launch as ol  # noqa: E402

import delphyne as dp  # noqa: E402
from ladon import bench  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT

SEEDS = (0, 1)

configs = [
    bench.ladon_config(name, seed)
    for seed in SEEDS
    for name in bench.LADONX_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=bench.LadonConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=bench.BASELINE_DIR,
        config_naming=bench.config_name,
    ).run_cli()
