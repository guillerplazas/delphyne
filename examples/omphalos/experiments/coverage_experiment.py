"""Approved 2026-09-11 coverage campaign; six runs of 40 cells, seed 0.

D adds family-excluded focused examples; E adds one bounded nested search.
No ACE adaptation, combinations, paid pilots, additional seeds or default
promotion. Train D/E, validation D/E, then test the validation winner and
flagship: at most 240 new cells. Reuse 80 historical train/validation controls.
Primary: complete kernel solves at actual cost <=$.10, including failures
and retries. Rank validation by qualified solves, then cost, then arm name.
Both technically sound arms reach validation without an effect/p-value gate.
Family two-sided p<.10 and 90% intervals describe evidence, not run admission.
Test is frozen once, never used for fixes; validation is development data.

Experiment liability <=$25 (benchmark 24, infrastructure retry 1). Separate
Sol-medium demo-authoring liability <=$3; no prover evaluation billed there.
All entries execute through OmphalosExperiment; both harnesses use this CLI:
 prepare-author | run --stage=author --arm=author | build-demos | seal
 run --stage=training|validation --arm=D|E --max_workers=24 --wait
 report --stage=training|validation | freeze-test
 run --stage=test --arm=D|E|reference --max_workers=24 --wait
 report --stage=test | status
"""

from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import csv
import json
import os
import re
from pathlib import Path
import sys
from typing import Any

import delphyne as dp
from delphyne.utils.typing import pydantic_load
import yaml

import ace.ace_grounded as ag
from experiments.ace.ace_bounded_experiment import (
    BoundedConfig,
    INCUMBENT,
    INCUMBENT_SHA,
    digest,
)
from experiments.ace.ace_contender_benchmark import reference_inventory
from experiments.common import ace_model_campaign as old
from experiments.common.minif2f_x import PARTITIONS_X
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from tools.reports.grounded_report import families, write_new
import prove_coverage as pc
import prove_grounded as pg
import runtime.pytanque_utils as pt
from runtime.tool_budget import ToolLimits

CAMPAIGN = ROOT / "experiments/campaigns/coverage_20260911"
OUTPUT = ROOT / "experiments/output/coverage_20260911"
BANK = "experiments/campaigns/coverage_20260911/demo_bank.json"
DEMOS = "demos/coverage.demo.yaml"
SOURCE = ROOT / "experiments/campaigns/ace_polish_20260909/artifact.json"
# Two structural and four representation examples, chosen from trainX only.
DEMO_SELECTION = (
    (3, "structure", ("sum_f",)),
    (11, "structure", ("sum_n", "prod_n")),
    (6, "bridge", ("INR",)),
    (19, "bridge", ("INR", "nat")),
    (20, "bridge", ("PI", "cos")),
    (22, "bridge", ("sqrt",)),
)


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: object) -> None:
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    write_new(CAMPAIGN / name, value)


def context(arm: str = "") -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    return replace(
        ctx,
        modules=(*ctx.modules, "prove_coverage"),
        demo_files=(*ctx.demo_files, ROOT / DEMOS)
        if arm == "D"
        else ctx.demo_files,
    )


@dataclass
class AuthorConfig:
    source: dict[str, Any]
    index: int

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if asdict(self) not in read("author_manifest.json"):
            raise ValueError("unregistered authoring request")
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = author_name(self, None)
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
        return dp.RunStrategyArgs(
            strategy="author_coverage_demo",
            args={"source": self.source},
            policy="author_policy",
            policy_args={},
            budget={"price": 0.5, "num_requests": 1},
        )


def author_name(c: AuthorConfig, _: object) -> str:
    return f"author-{c.index}"


@dataclass
class CoverageConfig(BoundedConfig):
    stage: str = "training"

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        rows = read(
            "test_manifest.json" if self.stage == "test" else "manifest.json"
        )
        if asdict(self) not in rows:
            raise ValueError("cell outside immutable manifest")
        result = super().instantiate(context)
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        if self.arm_label == "D":
            result.policy = "coverage_policy"
            result.policy_args["bank_file"] = BANK
        elif self.arm_label == "E":
            result.args["bounded_exploration"] = True
            result.policy = "coverage_policy"
        return result


def name(c: CoverageConfig, _: object) -> str:
    return f"{c.bench_name}__{c.stage}-{c.arm_label}__{c.model_name}__seed{c.seed}"


def config(bench: str, stage: str, arm: str) -> CoverageConfig:
    artifact = "experiments/campaigns/ace_bounded_20260908/artifact_v2.json"
    partition = {
        "training": "trainX",
        "validation": "validationX",
        "test": "testX",
    }[stage]
    return CoverageConfig(
        bench_name=bench,
        problem_file=PARTITIONS_X[partition][bench][0],
        model_name="gpt-5.6-luna",
        seed=0,
        num_requests=64,
        temperature=None,
        toolset="core",
        reasoning_effort="medium",
        max_dollar_budget=0.10,
        artifact=artifact,
        artifact_sha256=digest(ROOT / artifact),
        money=True,
        focused=True,
        admission=False,
        restart=False,
        stage=stage,
        arm_label=arm,
        playbook_file=str(INCUMBENT.relative_to(ROOT)),
        playbook_sha256=INCUMBENT_SHA,
    )


def prepare_author() -> None:
    claims = read_source()
    manifest = [asdict(AuthorConfig(c["evidence"], i)) for i, c in claims]
    save("author_manifest.json", manifest)
    save(
        "runtime.json",
        json.loads(
            (
                ROOT
                / "experiments/campaigns/ace_mechanisms_20260910/runtime.json"
            ).read_text()
        ),
    )
    save(
        "author_registration.json",
        dict(
            ceiling=3,
            model="gpt-5.6-sol",
            effort="medium",
            requests=len(manifest),
            source_sha256=digest(SOURCE),
            purpose="Develop examples, not evaluate prover performance",
        ),
    )
    Ledger(CAMPAIGN / "author.sqlite3").create(3, {"author": 3})


def read_source() -> list[tuple[int, dict[str, Any]]]:
    claims = json.loads(SOURCE.read_text())["state"]["claims"]
    rows = [(i, claims[i]) for i, _, _ in DEMO_SELECTION]
    for _, c in rows:
        if c["evidence"]["theorem_name"] not in PARTITIONS_X["trainX"]:
            raise ValueError("non-training authoring source")
    return rows


def build_demos() -> None:
    if digest(SOURCE) != read("author_registration.json")["source_sha256"]:
        raise ValueError("authoring source drift")
    demos: list[dict[str, Any]] = []
    bank: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for (i, c), (_, kind, match) in zip(read_source(), DEMO_SELECTION):
        e = pydantic_load(ag.TrainingTransition, c["evidence"])
        original = ag.checked_proof(
            e.problem_file,
            e.theorem_name,
            [*e.prefix, e.failed_action],
            ToolLimits(seconds=30),
            assisted=False,
        )
        result = yaml.safe_load(
            (
                OUTPUT / "author" / "configs" / f"author-{i}" / "result.yaml"
            ).read_text()
        )
        values: list[dict[str, Any]] = result["outcome"]["result"]["values"]
        authored: dict[str, Any] | None = values[0] if values else None
        script: str = authored["script"] if authored else ""
        raw_teacher_script = script
        tactics = pt.split_into_tactics(script) if script else []
        spec = pt.parse_problem(e.problem_file, show_definitions=True)
        expected_header = f"Theorem {e.theorem_name} {spec.theorem_statement}."
        if tactics and re.sub(r"\s+", "", tactics[0]) == re.sub(
            r"\s+", "", expected_header
        ):
            script = "\n".join(tactics[1:])
        accepted = None
        if script:
            accepted = ag.checked_proof(
                e.problem_file,
                e.theorem_name,
                pt.split_into_tactics(script),
                ToolLimits(seconds=30),
                assisted=False,
            )
        teacher_checked = accepted
        teacher_usable = (
            accepted is not None
            and pc.usable(original, accepted)
            and [
                re.sub(r"\s+", "", t)
                for t in pt.split_into_tactics(script)[: len(e.prefix)]
            ]
            == [re.sub(r"\s+", "", t) for t in e.prefix]
        )
        developer_repaired = False
        if not teacher_usable and script:
            from tools.data.coverage_demo_repairs import repair_draft

            repaired_script = repair_draft(i, script)
            repaired = ag.checked_proof(
                e.problem_file,
                e.theorem_name,
                pt.split_into_tactics(repaired_script),
                ToolLimits(seconds=30),
                assisted=False,
            )
            if pc.usable(original, repaired):
                script, accepted = repaired_script, repaired
                developer_repaired = True
        if not teacher_usable and not developer_repaired:
            script = "\n".join((*e.prefix, *c["action"]))
            accepted = ag.checked_proof(
                e.problem_file,
                e.theorem_name,
                pt.split_into_tactics(script),
                ToolLimits(seconds=30),
                assisted=False,
            )
        assert accepted is not None
        if not pc.usable(original, accepted):
            raise ValueError(
                f"Neither teacher nor verified source is executable: {i}: {accepted.outcome}, {accepted.feedback.error_message}"
            )
        cls = (
            pg.ChooseProofBridge
            if kind == "bridge"
            else pg.ChooseProofStructure
        )
        q = cls(
            pt.parse_problem(e.problem_file, show_definitions=True),
            {},
            verified_prefix="\n".join(original.feedback.proof_so_far),
            lesson=original.view,
        )
        demo_id = f"coverage-{i}"
        demos.append(
            dict(
                demonstration=demo_id,
                query=cls.__name__,
                args=asdict(q),
                answers=[dict(answer=f"```rocq\n{script}\n```", example=True)],
            )
        )
        demos.append(
            dict(
                demonstration=f"{demo_id}-navigation",
                strategy="demonstrate_coverage",
                args=dict(
                    query_kind=kind,
                    problem_file=e.problem_file,
                    theorem_name=e.theorem_name,
                    original=asdict(original),
                ),
                queries=[
                    dict(
                        query=cls.__name__,
                        args=asdict(q),
                        answers=[
                            dict(
                                answer=f"```rocq\n{script}\n```", example=False
                            )
                        ],
                    )
                ],
                tests=["run"],
            )
        )
        bank.append(
            dict(
                id=demo_id,
                query=cls.__name__,
                theorem=e.theorem_name,
                match_symbols=list(match),
                source_sha256=e.source_sha256,
            )
        )
        checks.append(
            dict(
                id=demo_id,
                teacher_used=teacher_usable,
                developer_repaired=developer_repaired,
                original=asdict(original),
                checked=asdict(accepted),
                script=script,
                teacher_result=authored,
                raw_teacher_script=raw_teacher_script,
                teacher_checked=asdict(teacher_checked)
                if teacher_checked
                else None,
            )
        )
    (ROOT / DEMOS).write_text(
        '# @config\n# modules: ["prove_grounded", "prove_coverage"]\n# @end\n# Frozen training-only examples and executable navigation; both harnesses.\n'
        + yaml.safe_dump(demos, sort_keys=False, allow_unicode=True)
    )
    all_problems = {
        k: v for panel in PARTITIONS_X.values() for k, v in panel.items()
    }
    save(
        "demo_bank.json", dict(examples=bank, families=families(all_problems))
    )
    save("demo_checks.json", checks)


def seal() -> None:
    refs, deps = reference_inventory()
    cs = [
        config(b, s, a)
        for s, p in (("training", "trainX"), ("validation", "validationX"))
        for a in ("D", "E")
        for b in PARTITIONS_X[p]
    ]
    save("manifest.json", [asdict(c) for c in cs])
    save("references.json", refs)
    deps.update(old.source_hashes())
    paths = [
        ROOT / "prove_coverage.py",
        ROOT / "tools/data/coverage_demo_repairs.py",
        ROOT / "tools/reports/coverage_audit.py",
        ROOT / "prove_grounded.py",
        Path(__file__),
        ROOT / DEMOS,
        ROOT / BANK,
        CAMPAIGN / "manifest.json",
        CAMPAIGN / "references.json",
        CAMPAIGN / "runtime.json",
    ]
    paths += list((ROOT / "prompts").rglob("*.jinja"))
    for c in cs:
        paths += [
            ROOT / c.problem_file,
            ROOT / c.artifact,
            ROOT / c.playbook_file,
        ]
    deps.update({str(p.relative_to(ROOT)): digest(p) for p in paths})
    all_problems = {
        k: v for panel in PARTITIONS_X.values() for k, v in panel.items()
    }
    save(
        "registration.json",
        dict(
            authorization="Guille: Implement the revised plan; $25 experiments, separate demo development; one seed per 40-cell run",
            ceiling=25,
            max_cells=240,
            seeds=[0],
            arms=["D", "E"],
            families=families(all_problems),
            dependencies=deps,
            selection="validation qualified solves descending, cost ascending, arm name",
            test_control="fresh flagship; no compatible bounded testX control identified in previous campaign inventories",
            exposure="historical controls; validation development; one test look; no protected challenge data",
            max_infrastructure_retries=4,
        ),
    )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(
        25, {"benchmark": 24, "retry": 1}
    )


def verify() -> None:
    old.verify_hashes(read("registration.json")["dependencies"])


def accounting(author: bool = False) -> dict[str, Any]:
    ledger = Ledger(
        CAMPAIGN / ("author.sqlite3" if author else "ledger.sqlite3")
    )
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,usage,cell FROM receipts"
        ).fetchall()
    costs: dict[str, float] = defaultdict(float)
    unresolved: list[str] = []
    for key, model, created, charged, usage, cell in rows:
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
                raise ValueError("receipt/token price mismatch")
        costs[cell] += charged
    return dict(
        costs=dict(costs),
        total=sum(costs.values()),
        requests=len(rows),
        unresolved=unresolved,
        ledger=ledger.summary(),
    )


def stage_configs(stage: str, arm: str) -> list[CoverageConfig]:
    manifest = read(
        "test_manifest.json" if stage == "test" else "manifest.json"
    )
    cs = [
        pydantic_load(CoverageConfig, c)
        for c in manifest
        if c["stage"] == stage and c["arm_label"] == arm
    ]
    if len(cs) != 40:
        raise ValueError("one benchmark run must have exactly 40 cells")
    return cs


def observations(
    stage: str, arm: str, acct: dict[str, Any]
) -> dict[tuple[str, str], Observation]:
    cs = stage_configs(stage, arm)
    output = OUTPUT / stage / arm
    records = {r.name: r for r in old.cells_of_run(output)}
    result: dict[tuple[str, str], Observation] = {}
    for c in cs:
        n = name(c, None)
        if n not in records:
            raise ValueError(f"missing cell: {n}; no verdict")
        r = records[n]
        path = output / "configs" / n
        for p in path.glob("exception*.txt"):
            if "CampaignExhausted" in p.read_text():
                raise ValueError("administrative censoring; no verdict")
        cost = acct["costs"].get(n, 0)
        if abs(cost - r.cost) > 1e-7:
            raise ValueError(f"cache/receipt mismatch: {n}")
        result[r.cell] = Observation(r.solved, cost, r.platform_failed)
    return result


def report(stage: str) -> None:
    verify()
    acct = accounting()
    if acct["unresolved"]:
        raise ValueError("unresolved liability; no verdict")
    labels = ["D", "E"] if stage != "test" else [read("selection.json")["arm"]]
    obs = {a: observations(stage, a, acct) for a in labels}
    if stage == "test":
        obs["reference"] = observations(stage, "reference", acct)
    else:
        obs["reference"] = {
            (r["theorem"], "0"): Observation(
                r["solved"], r["cost"], r["failed"]
            )
            for r in read("references.json")[stage]
        }
    metrics = {a: old.metrics(o) for a, o in obs.items()}
    comparisons: dict[str, Any] = {}
    for a in labels:
        pair = compare(
            obs["reference"],
            obs[a],
            list(obs["reference"]),
            families=read("registration.json")["families"],
        )
        pair.pop("verdict", None)
        pair["cost_p_two_sided_descriptive"] = cost_cluster_p(
            obs["reference"],
            obs[a],
            list(obs["reference"]),
            families=read("registration.json")["families"],
        )
        comparisons[a] = pair
    curves = {
        a: {
            str(cap): sum(
                v.solved and not v.failed and v.cost <= cap for v in o.values()
            )
            for cap in (0.025, 0.05, 0.075, 0.10)
        }
        for a, o in obs.items()
    }
    payload = dict(
        stage=stage,
        seed=0,
        cells_per_run=40,
        metrics=metrics,
        comparisons=comparisons,
        cost_qualified_curves=curves,
        curve_interpretation="retrospective final-cost qualification, not measured smaller-budget admission policies",
        accounting=acct,
        default_changed=False,
    )
    save(f"{stage}_report.json", payload)
    print(
        json.dumps(
            {k: v for k, v in payload.items() if k in ("stage", "metrics")},
            indent=2,
        ),
        flush=True,
    )
    export_receipts()


def freeze_test() -> None:
    report = read("validation_report.json")
    arm = min(
        ("D", "E"),
        key=lambda a: (
            -report["metrics"][a]["solves"],
            report["metrics"][a]["cost"],
            a,
        ),
    )
    save(
        "selection.json",
        dict(
            arm=arm,
            rule=read("registration.json")["selection"],
            validation_sha256=digest(CAMPAIGN / "validation_report.json"),
        ),
    )
    save(
        "test_manifest.json",
        [
            asdict(config(b, "test", a))
            for a in (arm, "reference")
            for b in PARTITIONS_X["testX"]
        ],
    )


def export_receipts() -> None:
    for author in (False, True):
        with (
            Ledger(
                CAMPAIGN / ("author.sqlite3" if author else "ledger.sqlite3")
            ).connect() as db,
            (
                CAMPAIGN
                / ("author_receipts.csv" if author else "receipts.csv")
            ).open("w") as f,
        ):
            cur = db.execute("SELECT * FROM receipts ORDER BY created,id")
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow([d[0] for d in cur.description])
            writer.writerows(cur.fetchall())


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    stage = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--stage=")),
        "training",
    )
    arm = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--arm=")), "D"
    )
    sys.argv[:] = [
        a for a in sys.argv if not a.startswith(("--stage=", "--arm="))
    ]
    if command == "prepare-author":
        prepare_author()
        return
    if command == "build-demos":
        build_demos()
        return
    if command == "seal":
        seal()
        return
    if command == "freeze-test":
        freeze_test()
        return
    if command == "report":
        report(stage)
        return
    if command == "status":
        print(
            json.dumps(
                {
                    k: accounting(a)
                    for k, a in (("experiments", False), ("authoring", True))
                    if (
                        CAMPAIGN
                        / ("author.sqlite3" if a else "ledger.sqlite3")
                    ).exists()
                },
                indent=2,
            )
        )
        return
    author = stage == "author"
    if not author:
        verify()
        if (CAMPAIGN / f"{stage}_report.json").exists():
            raise ValueError("stage completed; no reruns")
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(
        CAMPAIGN / ("author.sqlite3" if author else "ledger.sqlite3")
    )
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = "author" if author else "benchmark"
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")
    if author:
        ol.OmphalosExperiment(
            config_class=AuthorConfig,
            context=context(),
            configs=[
                pydantic_load(AuthorConfig, c)
                for c in read("author_manifest.json")
            ],
            output_dir=str((OUTPUT / "author").relative_to(ROOT)),
            config_naming=author_name,
            wait_for_slots=True,
            attempts=1,
        ).run_cli()
    else:
        ol.OmphalosExperiment(
            config_class=CoverageConfig,
            context=context(arm),
            configs=stage_configs(stage, arm),
            output_dir=str((OUTPUT / stage / arm).relative_to(ROOT)),
            config_naming=name,
            wait_for_slots=True,
            attempts=1,
        ).run_cli()


if __name__ == "__main__":
    main()
