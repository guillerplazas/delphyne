"""
A frozen v3 ACE playbook on testX — one look. Same pre-registration as
`ace_x_test_experiment.py`; per-arm output directory named by
playbook and render version (`ace_x_eval`).

Usage:
    python -m experiments.ace.ace_x3_test_experiment \
        --playbook=ace_x3_offline.yaml run --max_workers=4 --wait
"""

# pyright: strict

import experiments.common.ace_x_eval as ev
import experiments.common.minif2f_x as x
from experiments.common.ace_bench import ACEAgenticConfig, ace_config_name
import experiments.common.omphalos_launch as ol

import delphyne as dp

SEEDS = (0,)

configs = ev.ace_x_configs(x.TESTX_PROBLEMS, SEEDS)

_OUTPUT_DIR = ev.arm_output_dir("test")


if __name__ == "__main__":
    ev.announce(_OUTPUT_DIR)
    ol.OmphalosExperiment(
        config_class=ACEAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=_OUTPUT_DIR,
        config_naming=ace_config_name,
    ).run_cli()
