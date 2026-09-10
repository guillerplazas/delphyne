"""Registered applicability campaign, usable from Codex and Claude Code.

Stage A: 12 saved trainX states x R/Q/F/A, seed 0 (48 local episodes).
Stage B only after A passes: eight trainX theorems x R/F/A (24 full cells).
No 40-cell train-only repeat. Validation requires separate user approval:
40 validationX x seeds 0/1 x A/R (160 fresh cells), never testX.

A: >=5/6 correct positives, >=5/6 explicit negative abstentions, no admitted
negative; >=2 useful families; >=2 incremental useful transitions over F
in >=2 families OR equal useful count at >=15% lower cost.
B: >=3 triggered families, >=2 useful repairs; no fewer qualified solves
than R or F and >=15% lower total cost AND cost/solve than both.
Final primary metric: all-cell paired total API cost; practical savings
>=15%, cost/solve >=15% lower, no observed coverage loss. Cost p<.10,
two-sided family clustering; descriptive 90% intervals. Missing/censored
cells prohibit verdicts. Failed attempts stay in all denominators.

Authorized training ceiling $2.50: a $1, b $1.25, retry $.25. At most two
identified infrastructure retries, never logical or serialization retries.
No allocation transfers, extra seeds or automatic ceiling increases.
Teacher/role budget zero. Conditional validation ceiling $4, separately
approved, brings maximum total liability to $6.50. Ceiling is not a target.
"""

from dataclasses import dataclass
import os
import sys
from typing import Any

import delphyne as dp
from experiments.ace.ace_bounded_experiment import (
    BoundedConfig,
    INCUMBENT,
    INCUMBENT_SHA,
)
from ace.ace_playbook import Playbook
import experiments.common.omphalos_launch as ol
import experiments.common.miniF2F_bench as mf
from runtime.campaign_budget import Ledger
from tools.reports.ace_applicability_report import CAMPAIGN, ROOT, read, digest


@dataclass
class ApplicabilityConfig(BoundedConfig):
    phase: str = "a"
    state_id: str = ""
    snapshot: dict[str, Any] | None = None
    bank: list[dict[str, Any]] | None = None

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
        pb = Playbook.load(INCUMBENT)
        if pb.sha256() != INCUMBENT_SHA:
            raise ValueError("incumbent playbook changed")
        if self.phase == "a":
            return dp.RunStrategyArgs(
                strategy="repair_episode",
                args={
                    "state": self.snapshot,
                    "mode": self.arm_label,
                    "bank": self.bank or [],
                    "playbook": pb.render_prompt(),
                    "request_limit": 4,
                },
                policy="applicability_policy",
                policy_args={},
                budget={"price": 0.10, "num_requests": 4, "rocq_seconds": 300},
            )
        # Claims are disabled in the retained reference; avoid accidentally
        # enabling the polished artifact or its admission controls.
        args = dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args={
                "problem_file": self.problem_file,
                "theorem_name": self.bench_name,
                "playbook": pb.render_prompt(),
                "claims": [],
                "turn_budget": 64,
                "limits": {
                    "seconds": 60,
                    "rpc_calls": 512,
                    "view_bytes": 8192,
                },
                "verifier_seconds": 300,
                "admission": False,
                "focused": True,
                "restart": False,
            },
            policy="prove_theorem_grounded_policy",
            policy_args={
                "model_name": "gpt-5.6-luna",
                "reasoning_effort": "medium",
            },
            budget={"price": 0.10, "num_requests": 64, "rocq_seconds": 300},
        )
        if self.arm_label != "R":
            args.args.update(
                {"syntax_mode": self.arm_label, "syntax_bank": self.bank or []}
            )
            args.policy = "applicability_policy"
        return args


def name(config: ApplicabilityConfig, _: object) -> str:
    suffix = (
        f"-local{config.state_id.rsplit('-', 1)[-1]}-r4"
        if config.phase == "a"
        else "-r64"
    )
    return f"{config.bench_name}__{config.arm_label}{suffix}__gpt-5.6-luna__seed{config.seed}"


def configs(phase: str) -> list[ApplicabilityConfig]:
    manifest, artifact = read("registration.json"), read("artifact.json")
    if digest(CAMPAIGN / "artifact.json") != manifest["artifact_sha256"]:
        raise ValueError("artifact changed")
    snapshots = {row["id"]: row for row in artifact["states"]}
    partition = dict(mf.load_partition("benchmarks/trainX.txt")) | dict(
        mf.load_partition("benchmarks/validationX.txt")
    )
    result: list[ApplicabilityConfig] = []
    for row in manifest[f"schedule_{phase}"]:
        state = snapshots[row["state"]]["state"] if phase == "a" else None
        bench = state["theorem_name"] if state else row["bench"]
        result.append(
            ApplicabilityConfig(
                bench_name=bench,
                problem_file=partition[bench][0],
                phase=phase,
                state_id=row.get("state", ""),
                snapshot=state,
                bank=artifact["bank"],
                arm_label=row["arm"],
                seed=row["seed"],
                model_name="gpt-5.6-luna",
                temperature=None,
                reasoning_effort="medium",
                toolset="core",
                num_requests=4 if phase == "a" else 64,
                max_dollar_budget=0.10,
                admission=False,
                restart=False,
                money=True,
            )
        )
    return result


def authorize(phase: str) -> None:
    for path, expected in read("sealed.json")["execution_hashes"].items():
        if digest(ROOT / path) != expected:
            raise ValueError(f"frozen source changed: {path}")
    if phase in ("b", "validation") and not read("report_a.json")["go"]:
        raise ValueError("stage A did not pass")
    if phase == "validation":
        if not read("report_b.json")["go"]:
            raise ValueError("stage B did not pass")
        approval = read("validation_approval.json")
        if approval != {
            "approved": True,
            "ceiling": 4.0,
            "sealed_sha256": digest(CAMPAIGN / "sealed.json"),
        }:
            raise ValueError(
                "separate validation approval does not match freeze"
            )


def main() -> None:
    phase = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--phase=")), "a"
    )
    if phase not in ("a", "b", "validation"):
        raise ValueError("phase must be a, b, or validation")
    sys.argv[:] = [a for a in sys.argv if not a.startswith("--phase=")]
    if any("retry" in a for a in sys.argv):
        raise ValueError(
            "broad retries prohibited; use separately audited cell manifests"
        )
    ledger = CAMPAIGN / (
        "validation_ledger.sqlite3"
        if phase == "validation"
        else "ledger.sqlite3"
    )
    if "run" in sys.argv:
        authorize(phase)
        Ledger(ledger).create(
            4.0, {"validation": 4.0}
        ) if phase == "validation" else Ledger(ledger).create(
            2.5, {"a": 1.0, "b": 1.25, "retry": 0.25}
        )
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(ledger)
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = phase
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "admission.jsonl")
    ol.OmphalosExperiment(
        config_class=ApplicabilityConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs(phase),
        output_dir=f"experiments/output/ace_applicability_{phase}",
        config_naming=name,
        wait_for_slots=True,
        attempts=1,
    ).run_cli()


if __name__ == "__main__":
    main()
