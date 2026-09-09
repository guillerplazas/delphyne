"""
Unit tests for `ace_repairs` (pure Python — no LLM, no Rocq): the
pairing of consecutive attempts into verifier-accepted repairs (replace,
insert-before, no change, give-up), grouping keys, and the digest
rendering. Part of `make test-unit`.
"""


# pyright: strict

import ace.ace_repairs as rp  # noqa: E402

_UNKNOWN = (
    "(-1, 'The reference omega was not found in the current\nenvironment.')"
)
_RING = "(-1, 'Tactic failure: not a valid ring equation.')"


def _att(
    tactics: list[str],
    *,
    success: bool = False,
    idx: int | None = None,
    msg: str | None = None,
) -> rp.Attempt:
    return rp.Attempt(
        tactics=tuple(tactics),
        success=success,
        failing_index=idx,
        failing_tactic=None if idx is None else tactics[idx],
        error_message=msg,
        goals=("a : nat\n|- a <= 3",) if not success else (),
    )


def test_replace_and_solve() -> None:
    a = _att(["intros.", "omega."], idx=1, msg=_UNKNOWN)
    b = _att(["intros.", "lia."], success=True)
    reps = rp.repairs_of_cell("p", "p__c__m__seed0", [a, b])
    assert len(reps) == 1
    r = reps[0]
    assert r.before == ("omega.",) and r.after == ("lia.",)
    assert r.outcome == "solved" and r.unknown_name == "omega"
    assert r.key == ("unknown-reference", "`omega`")
    assert r.goal == "a <= 3"


def test_insert_before_failing_tactic_advances() -> None:
    a = _att(["intros.", "ring.", "lia."], idx=1, msg=_RING)
    b = _att(["intros.", "unfold Rsqr.", "ring.", "lia."], idx=3, msg=_RING)
    reps = rp.repairs_of_cell("p", "c", [a, b])
    assert len(reps) == 1
    assert reps[0].before == ("ring.",)
    assert reps[0].after == ("unfold Rsqr.", "ring.")
    assert reps[0].outcome == "advanced"
    assert reps[0].key == ("ring-failure", "`ring`")


def test_no_repair_cases() -> None:
    a = _att(["intros.", "ring."], idx=1, msg=_RING)
    # Same failure again: no advance.
    assert rp.repairs_of_cell("p", "c", [a, a]) == []
    # The failing tactic survived unchanged (a change elsewhere).
    b = _att(["intros x.", "ring."], idx=1, msg=_RING)
    assert rp.repairs_of_cell("p", "c", [a, b]) == []
    # Giving up is not a repair.
    c = _att(["intros.", "admit.", "ring."], idx=2, msg=_RING)
    assert rp.repairs_of_cell("p", "c", [a, c]) == []
    # Qed. rejections are not tactic repairs.
    q = rp.Attempt(("intros.", "Qed."), False, 1, "Qed.", "(-1, 'x')", ())
    assert rp.repairs_of_cell("p", "c", [q, b]) == []


def test_grouping_and_digest() -> None:
    a = _att(["intros.", "omega."], idx=1, msg=_UNKNOWN)
    b = _att(["intros.", "lia."], success=True)
    reps = rp.repairs_of_cell("p1", "p1__c__m__seed0", [a, b])
    reps += rp.repairs_of_cell("p2", "p2__c__m__seed0", [a, b])
    groups = rp.group_repairs(reps)
    assert len(groups) == 1
    g = groups[0]
    assert (g.fine_class, g.trigger, g.repairs, g.problems, g.solved) == (
        "unknown-reference",
        "`omega`",
        2,
        2,
        2,
    )
    assert g.after_heads == (("lia", 2),)
    text = rp.render_repairs(reps, cells=2)
    assert "unknown-reference at `omega`" in text
    assert "`omega.` → `lia.`" in text
    assert rp.render_repairs([], cells=0) == ""
    assert rp.name_replacements(reps)["omega"]["lia"] == 2


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
