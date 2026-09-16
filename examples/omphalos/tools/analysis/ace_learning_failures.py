"""Link every matched development outcome to its actual verifier/model logs.

This is descriptive post-run analysis. Error categories summarize terminal
symptoms; they do not establish which prompt rule caused an outcome.
"""

# ruff: noqa: E402
from runtime.ace_learning_scope import install

install()

from collections import Counter
import json
from pathlib import Path
from typing import Any

from experiments import ace_learning_experiment as c
from tools.reports.ace_learning_results import write


def terminals(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    with path.open() as stream:
        for index, line in enumerate(stream):
            row = json.loads(line)
            if row.get("kind") == "terminal_v2":
                result[row["cell"]] = dict(
                    event=row,
                    line=index + 1,
                    file=str(path.relative_to(c.ROOT)),
                )
    return result


def category(message: str) -> str:
    text = message.lower()
    if not text:
        return "none"
    if "bullet" in text or "focus" in text or "no such goal" in text:
        return "focus"
    if "not found" in text or "no such hypothesis" in text:
        return "missing_name_or_hypothesis"
    if "syntax" in text or "pattern" in text:
        return "syntax_or_pattern"
    if "unify" in text or "expected" in text or "no subterm" in text:
        return "type_or_rewrite_shape"
    if "remaining open goals" in text or "incomplete proof" in text:
        return "open_obligations"
    if "timeout" in text or "deadline" in text or "stack overflow" in text:
        return "resource"
    if (
        "no applicable tactic" in text
        or "cannot find witness" in text
        or "not a valid" in text
    ):
        return "tactic_does_not_close_goal"
    return "other_verifier_failure"


def summarize(
    row: dict[str, Any], stops: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    trace = c.read(row["trace_file"])
    attempts: list[dict[str, Any]] = []
    for check in trace["proof_checks"]:
        value: dict[str, Any] = check.get("result") or {}
        feedback: dict[str, Any] = value.get("feedback", {})
        error: str = feedback.get("error_message") or ""
        attempts.append(
            dict(
                cache_index=check["cache_index"],
                outcome=value.get("outcome"),
                success=feedback.get("success"),
                automation_finished=feedback.get("auto_finished"),
                failing_tactic=feedback.get("failing_tactic"),
                error=error,
                category=category(error),
                verified_prefix_length=len(feedback.get("proof_so_far", [])),
                remaining_goals=feedback.get("remaining_goals", []),
            )
        )
    original_arm = "candidate" if row["arm"] == "v2" else row["arm"]
    cell = f"{row['stage']}__{original_arm}__proof__{row['theorem']}__seed{row['seed']}"
    stop = stops.get(cell, {})
    last_admission: dict[str, Any] = (
        stop.get("event", {}).get("last_admission") or {}
    )
    finish = (
        "solved"
        if row["qualified"]
        else "platform_failed"
        if row["platform_failed"]
        else "admission:" + ",".join(last_admission.get("limiting", []))
        if last_admission.get("admitted") is False
        else "strategy_returned_without_proof"
    )
    return dict(
        **row,
        attempts=attempts,
        final_model_output=trace["model_calls"][-1]["output"]
        if trace["model_calls"]
        else None,
        stop=stop,
        terminal=finish,
        last_failure=next((a for a in reversed(attempts) if a["error"]), None),
        error_counts=dict(
            Counter(a["category"] for a in attempts if a["error"])
        ),
    )


def report() -> None:
    rows: list[dict[str, Any]] = c.read("analysis/proof_cells.json")
    old, new = (
        terminals(c.PRIOR / "events.jsonl"),
        terminals(c.CAMPAIGN / "events.jsonl"),
    )
    summaries = [summarize(r, old if r["arm"] == "v2" else new) for r in rows]
    write("analysis/cell_inspection.json", summaries)
    bank = {
        (r["stage"], r["arm"], r["theorem"], r["seed"]): r for r in summaries
    }
    comparisons: list[dict[str, Any]] = []
    for b in summaries:
        if b["arm"] == "v2":
            continue
        a = bank[(b["stage"], "v2", b["theorem"], b["seed"])]
        status = (
            "shared_success"
            if a["qualified"] and b["qualified"]
            else "candidate_win"
            if b["qualified"]
            else "candidate_loss"
            if a["qualified"]
            else "shared_failure"
        )
        comparisons.append(
            dict(
                stage=b["stage"],
                arm=b["arm"],
                theorem=b["theorem"],
                seed=b["seed"],
                status=status,
                v2=a,
                candidate=b,
            )
        )
    write("analysis/paired_inspection.json", comparisons)
    lines = [
        "# Every matched proof cell",
        "",
        "Descriptions below are terminal observations from actual logs, not causal diagnoses of book effects. Each trace contains all model outputs and verifier computations, including the complete submitted scripts. Admission stops can occur below $.10 when the next request's conservative estimate exceeds the remaining budget.",
        "",
    ]
    for r in comparisons:
        a, b = r["v2"], r["candidate"]
        lines.extend(
            [
                f"## {r['stage']} / {r['theorem']} / seed {r['seed']}: {r['status']}",
                "",
                f"v2: {a['terminal']}, ${a['cost']:.8f}, {a['requests']} model requests. Candidate {r['arm']}: {b['terminal']}, ${b['cost']:.8f}, {b['requests']} model requests.",
                "",
            ]
        )
        for label, value in (("v2", a), (r["arm"], b)):
            last = value["attempts"][-1] if value["attempts"] else None
            failure = value["last_failure"]
            evidence = value["trace_file"]
            lines.append(f"**{label} evidence:** [{evidence}]({evidence}).")
            if value["qualified"]:
                lines.append(
                    f"Terminal verifier: success={last['success'] if last else 'no check'}, assisted completion={last['automation_finished'] if last else 'unknown'}. Earlier verifier-error categories: {value['error_counts']}."
                )
            elif failure:
                lines.extend(
                    [
                        f"Last verifier symptom: {failure['category']}; tactic:",
                        "",
                        "```rocq",
                        failure["failing_tactic"] or "(none)",
                        "```",
                        "",
                        "```text",
                        failure["error"],
                        "```",
                        "",
                        f"Accepted prefix: {failure['verified_prefix_length']} tactics; remaining focused goals: {len(failure['remaining_goals'])}.",
                    ]
                )
            else:
                lines.append(
                    "No failed verifier receipt: inspect the final model output and terminal admission event in the linked cell record."
                )
            if value["stop"]:
                lines.append(
                    f"Terminal event: `{value['stop']['file']}:{value['stop']['line']}`; final model output and exact estimate/remaining budgets are preserved in `analysis/cell_inspection.json`."
                )
            lines.append("")
    (c.CAMPAIGN / "CELL_INSPECTION.md").write_text("\n".join(lines) + "\n")
    print(dict(Counter(r["status"] for r in comparisons)))


if __name__ == "__main__":
    report()
