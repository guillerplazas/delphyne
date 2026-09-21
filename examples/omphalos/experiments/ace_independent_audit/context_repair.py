"""Compile a narrow repair of two saved context-overflow proposals.

Both harnesses: ``python -m experiments.ace_independent_audit.context_repair``.
This is a zero-API diagnostic on an allowed validationX theorem. It preserves
the learned induction proof and replaces only whole-hypothesis expansion at
the final numeral conversion. These proofs are never benchmark replacements,
author evidence, or edits to a frozen playbook.
"""

import json
from pathlib import Path
import time
from typing import Any
from unittest.mock import patch

from .audit import cell
from .common import CAMPAIGN, OUTPUT, REPORT, allowed, now, read, save, sha
from .terminal_failure import hashes
from .verification import compile_one


def run() -> None:
    theorem = "amc12a_2008_p4"
    if allowed()[theorem][0] != "validation":
        raise ValueError("Unexpected diagnostic source partition")
    output = REPORT / "context_repair_certification.json"
    if output.exists():
        prior = read(output)
        for row in prior["repairs"]:
            directory = OUTPUT / row["batch"] / "configs" / row["cell"]
            if hashes(directory) != row["original_hashes"]:
                raise ValueError("Diagnostic source changed")
        print(json.dumps(dict(cached=True, repairs=len(prior["repairs"]))))
        return
    repairs: list[dict[str, Any]] = []
    for batch, arm in (
        ("core_pilot_book-part01", "P1"),
        ("core_frozen-part03", "B2"),
    ):
        identity = f"validation__{arm}__{theorem}__seed1"
        directory = OUTPUT / batch / "configs" / identity
        terminal = read(CAMPAIGN / "terminal_failures" / (identity + ".json"))
        if hashes(directory) != terminal["hashes"]:
            raise ValueError("Unaudited terminal source")
        original = cell((str(directory), theorem))
        check = original["checks"][-1]
        tactics = check["args"]["tactics"]
        if tactics[-2:] != ["cbn in H.", "exact H."]:
            raise ValueError("The observed reduction tail changed")
        revised = [
            *tactics[:-2],
            "eapply eq_trans; [exact H |].",
            "rewrite INR_IZR_INZ.",
            "ring.",
        ]
        repairs.append(
            dict(
                cell=identity,
                batch=batch,
                original_hashes=terminal["hashes"],
                original_check_index=check["index"],
                original_feedback_characters=len(
                    json.dumps(check["feedback"])
                ),
                original_script="\n".join(tactics),
                repaired_script="\n".join(revised),
            )
        )
    protocol = CAMPAIGN / "context_repair_protocol.json"
    if not protocol.exists():
        save(
            protocol,
            dict(
                registered_at=now(),
                repairs=repairs,
                intervention="Keep the proved induction lemma and its specialization. Use equality transitivity to isolate the closed RHS, convert INR to IZR, and normalize with ring; never unfold the501-factor product.",
                decision="Independently compile both complete scripts against the original statement. Retain failed probes too. These are hand-edited local diagnostics and cannot increase benchmark coverage or retroactively alter incurred cost.",
                paid_calls=0,
            ),
        )
    else:
        if read(protocol)["repairs"] != repairs:
            raise ValueError("Registered diagnostic proposals changed")
    for row in repairs:
        started = time.monotonic()
        with patch("openai.OpenAI", side_effect=AssertionError("No HTTP")):
            result = compile_one(
                (allowed()[theorem][1], theorem, row["repaired_script"])
            )
        row["verification_seconds"] = time.monotonic() - started
        row["kernel"] = result
    save(
        output,
        dict(
            repairs=repairs,
            passed=all(r["kernel"]["passed"] for r in repairs),
            protocol_sha=sha(protocol),
            diagnostic_source_sha=sha(Path(__file__)),
            paid_calls=0,
            benchmark_outcomes_changed=0,
            learning_inputs_changed=0,
        ),
    )
    print(
        json.dumps(
            [
                dict(
                    cell=r["cell"],
                    seconds=r["verification_seconds"],
                    **r["kernel"],
                )
                for r in repairs
            ],
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
