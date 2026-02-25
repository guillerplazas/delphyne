"""
Experiment for the sketch-guided step-by-step proof strategy.
Tests gpt-5-mini and gpt-5-nano on the full benchmark.
"""

import delphyne as dp
import mini_eqns_experiments as meq

MODELS = ["gpt-5-nano-2025-08-07"]
#MODELS = ["gpt-5-mini-2025-08-07"]
#, "gpt-5-nano-2025-08-07"]

configs = [
    meq.StepByStepConfig(
        bench_name=bench_name,
        model_name=model,
        temperature=1.0,
        max_feedback_cycles_per_step=20,
        max_steps=30,
        loop=False,
        max_dollar_budget=0.2,
        seed=seed,
    )
    for bench_name in list(meq.BENCHS.keys())
    for model in MODELS
    for seed in range(1)
]

if __name__ == "__main__":
    dp.Experiment(
        config_class=meq.StepByStepConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/output/{dp.path_stem(__file__)}",
    ).run_cli()
