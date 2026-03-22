#!/usr/bin/env python3
"""
Guided Interactive Experiment for Mini Equations

This experiment runs the guided proof strategy with enhanced prompts and
a light search configuration.

The policy default supports broader search, but this experiment keeps
`num_completions=2` to measure the prompt improvements under a modest
sampling budget.

To run:
    python experiments/guided_experiment.py run --max_workers=16

To clean the index before re-running with different configs:
    python experiments/guided_experiment.py clean_index

To list all configurations:
    python experiments/guided_experiment.py list

To check status:
    python experiments/guided_experiment.py status
"""

import delphyne as dp
import mini_eqns_experiments as meq

#MODELS = ["gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07"]
MODELS = ["gpt-5.4-nano"]
REASONING_EFFORTS = ["high"]  # e.g. [None], ["low"], ["medium"], ["high"]

configs = [
    meq.GuidedConfig(
        bench_name=bench_name,
        model_name=model,
        temperature=1.0,
        num_completions=2,
        max_feedback_cycles=10,
        loop=True,
        max_dollar_budget=0.2,
        seed=seed,
        reasoning_effort=reasoning_effort,
    )
    for bench_name in list(meq.BENCHS.keys())
    for model in MODELS
    for reasoning_effort in REASONING_EFFORTS
    for seed in range(1)
]

if __name__ == "__main__":
    dp.Experiment(
        config_class=meq.GuidedConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/report/{dp.path_stem(__file__)}",
    ).run_cli()
