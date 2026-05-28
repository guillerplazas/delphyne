"""
Run the agentic baseline strategy over the curated `dev_subset.txt`.

Usage:
    python experiments/dev_agentic_experiment.py run --max_workers=2
    python experiments/dev_agentic_experiment.py replay
    python experiments/dev_agentic_experiment.py force-summary --add-timing
"""

# pyright: strict

import miniF2F_bench as mf
import delphyne as dp


configs = [
    mf.AgenticConfig(
        bench_name=name,
        model_name="gpt-5.4-2026-03-05",
        temperature=None,
        max_feedback_cycles=6,
        num_requests=16,
        loop=False,
        seed=0,
    )
    for name in mf.PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/dev_agentic",
        config_naming=lambda cfg, _uid: f"{cfg.bench_name}__seed{cfg.seed}",
    ).run_cli()
