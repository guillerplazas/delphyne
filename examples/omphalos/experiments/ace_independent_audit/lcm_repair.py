"""Reproduce the saved decimal-normalization repair without model calls.

The hand-written script closes the original allowed theorem under both the
Rocq kernel and the ordinary proof bridge. Original paid outcomes and books
are unchanged. Timings in the certificate are the first uncached checks;
resumption verifies their artifacts rather than timing a cache lookup.
"""

from dataclasses import asdict
import json
import resource
import time
from unittest.mock import patch

from runtime import pytanque_utils as pt

from .campaign import activate
from .common import CAMPAIGN, REPORT, allowed, digest, read, save, sha
from .verification import compile_one


def run() -> None:
    protocol = CAMPAIGN / "lcm_repair_probe01_protocol.json"
    plan = read(protocol)
    theorem = plan["theorem"]
    if (
        theorem != "mathd_numbertheory_37"
        or allowed()[theorem][0] != "validation"
    ):
        raise ValueError("Unexpected diagnostic theorem")
    kernel_path = REPORT / "lcm_repair_probe01.json"
    runtime_path = REPORT / "lcm_repair_runtime.json"
    activate()
    limit = 4096 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    with patch("openai.OpenAI", side_effect=AssertionError("No HTTP")):
        if not kernel_path.exists():
            started = time.monotonic()
            result = compile_one(
                (allowed()[theorem][1], theorem, plan["proof"])
            )
            save(
                kernel_path,
                dict(kernel=result, elapsed=time.monotonic() - started),
            )
        kernel = read(kernel_path)
        if kernel["kernel"]["proof_sha"] != digest(plan["proof"]):
            raise ValueError("Registered proof changed")
        repeated = compile_one((allowed()[theorem][1], theorem, plan["proof"]))
        if repeated != kernel["kernel"]:
            raise ValueError("Kernel certificate changed")
        if not runtime_path.exists():
            started = time.monotonic()
            try:
                feedback = pt.check(
                    allowed()[theorem][1],
                    theorem,
                    pt.split_into_tactics(plan["proof"]),
                    probe_automation=False,
                    goal_caps=pt.GoalCaps(
                        probe=0, render=1, render_chars=1000
                    ),
                )
            finally:
                pt.MANAGER.recycle("completed local LCM repair diagnostic")
            save(
                runtime_path,
                dict(
                    feedback=asdict(feedback),
                    seconds=time.monotonic() - started,
                    paid_calls=0,
                    benchmark_outcomes_changed=0,
                ),
            )
        runtime = read(runtime_path)
        if runtime["feedback"]["proof_so_far"] != pt.split_into_tactics(
            plan["proof"]
        ):
            raise ValueError("Runtime checked a different script")
    passed = (
        kernel["kernel"]["passed"]
        and runtime["feedback"]["success"]
        and runtime["feedback"]["finished"]
        and not runtime["feedback"]["auto_finished"]
        and not runtime["feedback"]["remaining_goals"]
    )
    save(
        REPORT / "lcm_repair_certification.json",
        dict(
            passed=passed,
            theorem=theorem,
            protocol_sha=sha(protocol),
            kernel_artifact_sha=sha(kernel_path),
            runtime_artifact_sha=sha(runtime_path),
            kernel_seconds=kernel["elapsed"],
            runtime_seconds=runtime["seconds"],
            extra_import="DecimalNat, supplied inside the accepted proof script",
            manual_intervention="Keep the verified gcd/division prefix; normalize the structural decimal representation before nia instead of expanding unary multiplication.",
            paid_calls=0,
            benchmark_outcomes_changed=0,
            learning_inputs_changed=0,
        ),
    )
    if not passed:
        raise ValueError("The LCM diagnostic did not close")
    print(
        json.dumps(
            dict(
                passed=True,
                kernel_seconds=kernel["elapsed"],
                runtime_seconds=runtime["seconds"],
            )
        )
    )


if __name__ == "__main__":
    run()
