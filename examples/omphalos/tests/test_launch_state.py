"""
Unit tests for the launch layer (`experiments/common/omphalos_launch.py`):
ground-truth status rebuilds, launch locks and stream slots.

Pure Python — no Rocq, no API — part of `make test-unit`. The rebuild
identity test runs against the archived `x_validation_agentic`
directory *read-only* (`write=False`) when it is present.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


import experiments.common.omphalos_launch as ol  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT


def _config_dir(root: Path, name: str) -> Path:
    d = root / "configs" / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_ground_truth_rules() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        done = _config_dir(root, "done")
        (done / "result.yaml").write_text(
            "# delphyne-command\ncommand: run_strategy\noutcome:\n  result:\n    success: true\n"
        )
        assert ol.ground_truth(done) == "done"
        # exception.txt from an earlier attempt does not override a result
        (done / "exception.txt").write_text("Traceback ...")
        assert ol.ground_truth(done) == "done"
        failed = _config_dir(root, "failed")
        (failed / "exception.txt").write_text("Traceback ...")
        assert ol.ground_truth(failed) == "failed"
        todo = _config_dir(root, "todo")
        assert ol.ground_truth(todo) == "todo"
        truncated = _config_dir(root, "truncated")
        (truncated / "result.yaml").write_text(
            "# delphyne-command\ncommand: run_strategy\nargs:\n  strategy: ["
        )
        assert ol.ground_truth(truncated) == "todo"
        empty = _config_dir(root, "empty")
        (empty / "result.yaml").write_text("")
        assert ol.ground_truth(empty) == "todo"
        assert ol.ground_truth(root / "configs" / "missing") == "todo"
        # A large result whose `args` block pushes `outcome:` past the
        # first 4 KB (ACE cells carry the rendered playbook in args).
        big = _config_dir(root, "big")
        body = (
            "# delphyne-command\ncommand: run_strategy\nargs:\n  playbook: |\n"
            + "".join(
                f"    - [rocq-{i:05d}] bullet text {i}\n" for i in range(400)
            )
            + "outcome:\n  result:\n    success: false\n"
            + "    raw_trace: "
            + "x" * (5 * 2**20)
            + "\n"
        )
        (big / "result.yaml").write_text(body)
        assert ol.ground_truth(big) == "done"


def test_rebuild_identity_on_archived_run() -> None:
    """A finished archived run must need zero changes (read-only)."""
    run = _OMPHALOS_DIR / "experiments" / "output" / "x_validation_agentic"
    if not (run / "experiment.yaml").exists():
        print("  (archived run not present; skipped)")
        return
    import experiments.common.minif2f_x as x

    import delphyne as dp

    exp = ol.OmphalosExperiment(
        config_class=x.XAgenticConfig,
        context=dp.workspace_execution_context(
            str(
                _OMPHALOS_DIR
                / "experiments/baselines/x_validation_experiment.py"
            )
        ),
        configs=None,
        output_dir="experiments/output/x_validation_agentic",
    )
    delta = exp.rebuild(write=False)
    assert delta.counts.get("done", 0) == 80, delta.counts
    assert not delta.changes, delta.changes


def test_retry_failed_sets_exception_aside() -> None:
    import experiments.common.minif2f_x as x

    import delphyne as dp

    with tempfile.TemporaryDirectory(
        dir=_OMPHALOS_DIR / "experiments" / "output"
    ) as tmp:
        # `load()` creates the state file only when the directory does
        # not exist yet, so point it at a fresh subdirectory.
        rel = str((Path(tmp) / "run").relative_to(_OMPHALOS_DIR))
        exp = ol.OmphalosExperiment(
            config_class=x.XAgenticConfig,
            context=dp.workspace_execution_context(
                str(
                    _OMPHALOS_DIR
                    / "experiments/baselines/x_validation_experiment.py"
                )
            ),
            configs=[x.x_config("imo_1960_p2", 0, max_dollar_budget=0.1)],
            output_dir=rel,
            config_naming=x.x_config_name,
        )
        exp.load()
        state_names = list(exp.get_status().keys())
        assert state_names  # sanity: the state file exists
        import yaml

        out = exp.absolute_output_dir
        raw = yaml.safe_load((out / "experiment.yaml").read_text())
        name = next(iter(raw["configs"]))
        cfg = out / "configs" / name
        cfg.mkdir(parents=True)
        (cfg / "exception.txt").write_text("Traceback ...")
        (cfg / "cache.yaml").write_text("paid attempt\n")
        assert exp.rebuild(write=True).counts.get("failed") == 1
        assert exp.retry_failed() == 1
        assert ol.ground_truth(cfg) == "todo"
        assert list(cfg.glob("exception.txt.bak-*"))
        assert exp.get_status()["todo"] == 1
        (cfg / "cache.yaml").write_text("fresh attempt\n")
        backups = list(cfg.glob("attempts/*/cache.yaml"))
        assert len(backups) == 1
        assert backups[0].read_text() == "paid attempt\n"


def test_launch_lock_is_exclusive_across_processes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        with ol.launch_lock(out):
            code = textwrap.dedent(
                f"""
                import sys
                sys.path.insert(0, {str(_OMPHALOS_DIR / "experiments")!r})
                sys.path.insert(0, {str(_OMPHALOS_DIR)!r})
                import experiments.common.omphalos_launch as ol
                from pathlib import Path
                try:
                    with ol.launch_lock(Path({str(out)!r})):
                        print("acquired")
                except ol.LaunchRefused as e:
                    print("refused:", e)
                """
            )
            res = subprocess.run(
                [sys.executable, "-c", code], capture_output=True, text=True
            )
            assert res.stdout.startswith("refused:"), res.stdout + res.stderr
            assert f"pid={os.getpid()}" in res.stdout
        # released: a second holder now succeeds
        with ol.launch_lock(out):
            pass


def test_stream_slots_refuse_and_release() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["OMPHALOS_SLOT_DIR"] = tmp
        try:
            with ol.stream_slots(3, 4, wait=False) as held:
                assert len(held) == 3
                table = ol.slot_table(4)
                assert sum(1 for _, h in table if h) == 3
                try:
                    with ol.stream_slots(2, 4, wait=False):
                        raise AssertionError("should have refused")
                except ol.LaunchRefused as e:
                    assert "holders" in str(e)
                with ol.stream_slots(1, 4, wait=False) as more:
                    assert more == [3]
            assert all(h is None for _, h in ol.slot_table(4))
            try:
                with ol.stream_slots(5, 4, wait=False):
                    pass
            except ol.LaunchRefused as e:
                assert "exceeds" in str(e)
            else:
                raise AssertionError("max_workers above the cap must refuse")
        finally:
            del os.environ["OMPHALOS_SLOT_DIR"]


def test_result_scan_cache() -> None:
    """Verified-complete results are cached on their stat and persist."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        done = _config_dir(root, "cell")
        result = done / "result.yaml"
        result.write_text("command: run_strategy\noutcome:\n  result: 1\n")
        assert ol.ground_truth(done) == "done"
        ol.save_scan_caches()
        sidecar = root / ol.SCAN_CACHE_NAME
        assert sidecar.exists()
        # A fresh process (simulated by dropping the in-memory caches)
        # answers from the sidecar without parsing.
        ol._SCAN_CACHES.clear()  # pyright: ignore[reportPrivateUsage]
        import json

        entries = json.loads(sidecar.read_text())
        assert "cell" in entries
        assert ol.ground_truth(done) == "done"
        # Any change to the file (here: truncation) invalidates by stat.
        result.write_text("")
        assert ol.ground_truth(done) == "todo"
        ol.save_scan_caches()
        assert "cell" not in json.loads(sidecar.read_text())
        # Restored content re-verifies and re-caches.
        result.write_text("command: run_strategy\noutcome:\n  result: 1\n")
        assert ol.ground_truth(done) == "done"
        ol._SCAN_CACHES.pop(root, None)  # pyright: ignore[reportPrivateUsage]


def test_try_lock_probe_is_nondestructive() -> None:
    """A probe must not rewrite the holder note or keep the lock."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "x.lock"
        fd = ol._try_lock(path, "real-holder")  # pyright: ignore[reportPrivateUsage]
        assert fd is not None
        note = path.read_text()
        assert "real-holder" in note
        os.close(fd)
        probe_fd = ol._try_lock(path, "probe", probe=True)  # pyright: ignore[reportPrivateUsage]
        assert probe_fd is not None
        os.close(probe_fd)
        assert path.read_text() == note, "probe must leave the note intact"


def test_stream_slots_queue_is_ticket_first() -> None:
    """Free slots + a live queued waiter: a newcomer must not jump it."""
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["OMPHALOS_SLOT_DIR"] = tmp
        try:
            waiter = ol._take_ticket("queued-waiter")  # pyright: ignore[reportPrivateUsage]
            try:
                with ol.stream_slots(1, 4, wait=False):
                    raise AssertionError(
                        "a newcomer must queue behind a live ticket"
                    )
            except ol.LaunchRefused:
                pass
            # The refused newcomer left no ticket behind.
            assert ol._live_tickets() == [waiter]  # pyright: ignore[reportPrivateUsage]
            waiter.unlink()
            with ol.stream_slots(1, 4, wait=False) as held:
                assert held == [0]
            assert not ol._live_tickets()  # pyright: ignore[reportPrivateUsage]
        finally:
            del os.environ["OMPHALOS_SLOT_DIR"]


def test_group_members_and_kill() -> None:
    proc = subprocess.Popen(
        [sys.executable, "-c", "import os,time; os.setsid(); time.sleep(60)"],
    )
    try:
        # Give the child time to setsid.
        import time

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and proc.pid not in ol.group_members(
            proc.pid
        ):
            time.sleep(0.05)
        assert proc.pid in ol.group_members(proc.pid)
        assert ol.kill_group(proc.pid, grace_s=1.0) == 0
        proc.wait(timeout=5)
    finally:
        if proc.poll() is None:
            proc.kill()


def main() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"ok    {t.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {type(e).__name__}: {e}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
