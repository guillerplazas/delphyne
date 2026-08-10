"""
Agentic baseline with the "probing" toolset (rich + TryTactics) on
the test partition (`benchmarks/test.txt`). Control arm: the archived
seed-0 `"rich"` runs in `experiments/output/test_agentic`; same model
and request budget, so toolset is the only controlled difference.

Version note: outputs go to `test_probing_v2` — the calibrated
probing arm (probing-gated system-prompt discipline, tightened
TryTactics docstring, TryTactics few-shot workflow example). The
frozen pre-calibration sweep lives in `test_probing` (v1); its prompt
is no longer reproducible from this tree.

Two seeds per problem. Note that `seed` is a *labeling* knob:
`AgenticConfig.instantiate` does not forward it to the policy, but
distinct config names get distinct request caches, so the two seeds
are two independent samples (variation comes from provider
nondeterminism at the default temperature).

Usage:
    python experiments/test_probing_experiment.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf

import delphyne as dp

configs = [
    mf.AgenticConfig(
        bench_name=name,
        model_name=mf.CANONICAL_MODEL,
        temperature=None,
        toolset="probing",
        num_requests=32,
        loop=False,
        seed=seed,
    )
    for seed in (0, 1)
    for name in mf.TEST_PROBLEMS
]


if __name__ == "__main__":
    dp.Experiment(
        config_class=mf.AgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/test_probing_v2",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
