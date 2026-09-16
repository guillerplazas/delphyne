"""Receipt-based paired reports; only the registered validationX/testX cells.

Report generation is offline, never triggers paid runs, and does not inspect
test outcomes before the arm selection has been frozen. Both harnesses use
python -m experiments.ace_economy_experiment report (or select/replay).
"""

from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import replace
import csv
import gzip
import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import numpy as np
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command

from experiments import ace_economy_experiment as c
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import price_tokens
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)


def all_configs() -> list[c.Config]:
    return [
        config
        for p in sorted((c.CAMPAIGN / "manifests").glob("*.json"))
        for config in c.configs(p.stem)
    ]


def cells() -> list[dict[str, Any]]:
    ledger = c.accounting()
    if ledger["unresolved"] or ledger["billing_issues"]:
        raise ValueError("Unresolved billing prevents an economic verdict")
    rows: list[dict[str, Any]] = []
    for config in all_configs():
        result = c.cell_result(config)
        ident = c.name(config, None)
        cost = ledger["costs"].get(ident, 0.0)
        tokens = ledger["tokens"].get(ident, dict(input=0, cached=0, output=0))
        rows.append(
            dict(
                cell=ident,
                stage=config.stage,
                arm=config.arm,
                theorem=config.bench_name,
                seed=config.seed,
                cap=config.cap,
                solved=bool(result and result["success"]),
                qualified=bool(
                    result and result["success"] and cost <= config.cap + 1e-12
                ),
                failed=result is None,
                cost=cost,
                requests=result["spent_budget"].get("num_requests", 0)
                if result
                else 0,
                rocq_seconds=result["spent_budget"].get("rocq_seconds", 0)
                if result
                else 0,
                **tokens,
                uncached_cost=price_tokens(
                    "gpt-5.6-luna", tokens["input"], 0, tokens["output"]
                ),
            )
        )
    if len({r["cell"] for r in rows}) != len(rows):
        raise ValueError("Repeated campaign cell")
    if abs(sum(r["cost"] for r in rows) - ledger["total"]) > 1e-8:
        raise ValueError("Cell manifest does not account for every receipt")
    return rows


def paired(
    rows: list[dict[str, Any]],
    stage: str,
    arm: str,
    reference: str = "ace",
    seed: int | None = None,
) -> dict[str, Any]:
    expected = [
        (n, str(s))
        for n in c.partition(stage)
        for s in (
            (0, 1)
            if stage == "validation" and seed is None
            else (seed if seed is not None else 0,)
        )
    ]
    groups = c.families(stage)

    def observations(which: str) -> dict[tuple[str, str], Observation]:
        return {
            (r["theorem"], str(r["seed"])): Observation(
                r["solved"], r["cost"], r["failed"]
            )
            for r in rows
            if r["stage"] == stage
            and r["arm"] == which
            and (seed is None or r["seed"] == seed)
        }

    a, b = observations(reference), observations(arm)
    cap = 0.20 if arm == "budget" else 0.10
    result = compare(a, b, expected, families=groups, cap_a=0.10, cap_b=cap)
    if result["complete"]:
        result["cost_p_two_sided"] = cost_cluster_p(a, b, expected, groups)
        result["cost_per_solve_a"] = (
            result["cost_a"] / result["solved_a"]
            if result["solved_a"]
            else None
        )
        result["cost_per_solve_b"] = (
            result["cost_b"] / result["solved_b"]
            if result["solved_b"]
            else None
        )
        result["comparison"] = f"{reference} -> {arm}"
        result["observed_ten_percent_target"] = (
            result["solved_b"] >= result["solved_a"]
            and result["cost_ratio"] <= 0.90
        )
        if cap != 0.10:
            result["solved_b_at_common_10_cent_cutoff"] = sum(
                o.solved and not o.failed and o.cost <= 0.10
                for o in b.values()
            )
    return result


def candidate_interest(
    result: dict[str, Any], seeds: list[dict[str, Any]]
) -> bool:
    if not result["complete"] or any(not r["complete"] for r in seeds):
        return False
    if any(r["solved_b"] < r["solved_a"] for r in seeds):
        return False
    return bool(
        result["observed_ten_percent_target"]
        or (
            result["solved_b"] >= result["solved_a"] + 2
            and result["cost_per_solve_b"] <= 1.25 * result["cost_per_solve_a"]
        )
    )


def select() -> None:
    c.verify()
    if (c.CAMPAIGN / "selection.json").exists():
        return
    if (c.CAMPAIGN / "manifests/test.json").exists():
        raise ValueError("Selection cannot follow test dispatch")
    if any(
        not (c.CAMPAIGN / f"batches/{arm}.json").exists()
        for arm in ("baseline", "budget", "session", "views")
    ):
        raise ValueError("All registered validation panels are required")
    rows = cells()
    results: dict[str, Any] = {}
    eligible: list[str] = []
    for arm in ("budget", "session", "views"):
        result = paired(rows, "validation", arm)
        seeds = [paired(rows, "validation", arm, seed=s) for s in (0, 1)]
        results[arm] = dict(
            pooled=result,
            seeds=seeds,
            practical_interest=candidate_interest(result, seeds),
        )
        if results[arm]["practical_interest"]:
            eligible.append(arm)
    selected = (
        min(
            eligible,
            key=lambda a: (
                -results[a]["pooled"]["solved_b"],
                results[a]["pooled"]["cost_b"],
            ),
        )
        if eligible
        else None
    )
    c.save(
        "selection.json",
        dict(
            selected=selected,
            test_arms=["agentic", "ace"] + ([selected] if selected else []),
            criteria="Registered coverage first, cost second; no per-replicate coverage loss",
            validation=results,
            before_test=True,
        ),
    )
    print(
        json.dumps(
            dict(
                selected=selected,
                test_arms=c.read("selection.json")["test_arms"],
            )
        )
    )


def profile() -> dict[str, Any]:
    """Exact serialized character counts, not claims of tokenizer precision."""
    profiles: dict[str, Any] = {}
    for arm in c.ARMS:
        dirs = [
            p
            for p in (c.CAMPAIGN / "transport").glob(f"validation__{arm}__*")
            if p.is_dir()
        ]
        if not dirs:
            continue
        lengths: dict[str, list[int]] = defaultdict(list)
        calls: Counter[str] = Counter()
        for directory in dirs:
            for path in directory.glob("*.json.gz"):
                with gzip.open(path, "rt") as f:
                    value = json.load(f)
                request = value["request"]["request"]
                lengths["schemas_chars"].append(
                    len(json.dumps(request["tools"], ensure_ascii=False))
                )
                chat = request["chat"]
                lengths["system_chars"].append(
                    sum(
                        len(str(m.get("content", "")))
                        for m in chat
                        if m["role"] == "system"
                    )
                )
                lengths["all_message_chars"].append(
                    sum(len(str(m.get("content", ""))) for m in chat)
                )
                response = value["response"]
                budget = response["budget"]["values"]
                lengths["input_tokens"].append(budget.get("input_tokens", 0))
                lengths["output_tokens"].append(budget.get("output_tokens", 0))
                for out in response.get("outputs", []):
                    for tool in out.get("tool_calls", []):
                        calls[tool.get("name", "unknown")] += 1
                for m in chat:
                    if m["role"] == "tool":
                        lengths["resent_tool_output_chars"].append(
                            len(str(m.get("content", "")))
                        )
        profiles[arm] = dict(
            requests=len(lengths["input_tokens"]),
            observed_tool_calls=dict(calls),
            distributions={
                key: dict(
                    sum=sum(values),
                    median=float(np.median(values)),
                    p90=float(np.quantile(values, 0.9)),
                    max=max(values),
                )
                for key, values in lengths.items()
                if values
            },
        )
    return profiles


def report() -> None:
    c.verify()
    rows = cells()
    ledger = c.accounting()
    paired_results: dict[str, Any] = {}
    totals: dict[str, Any] = {}
    for stage in ("validation", "test"):
        available = {r["arm"] for r in rows if r["stage"] == stage}
        for arm in sorted(available):
            subset = [
                r for r in rows if r["stage"] == stage and r["arm"] == arm
            ]
            total: dict[str, Any] = {
                key: sum(r[key] for r in subset)
                for key in (
                    "cost",
                    "uncached_cost",
                    "input",
                    "cached",
                    "output",
                    "requests",
                    "rocq_seconds",
                    "qualified",
                    "failed",
                )
            }
            total["cells"] = len(subset)
            total["cost_per_solve"] = (
                total["cost"] / total["qualified"]
                if total["qualified"]
                else None
            )
            total["cache_fraction"] = (
                total["cached"] / total["input"] if total["input"] else None
            )
            totals[f"{stage}/{arm}"] = total
            if arm != "agentic":
                reference = "agentic" if arm == "ace" else "ace"
                paired_results[f"{stage}/{reference}_vs_{arm}"] = paired(
                    rows, stage, arm, reference
                )
    events = [
        json.loads(line)
        for line in (c.CAMPAIGN / "events.jsonl").read_text().splitlines()
    ]
    mechanism: dict[str, Counter[str]] = defaultdict(Counter)
    for event in events:
        parts = event.get("cell", "").split("__")
        if len(parts) < 2:
            continue
        if event["kind"] == "admission_v2" and event["decision"] == "declined":
            mechanism[parts[1]].update(event.get("limiting", []))
        if event["kind"] == "economy_session":
            mechanism[parts[1]]["session_resets"] += 1
    result = dict(
        totals=totals,
        paired=paired_results,
        mechanism={k: dict(v) for k, v in mechanism.items()},
        spend=ledger["total"],
        receipts=ledger["receipts"],
        unresolved=ledger["unresolved"],
        billing_issues=ledger["billing_issues"],
        preparation_lower_bound=0.91692376 + 0.45092992,
        statistical_caution="Historical development and test partitions were previously exposed; equal observed coverage is not proof of noninferiority. Advisor comparisons are exploratory.",
    )
    destination = c.CAMPAIGN / "analysis"
    destination.mkdir(exist_ok=True)
    (destination / "results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    (destination / "profile.json").write_text(
        json.dumps(profile(), indent=2, sort_keys=True) + "\n"
    )
    (destination / "accounting.json").write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n"
    )
    with (c.CAMPAIGN / "cells.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# ACE economics: measured results",
        "",
        "| Panel / arm | Qualified | Cost | Cost / solve |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key, value in totals.items():
        lines.append(
            f"| {key} | {value['qualified']}/{value['cells']} | ${value['cost']:.6f} | ${value['cost_per_solve']:.6f} |"
        )
    lines += [
        "",
        f"New experimental spend: **${ledger['total']:.8f} / $50**.",
        "",
        "Inference totals include unsuccessful attempts. Historical book preparation adds at least $1.36785368 before embeddings. See analysis/results.json for paired confidence intervals, caching sensitivity and denominators. No default promotion.",
    ]
    (c.CAMPAIGN / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(
        json.dumps(
            dict(totals=totals, spend=ledger["total"], paired=paired_results),
            indent=2,
        )
    )


def replay() -> None:
    c.verify()
    before = c.accounting()["receipts"]
    checks: list[dict[str, Any]] = []
    for config in all_configs():
        original = c.cell_result(config)
        if original is None:
            checks.append(
                dict(cell=c.name(config, None), platform_failed=True)
            )
            continue
        c.activate(events=False)
        args = config.instantiate(None)
        args.cache_mode, args.cache_file = (
            "replay",
            str(c.directory(config) / "cache.yaml"),
        )
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Replay forbids HTTP"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(c.context(), cache_root=Path("/")),
                add_header=False,
            )
        if (
            out.result is None
            or out.result.success != original["success"]
            or out.result.spent_budget != original["spent_budget"]
            or json.loads(json.dumps(list(out.result.values)))
            != original["values"]
        ):
            raise ValueError("Exact replay mismatch: " + c.name(config, None))
        checks.append(dict(cell=c.name(config, None), passed=True))
    if before != c.accounting()["receipts"]:
        raise ValueError("Replay created a paid receipt")
    c.save("replay.json", dict(passed=True, paid_calls=0, cells=checks))
    print(json.dumps(dict(replayed=len(checks), paid_calls=0)))
