"""Approved $10 ACE follow-up, trainX then ONE validationX seed-0 arm.

Protocol (fixed before paid work): eight trainX problems, two per monetary
admission / verified-advice admission / focused query / bounded restart
contrast. Each pair changes only its named switch in the new architecture.
At most sixteen pilot prover attempts, four offline adaptation episodes,
forty validation cells and four infrastructure retries. No testX access.

Pilot gates: no lost solve and no higher paired cost, with an observable
targeted transition or resource reduction; these are diagnostic, not powered
inference. Final artifact integrates passing switches, frozen before looking
at validation. Comparator is recorded x3-r64/seed0, rendering 3. Primary:
actual-cost-qualified solves (<= $0.10), useful effect >=5 percentage points;
secondary: >=10% lower total paired cost and no fewer observed solves.
Both use exploratory two-sided family-cluster p<0.10 with 90% intervals.
All failures and charges remain; incomplete/censored panels get no verdict.
No extra seeds or variants after validation. Cost uncertainty is descriptive
and historical controls are not contemporaneously randomized treatment.

Both Codex and Claude use this Python CLI and the same ledger. Typical:
 python -m experiments.ace.ace_bounded_experiment --phase=pilot run --max_workers=4 --wait
"""

from runtime.paths import OMPHALOS_ROOT

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import delphyne as dp
from delphyne.utils.typing import pydantic_load

import ace.ace_grounded as ag  # noqa: E402
from ace.ace_playbook import Playbook  # noqa: E402
from runtime.campaign_budget import Ledger  # noqa: E402
import experiments.common.miniF2F_bench as mf  # noqa: E402
import experiments.common.omphalos_launch as ol  # noqa: E402
from runtime.runtime_profiles import RuntimeProfile  # noqa: E402

ROOT = OMPHALOS_ROOT

CAMPAIGN = ROOT / "experiments/campaigns/ace_bounded_20260908"
ALLOCATIONS = {"training": 2.0, "validation": 7.5, "retry": 0.5}
INCUMBENT = ROOT / "experiments/playbooks/ace_x3_offline.yaml"
INCUMBENT_SHA = (
    "1e4aec7dbbe80e7a320db17a7c18fe0859bfc00898837c297be248a05dbde067"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def activate(stage: str) -> None:
    profile = RuntimeProfile.load(
        ROOT / "experiments/campaigns/ace_review_20260908/runtime.json"
    )
    profile.activate()
    ledger = CAMPAIGN / "ledger.sqlite3"
    Ledger(ledger).create(10.0, ALLOCATIONS)
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(ledger)
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = stage


def load_claims(path: str, sha256: str) -> tuple[ag.AdviceClaim, ...]:
    artifact = ROOT / path
    if digest(artifact) != sha256:
        raise ValueError("grounded artifact changed")
    raw = json.loads(artifact.read_text())
    return pydantic_load(tuple[ag.AdviceClaim, ...], raw["state"]["claims"])


@dataclass
class BoundedConfig(mf.ResponsesAgenticConfig):
    problem_file: str = ""
    artifact: str = ""
    artifact_sha256: str = ""
    runtime_json: str = ""
    partition_sha256: str = ""
    arm_label: str = "integrated"
    admission: bool = True
    focused: bool = True
    restart: bool = True
    money: bool = True
    operation_seconds: float = 60
    verifier_seconds: float = 300
    view_bytes: int = 8192

    def _problem(self) -> tuple[str, str]:
        return self.problem_file, self.bench_name

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1" if self.money else "0"
        pb = Playbook.load(INCUMBENT)
        if pb.sha256() != INCUMBENT_SHA:
            raise ValueError("incumbent playbook changed")
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args={
                "problem_file": self.problem_file,
                "theorem_name": self.bench_name,
                "playbook": pb.render_prompt(),
                "claims": [
                    asdict(c)
                    for c in load_claims(self.artifact, self.artifact_sha256)
                ],
                "turn_budget": self.num_requests,
                "limits": {
                    "seconds": self.operation_seconds,
                    "rpc_calls": 512,
                    "view_bytes": self.view_bytes,
                },
                "verifier_seconds": self.verifier_seconds,
                "admission": self.admission,
                "focused": self.focused,
                "restart": self.restart,
            },
            policy="prove_theorem_grounded_policy",
            policy_args={
                "model_name": self.model_name,
                "reasoning_effort": self.reasoning_effort,
            },
            budget={
                dp.NUM_REQUESTS: self.num_requests,
                dp.DOLLAR_PRICE: 0.10,
                "rocq_seconds": self.verifier_seconds,
            },
        )


def name(config: BoundedConfig, _: object) -> str:
    return f"{config.bench_name}__{config.arm_label}-r64__{config.model_name}__seed{config.seed}"


@dataclass
class GroundedAdaptConfig:
    bench_name: str
    evidence: dict[str, Any]
    source_sha256: str
    model_name: str = "gpt-5.6-luna"
    seed: int = 0

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = adapt_name(self, None)
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
        encoded = json.dumps(self.evidence, sort_keys=True).encode()
        if hashlib.sha256(encoded).hexdigest() != self.source_sha256:
            raise ValueError("adaptation evidence changed")
        return dp.RunStrategyArgs(
            strategy="adapt_grounded_transition",
            args={"evidence": self.evidence},
            policy="grounded_training_policy",
            policy_args={"model_name": self.model_name},
            budget={
                dp.NUM_REQUESTS: 3,
                dp.DOLLAR_PRICE: 0.25,
                "rocq_seconds": 300,
            },
        )


def adapt_name(config: GroundedAdaptConfig, _: object) -> str:
    return f"{config.bench_name}__adapt__{config.model_name}__seed0"


def configs(phase: str) -> list[BoundedConfig]:
    panel = json.loads((CAMPAIGN / "pilot_v2.json").read_text())
    if phase == "validation":
        frozen = json.loads((CAMPAIGN / "frozen.json").read_text())
        problems = mf.load_partition("benchmarks/validationX.txt")
        settings = [
            (bench, "integrated", frozen["switches"]) for bench in problems
        ]
        artifact = frozen["artifact"]
        artifact_sha = frozen["artifact_sha256"]
    elif phase == "pilot":
        problems = mf.load_partition("benchmarks/trainX.txt")
        artifact = panel["artifact"]
        artifact_sha = panel["artifact_sha256"]
        settings: list[tuple[str, str, dict[str, bool]]] = []
        for entry in panel["cases"]:
            mechanism = entry["mechanism"]
            common = {
                "money": False,
                "admission": mechanism in {"focused", "restart", "money"},
                "focused": mechanism in {"restart", "money"},
                "restart": False,
            }
            for treatment in (False, True):
                switches = {**common, mechanism: treatment}
                settings.append(
                    (
                        entry["bench"],
                        f"{mechanism}-{'on' if treatment else 'off'}",
                        switches,
                    )
                )
    else:
        raise ValueError("only pilot and validation are prover phases")
    result: list[BoundedConfig] = []
    runtime = (
        ROOT / "experiments/campaigns/ace_review_20260908/runtime.json"
    ).read_text()
    partition_hash = hashlib.sha256(
        json.dumps(dict(problems), sort_keys=True).encode()
    ).hexdigest()
    for bench, label, switches in settings:
        result.append(
            BoundedConfig(
                bench_name=bench,
                problem_file=problems[bench][0],
                model_name="gpt-5.6-luna",
                temperature=None,
                toolset="core",
                num_requests=64,
                seed=0,
                max_dollar_budget=0.1,
                reasoning_effort="medium",
                artifact=artifact,
                artifact_sha256=artifact_sha,
                runtime_json=runtime,
                partition_sha256=partition_hash,
                arm_label=label,
                admission=switches["admission"],
                focused=switches["focused"],
                restart=switches["restart"],
                money=switches["money"],
            )
        )
    if len(result) != (40 if phase == "validation" else 16):
        raise ValueError("unexpected campaign panel size")
    return result


def main() -> None:
    phase = "pilot"
    for flag in list(sys.argv[1:]):
        if flag.startswith("--phase="):
            phase = flag.split("=", 1)[1]
            sys.argv.remove(flag)
    if phase not in {"adapt", "pilot", "validation"}:
        raise ValueError(
            "phase must be adapt, pilot or validation; no test phase"
        )
    activate("validation" if phase == "validation" else "training")
    context = dp.workspace_execution_context(__file__)
    if phase == "adapt":
        raw = json.loads((CAMPAIGN / "evidence_v2.json").read_text())
        learning: list[GroundedAdaptConfig] = []
        for claim in raw["state"]["claims"][:4]:
            evidence = claim["evidence"]
            sha = hashlib.sha256(
                json.dumps(evidence, sort_keys=True).encode()
            ).hexdigest()
            learning.append(
                GroundedAdaptConfig(evidence["theorem_name"], evidence, sha)
            )
        ol.OmphalosExperiment(
            config_class=GroundedAdaptConfig,
            context=context,
            configs=learning,
            output_dir="experiments/output/ace_bounded_adapt",
            config_naming=adapt_name,
            wait_for_slots=True,
            attempts=1,
        ).run_cli()
    else:
        ol.OmphalosExperiment(
            config_class=BoundedConfig,
            context=context,
            configs=configs(phase),
            output_dir=f"experiments/output/ace_bounded_{phase}",
            config_naming=name,
            wait_for_slots=True,
            attempts=1,
        ).run_cli()


if __name__ == "__main__":
    main()
