"""
Scaffolding for the full miniF2F valid-split sweep, standard baseline.

Not run as part of the dev loop. Kept here so the cost of extending the
benchmark is mechanical: list all `valid/**/*.v` files, materialise a
`PROBLEMS` mapping in `miniF2F_bench`, and parameterise over models
and seeds.

Usage (when ready):
    python experiments/full_standard_experiment.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf
import delphyne as dp


MODELS = ["gpt-5.4-2026-03-05"]
SEEDS = [0]


configs = [
    mf.StandardConfig(
        bench_name=name,
        model_name=model,
        temperature=None,
        max_feedback_cycles=5,
        loop=False,
        seed=seed,
        max_dollar_budget=0.5,
    )
    for name in mf.PROBLEMS  # extend once `mf.PROBLEMS` covers the full split
    for model in MODELS
    for seed in SEEDS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.StandardConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/output/{dp.path_stem(__file__)}",
        config_naming=lambda cfg, _uid: f"{cfg.bench_name}__{cfg.model_name}__seed{cfg.seed}",
    ).run_cli()
