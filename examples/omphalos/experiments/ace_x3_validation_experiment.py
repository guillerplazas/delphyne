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

Usage:
    python experiments/ace_x3_validation_experiment.py \
        --playbook=ace_x3_offline.yaml run --max_workers=4 --wait
"""

# pyright: strict

import ace_x_eval as ev
import minif2f_x as x
from ace_bench import ACEAgenticConfig, ace_config_name
import omphalos_launch as ol

import delphyne as dp

SEEDS = (0, 1)

configs = ev.ace_x_configs(x.VALIDATIONX_PROBLEMS, SEEDS)

_OUTPUT_DIR = ev.arm_output_dir("validation")


if __name__ == "__main__":
    ev.announce(_OUTPUT_DIR)
    ol.OmphalosExperiment(
        config_class=ACEAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=_OUTPUT_DIR,
        config_naming=ace_config_name,
    ).run_cli()
