"""Preserve and resume one credit-exhausted trajectory without resampling.

``prepare`` is entirely offline. It retains the original cache, exception,
launcher state and receipt, then proves that all four registered controllers
reach the same rejected request after replaying the complete paid prefix.
This is administrative censoring, not a failed theorem or a terminal sample.

The continuation adapter changes only this launcher's cache initialization.
The ordinary launcher otherwise deletes the cache when retrying a worker.
Every saved compute/model entry must be consumed, every transport state must
replay exactly, and the first new request must equal the rejected request.
No model answer, budget, book, solver source or completed cell is replaced.
Both agent harnesses use this same module.
"""

from collections import Counter
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import contextmanager, redirect_stdout
from dataclasses import asdict, replace
import importlib
import io
import gzip
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.models import LLMCache, LLMRequest
from delphyne.stdlib.tasks import run_command
from pydantic import TypeAdapter

from runtime.campaign_budget import CampaignResponsesModel
from runtime.campaign_pause import request_pause
from runtime.replay_admission import PrefixCache, PrefixGuard, transport_state

from . import campaign as c
from .audit import cell, load_yaml
from .common import (
    CAMPAIGN,
    OUTPUT,
    REPORT,
    ROOT,
    allowed,
    digest,
    now,
    read,
    save,
    sha,
)
from .completion import ground_truth
from .cost_bounds import receipt_interval
from .economics import ledger_rows
from .resumption import running
from .terminal_failure import completed_result, normal_budget, normal_replay
from .transport import AuditModel
from .verification import compile_one

BATCH = "core_frozen-part06"
CELL = "train__A2__amc12b_2004_p3__seed1"
RECEIPT = "e6704e3786fe4061913e81fe7e06df55"
FOLDER = CAMPAIGN / "quota_recovery"
REASON = "Provider credit balance exhausted; exact trajectory continuation pending account access"


def job() -> c.Job:
    return next(
        c.Job(**v)
        for v in read(CAMPAIGN / "batches" / (BATCH + ".json"))
        if c.name(c.Job(**v), None) == CELL
    )


def raw_rejection() -> dict[str, Any]:
    path = CAMPAIGN / "responses" / CELL / (RECEIPT + ".json.gz")
    with gzip.open(path, "rt") as stream:
        return json.load(stream)


def source_check() -> dict[str, str]:
    sources = read(CAMPAIGN / "batch_sources" / (BATCH + ".json"))
    if any(sha(ROOT / name) != expected for name, expected in sources.items()):
        raise ValueError("The registered solver source changed")
    return sources


def preserve(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if sha(target) != sha(source):
            raise ValueError("A preserved administrative artifact changed")
    else:
        shutil.copy2(source, target)


class PrefixReached(Exception):
    """Offline sentinel: the exact rejected request was reached."""


@contextmanager
def continuation_adapter(
    prefix: Path,
    expected_request: dict[str, Any],
    *,
    offline: bool,
    events: list[dict[str, Any]],
    previous_response_id: str | None = None,
):
    """Install invocation-local guards; never alter the registered solver."""
    rs = importlib.import_module("delphyne.stdlib.commands.run_strategy")
    original_cache_spec = rs.with_cache_spec
    original_send = AuditModel._send_final_request  # pyright: ignore[reportPrivateUsage]
    guard: PrefixGuard | None = None
    expected_entries = Counter(digest(v) for v in load_yaml(prefix))

    def cache_spec(f: Callable[..., Any], **kwargs: Any) -> Any:
        if kwargs["cache_mode"] != "read_write":
            raise ValueError("Continuation must preserve and extend its cache")

        def receive(cache: LLMCache | None, embeddings: Any) -> Any:
            nonlocal guard
            if cache is None:
                raise ValueError("A saved request cache is required")
            actual = Counter(
                digest(v)
                for v in load_yaml(
                    Path(kwargs["cache_root"]) / kwargs["cache_file"]
                )
            )
            if actual != expected_entries:
                raise ValueError(
                    "The continuation did not load the exact prefix"
                )
            guard = PrefixGuard(set(cache.cache.dict))
            wrapped = LLMCache(
                PrefixCache(cache.cache.dict, cache.cache.mode, guard)
            )
            wrapped.num_seen = cache.num_seen
            return f(wrapped, embeddings)

        return original_cache_spec(receive, **kwargs)

    def send(model: AuditModel, request: LLMRequest) -> Any:
        if model.cell != CELL:
            raise ValueError(
                "Continuation dispatch escaped its registered cell"
            )
        first = not events
        if first:
            encoded = TypeAdapter(LLMRequest).dump_python(request, mode="json")
            if guard is None or guard.remaining or encoded != expected_request:
                raise ValueError(
                    "Paid prefix or first resumed request diverged"
                )
            events.append(
                dict(
                    request_sha=digest(encoded),
                    prefix_entries=sum(expected_entries.values()),
                    prefix_consumed=True,
                    transport_state_sha=digest(transport_state(model)),
                )
            )
            if offline:
                raise PrefixReached
            save(FOLDER / "first_request_guard.json", events[0])
        elif offline:
            raise AssertionError(
                "An offline replay attempted a second dispatch"
            )
        if first:
            # The quota rejection is not a new model response. Retain the
            # same diagnostic comparison ID on the first resumed request.
            with patch.object(
                model, "previous_response", return_value=previous_response_id
            ):
                return original_send(model, request)
        return original_send(model, request)

    with (
        patch.object(rs, "with_cache_spec", cache_spec),
        patch.object(AuditModel, "_send_final_request", send),
    ):
        yield


def offline_prefix(cap: float, prefix: Path) -> dict[str, Any]:
    c.activate()
    import os

    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
        FOLDER / "replay_events.jsonl"
    )
    rs = importlib.import_module("delphyne.stdlib.commands.run_strategy")
    before = sha(prefix)
    events: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(
        prefix="quota-prefix-", dir=CAMPAIGN
    ) as tmp:
        copied = Path(tmp) / "cache.yaml"
        shutil.copy2(prefix, copied)
        args = job().instantiate(None)
        args.budget = dict(price=cap, num_requests=32)
        args.cache_file = str(copied)
        args.cache_mode = "read_write"
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            continuation_adapter(
                prefix, raw_rejection()["request"], offline=True, events=events
            ),
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("HTTP forbidden"),
            ),
            patch(
                "openai.OpenAI", side_effect=AssertionError("HTTP forbidden")
            ),
            redirect_stdout(io.StringIO()),
        ):
            try:
                run_command(
                    rs.run_strategy,
                    args,
                    ctx=replace(c.context(), cache_root=Path("/")),
                    add_header=False,
                )
            except PrefixReached:
                pass
            else:
                raise ValueError("The exact rejected request was not reached")
    if len(events) != 1 or sha(prefix) != before:
        raise ValueError("Offline continuation changed its evidence")
    return dict(cap=cap, **events[0], paid_calls=0, passed=True)


def certify_returned() -> dict[str, Any]:
    destination = REPORT / "returned_part06_certification.json"
    if destination.exists():
        return read(destination)
    jobs = [c.Job(**v) for v in read(CAMPAIGN / "batches" / (BATCH + ".json"))]
    normal = [j for j in jobs if c.name(j, None) != CELL]
    if len(normal) != 99 or any(
        ground_truth(OUTPUT / BATCH / "configs" / c.name(j, None)) != "done"
        for j in normal
    ):
        raise ValueError("The other 99 outcomes are not complete")
    with ProcessPoolExecutor(max_workers=8) as pool:
        replays = list(pool.map(normal_replay, [(BATCH, j) for j in normal]))
        budget = list(
            pool.map(normal_budget, [(BATCH, asdict(j)) for j in normal])
        )
    proofs: dict[tuple[str, str, str], list[str]] = {}
    for j in normal:
        identity = c.name(j, None)
        for proof in completed_result(BATCH, identity)["values"]:
            key = (allowed()[j.theorem][1], j.theorem, str(proof))
            proofs.setdefault(key, []).append(identity)
    with ThreadPoolExecutor(max_workers=8) as pool:
        kernels = [
            dict(r, cells=proofs[k])
            for k, r in zip(proofs, pool.map(compile_one, proofs), strict=True)
        ]
    if not all(r["passed"] for r in kernels):
        raise ValueError("A returned proof failed independent compilation")
    result = dict(
        batch=BATCH,
        normal_completed_cells=len(normal),
        administratively_censored_cell=CELL,
        replays=replays,
        kernel=kernels,
        budget_scenarios=sum(map(len, budget)),
        paid_calls=0,
        note="The 99 returned cells are certified. The credit-exhausted cell is incomplete and excluded from any full-panel verdict; its paid prefix is retained separately.",
    )
    save(destination, result)
    return result


def prepare() -> dict[str, Any]:
    destination = FOLDER / "preparation.json"
    if destination.exists():
        record = read(destination)
        for filename, expected in record["preserved_hashes"].items():
            if sha(FOLDER / "original" / filename) != expected:
                raise ValueError(
                    "The preserved credit-exhaustion evidence changed"
                )
        source_check()
        return record
    if running(BATCH):
        raise ValueError("The original worker is still running")
    sources = source_check()
    directory = OUTPUT / BATCH / "configs" / CELL
    state = load_yaml(OUTPUT / BATCH / "experiment.yaml")["configs"]
    if (
        state[CELL]["status"] != "failed"
        or not state[CELL].get("end_time")
        or (directory / "result.yaml").exists()
        or any(v["status"] != "done" for k, v in state.items() if k != CELL)
    ):
        raise ValueError("Unexpected administrative interruption state")
    all_receipts = ledger_rows()
    for receipt in all_receipts:
        receipt_interval(receipt)
    receipts = sorted(
        [r for r in all_receipts if r["cell"] == CELL],
        key=lambda r: r["created"],
    )
    raw = raw_rejection()
    exception = raw.get("exception", {})
    if (
        len(receipts) != 9
        or receipts[-1]["id"] != RECEIPT
        or receipts[-1]["charged"] != 0
        or any(r["status"] != "settled" for r in receipts)
        or exception.get("type") != "RateLimitError"
        or not exception.get("rejected")
        or "credit_balance_exhausted" not in exception.get("message", "")
    ):
        raise ValueError(
            "Unexpected rejection or incomplete request accounting"
        )
    observed = cell((str(directory), job().theorem))
    prefix_cost = sum(r["charged"] for r in receipts)
    if (
        not observed["exact_cost"]
        or observed["counts"]["requests"] != 8
        or abs(observed["costs"]["price"] - prefix_cost) > 1e-9
    ):
        raise ValueError("The paid prefix does not reconcile")
    request_pause(CAMPAIGN / "PAUSED", REASON)
    if read(CAMPAIGN / "PAUSED")["reason"] != REASON:
        raise ValueError("A different pause also requires reconciliation")
    for filename in ("cache.yaml", "exception.txt"):
        preserve(directory / filename, FOLDER / "original" / filename)
    preserve(
        OUTPUT / BATCH / "experiment.yaml",
        FOLDER / "original" / "experiment.yaml",
    )
    prefix = FOLDER / "original" / "cache.yaml"
    replays = [
        offline_prefix(cap, prefix) for cap in (0.10, 0.05, 0.075, 0.09)
    ]
    normal = certify_returned()
    result = dict(
        prepared_at=now(),
        cell=CELL,
        batch=BATCH,
        receipt=RECEIPT,
        receipt_row=receipts[-1],
        raw_evidence_sha=sha(
            CAMPAIGN / "responses" / CELL / (RECEIPT + ".json.gz")
        ),
        preserved_hashes={
            p.name: sha(p) for p in (FOLDER / "original").iterdir()
        },
        batch_manifest_sha=sha(CAMPAIGN / "batches" / (BATCH + ".json")),
        registered_sources=sources,
        successful_responses=8,
        attempted_requests=9,
        prefix_cost=prefix_cost,
        rejected_cost=0.0,
        receipts=[r["id"] for r in receipts],
        exception=exception,
        prefix_replays=replays,
        other_cells_certified=normal["normal_completed_cells"],
        settled_research_cost=sum(
            r["charged"] for r in all_receipts if r["status"] == "settled"
        ),
        retained_unknown_invoice_upper=sum(
            r["charged"]
            for r in all_receipts
            if r["status"] == "bounded_charge"
        ),
        status="administratively_censored_pending_account_access",
        continuation="After account access is restored, replay the complete saved prefix and continue at the identical rejected request, within the original attempt and unchanged total budgets. Preserve the zero-charge rejection in all-attempt request counts. Never resample the preceding eight responses or classify the unfinished trajectory as a theorem failure.",
        paid_calls=0,
    )
    save(destination, result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "cell",
                    "prefix_cost",
                    "successful_responses",
                    "attempted_requests",
                    "other_cells_certified",
                    "status",
                    "paid_calls",
                )
            }
        )
    )
    return result


def reconcile_continuation() -> dict[str, Any]:
    """Verify provider identity, exact prefix inclusion and every charge."""
    from .completion import require_closed

    require_closed(BATCH)
    record = read(FOLDER / "preparation.json")
    directory = OUTPUT / BATCH / "configs" / CELL
    if ground_truth(directory) != "done":
        raise ValueError(
            "The resumed worker has not returned a completed result"
        )
    prefix = load_yaml(FOLDER / "original" / "cache.yaml")
    complete = load_yaml(directory / "cache.yaml")
    if Counter(map(digest, prefix)) - Counter(map(digest, complete)):
        raise ValueError(
            "The completed trajectory changed or omitted its paid prefix"
        )
    receipts = sorted(
        [r for r in ledger_rows() if r["cell"] == CELL],
        key=lambda r: r["created"],
    )
    if [r["id"] for r in receipts[:9]] != record["receipts"] or len(
        receipts
    ) <= 9:
        raise ValueError("The recorded prefix receipts changed")
    if any(r["status"] != "settled" for r in receipts):
        raise ValueError("The continuation has unresolved charges")
    with gzip.open(
        CAMPAIGN / "responses" / CELL / (receipts[9]["id"] + ".json.gz"), "rt"
    ) as stream:
        first = json.load(stream)
    rejected = raw_rejection()
    if (
        first["request"] != rejected["request"]
        or first["payload"] != rejected["payload"]
    ):
        raise ValueError(
            "The resumed provider request differs from the saved rejection"
        )
    exceptions = [
        r for r in receipts if json.loads(r["usage"]).get("rejected")
    ]
    observed = cell((str(directory), job().theorem))
    if (
        [r["id"] for r in exceptions] != [RECEIPT]
        or exceptions[0]["charged"] != 0
        or not observed["exact_cost"]
        or len(receipts) != observed["counts"]["requests"] + 1
        or abs(
            sum(r["charged"] for r in receipts) - observed["costs"]["price"]
        )
        > 1e-9
    ):
        raise ValueError("Continued trajectory accounting does not reconcile")
    certificate = dict(
        cell=CELL,
        batch=BATCH,
        preparation_sha=sha(FOLDER / "preparation.json"),
        start_sha=sha(FOLDER / "continuation_start.json"),
        guard_sha=sha(FOLDER / "first_request_guard.json"),
        completed_hashes={
            name: sha(directory / name)
            for name in ("cache.yaml", "result.yaml", "completed.json")
        },
        prefix_entries=len(prefix),
        prefix_included_exactly=True,
        first_resumed_request_and_payload_identical=True,
        zero_charge_rejections=[RECEIPT],
        successful_api_responses=observed["counts"]["requests"],
        attempted_api_requests=len(receipts),
        cost=observed["costs"]["price"],
        solved=observed["solved"],
        note="One original trajectory continued after account credit restoration. Eight prior responses and all compute feedback were replayed, not resampled. The credit rejection is retained at zero charge and included in attempted-request counts. The model budget counts successful responses as before. Cross-account cache behavior, if any, remains part of actual observed tariff costs.",
    )
    save(FOLDER / "continuation_certificate.json", certificate)
    return certificate


def restore_launcher_prefix(
    command_args: Any, context: Any, prefix: Path
) -> None:
    """Replace only this worker's fresh-cache initialization with its prefix."""
    policy_args: dict[str, Any] = command_args.policy_args or {}
    if policy_args.get("cell") != CELL:
        raise ValueError("The continuation tried to relaunch another cell")
    cache = Path(context.cache_root) / command_args.cache_file
    if cache.exists() or command_args.cache_mode != "create":
        raise ValueError("Unexpected launcher cache initialization")
    shutil.copy2(prefix, cache)
    command_args.cache_mode = "read_write"


def resume(account_ready_message: str) -> None:
    """Continue only after the user reports account access restored."""
    if not account_ready_message.strip():
        raise ValueError(
            "Record the actual account-readiness message, never a credential"
        )
    record = prepare()
    directory = OUTPUT / BATCH / "configs" / CELL
    pause = CAMPAIGN / "PAUSED"
    if running(BATCH) or not pause.exists() or read(pause)["reason"] != REASON:
        raise ValueError("The recorded credit pause is not the current state")
    if (FOLDER / "continuation_start.json").exists():
        raise ValueError(
            "This continuation already started; inspect its outcome before another dispatch"
        )
    for filename in ("cache.yaml", "exception.txt"):
        if sha(directory / filename) != record["preserved_hashes"][filename]:
            raise ValueError("The original censored trajectory changed")
    from delphyne.stdlib.experiments import experiment_launcher as el

    original_command = run_command
    prefix = FOLDER / "original" / "cache.yaml"
    rejected = raw_rejection()
    previous = (
        rejected["payload"]
        .get("extra_body", {})
        .get("prompt_cache_options", {})
        .get("comparison_response_id")
    )

    def continue_command(*args: Any, **kwargs: Any) -> Any:
        command_args = kwargs["args"]
        context = kwargs["ctx"]
        restore_launcher_prefix(command_args, context, prefix)
        events: list[dict[str, Any]] = []
        with continuation_adapter(
            prefix,
            rejected["request"],
            offline=False,
            events=events,
            previous_response_id=previous,
        ):
            return original_command(*args, **kwargs)

    save(
        FOLDER / "continuation_start.json",
        dict(
            at=now(),
            account_ready_message=account_ready_message,
            work_authorization=read(CAMPAIGN / "resumption.json")[
                "authorization"
            ],
            preparation_sha=sha(FOLDER / "preparation.json"),
            adapter_source_sha=sha(Path(__file__)),
            cell=CELL,
            scope="Only the interrupted trajectory resumes, under its original total budgets. The zero-charge rejected request is retried once; no successful model response is replaced. Other registered work remains in the original queue.",
        ),
    )
    preserve(pause, FOLDER / "original" / "pause.json")
    pause.unlink()
    import sys

    try:
        with (
            patch.object(el, "run_command", continue_command),
            patch.object(
                sys,
                "argv",
                [
                    "quota_recovery",
                    "run",
                    "--retry_errors",
                    "--max_workers=1",
                    "--wait",
                ],
            ),
        ):
            c.run_batch(BATCH)
        result = reconcile_continuation()
    except BaseException:
        request_pause(
            pause,
            "Credit continuation did not finish; preserve and inspect before further dispatch",
        )
        raise
    print(
        json.dumps(
            dict(
                cell=CELL,
                resumed=True,
                cost=result["cost"],
                solved=result["solved"],
            )
        )
    )


def administrative_rejections(identity: str, directory: Path) -> list[str]:
    """Attach independently reconciled zero-charge requests to final rows."""
    if identity != CELL:
        return []
    certificate = read(FOLDER / "continuation_certificate.json")
    if any(
        sha(directory / name) != expected
        for name, expected in certificate["completed_hashes"].items()
    ):
        raise ValueError("The administrative continuation evidence changed")
    for name, key in (
        ("preparation.json", "preparation_sha"),
        ("continuation_start.json", "start_sha"),
        ("first_request_guard.json", "guard_sha"),
    ):
        if sha(FOLDER / name) != certificate[key]:
            raise ValueError("The continuation's audit record changed")
    return certificate["zero_charge_rejections"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "resume"))
    parser.add_argument("--account-ready-message", default="")
    cli = parser.parse_args()
    if cli.action == "prepare":
        prepare()
    else:
        resume(cli.account_ready_message)
