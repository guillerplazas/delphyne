"""Offline transport recovery from the original stored provider responses.

Sidecars never modify original caches. Parser, reasoning state, translated
input bounds and full adaptive control are checked separately. An unavailable
response or replay mismatch is evidence to report, never a reason to replace
a sample. Census includes all matching permitted archives, not just wins.
"""

# pyright: reportPrivateUsage=false

from collections import Counter, defaultdict
from dataclasses import fields
import gzip
import json
import os
from pathlib import Path
from typing import Any

from delphyne.stdlib.models import (
    CachedRequest,
    LLMRequest,
    LLMOutput,
    LLMResponse,
)
from openai.types.responses import Response
from pydantic import TypeAdapter

from experiments.ace_thesis import campaign as old
from experiments.ace_sanitized.scope import partition
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import make_model
from runtime.replay_admission import fingerprint, transport_state
from tools.reports.ace_x3_forensics import raw

from . import campaign as c
from .audit import historical_cells, receipts
from .verification import kernel, replay_one


def replay_history() -> None:
    c.verify_seal()
    rows: list[dict[str, Any]] = []
    kernel_items: dict[tuple[str, str, str], list[str]] = {}
    for item in historical_cells():
        c.activate(events=False)
        os.environ.update(
            OMPHALOS_CAMPAIGN_STAGE="matrix",
            OMPHALOS_CAMPAIGN_CELL=item["cell"],
        )
        base = make_model(
            "gpt-5.6-luna",
            api="responses",
            for_tool_calls=True,
            reasoning_effort="medium",
            convert_user_feedback_to_tool=True,
        )
        assert isinstance(base, CampaignResponsesModel)
        model = CampaignResponsesModel(
            **{f.name: getattr(base, f.name) for f in fields(base) if f.init}
        )
        model.output_limit = 32768
        paid = receipts(Path(item["ledger"]), item["cell"])
        folder = c.ROOT / item["path"]
        entries = [
            e
            for e in raw(folder / "cache.yaml")
            if e["input"]["request"]["options"].get("model") != "__compute__"
        ]
        checked: list[dict[str, Any]] = []
        snapshots = c.CAMPAIGN / "historical_transport" / item["cell"]
        snapshots.mkdir(parents=True, exist_ok=True)
        result = raw(folder / "result.yaml")["outcome"]["result"]
        if result["success"]:
            key = (
                partition("validation")[item["theorem"]],
                item["theorem"],
                result["values"][0],
            )
            kernel_items.setdefault(key, []).append(item["cell"])
        try:
            if len(entries) != len(paid):
                raise ValueError("Receipt/cache count mismatch")
            for entry, receipt in zip(entries, paid):
                with gzip.open(
                    c.CAMPAIGN / "retrieved" / (receipt["id"] + ".json.gz"),
                    "rt",
                ) as stream:
                    retrieved = json.load(stream)
                if not retrieved["retrieved"]:
                    raise ValueError("Provider response unavailable")
                response = Response.model_validate(retrieved["response"])
                request = TypeAdapter(LLMRequest).validate_python(
                    entry["input"]["request"]
                )
                before = transport_state(model)
                bound = model._input_bound(request)
                if (
                    response.usage is None
                    or response.usage.to_dict()
                    != entry["output"]["usage_info"]
                ):
                    raise ValueError("Retrieved/cache usage mismatch")
                if bound != receipt["usage"]["input_bound"]:
                    raise ValueError(
                        f"Input reservation drift: {bound} versus {receipt['usage']['input_bound']}"
                    )
                output, _ = model._parse_response(response, request)
                expected = entry["output"].get("outputs", [])
                actual = [] if output is None else [output]
                if actual != TypeAdapter(list[LLMOutput]).validate_python(
                    expected
                ):
                    raise ValueError("Provider response/parser output drift")
                model.reasoning_allowance += response.usage.output_tokens
                normalized_request = TypeAdapter(CachedRequest).dump_python(
                    TypeAdapter(CachedRequest).validate_python(entry["input"]),
                    mode="json",
                )
                normalized_response = TypeAdapter(LLMResponse).dump_python(
                    TypeAdapter(LLMResponse).validate_python(entry["output"]),
                    mode="json",
                )
                path = snapshots / (
                    fingerprint(normalized_request) + ".json.gz"
                )
                value = dict(
                    version=1,
                    request=normalized_request,
                    before=fingerprint(before),
                    after=transport_state(model),
                    response=normalized_response,
                )
                if path.exists():
                    with gzip.open(path, "rt") as stream:
                        if json.load(stream) != value:
                            raise ValueError("Recovered snapshot drift")
                else:
                    with gzip.open(path, "xt") as stream:
                        json.dump(value, stream, sort_keys=True)
                checked.append(
                    dict(
                        receipt=receipt["id"],
                        request_sha256=fingerprint(entry["input"]),
                        input_bound=bound,
                        parser_equal=True,
                        before=fingerprint(before),
                        after=fingerprint(transport_state(model)),
                    )
                )
            arm = (
                "none_32768"
                if item["label"] == "historical_none"
                else "x3_32768"
            )
            job = c.Job(arm, item["theorem"], int(item["seed"]))
            replay_one(job, folder, snapshots, result)
            rows.append(
                dict(
                    cell=item["cell"],
                    label=item["label"],
                    theorem=item["theorem"],
                    passed=True,
                    requests=checked,
                )
            )
        except Exception as exc:
            rows.append(
                dict(
                    cell=item["cell"],
                    label=item["label"],
                    theorem=item["theorem"],
                    passed=False,
                    error=type(exc).__name__,
                    detail=str(exc),
                    requests=checked,
                )
            )
    c.save(
        "audit/historical_replay_v2.json",
        dict(
            cells=len(rows),
            passed=sum(r["passed"] for r in rows),
            requests_checked=sum(len(r["requests"]) for r in rows),
            results=rows,
            inference_requests=0,
        ),
    )
    kernel(kernel_items, "audit/historical_kernel.json")
    print(
        json.dumps(
            dict(
                cells=len(rows),
                replayed=sum(r["passed"] for r in rows),
                failures=dict(
                    Counter(r.get("detail") for r in rows if not r["passed"])
                ),
                unique_proofs=len(kernel_items),
            )
        )
    )


def census() -> None:
    book = historical_cells()[40]["record"]["book_sha256"]
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    included: list[dict[str, Any]] = []
    allowed = partition("validation")
    for item in old.read("audit/inventory.json")["included"]:
        if item["theorem"] not in allowed:
            continue
        record = old.read("audit/cells/" + fingerprint(item["path"]) + ".json")
        if record["book_sha256"] != book:
            continue
        included.append(record)
        comparator = dict(record["comparator"])
        comparator["policy_args"] = {
            k: v
            for k, v in comparator["policy_args"].items()
            if k
            not in ("snapshot_directory", "pause_file", "evidence_directory")
        }
        key = (
            record["campaign"],
            record["path"].rsplit("/configs/", 1)[0],
            fingerprint(comparator),
        )
        grouped[key].append(record)
    panels: list[dict[str, Any]] = []
    for (campaign, root, config), values in grouped.items():
        unique = {fingerprint(value["hashes"]) for value in values}
        panels.append(
            dict(
                campaign=campaign,
                root=root,
                comparator_sha256=config,
                cells=len(values),
                unique_measurements=len(unique),
                theorems=len({r["theorem"] for r in values}),
                seeds=sorted({r["seed"] for r in values}),
                solves=sum(r["solved"] for r in values),
                legacy_cost=sum(
                    r["cache_cost_current_tariff"] for r in values
                ),
                comparator=values[0]["comparator"],
                paths=[r["path"] for r in values],
            )
        )
    c.save(
        "audit/x3_census_v2.json",
        dict(
            book_sha256=book,
            cells=len(included),
            panels=panels,
            selection="Every permitted validation census record with exactly the historical rendered book hash; completeness and differing controls retained",
        ),
    )
    print(json.dumps(dict(x3_cells=len(included), panels=len(panels))))


def validate_provider_outputs() -> None:
    """Verify all parsed outputs even where encrypted input state is lost."""
    checked: list[dict[str, Any]] = []
    for item in historical_cells():
        c.activate(events=False)
        os.environ.update(
            OMPHALOS_CAMPAIGN_STAGE="matrix",
            OMPHALOS_CAMPAIGN_CELL=item["cell"],
        )
        model = make_model(
            "gpt-5.6-luna",
            api="responses",
            for_tool_calls=True,
            reasoning_effort="medium",
            convert_user_feedback_to_tool=True,
        )
        assert isinstance(model, CampaignResponsesModel)
        rows = receipts(Path(item["ledger"]), item["cell"])
        entries = [
            e
            for e in raw(c.ROOT / item["path"] / "cache.yaml")
            if e["input"]["request"]["options"].get("model") != "__compute__"
        ]
        if len(entries) != len(rows):
            raise ValueError("Receipt/cache alignment failure")
        for index, (entry, receipt) in enumerate(zip(entries, rows)):
            with gzip.open(
                c.CAMPAIGN / "retrieved" / (receipt["id"] + ".json.gz"), "rt"
            ) as stream:
                saved = json.load(stream)
            response = Response.model_validate(saved["response"])
            req = TypeAdapter(LLMRequest).validate_python(
                entry["input"]["request"]
            )
            bound = model._input_bound(req)
            output, _ = model._parse_response(response, req)
            if ([] if output is None else [output]) != TypeAdapter(
                list[LLMOutput]
            ).validate_python(entry["output"].get("outputs", [])):
                raise ValueError("Historical parser drift")
            assert response.usage is not None
            if response.usage.to_dict() != entry["output"]["usage_info"]:
                raise ValueError("Historical usage drift")
            model.reasoning_allowance += response.usage.output_tokens
            checked.append(
                dict(
                    cell=item["cell"],
                    receipt=receipt["id"],
                    index=index,
                    parser_equal=True,
                    usage_equal=True,
                    original_bound=receipt["usage"]["input_bound"],
                    retrieved_state_bound=bound,
                    missing_serialized_bytes=receipt["usage"]["input_bound"]
                    - bound,
                    service_tier=response.service_tier,
                    cache_retention=saved["response"].get(
                        "prompt_cache_retention"
                    ),
                )
            )
    c.save(
        "audit/provider_output_validation.json",
        dict(
            requests=len(checked),
            parser_equal=True,
            usage_equal=True,
            initial_bounds_equal=all(
                r["missing_serialized_bytes"] == 0
                for r in checked
                if r["index"] == 0
            ),
            requests_with_missing_transport_bytes=sum(
                r["missing_serialized_bytes"] != 0 for r in checked
            ),
            results=checked,
            limitation="Stored GET responses omit encrypted reasoning. Missing serialized bytes prevent reconstructing exact historical transport/admission on multi-turn runs. Equality of parsed outputs is established separately from full transport equality.",
        ),
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in c.read(
                    "audit/provider_output_validation.json"
                ).items()
                if k != "results"
            }
        )
    )
