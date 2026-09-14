"""Free, narrowly scoped real-Rocq transport parity for the snippet tool.

Both harnesses: python -m tools.reports.snippet_checks
Requires completed scoped tests/type/lint logs. This never creates API work.
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from dataclasses import asdict, replace
import json
import os
import subprocess
import sys
from typing import Any

from ace.rocq_snippets import check_snippet, context_for
from ace.ace_grounded import outcome_of
from runtime import pytanque_utils as pt
from runtime.paths import OMPHALOS_ROOT as ROOT


def cases() -> list[dict[str, Any]]:
    w = json.loads(
        (
            ROOT
            / "experiments/campaigns/ace_capacity_20260912/snippet_witness.json"
        ).read_text()
    )
    context = context_for(
        w["problem_file"], w["theorem_name"], (w["prefix"],), "parity"
    )
    good = "assert (hs : 0 <= (4 * x + 5) * (4 * x + 5)) by apply Rle_0_sqr."
    bad = "have hs : 0 <= (4 * x + 5) * (4 * x + 5) := Rle_0_sqr _."
    rows: list[dict[str, Any]] = []
    for label, ctx, code, expected in (
        ("bad syntax", context, bad, "rejected"),
        ("open fragment", context, good, "executed_open"),
        ("completed proof", context, good + " nra.", "completed"),
        ("malformed trailing text", context, good + " have", "rejected"),
        (
            "missing source context",
            replace(context, prefix=()),
            good,
            "rejected",
        ),
        ("shelved obligation", context, good + " shelve.", "executed_open"),
    ):
        if os.environ.get("OMPHALOS_PET_MODE") == "stdio":
            # The archived transport deliberately rejects whole-operation
            # contexts. Compare its existing unassisted verifier semantics;
            # never weaken that transport guard or claim bounded stdio works.
            feedback = pt.check(
                ctx.problem_file,
                ctx.theorem_name,
                [*ctx.prefix, code],
                probe_automation=False,
            )
            status = (
                "completed"
                if feedback.success
                else "executed_open"
                if feedback.failing_tactic == "Qed."
                and feedback.proof_so_far == [*ctx.prefix, code]
                else outcome_of(feedback)
            )
        else:
            r = check_snippet(
                ctx, code, dict(seconds=60, rpc_calls=512, view_bytes=8192)
            )
            feedback, status = r.checked.feedback, r.status
        if status != expected:
            raise ValueError((label, status, feedback))
        rows.append(
            dict(
                case=label,
                status=status,
                feedback=asdict(feedback),
            )
        )
    return rows


def main() -> None:
    if sys.argv[1:] == ["--cases"]:
        print(json.dumps(cases(), sort_keys=True))
        return
    from experiments.snippet_experiment import CAMPAIGN, save, sha

    modes: dict[str, Any] = {}
    for mode in ("socket", "stdio"):
        env = dict(os.environ, OMPHALOS_PET_MODE=mode)
        env.pop("OMPHALOS_ADMISSION_EVENTS", None)
        result = subprocess.run(
            [sys.executable, "-m", "tools.reports.snippet_checks", "--cases"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        modes[mode] = json.loads(result.stdout)
    if modes["socket"] != modes["stdio"]:
        raise ValueError("Real Rocq transport parity failed")
    for name in ("tests.log", "typecheck.log", "lint.log"):
        path = CAMPAIGN / name
        text = path.read_text()
        needle = {
            "tests.log": "passed",
            "typecheck.log": "0 errors",
            "lint.log": "All checks passed!",
        }[name]
        if needle not in text or "FAILED" in text or " failed," in text:
            raise ValueError("Scoped prerequisite check failed: " + name)
    save(
        "offline_checks.json",
        dict(
            passed=True,
            paid_requests=0,
            real_rocq_parity=modes,
            parity_scope="Bounded socket tool versus existing unassisted stdio checker; bounded stdio is unsupported",
            logs={
                n: sha(CAMPAIGN / n)
                for n in ("tests.log", "typecheck.log", "lint.log")
            },
            symlinks={
                n: (ROOT / n).is_symlink()
                for n in ("CLAUDE.md", "../../CLAUDE.md")
            },
        ),
    )
    print(
        "Six real-Rocq cases match socket tool versus legacy stdio; no API calls"
    )


if __name__ == "__main__":
    main()
