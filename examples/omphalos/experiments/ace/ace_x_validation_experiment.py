"""
A frozen ACE playbook on validationX, paired against the baseline.

Pre-registered before running (the same rule for every playbook arm
that goes through this script — offline, multi-epoch, no-Reflector,
monolithic, selective injection):

- Cells: every validationX problem x seeds {0, 1}, canonical luna
  configuration, definitions shown, cap `X_DOLLAR_CAP`; the only
  difference from `x_validation_experiment.py` is the playbook
  section of the system prompt.
- Control: the already-paid `x_validation_agentic` cells of the same
  problem and seed. Nothing is re-run.
- Primary: paired solves, exact two-sided sign test on the discordant
  cells (`tools/reports/ace_report.py`); fewer than 6 discordant cells is
  reported as UNDERPOWERED, not as a verdict.
- Secondary: paired spend among jointly-solved cells (median ratio),
  the error taxonomy (`tools/analysis/failure_analysis.py --compare`), and the
  offline cap curve (`tools/reports/ace_cap_report.py`).
- Selection rule for testX: an arm goes to testX only if it beats the
  baseline here on the primary metric or, at equal solves, is cheaper
  on the secondary at p < 0.05; the offline playbook (E1) goes
  regardless, as the paper's headline arm.
- Expected spend ≈ $1–2.5 per playbook arm; stop above $4.

Usage:
    python -m experiments.ace.ace_x_validation_experiment --playbook=ace_x_offline.yaml run --max_workers=4
    python -m experiments.ace.ace_x_validation_experiment --playbook=ace_x_offline.yaml --injection=top10 run --max_workers=4
"""

# pyright: strict

import experiments.common.ace_x_eval as ev
import experiments.common.minif2f_x as x
from experiments.common.ace_bench import ACEAgenticConfig, ace_config_name
import experiments.common.omphalos_launch as ol

import delphyne as dp

SEEDS = (0, 1)

assert ev.SELECTION.render_version == 2, (
    "the shared v2 directories hold render_version=2 cells only; v3+ "
    "playbooks go through experiments/ace_x3_*_experiment.py"
)
configs = ev.ace_x_configs(x.VALIDATIONX_PROBLEMS, SEEDS)


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=ACEAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/ace_x_validation_agentic",
        config_naming=ace_config_name,
    ).run_cli()
