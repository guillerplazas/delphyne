"""
Unit tests for the Ladon loop: pure Python, no API calls, no Rocq.

Run as `python -m ladon.test_ladon` (part of `make test-unit`). Tests
that need archived runs skip themselves when the directories are
absent, like `tools/test_launch_state.py`.
"""

# pyright: strict

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from string import Template
from typing import Any

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
for _sub in ("", "experiments", "tools"):
    _p = str(_OMPHALOS_DIR / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from cell_records import CellRecord  # noqa: E402
from decision_audit import MIN_DISCORDANT_FOR_SIG, sign_test  # noqa: E402

from ladon import bench  # noqa: E402
from ladon import claude_driver as C  # noqa: E402
from ladon import guard  # noqa: E402
from ladon import hints as H  # noqa: E402
from ladon import launch as L  # noqa: E402
from ladon import make_partition  # noqa: E402
from ladon import report as RP  # noqa: E402
from ladon import state as S  # noqa: E402
from ladon import verdict as V  # noqa: E402

HINTS_FILE = _OMPHALOS_DIR / "HINTS.md"
PROGRESS_FILE = _OMPHALOS_DIR / "PROGRESS.md"
VALIDATION_RUN = (
    _OMPHALOS_DIR / "experiments" / "output" / "x_validation_agentic"
)


def _cell(
    bench_name: str,
    seed: str,
    *,
    solved: bool,
    cost: float = 0.01,
    failed: bool = False,
) -> CellRecord:
    return CellRecord(
        name=f"{bench_name}__core-medium__gpt-5.6-luna__seed{seed}",
        bench=bench_name,
        seed=seed,
        arm="core-medium",
        model="gpt-5.6-luna",
        params={},
        status="failed" if failed else "done",
        solved=solved and not failed,
        input=1000,
        cached=500,
        output=100,
        requests=3,
        cost=cost,
        platform_failed=failed,
    )


def _arms(
    n: int = 40,
    *,
    a_only: int = 0,
    b_only: int = 0,
    both: int = 20,
    b_cost: float = 0.01,
    seeds: tuple[str, ...] = ("0", "1"),
) -> tuple[list[CellRecord], list[CellRecord]]:
    """Synthetic paired arms with a controlled discordance per seed."""
    a: list[CellRecord] = []
    b: list[CellRecord] = []
    for seed in seeds:
        for i in range(n):
            name = f"p{i}"
            if i < both:
                a.append(_cell(name, seed, solved=True))
                b.append(_cell(name, seed, solved=True, cost=b_cost))
            elif i < both + a_only:
                a.append(_cell(name, seed, solved=True))
                b.append(_cell(name, seed, solved=False, cost=b_cost))
            elif i < both + a_only + b_only:
                a.append(_cell(name, seed, solved=False))
                b.append(_cell(name, seed, solved=True, cost=b_cost))
            else:
                a.append(_cell(name, seed, solved=False))
                b.append(_cell(name, seed, solved=False, cost=b_cost))
    return a, b


def _trust(cells: list[CellRecord]) -> dict[str, bool]:
    return {c.name: True for c in cells}


def _hint(text: str, n: int) -> H.Hint:
    h = H.find_hint(text, n)
    assert h is not None, n
    return h


#####
##### hints.py
#####


def test_parse_real_hints() -> None:
    text = HINTS_FILE.read_text()
    hs = H.parse_hints(text)
    assert len(hs) >= 60, len(hs)
    by = {h.n: h for h in hs}
    assert by[54].status == "done" and by[49].status == "done"
    assert by[55].status == "partial"
    assert by[67].status == "open" and by[61].status == "open"
    assert by[28].status == "done"  # suffix-style ✅
    assert by[67].tag == "experiment" and by[54].tag == "tool"
    assert any(h.tag == "method" for h in hs)
    assert all(h.title for h in hs)


def test_mark_hint_touches_one_line() -> None:
    text = HINTS_FILE.read_text()
    marked = H.mark_hint(
        text, 67, "LADON INSPECT 2026-09-03 — 55 vs 54; inspect with Fable"
    )
    a, b = text.splitlines(), marked.splitlines()
    assert len(a) == len(b)
    changed = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    assert len(changed) == 1
    assert _hint(marked, 67).status == "inspect"
    assert not _hint(marked, 67).open
    kept = H.mark_hint(text, 66, "DONE 2026-09-03 by Ladon — KEEP: 60 vs 54")
    assert _hint(kept, 66).status == "done"
    human = H.mark_hint(text, 65, "LADON HUMAN 2026-09-03 — structural")
    assert _hint(human, 65).status == "human"


def test_append_hints_numbering_and_section() -> None:
    text = HINTS_FILE.read_text()
    top = H.max_number(text)
    new = [
        H.NewHint("experiment", "A first idea", "body " * 30),
        H.NewHint("tool", "A second", "short body"),
    ]
    out = H.append_hints(text, "2026-09-03", new)
    hs = H.parse_hints(out)
    assert hs[0].n == top + 2 and hs[1].n == top + 1
    assert hs[0].section == H.ladon_section_heading("2026-09-03")[3:]
    assert hs[0].status == "open" and hs[1].tag == "tool"
    out2 = H.append_hints(
        out, "2026-09-03", [H.NewHint("policy", "Third", "x")]
    )
    hs2 = H.parse_hints(out2)
    assert hs2[0].n == top + 3 and hs2[0].section == hs[0].section
    assert out2.count(H.ladon_section_heading("2026-09-03")) == 1
    block = out.splitlines()[hs[0].first_line : hs[0].last_line + 1]
    assert all(ln.startswith("   ") for ln in block[1:])


def test_progress_section_roundtrip() -> None:
    text = PROGRESS_FILE.read_text()
    heading = H.progress_heading("2026-09-03", "in progress")
    out = H.insert_progress_section(text, heading, "Intro.")
    lines = out.splitlines()
    first = next(i for i, ln in enumerate(lines) if H.HEADING_RE.match(ln))
    assert lines[first] == heading
    assert out.startswith(text[:200])
    out = H.append_to_section(out, heading, "- **Hint 1 — x**: y.")
    span = H.find_section(out, heading)
    assert span is not None
    body = "\n".join(out.splitlines()[span[0] : span[1]])
    assert "Intro." in body and "Hint 1" in body
    out = H.replace_heading(
        out, heading, H.progress_heading("2026-09-03", "1 hints, 0 kept")
    )
    assert "1 hints, 0 kept" in out and heading not in out


#####
##### verdict.py
#####


def test_sign_test_floor() -> None:
    assert MIN_DISCORDANT_FOR_SIG == 6
    assert sign_test(0, 6) < 0.05 and sign_test(0, 5) >= 0.05


def test_verdict_keep_on_solves() -> None:
    a, b = _arms(a_only=0, b_only=4)  # 8 discordant over two seeds
    p = V.pair(a, b, _trust(b))
    assert p.primary.b_only == 8 and p.primary.a_only == 0
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "KEEP" and v.rule == "solves", v


def test_verdict_keep_on_cost() -> None:
    a, b = _arms(both=30, b_cost=0.005)
    p = V.pair(a, b, _trust(b))
    assert p.secondary.cheaper == 60 and p.secondary.median_ratio == 0.5
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "KEEP" and v.rule == "cost", v


def test_verdict_cost_with_deficit_is_not_keep() -> None:
    a, b = _arms(a_only=1, b_only=0, b_cost=0.005)
    p = V.pair(a, b, _trust(b))
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "INSPECT" and v.rule == "cheaper-with-deficit", v


def test_verdict_discard_on_harm_and_null() -> None:
    a, b = _arms(a_only=4, b_only=0)
    p = V.pair(a, b, _trust(b))
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "DISCARD" and v.rule == "harm", v
    a, b = _arms(a_only=1, b_only=1)
    p = V.pair(a, b, _trust(b))
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "DISCARD" and v.rule == "null", v
    a, b = _arms(a_only=3, b_only=3)
    p = V.pair(a, b, _trust(b))
    assert p.primary.powered
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "DISCARD" and v.rule == "null", v


def test_verdict_inspect_when_underpowered() -> None:
    a, b = _arms(a_only=0, b_only=2)  # +4 net, p = 0.125
    p = V.pair(a, b, _trust(b))
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "INSPECT" and v.rule == "underpowered-solves", v


def test_verdict_integrity_first() -> None:
    a, b = _arms(a_only=0, b_only=4)
    p = V.pair(a, b, {})  # nothing verified
    assert p.reverify_failed == 2 * 24
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "INSPECT" and v.rule == "manufactured-solve"
    p = V.pair(a, b, _trust(b))
    v = V.judge(p, "select", V.integrity_of(p, frozen_violation=True))
    assert v.outcome == "DISCARD" and v.rule == "frozen-path"
    v = V.judge(p, "select", V.integrity_of(p, code_drift=True))
    assert v.outcome == "INSPECT" and v.rule == "code-drift"
    a, b = _arms()
    for i in range(4):
        b[i] = replace(
            b[i], platform_failed=True, solved=False, status="failed"
        )
    p = V.pair(a, b, _trust(b))
    v = V.judge(p, "select", V.integrity_of(p))
    assert v.outcome == "INSPECT" and v.rule == "incomplete"


def test_pair_restricts_to_registered_problems() -> None:
    a, b = _arms(n=40, both=20, seeds=("0", "1"))
    b3 = [c for c in b if c.bench in ("p0", "p1", "p2") and c.seed == "0"]
    p = V.pair(a, b3, _trust(b3), seeds=("0",), problems=("p0", "p1", "p2"))
    assert p.primary.cells == 3 and p.unpaired == 0
    p2 = V.pair(a, b3, _trust(b3), seeds=("0",))
    assert p2.unpaired == 37
    assert guard.ARM_DIR_RE.match("ladon_2026-09-03-dry_h0_agentic")


def test_verdict_screen_tier() -> None:
    a, b = _arms(a_only=4, b_only=0, seeds=("0",))
    p = V.pair(a, b, _trust(b), seeds=("0",))
    assert p.primary.cells == 40
    v = V.judge(p, "screen", V.integrity_of(p))
    assert v.outcome == "DISCARD" and v.rule == "screen-harm"
    a, b = _arms(a_only=3, b_only=0, seeds=("0",))
    p = V.pair(a, b, _trust(b), seeds=("0",))
    assert V.judge(p, "screen", V.integrity_of(p)).outcome == "PROMOTE"


def test_verdict_classes() -> None:
    a, b = _arms()
    p = V.pair(a, b, _trust(b))
    assert V.judge(p, "select", V.integrity_of(p), "A").rule == "analysis"
    assert V.judge(p, "select", V.integrity_of(p), "D").outcome == "HUMAN"


def test_pair_archived_baseline_with_itself() -> None:
    if not (VALIDATION_RUN / "experiment.yaml").exists():
        return
    cells = V.load_cells(VALIDATION_RUN)
    p = V.pair(cells, cells, _trust(cells))
    assert p.primary.discordant == 0 and p.primary.cells == len(cells)
    assert p.secondary.median_ratio == 1.0 and p.secondary.cheaper == 0
    assert V.judge(p, "select", V.integrity_of(p)).rule == "null"
    d = V.as_dict(p)
    assert d["cells"] == len(cells) and d["discordant_cells"] == []


#####
##### guard.py
#####


def test_frozen_rules() -> None:
    assert guard.is_frozen("benchmarks/ladonX.txt")
    assert guard.is_frozen("tools/decision_audit.py")
    assert guard.is_frozen("experiments/minif2f_x.py")
    assert guard.is_frozen("experiments/x_ladon_experiment.py")
    assert guard.is_frozen("miniF2F/valid/a.v")
    assert guard.is_frozen("ladon/cli.py") and guard.is_frozen("HINTS.md")
    assert not guard.is_frozen("ladon/nights/2026-09-03/hints/h1/arm.yaml")
    assert not guard.is_frozen("experiments/ladon_2026-09-03_h1_experiment.py")
    assert not guard.is_frozen("pytanque_utils.py")
    assert not guard.is_frozen("prompts/x.jinja")
    assert guard.ARM_DIR_RE.match("ladon_2026-09-03_h58_agentic")
    assert not guard.ARM_DIR_RE.match("x_ladon_agentic")


def test_manifest_from_snapshots() -> None:
    before = guard.Snapshot(
        files={
            "a.py": guard.FileStat(1, 1, "x"),
            "Makefile": guard.FileStat(1, 1, "m"),
        },
        outputs={"x_ladon_agentic": "1:1"},
        blocks={"model_registry.py": "h1"},
        head="abc",
        git_status=(),
    )
    after = guard.Snapshot(
        files={
            "a.py": guard.FileStat(2, 2, "y"),
            "experiments/ladon_2026-09-03_h1_experiment.py": guard.FileStat(
                1, 1, "n"
            ),
        },
        outputs={
            "x_ladon_agentic": "1:2",
            "ladon_2026-09-03_h1_agentic": "1:1",
            "rogue": "1:1",
        },
        blocks={"model_registry.py": "h2"},
        head="abc",
        git_status=("?? src/x.py",),
    )
    m = guard.manifest(before, after)
    assert m.modified == ("a.py",)
    assert m.created == ("experiments/ladon_2026-09-03_h1_experiment.py",)
    assert m.deleted == ("Makefile",)
    assert m.blocks_changed == ("model_registry.py",)
    assert m.outputs_changed == ("x_ladon_agentic",)
    assert set(m.outputs_new) == {"ladon_2026-09-03_h1_agentic", "rogue"}
    assert m.out_of_scope == ("?? src/x.py",)
    v = guard.violations(
        m,
        allowed_output=lambda n: n == "ladon_2026-09-03_h1_agentic",
        allowed_script=lambda r: r.endswith("_h1_experiment.py"),
    )
    joined = "\n".join(v)
    assert "block-frozen" in joined and "rogue" in joined
    assert "pre-existing output directory changed: x_ladon_agentic" in joined
    assert "outside examples/omphalos" in joined
    assert guard.touched_python(m) == [
        "a.py",
        "experiments/ladon_2026-09-03_h1_experiment.py",
    ]


def test_snapshot_in_scratch_tree() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        root = tmp / "omphalos"
        (root / "experiments" / "output").mkdir(parents=True)
        (root / "a.py").write_text("print(1)\n")
        s1 = guard.snapshot(root)
        (root / "a.py").write_text("print(2)\n")
        (root / "experiments" / "new_experiment.py").write_text("x = 1\n")
        s2 = guard.snapshot(root)
        assert s1["a.py"].sha != s2["a.py"].sha
        assert "experiments/new_experiment.py" in s2
        assert guard.output_snapshot(root) == {}
    finally:
        shutil.rmtree(tmp)


#####
##### launch.py
#####


def test_expected_seconds_on_archived_baseline() -> None:
    if not (VALIDATION_RUN / "experiment.yaml").exists():
        return
    secs = L.cell_seconds(VALIDATION_RUN)
    assert len(secs) == 80
    est = L.expected_seconds(VALIDATION_RUN, list(secs), 4)
    assert L.MIN_EXPECTED_S <= est <= 6 * 3600
    single = L.expected_seconds(VALIDATION_RUN, [next(iter(secs))], 4)
    assert single == L.MIN_EXPECTED_S
    assert L.counts(VALIDATION_RUN).complete


def test_launch_env() -> None:
    env = L.launch_env({"A": "1", "LADON_SMOKE": "1"}, seeds=(0, 1))
    assert env["LADON_SEEDS"] == "0,1" and "LADON_SMOKE" not in env
    assert L.launch_env({}, seeds=(0,), smoke=True)["LADON_SMOKE"] == "1"


#####
##### claude_driver.py
#####


def test_build_argv() -> None:
    if shutil.which("claude") is None:
        return
    call = C.ClaudeCall(
        phase="implement",
        prompt="hi",
        model="sonnet",
        effort="medium",
        max_turns=60,
        log=Path("/tmp/x.jsonl"),
        allowed=("Read", "Bash(python:*)"),
        disallowed=("Bash(git push:*)",),
        system_file=Path("ladon/LADON.md"),
        schema={"type": "object"},
        max_budget_usd=15,
        add_dirs=("/x",),
    )
    argv = C.build_argv(call)
    for flag in (
        "-p",
        "--model",
        "--effort",
        "--max-turns",
        "--permission-mode",
        "--output-format",
        "--verbose",
        "--allowedTools",
        "--disallowedTools",
        "--append-system-prompt-file",
        "--json-schema",
        "--max-budget-usd",
        "--add-dir",
        "--strict-mcp-config",
        "--no-session-persistence",
    ):
        assert flag in argv, flag
    assert "--bare" not in argv
    inline = C.build_argv(call, system_prompt_flag="inline")
    assert "--append-system-prompt" in inline
    assert "--append-system-prompt-file" not in inline


def test_env_for_claude() -> None:
    env = C.env_for_claude(
        {
            "ANTHROPIC_API_KEY": "k",
            "CLAUDECODE": "1",
            "CLAUDE_CODE_SESSION_ID": "s",
            "CLAUDE_CODE_OAUTH_TOKEN": "t",
            "OPENAI_API_KEY": "o",
            "PATH": "p",
        }
    )
    assert set(env) == {
        "CLAUDE_CODE_OAUTH_TOKEN",
        "OPENAI_API_KEY",
        "PATH",
        "BASH_DEFAULT_TIMEOUT_MS",
        "BASH_MAX_TIMEOUT_MS",
    }


def test_parse_stream_and_rate_limit() -> None:
    lines = [
        "not json",
        '{"type":"system","subtype":"init"}',
        '{"type":"rate_limit_event","rate_limit":{"five_hour":'
        '{"utilization":1.0,"resets_at":1800000000}}}',
        '{"type":"result","subtype":"success","result":"You\'ve hit your'
        ' session limit","total_cost_usd":0.01,"num_turns":1,'
        '"session_id":"s","structured_output":{"ok":true}}',
    ]
    result, windows = C.parse_stream(lines)
    assert result is not None and result["subtype"] == "success"
    assert windows["five_hour"]["resets_at"] == 1800000000
    res = C.ClaudeResult(
        rc=1,
        subtype="success",
        text="You've hit your session limit · resets in 2h 5m",
        structured=None,
        cost_usd=0,
        num_turns=1,
        session_id="s",
        duration_s=1,
        rate_limited=True,
        resets_at=None,
    )
    assert C.wait_seconds(res, 0) == 2 * 3600 + 5 * 60 + 60
    res2 = replace(res, text="limit", resets_at=1000.0)
    assert C.wait_seconds(res2, 0, now=100.0) == 960.0
    res3 = replace(res, text="limit")
    assert C.wait_seconds(res3, 1) == C.BACKOFF_FIRST_S * 2
    assert C.RATE_LIMIT_RE.search("You've hit your weekly limit")


def test_parse_json_output_shapes() -> None:
    single = json.dumps(
        {"type": "result", "subtype": "success", "result": '{"ok": true}'}
    )
    result, _ = C.parse_json_output(single)
    assert result is not None
    assert C._structured(result) == {"ok": True}  # pyright: ignore[reportPrivateUsage]
    arr = json.dumps(
        [{"type": "system"}, {"type": "result", "subtype": "error_max_turns"}]
    )
    result, _ = C.parse_json_output(arr)
    assert result is not None and result["subtype"] == "error_max_turns"


#####
##### state.py / report.py
#####


def test_night_roundtrip_and_report() -> None:
    tmp = Path(tempfile.mkdtemp())
    try:
        night = S.Night(
            date="2026-09-03", base_sha="abc12345", branch="feature/omphalos"
        )
        h = S.HintRun(
            n=58, title="Goal caps", tag="experiment", hint_class="B"
        )
        for st in ("implementing", "implemented", "guarded", "screening"):
            h.enter(st)
        night.hints[58] = h
        night.order.append(58)
        night.enter("running")
        path = tmp / "night.yaml"
        S.save(night, path)
        back = S.load(path)
        assert back.state == "running" and back.hints[58].state == "screening"
        assert back.hints[58].timeline["implemented"]
        assert back.active_hints[0].n == 58
        h2 = back.hints[58]
        h2.outcome, h2.rule, h2.reason = "INSPECT", "underpowered-solves", "+3"
        h2.numbers = {
            "a_solved": 54,
            "b_solved": 57,
            "a_only": 1,
            "b_only": 4,
            "p_two": 0.375,
            "joint": 53,
            "cheaper": 20,
            "dearer": 10,
            "median_ratio": 0.93,
            "p_cost": 0.1,
        }
        h2.enter("recorded")
        RP.append_ledger(tmp / "ledger.tsv", back, h2)
        rows = RP.read_ledger(tmp / "ledger.tsv")
        assert rows[0]["hint"] == "58" and rows[0]["outcome"] == "INSPECT"
        text = RP.render_report(back, night_dir=tmp)
        assert "Inspect with Fable" in text and "#58" in text
        assert "0.375" in text
    finally:
        shutil.rmtree(tmp)


#####
##### bench.py / make_partition.py / the arm template
#####


def test_partition_and_bench() -> None:
    assert make_partition.check() == []
    assert len(bench.LADONX_PROBLEMS) == 40
    cfg = bench.ladon_config(next(iter(bench.LADONX_PROBLEMS)), 1)
    assert bench.config_name(cfg, None).endswith("__seed1")
    assert cfg._problem()[0].startswith("miniF2F/")  # pyright: ignore[reportPrivateUsage]
    smoke = bench.ladon_config(bench.SMOKE_PROBLEMS[0], 0)
    assert smoke._problem()[1] == bench.SMOKE_PROBLEMS[0]  # pyright: ignore[reportPrivateUsage]


def test_arm_template_renders_and_runs() -> None:
    template = _OMPHALOS_DIR / "ladon" / "prompts" / "arm_template.py.txt"
    text = Template(template.read_text()).substitute(
        hint_n=1,
        title="t",
        date="2026-09-03",
        script="experiments/ladon_2026-09-03_h1_experiment.py",
        smoke_dir="experiments/output/ladon_2026-09-03_h1_smoke",
        output_dir="experiments/output/ladon_2026-09-03_h1_agentic",
    )
    compile(text, "arm_template", "exec")
    script = (
        _OMPHALOS_DIR / "experiments" / "ladon_0000-00-00_h0_experiment.py"
    )
    script.write_text(text)
    try:
        env = dict(os.environ, LADON_SEEDS="0", LADON_SMOKE="1")
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                "import runpy; m = runpy.run_path("
                f"{str(script)!r}); print(len(m['configs']), m['OUTPUT_DIR'])",
            ],
            cwd=_OMPHALOS_DIR,
            env=env,
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr[-800:]
        assert proc.stdout.strip() == (
            "3 experiments/output/ladon_2026-09-03_h1_smoke"
        )
    finally:
        script.unlink(missing_ok=True)


def main() -> int:
    tests: list[Any] = [
        v for k, v in globals().items() if k.startswith("test_")
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"ok    {t.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {t.__name__}: {type(e).__name__}: {e}")
    print(f"{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
