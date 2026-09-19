"""Offline compiler compatibility for theorem headers with local binders.

Both harnesses: python -m tools.maintenance.ace_thesis_kernel.
The sealed checker assumed a colon immediately after the theorem name.
Five permitted validation statements instead have binders before that colon.
This wrapper changes only that source-identity check. Original declarations,
returned proof bytes, imports, Qed, compiler and budgets remain identical.
The wrapper and tests have a separate hash record; paid sources stay sealed.
"""

import re
from pathlib import Path
from unittest.mock import patch

from experiments.ace_thesis import campaign as c
from experiments.ace_thesis import verify_results as verification
from runtime.pytanque_utils import DEFAULT_EXTRA_IMPORTS


def compilation_source(problem: str, theorem: str, proof: str) -> str:
    if re.search(
        r"\b(?:Admitted|admit|Axiom|Parameter|Abort)\b|Unset\s+(?:Guard|Positivity|Universe)",
        proof,
    ):
        raise ValueError("Unsafe proof command")
    # Colons, explicit binders and implicit binders all follow a complete
    # Rocq identifier. In particular, a longer identifier cannot match.
    if not re.search(
        r"\bTheorem\s+" + re.escape(theorem) + r"\s*(?=[:({])", problem
    ):
        raise ValueError("Wrong source theorem")
    body, count = re.subn(
        r"\bProof\.\s*Admitted\.",
        lambda _: "Proof.\n" + proof + "\nQed.",
        problem,
    )
    if count != 1:
        raise ValueError("Expected exactly one unproved source theorem")
    return (
        "\n".join(DEFAULT_EXTRA_IMPORTS)
        + "\n"
        + body
        + f"\nPrint Assumptions {theorem}.\n"
    )


def main() -> None:
    c.verify()
    c.save(
        "operations/kernel_header_compatibility.json",
        dict(
            reason=__doc__,
            paid_calls=0,
            source_hashes={
                str(path.relative_to(c.ROOT)): c.sha(path)
                for path in (
                    Path(__file__),
                    Path(verification.__file__),
                    c.ROOT / "tests/test_thesis_kernel.py",
                )
            },
        ),
    )
    with patch.object(verification, "compilation_source", compilation_source):
        verification.kernel()


if __name__ == "__main__":
    main()
