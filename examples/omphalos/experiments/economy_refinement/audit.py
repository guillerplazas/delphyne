"""Audit paid request contracts without changing or rerunning treatments.

Both harnesses: python -m experiments.economy_refinement.audit
Only completed, explicitly registered trainX/validationX cells are read.
"""

from collections import defaultdict
import gzip
import json
from pathlib import Path
from typing import Any

from experiments import ace_economy_refinement_experiment as c

from . import state


def audit(batches: list[str]) -> dict[str, Any]:
    c.verify()
    jobs = [job for batch in batches for job in c.configs(batch)]
    for batch in batches:
        if not (c.CAMPAIGN / f"batches/{batch}.json").exists():
            raise ValueError("Only completed batches can be audited")
    ids = {c.name(job, None) for job in jobs}
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for line in (c.CAMPAIGN / "events.jsonl").open():
        event = json.loads(line)
        if event.get("cell") in ids:
            events[event["cell"]].append(event)

    first: dict[tuple[str, str, int, bool, bool, bool], dict[str, Any]] = {}
    contract: dict[str, Any] | None = None
    cells: list[dict[str, Any]] = []
    for job in jobs:
        ident = c.name(job, None)
        initial: str | None = None
        first_request: dict[str, Any] | None = None
        terminal: dict[str, Any] = {}
        pending_reset = False
        resets = checks = snapshots = removed = 0
        for event in events[ident]:
            if event.get("kind") == "terminal_v2":
                terminal = event
            if (
                event.get("kind") == "refined_session"
                and event.get("decision") == "reset"
            ):
                resets += 1
                if not job.reset or event["reset"] != resets or resets > 2:
                    raise ValueError("Unexpected reset sequence: " + ident)
                delta = event["before_chars"] - event["after_chars"]
                if delta < 8192:
                    raise ValueError("Reset savings bound failed: " + ident)
                if pending_reset:
                    raise ValueError("Multiple resets before a response")
                removed += delta
                pending_reset = True
            if (
                event.get("kind") != "transport"
                or event.get("decision") != "saved"
            ):
                continue
            path = (
                c.CAMPAIGN
                / "transport"
                / ident
                / (event["request"] + ".json.gz")
            )
            saved = json.loads(gzip.decompress(path.read_bytes()))
            request = saved["request"]["request"]
            snapshots += 1
            if initial is None:
                initial = saved["before"]
                first_request = request
            observed = {
                key: value for key, value in request.items() if key != "chat"
            }
            if contract is None:
                contract = observed
            if observed != contract:
                raise ValueError(
                    "Tool/model request contract changed: " + ident
                )
            if pending_reset:
                if saved["before"] != initial:
                    raise ValueError("Reasoning survived a reset: " + ident)
                checks += 1
                pending_reset = False
        if first_request is None:
            raise ValueError("Missing initial request: " + ident)
        key = (
            job.stage,
            job.bench_name,
            job.seed,
            job.ace,
            job.compact,
            job.reset,
        )
        if key in first:
            raise ValueError("Duplicate registered cell")
        first[key] = first_request
        result = state.cell_result(job)
        last_admission: dict[str, Any] = terminal.get("last_admission") or {}
        spent: dict[str, Any] = result["spent_budget"] if result else {}
        cells.append(
            dict(
                cell=ident,
                arm=job.arm,
                snapshots=snapshots,
                first_system_chars=len(first_request["chat"][0]["content"]),
                resets=resets,
                removed_chars=removed,
                cleared_reasoning_checks=checks,
                reset_without_completed_response=pending_reset,
                solved=bool(result and result["success"]),
                platform_failed=result is None,
                terminal_decision=terminal.get("decision"),
                terminal_limiting=last_admission.get("limiting", []),
                spent_num_requests=spent.get("num_requests"),
                spent_rocq_seconds=spent.get("rocq_seconds"),
            )
        )

    initial_drop_pairs = initial_compact_pairs = 0
    for key, request in first.items():
        stage, theorem, seed, ace, compact, reset = key
        if reset:
            base = first[(stage, theorem, seed, ace, compact, False)]
            if request != base:
                raise ValueError("Drop changed the initial request")
            initial_drop_pairs += 1
        if compact:
            base = first.get((stage, theorem, seed, ace, False, reset))
            if base is not None:
                if request["chat"][1:] != base["chat"][1:]:
                    raise ValueError(
                        "Compact changed initial examples/problem"
                    )
                initial_compact_pairs += 1
    return dict(
        cells=cells,
        initial_drop_pairs=initial_drop_pairs,
        initial_compact_pairs=initial_compact_pairs,
        identical_tool_and_model_contract=True,
        cleared_reasoning_checks=sum(
            r["cleared_reasoning_checks"] for r in cells
        ),
        reset_without_completed_response=sum(
            r["reset_without_completed_response"] for r in cells
        ),
        audit_code_sha256=c.sha(Path(__file__)),
        interpretation="Initial drop pairs have identical complete requests. Initial compact pairs differ only in system prose. All saved requests retain identical tool schemas and model options. Reset checks use the transport state before the next completed response; a reset can instead end at budget admission or provider failure. These are mechanism checks, not cost or coverage estimates.",
    )


def main() -> None:
    if not (c.CAMPAIGN / "benchmark_finished.json").exists():
        raise ValueError("Wait for the benchmark to finish")
    batches = [
        batch
        for batch in c.BATCHES
        if (c.CAMPAIGN / f"batches/{batch}.json").exists()
    ]
    result = audit(batches)
    result["events_sha256"] = c.sha(c.CAMPAIGN / "events.jsonl")
    c.save("analysis/request_audit.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "cells"}))


if __name__ == "__main__":
    main()
