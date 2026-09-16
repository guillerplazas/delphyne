"""Bounded presentation of checked evidence; never change proof state."""

from dataclasses import replace
import hashlib
import json
from typing import Any, cast

import delphyne as dp

from ace.ace_grounded import Checked
from prove_grounded import ProposeProofScriptGrounded
from runtime.tool_budget import clip_utf8

VIEW_BYTES = 4096


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def goal_lines(
    goals: list[str], seen: set[str]
) -> tuple[list[str], list[tuple[str, str]]]:
    lines: list[str] = []
    definitions: list[tuple[str, str]] = []
    for goal in goals[:4]:
        key = fingerprint(goal)
        if key in seen:
            lines.append(f"Goal {key}: unchanged; see its earlier full state.")
        else:
            line = f"Goal {key}:\n{goal}"
            lines.append(line)
            definitions.append((key, line))
    return lines, definitions


def finish_view(
    lines: list[str], definitions: list[tuple[str, str]], seen: set[str]
) -> str:
    view = clip_utf8("\n".join(lines), VIEW_BYTES)
    # A truncated definition must never create an unresolved later alias.
    seen.update(key for key, line in definitions if line in view)
    return view


def feedback_view(
    checked: Checked, current_prefix: str, seen: set[str]
) -> str:
    feedback = checked.feedback
    prefix = "\n".join(feedback.proof_so_far)
    lines = [
        f"Outcome: {checked.outcome}",
        f"Remaining goals: {len(feedback.remaining_goals)}; showing up to 4.",
        "InspectProofState(tactics=verified prefix, start=4) shows later goals.",
        "Failing tactic: "
        + clip_utf8(feedback.failing_tactic or "(none)", 512),
        "Error: " + clip_utf8(feedback.error_message or "(none)", 768),
        (
            "Verified prefix: supplied in the current problem state."
            if prefix == current_prefix
            else "Verified prefix: first "
            f"{len(feedback.proof_so_far)} checked tactics of the "
            "preceding proposal."
        ),
    ]
    goals, definitions = goal_lines(feedback.remaining_goals, seen)
    lines.extend(goals)
    if feedback.probe:
        lines.append("Closing probes: " + json.dumps(feedback.probe[:4]))
    return finish_view(lines, definitions, seen)


def tool_view(text: str, seen: set[str]) -> str:
    try:
        value: Any = json.loads(text)
    except (ValueError, TypeError):
        return clip_utf8(text, VIEW_BYTES)
    if not isinstance(value, dict) or "output" not in value:
        return clip_utf8(text, VIEW_BYTES)
    data = cast(dict[str, Any], value)
    raw_goals: Any = data.get("goals", [])
    if not isinstance(raw_goals, list) or any(
        not isinstance(goal, str) for goal in cast(list[Any], raw_goals)
    ):
        return clip_utf8(text, VIEW_BYTES)
    goals = cast(list[str], raw_goals)
    lines = [
        f"Remaining goals: {data.get('total_goals', len(goals))}; "
        f"page starts at {data.get('start', 0)}.",
        f"Next page: {data.get('next')}; use InspectProofState if omitted.",
        "Output: " + clip_utf8(str(data["output"]), 2048),
    ]
    # Preserve additional status/error fields rather than implying success.
    lines.extend(
        f"{key}: {item}"
        for key, item in data.items()
        if key not in {"output", "goals", "total_goals", "start", "next"}
    )
    rendered, definitions = goal_lines(goals, seen)
    lines.extend(rendered)
    return finish_view(lines, definitions, seen)


def compact_query(
    query: ProposeProofScriptGrounded,
) -> ProposeProofScriptGrounded:
    """Rebuild aliases after every window selection; keep raw evidence intact."""
    seen: set[str] = set()
    prefix: list[dp.AnswerPrefixElement] = []
    for item in query.prefix:
        if isinstance(item, dp.FeedbackMessage) and isinstance(
            item.meta, Checked
        ):
            checked = replace(
                item.meta,
                view=feedback_view(item.meta, query.verified_prefix, seen),
            )
            prefix.append(replace(item, meta=checked))
        elif isinstance(item, dp.ToolResult) and isinstance(item.result, str):
            prefix.append(replace(item, result=tool_view(item.result, seen)))
        else:
            prefix.append(item)
    return replace(query, prefix=tuple(prefix))
