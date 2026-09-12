"""Read only allowlisted development panels; no aggregate archive scans.

Both harnesses: python -m tools.reports.coverage_cycle_audit preflight
or training / validation. No paid calls, no test access.
"""

from experiments import coverage_cycle_experiment as c
from collections import Counter, defaultdict
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Any, cast

import yaml
import delphyne as dp
from delphyne.utils.typing import pydantic_load
import ace.ace_grounded as ag
import ace.ace_applicability as aa
import prove_grounded as pg
import prove_coverage_cycle as cc
from runtime.stall import stalled, view_of_feedback, VerdictView
from tools.analysis.failure_analysis import refine_class


def cached(directory: Path) -> tuple[list[ag.Checked], list[int]]:
    entries = yaml.load(
        (directory / "cache.yaml").read_text(), Loader=yaml.CSafeLoader
    )
    checks: list[ag.Checked] = []
    sizes: list[int] = []
    for entry in entries:
        req = entry["input"]["request"]
        output: dict[str, Any] = entry.get("output") or {}
        if req["options"].get("model") != "__compute__":
            sizes.append(len(json.dumps(req["chat"], ensure_ascii=False)))
            continue
        text = str(req["chat"][-1].get("content", ""))
        if not text.startswith(
            ("fun: checked_proof", "fun: checked_syntax")
        ) or not output.get("outputs"):
            continue
        value = yaml.load(
            output["outputs"][0]["content"], Loader=yaml.CSafeLoader
        )
        if isinstance(value, dict) and "feedback" in value:
            checks.append(
                pydantic_load(ag.Checked, cast(dict[str, Any], value))
            )
    return checks, sizes


def preflight() -> None:
    rows: dict[str, Any] = {}
    env = c.context("D2").policy_env()
    selector = cc.relevant_examples(c.BANK)
    bank_names = {r["theorem"] for r in c.read("demo_bank.json")["examples"]}
    for ref in c.read("references.json")["training"]:
        theorem = ref["theorem"]
        checks, sizes = cached(
            c.ROOT / ref["source"] / "configs" / ref["name"]
        )
        spec = c.pt.parse_problem(c.partition("training")[theorem], True)
        selections: Counter[str] = Counter()
        patterns: Counter[str] = Counter()
        views: list[VerdictView] = []
        reachable = False
        for checked in checks:
            fb = checked.feedback
            if checked.outcome not in ("rejected", "incomplete"):
                continue
            view = view_of_feedback(fb)
            if view is not None:
                views.append(view)
                reachable |= stalled(views, "seenstate", 2)
            kind = ag.decision_kind(fb)
            query_type = {
                "reference": pg.ResolveProofReference,
                "bridge": pg.ChooseProofBridge,
                "structure": pg.ChooseProofStructure,
            }[kind]
            query = query_type(
                spec,
                {},
                prefix=(
                    dp.FeedbackMessage(
                        "feedback", checked.outcome, meta=checked
                    ),
                ),
            )
            for example in selector(env, query):
                if (
                    isinstance(example.query, pg.ProposeProofScriptGrounded)
                    and example.query.spec.theorem_name in bank_names
                ):
                    selections[example.query.spec.theorem_name] += 1
            pattern = aa.syntax_form(fb.failing_tactic or "")[0]
            if (
                "Syntax error" in (fb.error_message or "")
                and pattern != "unsupported"
            ):
                patterns[pattern] += 1
        rows[theorem] = dict(
            demo_selections=dict(selections),
            syntax_patterns=dict(patterns),
            cached_trigger=reachable,
            max_prompt_chars=max(sizes, default=0),
        )
    summary = dict(
        demo_cells=sum(bool(r["demo_selections"]) for r in rows.values()),
        syntax_cells=sum(bool(r["syntax_patterns"]) for r in rows.values()),
        cached_trigger_cells=sum(r["cached_trigger"] for r in rows.values()),
        context_cells=sum(
            r["max_prompt_chars"] > 24000 for r in rows.values()
        ),
    )
    c.save(
        "preflight.json",
        dict(
            summary=summary,
            cells=rows,
            caveat="Training cached-check sequence is a reach diagnostic, not exact live trigger/admission incidence. No paid pilot or outcome-derived threshold search.",
        ),
    )
    print(summary)


def audit(stage: str) -> None:
    if (
        stage not in c.STAGES
        or not (c.CAMPAIGN / f"{stage}_report.json").exists()
    ):
        raise ValueError("Require a completed allowed stage")
    c.verify()
    acct = c.accounting()
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for line in (c.CAMPAIGN / "events.jsonl").read_text().splitlines():
        row = json.loads(line)
        events[row["cell"]].append(row)
    refs = {r["theorem"]: r for r in c.read("references.json")[stage]}
    result: dict[str, Any] = {}
    for arm in c.ARMS:
        cells: dict[str, Any] = {}
        affected: Counter[str] = Counter()
        terminal: Counter[str] = Counter()
        wins: list[str] = []
        losses: list[str] = []
        mechanism: Counter[str] = Counter()
        obs = c.observations(stage, arm, acct)
        for cfg in c.configs(stage, arm):
            n = c.name(cfg, None)
            r = obs[(cfg.bench_name, "0")]
            ref = refs[cfg.bench_name]
            checks, sizes = cached(c.OUTPUT / stage / arm / "configs" / n)
            classes = Counter(
                refine_class(ch.feedback.error_message)
                for ch in checks
                if not ch.feedback.success
            )
            solved = r.solved and not r.failed and r.cost <= 0.1
            before = ref["solved"] and not ref["failed"] and ref["cost"] <= 0.1
            if solved and not before:
                wins.append(cfg.bench_name)
            if before and not solved:
                losses.append(cfg.bench_name)
            last = checks[-1] if checks else None
            if not solved:
                affected.update(classes.keys())
                terminal[
                    refine_class(last.feedback.error_message)
                    if last
                    else "no-submission"
                ] += 1
            counts = Counter(
                f"{e['kind']}:{e['decision']}"
                for e in events[n]
                if e["kind"]
                in (
                    "relevant_example",
                    "exploration",
                    "exploration_v2",
                    "history",
                    "checked_syntax",
                )
            )
            mechanism.update(counts)
            cells[cfg.bench_name] = dict(
                solved=solved,
                reference_solved=before,
                cost=r.cost,
                reference_cost=ref["cost"],
                platform_failed=r.failed,
                cached_failure_classes=dict(classes),
                mechanism=dict(counts),
                last_check=asdict(last) if last else None,
                max_prompt_chars=max(sizes, default=0),
                short_dispatches=sum(
                    e["kind"] == "model"
                    and e["decision"] == "invoked"
                    and e.get("output_limit") == 4096
                    for e in events[n]
                ),
                selected_examples=sorted(
                    {
                        e["example"]
                        for e in events[n]
                        if e["kind"] == "relevant_example"
                        and e["decision"] == "selected"
                    }
                ),
            )
        result[arm] = dict(
            cells=cells,
            new_solves=wins,
            lost_solves=losses,
            any_cached_failure=dict(affected),
            terminal_failure=dict(terminal),
            mechanism=dict(mechanism),
        )
    c.save(
        f"{stage}_audit.json",
        dict(
            stage=stage,
            interpretation="Training diagnosis"
            if stage == "training"
            else "Descriptive validation; no candidate edits",
            arms=result,
        ),
    )
    print(
        json.dumps(
            {
                a: {k: v for k, v in r.items() if k != "cells"}
                for a, r in result.items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    if sys.argv[1] == "preflight":
        preflight()
    else:
        audit(sys.argv[1])
