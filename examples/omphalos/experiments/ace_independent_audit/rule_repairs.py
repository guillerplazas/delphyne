"""Measured repair of three learned tactic claims, followed by 80 train cells.

This is a manually audited book ablation, not a new autonomous ACE author.
Only the three diagnosed A2 bullets change. The original A2 and A0 train
cells provide controls; no new controls, replicates or validation cells are
added. The exact sources and repairs are frozen before running this arm.
"""

from dataclasses import replace
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

from . import campaign as c
from .analysis import metrics, paired
from .common import CAMPAIGN, REPORT, now, read, save, sha
from .families import mapping
from .fresh import receipts, solver_rows
from .mechanisms import characterize
from .workflow import book, save_book, launch

REPAIRS = {
    "rocq-00009": "WHEN an induction hypothesis `a < b` must be multiplied by a real factor with `0 < f`, DO first try `nra` on the required polynomial inequality. If it does not close, derive `a * f < b * f` explicitly with `Rmult_lt_compat_r`, then use `nra` for the remaining algebra. PROVIDED the factor is strictly positive; explicit monotonicity is a fallback, not a universal requirement.\n",
    "rocq-00024": "WHEN `H : Rabs x = c` must yield a polynomial square fact, DO assert `Rabs x = Rabs c` using `rewrite (Rabs_right c) by lra; exact H`, apply `Rsqr_eq_asb_1`, then `unfold Rsqr` in the result before `nra`. PROVIDED `0 <= c`; target `c` explicitly so rewriting does not instead demand the unknown sign of `x`.\n",
    "rocq-00058": "WHEN `apply Extensionality_Ensembles` leaves `Same_set U A B`, DO use `unfold Same_set; split; intros x Hx`, then prove membership in the other set separately in each direction. PROVIDED the current goal is the generated `Same_set`; its unfolded form is a conjunction of two inclusions, so split before introducing an element.\n",
}

EXTRA = {
    "same_set_learned_imports": False,
    "same_set_repaired_imports": True,
    "rabs_learned_imports": False,
    "rabs_repaired_imports": True,
    "positive_multiply_nra_imports": True,
    "square_product_p1_imports": True,
}


def certify() -> None:
    executable = shutil.which("rocq")
    if executable is None:
        raise ValueError("Rocq is required")
    results: list[dict[str, Any]] = []
    for name, expected in EXTRA.items():
        previous = read(CAMPAIGN / "rule_probes" / (name + ".json"))
        with tempfile.TemporaryDirectory(prefix="ace-repair-") as tmp:
            source = Path(tmp) / "Probe.v"
            source.write_text(previous["source"])
            process = subprocess.run(
                [executable, "compile", "-q", str(source)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if (process.returncode == 0) != expected:
                raise ValueError("Learned-rule diagnosis changed: " + name)
            results.append(
                dict(
                    name=name,
                    compiles=expected,
                    source_sha=sha(source),
                    compiler_sha=sha(Path(executable)),
                    stdout=process.stdout,
                    decisive_error=process.stderr.split("Error:")[-1].strip()
                    if not expected
                    else None,
                )
            )
    save(
        REPORT / "rule_repair_certification.json",
        dict(
            probes=results,
            paid_calls=0,
            excluded="The six first drafts without the _imports suffix omitted the theorem-domain imports and are excluded. Their missing-symbol errors are not evidence about tactic validity.",
            conclusions={
                "rocq-00009": "nra proves the quantified positive-multiplication proposition directly. The explicit lemma remains a useful fallback; the blanket negative claim is too broad.",
                "rocq-00024": "The untargeted Rabs_right rewrite fails under exactly the advertised nonnegative-right-side assumptions. Explicitly targeting c succeeds.",
                "rocq-00058": "Unfolding Same_set exposes a conjunction, not an immediately quantified proposition. The published intro-before-split order fails; split-before-intros compiles.",
                "P1/rocq-00005": "The short book's product-form Rle_0_sqr assertion compiles for a universally quantified real variable.",
            },
            source_chain={
                "rocq-00009": {
                    "theorem": "induction_pord1p1on2powklt5on2",
                    "step": 4,
                    "auditor": 0,
                },
                "rocq-00024": {
                    "theorem": "amc12a_2002_p13",
                    "step": 14,
                    "auditor": 1,
                },
                "rocq-00058": {
                    "theorem": "mathd_algebra_224",
                    "step": 39,
                    "auditor": 4,
                },
            },
            limitations="These checks establish local correctness or overbreadth of the stated tactic recipes, not a coverage or cost improvement. The separately registered R1 benchmark measures the joint repair's effect.",
        ),
    )


def prepare() -> None:
    certify()
    original = read(CAMPAIGN / "books/A2_frozen.json")
    pb = book(original["playbook"])
    if not set(REPAIRS) <= {b.id for b in pb.bullets}:
        raise ValueError("Diagnosed original rules are missing")
    corrected = replace(
        pb,
        bullets=[
            replace(b, content=REPAIRS[b.id]) if b.id in REPAIRS else b
            for b in pb.bullets
        ],
    )
    filename = "books/R1_verified_rules.json"
    save_book(
        CAMPAIGN / filename,
        corrected,
        dict(
            source_book="books/A2_frozen.json",
            source_sha=sha(CAMPAIGN / "books/A2_frozen.json"),
            training_theorems=original["training_theorems"],
            repairs=REPAIRS,
            certificate_sha=sha(REPORT / "rule_repair_certification.json"),
            preparation="Same forty-source Sol A2 book, with three manually audited tactic claims repaired using synthetic compiled propositions. No new learning-model calls.",
        ),
    )
    path = CAMPAIGN / "rule_repair_protocol.json"
    if not path.exists():
        save(
            path,
            dict(
                registered_at=now(),
                cells=80,
                arm="R1",
                scope="All forty trainX problems, two replicates; no validation or closed data",
                baseline="Already registered A2 and A0 train cells; no additional controls or seeds",
                factor="Three compiled tactic-claim repairs as one joint rule-quality treatment; all other bullets and solver settings unchanged",
                book_sha=sha(CAMPAIGN / filename),
                motivation="Two advertised tactic recipes fail deterministic synthetic checks; one blanket claim unnecessarily excludes successful nra. Reflector, curator and terminal auditor passed these claims through.",
                decision="Report all-attempt cost, coverage, paired uncertainty and cost per solve. This is a diagnostic of rule-quality repair, with no minimum-effect gate or automatic promotion.",
                limitation="Manual audit is not an autonomous author recipe; reused earlier controls introduce temporal/cache differences. Selected from training evidence and synthetic probes before the full study's result analysis.",
            ),
        )
    jobs = [
        replace(j, robust=True)
        for j in c.ordered_jobs("train", [("R1", True, filename)])
    ]
    c.register("rule_repairs", jobs)
    print(
        json.dumps(dict(prepared=True, cells=len(jobs), paid_author_calls=0))
    )


def run() -> None:
    if (CAMPAIGN / "terminal_failures/rule_repairs.json").exists():
        from .terminal_failure import assert_closed

        assert_closed("rule_repairs")
        print("R1 is complete, including its audited terminal failure.")
        return
    launch("rule_repairs", workers=16)


def assess() -> None:
    rows = solver_rows(
        "rule_repairs", receipts(), allow_terminal_failures=True
    )
    if len(rows) != 80:
        raise ValueError("Rule repair denominator changed")
    core = read(REPORT / "fresh_cells.json")
    comparisons: dict[str, Any] = {}
    for arm in ("A0", "A2"):
        base = [r for r in core if r["stage"] == "train" and r["arm"] == arm]
        comparisons[arm] = dict(
            theorem=paired(base, rows), family=paired(base, rows, mapping())
        )
    save(
        REPORT / "rule_repair_results.json",
        dict(
            metrics=metrics(rows),
            comparisons=comparisons,
            protocol=read(CAMPAIGN / "rule_repair_protocol.json"),
        ),
    )
    save(
        REPORT / "rule_repair_cells.json",
        [
            dict(
                {
                    k: v
                    for k, v in row.items()
                    if k not in ("checks", "config", "value", "turns")
                },
                trace_summary=characterize(row),
            )
            for row in rows
        ],
    )
    print(json.dumps(dict(cells=80, metrics=metrics(rows))))


if __name__ == "__main__":
    import sys

    actions = {"prepare": prepare, "run": run, "assess": assess}
    if len(sys.argv) != 2 or sys.argv[1] not in actions:
        raise SystemExit("Use prepare, run, or assess")
    actions[sys.argv[1]]()
