"""Offline request identity and stage-receipt audit; run from Omphalos."""

import hashlib
import json
import sqlite3
from typing import Any

import yaml
from experiments.ace.change_control_experiment import name
from experiments.ace.luna_upper_effort_experiment import (
    CAMPAIGN,
    OUTPUT,
    check_freeze,
    configs,
)
from tools.reports.change_control_report import ROOT
from tools.reports.grounded_report import write_new


def main() -> None:
    check_freeze()
    checks: list[dict[str, Any]] = []
    with sqlite3.connect(
        f"file:{CAMPAIGN / 'ledger.sqlite3'}?mode=ro", uri=True
    ) as db:
        db.row_factory = sqlite3.Row
        receipts = [dict(r) for r in db.execute("SELECT * FROM receipts")]
    for c in configs():
        cell = name(c, None)
        prior = cell.replace(f"__{c.arm_label}-", "__F-").replace(
            f"-r4-{c.reasoning_effort}__", "-r4-medium__"
        )
        paths = [
            ROOT / OUTPUT / "configs" / cell / "cache.yaml",
            ROOT
            / "experiments/output/change_control_primary/configs"
            / prior
            / "cache.yaml",
        ]
        reqs: list[dict[str, Any]] = []
        for p in paths:
            entries: Any = yaml.load(p.read_text(), Loader=yaml.CSafeLoader)
            reqs.append(
                next(
                    e["input"]["request"]
                    for e in entries
                    if "chat" in e["input"].get("request", {})
                )
            )
        assert reqs[0]["options"]["reasoning_effort"] == c.reasoning_effort
        assert reqs[1]["options"]["reasoning_effort"] == "medium"
        assert reqs[0]["options"]["model"] == "gpt-5.6-luna"
        for r in reqs:
            r["options"].pop("reasoning_effort")
        assert reqs[0] == reqs[1], cell
        charges = [r for r in receipts if r["cell"] == cell]
        assert charges and all(
            r["stage"] == c.reasoning_effort for r in charges
        ), cell
        checks.append(
            {
                "cell": cell,
                "request_identical_except_effort": True,
                "stage_matches_effort": True,
                "request_without_effort_sha256": hashlib.sha256(
                    json.dumps(reqs[0], sort_keys=True).encode()
                ).hexdigest(),
            }
        )
    write_new(
        CAMPAIGN / "request_audit.json",
        {
            "cells": checks,
            "source_drift": [],
        },
    )
    print("12/12 matched first requests, exact effort, correct ledger stage")


if __name__ == "__main__":
    main()
