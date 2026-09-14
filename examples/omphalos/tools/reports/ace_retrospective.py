"""Build the ACE retrospective offline, from explicitly allowed sources.

Run from examples/omphalos with either harness:
    python -m tools.reports.ace_retrospective

No experiment runners, benchmark loaders, HTTP clients, or Rocq are used.
The source report and frozen measurements are never rewritten. Workbook
support is isolated under the report's .build/deps directory.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from collections.abc import Sequence
import csv
from datetime import date
import hashlib
import importlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from runtime.development_only import install

install()

from runtime.model_registry import price_tokens  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "report/ace_retrospective"
SNAPSHOT_DATE = date(2026, 9, 12)
Row = dict[str, Any]
SOURCES: dict[str, Row] = {}
CHECKS: list[Row] = []

CAMPAIGNS = (
    "ace_bounded_20260908",
    "ace_control_cycle_20260909",
    "ace_polish_20260909",
    "ace_applicability_20260909",
    "change_control_20260910",
    "terra_high_20260910",
    "luna_high_20260910",
    "luna_upper_20260910",
    "ace_models_20260910",
    "ace_contenders_20260910",
    "ace_mechanisms_20260910",
    "coverage_cycle_20260911",
    "ace_attribution_20260912",
    "ace_capacity_20260912",
)

# Exact directory names, not a recursive search of mixed historical runs.
ARCHIVES = (
    "ace_validation_agentic",
    "luna_validation_agentic",
    "x_train_agentic",
    "x_validation_agentic",
    "ace_x_validation_agentic",
    "ace_x_validation_ace_x3_noreflect_agentic",
    "ace_x_validation_ace_x3_offline_agentic",
    "ace_x_validation_ace_x3_offline_rv3_agentic",
    "ace_x_validation_ace_x3_noreflect_rv3_agentic",
    "ace_x_validation_ace_x3_mono_rv3_agentic",
    "ace_x_validation_ace_x3_offline_e3_rv3_agentic",
    "ace_x_validation_ace_x4_offline_rv3_agentic",
    "ace_x_validation_ace_x3_strong_rv3_agentic",
    "ace_x_validation_ace_x5_offline_rv3_agentic",
    "ace_x_validation_ace_x5_offline_rv2_agentic",
    "ace_x_validation_ace_x3_offline_rv2_agentic",
    "ace_x_validation_ace_digest_table_rv2_agentic",
    "acet_x_validation_ace_x5_offline_k3_agentic",
    "acet_x_validation_ace_x6_repairs_k3_r2_agentic",
    "x_validation_stall_seenstate4_agentic",
    "ace_online_x-online-s0_agentic",
    "ace_online_x-online-s1_agentic",
    "ace_online_x-online-warm-s0_agentic",
    "ace_online_x-online-warm-s1_agentic",
    "ace_online_x3-online-s0_agentic",
    "ace_online_x3-online-s1_agentic",
    "ace_online_x4-online-s0_agentic",
    "ace_review_development",
)


def allowed(path: str) -> Path:
    """Reject closed, mixed, and unregistered numerical sources before open."""
    p = (ROOT / path).resolve()
    rel = p.relative_to(ROOT).as_posix()
    lower = rel.lower()
    if "testx" in lower or "ace_challenge" in lower:
        raise PermissionError(f"Closed source: {rel}")
    if rel.startswith("experiments/campaigns/"):
        parts = rel.split("/")
        if parts[2] not in CAMPAIGNS and rel not in {
            "experiments/campaigns/coverage_20260911/training_report.json",
            "experiments/campaigns/coverage_20260911/validation_report.json",
        }:
            raise PermissionError(f"Unregistered campaign source: {rel}")
    elif rel.startswith("experiments/output/"):
        if rel.split("/")[2] not in ARCHIVES:
            raise PermissionError(f"Unregistered archive: {rel}")
    elif rel not in {
        "benchmarks/trainX.txt",
        "benchmarks/validationX.txt",
    }:
        raise PermissionError(f"Unregistered numerical input: {rel}")
    return p


def record_source(path: Path, role: str) -> bytes:
    content = path.read_bytes()
    rel = path.relative_to(ROOT).as_posix()
    SOURCES[rel] = dict(
        path=rel,
        status="used",
        role=role,
        bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
    )
    return content


def read_json(path: str) -> Any:
    return json.loads(record_source(allowed(path), "numerical evidence"))


def campaign(name: str, file: str = "final_report.json") -> Any:
    return read_json(f"experiments/campaigns/{name}/{file}")


def write_json(name: str, data: Any) -> None:
    (OUT / name).write_text(
        json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    )


def write_csv(name: str, rows: Sequence[Row]) -> None:
    if not rows:
        return
    columns = list(dict.fromkeys(k for row in rows for k in row))
    with (OUT / "data" / f"{name}.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=columns, lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    k: json.dumps(v) if isinstance(v, (dict, list)) else v
                    for k, v in row.items()
                }
            )


def check_close(label: str, actual: float, expected: float) -> None:
    if not math.isclose(actual, expected, abs_tol=1e-7, rel_tol=1e-7):
        raise ValueError(f"{label}: {actual} != {expected}")
    CHECKS.append(dict(check=label, actual=actual, expected=expected))


def header(path: Path) -> str:
    # Arguments can contain earlier outcomes and exceed 128 KiB. Locate the
    # actual command outcome before interpreting any success/spending field.
    with path.open() as stream:
        for line in stream:
            if line.rstrip() == "outcome:":
                return line + stream.read(65536)
    raise ValueError(f"No command outcome in {path}")


def field(text: str, key: str) -> str:
    match = re.search(rf"^\s*{re.escape(key)}:\s*(.*?)\s*$", text, re.M)
    if match is None:
        raise ValueError(f"Missing outcome field: {key}")
    return match[1]


def archive_rows() -> list[Row]:
    yaml: Any = importlib.import_module("yaml")
    dev_names: set[str] = set()
    for name in ("trainX", "validationX"):
        content = record_source(
            allowed(f"benchmarks/{name}.txt"), "development partition order"
        ).decode()
        dev_names.update(
            Path(line.strip()).stem
            for line in content.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    rows: list[Row] = []
    for run in ARCHIVES:
        meta = allowed(f"experiments/output/{run}/experiment.yaml")
        if not meta.exists():
            continue
        state: Any = yaml.safe_load(record_source(meta, "archive manifest"))
        for name, item in state["configs"].items():
            params = item["params"]
            model = params.get("model_name", "")
            if model != "gpt-5.6-luna":
                continue
            if run == "luna_validation_agentic" and (
                params.get("toolset") != "core"
                or params.get("reasoning_effort") != "medium"
            ):
                continue
            theorem = params.get("bench_name", "")
            if (
                run
                not in {"ace_validation_agentic", "luna_validation_agentic"}
                and theorem not in dev_names
            ):
                raise PermissionError(f"Nondevelopment cell in {run}")
            source = f"experiments/output/{run}/configs/{name}/result.yaml"
            result = allowed(source)
            status = item.get("status", "todo")
            base: Row = dict(
                archive=run,
                arm=name.split("__")[1],
                playbook=params.get("playbook_file", ""),
                rendering=params.get("render_version", 1),
                injection=params.get("injection", "full"),
                theorem=theorem,
                seed=int(params.get("seed", 0)),
                model=model,
                cap=float(params.get("max_dollar_budget", 0.1)),
                requests_allowed=params.get("num_requests", ""),
                source=source,
                status=status,
            )
            if not result.exists():
                base.update(
                    raw_solved=False,
                    qualified_solved=False,
                    cost_usd=None,
                    cost_basis="unavailable; no verdict",
                )
                rows.append(base)
                continue
            record_source(result, "archived command outcome")
            text = header(result)
            spent = text[text.index("spent_budget:") :]
            values = {
                k: int(float(field(spent, k)))
                for k in (
                    "input_tokens",
                    "cached_input_tokens",
                    "output_tokens",
                    "num_completions",
                )
            }
            cost = price_tokens(
                model,
                values["input_tokens"],
                values["cached_input_tokens"],
                values["output_tokens"],
                on=SNAPSHOT_DATE,
            )
            raw = field(text, "success") == "true"
            base.update(
                status="done",
                raw_solved=raw,
                qualified_solved=raw and cost <= base["cap"] + 1e-10,
                cost_usd=cost,
                cost_basis="2026-09-12 token repricing",
                **values,
            )
            rows.append(base)
    return rows


def summarize_archives(rows: list[Row]) -> list[Row]:
    groups: dict[tuple[str, str, str], list[Row]] = defaultdict(list)
    for r in rows:
        # Online book hashes change by step; the entire chain is one arm.
        arm = "evolving book" if "ace_online_" in r["archive"] else r["arm"]
        key = (r["archive"], arm, str(r["seed"]))
        groups[key].append(r)
    result: list[Row] = []
    for (run, arm, seed), cells in sorted(groups.items()):
        complete = all(r["status"] == "done" for r in cells)
        costs = [r["cost_usd"] for r in cells if r["cost_usd"] is not None]
        result.append(
            dict(
                archive=run,
                arm=arm,
                seed=int(seed),
                cells=len(cells),
                complete=complete,
                raw_solves=sum(r["raw_solved"] for r in cells),
                qualified_solves=sum(r["qualified_solved"] for r in cells),
                cost_usd=sum(costs) if complete else None,
                observed_cost_lower_bound=sum(costs),
                cap=cells[0]["cap"],
                cost_basis="2026-09-12 repricing; separate from campaign bills",
                playbook=cells[0]["playbook"]
                if "online_" not in run
                else "evolving",
                rendering=cells[0]["rendering"],
            )
        )
    return result


def extract_tables() -> dict[str, list[Row]]:
    tables: dict[str, list[Row]] = {}
    cross = campaign("ace_capacity_20260912", "crossover_report.json")
    tables["crossover_cells"] = cross["rows"]
    tables["crossover"] = [
        dict(arm=k, **v) for k, v in cross["groups"].items()
    ]
    for arm, expected in cross["groups"].items():
        model, book = arm.split("/")
        rows = [
            r
            for r in cross["rows"]
            if r["model"] == model and r["book"] == book
        ]
        if len({r["theorem"] for r in rows}) != 40:
            raise ValueError(f"Incomplete crossover group: {arm}")
        check_close(arm + " count", len(rows), expected["cells"])
        check_close(
            arm + " cost", sum(r["cost"] for r in rows), expected["cost"]
        )
        check_close(
            arm + " solves",
            sum(
                r["solved"]
                and not r["failed"]
                and r["cost"] <= expected["cap"] + 1e-10
                for r in rows
            ),
            expected["qualified_solves"],
        )
        for r in rows:
            priced = price_tokens(
                model,
                int(r["input_tokens"]),
                int(r["cached_input_tokens"]),
                int(r["output_tokens"]),
                on=SNAPSHOT_DATE,
            )
            check_close(r["source"] + " repricing", priced, r["cost"])
    main = campaign("ace_attribution_20260912", "complete_report.json")
    tables["attribution"] = []
    tables["attribution_cells"] = []
    for stage, data in main["partitions"].items():
        for arm, metrics in data["metrics"].items():
            tables["attribution"].append(dict(stage=stage, arm=arm, **metrics))
            observed = data["observations"][arm]
            check_close(
                stage + arm + " total",
                sum(r["cost"] for r in observed.values()),
                metrics["cost"],
            )
            for theorem, row in observed.items():
                tables["attribution_cells"].append(
                    dict(stage=stage, arm=arm, theorem=theorem, seed=0, **row)
                )
    mechanism = campaign("ace_capacity_20260912", "mechanism_report_v2.json")
    tables["continuations"] = []
    tables["diagnostic_cells"] = []
    for level, data in mechanism.items():
        for arm, values in data["groups"].items():
            tables["continuations"].append(
                dict(level=int(level), arm=arm, **values)
            )
        tables["diagnostic_cells"].extend(
            dict(
                level=int(level),
                **{k: v for k, v in r.items() if k != "level"},
            )
            for r in data["rows"]
        )
    evolution = campaign("ace_attribution_20260912", "training_evolution.json")
    tables["book_evolution"] = [
        dict(model=model, batch=i + 1, **row)
        for model, data in evolution.items()
        for i, row in enumerate(data["batches"])
    ]
    tables["preparation"] = []
    for model, filename in (
        ("luna", "luna_preparation_accounting.json"),
        ("terra", "training_accounting.json"),
    ):
        data = campaign("ace_attribution_20260912", filename)
        for role, values in data.get("roles", data).items():
            tables["preparation"].append(
                dict(
                    model=model,
                    role=role,
                    cost=values["cost"],
                    requests=values["requests"],
                    embedding_status="unavailable"
                    if model == "luna"
                    else "included",
                )
            )
    tables["campaign_receipts"] = []
    seen_receipts: set[str] = set()
    for name in CAMPAIGNS:
        files = sorted(
            (ROOT / "experiments/campaigns" / name).glob("receipts*.csv")
        )
        if not files:
            continue
        unique_cost, duplicates, unsettled, count = 0.0, 0, 0, 0
        for path in files:
            content = record_source(
                allowed(path.relative_to(ROOT).as_posix()),
                "settled request receipt export",
            ).decode()
            for r in csv.DictReader(content.splitlines()):
                if r["id"] in seen_receipts:
                    duplicates += 1
                    continue
                seen_receipts.add(r["id"])
                count += 1
                unsettled += r["status"] != "settled"
                if r["charged"]:
                    unique_cost += float(r["charged"])
        tables["campaign_receipts"].append(
            dict(
                campaign=name,
                unique_receipts=count,
                duplicate_receipts_excluded=duplicates,
                charged_usd=unique_cost,
                unsettled_receipts=unsettled,
                basis="receipt exports; excludes assistant and engineering costs",
            )
        )
    tables["development_comparisons"] = []
    for camp in (
        "ace_contenders_20260910",
        "ace_mechanisms_20260910",
        "coverage_20260911",
        "coverage_cycle_20260911",
    ):
        for stage in ("training", "validation"):
            data = (
                campaign(camp, "final_report.json")[stage]
                if camp == "ace_contenders_20260910"
                else campaign(camp, f"{stage}_report.json")
            )
            for arm, values in data["metrics"].items():
                tables["development_comparisons"].append(
                    dict(campaign=camp, stage=stage, arm=arm, **values)
                )
    tables["budget_history"] = []
    for camp, label in (
        ("ace_bounded_20260908", "Bounded"),
        ("ace_polish_20260909", "Polish"),
        ("ace_control_cycle_20260909", "Control cycle"),
    ):
        data = campaign(camp)
        compare = (
            data["candidate"] if camp == "ace_control_cycle_20260909" else data
        )
        for side, arm in (("a", "Reference"), ("b", label)):
            tables["budget_history"].append(
                dict(
                    campaign=camp,
                    arm=arm,
                    cells=compare["cells"],
                    solves=compare[f"solved_{side}"],
                    cost=compare[f"cost_{side}"],
                    source=f"experiments/campaigns/{camp}/final_report.json",
                )
            )
    tables["local_applicability"] = [
        dict(arm=k, **v)
        for k, v in campaign("ace_applicability_20260909")["arms"].items()
    ]
    tables["creator_quality"] = []
    creator = campaign("ace_capacity_20260912", "creator_quality.json")
    write_json("data/creator_quality.json", creator)
    for name in (
        "pricing_sensitivity.json",
        "prefix_cost_conservation.json",
        "final_accounting.json",
        "creator_terminal_evidence.json",
        "causal_exposure_audit.json",
    ):
        value = campaign("ace_capacity_20260912", name)
        write_json("data/" + name, value)
    tables["archive_cells"] = archive_rows()
    tables["archive_summary"] = summarize_archives(tables["archive_cells"])
    return tables


def cumulative(
    rows: Sequence[Row], order: Sequence[str], cap: float
) -> list[Row]:
    by_theorem = {r["theorem"]: r for r in rows}
    if len(by_theorem) != len(rows) or set(by_theorem) != set(order):
        raise ValueError("Cumulative curves require a complete unique panel")
    cost, solves = 0.0, 0
    points: list[Row] = [dict(index=0, theorem="", spend=0.0, solves=0)]
    for index, theorem in enumerate(order, 1):
        r = by_theorem[theorem]
        cost += r["cost"]
        solves += int(
            r["solved"] and not r["failed"] and r["cost"] <= cap + 1e-10
        )
        points.append(
            dict(index=index, theorem=theorem, spend=cost, solves=solves)
        )
    return points


def qualification(
    rows: Sequence[Row], thresholds: Sequence[float]
) -> list[Row]:
    return [
        dict(
            threshold=t,
            solves=sum(
                r["solved"] and not r["failed"] and r["cost"] <= t + 1e-10
                for r in rows
            ),
        )
        for t in thresholds
    ]


def plots(tables: dict[str, list[Row]]) -> None:
    mpl: Any = importlib.import_module("matplotlib")
    mpl.use("Agg")
    plt: Any = importlib.import_module("matplotlib.pyplot")
    np: Any = importlib.import_module("numpy")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "normal",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
        }
    )
    colors = ("#17648e", "#bd5b29", "#4f7c52", "#815d9b", "#555555")

    def save(fig: Any, name: str) -> None:
        for ext in ("pdf", "png"):
            fig.savefig(
                OUT / "figures" / f"{name}.{ext}", dpi=190, bbox_inches="tight"
            )
        plt.close(fig)

    def grid(ax: Any) -> None:
        ax.grid(axis="y", color="#dddddd", linewidth=0.6)
        ax.set_axisbelow(True)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set(xlim=(0, 10), ylim=(0, 4))
    ax.axis("off")
    boxes = [
        (0.1, 2.1, "Generator", "Attempt a proof\nusing the current book"),
        (
            3.5,
            2.1,
            "Reflector",
            "Explain the recorded\ntrajectory and feedback",
        ),
        (6.9, 2.1, "Curator / reducer", "Propose a few\nreusable additions"),
        (
            0.1,
            0.1,
            "Rocq verifier",
            "Accept proof, or return\nchecked state and errors",
        ),
        (
            6.9,
            0.1,
            "Deterministic update",
            "Merge, refine, hash\nand store the playbook",
        ),
    ]
    for x, y, title, body in boxes:
        ax.add_patch(
            plt.Rectangle((x, y), 2.9, 1.3, fill=False, edgecolor="#555555")
        )
        ax.text(x + 1.45, y + 0.95, title, ha="center", weight="bold")
        ax.text(
            x + 1.45, y + 0.43, body, ha="center", va="center", fontsize=10
        )
    for a, b in [
        ((3, 2.75), (3.5, 2.75)),
        ((6.4, 2.75), (6.9, 2.75)),
        ((8.35, 2.1), (8.35, 1.4)),
        ((1.55, 2.1), (1.55, 1.4)),
        ((3, 0.75), (4.8, 2.1)),
        ((6.9, 0.75), (3, 2.4)),
    ]:
        ax.annotate(
            "",
            xy=b,
            xytext=a,
            arrowprops=dict(arrowstyle="->", color="#555555"),
        )
    ax.text(4.9, 0.1, "Book used on later tasks", ha="center", fontsize=9)
    save(fig, "pipeline")

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5), layout="constrained")
    for ax, camp, title in zip(
        axes,
        (
            "ace_bounded_20260908",
            "ace_control_cycle_20260909",
            "ace_polish_20260909",
        ),
        (
            "Bounded · 40 cells",
            "Control cycle · 40 cells",
            "Polish · 80 cells",
        ),
        strict=True,
    ):
        rows = [r for r in tables["budget_history"] if r["campaign"] == camp]
        for i, r in enumerate(rows):
            ax.scatter(r["cost"], r["solves"], color=colors[i], s=65)
            ax.annotate(
                f"{r['arm']}\n{r['solves']} solves / ${r['cost']:.3f}",
                (r["cost"], r["solves"]),
                xytext=(0, 13 if i == 0 else -28),
                textcoords="offset points",
                ha="center",
                fontsize=8,
            )
        ax.set(
            title=title,
            xlabel="All-cell inference cost ($)",
            ylabel="Qualified solved cells",
        )
        ax.set_ylim(
            min(r["solves"] for r in rows) - 3,
            max(r["solves"] for r in rows) + 3,
        )
        ax.margins(x=0.45)
        grid(ax)
    save(fig, "budget_tradeoffs")

    order = [
        Path(line.strip()).stem
        for line in allowed("benchmarks/validationX.txt")
        .read_text()
        .splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    tables["cumulative_curves"] = []
    tables["threshold_curves"] = []
    for mi, model in enumerate(("gpt-5.6-luna", "gpt-5.6-terra")):
        for bi, book in enumerate(("none", "luna", "terra")):
            rows = [
                r
                for r in tables["crossover_cells"]
                if r["model"] == model and r["book"] == book
            ]
            cap = 0.1 if mi == 0 else 1.0
            points = cumulative(rows, order, cap)
            label = {
                "none": "No book",
                "luna": "Luna book",
                "terra": "Terra book",
            }[book]
            axes[mi].step(
                [r["spend"] for r in points],
                [r["solves"] for r in points],
                where="post",
                label=label,
                color=colors[bi],
            )
            tables["cumulative_curves"].extend(
                dict(model=model, book=book, **r) for r in points
            )
            qs = qualification(
                rows,
                sorted(
                    set(
                        [0.0, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0]
                        + [r["cost"] for r in rows]
                    )
                ),
            )
            tables["threshold_curves"].extend(
                dict(model=model, book=book, **r) for r in qs
            )
        axes[mi].set(
            title=("Luna" if mi == 0 else "Terra") + " · validation, seed 0",
            xlabel="Cumulative recorded inference spending ($)",
            ylabel="Cumulative qualified solves",
            ylim=(0, 41),
        )
        axes[mi].legend(fontsize=8)
        grid(axes[mi])
    save(fig, "cumulative_spend")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for ax, normalized in zip(axes, (False, True), strict=True):
        for mi, model in enumerate(("gpt-5.6-luna", "gpt-5.6-terra")):
            for bi, book in enumerate(
                ("none", "luna" if mi == 0 else "terra")
            ):
                rows = [
                    dict(
                        r,
                        cost=r["cost"] / (10 if normalized and mi == 1 else 1),
                    )
                    for r in tables["crossover_cells"]
                    if r["model"] == model and r["book"] == book
                ]
                thresholds = sorted(
                    set([0.0, 0.1] + [r["cost"] for r in rows])
                )
                points = qualification(rows, thresholds)
                label = ("Luna" if mi == 0 else "Terra") + (
                    " / no book" if bi == 0 else " / own book"
                )
                ax.step(
                    [r["threshold"] for r in points],
                    [r["solves"] for r in points],
                    where="post",
                    color=colors[mi],
                    linestyle="--" if bi == 0 else "-",
                    label=label,
                )
        ax.set(
            xlim=(0, 0.1),
            ylim=(0, 33),
            xlabel="Maximum final cost of a qualifying solve ($)",
            ylabel="Qualifying solves out of 40",
            title="Luna-rate repricing"
            if normalized
            else "Recorded prices · common $0.10 window",
        )
        ax.legend(fontsize=8, loc="lower right")
        grid(ax)
    save(fig, "cost_thresholds")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    rows = tables["crossover"]
    for i, r in enumerate(rows):
        model, book = r["arm"].split("/")
        name = model.rsplit("-", 1)[-1].capitalize() + " / " + book
        axes[0].scatter(
            r["cost"],
            r["qualified_solves"],
            color=colors[0 if "luna" in model else 1],
            marker=("o", "s", "^")[("none", "luna", "terra").index(book)],
            s=65,
        )
        axes[0].annotate(
            name,
            (r["cost"], r["qualified_solves"]),
            xytext=(5, 8 if i % 2 else -13),
            textcoords="offset points",
            fontsize=8,
        )
        axes[1].bar(
            i - 0.18,
            r["cost"],
            0.35,
            color=colors[0],
            label="Recorded prices" if i == 0 else None,
        )
        axes[1].bar(
            i + 0.18,
            r["uncached_cost"],
            0.35,
            color="#999999",
            label="Uncached sensitivity" if i == 0 else None,
        )
    axes[0].set(
        xscale="log",
        xlabel="All-cell inference cost ($, log scale)",
        ylabel="Qualified solves / 40",
        ylim=(22, 32),
        title="Solver × book crossover",
    )
    axes[0].margins(x=0.45)
    axes[1].set(
        xticks=range(6),
        xticklabels=[
            r["arm"].replace("gpt-5.6-", "").replace("/", "\n") for r in rows
        ],
        yscale="log",
        ylabel="All-cell cost ($, log scale)",
        title="Dependence on cached-input billing",
    )
    axes[1].legend(fontsize=8)
    for ax in axes:
        grid(ax)
    save(fig, "crossover_and_cache")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for mi, model in enumerate(("gpt-5.6-luna", "gpt-5.6-terra")):
        for profile, style in (("C", "--"), ("E", "-")):
            rows = sorted(
                [
                    r
                    for r in tables["continuations"]
                    if r["arm"] == f"{model}/{profile}"
                ],
                key=lambda r: r["level"],
            )
            label = model.rsplit("-", 1)[-1].capitalize() + (
                " / no book" if profile == "C" else " / corrected book"
            )
            for ax, x in (
                (axes[0], [r["level"] for r in rows]),
                (axes[1], [r["cost"] for r in rows]),
            ):
                ax.plot(
                    x,
                    [r["qualified_solves"] for r in rows],
                    marker="o",
                    color=colors[mi],
                    linestyle=style,
                    label=label,
                )
    axes[0].set(
        xticks=[0, 1, 2],
        xticklabels=["Initial", "Money ×2", "+ requests /\nverifier ×2"],
        ylabel="Qualified solves out of 8",
        title="Exact continuation of selected training paths",
        ylim=(0, 8.4),
    )
    axes[1].set(
        xlabel="Full path cost, including prefix once ($)",
        ylabel="Qualified solves out of 8",
        title="Additional spending and recovered proofs",
        ylim=(0, 8.4),
    )
    axes[0].legend(fontsize=8, loc="lower left")
    for ax in axes:
        grid(ax)
    save(fig, "continuations")

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout="constrained")
    for mi, model in enumerate(("luna", "terra")):
        rows = [r for r in tables["book_evolution"] if r["model"] == model]
        axes[0].plot(
            [4 * r["batch"] for r in rows],
            [r["tokens"] for r in rows],
            marker="o",
            color=colors[mi],
            label=model.capitalize(),
        )
        axes[1].plot(
            [4 * r["batch"] for r in rows],
            np.cumsum([r["solves"] for r in rows]),
            marker="o",
            color=colors[mi],
            label=model.capitalize(),
        )
    axes[0].axhline(
        4000, color="#888888", linestyle="--", label="4,000-token guard"
    )
    axes[0].set(
        xlabel="Training problems processed",
        ylabel="Estimated playbook tokens",
        title="Book growth after each four-problem batch",
    )
    axes[1].set(
        xlabel="Training problems processed",
        ylabel="Cumulative generator solves",
        title="Evolving-book adaptation; different controller",
    )
    for ax in axes:
        ax.legend(fontsize=8)
        grid(ax)
    save(fig, "book_evolution")

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout="constrained")
    for ai, arm in enumerate(("D2", "E2", "S", "H")):
        rows = [
            r
            for r in tables["development_comparisons"]
            if r["campaign"] == "coverage_cycle_20260911" and r["arm"] == arm
        ]
        rows.sort(key=lambda r: r["stage"])
        axes[0].plot(
            [0, 1],
            [
                r["solves"] - (28 if r["stage"] == "training" else 27)
                for r in rows
            ],
            marker="o",
            color=colors[ai],
            label=arm,
        )
        axes[1].plot(
            [0, 1],
            [
                100
                * (
                    r["cost"]
                    / (0.68922336 if r["stage"] == "training" else 0.66722836)
                    - 1
                )
                for r in rows
            ],
            marker="o",
            color=colors[ai],
            label=arm,
        )
    for ax in axes:
        ax.set(xticks=[0, 1], xticklabels=["Training", "Validation"])
        ax.axhline(0, color="#888888", linewidth=0.8)
        ax.legend(fontsize=8)
        grid(ax)
    axes[0].set(
        title="Four isolated development treatments",
        ylabel="Solve difference versus stage reference",
    )
    axes[1].set(
        title="Cost changes include unsuccessful cells",
        ylabel="Total cost change versus reference (%)",
    )
    save(fig, "coverage_transfer")

    tables["amortization"] = []
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout="constrained")
    for mi, model in enumerate(("luna", "terra")):
        groups = {
            r["arm"].split("/")[1]: r
            for r in tables["crossover"]
            if r["arm"].startswith(f"gpt-5.6-{model}/")
        }
        prep = sum(
            r["cost"] for r in tables["preparation"] if r["model"] == model
        )
        for n in [10, 40, 100, 200, 500, 1000, 2000]:
            tables["amortization"].append(
                dict(
                    model=model,
                    problems=n,
                    preparation_cost=prep,
                    own_book_inference_per_problem=groups[model]["cost"] / 40,
                    no_book_inference_per_problem=groups["none"]["cost"] / 40,
                    amortized_per_problem=prep / n
                    + groups[model]["cost"] / 40,
                    qualification="Scenario; Luna preparation excludes unavailable historical embeddings",
                )
            )
        data = [r for r in tables["amortization"] if r["model"] == model]
        axes[mi].plot(
            [r["problems"] for r in data],
            [r["amortized_per_problem"] for r in data],
            marker="o",
            color=colors[mi],
            label="Own book + preparation / N",
        )
        axes[mi].axhline(
            groups["none"]["cost"] / 40,
            color="#555555",
            linestyle="--",
            label="No book, observed inference / problem",
        )
        axes[mi].set(
            xscale="log",
            xlabel="Assumed future workload N (log scale)",
            ylabel="Dollars per attempted problem",
            title=model.capitalize() + " · constant-workload scenario",
        )
        axes[mi].legend(fontsize=8)
        grid(axes[mi])
    save(fig, "amortization")

    selected = {
        "x_validation_agentic": "No ACE",
        "ace_x_validation_ace_x3_offline_rv3_agentic": "X3",
        "ace_x_validation_ace_x3_noreflect_rv3_agentic": "No reflector",
        "ace_x_validation_ace_x3_offline_e3_rv3_agentic": "Three epochs",
        "ace_x_validation_ace_x3_mono_rv3_agentic": "Monolithic",
        "ace_x_validation_ace_x4_offline_rv3_agentic": "Cited-only",
        "ace_x_validation_ace_x3_strong_rv3_agentic": "Stronger writers",
        "ace_x_validation_ace_x5_offline_rv3_agentic": "V5",
        "ace_x_validation_ace_x5_offline_rv2_agentic": "V5, rendering 2",
        "ace_x_validation_ace_x3_offline_rv2_agentic": "X3, rendering 2",
        "ace_x_validation_ace_digest_table_rv2_agentic": "Digest table",
        "acet_x_validation_ace_x5_offline_k3_agentic": "Hint on error",
        "acet_x_validation_ace_x6_repairs_k3_r2_agentic": "Repair bullets",
    }
    fig, axes = plt.subplots(1, 2, figsize=(10, 6), layout="constrained")
    vals: list[Row] = []
    for run, label in selected.items():
        rs = [r for r in tables["archive_summary"] if r["archive"] == run]
        if len(rs) != 2 or not all(r["complete"] for r in rs):
            raise ValueError(f"Incomplete selected archive: {run}")
        vals.append(
            dict(
                label=label,
                raw=sum(r["raw_solves"] for r in rs),
                qualified=sum(r["qualified_solves"] for r in rs),
                cost=sum(r["cost_usd"] for r in rs),
            )
        )
    for ax, key, xlabel in (
        (axes[0], "raw", "Raw solved cells / 80 (40 theorems × 2 seeds)"),
        (axes[1], "cost", "Whole-panel cost at 2026-09-12 rates ($)"),
    ):
        ax.barh(
            range(len(vals)),
            [r[key] for r in vals],
            color=["#555555"] + [colors[0]] * (len(vals) - 1),
        )
        ax.set(
            yticks=range(len(vals)),
            yticklabels=[r["label"] for r in vals],
            xlabel=xlabel,
        )
        ax.invert_yaxis()
        for i, r in enumerate(vals):
            ax.text(
                r[key] + (0.25 if key == "raw" else 0.01),
                i,
                str(r[key]) if key == "raw" else f"{r[key]:.3f}",
                va="center",
                fontsize=8,
            )
        ax.set_xlim(0, max(r[key] for r in vals) * 1.15)
    save(fig, "historical_matrix")
    tables["historical_matrix"] = vals


def workbook(tables: dict[str, list[Row]]) -> None:
    sys.path.insert(0, str(OUT / ".build/deps"))
    xl: Any = importlib.import_module("openpyxl")
    styles: Any = importlib.import_module("openpyxl.styles")
    book = xl.Workbook()
    intro = book.active
    intro.title = "Read me"
    for line in (
        "ACE retrospective: inspect chart inputs and their source records",
        "Snapshot: 2026-09-12. Development evidence only; testX and challenge excluded.",
        "Costs include unsolved cells. Reused observations are not new research spending.",
        "Cumulative curves follow the fixed validation file order, not an online scheduler.",
        "Threshold curves qualify final observed costs; they are not smaller-cap experiments.",
        "Archive token repricing excludes unrecoverable additional retry charges.",
        "Continuation costs contain the paid prefix once. Carried cells are not new runs.",
        "Luna preparation cost excludes unavailable historical embedding charges.",
        "See report.pdf for limitations, source hierarchy, and statistical interpretation.",
    ):
        intro.append([line])
    intro.column_dimensions["A"].width = 115
    for name, rows in tables.items():
        if not rows:
            continue
        sheet = book.create_sheet(name[:31])
        keys = list(dict.fromkeys(k for r in rows for k in r))
        sheet.append(keys)
        for row in rows:
            values: list[Any] = []
            for key in keys:
                v = row.get(key)
                if isinstance(v, (list, dict)):
                    v = json.dumps(v, ensure_ascii=False)
                if isinstance(v, str) and v.startswith(("=", "+", "-", "@")):
                    v = "'" + v
                values.append(v)
            sheet.append(values)
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = styles.Font(bold=True, color="FFFFFF")
            cell.fill = styles.PatternFill("solid", fgColor="444444")
        for column in sheet.columns:
            key = column[0].value
            sheet.column_dimensions[column[0].column_letter].width = min(
                55, max(14, len(str(key)) + 3)
            )
            if "cost" in str(key) or "spend" in str(key):
                for cell in column[1:]:
                    if isinstance(cell.value, (float, int)):
                        cell.number_format = "0.00000000"
    # Simple, auditable formulas in the summary make derived quantities
    # inspectable in spreadsheet applications; source numbers stay intact.
    summary = book["crossover"]
    columns = {cell.value: cell.column for cell in summary[1]}
    c = summary.max_column + 1
    summary.cell(1, c, "recomputed_cost_per_solve")
    for row in range(2, summary.max_row + 1):
        cost = summary.cell(row, columns["cost"]).coordinate
        solves = summary.cell(row, columns["qualified_solves"]).coordinate
        summary.cell(
            row, c, f'=IF({solves}=0,"",{cost}/{solves})'
        ).number_format = "0.00000000"
    book.save(OUT / "chart_data.xlsx")


def documentation_inventory() -> list[Row]:
    """Index permitted prose/code; never open excluded mixed documents."""
    report = (OUT / "report.md").read_text()
    linked: set[Path] = set()
    for link in re.findall(r"\]\(([^)]+)\)", report):
        if link.startswith("../../"):
            path = (OUT / link).resolve()
            if not path.is_file():
                raise ValueError(f"Broken source link: {link}")
            linked.add(path)
    candidates: set[Path] = set(linked)
    for folder in ("docs", "memory", "papers"):
        candidates.update(
            p
            for p in (ROOT / folder).iterdir()
            if p.is_file() and p.suffix in {".md", ".pdf"}
        )
    candidates.update((ROOT / "report").glob("*.html"))
    candidates.update(ROOT.glob("*.md"))
    for folder in (
        "ace",
        "runtime",
        "experiments/ace",
        "prompts/ace",
        "tools/reports",
        "tools/analysis",
    ):
        candidates.update(
            p
            for p in (ROOT / folder).rglob("*")
            if p.is_file() and p.suffix in {".py", ".jinja"}
        )
    for camp in (ROOT / "experiments/campaigns").iterdir():
        candidates.update(camp.glob("*.md"))
    excluded_mixed = {
        "PROGRESS.md",
        "HINTS.md",
        "README.md",
        "CLAUDE.md",
        "docs/CLOSED_HINTS.md",
        "docs/thesis_decisions.md",
        "docs/ace_review.md",
        "memory/omphalos-coverage.md",
        "memory/omphalos-ace-review.md",
        "memory/omphalos-x-partitions-ace-v2.md",
        "memory/MEMORY.md",
    }
    rows: list[Row] = []
    index = [
        "# Source catalogue",
        "",
        "Review levels are explicit: numerical verification, cited-source inspection, text/structure indexing, or exclusion. Large appendices are indexed in full and inspected selectively; this is not a claim that every model turn was individually read.",
        "",
    ]
    implementation = [
        "# Implementation index",
        "",
        "Static parsing only; experiment modules are not imported. Descriptions are source docstrings and may refer to historical behavior. The main report distinguishes implementation from measured effects.",
        "",
    ]
    for path in sorted(candidates):
        rel = path.relative_to(ROOT).as_posix()
        if path == Path(__file__).resolve():
            continue
        row: Row = dict(
            path=rel, bytes=path.stat().st_size, sha256="", role="", status=""
        )
        if (
            rel in excluded_mixed
            or rel.startswith("report/")
            or rel.startswith("experiments/campaigns/ace_review_")
            or rel.startswith("experiments/campaigns/coverage_20260911/")
            or "test_experiment" in rel
            or "testX" in rel
        ):
            row.update(
                status="excluded",
                role="closed/mixed outcomes, conservative exclusion, or canonical symlink alias",
            )
        elif path.suffix == ".pdf":
            content = path.read_bytes()
            row.update(
                status="reference reviewed by selected sections",
                role="supplied primary paper",
                sha256=hashlib.sha256(content).hexdigest(),
            )
        elif path.suffix in {".py", ".jinja"}:
            text = record_source(
                path, "static implementation evidence"
            ).decode()
            row.update(SOURCES[rel])
            row["status"] = (
                "cited and selectively inspected"
                if path in linked
                else "structure indexed"
            )
            if path.suffix == ".py":
                tree = ast.parse(text)
                doc = ast.get_docstring(tree) or ""
                implementation.extend(
                    [f"## {rel}", "", doc.split("\n\n")[0], ""]
                )
                for node in tree.body:
                    if isinstance(
                        node,
                        (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
                    ):
                        desc = (
                            (ast.get_docstring(node) or "")
                            .split("\n\n")[0]
                            .replace("\n", " ")
                        )
                        implementation.append(
                            f"- `{node.name}` (line {node.lineno}): {desc}".rstrip()
                        )
                implementation.append("")
        elif (
            path in linked
            or rel.startswith(
                tuple(f"experiments/campaigns/{c}/" for c in CAMPAIGNS)
            )
            or rel
            in {
                "docs/LINKS.md",
                "docs/usage.md",
                "papers/README.md",
                "memory/README.md",
                "memory/dual-harness-setup.md",
                "memory/no-unprompted-commits.md",
                "memory/omphalos-ace-applicability.md",
                "memory/omphalos-ace-attribution.md",
                "memory/omphalos-ace-bounded.md",
                "memory/omphalos-ace-capacity.md",
                "memory/omphalos-ace-mechanisms.md",
                "memory/omphalos-ace-models.md",
                "memory/omphalos-ace-polish.md",
                "memory/omphalos-benchmark-partitions.md",
                "memory/omphalos-change-control.md",
                "memory/omphalos-coverage-cycle.md",
                "memory/omphalos-local-conventions.md",
                "memory/omphalos-server-migration.md",
                "memory/pricing-table-no-auto-update.md",
                "memory/server-name-i34-gpu01.md",
            }
        ):
            text = record_source(
                path, "narrative / provenance evidence"
            ).decode()
            row.update(SOURCES[rel])
            row["status"] = (
                "cited and selectively inspected"
                if path in linked
                else "text indexed; corroborating source"
            )
            if "APPENDIX" in path.name:
                row["status"] = (
                    "complete section index; representative cases inspected"
                )
            headings = re.findall(r"^#{1,4} (.+)$", text, re.M)
            row["headings"] = len(headings)
            row["words"] = len(text.split())
            index.extend([f"## {rel}", "", row["status"], ""])
            index.extend(f"- {h}" for h in headings)
            index.append("")
        else:
            row.update(
                status="not used",
                role="unrelated, superseded, or insufficiently isolated from mixed history",
            )
        rows.append(row)
    (OUT / "source_catalogue.md").write_text("\n".join(index).rstrip() + "\n")
    (OUT / "implementation_index.md").write_text(
        "\n".join(implementation).rstrip() + "\n"
    )
    return rows


def appendices(tables: dict[str, list[Row]]) -> None:
    def money(value: Any) -> str:
        return "unavailable" if value is None else f"${float(value):.6f}"

    lines = [
        "# Numerical and source appendices",
        "",
        "These tables are generated from the same records as the figures and workbook. Archive costs use the fixed September 12, 2026 token schedule; recent campaign reports retain their documented charged-cost basis. Missing archival outcomes block complete-panel verdicts.",
        "",
        "## Historical archive catalogue",
        "",
        "Each row is one registered arm and seed. Short labels below are display names; the CSV retains exact archive, book, and source paths. Raw successes and successes qualified at the nominal token-repriced cap are shown separately.",
        "",
        "| Archive / treatment | Seed | Cells | Raw | Qualified | Cost | Complete |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in tables["archive_summary"]:
        name = (
            row["archive"]
            .replace("ace_x_validation_", "")
            .replace("acet_x_validation_", "triggered-")
            .replace("_agentic", "")
            .replace("ace_online_", "online-")
        )
        name = name.replace("_", " ")
        if row["archive"] in {
            "ace_x_validation_agentic",
            "ace_review_development",
            "ace_x_validation_ace_x3_offline_agentic",
        }:
            name += " / " + row["arm"].replace("-core-medium", "")
        lines.append(
            f"| {name} | {row['seed']} | {row['cells']} | {row['raw_solves']} | {row['qualified_solves']} | {money(row['cost_usd'])} | {'yes' if row['complete'] else 'no'} |"
        )
    lines.extend(
        [
            "",
            "Incomplete rows show observed successes only, not completed-panel coverage. They are excluded from the historical comparison figure. Their recorded cost lower bounds remain available in the CSV. A full report of their failed-attempt bill would require surviving receipts or a separately scoped recovery audit.",
            "",
            "## Recent development comparisons",
            "",
            "The reference is local to each campaign and stage. Repeated reference rows do not represent newly purchased controls.",
            "",
            "| Campaign | Stage | Arm | Cells | Solves | Cost |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for r in tables["development_comparisons"]:
        name = (
            r["campaign"]
            .replace("_20260910", "")
            .replace("_20260911", "")
            .replace("ace_", "")
            .replace("_", " ")
        )
        lines.append(
            f"| {name} | {r['stage']} | {r['arm']} | {r['cells']} | {r['solves']} | {money(r['cost'])} |"
        )
    lines.extend(
        [
            "",
            "## Accessible settled receipt exports",
            "",
            "This is a scoped subtotal of distinct request IDs in thirteen accessible campaign exports. It excludes the review, early archives, the mixed fixed-book coverage campaign, assistant usage, engineering, and the control cycle's conservative liability. It is not total Omphalos expenditure. The attribution/capacity entries are the component invoices, counted once.",
            "",
            "| Campaign | Unique receipts | Recorded charge | Unsettled |",
            "|---|---:|---:|---:|",
        ]
    )
    for r in tables["campaign_receipts"]:
        lines.append(
            f"| {r['campaign'].replace('_', ' ')} | {r['unique_receipts']} | {money(r['charged_usd'])} | {r['unsettled_receipts']} |"
        )
    total = sum(r["charged_usd"] for r in tables["campaign_receipts"])
    lines.extend(
        [
            "",
            f"Scoped receipt subtotal: **{money(total)}**. Duplicate request IDs are excluded by the builder; none were duplicated in these exports. The separately documented control-cycle conservative liability is $2.99915804 and is not silently added as a settled receipt charge.",
            "",
            "## Source coverage and reproducibility",
            "",
        ]
    )
    docs = tables["document_inventory"]
    counts: dict[str, int] = defaultdict(int)
    for r in docs:
        counts[r["status"]] += 1
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: {count} files.")
    lines.extend(
        [
            "",
            f"The numerical/source hash inventory contains {len(SOURCES)} inputs. The complete paths and hashes are in the Sources workbook sheet and source-input JSON. The document inventory separately records exclusions and review depth. Source catalogue and implementation index are companion editable files.",
            "",
            "The snapshot was taken from repository revision `97510c9f51bde36029c22deeb4bf956a5c288eca`. Existing local editor settings were preserved. The report builder reads permitted frozen records without launching experiment runners, model requests, or Rocq. All generated data and code stay inside Omphalos.",
            "",
            "## Coverage gaps",
            "",
            "- Closed testX and protected challenge stages, including mixed final reports, are excluded.",
            "- Some project-wide prose and old HTML reports mix restricted results and were not reopened.",
            "- Historical archives without all terminal results remain incomplete, rather than being scored on a favorable subset.",
            "- Old retry bills and Luna's historical embedding charge are not fully recoverable from the selected records.",
            "- Large per-case appendices are indexed exhaustively by section; the main narrative audits representative mechanisms and does not claim a line-by-line reading of every model transcript.",
            "- No current-source reproduction is claimed for the incomplete surviving control-cycle implementation.",
            "",
        ]
    )
    (OUT / "appendices.md").write_text("\n".join(lines))
    text = (OUT / "report.md").read_text()
    refs = re.findall(r"^\[\^([^]]+)\]: (.+)$", text, re.M)
    source_lines = [
        "# Sources",
        "",
        "Full references corresponding to the numbered footnotes. Repository links are relative to the report folder; the accompanying source inventory preserves exact paths and hashes. External references were checked on September 12, 2026; source versions are specified where applicable.",
        "",
    ]
    source_lines.extend(f"{i}. {body}" for i, (_, body) in enumerate(refs, 1))
    (OUT / "sources.md").write_text("\n".join(source_lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-only", action="store_true")
    args = parser.parse_args()
    (OUT / "data").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    tables = extract_tables()
    plots(tables)
    tables["document_inventory"] = documentation_inventory()
    appendices(tables)
    tables["sources"] = sorted(SOURCES.values(), key=lambda r: r["path"])
    tables["checks"] = CHECKS
    for name, rows in tables.items():
        write_csv(name, rows)
    workbook(tables)
    write_json("data/source_inputs.json", tables["sources"])
    write_json("data/numerical_checks.json", CHECKS)
    if not args.data_only:
        subprocess.run(
            [
                "pandoc",
                "report.md",
                "appendices.md",
                "sources.md",
                "--standalone",
                "--toc",
                "--toc-depth=2",
                "--number-sections",
                "--pdf-engine=xelatex",
                "--resource-path=.",
                "-V",
                "documentclass=article",
                "-V",
                "papersize=a4",
                "-V",
                "geometry:margin=22mm",
                "-V",
                "fontsize=10pt",
                "-V",
                "colorlinks=true",
                "-V",
                "urlcolor=MidnightBlue",
                "-V",
                "linkcolor=black",
                "-V",
                "mainfont=DejaVu Serif",
                "-V",
                "sansfont=DejaVu Sans",
                "-V",
                "monofont=DejaVu Sans Mono",
                "-o",
                "report.pdf",
            ],
            cwd=OUT,
            check=True,
        )
    print(
        f"Built {len(tables)} tables and {len(CHECKS)} numerical checks in {OUT}"
    )


if __name__ == "__main__":
    main()
