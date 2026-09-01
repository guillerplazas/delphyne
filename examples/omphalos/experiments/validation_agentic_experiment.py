"""
Agentic baseline (canonical "rich" toolset) on the validation
partition (`benchmarks/validation.txt`, the tuning set: one round of
infrastructure fixes was mined from its failure traces). Same knobs as
`train_agentic_experiment.py`.

Usage:
    python experiments/validation_agentic_experiment.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf
import omphalos_launch as ol

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
    for name in mf.VALIDATION_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/validation_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
