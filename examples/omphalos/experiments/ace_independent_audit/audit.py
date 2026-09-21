"""Reconstruct permitted historical cells directly, never from reports.

All pricing in this census is normalized to 2026-09-19 standard US rates.
Missing cache-write usage makes the exact four-category cost unavailable.
Such cells retain their three-category lower bound and are explicitly flagged.
No campaign aggregate, partition loader, seal or historical summary is opened.
"""

from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, cast

import yaml

from .accounting import price
from .common import ROOT, REPORT, allowed, digest

DAY = date(2026, 9, 19)


def load_yaml(path: Path) -> Any:
    return yaml.load(path.read_text(), Loader=yaml.CSafeLoader)


def candidates() -> tuple[list[tuple[str, str]], dict[str, int]]:
    names = sorted(allowed(), key=len, reverse=True)
    pattern = re.compile(
        r"(?<![a-z0-9])(" + "|".join(map(re.escape, names)) + r")(?![a-z0-9])"
    )
    items: list[tuple[str, str]] = []
    excluded: Counter[str] = Counter()
    for archive in ("output", "previous"):
        base = ROOT / "experiments" / archive
        for directory, dirs, files in os.walk(base):
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    t in d.lower()
                    for t in (
                        "test",
                        "challenge",
                        "review",
                        "reserved",
                        "ladon",
                        "__pycache__",
                    )
                )
            ]
            if "result.yaml" not in files and "exception.txt" not in files:
                continue
            path = Path(directory)
            # Cell names, rather than arbitrary filenames or file contents,
            # must establish development membership before the first read.
            match = pattern.search(str(path.relative_to(base)))
            if match is None:
                excluded["no_explicit_allowed_theorem_in_path"] += 1
                continue
            items.append((str(path), match.group(1)))
    return sorted(items), dict(excluded)


def cell(item: tuple[str, str]) -> dict[str, Any]:
    folder, theorem = Path(item[0]), item[1]
    stage, problem = allowed()[theorem]
    result_path = folder / "result.yaml"
    raw: dict[str, Any] = (
        load_yaml(result_path) if result_path.exists() else {}
    )
    args = raw.get("args", {})
    sa = args.get("args", {})
    if sa.get("problem_file") and not str(sa["problem_file"]).endswith(
        problem
    ):
        raise ValueError(
            "Cell problem disagrees with explicit path membership"
        )
    if sa.get("theorem_name", theorem) != theorem:
        raise ValueError("Cell theorem mismatch")
    outer: dict[str, Any] = raw.get("outcome") or {}
    outcome: dict[str, Any] = outer.get("result") or {}
    cache = folder / "cache.yaml"
    rows: list[dict[str, Any]] = load_yaml(cache) if cache.exists() else []
    counts: Counter[str] = Counter()
    models: Counter[str] = Counter()
    tools: set[str] = set()
    request_hashes: list[str] = []
    checks: list[dict[str, Any]] = []
    turns: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    missing: Counter[str] = Counter()
    for i, row in enumerate(rows or []):
        output: dict[str, Any] = row.get("output") or {}
        request: dict[str, Any] = row.get("input", {}).get("request", {})
        model = output.get("model_name") or request.get("options", {}).get(
            "model", ""
        )
        if model == "__compute__":
            try:
                command: dict[str, Any] = yaml.safe_load(
                    request["chat"][-1]["content"]
                )
                answer: Any = yaml.safe_load(output["outputs"][0]["content"])
                function = command.get("fun", "")
                counts["compute:" + function] += 1
                if isinstance(answer, dict):
                    feedback: Any = cast(dict[str, Any], answer).get(
                        "feedback", answer
                    )
                    if isinstance(feedback, dict) and "success" in feedback:
                        feedback = cast(dict[str, Any], feedback)
                        entry = dict(
                            index=i,
                            function=function,
                            args=command.get("args"),
                            feedback=feedback,
                        )
                        checks.append(entry)
                        counts["checks"] += 1
                        counts["auto_finished"] += bool(
                            feedback.get("auto_finished")
                        )
                        counts["successful_checks"] += bool(
                            feedback.get("success")
                        )
            except (KeyError, TypeError, yaml.YAMLError):
                missing["unparsed_compute"] += 1
            continue
        if not model:
            missing["model"] += 1
            continue
        counts["requests"] += 1
        models[model] += 1
        request_hashes.append(digest(request))
        for t in request.get("tools", []):
            tools.add(
                t.get("name", t.get("function", {}).get("name", "unknown"))
            )
        u: dict[str, Any] = output.get("usage_info") or {}
        if "prompt_tokens" in u:
            u = dict(
                input_tokens=u["prompt_tokens"],
                output_tokens=u.get("completion_tokens"),
                input_tokens_details=u.get("prompt_tokens_details", {}),
                output_tokens_details=u.get("completion_tokens_details", {}),
            )
        details: dict[str, Any] = u.get("input_tokens_details") or {}
        complete = all(
            type(v) is int
            for v in (
                u.get("input_tokens"),
                u.get("output_tokens"),
                details.get("cached_tokens"),
                details.get("cache_write_tokens"),
            )
        )
        if not complete:
            missing["four_category_usage"] += 1
            b = output.get("budget", {}).get("values", {})
            u = dict(
                input_tokens=u.get("input_tokens", b.get("input_tokens", 0)),
                output_tokens=u.get(
                    "output_tokens", b.get("output_tokens", 0)
                ),
                input_tokens_details=dict(
                    cached_tokens=details.get(
                        "cached_tokens", b.get("cached_input_tokens", 0)
                    ),
                    cache_write_tokens=details.get("cache_write_tokens", 0),
                ),
            )
        try:
            costs = price(u, model, on=DAY)
            totals.update(costs)
            turns.append(dict(index=i, **costs))
        except (ValueError, TypeError):
            missing["unpriced_request"] += 1
        usage: dict[str, Any] = output.get("usage_info") or {}
        counts["reasoning_tokens"] += (
            usage.get("output_tokens_details", {}).get("reasoning_tokens", 0)
            or 0
        )
        for out in output.get("outputs", []):
            for tool in out.get("tool_calls", []):
                counts["tool:" + tool.get("name", "unknown")] += 1
        for log in output.get("log_items", []):
            counts[
                "log:" + str(log.get("name", log.get("label", "unknown")))
            ] += 1
    config = dict(
        strategy=args.get("strategy"),
        policy=args.get("policy"),
        budget=args.get("budget"),
        policy_args=args.get("policy_args"),
        strategy_args={
            k: v
            for k, v in sa.items()
            if k not in ("problem_file", "theorem_name")
        },
    )
    # This is an exact identity, not a claim that different historical paths
    # are comparable. Reporting forms matched panels separately.
    rel = folder.relative_to(ROOT / "experiments")
    seed = re.search(r"seed[_-]?(\d+)", folder.name)
    return dict(
        status="result" if result_path.exists() else "platform_error",
        archived_attempt=any(
            p in {"attempts", ".attempts"} for p in folder.parts
        ),
        path=str(folder.relative_to(ROOT)),
        archive=rel.parts[0],
        campaign=rel.parts[1],
        theorem=theorem,
        stage=stage,
        seed=int(seed[1]) if seed else None,
        config=config,
        config_hash=digest(config),
        models=dict(models),
        tools=sorted(tools),
        solved=bool(outcome.get("values")),
        value=outcome.get("values", []),
        diagnostics=raw.get("outcome", {}).get("diagnostics", []),
        spent_budget=outcome.get("spent_budget", {}),
        counts=dict(counts),
        costs=dict(totals),
        missing=dict(missing),
        exact_cost=not missing.get("four_category_usage")
        and not missing.get("unpriced_request"),
        request_digest=digest(request_hashes),
        first_request=request_hashes[:1],
        result_sha=hashlib.sha256(result_path.read_bytes()).hexdigest()
        if result_path.exists()
        else None,
        cache_sha=hashlib.sha256(cache.read_bytes()).hexdigest()
        if cache.exists()
        else None,
        checks=checks,
        turns=turns,
        exception=(folder / "exception.txt").read_text()
        if (folder / "exception.txt").exists()
        else None,
    )


def run() -> None:
    REPORT.mkdir(exist_ok=True, parents=True)
    items, excluded = candidates()
    (REPORT / "audit_inventory.json").write_text(
        json.dumps(
            dict(
                selected=len(items),
                excluded=excluded,
                paths=[i[0] for i in items],
                tariff_date=str(DAY),
                tier_assumption="default",
                regional_assumption=False,
            ),
            indent=2,
        )
    )
    totals: Counter[str] = Counter()
    errors: list[dict[str, str]] = []
    destination = REPORT / "raw_cells.jsonl"
    with (
        destination.open("w") as stream,
        ProcessPoolExecutor(max_workers=8) as pool,
    ):
        for _item, row in zip(items, pool.map(safe_cell, items), strict=True):
            if "error" in row:
                errors.append(row)
            else:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
                totals[row["campaign"]] += 1
    (REPORT / "audit_completion.json").write_text(
        json.dumps(
            dict(
                rows=sum(totals.values()),
                campaigns=dict(totals),
                errors=errors,
            ),
            indent=2,
        )
    )
    print(
        json.dumps(
            dict(
                rows=sum(totals.values()), campaigns=len(totals), errors=errors
            )
        )
    )


def safe_cell(item: tuple[str, str]) -> dict[str, Any]:
    try:
        return cell(item)
    except Exception as e:
        return dict(path=item[0], error=type(e).__name__ + ": " + str(e))
