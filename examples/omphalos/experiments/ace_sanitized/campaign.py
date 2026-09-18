"""Sanitized ACE: separate mechanisms, then a fair agentic comparison.

Authorized September 17, 2026: $25 NEW API liability, trainX/validationX
only. No testX/challenge access, additional seeds, or default promotion.
Learning <=$2; proof development <=$6; core validation reserved $16; $1
reserve. Unspent completed-stage allocations may fund complete additional
panels; old campaigns make no calls and their charges are not erased.

Eight fixed trainX problems, seed 0, six isolated configurations = 48
proof pilots. One eight-cell combination pilot is permitted. Proof limit
$.10, 64 requests, 300 verifier seconds, Luna medium Responses; tools,
verification and demonstrations remain fixed. Baseline plus output cap,
one drop, concise instructions, bounded feedback, or revised book. No
handoff, learned memory or new tool is added to non-ACE.

Freeze before validation. Core: 40 problems x two replicates x ordinary
non-ACE/selected ACE = 160 cells. Select the training-frontier candidate
with lowest cost per qualified solve (tie: higher coverage, lower cost,
arm name). Retain a distinct highest-coverage frontier candidate. Explore
trade-offs; no per-replicate veto, effect-size veto or significance gate.
The combination contains individually non-dominated controls and is tested
once before selection. A book with unsupported retained edits is ineligible.

Additional panels, in order: the selected generic controller with an empty
book; selected controller with incumbent book when different; distinct
coverage candidate. Each is exactly 80 cells and requires its entire $8
nominal liability to fit. Deduplicate identical treatments and reuse exact
compatible controls. No unbounded sweep or implicit allowance extension.

Coverage percent and all-attempt budget-reduction percent are primary;
cost/solve is a selection aid, not a substitute. Report preparation and
cache sensitivity separately. Complete paired denominators, family-clustered
90% intervals, two-sided p<.10 for statistical support only. Platform
failures remain denominators; administrative censoring forbids a verdict.
One supervised attempt, all requests reserved, unknown billing halts work.
Both harnesses use python -m experiments.ace_sanitized.
"""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any

import delphyne as dp
import yaml

from ace.ace_playbook import Playbook
from experiments.common import omphalos_launch as ol
from experiments.common.ace_learning_io import accounting as ledger_accounting
from runtime.campaign_budget import Ledger
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile

from .control import Controls
from .scope import partition

NAME = "ace_sanitized_20260917"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
REFERENCE = ROOT / "experiments/campaigns/ace_economy_20260916"
REFINEMENT = ROOT / "experiments/campaigns/ace_economy_refinement_20260916"
LEARNING = ROOT / "experiments/campaigns/ace_learning_20260914"
REVISION = ROOT / "experiments/campaigns/ace_revision_20260913"
CEILING = 25.0
ALLOCATIONS = dict(learning=2.0, pilots=6.0, validation=16.0, reserve=1.0)
PILOT_THEOREMS = (
    "aime_1988_p3",
    "amc12a_2016_p2",
    "amc12_2000_p6",
    "amc12a_2020_p13",
    "mathd_algebra_185",
    "mathd_algebra_224",
    "mathd_numbertheory_48",
    "mathd_numbertheory_221",
)
ISOLATED = {
    "incumbent": Controls(),
    "output": Controls(output_tokens=8192),
    "drop": Controls(drop=True),
    "concise": Controls(concise=True),
    "views": Controls(views=True),
    "book": Controls(),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(filename: str) -> Any:
    return json.loads((CAMPAIGN / filename).read_text())


def save(filename: str, value: Any) -> None:
    path = CAMPAIGN / filename
    encoded = json.dumps(value, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != encoded:
            raise ValueError("Immutable artifact changed: " + filename)
        return
    with path.open("x") as out:
        out.write(encoded)


def context() -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    demos = [
        ROOT / f"demos/{n}.demo.yaml"
        for n in (
            "writer_drafts",
            "ace_roles",
            "ace_role_revision",
            "ace_learning",
        )
    ]
    return replace(
        ctx,
        modules=(
            *ctx.modules,
            "prove_economy",
            "prove_ace_roles",
            "prove_ace_role_revision",
            "prove_ace_learning",
            "prove_writer_drafts",
            "prove_writer_receipts",
            "prove_evidence",
            "prove_resource_completion",
            "experiments.ace_sanitized.control",
            "experiments.ace_sanitized.roles",
        ),
        demo_files=(*ctx.demo_files, *demos),
    )


@dataclass(frozen=True)
class Job:
    stage: str
    arm: str
    role: str
    theorem: str
    input_file: str
    input_sha256: str
    seed: int = 0

    def __post_init__(self) -> None:
        if self.stage not in ("learning", "pilots", "validation"):
            raise ValueError("Unregistered stage")
        if self.role not in (
            "proof",
            "schema",
            "review",
            "reflector",
            "curator",
            "reducer",
        ):
            raise ValueError("Unregistered role")
        if (self.role == "proof") != (self.stage != "learning"):
            raise ValueError("Role/stage mismatch")
        if self.seed not in ((0, 1) if self.stage == "validation" else (0,)):
            raise ValueError("Unregistered replicate")
        if (
            not self.input_file.startswith("inputs/")
            or ".." in Path(self.input_file).parts
        ):
            raise ValueError("Input outside campaign")

    @property
    def cap(self) -> float:
        return (
            0.10
            if self.role == "proof"
            else (0.20 if self.role in ("curator", "reducer") else 0.05)
        )

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if sha(CAMPAIGN / self.input_file) != self.input_sha256:
            raise ValueError("Input provenance drift")
        data = read(self.input_file)
        args = data["args"]
        snapshot = str(CAMPAIGN / "transport" / name(self, None))
        os.environ.update(
            OMPHALOS_CAMPAIGN_CELL=name(self, None),
            OMPHALOS_CAMPAIGN_STAGE=self.stage,
        )
        if self.role == "proof":
            stage = "validation" if self.stage == "validation" else "train"
            if partition(stage).get(self.theorem) != args["problem_file"]:
                raise ValueError("Proof outside authorized partition")
            if self.arm.startswith("agentic") and args["playbook"]:
                raise ValueError("Non-ACE must have an empty book")
            policy, options = (
                "sanitized_proof_policy",
                dict(controls=data["controls"]),
            )
        else:
            policy, options = (
                "sanitized_role_policy",
                dict(dollar_cap=self.cap, guidance=data.get("guidance", True)),
            )
        return dp.RunStrategyArgs(
            strategy={
                "proof": "prove_theorem_grounded",
                "schema": "learning_plan_pilot",
                "review": "learning_review_pilot",
                "reflector": "reflect_learning_repairs",
                "curator": "write_learning_book_edits",
                "reducer": "write_learning_book_edits",
            }[self.role],
            args=args,
            policy=policy,
            policy_args=dict(
                snapshot_directory=snapshot,
                pause_file=str(CAMPAIGN / "PAUSED"),
                **options,
            ),
            budget=dict(
                price=self.cap,
                num_requests=64
                if self.role == "proof"
                else (1 if self.role in ("schema", "review") else 7),
                rocq_seconds=300 if self.role == "proof" else 180,
            ),
        )


def name(job: Job, _: object) -> str:
    return f"{job.stage}__{job.arm}__{job.role}__{job.theorem}__seed{job.seed}"


def directory(job: Job) -> Path:
    return OUTPUT / job.stage / "configs" / name(job, None)


def make_job(
    stage: str,
    arm: str,
    role: str,
    theorem: str,
    data: dict[str, Any],
    seed: int = 0,
) -> Job:
    path = f"inputs/{stage}/{arm}_{role}_{theorem}_{seed}.json"
    save(path, data)
    return Job(stage, arm, role, theorem, path, sha(CAMPAIGN / path), seed)


def proof_job(
    stage: str,
    arm: str,
    theorem: str,
    seed: int,
    controls: Controls,
    book: Playbook | None,
) -> Job:
    split = "validation" if stage == "validation" else "train"
    return make_job(
        stage,
        arm,
        "proof",
        theorem,
        dict(
            controls=asdict(controls),
            book_sha256=book.sha256() if book is not None else None,
            args=dict(
                problem_file=partition(split)[theorem],
                theorem_name=theorem,
                playbook=book.render_prompt() if book else "",
                claims=[],
                turn_budget=64,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
                verifier_seconds=300,
                admission=False,
                focused=True,
                restart=False,
            ),
        ),
        seed,
    )


def jobs(batch: str) -> list[Job]:
    return [Job(**item) for item in read(f"manifests/{batch}.json")]


def all_jobs() -> list[Job]:
    result: dict[str, Job] = {}
    for path in sorted((CAMPAIGN / "manifests").glob("*.json")):
        for item in json.loads(path.read_text()):
            job = Job(**item)
            ident = name(job, None)
            if ident in result and result[ident] != job:
                raise ValueError("Cell identity collision")
            result[ident] = job
    return list(result.values())


def accounting() -> dict[str, Any]:
    return ledger_accounting(CAMPAIGN)


def activate(*, events: bool = True) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ.update(
        OMPHALOS_CAMPAIGN_LEDGER=str(CAMPAIGN / "ledger.sqlite3"),
        OMPHALOS_ESTIMATE_DOLLARS="1",
    )
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )
    else:
        os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)


def source_paths() -> list[Path]:
    # Explicit development seal; never run a legacy mixed-scope verifier.
    paths = [
        ROOT / p
        for p in json.loads((REFERENCE / "validation_seal.json").read_text())
    ]
    paths += list(Path(__file__).parent.glob("*.py"))
    paths += list((Path(__file__).parent / "templates").glob("*.jinja"))
    paths += list((ROOT / "prompts/ace/role_skills_v2").glob("*.md"))
    paths += list((ROOT / "prompts/ace/role_skills_v3").glob("*.md"))
    paths += [
        ROOT / "experiments/economy_refinement/window.py",
        ROOT / "experiments/common/ace_learning_io.py",
        ROOT / "tools/analysis/paired_evaluation.py",
        ROOT / "benchmarks/trainX.txt",
        ROOT / "tests/test_ace_sanitized.py",
        CAMPAIGN / "protocol.json",
        CAMPAIGN / "runtime.json",
        CAMPAIGN / "role_registration.json",
        CAMPAIGN / "role_inputs.json",
        LEARNING / "pilot_registration.json",
        REVISION / "protocol.json",
    ]
    paths += [ROOT / p for p in partition("train").values()]
    paths += list(context().demo_files)
    paths += [LEARNING / "sources" / f"{n}.json" for n in partition("train")]
    if (CAMPAIGN / "role_inputs.json").exists():
        paths += [CAMPAIGN / p for p in read("role_inputs.json")]
    return sorted(set(paths))


def prepare() -> None:
    if (CAMPAIGN / "seal.json").exists():
        verify()
        return
    for theorem in PILOT_THEOREMS:
        if theorem not in partition("train"):
            raise ValueError("Pilot outside trainX")
    if not (CAMPAIGN / "protocol.json").exists():
        save(
            "protocol.json",
            dict(
                protocol=__doc__,
                created=datetime.now(timezone.utc).isoformat(),
                ceiling=CEILING,
                allocations=ALLOCATIONS,
                authorized_partitions=["trainX", "validationX"],
                pilot_theorems=PILOT_THEOREMS,
                pilot_cells=48,
                combination_cells=8,
                core_validation_cells=160,
                max_extra_cells=240,
                defaults_changed=False,
                legacy_measurements_unchanged=True,
            ),
        )
    save("runtime.json", json.loads((REFINEMENT / "runtime.json").read_text()))
    Ledger(CAMPAIGN / "ledger.sqlite3").create(CEILING, ALLOCATIONS)


def seal() -> None:
    if accounting()["receipts"]:
        raise ValueError("Seal the implementation before paid work")
    reference = json.loads((REFERENCE / "validation_seal.json").read_text())
    for path, expected in reference.items():
        if sha(ROOT / path) != expected:
            raise ValueError("Historical source drift: " + path)
    save(
        "seal.json", {str(p.relative_to(ROOT)): sha(p) for p in source_paths()}
    )


def verify() -> None:
    if (CAMPAIGN / "PAUSED").exists():
        raise ValueError("Campaign is paused")
    paths = source_paths()
    sealed = read("seal.json")
    if set(sealed) != {str(p.relative_to(ROOT)) for p in paths}:
        raise ValueError("Unexpected source seal entry")
    for path in paths:
        if sha(path) != sealed[str(path.relative_to(ROOT))]:
            raise ValueError("Source/input drift: " + str(path))
    a = accounting()
    if (
        a["unresolved"]
        or a["billing_issues"]
        or a["ledger"]["liability"] > CEILING + 1e-9
    ):
        raise ValueError("Billing requires reconciliation")


def cell_result(job: Job) -> dict[str, Any] | None:
    folder = directory(job)
    status = ol.ground_truth(folder)
    if status not in ("done", "failed"):
        raise ValueError("Missing required cell: " + name(job, None))
    raw: dict[str, Any] = (
        yaml.safe_load((folder / "result.yaml").read_text())
        if (folder / "result.yaml").exists()
        else {}
    )
    diagnostic = (
        str(raw.get("diagnostics", ""))
        + str(raw.get("outcome", {}).get("diagnostics", ""))
        + "".join(p.read_text() for p in folder.glob("exception*.txt"))
    )
    if any(s in diagnostic for s in ("CampaignExhausted", "CampaignPaused")):
        raise ValueError("Administrative censoring: " + name(job, None))
    return raw.get("outcome", {}).get("result") if status == "done" else None


def fits(selected: list[Job]) -> bool:
    a = accounting()
    if a["unresolved"] or a["billing_issues"]:
        raise ValueError("Settle billing before dispatch")
    if not selected:
        return True
    stage = selected[0].stage
    if any(j.stage != stage for j in selected):
        raise ValueError("A dispatch batch must use one allocation")
    used = sum(
        r["dollars"] for r in a["ledger"]["groups"] if r["stage"] == stage
    )
    needed = sum(
        j.cap
        for j in selected
        if ol.ground_truth(directory(j)) not in ("done", "failed")
    )
    return (
        used + needed <= a["ledger"]["allocations"][stage] + 1e-9
        and a["ledger"]["liability"] + needed <= CEILING + 1e-9
    )


def launch(batch: str, selected: list[Job]) -> bool:
    verify()
    if (CAMPAIGN / f"batches/{batch}.json").exists():
        if selected != jobs(batch):
            raise ValueError("Batch changed")
        return True
    if not fits(selected):
        return False
    save(f"manifests/{batch}.json", [asdict(j) for j in selected])
    if selected:
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "experiments.ace_sanitized",
                "run-batch",
                batch,
                "run",
                "--max_workers=24",
                "--wait",
            ],
            cwd=ROOT,
            check=False,
        )
        for job in selected:
            cell_result(job)
        code = process.returncode
    else:
        code = 0
    verify()
    save(
        f"batches/{batch}.json",
        dict(
            exit_code=code,
            states={
                name(j, None): ol.ground_truth(directory(j)) for j in selected
            },
        ),
    )
    return True


def run_batch(batch: str) -> None:
    verify()
    selected = jobs(batch)
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher lacks credential")
    if not fits(selected):
        raise ValueError("Full batch liability does not fit")
    if selected[0].stage == "validation":
        from .workflow import verify_freeze

        verify_freeze()
    activate()
    ol.OmphalosExperiment(
        config_class=Job,
        configs=selected,
        context=context(),
        output_dir=str((OUTPUT / selected[0].stage).relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def transfer_unused(source: str, target: str) -> None:
    a = accounting()
    if a["unresolved"] or a["billing_issues"]:
        raise ValueError("Settle charges before transfer")
    used = sum(
        r["dollars"] for r in a["ledger"]["groups"] if r["stage"] == source
    )
    amount = a["ledger"]["allocations"][source] - used
    if amount > 1e-8:
        Ledger(CAMPAIGN / "ledger.sqlite3").transfer(
            source, target, amount, f"{source} complete; no further calls"
        )


def pilot() -> None:
    audit = read("book_audit.json")
    if not audit["eligible"] or audit["book_file_sha256"] != sha(
        CAMPAIGN / "book.yaml"
    ):
        raise ValueError("Audit the new book before proof pilots")
    book = Playbook.load(REFERENCE / "book.yaml")
    learned = Playbook.load(CAMPAIGN / "book.yaml")
    selected = [
        proof_job(
            "pilots",
            arm,
            theorem,
            0,
            controls,
            learned if arm == "book" else book,
        )
        for theorem in PILOT_THEOREMS
        for arm, controls in ISOLATED.items()
    ]
    random.Random(20260917).shuffle(selected)
    if not launch("pilot", selected):
        raise ValueError("Complete registered pilot does not fit")
