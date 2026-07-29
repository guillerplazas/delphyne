"""
Agentic baseline (canonical "rich" toolset) on benchmark set 1
(`benchmarks/set1.txt`, the curated development subset).

Set 1 doubles as the cost/performance frontier: every problem runs
once per gpt-5.6 tier (`mf.FRONTIER_MODELS`). Summarize the frontier
with `experiments/frontier_report.py`.

Usage:
    python experiments/set1_agentic_experiment.py run --max_workers=4
    python experiments/set1_agentic_experiment.py replay
    python experiments/set1_agentic_experiment.py force-summary --add-timing
"""

# pyright: strict

import miniF2F_bench as mf

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
    for name in mf.SET1_PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/set1_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
