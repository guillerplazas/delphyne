"""
Unit tests for `ace_evidence` (pure Python — no LLM, no Rocq).

Covers: the digest's ranking, caps and empty rendering; identifier
extraction from a line-wrapped Rocq message; tactic heads; the reading
of the three `Locate` answers observed on 2026-09-02; the primitive
allow-list; the pitfalls extraction; import signatures. Part of
`make test-unit`.
"""


# pyright: strict

import tempfile
from pathlib import Path


import ace.ace_evidence as ev  # noqa: E402


def _v(bench: str, cls: str, tactic: str, msg: str) -> ev.FailedVerdict:
    return ev.FailedVerdict(bench, cls, tactic, msg)


def test_unknown_identifier_wrapped() -> None:
    wrapped = (
        "(-1, 'The variable functional_extensionality was not found in the"
        " current\nenvironment.')"
    )
    assert ev.unknown_identifier(wrapped) == "functional_extensionality"
    assert (
        ev.unknown_identifier(
            "The reference norm_num was not found in the current environment."
        )
        == "norm_num"
    )
    assert ev.unknown_identifier("Syntax error: whatever") is None


def test_tactic_head() -> None:
    assert ev.tactic_head("norm_num in Hsum |- *.") == "norm_num … in"
    assert ev.tactic_head("- set p := 15^233.") == "set … :="
    assert ev.tactic_head("{ apply functional_extensionality.") == "apply"
    assert ev.tactic_head("assert (Hc : 0 < c)%nat by nia.") == "assert … by"
    assert ev.tactic_head("2: vm_compute.") == "vm_compute"
    assert ev.tactic_head("   ") == "(empty)"


def test_digest_ranking_caps_and_empty() -> None:
    assert ev.render_digest([], attempts=0) == ""
    verdicts = [
        _v(
            "p1",
            "unknown-reference",
            "norm_num.",
            "The reference norm_num was not found in the current environment.",
        ),
        _v(
            "p2",
            "unknown-reference",
            "norm_num in H.",
            "The reference norm_num was not found in the current\nenvironment.",
        ),
        _v(
            "p2",
            "unknown-reference",
            "omega.",
            "The reference omega was not found in the current environment.",
        ),
        _v("p1", "syntax-error", "set p := 3.", "Syntax error: x"),
        _v("p1", "syntax-error", "set q := 4.", "Syntax error: y"),
        _v("p1", "syntax-error", "cbv [a, b].", "Syntax error: z"),
        _v(
            "p3", "prover-crash", "vm_compute.", "No response from pet process"
        ),
    ]
    summary = ev.summarize(verdicts)
    # unknown-reference spans 2 problems -> first; syntax-error has more
    # verdicts but one problem -> after prover-crash? No: prover-crash
    # has 1 problem / 1 verdict, syntax-error 1 problem / 3 verdicts.
    assert [c.label for c in summary] == [
        "unknown-reference",
        "syntax-error",
        "prover-crash",
    ]
    unk = summary[0]
    assert unk.names == (("norm_num", 2), ("omega", 1))
    syn = summary[1]
    assert syn.heads[0][0] == "set … :=" and syn.heads[0][1] == 2
    assert syn.heads[0][2] == "set p := 3."  # shortest example
    # caps
    capped = ev.summarize(verdicts, max_classes=1, max_items=1)
    assert len(capped) == 1 and len(capped[0].names) == 1
    text = ev.render_digest(verdicts, attempts=3)
    assert text.startswith("3 attempt(s) on this pool so far, 7 failed")
    assert (
        "`norm_num` (2)" in text
        and "`set … :=` (2; e.g. `set p := 3.`)" in text
    )
    # order-independence: a permutation renders identically
    assert ev.render_digest(list(reversed(verdicts)), attempts=3) == text


def test_grounding_verdicts_and_allowlist() -> None:
    assert (
        ev.grounding_verdict("Constant Stdlib.Reals.R_sqrt.pow2_sqrt")
        == "grounded"
    )
    assert (
        ev.grounding_verdict(
            "Ltac Stdlib.micromega.Lia.nia\n  (shorter name…)"
        )
        == "grounded"
    )
    assert ev.grounding_verdict("No object of basename norm_num") == "missing"
    assert ev.grounding_verdict("Rocq rejected the command: boom") == "error"
    assert ev.grounding_verdict("Failed to open session: x") == "error"
    names = [
        "`pow2_sqrt`",
        "Nat.div_mod_eq.",
        "assert",
        "(x + y)%nat",
        "pow2_sqrt",
        "lia",
        "Rle_0_sqr'",
    ]
    assert ev.checkable_references(names) == [
        "pow2_sqrt",
        "Nat.div_mod_eq",
        "Rle_0_sqr'",
    ]
    assert ev.locate_command("Nat.div_mod_eq") == "Locate Nat.div_mod_eq."
    # Built-in tactic keywords are not objects (`Locate decompose.` answers
    # `No object`); the x5 run refused one ADD for exactly this reason.
    assert ev.checkable_references(["decompose", "firstorder", "elim"]) == []


def test_known_guidance() -> None:
    text = ev.known_guidance()
    assert text.startswith("## Pitfalls")
    assert "Name everything you introduce" in text
    assert "## Budget" not in text and "{{" not in text


def test_import_signature_and_representatives() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a.v"
        b = Path(tmp) / "b.v"
        c = Path(tmp) / "c.v"
        a.write_text(
            "Require Import Reals.\nOpen Scope R_scope.\nTheorem t : True. Admitted.\n"
        )
        b.write_text("Require   Import Reals.\nTheorem u : True. Admitted.\n")
        c.write_text(
            "From Coq Require Import Arith.\nRequire Import Lia.\nTheorem w : True. Admitted.\n"
        )
        assert ev.import_signature(a) == "Require Import Reals."
        assert ev.import_signature(a) == ev.import_signature(b)
        assert (
            ev.import_signature(c)
            == "From Coq Require Import Arith.\nRequire Import Lia."
        )
        pool = {"a": (str(a), "t"), "b": (str(b), "u"), "c": (str(c), "w")}
        assert ev.representative_files(pool) == [(str(a), "t"), (str(c), "w")]


def main() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
