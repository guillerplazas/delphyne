"""
Stop every running omphalos launch (free the RAM), and say how to resume.

`make stop` (this script's `stop` command) finds the live launchers
through the lock files the launch layer keeps — the machine-wide Rocq
stream slots under `~/.cache/omphalos/slots/` and every
`experiments/output/*/.launch.lock` — sends each launcher SIGINT (the
launch layer forwards it to the attempt's process group and the stdlib
saves the experiment state), waits up to `--grace` seconds, escalates
to a group kill for whatever survives, and finally lists any
`pet-server` or worker still alive. It ends with the exact commands
that resume each stopped launch (recorded in the lock notes), plus the
idempotent `make -j3 ace-x-matrix` that re-queues the whole matrix.

Cost of stopping: the cells that were in flight are lost and re-paid
on resume — at most `max_workers` per launch (the stdlib retry deletes
a config's cache). Completed cells are never touched: statuses are
rebuilt from `result.yaml` files before every attempt.

Only lock files that are actually HELD (flock probe) and whose holder
pid is alive are listed — stale text in a free lock file is ignored.

Usage:
    python -m tools.maintenance.stop_launches list
    python -m tools.maintenance.stop_launches stop [--grace 60] [--dry]
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import os
import signal
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


import experiments.common.omphalos_launch as ol  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT


@dataclass(frozen=True)
class Holder:
    kind: Literal["slot", "launch"]
    path: Path
    pid: int
    dir: str
    cmd: str | None
    cwd: str | None
    at: str
    alive: bool


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _held(path: Path) -> str | None:
    """The lock file's text if it is currently held, else None."""
    fd = ol._try_lock(path, "probe")  # pyright: ignore[reportPrivateUsage]
    if fd is None:
        try:
            return path.read_text()
        except OSError:
            return ""
    os.close(fd)
    return None


def held_locks(max_streams: int | None = None) -> list[Holder]:
    """Every held slot and launch lock, with liveness of its holder."""
    out: list[Holder] = []
    n = max_streams if max_streams is not None else ol.default_max_streams()
    paths: list[tuple[Literal["slot", "launch"], Path]] = [
        ("slot", ol.slot_dir() / f"slot-{i}.lock") for i in range(n)
    ]
    output = _OMPHALOS_DIR / "experiments" / "output"
    if output.exists():
        for d in sorted(output.iterdir()):
            lock = d / ol.LAUNCH_LOCK_NAME
            if lock.exists():
                paths.append(("launch", lock))
    for kind, path in paths:
        if not path.exists():
            continue
        text = _held(path)
        if text is None:
            continue
        h = ol.parse_holder(text)
        try:
            pid = int(h.get("pid", "0"))
        except ValueError:
            pid = 0
        out.append(
            Holder(
                kind=kind,
                path=path,
                pid=pid,
                dir=h.get("dir", "?"),
                cmd=h.get("cmd"),
                cwd=h.get("cwd"),
                at=h.get("at", "?"),
                alive=pid > 0 and _alive(pid),
            )
        )
    return out


def launcher_pids(holders: Sequence[Holder]) -> list[int]:
    seen: list[int] = []
    for h in holders:
        if h.alive and h.pid not in seen:
            seen.append(h.pid)
    return seen


def _children(pid: int) -> list[int]:
    kids: list[int] = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/stat") as f:
                stat = f.read()
        except OSError:
            continue
        fields = stat[stat.rfind(")") + 2 :].split()
        if len(fields) > 1 and int(fields[1]) == pid:
            kids.append(int(entry))
    return kids


def attempt_groups(launcher_pid: int) -> list[int]:
    """Process groups of the launcher's attempt children (session leaders)."""
    groups: list[int] = []
    for kid in _children(launcher_pid):
        try:
            with open(f"/proc/{kid}/stat") as f:
                stat = f.read()
        except OSError:
            continue
        fields = stat[stat.rfind(")") + 2 :].split()
        if len(fields) > 2 and int(fields[2]) == kid:
            groups.append(kid)
    return groups


def survivors() -> list[str]:
    """Rocq servers and pool workers still alive after a stop."""
    out: list[str] = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open(f"/proc/{entry}/cmdline", "rb") as f:
                cmd = f.read().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if "pet-server" in cmd or "experiments/" in cmd and "python" in cmd:
            if int(entry) != os.getpid():
                out.append(f"{entry}: {cmd.strip()[:100]}")
    return out


def resume_commands(holders: Sequence[Holder]) -> list[str]:
    cmds: list[str] = []
    for h in holders:
        if h.kind != "launch" or not h.cmd:
            continue
        cmd = h.cmd
        if " run" in cmd and "--wait" not in cmd:
            cmd += " --wait"
        line = f"cd {h.cwd} && {cmd}" if h.cwd else cmd
        if line not in cmds:
            cmds.append(line)
    return cmds


def describe(holders: Sequence[Holder]) -> list[str]:
    lines: list[str] = []
    for h in holders:
        state = "alive" if h.alive else "DEAD (stale lock)"
        lines.append(
            f"{h.kind:6s} {h.path.name:18s} pid={h.pid} {state} dir={h.dir} "
            f"since {h.at}"
        )
    return lines


def stop(grace_s: float = 60.0, dry: bool = False) -> int:
    holders = held_locks()
    for line in describe(holders):
        print(line)
    pids = launcher_pids(holders)
    if not pids:
        print("no live launch to stop")
        _print_resume(holders)
        return 0
    groups = {pid: attempt_groups(pid) for pid in pids}
    print(f"stopping launcher(s) {pids} (attempt groups {groups})")
    if dry:
        _print_resume(holders)
        return 0
    for pid in pids:
        try:
            os.kill(pid, signal.SIGINT)
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + grace_s
    while time.monotonic() < deadline and any(_alive(p) for p in pids):
        time.sleep(1)
    left = [p for p in pids if _alive(p)]
    if left:
        print(f"escalating: {left} still alive after {grace_s:.0f}s")
        for pid in left:
            for g in groups.get(pid, []):
                ol.kill_group(g)
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        time.sleep(2)
        for pid in left:
            if _alive(pid):
                os.kill(pid, signal.SIGKILL)
    for pid, gs in groups.items():
        for g in gs:
            ol.kill_group(g, grace_s=2.0)
    rest = survivors()
    if rest:
        print("WARNING: survivors:")
        for r in rest:
            print(f"  {r}")
    else:
        print("all launches stopped; no Rocq server or worker survives")
    _print_resume(holders)
    return 1 if rest else 0


def _print_resume(holders: Sequence[Holder]) -> None:
    cmds = resume_commands(holders)
    if cmds:
        print("resume with:")
        for c in cmds:
            print(f"  {c}")
    print("or re-queue everything: make -j3 ace-x-matrix")


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sp = sub.add_parser("stop")
    sp.add_argument("--grace", type=float, default=60.0)
    sp.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    if args.cmd == "list":
        holders = held_locks()
        for line in describe(holders) or ["no held locks"]:
            print(line)
        _print_resume(holders)
        return 0
    return stop(grace_s=float(args.grace), dry=bool(args.dry))


if __name__ == "__main__":
    raise SystemExit(main())
