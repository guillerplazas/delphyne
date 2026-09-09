"""
The canonical luna configuration with a stall rule, on validationX.

Pre-registration (2026-09-06, before any cell ran). The stall rule and
its `k` come from `tools/reports/stall_report.py --tune x_train_agentic` (the
grid and the selection are recorded in `experiments/output/stall/
tune_trainX.json`): `seenstate k=4` — stop after four consecutive
rejections whose (class, goal count, first conclusion) state was
already seen in the cell. Its exact effect on validationX and ladonX is
already known from the replay of the recorded baselines (validationX:
54 → 53 solves, spend −7 %; ladonX: 56 → 56, −13 %); this live arm
exists to prove the implementation, not to measure the effect.

- **Primary = parity**: `tools/reports/stall_report.py --rule seenstate --k 4
  --parity <this directory>` must report no violation — every live
  cell stops exactly where the replay of its own verdicts says
  (proposal count and no billed request after the stop).
- **Secondary**: paired spend and solves against the baseline's cells
  (`x_validation_agentic`, same seed), expected to reproduce the exact
  replay within the 1–3-cell run-to-run noise; `prover-crash` rate.
- Seed 0 only (`--seeds=0`); seed 1 is not needed for the measurement.

`STALL_SMOKE=1` runs three trainX cells first (two the rule stops in
the recorded baseline, one cheap solve) into `<dir>_smoke`.

Usage:
    STALL_SMOKE=1 python -m experiments.ablations.x_stall_experiment --seeds=0 \\
        run --max_workers=2 --wait
    python -m experiments.ablations.x_stall_experiment --seeds=0 run --max_workers=2 --wait
"""

# pyright: strict

import os
import sys

import experiments.common.minif2f_x as x
import experiments.common.omphalos_launch as ol

import delphyne as dp

RULE = "seenstate"
K = 4


def _take_flag(name: str, default: str) -> str:
    prefix = f"--{name}="
    value = default
    for arg in list(sys.argv[1:]):
        if arg.startswith(prefix):
            value = arg[len(prefix) :]
            sys.argv.remove(arg)
    return value


SEEDS = tuple(int(s) for s in _take_flag("seeds", "0").split(",") if s)

SMOKE_PROBLEMS = (
    "algebra_amgm_sum1toneqn_prod1tonleq1",
    "mathd_algebra_185",
    "amc12a_2016_p2",
)
_SMOKE = bool(os.environ.get("STALL_SMOKE"))
_PROBLEMS = (
    {k: x.TRAINX_PROBLEMS[k] for k in SMOKE_PROBLEMS}
    if _SMOKE
    else x.VALIDATIONX_PROBLEMS
)

configs = [
    x.StallXAgenticConfig(
        bench_name=name,
        model_name=x.X_MODEL,
        temperature=None,
        toolset=x.X_TOOLSET,
        num_requests=x.X_NUM_REQUESTS,
        loop=False,
        seed=seed,
        max_dollar_budget=x.X_DOLLAR_CAP,
        reasoning_effort=x.X_EFFORT,
        stall_rule=RULE,
        stall_k=K,
    )
    for seed in SEEDS
    for name in _PROBLEMS
]

_OUTPUT_DIR = f"experiments/output/x_validation_stall_{RULE}{K}_agentic" + (
    "_smoke" if _SMOKE else ""
)


if __name__ == "__main__":
    print(
        f"stall arm: rule={RULE} k={K} seeds={list(SEEDS)} "
        f"cells={len(configs)} output_dir={_OUTPUT_DIR}",
        flush=True,
    )
    ol.OmphalosExperiment(
        config_class=x.StallXAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=_OUTPUT_DIR,
        config_naming=x.x_stall_config_name,
    ).run_cli()
