"""Compact failure observations, not new evaluation or automatic repairs.

Both harnesses: python -m tools.reports.coverage_audit --stage training
Training traces inform diagnosis. Validation/test summaries are descriptive
only and may not be reused to author examples or alter frozen candidates.
"""

from collections import Counter, defaultdict
import argparse
import json
from typing import Any, cast

from experiments import coverage_experiment as c
from tools.reports.ace_mechanisms_audit import summarize
from tools.analysis.failure_analysis import refine_class


def audit(stage: str) -> None:
    c.verify()
    if not (c.CAMPAIGN / f"{stage}_report.json").exists():
        raise ValueError("audit requires a complete reported panel")
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for line in (c.CAMPAIGN / "events.jsonl").read_text().splitlines():
        row = json.loads(line)
        events[row["cell"]].append(row)
    acct = c.accounting()
    arms = (
        ("D", "E") if stage != "test" else (c.read("selection.json")["arm"],)
    )
    summaries: dict[str, Any] = {}
    details: dict[str, Any] = {}
    for arm in arms:
        obs = c.observations(stage, arm, acct)
        baseline = (
            c.observations(stage, "reference", acct)
            if stage == "test"
            else {
                (r["theorem"], "0"): c.Observation(
                    r["solved"], r["cost"], r["failed"]
                )
                for r in c.read("references.json")[stage]
            }
        )
        terminal: Counter[str] = Counter()
        affected: Counter[str] = Counter()
        event_counts: Counter[str] = Counter()
        wins: list[str] = []
        losses: list[str] = []
        cells: dict[str, Any] = {}
        for cfg in c.stage_configs(stage, arm):
            n = c.name(cfg, None)
            key = (cfg.bench_name, "0")
            r = obs[key]
            ref = baseline[key]
            solved = r.solved and not r.failed and r.cost <= 0.1
            before = ref.solved and not ref.failed and ref.cost <= 0.1
            if solved and not before:
                wins.append(cfg.bench_name)
            if before and not solved:
                losses.append(cfg.bench_name)
            detail = summarize(
                c.OUTPUT / stage / arm / "configs" / n, events[n]
            )
            last = cast(dict[str, Any], detail["last_cached_check"] or {})
            fb = cast(dict[str, Any], last.get("feedback", {}))
            failure = (
                refine_class(fb.get("error_message"))
                if fb
                else "no-proof-submission"
            )
            if not solved:
                terminal[failure] += 1
                affected.update(detail["cached_failure_classes"].keys())
            mechanism = Counter(
                f"{e['kind']}:{e['decision']}"
                for e in events[n]
                if e["kind"] in ("exploration", "coverage_example")
            )
            event_counts.update(mechanism)
            cells[cfg.bench_name] = dict(
                solved=solved,
                reference_solved=before,
                cost=r.cost,
                reference_cost=ref.cost,
                platform_failed=r.failed,
                cached_failure_classes=detail["cached_failure_classes"],
                cached_checks=detail["cached_checks"],
                terminal_class=failure,
                last_action=fb.get("failing_tactic"),
                last_error=(fb.get("error_message") or "")[:2500],
                verified_prefix_length=len(fb.get("proof_so_far", [])),
                goal_count=len(fb.get("remaining_goals", [])),
                last_goals=[
                    g[:2000] for g in fb.get("remaining_goals", [])[:2]
                ],
                output_errors=detail["model_output_failures"],
                mechanism_events=dict(mechanism),
                selected_examples=sorted(
                    {
                        e["example"]
                        for e in events[n]
                        if e["kind"] == "coverage_example"
                        and e["decision"] == "selected"
                    }
                ),
                exploration_modes=[
                    e["mode"]
                    for e in events[n]
                    if e["kind"] == "exploration" and e["decision"] == "query"
                ],
                admission_refusals=detail["admission_refusals"],
            )
        details[arm] = cells
        summaries[arm] = dict(
            new_solves=wins,
            lost_solves=losses,
            unsolved_terminal_classes=dict(terminal.most_common()),
            unsolved_problems_by_any_cached_failure=dict(
                affected.most_common()
            ),
            mechanism_events=dict(event_counts),
            cells_with_exploration=sum(
                bool(r["exploration_modes"]) for r in cells.values()
            ),
            cells_with_examples=sum(
                bool(r["selected_examples"]) for r in cells.values()
            ),
            cells_with_output_errors=sum(
                bool(r["output_errors"]) for r in cells.values()
            ),
        )
    payload = dict(
        stage=stage,
        summary=summaries,
        cells=details,
        interpretation="Cached failure classes and terminal cached checks are diagnostic associations, not causal labels or exact final runtime states. Invocation events are counted separately. No hypothetical solves.",
        exposure="Training diagnosis"
        if stage == "training"
        else "Descriptive only; never feed these observations into candidate edits or demonstrations",
    )
    c.save(f"{stage}_audit.json", payload)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage", choices=("training", "validation", "test"), required=True
    )
    audit(parser.parse_args().stage)
