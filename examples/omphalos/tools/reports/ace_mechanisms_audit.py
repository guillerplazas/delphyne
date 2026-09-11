"""Read-only failure/trigger audit of the approved mechanism panels.

Both harnesses: python -m tools.reports.ace_mechanisms_audit. Only trainX
and validationX references and this campaign are read. Cache checks are
not invocation counts; invocation events are reported separately.
"""

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, cast
import json
import yaml

from experiments.ace import ace_mechanisms_experiment as campaign
import ace.ace_applicability as aa
from tools.analysis.failure_analysis import refine_class
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)


def checks_of(directory: Path) -> list[dict[str, Any]]:
    cache = directory / "cache.yaml"
    if not cache.exists():
        return []
    entries: Any = yaml.load(cache.read_text(), Loader=yaml.CSafeLoader) or []
    checks: list[dict[str, Any]] = []
    for entry in entries:
        request = entry["input"]["request"]
        if request["options"].get("model") != "__compute__" or not entry.get(
            "output"
        ):
            continue
        text = str(request["chat"][-1].get("content", ""))
        if not any(
            text.startswith(f"fun: {n}")
            for n in ("checked_proof", "checked_syntax")
        ):
            continue
        value: Any = yaml.load(
            entry["output"]["outputs"][0]["content"], Loader=yaml.CSafeLoader
        )
        if not isinstance(value, dict) or "feedback" not in value:
            continue
        checks.append(cast(dict[str, Any], value))
    return checks


def summarize(directory: Path, events: list[dict[str, Any]]) -> dict[str, Any]:
    checks = checks_of(directory)
    cache = directory / "cache.yaml"
    entries: Any = (
        yaml.load(cache.read_text(), Loader=yaml.CSafeLoader)
        if cache.exists()
        else []
    )
    output_failures: list[dict[str, Any]] = []
    last_inspection: Any = None
    for entry in entries:
        req = entry["input"]["request"]
        output: dict[str, Any] = entry.get("output") or {}
        output_failures.extend(
            log
            for log in output.get("log_items", [])
            if log.get("level") == "error"
        )
        if (
            req["options"].get("model") == "__compute__"
            and str(req["chat"][-1].get("content", "")).startswith(
                "fun: inspect_proof_state"
            )
            and output.get("outputs")
        ):
            last_inspection = yaml.load(
                output["outputs"][0]["content"], Loader=yaml.CSafeLoader
            )
    classes: Counter[str] = Counter()
    repeats = 0
    seen: set[str] = set()
    candidates: list[dict[str, Any]] = []
    for checked in checks:
        fb = checked["feedback"]
        if fb["success"]:
            continue
        classes[refine_class(fb.get("error_message"))] += 1
        key = json.dumps(
            [
                fb.get(k)
                for k in (
                    "proof_so_far",
                    "remaining_goals",
                    "failing_tactic",
                    "error_message",
                )
            ],
            sort_keys=True,
        )
        repeats += key in seen
        seen.add(key)
        action, error = (
            fb.get("failing_tactic") or "",
            fb.get("error_message") or "",
        )
        pattern, correction = aa.syntax_form(action)
        if (
            checked["outcome"] == "rejected"
            and "Syntax error" in error
            and pattern != "unsupported"
        ):
            candidates.append(
                dict(
                    pattern=pattern,
                    failed_action=action,
                    candidate=correction,
                    prefix=fb.get("proof_so_far", []),
                    goals=fb.get("remaining_goals", []),
                )
            )
    last = checks[-1] if checks else {}
    return dict(
        model_output_failures=output_failures,
        last_inspection_preview=last_inspection,
        cached_checks=len(checks),
        repeated_cached_failures=repeats,
        cached_failure_classes=dict(classes),
        cached_outcomes=dict(Counter(c["outcome"] for c in checks)),
        last_cached_check=last,
        candidate_states=candidates,
        mechanism_events=[
            e
            for e in events
            if e.get("kind")
            in ("checked_syntax", "verified_progress", "recovery", "stop")
        ],
        admission_refusals=[
            e
            for e in events
            if e.get("kind") == "admission" and e.get("decision") == "declined"
        ],
        invocation_events=[e for e in events if e.get("kind") == "compute"],
    )


def main() -> None:
    campaign.verify()
    event_path = campaign.CAMPAIGN / "events.jsonl"
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if event_path.exists():
        for line in event_path.read_text().splitlines():
            e = json.loads(line)
            events[e.get("cell", "")].append(e)
    references = campaign.read("references.json")
    data: dict[str, Any] = dict(training={}, validation={})
    for stage in ("training", "validation"):
        report_path = campaign.CAMPAIGN / f"{stage}_report.json"
        if not report_path.exists():
            continue
        report = campaign.read(f"{stage}_report.json")
        baseline = report["cells"]["reference"]
        refs = {(r["theorem"], str(r["seed"])): r for r in references[stage]}
        reused_e = {(r["theorem"], str(r["seed"])): r for r in references["E"]}
        configurations = {
            (c.bench_name, str(c.seed), c.arm_label): c
            for c in campaign.configs(stage)
        }
        for arm, cells in report["cells"].items():
            audited: dict[str, Any] = {}
            for key, cell in cells.items():
                bench, seed = key.rsplit("__seed", 1)
                if arm == "reference":
                    r = refs[bench, seed]
                    name = r["name"]
                    directory = campaign.ROOT / r["source"] / "configs" / name
                elif (
                    arm == "E"
                    and (bench, seed) in reused_e
                    and stage == "training"
                ):
                    r = reused_e[bench, seed]
                    name = r["name"]
                    directory = campaign.ROOT / r["source"] / "configs" / name
                else:
                    name = campaign.name(
                        configurations[bench, seed, arm], None
                    )
                    directory = campaign.OUTPUT / stage / "configs" / name
                observed = summarize(directory, events[name])
                qualified = (
                    cell["solved"]
                    and not cell["failed"]
                    and cell["cost"] <= 0.1
                )
                reference = baseline[key]
                before = (
                    reference["solved"]
                    and not reference["failed"]
                    and reference["cost"] <= 0.1
                )
                observed.update(
                    solved=qualified,
                    cost=cell["cost"],
                    platform_failed=cell["failed"],
                    coverage_change=int(qualified) - int(before),
                    paired_cost_delta=cell["cost"] - reference["cost"],
                )
                audited[key] = observed
            data[stage][arm] = audited
    summary: dict[str, Any] = {}
    mechanism_comparisons: dict[str, Any] = {}
    training_report = campaign.CAMPAIGN / "training_report.json"
    if training_report.exists():
        reports = campaign.read("training_report.json")["cells"]
        for left, right in (("S", "C"), ("C", "R")):
            maps: list[dict[tuple[str, str], Observation]] = []
            for arm in (left, right):
                maps.append(
                    {
                        tuple(k.rsplit("__seed", 1)): Observation(**v)
                        for k, v in reports[arm].items()
                    }
                )
            families = campaign.read("registration.json")["families"]
            paired = compare(
                maps[0], maps[1], list(maps[0]), families=families
            )
            paired.pop("verdict")
            paired["cost_p_two_sided"] = cost_cluster_p(
                maps[0], maps[1], list(maps[0]), families=families
            )
            mechanism_comparisons[f"{right}_versus_{left}"] = paired
    for stage, arms in data.items():
        summary[stage] = {}
        for arm, cells in arms.items():
            mechanisms: Counter[str] = Counter()
            failed_classes: Counter[str] = Counter()
            wins: list[str] = []
            losses: list[str] = []
            for key, row in cells.items():
                for e in row["mechanism_events"]:
                    mechanisms[f"{e['kind']}:{e['decision']}"] += 1
                if not row["solved"]:
                    failed_classes[
                        refine_class(
                            row["last_cached_check"]
                            .get("feedback", {})
                            .get("error_message")
                        )
                    ] += 1
                if row["coverage_change"] > 0:
                    wins.append(key)
                elif row["coverage_change"] < 0:
                    losses.append(key)
            summary[stage][arm] = dict(
                cells_with_output_errors=sum(
                    bool(r["model_output_failures"]) for r in cells.values()
                ),
                wins=wins,
                losses=losses,
                mechanism_events=dict(mechanisms),
                terminal_cached_failure_classes=dict(failed_classes),
                repaired_cells=sum(
                    any(
                        e["kind"] == "checked_syntax"
                        and e["decision"] == "accepted"
                        for e in r["mechanism_events"]
                    )
                    for r in cells.values()
                ),
                recovered_cells=sum(
                    any(
                        e["kind"] == "recovery" and e["decision"] == "admitted"
                        for e in r["mechanism_events"]
                    )
                    for r in cells.values()
                ),
                recovered_and_solved=[
                    k
                    for k, r in cells.items()
                    if r["solved"]
                    and any(
                        e["kind"] == "recovery" and e["decision"] == "admitted"
                        for e in r["mechanism_events"]
                    )
                ],
            )
    result = dict(
        summary=summary,
        cells=data,
        mechanism_comparisons=mechanism_comparisons,
        limits="Heuristic cached failure classes are not causal root causes; explicit events identify invocations, no hypothetical recovery/repair solves.",
    )
    campaign.save("failure_audit.json", result)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
