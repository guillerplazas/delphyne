"""
Unit tests for `experiments/ace_x_eval.py` — the evaluation-arm
selection that the 2026-08-26 audit found silently falling back to the
v2 playbook (the flag was consumed from `sys.argv` on first read) and
hard-coding `render_version=2`.

Pure Python, no Rocq, no API: part of `make test-unit`. Each case runs
the module in a fresh interpreter because the selection is parsed at
import.
"""

# pyright: strict

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent


def _run(*argv: str, code: str) -> tuple[int, str, str]:
    script = (
        textwrap.dedent(
            f"""
        import sys
        sys.argv = ["x.py", *{list(argv)!r}]
        sys.path.insert(0, {str(_OMPHALOS_DIR / "experiments")!r})
        sys.path.insert(0, {str(_OMPHALOS_DIR)!r})
        import ace_x_eval as ev
        """
        )
        + code
    )
    res = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=_OMPHALOS_DIR,
    )
    return res.returncode, res.stdout, res.stderr


def test_selection_is_parsed_once_and_flags_are_stripped() -> None:
    rc, out, err = _run(
        "--playbook=ace_x3_offline.yaml",
        "run",
        "--max_workers=4",
        code=(
            "s = ev.SELECTION\n"
            "print(s.playbook_name, s.sha8, s.render_version, s.render_source)\n"
            "print(ev.selected_playbook()[1][:8], ev.selected_playbook()[1][:8])\n"
            "print(sys.argv)\n"
            "print(ev.arm_output_dir('validation'))\n"
        ),
    )
    assert rc == 0, err
    lines = out.strip().splitlines()
    assert lines[0] == "ace_x3_offline.yaml 1e4aec7d 3 provenance", lines
    assert lines[1] == "1e4aec7d 1e4aec7d", "second call must not fall back"
    assert lines[2] == "['x.py', 'run', '--max_workers=4']", lines[2]
    assert lines[3].endswith("ace_x_validation_ace_x3_offline_rv3_agentic")


def test_default_playbook_is_v2_at_render_version_2() -> None:
    rc, out, err = _run(
        "run",
        code="print(ev.SELECTION.playbook_name, ev.SELECTION.render_version)",
    )
    assert rc == 0, err
    assert out.strip() == "ace_x_offline.yaml 2"


def test_override_and_injection_reach_dir_and_configs() -> None:
    rc, out, err = _run(
        "--playbook=ace_x3_offline.yaml",
        "--render_version=2",
        "--injection=top10",
        code=(
            "import minif2f_x as x\n"
            "cfgs = ev.ace_x_configs(dict(list(x.VALIDATIONX_PROBLEMS.items())[:2]), (0,))\n"
            "print(ev.arm_output_dir('test'))\n"
            "print(cfgs[0].render_version, cfgs[0].injection, cfgs[0].playbook_sha256[:8])\n"
        ),
    )
    assert rc == 0, err
    lines = out.strip().splitlines()
    assert lines[0].endswith("ace_x_test_ace_x3_offline_top10_rv2_agentic")
    assert lines[1] == "2 top10 1e4aec7d"
    assert "deliberate ablation" in err


def test_announce_refuses_a_directory_of_another_arm() -> None:
    with tempfile.TemporaryDirectory(
        dir=_OMPHALOS_DIR / "experiments" / "output"
    ) as tmp:
        rel = str(Path(tmp).relative_to(_OMPHALOS_DIR))
        (Path(tmp) / "experiment.yaml").write_text(
            "name: null\ndescription: null\nconfigs:\n"
            "  c1:\n    params:\n      playbook_sha256: 1ac8a092deadbeef\n"
            "      render_version: 2\n    status: done\n"
        )
        rc, out, err = _run(
            "--playbook=ace_x3_offline.yaml",
            code=f"ev.announce({rel!r})",
        )
        assert rc == 3, (rc, out, err)
        assert "REFUSING" in err and "sha=1ac8a092 rv=2" in err
        rc, out, err = _run(
            "--playbook=ace_x_offline.yaml",
            code=f"ev.announce({rel!r})",
        )
        assert rc == 0, (rc, out, err)


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
