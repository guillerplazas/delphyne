"""
Run the agentic baseline over the curated `dev_subset.txt`, comparing
the "full" toolset (ReadSkill + SearchRocq + TryTactic) against the
"lean" one (no TryTactic) — 20 problems x 2 toolsets = 40 configs.
The `toolset` column in `results_summary.csv` is the comparison axis.

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
        toolset=toolset,
        num_requests=16,
        loop=False,
        seed=0,
    )
    for toolset in ("full", "lean")
    for name in mf.PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/dev_agentic_toolsets",
        config_naming=lambda cfg, _uid:
            f"{cfg.bench_name}__{cfg.toolset}__seed{cfg.seed}",
    ).run_cli()
