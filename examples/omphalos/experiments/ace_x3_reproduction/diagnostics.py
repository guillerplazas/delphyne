"""Trace-level cap, cache and per-exercise evidence; no outcome selection."""

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

from delphyne.stdlib.models import LLMRequest
from pydantic import TypeAdapter

from experiments.ace_thesis import campaign as old
from experiments.ace_thesis.evidence import feedbacks, failure_category
from runtime.replay_admission import fingerprint
from tools.reports.ace_x3_forensics import raw

from . import campaign as c


def terminations(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Separate the controller's actual stop from the last proof error."""
    allowed = {r["cell"]: r for r in rows}
    terminal: dict[str, dict[str, Any]] = {}
    for line in (c.CAMPAIGN / "events.jsonl").open():
        event = json.loads(line)
        if event["kind"] != "terminal_v2" or event["cell"] not in allowed:
            continue
        if event["cell"] in terminal:
            raise ValueError("Duplicate terminal event")
        terminal[event["cell"]] = event
    if terminal.keys() != allowed.keys():
        raise ValueError("Missing terminal evidence")
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for cell, row in allowed.items():
        event = terminal[cell]
        if (event["decision"] == "solved") != row["solved"]:
            raise ValueError("Terminal outcome disagrees with result")
        limiting = event.get("last_admission", {}).get("limiting", [])
        reason = (
            "solved"
            if row["solved"]
            else "+".join(limiting) or event["decision"]
        )
        counts[row["label"]][reason] += 1
    return dict(
        counts={k: dict(v) for k, v in counts.items()},
        cells=terminal,
        limitation="A resource admission denial identifies why observed search stopped. It does not establish that more resources would solve the theorem; the last checked tactic failure is recorded separately in the exercise dossier.",
    )


def admission_tails(
    events: Path, rows: list[dict[str, Any]]
) -> dict[str, Any]:
    allowed = {r["cell"]: r for r in rows}
    estimates: dict[str, dict[str, Any]] = {}
    first: dict[str, dict[str, Any]] = {}
    observed: dict[str, set[str]] = defaultdict(set)
    for line in events.open():
        event = json.loads(line)
        cell = event.get("cell")
        if cell not in allowed:
            continue
        if event["kind"] == "estimate_v2":
            estimates[cell] = event
        if event["kind"] != "admission_v2" or not event["admitted"]:
            continue
        estimate = estimates.get(cell)
        if not estimate or estimate["output_limit"] != 8192:
            continue
        if event["estimate"].get("num_requests") != 1:
            continue
        if event["estimate"] != estimate["estimate"]:
            raise ValueError("Cannot associate admission with its estimate")
        observed[cell].add(estimate["request"])
        if (
            estimate["shadow_price_32768"]
            > event["remaining"]["price"] + 1e-12
        ):
            first.setdefault(
                cell,
                dict(
                    request=estimate["request"],
                    remaining=event["remaining"]["price"],
                    estimate_8192=estimate["estimate"]["price"],
                    estimate_32768=estimate["shadow_price_32768"],
                ),
            )
    tails: list[dict[str, Any]] = []
    request_type = TypeAdapter(LLMRequest)
    for cell, point in first.items():
        row = allowed[cell]
        entries = [
            e
            for e in raw(c.ROOT / row["path"] / "cache.yaml")
            if e["input"]["request"]["options"].get("model") != "__compute__"
        ]
        indices = [
            i
            for i, e in enumerate(entries)
            if fingerprint(
                request_type.dump_python(
                    request_type.validate_python(e["input"]["request"]),
                    mode="json",
                )
            )
            == point["request"]
        ]
        if not indices:
            # A request admitted but rejected before a cache write has no
            # observed tail. Keep it visible instead of assigning free work.
            tails.append(
                dict(
                    cell=cell,
                    label=row["label"],
                    theorem=row["theorem"],
                    **point,
                    cached_tail_available=False,
                )
            )
            continue
        index = indices[0]
        tail = entries[index:]
        tails.append(
            dict(
                cell=cell,
                label=row["label"],
                theorem=row["theorem"],
                **point,
                cached_tail_available=True,
                tail_requests=len(tail),
                tail_legacy_cost=sum(
                    e["output"]["budget"]["values"]["price"] for e in tail
                ),
                solved=row["solved"],
            )
        )
    return dict(
        affected_cells=dict(Counter(r["label"] for r in tails)),
        unique_admissions={
            label: sum(
                len(observed[r["cell"]]) for r in rows if r["label"] == label
            )
            for label in sorted({r["label"] for r in rows})
        },
        tails=tails,
        limitation="A 32768 reservation could not admit this request on the observed 8192 prefix. The counterfactual model outputs and proof outcomes are unobserved; tail cost is descriptive, not a causal saving.",
    )


def exercise_evidence(row: dict[str, Any]) -> dict[str, Any]:
    folder = c.ROOT / row["path"]
    checks = feedbacks(folder)
    counts: Counter[str] = Counter()
    for check in checks:
        feedback = check["feedback"]
        category = (
            "success"
            if feedback.get("success")
            else failure_category(
                feedback.get("error_message") or "",
                feedback.get("failing_tactic") or "",
            )
        )
        check["category"] = category
        counts[category] += 1
    cache: list[dict[str, Any]] = (
        raw(folder / "cache.yaml") if (folder / "cache.yaml").exists() else []
    )
    llm = [
        e
        for e in cache
        if e["input"]["request"]["options"].get("model") != "__compute__"
    ]
    provider: list[dict[str, Any]] = []
    for index, entry in enumerate(llm):
        request = entry["input"]["request"]
        output = entry["output"]
        provider.append(
            dict(
                index=index,
                request_sha256=fingerprint(request),
                input_tokens=output.get("usage_info", {}).get("input_tokens"),
                usage=output.get("usage_info"),
                outputs=output.get("outputs"),
                options=request["options"],
            )
        )
    result = (
        raw(folder / "result.yaml").get("outcome", {}).get("result")
        if (folder / "result.yaml").exists()
        else None
    )
    return dict(
        **row,
        failure_categories=dict(counts),
        terminal_check=checks[-1] if checks else None,
        checks=checks,
        returned_proof=result["values"] if result else [],
        requests_evidence=provider,
    )


def historical_diagnostics() -> None:
    rows = c.read("audit/cells.json")
    c.save(
        "audit/admission_tails_v2.json",
        admission_tails(
            old.CAMPAIGN / "events.jsonl",
            [
                r
                for r in rows
                if r["label"]
                in ("previous_nonace_matched", "previous_ace_historical")
            ],
        ),
    )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["theorem"]].append(exercise_evidence(row))
    for theorem, values in grouped.items():
        c.save("audit/exercises/" + theorem + ".json", values)
    print(
        json.dumps(
            dict(
                exercises=len(grouped),
                cells=len(rows),
                affected=c.read("audit/admission_tails_v2.json")[
                    "affected_cells"
                ],
            )
        )
    )


def input_stability(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Check actual rendered histories, not just initial request hashes."""
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    categories: dict[str, dict[str, Counter[str]]] = defaultdict(
        lambda: defaultdict(Counter)
    )
    changes: list[dict[str, Any]] = []
    requests: list[dict[str, Any]] = []
    for row in rows:
        entries = [
            e
            for e in raw(c.ROOT / row["path"] / "cache.yaml")
            if e["input"]["request"]["options"].get("model") != "__compute__"
        ]
        before: dict[str, Any] | None = None
        previous_hits: set[int] = set()
        for index, entry in enumerate(entries):
            after = entry["input"]["request"]
            output = entry["output"]
            theorem_indices = [
                i
                for i, message in enumerate(after["chat"])
                if message["role"] == "user"
                and "Theorem " + row["theorem"] + " " in message["content"]
            ]
            if not theorem_indices:
                raise ValueError("Cannot locate actual theorem user message")
            # Later checker feedback may quote a submitted declaration of
            # this same theorem. It is history, not another demonstration.
            theorem_index = theorem_indices[0]
            logs = {
                item["metadata"]["msg_index_in_chat"]: item["message"]
                for item in output.get("log_items", [])
                if item["message"]
                in ("reasoning_cache_hit", "reasoning_cache_miss")
                and item["metadata"]["msg_index_in_chat"] > theorem_index
            }
            hits = {i for i, v in logs.items() if v == "reasoning_cache_hit"}
            misses = set(logs) - hits
            phase = "first"
            changed_messages: list[int] = []
            if before is not None:
                checks = dict(
                    chat_append_only=after["chat"][: len(before["chat"])]
                    == before["chat"],
                    tools_equal=before.get("tools", [])
                    == after.get("tools", []),
                    options_equal=before["options"] == after["options"],
                )
                grouped[row["label"]].update(
                    dict(pairs=1, **{k: int(v) for k, v in checks.items()})
                )
                phase = "append" if all(checks.values()) else "rewrite"
                changed_messages = [
                    i
                    for i, message in enumerate(before["chat"])
                    if i >= len(after["chat"]) or after["chat"][i] != message
                ]
                if phase == "rewrite":
                    changes.append(
                        dict(
                            cell=row["cell"],
                            index=index,
                            changed_messages=changed_messages,
                            theorem_message_only=changed_messages
                            == [theorem_index],
                            **checks,
                        )
                    )
            usage = output["usage_info"]
            details = usage["input_tokens_details"]
            metrics = dict(
                requests=1,
                input=usage["input_tokens"],
                cached=details["cached_tokens"],
                written=details["cache_write_tokens"],
                output=usage["output_tokens"],
                reasoning_hits=len(hits),
                reasoning_misses=len(misses),
                hits_becoming_misses=len(previous_hits & misses),
            )
            categories[row["label"]][phase].update(metrics)
            requests.append(
                dict(
                    cell=row["cell"],
                    label=row["label"],
                    index=index,
                    phase=phase,
                    changed_messages=changed_messages,
                    reasoning_hit_indices=sorted(hits),
                    reasoning_miss_indices=sorted(misses),
                    **metrics,
                )
            )
            before, previous_hits = after, hits
    return dict(
        groups={k: dict(v) for k, v in grouped.items()},
        categories={
            label: {phase: dict(values) for phase, values in phases.items()}
            for label, phases in categories.items()
        },
        changes=changes,
        requests=requests,
        limitation="Rendered Delphyne chat/tools/options and actual reasoning-cache logs, excluding demonstration assistants before the target theorem. Counts are repeated lookups, not distinct reasoning items. Phase-conditioned token usage is observational, not a causal estimate of savings from a rewrite fix. Failed provider calls absent from local caches are excluded. Historical encrypted reasoning transport and provider cache routing are not reconstructed.",
    )
