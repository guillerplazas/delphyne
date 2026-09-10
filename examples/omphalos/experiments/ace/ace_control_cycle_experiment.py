"""Registered 120-cell bounded ACE control cycle (trainX, trainX, validationX).

The tuning pass collects only trainX evidence.  Its settled output traces
determine one conservative completion cap and its re-verified transitions
determine one artifact/demonstration set.  Those files are frozen before the
trained trainX and validationX passes.  The validation decision is observed
Pareto improvement over the retained bounded reference: complete panel, at
least 25 qualified solves, and lower total charged cost.  No testX, protected
challenge data, extra seeds, or paid adaptation-role calls are permitted.
"""

# pyright: strict

from dataclasses import dataclass
import json
import os
import sys
from typing import cast

import delphyne as dp

from experiments.ace.ace_bounded_experiment import BoundedConfig, ROOT
import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.runtime_profiles import RuntimeProfile

CAMPAIGN = ROOT / "experiments/campaigns/ace_control_cycle_20260909"
ALLOCATIONS = {
    "tuning": 1.25,
    "training": 1.25,
    "validation": 1.25,
    "retry": 0.25,
}
INITIAL_ARTIFACT = (
    "experiments/campaigns/ace_bounded_20260908/artifact_v2.json"
)
INITIAL_ARTIFACT_SHA = (
    "edbc4e4da6c76e44a2c9a9588870a246a8d023b30ce622f288b985adf75fcaa6"
)


def activate(stage: str) -> None:
    RuntimeProfile.load(
        ROOT / "experiments/campaigns/ace_review_20260908/runtime.json"
    ).activate()
    ledger = CAMPAIGN / "ledger.sqlite3"
    Ledger(ledger).create(4.0, ALLOCATIONS)
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(ledger)
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = stage
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "admission.jsonl")


@dataclass
class CycleConfig(BoundedConfig):
    phase: str = "tuning"
    output_limit: int = 32768

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        args = super().instantiate(context)
        os.environ["OMPHALOS_OUTPUT_LIMIT"] = str(self.output_limit)
        return args


def config_name(config: CycleConfig, _: object) -> str:
    return (
        f"{config.bench_name}__{config.arm_label}-r64"
        f"__{config.model_name}__seed{config.seed}"
    )


def frozen() -> dict[str, object]:
    return json.loads((CAMPAIGN / "frozen.json").read_text())


def configs(phase: str) -> list[CycleConfig]:
    if phase == "tuning":
        problems = mf.load_partition("benchmarks/trainX.txt")
        artifact, sha, limit, recovery, label = (
            INITIAL_ARTIFACT,
            INITIAL_ARTIFACT_SHA,
            32768,
            False,
            "tuning",
        )
    elif phase in {"training", "validation"}:
        state = frozen()
        problems = mf.load_partition(
            f"benchmarks/{'trainX' if phase == 'training' else 'validationX'}.txt"
        )
        artifact = str(state["artifact"])
        sha = str(state["artifact_sha256"])
        limit = cast(int, state["output_limit"])
        recovery, label = (
            True,
            "trained" if phase == "training" else "validation",
        )
    else:
        raise ValueError("phase must be tuning, training, or validation")
    return [
        CycleConfig(
            bench_name=bench,
            problem_file=spec[0],
            model_name="gpt-5.6-luna",
            temperature=None,
            toolset="core",
            num_requests=64,
            seed=0,
            max_dollar_budget=0.10,
            reasoning_effort="medium",
            artifact=artifact,
            artifact_sha256=sha,
            arm_label=label,
            admission=True,
            focused=True,
            restart=False,
            money=True,
            resource_recovery=recovery,
            phase=phase,
            output_limit=limit,
        )
        for bench, spec in problems.items()
    ]


def main() -> None:
    if "run" in sys.argv or "resume" in sys.argv:
        raise ValueError(
            "Historical control cycle is closed; its runtime cannot be "
            "reconstructed from the surviving source. Use ace_polish_experiment."
        )
    phase = next(
        (
            arg.split("=", 1)[1]
            for arg in sys.argv[1:]
            if arg.startswith("--phase=")
        ),
        "tuning",
    )
    sys.argv[:] = [arg for arg in sys.argv if not arg.startswith("--phase=")]
    # Delphyne's retry_errors keeps the exact existing configuration and
    # cache.  Charge its one transport retry against the separately reserved
    # retry stage rather than widening any experimental cell budget.
    activate("retry" if "--retry_errors" in sys.argv else phase)
    ol.OmphalosExperiment(
        config_class=CycleConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs(phase),
        output_dir=f"experiments/output/ace_control_cycle_{phase}",
        config_naming=config_name,
        wait_for_slots=True,
        attempts=1,
    ).run_cli()


if __name__ == "__main__":
    main()
