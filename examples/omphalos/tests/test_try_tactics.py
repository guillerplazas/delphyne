"""
Smoke test for `pytanque_utils.try_tactics` (the native TryTactics
probe). Pure pytanque — no LLM, no Delphyne — so it can run anytime.

Run `python -m tests.test_try_tactics` (from any cwd). Exercises, on
the demo problem `algebra_binomnegdiscrineq_10alt28asqp1` (a machinery
test, so using a demo problem is fine):

  1. happy path: mixed candidates including a duplicate, a tactic that
     fails on an R goal (`lia`), a structural opener, and a closer
     (`nra`);
  2. prefix failure: a bogus tactic in the prefix;
  3. empty candidate list;
  4. over-cap candidate list (cap + 1 entries).
"""

import runtime.pytanque_utils as pt  # noqa: E402

_PROBLEM = "miniF2F/valid/algebra/algebra_binomnegdiscrineq_10alt28asqp1.v"
_THEOREM = "algebra_binomnegdiscrineq_10alt28asqp1"


def _banner(title: str) -> None:
    print(f"\n{'=' * 66}\n{title}\n{'=' * 66}")


def main() -> None:
    _banner("1. Happy path: prefix `intros a.`, mixed candidates")
    print(
        pt.try_tactics(
            _PROBLEM,
            _THEOREM,
            "intros a.",
            [
                "nra.",
                "lia.",
                "nra.",  # exact duplicate of #1 -> skipped
                "replace (a ^ 2) with (a * a) by ring.",
                "induction a",  # no final `.` -> skipped
            ],
        )
    )

    _banner("2. Prefix failure: bogus tactic in the prefix")
    print(
        pt.try_tactics(
            _PROBLEM,
            _THEOREM,
            "intros a. bogus_tactic_name.",
            ["nra."],
        )
    )

    _banner("3. Empty candidate list")
    print(pt.try_tactics(_PROBLEM, _THEOREM, "intros a.", []))

    _banner("4. Over-cap candidate list (cap + 1 distinct entries)")
    over_cap = [
        f"assert (H{i} : {i} = {i}) by reflexivity."
        for i in range(pt.MAX_TRY_TACTICS_CANDIDATES + 1)
    ]
    report = pt.try_tactics(_PROBLEM, _THEOREM, "intros a.", over_cap)
    print(report)
    assert "1 candidate(s) beyond" in report, "cap notice missing"

    print("\nAll try_tactics smoke scenarios ran.")


if __name__ == "__main__":
    main()
