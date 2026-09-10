"""Preregistered $8 bounded ACE polish campaign (both agent harnesses).

24 trainX pilot cells: recovery, matched examples, output downshift, each on
four deterministically selected training problems, paired off/on at seed 0.
Each contrast changes only the named switch; typed admission is common.
Keep a switch only if exercised and either no fewer qualified solves with
strictly lower cost, or more solves with cost ratio <=1.20. These small
panels screen mechanisms; they are not inferential evidence.

Freeze once, then 40 trainX candidate cells (seed 0), 80 validationX
candidate and 80 fresh bounded reference cells (seeds 0/1). No tuning
between seeds, extra variants, testX or protected challenge data. Primary
utility gates: >=15% lower paired total cost with loss <=2/80 solves, or
gain >=4/80 with cost ratio <=1.20 (1.15 is the target). Qualified solves
require a verified proof at actual charged cost <=$0.10, including retries.
Report all-cell costs, cost/solve, family-clustered two-sided p<0.10 and
90% intervals separately from practical gates. Missing/censored cells
preclude verdicts. Historical comparators are descriptive only.

API liability ceiling $8: demos .60, pilots .80, train 1.10, validation 5,
retry .50. At most four infrastructure retries; no logical-failure retries.
Assistant usage is unmetered. Closed stage slack may be transferred to a
later registered stage, with a recorded reason, without adding any cells.
"""

from dataclasses import dataclass
import json
import os
import random
import sys
from typing import Any

import delphyne as dp
from experiments.ace.ace_bounded_experiment import BoundedConfig, digest
import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.paths import OMPHALOS_ROOT as ROOT

CAMPAIGN = ROOT / "experiments/campaigns/ace_polish_20260909"
ALLOCATIONS = {
    "demos": 0.60,
    "pilots": 0.80,
    "training": 1.10,
    "validation": 5.0,
    "retry": 0.50,
}
MECHANISMS = ("resource_recovery", "matched_advice", "output_recovery")


def read(name: str) -> dict[str, Any]:
    return json.loads((CAMPAIGN / name).read_text())


@dataclass
class PolishConfig(BoundedConfig):
    phase: str = "pilots"

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        args = super().instantiate(context)
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        return args


def name(config: PolishConfig, _: object) -> str:
    return f"{config.bench_name}__{config.arm_label}-r64__{config.model_name}__seed{config.seed}"


def configs(phase: str) -> list[PolishConfig]:
    registration = read("registration.json")
    train = mf.load_partition("benchmarks/trainX.txt")
    validation = mf.load_partition("benchmarks/validationX.txt")
    artifact = str((CAMPAIGN / "artifact.json").relative_to(ROOT))
    rows: list[PolishConfig] = []

    def add(
        bench: str,
        seed: int,
        arm: str,
        switches: dict[str, bool],
        reference: bool = False,
    ) -> None:
        rows.append(
            PolishConfig(
                bench_name=bench,
                problem_file=(dict(train) | dict(validation))[bench][0],
                model_name="gpt-5.6-luna",
                seed=seed,
                num_requests=64,
                temperature=None,
                toolset="core",
                reasoning_effort="medium",
                max_dollar_budget=0.10,
                artifact=artifact,
                artifact_sha256=registration["artifact_sha256"],
                arm_label=arm,
                phase=phase,
                admission=False,
                focused=True,
                restart=False,
                money=True,
                polished=not reference,
                resource_recovery=switches.get("resource_recovery", False),
                matched_advice=switches.get("matched_advice", False),
                output_recovery=switches.get("output_recovery", False),
            )
        )

    if phase == "pilots":
        for mechanism in MECHANISMS:
            for bench in registration["pilots"][mechanism]:
                for enabled in (False, True):
                    add(
                        bench,
                        0,
                        f"{mechanism}-{'on' if enabled else 'off'}",
                        {mechanism: enabled},
                    )
    elif phase == "training":
        for bench in train:
            add(bench, 0, "candidate", read("frozen.json")["switches"])
    elif phase == "validation":
        rng = random.Random(20260909)
        cells = [(bench, seed) for seed in (0, 1) for bench in validation]
        rng.shuffle(cells)
        for bench, seed in cells:
            arms = [False, True]
            rng.shuffle(arms)
            for reference in arms:
                add(
                    bench,
                    seed,
                    "reference" if reference else "candidate",
                    {} if reference else read("frozen.json")["switches"],
                    reference,
                )
    else:
        raise ValueError("phase must be pilots, training or validation")
    return rows


def verify_sources(manifest: dict[str, Any]) -> None:
    for path, expected in manifest["execution_hashes"].items():
        if digest(ROOT / path) != expected:
            raise ValueError(f"frozen execution file changed: {path}")


def main() -> None:
    phase = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--phase=")),
        "pilots",
    )
    sys.argv[:] = [a for a in sys.argv if not a.startswith("--phase=")]
    if "--retry_errors" in " ".join(sys.argv):
        raise ValueError(
            "Use an explicitly enumerated retry manifest; broad retries are prohibited"
        )
    if "run" in sys.argv:
        verify_sources(
            read("registration.json" if phase == "pilots" else "frozen.json")
        )
        Ledger(CAMPAIGN / "ledger.sqlite3").create(8.0, ALLOCATIONS)
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = phase
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "admission.jsonl")
    ol.OmphalosExperiment(
        config_class=PolishConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs(phase),
        output_dir=f"experiments/output/ace_polish_{phase}",
        config_naming=name,
        wait_for_slots=True,
        attempts=1,
    ).run_cli()


if __name__ == "__main__":
    main()
