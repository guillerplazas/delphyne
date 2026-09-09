"""
Tests for the Rocq transport layer (`rocq_server`) and the prefix memo
in `pytanque_utils`. Needs `pet-server` on the PATH (a few seconds of
Rocq, no API calls): `make test-rocq`.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import os
import signal
import time
from pathlib import Path


import runtime.pytanque_utils as pt  # noqa: E402
import runtime.rocq_server as rs  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT
PROBLEM = str(_OMPHALOS_DIR / "miniF2F/test/imo/imo_1960_p2.v")
THM = "imo_1960_p2"
IMPORTS = pt.DEFAULT_EXTRA_IMPORTS


def _aug() -> str:
    return rs.augmented_path(PROBLEM, IMPORTS)


def test_augmented_path_is_stable_and_legacy_identical() -> None:
    a = _aug()
    b = _aug()
    assert a == b
    p = Path(a)
    assert p.is_relative_to(rs.AUG_DIR)
    legacy = "\n".join(IMPORTS) + "\n" + Path(PROBLEM).read_text()
    assert p.read_text() == legacy
    # A different import set maps to a different, equally stable path.
    other = rs.augmented_path(PROBLEM, ("Require Import Lia.",))
    assert other != a
    assert not Path(a).is_relative_to(_OMPHALOS_DIR / "miniF2F")


def test_start_works_from_aug_dir_and_is_warm() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    rs.MANAGER.recycle("test")
    f = _aug()
    with rs.MANAGER.session(f) as c:
        c.start(f, THM)
    t0 = time.perf_counter()
    with rs.MANAGER.session(f) as c:
        s = c.start(f, THM)
        s = c.run(s, "intros.", timeout=10)
        assert len(c.goals(s)) == 1
    assert time.perf_counter() - t0 < 0.5, "warm start should be milliseconds"
    assert rs.MANAGER.stats().alive


def test_transport_failure_is_petanque_error_and_respawns() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    f = _aug()
    gen = rs.MANAGER.generation
    with rs.MANAGER.session(f) as c:
        s = c.start(f, THM)
        pid = rs.MANAGER.stats().pid
        assert pid is not None
        os.kill(pid, signal.SIGKILL)
        try:
            c.run(s, "intros.", timeout=10)
        except rs.TransportError as e:
            assert isinstance(e, rs.ConnectionLost)
            assert getattr(c, "poisoned")
        else:
            raise AssertionError("expected a transport error")
    assert rs.MANAGER.generation == gen + 1, "one kill = one recycle"
    with rs.MANAGER.session(f) as c:
        c.start(f, THM)
    assert rs.MANAGER.stats().alive


def test_reply_cap_recycles() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    f = _aug()
    rs.configure(reply_cap_bytes=64)
    try:
        gen = rs.MANAGER.generation
        with rs.MANAGER.session(f) as c:
            try:
                c.start(f, THM)
            except rs.ReplyTooLarge:
                pass
            else:
                raise AssertionError("expected ReplyTooLarge")
        assert rs.MANAGER.generation == gen + 1
    finally:
        rs.configure(reply_cap_bytes=rs.Settings().reply_cap_bytes)
    with rs.MANAGER.session(f) as c:
        c.start(f, THM)


def test_deadline_backstop() -> None:
    """A tactic that never returns is cut by the socket deadline."""
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    f = _aug()
    rs.configure(rpc_margin_s=0.5)
    try:
        with rs.MANAGER.session(f) as c:
            s = c.start(f, THM)
            t0 = time.perf_counter()
            try:
                # A bullet-led sentence escapes pytanque's `Timeout`
                # wrapper (the old unguarded-hang case): only the
                # socket deadline can end it.
                c.run(s, "intros x H0 H1 H2; repeat split; nra.", timeout=1)
            except rs.TransportError as e:
                assert isinstance(e, rs.Deadline), e
            except pt.PetanqueError:
                pass  # Rocq's own Timeout fired first: also fine
            assert time.perf_counter() - t0 < 10
    finally:
        rs.configure(rpc_margin_s=rs.Settings().rpc_margin_s)


def test_fork_guard() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    f = _aug()
    with rs.MANAGER.session(f) as c:
        c.start(f, THM)
    parent_pid = rs.MANAGER.stats().pid
    assert parent_pid is not None
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:  # child
        os.close(r)
        st = rs.MANAGER.stats()
        os.write(w, f"{int(st.alive)} {st.pid}".encode())
        os.close(w)
        os._exit(0)
    os.close(w)
    os.waitpid(pid, 0)
    msg = os.read(r, 100).decode()
    os.close(r)
    assert msg == "0 None", f"child must start without a server, got {msg!r}"
    assert rs.MANAGER.stats().alive, "the child's exit must not kill ours"
    assert rs.MANAGER.stats().pid == parent_pid


def test_file_change_recycles() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    f = _aug()
    g = rs.augmented_path(
        str(_OMPHALOS_DIR / "miniF2F/valid/aime/aime_1991_p6.v"), IMPORTS
    )
    with rs.MANAGER.session(f) as c:
        c.start(f, THM)
    gen = rs.MANAGER.generation
    with rs.MANAGER.session(g) as c:
        c.start(g, "aime_1991_p6")
    assert rs.MANAGER.generation == gen + 1
    assert rs.MANAGER.recycles.get("file-change", 0) >= 1


def test_prefix_memo_reuses_states() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    rs.MANAGER.recycle("test")
    script = ["intros x H0 H1 H2.", "split."]
    fb1 = pt.check_assisted(PROBLEM, THM, script)
    n1 = pt.prefix_memo_size()
    assert n1 >= 3  # start state + two prefixes
    fb2 = pt.check_assisted(PROBLEM, THM, [*script, "nra."])
    assert fb1.remaining_goals and fb2.failing_index is not None
    # The extended script reused the memoised prefix: only new entries.
    assert pt.prefix_memo_size() == n1 + 1
    # Preview and verification agree with a cold run (the check memo
    # is cleared so the rerun actually re-executes).
    rs.MANAGER.recycle("test")
    pt.clear_check_memo()
    cold = pt.check_assisted(PROBLEM, THM, [*script, "nra."])
    assert cold == fb2


def test_stdio_mode_matches_socket() -> None:
    script = ["intros x H0 H1 H2.", "split.", "nra."]
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    pt.clear_check_memo()  # this test is about re-execution parity
    a = pt.check_assisted(PROBLEM, THM, script)
    q_a = pt.query(PROBLEM, THM, "Check sqrt.")
    os.environ["OMPHALOS_PET_MODE"] = "stdio"
    pt.clear_check_memo()
    b = pt.check_assisted(PROBLEM, THM, script)
    q_b = pt.query(PROBLEM, THM, "Check sqrt.")
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    assert a == b
    assert q_a == q_b


def test_goal_caps_shape() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    caps = pt.GoalCaps(probe=1, render=1, render_chars=40)
    fb = pt.check_assisted(
        PROBLEM, THM, ["intros x H0 H1 H2.", "split."], goal_caps=caps
    )
    assert fb.probe is not None and len(fb.probe) == 1
    assert len(fb.remaining_goals) == 2  # one goal + the marker
    assert "1 more goal(s) not shown" in fb.remaining_goals[-1]
    assert fb.remaining_goals[0].endswith("[goal truncated]")
    plain = pt.check_assisted(PROBLEM, THM, ["intros x H0 H1 H2.", "split."])
    assert plain.probe is not None and len(plain.probe) == 2


def test_check_memo_hit_guards_and_kill_switch() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    rs.MANAGER.recycle("test")
    pt.clear_check_memo()
    script = ["intros x H0 H1 H2.", "split.", "nra."]
    fb1 = pt.check_assisted(PROBLEM, THM, script)
    n = pt.check_memo_size()
    assert n == 1
    sessions_before = rs.MANAGER.stats().sessions
    fb2 = pt.check_assisted(PROBLEM, THM, script)
    assert fb2 == fb1
    assert fb2 is not fb1, "hits must be private copies"
    assert rs.MANAGER.stats().sessions == sessions_before, (
        "a memo hit must not open a session"
    )
    # A memo hit survives a recycle: the verdict does not depend on
    # the server generation, unlike the prefix memo.
    rs.MANAGER.recycle("test")
    assert pt.check_assisted(PROBLEM, THM, script) == fb1
    # Kill switch: OMPHALOS_CHECK_MEMO=0 re-executes.
    os.environ["OMPHALOS_CHECK_MEMO"] = "0"
    try:
        with_off = pt.check_assisted(PROBLEM, THM, script)
        assert with_off == fb1
        assert pt.check_memo_size() == n, "disabled memo must not grow"
    finally:
        del os.environ["OMPHALOS_CHECK_MEMO"]
    # A call the transport did not survive is not stored: with a tiny
    # reply cap the session fails to start (a recycle mid-call), the
    # feedback reports the failure, and nothing is memoised for the key.
    pt.clear_check_memo()
    rs.configure(reply_cap_bytes=64)
    try:
        bad = pt.check_assisted(PROBLEM, THM, script)
        assert not bad.success and bad.error_message is not None
        assert pt.check_memo_size() == 0, "failed transport must not memoise"
    finally:
        rs.configure(reply_cap_bytes=rs.Settings().reply_cap_bytes)
    good = pt.check_assisted(PROBLEM, THM, script)
    assert good == fb1
    assert pt.check_memo_size() == 1


def test_rlimit_spawn_failure_falls_back_loudly() -> None:
    os.environ["OMPHALOS_PET_MODE"] = "socket"
    rs.MANAGER.recycle("test")
    rs.configure(server_rlimit_as_mb=16, spawn_timeout_s=5)
    before = rs.MANAGER.stats().fallbacks
    try:
        f = _aug()
        with rs.MANAGER.session(f) as c:
            s = c.start(f, THM)
            assert not s.proof_finished
        assert rs.MANAGER.stats().fallbacks == before + 1
    finally:
        base = rs.Settings()
        rs.configure(
            server_rlimit_as_mb=base.server_rlimit_as_mb,
            spawn_timeout_s=base.spawn_timeout_s,
        )
        rs.MANAGER.recycle("test")


def main() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    failed = 0
    for t in tests:
        t0 = time.perf_counter()
        try:
            t()
            print(f"ok    {t.__name__} ({time.perf_counter() - t0:.1f}s)")
        except Exception as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {type(e).__name__}: {e}")
    print(f"{len(tests) - failed}/{len(tests)} passed; {rs.MANAGER.stats()}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
