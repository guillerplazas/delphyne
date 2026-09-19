"""Read exact Compute evidence without importing historical runners."""

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any, cast

import yaml

from ace.rocq_snippets import context_for
from ace.role_contracts import TrainingEvent
from ace.terminal_evidence import extract_terminal_evidence


def computations(folder: Path) -> list[dict[str, Any]]:
    path = folder / "cache.yaml"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    cache: list[dict[str, Any]] = yaml.load(
        path.read_text(), Loader=yaml.CSafeLoader
    )
    for entry in cache:
        request = entry["input"]["request"]
        if request["options"].get("model") != "__compute__":
            continue
        call = yaml.load(
            request["chat"][-1]["content"], Loader=yaml.CSafeLoader
        )
        output: dict[str, Any] = entry.get("output") or {}
        outputs: list[dict[str, Any]] = output.get("outputs") or []
        if outputs:
            value = yaml.load(outputs[0]["content"], Loader=yaml.CSafeLoader)
            rows.append(dict(call=call, value=value))
    return rows


def feedbacks(folder: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in computations(folder):
        value = row["value"]
        if not isinstance(value, dict):
            continue
        value = cast(dict[str, Any], value)
        value = value.get("checked", value)
        fb = value.get("feedback", value)
        if "proof_so_far" in fb or "failing_tactic" in fb:
            result.append(
                dict(
                    call=row["call"],
                    feedback=fb,
                    outcome=value.get("outcome", "legacy"),
                )
            )
    return result


def learning_source(
    folder: Path, theorem: str, generator_book: str
) -> dict[str, Any]:
    terminal = extract_terminal_evidence(folder, theorem)
    events: list[TrainingEvent] = []
    checks = feedbacks(folder)
    for i, row in enumerate(checks):
        fb = row["feedback"]
        success = bool(fb.get("success"))
        prefix = () if success else tuple(fb.get("proof_so_far", ()))
        events.append(
            TrainingEvent(
                f"e{i + 1}",
                context_for(
                    terminal.problem_file,
                    theorem,
                    prefix,
                    terminal.cache_sha256,
                ),
                "\n".join(terminal.accepted_script)
                if success
                else (fb.get("failing_tactic") or ""),
                row["outcome"],
                fb.get("error_message") or "",
                tuple(fb.get("remaining_goals", ())),
            )
        )
    entries: list[dict[str, Any]] = yaml.load(
        (folder / "cache.yaml").read_text(), Loader=yaml.CSafeLoader
    )
    calls = [
        e
        for e in entries
        if e["input"]["request"]["options"].get("model") != "__compute__"
    ]
    conversation: list[dict[str, Any]] = []
    last: dict[str, Any] = {}
    if calls:
        chat: list[dict[str, Any]] = calls[-1]["input"]["request"]["chat"]
        start = next(
            (
                i
                for i, m in enumerate(chat)
                if m.get("role") == "user" and theorem in json.dumps(m)
            ),
            len(chat),
        )
        conversation = chat[start:]
        last = calls[-1].get("output") or {}
    # Preserve visible tool actions as well as local checks. Opaque provider
    # reasoning is not fabricated. Terminal v2 retains the complete accepted
    # proof including any automation tail, independent of dialogue length.
    return dict(
        problem_file=terminal.problem_file,
        generator_book=generator_book,
        trajectory=yaml.safe_dump(
            dict(
                conversation=conversation,
                final_output=last,
                verifier_checks=checks,
            ),
            sort_keys=False,
        ),
        terminal=asdict(terminal),
        events=[asdict(e) for e in events],
    )


def failure_category(error: str, tactic: str = "") -> str:
    text = (error + " " + tactic).lower()
    patterns = (
        (
            "verifier_resource",
            ("timeout", "resourceexhaust", "out of memory", "deadline"),
        ),
        ("syntax", ("syntax error", "illegal begin", "lexer")),
        (
            "unknown_reference",
            ("not found", "reference", "unbound", "not declared"),
        ),
        (
            "unproved_prerequisite",
            (
                "unable to unify",
                "cannot unify",
                "no applicable",
                "no such hypothesis",
            ),
        ),
        (
            "arithmetic_or_search",
            (
                "cannot find witness",
                "not a valid ring",
                "tactic failure",
                "failed",
            ),
        ),
        ("incomplete_proof", ("incomplete proof", "remaining open", "qed.")),
    )
    return next(
        (label for label, terms in patterns if any(t in text for t in terms)),
        "other_or_unobserved",
    )
