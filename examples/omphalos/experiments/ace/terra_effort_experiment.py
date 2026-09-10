"""2026-09-10 user-authorized high-effort extension; six trainX resets.

Primary endpoint: correct applicability versus archived Terra medium.
Practical signal: >=1 additional correct decision, no lost correct state;
report cost/correct and all-cell cost separately, never promote from this
panel. Secondary comparator: archived Terra low. Family two-sided p<.10,
Holm over two comparisons per endpoint; descriptive 90% intervals.
Ceiling $1.20 (high $1.20, retries/teacher $0); <=4 requests per state,
local $1 reservation allowance, one worker. No automatic expansion/retries.
Identical frozen strategy, demos, tools and output cap; only effort changes.
Historical controls make this exploratory, not a fresh randomized trial.
Both harnesses: python -m experiments.ace.terra_effort_experiment
prepare | report | run --max_workers=1 --wait.
"""

from dataclasses import asdict
from datetime import datetime, timezone
import csv
import json
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any

import delphyne as dp
import yaml
from experiments.ace.change_control_experiment import (
    ChangeConfig,
    authorize,
    configs as old_configs,
    name,
)
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.model_registry import price_tokens
from tools.reports import change_control_report as old

CAMPAIGN = old.ROOT / "experiments/campaigns/terra_high_20260910"
OUTPUT = "experiments/output/terra_high_20260910"


def configs() -> list[ChangeConfig]:
    result = [c for c in old_configs("terra") if c.arm_label == "TM"]
    for c in result:
        c.arm_label = "TH"
        c.reasoning_effort = "high"
    return result


def check_freeze() -> None:
    authorize("terra")
    sealed = json.loads((CAMPAIGN / "sealed.json").read_text())
    for path, sha in sealed["execution_hashes"].items():
        if old.digest(old.ROOT / path) != sha:
            raise ValueError(f"source changed: {path}")


def prepare() -> None:
    authorize("terra")
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    old.write_new(
        CAMPAIGN / "registration.json",
        {
            "approval": "User requested checking scaled Terra effort",
            "ceiling": 1.2,
            "allocations": {"high": 1.2},
            "retries": 0,
            "teacher": 0,
            "full_problems": 0,
            "schedule": [
                {"cell": name(c, None), "state": c.state_id, "seed": 0}
                for c in configs()
            ],
            "protocol": __doc__,
            "settings": old.read("registration.json")["settings"],
            "effort_override": "high",
            "controls": "change_control_20260910/report_terra.json",
            "historical_controls": True,
        },
    )
    paths = [
        Path(__file__),
        CAMPAIGN / "registration.json",
        old.CAMPAIGN / "report_terra.json",
        old.CAMPAIGN / "sealed.json",
    ]
    old.write_new(
        CAMPAIGN / "sealed.json",
        {
            "execution_hashes": {
                str(p.relative_to(old.ROOT)): old.digest(p) for p in paths
            }
        },
    )


def report() -> None:
    check_freeze()
    with sqlite3.connect(
        f"file:{CAMPAIGN / 'ledger.sqlite3'}?mode=ro", uri=True
    ) as db:
        db.row_factory = sqlite3.Row
        receipts = [
            dict(r)
            for r in db.execute("SELECT * FROM receipts ORDER BY created,id")
        ]
    for r in receipts:
        if r["status"] == "settled":
            u = json.loads(r["usage"])
            cost = price_tokens(
                r["model"],
                u.get("input_tokens", 0),
                u.get("input_tokens_details", {}).get("cached_tokens", 0),
                u.get("output_tokens", 0),
                on=datetime.fromtimestamp(r["created"], timezone.utc).date(),
            )
            if r["charged"] is None or abs(cost - r["charged"]) > 1e-9:
                raise ValueError("repricing mismatch")
    states = {s["id"]: s for s in old.read("artifact.json")["states"]}
    rows: list[dict[str, Any]] = []
    for c in configs():
        cell = name(c, None)
        directory = old.ROOT / OUTPUT / "configs" / cell
        result, repair = old.result_of(directory)
        charges = [r for r in receipts if r["cell"] == cell]
        cost = sum(
            r["charged"] if r["charged"] is not None else r["reserved"]
            for r in charges
        )
        error = "\n".join(
            p.read_text() for p in directory.glob("exception*.txt")
        )
        positive = states[c.state_id]["positive"]
        correct = bool(
            repair
            and (
                repair.executed
                if positive
                else repair.decision.decision == "abstain"
                and repair.status == "abstained"
                and (
                    repair.checked is None
                    or repair.checked.outcome == "rejected"
                )
            )
        )
        calls: list[Any] = []
        cache = directory / "cache.yaml"
        if cache.exists():
            entries: Any = yaml.load(
                cache.read_text(), Loader=yaml.CSafeLoader
            )
            for entry in entries:
                for output in entry["output"].get("outputs", []):
                    calls.extend(output.get("tool_calls", []) or [])
        usage = [json.loads(r["usage"]) for r in charges if r["usage"]]
        rows.append(
            {
                "cell": cell,
                "state_id": c.state_id,
                "bench": c.bench_name,
                "arm": "TH",
                "seed": 0,
                "positive": positive,
                "decision_correct": correct,
                "repair": asdict(repair) if repair else None,
                "cost": cost,
                "repair_cost": cost,
                "requests": len(charges),
                "platform_failed": bool(error),
                "exception": error,
                "missing": result is None,
                "censored": "CampaignExhausted" in error,
                "tool_calls": calls,
                "reasoning_tokens": sum(
                    u.get("output_tokens_details", {}).get(
                        "reasoning_tokens", 0
                    )
                    for u in usage
                ),
                "input_tokens": sum(u.get("input_tokens", 0) for u in usage),
                "cached_tokens": sum(
                    u.get("input_tokens_details", {}).get("cached_tokens", 0)
                    for u in usage
                ),
                "output_tokens": sum(u.get("output_tokens", 0) for u in usage),
            }
        )
    unresolved = [r["id"] for r in receipts if r["charged"] is None]
    complete = not unresolved and not any(
        r["missing"] or r["platform_failed"] or r["censored"] for r in rows
    )
    controls = old.read("report_terra.json")["cells"]
    combined = controls + rows
    contrasts = {
        arm: old.paired(combined, arm, "TH", "decision_correct", "repair_cost")
        for arm in ("TM", "TL")
    }
    for key in ("p_two_sided", "cost_p_two_sided"):
        ps = old.holm([c.get(key, 1.0) for c in contrasts.values()])
        for c, p in zip(contrasts.values(), ps, strict=True):
            c[key + "_holm"] = p
    medium = {r["state_id"]: r for r in controls if r["arm"] == "TM"}
    correct = sum(r["decision_correct"] for r in rows)
    cost = sum(r["cost"] for r in rows)
    old.write_new(
        CAMPAIGN / "report.json",
        {
            "complete": complete,
            "cells": rows,
            "cost": cost,
            "correct": correct,
            "denominator": 6,
            "cost_per_correct": cost / correct if correct else None,
            "requests": len(receipts),
            "unresolved": unresolved,
            "contrasts": contrasts,
            "practical_signal": bool(
                complete
                and correct
                >= 1 + sum(r["decision_correct"] for r in medium.values())
                and all(
                    not medium[r["state_id"]]["decision_correct"]
                    or r["decision_correct"]
                    for r in rows
                )
            ),
            "promote": False,
            "full_problems": 0,
            "qualified_solves": 0,
            "cost_per_qualified_solve": None,
            "ledger": Ledger(CAMPAIGN / "ledger.sqlite3").summary(),
        },
    )
    with (CAMPAIGN / "receipts.csv").open("x", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(receipts[0]) if receipts else ["id"]
        )
        writer.writeheader()
        writer.writerows(receipts)


def main() -> None:
    if sys.argv[1:] == ["prepare"]:
        prepare()
        return
    if sys.argv[1:] == ["report"]:
        report()
        return
    if any("retry" in arg for arg in sys.argv):
        raise ValueError("retries not authorized")
    check_freeze()
    if "run" in sys.argv:
        Ledger(CAMPAIGN / "ledger.sqlite3").create(1.2, {"high": 1.2})
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = "high"
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")
    ol.OmphalosExperiment(
        config_class=ChangeConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs(),
        output_dir=OUTPUT,
        config_naming=name,
        wait_for_slots=True,
        attempts=1,
    ).run_cli()


if __name__ == "__main__":
    main()
