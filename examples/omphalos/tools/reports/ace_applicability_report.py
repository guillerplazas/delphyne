"""Immutable preparation and complete-panel applicability reports; no API calls.

Both harnesses: python -m tools.reports.ace_applicability_report prepare|seal|report_a|report_b
"""

from dataclasses import asdict
from datetime import datetime, timezone
import sqlite3
import hashlib
import json
from pathlib import Path
import random
import sys
from typing import Any

import yaml

import ace.ace_applicability as aa
import ace.ace_grounded as ag
from ace.ace_evidence import import_signature
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits
from tools.reports.grounded_report import write_new, families
import experiments.common.miniF2F_bench as mf

CAMPAIGN = ROOT / "experiments/campaigns/ace_applicability_20260909"
PANEL: tuple[tuple[str, int, bool], ...] = (
    ("amc12a_2002_p13", 35, True),
    ("amc12a_2002_p13", 37, False),
    ("amc12a_2003_p1", 9, True),
    ("amc12a_2003_p1", 1, False),
    ("amc12a_2016_p2", 55, True),
    ("amc12a_2016_p2", 41, False),
    ("amc12a_2020_p13", 27, False),
    ("imo_1968_p5_1", 11, True),
    ("imo_1968_p5_1", 19, False),
    ("imo_1983_p6", 11, True),
    ("mathd_algebra_185", 32, True),
    ("mathd_algebra_323", 1, False),
)
DONORS = (
    ("amc12_2000_p6", 21, True),
    ("imo_1963_p5", 31, True),
    ("mathd_algebra_206", 7, True),
    ("amc12b_2003_p17", 23, False),
    ("mathd_algebra_28", 1, False),
)
# A witness must close a named obligation or establish a proved fact. A
# state change or alias is not itself a witness. Witnesses never enter prompts.
WITNESSES: dict[str, tuple[str, ...]] = {
    "amc12a_2002_p13-35": ("exact H.",),
    "amc12a_2003_p1-9": ("rewrite IH.", "lia."),
    "imo_1968_p5_1-11": (),  # the correction itself closes this focused goal
    "imo_1983_p6-11": ("assert (Hx : 0 < x) by (unfold x; lra).",),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> dict[str, Any]:
    return json.loads((CAMPAIGN / name).read_text())


def source(
    run: str, bench: str, index: int
) -> tuple[aa.RepairState, str, str]:
    allowed = mf.load_partition("benchmarks/trainX.txt")
    if bench not in allowed:
        raise ValueError("source is not trainX")
    directories = list(
        (ROOT / f"experiments/output/{run}/configs").glob(f"{bench}__*")
    )
    if len(directories) != 1:
        raise ValueError("ambiguous source cell")
    path = directories[0] / "cache.yaml"
    raw: Any = yaml.load(path.read_text(), Loader=yaml.CSafeLoader)
    entry = raw[index]
    call = yaml.safe_load(entry["input"]["request"]["chat"][-1]["content"])
    if call["fun"] != "checked_proof":
        raise ValueError("source index is not a proof check")
    checked = yaml.safe_load(entry["output"]["outputs"][0]["content"])
    f = checked["feedback"]
    if (call["args"]["problem_file"], call["args"]["theorem_name"]) != (
        allowed[bench][0],
        bench,
    ):
        raise ValueError("source theorem/file mismatch")
    prefix = (
        tuple(call["args"]["tactics"][: f["failing_index"]])
        if f["failing_index"] is not None
        else tuple(f["proof_so_far"])
    )
    return (
        aa.RepairState(
            allowed[bench][0],
            bench,
            prefix,
            f["failing_tactic"] or "",
            f["error_message"] or "",
            checked["outcome"],
            tuple(f["remaining_goals"]),
            import_signature(ROOT / allowed[bench][0]),
        ),
        directories[0].name,
        digest(path),
    )


def check_state(state: aa.RepairState) -> dict[str, Any]:
    initial = ag.checked_proof(
        state.problem_file,
        state.theorem_name,
        list(state.prefix),
        ToolLimits(seconds=10),
        assisted=False,
    )
    if initial.outcome not in (
        "incomplete",
        "accepted",
    ) or initial.feedback.proof_so_far != list(state.prefix):
        raise ValueError(
            f"prefix cannot be reconstructed: {state.theorem_name}"
        )
    pattern, correction = aa.syntax_form(state.failed_action)
    answer = aa.RepairDecision(
        "repair", pattern, correction, "syntax-only local check"
    )
    checked = aa.check_repair(state, answer, ToolLimits(seconds=10))
    return {
        "before": asdict(initial),
        "after": asdict(checked),
        "executed": aa.executed(state, answer, checked),
    }


def prepare() -> None:
    if CAMPAIGN.exists():
        raise ValueError(
            "refusing to replace preparation; retain failed evidence"
        )
    CAMPAIGN.mkdir(parents=True)
    bank: list[aa.RepairExample] = []
    validations: dict[str, Any] = {}
    try:
        for bench, index, positive in DONORS:
            state, cell, sha = source("ace_control_cycle_tuning", bench, index)
            key = f"{bench}-{index}"
            result = check_state(state)
            validations[key] = result
            if result["executed"] != positive:
                raise ValueError(f"donor verdict differs: {key}")
            pattern, correction = aa.syntax_form(state.failed_action)
            answer = aa.RepairDecision(
                "repair" if positive else "abstain",
                pattern,
                correction if positive else "",
                "Verified syntax-only local application"
                if positive
                else "The syntax-only form lacks conversion or reference support in this state",
            )
            bank.append(aa.RepairExample(key, state, answer, cell, sha, index))
        rows: list[dict[str, Any]] = []
        for bench, index, positive in PANEL:
            state, cell, sha = source("ace_polish_training", bench, index)
            key = f"{bench}-{index}"
            result = check_state(state)
            validations[key] = result
            if result["executed"] != positive:
                raise ValueError(f"panel verdict differs: {key}")
            witness = WITNESSES.get(key)
            if witness is not None:
                _, correction = aa.syntax_form(state.failed_action)
                tactics = [
                    *state.prefix,
                    *ag.pt.split_into_tactics(correction),
                    *witness,
                ]
                checked = ag.checked_proof(
                    state.problem_file,
                    bench,
                    tactics,
                    ToolLimits(seconds=10),
                    assisted=False,
                )
                if (
                    checked.outcome not in ("accepted", "incomplete")
                    or checked.feedback.proof_so_far != tactics
                ):
                    raise ValueError(f"downstream witness failed: {key}")
                validations[key]["witness"] = asdict(checked)
            rows.append(
                {
                    "id": key,
                    "state": asdict(state),
                    "source_cell": cell,
                    "source_sha256": sha,
                    "source_index": index,
                    "positive": positive,
                    "witness": witness,
                }
            )
        data = {"bank": [asdict(e) for e in bank], "states": rows}
        write_new(CAMPAIGN / "artifact.json", data)
        write_new(CAMPAIGN / "preparation_checks.json", validations)
        demo_file = ROOT / "demos/applicability.demo.yaml"
        if demo_file.exists():
            raise ValueError("refusing to overwrite demonstration file")
        demos: list[dict[str, Any]] = []
        for example in bank:
            args = {
                "state": asdict(example.state),
                "available_skills": {},
                "example_ids": [example.id],
                "demonstration": True,
            }
            answer = {"answer": asdict(example.answer)}
            demos.append(
                {
                    "demonstration": example.id,
                    "query": "DecideSyntaxRepair",
                    "args": args,
                    "answers": [answer],
                }
            )
            demos.append(
                {
                    "demonstration": example.id + "-checked",
                    "strategy": "verify_syntax_demo",
                    "args": {
                        "state": asdict(example.state),
                        "example_id": example.id,
                        "expected": example.answer.decision == "repair",
                    },
                    "tests": ["run | success"],
                    "queries": [
                        {
                            "query": "DecideSyntaxRepair",
                            "args": args,
                            "answers": [{**answer, "example": False}],
                        }
                    ],
                }
            )
        demo_file.write_text(yaml.safe_dump(demos, sort_keys=False))
        rng = random.Random(20260910)
        order_a = sorted(row["id"] for row in rows)
        rng.shuffle(order_a)
        schedule_a: list[dict[str, Any]] = []
        for state in order_a:
            arms = ["R", "Q", "F", "A"]
            rng.shuffle(arms)
            schedule_a.extend(
                {"state": state, "arm": arm, "seed": 0} for arm in arms
            )
        names = sorted({b for b, _, _ in PANEL})
        rng.shuffle(names)
        schedule_b: list[dict[str, Any]] = []
        for bench in names:
            arms = ["R", "F", "A"]
            rng.shuffle(arms)
            schedule_b.extend(
                {"bench": bench, "arm": arm, "seed": 0} for arm in arms
            )
        validation = mf.load_partition("benchmarks/validationX.txt")
        cells = [
            (bench, seed) for bench in sorted(validation) for seed in (0, 1)
        ]
        rng.shuffle(cells)
        schedule_v: list[dict[str, Any]] = []
        for bench, seed in cells:
            arms = ["R", "A"]
            rng.shuffle(arms)
            schedule_v.extend(
                {"bench": bench, "arm": arm, "seed": seed} for arm in arms
            )
        write_new(
            CAMPAIGN / "registration.json",
            {
                "authorized_ceiling": 2.5,
                "allocations": {"a": 1.0, "b": 1.25, "retry": 0.25},
                "conditional_validation_ceiling": 4.0,
                "teacher_budget": 0,
                "retry_limit": 2,
                "schedule_a": schedule_a,
                "schedule_b": schedule_b,
                "schedule_validation": schedule_v,
                "families": families(
                    dict(mf.load_partition("benchmarks/trainX.txt"))
                    | dict(validation)
                ),
                "artifact_sha256": digest(CAMPAIGN / "artifact.json"),
                "validation_authorized": False,
            },
        )
    except Exception as exc:
        write_new(
            CAMPAIGN / "preparation_failed.json",
            {"error": str(exc), "checks": validations, "paid_calls": 0},
        )
        raise


def seal() -> None:
    manifest = read("registration.json")
    paths = [
        ROOT / "delphyne.yaml",
        ROOT / "demos/applicability.demo.yaml",
        CAMPAIGN / "artifact.json",
        CAMPAIGN / "registration.json",
    ]
    for pattern in (
        "prove_*.py",
        "ace/*.py",
        "runtime/*.py",
        "prompts/**/*.jinja",
        "demos/*.demo.yaml",
        "experiments/common/*.py",
    ):
        paths.extend(ROOT.glob(pattern))
    paths.extend(
        ROOT / p
        for p in (
            "experiments/ace/ace_applicability_experiment.py",
            "tools/reports/ace_applicability_report.py",
            "benchmarks/trainX.txt",
            "benchmarks/validationX.txt",
        )
    )
    write_new(
        CAMPAIGN / "sealed.json",
        {
            "execution_hashes": {
                str(p.relative_to(ROOT)): digest(p) for p in sorted(set(paths))
            },
            "registration": manifest,
        },
    )


def stage_a_gate(
    rows: list[dict[str, Any]], family: dict[str, str]
) -> dict[str, Any]:
    by_arm = {
        arm: [r for r in rows if r["arm"] == arm]
        for arm in ("R", "Q", "F", "A")
    }
    complete = all(len(v) == 12 for v in by_arm.values()) and not any(
        r["missing"] or r["censored"] for r in rows
    )
    summaries = {
        arm: {
            "correct_positive": sum(
                r["positive"] and r["executed"] for r in values
            ),
            "negative_abstentions": sum(
                not r["positive"] and r["explicit_abstention"] for r in values
            ),
            "admitted_negative": sum(
                not r["positive"] and r["executed"] for r in values
            ),
            "useful": sum(r["useful"] for r in values),
            "cost": sum(r["cost"] for r in values),
            "platform_failures": sum(r["platform_failed"] for r in values),
        }
        for arm, values in by_arm.items()
    }
    f = {r["state_id"]: r for r in by_arm["F"]}
    incremental = [
        r
        for r in by_arm["A"]
        if r["useful"] and not f.get(r["state_id"], {}).get("useful", False)
    ]
    useful_families = {family[r["bench"]] for r in by_arm["A"] if r["useful"]}
    a, fixed = summaries["A"], summaries["F"]
    benefit = (
        a["useful"] - fixed["useful"] >= 2
        and len({family[r["bench"]] for r in incremental}) >= 2
    ) or (
        a["useful"] == fixed["useful"]
        and a["cost"] <= 0.85 * fixed["cost"]
        and fixed["cost"] > 0
    )
    go = (
        complete
        and not any(r["platform_failed"] for r in rows)
        and a["correct_positive"] >= 5
        and a["negative_abstentions"] >= 5
        and a["admitted_negative"] == 0
        and len(useful_families) >= 2
        and benefit
    )
    return {
        "complete": complete,
        "go": go,
        "arms": summaries,
        "useful_families": sorted(useful_families),
        "benefit_over_fixed": benefit,
        "verdict": "pass_screen"
        if go
        else "incomplete"
        if not complete
        else "stop_no_go",
    }


def accounting(phase: str) -> tuple[dict[str, float], dict[str, Any]]:
    import csv
    from runtime.campaign_budget import Ledger
    from runtime.model_registry import price_tokens

    path = CAMPAIGN / (
        "validation_ledger.sqlite3"
        if phase == "validation"
        else "ledger.sqlite3"
    )
    ledger = Ledger(path)
    costs: dict[str, float] = {}
    unknown: list[str] = []
    with ledger.connect() as db:
        db.row_factory = sqlite3.Row
        receipts = [
            dict(r)
            for r in db.execute("SELECT * FROM receipts ORDER BY created,id")
        ]
    for r in receipts:
        cost = float(
            r["charged"] if r["charged"] is not None else r["reserved"]
        )
        costs[r["cell"]] = costs.get(r["cell"], 0) + cost
        if r["charged"] is None:
            unknown.append(r["id"])
        elif r["status"] == "settled":
            usage = json.loads(r["usage"])
            expected = price_tokens(
                r["model"],
                usage.get("input_tokens", 0),
                usage.get("input_tokens_details", {}).get("cached_tokens", 0),
                usage.get("output_tokens", 0),
                on=datetime.fromtimestamp(r["created"], timezone.utc).date(),
            )
            if abs(expected - cost) > 1e-9:
                raise ValueError("receipt repricing mismatch")
    target = CAMPAIGN / f"receipts_{phase}.csv"
    with target.open("x", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(receipts[0]) if receipts else ["id"]
        )
        writer.writeheader()
        writer.writerows(receipts)
    return costs, {
        "ledger": ledger.summary(),
        "unresolved": unknown,
        "receipts": len(receipts),
    }


def report(phase: str) -> None:
    from experiments.ace.ace_applicability_experiment import configs, name
    from tools.analysis.cell_records import cells_of_run
    from tools.analysis.paired_evaluation import (
        Observation,
        compare,
        cost_cluster_p,
    )
    from delphyne.utils.typing import pydantic_load
    from prove_applicability import RepairResult

    target = CAMPAIGN / f"report_{phase}.json"
    if target.exists():
        raise ValueError("report already frozen")
    run = ROOT / f"experiments/output/ace_applicability_{phase}"
    records = {r.name: r for r in cells_of_run(run)}
    costs, bill = accounting(phase)
    expected_configs = configs(phase)
    rows: list[dict[str, Any]] = []
    artifact = read("artifact.json")
    states = {s["id"]: s for s in artifact["states"]}
    for config in expected_configs:
        cell = name(config, None)
        rec = records.get(cell)
        directory = run / "configs" / cell
        exception = (
            (directory / "exception.txt").read_text()
            if (directory / "exception.txt").exists()
            else ""
        )
        if rec is not None and rec.requests and cell not in costs:
            raise ValueError(f"missing receipt accounting: {cell}")
        cost = costs.get(cell, 0.0)
        row: dict[str, Any] = {
            "cell": cell,
            "bench": config.bench_name,
            "state_id": config.state_id,
            "seed": str(config.seed),
            "arm": config.arm_label,
            "cost": cost,
            "missing": rec is None,
            "censored": "CampaignExhausted" in exception,
            "platform_failed": bool(rec and rec.platform_failed),
            "qualified": bool(
                rec and rec.solved and not rec.platform_failed and cost <= 0.10
            ),
            "executed": False,
            "explicit_abstention": False,
            "useful": False,
        }
        result_path = directory / "result.yaml"
        outcome: dict[str, Any] = {}
        if result_path.exists():
            # Read only the actual top-level outcome, irrespective of argument
            # size or historical success fields inside those arguments.
            with result_path.open() as handle:
                for line in handle:
                    if line.rstrip() == "outcome:":
                        outcome = (
                            yaml.load(
                                line + handle.read(), Loader=yaml.CSafeLoader
                            )["outcome"].get("result")
                            or {}
                        )
                        break
        values = outcome.get("values", [])
        if phase == "a":
            spec = states[config.state_id]
            row["positive"] = spec["positive"]
            row["qualified"] = False  # local results are never theorem solves
            if values:
                value = pydantic_load(RepairResult, values[0])
                row.update(
                    executed=value.executed,
                    explicit_abstention=value.status == "abstained",
                    decision=asdict(value.decision),
                    status=value.status,
                    local_requests=value.requests,
                )
                row["useful"] = bool(
                    value.executed
                    and (
                        spec["witness"] is not None
                        or (value.checked and value.checked.feedback.success)
                    )
                )
                if value.checked:
                    row["local_outcome"] = value.checked.outcome
        else:
            row["proof"] = values[0] if values else ""
        rows.append(row)
    family = read("registration.json")["families"]
    if phase == "a":
        result = stage_a_gate(rows, family)
        result["local_episodes_not_full_theorem_cells"] = True
        contrasts: dict[str, Any] = {}
        for left, right in (("R", "Q"), ("Q", "F"), ("F", "A")):
            controls = {
                (r["bench"], r["state_id"]): Observation(
                    r["useful"], r["cost"], r["platform_failed"]
                )
                for r in rows
                if r["arm"] == left and not r["missing"]
            }
            candidates = {
                (r["bench"], r["state_id"]): Observation(
                    r["useful"], r["cost"], r["platform_failed"]
                )
                for r in rows
                if r["arm"] == right and not r["missing"]
            }
            cells = [
                (r["bench"], r["state_id"]) for r in rows if r["arm"] == left
            ]
            comparison = compare(controls, candidates, cells, families=family)
            if comparison["complete"]:
                comparison["cost_p_two_sided"] = cost_cluster_p(
                    controls, candidates, cells, family
                )
            contrasts[f"{right}_vs_{left}"] = comparison
        result["exploratory_useful_transition_contrasts"] = contrasts
    else:
        comparisons: dict[str, Any] = {}
        for control in ("R", "F") if phase == "b" else ("R",):
            a = {
                (r["bench"], r["seed"]): Observation(
                    r["qualified"], r["cost"], r["platform_failed"]
                )
                for r in rows
                if r["arm"] == control and not r["missing"]
            }
            b = {
                (r["bench"], r["seed"]): Observation(
                    r["qualified"], r["cost"], r["platform_failed"]
                )
                for r in rows
                if r["arm"] == "A" and not r["missing"]
            }
            cells = [
                (c.bench_name, str(c.seed))
                for c in expected_configs
                if c.arm_label == "A"
            ]
            comp = compare(a, b, cells, families=family)
            if comp["complete"]:
                comp["cost_p_two_sided"] = cost_cluster_p(a, b, cells, family)
                sa, sb = comp["solved_a"], comp["solved_b"]
                comp["cost_per_solve"] = [
                    comp["cost_a"] / sa if sa else None,
                    comp["cost_b"] / sb if sb else None,
                ]
                comp["practical"] = bool(
                    sa > 0
                    and sb >= sa
                    and comp["cost_b"] <= 0.85 * comp["cost_a"]
                    and comp["cost_b"] / sb <= 0.85 * comp["cost_a"] / sa
                )
            comparisons[control] = comp
        events = [
            json.loads(line)
            for line in (CAMPAIGN / "admission.jsonl").read_text().splitlines()
        ]
        triggered: set[str] = set()
        useful: set[str] = set()
        for row in rows:
            if row["arm"] != "A":
                continue
            own = [
                e
                for e in events
                if e.get("cell") == row["cell"] and e.get("stage") == phase
            ]
            if any(
                e["kind"] == "syntax_query" and e["decision"] == "answered"
                for e in own
            ):
                triggered.add(family[row["bench"]])
            final = ag.pt.split_into_tactics(row["proof"])
            for e in own:
                if e["kind"] == "syntax_repair" and e["decision"] == "checked":
                    prefix = e["original_prefix"] + ag.pt.split_into_tactics(
                        e["correction"]
                    )
                    if (
                        row["qualified"]
                        and final[: len(prefix)] == prefix
                        and e["prefix"][: len(prefix)] == prefix
                    ):
                        useful.add(family[row["bench"]])
        complete = not any(r["missing"] or r["censored"] for r in rows)
        practical = all(
            c.get("practical", False) for c in comparisons.values()
        )
        go = (
            complete
            and practical
            and not any(r["platform_failed"] for r in rows)
        )
        if phase == "b":
            go = go and len(triggered) >= 3 and len(useful) >= 2
        result = {
            "complete": complete,
            "go": go,
            "comparisons": comparisons,
            "triggered_families": sorted(triggered),
            "useful_repair_families": sorted(useful),
            "statistically_supported_saving": phase == "validation"
            and go
            and comparisons["R"].get("cost_p_two_sided", 1) < 0.10,
            "promotion": False,
        }
    if bill["unresolved"]:
        result["go"] = False
        result["verdict"] = "unresolved_liability"
    result.update(accounting=bill, cells=rows, historical_controls_used=False)
    write_new(target, result)
    print(
        json.dumps({k: v for k, v in result.items() if k != "cells"}, indent=2)
    )


if __name__ == "__main__":
    command = sys.argv[1]
    if command.startswith("report_"):
        report(command.removeprefix("report_"))
    else:
        {"prepare": prepare, "seal": seal}[command]()
