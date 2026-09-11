"""Approved $10 mechanism campaign, 2026-09-10; both agent harnesses.

24 local cells: six trainX states x F/C x full/explicit continuation, seed 0.
144 new full trainX cells: S/C/R each 40, E 24; reuse E's 16 incumbent-book
xhigh cells and 40 flagship train controls. S changes the response contract;
C adds checked change/set/nra; R adds verified-progress output recovery;
E changes only prover effort. Freeze one winner before validation: 40 x two
seeds = 80 new cells, with 80 historical flagship controls. Maximum 248 new
cells, no outcome pruning within stages, no automatic default promotion.

Primary endpoint: qualified solves at actual cost <=$.10. Practical value:
extra solves at <=1.20 total cost and no worse cost/solve, or equal coverage
at lower cost. Rank qualifying arms by coverage then cost. If none qualifies,
one exploratory contender may lose <=1 train solve while improving both
cost and cost/solve >=10%; label the trade-off. Otherwise stop after train.
Two-sided family p<.10 and 90% intervals describe support, not pilot gates.
No protected outcomes, new advice, extra seeds, combinations or broad retries.

CLI: prepare | run --stage=local|training|validation --max_workers=24 --wait
     report --stage=local|training|validation | status
"""

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import csv
import json
import os
from pathlib import Path
import random
import sys
from typing import Any

import delphyne as dp
from delphyne.utils.typing import pydantic_load
import yaml

from ace.change_progress import audit_progress
import ace.ace_applicability as aa
from experiments.ace.ace_bounded_experiment import BoundedConfig
from experiments.ace.ace_contender_benchmark import reference_inventory
from experiments.common import ace_model_campaign as old
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.runtime_profiles import RuntimeProfile
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from tools.reports.change_control_report import result_of

ROOT = old.ROOT
CAMPAIGN = ROOT / "experiments/campaigns/ace_mechanisms_20260910"
OUTPUT = ROOT / "experiments/output/ace_mechanisms_20260910"
ALLOCATIONS = {"local": 0.5, "training": 4.5, "validation": 4.5, "retry": 0.5}
ARMS = ("S", "C", "R", "E")


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, data: object) -> None:
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    old.write_new(CAMPAIGN / name, data)


@dataclass
class MechanismConfig(BoundedConfig):
    phase: str = "training"
    continuation: bool = False
    checked_repair: bool = False
    verified_recovery: bool = False
    state_id: str = ""
    snapshot: dict[str, Any] | None = None
    bank: list[dict[str, Any]] | None = None
    local_arm: str = ""

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if asdict(self) not in read(f"{self.phase}_manifest.json"):
            raise ValueError("cell outside frozen campaign manifest")
        result = super().instantiate(context)
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        if self.phase == "local":
            result.strategy = "change_episode"
            result.args = dict(
                state=self.snapshot,
                arm=self.local_arm,
                bank=self.bank or [],
                playbook=result.args["playbook"],
                request_limit=4,
                continuation=self.continuation,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
            )
            result.policy = (
                "continuation_policy"
                if self.continuation
                else "change_control_policy"
            )
            result.policy_args = dict(
                model_name=self.model_name,
                reasoning_effort=self.reasoning_effort,
            )
            if self.continuation:
                result.policy_args.update(turn_budget=4, typed_limits=True)
        elif self.arm_label != "E":
            result.args.update(
                continuation=self.continuation,
                checked_repair=self.checked_repair,
                verified_recovery=self.verified_recovery,
            )
            result.policy = "continuation_policy"
            result.policy_args = dict(
                model_name=self.model_name,
                reasoning_effort=self.reasoning_effort,
                recovery=self.verified_recovery,
            )
        return result


def name(c: MechanismConfig, _: object) -> str:
    return f"{c.bench_name}__{c.phase}-{c.arm_label}__{c.model_name}__seed{c.seed}"


def proof_config(
    bench: str, arm: str, phase: str, seed: int = 0
) -> MechanismConfig:
    c = old.proof_config(
        bench,
        "xhigh" if arm == "E" else "medium",
        old.read("registration.json")["incumbent"],
        phase,
        seed=seed,
        label=arm,
    )
    result = pydantic_load(MechanismConfig, asdict(c))
    result.continuation = arm != "E"
    result.checked_repair = arm in ("C", "R")
    result.verified_recovery = arm == "R"
    return result


def hash_paths(paths: list[Path]) -> dict[str, str]:
    return {str(p.relative_to(ROOT)): old.digest(p) for p in paths}


def effective(c: BoundedConfig) -> dp.RunStrategyArgs:
    args = BoundedConfig.instantiate(c, None)
    args.args.pop("claims")  # Inactive in every frozen flagship/E control.
    return args


def prepare() -> None:
    if (CAMPAIGN / "registration.json").exists():
        verify()
        return
    reg = old.read("registration.json")
    refs, deps = reference_inventory()
    proof_output = old.OUTPUT / "proof"
    records = {r.name: r for r in old.cells_of_run(proof_output)}
    costs = old.accounting()["costs"]
    reuse: list[dict[str, Any]] = []
    for bench in reg["panels"]["source"] + reg["panels"]["screen"]:
        source = old.proof_config(bench, "xhigh", reg["incumbent"], "prover")
        n = old.proof_name(source, None)
        r = records[n]
        actual = pydantic_load(BoundedConfig, r.params)
        if effective(actual) != effective(source) or r.platform_failed:
            raise ValueError(f"incompatible E reference: {n}")
        if abs(costs[n] - r.cost) > 1e-7:
            raise ValueError("E receipt mismatch")
        reuse.append(
            dict(
                theorem=bench,
                seed=0,
                name=n,
                source=str(proof_output.relative_to(ROOT)),
                solved=r.solved,
                failed=r.platform_failed,
                cost=costs[n],
            )
        )
        deps.update(
            hash_paths(
                [
                    proof_output / "configs" / n / p
                    for p in ("cache.yaml", "result.yaml")
                ]
            )
        )
    val_output = ROOT / "experiments/output/ace_polish_validation"
    val_records = {r.name: r for r in old.cells_of_run(val_output)}
    val_costs: dict[str, float] = defaultdict(float)
    with (
        ROOT / "experiments/campaigns/ace_polish_20260909/receipts.csv"
    ).open() as f:
        for row in csv.DictReader(f):
            val_costs[row["cell"]] += float(row["charged"])
    for bench in reg["validation"]:
        n = f"{bench}__reference-r64__{old.LUNA}__seed1"
        r = val_records[n]
        expected = old.proof_config(
            bench, "medium", reg["incumbent"], "validation", seed=1
        )
        if effective(pydantic_load(BoundedConfig, r.params)) != effective(
            expected
        ):
            raise ValueError(f"incompatible seed-1 reference: {n}")
        if r.platform_failed or abs(r.cost - val_costs[n]) > 1e-7:
            raise ValueError(f"incomplete reference accounting: {n}")
        refs["validation"].append(
            dict(
                theorem=bench,
                seed=1,
                name=n,
                source=str(val_output.relative_to(ROOT)),
                solved=r.solved,
                failed=r.platform_failed,
                cost=val_costs[n],
            )
        )
        deps.update(
            hash_paths(
                [
                    val_output / "configs" / n / p
                    for p in ("cache.yaml", "result.yaml")
                ]
            )
        )
    refs["E"] = reuse
    save("references.json", refs)
    artifact_path = (
        ROOT / "experiments/campaigns/change_control_20260910/artifact.json"
    )
    artifact = json.loads(artifact_path.read_text())
    save("local_artifact.json", artifact)
    local: list[MechanismConfig] = []
    for row in artifact["states"]:
        for arm in ("F", "C"):
            for contract in ("full", "explicit"):
                c = proof_config(row["state"]["theorem_name"], "S", "training")
                c.phase, c.state_id, c.snapshot = (
                    "local",
                    row["id"],
                    row["state"],
                )
                c.bank, c.local_arm = artifact["bank"], arm
                c.arm_label = f"{arm}-{contract}"
                c.num_requests, c.continuation = 4, contract == "explicit"
                local.append(c)
    reused = {r["theorem"] for r in reuse}
    training = [
        proof_config(b, a, "training")
        for b in reg["train"]
        for a in ARMS
        if not (a == "E" and b in reused)
    ]
    assert len(local) == 24 and len(training) == 144 and len(reuse) == 16
    rng = random.Random(20260913)
    for stage, configs in (("local", local), ("training", training)):
        rng.shuffle(configs)
        save(f"{stage}_manifest.json", [asdict(c) for c in configs])
    save("runtime.json", old.read("runtime.json"))
    deps.update(old.source_hashes())
    deps.update(
        hash_paths(
            [
                Path(__file__),
                artifact_path,
                ROOT / "experiments/ace/ace_contender_benchmark.py",
                ROOT / "tools/reports/change_control_report.py",
                ROOT / "tests/test_ace_mechanisms.py",
                ROOT / "demos/continuation_protocol.demo.yaml",
                ROOT / "Makefile",
                *[
                    CAMPAIGN / f
                    for f in (
                        "local_manifest.json",
                        "training_manifest.json",
                        "references.json",
                        "runtime.json",
                        "local_artifact.json",
                        "README.md",
                    )
                ],
            ]
        )
    )
    for c in local + training:
        deps.update(
            hash_paths(
                [
                    ROOT / c.problem_file,
                    ROOT / c.playbook_file,
                    ROOT / c.artifact,
                ]
            )
        )
    save(
        "registration.json",
        dict(
            authorization="Guille: Implement the plan; balanced criteria and $10",
            ceiling=10.0,
            allocations=ALLOCATIONS,
            max_new_cells=248,
            families=reg["families"],
            train=reg["train"],
            validation=reg["validation"],
            dependencies=deps,
            historical_controls=True,
            default_changed=False,
            max_infrastructure_retries=1,
            selection_rule=__doc__,
        ),
    )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(10.0, ALLOCATIONS)


def verify() -> None:
    old.verify_hashes(read("registration.json")["dependencies"])
    if (CAMPAIGN / "selection.json").exists():
        selection = read("selection.json")
        if selection["arm"] is not None:
            if (
                old.digest(CAMPAIGN / "validation_manifest.json")
                != selection["manifest_sha256"]
            ):
                raise ValueError("validation manifest changed")


def accounting() -> dict[str, Any]:
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,usage,cell,stage FROM receipts"
        ).fetchall()
    costs: dict[str, float] = defaultdict(float)
    stages: dict[str, float] = defaultdict(float)
    unresolved: list[str] = []
    for key, model, created, charged, usage, cell, stage in rows:
        if charged is None:
            unresolved.append(key)
            continue
        u = json.loads(usage or "{}")
        if charged or "input_tokens" in u:
            actual = old.price_tokens(
                model,
                u["input_tokens"],
                u.get("input_tokens_details", {}).get("cached_tokens", 0),
                u.get("output_tokens", 0),
                on=datetime.fromtimestamp(created, timezone.utc).date(),
            )
            if abs(actual - charged) > 1e-8:
                raise ValueError("receipt token mismatch")
        costs[cell] += charged
        stages[stage] += charged
    return dict(
        costs=dict(costs),
        stages=dict(stages),
        total=sum(costs.values()),
        unresolved=unresolved,
        requests=len(rows),
        ledger=ledger.summary(),
    )


def configs(stage: str) -> list[MechanismConfig]:
    return [
        pydantic_load(MechanismConfig, c)
        for c in read(f"{stage}_manifest.json")
    ]


def observations(
    stage: str, arm: str, acct: dict[str, Any]
) -> dict[tuple[str, str], Observation]:
    if acct["unresolved"]:
        raise ValueError("unresolved charges; no verdict")
    records = {r.name: r for r in old.cells_of_run(OUTPUT / stage)}
    result: dict[tuple[str, str], Observation] = {}
    for c in configs(stage):
        if c.arm_label != arm:
            continue
        n = name(c, None)
        if n not in records:
            raise ValueError(f"missing cell: {n}; no verdict")
        r = records[n]
        directory = OUTPUT / stage / "configs" / n
        if any(
            "CampaignExhausted" in p.read_text()
            for p in directory.glob("exception*.txt")
        ):
            raise ValueError("administratively censored panel; no verdict")
        cost = acct["costs"].get(n, 0.0)
        if abs(cost - r.cost) > 1e-7:
            raise ValueError(f"receipt/cache mismatch: {n}")
        cache = directory / "cache.yaml"
        if cache.exists():
            entries: Any = (
                yaml.load(cache.read_text(), Loader=yaml.CSafeLoader) or []
            )
            for row in entries:
                opts = row["input"]["request"].get("options", {})
                if opts.get("model") in (None, "__compute__"):
                    continue
                if (
                    opts.get("model") != c.model_name
                    or opts.get("reasoning_effort") != c.reasoning_effort
                ):
                    raise ValueError(f"actual model drift: {n}")
                allowed = (32768, 4096) if c.verified_recovery else (32768,)
                if opts.get("max_completion_tokens") not in allowed:
                    raise ValueError(f"actual output allowance drift: {n}")
        if r.cell in result:
            raise ValueError("duplicate cell")
        result[r.cell] = Observation(r.solved, cost, r.platform_failed)
    return result


def historical(key: str) -> dict[tuple[str, str], Observation]:
    return {
        (r["theorem"], str(r["seed"])): Observation(
            r["solved"], r["cost"], r["failed"]
        )
        for r in read("references.json")[key]
    }


def select(metrics: dict[str, Any]) -> tuple[str | None, str]:
    baseline = metrics["reference"]
    good = [
        a
        for a in ARMS
        if (
            metrics[a]["solves"] > baseline["solves"]
            and old.eligible(metrics[a], baseline, 1)
        )
        or (
            metrics[a]["solves"] == baseline["solves"]
            and metrics[a]["cost"] < baseline["cost"]
        )
    ]
    if good:
        return min(
            good, key=lambda a: (-metrics[a]["solves"], metrics[a]["cost"], a)
        ), "practical improvement"
    exploratory = [
        a
        for a in ARMS
        if metrics[a]["solves"] >= baseline["solves"] - 1
        and metrics[a]["cost"] <= 0.9 * baseline["cost"]
        and metrics[a]["cost_per_solve"] is not None
        and metrics[a]["cost_per_solve"] <= 0.9 * baseline["cost_per_solve"]
    ]
    if exploratory:
        return min(
            exploratory,
            key=lambda a: (-metrics[a]["solves"], metrics[a]["cost"], a),
        ), "exploratory coverage trade-off"
    return None, "no contender meets the registered follow-up rule"


def report(stage: str) -> None:
    verify()
    if (CAMPAIGN / f"{stage}_report.json").exists():
        print(json.dumps(read(f"{stage}_report.json"), indent=2))
        return
    acct = accounting()
    report_data: dict[str, Any]
    if stage == "local":
        rows: list[dict[str, Any]] = []
        states = {r["id"]: r for r in read("local_artifact.json")["states"]}
        for c in configs(stage):
            observations(
                stage, c.arm_label, acct
            )  # Complete accounting first.
            result, repair = result_of(
                OUTPUT / stage / "configs" / name(c, None)
            )
            state = pydantic_load(aa.RepairState, states[c.state_id]["state"])
            checked = (
                result.continuation.checked
                if result and result.continuation
                else None
            )
            audit = audit_progress(state, checked) if checked else None
            useful = bool(
                checked
                and (checked.feedback.success or (audit and audit.useful))
            )
            rows.append(
                dict(
                    cell=name(c, None),
                    state_id=c.state_id,
                    arm=c.arm_label,
                    cost=acct["costs"].get(name(c, None), 0.0),
                    useful=useful,
                    decision_correct=bool(
                        repair
                        and repair.executed == states[c.state_id]["positive"]
                    ),
                    continuation_status=result.continuation.status
                    if result and result.continuation
                    else None,
                    progress=asdict(audit) if audit else None,
                )
            )
        report_data = dict(
            complete=True,
            rows=rows,
            accounting=acct,
            metrics={
                a: dict(
                    cells=sum(r["arm"] == a for r in rows),
                    useful=sum(r["useful"] for r in rows if r["arm"] == a),
                    cost=sum(r["cost"] for r in rows if r["arm"] == a),
                )
                for a in ("F-full", "C-full", "F-explicit", "C-explicit")
            },
        )
    else:
        baseline = historical(stage)
        selected = (
            ARMS if stage == "training" else (read("selection.json")["arm"],)
        )
        arms = {a: observations(stage, a, acct) for a in selected}
        if stage == "training":
            if set(arms["E"]) & set(historical("E")):
                raise ValueError("duplicate E cells")
            arms["E"].update(historical("E"))
        if any(set(v) != set(baseline) for v in arms.values()):
            raise ValueError("incomplete expected problem-seed panel")
        arms["reference"] = baseline
        metrics = {a: old.metrics(obs) for a, obs in arms.items()}
        pairs: dict[str, Any] = {}
        for a in selected:
            pair = compare(
                baseline,
                arms[a],
                list(baseline),
                families=read("registration.json")["families"],
            )
            pair.pop("verdict")
            pair["cost_p_two_sided"] = cost_cluster_p(
                baseline,
                arms[a],
                list(baseline),
                families=read("registration.json")["families"],
            )
            pairs[a] = pair
        report_data = dict(
            complete=True,
            metrics=metrics,
            comparisons=pairs,
            accounting=acct,
            cells={
                a: {f"{b}__seed{s}": asdict(o) for (b, s), o in obs.items()}
                for a, obs in arms.items()
            },
            per_seed={
                str(s): {
                    a: old.metrics(
                        {k: v for k, v in obs.items() if k[1] == str(s)}
                    )
                    for a, obs in arms.items()
                }
                for s in ((0,) if stage == "training" else (0, 1))
            },
            default_changed=False,
        )
        if stage == "training":
            arm, reason = select(metrics)
            selection: dict[str, Any] = dict(
                arm=arm, reason=reason, metrics=metrics
            )
            if arm is not None:
                val = [
                    proof_config(b, arm, "validation", s)
                    for b in read("registration.json")["validation"]
                    for s in (0, 1)
                ]
                random.Random(20260914).shuffle(val)
                assert len(val) == 80
                save("validation_manifest.json", [asdict(c) for c in val])
                selection["manifest_sha256"] = old.digest(
                    CAMPAIGN / "validation_manifest.json"
                )
            save("selection.json", selection)
    save(f"{stage}_report.json", report_data)
    with (
        Ledger(CAMPAIGN / "ledger.sqlite3").connect() as db,
        (CAMPAIGN / "receipts.csv").open("w") as f,
    ):
        cur = db.execute("SELECT * FROM receipts ORDER BY created,id")
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([d[0] for d in cur.description])
        writer.writerows(cur.fetchall())
    print(
        json.dumps(
            {
                k: v
                for k, v in report_data.items()
                if k not in ("cells", "rows")
            },
            indent=2,
        )
    )


def main() -> None:
    stage = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--stage=")),
        "local",
    )
    sys.argv[:] = [a for a in sys.argv if not a.startswith("--stage=")]
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if command == "prepare":
        prepare()
        return
    if command == "status":
        print(json.dumps(accounting(), indent=2))
        return
    if stage not in ("local", "training", "validation"):
        raise ValueError("unknown stage")
    if command == "report":
        report(stage)
        return
    verify()
    if command == "run":
        if (CAMPAIGN / f"{stage}_report.json").exists():
            raise ValueError("completed stage; no new calls")
        prerequisite = {
            "training": "local_report.json",
            "validation": "training_report.json",
        }.get(stage)
        if prerequisite and not (CAMPAIGN / prerequisite).exists():
            raise ValueError("prerequisite stage incomplete")
    if any("retry" in a for a in sys.argv):
        raise ValueError(
            "retry requires a frozen single infrastructure-cell manifest"
        )
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = stage
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")
    ol.OmphalosExperiment(
        config_class=MechanismConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs(stage),
        output_dir=str((OUTPUT / stage).relative_to(ROOT)),
        config_naming=name,
        wait_for_slots=True,
        attempts=1,
    ).run_cli()


if __name__ == "__main__":
    main()
