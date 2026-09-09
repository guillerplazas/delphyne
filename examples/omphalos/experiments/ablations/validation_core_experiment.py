"""
Agentic baseline with the "core" toolset on the validation partition
(`benchmarks/validation.txt`).

Toolset ablation. Control arm: the seed-0 `"rich"` runs in
`experiments/output/validation_agentic` — same model, same request
budget, same verifier, same seed, so `toolset` is the only controlled
difference.

Why re-measure. The rich-vs-core comparison was decided under
gpt-5.4 across four dev-partition iterations (PROGRESS.md): rich and
core tied at 8/20 while tools were the only difference, and rich pulled
ahead (12/20 vs 7/20) only once automation-assisted verification
landed. That conclusion has never been checked on gpt-5.6, and the
current model calls a tool in only ~40% of validation configs — so the
canonical toolset may no longer be earning its extra prompt cost.

`"core"` advertises `ReadSkill` + `SearchRocq` and leans on *partial
proposals* for structural exploration: `check_proof_assisted` reports
the verified prefix and the exact remaining goals whenever a script
applies cleanly without closing the goal, so a proposal doubles as a
preview. `"rich"` swaps `SearchRocq` for `InspectAt` (which subsumes
it) and adds `TryAutomation`.

Usage:
    python -m experiments.ablations.validation_core_experiment run --max_workers=4
"""

# pyright: strict

import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp

configs = [
    mf.AgenticConfig(
        bench_name=name,
        model_name=mf.CANONICAL_MODEL,
        temperature=None,
        toolset="core",
        num_requests=32,
        loop=False,
        seed=0,
    )
    for name in mf.VALIDATION_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/validation_core",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
