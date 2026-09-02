"""
Chart data for `report/ace_x_report.html` — the ACE v2 study on the X
partitions, plus the solves-vs-cost evolution of the agentic prover.

Offline: reads recorded runs, recomputes every cost from token counts
at today's dated rate (`model_registry.pricing_for`), and rewrites only
the `const NAME = ...;` lines of the report, so prose and styling
survive a regeneration and a run that finds nothing to change is a
check that the figures still match the data. A JSON sidecar
(`report/ace_x_report.data.json`) is written as well, so the numbers
can be read without a browser.

Blocks:

- `EVOLUTION` — on the original test partition, one solves-vs-cap
  curve per generation of the prover: gpt-5.4 `rich` (chat), terra
  `rich` (chat), terra Responses `low`, luna canonical, ACE v1. Exact,
  by the prefix argument (`tools/budget_ablation.Trace`).
- `X_ARMS` — every arm recorded on validationX/testX: the baseline and
  each ACE playbook / online chain, with per-cell solved + cost.
- `X_PAIRED` — baseline-vs-arm pairing per partition: discordant
  cells, exact sign test, median cost ratio on jointly-solved cells.
- `X_CAPS` — paired solves-vs-cap curves on the X partitions.
- `X_ADAPT` — playbook trajectory per adaptation variant from
  `steps.csv` (bullets, tokens, dedup/refine counts, curator and
  reflector failure rates, and for online chains the running solves).
- `X_TAXONOMY` — Rocq error classes by problems affected, per arm.
- `X_COST` — adaptation spend by role per variant (the paper's Table
  12 analogue) and evaluation-stage token accounting (their Table 14 /
  KV-cache argument): input, cached share, output per arm.
- `META` — pricing date, partition sizes, generation time.

Usage:
    python tools/ace_x_report_data.py            # regenerate
    python tools/ace_x_report_data.py --check    # exit 1 if the page is stale
"""

# pyright: strict

import argparse
import csv
import json
import re
import statistics
import sys
from functools import cache
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any, cast

import yaml

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_OMPHALOS_DIR))
sys.path.insert(0, str(_OMPHALOS_DIR / "tools"))

from budget_ablation import LOG_DOLLAR_CAPS, Trace, load_run  # noqa: E402
from decision_audit import MIN_DISCORDANT_FOR_SIG, sign_test  # noqa: E402
from failure_analysis import load_run as load_verdicts  # noqa: E402
from failure_analysis import tally  # noqa: E402
from model_registry import current_pricing_date, pricing_for  # noqa: E402

from ace_playbook import Playbook  # noqa: E402
from cell_records import CellRecord, cells_of_run  # noqa: E402

REPORT = _OMPHALOS_DIR / "report" / "ace_x_report.html"
SIDECAR = _OMPHALOS_DIR / "report" / "ace_x_report.data.json"
OUTPUT = _OMPHALOS_DIR / "experiments" / "output"
PLAYBOOKS = _OMPHALOS_DIR / "experiments" / "playbooks"
BENCHMARKS = _OMPHALOS_DIR / "benchmarks"

LUNA = "gpt-5.6-luna"
CANONICAL = {"reasoning_effort": "medium", "toolset": "core"}

_NAME_RE = re.compile(
    r"^(?P<bench>.+?)__(?P<arm>.+?)__(?P<model>.+?)__seed(?P<seed>\d+)$"
)
_ACE_ARM_RE = re.compile(
    r"^ace-(?P<sha>[0-9a-f]{8})(?:-k(?P<k>\d+))?-core-medium$"
)

type Cell = tuple[str, str]


#####
##### Cells and traces
#####


def _cost(row: Mapping[str, str], model: str) -> float:
    rates = pricing_for(model)
    inp = int(row["input_tokens"])
    cached = int(row["cached_input_tokens"])
    outp = int(row["output_tokens"])
    return (
        (inp - cached) * rates.dollars_per_input_token
        + cached * rates.dollars_per_cached_input_token
        + outp * rates.dollars_per_output_token
    )


def _rows(run: Path) -> list[dict[str, str]]:
    summary = run / "results_summary.csv"
    if not summary.exists():
        return []
    with summary.open() as f:
        return list(csv.DictReader(f))


def _config_names(run: Path) -> dict[str, str]:
    """`bench__...` directory name per (bench, seed) via experiment.yaml."""
    state = run / "experiment.yaml"
    if not state.exists():
        return {}
    raw: Any = yaml.safe_load(state.read_text())
    return {name: name for name in raw["configs"]}


def _cells_of(
    run: Path, model: str, arm_re: "re.Pattern[str] | None"
) -> dict[str, dict[Cell, dict[str, Any]]]:
    """
    `arm -> (bench, seed) -> {solved, cost, input, cached, output,
    requests, platformFailed}` for every recorded cell of the run whose
    arm matches, from ground truth (`cell_records`): done cells and
    platform-failed cells (scored unsolved), never `todo` ones.
    """
    out: dict[str, dict[Cell, dict[str, Any]]] = {}
    for rec in cells_of_run(run):
        if rec.model != model:
            continue
        if arm_re is not None and not arm_re.match(rec.arm):
            continue
        out.setdefault(rec.arm, {})[rec.cell] = rec.as_dict()
    return out


def _records_of(
    run: Path, model: str, arm_re: "re.Pattern[str] | None"
) -> dict[str, list[CellRecord]]:
    out: dict[str, list[CellRecord]] = {}
    for rec in cells_of_run(run):
        if rec.model != model:
            continue
        if arm_re is not None and not arm_re.match(rec.arm):
            continue
        out.setdefault(rec.arm, []).append(rec)
    return out


def _traces(
    run: Path, model: str, arm_re: "re.Pattern[str] | None"
) -> dict[str, dict[Cell, Trace]]:
    out: dict[str, dict[Cell, Trace]] = {}
    if not (run / "results_summary.csv").exists():
        return out
    for t in load_run(str(run.relative_to(_OMPHALOS_DIR)), model, False):
        m = _NAME_RE.match(t.name)
        assert m is not None, t.name
        if arm_re is not None and not arm_re.match(m.group("arm")):
            continue
        out.setdefault(m.group("arm"), {})[
            (m.group("bench"), m.group("seed"))
        ] = t
    return out


def _curve(traces: Sequence[Trace]) -> list[dict[str, float | int]]:
    pts: list[dict[str, float | int]] = []
    for cap in LOG_DOLLAR_CAPS:
        spend = 0.0
        solved = 0
        for t in traces:
            s, ok = t.under_dollar_cap(cap)
            spend += s
            solved += ok
        pts.append({"cap": cap, "spend": round(spend, 5), "solved": solved})
    return pts


#####
##### Blocks
#####


EVOLUTION_ARMS: tuple[
    tuple[str, str, str, str, dict[str, str] | None], ...
] = (
    (
        "gpt54",
        "gpt-5.4 · rich · chat (2026-06)",
        "experiments/previous/gpt54_set3_agentic",
        "gpt-5.4-2026-03-05",
        None,
    ),
    (
        "terra_chat",
        "terra · rich · chat, uncapped (2026-07-21)",
        "experiments/output/test_agentic",
        "gpt-5.6-terra",
        {"toolset": "rich"},
    ),
    (
        "terra_resp",
        "terra · Responses · low · $0.30 cap (2026-08-12)",
        "experiments/output/responses_test_agentic",
        "gpt-5.6-terra",
        None,
    ),
    (
        "luna",
        "luna · core · medium · $0.05 cap (2026-08-13)",
        "experiments/output/luna_test_agentic",
        LUNA,
        {"reasoning_effort": "medium", "toolset": "core"},
    ),
    (
        "ace_v1",
        "luna + ACE v1 playbook (2026-08-24)",
        "experiments/output/ace_test_agentic",
        LUNA,
        None,
    ),
)


def build_evolution() -> dict[str, Any]:
    """Solves vs spend at every cap, per generation, original test set."""
    arms: list[dict[str, Any]] = []
    for key, label, run, model, select in EVOLUTION_ARMS:
        if not (_OMPHALOS_DIR / run / "results_summary.csv").exists():
            continue
        traces = load_run(run, model, False, select)
        arms.append(
            {
                "key": key,
                "label": label,
                "model": model,
                "cells": len(traces),
                "solved": sum(t.solved_at is not None for t in traces),
                "spend": round(sum(sum(t.prices) for t in traces), 4),
                "curve": _curve(traces),
            }
        )
    return {"partition": "test (original, 20 problems)", "arms": arms}


@cache
def _playbook_labels() -> dict[str, str]:
    """sha8 -> frozen playbook file name."""
    out: dict[str, str] = {}
    for f in sorted(PLAYBOOKS.glob("*.yaml")):
        if f.name.endswith(".provenance.yaml"):
            continue
        out[Playbook.load(f).sha256()[:8]] = f.stem
    return out


def _arm_label(arm: str, labels: Mapping[str, str]) -> str:
    m = _ACE_ARM_RE.match(arm)
    if m is None:
        return arm
    name = labels.get(m.group("sha"), f"playbook {m.group('sha')}")
    return f"{name} (top{m.group('k')})" if m.group("k") else name


def _provenance_rv(stem: str) -> int | None:
    side = PLAYBOOKS / f"{stem}.provenance.yaml"
    if not side.exists():
        return None
    raw: Any = yaml.safe_load(side.read_text())
    rv = cast(dict[str, Any], raw or {}).get("render_version")
    return int(rv) if rv is not None else None


def _qualified_label(
    arm: str,
    records: Sequence[CellRecord],
    labels: Mapping[str, str],
    seen: dict[str, int],
) -> str:
    """
    Label of an evaluated arm: the playbook stem (+ `(topK)`), then
    ` · rv{N}` when the cells were rendered at a version other than the
    one the playbook was adapted under, then ` · replicate{i}` when the
    same (playbook, rv, injection) was already labelled from an earlier
    directory — an identical-config rerun, which is noise-floor
    evidence, not a new arm.
    """
    base = _arm_label(arm, labels)
    rv = int(records[0].params.get("render_version", 1)) if records else 1
    m = _ACE_ARM_RE.match(arm)
    stem = labels.get(m.group("sha"), "") if m else ""
    prov = _provenance_rv(stem) if stem else None
    label = base if prov is None or prov == rv else f"{base} · rv{rv}"
    n = seen.get(label, 0)
    seen[label] = n + 1
    return label if n == 0 else f"{label} · replicate{n}"


X_PARTS = ("validationX", "testX")


@cache
def _x_arms(part: str) -> dict[str, dict[str, Any]]:
    """
    Every arm on one X partition: `label -> {cells, kind}`.

    Baseline from `x_<part>_agentic`; frozen playbooks from
    `ace_x_<part>_agentic` (one arm per sha8); online chains from every
    `ace_online_<variant>_agentic` whose problems lie in the partition.
    """
    short = part.removesuffix("X").lower()
    labels = _playbook_labels()
    out: dict[str, dict[str, Any]] = {}
    base = _cells_of(OUTPUT / f"x_{short}_agentic", LUNA, None)
    for arm, cells in base.items():
        out["baseline"] = {"cells": cells, "kind": "baseline", "arm": arm}
    arm_dirs = [OUTPUT / f"ace_x_{short}_agentic"] + sorted(
        OUTPUT.glob(f"ace_x_{short}_ace_*_agentic")
    )
    seen: dict[str, int] = {}
    for run_dir in arm_dirs:
        for arm, recs in _records_of(run_dir, LUNA, _ACE_ARM_RE).items():
            label = _qualified_label(arm, recs, labels, seen)
            out[label] = {
                "cells": {r.cell: r.as_dict() for r in recs},
                "kind": "offline",
                "arm": arm,
                "dir": run_dir.name,
            }
    partition = set(_partition(part))
    for run in sorted(OUTPUT.glob("ace_online_*_agentic")):
        variant = run.name.removeprefix("ace_online_").removesuffix("_agentic")
        cells: dict[Cell, dict[str, Any]] = {}
        for _arm, arm_cells in _cells_of(run, LUNA, _ACE_ARM_RE).items():
            cells.update(arm_cells)
        if cells and all(c[0] in partition for c in cells):
            out[f"online {variant}"] = {
                "cells": cells,
                "kind": "online",
                "arm": variant,
            }
    return out


def _partition(part: str) -> list[str]:
    path = BENCHMARKS / f"{part}.txt"
    return [
        Path(line.strip()).stem
        for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def _serialise_cells(
    cells: Mapping[Cell, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "bench": b,
            "seed": s,
            **{
                k: (round(v, 6) if isinstance(v, float) else v)
                for k, v in d.items()
            },
        }
        for (b, s), d in sorted(cells.items())
    ]


def build_x_arms() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for part in X_PARTS:
        arms = _x_arms(part)
        if not arms:
            continue
        out[part] = {
            label: {
                "kind": a["kind"],
                "dir": a.get("dir"),
                "cells": _serialise_cells(a["cells"]),
                "solved": sum(1 for c in a["cells"].values() if c["solved"]),
                "n": len(a["cells"]),
                "failed": sum(
                    1 for c in a["cells"].values() if c.get("platformFailed")
                ),
                "spend": round(sum(c["cost"] for c in a["cells"].values()), 4),
            }
            for label, a in arms.items()
        }
    return out


def _pair(
    base: Mapping[Cell, Mapping[str, Any]],
    other: Mapping[Cell, Mapping[str, Any]],
    *,
    with_sensitivity: bool = True,
) -> dict[str, Any]:
    """
    Paired readout. Platform-failed cells count as unsolved (the
    conservative reading); `dropFailed` repeats the readout on the
    cells that completed on both sides (the pre-2026-08-26 behaviour),
    so a reader can see whether the failures moved anything.
    """
    cells = sorted(set(base) & set(other))
    if with_sensitivity:
        ok = [
            c
            for c in cells
            if not base[c].get("platformFailed")
            and not other[c].get("platformFailed")
        ]
        drop = _pair(
            {c: base[c] for c in ok},
            {c: other[c] for c in ok},
            with_sensitivity=False,
        )
        drop_failed = {
            k: drop[k]
            for k in (
                "cells",
                "baseSolved",
                "armSolved",
                "baseOnly",
                "armOnly",
                "p",
                "medianCostRatio",
            )
        }
    else:
        drop_failed = None
    b_only = sum(
        1 for c in cells if base[c]["solved"] and not other[c]["solved"]
    )
    o_only = sum(
        1 for c in cells if other[c]["solved"] and not base[c]["solved"]
    )
    both = [c for c in cells if base[c]["solved"] and other[c]["solved"]]
    ratios = [
        other[c]["cost"] / base[c]["cost"] for c in both if base[c]["cost"] > 0
    ]
    cheaper = sum(1 for r in ratios if r < 0.98)
    dearer = sum(1 for r in ratios if r > 1.02)
    return {
        "cells": len(cells),
        "baseSolved": sum(1 for c in cells if base[c]["solved"]),
        "armSolved": sum(1 for c in cells if other[c]["solved"]),
        "baseOnly": b_only,
        "armOnly": o_only,
        "p": round(sign_test(b_only, o_only), 4),
        "pOneSided": round(sign_test(b_only, o_only, one_sided=True), 4),
        "underpowered": (b_only + o_only) < MIN_DISCORDANT_FOR_SIG,
        "jointlySolved": len(both),
        "medianCostRatio": round(statistics.median(ratios), 3)
        if ratios
        else None,
        "cheaper": cheaper,
        "dearer": dearer,
        "pCost": round(sign_test(dearer, cheaper), 4) if ratios else None,
        "baseSpend": round(sum(base[c]["cost"] for c in cells), 4),
        "armSpend": round(sum(other[c]["cost"] for c in cells), 4),
        "baseOutputMedian": statistics.median(base[c]["output"] for c in cells)
        if cells
        else None,
        "armOutputMedian": statistics.median(other[c]["output"] for c in cells)
        if cells
        else None,
        "baseFailed": sum(1 for c in cells if base[c].get("platformFailed")),
        "armFailed": sum(1 for c in cells if other[c].get("platformFailed")),
        "dropFailed": drop_failed,
    }


@cache
def build_x_paired() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for part in X_PARTS:
        arms = _x_arms(part)
        if "baseline" not in arms:
            continue
        base = arms["baseline"]["cells"]
        out[part] = {
            label: {"kind": a["kind"], **_pair(base, a["cells"])}
            for label, a in arms.items()
            if label != "baseline"
        }
    return out


def build_x_caps() -> dict[str, Any]:
    out: dict[str, Any] = {}
    labels = _playbook_labels()
    for part in X_PARTS:
        short = part.removesuffix("X").lower()
        base = _traces(OUTPUT / f"x_{short}_agentic", LUNA, None)
        if not base:
            continue
        base_cells = next(iter(base.values()))
        arms: dict[str, dict[Cell, Trace]] = {}
        for arm, cells in _traces(
            OUTPUT / f"ace_x_{short}_agentic", LUNA, _ACE_ARM_RE
        ).items():
            arms[_arm_label(arm, labels)] = cells
        partition = set(_partition(part))
        for run in sorted(OUTPUT.glob("ace_online_*_agentic")):
            variant = run.name.removeprefix("ace_online_").removesuffix(
                "_agentic"
            )
            merged: dict[Cell, Trace] = {}
            for cells in _traces(run, LUNA, _ACE_ARM_RE).values():
                merged.update(cells)
            if merged and all(c[0] in partition for c in merged):
                arms[f"online {variant}"] = merged
        block: dict[str, Any] = {
            "baseline": _curve([base_cells[c] for c in sorted(base_cells)]),
            "cellsTotal": len(base_cells),
        }
        for label, cells in arms.items():
            common = sorted(set(base_cells) & set(cells))
            rows: list[dict[str, Any]] = []
            for cap in LOG_DOLLAR_CAPS:
                b_solved = a_solved = b_only = a_only = 0
                b_spend = a_spend = 0.0
                for c in common:
                    bs, bok = base_cells[c].under_dollar_cap(cap)
                    as_, aok = cells[c].under_dollar_cap(cap)
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
                        "armSolved": a_solved,
                        "baseOnly": b_only,
                        "armOnly": a_only,
                        "p": round(sign_test(b_only, a_only), 4),
                        "baseSpend": round(b_spend, 5),
                        "armSpend": round(a_spend, 5),
                    }
                )
            block[label] = {"cells": len(common), "rows": rows}
        out[part] = block
    return out


@cache
def build_x_adapt() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for d in sorted(PLAYBOOKS.glob("ace_adaptation*")):
        if not d.is_dir():
            continue
        variant = (
            d.name.removeprefix("ace_adaptation").removeprefix("_") or "train"
        )
        csv_path = d / "steps.csv"
        if not csv_path.exists():
            continue
        with csv_path.open() as f:
            rows = list(csv.DictReader(f))
        if not rows:
            continue
        v2 = int(rows[0].get("schema_version") or 0) >= 2
        steps: list[dict[str, Any]] = []
        cum_solved = 0
        for r in rows:
            solved = int(r.get("generator_solved") or 0) if v2 else None
            if solved:
                cum_solved += 1
            steps.append(
                {
                    "step": int(r["step"]),
                    "epoch": int(r.get("epoch") or 0),
                    "bench": r["bench"],
                    "bullets": int(r["bullets_after"]),
                    "tokens": int(r["tokens_after"]),
                    "added": int(r["added"]),
                    "deduped": int(r["deduped"]),
                    "dropped": int(r["dropped"]),
                    "refined": int(r.get("refined") or 0),
                    "pruned": int(r.get("pruned") or 0),
                    "merged": int(r.get("merged") or 0),
                    "compacted": int(r.get("compacted") or 0),
                    "solved": solved,
                    "cumSolved": cum_solved if v2 else None,
                    "curatorFailed": int(r.get("curator_failed") or 0),
                    "reflectorFailed": int(r.get("reflector_failed") or 0),
                    "citedCount": (
                        int(r["cited_count"])
                        if r.get("cited_count") not in (None, "")
                        else None
                    ),
                    "tagsDropped": int(r.get("tags_dropped") or 0),
                    # schema 4 (2026-09-02): the accounting v3 lacked
                    "skippedTrivial": int(r.get("skipped_trivial") or 0),
                    "proposed": int(r.get("proposed") or 0),
                    "reducedOut": int(r.get("reduced_out") or 0),
                    "ungrounded": int(r.get("ungrounded") or 0),
                    "groundingError": int(r.get("grounding_error") or 0),
                }
            )
        out[variant] = {
            "mode": rows[0].get("mode") or "offline",
            "schema": 2 if v2 else 1,
            "steps": steps,
            "curatorFailRate": round(
                sum(s["curatorFailed"] for s in steps) / len(steps), 3
            ),
            "reflectorFailRate": round(
                sum(s["reflectorFailed"] for s in steps) / len(steps), 3
            ),
            "dedupTotal": sum(s["deduped"] for s in steps),
            "prunedTotal": sum(
                s["pruned"] + s["merged"] + s["compacted"] for s in steps
            ),
        }
    return out


def build_x_taxonomy() -> dict[str, Any]:
    out: dict[str, Any] = {}
    labels = _playbook_labels()
    for part in X_PARTS:
        short = part.removesuffix("X").lower()
        block: dict[str, Any] = {}
        base_run = OUTPUT / f"x_{short}_agentic"
        if not (base_run / "results_summary.csv").exists():
            continue
        block["baseline"] = _tally(base_run, re.compile(r"core-medium"))
        seen: dict[str, int] = {}
        for ace_run in [OUTPUT / f"ace_x_{short}_agentic"] + sorted(
            OUTPUT.glob(f"ace_x_{short}_ace_*_agentic")
        ):
            if not (ace_run / "results_summary.csv").exists():
                continue
            for arm, recs in _records_of(ace_run, LUNA, _ACE_ARM_RE).items():
                label = _qualified_label(arm, recs, labels, seen)
                block[label] = _tally(ace_run, re.compile(re.escape(arm)))
        partition = set(_partition(part))
        for run in sorted(OUTPUT.glob("ace_online_*_agentic")):
            if not (run / "results_summary.csv").exists():
                continue
            benches = {
                m.group("bench")
                for n in _config_names(run)
                if (m := _NAME_RE.match(n))
            }
            if benches and benches <= partition:
                variant = run.name.removeprefix("ace_online_").removesuffix(
                    "_agentic"
                )
                block[f"online {variant}"] = _tally(run, _ACE_ARM_RE)
        out[part] = block
    return out


def _tally(run: Path, arm: "re.Pattern[str]") -> dict[str, Any]:
    verdicts = load_verdicts(run, arm)
    t = tally(verdicts)
    return {
        cls: {"problems": len(v.problems), "verdicts": v.verdicts}
        for cls, v in t.items()
        if v.verdicts
    }


@cache
def build_x_cost() -> dict[str, Any]:
    """Adaptation spend by role per variant; evaluation-stage tokens."""
    adapt: dict[str, Any] = {}
    for run in sorted(OUTPUT.glob("ace_adaptation_*")):
        variant = run.name.removeprefix("ace_adaptation_")
        rows = _rows(run)
        if not rows:
            continue
        by_role: dict[str, dict[str, float]] = {}
        for r in rows:
            role = r.get("role") or "?"
            d = by_role.setdefault(
                role,
                {
                    "calls": 0,
                    "input": 0,
                    "cached": 0,
                    "output": 0,
                    "spend": 0.0,
                },
            )
            d["calls"] += 1
            d["input"] += int(r["input_tokens"])
            d["cached"] += int(r["cached_input_tokens"])
            d["output"] += int(r["output_tokens"])
            d["spend"] += _cost(r, r["model_name"])
        adapt[variant] = {
            role: {
                k: (round(v, 4) if k == "spend" else int(v))
                for k, v in d.items()
            }
            for role, d in by_role.items()
        }
        adapt[variant]["total"] = round(
            sum(d["spend"] for d in by_role.values()), 4
        )
    evaluation: dict[str, Any] = {}
    for part in X_PARTS:
        arms = _x_arms(part)
        if not arms:
            continue
        evaluation[part] = {}
        for label, a in arms.items():
            cells = a["cells"].values()
            inp = sum(c["input"] for c in cells)
            cached = sum(c["cached"] for c in cells)
            evaluation[part][label] = {
                "cells": len(a["cells"]),
                "failed": sum(1 for c in cells if c.get("platformFailed")),
                "input": inp,
                "cached": cached,
                "cachedShare": round(cached / inp, 3) if inp else None,
                "output": sum(c["output"] for c in cells),
                "requests": sum(c["requests"] for c in cells),
                "spend": round(sum(c["cost"] for c in cells), 4),
                "medianOutputPerCell": statistics.median(
                    c["output"] for c in cells
                )
                if cells
                else None,
            }
    return {"adaptation": adapt, "evaluation": evaluation}


#####
##### The paper's experiments, and the reference audit, from data
#####


def _find_pair(part: str, label: str) -> dict[str, Any] | None:
    block = build_x_paired().get(part, {})
    return cast(dict[str, Any] | None, block.get(label))


def _delta(p: Mapping[str, Any] | None) -> str | None:
    if p is None:
        return None
    d = int(p["armSolved"]) - int(p["baseSolved"])
    s = f"{d:+d} solves ({p['armOnly']}–{p['baseOnly']} discordant, p={p['p']}"
    if p.get("underpowered"):
        s += ", underpowered"
    s += f") · cost ×{p.get('medianCostRatio') or '?'}"
    if p.get("armFailed") or p.get("baseFailed"):
        s += f" · failed cells arm {p.get('armFailed')}/base {p.get('baseFailed')}"
    return s


def _adapt_stats(variant: str) -> dict[str, Any] | None:
    return cast(dict[str, Any] | None, build_x_adapt().get(variant))


def _collapse(variant: str) -> str | None:
    a = _adapt_stats(variant)
    if a is None:
        return None
    steps = cast(list[dict[str, Any]], a["steps"])
    drop = 0
    for i in range(1, len(steps)):
        drop = min(drop, int(steps[i]["tokens"]) - int(steps[i - 1]["tokens"]))
    fails = round(float(a["curatorFailRate"]) * 100)
    return (
        f"largest one-step size change {drop} tok over {len(steps)} steps; "
        f"curator failed {fails}% of rewrites"
    )


def _paper_row(
    key: str,
    paper: str,
    their: str,
    ours_setting: str,
    ours_result: str | None,
    assessment: str,
    status: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "paper": paper,
        "theirResult": their,
        "ourSetting": ours_setting,
        "ourResult": ours_result,
        "assessment": assessment,
        "status": status,
    }


def _direction(
    arm: Mapping[str, Any] | None, positive: bool
) -> tuple[str, str]:
    """`(assessment, status)` of one paired arm against the paper's sign."""
    if arm is None:
        return "not yet measured", "pending"
    d = int(arm["armSolved"]) - int(arm["baseSolved"])
    signed = d if positive else -d
    if arm.get("underpowered"):
        if d == 0:
            return "null (no discordant signal)", "measured"
        return (
            "direction matches, underpowered"
            if signed > 0
            else "direction differs, underpowered"
        ), "measured"
    return ("replicates" if signed > 0 else "does not replicate"), "measured"


def _gap(
    a: Mapping[str, Any] | None,
    b: Mapping[str, Any] | None,
    paper_says_a_lower: bool,
) -> tuple[str | None, str, str]:
    """Compare two arms' deltas vs baseline: `(text, assessment, status)`."""
    if a is None or b is None:
        return None, "not yet measured", "pending"
    da = int(a["armSolved"]) - int(a["baseSolved"])
    db = int(b["armSolved"]) - int(b["baseSolved"])
    text = f"{da:+d} vs {db:+d} solves against baseline"
    if da == db:
        return text, "no gap here", "measured"
    matches = (da < db) == paper_says_a_lower
    return (
        text,
        ("direction matches" if matches else "direction differs"),
        "measured",
    )


def build_x_paper() -> list[dict[str, Any]]:
    """
    The paper's experiment matrix mapped onto our arms, computed from
    the paired blocks. Rows whose arm has not run say so (`pending`);
    rows we deliberately do not run say so (`not-run`); rows that are
    a property of the implementation rather than an experiment are
    `disclosed`.
    """
    v = "validationX"
    off2 = _find_pair(v, "ace_x_offline")
    off3 = _find_pair(v, "ace_x3_offline")
    off4 = _find_pair(v, "ace_x4_offline")
    e3_3 = _find_pair(v, "ace_x3_offline_e3")
    e3_2 = _find_pair(v, "ace_x_offline_e3")
    nr3 = _find_pair(v, "ace_x3_noreflect")
    nr2 = _find_pair(v, "ace_x_noreflect")
    mono3 = _find_pair(v, "ace_x3_mono")
    mono2 = _find_pair(v, "ace_x_mono")
    paired = build_x_paired().get(v, {})
    online_cold = {
        k: p
        for k, p in paired.items()
        if p["kind"] == "online" and "warm" not in k
    }
    online_warm = {
        k: p
        for k, p in paired.items()
        if p["kind"] == "online" and "warm" in k
    }
    test = build_x_paired().get("testX", {})
    rows: list[dict[str, Any]] = []

    def pooled(arms: Mapping[str, Any]) -> str | None:
        if not arms:
            return None
        parts = [
            f"{k.replace('online ', '')}: {_delta(p)}" for k, p in arms.items()
        ]
        return "; ".join(parts)

    a, st = _direction(off3 or off2, True)
    rows.append(
        _paper_row(
            "offline",
            "Offline adaptation, no GT labels (Table 1)",
            "+14.8 avg on AppWorld, +8.0 avg on finance",
            "trainX → validationX (2 seeds), Rocq verdict as the only supervision; v3 playbook rendered at rv3",
            _delta(off3) or (f"v2: {_delta(off2)}" if off2 else None),
            a
            + (f"; v2 generation: {_delta(off2)}" if off2 and off3 else "")
            + (
                f"; testX one look: {_delta(test.get('ace_x3_offline'))}"
                if test.get("ace_x3_offline")
                else ""
            ),
            st,
        )
    )
    text, a, st = _gap(e3_3 or e3_2, off3 or off2, False)
    rows.append(
        _paper_row(
            "multi-epoch",
            "Multi-epoch adaptation (Table 3; paper uses 5 epochs)",
            "+2.6 over single epoch",
            "3 shuffled epochs on trainX; v3 with the 8k guard (v2's 4k guard froze epochs 2–3 into paid no-ops)",
            text,
            a,
            st,
        )
    )
    text, a, st = _gap(nr3 or nr2, off3 or off2, True)
    rows.append(
        _paper_row(
            "no-reflector",
            "Removing the Reflector (Table 3)",
            "−2.6 without it (offline, AppWorld)",
            "Curator fed the raw trajectory instead of a reflection; no bullet tags ever move a counter",
            text,
            a,
            st,
        )
    )
    text, a, st = _gap(mono3 or mono2, off3 or off2, True)
    rows.append(
        _paper_row(
            "monolithic",
            "Incremental deltas vs monolithic rewrite (§A.5)",
            "−13.4 avg for monolithic on AppWorld",
            "Curator rewrites the whole playbook each step (ids reassigned, counters lost)",
            text,
            a,
            st,
        )
    )
    col = _collapse("x3-mono") or _collapse("x-mono")
    rows.append(
        _paper_row(
            "collapse",
            "Context collapse under full rewrites (Fig. 2)",
            "18,282 → 122 tokens in one step",
            "size trajectory of the monolithic arm; a collapse is a ≥3-digit one-step drop",
            col,
            "reproduced"
            if col and re.search(r"change -\d{3,}", col)
            else ("did not reproduce" if col else "not yet measured"),
            "measured" if col else "pending",
        )
    )
    rows.append(
        _paper_row(
            "online",
            "Online / test-time adaptation, cold start (Table 1)",
            "+17.1 avg (their best AppWorld arm)",
            "one chain per seed over validationX in file order; predict, then update (window 1)",
            pooled(online_cold),
            "see the paired rows; the only positive signal of the study so far (v2: +1 on both seeds)"
            if online_cold
            else "not yet measured",
            "measured" if online_cold else "pending",
        )
    )
    rows.append(
        _paper_row(
            "warmup",
            "Online with offline warm-up (Table 3)",
            "+3.4 over cold online",
            "chain starts from the frozen offline playbook (v2 evidence; v3 warm chains cut from scope)",
            pooled(online_warm),
            "v2: warm-up HURT on both seeds (2–6 pooled discordant) — the opposite direction"
            if online_warm
            else "not yet measured",
            "measured" if online_warm else "not-run",
        )
    )
    text, a, st = _gap(off4, off3, False)
    rows.append(
        _paper_row(
            "attribution",
            "Generator-side attribution: Reflector sees only cited bullets (§3.1, their code)",
            "part of every ACE arm in the reference",
            "v4: reflector_scope=cited (driver-side parse of the generator's cited ids); minimal pair against x3-offline",
            text,
            a if off4 else "pre-registered; runs after the v3 evaluations",
            st,
        )
    )
    adapt = build_x_adapt()
    dedup_total = sum(int(a["dedupTotal"]) for a in adapt.values())
    rows.append(
        _paper_row(
            "dedup",
            "Semantic de-duplication threshold (§A.6)",
            "opt-in; 0.90 best on FiNER (78.6)",
            "always-on embedding dedup at 0.88 + deterministic fold",
            f"fired {dedup_total} times across every recorded variant",
            "inert here: playbooks stay far below the size where duplicates accumulate",
            "measured",
        )
    )
    cost = build_x_cost().get("evaluation", {}).get(v, {})
    base_c = cast(dict[str, Any] | None, cost.get("baseline"))
    arm_c = next((d for k, d in cost.items() if k != "baseline"), None)
    rows.append(
        _paper_row(
            "serving",
            "Serving cost: long contexts, high cache reuse (Table 14)",
            "91.8% of evaluation input served from cache",
            "Responses API prompt cache; playbook resent on every turn",
            f"{round(float(arm_c['cachedShare']) * 100)}% cached input on an ACE arm "
            f"(baseline {round(float(base_c['cachedShare']) * 100)}%)"
            if arm_c
            and base_c
            and arm_c.get("cachedShare")
            and base_c.get("cachedShare")
            else None,
            "measured" if arm_c else "not yet measured",
            "measured" if arm_c else "pending",
        )
    )
    rows.append(
        _paper_row(
            "rounds",
            "Reflection repair rounds (§A.6: 1 → 61.3, 5 → 67.6, 10 → 65.2)",
            "reflect → regenerate up to 5×",
            "one reflection per sample; the 32-turn agentic loop with verifier feedback is the domain-native repair loop",
            None,
            "not run: a repair round is another full generator cell per step; disclosed as a deviation",
            "not-run",
        )
    )
    rows.append(
        _paper_row(
            "checkpoint",
            "Best-playbook checkpoint on validation accuracy (offline)",
            "kept the best of the periodic validation checkpoints",
            "the final playbook is frozen; every step's playbook is stored (`playbook_step_NN`) but not selected on",
            None,
            "not done; with 40 steps and their default eval_steps=100 the reference would not checkpoint either",
            "disclosed",
        )
    )
    rows.append(
        _paper_row(
            "batch",
            "Batch size (paper: 1; repo: sqrt(n) curator groups + aggregation)",
            "batch size 1 in every reported run",
            "v3/v4 offline arms use batch 4 + one reducer (the repo's aggregation prompt); the A2 gate compared batch 1 vs 4 on 12 steps",
            "A2 gate: 11/12 vs 11/12 generator solves; batch-4 playbook ~2.5× smaller",
            "disclosed: a treatment property of the v3/v4 offline arms, not a paper setting",
            "disclosed",
        )
    )
    return rows


def build_x_audit() -> list[dict[str, Any]]:
    """The 2026-08-26 audit of our implementation against the reference."""
    adapt = build_x_adapt()
    cited = {
        k: [
            s.get("citedCount")
            for s in cast(list[dict[str, Any]], v["steps"])
            if s.get("citedCount") is not None
        ]
        for k, v in adapt.items()
    }
    v3_cited = [
        c
        for k, cs in cited.items()
        if k.startswith("x3") or k.startswith("x4")
        for c in cs
    ]
    cite_text = (
        f"{sum(1 for c in v3_cited if c)} of {len(v3_cited)} v3/v4 generator cells cited ≥1 bullet"
        if v3_cited
        else "cited counts appear after the zero-spend re-derivation"
    )

    def row(
        key: str,
        divergence: str,
        reference: str,
        ours: str,
        status: str,
        evidence: str,
    ) -> dict[str, Any]:
        return {
            "key": key,
            "divergence": divergence,
            "reference": reference,
            "ours": ours,
            "status": status,
            "evidence": evidence,
        }

    return [
        row(
            "eval-playbook",
            "The first 'v3' evaluations scored the v2 playbook",
            "n/a",
            "`ace_x_eval` consumed `--playbook=` from argv on first read; the second read fell back to the v2 default. 123 of 152 'v3' cells pinned sha 1ac8a092",
            "corrected",
            "sha in every `experiment.yaml`; fresh `_rv3` directories; the old directories are kept as v2 replicates",
        ),
        row(
            "eval-rv",
            "Evaluation rendered every playbook at render_version 2",
            "one prompt in adaptation and evaluation",
            "v3 playbooks adapted under the directive prompt + citation ask were scored under the v2 advisory prompt",
            "corrected",
            "render version now read from the provenance sidecar; directory names carry `_rv{N}`",
        ),
        row(
            "citation",
            "Citation ask without a citation channel",
            "Generator returns `bullet_ids`; Reflector sees only those bullets; counters move only for them",
            "v3 asked for ids and parsed nothing; the Reflector saw the whole playbook",
            "corrected in v4",
            f"`reflector_scope=cited`: ids parsed from the generator's own messages; {cite_text}",
        ),
        row(
            "failed-cells",
            "Platform-failed cells dropped from every pairing",
            "API-error samples are excluded from adaptation, not from evaluation denominators",
            "denominators of 73/74 instead of 80; no 'unsolved — platform memory' scoring existed",
            "corrected",
            "failed cells scored unsolved with `platformFailed`; sensitivity line drops them",
        ),
        row(
            "dedup",
            "Grow-and-refine is inert",
            "opt-in analyzer, off by default",
            "always-on embedding dedup at 0.88 fired 0 times in every variant",
            "open",
            "steps.csv `deduped` sums",
        ),
        row(
            "budget",
            "Hard 4k-token guard vs advisory 80k budget",
            "prose budget, never enforced",
            "deterministic refusal above 4k (8k on the e3 arm); bound only on v2 e3",
            "argued: every playbook token is resent on every turn under a per-problem cap",
            "`dropped` column",
        ),
        row(
            "rounds",
            "One reflection, no repair loop",
            "reflect → regenerate up to 5×",
            "one Reflector call per sample; the agentic loop's verifier turns are the repair loop",
            "argued",
            "prove_ace.py, ace_adaptation.py",
        ),
        row(
            "checkpoint",
            "No best-playbook checkpoint",
            "best validation checkpoint (offline)",
            "final playbook frozen; per-step playbooks stored",
            "open",
            "playbooks/*/playbook_step_NN.yaml",
        ),
        row(
            "counters",
            "Counters hidden from the Generator (v2+)",
            "shown in the finance repo; stripped in the AppWorld fork",
            "ids only in the Generator's prompt (cache stability); counters shown to the Curator",
            "argued",
            "render_prompt vs render_markdown",
        ),
        row(
            "batch",
            "Batch 4 + reducer in v3/v4 offline arms",
            "batch size 1 in the paper",
            "reducer = their aggregation prompt; A2 gate on 12 steps",
            "argued",
            "x3-gate-b1",
        ),
        row(
            "minimal-pairs",
            "v3 was not a minimal pair against v2",
            "n/a",
            "batching and the prompt polish changed together",
            "disclosed; v4 is a minimal pair against v3",
            "VARIANTS table",
        ),
        row(
            "reflector-scope",
            "Reflector shown ids only (v2/v3)",
            "Reflector sees cited bullets with counters",
            "the rendering the Generator saw",
            "argued",
            "_reflector_playbook",
        ),
        # ---- 2026-09-02: v5 (evidence-first curation) and x3-strong ----
        row(
            "digest",
            "Pool-level verifier-failure digest in the curation prompts",
            "the Reflector reflects per sample; nothing aggregates execution feedback across samples",
            "contract-4 Curator, contract-2 Reducer and the Auditor see error classes ranked by problems × verdicts, the unknown names and the failing tactic heads (`ace_evidence.render_digest`), plus the prover's own pitfalls",
            "omphalos addition, disclosed",
            "PROGRESS 2026-09-02 §1 (C1, C4): the most frequent failure classes had no bullet; the reducer preferred distinctive over frequent",
        ),
        row(
            "grounding",
            "Verifier-grounded curation",
            "no check that a bullet's lemma names exist",
            "every ADD lists `references`; `Locate <name>.` through the bridge (cached compute) refuses bullets naming objects Rocq does not know; bridge failures keep the bullet and are counted",
            "omphalos addition, disclosed",
            "`grounding.log.yaml`, steps.csv `ungrounded` / `grounding_error`; v3's `rocq-00007` recommended `Nat.div_mod_eq` and the arm then failed to resolve it",
        ),
        row(
            "skip-trivial",
            "No Reflector/Curator call on a first-proposal solve",
            "reflects on every sample",
            "`skip_trivial`: a ≤1-request solve produces no role call (33/40 x3 steps were solves; step 13's reflection restated `rocq-00001`)",
            "cost-motivated deviation, disclosed",
            "steps.csv `skipped_trivial`",
        ),
        row(
            "audit",
            "One terminal whole-playbook audit pass",
            "no terminal pass; the monolithic rewrite is the ablation (context collapse)",
            "`AuditPlaybook` once after the last step: default keep, per-bullet reasons, counters preserved, ≤6 grounded additions; the pre-audit playbook is frozen alongside (`ace_x5_offline_preaudit.yaml`) so the pass is ablatable",
            "in-spirit deviation, mitigated and disclosed",
            "`audit.log.yaml`; both playbooks' provenance sidecars",
        ),
        row(
            "role-strength",
            "Stronger Reflector/Curator on the same Generator",
            "one model for all roles (Table 16 varies the Reflector model)",
            "`x3-strong`: gpt-5.6-terra Reflector and curation roles (curator, reducer), luna Generator, `role_cap` 0.25 — a minimal pair of x3-offline",
            "measured (2026-09-02)",
            "`tools/test_ace_driver.py::test_x3_strong_is_a_minimal_pair_of_x3`",
        ),
    ]


#####
##### Benchmark partitions and platform performance
#####

_FAMILY_ORDER = (
    "imo",
    "aime",
    "amc",
    "induction",
    "algebra",
    "numbertheory",
    "mathd/algebra",
    "mathd/numbertheory",
)
_COMPETITION = {"imo", "aime", "amc"}


def _family(rel: str) -> str:
    parts = Path(rel).parts  # miniF2F/<split>/<family>[/<sub>]/<file>.v
    fam = parts[2]
    return f"{fam}/{parts[3]}" if fam == "mathd" else fam


def _partition_files(name: str) -> list[str]:
    path = BENCHMARKS / f"{name}.txt"
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def _baseline_solves(
    run: str, seeds: tuple[str, ...]
) -> dict[str, Any] | None:
    d = OUTPUT / run
    if not (d / "experiment.yaml").exists():
        return None
    recs = [r for r in cells_of_run(d) if r.model == LUNA and r.seed in seeds]
    recs = [r for r in recs if r.arm == "core-medium"]
    if not recs:
        return None
    return {
        "cells": len(recs),
        "solved": sum(1 for r in recs if r.solved),
        "spend": round(sum(r.cost for r in recs), 4),
        "problemsSolvedEverySeed": len(
            {r.bench for r in recs if r.solved}
            - {r.bench for r in recs if not r.solved}
        ),
        "problemsNeverSolved": len(
            {r.bench for r in recs if not r.solved}
            - {r.bench for r in recs if r.solved}
        ),
    }


def build_bench() -> dict[str, Any]:
    """
    Composition of the original 20-problem partitions and the 40-problem
    X partitions (family counts, competition share) with the canonical
    luna baseline's solves on each — the motivation for the X partitions.
    """
    parts = (
        ("train", "luna_train_agentic", ("0",)),
        ("validation", "luna_validation_agentic", ("0", "1")),
        ("test", "luna_test_agentic", ("0",)),
        ("trainX", "x_train_agentic", ("0", "1")),
        ("validationX", "x_validation_agentic", ("0", "1")),
        ("testX", "x_test_agentic", ("0",)),
    )
    out: dict[str, Any] = {"families": list(_FAMILY_ORDER), "partitions": {}}
    for name, run, seeds in parts:
        files = _partition_files(name)
        fams = [_family(f) for f in files]
        counts = {f: fams.count(f) for f in _FAMILY_ORDER}
        comp = sum(1 for f in fams if f in _COMPETITION)
        out["partitions"][name] = {
            "n": len(files),
            "generation": "X" if name.endswith("X") else "original",
            "families": counts,
            "competition": comp,
            "competitionShare": round(comp / len(files), 3),
            "baseline": _baseline_solves(run, seeds),
        }
    return out


PERF: dict[str, Any] = {
    "measuredOn": "2026-08-26",
    "source": "PROGRESS.md 2026-08-26 (platform rebuild); tools/bench_rocq.py; tools/bridge_parity.py",
    "rows": [
        {
            "what": "Rocq session per tool call",
            "before": "fresh `pet` process + document rebuild: 450–850 ms",
            "after": "private warm server, stable document: 2–3 ms (bench: 548 → 19 ms median per call, 10× on a 40-call cell)",
        },
        {
            "what": "Socket mode of 2026-08-25",
            "before": "random temp URI per call: 200–300 ms and +40–50 MB server RSS per call, never freed (the 'memory balloon')",
            "after": "content-addressed augmented file per problem; server recycled per cell / on RSS budget",
        },
        {
            "what": "Hangs and balloons",
            "before": "no transport timeout; 13 h and 36 min hangs; kernel OOM kills breaking the pool",
            "after": "deadline on every RPC, 16 MiB reply cap, RLIMIT_AS on the server, memory floor; a runaway tactic fails as a recorded error",
        },
        {
            "what": "Worker memory",
            "before": "believed to be the Delphyne tree cache (4 GB)",
            "after": "measured: 172 MB peak on the heaviest cell — the balloons were unbounded Rocq replies",
        },
        {
            "what": "Concurrency",
            "before": "single worker per launch, shell watchdog, pkill rituals",
            "after": "4 machine-wide Rocq streams (memory-bound on 7.4 GB), FIFO slot queue, LLM-only phases off the slots; several launches at once",
        },
        {
            "what": "Reliability",
            "before": "statuses lost on a broken pool, orphans racing relaunches, corrupted state files",
            "after": "supervised attempts: group kill, statuses rebuilt from result files, bounded retries; chaos-tested (SIGKILL a worker mid-run)",
        },
        {
            "what": "Bridge correctness",
            "before": "—",
            "after": "byte-identical to the archive on 117/120 archived calls (the rest: crashed-process messages now explicit)",
        },
        {
            "what": "Cell wall-clock",
            "before": "median 159 s; 8 of 80 cells held 57 % of the time (goal floods)",
            "after": "same median (LLM-bound); the tail is bounded, not removed — the goal cap is a pre-registered treatment, not run",
        },
    ],
}


def build_meta() -> dict[str, Any]:
    return {
        "generated": str(date.today()),
        "pricingDate": str(current_pricing_date()),
        "partitions": {
            p: len(_partition(p)) for p in ("trainX", "validationX", "testX")
        },
    }


#####
##### Writing
#####


def rewrite(report: Path, blocks: Mapping[str, Any]) -> bool:
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


def build_all() -> dict[str, Any]:
    return {
        "META": build_meta(),
        "EVOLUTION": build_evolution(),
        "X_ARMS": build_x_arms(),
        "X_PAIRED": build_x_paired(),
        "X_CAPS": build_x_caps(),
        "X_ADAPT": build_x_adapt(),
        "X_TAXONOMY": build_x_taxonomy(),
        "X_COST": build_x_cost(),
        "X_PAPER": build_x_paper(),
        "X_AUDIT": build_x_audit(),
        "BENCH": build_bench(),
        "PERF": PERF,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the ACE X report data. Offline."
    )
    parser.add_argument(
        "--check", action="store_true", help="exit 1 if the page is stale"
    )
    args = parser.parse_args()
    blocks = build_all()
    SIDECAR.write_text(json.dumps(blocks, indent=1, sort_keys=True) + "\n")
    print(f"wrote {SIDECAR.relative_to(_OMPHALOS_DIR)}")
    if not REPORT.exists():
        print(
            f"{REPORT.relative_to(_OMPHALOS_DIR)} does not exist yet; JSON only"
        )
        return 0
    if args.check:
        text = REPORT.read_text()
        stale = False
        for name, value in blocks.items():
            payload = json.dumps(value, separators=(",", ":"))
            if f"const {name} = {payload};" not in text:
                stale = True
                print(f"stale: {name}")
        return 1 if stale else 0
    changed = rewrite(REPORT, blocks)
    print(
        "updated" if changed else "no change to",
        REPORT.relative_to(_OMPHALOS_DIR),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
