"""
Standard baseline on benchmark set 1 (`benchmarks/set1.txt`,
the curated development subset).

Usage:
    python experiments/set1_standard_experiment.py run --max_workers=4
    python experiments/set1_standard_experiment.py replay
    python experiments/set1_standard_experiment.py force-summary --add-timing
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
    for name in mf.SET1_PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.StandardConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/set1_standard",
        config_naming=lambda cfg, _uid: f"{cfg.bench_name}__seed{cfg.seed}",
    ).run_cli()
