"""
Agentic baseline (canonical "rich" toolset) on benchmark set 2
(`benchmarks/set2.txt`, the first holdout). Same knobs as
`set1_agentic_experiment.py`.

Usage:
    python experiments/set2_agentic_experiment.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf

import delphyne as dp

configs = [
    mf.AgenticConfig(
        bench_name=name,
        model_name="gpt-5.4-2026-03-05",
        temperature=None,
        toolset="rich",
        num_requests=32,
        loop=False,
        seed=0,
    )
    for name in mf.SET2_PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/set2_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}__seed{cfg.seed}"
        ),
    ).run_cli()
