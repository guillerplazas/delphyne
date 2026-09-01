"""
Scaffolding for the full miniF2F valid-split sweep, agentic baseline.

Not run as part of the dev loop. Mirrors `full_standard_experiment.py`
but uses `AgenticConfig` and a slightly higher per-problem budget to
accommodate the LLM's tool calls.

Usage (when ready):
    python experiments/full_agentic_experiment.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf
import omphalos_launch as ol
import delphyne as dp


MODELS = [mf.CANONICAL_MODEL]
SEEDS = [0]


configs = [
    mf.AgenticConfig(
        bench_name=name,
        model_name=model,
        temperature=None,
        toolset="rich",  # canonical: ties "core" at 8/20, marginally cheaper
        num_requests=20,
        loop=False,
        seed=seed,
        max_dollar_budget=0.7,
    )
    for name in mf.TRAIN_PROBLEMS  # extend to the full valid split later
    for model in MODELS
    for seed in SEEDS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/output/{dp.path_stem(__file__)}",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
