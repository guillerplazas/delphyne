"""
Child process of `ladon/reverify.py`: replay proof scripts with the
checker found at `--pristine` (a git worktree of the night's base
commit) and write one verdict per cell.

Deliberately minimal and self-contained: it imports nothing from the
live tree except the standard library, puts the pristine directory
first on `sys.path`, and refuses to run if `pytanque_utils` or
`rocq_server` resolve anywhere else.
"""

# pyright: strict

import argparse
import importlib
import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, cast


class _Timeout(Exception):
    pass


def _alarm(_signum: int, _frame: Any) -> None:
    raise _Timeout()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pristine", required=True)
    ap.add_argument("--jobs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()
    pristine = Path(args.pristine).resolve()
    module_prefix = (
        "runtime." if (pristine / "runtime/pytanque_utils.py").exists() else ""
    )
    if not (
        pristine / (module_prefix.replace(".", "/") + "pytanque_utils.py")
    ).exists():
        print(
            f"no runtime/pytanque_utils.py under {pristine}", file=sys.stderr
        )
        return 2
    sys.path.insert(0, str(pristine))
    os.chdir(pristine)
    # Older frozen night commits use the pre-package layout. In either
    # case both checker modules must resolve inside this pristine tree.
    pt: Any = importlib.import_module(module_prefix + "pytanque_utils")
    rocq_server: Any = importlib.import_module(module_prefix + "rocq_server")

    for mod in (pt, rocq_server):
        f = Path(str(mod.__file__)).resolve()
        if pristine not in f.parents:
            print(
                f"{mod.__name__} resolved outside the pristine tree: {f}",
                file=sys.stderr,
            )
            return 2
    raw: Any = json.loads(Path(args.jobs).read_text())
    jobs = cast(list[dict[str, str]], raw)
    cells: dict[str, dict[str, Any]] = {}
    signal.signal(signal.SIGALRM, _alarm)
    for job in jobs:
        name = job["name"]
        started = time.monotonic()
        info: dict[str, Any] = {"ok": False, "finished": False, "error": None}
        try:
            problem = (pristine / job["problem_file"]).resolve()
            if pristine not in problem.parents or not problem.exists():
                raise ValueError(
                    f"problem file outside the pristine tree: {problem}"
                )
            if (
                problem.stem != job["theorem_name"]
                or job["bench"] != problem.stem
            ):
                raise ValueError(
                    f"theorem/bench mismatch: {problem.stem} vs"
                    f" {job['theorem_name']} / {job['bench']}"
                )
            tactics = pt.split_into_tactics(job["script"])
            if not tactics:
                raise ValueError("empty proof script")
            signal.alarm(int(args.timeout))
            try:
                fb = pt.check(
                    str(problem),
                    job["theorem_name"],
                    tactics,
                    probe_automation=False,
                )
            finally:
                signal.alarm(0)
            info["ok"] = bool(fb.success)
            info["finished"] = bool(fb.finished)
            info["error"] = fb.error_message
            info["remaining_goals"] = len(fb.remaining_goals)
        except _Timeout:
            info["error"] = f"timeout after {args.timeout}s"
        except Exception as e:  # noqa: BLE001 — recorded, never fatal
            info["error"] = f"{type(e).__name__}: {e}"
        info["seconds"] = round(time.monotonic() - started, 1)
        cells[name] = info
        print(
            f"{name}: {'ok' if info['ok'] else 'FAIL'} ({info['seconds']}s) {info['error'] or ''}",
            flush=True,
        )
    doc = {
        "meta": {
            "pristine": str(pristine),
            "pytanque_utils": str(pt.__file__),
            "rocq_server": str(rocq_server.__file__),
            "checked": len(cells),
            "failed": sorted(n for n, i in cells.items() if not i["ok"]),
            "at": time.strftime("%F %T"),
        },
        "cells": cells,
    }
    Path(args.out).write_text(json.dumps(doc, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
