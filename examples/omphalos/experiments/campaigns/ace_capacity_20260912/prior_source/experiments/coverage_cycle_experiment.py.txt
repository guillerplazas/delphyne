"""Authorized four-arm development-only cycle: 8 x 40 cells, seed 0.

Both harnesses: python -m experiments.coverage_cycle_experiment
prepare | seal | run --stage=training|validation --arm=D2|E2|S|H
report --stage=training|validation | status. No test stage exists.
"""

# ruff: noqa: E402 -- guard must precede imports with potential I/O
from runtime.development_only import install

install()

from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

import delphyne as dp
import yaml
from ace.ace_playbook import Playbook
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.model_registry import price_tokens
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile
import runtime.pytanque_utils as pt
from tools.analysis.cell_records import cells_of_run
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)

CAMPAIGN = ROOT / "experiments/campaigns/coverage_cycle_20260911"
OUTPUT = ROOT / "experiments/output/coverage_cycle_20260911"
ARMS = ("D2", "E2", "S", "H")
STAGES = ("training", "validation")
CARRY = 3.70503274
CEILING = 25 - CARRY
BANK = "experiments/campaigns/coverage_cycle_20260911/demo_bank.json"
INCUMBENT = ROOT / "experiments/playbooks/ace_x3_offline.yaml"
INCUMBENT_SHA = (
    "1e4aec7dbbe80e7a320db17a7c18fe0859bfc00898837c297be248a05dbde067"
)


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name: str, value: Any) -> None:
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    with (CAMPAIGN / name).open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def partition(stage: str) -> dict[str, str]:
    if stage not in STAGES:
        raise ValueError("Only training and validation are allowed")
    filename = "trainX.txt" if stage == "training" else "validationX.txt"
    rows = [
        s.strip()
        for s in (ROOT / "benchmarks" / filename).read_text().splitlines()
        if s.strip() and not s.startswith("#")
    ]
    result = {Path(s).stem: s for s in rows}
    assert len(result) == 40
    return result


def family_map() -> dict[str, str]:
    problems = partition("training") | partition("validation")
    parent = {n: n for n in problems}

    def find(n: str) -> str:
        while parent[n] != n:
            n = parent[n]
        return n

    templates: dict[str, str] = {}
    for name, file in sorted(problems.items()):
        statement = re.sub(
            r"\b\d+\b",
            "NUMBER",
            " ".join(pt.parse_problem(file, True).theorem_statement.split()),
        )
        keys = [statement]
        if name.startswith(("imo_", "aime_", "amc")):
            keys.append(re.sub(r"(_p\d+)_\d+$", r"\1", name))
        for key in keys:
            if key in templates:
                parent[find(name)] = find(templates[key])
            else:
                templates[key] = name
    return {n: find(n) for n in problems}


def context(arm: str = "") -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    return replace(
        ctx,
        modules=(*ctx.modules, "prove_coverage", "prove_coverage_cycle"),
        demo_files=(*ctx.demo_files, ROOT / "demos/coverage.demo.yaml")
        if arm == "D2"
        else ctx.demo_files,
    )


@dataclass
class CycleConfig:
    bench_name: str
    problem_file: str
    stage: str
    arm: str
    model_name: str = "gpt-5.6-luna"
    seed: int = 0

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if asdict(self) not in read("manifest.json"):
            raise ValueError("Unregistered cell")
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
        if digest(INCUMBENT) != INCUMBENT_SHA:
            raise ValueError("Playbook drift")
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args=dict(
                problem_file=self.problem_file,
                theorem_name=self.bench_name,
                playbook=Playbook.load(INCUMBENT).render_prompt(),
                claims=[],
                turn_budget=64,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
                verifier_seconds=300,
                admission=False,
                focused=True,
                restart=False,
                **({"exploration_v2": True} if self.arm == "E2" else {}),
                **({"checked_repair": True} if self.arm == "S" else {}),
                **({"compact_history": True} if self.arm == "H" else {}),
            ),
            policy="cycle_policy",
            policy_args=dict(
                model_name=self.model_name,
                reasoning_effort="medium",
                **({"bank_file": BANK} if self.arm == "D2" else {}),
            ),
            budget={"price": 0.10, "num_requests": 64, "rocq_seconds": 300},
        )


def name(c: CycleConfig, _: object) -> str:
    return f"{c.bench_name}__{c.stage}-{c.arm}__{c.model_name}__seed{c.seed}"


def configs(stage: str, arm: str) -> list[CycleConfig]:
    if stage not in STAGES or arm not in ARMS:
        raise ValueError("Unsupported stage/arm")
    result = [
        CycleConfig(**r)
        for r in read("manifest.json")
        if r["stage"] == stage and r["arm"] == arm
    ]
    assert len(result) == 40
    return result


def prepare() -> None:
    refs = json.loads(
        (
            ROOT / "experiments/campaigns/coverage_20260911/references.json"
        ).read_text()
    )
    save("references.json", {s: refs[s] for s in STAGES})
    save(
        "runtime.json",
        json.loads(
            (
                ROOT / "experiments/campaigns/coverage_20260911/runtime.json"
            ).read_text()
        ),
    )
    save(
        "manifest.json",
        [
            asdict(CycleConfig(n, p, s, a))
            for s in STAGES
            for a in ARMS
            for n, p in partition(s).items()
        ],
    )
    # Read only the six training demos, not the old mixed-partition bank.
    demos = yaml.safe_load((ROOT / "demos/coverage.demo.yaml").read_text())
    operations = {
        3: ("sum_unfold", 2),
        11: ("product_induction", 2),
        6: ("numeral_coercion", 2),
        19: ("recurrence_coercion", 4),
        20: ("trig_identity", 3),
        22: ("sqrt_side_condition", 3),
    }
    bank: list[dict[str, Any]] = []
    for d in demos:
        if "query" not in d:
            continue
        ident = d["demonstration"]
        i = int(ident.split("-")[-1])
        op, specificity = operations[i]
        theorem = d["args"]["spec"]["theorem_name"]
        assert theorem in partition("training")
        bank.append(
            dict(
                id=ident,
                theorem=theorem,
                query=d["query"],
                operation=op,
                specificity=specificity,
            )
        )
    assert len(bank) == 6
    save("demo_bank.json", dict(examples=bank, families=family_map()))


def seal() -> None:
    paths = [Path(__file__), ROOT / "delphyne.yaml", INCUMBENT]
    paths += [
        ROOT / n
        for n in (
            "prove_grounded.py",
            "prove_coverage.py",
            "prove_coverage_cycle.py",
            "prove_continuation.py",
            "prove_agentic.py",
            "prove_ace.py",
        )
    ]
    for directory, pattern in [
        ("runtime", "*.py"),
        ("ace", "*.py"),
        ("prompts", "*.jinja"),
    ]:
        paths += list((ROOT / directory).rglob(pattern))
    paths += list(context("D2").demo_files)
    paths += [
        ROOT / "demos/coverage_cycle.demo.yaml",
        ROOT / "tools/reports/coverage_cycle_audit.py",
        CAMPAIGN / "preflight.json",
    ]
    paths += [
        CAMPAIGN / n
        for n in (
            "manifest.json",
            "references.json",
            "runtime.json",
            "demo_bank.json",
        )
    ]
    paths += [
        ROOT / "benchmarks" / n for n in ("trainX.txt", "validationX.txt")
    ]
    paths += [ROOT / p for s in STAGES for p in partition(s).values()]
    for s in STAGES:
        assert len(read("references.json")[s]) == 40
        for r in read("references.json")[s]:
            assert r["effective_config_matches"] and r["seed"] == 0
            paths += [
                ROOT / r["source"] / "configs" / r["name"] / n
                for n in ("cache.yaml", "result.yaml")
            ]
    save(
        "registration.json",
        dict(
            authorization="Guille: implement four isolated hints 126/127/122/109; no testX access",
            carry_in=CARRY,
            ceiling=CEILING,
            cells=320,
            runs=8,
            seed=0,
            arms=ARMS,
            families=family_map(),
            dependencies={str(p.relative_to(ROOT)): digest(p) for p in paths},
            default_changed=False,
            max_retries=4,
        ),
    )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(
        CEILING, {"benchmark": CEILING - 1, "retry": 1}
    )


def verify() -> None:
    for p, expected in read("registration.json")["dependencies"].items():
        if digest(ROOT / p) != expected:
            raise ValueError(f"Frozen dependency changed: {p}")


def accounting() -> dict[str, Any]:
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    costs: dict[str, float] = defaultdict(float)
    unresolved: list[str] = []
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,usage,cell FROM receipts"
        ).fetchall()
    for ident, model, created, charged, usage, cell in rows:
        if charged is None:
            unresolved.append(ident)
            continue
        u = json.loads(usage or "{}")
        if charged or "input_tokens" in u:
            actual = price_tokens(
                model,
                u["input_tokens"],
                u.get("input_tokens_details", {}).get("cached_tokens", 0),
                u.get("output_tokens", 0),
                on=datetime.fromtimestamp(created, timezone.utc).date(),
            )
            if abs(actual - charged) > 1e-8:
                raise ValueError("Receipt price mismatch")
        costs[cell] += charged
    return dict(
        costs=dict(costs),
        total=sum(costs.values()),
        requests=len(rows),
        unresolved=unresolved,
        ledger=ledger.summary(),
    )


def observations(
    stage: str, arm: str, acct: dict[str, Any]
) -> dict[tuple[str, str], Observation]:
    run = OUTPUT / stage / arm
    records = {r.name: r for r in cells_of_run(run)}
    result: dict[tuple[str, str], Observation] = {}
    for c in configs(stage, arm):
        n = name(c, None)
        if n not in records:
            raise ValueError(f"Missing cell: {n}")
        r = records[n]
        for p in (run / "configs" / n).glob("exception*.txt"):
            if "CampaignExhausted" in p.read_text():
                raise ValueError("Administrative censoring: no verdict")
        cost = acct["costs"].get(n, 0)
        if abs(cost - r.cost) > 1e-7:
            raise ValueError(f"Cache/receipt mismatch: {n}")
        result[r.cell] = Observation(r.solved, cost, r.platform_failed)
    return result


def metrics(obs: dict[tuple[str, str], Observation]) -> dict[str, Any]:
    solves = sum(
        v.solved and not v.failed and v.cost <= 0.10 for v in obs.values()
    )
    cost = sum(v.cost for v in obs.values())
    return dict(
        cells=len(obs),
        solves=solves,
        cost=cost,
        cost_per_solve=cost / solves if solves else None,
    )


def report(stage: str) -> None:
    if stage not in STAGES:
        raise ValueError("Unsupported stage")
    verify()
    acct = accounting()
    if acct["unresolved"]:
        raise ValueError("Unresolved charges")
    obs = {a: observations(stage, a, acct) for a in ARMS}
    obs["reference"] = {
        (r["theorem"], "0"): Observation(r["solved"], r["cost"], r["failed"])
        for r in read("references.json")[stage]
    }
    fam = read("registration.json")["families"]
    comparisons: dict[str, Any] = {}
    for a in ARMS:
        v = compare(
            obs["reference"], obs[a], list(obs["reference"]), families=fam
        )
        v.pop("verdict", None)
        v["cost_p_descriptive"] = cost_cluster_p(
            obs["reference"], obs[a], list(obs["reference"]), families=fam
        )
        comparisons[a] = v
    payload: dict[str, Any] = dict(
        stage=stage,
        metrics={a: metrics(o) for a, o in obs.items()},
        comparisons=comparisons,
        accounting=acct,
        cost_qualified_curves={
            a: {
                str(cap): sum(
                    v.solved and not v.failed and v.cost <= cap
                    for v in o.values()
                )
                for cap in (0.025, 0.05, 0.075, 0.1)
            }
            for a, o in obs.items()
        },
        curve_interpretation="Retrospective final-cost qualification, not smaller-budget admission experiments",
        default_changed=False,
    )
    save(stage + "_report.json", payload)
    if stage == "validation":
        save(
            "selection.json",
            dict(
                arm=min(
                    ARMS,
                    key=lambda a: (
                        -payload["metrics"][a]["solves"],
                        payload["metrics"][a]["cost"],
                        a,
                    ),
                ),
                rule="validation coverage then cost; descriptive recommendation only; no further run",
            ),
        )
    export_receipts()
    print(json.dumps(payload["metrics"], indent=2), flush=True)


def export_receipts() -> None:
    with (
        Ledger(CAMPAIGN / "ledger.sqlite3").connect() as db,
        (CAMPAIGN / "receipts.csv").open("w") as f,
    ):
        cursor = db.execute("SELECT * FROM receipts ORDER BY created,id")
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([d[0] for d in cursor.description])
        writer.writerows(cursor)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    stage = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--stage=")),
        "training",
    )
    arm = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--arm=")), "D2"
    )
    if stage not in STAGES or arm not in ARMS:
        raise ValueError("Unsupported stage/arm")
    sys.argv[:] = [
        a for a in sys.argv if not a.startswith(("--stage=", "--arm="))
    ]
    if command == "prepare":
        prepare()
        return
    if command == "seal":
        seal()
        return
    if command == "report":
        report(stage)
        return
    if command == "status":
        print(json.dumps(accounting(), indent=2))
        return
    verify()
    if (CAMPAIGN / f"{stage}_report.json").exists():
        raise ValueError("Stage complete; no rerun")
    if (
        stage == "validation"
        and not (CAMPAIGN / "training_report.json").exists()
    ):
        raise ValueError("Training must finish first")
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = "benchmark"
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")
    ol.OmphalosExperiment(
        config_class=CycleConfig,
        context=context(arm),
        configs=configs(stage, arm),
        output_dir=str((OUTPUT / stage / arm).relative_to(ROOT)),
        config_naming=name,
        wait_for_slots=True,
        attempts=1,
    ).run_cli()


if __name__ == "__main__":
    main()
