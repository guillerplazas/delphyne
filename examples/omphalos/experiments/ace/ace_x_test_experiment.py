"""
A frozen ACE playbook on testX — one look.

Pre-registered before running:

- Cells: every testX problem, seed 0, exactly as
  `x_test_experiment.py` plus the playbook section.
- Control: the already-paid `x_test_agentic` cells.
- Which playbooks may come here: the offline playbook (E1) as the
  paper's headline arm, and any other arm only if it was selected on
  validationX by the rule in `ace_x_validation_experiment.py`. Online
  arms are evaluated by their own driver
  (`ace_adaptation.py run --variant=x-online-testX`), not here.
- Readout: paired solves + sign test, paired spend, taxonomy, cap
  curve — reported, never used to change anything.
- Expected spend ≈ $0.5–1.2 per arm; stop above $2.

Usage:
    python -m experiments.ace.ace_x_test_experiment --playbook=ace_x_offline.yaml run --max_workers=4
"""

# pyright: strict

import experiments.common.ace_x_eval as ev
import experiments.common.minif2f_x as x
from experiments.common.ace_bench import ACEAgenticConfig, ace_config_name
import experiments.common.omphalos_launch as ol

import delphyne as dp

SEEDS = (0,)

assert ev.SELECTION.render_version == 2, (
    "the shared v2 directories hold render_version=2 cells only; v3+ "
    "playbooks go through experiments/ace_x3_*_experiment.py"
)
configs = ev.ace_x_configs(x.TESTX_PROBLEMS, SEEDS)


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=ACEAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/ace_x_test_agentic",
        config_naming=ace_config_name,
    ).run_cli()
