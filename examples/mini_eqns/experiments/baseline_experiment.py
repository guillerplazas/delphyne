#!/usr/bin/env python3
"""
Baseline Interactive Experiment for Mini Equations

This experiment runs the interactive proof strategy on a grid of configurations,
testing different models, temperatures, and feedback cycles.

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

# Model configurations
SMALL_MODELS = ["gpt-5.4-nano"]
#SMALL_MODELS = ["gpt-5-mini-2025-08-07"]
#LARGE_MODELS = ["gpt-4o"]
REASONING_EFFORTS = ["xhigh"]  # e.g. [None], ["low"], ["medium"], ["high"]

# Create experiment configurations
configs = [
    meq.BaselineConfig(
        bench_name=bench_name,
        model_name=model,
        temperature=temperature,
        max_feedback_cycles=max_feedback_cycles,
        loop=True,
        max_dollar_budget=0.2,
        seed=seed,
        reasoning_effort=reasoning_effort,
    )
    # Run on all equations from benchmark file
    for bench_name in list(meq.BENCHS.keys())
    # Use different models
    #for model in [*SMALL_MODELS, *LARGE_MODELS]
    for model in [*SMALL_MODELS]
    # Temperature variations (more for small models)
    #for temperature in ([0.7, 1.0, 1.5] if model in SMALL_MODELS else [0.7, 1.0])
    for temperature in ([1.0] if model in SMALL_MODELS else [1.0]) # KEEP DEFAULT
    for reasoning_effort in REASONING_EFFORTS
    # Feedback cycle variations (more for large models)
    #for max_feedback_cycles in ([3] if model in SMALL_MODELS else [0, 1, 3])
    for max_feedback_cycles in ([10] if model in SMALL_MODELS else [20])
    # Multiple seeds for reproducibility
    for seed in range(1)
]

if __name__ == "__main__":
    dp.Experiment(
        config_class=meq.BaselineConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/report/{dp.path_stem(__file__)}",
    ).run_cli()
