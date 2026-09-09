"""
Regenerate the data blocks embedded in `report/ace_report.html`.

Mirrors `tools/reports/report_chart_data.py`, including its central rule: only
the `const NAME = ...;` lines inside the report's script are replaced,
so prose and styling survive a regeneration untouched, and a run that
finds nothing to change is a check that the figures on the page still
match the data behind them.

One generator feeds one live report. `report/meeting_report.html`
belongs to `report_chart_data.py`, and `report/cost_report.html` is a
frozen 2026-08-12 snapshot that is never regenerated.

Usage:
    python -m tools.reports.ace_report_data            # rewrite the report
    python -m tools.reports.ace_report_data --print    # dump JSON, touch nothing
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import csv
import json
import re
import statistics
from pathlib import Path
from typing import Any


from tools.analysis.budget_ablation import LOG_DOLLAR_CAPS, Trace, load_run  # noqa: E402
from tools.analysis.decision_audit import sign_test  # noqa: E402
from tools.analysis.failure_analysis import load_run as load_verdicts, tally  # noqa: E402
from ace.ace_playbook import Playbook  # noqa: E402
from runtime.model_registry import pricing_for  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT

REPORT = _OMPHALOS_DIR / "report" / "ace_report.html"

MODEL = "gpt-5.6-luna"
CANONICAL = {"reasoning_effort": "medium", "toolset": "core"}

ARMS = {
    "validation": (
        "experiments/output/luna_validation_agentic",
        "experiments/output/ace_validation_agentic",
    ),
    "test": (
        "experiments/output/luna_test_agentic",
        "experiments/output/ace_test_agentic",
    ),
}

_NAME_RE = re.compile(
    r"^(?P<bench>.+?)__(?P<arm>.+?)__.+?__seed(?P<seed>\d+)$"
)

type Cell = tuple[str, str]


def _cells(path: Path, canonical_only: bool) -> dict[Cell, dict[str, Any]]:
    """`(bench, seed) -> {solved, cost, output, input, cached}`."""
    rates = pricing_for(MODEL)
    out: dict[Cell, dict[str, Any]] = {}
    summary = path / "results_summary.csv"
    if not summary.exists():
        return out
    for row in csv.DictReader(summary.open()):
        if canonical_only and any(
            row.get(k) != v for k, v in CANONICAL.items()
        ):
            continue
        inp = int(row["input_tokens"])
        cached = int(row["cached_input_tokens"])
        outp = int(row["output_tokens"])
        out[(row["bench_name"], row["seed"])] = {
            "solved": row["success"] == "True",
            "cost": (
                (inp - cached) * rates.dollars_per_input_token
                + cached * rates.dollars_per_cached_input_token
                + outp * rates.dollars_per_output_token
            ),
            "output": outp,
            "input": inp,
            "cached": cached,
        }
    return out


def build_paired() -> dict[str, Any]:
    """Per-cell baseline-vs-ACE costs, plus the paired statistics."""
    blocks: dict[str, Any] = {}
    for part, (b_run, a_run) in ARMS.items():
        base = _cells(_OMPHALOS_DIR / b_run, True)
        ace = _cells(_OMPHALOS_DIR / a_run, False)
        cells = sorted(set(base) & set(ace))
        if not cells:
            continue
        pts = [
            {
                "bench": c[0],
                "seed": c[1],
                "base": round(base[c]["cost"], 6),
                "ace": round(ace[c]["cost"], 6),
                "baseSolved": base[c]["solved"],
                "aceSolved": ace[c]["solved"],
            }
            for c in cells
        ]
        b_only = sum(
            1 for c in cells if base[c]["solved"] and not ace[c]["solved"]
        )
        a_only = sum(
            1 for c in cells if ace[c]["solved"] and not base[c]["solved"]
        )
        joint = [c for c in cells if base[c]["solved"] and ace[c]["solved"]]
        ratios = [ace[c]["cost"] / base[c]["cost"] for c in joint]
        blocks[part] = {
            "points": pts,
            "cells": len(cells),
            "baseSolved": sum(base[c]["solved"] for c in cells),
            "aceSolved": sum(ace[c]["solved"] for c in cells),
            "baseOnly": b_only,
            "aceOnly": a_only,
            "p": round(sign_test(b_only, a_only), 4),
            "joint": len(joint),
            "medianRatio": (
                round(statistics.median(ratios), 4) if ratios else None
            ),
            "medOutputBase": statistics.median(
                base[c]["output"] for c in joint
            )
            if joint
            else None,
            "medOutputAce": statistics.median(ace[c]["output"] for c in joint)
            if joint
            else None,
            "cachedBase": round(
                sum(base[c]["cached"] for c in joint)
                / max(sum(base[c]["input"] for c in joint), 1),
                4,
            )
            if joint
            else None,
            "cachedAce": round(
                sum(ace[c]["cached"] for c in joint)
                / max(sum(ace[c]["input"] for c in joint), 1),
                4,
            )
            if joint
            else None,
        }
    return blocks


def _trace_cells(run: str, select: dict[str, str]) -> dict[Cell, Trace]:
    out: dict[Cell, Trace] = {}
    for t in load_run(run, MODEL, True, select):
        m = _NAME_RE.match(t.name)
        assert m is not None, f"unexpected config name {t.name!r}"
        out[(m.group("bench"), m.group("seed"))] = t
    return out


def build_caps() -> dict[str, Any]:
    """
    Solves and spend against the per-problem dollar cap, both arms,
    paired per cell. Exact: a capped run is a prefix of a recorded one.
    """
    b_run, a_run = ARMS["validation"]
    base = _trace_cells(b_run, CANONICAL)
    ace = _trace_cells(a_run, CANONICAL)
    cells = sorted(set(base) & set(ace))
    rows: list[dict[str, Any]] = []
    for cap in LOG_DOLLAR_CAPS:
        b_solved = a_solved = b_only = a_only = 0
        b_spend = a_spend = 0.0
        for c in cells:
            bs, bok = base[c].under_dollar_cap(cap)
            as_, aok = ace[c].under_dollar_cap(cap)
            b_spend += bs
            a_spend += as_
            b_solved += bok
            a_solved += aok
            b_only += bok and not aok
            a_only += aok and not bok
        rows.append(
            {
                "cap": cap,
                "baseSolved": b_solved,
                "aceSolved": a_solved,
                "baseOnly": b_only,
                "aceOnly": a_only,
                "p": round(sign_test(b_only, a_only), 4),
                "baseSpend": round(b_spend, 5),
                "aceSpend": round(a_spend, 5),
            }
        )
    return {"cells": len(cells), "rows": rows}


def build_taxonomy() -> dict[str, Any]:
    """Rocq error classes by problems affected, both arms."""
    arm_re = re.compile(r"core-medium|ace-[0-9a-f]{8}(?:-k\d+)?-core-medium")
    out: dict[str, Any] = {}
    for label, run in (
        ("baseline", ARMS["validation"][0]),
        ("ace", ARMS["validation"][1]),
    ):
        path = _OMPHALOS_DIR / run
        if not (path / "results_summary.csv").exists():
            continue
        counts = tally(load_verdicts(path, arm_re))
        out[label] = {
            name: len(t.problems) for name, t in counts.items() if t.problems
        }
    return out


def build_adapt() -> dict[str, Any]:
    """
    Playbook size per adaptation step, per variant.

    Read from the per-step playbook *files* rather than `steps.csv`,
    because those are written after every step while the summary is
    only complete once a run finishes — so an in-flight or interrupted
    variant still charts correctly, and the chart can never show a
    stale trajectory from an earlier, shorter run. `steps.csv` is still
    consulted for the per-step merge counters it alone records.
    """
    out: dict[str, Any] = {}
    root = _OMPHALOS_DIR / "experiments" / "playbooks"
    for steps_dir in sorted(root.glob("ace_adaptation*")):
        if not steps_dir.is_dir():
            continue
        name = steps_dir.name.removeprefix("ace_adaptation")
        variant = name.lstrip("_") or "train"
        files = sorted(steps_dir.glob("playbook_step_*.yaml"))
        if len(files) < 2:
            continue
        counters: dict[int, dict[str, str]] = {}
        csv_path = steps_dir / "steps.csv"
        if csv_path.exists():
            for r in csv.DictReader(csv_path.open()):
                counters[int(r["step"])] = r
        steps: list[dict[str, Any]] = []
        for f in files:
            step = int(f.stem.rsplit("_", 1)[1])
            if step == 0:
                continue
            pb = Playbook.load(f)
            row = counters.get(step - 1, {})
            steps.append(
                {
                    "step": step - 1,
                    "bullets": len(pb.bullets),
                    "tokens": pb.token_estimate(),
                    "added": int(row.get("added", 0) or 0),
                    "deduped": int(row.get("deduped", 0) or 0),
                }
            )
        if not steps:
            continue
        first = counters.get(0, {})
        out[variant] = {
            "curatorMode": first.get("curator_mode", "incremental"),
            "reflector": first.get("reflector", "on"),
            "complete": len(steps) >= 20,
            "steps": steps,
        }
    return out


def build_defs() -> dict[str, Any]:
    """The definitions-visible arm against its paid control cells."""
    run = _OMPHALOS_DIR / "experiments" / "output" / "defs_agentic"
    if not (run / "results_summary.csv").exists():
        return {}
    defs = _cells(run, False)
    control: dict[Cell, dict[str, Any]] = {}
    for part in ("validation", "test"):
        control.update(_cells(_OMPHALOS_DIR / ARMS[part][0], True))
    rows: list[dict[str, Any]] = []
    for cell in sorted(defs):
        if cell not in control:
            continue
        rows.append(
            {
                "bench": cell[0],
                "seed": cell[1],
                "before": control[cell]["solved"],
                "after": defs[cell]["solved"],
            }
        )
    fixed = sum(1 for r in rows if r["after"] and not r["before"])
    broke = sum(1 for r in rows if r["before"] and not r["after"])
    return {"rows": rows, "fixed": fixed, "broke": broke}


def rewrite(report: Path, blocks: dict[str, Any]) -> bool:
    """
    Replace each `const NAME = ...;` line in the report's script.

    Only those lines are touched, so prose and styling survive a
    regeneration untouched.
    """
    text = report.read_text()
    original = text
    for name, value in blocks.items():
        payload = json.dumps(value, separators=(",", ":"))
        pattern = re.compile(rf"(const {name} = ).*?(;\n)", re.S)
        assert pattern.search(text), f"{name} not found in {report}"
        text = pattern.sub(
            lambda m: m.group(1) + payload + m.group(2), text, count=1
        )
    if text != original:
        report.write_text(text)
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate the JSON blocks in report/ace_report.html from "
            "the recorded runs. Offline; makes no API calls."
        )
    )
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()

    blocks: dict[str, Any] = {
        "PAIRED": build_paired(),
        "CAPS": build_caps(),
        "TAXONOMY": build_taxonomy(),
        "ADAPT": build_adapt(),
        "DEFS": build_defs(),
    }
    if args.print:
        print(json.dumps(blocks, indent=2))
        return 0
    assert REPORT.exists(), f"no report at {REPORT}"
    changed = rewrite(REPORT, blocks)
    print(
        f"{'Updated' if changed else 'No change to'} "
        f"{REPORT.relative_to(_OMPHALOS_DIR)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
