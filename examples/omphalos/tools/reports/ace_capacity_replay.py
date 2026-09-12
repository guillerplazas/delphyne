"""Exact HTTP- and Rocq-disabled replay of registered new measurements."""

# ruff: noqa: E402
from runtime.development_only import install

install()

from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict
from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
import os
from pathlib import Path
import sys
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from experiments.ace import ace_capacity_experiment as c
from runtime.campaign_budget import CampaignResponsesModel
from runtime import pytanque_utils as pt
from tools.analysis.cell_records import (
    _result_head,  # pyright: ignore[reportPrivateUsage]
    _field,  # pyright: ignore[reportPrivateUsage]
)


def replay(job: dict[str, Any]) -> dict[str, Any]:
    cls = c.RoleConfig if job["kind"] == "role" else c.ProofConfig
    cfg = cls(**job["config"])
    c.activate(job["stage"])
    output = c.CAMPAIGN / "replay_events" / (cfg.identifier() + ".jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(output)
    args = cfg.instantiate(None)
    source = c.ROOT / job["source"]
    args.cache_file = str(source / "cache.yaml")
    args.cache_mode = "replay"
    args.export_raw_trace = args.export_browsable_trace = args.export_log = (
        False
    )
    if isinstance(cfg, c.ProofConfig):
        args.policy_args["prefix_cache"] = ""
    if c.ol.ground_truth(source) == "failed":
        # A rejected request has no response snapshot. Replay all completed
        # requests, then stop at its exact dispatch barrier without HTTP.
        errors = "\n".join(
            p.read_text() for p in source.glob("exception*.txt")
        )
        if (
            "openai.BadRequestError" not in errors
            or "invalid_prompt" not in errors
        ):
            raise ValueError("Unregistered failure kind")
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=RuntimeError("ARCHIVED_DISPATCH_BARRIER"),
            ),
            patch.object(
                pt, "check", side_effect=AssertionError("Replay forbids Rocq")
            ),
            redirect_stdout(io.StringIO()),
        ):
            try:
                run_command(
                    run_strategy,
                    args,
                    ctx=replace(c.context(), cache_root=Path("/")),
                    add_header=False,
                )
            except RuntimeError as exc:
                if str(exc) != "ARCHIVED_DISPATCH_BARRIER":
                    raise
            except ValueError as exc:
                if str(exc) != "Exact replay requires a transport snapshot":
                    raise
            else:
                raise ValueError(
                    "Failed prefix did not reach its dispatch barrier"
                )
        return dict(
            identifier=cfg.identifier(),
            source=job["source"],
            passed=True,
            success=False,
            failure_preserved=True,
            http_calls=0,
            rocq_computations=0,
            caveat="Exact cached prefix and failed dispatch admission; remote rejection is not reissued. Sequence equality is checked by audit.",
        )
    head = _result_head(source / "result.yaml")
    expected_success = _field(head, "success") == "true"
    budget = head[head.find("spent_budget:") :]
    expected = {
        key: float(_field(budget, key) or 0)
        for key in (
            "price",
            "num_completions",
            "input_tokens",
            "cached_input_tokens",
            "output_tokens",
            "rocq_seconds",
        )
    }
    with (
        patch.object(
            CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("Replay forbids HTTP"),
        ),
        patch.object(
            pt,
            "check",
            side_effect=AssertionError("Replay forbids Rocq execution"),
        ),
        redirect_stdout(io.StringIO()),
    ):
        outcome = run_command(
            run_strategy,
            args,
            ctx=replace(c.context(), cache_root=Path("/")),
            add_header=False,
        )
    result = outcome.result
    if result is None or result.success != expected_success:
        raise ValueError((cfg.identifier(), outcome.diagnostics))
    for key, value in expected.items():
        if abs(result.spent_budget.get(key, 0) - value) > 1e-8:
            raise ValueError(
                (cfg.identifier(), key, value, result.spent_budget.get(key))
            )
    events = [json.loads(line) for line in output.read_text().splitlines()]
    terminal = next(e for e in reversed(events) if e["kind"] == "terminal_v2")
    return dict(
        identifier=cfg.identifier(),
        source=job["source"],
        passed=True,
        success=result.success,
        spent=result.spent_budget,
        restored=sum(
            e["kind"] == "transport" and e["decision"] == "restored"
            for e in events
        ),
        terminal={
            k: terminal[k]
            for k in ("decision", "spent", "last_admission", "pending")
        },
        http_calls=0,
        rocq_computations=0,
    )


def main() -> None:
    group = sys.argv[1] if len(sys.argv) > 1 else "cross"
    c.verify()
    if group == "audit":
        audit_admissions()
        return
    jobs: list[dict[str, Any]] = []
    if group in ("cross", "creation", "mechanisms"):
        cls = c.RoleConfig if group == "creation" else c.ProofConfig
        for raw in c.read(f"planned_{group}.json"):
            cfg = cls(**raw)
            source = c.OUTPUT / group / "configs" / cfg.identifier()
            if c.ol.ground_truth(source) != "done":
                raise ValueError(f"No complete replay source: {source}")
            jobs.append(
                dict(
                    kind="role" if group == "creation" else "proof",
                    stage=group,
                    config=raw,
                    source=str(source.relative_to(c.ROOT)),
                )
            )
    elif group in ("headroom1", "headroom2"):
        level = int(group[-1])
        for raw in c.read("planned_mechanisms.json"):
            if raw["profile"] not in ("C", "E"):
                continue
            cfg = c.ProofConfig(**(raw | {"level": level}))
            if (c.CAMPAIGN / "carried" / f"{cfg.identifier()}.json").exists():
                continue
            jobs.append(
                dict(
                    kind="proof",
                    stage="headroom",
                    config=raw | {"level": level},
                    source=str(cfg.directory().relative_to(c.ROOT)),
                )
            )
    else:
        raise ValueError(group)
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for row in pool.map(replay, jobs):
            results.append(row)
            if len(results) % 20 == 0:
                print(
                    f"Exact replay {group}: {len(results)}/{len(jobs)}",
                    flush=True,
                )
    c.save(
        f"replay_{group}.json",
        dict(cells=len(results), all_passed=True, results=results),
    )


def audit_admissions() -> None:
    """Compare every estimate, budget decision and terminal against live."""
    kinds = {"estimate_v2", "admission_v2", "terminal_v2"}

    def clean(event: dict[str, Any]) -> dict[str, Any]:
        return {
            k: v
            for k, v in event.items()
            if k not in ("time", "pid", "stage", "cell")
        }

    paid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for line in (c.CAMPAIGN / "events.jsonl").read_text().splitlines():
        event = json.loads(line)
        if event["kind"] in kinds:
            paid[event["cell"]].append(clean(event))
    for group in ("cross", "creation", "mechanisms", "headroom1", "headroom2"):
        manifest = c.read(f"replay_{group}.json")
        items: list[dict[str, Any]] = []
        for row in manifest["results"]:
            name = row["identifier"]
            replayed = [
                clean(event)
                for line in (c.CAMPAIGN / "replay_events" / f"{name}.jsonl")
                .read_text()
                .splitlines()
                if (event := json.loads(line))["kind"] in kinds
            ]
            if paid[name] != replayed:
                raise ValueError(f"Admission or terminal drift: {name}")
            items.append(
                dict(
                    identifier=name,
                    equal=True,
                    paid_events=len(paid[name]),
                    replay_events=len(replayed),
                )
            )
        name = f"admission_parity_{group}.json"
        value = dict(all_equal=True, items=items)
        if (c.CAMPAIGN / name).exists():
            assert c.read(name) == value
        else:
            c.save(name, value)


if __name__ == "__main__":
    main()
