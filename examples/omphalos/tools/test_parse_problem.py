"""
Unit tests for `pytanque_utils.parse_problem`'s definitions capture.

Pure Python, no Rocq, no API: part of `make test-unit`.
"""

# pyright: strict

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytanque_utils as pt  # noqa: E402

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent


def _all_problem_files() -> list[Path]:
    return sorted((_OMPHALOS_DIR / "miniF2F").rglob("*.v"))


def test_default_is_the_historical_prompt() -> None:
    for path in _all_problem_files():
        spec = pt.parse_problem(str(path))
        assert spec.definitions == "", path


def test_every_preamble_is_captured() -> None:
    """
    Every file whose preamble holds more than imports/scopes yields a
    non-empty `definitions`; every other file yields "". The count of
    the former is the 42 the defs experiment was built on, plus the one
    file (`amc12a_2003_p23`) whose `Module` line the old allow-list
    regex missed — 43 in total.
    """
    with_defs: list[str] = []
    for path in _all_problem_files():
        spec = pt.parse_problem(str(path), show_definitions=True)
        text = path.read_text()
        preamble = text[: text.index(f"Theorem {path.stem}")]
        residue = pt._IMPORT_LINE_RE.sub(  # pyright: ignore[reportPrivateUsage]
            "",
            pt._strip_comments(preamble),  # pyright: ignore[reportPrivateUsage]
        ).strip()
        assert bool(spec.definitions) == bool(residue), path
        if spec.definitions:
            with_defs.append(path.stem)
    assert len(with_defs) == 43, len(with_defs)
    assert "amc12a_2003_p23" in with_defs


def test_module_line_survives() -> None:
    path = _OMPHALOS_DIR / "miniF2F/test/amc/amc12a_2003_p23.v"
    spec = pt.parse_problem(str(path), show_definitions=True)
    assert "Module NS := FSetWeakList.Make(Nat_as_OT)." in spec.definitions


def test_fixpoint_and_notation_kept_verbatim() -> None:
    path = (
        _OMPHALOS_DIR / "miniF2F/test/induction/induction_sumkexp3eqsumksq.v"
    )
    spec = pt.parse_problem(str(path), show_definitions=True)
    assert spec.definitions.startswith("Fixpoint sum_to")
    assert "Notation" in spec.definitions
    assert "Require Import" not in spec.definitions
    assert spec.imports == "Require Import Coq.Arith.Arith."
    # Imports are untouched by the flag.
    assert spec.imports == pt.parse_problem(str(path)).imports


def test_split_focus() -> None:
    """
    The bullet/brace splitter behind `_run_guarded`: leading focusing
    tokens come off (each a complete, non-diverging proof step), the
    guarded remainder keeps its trailing `.`. A bare bullet stays in
    the remainder — unguarded, but a lone focus step cannot diverge.
    """
    split = pt._split_focus  # pyright: ignore[reportPrivateUsage]
    assert split("- nia.") == (["-"], "nia.")
    assert split("-- lia.") == (["--"], "lia.")
    assert split("- { field_simplify. }") == (["-", "{"], "field_simplify. }")
    assert split("nia.") == ([], "nia.")
    assert split("2: nia.") == ([], "2: nia.")
    assert split("-") == ([], "-")
    assert split("{ }") == (["{"], "}")


def test_nested_comments_are_stripped() -> None:
    strip = pt._strip_comments  # pyright: ignore[reportPrivateUsage]
    assert strip("a (* x (* y *) z *) b") == "a  b"
    assert strip("no comments") == "no comments"


def main() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
