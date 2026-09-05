"""
A frozen v3 ACE playbook on validationX, paired against the baseline.

Same pre-registration as `ace_x_validation_experiment.py` (paired
solves, sign test, spend on jointly-solved cells, taxonomy, cap curve;
selection rule for testX unchanged) with two v3 differences:

- Per-arm output directory (`ace_x_eval.arm_output_dir`), so arms can
  run concurrently — the shared-state corruption of 2026-08-25 cannot
  recur by construction.
- The playbook is rendered at the version it was adapted under (from
  its provenance sidecar; `--render_version=` overrides deliberately),
  and the directory name carries it (`_rv{N}`), so an arm can never be
  scored under another arm's prompt again (2026-08-26 audit: the first
  "v3" evaluations had silently evaluated the v2 playbook at v2).

Hint on error (2026-09-05, `--injection=triggered`): the same script
evaluates a playbook delivered on error only (`ACETriggeredConfig`,
`acet_x_validation_<stem>_k<K>_agentic`). Pre-registration of that arm
(before any cell ran): primary = paired spend on jointly solved cells
against `x_validation_agentic` (2 % tie band, exact sign test, median
ratio) with solve non-inferiority (arm-only minus base-only >= -2),
co-primary = paired solves (six-cell floor); secondary = requests on
jointly solved cells, the per-request token/spend decomposition, the
repeat-of-class rate, first-error classes, hints fired and the class
recurrence after a hint (`tools/ace_diagnosis.py`); also paired against
the same playbook at full injection
(`ace_x_validation_ace_x5_offline_rv3_agentic`). Seed 0 first
(`--seeds=0`); seed 1 is added unless seed 0 loses four or more net
solves. Development-cycle comparison on validationX; ladonX confirms.

Usage:
    python experiments/ace_x3_validation_experiment.py \
        --playbook=ace_x3_offline.yaml run --max_workers=4 --wait
    python experiments/ace_x3_validation_experiment.py \
        --playbook=ace_x5_offline.yaml --injection=triggered --seeds=0 \
        run --max_workers=4 --wait
"""

# pyright: strict

import os

import ace_x_eval as ev
import minif2f_x as x
import omphalos_launch as ol

import delphyne as dp

SEEDS = ev.selected_seeds()

SMOKE_PROBLEMS = (
    "mathd_numbertheory_221",
    "mathd_algebra_28",
    "amc12a_2003_p1",
)
"""
`ACE_SMOKE=1`: three cheap trainX problems the baseline solves after at
least one rejected proposal (2–3 requests, seed 0), so a smoke of a
hint-on-error arm exercises the feedback path for about a cent, into
`<arm directory>_smoke`. Never the validationX cells.
"""

_SMOKE = bool(os.environ.get("ACE_SMOKE"))
_PROBLEMS = (
    {k: x.TRAINX_PROBLEMS[k] for k in SMOKE_PROBLEMS}
    if _SMOKE
    else x.VALIDATIONX_PROBLEMS
)

configs = ev.ace_x_configs(_PROBLEMS, SEEDS)

_OUTPUT_DIR = ev.arm_output_dir("validation") + ("_smoke" if _SMOKE else "")


if __name__ == "__main__":
    ev.announce(_OUTPUT_DIR)
    ol.OmphalosExperiment(
        config_class=ev.config_class(),
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=_OUTPUT_DIR,
        config_naming=ev.config_naming(),
    ).run_cli()
