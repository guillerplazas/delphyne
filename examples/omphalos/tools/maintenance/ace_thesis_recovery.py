"""Continue collateral ledger pauses without retrying a provider rejection.

The rejected request remains a failed cell. Only administrative interruptions
resume, after offline equality of the cached prefix, next request, transport
state and spent budget. The original runner and source seal stay unchanged.
Canonical cell directories become symlinks to complete continuation archives;
every interrupted directory is preserved byte for byte in interrupted_round1.
No new theorem, seed, treatment, budget or attempt at a solved/failed proof.

Both harnesses: prepare; checkpoints; reconcile; run run --max_workers=24
--wait; finalize. All charges remain in the original fresh-$50 ledger.
"""

from contextlib import redirect_stdout
from copy import copy
from dataclasses import dataclass, replace
import io
import json
import os
from pathlib import Path
import sys
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.models import LLMRequest, load_request_cache
from delphyne.stdlib.tasks import run_command
from pydantic import TypeAdapter

from experiments.ace_thesis import campaign as c
from experiments.ace_sanitized.control import Controls, sanitized_proof_policy
from experiments.economy_refinement.recovery import (
    CheckpointGuard,
    CheckpointReached,
    receipt_record,
    reconcile_record,
)
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.replay_admission import PrefixCache, fingerprint, transport_state

INCIDENT = "operations/round1_incident.json"
_REQUEST = TypeAdapter(LLMRequest)


def original_directory(job: c.Job) -> Path:
    archive = c.OUTPUT / "interrupted_round1/configs" / c.name(job, None)
    return archive if archive.exists() else c.directory(job)


def continued_thesis_policy(
    snapshot_directory: str,
    pause_file: str,
    prefix_cache: str,
    expected_next: str,
    controls: Controls = Controls(),
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    inner = sanitized_proof_policy(snapshot_directory, pause_file, controls)

    def resume[T](
        tree: dp.Tree[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, T],
        env: dp.PolicyEnv,
    ) -> dp.StreamGen[T]:
        if env.cache is None:
            raise ValueError("Continuation requires a request cache")
        with load_request_cache(Path(prefix_cache), mode="read_only") as old:
            entries = dict(old.cache.dict)
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
                raise ValueError("Saved continuation boundary was not reached")
        finally:
            if destination is not None:
                os.environ["OMPHALOS_ADMISSION_EVENTS"] = destination

    return dp.Policy(resume)


def context() -> dp.ExecutionContext:
    ctx = c.context()
    return replace(
        ctx, modules=(*ctx.modules, "tools.maintenance.ace_thesis_recovery")
    )


@dataclass(frozen=True)
class ResumeJob(c.Job):
    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        incident = c.read(INCIDENT)
        ident = c.name(self, None)
        if (
            ident not in incident["interrupted"]
            or ident == incident["rejected"]
        ):
            raise ValueError(
                "Only collateral administrative pauses may resume"
            )
        args = super().instantiate(context)
        args.policy = "continued_thesis_policy"
        args.policy_args.update(
            prefix_cache=str(original_directory(self) / "cache.yaml"),
            expected_next=incident["checkpoints"][ident]["request"],
        )
        return args


def prepare() -> None:
    if (c.CAMPAIGN / INCIDENT).exists():
        return
    if c.read("seal.json") != {
        str(p.relative_to(c.ROOT)): c.sha(p) for p in c.source_paths()
    }:
        raise ValueError("Original source drift")
    account = c.accounting()
    if account["unresolved"] or len(account["billing_issues"]) != 1:
        raise ValueError("Unexpected accounting condition")
    receipt = receipt_record(
        Ledger(c.CAMPAIGN / "ledger.sqlite3"), account["billing_issues"][0]
    )
    rejected = receipt["cell"]
    interrupted: list[str] = []
    hashes: dict[str, dict[str, str]] = {}
    for job in c.jobs("round1"):
        if c.ol.ground_truth(c.directory(job)) != "failed":
            continue
        ident = c.name(job, None)
        error = (c.directory(job) / "exception.txt").read_text()
        if ident == rejected:
            if (
                "Error code: 400" not in error
                or "'code': 'invalid_prompt'" not in error
            ):
                raise ValueError("Unknown provider error")
        elif "Campaign billing requires reconciliation" in error:
            interrupted.append(ident)
        else:
            raise ValueError("Unexpected failed cell")
        hashes[ident] = {
            p.name: c.sha(p) for p in c.directory(job).iterdir() if p.is_file()
        }
    if rejected not in hashes or not interrupted:
        raise ValueError("Incomplete incident scope")
    latest: dict[str, dict[str, Any]] = {ident: {} for ident in interrupted}
    for line in (c.CAMPAIGN / "events.jsonl").open():
        event = json.loads(line)
        if event.get("cell") not in latest:
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
        raise ValueError("Incomplete checkpoints")
    c.save(
        INCIDENT,
        dict(
            protocol=__doc__,
            rejected=rejected,
            interrupted=sorted(interrupted),
            original_receipt=receipt,
            original_hashes=hashes,
            checkpoints=latest,
            accounting_before=account,
            rejected_request_retries=0,
            new_cells=0,
            original_source_seal=c.sha(c.CAMPAIGN / "seal.json"),
        ),
    )


def verify_originals() -> None:
    incident = c.read(INCIDENT)
    for job in c.jobs("round1"):
        ident = c.name(job, None)
        for filename, expected in (
            incident["original_hashes"].get(ident, {}).items()
        ):
            if c.sha(original_directory(job) / filename) != expected:
                raise ValueError("Interrupted evidence changed")


def checkpoints() -> None:
    verify_originals()
    before = c.accounting()["receipts"]
    incident = c.read(INCIDENT)
    checks: list[dict[str, Any]] = []
    for job in c.jobs("round1"):
        ident = c.name(job, None)
        if ident not in incident["interrupted"]:
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
        args = ResumeJob(**job.__dict__).instantiate(None)
        args.cache_mode, args.cache_file = (
            "read_only",
            str(original_directory(job) / "cache.yaml"),
        )
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
            raise ValueError("Checkpoint mismatch: " + ident)
        checks.append(
            dict(
                cell=ident,
                request=True,
                transport=True,
                spent=True,
                paid_calls=0,
            )
        )
    if c.accounting()["receipts"] != before:
        raise ValueError("Offline checkpoint created a receipt")
    c.save(
        "operations/round1_checkpoints.json",
        dict(passed=True, cells=checks, paid_calls=0),
    )
    print(json.dumps(dict(checkpoints=len(checks), paid_calls=0)), flush=True)


def reconcile() -> None:
    verify_originals()
    if not c.read("operations/round1_checkpoints.json")["passed"]:
        raise ValueError("Checkpoint evidence required")
    from experiments.economy_refinement import recovery

    paths = [
        Path(__file__),
        Path(recovery.__file__),
        c.ROOT / "tests/test_thesis_recovery.py",
    ]
    c.save(
        "operations/round1_recovery_seal.json",
        {str(p.relative_to(c.ROOT)): c.sha(p) for p in paths},
    )
    incident = c.read(INCIDENT)
    reconcile_record(
        Ledger(c.CAMPAIGN / "ledger.sqlite3"),
        incident["original_receipt"],
        INCIDENT,
    )
    c.verify()
    if c.accounting()["total"] != incident["accounting_before"]["total"]:
        raise ValueError("Reconciliation changed money")


def run() -> None:
    c.verify()
    verify_originals()
    for path, expected in c.read(
        "operations/round1_recovery_seal.json"
    ).items():
        if c.sha(c.ROOT / path) != expected:
            raise ValueError("Recovery source drift")
    incident = c.read(INCIDENT)
    jobs = [
        ResumeJob(**j.__dict__)
        for j in c.jobs("round1")
        if c.name(j, None) in incident["interrupted"]
    ]
    account = c.accounting()
    liability = sum(j.cap for j in jobs)
    used = sum(
        g["dollars"]
        for g in account["ledger"]["groups"]
        if g["stage"] == "round1"
    )
    if (
        used + liability > c.ALLOCATIONS["round1"]
        or account["total"] + liability > c.CEILING
    ):
        raise ValueError("Complete continuation liability does not fit")
    c.activate()
    c.ol.OmphalosExperiment(
        config_class=ResumeJob,
        configs=jobs,
        context=context(),
        output_dir=str((c.OUTPUT / "resume_round1").relative_to(c.ROOT)),
        config_naming=c.name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def finalize() -> None:
    c.verify()
    verify_originals()
    incident = c.read(INCIDENT)
    jobs = [
        j
        for j in c.jobs("round1")
        if c.name(j, None) in incident["interrupted"]
    ]
    for job in jobs:
        resumed = c.OUTPUT / "resume_round1/configs" / c.name(job, None)
        if c.ol.ground_truth(resumed) not in ("done", "failed"):
            raise ValueError("Missing continuation")
        diagnostic = "".join(
            p.read_text() for p in resumed.glob("exception*.txt")
        )
        if "CampaignExhausted" in diagnostic or "CampaignPaused" in diagnostic:
            raise ValueError("Continuation remains administratively censored")
    # Scripted archive migration: originals survive, canonical paths resolve
    # complete logical cells, and the frozen runner needs no modifications.
    for job in jobs:
        canonical = c.directory(job)
        archived = c.OUTPUT / "interrupted_round1/configs" / c.name(job, None)
        resumed = c.OUTPUT / "resume_round1/configs" / c.name(job, None)
        if not canonical.is_symlink():
            archived.parent.mkdir(parents=True, exist_ok=True)
            canonical.rename(archived)
            canonical.symlink_to(
                os.path.relpath(resumed, canonical.parent),
                target_is_directory=True,
            )
        elif canonical.resolve() != resumed.resolve():
            raise ValueError("Unexpected canonical alias")
    verify_originals()
    c.save(
        "operations/round1_recovered.json",
        dict(
            originals_preserved=True,
            canonical_aliases=incident["interrupted"],
            provider_failure=incident["rejected"],
            original_receipt_preserved_in="ledger.reconciliations",
            accounting=c.accounting(),
        ),
    )


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "run":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        run()
    elif action in ("prepare", "checkpoints", "reconcile", "finalize"):
        {
            "prepare": prepare,
            "checkpoints": checkpoints,
            "reconcile": reconcile,
            "finalize": finalize,
        }[action]()
    else:
        raise SystemExit(
            "prepare | checkpoints | reconcile | run run --max_workers=24 --wait | finalize"
        )


if __name__ == "__main__":
    main()
