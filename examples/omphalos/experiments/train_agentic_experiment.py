"""
Agentic baseline (canonical "rich" toolset) on the train partition
(`benchmarks/train.txt`, the curated development set: the baselines
were iterated against it, so its numbers are in-sample).

Train doubles as the cost/performance frontier: every problem runs
once per gpt-5.6 tier (`mf.FRONTIER_MODELS`). Summarize the frontier
with `experiments/frontier_report.py`.

Usage:
    python experiments/train_agentic_experiment.py run --max_workers=4
    python experiments/train_agentic_experiment.py replay
    python experiments/train_agentic_experiment.py force-summary --add-timing
"""

# pyright: strict

import miniF2F_bench as mf
import omphalos_launch as ol

import delphyne as dp

configs = [
    mf.AgenticConfig(
        bench_name=name,
        model_name=model,
        temperature=None,
        toolset="rich",
        num_requests=32,
        loop=False,
        seed=0,
    )
    for model in mf.FRONTIER_MODELS
    for name in mf.TRAIN_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/train_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
