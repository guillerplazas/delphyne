"""Read-only analysis of the completed bounded campaign, without APIs/Rocq.

Only the frozen validation panel and its historical X3 seed-0 comparator
are read. Cached records are not invocation logs. Stop reasons below are
inferences, because declined admissions were not explicitly exported.
The small synthetic computation demonstrates reservation behavior without
executing a prover. Both agent harnesses can run this Python entrypoint.
"""

from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import delphyne as dp  # noqa: E402
from failure_analysis import refine_class  # noqa: E402
from prove_grounded import grounded_search  # noqa: E402
from tool_budget import ToolLimits  # noqa: E402

CAMPAIGN = ROOT / "experiments/campaigns/ace_bounded_20260908"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zero_work(limits: ToolLimits) -> dict[str, float]:
    return {"elapsed": 0.0, "requested_seconds": limits.seconds}


@dp.strategy
def short_compute() -> dp.Strategy[dp.Compute, object, dict[str, float]]:
    return (yield from dp.compute(zero_work)(ToolLimits(seconds=7)))


def reservation_probe() -> dict[str, int]:
    env = dp.PolicyEnv(
        object_loader=dp.ObjectLoader.trivial(),
        prompt_dirs=(),
        demonstration_files=(),
        data_dirs=(),
    )
    counts: dict[str, int] = {}
    for allowance in (7, 60):
        stream = short_compute().run_toplevel(env, grounded_search() & None)
        values, _ = stream.collect(
            budget=dp.BudgetLimit({"rocq_seconds": allowance})
        )
        counts[f"results_under_{allowance}_seconds"] = len(values)
    return counts


def main() -> None:
    frozen = json.loads((CAMPAIGN / "frozen.json").read_text())
    for name, sha in frozen["execution_hashes"].items():
        if digest(ROOT / name) != sha:
            raise ValueError(f"frozen execution source changed: {name}")
    cells = json.loads((CAMPAIGN / "validation_cells.json").read_text())
    prior_path = (
        ROOT
        / "experiments/campaigns/ace_review_20260908/development_cells.json"
    )
    prior = json.loads(prior_path.read_text())
    old = {
        n.split("__")[0]: row
        for n, row in prior.items()
        if "__x3-r64__" in n and n.endswith("__seed0")
    }
    run = ROOT / "experiments/output/ace_bounded_validation/configs"
    hashes = {str(prior_path.relative_to(ROOT)): digest(prior_path)}
    failures: list[dict[str, Any]] = []
    discordant: list[dict[str, Any]] = []
    classes: Counter[str] = Counter()
    terminals: Counter[str] = Counter()
    outcomes: Counter[str] = Counter()
    repeated = rejected = 0
    for name, cell in sorted(cells.items()):
        bench = cell["cell"][0]
        directory = run / name
        path = directory / "result.yaml"
        result: Any = yaml.load(path.read_text(), Loader=yaml.CSafeLoader)[
            "outcome"
        ]["result"]
        cache_path = directory / "cache.yaml"
        entries: list[dict[str, Any]] = yaml.load(
            cache_path.read_text(), Loader=yaml.CSafeLoader
        )
        hashes[str(path.relative_to(ROOT))] = digest(path)
        hashes[str(cache_path.relative_to(ROOT))] = digest(cache_path)
        checks: list[dict[str, Any]] = []
        max_chat = 0
        for entry in entries:
            req = entry["input"]["request"]
            chat = req["chat"]
            if req["options"]["model"] != "__compute__":
                max_chat = max(max_chat, len(json.dumps(chat).encode()))
                continue
            body = str(chat[-1].get("content", ""))
            output = entry.get("output")
            if body.startswith("fun: checked_proof") and output:
                checked: Any = yaml.load(
                    output["outputs"][0]["content"], Loader=yaml.CSafeLoader
                )
                checks.append(checked)
                outcomes[checked["outcome"]] += 1
        seen: set[str] = set()
        for checked in checks:
            fb = checked["feedback"]
            if fb["success"]:
                continue
            rejected += 1
            classes[refine_class(fb.get("error_message"))] += 1
            key = json.dumps(
                [
                    fb.get(k)
                    for k in (
                        "failing_tactic",
                        "error_message",
                        "proof_so_far",
                        "remaining_goals",
                    )
                ],
                sort_keys=True,
            )
            repeated += key in seen
            seen.add(key)
        before = bool(
            old[bench]["solved"] and old[bench]["charged_cost"] <= 0.1
        )
        if before != cell["solved"]:
            discordant.append(
                {
                    "bench": bench,
                    "x3_qualified": before,
                    "x3_cost": old[bench]["charged_cost"],
                    "x3_requests": old[bench]["http_attempts"],
                    "bounded_qualified": cell["solved"],
                    "bounded_cost": cell["cost"],
                }
            )
        if cell["solved"]:
            continue
        last = checks[-1] if checks else {}
        fb = last.get("feedback", {})
        terminal = refine_class(fb.get("error_message"))
        terminals[terminal] += 1
        trace = result["raw_trace"]
        last_node = max(int(n) for n in trace["nodes"])
        cands = f"local(%{last_node}, cands)" in trace["spaces"].values()
        spent = result["spent_budget"]
        hint = (
            "monetary admission (inferred)"
            if cands
            else "compute admission (inferred)"
        )
        failures.append(
            {
                "bench": bench,
                "cost": cell["cost"],
                "requests": spent.get("num_requests", 0),
                "rocq_seconds": spent.get("rocq_seconds", 0),
                "remaining_rocq_seconds": 300 - spent.get("rocq_seconds", 0),
                "last_recorded_class": terminal,
                "last_recorded_outcome": last.get("outcome"),
                "last_error": fb.get("error_message"),
                "last_tactic": fb.get("failing_tactic"),
                "goals": len(fb.get("remaining_goals", [])),
                "verified_prefix_length": len(fb.get("proof_so_far", [])),
                "max_cached_chat_bytes": max_chat,
                "stop_inference": hint,
                "last_check_elapsed": last.get("elapsed"),
            }
        )
    with (CAMPAIGN / "receipts.csv").open(newline="") as stream:
        receipts = list(csv.DictReader(stream))
    token_stats: dict[str, dict[str, float]] = {}
    for stage in ("training", "validation"):
        counts = [
            json.loads(r["usage"])["output_tokens"]
            for r in receipts
            if r["stage"] == stage
        ]
        token_stats[stage] = {
            "max": float(max(counts)),
            "p95": float(np.quantile(counts, 0.95)),
            "requests": len(counts),
        }
    final = json.loads((CAMPAIGN / "final_report.json").read_text())
    rows: dict[str, Any] = {
        "source_hashes": hashes,
        "script_sha256": digest(Path(__file__)),
        "scope": "User-authorized post-run diagnostic use of validationX; no fresh inference or confirmation claim; no API/Rocq calls.",
        "record_order_limit": "Last/repeated means cache insertion order, not last invocation; missing admission events prevent definitive stop attribution.",
        "compute_probe": reservation_probe(),
        "failures": failures,
        "discordant": discordant,
        "failure_classes": dict(classes.most_common()),
        "terminal_classes": dict(terminals.most_common()),
        "typed_check_outcomes": dict(outcomes),
        "unsolved_cost": sum(r["cost"] for r in failures),
        "failed_check_records": rejected,
        "repeated_failed_fingerprints": repeated,
        "output_tokens_including_reasoning": token_stats,
        "cost_per_qualified_solve": {
            "x3": final["cost_a"] / 28,
            "bounded": final["cost_b"] / 25,
        },
        "unspent_api_ceiling": 10 - final["campaign"]["liability"],
    }
    target = CAMPAIGN / "failure_audit.json"
    text = json.dumps(rows, indent=2, sort_keys=True) + "\n"
    if target.exists() and target.read_text() != text:
        raise ValueError("refusing to overwrite an existing audit")
    target.write_text(text)
    print(
        json.dumps(
            {
                k: v
                for k, v in rows.items()
                if k not in {"source_hashes", "failures"}
            },
            indent=2,
        )
    )
    for row in failures:
        print(
            row["bench"],
            row["last_recorded_class"],
            row["stop_inference"],
            row["last_tactic"],
        )


if __name__ == "__main__":
    main()
