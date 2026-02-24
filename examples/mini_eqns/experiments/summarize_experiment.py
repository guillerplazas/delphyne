#!/usr/bin/env python3
"""
Summarize an experiment's results into a summary.txt file.

Usage:
    python experiments/summarize_experiment.py experiments/output/guided_experiment
"""

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path


def summarize(output_dir: Path) -> str:
    # Read results
    csv_path = output_dir / "results_summary.csv"
    if not csv_path.exists():
        print(f"Error: {csv_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(csv_path, "r") as f:
        rows = list(csv.DictReader(f))

    total = len(rows)
    successes = sum(1 for r in rows if r["success"] == "True")
    total_cost = sum(float(r["price"]) for r in rows)
    avg_cost_per_success = total_cost / successes if successes > 0 else float("inf")

    # Compute wall-clock time from config file modification times
    configs_dir = output_dir / "configs"
    wall_clock = "N/A"
    if configs_dir.exists():
        config_files = list(configs_dir.iterdir())
        if config_files:
            mtimes = [f.stat().st_mtime for f in config_files]
            earliest = min(mtimes)
            latest = max(mtimes)
            duration_s = latest - earliest
            hours, rem = divmod(int(duration_s), 3600)
            minutes, seconds = divmod(rem, 60)
            wall_clock = f"{hours}h {minutes}m {seconds}s ({duration_s:.1f}s)"

    lines = [
        f"Experiment: {output_dir.name}",
        f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Total cost:           ${total_cost:.4f}",
        f"Successes:            {successes}/{total}",
        f"Avg cost per success: ${avg_cost_per_success:.4f}",
        f"Wall-clock time:      {wall_clock}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python summarize_experiment.py <output_dir>", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    summary = summarize(output_dir)
    print(summary)

    summary_path = output_dir / "summary.txt"
    summary_path.write_text(summary)
    print(f"Written to {summary_path}")


if __name__ == "__main__":
    main()
