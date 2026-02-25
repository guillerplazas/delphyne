#!/usr/bin/env python3
"""
Summarize an experiment's results.

Usage:
    # Summarize a specific experiment:
    python experiments/summarize_experiment.py experiments/output/guided_experiment

    # Summarize all experiments (one line each):
    python experiments/summarize_experiment.py
"""

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"


def _wall_clock(output_dir: Path) -> str:
    configs_dir = output_dir / "configs"
    if not configs_dir.exists():
        return "N/A"
    config_files = list(configs_dir.iterdir())
    if not config_files:
        return "N/A"
    mtimes = [f.stat().st_mtime for f in config_files]
    duration_s = max(mtimes) - min(mtimes)
    hours, rem = divmod(int(duration_s), 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours}h {minutes}m {seconds}s"


def summarize(output_dir: Path) -> str:
    csv_path = output_dir / "results_summary.csv"
    if not csv_path.exists():
        print(f"Error: {csv_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(csv_path, "r") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    successes = sum(1 for r in rows if r["success"] == "True")
    total_cost = sum(float(r["price"]) for r in rows)
    # Cost of successes only: sum costs from successful runs divided by count
    success_cost = sum(float(r["price"]) for r in rows if r["success"] == "True")
    avg_cost_per_success = success_cost / successes if successes > 0 else float("inf")

    lines = [
        f"Experiment: {output_dir.name}",
        f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Total cost:           ${total_cost:.4f}",
        f"Successes:            {successes}/{total}",
        f"Avg cost per success: ${avg_cost_per_success:.4f}",
        f"Wall-clock time:      {_wall_clock(output_dir)}",
        "",
    ]
    return "\n".join(lines)


def _one_liner(output_dir: Path) -> str:
    csv_path = output_dir / "results_summary.csv"
    if not csv_path.exists():
        return f"{output_dir.name:<45} (no results yet)"

    with open(csv_path, "r") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    successes = sum(1 for r in rows if r["success"] == "True")
    total_cost = sum(float(r["price"]) for r in rows)
    success_cost = sum(float(r["price"]) for r in rows if r["success"] == "True")
    avg_cost_per_success = success_cost / successes if successes > 0 else float("inf")

    return (
        f"{output_dir.name:<45}"
        f"  {successes}/{total}"
        f"  total=${total_cost:.3f}"
        f"  avg/success=${avg_cost_per_success:.4f}"
        f"  {_wall_clock(output_dir)}"
    )


def main() -> None:
    if len(sys.argv) < 2:
        # Summarize all experiments
        if not OUTPUT_DIR.exists():
            print(f"No output directory found at {OUTPUT_DIR}", file=sys.stderr)
            sys.exit(1)
        dirs = sorted(d for d in OUTPUT_DIR.iterdir() if d.is_dir())
        if not dirs:
            print("No experiments found.", file=sys.stderr)
            sys.exit(1)
        for d in dirs:
            csv_path = d / "results_summary.csv"
            if csv_path.exists():
                summary = summarize(d)
                summary_path = d / "summary.txt"
                summary_path.write_text(summary)
            print(_one_liner(d))
        return

    output_dir = Path(sys.argv[1])
    summary = summarize(output_dir)
    print(summary)

    summary_path = output_dir / "summary.txt"
    summary_path.write_text(summary)
    print(f"Written to {summary_path}")


if __name__ == "__main__":
    main()
