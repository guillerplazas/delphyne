"""Matched $.20 ACE attribution, validationX only; no held-out dispatch.

Registered from the first validation budget intervention: ACE improves
46/80 to 53/80 but costs 2.144x, failing the original efficiency gate. Keep
that verdict. Add exactly 80 empty-book cells at the SAME $.20 allowance
and reuse the 80 paid ACE-budget cells. No new seed, model, book, prompt,
output limit, session setting, verifier cap or adaptation. The latest user
correction revokes every test plan, including the unrun draft follow-up.

Primary target: >=10% inference savings without pooled or per-replicate
coverage loss. Report cost/solve, failed cells, family-clustered 90% CIs,
two-sided p<.10, uncached same-token sensitivity and preparation. This is
exploratory, reused validation data with historical controls by hours;
no independent confirmation or default promotion.

The SAME $50 ceiling covers both campaigns. Start only after all 400 main
validation cells settle. Main paid work ends there. This ledger receives
$16 (80 x $.20), only if that fits the remaining joint authorization.
Conservative HTTP reservations enforce it. Refuse changes to main spending,
incomplete accounting or unfundable full batches. No retry or extra cell.
Both harnesses use prepare, validation, report and replay; paid work uses
the supervised 24-worker launcher in tmux. Never use the old main verifier.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any

import delphyne as dp
import yaml

from experiments import ace_economy_experiment as base
from experiments import ace_economy_validation as scoped
from experiments.common import omphalos_launch as ol
from experiments.common.ace_learning_io import accounting as ledger_accounting
from runtime.campaign_budget import Ledger
from runtime.model_registry import price_tokens
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)

NAME = "ace_economy_budget_20260916"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != encoded:
            raise ValueError("Immutable follow-up artifact changed: " + name)
    else:
        path.write_text(encoded)


@dataclass(frozen=True)
class Config:
    stage: str
    arm: str
    bench_name: str
    seed: int

    def __post_init__(self) -> None:
        if self.stage != "validation":
            raise ValueError("Only validationX is authorized")

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        problems = scoped.partition(self.stage)
        if self.arm != "agentic":
            raise ValueError("Reuse the paid ACE validation references")
        if self.seed not in (0, 1) or self.bench_name not in problems:
            raise ValueError("Unregistered follow-up cell")
        if base.sha(base.CAMPAIGN / "book.yaml") != base.BOOK_SHA:
            raise ValueError("Frozen v2 book changed")
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args=dict(
                problem_file=problems[self.bench_name],
                theorem_name=self.bench_name,
                playbook="",
                claims=[],
                turn_budget=64,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
                verifier_seconds=300,
                admission=False,
                focused=True,
                restart=False,
            ),
            policy="economy_proof_policy",
            policy_args=dict(
                snapshot_directory=str(
                    CAMPAIGN / "transport" / name(self, None)
                ),
                pause_file=str(CAMPAIGN / "PAUSED"),
                dollar_cap=0.20,
                split_session=False,
            ),
            budget=dict(price=0.20, num_requests=64, rocq_seconds=300),
        )


def name(config: Config, _: object) -> str:
    return (
        f"{config.stage}__{config.arm}__{config.bench_name}__seed{config.seed}"
    )


def directory(config: Config) -> Path:
    return OUTPUT / config.stage / "configs" / name(config, None)


def accounting() -> dict[str, Any]:
    return ledger_accounting(CAMPAIGN)


def main_development_cost() -> float:
    charges = base.accounting()
    if charges["unresolved"] or charges["billing_issues"]:
        raise ValueError("Main campaign must settle before follow-up dispatch")
    if any(not cell.startswith("validation__") for cell in charges["costs"]):
        raise ValueError("Main ledger contains an unauthorized cell")
    return charges["total"]


def prepare() -> None:
    scoped.verify()
    if (CAMPAIGN / "seal.json").exists():
        verify()
        return
    if any(
        not (base.CAMPAIGN / f"batches/{key}.json").exists()
        for key in ("baseline", "budget", "session", "views")
    ):
        raise ValueError("Finish the original development batches first")
    spent = main_development_cost()
    ceiling = 16.0
    if spent + ceiling > 50 + 1e-8:
        raise ValueError("Cannot fund the full new validation panel")
    save(
        "protocol.json",
        dict(
            protocol=__doc__,
            created=datetime.now(timezone.utc).isoformat(),
            main_development_spend=spent,
            main_future_paid_calls=0,
            authorized_partition="validationX",
            new_ceiling=ceiling,
            joint_ceiling=50,
            new_validation_cells=80,
            reused_validation_cells=80,
            new_held_out_cells=0,
            candidate_frozen_before_new_validation=True,
            book_sha256=base.BOOK_SHA,
        ),
    )
    save("runtime.json", base.read("runtime.json"))
    Ledger(CAMPAIGN / "ledger.sqlite3").create(
        ceiling, {"experiments": ceiling}
    )
    save(
        "seal.json",
        {
            str(p.relative_to(ROOT)): base.sha(p)
            for p in (
                Path(__file__),
                CAMPAIGN / "protocol.json",
                CAMPAIGN / "runtime.json",
                base.CAMPAIGN / "validation_seal.json",
                ROOT / "tests/test_economy_budget.py",
            )
        },
    )


def verify() -> None:
    scoped.verify()
    for path, digest in read("seal.json").items():
        if base.sha(ROOT / path) != digest:
            raise ValueError("Follow-up source drift: " + path)
    if (
        abs(
            main_development_cost()
            - read("protocol.json")["main_development_spend"]
        )
        > 1e-8
    ):
        raise ValueError("Main development spending changed after reservation")
    main_total = base.accounting()["total"]
    if main_total + accounting()["ledger"]["liability"] > 50 + 1e-8:
        raise ValueError("Combined authorization exceeded")


def activate(*, events: bool = True) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ.update(
        OMPHALOS_CAMPAIGN_LEDGER=str(CAMPAIGN / "ledger.sqlite3"),
        OMPHALOS_CAMPAIGN_STAGE="experiments",
        OMPHALOS_ESTIMATE_DOLLARS="1",
    )
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )
    else:
        os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)


def configs(stage: str) -> list[Config]:
    if stage != "validation":
        raise ValueError("Only validationX is authorized")
    return [Config(**v) for v in read(f"manifests/{stage}.json")]


def cell_result(config: Config) -> dict[str, Any] | None:
    folder = directory(config)
    state = ol.ground_truth(folder)
    if state not in ("done", "failed"):
        raise ValueError("Missing follow-up cell: " + name(config, None))
    raw: dict[str, Any] = (
        yaml.safe_load((folder / "result.yaml").read_text())
        if (folder / "result.yaml").exists()
        else {}
    )
    diagnostics = (
        str(raw.get("diagnostics", ""))
        + str(raw.get("outcome", {}).get("diagnostics", ""))
        + "".join(p.read_text() for p in folder.glob("exception*.txt"))
    )
    if any(s in diagnostics for s in ("CampaignExhausted", "CampaignPaused")):
        raise ValueError("Administratively censored follow-up cell")
    return raw.get("outcome", {}).get("result") if state == "done" else None


def launch(stage: str) -> None:
    if stage != "validation":
        raise ValueError("Only validationX is authorized")
    verify()
    if (CAMPAIGN / f"batches/{stage}.json").exists():
        return
    jobs = [
        Config("validation", "agentic", n, seed)
        for seed in (0, 1)
        for n in scoped.partition()
    ]
    random.Random(202609162).shuffle(jobs)
    state = accounting()
    needed = 0.20 * sum(
        ol.ground_truth(directory(job)) not in ("done", "failed")
        for job in jobs
    )
    if (
        state["unresolved"]
        or state["billing_issues"]
        or state["ledger"]["liability"] + needed
        > state["ledger"]["ceiling"] + 1e-8
    ):
        raise ValueError("Full follow-up batch is not fundable")
    save(f"manifests/{stage}.json", [asdict(job) for job in jobs])
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.ace_economy_budget_experiment",
            "run-batch",
            stage,
            "run",
            "--max_workers=24",
            "--wait",
        ],
        cwd=ROOT,
        check=False,
    )
    for job in jobs:
        cell_result(job)
    verify()
    save(
        f"batches/{stage}.json",
        dict(
            exit_code=process.returncode,
            states={
                name(job, None): ol.ground_truth(directory(job))
                for job in jobs
            },
        ),
    )


def run_batch(stage: str) -> None:
    if stage != "validation":
        raise ValueError("Only validationX is authorized")
    verify()
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher lacks credential")
    activate()
    ol.OmphalosExperiment(
        config_class=Config,
        configs=configs(stage),
        context=base.context(),
        output_dir=str((OUTPUT / stage).relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def panel(stage: str) -> dict[str, Any]:
    if stage != "validation":
        raise ValueError("Only validationX is authorized")
    verify()
    own, reference = accounting(), base.accounting()
    if own["unresolved"] or own["billing_issues"]:
        raise ValueError("Unresolved follow-up billing")
    observations: dict[str, dict[tuple[str, str], Observation]] = {
        a: {} for a in ("agentic", "ace")
    }
    tokens: dict[str, dict[str, int]] = {
        a: dict(input=0, cached=0, output=0) for a in observations
    }
    for arm in observations:
        for n in scoped.partition():
            for seed in (0, 1):
                if arm == "ace":
                    old = base.Config(stage, "budget", n, seed)
                    result, charges, ident = (
                        base.cell_result(old),
                        reference,
                        base.name(old, None),
                    )
                else:
                    job = Config(stage, arm, n, seed)
                    result, charges, ident = (
                        cell_result(job),
                        own,
                        name(job, None),
                    )
                observations[arm][(n, str(seed))] = Observation(
                    bool(result and result["success"]),
                    charges["costs"].get(ident, 0),
                    result is None,
                )
                for key in tokens[arm]:
                    tokens[arm][key] += (
                        charges["tokens"].get(ident, {}).get(key, 0)
                    )
    expected = list(observations["agentic"])
    families = base.families(stage)
    result = compare(
        observations["agentic"],
        observations["ace"],
        expected,
        families=families,
        cap_a=0.20,
        cap_b=0.20,
    )
    result["cost_p_two_sided"] = cost_cluster_p(
        observations["agentic"], observations["ace"], expected, families
    )
    result["cost_per_solve_agentic"] = (
        result["cost_a"] / result["solved_a"] if result["solved_a"] else None
    )
    result["cost_per_solve_ace"] = (
        result["cost_b"] / result["solved_b"] if result["solved_b"] else None
    )
    result["observed_target"] = (
        result["solved_b"] >= result["solved_a"]
        and result["cost_ratio"] <= 0.9
    )
    result["tokens"] = tokens
    result["uncached_costs"] = {
        arm: price_tokens("gpt-5.6-luna", t["input"], 0, t["output"])
        for arm, t in tokens.items()
    }
    result["per_seed"] = {
        seed: {
            arm: dict(
                solved=sum(
                    o.solved and not o.failed and o.cost <= 0.20
                    for (_, s), o in values.items()
                    if s == seed
                ),
                cost=sum(o.cost for (_, s), o in values.items() if s == seed),
            )
            for arm, values in observations.items()
        }
        for seed in ("0", "1")
        if any(s == seed for _, s in expected)
    }
    return result


def report() -> None:
    verify()
    data = dict(
        validation=panel("validation"),
        new_spend=accounting()["total"],
        main_spend=base.accounting()["total"],
        combined_spend=accounting()["total"] + base.accounting()["total"],
        reused_ace_validation_cells=80,
        preparation_lower_bound=1.36785368,
    )
    (CAMPAIGN / "results.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(data, indent=2))


def replay() -> None:
    from tools.analysis.replay_economy import assemble, replay_batch

    module = sys.modules[__name__]
    replay_batch(module, "validation")
    assemble(module)


def main() -> None:
    action = sys.argv.pop(1)
    if action == "run-batch":
        run_batch(sys.argv.pop(1))
    elif action == "validation":
        launch(action)
    elif action in ("prepare", "report", "replay"):
        {
            "prepare": prepare,
            "report": report,
            "replay": replay,
        }[action]()
    else:
        raise SystemExit("prepare | validation | report | replay")


if __name__ == "__main__":
    main()
