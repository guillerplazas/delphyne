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

import mini_eqns_experiments as meq

# Model configurations
SMALL_MODELS = ["gpt-4o-mini"]
LARGE_MODELS = ["gpt-4o"]

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
    )
    # Test on first 10 equations for initial experiments
    for bench_name in list(meq.BENCHS.keys())[:10]
    # Use different models
    for model in [*SMALL_MODELS, *LARGE_MODELS]
    # Temperature variations (more for small models)
    #for temperature in ([0.7, 1.0, 1.5] if model in SMALL_MODELS else [0.7, 1.0])
    for temperature in ([1.0] if model in SMALL_MODELS else [1.0]) # KEEP DEFAULT
    # Feedback cycle variations (more for large models)
    #for max_feedback_cycles in ([3] if model in SMALL_MODELS else [0, 1, 3])
    for max_feedback_cycles in ([3] if model in SMALL_MODELS else [3])
    # Multiple seeds for reproducibility
    for seed in range(3)
]

if __name__ == "__main__":
    meq.make_experiment(
        meq.baseline_experiment,
        configs,
        "output",
        __file__
    ).run_cli()