"""Frozen trainX preparation and accounting; no model/API calls.

Both harnesses: python -m tools.reports.change_control_report
prepare|seal|primary|terra. Historical campaigns are read-only inputs.
"""

from dataclasses import asdict
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any

import yaml
from delphyne.utils.typing import pydantic_load
import ace.ace_applicability as aa
import ace.ace_grounded as ag
from ace.change_progress import audit_progress
import runtime.pytanque_utils as pt
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits
from runtime.campaign_budget import Ledger
from runtime.model_registry import price_tokens
from tools.reports.ace_applicability_report import source
from tools.reports.grounded_report import write_new, families
import experiments.common.miniF2F_bench as mf
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from prove_change_control import ChangeEpisodeResult, RepairCheckpoint
from prove_applicability import RepairResult

CAMPAIGN = ROOT / "experiments/campaigns/change_control_20260910"
OLD = ROOT / "experiments/campaigns/ace_applicability_20260909"
PANEL = (
    "amc12a_2002_p13-35",
    "amc12a_2003_p1-9",
    "amc12a_2016_p2-55",
    "amc12a_2020_p13-27",
    "imo_1968_p5_1-19",
    "imo_1983_p6-33",
)
ENABLING = ("amc12a_2003_p1", "imo_1983_p6")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> dict[str, Any]:
    return json.loads((CAMPAIGN / name).read_text())


def prepare() -> None:
    if (CAMPAIGN / "artifact.json").exists():
        raise ValueError("preparation already exists")
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    old = json.loads((OLD / "artifact.json").read_text())
    states = {r["id"]: r for r in old["states"]}
    state, cell, sha = source("ace_polish_training", "imo_1983_p6", 33)
    if (
        sha
        != "fd3e7f82a542ffe439bb642a8253ba8b8d592830ba9160c44d51c1fb13c94c6d"
    ):
        raise ValueError("new source changed")
    states[PANEL[-1]] = {
        "id": PANEL[-1],
        "positive": True,
        "state": asdict(state),
        "source_cell": cell,
        "source_index": 33,
        "source_sha256": sha,
        "witness": ["nra."],
    }
    allowed = mf.load_partition("benchmarks/trainX.txt")
    audits: dict[str, Any] = {}
    for key in PANEL:
        row = states[key]
        s = pydantic_load(aa.RepairState, row["state"])
        if (s.problem_file, s.theorem_name) != allowed[s.theorem_name]:
            raise ValueError("not trainX")
        path = (
            ROOT
            / "experiments/output/ace_polish_training/configs"
            / row["source_cell"]
            / "cache.yaml"
        )
        if digest(path) != row["source_sha256"]:
            raise ValueError("source changed")
        before = ag.checked_proof(
            s.problem_file,
            s.theorem_name,
            list(s.prefix),
            ToolLimits(seconds=10),
            assisted=False,
        )
        if (
            before.outcome != "incomplete"
            or before.feedback.proof_so_far != list(s.prefix)
        ):
            raise ValueError("prefix replay failed")
        pattern, correction = aa.syntax_form(s.failed_action)
        answer = aa.RepairDecision(
            "repair", pattern, correction, "local audit"
        )
        after = aa.check_repair(s, answer, ToolLimits(seconds=10))
        if aa.executed(s, answer, after) != row["positive"]:
            raise ValueError("candidate verdict changed")
        audit: dict[str, Any] = {
            "before": asdict(before),
            "after": asdict(after),
        }
        if row["witness"] is not None:
            for label, prep in (
                ("without_change", []),
                ("with_change", pt.split_into_tactics(correction)),
            ):
                checked = ag.checked_proof(
                    s.problem_file,
                    s.theorem_name,
                    [*s.prefix, *prep, *row["witness"]],
                    ToolLimits(seconds=10),
                    assisted=False,
                )
                progress = audit_progress(s, checked)
                audit[label] = {
                    "checked": asdict(checked),
                    "progress": asdict(progress),
                }
            if not audit["with_change"]["progress"]["useful"]:
                raise ValueError(f"witness not useful: {key}")
            if (
                s.theorem_name in ENABLING
                and audit["without_change"]["progress"]["useful"]
            ):
                raise ValueError("enabling witness already works")
        row["exposure"] = (
            "additional_inspected_trainX"
            if key == PANEL[-1]
            else "previous_diagnostic"
        )
        audits[key] = audit
    artifact = {"bank": old["bank"], "states": [states[k] for k in PANEL]}
    write_new(CAMPAIGN / "artifact.json", artifact)
    write_new(CAMPAIGN / "preparation_checks.json", audits)
    schedules: dict[str, list[dict[str, Any]]] = {"primary": [], "terra": []}
    for i, key in enumerate(PANEL):
        for stage, arms in (("primary", ["F", "C"]), ("terra", ["TL", "TM"])):
            for arm in arms if i % 2 == 0 else arms[::-1]:
                schedules[stage].append({"state": key, "arm": arm, "seed": 0})
    write_new(
        CAMPAIGN / "registration.json",
        {
            "approval": "User: Implement the plan (2026-09-10)",
            "ceiling": 3.0,
            "allocations": {"primary": 1.2, "terra": 1.2, "retry": 0.6},
            "retry_limit": 1,
            "teacher_budget": 0,
            "full_train_authorized": False,
            "validation_authorized": False,
            "schedules": schedules,
            "artifact_sha256": digest(CAMPAIGN / "artifact.json"),
            "families": families(
                {
                    s["state"]["theorem_name"]: allowed[
                        s["state"]["theorem_name"]
                    ]
                    for s in artifact["states"]
                }
            ),
            "settings": {
                "api": "responses",
                "output_limit": 32768,
                "request_limit": 4,
                "local_luna_cap": 0.1,
                "local_terra_cap": 1.0,
                "verifier_seconds": 300,
                "operation_seconds": 60,
                "rpc_calls": 512,
                "view_bytes": 8192,
                "temperature": None,
                "assisted": False,
                "primary_model": "gpt-5.6-luna",
                "primary_effort": "medium",
                "terra_efforts": ["low", "medium"],
            },
            "primary_metric": "paired all-cell total API cost",
            "practical_gate": "all candidate verdicts correct; useful in both enabling families; no lost F useful cell; >=15% lower cost and cost/useful; complete",
            "statistics": "family-clustered two-sided p<.10; descriptive 90% intervals; Holm over three Terra contrasts for each endpoint",
        },
    )


def seal() -> None:
    paths: set[Path] = set()
    for pattern in (
        "prove_*.py",
        "ace/*.py",
        "runtime/*.py",
        "prompts/**/*.jinja",
        "demos/*.demo.yaml",
        "experiments/common/*.py",
        "tests/test_change_control*.py",
    ):
        paths.update(ROOT.glob(pattern))
    paths.update(
        ROOT / p
        for p in (
            "delphyne.yaml",
            "Makefile",
            "benchmarks/trainX.txt",
            "experiments/ace/change_control_experiment.py",
            "experiments/ace/ace_bounded_experiment.py",
            "experiments/playbooks/ace_x3_offline.yaml",
            "tools/reports/change_control_report.py",
            "tools/reports/ace_applicability_report.py",
            "tools/reports/grounded_report.py",
            "tools/analysis/paired_evaluation.py",
        )
    )
    paths.update(
        CAMPAIGN / p
        for p in ("artifact.json", "registration.json", "README.md")
    )
    for row in read("artifact.json")["states"]:
        paths.add(ROOT / row["state"]["problem_file"])
    write_new(
        CAMPAIGN / "sealed.json",
        {
            "execution_hashes": {
                str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)
            },
            "registration": read("registration.json"),
        },
    )


def receipt_rows() -> list[dict[str, Any]]:
    path = CAMPAIGN / "ledger.sqlite3"
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        rows = [
            dict(r)
            for r in db.execute("SELECT * FROM receipts ORDER BY created,id")
        ]
    for row in rows:
        if row["status"] == "settled":
            u = json.loads(row["usage"])
            cost = price_tokens(
                row["model"],
                u.get("input_tokens", 0),
                u.get("input_tokens_details", {}).get("cached_tokens", 0),
                u.get("output_tokens", 0),
                on=datetime.fromtimestamp(row["created"], timezone.utc).date(),
            )
            if row["charged"] is None or abs(cost - row["charged"]) > 1e-9:
                raise ValueError("receipt repricing mismatch")
    return rows


def result_of(
    directory: Path,
) -> tuple[ChangeEpisodeResult | None, RepairResult | None]:
    result, repair = None, None
    path = directory / "result.yaml"
    if path.exists():
        raw: Any = yaml.load(path.read_text(), Loader=yaml.CSafeLoader)
        outcome: dict[str, Any] = raw.get("outcome") or {}
        payload: dict[str, Any] = outcome.get("result") or {}
        values: list[Any] = payload.get("values", [])
        if values:
            result = pydantic_load(ChangeEpisodeResult, values[0])
            repair = result.repair
    path = directory / "cache.yaml"
    if repair is None and path.exists():
        entries: Any = yaml.load(path.read_text(), Loader=yaml.CSafeLoader)
        for entry in entries:
            chat = entry["input"]["request"]["chat"]
            if not chat or not isinstance(chat[-1]["content"], str):
                continue
            if "fun: checkpoint_repair" not in chat[-1]["content"]:
                continue
            output = yaml.safe_load(entry["output"]["outputs"][0]["content"])
            repair = pydantic_load(RepairCheckpoint, output).repair
    return result, repair


def paired(
    rows: list[dict[str, Any]],
    left: str,
    right: str,
    endpoint: str,
    cost_key: str = "cost",
) -> dict[str, Any]:
    expected = [
        (r["state"]["theorem_name"], r["id"])
        for r in read("artifact.json")["states"]
    ]
    groups = read("registration.json")["families"]
    maps = [
        {
            (r["bench"], r["state_id"]): Observation(
                bool(r[endpoint]), r[cost_key], r["platform_failed"]
            )
            for r in rows
            if r["arm"] == arm
        }
        for arm in (left, right)
    ]
    result = compare(
        maps[0], maps[1], expected, families=groups, cap_a=1.0, cap_b=1.0
    )
    if result["complete"]:
        result["cost_p_two_sided"] = cost_cluster_p(
            maps[0], maps[1], expected, groups
        )
    return result


def primary_gate(rows: list[dict[str, Any]], complete: bool) -> bool:
    f = {r["state_id"]: r for r in rows if r["arm"] == "F"}
    c = [r for r in rows if r["arm"] == "C"]
    fc = sum(r["cost"] for r in f.values())
    cc = sum(r["cost"] for r in c)
    fu = sum(r["useful"] for r in f.values())
    cu = sum(r["useful"] for r in c)
    return bool(
        complete
        and len(f) == len(c) == 6
        and all(r["decision_correct"] for r in c)
        and set(ENABLING) <= {r["bench"] for r in c if r["useful"]}
        and all(not f[r["state_id"]]["useful"] or r["useful"] for r in c)
        and fu > 0
        and cu > 0
        and fc > 0
        and cc <= 0.85 * fc
        and cc / cu <= 0.85 * fc / fu
    )


def holm(values: list[float]) -> list[float]:
    result = [1.0] * len(values)
    prior = 0.0
    for rank, i in enumerate(
        sorted(range(len(values)), key=lambda i: values[i])
    ):
        prior = max(prior, min(1.0, (len(values) - rank) * values[i]))
        result[i] = prior
    return result


def report(stage: str) -> None:
    from experiments.ace.change_control_experiment import configs, name

    if (CAMPAIGN / f"report_{stage}.json").exists():
        raise ValueError("report already frozen")
    receipts = receipt_rows()
    events_path = CAMPAIGN / "events.jsonl"
    events = (
        [json.loads(line) for line in events_path.read_text().splitlines()]
        if events_path.exists()
        else []
    )
    preparation = read("preparation_checks.json")
    rows: list[dict[str, Any]] = []
    states = {s["id"]: s for s in read("artifact.json")["states"]}
    for config in configs(stage):
        cell = name(config, None)
        directory = (
            ROOT / f"experiments/output/change_control_{stage}/configs" / cell
        )
        result, repair = result_of(directory)
        charges = [r for r in receipts if r["cell"] == cell]
        cost = sum(
            r["charged"] if r["charged"] is not None else r["reserved"]
            for r in charges
        )
        error = "\n".join(
            p.read_text() for p in directory.glob("exception*.txt")
        )
        state = pydantic_load(aa.RepairState, states[config.state_id]["state"])
        positive = states[config.state_id]["positive"]
        audit: dict[str, Any] | None = None
        if result and result.continuation and result.continuation.checked:
            audit = asdict(audit_progress(state, result.continuation.checked))
        phase_count = repair.requests if repair else len(charges)
        phase_charges = charges[:phase_count]
        row: dict[str, Any] = {
            "cell": cell,
            "state_id": config.state_id,
            "bench": config.bench_name,
            "seed": 0,
            "arm": config.arm_label,
            "cost": cost,
            "requests": len(charges),
            "repair_requests": phase_count,
            "repair_cost": sum(
                r["charged"] if r["charged"] is not None else r["reserved"]
                for r in phase_charges
            ),
            "missing": not (directory / "result.yaml").exists() and not error,
            "censored": "CampaignExhausted" in error,
            "platform_failed": bool(error),
            "exception": error,
            "positive": positive,
            "repair": asdict(repair) if repair else None,
            "executed": bool(repair and repair.executed),
            "decision_correct": bool(
                repair
                and (
                    repair.executed
                    if positive
                    else repair.decision.decision == "abstain"
                    and (
                        repair.status == "abstained" or config.arm_label == "C"
                    )
                    and (
                        repair.checked is None
                        or repair.checked.outcome == "rejected"
                    )
                )
            ),
            "useful": bool(audit and audit["useful"]),
            "progress_audit": audit,
            "local_result": asdict(result) if result else None,
            "qualified_full_solve": False,
            "explicit_abstention": bool(
                repair
                and repair.decision.decision == "abstain"
                and (repair.status == "abstained" or config.arm_label == "C")
            ),
            "witness_enabled": bool(
                repair
                and repair.executed
                and preparation[config.state_id]
                .get("with_change", {})
                .get("progress", {})
                .get("useful")
            ),
            "witness_already_worked": bool(
                preparation[config.state_id]
                .get("without_change", {})
                .get("progress", {})
                .get("useful")
            ),
            "verifier_seconds": result.elapsed
            if result
            else repair.elapsed
            if repair
            else None,
            "scoring_unavailable": bool(
                audit and audit["outcome"] == "unavailable"
            ),
            "budget_events": [
                e
                for e in events
                if e["cell"] == cell and e["kind"] in ("admission", "stop")
            ],
            "compute_events": [
                e
                for e in events
                if e["cell"] == cell and e["kind"] == "compute"
            ],
        }
        for key in ("input_tokens", "output_tokens"):
            row[key] = sum(
                json.loads(r["usage"]).get(key, 0)
                for r in charges
                if r["usage"]
            )
        row["reasoning_tokens"] = sum(
            json.loads(r["usage"])
            .get("output_tokens_details", {})
            .get("reasoning_tokens", 0)
            for r in charges
            if r["usage"]
        )
        row["cached_tokens"] = sum(
            json.loads(r["usage"])
            .get("input_tokens_details", {})
            .get("cached_tokens", 0)
            for r in charges
            if r["usage"]
        )
        cache = directory / "cache.yaml"
        tool_calls: list[Any] = []
        if cache.exists():
            entries: Any = yaml.load(
                cache.read_text(), Loader=yaml.CSafeLoader
            )
            for entry in entries:
                for output in entry["output"].get("outputs", []):
                    tool_calls.extend(output.get("tool_calls", []) or [])
        row["tool_calls"] = tool_calls
        rows.append(row)
    unresolved = [r["id"] for r in receipts if r["charged"] is None]
    complete = not unresolved and not any(
        r["missing"]
        or r["censored"]
        or r["platform_failed"]
        or r["scoring_unavailable"]
        for r in rows
    )
    result_report: dict[str, Any] = {
        "stage": stage,
        "complete": complete,
        "cells": rows,
        "cost": sum(r["cost"] for r in rows),
        "requests": sum(r["requests"] for r in rows),
        "unresolved": unresolved,
        "ledger": Ledger(CAMPAIGN / "ledger.sqlite3").summary(),
        "full_problems": 0,
        "teacher_calls": 0,
        "local_episodes": len(rows),
        "arms": {},
        "promote": False,
    }
    for arm in sorted({r["arm"] for r in rows}):
        subset = [r for r in rows if r["arm"] == arm]
        useful = sum(r["useful"] for r in subset)
        cost = sum(r["cost"] for r in subset)
        result_report["arms"][arm] = {
            "useful": useful,
            "cost": cost,
            "cost_per_useful": cost / useful if useful else None,
            "decision_correct": sum(r["decision_correct"] for r in subset),
            "executed": sum(r["executed"] for r in subset),
            "denominator": len(subset),
        }
    if stage == "primary":
        result_report["go"] = primary_gate(rows, complete)
        result_report["comparison"] = paired(rows, "F", "C", "useful")
        result_report["verdict"] = (
            "pass_local_screen"
            if result_report["go"]
            else "stop_no_go"
            if complete
            else "incomplete"
        )
    else:
        controls = [
            dict(r, arm="LM")
            for r in read("report_primary.json")["cells"]
            if r["arm"] == "F"
        ]
        combined = controls + rows
        contrasts = [
            paired(combined, a, b, "decision_correct", "repair_cost")
            for a, b in (("LM", "TL"), ("LM", "TM"), ("TL", "TM"))
        ]
        for key in ("p_two_sided", "cost_p_two_sided"):
            adjusted = holm([c.get(key, 1.0) for c in contrasts])
            for c, p in zip(contrasts, adjusted, strict=True):
                c[key + "_holm"] = p
        result_report["contrasts"] = dict(
            zip(("TL_vs_LM", "TM_vs_LM", "TM_vs_TL"), contrasts, strict=True)
        )
        result_report["verdict"] = (
            "diagnostic_only" if complete else "incomplete_no_ranking"
        )
    write_new(CAMPAIGN / f"report_{stage}.json", result_report)
    with (CAMPAIGN / f"receipts_{stage}.csv").open("x", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(receipts[0]) if receipts else ["id"]
        )
        writer.writeheader()
        writer.writerows(r for r in receipts if r["stage"] == stage)
    print(
        json.dumps(
            {
                k: v
                for k, v in result_report.items()
                if k not in ("cells", "comparison", "contrasts")
            },
            indent=2,
        )
    )


def main() -> None:
    command = sys.argv[1]
    if command == "prepare":
        prepare()
    elif command == "seal":
        seal()
    elif command in ("primary", "terra"):
        report(command)
    else:
        raise ValueError("no paid or full-problem command")


if __name__ == "__main__":
    main()
