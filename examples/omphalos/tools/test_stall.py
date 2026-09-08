"""
Unit tests for `stall.py` and `tools/stall_report.py` (pure Python —
no LLM, no Rocq): the four rules on hand-built verdict sequences,
`stop_after` versus `stalled` step by step, the prefix reader, the
cache replay on a synthetic cell (tool-call billing, tail), and the
parity check. Part of `make test-unit`.
"""

# pyright: strict

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import delphyne as dp  # noqa: E402

import pytanque_utils as pt  # noqa: E402
import stall  # noqa: E402
import stall_report as sr  # noqa: E402

_RING = "(-1, 'Tactic failure: not a valid ring equation.')"
_INC = "(-1, 'Attempt to save an incomplete proof')"


def _v(cls: str, n: int, key: str, idx: int) -> stall.VerdictView:
    return stall.VerdictView(cls, n, key, idx, idx)


def test_rules() -> None:
    seq = [
        _v("ring-failure", 1, "a", 0),
        _v("ring-failure", 1, "a", 0),
        _v("ring-failure", 1, "a", 0),
        _v("incomplete-proof", 2, "b", 3),
        _v("incomplete-proof", 2, "b", 5),
        _v("incomplete-proof", 2, "b", 7),
    ]
    # noadvance: indices 0,0,0 then 3,5,7 advance.
    assert stall.stop_after(seq, "noadvance", 2) == 3
    assert stall.stop_after(seq, "noadvance", 3) is None
    # samegoal: 2 repeats of (1,a) after the first, then 2 of (2,b).
    assert stall.stop_after(seq, "samegoal", 2) == 3
    assert stall.stop_after(seq, "samegoal", 3) is None
    # seenstate: states repeat from the 2nd verdict on; the class change
    # at verdict 4 is a new state.
    assert stall.stop_after(seq, "seenstate", 2) == 3
    # ... and the two runs of repeats are only 2 long each.
    assert stall.stop_after(seq, "seenstate", 3) is None
    # sameclass: three ring failures = 2 same-as-previous flags, then
    # the class changes and the count restarts.
    assert stall.stop_after(seq, "sameclass", 2) == 3
    assert stall.stop_after(seq, "sameclass", 3) is None
    seq7 = seq + [_v("incomplete-proof", 2, "b", 9)]
    assert stall.stop_after(seq7, "sameclass", 3) == 7
    assert stall.stop_after(seq7, "seenstate", 3) == 7
    assert stall.stop_after([], "sameclass", 1) is None
    assert stall.stop_after(seq, "sameclass", 0) is None


def test_stalled_matches_stop_after_step_by_step() -> None:
    seq = [_v("x", 1, "g", i) for i in (0, 0, 2, 2, 2, 2)]
    for rule in stall.RULES:
        for k in (1, 2, 3):
            first = None
            for n in range(1, len(seq) + 1):
                if stall.stalled(seq[:n], rule, k):
                    first = n
                    break
            assert first == stall.stop_after(seq, rule, k), (rule, k)


def test_view_and_prefix() -> None:
    fb = pt.Feedback(
        success=False,
        failing_index=2,
        failing_tactic="ring.",
        error_message=_RING,
        remaining_goals=["x : R\n|- x  <=  1"],
        proof_so_far=["intros.", "unfold f."],
    )
    v = stall.view_of_feedback(fb)
    assert v == stall.VerdictView("ring-failure", 1, "x <= 1", 2, 2)
    assert stall.view_of_feedback(pt.Feedback(success=True)) is None
    prefix = [
        dp.FeedbackMessage(kind="feedback", label="feedback", meta=fb),
        dp.FeedbackMessage(kind="feedback", label="parse", meta=None),
        dp.FeedbackMessage(
            kind="feedback", label="feedback", meta=pt.Feedback(success=True)
        ),
    ]
    assert stall.views_of_prefix(prefix) == [v]
    assert stall.goal_key("a\n|- b   c") == "b c"
    assert stall.goal_key("no turnstile") == "no turnstile"


def _cache(entries: list[str]) -> str:
    return "".join(entries)


def _llm(inp: int, out: int) -> str:
    return (
        "- input:\n    request:\n      chat:\n        - role: user\n"
        "          content: hi\n      options:\n        model: gpt-5.6-luna\n"
        "    iter: 1\n  output:\n    outputs:\n      - content: x\n"
        f"    budget:\n      values:\n        input_tokens: {inp}\n"
        f"        cached_input_tokens: 0\n        output_tokens: {out}\n"
        "        price: 0.001\n"
    )


def _check(success: bool, idx: int, msg: str) -> str:
    body = (
        f"success: {'true' if success else 'false'}\n"
        + ("" if success else f"failing_index: {idx}\n")
        + ("" if success else "failing_tactic: 'ring.'\n")
        + ("" if success else f"error_message: {msg!r}\n")
        + (
            "remaining_goals: []\n"
            if success
            else "remaining_goals:\n  - '|- x <= 1'\n"
        )
        + "proof_so_far: []\n"
    )
    return (
        "- input:\n    request:\n      chat:\n        - role: user\n"
        "          content: |\n            fun: check_assisted\n"
        "            args: {}\n      options:\n        model: __compute__\n"
        "    iter: 1\n  output:\n    outputs:\n      - content: |\n"
        + "".join(f"          {line}\n" for line in body.splitlines())
    )


def test_replay_and_parity() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp) / "run"
        # Cell A: tool call, proposal (ring), proposal (ring), proposal
        # (ring), solved on the 4th proposal, plus a billed tail.
        a = run / "configs" / "p1__core-medium__gpt-5.6-luna__seed0"
        a.mkdir(parents=True)
        a.joinpath("cache.yaml").write_text(
            _cache(
                [
                    _llm(1000, 10),
                    _llm(1000, 10),
                    _check(False, 1, _RING),
                    _llm(1000, 10),
                    _check(False, 1, _RING),
                    _llm(1000, 10),
                    _check(False, 1, _RING),
                    _llm(1000, 10),
                    _check(True, 0, ""),
                    _llm(1000, 10),
                ]
            )
        )
        (run / "results_summary.csv").write_text(
            "bench_name,seed,success\np1,0,True\n"
        )
        cells = sr.load_run(run)
        c = cells[("p1", "0")]
        assert c.proposals == 4 and c.solved
        assert len(c.prices) == 5  # four proposals + tail
        assert abs(c.prices[0] - 2 * c.prices[1]) < 1e-12  # tool call billed
        spend, ok, stop = c.under("sameclass", 2)
        assert stop == 3 and not ok
        assert abs(spend - sum(c.prices[:3])) < 1e-12
        spend, ok, stop = c.under("sameclass", 5)
        assert stop is None and ok and abs(spend - c.total) < 1e-12
        r = sr.apply_rule("run", cells, "sameclass", 2)
        assert r.lost == ["p1/s0"] and r.stopped == 1
        rows = sr.grid("run", cells)
        assert len(rows) == len(stall.RULES) * len(stall.K_GRID)
        # Parity: the cell continued past the replay's stop -> violation.
        assert sr.parity(cells, "sameclass", 2)
        assert not sr.parity(cells, "sameclass", 5)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
