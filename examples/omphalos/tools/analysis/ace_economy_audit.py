"""Offline prompt and budget diagnosis for the registered economics campaign.

Serialized chat messages place assistant text under ``answer``; this audit
counts those fields as well as user/tool content. The earlier frozen report
profile's ``all_message_chars`` and ``resent_tool_output_chars`` count only
top-level content, so they omit nested assistant answers and tool results.
These diagnostics supersede those descriptive fields; all money comes from
actual provider token receipts. Sealed selection and measurement code stays
unchanged; this independent offline audit corrects only prompt attribution.
"""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import json
import sqlite3
from typing import Any

import numpy as np

from experiments import ace_economy_validation as c
from runtime.model_registry import pricing_for


def distribution(values: list[int | float]) -> dict[str, int | float]:
    if not values:
        return dict(count=0, total=0)
    return dict(
        count=len(values),
        total=sum(values),
        median=float(np.median(values)),
        p90=float(np.quantile(values, 0.9)),
        maximum=max(values),
    )


def message_text(message: dict[str, Any]) -> str:
    if "answer" in message:
        answer = message["answer"]
        return str(answer.get("content", "")) + json.dumps(
            answer.get("tool_calls", []), ensure_ascii=False
        )
    if "result" in message:
        return str(message["result"])
    return str(message.get("content", ""))


def audit() -> dict[str, Any]:
    c.verify()
    current = c.accounting()
    if current["unresolved"] or current["billing_issues"]:
        raise ValueError("Finish and reconcile all requests first")
    with sqlite3.connect(c.CAMPAIGN / "ledger.sqlite3") as db:
        receipts = db.execute(
            "SELECT cell,usage,charged,created FROM receipts ORDER BY created,id"
        ).fetchall()
    by_cell: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cell, raw, charged, created in receipts:
        if not cell.startswith("validation__"):
            raise ValueError(
                "Only registered validation receipts are authorized"
            )
        usage = json.loads(raw)
        if "input_tokens" not in usage:
            continue
        by_cell[cell].append(
            dict(
                input=usage["input_tokens"],
                cached=usage.get("input_tokens_details", {}).get(
                    "cached_tokens", 0
                ),
                output=usage["output_tokens"],
                reasoning=usage.get("output_tokens_details", {}).get(
                    "reasoning_tokens", 0
                ),
                cost=charged,
                time=created,
            )
        )
    numbers: dict[str, dict[str, list[int | float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    tools: dict[str, Counter[str]] = defaultdict(Counter)
    sections: dict[str, Counter[str]] = defaultdict(Counter)
    mechanisms: dict[str, Counter[str]] = defaultdict(Counter)
    output_limits: dict[str, Counter[str]] = defaultdict(Counter)
    output_extremes: list[dict[str, Any]] = []
    for cell, calls in by_cell.items():
        stage, arm = cell.split("__")[:2]
        key = f"{stage}/{arm}"
        metrics = numbers[key]
        metrics["requests_per_problem"].append(len(calls))
        metrics["problem_cost"].append(sum(v["cost"] for v in calls))
        metrics["last_request_input_tokens"].append(calls[-1]["input"])
        metrics["first_request_input_tokens"].append(calls[0]["input"])
        metrics["last_to_first_input_ratio"].append(
            calls[-1]["input"] / calls[0]["input"]
        )
        for call in calls:
            rates = pricing_for(
                "gpt-5.6-luna",
                on=datetime.fromtimestamp(call["time"], timezone.utc).date(),
            )
            for field in ("input", "cached", "output", "reasoning"):
                metrics[field + "_tokens"].append(call[field])
            metrics["cached_input_dollars"].append(
                call["cached"] * rates.dollars_per_cached_input_token
            )
            metrics["fresh_input_dollars"].append(
                (call["input"] - call["cached"])
                * rates.dollars_per_input_token
            )
            metrics["output_dollars"].append(
                call["output"] * rates.dollars_per_output_token
            )
        for path in (c.CAMPAIGN / "transport" / cell).glob("*.json.gz"):
            with gzip.open(path, "rt") as f:
                saved = json.load(f)
            request = saved["request"]["request"]
            metrics["tool_schema_json_chars"].append(
                len(json.dumps(request["tools"], ensure_ascii=False))
            )
            messages = request["chat"]
            metrics["all_message_text_chars"].append(
                sum(len(message_text(m)) for m in messages)
            )
            for message in messages:
                role = message["role"]
                text = message_text(message)
                metrics[role + "_message_chars"].append(len(text))
                if role == "system":
                    for section in text.split("\n## ")[1:]:
                        heading = section.splitlines()[0]
                        sections[key][heading] += len(section)
                if role == "tool":
                    metrics["resent_tool_outputs_over_4096_chars"].append(
                        int(len(text) > 4096)
                    )
            for out in saved["response"].get("outputs", []):
                output_tokens = saved["response"]["budget"]["values"].get(
                    "output_tokens", 0
                )
                output_limits[key]["responses"] += 1
                output_limits[key]["over_4096_tokens"] += int(
                    output_tokens > 4096
                )
                output_limits[key]["over_8192_tokens"] += int(
                    output_tokens > 8192
                )
                if out.get("finish_reason") == "length":
                    output_limits[key]["length_limited"] += 1
                    output_extremes.append(
                        dict(
                            cell=cell,
                            snapshot=path.name,
                            output_tokens=output_tokens,
                            content_chars=len(out.get("content") or ""),
                            finish_reason="length",
                        )
                    )
                for tool in out.get("tool_calls", []):
                    tools[key][tool["name"]] += 1
    for line in (c.CAMPAIGN / "events.jsonl").read_text().splitlines():
        event = json.loads(line)
        parts = event.get("cell", "").split("__")
        if len(parts) < 2:
            continue
        key = "/".join(parts[:2])
        if event["kind"] == "admission_v2" and event["decision"] == "declined":
            mechanisms[key].update(event.get("limiting", []))
        if event["kind"] == "economy_session":
            mechanisms[key]["resets"] += 1
            numbers[key]["reset_removed_visible_chars"].append(
                event["before_chars"] - event["after_chars"]
            )
    result: dict[str, Any] = dict(
        arms={
            key: dict(
                distributions={
                    field: distribution(values)
                    for field, values in metrics.items()
                },
                tool_calls=dict(tools[key]),
                resent_system_section_chars=dict(sections[key]),
                mechanisms=dict(mechanisms[key]),
                output_limits=dict(output_limits[key]),
            )
            for key, metrics in numbers.items()
        },
        units="Provider token counts and dated dollars; prompt components are characters, not tokens. Repeated message appearances count resending work.",
        new_spend=current["total"],
        length_limited_outputs=output_extremes,
        profile_correction="Use this audit's all_message_text_chars and tool_message_chars; the frozen profile omitted nested assistant answers and tool results.",
    )
    reconstructed = sum(
        sum(values[field])
        for values in numbers.values()
        for field in (
            "cached_input_dollars",
            "fresh_input_dollars",
            "output_dollars",
        )
    )
    if abs(reconstructed - current["total"]) > 1e-8:
        raise ValueError("Cost decomposition does not equal settled receipts")
    destination = c.CAMPAIGN / "analysis/diagnostics.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
