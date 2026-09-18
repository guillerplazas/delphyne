"""Presentation-only bounded views. Raw verifier evidence is never changed."""

from dataclasses import replace
import json
from typing import Any, cast

import delphyne as dp

from ace.ace_grounded import Checked
from prove_agentic import ReadSkill
from prove_grounded import ProposeProofScriptGrounded
from runtime.tool_budget import clip_utf8

VIEW_BYTES = 4096


def checked_view(checked: Checked, current_prefix: str) -> str:
    feedback = checked.feedback
    lines = [
        f"Outcome: {checked.outcome}",
        "Failing tactic: "
        + clip_utf8(feedback.failing_tactic or "(none)", 384),
        "Error: " + clip_utf8(feedback.error_message or "(none)", 768),
        f"Remaining goals: {len(feedback.remaining_goals)}.",
        "InspectProofState(tactics=verified prefix, start=4) pages later goals.",
        (
            "Verified prefix: supplied in the current problem state."
            if "\n".join(feedback.proof_so_far) == current_prefix
            else "Verified prefix: first "
            f"{len(feedback.proof_so_far)} checked tactics of the "
            "preceding proposal."
        ),
    ]
    lines.extend(
        f"Goal {i}:\n{goal}"
        for i, goal in enumerate(feedback.remaining_goals[:4])
    )
    if feedback.probe:
        lines.append("Closing probes: " + json.dumps(feedback.probe[:4]))
    return clip_utf8("\n".join(lines), VIEW_BYTES)


def inspection_view(text: str) -> str:
    try:
        data: Any = json.loads(text)
    except (ValueError, TypeError):
        return clip_utf8(text, VIEW_BYTES)
    if not isinstance(data, dict) or "output" not in data:
        return clip_utf8(text, VIEW_BYTES)
    data = cast(dict[str, Any], data)
    # Reserve room for both the command result and the current goal. Do not
    # put unbounded output before either the status or the recovery command.
    lines = [
        "InspectProofState can inspect the same prefix and page later goals.",
        f"Remaining goals: {data.get('total_goals', '?')}; "
        f"page starts at {data.get('start', 0)}; next: {data.get('next')}.",
    ]
    for key in ("status", "outcome", "error", "error_message"):
        if key in data:
            lines.append(f"{key}: " + clip_utf8(str(data[key]), 512))
    lines.append("Output: " + clip_utf8(str(data["output"]), 1536))
    goals = data.get("goals", [])
    if isinstance(goals, list):
        lines.extend(
            f"Goal {i}:\n{g}" for i, g in enumerate(cast(list[Any], goals)[:4])
        )
    for key, value in data.items():
        if key not in {
            "output",
            "goals",
            "total_goals",
            "start",
            "next",
            "status",
            "outcome",
            "error",
            "error_message",
        }:
            lines.append(f"{key}: " + clip_utf8(str(value), 256))
    return clip_utf8("\n".join(lines), VIEW_BYTES)


def bounded_query(
    query: ProposeProofScriptGrounded,
) -> ProposeProofScriptGrounded:
    prefix: list[dp.AnswerPrefixElement] = []
    for item in query.prefix:
        if isinstance(item, dp.FeedbackMessage) and isinstance(
            item.meta, Checked
        ):
            prefix.append(
                replace(
                    item,
                    meta=replace(
                        item.meta,
                        view=checked_view(item.meta, query.verified_prefix),
                    ),
                )
            )
        elif isinstance(item, dp.ToolResult) and isinstance(item.result, str):
            # ReadSkill has no pagination; retain its existing 8192-byte
            # allowance. Its omission must not become irrecoverable here.
            prefix.append(
                item
                if item.call.name == ReadSkill.__name__
                else replace(item, result=inspection_view(item.result))
            )
        else:
            prefix.append(item)
    return replace(query, prefix=tuple(prefix))
