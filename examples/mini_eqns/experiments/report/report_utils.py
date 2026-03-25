from __future__ import annotations

from dataclasses import dataclass
from html import escape
import math
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import yaml

REASONING_ORDER = ["None", "low", "medium", "high", "xhigh", "unspecified"]
STEP_REASONING_ORDER = ["None", "low", "medium", "high", "xhigh"]
MODEL_ORDER = ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano"]
FAMILY_COLORS = {
    "baseline": "#1d4ed8",
    "guided": "#ea580c",
    "step_by_step": "#15803d",
}
LEGACY_REASONING_EFFORT = {
    "baseline_experiment_1": "None",
    "baseline_experiment_6": "None",
}


@dataclass(frozen=True)
class ReportPaths:
    repo_root: Path
    report_root: Path
    benchmark_file: Path


def find_report_paths(start: Path | None = None) -> ReportPaths:
    start = (start or Path.cwd()).resolve()
    for candidate in [start, *start.parents]:
        report_root = candidate / "examples" / "mini_eqns" / "experiments" / "report"
        benchmark_file = candidate / "examples" / "mini_eqns" / "benchmark" / "htps.txt"
        if report_root.exists() and benchmark_file.exists():
            return ReportPaths(candidate, report_root, benchmark_file)
    raise FileNotFoundError("Could not locate examples/mini_eqns/experiments/report")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    return data if isinstance(data, dict) else {}


def normalize_reasoning_effort(value: Any, experiment_name: str) -> str:
    if experiment_name in LEGACY_REASONING_EFFORT:
        return LEGACY_REASONING_EFFORT[experiment_name]
    if value in (None, ""):
        return "unspecified"
    if str(value).lower() == "none":
        return "None"
    return str(value)


def infer_family(experiment_name: str) -> str:
    if experiment_name.startswith("baseline_experiment_"):
        return "baseline"
    if experiment_name.startswith("guided_experiment_"):
        return "guided"
    if experiment_name.startswith("step_by_step_experiment_"):
        return "step_by_step"
    return "other"


def model_label(model_name: str) -> str:
    return {
        "gpt-5.4": "GPT-5.4",
        "gpt-5.4-mini": "GPT-5.4 mini",
        "gpt-5.4-nano": "GPT-5.4 nano",
    }.get(model_name, model_name)


def experiment_short_label(experiment_name: str) -> str:
    return (
        experiment_name.replace("baseline_experiment_", "B")
        .replace("guided_experiment_", "G")
        .replace("step_by_step_experiment_", "S")
    )


def money(value: float) -> str:
    return f"${value:.2f}"


def precise_money(value: float) -> str:
    return f"${value:.4f}"


def load_benchmarks(benchmark_file: Path) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    with benchmark_file.open() as handle:
        index = 1
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line.split("#", 1)[0].strip()
            if "=" not in line:
                continue
            lhs, rhs = line.split("=", 1)
            rows.append(
                {
                    "bench_name": f"{index:03d}",
                    "lhs": lhs.strip(),
                    "rhs": rhs.strip(),
                    "equation": f"{lhs.strip()} = {rhs.strip()}",
                }
            )
            index += 1
    return pd.DataFrame(rows)


def _first_config_params(experiment_dir: Path) -> dict[str, Any]:
    experiment = load_yaml(experiment_dir / "experiment.yaml")
    configs = experiment.get("configs", {})
    if not configs:
        return {}
    first_config = next(iter(configs.values()))
    return dict(first_config.get("params", {}))


def load_experiment_rows(experiment_dir: Path) -> pd.DataFrame:
    params = _first_config_params(experiment_dir)
    family = infer_family(experiment_dir.name)

    rows = pd.read_csv(experiment_dir / "results_summary.csv", dtype={"bench_name": str})
    rows["bench_name"] = rows["bench_name"].str.zfill(3)
    rows["success"] = rows["success"].astype(str).str.lower().eq("true")
    rows["price"] = pd.to_numeric(rows["price"])
    rows["experiment_name"] = experiment_dir.name
    rows["family"] = family

    if family == "step_by_step":
        rows["model_name"] = params.get("step_model_name", "unknown")
        rows["reasoning_effort"] = normalize_reasoning_effort(
            params.get("step_reasoning_effort"),
            experiment_dir.name,
        )
        rows["sketch_model_name"] = params.get("sketch_model_name", "unknown")
        rows["sketch_reasoning_effort"] = normalize_reasoning_effort(
            params.get("sketch_reasoning_effort"),
            experiment_dir.name,
        )
        rows["step_model_name"] = params.get("step_model_name", "unknown")
        rows["step_reasoning_effort"] = normalize_reasoning_effort(
            params.get("step_reasoning_effort"),
            experiment_dir.name,
        )
        rows["configured_num_completions"] = params.get("num_completions", 1)
        rows["configured_max_feedback_cycles"] = params.get("max_feedback_cycles_per_step")
        rows["configured_max_steps"] = params.get("max_steps")
        rows["configured_max_sketch_feedback_cycles"] = params.get("max_sketch_feedback_cycles")
        rows["configured_budget"] = params.get("max_dollar_budget")
        rows["configured_loop"] = params.get("loop")
    else:
        rows["model_name"] = params.get(
            "model_name",
            rows.get("model_name", pd.Series(["unknown"])).iloc[0],
        )
        rows["reasoning_effort"] = normalize_reasoning_effort(
            params.get("reasoning_effort"),
            experiment_dir.name,
        )
        rows["sketch_model_name"] = None
        rows["sketch_reasoning_effort"] = None
        rows["step_model_name"] = None
        rows["step_reasoning_effort"] = None
        rows["configured_num_completions"] = params.get("num_completions", 1)
        rows["configured_max_feedback_cycles"] = params.get(
            "max_feedback_cycles",
            params.get("max_feedback_cycles_per_step"),
        )
        rows["configured_max_steps"] = None
        rows["configured_max_sketch_feedback_cycles"] = None
        rows["configured_budget"] = params.get("max_dollar_budget")
        rows["configured_loop"] = params.get("loop")
    return rows


def load_report_runs(report_root: Path) -> pd.DataFrame:
    frames = []
    for experiment_dir in sorted(path for path in report_root.iterdir() if path.is_dir()):
        if (experiment_dir / "experiment.yaml").exists() and (experiment_dir / "results_summary.csv").exists():
            frames.append(load_experiment_rows(experiment_dir))
    if not frames:
        raise FileNotFoundError(f"No experiment outputs found in {report_root}")
    return pd.concat(frames, ignore_index=True)


def build_experiment_inventory(runs: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        runs.groupby("experiment_name", dropna=False)
        .agg(
            family=("family", "first"),
            model_name=("model_name", "first"),
            reasoning_effort=("reasoning_effort", "first"),
            sketch_model_name=("sketch_model_name", "first"),
            sketch_reasoning_effort=("sketch_reasoning_effort", "first"),
            step_model_name=("step_model_name", "first"),
            step_reasoning_effort=("step_reasoning_effort", "first"),
            configured_num_completions=("configured_num_completions", "first"),
            configured_max_feedback_cycles=("configured_max_feedback_cycles", "first"),
            configured_max_steps=("configured_max_steps", "first"),
            configured_max_sketch_feedback_cycles=("configured_max_sketch_feedback_cycles", "first"),
            configured_budget=("configured_budget", "first"),
            configured_loop=("configured_loop", "first"),
            solved=("success", "sum"),
            total=("bench_name", "size"),
            total_cost=("price", "sum"),
        )
        .reset_index()
    )
    grouped["avg_cost_per_success"] = grouped.apply(
        lambda row: row["total_cost"] / row["solved"] if row["solved"] else float("inf"),
        axis=1,
    )
    grouped["reasoning_effort"] = pd.Categorical(
        grouped["reasoning_effort"],
        categories=REASONING_ORDER,
        ordered=True,
    )
    grouped["model_name"] = pd.Categorical(
        grouped["model_name"],
        categories=MODEL_ORDER,
        ordered=True,
    )
    grouped["step_reasoning_effort"] = pd.Categorical(
        grouped["step_reasoning_effort"],
        categories=REASONING_ORDER,
        ordered=True,
    )
    grouped["step_model_name"] = pd.Categorical(
        grouped["step_model_name"],
        categories=MODEL_ORDER,
        ordered=True,
    )
    return grouped.sort_values(
        ["family", "model_name", "reasoning_effort", "experiment_name"]
    ).reset_index(drop=True)


def select_best_configs(inventory: pd.DataFrame) -> pd.DataFrame:
    ranked = inventory.sort_values(
        ["family", "solved", "total_cost", "avg_cost_per_success"],
        ascending=[True, False, True, True],
    )
    return ranked.groupby("family", as_index=False).head(1).reset_index(drop=True)


def load_budget_curve(experiment_dir: Path) -> pd.DataFrame:
    curve = pd.read_csv(experiment_dir / "budget_vs_solved_points.csv")
    curve["experiment_name"] = experiment_dir.name
    return curve


def load_budget_curves(report_root: Path, experiment_names: list[str]) -> pd.DataFrame:
    frames = [load_budget_curve(report_root / name) for name in experiment_names]
    return pd.concat(frames, ignore_index=True)


def build_step_advantage_table(
    runs: pd.DataFrame,
    benchmarks: pd.DataFrame,
    baseline_experiment: str,
    guided_experiment: str,
    step_experiment: str,
) -> pd.DataFrame:
    left = runs.loc[runs["experiment_name"] == baseline_experiment, ["bench_name", "success"]].rename(
        columns={"success": "baseline"}
    )
    middle = runs.loc[runs["experiment_name"] == guided_experiment, ["bench_name", "success"]].rename(
        columns={"success": "guided"}
    )
    right = runs.loc[runs["experiment_name"] == step_experiment, ["bench_name", "success"]].rename(
        columns={"success": "step_by_step"}
    )
    merged = benchmarks.merge(left, on="bench_name").merge(middle, on="bench_name").merge(right, on="bench_name")
    merged["status"] = "same_or_mixed"
    merged.loc[
        merged["step_by_step"] & (~merged["baseline"]) & (~merged["guided"]),
        "status",
    ] = "step_only"
    merged.loc[
        (~merged["step_by_step"]) & (merged["baseline"] | merged["guided"]),
        "status",
    ] = "step_regression"
    return merged


def build_step_missing_table(inventory: pd.DataFrame) -> pd.DataFrame:
    step = inventory.loc[inventory["family"] == "step_by_step"].copy()
    rows: list[dict[str, str]] = []
    for model in MODEL_ORDER:
        for effort in ["None", "low", "medium", "high"]:
            subset = step.loc[
                (step["model_name"].astype(str) == model)
                & (step["reasoning_effort"].astype(str) == effort)
            ]
            if subset.empty:
                status = "missing"
                runs = "—"
            else:
                status = "present"
                runs = ", ".join(experiment_short_label(str(name)) for name in subset["experiment_name"])
            rows.append(
                {
                    "step model": model_label(model),
                    "step effort": effort,
                    "status": status,
                    "runs": runs,
                }
            )
    return pd.DataFrame(rows)


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#" + "".join(f"{channel:02x}" for channel in rgb)


def _mix(color_a: str, color_b: str, weight: float) -> str:
    a = _hex_to_rgb(color_a)
    b = _hex_to_rgb(color_b)
    mixed = tuple(round(a[i] * (1 - weight) + b[i] * weight) for i in range(3))
    return _rgb_to_hex(mixed)


def render_simple_table_html(
    df: pd.DataFrame,
    formatters: dict[str, Callable[[Any], str]] | None = None,
    index: bool = False,
) -> str:
    formatters = formatters or {}
    columns = list(df.columns)
    parts = ['<table class="report-simple-table">', "<thead><tr>"]
    if index:
        parts.append("<th></th>")
    for column in columns:
        parts.append(f"<th>{escape(str(column))}</th>")
    parts.append("</tr></thead><tbody>")
    for idx, row in df.iterrows():
        parts.append("<tr>")
        if index:
            parts.append(f"<th>{escape(str(idx))}</th>")
        for column in columns:
            value = row[column]
            rendered = formatters[column](value) if column in formatters else str(value)
            parts.append(f"<td>{escape(rendered)}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def render_strategy_matrix_html(inventory: pd.DataFrame, family: str) -> str:
    subset = inventory.loc[inventory["family"] == family].copy()
    if subset.empty:
        return "<p>No runs available.</p>"
    family_color = FAMILY_COLORS.get(family, "#334155")
    models = [m for m in MODEL_ORDER if m in set(subset["model_name"].astype(str))]
    efforts = [
        effort
        for effort in ["None", "low", "medium", "high", "xhigh"]
        if effort in set(subset["reasoning_effort"].astype(str))
    ]
    max_solved = max(int(subset["solved"].max()), 1)

    parts = ['<table class="strategy-matrix">', "<thead><tr><th>Model</th>"]
    for effort in efforts:
        parts.append(f"<th>{escape(effort)}</th>")
    parts.append("</tr></thead><tbody>")

    for model in models:
        parts.append(f"<tr><th>{escape(model_label(model))}</th>")
        model_rows = subset.loc[subset["model_name"].astype(str) == model]
        for effort in efforts:
            cell = model_rows.loc[model_rows["reasoning_effort"].astype(str) == effort]
            if cell.empty:
                parts.append('<td class="empty">—</td>')
                continue
            row = cell.iloc[0]
            weight = max(0.18, min(0.90, float(row["solved"]) / max_solved))
            background = _mix("#f8fafc", family_color, weight)
            parts.append(
                "<td>"
                f'<div class="matrix-card" style="background:{background};">'
                f'<div class="solve">{int(row["solved"])} / 22</div>'
                f'<div class="cost">{money(float(row["total_cost"]))}</div>'
                f'<div class="label">{escape(experiment_short_label(str(row["experiment_name"])))}</div>'
                "</div>"
                "</td>"
            )
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def render_step_by_step_matrix_html(inventory: pd.DataFrame) -> str:
    subset = inventory.loc[inventory["family"] == "step_by_step"].copy()
    if subset.empty:
        return "<p>No step-by-step runs available.</p>"
    family_color = FAMILY_COLORS["step_by_step"]
    models = [m for m in MODEL_ORDER if m in set(subset["model_name"].astype(str))]
    efforts = [
        effort
        for effort in STEP_REASONING_ORDER
        if effort in set(subset["reasoning_effort"].astype(str))
    ]
    max_solved = max(int(subset["solved"].max()), 1)

    parts = ['<table class="strategy-matrix">', "<thead><tr><th>Step model</th>"]
    for effort in efforts:
        parts.append(f"<th>{escape(effort)}</th>")
    parts.append("</tr></thead><tbody>")

    for model in models:
        parts.append(f"<tr><th>{escape(model_label(model))}</th>")
        model_rows = subset.loc[subset["model_name"].astype(str) == model]
        for effort in efforts:
            cell = model_rows.loc[model_rows["reasoning_effort"].astype(str) == effort].copy()
            if cell.empty:
                parts.append('<td class="empty">—</td>')
                continue
            solved_min = int(cell["solved"].min())
            solved_max = int(cell["solved"].max())
            cost_min = float(cell["total_cost"].min())
            cost_max = float(cell["total_cost"].max())
            weight = max(0.18, min(0.90, solved_max / max_solved))
            background = _mix("#f8fafc", family_color, weight)
            run_labels = ", ".join(experiment_short_label(str(name)) for name in cell["experiment_name"])
            if len(cell) == 1:
                solve_text = f"{solved_max} / 22"
                cost_text = money(cost_max)
                label_text = run_labels
            else:
                solve_text = f"{solved_min}-{solved_max} / 22"
                cost_text = f"{money(cost_min)}-{money(cost_max)}"
                label_text = f"{len(cell)} runs: {run_labels}"
            parts.append(
                "<td>"
                f'<div class="matrix-card" style="background:{background};">'
                f'<div class="solve">{escape(solve_text)}</div>'
                f'<div class="cost">{escape(cost_text)}</div>'
                f'<div class="label">{escape(label_text)}</div>'
                "</div>"
                "</td>"
            )
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def _ticks(max_value: float, count: int) -> list[float]:
    if max_value <= 0:
        return [0.0, 1.0]
    raw_step = max_value / max(1, count - 1)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude
    if normalized <= 1:
        nice_step = magnitude
    elif normalized <= 2:
        nice_step = 2 * magnitude
    elif normalized <= 5:
        nice_step = 5 * magnitude
    else:
        nice_step = 10 * magnitude
    limit = math.ceil(max_value / nice_step) * nice_step
    return [i * nice_step for i in range(int(round(limit / nice_step)) + 1)]


def render_budget_curves_svg(
    curves: pd.DataFrame,
    inventory: pd.DataFrame,
    title: str = "Budget curves for the best runs",
) -> str:
    width, height = 880, 460
    margin = {"left": 72, "right": 220, "top": 48, "bottom": 56}
    plot_width = width - margin["left"] - margin["right"]
    plot_height = height - margin["top"] - margin["bottom"]
    meta = inventory.set_index("experiment_name")
    max_x = max(float(curves["budget_dollars"].max()), 0.01)
    max_y = max(float(curves["solved_problems"].max()), 1.0)

    def x_to_px(x: float) -> float:
        return margin["left"] + (x / max_x) * plot_width

    def y_to_px(y: float) -> float:
        return margin["top"] + plot_height - (y / max_y) * plot_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fffdf8"/>',
        f'<text x="{width / 2}" y="28" text-anchor="middle" font-size="18" font-family="Georgia">{escape(title)}</text>',
    ]

    for tick in _ticks(max_x, 6):
        x = x_to_px(tick)
        parts.append(
            f'<line x1="{x:.2f}" y1="{margin["top"]}" x2="{x:.2f}" y2="{margin["top"] + plot_height}" stroke="#e5e7eb" stroke-dasharray="3 4"/>'
        )
        parts.append(
            f'<text x="{x:.2f}" y="{height - 22}" text-anchor="middle" font-size="11" fill="#475569">{money(tick)}</text>'
        )
    for tick in range(int(max_y) + 1):
        y = y_to_px(tick)
        parts.append(
            f'<line x1="{margin["left"]}" y1="{y:.2f}" x2="{margin["left"] + plot_width}" y2="{y:.2f}" stroke="#e5e7eb" stroke-dasharray="3 4"/>'
        )
        parts.append(
            f'<text x="{margin["left"] - 10}" y="{y + 4:.2f}" text-anchor="end" font-size="11" fill="#475569">{tick}</text>'
        )

    parts.append(
        f'<line x1="{margin["left"]}" y1="{margin["top"] + plot_height}" x2="{margin["left"] + plot_width}" y2="{margin["top"] + plot_height}" stroke="#0f172a"/>'
    )
    parts.append(
        f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{margin["top"] + plot_height}" stroke="#0f172a"/>'
    )
    parts.append(
        f'<text x="{margin["left"] + plot_width / 2}" y="{height - 4}" text-anchor="middle" font-size="13">Per-problem budget (USD)</text>'
    )
    parts.append(
        f'<text x="18" y="{margin["top"] + plot_height / 2}" text-anchor="middle" font-size="13" transform="rotate(-90 18 {margin["top"] + plot_height / 2})">Solved benchmarks</text>'
    )

    legend_x = margin["left"] + plot_width + 24
    legend_y = margin["top"] + 24
    legend_height = max(124, 24 + 34 * max(1, curves["experiment_name"].nunique()))
    parts.append(
        f'<rect x="{legend_x - 14}" y="{legend_y - 22}" width="188" height="{legend_height}" rx="10" fill="#ffffff" stroke="#e2e8f0"/>'
    )

    for index, (experiment_name, subset) in enumerate(curves.groupby("experiment_name")):
        subset = subset.sort_values("budget_dollars")
        family = str(meta.loc[experiment_name, "family"])
        color = FAMILY_COLORS.get(family, "#555555")
        points = list(zip(subset["budget_dollars"], subset["solved_problems"]))
        if not points:
            continue
        path = [f"M {x_to_px(float(points[0][0])):.2f} {y_to_px(float(points[0][1])):.2f}"]
        current_y = float(points[0][1])
        for next_x, next_y in points[1:]:
            path.append(f"L {x_to_px(float(next_x)):.2f} {y_to_px(current_y):.2f}")
            path.append(f"L {x_to_px(float(next_x)):.2f} {y_to_px(float(next_y)):.2f}")
            current_y = float(next_y)
        parts.append(f'<path d="{" ".join(path)}" fill="none" stroke="{color}" stroke-width="3.4"/>')
        end_x = x_to_px(float(points[-1][0]))
        end_y = y_to_px(float(points[-1][1]))
        parts.append(f'<circle cx="{end_x:.2f}" cy="{end_y:.2f}" r="4.8" fill="{color}"/>')

        legend_line_y = legend_y + index * 34
        solved = int(meta.loc[experiment_name, "solved"])
        cost = precise_money(float(meta.loc[experiment_name, "total_cost"]))
        family_label = family.replace("_", " ").title()
        parts.append(
            f'<line x1="{legend_x}" y1="{legend_line_y}" x2="{legend_x + 24}" y2="{legend_line_y}" stroke="{color}" stroke-width="4"/>'
        )
        parts.append(
            f'<text x="{legend_x + 32}" y="{legend_line_y + 4}" font-size="12" fill="#0f172a">{escape(f"{family_label} ({experiment_short_label(experiment_name)})")}</text>'
        )
        parts.append(
            f'<text x="{legend_x + 32}" y="{legend_line_y + 18}" font-size="11" fill="#475569">{escape(f"{solved}/22 solved, {cost}")}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)
