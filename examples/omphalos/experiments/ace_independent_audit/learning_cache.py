"""Six-call learning-only check of avoiding unused implicit cache writes.

The completed full preparations have zero cache reads. Reuse exactly six
recorded Sol author requests: reflection/curation at steps 10 and 30, and
terminal auditors 0 and 4. Change only prompt-cache mode to explicit with
no breakpoints. Make one request each, without retries or book updates.
Primary measurement: input tariff at identical recorded input content.
Output cost and schema validity are reported, not assumed identical.
This is a preparation diagnostic, never a benchmark solver treatment.
"""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import json
from typing import Any, cast
from urllib.parse import urlparse

import openai
from openai.types.responses import Response
from pydantic import TypeAdapter
import yaml

from runtime.campaign_budget import Ledger
from runtime.campaign_pause import request_pause

from .accounting import price, reserve
from .common import CAMPAIGN, REPORT, allowed, now, read, save, sha
from .economics import ledger_rows
from .learning import Delta, Reflection, Revision
from .learning_v3 import outer_yaml


def one_shot_payload(original: dict[str, Any]) -> dict[str, Any]:
    """Opt-in one-shot author policy; preserve every model-visible token."""
    payload = deepcopy(original)
    if "prompt_cache_breakpoint" in json.dumps(payload):
        raise ValueError("Explicit breakpoints already exist")
    if "prompt_cache_options" in payload:
        raise ValueError("Unexpected top-level cache policy")
    extra = dict(payload.get("extra_body", {}))
    extra["prompt_cache_options"] = dict(mode="explicit")
    payload["extra_body"] = extra
    return payload


def register() -> None:
    path = CAMPAIGN / "learning_cache_protocol.json"
    if path.exists():
        return
    selected = [
        row
        for row in ledger_rows()
        if row["cell"].startswith("full_A2__sol_medium__")
        and any(
            part in row["cell"]
            for part in (
                "__step10__",
                "__step30__",
                "__terminal_refine_0",
                "__terminal_refine_4",
            )
        )
    ]
    if len(selected) != 6 or any(r["status"] != "settled" for r in selected):
        raise ValueError("Expected six completed one-call author references")
    sources: list[dict[str, Any]] = []
    for row in selected:
        role_input = read(CAMPAIGN / "role_inputs" / (row["cell"] + ".json"))
        evidence = json.loads(role_input["evidence"])
        for trajectory in evidence.get("trajectories", [evidence]):
            if allowed().get(trajectory["theorem"], (None,))[0] != "train":
                raise ValueError("Diagnostic source is outside trainX")
        source = (
            CAMPAIGN / "responses" / row["cell"] / (row["id"] + ".json.gz")
        )
        sources.append(
            dict(
                cell=row["cell"],
                receipt=row["id"],
                response_file=str(source.relative_to(CAMPAIGN)),
                response_sha=sha(source),
            )
        )
    save(
        path,
        dict(
            registered_at=now(),
            calls=6,
            benchmark_cells=0,
            purpose=__doc__,
            source_selection="Fixed full_A2 steps10/30 and terminal audits0/4; no selection by diagnostic output",
            sources=sources,
            decision="Measure ordinary/read/write input categories, billed input, output cost, and role-schema validity. Do not relabel preparation savings as the thesis inference-cost target.",
            reference="https://developers.openai.com/api/docs/guides/prompt-caching#how-caching-works",
            limitation="Reuses historical identical author requests; fresh output content/tokens may differ. No new playbook is constructed or benchmarked. No artificial cache warming.",
        ),
    )


def call(source: dict[str, Any]) -> dict[str, Any]:
    identity = "learning_cache__" + source["cell"]
    result_path = CAMPAIGN / "learning_cache" / (identity + ".json")
    if result_path.exists():
        return read(result_path)
    if (CAMPAIGN / "HOLD_NEW_BATCHES.json").exists():
        raise ValueError("User-requested hold on new diagnostic calls")
    if (CAMPAIGN / "PAUSED").exists():
        raise ValueError("Campaign billing pause")
    if any(row["cell"] == identity for row in ledger_rows()):
        raise ValueError("A prior diagnostic request needs reconciliation")
    path = CAMPAIGN / source["response_file"]
    if sha(path) != source["response_sha"]:
        raise ValueError("Recorded author request changed")
    with gzip.open(path, "rt") as stream:
        original = json.load(stream)
    payload = one_shot_payload(original["payload"])
    if payload["model"] != "gpt-5.6-sol":
        raise ValueError("Unexpected learning model")
    day = datetime.now(timezone.utc).date()
    bound = reserve(
        payload["model"],
        original["input_bound"],
        payload["max_output_tokens"],
        day,
    )
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    key = ledger.reserve(
        "diagnostics",
        payload["model"],
        bound,
        identity,
        halt_on_billing_issue=True,
    )
    raw: dict[str, Any] = dict(
        receipt=key,
        cell=identity,
        started=now(),
        request=original["request"],
        payload=payload,
        input_bound=original["input_bound"],
        reserved=bound,
        source=source,
    )
    destination = CAMPAIGN / "responses" / identity / (key + ".json.gz")
    destination.parent.mkdir(parents=True, exist_ok=True)

    def persist() -> None:
        with gzip.open(destination, "xt") as stream:
            json.dump(raw, stream, sort_keys=True)

    try:
        with openai.OpenAI(max_retries=0, timeout=600) as client:
            raw["endpoint"] = str(client.base_url)
            host = urlparse(str(raw["endpoint"])).hostname
            if host != urlparse(str(original["endpoint"])).hostname:
                raise ValueError("Diagnostic endpoint differs from its source")
            response = cast(Response, client.responses.create(**payload))
    except Exception as exc:
        rejected = isinstance(
            exc, openai.APIStatusError
        ) and exc.status_code in {400, 401, 403, 404, 422, 429}
        raw["exception"] = dict(
            type=type(exc).__name__, message=str(exc), rejected=rejected
        )
        persist()
        ledger.settle(key, 0.0 if rejected else None, raw["exception"])
        if not rejected:
            request_pause(
                CAMPAIGN / "PAUSED", "Unresolved learning diagnostic billing"
            )
        raise
    raw["response"] = response.to_dict()
    raw["finished"] = now()
    persist()
    try:
        usage = response.usage
        if usage is None or usage.input_tokens > original["input_bound"]:
            raise ValueError("Invalid diagnostic usage")
        actual = price(
            usage.to_dict(),
            response.model,
            on=day,
            tier=response.service_tier or "unresolved",
            regional=host != "api.openai.com",
        )
    except Exception:
        ledger.settle(key, None, {"response_id": response.id})
        request_pause(CAMPAIGN / "PAUSED", "Unresolved diagnostic tariff")
        raise
    ledger.settle(
        key,
        actual["price"],
        dict(
            **usage.to_dict(),
            response_id=response.id,
            model=response.model,
            status=response.status,
            service_tier=response.service_tier,
            endpoint=raw["endpoint"],
            input_bound=original["input_bound"],
        ),
    )
    reference = price(
        original["response"]["usage"],
        original["response"]["model"],
        on=datetime.fromisoformat(original["started"]).date(),
        tier=original["response"]["service_tier"],
        regional=host != "api.openai.com",
    )
    role = (
        "reflect"
        if "__reflect__" in identity
        else "curate"
        if "__curate__" in identity
        else "refine"
    )
    schemas: dict[str, Any] = dict(
        reflect=Reflection, curate=Delta, refine=Revision
    )
    parsing: dict[str, Any]
    try:
        value = yaml.safe_load(outer_yaml(response.output_text))
        parsed = TypeAdapter(schemas[role]).validate_python(value)
        parsing = dict(
            valid=True, value=TypeAdapter(schemas[role]).dump_python(parsed)
        )
    except Exception as exc:
        parsing = dict(valid=False, error=type(exc).__name__ + ": " + str(exc))
    result = dict(
        cell=identity,
        receipt=key,
        source=source,
        role=role,
        original=reference,
        actual=actual,
        parsing=parsing,
        status=response.status,
        identical_input_tokens=actual["input"] == reference["input"],
        input_saving=1 - actual["input_cost"] / reference["input_cost"],
        total_saving=1 - actual["price"] / reference["price"],
        no_cache_reads_or_writes=actual["cached"] == actual["written"] == 0,
        raw_sha=sha(destination),
    )
    save(result_path, result)
    return result


def run() -> None:
    # Validate client configuration before reserving any request liability.
    with openai.OpenAI(max_retries=0, timeout=600) as client:
        if urlparse(str(client.base_url)).hostname not in (
            "api.openai.com",
            "us.api.openai.com",
            "eu.api.openai.com",
        ):
            raise ValueError("Unregistered diagnostic endpoint")
    register()
    sources = read(CAMPAIGN / "learning_cache_protocol.json")["sources"]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(call, sources))
    original_input = sum(r["original"]["input_cost"] for r in rows)
    actual_input = sum(r["actual"]["input_cost"] for r in rows)
    result = dict(
        calls=len(rows),
        benchmark_cells=0,
        results=rows,
        input_cost=dict(
            original=original_input,
            actual=actual_input,
            saving=1 - actual_input / original_input,
        ),
        original_total=sum(r["original"]["price"] for r in rows),
        actual_total=sum(r["actual"]["price"] for r in rows),
        valid_outputs=sum(r["parsing"]["valid"] for r in rows),
        equal_input_counts=all(r["identical_input_tokens"] for r in rows),
        zero_reads_and_writes=all(r["no_cache_reads_or_writes"] for r in rows),
        protocol=read(CAMPAIGN / "learning_cache_protocol.json"),
    )
    save(REPORT / "learning_cache_diagnostic.json", result)
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in ("results", "protocol")
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    run()
