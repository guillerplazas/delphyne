"""
Run the baseline strategy over the curated `dev_subset.txt`.

Usage:
    python experiments/dev_baseline_experiment.py run --max_workers=2
    python experiments/dev_baseline_experiment.py replay
    python experiments/dev_baseline_experiment.py force-summary --add-timing
"""

# pyright: strict

import miniF2F_bench as mf
import delphyne as dp


configs = [
    mf.BaselineConfig(
        bench_name=name,
        model_name="gpt-5.4-2026-03-05",
        temperature=None,
        max_feedback_cycles=3,
        loop=False,
        seed=0,
    )
    for name in mf.PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.BaselineConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/output/{dp.path_stem(__file__)}_1",
        config_naming=lambda cfg, _uid: f"{cfg.bench_name}__seed{cfg.seed}",
    ).run_cli()
