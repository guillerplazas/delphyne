"""
Responses-API agentic arm on the validation partition.

Confirms the train winner. Only the winning arm runs here: the
reasoning-effort curve was mapped on train (`responses_train_experiment`),
and re-mapping it on validation would be tuning on a partition that is
supposed to check the tuning.

Winner on train, at a matched $0.30 per-problem cap:

    chat completions          20/20  $1.126  145 turns
    responses, effort none    18/20  $1.415  192 turns
    responses, effort low     20/20  $0.663  110 turns
    responses, effort medium  20/20  $0.810  113 turns

so `low` it is — same solves as the control for 41% less, by needing
fewer turns rather than cheaper ones.

Usage:
    python experiments/responses_validation_experiment.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf
import omphalos_launch as ol

import delphyne as dp

WINNING_EFFORT = "low"

configs = [
    mf.ResponsesAgenticConfig(
        bench_name=name,
        model_name=mf.CANONICAL_MODEL,
        temperature=None,
        toolset="rich",
        num_requests=32,
        loop=False,
        seed=0,
        max_dollar_budget=mf.PER_PROBLEM_DOLLAR_CAP,
        reasoning_effort=WINNING_EFFORT,
    )
    for name in mf.VALIDATION_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.ResponsesAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/responses_validation_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.reasoning_effort}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
