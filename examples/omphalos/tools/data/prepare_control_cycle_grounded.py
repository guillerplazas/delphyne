"""Freeze re-verified trainX evidence from the control-cycle tuning pass."""

# pyright: strict

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Any, cast

import yaml

import ace.ace_grounded as ag
from ace.ace_evidence import import_signature, unknown_identifier
import runtime.pytanque_utils as pt
from runtime.paths import OMPHALOS_ROOT

ROOT = OMPHALOS_ROOT
CAMPAIGN = ROOT / "experiments/campaigns/ace_control_cycle_20260909"
RUN = ROOT / "experiments/output/ace_control_cycle_tuning"


def transitions() -> list[ag.TrainingTransition]:
    """Extract consecutive rejected/accepted checks from trainX cache traces."""
    allowed = {
        Path(line).stem: line
        for raw in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    }
    result: list[ag.TrainingTransition] = []
    for directory in sorted((RUN / "configs").glob("*")):
        bench = directory.name.split("__", 1)[0]
        cache = directory / "cache.yaml"
        if bench not in allowed or not cache.exists():
            continue
        content = cache.read_bytes()
        checks: list[tuple[list[str], dict[str, Any]]] = []
        solution: tuple[str, ...] = ()
        for entry in cast(list[dict[str, Any]], yaml.safe_load(content) or []):
            request = cast(dict[str, Any], entry.get("input") or {}).get(
                "request", {}
            )
            chat = cast(list[dict[str, Any]], request.get("chat", []))
            output = cast(dict[str, Any], entry.get("output") or {})
            outputs = cast(list[dict[str, Any]], output.get("outputs", []))
            if (
                not chat
                or not outputs
                or not str(chat[-1].get("content", ""))
                .lstrip()
                .startswith("fun: checked_proof")
            ):
                continue
            call = cast(
                dict[str, Any], yaml.safe_load(str(chat[-1]["content"]))
            )
            response = cast(
                dict[str, Any], yaml.safe_load(str(outputs[0]["content"]))
            )
            feedback = cast(dict[str, Any], response.get("feedback") or {})
            checks.append(
                (cast(list[str], call["args"].get("tactics", [])), feedback)
            )
            if feedback.get("success"):
                solution = tuple(feedback.get("proof_so_far") or ())
        for (before, failed), (_, following) in zip(checks, checks[1:]):
            index = failed.get("failing_index")
            accepted = cast(list[str], following.get("proof_so_far") or [])
            if (
                index is None
                or failed.get("success")
                or len(accepted) <= int(index)
            ):
                continue
            prefix = before[: int(index)]
            if accepted[: int(index)] != prefix:
                continue
            action = (str(accepted[int(index)]),)
            failed_action = str(failed.get("failing_tactic") or "Qed.")
            if action == (failed_action,):
                continue
            result.append(
                ag.TrainingTransition(
                    allowed[bench],
                    bench,
                    directory.name,
                    hashlib.sha256(content).hexdigest(),
                    tuple(prefix),
                    failed_action,
                    str(failed.get("error_message") or ""),
                    tuple(failed.get("remaining_goals") or ()),
                    action,
                    solution,
                )
            )
    return result


def priority(item: ag.TrainingTransition) -> tuple[int, str, str]:
    error = item.error.lower()
    category = (
        0
        if "syntax" in error or "field_simplify" in error
        else 1
        if "ring" in error or "normal" in error
        else 2
        if "unif" in error or "reflexivity" in error
        else 3
        if "type" in error or "expected" in error
        else 4
    )
    return category, item.theorem_name, item.failed_action


def main() -> None:
    target = CAMPAIGN / "artifact.json"
    if target.exists():
        raise ValueError(f"refusing to replace frozen artifact: {target}")
    expected = {
        Path(line).stem
        for raw in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    }
    completed = {
        directory.name.split("__", 1)[0]
        for directory in (RUN / "configs").glob("*")
        if (directory / "result.yaml").exists()
    }
    if completed != expected:
        raise ValueError(
            "tuning panel is incomplete: "
            f"missing={sorted(expected - completed)} "
            f"unexpected={sorted(completed - expected)}"
        )
    checked: list[ag.ClaimVerdict] = []
    used: set[str] = set()
    source = sorted(transitions(), key=priority)
    for item in source:
        if len(checked) >= 24 or len(used) >= 12 or item.theorem_name in used:
            continue
        kind = ag.decision_kind(
            pt.Feedback(False, 0, item.failed_action, item.error)
        )
        claim = ag.AdviceClaim(
            f"cycle-{item.source_sha256[:8]}-{len(checked)}",
            kind,
            f"At the recorded verified prefix after {item.failed_action!r}.",
            (),
            item.correction,
            item,
            import_signature(ROOT / item.problem_file),
            unknown_identifier(item.error) or "",
        )
        verdict = ag.validate_claim(claim)
        checked.append(verdict)
        if verdict.status == "verified":
            used.add(item.theorem_name)
    state = ag.AdaptationState().admit(tuple(checked))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "source": "ace_control_cycle_tuning/trainX/seed0",
                "candidates": len(source),
                "state": asdict(state),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    print(json.dumps({"candidates": len(source), "claims": len(state.claims)}))


if __name__ == "__main__":
    main()
