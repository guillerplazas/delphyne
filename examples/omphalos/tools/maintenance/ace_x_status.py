"""
One screen: every X / ACE experiment directory's ground-truth status.

For each directory under `experiments/output/` that belongs to the X
partitions study (baselines, ACE evaluation arms, online chains,
adaptation drivers), reads `experiment.yaml` and classifies every
registered config by what is actually on disk (`omphalos_launch.
ground_truth`: `result.yaml` ⇒ done, `exception.txt` ⇒ failed, else
todo), grouped by arm (playbook sha8 + render version + injection).
Then the launch-lock holder of each directory and the slot table.
Read-only: the state files are not rewritten (`run`/`rebuild` do that).

Usage:
    python -m tools.maintenance.ace_x_status [--all]
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any, cast

import yaml


import experiments.common.omphalos_launch as ol  # noqa: E402
import tools.maintenance.stop_launches as sl  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT

OUTPUT = _OMPHALOS_DIR / "experiments" / "output"
_X_DIRS = re.compile(
    r"^(x_(train|validation|test)_agentic|ace_x_.*_agentic|"
    r"acet_x_.*_agentic|ace_ladon_.*_agentic|ace_triggers_.*|ace_repairs_.*|"
    r"ace_online_.*_agentic|ace_adaptation_x[0-9]?-.*)$"
)


def _arm_of(params: dict[str, Any]) -> str:
    sha = str(params.get("playbook_sha256", ""))[:8]
    if not sha:
        return (
            str(params.get("toolset", "core"))
            + "-"
            + str(params.get("reasoning_effort", ""))
        )
    rv = int(params.get("render_version", 1))
    inj = str(params.get("injection", "full"))
    role = params.get("role")
    tail = f" {role}" if role else ""
    return f"ace-{sha} rv{rv}{'' if inj == 'full' else ' ' + inj}{tail}"


def status_of(run: Path) -> dict[str, Counter[str]]:
    state = run / "experiment.yaml"
    raw: Any = yaml.safe_load(state.read_text()) if state.exists() else None
    state_map = cast(dict[str, Any], raw or {})
    configs = cast(dict[str, dict[str, Any]], state_map.get("configs", {}))
    out: dict[str, Counter[str]] = {}
    adaptation = run.name.startswith("ace_adaptation")
    for name, info in configs.items():
        params = cast(dict[str, Any], info.get("params", {}))
        # Adaptation drivers pin one playbook per step: group by role.
        arm = str(params.get("role", "?")) if adaptation else _arm_of(params)
        truth = ol.ground_truth(run / "configs" / name)
        out.setdefault(arm, Counter())[truth] += 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument(
        "--all", action="store_true", help="every directory, not only X/ACE"
    )
    args = ap.parse_args()
    holders = {h.dir: h for h in sl.held_locks() if h.kind == "launch"}
    for run in sorted(OUTPUT.iterdir()):
        if not run.is_dir() or not (run / "experiment.yaml").exists():
            continue
        if not args.all and not _X_DIRS.match(run.name):
            continue
        arms = status_of(run)
        if not arms:
            continue
        total = sum(sum(c.values()) for c in arms.values())
        lock = holders.get(run.name)
        held = (
            f"  [running: pid {lock.pid} since {lock.at}]"
            if lock and lock.alive
            else ""
        )
        print(f"{run.name} ({total} configs){held}")
        for arm, c in sorted(arms.items()):
            n = sum(c.values())
            print(
                f"    {arm:40s} done {c['done']:3d}  failed {c['failed']:3d}"
                f"  todo {c['todo']:3d}  / {n}"
            )
    print("\nRocq stream slots:")
    for i, holder in ol.slot_table():
        print(f"  slot {i}: {holder.split(' cwd=')[0] if holder else 'free'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
