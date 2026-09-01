"""
Reliable launching of omphalos experiments (a layer over `dp.Experiment`).

Every experiment script used to end in `dp.Experiment(...).run_cli()`;
they now end in `ol.OmphalosExperiment(...).run_cli()` and inherit:

- **one launch per output directory** — an `flock` on
  `<output_dir>/.launch.lock`; a second launch fails fast instead of
  interleaving writes to `experiment.yaml` (observed corruption);
- **machine-wide stream admission** — `max_workers` slots out of
  `OMPHALOS_MAX_STREAMS` (default 4, the memory-bound ceiling of the
  7.4 GB box) held as lock files under `~/.cache/omphalos/slots`; a
  launch that cannot get its slots refuses (or waits with `--wait`);
  locks vanish with the process, so nothing leaks;
- **supervised attempts** — each `resume` runs in a forked child that
  is its own session leader, so the stdlib launcher's pool workers and
  their private Rocq servers share one process group: a broken pool
  (worker OOM, `BrokenProcessPool`, escaping exception) ends the child
  non-zero, the whole group is killed (no orphans racing a relaunch),
  statuses are rebuilt from ground truth and the attempt is retried,
  bounded by `OMPHALOS_RESUME_ATTEMPTS`; Ctrl-C is forwarded to the
  group so the stdlib's own save-on-interrupt path runs;
- **ground-truth statuses** — the stdlib persists statuses only at the
  end of a `resume`, so after a crash `experiment.yaml` lies; before and
  after every attempt statuses are rebuilt from the per-config files
  (`result.yaml` written once at completion ⇒ done; `exception.txt`
  without a result ⇒ failed; else todo). Completed cells are never
  re-paid after a crash;
- **per-worker bounds** — a `WorkersSetup` initializer gives each pool
  worker an address-space limit (`OMPHALOS_WORKER_RLIMIT_AS_MB`), the
  Rocq transport settings, and the in-process Rocq supervisor thread
  (which also exits a worker whose launcher died);
- **lean exports** — `export_browsable_trace` / `export_log` default to
  off (no omphalos tool reads them; the browsable trace forces the
  whole search tree to stay in memory), `export_raw_trace` stays on;
- **one log per attempt** under `experiments/logs/`.

Environment knobs: `OMPHALOS_MAX_STREAMS`, `OMPHALOS_SLOT_DIR`,
`OMPHALOS_WORKER_RLIMIT_AS_MB`, `OMPHALOS_RESUME_ATTEMPTS`, plus the
`OMPHALOS_PET_*` transport settings documented in `rocq_server`.

CLI additions over the stdlib `ExperimentCLI`: `run --wait`, `run
--dry`, `status` (state file vs ground truth, slot table), `rebuild`,
`slots`.
"""

# pyright: strict

from __future__ import annotations

import fcntl
import multiprocessing as mp
import os
import shlex
import signal
import socket
import sys
import time
import traceback
from collections.abc import Generator, Sequence
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, cast

import fire  # type: ignore
import yaml

import delphyne as dp
from delphyne.stdlib.experiments.experiment_launcher import ExperimentCLI

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
if str(_OMPHALOS_DIR) not in sys.path:
    sys.path.insert(0, str(_OMPHALOS_DIR))

LOG_DIR = _OMPHALOS_DIR / "experiments" / "logs"
LAUNCH_LOCK_NAME = ".launch.lock"
RESULT_FILE = "result.yaml"
EXCEPTION_FILE = "exception.txt"
STATE_FILE = "experiment.yaml"
RESULT_HEAD_SCAN = 2 * 2**20
"""Bytes scanned for the top-level `outcome:` key in large results."""

Status = Literal["todo", "done", "failed"]


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    return int(raw) if raw else default


def default_max_streams() -> int:
    return _env_int("OMPHALOS_MAX_STREAMS", 4)


def slot_dir() -> Path:
    raw = os.environ.get("OMPHALOS_SLOT_DIR")
    return (
        Path(raw).expanduser()
        if raw
        else Path.home() / ".cache" / "omphalos" / "slots"
    )


def worker_rlimit_as_mb() -> int:
    return _env_int("OMPHALOS_WORKER_RLIMIT_AS_MB", 4096)


def resume_attempts() -> int:
    return _env_int("OMPHALOS_RESUME_ATTEMPTS", 3)


class LaunchRefused(RuntimeError):
    """A lock or slot could not be acquired; nothing was started."""


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log(msg: str) -> None:
    print(f"[launch {_now()}] {msg}", flush=True)


def original_cmdline() -> list[str]:
    """
    The process's command line as launched. `sys.argv` is not it:
    experiment scripts strip their own flags before `fire` runs.
    """
    try:
        with open("/proc/self/cmdline", "rb") as f:
            parts = f.read().split(b"\0")
        argv = [p.decode(errors="replace") for p in parts if p]
        if argv:
            return argv
    except OSError:
        pass
    return list(getattr(sys, "orig_argv", sys.argv))


def lock_note(output_dir: Path, extra: str = "") -> str:
    """
    What a lock file records about its holder, after `pid= host= at=`:
    the experiment directory, extras, the cwd and — LAST, since it
    contains spaces — the full command line, so `tools/stop_launches.py`
    can print exact resume commands.
    """
    cmd = shlex.join(original_cmdline())
    return (
        f"dir={output_dir.name} {extra} cwd={os.getcwd()} cmd={cmd}".replace(
            "  ", " "
        )
    )


def parse_holder(text: str) -> dict[str, str]:
    """Inverse of the lock-file line: `pid`, `host`, `at`, `dir`, ..., `cmd`."""
    text = text.strip()
    out: dict[str, str] = {}
    head, sep, cmd = text.partition(" cmd=")
    if sep:
        out["cmd"] = cmd
    for tok in head.split():
        k, eq, v = tok.partition("=")
        if eq:
            out[k] = v
    return out


#####
##### Locks
#####


def _holder(path: Path) -> str:
    try:
        return path.read_text().strip() or "unknown"
    except OSError:
        return "unknown"


def _try_lock(path: Path, note: str) -> int | None:
    """Non-blocking exclusive `flock`; returns the fd (kept open) or None."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return None
    os.ftruncate(fd, 0)
    os.write(
        fd,
        f"pid={os.getpid()} host={socket.gethostname()} at={_now()} {note}\n".encode(),
    )
    return fd


@contextmanager
def launch_lock(output_dir: Path) -> Generator[None]:
    """Exclusive launch on `output_dir`; refuses if another launch holds it."""
    path = output_dir / LAUNCH_LOCK_NAME
    fd = _try_lock(path, lock_note(output_dir))
    if fd is None:
        raise LaunchRefused(
            f"another launch holds {path} ({_holder(path)}); refusing to "
            "run two launches on one experiment directory"
        )
    try:
        yield
    finally:
        os.close(fd)


def slot_table(max_streams: int | None = None) -> list[tuple[int, str | None]]:
    """`(slot, holder-or-None)` for every slot (holder = probe by flock)."""
    n = max_streams if max_streams is not None else default_max_streams()
    out: list[tuple[int, str | None]] = []
    for i in range(n):
        path = slot_dir() / f"slot-{i}.lock"
        fd = _try_lock(path, "probe")
        if fd is None:
            out.append((i, _holder(path)))
        else:
            os.close(fd)
            out.append((i, None))
    return out


@contextmanager
def stream_slots(
    n: int, max_streams: int, *, wait: bool, note: str = ""
) -> Generator[list[int]]:
    """
    Hold `n` of the `max_streams` machine-wide slots for the duration.

    Waiting is FIFO with accumulation: a waiter takes a ticket, and
    only the earliest live ticket may acquire; it keeps every slot it
    manages to grab until it has `n` of them. Without this a launch that
    needs 4 slots starves behind chains that re-take single slots
    between steps. Refuses immediately when `wait` is false and fewer
    than `n` slots are free.
    """
    if n > max_streams:
        raise LaunchRefused(
            f"max_workers={n} exceeds OMPHALOS_MAX_STREAMS={max_streams}"
        )
    held: list[tuple[int, int]] = []

    def grab() -> None:
        for i in range(max_streams):
            if len(held) >= n:
                return
            if any(i == j for j, _ in held):
                continue
            fd = _try_lock(slot_dir() / f"slot-{i}.lock", note)
            if fd is not None:
                held.append((i, fd))

    def release() -> None:
        for _, fd in held:
            os.close(fd)
        held.clear()

    # Strict FIFO: a newcomer may only grab immediately when nobody is
    # queued; otherwise it queues behind the earlier waiters even if a
    # slot happens to be free (else single-slot chains starve a
    # four-slot evaluation forever).
    if not _live_tickets():
        grab()
    if len(held) < n and not wait:
        release()
        holders = [f"{i}:{h}" for i, h in slot_table(max_streams) if h]
        raise LaunchRefused(
            f"need {n} Rocq stream slot(s), fewer are free "
            f"(OMPHALOS_MAX_STREAMS={max_streams}); holders: "
            f"{'; '.join(holders) or 'none'}. Use --wait to queue."
        )
    ticket: Path | None = None
    announced = False
    try:
        if len(held) < n:
            ticket = _take_ticket(note)
        while len(held) < n:
            if _is_head(ticket):
                grab()
            else:
                release()  # never hoard behind an earlier waiter
            if len(held) >= n:
                break
            if not announced:
                holders = [f"{i}:{h}" for i, h in slot_table(max_streams) if h]
                _log(
                    f"waiting for {n - len(held)} more slot(s) (queue rank "
                    f"{_rank(ticket)}); holders: {'; '.join(holders)}"
                )
                announced = True
            time.sleep(3)
    finally:
        if ticket is not None:
            ticket.unlink(missing_ok=True)
    try:
        yield [i for i, _ in held]
    finally:
        release()


def _queue_dir() -> Path:
    d = slot_dir() / "queue"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _take_ticket(note: str) -> Path:
    t = _queue_dir() / f"{time.time():017.6f}-{os.getpid()}.ticket"
    t.write_text(note)
    return t


def _live_tickets() -> list[Path]:
    out: list[Path] = []
    for t in sorted(_queue_dir().glob("*.ticket")):
        try:
            pid = int(t.stem.rsplit("-", 1)[1])
        except (IndexError, ValueError):
            t.unlink(missing_ok=True)
            continue
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            t.unlink(missing_ok=True)  # its owner died: drop the ticket
            continue
        except PermissionError:
            pass
        out.append(t)
    return out


def _rank(ticket: Path | None) -> int:
    if ticket is None:
        return 0
    live = _live_tickets()
    return live.index(ticket) if ticket in live else 0


def _is_head(ticket: Path | None) -> bool:
    return ticket is None or _rank(ticket) == 0


#####
##### Worker setup
#####


@dataclass(frozen=True)
class WorkerSetupArgs:
    pet_mode: str
    worker_rlimit_as_mb: int
    omphalos_dir: str


_setup_args: WorkerSetupArgs | None = None


def _worker_common() -> WorkerSetupArgs:
    """Runs in the attempt process; the result is pickled to workers."""
    import rocq_server

    return _setup_args or WorkerSetupArgs(
        pet_mode=rocq_server.pet_mode(),
        worker_rlimit_as_mb=worker_rlimit_as_mb(),
        omphalos_dir=str(_OMPHALOS_DIR),
    )


def _worker_init(args: WorkerSetupArgs) -> None:
    """Pool-worker initializer (top-level: pickled by name)."""
    import resource

    if args.worker_rlimit_as_mb > 0:
        cap = args.worker_rlimit_as_mb * 2**20
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        if hard == resource.RLIM_INFINITY or cap < hard:
            resource.setrlimit(resource.RLIMIT_AS, (cap, hard))
        del soft
    os.environ["OMPHALOS_PET_MODE"] = args.pet_mode
    if args.omphalos_dir not in sys.path:
        sys.path.insert(0, args.omphalos_dir)
    import rocq_server

    rocq_server.MANAGER.start_supervisor_thread(exit_when_orphaned=True)


#####
##### Ground truth
#####


def _yaml_load(path: Path) -> Any:
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    with path.open() as f:
        return yaml.load(f, Loader=loader)  # type: ignore[reportUnknownMemberType]


def _result_is_complete(path: Path) -> bool:
    """
    `result.yaml` is written once, at completion, so its presence
    means "done" — unless a killed worker left it truncated. Small
    files are parsed; large ones (traces) are checked for the closing
    structure to avoid minute-long parses.
    """
    try:
        size = path.stat().st_size
    except OSError:
        return False
    if size == 0:
        return False
    if size <= 4 * 2**20:
        try:
            raw = _yaml_load(path)
        except Exception:
            return False
        return isinstance(raw, dict) and "outcome" in cast(dict[str, Any], raw)
    # Large files: the `args` block precedes `outcome:` and can itself
    # be long (an ACE cell's args carry the rendered playbook, ~10-20
    # KB), so scan a generous head for the top-level key.
    with path.open("rb") as f:
        head = f.read(RESULT_HEAD_SCAN)
    return b"\noutcome:" in head


def ground_truth(config_dir: Path) -> Status:
    if _result_is_complete(config_dir / RESULT_FILE):
        return "done"
    if (config_dir / EXCEPTION_FILE).exists():
        return "failed"
    return "todo"


@dataclass
class StatusDelta:
    changes: dict[str, tuple[str, str]] = field(
        default_factory=dict[str, tuple[str, str]]
    )
    counts: dict[str, int] = field(default_factory=dict[str, int])

    def summary(self) -> str:
        c = self.counts
        base = f"todo={c.get('todo', 0)} done={c.get('done', 0)} failed={c.get('failed', 0)}"
        if not self.changes:
            return base + " (state file matches ground truth)"
        return base + f" ({len(self.changes)} status(es) rebuilt from disk)"


def rebuild_statuses(exp: dp.Experiment[Any], *, write: bool) -> StatusDelta:
    """
    Reconcile `experiment.yaml` with the per-config files. With
    `write`, a timestamped backup is kept next to the state file.
    """
    state = exp._load_state()  # pyright: ignore[reportPrivateUsage]
    delta = StatusDelta()
    if state is None:
        return delta
    out_dir = exp.absolute_output_dir
    for name, info in state.configs.items():
        truth = ground_truth(out_dir / "configs" / name)
        if info.status != truth:
            delta.changes[name] = (info.status, truth)
            info.status = truth
        delta.counts[truth] = delta.counts.get(truth, 0) + 1
    if write and delta.changes:
        state_file = out_dir / STATE_FILE
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = out_dir / f"{STATE_FILE}.bak-{stamp}"
        backup.write_bytes(state_file.read_bytes())
        exp._save_state(state)  # pyright: ignore[reportPrivateUsage]
        for name, (old, new) in delta.changes.items():
            _log(f"status {name}: {old} -> {new}")
    return delta


#####
##### Process-group helpers
#####


def group_members(pgid: int) -> list[int]:
    pids: list[int] = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        pid = int(entry)
        if pid == os.getpid():
            continue
        try:
            with open(f"/proc/{pid}/stat") as f:
                stat = f.read()
        except OSError:
            continue
        # field 5 (after the parenthesised comm) is pgrp
        fields = stat[stat.rfind(")") + 2 :].split()
        # fields: state, ppid, pgrp, ... — zombies are already dead.
        if len(fields) > 2 and int(fields[2]) == pgid and fields[0] != "Z":
            pids.append(pid)
    return pids


def kill_group(pgid: int, *, grace_s: float = 5.0) -> int:
    """SIGTERM then SIGKILL the group; returns the number of survivors."""
    for sig, wait in ((signal.SIGTERM, grace_s), (signal.SIGKILL, 2.0)):
        if not group_members(pgid):
            return 0
        try:
            os.killpg(pgid, sig)
        except ProcessLookupError:
            return 0
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline and group_members(pgid):
            time.sleep(0.1)
    return len(group_members(pgid))


class _Tee:
    def __init__(self, *streams: Any) -> None:
        self._streams = streams

    def write(self, s: str) -> int:
        for st in self._streams:
            st.write(s)
        return len(s)

    def flush(self) -> None:
        for st in self._streams:
            st.flush()

    def isatty(self) -> bool:
        return False


def _raise_interrupt(signum: int, _frame: Any) -> None:
    raise KeyboardInterrupt(f"signal {signum}")


def _install_stop_signals() -> None:
    """
    `make stop` speaks SIGINT/SIGTERM. A launch started as a background
    job from a non-interactive shell inherits SIGINT ignored, so both
    signals are (re)bound to raise `KeyboardInterrupt` in the launcher
    — the path that forwards the stop to the attempt group and lets the
    stdlib save its state.
    """
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _raise_interrupt)
        except (ValueError, OSError):
            pass  # not the main thread: leave the defaults


def _attempt_main(
    exp: dp.Experiment[Any],
    max_workers: int,
    log_progress: bool,
    log_path: str,
) -> None:
    """Body of the supervised child: its own session, stdlib `resume`."""
    os.setsid()
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    log = open(log_path, "a", buffering=1)
    sys.stdout = _Tee(sys.__stdout__, log)  # type: ignore[assignment]
    sys.stderr = _Tee(sys.__stderr__, log)  # type: ignore[assignment]
    rc = 0
    try:
        base = cast(Any, dp.Experiment)
        base.resume(exp, max_workers=max_workers, log_progress=log_progress)
    except BaseException:
        traceback.print_exc()
        rc = 2
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        log.close()
    os._exit(rc)


#####
##### The experiment class
#####


@dataclass(kw_only=True)
class OmphalosExperiment[C: dp.ExperimentConfig](dp.Experiment[C]):
    """`dp.Experiment` with locks, slots, supervised attempts and rebuilds."""

    max_streams: int = field(default_factory=default_max_streams)
    attempts: int = field(default_factory=resume_attempts)
    wait_for_slots: bool = False
    needs_rocq: bool = True
    """Pure-LLM launches (ACE Reflector / Curator / Reducer phases) hold
    no Rocq stream slot: they spawn no prover and cost ~130 MB a worker,
    so they run alongside the Rocq streams instead of queuing behind
    them (the adaptation chain's four phases used to serialise on the
    slot table one after another)."""

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.export_browsable_trace is None:
            self.export_browsable_trace = False
        if self.export_log is None:
            self.export_log = False
        if self.export_raw_trace is None:
            self.export_raw_trace = True
        if self.workers_setup is None:
            self.workers_setup = dp.WorkersSetup(_worker_common, _worker_init)

    # --- statuses --------------------------------------------------------

    def rebuild(self, *, write: bool = True) -> StatusDelta:
        return rebuild_statuses(self, write=write)

    def retry_failed(self) -> int:
        """
        Make every failed cell retryable: its `exception.txt` is set
        aside as a dated `.bak` (the record survives) so the ground
        truth becomes `todo`, then the state is rebuilt. The stdlib's
        `mark_errors_as_todos` alone is undone by the next rebuild.
        Returns the number of cells queued for retry.
        """
        state = self._load_state()  # pyright: ignore[reportPrivateUsage]
        if state is None:
            return 0
        out_dir = self.absolute_output_dir
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        n = 0
        for name in state.configs:
            cfg = out_dir / "configs" / name
            if ground_truth(cfg) != "failed":
                continue
            exc = cfg / EXCEPTION_FILE
            exc.rename(cfg / f"{EXCEPTION_FILE}.bak-{stamp}")
            n += 1
            _log(f"retry {name}: exception set aside")
        self.rebuild(write=True)
        return n

    def _has_todo(self) -> bool:
        return self.get_status()["todo"] > 0

    # --- supervised resume ----------------------------------------------

    def resume(
        self,
        max_workers: int = 1,
        log_progress: bool = True,
        interactive: bool = False,
    ) -> None:
        global _setup_args
        _install_stop_signals()
        if interactive:
            _log(
                "--interactive is not available under the supervised launcher; ignored"
            )
        out_dir = self.absolute_output_dir
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        import rocq_server

        _setup_args = WorkerSetupArgs(
            pet_mode=rocq_server.pet_mode(),
            worker_rlimit_as_mb=worker_rlimit_as_mb(),
            omphalos_dir=str(_OMPHALOS_DIR),
        )
        with ExitStack() as stack:
            stack.enter_context(launch_lock(out_dir))
            # Nothing to run (a cached re-derivation, a finished
            # directory): say so and leave without touching the slots.
            delta = self.rebuild(write=True)
            if not self._has_todo():
                _log(f"{out_dir.name}: nothing to do — {delta.summary()}")
                return
            slots: list[int] = []
            if self.needs_rocq:
                slots = stack.enter_context(
                    stream_slots(
                        max_workers,
                        self.max_streams,
                        wait=self.wait_for_slots,
                        note=lock_note(out_dir, f"workers={max_workers}"),
                    )
                )
            _log(
                f"{out_dir.name}: workers={max_workers} "
                f"slots={slots if self.needs_rocq else 'none (LLM-only)'} "
                f"pet_mode={_setup_args.pet_mode} worker_rlimit={_setup_args.worker_rlimit_as_mb}MB"
            )
            for attempt in range(1, self.attempts + 1):
                if attempt > 1:
                    delta = self.rebuild(write=True)
                _log(f"attempt {attempt}/{self.attempts}: {delta.summary()}")
                if not self._has_todo():
                    break
                rc = self._run_attempt(max_workers, log_progress, attempt)
                if rc == 0:
                    break
                _log(f"attempt {attempt} ended with rc={rc}; cleaning up")
            delta = self.rebuild(write=True)
            _log(f"final: {delta.summary()}")

    def _run_attempt(
        self, max_workers: int, log_progress: bool, attempt: int
    ) -> int:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_path = (
            LOG_DIR / f"{self.absolute_output_dir.name}-{stamp}-a{attempt}.log"
        )
        _log(f"attempt log: {log_path}")
        ctx = mp.get_context("fork")
        child = ctx.Process(
            target=_attempt_main,
            args=(self, max_workers, log_progress, str(log_path)),
        )
        child.start()
        assert child.pid is not None
        pgid = child.pid  # setsid() in the child makes pid == pgid
        try:
            while child.is_alive():
                child.join(1.0)
        except KeyboardInterrupt:
            _log("interrupted: forwarding SIGINT to the attempt (30 s grace)")
            try:
                os.killpg(pgid, signal.SIGINT)
            except ProcessLookupError:
                pass
            deadline = time.monotonic() + 30
            while child.is_alive() and time.monotonic() < deadline:
                try:
                    child.join(1.0)
                except KeyboardInterrupt:
                    break
            survivors = kill_group(pgid)
            _log(f"attempt stopped; {survivors} survivor(s)")
            raise
        finally:
            survivors = kill_group(pgid)
            if survivors:
                _log(
                    f"WARNING: {survivors} process(es) of group {pgid} survived"
                )
        return child.exitcode if child.exitcode is not None else 1

    # --- CLI --------------------------------------------------------------

    def status_lines(self) -> list[str]:
        delta = self.rebuild(write=False)
        lines = [f"Experiment '{self.name}': {delta.summary()}"]
        for name, (old, new) in sorted(delta.changes.items()):
            lines.append(f"  drift {name}: file says {old}, disk says {new}")
        lines.append("Rocq stream slots:")
        for i, holder in slot_table(self.max_streams):
            lines.append(f"  slot {i}: {holder or 'free'}")
        lock = self.absolute_output_dir / LAUNCH_LOCK_NAME
        fd = _try_lock(lock, "probe")
        if fd is None:
            lines.append(f"launch lock: HELD ({_holder(lock)})")
        else:
            os.close(fd)
            lines.append("launch lock: free")
        return lines

    def run_cli(self) -> None:
        fire.Fire(OmphalosCLI(self))  # type: ignore[reportUnknownMemberType]


class OmphalosCLI(ExperimentCLI):
    """The stdlib CLI plus `--wait`, `--dry`, `status`, `rebuild`, `slots`."""

    def __init__(self, experiment: OmphalosExperiment[Any]):
        super().__init__(experiment)
        self.oexp = experiment

    def run(  # type: ignore[override]
        self,
        *,
        max_workers: int = 1,
        retry_errors: bool = False,
        interactive: bool = False,
        wait: bool = False,
        dry: bool = False,
        max_streams: int | None = None,
        log: bool | None = None,
        log_level: str | None = None,
        cache: bool | None = None,
        raw_trace: bool | None = None,
        browsable_trace: bool | None = None,
        verbose_snapshots: bool | None = None,
    ) -> None:
        """
        Start or resume the experiment under the supervised launcher.

        Extra arguments: `wait` queues for stream slots instead of
        refusing; `dry` prints the rebuilt statuses and the slot table
        without running; `max_streams` overrides OMPHALOS_MAX_STREAMS.
        """
        self.oexp.wait_for_slots = wait
        if max_streams is not None:
            self.oexp.max_streams = max_streams
        if dry:
            self.oexp.load()
            for line in self.oexp.status_lines():
                print(line)
            print(f"would run with max_workers={max_workers}")
            return
        if retry_errors:
            self.oexp.load()
            n = self.oexp.retry_failed()
            _log(f"{n} failed cell(s) queued for retry")
        try:
            super().run(
                max_workers=max_workers,
                retry_errors=False,
                interactive=interactive,
                log=log,
                log_level=log_level,
                cache=cache,
                raw_trace=raw_trace,
                browsable_trace=browsable_trace,
                verbose_snapshots=verbose_snapshots,
            )
        except LaunchRefused as e:
            print(f"launch refused: {e}", file=sys.stderr)
            raise SystemExit(3)
        if self.oexp.get_status()["todo"] or self.oexp.get_status()["failed"]:
            raise SystemExit(1)

    def status(self) -> None:  # type: ignore[override]
        """State file vs ground truth, plus slot and lock occupancy."""
        self.oexp.load()
        for line in self.oexp.status_lines():
            print(line)

    def rebuild(self) -> None:
        """Rewrite `experiment.yaml` statuses from the per-config files."""
        self.oexp.load()
        delta = self.oexp.rebuild(write=True)
        print(delta.summary())

    def slots(self) -> None:
        """Print the machine-wide Rocq stream slot table."""
        for i, holder in slot_table(self.oexp.max_streams):
            print(f"slot {i}: {holder or 'free'}")


__all__ = [
    "LaunchRefused",
    "OmphalosCLI",
    "OmphalosExperiment",
    "StatusDelta",
    "ground_truth",
    "group_members",
    "kill_group",
    "launch_lock",
    "lock_note",
    "original_cmdline",
    "parse_holder",
    "rebuild_statuses",
    "slot_table",
    "stream_slots",
]


def configs_of(exp: dp.Experiment[Any]) -> Sequence[Any]:
    """The configs registered on `exp` (empty when none)."""
    return exp.configs or []
