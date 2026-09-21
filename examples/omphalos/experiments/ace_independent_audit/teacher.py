"""Completion/repair evidence exists only in the learning process.

The plain trajectory is fixed before these calls. No solver score is changed.
Every proposed automatic completion is rechecked with automation disabled.
"""

from dataclasses import asdict, dataclass
import json
import sys
import time
from typing import Any

import delphyne as dp

from experiments.common import omphalos_launch as ol
from experiments.ace_sanitized.scope import partition
from runtime import pytanque_utils as pt
from runtime.tool_budget import ToolLimits, operation, OperationExhausted
from runtime.rocq_server import TransportError

from . import campaign as c
from .common import CAMPAIGN, OUTPUT, ROOT, read, save, sha
from .workflow import result
from .verification import compile_one


def completion_evidence(
    theorem: str, source_file: str, source_sha: str
) -> list[dict[str, Any]]:
    path = CAMPAIGN / source_file
    if theorem not in partition("train") or sha(path) != source_sha:
        raise ValueError("Unauthorized or changed teacher source")
    evidence = read(path)
    if evidence["theorem"] != theorem:
        raise ValueError("Teacher theorem mismatch")
    problem = partition("train")[theorem]
    receipts: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    operation_started = time.monotonic()
    for check in evidence["checks"]:
        submitted = tuple(check["args"]["tactics"])
        if submitted in seen or check["feedback"].get("success"):
            continue
        seen.add(submitted)
        started = time.monotonic()
        remaining = 300 - (started - operation_started)
        if remaining <= 0:
            receipts.append(
                dict(
                    source_check_index=check["index"],
                    accepted=[],
                    administrative_stop="300 second training completion work allowance",
                )
            )
            break
        try:
            with operation(
                ToolLimits(seconds=min(60, remaining), rpc_calls=512)
            ):
                assisted = pt.check_assisted(problem, theorem, list(submitted))
        except (OperationExhausted, TransportError) as e:
            receipts.append(
                dict(
                    source_check_index=check["index"],
                    accepted=[],
                    exception_type=type(e).__name__,
                    work_limit=str(e),
                    seconds=time.monotonic() - started,
                )
            )
            continue
        accepted = assisted.proof_so_far if assisted.success else []
        # Independent call with no completion or result-memo shortcut.
        pt.clear_check_memo()
        verified = pt.check(problem, theorem, accepted) if accepted else None
        kernel = (
            compile_one((problem, theorem, "\n".join(accepted)))
            if accepted
            else None
        )
        common = 0
        for a, b in zip(submitted, accepted):
            if a != b:
                break
            common += 1
        receipts.append(
            dict(
                source_check_index=check["index"],
                submitted=list(submitted),
                original_feedback=check["feedback"],
                assisted=asdict(assisted),
                accepted=accepted,
                independent_plain_check=asdict(verified) if verified else None,
                common_prefix=accepted[:common],
                replacement_tail=accepted[common:],
                caveat="Only the full accepted script is certified. Tail is a textual diff. Original state is retained; tactic generalization needs its stated conditions.",
                independent_kernel=kernel,
                seconds=time.monotonic() - started,
            )
        )
        if accepted and (
            verified is None
            or not verified.success
            or kernel is None
            or not kernel["passed"]
        ):
            raise ValueError(
                "Automatic completion failed independent plain check"
            )
    return receipts


@dp.strategy
def audit_teacher(
    theorem: str, source_file: str, source_sha: str
) -> dp.Strategy[dp.Compute, object, list[dict[str, Any]]]:
    return (
        yield from dp.compute(completion_evidence)(
            theorem, source_file, source_sha
        )
    )


def audit_teacher_policy() -> dp.Policy[dp.Compute, object]:
    return dp.just_compute(object())


@dataclass(frozen=True)
class TeacherJob:
    theorem: str
    source_file: str
    source_sha: str

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        return dp.RunStrategyArgs(
            strategy="audit_teacher",
            args=asdict(self),
            policy="audit_teacher_policy",
            policy_args={},
            budget={},
        )


def teacher_name(job: TeacherJob, _: object) -> str:
    return "teacher__" + job.theorem


def prepare() -> None:
    jobs: list[TeacherJob] = []
    for theorem in partition("train"):
        path = CAMPAIGN / "evidence" / f"source_plain_v2__{theorem}.json"
        jobs.append(
            TeacherJob(theorem, str(path.relative_to(CAMPAIGN)), sha(path))
        )
    save(CAMPAIGN / "teacher_manifest.json", [asdict(j) for j in jobs])


def run() -> None:
    from dataclasses import replace

    c.activate()
    ctx = c.context()
    ctx = replace(
        ctx,
        modules=[*ctx.modules, "experiments.ace_independent_audit.teacher"],
    )
    jobs = [TeacherJob(**v) for v in read(CAMPAIGN / "teacher_manifest.json")]
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    ol.OmphalosExperiment(
        config_class=TeacherJob,
        configs=jobs,
        context=ctx,
        output_dir=str((OUTPUT / "teacher").relative_to(ROOT)),
        config_naming=teacher_name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def collect() -> None:
    total = success = 0
    for raw in read(CAMPAIGN / "teacher_manifest.json"):
        j = TeacherJob(**raw)
        values = result("teacher", teacher_name(j, None))["values"]
        if len(values) != 1:
            raise ValueError("Missing teacher output")
        evidence = read(CAMPAIGN / j.source_file)
        evidence["training_only_completion"] = values[0]
        save(
            CAMPAIGN / "evidence" / f"teacher_plain_v2__{j.theorem}.json",
            evidence,
        )
        total += len(values[0])
        success += sum(bool(r["accepted"]) for r in values[0])
    print(
        json.dumps(dict(teacher_checks=total, completed_and_rechecked=success))
    )
