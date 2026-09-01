"""
Does the tool machinery still earn its place? Multi-seed, on the
current best configuration.

The 2026-08-12 decision audit found that `"rich"` — the canonical
toolset, and the reason `InspectAt` and `TryAutomation` exist — has no
measured advantage over `"core"`. Pooling all four gpt-5.4-era matched
iterations gives 23 discordant problems, which is ample power, and rich
wins only 15 of them (p=0.21). Re-tested once on gpt-5.6 it lost by one.

That verdict was reached on a system that has since changed twice: it
now runs under a binding dollar cap and through the Responses API with
reasoning on. This re-asks the question on the configuration that
actually won, and asks it with enough seeds to answer.

On train the question cannot be answered on solves at all: both
toolsets score 20/20 on every seed, so the partition is saturated and
carries no discriminating signal. It still answered on *cost* (core ran
29% cheaper for identical results), but a solve-rate comparison needs a
partition with headroom. Validation has it -- the current best
configuration scores 16/20 there.

What the answer changes:

- If core matches rich, the exploration tools are dead weight on this
  model class, and the +11-over-standard gap belongs to the verifier
  (`check_proof_assisted`) and the error-mined prompt guidance. That
  would make the cheap path the good one.
- If rich wins now where it did not before, reasoning is what makes the
  tools usable — which would be a finding about *when* tool machinery
  pays, not whether.

Usage:
    python experiments/responses_toolset_ablation_validation.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf
import omphalos_launch as ol

import delphyne as dp

TOOLSETS = ("rich", "core")
SEEDS = (1, 2)
"""
Seed 0 of the `rich` arm already exists in
`experiments/output/responses_validation_agentic`, so it is not
repeated here. `seed` does not seed the provider — sampling is
nondeterministic regardless — it just distinguishes independent
repeats, which is exactly what is wanted for a noise estimate.
"""

configs = [
    mf.ResponsesAgenticConfig(
        bench_name=name,
        model_name=mf.CANONICAL_MODEL,
        temperature=None,
        toolset=toolset,
        num_requests=32,
        loop=False,
        seed=seed,
        max_dollar_budget=mf.PER_PROBLEM_DOLLAR_CAP,
        reasoning_effort="low",
    )
    for toolset in TOOLSETS
    for seed in SEEDS
    for name in mf.VALIDATION_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.ResponsesAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/responses_toolset_ablation_validation",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
