#!/usr/bin/env python3
"""
Generate paper-style budget curves for mini_eqns experiments.

For each experiment directory, this script builds a step curve:

    x = per-problem inference budget in dollars
    y = number of solved problems

Each problem contributes at the cheapest budget at which it was solved.
If an experiment contains multiple runs for the same `bench_name`, the
curve counts that problem once, at its minimum successful cost.

Outputs per experiment:
- `budget_vs_solved.svg`
- `budget_vs_solved_points.csv`

Usage:
    python experiments/plot_budget_curves.py
    python experiments/plot_budget_curves.py experiments/output/guided_experiment_nano
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


OUTPUT_DIR = Path(__file__).parent / "output"


@dataclass
class ConfigRun:
    config_id: str
    problem_key: str
    success: bool
    spent_price: float | None
    budget_cap: float | None


@dataclass
class ProblemOutcome:
    problem_key: str
    solved_price: float | None
    budget_cap: float


def load_yaml(path: Path) -> dict[str, Any]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


SUCCESS_RE = re.compile(r"^\s*success:\s*(true|false)\s*$", re.IGNORECASE | re.MULTILINE)
SPENT_BUDGET_PRICE_RE = re.compile(
    r"^\s*spent_budget:\s*$.*?^\s*price:\s*([0-9.eE+-]+)\s*$",
    re.MULTILINE | re.DOTALL,
)


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_result_summary(result_file: Path) -> tuple[bool, float | None]:
    """
    Extract only the fields needed for budget curves from a large `result.yaml`.
    This avoids loading full raw traces into memory.
    """
    text = result_file.read_text()
    success_match = SUCCESS_RE.search(text)
    price_match = SPENT_BUDGET_PRICE_RE.search(text)
    success = (
        success_match is not None
        and success_match.group(1).strip().lower() == "true"
    )
    spent_price = as_float(price_match.group(1)) if price_match else None
    return success, spent_price


def load_config_runs(experiment_dir: Path) -> list[ConfigRun]:
    experiment_file = experiment_dir / "experiment.yaml"
    if not experiment_file.exists():
        raise FileNotFoundError(f"Missing experiment file: {experiment_file}")

    experiment = load_yaml(experiment_file)
    configs = experiment.get("configs", {})
    if not isinstance(configs, dict):
        raise ValueError(f"Malformed configs section in {experiment_file}")

    runs: list[ConfigRun] = []
    for config_id, meta in configs.items():
        if not isinstance(meta, dict):
            continue
        params = meta.get("params", {})
        if not isinstance(params, dict):
            params = {}
        bench_name = str(params.get("bench_name", config_id))
        budget_cap = as_float(params.get("max_dollar_budget"))

        result_file = experiment_dir / "configs" / str(config_id) / "result.yaml"
        success = False
        spent_price: float | None = None
        if result_file.exists():
            success, spent_price = load_result_summary(result_file)

        runs.append(
            ConfigRun(
                config_id=str(config_id),
                problem_key=bench_name,
                success=success,
                spent_price=spent_price,
                budget_cap=budget_cap,
            )
        )
    return runs


def collapse_to_problems(runs: list[ConfigRun]) -> list[ProblemOutcome]:
    grouped: dict[str, list[ConfigRun]] = {}
    for run in runs:
        grouped.setdefault(run.problem_key, []).append(run)

    problems: list[ProblemOutcome] = []
    for problem_key, group in grouped.items():
        solved_prices = sorted(
            price
            for price in (run.spent_price for run in group if run.success)
            if price is not None
        )
        solved_price = solved_prices[0] if solved_prices else None

        caps = [
            cap
            for cap in (
                *[run.budget_cap for run in group],
                *[run.spent_price for run in group],
            )
            if cap is not None
        ]
        budget_cap = max(caps) if caps else 0.0
        problems.append(
            ProblemOutcome(
                problem_key=problem_key,
                solved_price=solved_price,
                budget_cap=budget_cap,
            )
        )
    return sorted(problems, key=lambda p: p.problem_key)


def build_curve_points(problems: list[ProblemOutcome]) -> list[tuple[float, int]]:
    solved_prices = sorted(
        problem.solved_price for problem in problems if problem.solved_price is not None
    )

    points: list[tuple[float, int]] = [(0.0, 0)]
    solved_so_far = 0
    i = 0
    while i < len(solved_prices):
        price = solved_prices[i]
        same_price = 0
        while i < len(solved_prices) and solved_prices[i] == price:
            same_price += 1
            i += 1
        solved_so_far += same_price
        points.append((price, solved_so_far))
    return points


def nice_ticks(max_value: float, count: int = 6) -> list[float]:
    if max_value <= 0:
        return [0.0, 1.0]
    raw_step = max_value / max(1, count - 1)
    magnitude = 10 ** math.floor(math.log10(raw_step))
    normalized = raw_step / magnitude
    if normalized <= 1:
        nice_step = 1 * magnitude
    elif normalized <= 2:
        nice_step = 2 * magnitude
    elif normalized <= 5:
        nice_step = 5 * magnitude
    else:
        nice_step = 10 * magnitude
    tick_max = math.ceil(max_value / nice_step) * nice_step
    ticks = [i * nice_step for i in range(int(round(tick_max / nice_step)) + 1)]
    if ticks[-1] < max_value:
        ticks.append(ticks[-1] + nice_step)
    return ticks


def fmt_dollars(value: float) -> str:
    if value >= 1:
        return f"${value:.2f}"
    if value >= 0.1:
        return f"${value:.2f}"
    if value >= 0.01:
        return f"${value:.3f}"
    return f"${value:.4f}"


def svg_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def step_path_data(
    curve_points: list[tuple[float, int]],
    x_max: float,
    x_to_px,
    y_to_px,
) -> str:
    parts: list[str] = []
    current_x, current_y = curve_points[0]
    parts.append(f"M {x_to_px(current_x):.2f} {y_to_px(current_y):.2f}")

    for next_x, next_y in curve_points[1:]:
        parts.append(f"L {x_to_px(next_x):.2f} {y_to_px(current_y):.2f}")
        parts.append(f"L {x_to_px(next_x):.2f} {y_to_px(next_y):.2f}")
        current_x, current_y = next_x, next_y

    parts.append(f"L {x_to_px(x_max):.2f} {y_to_px(current_y):.2f}")
    return " ".join(parts)


def render_svg(experiment_name: str, problems: list[ProblemOutcome]) -> str:
    width = 900
    height = 560
    margin_left = 90
    margin_right = 30
    margin_top = 70
    margin_bottom = 80

    solved_total = sum(1 for p in problems if p.solved_price is not None)
    total_problems = len(problems)
    max_cap = max((p.budget_cap for p in problems), default=0.0)
    max_success = max(
        (p.solved_price for p in problems if p.solved_price is not None),
        default=0.0,
    )
    x_max = max(max_cap, max_success, 1e-6)
    y_max = max(total_problems, 1)

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    x_ticks = nice_ticks(x_max)
    x_display_max = max(x_ticks[-1], x_max)

    def x_to_px(x: float) -> float:
        return margin_left + (x / x_display_max) * plot_width

    def y_to_px(y: float) -> float:
        return margin_top + plot_height - (y / y_max) * plot_height

    y_ticks = list(range(0, y_max + 1, max(1, math.ceil(y_max / 8))))
    if y_ticks[-1] != y_max:
        y_ticks.append(y_max)

    curve_points = build_curve_points(problems)
    path_data = step_path_data(curve_points, x_display_max, x_to_px, y_to_px)

    markers = []
    for x, y in curve_points[1:]:
        markers.append(
            f'<circle cx="{x_to_px(x):.2f}" cy="{y_to_px(y):.2f}" r="4" '
            f'fill="#0f766e" stroke="white" stroke-width="1.5" />'
        )

    grid_lines: list[str] = []
    x_tick_labels: list[str] = []
    for tick in x_ticks:
        px = x_to_px(tick)
        grid_lines.append(
            f'<line x1="{px:.2f}" y1="{margin_top}" x2="{px:.2f}" '
            f'y2="{height - margin_bottom}" stroke="#e5e7eb" stroke-width="1" />'
        )
        x_tick_labels.append(
            f'<text x="{px:.2f}" y="{height - margin_bottom + 24}" '
            f'text-anchor="middle" font-size="12" fill="#374151">{fmt_dollars(tick)}</text>'
        )

    y_tick_labels: list[str] = []
    for tick in y_ticks:
        py = y_to_px(tick)
        grid_lines.append(
            f'<line x1="{margin_left}" y1="{py:.2f}" x2="{width - margin_right}" '
            f'y2="{py:.2f}" stroke="#e5e7eb" stroke-width="1" />'
        )
        y_tick_labels.append(
            f'<text x="{margin_left - 12}" y="{py + 4:.2f}" text-anchor="end" '
            f'font-size="12" fill="#374151">{tick}</text>'
        )

    title = svg_escape(experiment_name)
    subtitle = svg_escape(
        f"Solved {solved_total}/{total_problems} problems | final budget ceiling {fmt_dollars(max_cap)}"
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Budget curve for {title}">
  <rect width="100%" height="100%" fill="#fcfcfd" />
  <text x="{margin_left}" y="32" font-size="24" font-weight="700" fill="#111827">{title}</text>
  <text x="{margin_left}" y="54" font-size="14" fill="#4b5563">{subtitle}</text>
  {''.join(grid_lines)}
  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#111827" stroke-width="1.5" />
  <line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" stroke="#111827" stroke-width="1.5" />
  <path d="{path_data}" fill="none" stroke="#0f766e" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" />
  {''.join(markers)}
  {''.join(x_tick_labels)}
  {''.join(y_tick_labels)}
  <text x="{margin_left + plot_width / 2:.2f}" y="{height - 20}" text-anchor="middle" font-size="14" fill="#111827">Per-problem inference budget (USD)</text>
  <text x="24" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" font-size="14" fill="#111827" transform="rotate(-90, 24, {margin_top + plot_height / 2:.2f})">Solved problems</text>
</svg>
"""


def write_curve_points_csv(path: Path, problems: list[ProblemOutcome]) -> None:
    points = build_curve_points(problems)
    max_cap = max((p.budget_cap for p in problems), default=0.0)
    max_success = max(
        (p.solved_price for p in problems if p.solved_price is not None),
        default=0.0,
    )
    x_max = max(max_cap, max_success, 0.0)
    if points[-1][0] != x_max:
        points = [*points, (x_max, points[-1][1])]

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["budget_dollars", "solved_problems"])
        writer.writerows(points)


def generate_for_experiment(experiment_dir: Path) -> tuple[int, int]:
    runs = load_config_runs(experiment_dir)
    problems = collapse_to_problems(runs)

    svg = render_svg(experiment_dir.name, problems)
    svg_path = experiment_dir / "budget_vs_solved.svg"
    points_path = experiment_dir / "budget_vs_solved_points.csv"
    svg_path.write_text(svg)
    write_curve_points_csv(points_path, problems)

    solved = sum(1 for p in problems if p.solved_price is not None)
    return solved, len(problems)


def iter_experiment_dirs(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p) for p in paths]
    if not OUTPUT_DIR.exists():
        raise FileNotFoundError(f"No output directory found at {OUTPUT_DIR}")
    return sorted(path for path in OUTPUT_DIR.iterdir() if path.is_dir())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        help="Experiment output directories. Defaults to all directories under experiments/output.",
    )
    args = parser.parse_args()

    experiment_dirs = iter_experiment_dirs(args.paths)
    if not experiment_dirs:
        raise SystemExit("No experiment directories found.")

    for experiment_dir in experiment_dirs:
        solved, total = generate_for_experiment(experiment_dir)
        print(
            f"{experiment_dir.name:<45}  {solved:>2}/{total:<2}  "
            f"{experiment_dir / 'budget_vs_solved.svg'}"
        )


if __name__ == "__main__":
    main()
