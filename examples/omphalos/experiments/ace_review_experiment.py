"""Registered ACE review campaign (2026-09-08), fresh controls only.

Primary: family-clustered difference in verified solve probability at
actual charged cost <= $0.10, two replicates; improvement requires >=5
percentage points and two-sided p<.05. Failures remain in denominators;
incomplete runs cannot receive verdicts. Development selects one frozen
artifact, then the protected challenge receives one final comparison.

Calibration: baseline at 32/64 requests on trainX, two replicates. Choose
64 only for >=5 points overall and no decline in either replicate.
Development: baseline, frozen x3, repair seed0 and seed1 on validationX.
Seed0 is the repair deployment artifact, not the better training seed.
Tie-break: lower total cost, then incumbent. Terra reference is core/low,
32 requests/$0.30, one replicate on the frozen stratified 32-cell subset.
All runs use the campaign's 32K output limit and no hidden SDK retries.

Example:
 python experiments/ace_review_experiment.py --phase=calibration run --wait
 python experiments/ace_review_experiment.py --phase=development --requests=32 run --wait
"""

# pyright: strict

import hashlib
import json
import os
import random
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import delphyne as dp

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import miniF2F_bench as mf  # noqa: E402
import minif2f_x as x  # noqa: E402
import omphalos_launch as ol  # noqa: E402
from ace_playbook import Playbook  # noqa: E402
from ace_review_benchmark import load as load_challenge  # noqa: E402
from campaign_budget import Ledger  # noqa: E402
from runtime_profiles import RuntimeProfile  # noqa: E402

CAMPAIGN = ROOT / "experiments/campaigns/ace_review_20260908"
ALLOCATIONS = {
    "calibration": 4.0,
    "adaptation": 8.0,
    "development": 8.0,
    "confirmation": 18.0,
    "terra": 7.0,
    "contingency": 5.0,
}


def campaign_profile() -> RuntimeProfile:
    return RuntimeProfile.load(CAMPAIGN / "runtime.json")


def activate_budget(stage: str) -> None:
    campaign_profile().activate()
    ledger = CAMPAIGN / "ledger.sqlite3"
    Ledger(ledger).create(50.0, ALLOCATIONS)
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(ledger)
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = stage


@dataclass
class ReviewConfig(mf.ResponsesAgenticConfig):
    """Fresh identity space: explicit theorem, partition and runtime."""

    problem_file: str = ""
    partition_sha256: str = ""
    runtime_json: str = ""
    playbook_file: str = ""
    playbook_sha256: str = ""
    arm_label: str = "baseline"
    campaign_version: int = 1

    def _problem(self) -> tuple[str, str]:
        return self.problem_file, self.bench_name

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        args = super().instantiate(context)
        args.args["show_definitions"] = True
        if self.playbook_file:
            pb = Playbook.load(ROOT / self.playbook_file)
            if pb.sha256() != self.playbook_sha256:
                raise ValueError("campaign playbook changed")
            args.strategy = "prove_theorem_ace"
            args.policy = "prove_theorem_ace_policy"
            args.args["playbook"] = pb.render_prompt()
            args.args["render_version"] = 3
        return args


def name(cfg: ReviewConfig, _uid: object) -> str:
    return (
        f"{cfg.bench_name}__{cfg.arm_label}-r{cfg.num_requests}"
        f"__{cfg.model_name}__seed{cfg.seed}"
    )


def configs_for(
    phase: str,
    requests: int,
    arm: str,
    workers: int | None = None,
) -> list[ReviewConfig]:
    profile = campaign_profile()
    if workers is not None and not 1 <= workers <= profile.streams:
        raise ValueError("workers exceed the registered stream ceiling")
    runtime = json.dumps(asdict(profile), sort_keys=True)
    challenge = load_challenge()
    if phase == "calibration":
        problems = dict(x.TRAINX_PROBLEMS)
        arms = {"baseline": ""}
        counts = (32, 64)
    elif phase == "development":
        problems = dict(x.VALIDATIONX_PROBLEMS)
        arms = {
            "baseline": "",
            "x3": "ace_x3_offline.yaml",
            "repair0": "ace_review_repair_s0.yaml",
            "repair1": "ace_review_repair_s1.yaml",
        }
        counts = (requests,)
    elif phase in {"confirmation", "terra"}:
        selection_path = CAMPAIGN / "selection.json"
        if not selection_path.exists():
            raise ValueError(
                "freeze development selection before confirmation"
            )
        selection: Any = json.loads(selection_path.read_text())
        selected_requests = int(selection["requests"])
        rows: dict[str, Any] = challenge["problems"]
        allowed: list[str] = (
            challenge["terra_subset"] if phase == "terra" else list(rows)
        )
        problems = {n: (rows[n]["file"], rows[n]["theorem"]) for n in allowed}
        arms = {"baseline": "", "selected": selection["playbook"]}
        counts = (selected_requests,)
        if phase == "terra":
            arms, counts = {"terra": ""}, (32,)
    else:
        raise ValueError(f"unknown phase {phase}")
    if arm != "all":
        if arm not in arms:
            raise ValueError(f"arm must be one of {list(arms)}")
        arms = {arm: arms[arm]}
    partition_hash = hashlib.sha256(
        json.dumps(problems, sort_keys=True).encode()
    ).hexdigest()
    configs: list[ReviewConfig] = []
    for label, playbook in arms.items():
        path = f"experiments/playbooks/{playbook}" if playbook else ""
        pb_sha = Playbook.load(ROOT / path).sha256() if path else ""
        for count in counts:
            for seed in (0,) if phase == "terra" else (0, 1):
                for bench, (file, _) in problems.items():
                    configs.append(
                        ReviewConfig(
                            bench_name=bench,
                            problem_file=file,
                            model_name="gpt-5.6-terra"
                            if phase == "terra"
                            else x.X_MODEL,
                            toolset="core",
                            temperature=None,
                            num_requests=count,
                            seed=seed,
                            max_dollar_budget=0.30
                            if phase == "terra"
                            else 0.10,
                            reasoning_effort="low"
                            if phase == "terra"
                            else "medium",
                            partition_sha256=partition_hash,
                            runtime_json=runtime,
                            playbook_file=path,
                            playbook_sha256=pb_sha,
                            arm_label=label,
                        )
                    )
    random.Random(20260908).shuffle(configs)
    return configs


def take_flag(key: str, default: str) -> str:
    prefix = f"--{key}="
    found = [a for a in sys.argv[1:] if a.startswith(prefix)]
    if len(found) > 1:
        raise ValueError(f"duplicate {prefix} flag")
    if found:
        sys.argv.remove(found[0])
        return found[0][len(prefix) :]
    return default


def experiment(
    phase: str,
    requests: int = 32,
    arm: str = "all",
    workers: int | None = None,
) -> ol.OmphalosExperiment[ReviewConfig]:
    return ol.OmphalosExperiment(
        config_class=ReviewConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs_for(phase, requests, arm, workers),
        output_dir=f"experiments/output/ace_review_{phase}",
        config_naming=name,
        wait_for_slots=True,
    )


def main() -> None:
    phase = take_flag("phase", "calibration")
    requests = int(take_flag("requests", "32"))
    arm = take_flag("arm", "all")
    budget_stage = take_flag("budget_stage", phase)
    if budget_stage not in {phase, "contingency"}:
        raise ValueError(
            "only the phase allocation or contingency may fund a run"
        )
    activate_budget(budget_stage)
    worker_flags = [a for a in sys.argv if a.startswith("--max_workers=")]
    workers = int(worker_flags[0].split("=", 1)[1]) if worker_flags else None
    if "run" in sys.argv and not worker_flags:
        sys.argv.append(f"--max_workers={campaign_profile().workers}")
    experiment(phase, requests, arm, workers).run_cli()


if __name__ == "__main__":
    main()
