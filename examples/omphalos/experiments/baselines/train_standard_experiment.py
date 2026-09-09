"""
Standard baseline on the train partition (`benchmarks/train.txt`,
the curated development set: the baselines were iterated against it,
so its numbers are in-sample).

Train doubles as the cost/performance frontier: every problem runs
once per gpt-5.6 tier (`mf.FRONTIER_MODELS`). Summarize the frontier
with `tools/reports/frontier_report.py`.

Usage:
    python -m experiments.baselines.train_standard_experiment run --max_workers=4
    python -m experiments.baselines.train_standard_experiment replay
    python -m experiments.baselines.train_standard_experiment force-summary --add-timing
"""

# pyright: strict

import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp

configs = [
    mf.StandardConfig(
        bench_name=name,
        model_name=model,
        temperature=None,
        max_feedback_cycles=3,
        loop=False,
        seed=0,
    )
    for model in mf.FRONTIER_MODELS
    for name in mf.TRAIN_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.StandardConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/train_standard",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
