"""
Unit tests for `tools/analysis/ace_diagnosis.py` (pure Python — no LLM, no
Rocq): the turn profile over a synthetic run, the citation walk over
a synthetic cache, and the per-request decomposition arithmetic.
Part of `make test-unit`.
"""

# pyright: strict

import tempfile
from pathlib import Path


import tools.analysis.ace_diagnosis as dg  # noqa: E402
from tools.analysis.cell_records import CellRecord  # noqa: E402
from tools.analysis.failure_analysis import Verdict  # noqa: E402

_UNKNOWN = (
    "(-1, 'The reference omega was not found in the current\nenvironment.')"
)
"""A real line break, as Rocq's pretty-printer wraps it."""
_RING = "(-1, 'Tactic failure: not a valid ring equation.')"
_INCOMPLETE = "(-1, 'Attempt to save an incomplete proof')"


def _v(cfg: str, solved: bool, ok: bool, msg: str | None) -> Verdict:
    return Verdict(
        bench=cfg.split("__")[0],
        config=cfg,
        solved_run=solved,
        success=ok,
        failing_tactic="omega." if msg else None,
        error_message=msg,
        n_remaining_goals=0,
        finished=ok,
    )


def test_turn_profile() -> None:
    a = "p1__core-medium__m__seed0"
    b = "p2__core-medium__m__seed0"
    c = "p3__core-medium__m__seed0"
    verdicts = [
        _v(a, True, False, _UNKNOWN),
        _v(a, True, False, _UNKNOWN),
        _v(a, True, False, _RING),
        _v(a, True, True, None),
        _v(b, False, False, _RING),
        _v(b, False, False, _INCOMPLETE),
        _v(c, True, True, None),
    ]
    p = dg.turn_profile(verdicts)
    assert p.cells == 3 and p.solved_cells == 2 and p.first_try_solves == 1
    assert p.tax_by_class == {"unknown-reference": 2, "ring-failure": 1}
    assert p.tax_total == 3
    assert p.repeats_on_solved == 1 and p.repeats_of_class == 1
    assert p.repeats_of_name == 1
    assert p.terminal_by_class == {"incomplete-proof": 1}
    assert p.last5_by_class == {"ring-failure": 1, "incomplete-proof": 1}
    assert p.first_error_by_class == {
        "unknown-reference": 1,
        "ring-failure": 1,
    }
    assert p.heaviest_solved[0] == (3, a)
    assert p.as_dict()["taxTotal"] == 3


def _cache(entries: list[tuple[str, str]]) -> str:
    """`(model, content)` pairs as a minimal cache.yaml text."""
    out: list[str] = []
    for model, content in entries:
        body = (
            "fun: check_assisted\nargs: {}\n"
            if model == "__compute__"
            else "hi"
        )
        out.append(
            "- input:\n    request:\n      chat:\n        - role: user\n"
            "          content: |\n"
            + "".join(f"            {line}\n" for line in body.splitlines())
            + f"      options:\n        model: {model}\n"
            "    iter: 1\n  output:\n    outputs:\n      - content: |\n"
            + "".join(f"          {line}\n" for line in content.splitlines())
        )
    return "".join(out)


def test_turns_of_cache_pairs_messages_with_verdicts() -> None:
    text = _cache(
        [
            ("m", "I rely on rocq-00006 and rocq-00010.\n```rocq\nlia.\n```"),
            ("__compute__", f"success: false\nerror_message: {_RING!r}\n"),
            ("m", "tool call, no proposal"),
            ("m", "```rocq\nnra.\n```"),
            ("__compute__", "success: true\n"),
        ]
    )
    with tempfile.TemporaryDirectory() as tmp:
        cache = Path(tmp) / "cache.yaml"
        cache.write_text(text)
        turns = dg.turns_of_cache(cache)
    assert [t.cited for t in turns] == [
        ("rocq-00006", "rocq-00010"),
        (),
        (),
    ]
    assert turns[0].verdict_class == "ring-failure" and not turns[0].success
    assert turns[1].verdict_class is None
    assert turns[2].success


def _rec(name: str, inp: int, cached: int, out: int, reqs: int) -> CellRecord:
    bench, _, model, seed = name.split("__")
    return CellRecord(
        name=name,
        bench=bench,
        seed=seed.removeprefix("seed"),
        arm="core-medium",
        model=model,
        params={},
        status="done",
        solved=True,
        input=inp,
        cached=cached,
        output=out,
        requests=reqs,
        cost=0.0,
        platform_failed=False,
    )


def test_per_request_decomposition() -> None:
    cells = [
        _rec("p1__a__gpt-5.6-luna__seed0", 1000, 600, 100, 2),
        _rec("p2__a__gpt-5.6-luna__seed0", 3000, 2400, 300, 2),
    ]
    pr = dg.per_request(cells)
    assert pr.requests == 4
    assert abs(pr.uncached - 250) < 1e-9
    assert abs(pr.cached - 750) < 1e-9
    assert abs(pr.output - 100) < 1e-9
    rates = dg.Rates.of("gpt-5.6-luna")
    assert (
        abs(
            pr.usd
            - (250 * rates.input + 750 * rates.cached + 100 * rates.output)
        )
        < 1e-12
    )
    assert dg.per_request([]).requests == 0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
