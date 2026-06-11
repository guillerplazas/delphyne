"""
Standard baseline on benchmark set 3 (`benchmarks/set3.txt`,
the second holdout). Same knobs as `set1_standard_experiment.py`.

Usage:
    python experiments/set3_standard_experiment.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf

import delphyne as dp

configs = [
    mf.StandardConfig(
        bench_name=name,
        model_name="gpt-5.4-2026-03-05",
        temperature=None,
        max_feedback_cycles=3,
        loop=False,
        seed=0,
    )
    for name in mf.SET3_PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.StandardConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/set3_standard",
        config_naming=lambda cfg, _uid: f"{cfg.bench_name}__seed{cfg.seed}",
    ).run_cli()
