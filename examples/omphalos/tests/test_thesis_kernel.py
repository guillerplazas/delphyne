"""Regression checks for independent compilation of binder-style headers."""

import pytest

from experiments.ace_thesis.verify_results import (
    compilation_source as sealed_source,
)
from tools.maintenance.ace_thesis_kernel import compilation_source


@pytest.mark.parametrize(
    "statement,proof",
    [
        ("Theorem demo : True.", "exact I."),
        ("Theorem demo\n  (n : nat) : n = n.", "reflexivity."),
        ("Theorem demo {n : nat} : n = n.", "reflexivity."),
    ],
)
def test_original_declaration_is_preserved(statement: str, proof: str) -> None:
    problem = statement + "\nProof.\nAdmitted."
    source = compilation_source(problem, "demo", proof)
    assert statement + "\nProof.\n" + proof + "\nQed." in source
    assert source.endswith("Print Assumptions demo.\n")
    if statement == "Theorem demo : True.":
        assert source == sealed_source(problem, "demo", proof)


def test_wrong_name_and_admission_still_fail() -> None:
    problem = "Theorem demo_extra (n : nat) : n = n.\nProof.\nAdmitted."
    with pytest.raises(ValueError, match="Wrong source theorem"):
        compilation_source(problem, "demo", "reflexivity.")
    with pytest.raises(ValueError, match="Unsafe proof command"):
        compilation_source(problem, "demo_extra", "admit.")
    with pytest.raises(ValueError, match="exactly one"):
        compilation_source(
            problem + "\nProof.\nAdmitted.", "demo_extra", "auto."
        )
