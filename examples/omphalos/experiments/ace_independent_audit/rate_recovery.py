"""Exact continuation after the replacement account's temporary TPM limit.

Resource-only amendment: four Rocq workers, one serialized HTTP dispatch,
400,000 observed input-plus-output tokens/minute pacing, and bounded retries
only for explicit zero-charge temporary 429 rejections. All original solver
settings, successful responses and registered cells remain unchanged.
Both harnesses use this entry point. SDK retries remain disabled.
"""

from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import fcntl
import gzip
import json
from pathlib import Path
import random
import re
import sys
import time
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.models import LLMRequest, LLMResponse
from delphyne.stdlib.tasks import run_command
import openai
from pydantic import TypeAdapter

from runtime.campaign_pause import request_pause
from runtime.replay_admission import transport_state

from . import campaign as c
from . import quota_recovery as q
from .audit import cell, load_yaml
from .common import CAMPAIGN, OUTPUT, ROOT, digest, now, read, save, sha
from .completion import ground_truth, require_closed
from .economics import ledger_rows
from .prefix_snapshots import isolated_snapshots
from .resumption import running
from .transport import AuditModel

BATCH = "core_frozen-part07"
FOLDER = CAMPAIGN / "rate_recovery"
FOLLOWING = ("core_scaling-part00", "core_scaling-part01", "adaptive_frozen")
WORKERS = 4
TOKEN_RATE = 400000


def raw_response(identity: str, receipt: str) -> tuple[Path, dict[str, Any]]:
    path = CAMPAIGN / "responses" / identity / (receipt + ".json.gz")
    with gzip.open(path, "rt") as stream:
        return path, json.load(stream)


def temporary_rejection(raw: dict[str, Any]) -> bool:
    error = raw.get("exception", {})
    return (
        error.get("type") == "RateLimitError"
        and error.get("rejected") is True
        and "'code': 'rate_limit_exceeded'" in error.get("message", "")
        and "tokens per min (TPM)" in error["message"]
    )


def jobs(batch: str) -> dict[str, c.Job]:
    return {
        c.name(j, None): j
        for value in read(CAMPAIGN / "batches" / (batch + ".json"))
        for j in [c.Job(**value)]
    }


def check_sources(batch: str) -> dict[str, str]:
    sources = read(CAMPAIGN / "batch_sources" / (batch + ".json"))
    if any(sha(ROOT / name) != expected for name, expected in sources.items()):
        raise ValueError("The registered solver source changed")
    return sources


def prepare() -> dict[str, Any]:
    path = FOLDER / "preparation.json"
    if path.exists():
        return read(path)
    if running(BATCH):
        raise ValueError("Wait for the current batch to return")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for receipt in ledger_rows():
        grouped.setdefault(receipt["cell"], []).append(receipt)
    interrupted: dict[str, Any] = {}
    completed: dict[str, Any] = {}
    for identity, job in jobs(BATCH).items():
        directory = OUTPUT / BATCH / "configs" / identity
        if ground_truth(directory) == "done":
            completed[identity] = {
                n: sha(directory / n)
                for n in ("cache.yaml", "result.yaml", "completed.json")
            }
            continue
        receipts = sorted(grouped[identity], key=lambda r: r["created"])
        raws = [raw_response(identity, r["id"])[1] for r in receipts]
        observed = cell((str(directory), job.theorem))
        if (
            ground_truth(directory) != "failed"
            or any(r["status"] != "settled" for r in receipts)
            or any("exception" in r for r in raws[:-1])
            or not temporary_rejection(raws[-1])
            or receipts[-1]["charged"] != 0
            or observed["counts"].get("requests", 0) != len(receipts) - 1
            or abs(
                observed["costs"].get("price", 0)
                - sum(r["charged"] for r in receipts)
            )
            > 1e-9
        ):
            raise ValueError("Unrecognized interruption: " + identity)
        original = FOLDER / "cells" / identity / "original"
        for filename in ("cache.yaml", "exception.txt"):
            q.preserve(directory / filename, original / filename)
        record = dict(
            cell=identity,
            batch=BATCH,
            prefix_responses=len(receipts) - 1,
            prefix_cost=sum(r["charged"] for r in receipts),
            receipts=[r["id"] for r in receipts],
            rejection=receipts[-1]["id"],
            preserved_hashes={
                n: sha(original / n) for n in ("cache.yaml", "exception.txt")
            },
            raw_hashes={
                r["id"]: sha(raw_response(identity, r["id"])[0])
                for r in receipts
            },
        )
        save(original.parent / "preparation.json", record)
        interrupted[identity] = record
    if len(completed) != 13 or len(interrupted) != 87:
        raise ValueError("Observed rate-limit incident denominator changed")
    q.preserve(
        OUTPUT / BATCH / "experiment.yaml", FOLDER / "original_experiment.yaml"
    )
    result = dict(
        at=now(),
        batch=BATCH,
        completed=completed,
        interrupted=interrupted,
        sources=check_sources(BATCH),
        scope="Continue 87 administrative interruptions and the original remaining 320 unlaunched cells. No new cells, seeds, solver changes, or successful-response replacements.",
        authorization=read(CAMPAIGN / "key_resumption_20260920.json"),
        workers=WORKERS,
        simultaneous_http=1,
        observed_token_pacing_per_minute=TOKEN_RATE,
        provider_reported_tpm=500000,
        maximum_temporary_retries=12,
        maximum_retry_seconds=900,
        docs="https://developers.openai.com/api/docs/guides/rate-limits",
        interpretation="Temporary token-rate rejections are administrative interruptions, not proof outcomes. All raw zero-charge receipts remain in all-attempt accounting. Queue/cache timing changes are disclosed; no hypothetical invoice replaces actual charges.",
    )
    save(path, result)
    print(
        json.dumps(dict(preserved=len(interrupted), completed=len(completed)))
    )
    return result


def offline_one(identity: str) -> dict[str, Any]:
    folder = FOLDER / "cells" / identity
    destination = folder / "prefix_certificate.json"
    if destination.exists():
        return read(destination)
    record = read(folder / "preparation.json")
    prefix = folder / "original/cache.yaml"
    with (
        patch.object(q, "BATCH", BATCH),
        patch.object(q, "CELL", identity),
        patch.object(q, "FOLDER", folder),
        patch.object(q, "RECEIPT", record["rejection"]),
        isolated_snapshots(identity, prefix),
    ):
        result = q.offline_prefix(0.10, prefix)
    result.update(
        cell=identity, preparation_sha=sha(folder / "preparation.json")
    )
    save(destination, result)
    return result


def offline() -> None:
    preparation = prepare()
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(offline_one, preparation["interrupted"]))
    if not all(r["passed"] and r["paid_calls"] == 0 for r in results):
        raise ValueError("An administrative prefix did not replay")
    save(FOLDER / "prefix_certification.json", results)
    print(json.dumps(dict(prefixes=len(results), paid_calls=0, passed=True)))


def retry_delay(error: openai.RateLimitError, attempt: int) -> float:
    """Respect a server minimum; never retry a billing or oversized request."""
    if error.code != "rate_limit_exceeded":
        raise error
    message = str(error)
    if "tokens per min (TPM)" not in message or "Request too large" in message:
        raise error
    amount = re.search(r"Limit\s+(\d+).*?Requested\s+(\d+)", message)
    if amount and int(amount[2]) > int(amount[1]):
        raise error
    headers = error.response.headers
    minimum = 0.0
    if headers.get("retry-after-ms"):
        try:
            minimum = max(minimum, float(headers["retry-after-ms"]) / 1000)
        except ValueError:
            pass
    value = headers.get("retry-after")
    if value:
        try:
            minimum = max(minimum, float(value))
        except ValueError:
            try:
                parsed = parsedate_to_datetime(value)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                minimum = max(
                    minimum,
                    (parsed - datetime.now(timezone.utc)).total_seconds(),
                )
            except (ValueError, TypeError, OverflowError):
                pass
    hint = re.search(r"try again in ([\d.]+)(ms|s)", message)
    if hint:
        minimum = max(
            minimum, float(hint[1]) / (1000 if hint[2] == "ms" else 1)
        )
    return max(minimum, min(60, 5 * 2**attempt)) + random.uniform(0.1, 0.5)


@contextmanager
def paced_transport():
    """Wrap audited dispatch, leaving its receipts and returned data intact."""
    original = AuditModel._send_final_request  # pyright: ignore[reportPrivateUsage]
    FOLDER.mkdir(parents=True, exist_ok=True)

    def send(model: AuditModel, request: LLMRequest) -> LLMResponse:
        encoded = TypeAdapter(LLMRequest).dump_python(request, mode="json")
        state = digest(transport_state(model))
        previous = model.previous_response()
        with (FOLDER / "dispatch.lock").open("a+") as gate:
            fcntl.flock(gate.fileno(), fcntl.LOCK_EX)
            pacing = FOLDER / "next_dispatch.txt"
            next_start = float(pacing.read_text()) if pacing.exists() else 0
            time.sleep(max(0, next_start - time.time()))
            started = time.time()
            with patch.object(
                model, "previous_response", return_value=previous
            ):
                for attempt in range(13):
                    try:
                        response = original(model, request)
                    except openai.RateLimitError as error:
                        if digest(transport_state(model)) != state or (
                            TypeAdapter(LLMRequest).dump_python(
                                request, mode="json"
                            )
                            != encoded
                        ):
                            raise ValueError(
                                "A rejected dispatch changed model state"
                            )
                        delay = retry_delay(error, attempt)
                        if (
                            attempt == 12
                            or time.time() + delay - started > 900
                        ):
                            request_pause(
                                Path(model.pause_file),
                                "Temporary rate retry allowance exhausted; preserve the exact trajectory",
                            )
                            raise
                        with (FOLDER / "dispatch_events.jsonl").open(
                            "a"
                        ) as log:
                            log.write(
                                json.dumps(
                                    dict(
                                        at=now(),
                                        cell=model.cell,
                                        request_sha=digest(encoded),
                                        retry=attempt + 1,
                                        wait_seconds=delay,
                                        code=error.code,
                                    )
                                )
                                + "\n"
                            )
                        time.sleep(delay)
                    else:
                        usage = response.usage_info or {}
                        tokens = usage.get("input_tokens", 0) + usage.get(
                            "output_tokens", 0
                        )
                        pacing.write_text(
                            str(
                                max(
                                    time.time(),
                                    started + tokens * 60 / TOKEN_RATE,
                                )
                            )
                        )
                        return response
        raise AssertionError("Unreachable rate-retry exhaustion")

    with patch.object(AuditModel, "_send_final_request", send):
        yield


def run_batch(batch: str, *, continuation: bool) -> None:
    from delphyne.stdlib.experiments import experiment_launcher as el

    if running(batch):
        raise ValueError("The target batch is already active")
    if continuation:
        preparation = prepare()
        prefixes = read(FOLDER / "prefix_certification.json")
        if {r["cell"] for r in prefixes} != preparation["interrupted"].keys():
            raise ValueError("A required exact-prefix check is missing")
        check_sources(batch)
    else:
        preparation = {}
        if (OUTPUT / batch / "experiment.yaml").exists():
            raise ValueError("New dispatch cannot replace an existing batch")

    def continue_command(*args: Any, **kwargs: Any) -> Any:
        identity = kwargs["args"].policy_args["cell"]
        if identity not in preparation["interrupted"]:
            raise ValueError("Continuation escaped its interrupted cells")
        record = preparation["interrupted"][identity]
        folder = FOLDER / "cells" / identity
        rejected = raw_response(identity, record["rejection"])[1]
        previous = (
            rejected["payload"]
            .get("extra_body", {})
            .get("prompt_cache_options", {})
            .get("comparison_response_id")
        )
        events: list[dict[str, Any]] = []
        with (
            patch.object(q, "CELL", identity),
            patch.object(q, "FOLDER", folder),
        ):
            q.restore_launcher_prefix(
                kwargs["args"], kwargs["ctx"], folder / "original/cache.yaml"
            )
            with q.continuation_adapter(
                folder / "original/cache.yaml",
                rejected["request"],
                offline=False,
                events=events,
                previous_response_id=previous,
            ):
                return run_command(*args, **kwargs)

    argv = ["rate_recovery", "run", f"--max_workers={WORKERS}", "--wait"]
    if continuation:
        argv.append("--retry_errors")
    start = FOLDER / (batch + "-start.json")
    save(
        start,
        dict(
            at=now(),
            batch=batch,
            continuation=continuation,
            source_sha=sha(Path(__file__)),
            workers=WORKERS,
            cell_count=len(jobs(batch)),
        ),
    )
    with paced_transport(), patch.object(sys, "argv", argv):
        if continuation:
            with patch.object(el, "run_command", continue_command):
                c.run_batch(batch)
        else:
            c.run_batch(batch)
    require_closed(batch)
    certify_batch(batch)


def certify_batch(batch: str) -> None:
    require_closed(batch)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for receipt in ledger_rows():
        grouped.setdefault(receipt["cell"], []).append(receipt)
    for identity, job in jobs(batch).items():
        receipts = sorted(
            grouped.get(identity, []), key=lambda r: r["created"]
        )
        raw = [raw_response(identity, r["id"])[1] for r in receipts]
        if not any(temporary_rejection(r) for r in raw):
            continue
        directory = OUTPUT / batch / "configs" / identity
        before = 0
        events: list[dict[str, Any]] = []
        for i, (receipt, value) in enumerate(zip(receipts, raw, strict=True)):
            if receipt["status"] != "settled":
                raise ValueError("Unresolved charge in continued cell")
            if "exception" in value:
                if (
                    not temporary_rejection(value)
                    or receipt["charged"] != 0
                    or i + 1 == len(raw)
                ):
                    raise ValueError("Unrecognized or unfinished rejection")
                if any(
                    value[k] != raw[i + 1][k] for k in ("request", "payload")
                ):
                    raise ValueError(
                        "A rate retry changed the provider payload"
                    )
                events.append(
                    dict(receipt=receipt["id"], before_response=before + 1)
                )
            else:
                before += 1
        observed = cell((str(directory), job.theorem))
        if (
            before != observed["counts"].get("requests", 0)
            or abs(
                sum(r["charged"] for r in receipts)
                - observed["costs"].get("price", 0)
            )
            > 1e-9
        ):
            raise ValueError("Rate-recovered cell does not reconcile")
        folder = FOLDER / "cells" / identity
        preserved: dict[str, str] = {}
        if (folder / "preparation.json").exists():
            prefix = load_yaml(folder / "original/cache.yaml")
            complete = load_yaml(directory / "cache.yaml")
            if Counter(map(digest, prefix)) - Counter(map(digest, complete)):
                raise ValueError("A continued cell changed its paid prefix")
            record = read(folder / "preparation.json")
            if [
                r["id"] for r in receipts[: len(record["receipts"])]
            ] != record["receipts"]:
                raise ValueError("The original paid receipts changed")
            preserved = {
                n: sha(folder / n)
                for n in (
                    "preparation.json",
                    "prefix_certificate.json",
                    "first_request_guard.json",
                )
            }
        save(
            FOLDER / "certificates" / (identity + ".json"),
            dict(
                cell=identity,
                batch=batch,
                events=events,
                completed_hashes={
                    n: sha(directory / n)
                    for n in ("cache.yaml", "result.yaml", "completed.json")
                },
                raw_hashes={
                    r["id"]: sha(raw_response(identity, r["id"])[0])
                    for r in receipts
                },
                preserved=preserved,
                successful_responses=before,
                attempted_requests=len(receipts),
                cost=observed["costs"].get("price", 0),
                passed=True,
            ),
        )
    if batch == BATCH:
        for identity, hashes in read(FOLDER / "preparation.json")[
            "completed"
        ].items():
            if any(
                sha(OUTPUT / batch / "configs" / identity / n) != value
                for n, value in hashes.items()
            ):
                raise ValueError("An already completed cell changed")
    print(
        json.dumps(dict(batch=batch, rate_accounting_certified=True)),
        flush=True,
    )


def rejection_events(identity: str, directory: Path) -> list[dict[str, Any]]:
    path = FOLDER / "certificates" / (identity + ".json")
    if not path.exists():
        return []
    certificate = read(path)
    if any(
        sha(directory / n) != value
        for n, value in certificate["completed_hashes"].items()
    ):
        raise ValueError("Certified rate continuation changed")
    for receipt, value in certificate["raw_hashes"].items():
        if sha(raw_response(identity, receipt)[0]) != value:
            raise ValueError("A rate-continuation receipt changed")
    folder = FOLDER / "cells" / identity
    if any(
        sha(folder / n) != value
        for n, value in certificate["preserved"].items()
    ):
        raise ValueError("Rate-continuation provenance changed")
    return certificate["events"]


def run() -> None:
    run_batch(BATCH, continuation=True)
    for batch in FOLLOWING:
        run_batch(batch, continuation=False)


if __name__ == "__main__":
    actions = {"prepare": prepare, "offline": offline, "run": run}
    if len(sys.argv) != 2 or sys.argv[1] not in actions:
        raise SystemExit("Use prepare, offline, or run")
    actions[sys.argv[1]]()
