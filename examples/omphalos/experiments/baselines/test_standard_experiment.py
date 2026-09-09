"""
Standard baseline on the test partition (`benchmarks/test.txt`,
fully out-of-sample: never used for any iteration or tuning
decision). Same knobs as `train_standard_experiment.py`.

Usage:
    python -m experiments.baselines.test_standard_experiment run --max_workers=4
"""

# pyright: strict

import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp

configs = [
    mf.StandardConfig(
        bench_name=name,
        model_name=mf.CANONICAL_MODEL,
        temperature=None,
        max_feedback_cycles=3,
        loop=False,
        seed=0,
    )
    for name in mf.TEST_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.StandardConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/test_standard",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
