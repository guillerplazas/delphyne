"""Re-run synthetic Rocq counterexamples to specific learned claims.

These are small constructed propositions, never extra benchmark problems.
Expected tactic failures are diagnostic observations, not solver outcomes.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

from .common import CAMPAIGN, REPORT, read, save, sha

EXPECTED = {
    "square_nra": True,
    "square_affine_nra": False,
    "square_product_nra": False,
    "square_affine_explicit_lemma": True,
    "square_product_explicit_lemma": True,
    "vm_introspection_vs_execution": True,
    "set_unparenthesized": False,
    "set_parenthesized": True,
    "log_field_only": False,
    "log_rewrite_power": True,
}


def run_one(name: str) -> dict[str, Any]:
    prior = read(CAMPAIGN / "rule_probes" / (name + ".json"))
    executable = shutil.which("rocq")
    if executable is None:
        raise ValueError("Missing Rocq compiler")
    with tempfile.TemporaryDirectory(prefix="ace-rule-") as temporary:
        source = Path(temporary) / "Probe.v"
        source.write_text(prior["source"])
        process = subprocess.run(
            [executable, "compile", "-q", str(source)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        actual = process.returncode == 0
        if actual != EXPECTED[name] or actual != (prior["exit_code"] == 0):
            raise ValueError("Synthetic tactic outcome changed: " + name)
        if (
            name == "vm_introspection_vs_execution"
            and "vm_compute not a defined object" not in process.stdout
        ):
            raise ValueError("Introspection diagnosis was not reproduced")
        return dict(
            name=name,
            compiles=actual,
            expected=EXPECTED[name],
            source_sha=sha(source),
            compiler_sha=sha(Path(executable)),
            stdout=process.stdout,
            decisive_error=process.stderr.split("Error:", 1)[-1].strip()
            if not actual
            else None,
        )


def run() -> None:
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run_one, EXPECTED))
    save(
        REPORT / "rule_probe_certification.json",
        dict(
            probes=results,
            paid_calls=0,
            conclusions=[
                "A simple square is solvable by nra; the tested affine and product squares need an explicit nonnegativity lemma. The old generic warning is overbroad, but its fallback is useful on the compound cases.",
                "About vm_compute is object introspection, not a test of whether the built-in tactic executes. The same Rocq file reports no defined object and successfully checks the tactic proof.",
                "Unparenthesized set syntax is rejected, while the parenthesized form works. The historical pose workaround is also a valid alternative; it must not be labeled false.",
                "Field alone does not prove the tested logarithm identity. Rewriting the power logarithm before ring does.",
            ],
            exploratory_exclusion="square_product_lemma used unsupported nra [lemma] syntax in an initial manual probe. Its failure is preserved, but is not counted as evidence about the explicit-lemma method. The corrected explicit-lemma probes both compile.",
        ),
    )
    print(dict(probes=len(results), reproduced=True, paid_calls=0))


if __name__ == "__main__":
    run()
