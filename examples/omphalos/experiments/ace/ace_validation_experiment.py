"""
Evaluate the frozen ACE playbook on validation (paired vs baseline).

The evaluation half of the ACE replication (see
`experiments/ace/ace_adaptation.py` for the adaptation half and the list
of deviations from arXiv:2510.04618): the canonical agentic
configuration — gpt-5.6-luna, `core`, `reasoning_effort="medium"`,
Responses API, 32 requests, `LUNA_DOLLAR_CAP` — with the frozen
`experiments/playbooks/ace_v1.yaml` injected into the system prompt,
on all 20 validation problems, seeds 0 and 1. The playbook is the ONLY
change against the baseline arm (few-shot messages are byte-identical
by construction — verified on the smoke command's cache), honouring
the one-change-per-experiment rule.

**Pre-registered metrics and decision rule** (written before running):

- Baseline: the existing frozen `core-medium` seeds {0, 1} cells of
  `experiments/output/luna_validation_agentic` — no baseline re-runs.
- **Primary: solved cells** over the 40 problem-seed cells, paired per
  cell. Decision by exact sign test on the discordant cells,
  two-sided quoted (one-sided also reported; pre-registered direction:
  ACE solves more). Power floor: 6 one-sided discordant cells are
  needed for p < 0.05, and identical configs disagree on 1-3 cells
  run-to-run, so any smaller discordant count is reported as
  UNDERPOWERED rather than as a verdict.
- **Secondary: per-cell spend among jointly-solved cells** (sign test
  with a 2% tie band + median ratio), costs recomputed from token
  counts via `model_registry.pricing_for` — never the archived
  `price` column. This is where the thesis-relevant question lives:
  does the playbook's per-turn input tax buy fewer turns/retries
  under the same dollar cap?
- Pooled totals are printed last and labelled by `tools/reports/ace_report.py`
  (pooling this cost distribution manufactures effects; see
  PROGRESS.md 2026-08-24).

Read the results with `make ace-report`.

Usage:
    python -m experiments.ace.ace_validation_experiment run --max_workers=4
    python -m experiments.ace.ace_validation_experiment replay
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict


import experiments.common.ace_bench as ace_bench
import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp
from ace.ace_playbook import Playbook

SEEDS = (0, 1)

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
    for name in mf.VALIDATION_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=ace_bench.ACEAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/ace_validation_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__ace-{cfg.playbook_sha256[:8]}"
            f"-{cfg.toolset}-{cfg.reasoning_effort}"
            f"__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
