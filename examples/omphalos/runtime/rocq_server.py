"""
Transport and lifecycle for the Rocq (petanque) bridge.

`pytanque_utils` decides *what* to ask Rocq; this module decides *how*
the question travels and keeps the prover process alive, bounded and
private. Pure Python, no Delphyne imports.

Design (2026-08-26, measured before adoption — numbers in PROGRESS):

- One private `pet-server` per Python process, spawned lazily on a
  free port and never shared: two concurrent sessions on one server
  corrupt each other's environments (probed 2026-08-25), and forked
  pool workers must not inherit their parent's server (owner-pid
  guard + `os.register_at_fork`).
- Problem files are elaborated from a *stable* path per (file, extra
  imports): petanque keys its document table by URI, so a stable URI
  turns `start` from ~500 ms (fresh document per call) into ~2 ms and
  keeps the server's memory flat. The random temp copy of the previous
  implementation defeated the warm cache and leaked ~50 MB per call.
- Every RPC carries a transport deadline (the library blocks forever
  on `start`/`goals` and, in STDIO mode, on everything), every reply
  is size-capped (the library accumulates fragments without bound —
  34 archived `MemoryError`s), and the server runs under an address
  space limit so a ballooning tactic dies as a Rocq error instead of
  a kernel OOM sweep that breaks the experiment pool.
- The server is recycled between sessions when it died, when the
  problem file changes (once per experiment cell), when its RSS
  exceeds a budget, or after too many sessions: petanque never frees
  proof states, so a long-lived server only grows.
- Any transport failure poisons the session, recycles the server (it
  may still be computing) and surfaces as a `PetanqueError` subclass,
  so the tools render feedback and the cell continues.
- `OMPHALOS_PET_MODE=stdio` restores the archived transport (one
  fresh `pet` per session) for parity runs. If the server cannot be
  brought up, the session falls back to STDIO loudly (logged, counted).
"""

from __future__ import annotations

from runtime.paths import OMPHALOS_ROOT

import atexit
import functools
import hashlib
import json
import logging
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from collections import Counter
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal, cast

from pytanque import PetanqueError, Pytanque, PytanqueMode
from pytanque.client import PETANQUE_ROUTES, Failure, Response, mk_request
from pytanque.routes import RouteName

import runtime.tool_budget as tb

_WORKSPACE_ROOT = OMPHALOS_ROOT
ROCQ_CACHE_DIR = _WORKSPACE_ROOT / ".rocq_cache"
"""cwd of every Rocq process: micromega writes `.lia.cache` etc. here."""
AUG_DIR = ROCQ_CACHE_DIR / "aug"
"""Stable augmented problem files, one directory per content digest."""
LOG_DIR = ROCQ_CACHE_DIR / "logs"

_log = logging.getLogger("omphalos.rocq")

PetMode = Literal["socket", "stdio"]


def pet_mode() -> PetMode:
    """
    Transport selected by `OMPHALOS_PET_MODE`, read at call time so a
    worker initializer can set it after import. Default: `socket`.
    """
    raw = os.environ.get("OMPHALOS_PET_MODE", "socket").strip().lower()
    if raw not in ("socket", "stdio"):
        raise ValueError(
            f"OMPHALOS_PET_MODE={raw!r}: expected 'socket' or 'stdio'"
        )
    return raw  # type: ignore[return-value]


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    return int(raw) if raw else default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    return float(raw) if raw else default


@dataclass(frozen=True)
class Settings:
    """
    Bounds for the private server. Every field has an environment
    override (`OMPHALOS_PET_*`) so launches can tune them without code
    changes; `configure` sets them programmatically.
    """

    rpc_deadline_s: float = 60.0
    """Socket deadline for RPCs that carry no Rocq `Timeout` (start, goals)."""
    rpc_margin_s: float = 15.0
    """Added to a `run` call's Rocq `Timeout` so Rocq's own (clean) timeout
    fires first; the socket deadline is the backstop for tactics that do
    not poll for interrupts."""
    reply_cap_bytes: int = 16 * 2**20
    """Largest reply accepted; beyond it the server is recycled."""
    server_rlimit_as_mb: int = 3072
    """Address-space limit of the server process (`prlimit --as`)."""
    server_max_rss_mb: int = 1536
    """Recycle the server between sessions above this resident size."""
    server_max_sessions: int = 5000
    spawn_timeout_s: float = 15.0
    supervisor_period_s: float = 15.0
    session_max_s: float = 1800.0
    """Supervisor kills a server held by one session longer than this."""
    memory_floor_mb: int = 768
    """Machine-wide floor on `MemAvailable`: below it, a server that has
    grown past `memory_floor_hog_mb` recycles itself — a recorded
    transport failure for that one cell instead of a kernel OOM kill of
    a random process (measured 2026-08-26: three servers at 1.9 GB each
    were OOM-killed under four streams on the 7.4 GB box)."""
    memory_floor_hog_mb: int = 1024

    @staticmethod
    def from_env() -> Settings:
        base = Settings()
        return Settings(
            rpc_deadline_s=_env_float(
                "OMPHALOS_PET_RPC_DEADLINE_S", base.rpc_deadline_s
            ),
            rpc_margin_s=_env_float(
                "OMPHALOS_PET_RPC_MARGIN_S", base.rpc_margin_s
            ),
            reply_cap_bytes=_env_int(
                "OMPHALOS_PET_REPLY_CAP_MB", base.reply_cap_bytes // 2**20
            )
            * 2**20,
            server_rlimit_as_mb=_env_int(
                "OMPHALOS_PET_RLIMIT_AS_MB", base.server_rlimit_as_mb
            ),
            server_max_rss_mb=_env_int(
                "OMPHALOS_PET_MAX_RSS_MB", base.server_max_rss_mb
            ),
            server_max_sessions=_env_int(
                "OMPHALOS_PET_MAX_SESSIONS", base.server_max_sessions
            ),
            spawn_timeout_s=_env_float(
                "OMPHALOS_PET_SPAWN_TIMEOUT_S", base.spawn_timeout_s
            ),
            supervisor_period_s=_env_float(
                "OMPHALOS_PET_SUPERVISOR_PERIOD_S", base.supervisor_period_s
            ),
            session_max_s=_env_float(
                "OMPHALOS_PET_SESSION_MAX_S", base.session_max_s
            ),
            memory_floor_mb=_env_int(
                "OMPHALOS_MEM_FLOOR_MB", base.memory_floor_mb
            ),
            memory_floor_hog_mb=_env_int(
                "OMPHALOS_MEM_FLOOR_HOG_MB", base.memory_floor_hog_mb
            ),
        )


#####
##### Errors
#####


class TransportError(PetanqueError):
    """
    A failure of the *channel* to Rocq rather than of Rocq itself. A
    `PetanqueError` subclass so every existing `except PetanqueError`
    in the bridge renders it as tool feedback.
    """

    code: int = -33000

    def __init__(self, message: str):
        super().__init__(self.code, message)  # type: ignore[reportUnknownMemberType]
        self.message = message

    def __str__(self) -> str:
        return f"({self.code}, {self.message!r})"


class Deadline(TransportError):
    code = -33000


class ReplyTooLarge(TransportError):
    code = -33001


class ConnectionLost(TransportError):
    code = -33002


class ServerUnavailable(TransportError):
    code = -33003


TRANSPORT_FAILURE_TEXT = (
    "Rocq transport failure ({kind}): the prover server was restarted "
    "and this attempt has no verdict. Try again with a cheaper tactic "
    "or a smaller proof state."
)


#####
##### Bounded client
#####


class BoundedPytanque(Pytanque):
    """
    Socket-mode `Pytanque` with a byte cap on replies and a deadline
    on every RPC. Any transport failure poisons the client (it must
    not be reused: the server may still be computing the old request)
    and is reported to `on_failure` before being raised.
    """

    def __init__(
        self,
        host: str,
        port: int,
        *,
        settings: Settings,
        on_failure: Callable[[str], None],
    ) -> None:
        super().__init__(host, port, mode=PytanqueMode.SOCKET)  # type: ignore[reportUnknownMemberType]
        self.poisoned = False
        self._settings = settings
        self._on_failure = on_failure

    def _fail(self, kind: str) -> None:
        if not self.poisoned:
            self.poisoned = True
            self._on_failure(kind)

    def _read_socket_response(self, size: int) -> str:  # type: ignore[override]
        cap = self._settings.reply_cap_bytes
        chunks: list[bytes] = []
        total = 0
        sock = cast(socket.socket, self.socket)  # type: ignore[reportUnknownMemberType]
        rpc_end = (
            time.monotonic()
            + (sock.gettimeout() or self._settings.rpc_deadline_s)
            if tb.CURRENT.get() is not None
            else None
        )
        while True:
            if rpc_end is not None:
                left = rpc_end - time.monotonic()
                if left <= 0:
                    raise TimeoutError("RPC deadline across receives")
                sock.settimeout(tb.clamp_timeout(left))
            chunk = sock.recv(size)
            if not chunk:
                raise ConnectionLost("the Rocq server closed the connection")
            chunks.append(chunk)
            total += len(chunk)
            if total > cap:
                raise ReplyTooLarge(
                    f"reply exceeded {cap // 2**20} MiB "
                    "(goal state too large to transfer)"
                )
            if chunk.endswith(b"\n"):
                break
        # Decoding the joined bytes (instead of each fragment) is a
        # strict fix: a multibyte character straddling two fragments was
        # silently dropped by the library's per-fragment decode.
        return b"".join(chunks).decode(errors="ignore")

    def _query_unlogged(
        self,
        route_name: Any,
        params: Any,
        size: int,
        timeout: float | None,
    ) -> Any:
        """
        `Pytanque.query`, socket branch, minus its two `logger.info`
        f-strings: the library formats the full payload and the full
        raw reply *eagerly* — with no handler configured that is pure
        string copying, tens of MB for a reply near the cap, on every
        RPC. Behaviour is otherwise byte-identical (same requests, same
        replies, same errors); `tests/test_rocq_server.py` pins it
        against the parent implementation.
        """
        if self.mode != PytanqueMode.SOCKET:  # pragma: no cover
            return super().query(  # type: ignore[reportUnknownMemberType]
                route_name, params, size=size, timeout=timeout
            )
        self.id += 1
        request = mk_request(  # type: ignore[reportUnknownMemberType]
            self.id, params, route_name, project_state=True
        )
        payload = request.to_json()  # type: ignore[reportUnknownMemberType]
        sock = cast(socket.socket, self.socket)  # type: ignore[reportUnknownMemberType]
        sock.settimeout(timeout)
        try:
            data = json.dumps(payload) + "\n"
            sock.sendall(data.encode())
            raw = self._read_socket_response(size)
        except TimeoutError:
            raise PetanqueError(-33000, f"Timeout on {self.id}")  # type: ignore[reportUnknownMemberType]
        try:
            resp = cast(Any, Response).from_json_string(raw)
            if resp.id != self.id:
                raise PetanqueError(  # type: ignore[reportUnknownMemberType]
                    -32603, f"Sent request {self.id}, got response {resp.id}"
                )
            if not resp.result and resp.result is not False:
                return None
            response_cls = PETANQUE_ROUTES[route_name].response_cls  # type: ignore[reportUnknownMemberType]
            return response_cls.from_json(resp.result)
        except ValueError:
            failure = cast(Any, Failure).from_json_string(raw)
            raise PetanqueError(  # type: ignore[reportUnknownMemberType]
                failure.error.code, failure.error.message
            )

    def query(  # type: ignore[override]
        self,
        route_name: Any,
        params: Any,
        size: int = 65536,
        timeout: float | None = None,
    ) -> Any:
        if self.poisoned:
            raise ConnectionLost("session poisoned by an earlier failure")
        s = self._settings
        if timeout is None:
            deadline = s.rpc_deadline_s
        elif route_name == RouteName.RUN:
            # `run(timeout=t)` wraps the command in Rocq's `Timeout t`;
            # give Rocq the chance to report it cleanly first.
            deadline = timeout + s.rpc_margin_s
        else:
            deadline = timeout
        op = tb.CURRENT.get()
        if op is not None:
            deadline = op.admit_rpc(deadline)
        try:
            return self._query_unlogged(
                route_name, params, size=size, timeout=deadline
            )
        except tb.OperationExhausted:
            self._fail("OperationBudget")
            raise
        except TransportError as e:
            self._fail(type(e).__name__)
            raise
        except PetanqueError as e:
            if getattr(e, "code", None) == -33000:
                # pytanque's own socket-timeout mapping.
                self._fail("Deadline")
                raise Deadline(
                    f"no reply from the Rocq server within {deadline:.0f}s"
                ) from e
            raise
        except (OSError, ValueError, KeyError, AttributeError) as e:
            # OSError: socket errors; the others: pytanque failing to
            # parse a truncated reply after the peer vanished.
            self._fail("ConnectionLost")
            raise ConnectionLost(f"{type(e).__name__}: {e}") from e


#####
##### Stable augmented files
#####

_AUG_MEMO: dict[tuple[str, tuple[str, ...], int, int], str] = {}
"""`(src, extra_imports, src size, src mtime_ns)` -> verified dst path.
The bridge calls `augmented_path` on *every* tool call; without the
memo each call re-reads the source and the destination and re-hashes
the content. Keyed by the source's stat so an edited problem file
invalidates naturally (benchmark files are frozen in practice)."""


def augmented_path(file: str, extra_imports: tuple[str, ...]) -> str:
    """
    The path pytanque is pointed at for `file` with `extra_imports`
    prepended: a copy under `AUG_DIR/<digest>/<name>`, byte-identical
    to the temp copy the previous implementation wrote (same preamble,
    same line numbers, same error messages), but *stable*: the same
    inputs map to the same path, so a warm server reuses its document.

    Written atomically (`os.replace`) and only when missing or stale;
    concurrent workers converge on identical bytes. Lives outside the
    miniF2F `_CoqProject` tree, which petanque restricts theorem lookup
    to. Never unlinked (488 problems, ~1 MB in total).
    """
    src = Path(file).resolve()
    if not extra_imports:
        return str(src)
    try:
        st = src.stat()
        memo_key = (str(src), extra_imports, st.st_size, st.st_mtime_ns)
    except OSError:
        memo_key = None
    if memo_key is not None:
        hit = _AUG_MEMO.get(memo_key)
        if hit is not None and Path(hit).exists():
            return hit
    body = src.read_bytes()
    content = ("\n".join(extra_imports) + "\n").encode() + body
    digest = hashlib.sha256(str(src).encode() + b"\0" + content).hexdigest()
    dst = AUG_DIR / digest[:16] / src.name
    try:
        if dst.read_bytes() == content:
            if memo_key is not None:
                _AUG_MEMO[memo_key] = str(dst)
            return str(dst)
    except OSError:
        pass
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(
        f".{dst.name}.{os.getpid()}.{threading.get_ident()}.tmp"
    )
    tmp.write_bytes(content)
    os.replace(tmp, dst)
    if memo_key is not None:
        _AUG_MEMO[memo_key] = str(dst)
    return str(dst)


#####
##### Server manager
#####


@dataclass
class _Server:
    proc: subprocess.Popen[bytes]
    port: int
    owner_pid: int
    generation: int
    started_at: float
    log_path: Path
    sessions: int = 0
    current_file: str | None = None
    in_session_since: float | None = None


@dataclass(frozen=True)
class ServerStats:
    mode: PetMode
    generation: int
    alive: bool
    pid: int | None
    sessions: int
    rss_mb: float | None
    recycles: dict[str, int]
    fallbacks: int


@functools.cache
def _which(name: str) -> str | None:
    """`shutil.which`, cached: `_spawn` used to re-scan PATH per spawn."""
    return shutil.which(name)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def mem_available_mb() -> float | None:
    """`MemAvailable` from /proc/meminfo, in MB (None off Linux)."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / 1024
    except OSError:
        return None
    return None


def _rss_mb(pid: int) -> float | None:
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024
    except OSError:
        return None
    return None


class PetServerManager:
    """
    Owner of this process's private `pet-server`. `session()` is the
    only entry point the bridge uses; everything else is lifecycle.
    """

    def __init__(self) -> None:
        self.settings = Settings.from_env()
        self._state_lock = threading.Lock()  # server handle mutations
        self._session_lock = threading.RLock()  # sessions are sequential
        self._server: _Server | None = None
        self._generation = 0
        self._pending_recycle: str | None = None
        self._supervisor: threading.Thread | None = None
        self._exit_when_orphaned = False
        self._warned_fallback = False
        self._fallbacks = 0
        self.recycles: Counter[str] = Counter()

    # --- introspection -------------------------------------------------

    @property
    def generation(self) -> int:
        """Incremented on every recycle; memoised states are keyed by it."""
        return self._generation

    def rss_mb(self) -> float | None:
        s = self._server
        return _rss_mb(s.proc.pid) if s is not None else None

    def over_budget(self) -> bool:
        rss = self.rss_mb()
        return rss is not None and rss >= self.settings.server_max_rss_mb

    def stats(self) -> ServerStats:
        s = self._server
        return ServerStats(
            mode=pet_mode(),
            generation=self._generation,
            alive=s is not None and s.proc.poll() is None,
            pid=s.proc.pid if s is not None else None,
            sessions=s.sessions if s is not None else 0,
            rss_mb=self.rss_mb(),
            recycles=dict(self.recycles),
            fallbacks=self._fallbacks,
        )

    # --- lifecycle -----------------------------------------------------

    def configure(self, **overrides: Any) -> None:
        """Override settings (e.g. from a worker initializer)."""
        self.settings = replace(self.settings, **overrides)

    def request_recycle(self, reason: str) -> None:
        """Recycle before the next session (never mid-session)."""
        self._pending_recycle = reason

    def recycle(self, reason: str) -> None:
        """Kill this process's server now (if any) and bump the generation."""
        with self._state_lock:
            self._kill_locked(reason)

    def _kill_locked(self, reason: str) -> None:
        s = self._server
        self._server = None
        self._pending_recycle = None
        self._generation += 1
        self.recycles[reason] += 1
        if s is None or s.owner_pid != os.getpid():
            return
        if s.proc.poll() is None:
            s.proc.kill()
            try:
                s.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        _log.info("pet-server pid %d recycled: %s", s.proc.pid, reason)

    def _forget(self) -> None:
        """After fork in the child: the server belongs to the parent."""
        self._server = None
        self._supervisor = None
        self._session_lock = threading.RLock()
        self._state_lock = threading.Lock()

    def _atexit(self) -> None:
        s = self._server
        if s is not None and s.owner_pid == os.getpid():
            self._kill_locked("atexit")

    def _spawn(self) -> _Server | None:
        st = self.settings
        spawn_seconds = tb.clamp_timeout(st.spawn_timeout_s)
        ROCQ_CACHE_DIR.mkdir(exist_ok=True)
        LOG_DIR.mkdir(exist_ok=True)
        port = _free_port()
        cmd = ["pet-server", "-p", str(port)]
        # `setpriv --pdeathsig`: the server dies with this process even on
        # SIGKILL. `prlimit --as`: address-space cap. Both exec the next
        # command in place (same pid), no `preexec_fn` in a threaded
        # parent.
        if _which("setpriv"):
            cmd = ["setpriv", "--pdeathsig=KILL", *cmd]
        if _which("prlimit"):
            cap = st.server_rlimit_as_mb * 2**20
            cmd = ["prlimit", f"--as={cap}", *cmd]
        log_path = LOG_DIR / f"pet-server-{os.getpid()}-{self._generation}.log"
        try:
            with open(log_path, "ab") as log:
                proc = subprocess.Popen(
                    cmd,
                    cwd=ROCQ_CACHE_DIR,
                    stdout=subprocess.DEVNULL,
                    stderr=log,
                )
        except OSError as e:
            _log.error("cannot spawn pet-server: %s", e)
            return None
        deadline = time.monotonic() + spawn_seconds
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                _log.error(
                    "pet-server exited at startup (rc=%s); see %s",
                    proc.returncode,
                    log_path,
                )
                return None
            try:
                with socket.create_connection(("127.0.0.1", port), 0.3):
                    return _Server(
                        proc=proc,
                        port=port,
                        owner_pid=os.getpid(),
                        generation=self._generation,
                        started_at=time.monotonic(),
                        log_path=log_path,
                    )
            except OSError:
                time.sleep(0.1)
        proc.kill()
        _log.error("pet-server did not accept connections in time")
        return None

    def _open(self, doc_file: str) -> tuple[_Server, BoundedPytanque] | None:
        st = self.settings
        with self._state_lock:
            s = self._server
            if s is not None and s.owner_pid != os.getpid():
                self._server = None  # inherited through fork: not ours
                s = None
            reason: str | None = None
            if s is None:
                pass
            elif s.proc.poll() is not None:
                reason = "died"
            elif self._pending_recycle is not None:
                reason = self._pending_recycle
            elif s.current_file not in (None, doc_file):
                reason = "file-change"
            elif s.sessions >= st.server_max_sessions:
                reason = "sessions"
            elif self.over_budget():
                reason = "rss"
            if reason is not None:
                self._kill_locked(reason)
                s = None
            if s is None:
                s = self._spawn()
                if s is None:
                    return None
                self._server = s
        client = BoundedPytanque(
            "127.0.0.1",
            s.port,
            settings=st,
            on_failure=lambda kind: self.recycle(f"transport:{kind}"),
        )
        try:
            client.connect()
        except OSError as e:
            _log.error("cannot connect to pet-server: %s", e)
            self.recycle("connect-failed")
            return None
        return s, client

    def _fallback_warning(self) -> None:
        self._fallbacks += 1
        if not self._warned_fallback:
            self._warned_fallback = True
            msg = (
                "omphalos: private pet-server unavailable; falling back to "
                "STDIO sessions for this process (slower, unbounded). "
                f"See {LOG_DIR}."
            )
            _log.error(msg)
            print(msg, file=sys.stderr)

    @contextmanager
    def _session_admission(self) -> Generator[None]:
        op = tb.CURRENT.get()
        if op is None:
            with self._session_lock:
                yield
            return
        if not self._session_lock.acquire(timeout=op.remaining()):
            op.exhausted = "operation deadline waiting for session"
            raise tb.OperationExhausted(op.exhausted)
        try:
            op.remaining()
            yield
        finally:
            self._session_lock.release()

    @contextmanager
    def session(self, doc_file: str) -> Generator[Pytanque]:
        """
        A petanque client for `doc_file` (the augmented path). Socket
        mode: a fresh connection to this process's warm server, with
        the recycle policy applied first. STDIO mode (or fallback): a
        fresh `pet` subprocess, exactly the archived transport.
        """
        with self._session_admission():
            if pet_mode() == "socket":
                self.start_supervisor_thread(
                    exit_when_orphaned=self._exit_when_orphaned
                )
                opened = self._open(doc_file)
                if opened is not None:
                    server, client = opened
                    server.sessions += 1
                    server.current_file = doc_file
                    server.in_session_since = time.monotonic()
                    try:
                        yield client
                    finally:
                        server.in_session_since = None
                        try:
                            client.close()
                        except Exception:
                            pass
                        if client.poisoned and self._server is server:
                            # Not already recycled by `on_failure`.
                            self.recycle("poisoned")
                    return
                if tb.CURRENT.get() is not None:
                    raise ConnectionLost(
                        "bounded operation: socket server unavailable"
                    )
                self._fallback_warning()
            if tb.CURRENT.get() is not None:
                raise ConnectionLost(
                    "bounded operations require socket transport"
                )
            with _stdio_session() as client:
                yield client

    # --- supervisor ----------------------------------------------------

    def start_supervisor_thread(
        self, *, exit_when_orphaned: bool = False
    ) -> None:
        """
        Daemon thread: recycles a server that outgrew its budget by a
        wide margin or has been held by one session for too long (the
        in-flight RPC then fails as `ConnectionLost` — the same blast
        radius as the old external watchdog, without `pkill`). With
        `exit_when_orphaned`, a pool worker whose launcher died exits
        instead of keeping its cell alive against a relaunch.
        """
        self._exit_when_orphaned = exit_when_orphaned
        if self._supervisor is not None and self._supervisor.is_alive():
            return
        t = threading.Thread(
            target=self._supervise, name="pet-supervisor", daemon=True
        )
        self._supervisor = t
        t.start()

    def _supervise(self) -> None:
        while True:
            time.sleep(self.settings.supervisor_period_s)
            try:
                self._supervise_once()
            except Exception as e:  # never let the supervisor die
                _log.error("pet supervisor: %s", e)

    def _supervise_once(self) -> None:
        if self._exit_when_orphaned and os.getppid() == 1:
            self.recycle("supervisor:orphan")
            _log.error("launcher gone; worker %d exiting", os.getpid())
            os._exit(3)
        s = self._server
        if s is None or s.owner_pid != os.getpid():
            return
        rss = _rss_mb(s.proc.pid)
        if rss is not None and rss >= 1.25 * self.settings.server_max_rss_mb:
            self.recycle("supervisor:rss")
            return
        avail = mem_available_mb()
        if (
            rss is not None
            and avail is not None
            and avail < self.settings.memory_floor_mb
            and rss >= self.settings.memory_floor_hog_mb
        ):
            _log.error(
                "memory floor: %.0f MB available, server at %.0f MB — recycling",
                avail,
                rss,
            )
            self.recycle("supervisor:memory-floor")
            return
        since = s.in_session_since
        if since is not None and (
            time.monotonic() - since > self.settings.session_max_s
        ):
            self.recycle("supervisor:session")


@contextmanager
def _stdio_session() -> Generator[Pytanque]:
    """One fresh `pet` subprocess, cwd `.rocq_cache/` (archived transport)."""
    ROCQ_CACHE_DIR.mkdir(exist_ok=True)
    cwd = os.getcwd()
    os.chdir(ROCQ_CACHE_DIR)
    try:
        client = Pytanque(mode=PytanqueMode.STDIO)  # type: ignore[reportUnknownMemberType]
        client.__enter__()
    finally:
        os.chdir(cwd)
    try:
        yield client
    finally:
        client.__exit__(None, None, None)


MANAGER = PetServerManager()
"""This process's server manager. Forked children start empty."""

os.register_at_fork(after_in_child=MANAGER._forget)  # pyright: ignore[reportPrivateUsage]
atexit.register(MANAGER._atexit)  # pyright: ignore[reportPrivateUsage]


def configure(**overrides: Any) -> None:
    """`MANAGER.configure`, exported for worker initializers."""
    MANAGER.configure(**overrides)


__all__ = [
    "AUG_DIR",
    "ROCQ_CACHE_DIR",
    "MANAGER",
    "BoundedPytanque",
    "ConnectionLost",
    "Deadline",
    "PetServerManager",
    "ReplyTooLarge",
    "ServerStats",
    "ServerUnavailable",
    "Settings",
    "TransportError",
    "TRANSPORT_FAILURE_TEXT",
    "augmented_path",
    "mem_available_mb",
    "configure",
    "pet_mode",
]
