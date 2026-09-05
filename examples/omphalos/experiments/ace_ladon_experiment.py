"""
A frozen ACE playbook on ladonX, paired against `x_ladon_agentic`.

The confirmation run of the 2026-09-05 cycle: the arm selected on
validationX (development ground, where every prior ACE arm lives) is
re-run on a second set against its own baseline, so "it works" rests
on two independent paired readouts rather than one. Same selection
flags as `ace_x3_validation_experiment.py` (`--playbook=`,
`--injection=full|top<k>|triggered`, `--triggers=`, `--max_hints=`,
`--seeds=`), same pre-registered metrics (paired spend on jointly
solved cells with solve non-inferiority; paired solves co-primary).
Output directory: `experiments/output/ace_ladon_<stem>_<injection>_agentic`.

ladonX is Ladon's selection partition; this script is run by hand, not
by the loop, and testX stays untouched.

Usage:
    python experiments/ace_ladon_experiment.py \\
        --playbook=ace_x5_offline.yaml --injection=triggered --seeds=0,1 \\
        run --max_workers=4 --wait
"""

# pyright: strict

import sys
from dataclasses import dataclass
from pathlib import Path

import ace_x_eval as ev
import omphalos_launch as ol
from ace_bench import ACEAgenticConfig, ACETriggeredConfig

import delphyne as dp

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
if str(_OMPHALOS_DIR) not in sys.path:
    sys.path.insert(0, str(_OMPHALOS_DIR))

from ladon.bench import LADONX_PROBLEMS  # noqa: E402


@dataclass
class ACELadonConfig(ACEAgenticConfig):
    """`ACEAgenticConfig` whose bench names may come from ladonX."""

    def _problem(self) -> tuple[str, str]:
        if self.bench_name in LADONX_PROBLEMS:
            return LADONX_PROBLEMS[self.bench_name]
        return super()._problem()


@dataclass
class ACETriggeredLadonConfig(ACETriggeredConfig):
    """`ACETriggeredConfig` whose bench names may come from ladonX."""

    def _problem(self) -> tuple[str, str]:
        if self.bench_name in LADONX_PROBLEMS:
            return LADONX_PROBLEMS[self.bench_name]
        return super()._problem()


SEEDS = ev.selected_seeds()
_SEL = ev.SELECTION
_CLASS = ACETriggeredLadonConfig if _SEL.triggered else ACELadonConfig

configs = [_CLASS(**vars(c)) for c in ev.ace_x_configs(LADONX_PROBLEMS, SEEDS)]

_OUTPUT_DIR = (
    f"experiments/output/ace_ladon_{_SEL.stem}_"
    + (f"trig_k{_SEL.max_hints}" if _SEL.triggered else _SEL.injection)
    + "_agentic"
)


if __name__ == "__main__":
    ev.announce(_OUTPUT_DIR)
    ol.OmphalosExperiment(
        config_class=_CLASS,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=_OUTPUT_DIR,
        config_naming=ev.config_naming(),
    ).run_cli()
