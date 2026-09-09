"""
Luna's winning configuration on the validation partition.

Confirms the train result out of sample. Only the winning arm runs
here: the effort x toolset grid was mapped on train
(`luna_train_experiment`), and re-mapping it on validation would be
tuning on the partition that is supposed to check the tuning.

Train, all arms under a deliberately loose cap (see the train script),
`core` column:

    none    12/20  $0.2828   302 turns
    low     20/20  $0.1240   165 turns
    medium  20/20  $0.0799   121 turns   <- cheapest
    high    20/20  $0.1115   124 turns
    xhigh   20/20  $0.1644   152 turns
    max     20/20  $0.1558   119 turns

Solves saturate at `low`, but *cost* keeps falling to `medium` and then
rises again — so the optimum is not where a solve-count-only reading
would put it. Note this differs from terra, whose optimum was `low`
(`low -> medium` there was +22% for no extra solves): the weaker the
model, the more reasoning pays, because reasoning buys turns and turns
are what cost money. Effort is not transferable between model tiers.

For reference, terra at its own best scores 20/20 for $0.530, so luna
matches it on train for about a seventh of the cost. The `none` arms
are the control that makes the claim attributable: without reasoning
luna manages 12-13/20 and burns twice the turns, so the win belongs to
reasoning rather than to the API or the price cut.

The cap is `LUNA_DOLLAR_CAP`, derived from the train sweep by the same
rule used for terra (smallest round cap costing train no solves).

Usage:
    python -m experiments.baselines.luna_validation_experiment run --max_workers=4
"""

# pyright: strict

import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp

WINNING_EFFORT = "medium"
WINNING_TOOLSET = "core"

SEEDS = (0, 1)
"""
Two seeds, not one. The decision audit's whole point is that a single
20-problem run cannot separate a small difference from noise, and luna
is cheap enough that there is no excuse.
"""

configs = [
    mf.ResponsesAgenticConfig(
        bench_name=name,
        model_name="gpt-5.6-luna",
        temperature=None,
        toolset=WINNING_TOOLSET,
        num_requests=32,
        loop=False,
        seed=seed,
        max_dollar_budget=mf.LUNA_DOLLAR_CAP,
        reasoning_effort=WINNING_EFFORT,
    )
    for seed in SEEDS
    for name in mf.VALIDATION_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.ResponsesAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/luna_validation_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}-{cfg.reasoning_effort}"
            f"__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
