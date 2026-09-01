"""
Does presenting verifier feedback as a *tool* message help the canonical
agentic loop?

The question. In `dp.interact`, prover feedback becomes a
`FeedbackMessage` and is rendered as a **user** message; genuine tool
results (`ReadSkill`, `SearchRocq`, ...) are already `tool`-role.
`convert_user_feedback_to_tool` rewrites each feedback turn into a
synthetic `__fetch_user_feedback__` call plus a tool result, so a user
turn cannot break the provider's KV cache. It defaults to on whenever
the reasoning cache is on.

Why re-ask it. It has been measured twice and neither run settles the
current configuration:

- *Agentic, terra, one seed* (`responses_train_experiment.py`, the
  `a1x-low-nocvt` arm): 20/20 $0.635 off vs 20/20 $0.663 on. Off is
  marginally cheaper, but that is one seed on a saturated partition,
  and terra is no longer the canonical model.
- *Standard loop, 4-arm factorial* (`baseline_api_experiment.py`): noise
  in both directions once paired per cell — see the 2026-08-13
  PROGRESS.md entry and its 2026-08-24 correction. That is the
  three-turn feedback loop, not this one.

Nobody has run it on the agentic loop under **luna**, which is where it
should matter most: this loop is long (a dozen-plus turns), so there is
real conversation for a cache break to damage, and luna's rate card
prices input relatively higher than terra's, which is exactly the ratio
the earlier decomposition showed this class of feature is sensitive to.

Pre-registered before running:

- **Primary metric: paired per problem-seed spend.** Sign test on the
  direction plus the median per-cell ratio — *not* the pooled total.
  Pooling is what produced the retracted reading on the standard loop:
  the cost distribution is heavy-tailed (worst cell 17.8× the median),
  so a pooled sum tracks a handful of runaway configs.
- **Secondary metric: solves.** Underpowered by construction: 40 cells
  still need 6 one-sided discordant problems for p < 0.05, so a null
  here means "not settled", not "no difference".
- **Pair only on cells both arms completed.** Responses arms have died
  with `context_length_exceeded` where chat did not (hint 31); pooling
  40 against 39 reads as a cost difference that is not there.
- Train only. Test is the one clean out-of-sample partition and this is
  a mechanism question, not a headline.

Expected spend ≈ $0.32 (canonical luna train is ~$0.080 for 20
problems); stop and investigate if it passes $0.50.

Usage:
    python experiments/luna_cvt_ablation.py run --max_workers=4
"""

# pyright: strict

import miniF2F_bench as mf
import omphalos_launch as ol

import delphyne as dp

CANONICAL_EFFORT = "medium"
CANONICAL_TOOLSET = "core"

CONVERSIONS = (True, False)
"""
The single controlled difference. Everything else is the canonical luna
configuration, so this is an arm-per-flag comparison in the sense of
hint 30.
"""

SEEDS = (0, 1)
"""
Two seeds, as on every other luna sweep. `seed` does not seed the
provider — sampling is nondeterministic regardless — it distinguishes
independent repeats, which is what the noise estimate needs.
"""

configs = [
    mf.ResponsesAgenticConfig(
        bench_name=name,
        model_name="gpt-5.6-luna",
        temperature=None,
        toolset=CANONICAL_TOOLSET,
        num_requests=32,
        loop=False,
        seed=seed,
        max_dollar_budget=mf.LUNA_DOLLAR_CAP,
        reasoning_effort=CANONICAL_EFFORT,
        convert_user_feedback_to_tool=convert,
    )
    for convert in CONVERSIONS
    for seed in SEEDS
    for name in mf.TRAIN_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.ResponsesAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/luna_cvt_ablation",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}"
            f"__cvt-{'on' if cfg.convert_user_feedback_to_tool else 'off'}"
            f"__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
