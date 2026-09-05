"""
Unit tests for `ace_triggers` (pure Python — no LLM, no Rocq).

Covers: table construction and its refusals (unknown id, unknown
class, bad regex, over-long pattern), the scoring order (name >
pattern > class, goal patterns only rank), the hint cap and the empty
cases, the self-contained YAML round trip and its hash, `coverage`
over a synthetic recorded run, and the hinted verifier's feedback
object. Part of `make test-unit`.
"""

# pyright: strict

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ace_triggers as tr  # noqa: E402
from ace_playbook import Bullet, Playbook  # noqa: E402

_UNKNOWN = (
    "(-1, 'The reference omega was not found in the current\nenvironment.')"
)
"""A real line break, as Rocq's pretty-printer wraps it."""
_RING = "(-1, 'Tactic failure: not a valid ring equation.')"
_SYNTAX = "(-1, 'Syntax error: [tactic] expected after [ltac_use_default].')"


def _playbook() -> Playbook:
    return Playbook(
        next_id=4,
        bullets=[
            Bullet(
                id="rocq-00001",
                section="pitfalls",
                content="`omega` does not exist; use `lia`.",
            ),
            Bullet(
                id="rocq-00002",
                section="tactics",
                content="`ring` proves equalities only; use `nra` for `<=`.",
            ),
            Bullet(
                id="rocq-00003",
                section="strategy",
                content="Strengthen the induction invariant.",
            ),
        ],
    )


def _table() -> tr.TriggerTable:
    return tr.TriggerTable.build(
        _playbook(),
        [
            tr.TriggerSpec(
                "rocq-00001", classes=["unknown-reference"], names=["`omega`"]
            ),
            tr.TriggerSpec(
                "rocq-00002",
                classes=["ring-failure", "syntax-error"],
                patterns=["not a valid ring equation"],
                goal_patterns=[r"<="],
            ),
        ],
    )


def test_build_refusals() -> None:
    pb = _playbook()
    for bad in (
        [tr.TriggerSpec("rocq-00099")],
        [tr.TriggerSpec("rocq-00001", classes=["nonsense"])],
        [tr.TriggerSpec("rocq-00001", patterns=["("])],
        [tr.TriggerSpec("rocq-00001", patterns=["x" * 200])],
        [tr.TriggerSpec("rocq-00001"), tr.TriggerSpec("rocq-00001")],
    ):
        try:
            tr.TriggerTable.build(pb, bad)
        except tr.TriggerError:
            continue
        raise AssertionError(f"accepted {bad}")


def test_unmentioned_bullet_is_unarmed() -> None:
    table = _table()
    assert [e.bullet_id for e in table.entries] == [
        "rocq-00001",
        "rocq-00002",
        "rocq-00003",
    ]
    assert not table.entries[2].armed
    assert table.entries[0].names == ("omega",)


def test_scoring_order() -> None:
    table = _table()
    # A name match outranks everything; the class-only match is last.
    ids = tr.select_ids(
        table,
        error_class="unknown-reference",
        coarse_class="unknown-reference",
        error_message=_UNKNOWN,
        failing_tactic="omega.",
        goals=(),
    )
    assert ids == ["rocq-00001"], ids
    # Pattern (2) plus class (1) plus goal (1) for the ring bullet.
    ids = tr.select_ids(
        table,
        error_class="ring-failure",
        coarse_class="other",
        error_message=_RING,
        failing_tactic="ring.",
        goals=("x <= y",),
    )
    assert ids == ["rocq-00002"], ids
    e = table.entries[1]
    assert (
        tr.score(
            e,
            error_class="ring-failure",
            coarse_class="other",
            error_message=_RING,
            failing_tactic="ring.",
            goals=("x <= y",),
        )
        == tr.SCORE_PATTERN + tr.SCORE_CLASS + tr.SCORE_GOAL
    )
    # A goal pattern alone never fires.
    assert (
        tr.score(
            e,
            error_class="timeout",
            coarse_class="timeout",
            error_message="Timeout!",
            failing_tactic="nia.",
            goals=("x <= y",),
        )
        == 0
    )
    # A bullet with goal patterns is silent when the goal does not
    # match (precondition), even on a class match ...
    ids = tr.select_ids(
        table,
        error_class="syntax-error",
        coarse_class="syntax-error",
        error_message=_SYNTAX,
        failing_tactic="set p := 1.",
        goals=("x = y",),
    )
    assert ids == [], ids
    # ... and fires when it does.
    ids = tr.select_ids(
        table,
        error_class="syntax-error",
        coarse_class="syntax-error",
        error_message=_SYNTAX,
        failing_tactic="set p := 1.",
        goals=("x <= y",),
    )
    assert ids == ["rocq-00002"], ids
    # A name match bypasses the goal precondition.
    gated = tr.TriggerTable.build(
        _playbook(),
        [tr.TriggerSpec("rocq-00001", names=["omega"], goal_patterns=["zzz"])],
    )
    assert tr.select_ids(
        gated,
        error_class="unknown-reference",
        coarse_class="unknown-reference",
        error_message=_UNKNOWN,
        failing_tactic="omega.",
        goals=("x = y",),
    ) == ["rocq-00001"]


def test_rule_2_classes_are_a_precondition() -> None:
    # The ring bullet lists classes; under rule 2 its pattern cannot
    # summon it on a rejection of another class ...
    table = tr.TriggerTable.build(
        _playbook(),
        [
            tr.TriggerSpec(
                "rocq-00002",
                classes=["syntax-error"],
                patterns=["not a valid ring equation"],
            ),
            tr.TriggerSpec("rocq-00001", names=["omega"], classes=["timeout"]),
        ],
    )
    for rule, expected in ((1, ["rocq-00002"]), (2, [])):
        got = tr.select_ids(
            table,
            error_class="ring-failure",
            coarse_class="other",
            error_message=_RING,
            failing_tactic="ring.",
            goals=(),
            rule=rule,
        )
        assert got == expected, (rule, got)
    # ... but a name match bypasses the class precondition.
    assert tr.select_ids(
        table,
        error_class="unknown-reference",
        coarse_class="unknown-reference",
        error_message=_UNKNOWN,
        failing_tactic="omega.",
        goals=(),
        rule=2,
    ) == ["rocq-00001"]


def test_select_hints_cap_and_empty() -> None:
    table = _table()
    hints = tr.select_hints(
        table,
        error_message=_UNKNOWN,
        failing_tactic="omega.",
        goals=(),
        k=1,
    )
    assert [h.id for h in hints] == ["rocq-00001"]
    assert hints[0].content.startswith("`omega`")
    assert (
        tr.select_hints(
            table, error_message=None, failing_tactic=None, goals=()
        )
        == []
    )
    assert (
        tr.select_hints(
            table,
            error_message="(-1, 'Timeout!')",
            failing_tactic="nia.",
            goals=(),
        )
        == []
    )
    assert tr.render_hints(hints) == (
        "- [rocq-00001] `omega` does not exist; use `lia`."
    )


def test_roundtrip_and_hash() -> None:
    table = _table()
    text = table.dumps()
    back = tr.TriggerTable.loads(text)
    assert back == table
    assert back.sha256() == table.sha256()
    assert tr.parse_table(text) is tr.parse_table(text)
    assert back.playbook_sha256 == _playbook().sha256()


def _write_cache(cell: Path, messages: list[str]) -> None:
    cell.mkdir(parents=True)
    entries: list[str] = []
    for msg in messages:
        body = (
            "- input:\n    request:\n      chat:\n        - role: user\n"
            "          content: |\n            fun: check_assisted\n"
            "            args:\n              file: f.v\n"
            "      options:\n        model: __compute__\n"
            "    iter: 1\n  output:\n    outputs:\n      - content: |\n"
            "          success: false\n"
            "          failing_tactic: 'omega.'\n"
            f"          error_message: {msg!r}\n"
            "          remaining_goals:\n"
            "            - 'x <= y'\n"
        )
        entries.append(body)
    (cell / "cache.yaml").write_text("".join(entries))


def test_coverage_on_synthetic_run() -> None:
    table = _table()
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp) / "run"
        (run / "configs").mkdir(parents=True)
        (run / "results_summary.csv").write_text(
            "bench_name,success\np1,True\np2,False\n"
        )
        _write_cache(
            run / "configs" / "p1__core-medium__m__seed0",
            [_UNKNOWN, _RING],
        )
        _write_cache(
            run / "configs" / "p2__core-medium__m__seed0",
            ["(-1, 'Timeout!')"],
        )
        cov = tr.coverage(table, [run])
    assert cov.verdicts == 3 and cov.covered == 2
    assert cov.fired == {"rocq-00001": 1, "rocq-00002": 1, "rocq-00003": 0}
    assert cov.unarmed == ("rocq-00003",)
    assert cov.silent == ()
    assert cov.by_class["timeout"] == (1, 0)
    assert "rocq-00003" in cov.render()


def test_hinted_feedback_carries_hints() -> None:
    from prove_ace import HintedFeedback

    fb = HintedFeedback(success=False, hints=[tr.Hint("rocq-00001", "x")])
    assert fb.hints[0].id == "rocq-00001"
    assert not fb.finished and fb.remaining_goals == []


def test_taxonomy_rendering_names_every_class() -> None:
    text = tr.render_taxonomy()
    for cls in tr.KNOWN_CLASSES:
        assert f"`{cls}`" in text, cls


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
