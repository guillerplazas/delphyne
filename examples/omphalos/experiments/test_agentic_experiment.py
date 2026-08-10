"""
Agentic baseline (canonical "rich" toolset) on the test partition
(`benchmarks/test.txt`, fully out-of-sample: never used for any
iteration or tuning decision). Same knobs as
`train_agentic_experiment.py`.

Usage:
    python experiments/test_agentic_experiment.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf

import delphyne as dp

configs = [
    mf.AgenticConfig(
        bench_name=name,
        model_name=mf.CANONICAL_MODEL,
        temperature=None,
        toolset="rich",
        num_requests=32,
        loop=False,
        seed=0,
    )
    for name in mf.TEST_PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/test_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
