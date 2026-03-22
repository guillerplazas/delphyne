#!/usr/bin/env python3
"""Summarize a step-by-step experiment run and compare it to a baseline CSV."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
import re

import yaml

import mini_eqns_experiments as meq

RULE_RE = re.compile(r"rule:\s*([A-Za-z_][A-Za-z0-9_]*)")



def load_baseline(path: Path) -> dict[str, bool]:
    with path.open() as f:
        rows = list(csv.DictReader(f))
    return {row["bench_name"].zfill(3): row["success"] == "True" for row in rows}



def expected_request_cap(data: dict) -> int:
    args = data["args"]
    policy_args = args["policy_args"]
    max_steps = args["args"].get("max_steps", 20)
    max_feedback = policy_args.get("max_feedback_cycles_per_step", 2)
    max_sketch_feedback = policy_args.get("max_sketch_feedback_cycles", 1)
    return (max_sketch_feedback + 1) + max_steps * (max_feedback + 1)



def summarize_result(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text())
    result = data["outcome"]["result"]
    eq = tuple(data["args"]["args"]["equality"])
    policy_args = data["args"]["policy_args"]
    spent = result.get("spent_budget", {})
    success = bool(result.get("success"))
    unsupported_rules: Counter[str] = Counter()

    for entry in result.get("log", []):
        if entry.get("message") != "llm_response":
            continue
        outputs = entry.get("metadata", {}).get("response", {}).get("outputs", [])
        if not outputs:
            continue
        content = outputs[0].get("content", "")
        for rule_name in RULE_RE.findall(content):
            if rule_name not in meq.BENCHS and rule_name not in {
                "cos_zero",
                "sin_zero",
                "sin_halfpi",
                "cos_halfpi",
                "sin_neg",
                "cos_neg",
                "cos_add",
                "sin_add",
            }:
                unsupported_rules[rule_name] += 1

    return {
        "bench_name": next(
            key for key, value in meq.BENCHS.items() if value == eq
        ),
        "equation": eq,
        "success": success,
        "num_requests": int(spent.get("num_requests", 0)),
        "price": float(spent.get("price", 0.0)),
        "request_cap": expected_request_cap(data),
        "step_model_name": policy_args.get("step_model_name"),
        "step_reasoning_effort": policy_args.get("step_reasoning_effort"),
        "unsupported_rules": unsupported_rules,
    }



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "experiment_dir",
        nargs="?",
        default="examples/mini_eqns/experiments/output/step_by_step_experiment",
        help="Path to an experiment output directory",
    )
    parser.add_argument(
        "--baseline",
        default="examples/mini_eqns/experiments/output/baseline_experiment_5_mini_max_10/results_summary.csv",
        help="Optional baseline results_summary.csv for per-benchmark comparison",
    )
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir)
    results = sorted(experiment_dir.glob("configs/*/result.yaml"))
    if not results:
        raise SystemExit(f"No result files found under {experiment_dir}")

    baseline_path = Path(args.baseline)
    baseline = load_baseline(baseline_path) if baseline_path.exists() else None

    summaries = [summarize_result(path) for path in results]
    successes = [s for s in summaries if s["success"]]
    failures = [s for s in summaries if not s["success"]]
    saturated_failures = [
        s for s in failures if s["num_requests"] >= s["request_cap"]
    ]
    unsupported = Counter()
    for summary in summaries:
        unsupported.update(summary["unsupported_rules"])

    print(f"Experiment: {experiment_dir}")
    print(f"Solved: {len(successes)}/{len(summaries)}")
    print(f"Total cost: ${sum(s['price'] for s in summaries):.4f}")
    print(
        f"Failed runs that hit request cap: {len(saturated_failures)}/{len(failures)}"
    )
    print()

    if unsupported:
        print("Unsupported invented rules proposed:")
        for rule_name, count in unsupported.most_common():
            print(f"  {rule_name}: {count}")
        print()

    if baseline is not None:
        print("Per-benchmark comparison vs baseline:")
        for summary in sorted(summaries, key=lambda s: s["bench_name"]):
            bid = str(summary["bench_name"])
            base = baseline.get(bid)
            marker = "same"
            if base is not None and summary["success"] != base:
                marker = "improved" if summary["success"] else "regressed"
            eq = summary["equation"]
            print(
                f"  {bid}: step={'Y' if summary['success'] else 'N'} "
                f"baseline={'Y' if base else 'N'} {marker} | {eq[0]} = {eq[1]}"
            )


if __name__ == "__main__":
    main()
