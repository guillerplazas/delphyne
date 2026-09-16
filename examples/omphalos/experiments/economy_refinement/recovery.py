"""Audit one HTTP-400 rejection; resume only its two collateral pauses.

The rejected prompt is neither retried nor rewritten and counts as a
platform failure. Preserve all original receipts, caches and exceptions.
Only zero-charge settled metadata is reconciled, with an audit table; the
global ledger guard and every money/request/verifier limit remain intact.

Two administrative continuations replay their exact cached prefix, including
spent resources, before sending the unchanged next request. A prefix guard
rejects any divergence. New results go to resume01; original files stay
immutable. No new problem, seed, model, treatment or solve retry is added.

Both harnesses: prepare, checkpoints (HTTP blocked), reconcile, run, finalize.
The recovery source seal is prospective; the original runtime seal remains.
"""

from contextlib import redirect_stdout
from copy import copy
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, override
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.models import (
    CachedRequest,
    LLMRequest,
    load_request_cache,
)
from delphyne.stdlib.tasks import run_command
from pydantic import TypeAdapter

from experiments import ace_economy_refinement_experiment as c
from runtime.admission_events import record
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.replay_admission import (
    PrefixCache,
    PrefixGuard,
    fingerprint,
    transport_state,
)
from tools.analysis.replay_economy import own_receipts

from . import state
from .policy import refined_economy_policy

REJECTED = "validation__ace_reset__algebra_others_exirrpowirrrat__seed0"
INTERRUPTED = (
    "validation__agentic_reset__algebra_others_exirrpowirrrat__seed1",
    "validation__agentic_reset_compact__algebra_others_exirrpowirrrat__seed1",
)
INCIDENT = "operations/incident01.json"
_REQUEST = TypeAdapter(LLMRequest)


@dataclass
class CheckpointGuard(PrefixGuard):
    expected_next: str = ""
    event_file: str | None = None
    reached: bool = False

    @override
    def consume(self, request: CachedRequest) -> None:
        if self.remaining:
            super().consume(request)
            return
        if not self.reached:
            key = fingerprint(
                _REQUEST.dump_python(request.request, mode="json")
            )
            if key != self.expected_next:
                raise ValueError("Continuation's next request changed")
            self.reached = True
            if self.event_file is not None:
                os.environ["OMPHALOS_ADMISSION_EVENTS"] = self.event_file
            record("resumption", "prefix_consumed", request=key)


def continued_economy_policy(
    snapshot_directory: str,
    pause_file: str,
    prefix_cache: str,
    expected_next: str,
    reset: bool = False,
    compact: bool = False,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    inner = refined_economy_policy(
        snapshot_directory, pause_file, reset, compact
    )

    def resume[T](
        tree: dp.Tree[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, T],
        env: dp.PolicyEnv,
    ) -> dp.StreamGen[T]:
        if env.cache is None:
            raise ValueError(
                "A continuation requires the shared request cache"
            )
        with load_request_cache(Path(prefix_cache), mode="read_only") as old:
            entries = dict(old.cache.dict)
        if not entries:
            raise ValueError("Missing interrupted prefix")
        for key, value in entries.items():
            if (
                key in env.cache.cache.dict
                and env.cache.cache.dict[key] != value
            ):
                raise ValueError("Continuation cache conflict")
        env.cache.cache.dict.update(entries)
        destination = os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)
        guard = CheckpointGuard(set(entries), expected_next, destination)
        local = copy(env)
        local.cache = dp.LLMCache(
            PrefixCache(env.cache.cache.dict, "read_write", guard)
        )
        local.cache.num_seen = env.cache.num_seen
        try:
            yield from inner(tree, local)
            if guard.remaining or not guard.reached:
                raise ValueError(
                    "Continuation did not reach its saved boundary"
                )
        finally:
            if destination is not None:
                os.environ["OMPHALOS_ADMISSION_EVENTS"] = destination

    return dp.Policy(resume)


def context() -> dp.ExecutionContext:
    ctx = c.context()
    return replace(
        ctx, modules=(*ctx.modules, "experiments.economy_refinement.recovery")
    )


@dataclass(frozen=True)
class ResumeConfig(c.Config):
    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        ident = c.name(self, None)
        if ident not in INTERRUPTED:
            raise ValueError("Only the two administrative pauses may resume")
        args = super().instantiate(context)
        args.policy = "continued_economy_policy"
        args.policy_args.update(
            prefix_cache=str(c.directory(self) / "cache.yaml"),
            expected_next=c.read(INCIDENT)["checkpoints"][ident]["request"],
        )
        return args


def receipt_record(ledger: Ledger, receipt: str) -> dict[str, Any]:
    with ledger.connect() as db:
        row = db.execute(
            "SELECT * FROM receipts WHERE id=?", (receipt,)
        ).fetchone()
        columns = [r[1] for r in db.execute("PRAGMA table_info(receipts)")]
    if row is None:
        raise ValueError("Missing receipt")
    return dict(zip(columns, row))


def reconcile_record(
    ledger: Ledger, original: dict[str, Any], evidence: str
) -> None:
    if (
        original["status"] != "settled"
        or original["charged"] != 0
        or json.loads(original["usage"]) != {"exception": "BadRequestError"}
    ):
        raise ValueError(
            "Only an already-settled zero-charge rejection qualifies"
        )
    usage = dict(
        reconciled_exception="BadRequestError",
        http_status=400,
        error_code="invalid_prompt",
        reconciliation=evidence,
        input_tokens=0,
        output_tokens=0,
        usage_origin="No provider usage returned; zero-charge rejected request",
    )
    with ledger.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT * FROM receipts WHERE id=?", (original["id"],)
        ).fetchone()
        if row is None:
            raise ValueError("Receipt disappeared before reconciliation")
        columns = [r[1] for r in db.execute("PRAGMA table_info(receipts)")]
        current = dict(zip(columns, row))
        db.execute(
            "CREATE TABLE IF NOT EXISTS reconciliations (receipt TEXT PRIMARY KEY, created REAL, original TEXT, evidence TEXT)"
        )
        prior = db.execute(
            "SELECT original,evidence FROM reconciliations WHERE receipt=?",
            (original["id"],),
        ).fetchone()
        if prior is not None:
            if (
                json.loads(prior[0]) != original
                or prior[1] != evidence
                or current
                != {**original, "usage": json.dumps(usage, sort_keys=True)}
            ):
                raise ValueError("Reconciliation audit conflict")
            return
        if current != original:
            raise ValueError("Receipt changed before reconciliation")
        db.execute(
            "INSERT INTO reconciliations VALUES (?,?,?,?)",
            (
                original["id"],
                time.time(),
                json.dumps(original, sort_keys=True),
                evidence,
            ),
        )
        db.execute(
            "UPDATE receipts SET usage=? WHERE id=?",
            (json.dumps(usage, sort_keys=True), original["id"]),
        )


def prepare() -> None:
    c.verify()
    if (c.CAMPAIGN / INCIDENT).exists():
        return
    account = c.accounting()
    if account["unresolved"] or len(account["billing_issues"]) != 1:
        raise ValueError("Unexpected billing state")
    ledger = Ledger(c.CAMPAIGN / "ledger.sqlite3")
    original = receipt_record(ledger, account["billing_issues"][0])
    if original["cell"] != REJECTED or original["stage"] != "benchmark":
        raise ValueError("Unknown failed request")
    jobs = {c.name(j, None): j for j in c.configs("final00")}
    failed = {
        ident
        for ident, j in jobs.items()
        if c.ol.ground_truth(c.directory(j)) == "failed"
    }
    if failed != {REJECTED, *INTERRUPTED}:
        raise ValueError("Unexpected failed cells")
    files: dict[str, str] = {}
    for ident in failed:
        folder = c.directory(jobs[ident])
        exception = (folder / "exception.txt").read_text()
        if ident == REJECTED:
            if (
                "Error code: 400" not in exception
                or "'code': 'invalid_prompt'" not in exception
            ):
                raise ValueError("Not the documented provider rejection")
        elif "Campaign billing requires reconciliation" not in exception:
            raise ValueError("Not an administrative pause")
        for filename in ("exception.txt", "cache.yaml"):
            p = folder / filename
            files[str(p.relative_to(c.ROOT))] = c.sha(p)
    latest: dict[str, dict[str, Any]] = {ident: {} for ident in failed}
    for line in (c.CAMPAIGN / "events.jsonl").open():
        event = json.loads(line)
        if event.get("cell") not in failed:
            continue
        values = latest[event["cell"]]
        if event["kind"] == "estimate_v2":
            values.update(
                request=event["request"],
                transport_state=event["transport_state"],
            )
        if event["kind"] == "admission_v2" and event["decision"] == "admitted":
            values["spent"] = event["spent"]
    if any(
        set(v) != {"request", "transport_state", "spent"}
        for v in latest.values()
    ):
        raise ValueError("Incomplete interruption checkpoint")
    c.save(
        INCIDENT,
        dict(
            created=datetime.now(timezone.utc).isoformat(),
            protocol=__doc__,
            rejected_cell=REJECTED,
            interrupted_cells=list(INTERRUPTED),
            original_receipt=original,
            immutable_files=files,
            checkpoints=latest,
            paid_retries_of_rejected_request=0,
            new_problem_seed_cells=0,
            prompt_changes=0,
            budget_changes=0,
            accounting_before=account,
            official_reference="https://developers.openai.com/api/docs/guides/error-codes",
            billing_basis="Existing adapter classified this HTTP 400 as settled at zero; no amount or liability is reduced by this reconciliation.",
        ),
    )


def verify_incident() -> None:
    c.verify()
    incident = c.read(INCIDENT)
    if (
        incident["rejected_cell"] != REJECTED
        or tuple(incident["interrupted_cells"]) != INTERRUPTED
    ):
        raise ValueError("Recovery scope changed")
    expected = {
        str((c.directory(job) / filename).relative_to(c.ROOT))
        for job in c.configs("final00")
        if c.name(job, None) in {REJECTED, *INTERRUPTED}
        for filename in ("cache.yaml", "exception.txt")
    }
    if set(incident["immutable_files"]) != expected:
        raise ValueError("Unexpected interrupted archive path")
    for path, digest in incident["immutable_files"].items():
        if c.sha(c.ROOT / path) != digest:
            raise ValueError("Interrupted archive changed")


class CheckpointReached(RuntimeError):
    pass


def checkpoints() -> None:
    verify_incident()
    checks: list[dict[str, Any]] = []
    before = own_receipts(c.CAMPAIGN)
    incident = c.read(INCIDENT)
    for job in c.configs("final00"):
        ident = c.name(job, None)
        if ident not in {REJECTED, *INTERRUPTED}:
            continue
        expected = incident["checkpoints"][ident]
        captured: list[dict[str, Any]] = []
        admissions: list[dict[str, Any]] = []

        def stop(model: CampaignResponsesModel, request: LLMRequest) -> None:
            captured.append(
                dict(
                    request=fingerprint(
                        _REQUEST.dump_python(request, mode="json")
                    ),
                    transport_state=fingerprint(transport_state(model)),
                )
            )
            raise CheckpointReached("Offline checkpoint; HTTP blocked")

        def admission(kind: str, decision: str, **data: Any) -> None:
            if kind == "admission_v2" and decision == "admitted":
                admissions.append(data)

        c.activate(events=False)
        args = job.instantiate(None)
        args.policy = "continued_economy_policy"
        args.policy_args.update(
            prefix_cache=str(c.directory(job) / "cache.yaml"),
            expected_next=expected["request"],
        )
        args.cache_mode = "read_only"
        args.cache_file = str(c.directory(job) / "cache.yaml")
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(CampaignResponsesModel, "_send_final_request", stop),
            patch("runtime.replay_admission.record", admission),
            redirect_stdout(io.StringIO()),
        ):
            try:
                run_command(
                    run_strategy,
                    args,
                    ctx=replace(context(), cache_root=Path("/")),
                    add_header=False,
                )
            except CheckpointReached:
                pass
        if (
            captured
            != [
                dict(
                    request=expected["request"],
                    transport_state=expected["transport_state"],
                )
            ]
            or not admissions
            or admissions[-1]["spent"] != expected["spent"]
        ):
            raise ValueError(
                "Interrupted prefix checkpoint mismatch: " + ident
            )
        checks.append(
            dict(
                cell=ident,
                matched_request=True,
                matched_transport=True,
                matched_spent=True,
                paid_calls=0,
            )
        )
    if own_receipts(c.CAMPAIGN) != before:
        raise ValueError("Offline checkpoint created a receipt")
    c.save(
        "operations/checkpoints01.json",
        dict(passed=True, cells=checks, paid_calls=0),
    )
    print(json.dumps(checks, indent=2))


def reconcile() -> None:
    verify_incident()
    if not c.read("operations/checkpoints01.json")["passed"]:
        raise ValueError("Exact prefix verification required")
    sources = [
        Path(__file__),
        Path(state.__file__),
        c.ROOT / "tests/test_economy_recovery.py",
    ]
    c.save(
        "operations/recovery_seal01.json",
        {str(p.relative_to(c.ROOT)): c.sha(p) for p in sources},
    )
    incident = c.read(INCIDENT)
    reconcile_record(
        Ledger(c.CAMPAIGN / "ledger.sqlite3"),
        incident["original_receipt"],
        INCIDENT,
    )
    c.verify()
    account = c.accounting()
    if account["unresolved"] or account["billing_issues"]:
        raise ValueError("Billing is still unresolved")
    if abs(account["total"] - incident["accounting_before"]["total"]) > 1e-12:
        raise ValueError("Reconciliation changed money")


def run() -> None:
    verify_incident()
    seal = c.read("operations/recovery_seal01.json")
    expected = {
        str(p.relative_to(c.ROOT))
        for p in (
            Path(__file__),
            Path(state.__file__),
            c.ROOT / "tests/test_economy_recovery.py",
        )
    }
    if set(seal) != expected:
        raise ValueError("Unexpected recovery source path")
    for path, digest in seal.items():
        if c.sha(c.ROOT / path) != digest:
            raise ValueError("Recovery source changed")
    account = c.accounting()
    if (
        account["unresolved"]
        or account["billing_issues"]
        or account["ledger"]["liability"] + 0.2 > c.CEILING
    ):
        raise ValueError("Administrative continuations cannot be admitted")
    c.activate()
    jobs = [
        ResumeConfig(**j.__dict__)
        for j in c.configs("final00")
        if c.name(j, None) in INTERRUPTED
    ]
    c.ol.OmphalosExperiment(
        config_class=ResumeConfig,
        configs=jobs,
        context=context(),
        output_dir=str((c.OUTPUT / "resume01").relative_to(c.ROOT)),
        config_naming=c.name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def finalize() -> None:
    verify_incident()
    jobs = c.configs("final00")
    for job in jobs:
        state.cell_result(job)
    account = c.accounting()
    if account["unresolved"] or account["billing_issues"]:
        raise ValueError("Wait for billing settlement")
    c.save(
        "batches/final00.json",
        dict(
            exit_code=None,
            administrative_continuations=list(INTERRUPTED),
            platform_failure=REJECTED,
            incident=INCIDENT,
            states={
                c.name(j, None): c.ol.ground_truth(state.directory(j))
                for j in jobs
            },
        ),
    )
    c.save(
        "operations/completed01.json",
        dict(
            preserved_provider_failure=REJECTED,
            continued_cells=list(INTERRUPTED),
            original_archives_unchanged=True,
            accounting=account,
        ),
    )


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "run":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        run()
    elif action == "prepare":
        prepare()
    elif action == "checkpoints":
        checkpoints()
    elif action == "reconcile":
        reconcile()
    elif action == "finalize":
        finalize()
    else:
        raise SystemExit(
            "prepare | checkpoints | reconcile | run run --max_workers=2 --wait | finalize"
        )
