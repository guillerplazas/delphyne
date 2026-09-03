"""
Re-verification of an arm's claimed solves by pristine code.

A hint may legitimately touch the verifier, the bridge or the strategy
(class B/C work on `pytanque_utils.py` is exactly what HINTS #64
asks for) — and a hint that weakens the checker would manufacture
solves the paired test cannot tell from real ones. So before a
verdict, every proof script the arm recorded as a success is replayed
by the checker of the night's base commit, checked out in a separate
git worktree, with the automation battery off (`probe_automation=
False`, the strictest form): a solve counts only if `Qed` passes there.

The worktree is hermetic because `pytanque_utils` and `rocq_server`
anchor every path on their own `__file__` (the augmented problem
files, the Rocq cache, the pet-server cwd). The check runs in a child
process (`ladon/reverify_worker.py`) whose `sys.path[0]` is the
pristine tree, under one machine-wide Rocq stream slot so it queues
behind launches like any other Rocq consumer.
"""

# pyright: strict

import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
for _sub in ("", "experiments"):
    _p = str(_OMPHALOS_DIR / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import omphalos_launch as ol  # noqa: E402

from ladon import guard  # noqa: E402

PRISTINE_ROOT = Path(
    os.environ.get("LADON_PRISTINE_ROOT", "~/.cache/omphalos/ladon")
).expanduser()
WORKER = Path(__file__).resolve().parent / "reverify_worker.py"
PER_CELL_TIMEOUT_S = 15 * 60
RESULT_HEAD = 2 * 2**20
_RAW_TRACE_RE = re.compile(r"^\s*raw_trace:")


def worktree_path(sha: str) -> Path:
    return PRISTINE_ROOT / f"pristine-{sha[:8]}"


def ensure_worktree(sha: str) -> Path:
    """Check `sha` out as a detached worktree (idempotent)."""
    path = worktree_path(sha)
    guard.git("worktree", "prune")
    if path.exists():
        have = guard.git("rev-parse", "HEAD", cwd=path).strip()
        if have == sha:
            return path
        guard.git("worktree", "remove", "--force", str(path), check=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    guard.git("worktree", "add", "--detach", str(path), sha)
    assert guard.git("rev-parse", "HEAD", cwd=path).strip() == sha
    return path


def remove_worktree(path: Path) -> None:
    if path.exists():
        guard.git("worktree", "remove", "--force", str(path), check=False)
    guard.git("worktree", "prune", check=False)


def _result_prefix(path: Path) -> dict[str, Any]:
    """
    The result document up to its `raw_trace` field, read line by line
    the way the stdlib's `_results_summary` does (files are megabytes).
    """
    prefix: list[str] = []
    size = 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        while line := f.readline():
            if _RAW_TRACE_RE.match(line):
                break
            prefix.append(line)
            size += len(line)
            if size > RESULT_HEAD:
                break
    raw: Any = yaml.safe_load("".join(prefix))
    return cast(dict[str, Any], raw or {})


@dataclass(frozen=True)
class Job:
    name: str
    bench: str
    problem_file: str
    theorem_name: str
    script: str

    def as_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "bench": self.bench,
            "problem_file": self.problem_file,
            "theorem_name": self.theorem_name,
            "script": self.script,
        }


def jobs_for(arm_dir: Path) -> list[Job]:
    """One job per solved cell: the recorded problem and proof script."""
    jobs: list[Job] = []
    configs = arm_dir / "configs"
    if not configs.exists():
        return jobs
    for cfg in sorted(configs.iterdir()):
        result = cfg / ol.RESULT_FILE
        if ol.ground_truth(cfg) != "done":
            continue
        doc = _result_prefix(result)
        outcome = cast(dict[str, Any], doc.get("outcome") or {})
        res = cast(dict[str, Any], outcome.get("result") or {})
        if not res.get("success"):
            continue
        values = cast(list[Any], res.get("values") or [])
        args = cast(dict[str, Any], doc.get("args") or {})
        inner = cast(dict[str, Any], args.get("args") or {})
        script = str(values[0]) if values else ""
        jobs.append(
            Job(
                name=cfg.name,
                bench=cfg.name.split("__", 1)[0],
                problem_file=str(inner.get("problem_file", "")),
                theorem_name=str(inner.get("theorem_name", "")),
                script=script,
            )
        )
    return jobs


@dataclass(frozen=True)
class ReverifyReport:
    checked: int
    failed: tuple[str, ...]
    verified: dict[str, bool]
    meta: dict[str, Any]

    @property
    def ok(self) -> bool:
        return not self.failed


def reverify(
    arm_dir: Path,
    pristine: Path,
    *,
    out: Path,
    log: Path,
    env: Mapping[str, str] | None = None,
    per_cell_timeout_s: int = PER_CELL_TIMEOUT_S,
    hold_slot: bool = True,
) -> ReverifyReport:
    jobs = jobs_for(arm_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    jobs_path = out.with_name(out.stem + "_jobs.json")
    jobs_path.write_text(json.dumps([j.as_dict() for j in jobs], indent=1))
    pristine_omphalos = pristine / "examples" / "omphalos"
    child_env = dict(env if env is not None else os.environ)
    child_env.update(
        {"OMPHALOS_PET_MODE": "socket", "OMPHALOS_CHECK_MEMO": "0"}
    )
    cmd = [
        sys.executable,
        str(WORKER),
        "--pristine",
        str(pristine_omphalos),
        "--jobs",
        str(jobs_path),
        "--out",
        str(out),
        "--timeout",
        str(per_cell_timeout_s),
    ]
    log.parent.mkdir(parents=True, exist_ok=True)

    def run_worker() -> int:
        with log.open("ab") as lf:
            lf.write(
                f"\n[ladon] reverify {arm_dir.name} at {time.strftime('%F %T')}\n".encode()
            )
            lf.flush()
            return subprocess.run(
                cmd,
                cwd=pristine_omphalos,
                env=child_env,
                stdin=subprocess.DEVNULL,
                stdout=lf,
                stderr=subprocess.STDOUT,
            ).returncode

    if jobs:
        if hold_slot:
            note = ol.lock_note(arm_dir, "ladon-reverify")
            with ol.stream_slots(
                1, ol.default_max_streams(), wait=True, note=note
            ):
                rc = run_worker()
        else:
            rc = run_worker()
        if rc != 0 or not out.exists():
            raise RuntimeError(f"reverify worker failed (rc={rc}); see {log}")
        raw: Any = json.loads(out.read_text())
        doc = cast(dict[str, Any], raw)
    else:
        doc = {"cells": {}, "meta": {"pristine": str(pristine_omphalos)}}
        out.write_text(json.dumps(doc, indent=1))
    cells = cast(dict[str, dict[str, Any]], doc.get("cells", {}))
    verified = {name: bool(info.get("ok")) for name, info in cells.items()}
    failed = tuple(sorted(n for n, ok in verified.items() if not ok))
    return ReverifyReport(
        checked=len(verified),
        failed=failed,
        verified=verified,
        meta=cast(dict[str, Any], doc.get("meta", {})),
    )
