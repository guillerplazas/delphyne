"""
Running an experiment script on Ladon's behalf.

The orchestrator — never the implement session — pays for cells. It
runs `python experiments/<script>.py run --max_workers=N --wait` as a
subprocess in its own session, so that a kill on deadline can take the
whole launcher group with it (`omphalos_launch.kill_group`), and reads
the outcome from the ground-truth cell counts rather than from the
process's stdout.

Deadlines come from the archived baseline: the expected wall-clock of
an arm is the baseline's own per-cell durations on the same cells,
packed onto `max_workers` streams, times a slack factor; the kill fires
at twice that (the autoresearch 2× margin). The floor of 45 minutes
keeps a tiny arm from being killed by its own start-up.

Exit codes of the launcher (`omphalos_launch.OmphalosCLI.run`): 0 =
every cell done, 1 = todo/failed cells remain after the attempts, 3 =
launch refused (no free stream slots without `--wait`), 130 =
interrupted. `LADON_SEEDS` selects the seeds an arm script registers
(`ladon/prompts/arm_template.py.txt`), which is how the screen tier
(seed 0) and the select tier (seeds 0,1) share one output directory:
the stdlib launcher adds new configs as `todo` and skips done cells.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import yaml


import experiments.common.omphalos_launch as ol  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT

MIN_EXPECTED_S = 45 * 60.0
SLACK = 1.3
KILL_FACTOR = 2.0
SIGINT_GRACE_S = 90.0
POLL_S = 30.0
FALLBACK_CELL_S = 150.0
"""Per-cell wall-clock assumed when the baseline has no matching cell."""


@dataclass(frozen=True)
class Counts:
    done: int
    failed: int
    todo: int

    @property
    def total(self) -> int:
        return self.done + self.failed + self.todo

    @property
    def complete(self) -> bool:
        return self.todo == 0 and self.failed == 0 and self.done > 0

    def __str__(self) -> str:
        return f"{self.done} done, {self.failed} failed, {self.todo} todo"


@dataclass(frozen=True)
class LaunchResult:
    rc: int | None
    timed_out: bool
    wall_s: float
    counts: Counts
    log: Path

    @property
    def interrupted(self) -> bool:
        return self.rc in (130, -2, -15)


def _to_seconds(v: Any) -> float | None:
    if isinstance(v, datetime):
        return v.timestamp()
    if isinstance(v, str) and v.strip():
        try:
            return datetime.fromisoformat(v.strip()).timestamp()
        except ValueError:
            return None
    return None


def _state_configs(run_dir: Path) -> dict[str, dict[str, Any]]:
    state = run_dir / ol.STATE_FILE
    if not state.exists():
        return {}
    raw: Any = yaml.safe_load(state.read_text())
    state_map = cast(dict[str, Any], raw or {})
    return cast(dict[str, dict[str, Any]], state_map.get("configs", {}))


def cell_seconds(run_dir: Path) -> dict[tuple[str, str], float]:
    """Per (bench, seed) wall-clock of the cells recorded in a run."""
    out: dict[tuple[str, str], float] = {}
    for info in _state_configs(run_dir).values():
        params = cast(dict[str, Any], info.get("params", {}))
        start = _to_seconds(info.get("start_time"))
        end = _to_seconds(info.get("end_time"))
        if start is None or end is None or end < start:
            continue
        key = (str(params.get("bench_name", "")), str(params.get("seed", "")))
        out[key] = end - start
    return out


def expected_seconds(
    baseline_dir: Path,
    cells: Iterable[tuple[str, str]],
    max_workers: int,
) -> float:
    secs = cell_seconds(baseline_dir)
    picked = [secs.get(c, FALLBACK_CELL_S) for c in cells]
    if not picked:
        return MIN_EXPECTED_S
    est = max(sum(picked) / max(1, max_workers), max(picked)) * SLACK
    return max(est, MIN_EXPECTED_S)


def prune_todo_seeds(run_dir: Path, seeds: Sequence[int]) -> int:
    """
    Drop `todo` entries whose seed is not in `seeds` from the state file.

    A `status` or `--dry` run of an arm script without `LADON_SEEDS`
    registers every cell of the full arm as todo (seen on 2026-09-04,
    hint 64: the screen tier then ran both seeds). Only entries with no
    cell on disk are removed; done and failed cells are never touched.
    """
    state = run_dir / ol.STATE_FILE
    if not state.exists():
        return 0
    raw: Any = yaml.safe_load(state.read_text())
    doc = cast(dict[str, Any], raw or {})
    configs = cast(dict[str, dict[str, Any]], doc.get("configs", {}))
    keep = {str(s) for s in seeds}
    drop = [
        name
        for name, info in configs.items()
        if str(cast(dict[str, Any], info.get("params", {})).get("seed", ""))
        not in keep
        and ol.ground_truth(run_dir / "configs" / name) == "todo"
    ]
    for name in drop:
        del configs[name]
    if drop:
        tmp = state.with_suffix(".yaml.tmp")
        tmp.write_text(yaml.safe_dump(doc, sort_keys=False))
        os.replace(tmp, state)
    return len(drop)


def counts(run_dir: Path) -> Counts:
    done = failed = todo = 0
    for name in _state_configs(run_dir):
        truth = ol.ground_truth(run_dir / "configs" / name)
        if truth == "done":
            done += 1
        elif truth == "failed":
            failed += 1
        else:
            todo += 1
    return Counts(done, failed, todo)


def run_script(
    script: Path,
    args: Sequence[str],
    *,
    env: Mapping[str, str],
    log: Path,
    timeout_s: float,
    run_dir: Path,
    poll_s: float = POLL_S,
    tick: Callable[[float, Counts], None] | None = None,
) -> LaunchResult:
    """
    Run `python script *args` detached in its own session, appending
    stdout+stderr to `log`; kill the group at `timeout_s`.
    """
    log.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    timed_out = False
    with log.open("ab") as out:
        out.write(
            f"\n[ladon] {datetime.now():%Y-%m-%d %H:%M:%S} run {script.name}"
            f" {' '.join(args)} (deadline {timeout_s / 60:.0f} min)\n".encode()
        )
        out.flush()
        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                script.relative_to(_OMPHALOS_DIR)
                .with_suffix("")
                .as_posix()
                .replace("/", "."),
                *args,
            ],
            cwd=_OMPHALOS_DIR,
            env=dict(env),
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        last_tick = started
        try:
            while proc.poll() is None:
                now = time.monotonic()
                if now - started > timeout_s:
                    timed_out = True
                    _stop(proc)
                    break
                if tick is not None and now - last_tick >= poll_s:
                    tick(now - started, counts(run_dir))
                    last_tick = now
                time.sleep(min(poll_s, 5.0))
        except KeyboardInterrupt:
            # Ladon itself was told to stop: take the launcher down too.
            _stop(proc)
            raise
        rc = proc.poll()
    return LaunchResult(
        rc=rc,
        timed_out=timed_out,
        wall_s=time.monotonic() - started,
        counts=counts(run_dir),
        log=log,
    )


def _stop(proc: subprocess.Popen[bytes]) -> None:
    """SIGINT (the launcher rebinds it to a clean stop), then the group."""
    try:
        proc.send_signal(signal.SIGINT)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + SIGINT_GRACE_S
    while time.monotonic() < deadline and proc.poll() is None:
        time.sleep(1)
    if proc.poll() is None:
        ol.kill_group(proc.pid)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def launch_env(
    base: Mapping[str, str], *, seeds: Sequence[int], smoke: bool = False
) -> dict[str, str]:
    env = dict(base)
    env["LADON_SEEDS"] = ",".join(str(s) for s in seeds)
    if smoke:
        env["LADON_SMOKE"] = "1"
    else:
        env.pop("LADON_SMOKE", None)
    return env


def launch_arm(
    script: Path,
    *,
    run_dir: Path,
    seeds: Sequence[int],
    max_workers: int,
    timeout_s: float,
    log: Path,
    env: Mapping[str, str] | None = None,
    retry_errors: bool = False,
    tick: Callable[[float, Counts], None] | None = None,
) -> LaunchResult:
    args = ["run", f"--max_workers={max_workers}", "--wait"]
    if retry_errors:
        args.append("--retry_errors")
    return run_script(
        script,
        args,
        env=launch_env(env if env is not None else os.environ, seeds=seeds),
        log=log,
        timeout_s=timeout_s,
        run_dir=run_dir,
        tick=tick,
    )


def rebuild(script: Path, *, env: Mapping[str, str] | None = None) -> int:
    """`python script rebuild` — statuses from the per-config files."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            script.relative_to(_OMPHALOS_DIR)
            .with_suffix("")
            .as_posix()
            .replace("/", "."),
            "rebuild",
        ],
        cwd=_OMPHALOS_DIR,
        env=dict(env if env is not None else os.environ),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    return proc.returncode
