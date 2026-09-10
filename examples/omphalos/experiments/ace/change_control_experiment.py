"""Approved 2026-09-10: six trainX states, seed 0; no full problems.

Primary: 6 x F/C Luna medium (12). Diagnostic: 6 x Terra low/medium
(12), reusing the six F applicability phases as Luna controls. All use
fixed demos, Responses, 32768 output tokens and <=4 model requests.
Primary metric: paired all-cell cost. Gate: >=15% lower cost and cost/useful,
no lost useful cell, all four conversions accepted and two negatives refused,
useful continuation in induction and IMO-1983 families, complete accounting.
Two-sided family p<.10 and descriptive 90% intervals are separate from gates.
Terra's three exploratory contrasts use Holm-adjusted p values.

$3 ceiling: primary $1.20, terra $1.20, one infrastructure retry $0.60.
Local caps: Luna $.10, Terra $1; full X caps remain $.10. Teacher budget zero.
No automatic retry, transfer, new seed, adaptation, full train or validation.
Both Codex and Claude Code use this module through the supervised launcher.
"""

from dataclasses import dataclass
import os
import sys
from typing import Any

import delphyne as dp
from ace.ace_playbook import Playbook
from experiments.ace.ace_bounded_experiment import (
    BoundedConfig,
    INCUMBENT,
    INCUMBENT_SHA,
)
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from tools.reports.change_control_report import CAMPAIGN, ROOT, read, digest


@dataclass
class ChangeConfig(BoundedConfig):
    stage: str = "primary"
    state_id: str = ""
    snapshot: dict[str, Any] | None = None
    bank: list[dict[str, Any]] | None = None

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
        pb = Playbook.load(INCUMBENT)
        if pb.sha256() != INCUMBENT_SHA:
            raise ValueError("incumbent changed")
        return dp.RunStrategyArgs(
            strategy="change_episode",
            args={
                "state": self.snapshot,
                "arm": "C" if self.arm_label == "C" else "F",
                "bank": self.bank or [],
                "playbook": pb.render_prompt(),
                "diagnostic_only": self.stage == "terra",
                "request_limit": 4,
                "limits": {
                    "seconds": 60,
                    "rpc_calls": 512,
                    "view_bytes": 8192,
                },
            },
            policy="change_control_policy",
            policy_args={
                "model_name": self.model_name,
                "reasoning_effort": self.reasoning_effort,
                "dollar_limit": self.max_dollar_budget,
            },
            budget={
                "price": self.max_dollar_budget or 0.10,
                "num_requests": 4,
                "rocq_seconds": 300,
            },
        )


def name(config: ChangeConfig, _: object) -> str:
    return (
        f"{config.bench_name}__{config.arm_label}-local"
        f"{config.state_id.rsplit('-', 1)[-1]}-r4-{config.reasoning_effort}__"
        f"{config.model_name}__seed{config.seed}"
    )


def configs(stage: str) -> list[ChangeConfig]:
    if stage not in ("primary", "terra"):
        raise ValueError("full train and validation require separate approval")
    artifact, registration = read("artifact.json"), read("registration.json")
    if digest(CAMPAIGN / "artifact.json") != registration["artifact_sha256"]:
        raise ValueError("artifact changed")
    states = {r["id"]: r["state"] for r in artifact["states"]}
    result: list[ChangeConfig] = []
    for row in registration["schedules"][stage]:
        state = states[row["state"]]
        result.append(
            ChangeConfig(
                bench_name=state["theorem_name"],
                problem_file=state["problem_file"],
                state_id=row["state"],
                snapshot=state,
                bank=artifact["bank"],
                stage=stage,
                arm_label=row["arm"],
                seed=0,
                temperature=None,
                model_name="gpt-5.6-terra"
                if stage == "terra"
                else "gpt-5.6-luna",
                reasoning_effort="low" if row["arm"] == "TL" else "medium",
                toolset="core",
                num_requests=4,
                max_dollar_budget=1.0 if stage == "terra" else 0.10,
                admission=False,
                restart=False,
                money=True,
            )
        )
    return result


def authorize(stage: str) -> None:
    if stage not in ("primary", "terra"):
        raise ValueError("stage not approved")
    for path, sha in read("sealed.json")["execution_hashes"].items():
        if digest(ROOT / path) != sha:
            raise ValueError(f"frozen execution changed: {path}")
    if stage == "terra" and not read("report_primary.json")["complete"]:
        raise ValueError("complete primary panel before Terra")


def main() -> None:
    stage = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--stage=")),
        "primary",
    )
    sys.argv[:] = [a for a in sys.argv if not a.startswith("--stage=")]
    if any("retry" in a for a in sys.argv):
        raise ValueError("automatic/broad retries prohibited")
    if "run" in sys.argv:
        authorize(stage)
        Ledger(CAMPAIGN / "ledger.sqlite3").create(
            3.0, {"primary": 1.2, "terra": 1.2, "retry": 0.6}
        )
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = stage
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")
    ol.OmphalosExperiment(
        config_class=ChangeConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs(stage),
        output_dir=f"experiments/output/change_control_{stage}",
        config_naming=name,
        wait_for_slots=True,
        attempts=1,
    ).run_cli()


if __name__ == "__main__":
    main()
