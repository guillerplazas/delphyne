"""
Offline audit for the runaway-goal treatment (`pytanque_utils.GoalCaps`).

Scans the archived compute calls of one or more runs and reports, per
failed verification, how many goals were left open, how many the
battery probed and how many characters of goal text the feedback
carried — so the treatment's constants (`probe`, `render`,
`render_chars`) are chosen from data, and so the report can say how
many archived cells the caps would have touched (and whether those
cells were solved).

No Rocq, no API: reads `cache.yaml` and `results_summary.csv`.

Usage:
    python tools/goal_cap_audit.py [--run x_validation_agentic ...]
        [--probe 24 --render 12 --render-chars 2000]
"""

# pyright: strict

import argparse
import csv
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytanque_utils as pt  # noqa: E402

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent


@dataclass
class CheckStats:
    config: str
    goals: int
    probed: int
    chars: int
    max_goal_chars: int


def _loader() -> Any:
    return getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def scan_config(config_dir: Path) -> list[CheckStats]:
    cache = config_dir / "cache.yaml"
    if not cache.exists():
        return []
    raw: Any = yaml.load(cache.read_text(), Loader=_loader())
    out: list[CheckStats] = []
    for e in cast(list[dict[str, Any]], raw):
        req = cast(dict[str, Any], e["input"]["request"])
        if cast(dict[str, Any], req.get("options", {})).get("model") != (
            "__compute__"
        ):
            continue
        q = cast(dict[str, Any], yaml.safe_load(req["chat"][0]["content"]))
        if q["fun"] not in ("check", "check_assisted"):
            continue
        outputs = cast(list[dict[str, Any]], e["output"]["outputs"])
        fb = cast(dict[str, Any], yaml.safe_load(outputs[0]["content"]))
        goals = cast(list[str], fb.get("remaining_goals") or [])
        probe = cast(list[Any] | None, fb.get("probe"))
        out.append(
            CheckStats(
                config=config_dir.name,
                goals=len(goals),
                probed=len(probe) if probe is not None else 0,
                chars=sum(len(g) for g in goals),
                max_goal_chars=max((len(g) for g in goals), default=0),
            )
        )
    return out


def _solved(run_dir: Path) -> dict[str, bool]:
    summary = run_dir / "results_summary.csv"
    if not summary.exists():
        return {}
    out: dict[str, bool] = {}
    with summary.open() as f:
        for row in csv.DictReader(f):
            name = (
                f"{row['bench_name']}__{row.get('toolset', 'rich')}-"
                f"{row.get('reasoning_effort', '')}__{row['model_name']}"
                f"__seed{row.get('seed', '0')}"
            )
            out[name] = row.get("success") == "True"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--run", action="append", default=[])
    caps = pt.GoalCaps()
    ap.add_argument("--probe", type=int, default=caps.probe)
    ap.add_argument("--render", type=int, default=caps.render)
    ap.add_argument("--render-chars", type=int, default=caps.render_chars)
    args = ap.parse_args()
    runs = cast(list[str], args.run) or [
        "x_validation_agentic",
        "x_train_agentic",
    ]
    stats: list[CheckStats] = []
    solved: dict[str, bool] = {}
    for run in runs:
        run_dir = _OMPHALOS_DIR / "experiments" / "output" / run
        solved.update(_solved(run_dir))
        for c in sorted((run_dir / "configs").iterdir()):
            stats.extend(scan_config(c))
    if not stats:
        print("no checks found")
        return 1
    failed = [s for s in stats if s.goals > 0]
    goals = sorted(s.goals for s in failed)
    chars = sorted(s.chars for s in failed)

    def pct(v: list[int], p: float) -> int:
        return v[min(len(v) - 1, int(p * len(v)))] if v else 0

    print(
        f"runs: {', '.join(runs)}; {len(stats)} checks, {len(failed)} with open goals"
    )
    print(
        f"open goals per failed check: median {statistics.median(goals):.0f}, "
        f"p90 {pct(goals, 0.9)}, p99 {pct(goals, 0.99)}, max {max(goals)}"
    )
    print(
        f"goal text per feedback: median {statistics.median(chars):.0f} ch, "
        f"p90 {pct(chars, 0.9)}, p99 {pct(chars, 0.99)}, max {max(chars)}"
    )
    print(
        f"battery goal-slots probed in total: {sum(s.probed for s in stats)}"
    )
    touched_probe = {s.config for s in failed if s.goals > int(args.probe)}
    touched_render = {s.config for s in failed if s.goals > int(args.render)}
    touched_chars = {
        s.config for s in failed if s.max_goal_chars > int(args.render_chars)
    }
    touched = touched_probe | touched_render | touched_chars
    n_cells = len({s.config for s in stats})
    print(
        f"\ncaps probe={args.probe} render={args.render} render_chars={args.render_chars}:"
    )
    print(
        f"  cells touched: {len(touched)} of {n_cells} "
        f"(by probe cap {len(touched_probe)}, render cap {len(touched_render)}, "
        f"char cap {len(touched_chars)})"
    )
    solved_touched = sorted(c for c in touched if solved.get(c))
    print(f"  of which archived as SOLVED: {len(solved_touched)}")
    for c in solved_touched:
        print(f"    {c}")
    slots_saved = sum(max(0, s.probed - int(args.probe)) for s in stats)
    print(
        f"  battery goal-slots the probe cap would have skipped: {slots_saved}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
