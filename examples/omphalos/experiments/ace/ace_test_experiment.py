"""
ACE playbook on the TEST partition — the out-of-sample look.

The clean-partition arm of the ACE study (see
`experiments/ace/ace_adaptation.py` for the method and its deviations from
arXiv:2510.04618, and `ace_validation_experiment.py` for the tuning
half). Canonical agentic configuration — gpt-5.6-luna, `core`,
`reasoning_effort="medium"`, Responses API, 32 requests,
`LUNA_DOLLAR_CAP` — with a frozen playbook injected into the system
prompt. The playbook is the only change against the baseline arm.

**Pre-registered metric and decision rule** (written before running):

- Baseline: the frozen `experiments/output/luna_test_agentic`
  `core-medium` seed-0 cells (16/20, $0.2879). Not re-run.
- Seed 0 only, matching the baseline arm and the house convention for
  test (`luna_test_experiment.py`: variance is characterised on train
  and validation, not on the clean partition).
- Primary: solved cells over the 20 problem cells, paired per cell,
  exact sign test on the discordant cells. Power floor: 6 one-sided
  discordant cells for p < 0.05, against a noise floor of 1-3 — a
  smaller discordant count is reported as UNDERPOWERED, never as a
  verdict.
- Secondary: per-cell spend among jointly-solved cells, prices
  recomputed from token counts via `model_registry.pricing_for`.

**Honesty note on the test partition.** House rule is one look per
headline. This study spends two: once here with `ace_v1` (the
first-generation playbook), and once at the end with whichever
configuration validation selects. Both looks are reported, neither is
mined — no failure seen on test may be used to change any prompt,
playbook or policy. The second look is therefore a confirmation of a
validation-selected choice, not a selection criterion itself.

Read the results with `make ace-report-test`.

Usage:
    python -m experiments.ace.ace_test_experiment run --max_workers=4
    python -m experiments.ace.ace_test_experiment replay
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict


import experiments.common.ace_bench as ace_bench
import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp


from ace.ace_playbook import Playbook  # noqa: E402

SEEDS = (0,)

PLAYBOOK_FILE = "experiments/playbooks/ace_v1.yaml"

_playbook_sha = Playbook.load(OMPHALOS_ROOT / PLAYBOOK_FILE).sha256()


configs = [
    ace_bench.ACEAgenticConfig(
        bench_name=name,
        model_name="gpt-5.6-luna",
        temperature=None,
        toolset="core",
        num_requests=32,
        loop=False,
        seed=seed,
        max_dollar_budget=mf.LUNA_DOLLAR_CAP,
        reasoning_effort="medium",
        playbook_file=PLAYBOOK_FILE,
        playbook_sha256=_playbook_sha,
    )
    for seed in SEEDS
    for name in mf.TEST_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=ace_bench.ACEAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/ace_test_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__ace-{cfg.playbook_sha256[:8]}"
            f"-{cfg.toolset}-{cfg.reasoning_effort}"
            f"__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
