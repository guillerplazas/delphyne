#!/usr/bin/env python3
"""
Baseline Interactive Experiment for Mini Equations.

This experiment runs the interactive baseline on the full benchmark using
`gpt-5.4`, `gpt-5.4-mini`, and `gpt-5.4-nano`, with reasoning effort as
our primary tuning axis.

To run:
    python experiments/baseline_experiment.py run --max_workers=1

To clean the index before re-running with different configs:
    python experiments/baseline_experiment.py clean_index

To list all configurations:
    python experiments/baseline_experiment.py list

To check status:
    python experiments/baseline_experiment.py status
"""

import delphyne as dp
import mini_eqns_experiments as meq

MODEL_CONFIGS = [("gpt-5.4-mini", ["low"])]
#   ("gpt-5.4", ["medium", "high"]),
#   ("gpt-5.4-mini", ["low", "medium", "high"]),
#    ("gpt-5.4-nano", ["low", "medium", "high"]),
#]

configs = [
    meq.BaselineConfig(
        bench_name=bench_name,
        model_name=model_name,
        temperature=None,
        max_feedback_cycles=10,
        loop=True,
        max_dollar_budget=0.2,
        seed=seed,
        reasoning_effort=reasoning_effort,
    )
    for bench_name in list(meq.BENCHS.keys())
    for (model_name, efforts) in MODEL_CONFIGS
    for reasoning_effort in efforts
    for seed in range(1)
]

if __name__ == "__main__":
    dp.Experiment(
        config_class=meq.BaselineConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/report/{dp.path_stem(__file__)}",
    ).run_cli()
