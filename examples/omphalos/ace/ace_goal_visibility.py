"""Version 2 feedback for incomplete proofs with no focused goals.

Uses training-testable functional replay and the existing verifier limits.
An empty focused-goal list never changes the kernel's completion verdict.
"""

from dataclasses import replace
import json
import time

from ace import ace_grounded as ag
from runtime import pytanque_utils as pt
from runtime import rocq_server
from runtime.admission_events import computation_started
from runtime.tool_budget import (
    OperationExhausted,
    ToolLimits,
    clip_utf8,
    operation,
)


def inspect_obligations(
    problem_file: str,
    theorem_name: str,
    tactics: str,
    limits: ToolLimits = ToolLimits(),
    command: str = "",
) -> ag.Inspection:
    computation_started("inspect_obligations")
    if command not in ("", "Show.", "Show Existentials."):
        return ag.Inspection(
            "Use Show. or Show Existentials.", 0, 0, "rejected"
        )
    with operation(limits) as op:
        outcome: ag.Outcome = "unknown"
        payload: dict[str, object] = {"obligations_status": "unknown"}
        try:
            file = str((ag.ROOT / problem_file).resolve())
            augmented = rocq_server.augmented_path(
                file, pt.DEFAULT_EXTRA_IMPORTS
            )
            with rocq_server.MANAGER.session(augmented) as client:
                replay = pt._open_and_replay(  # pyright: ignore[reportPrivateUsage]
                    client,
                    augmented,
                    theorem_name,
                    pt.split_into_tactics(tactics),
                    stop_when_finished=False,
                    timeout=pt.PROOF_TACTIC_TIMEOUT,
                )
                if replay.start_error or replay.failing_index is not None:
                    payload["error"] = (
                        replay.start_error
                        or replay.error_message
                        or "Replay failed"
                    )
                else:
                    assert replay.state is not None
                    commands = (
                        (command,)
                        if command
                        else ("Show.", "Show Existentials.")
                    )
                    results: dict[str, str] = {}
                    payload["inspection"] = results
                    for cmd in commands:
                        after = client.run(
                            replay.state, cmd, timeout=pt.PROOF_TACTIC_TIMEOUT
                        )
                        results[cmd] = str(after.feedback)
                    payload.update(
                        obligations_status="inspection_available",
                        kernel_completion="not_established_by_inspection",
                        inspection=results,
                    )
                    outcome = "accepted"
        except Exception as exc:
            payload["error"] = f"{type(exc).__name__}: {exc}"
            outcome = (
                "resource_exhausted"
                if isinstance(exc, OperationExhausted)
                else "unknown"
            )
        if op.exhausted:
            outcome = "resource_exhausted"
            payload.update(obligations_status="unknown", error=op.exhausted)
        return ag.Inspection(
            clip_utf8(
                json.dumps(payload, ensure_ascii=False), limits.view_bytes
            ),
            op.elapsed,
            op.calls,
            outcome,
        )


def checked_proof_v2(
    problem_file: str,
    theorem_name: str,
    tactics: list[str],
    limits: ToolLimits = ToolLimits(),
    assisted: bool = True,
) -> ag.Checked:
    start = time.monotonic()
    checked = ag.checked_proof(
        problem_file, theorem_name, tactics, limits, assisted
    )
    if (
        checked.outcome != "incomplete"
        or checked.feedback.success
        or checked.feedback.remaining_goals
    ):
        return checked
    remaining = limits.seconds - (time.monotonic() - start)
    calls = limits.rpc_calls - checked.rpc_calls
    extra: dict[str, object] = {
        "obligations_status": "unknown",
        "completion": "Qed rejected: obligations remain despite no focused goals.",
    }
    elapsed, rpc_calls = checked.elapsed, checked.rpc_calls
    if remaining > 0 and calls > 0:
        inspected = inspect_obligations(
            problem_file,
            theorem_name,
            "\n".join(checked.feedback.proof_so_far),
            ToolLimits(remaining, calls, min(limits.view_bytes, 4096)),
        )
        elapsed += inspected.elapsed
        rpc_calls += inspected.rpc_calls
        extra["obligations_inspection"] = inspected.text
        extra["obligations_status"] = inspected.outcome
    else:
        extra["inspection_error"] = "No verifier allowance remains."
    payload = json.loads(
        ag.feedback_view(checked.feedback, checked.outcome, 10**9)
    )
    view = clip_utf8(
        json.dumps({**extra, **payload}, ensure_ascii=False), limits.view_bytes
    )
    return replace(checked, elapsed=elapsed, rpc_calls=rpc_calls, view=view)


def inspect_proof_state_v2(
    problem_file: str,
    theorem_name: str,
    tactics: str,
    command: str = "",
    start: int = 0,
    limits: ToolLimits = ToolLimits(),
) -> ag.Inspection:
    if command.strip().startswith("Show"):
        return inspect_obligations(
            problem_file, theorem_name, tactics, limits, command.strip()
        )
    return ag.inspect_proof_state(
        problem_file, theorem_name, tactics, command, start, limits
    )
