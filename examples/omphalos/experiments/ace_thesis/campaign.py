"""Fresh $50 ACE study, authorized by Guille on 2026-09-18.

Only trainX/validationX. Two prospective development rounds (72 and 48
cells), <=$4 learning, then at most four interleaved 80-cell validation
panels ($32), with $2 reserve. No additional arms/seeds or default changes.
Luna medium Responses; identical tools, history, demonstrations, $0.10,
64 requests and 300 verifier seconds. All matched arms use 8192 output
tokens; the ordinary non-ACE comparator retains 32768. No inference-time
learning, retrieval, reset or new tools. Learning is reported separately.

Primary descriptive targets: +10 percentage points coverage, OR >=10%
all-attempt inference savings without pooled coverage loss. No per-seed
veto. Family-clustered 90% intervals and two-sided p<.10 describe support;
they are not pilot gates. ValidationX is reused development data, not an
untouched confirmation. Missing/administratively censored cells prohibit
a verdict. Platform failures remain in the denominator. One attempt.
"""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import delphyne as dp
import yaml

from experiments.ace_sanitized.control import Controls
from experiments.ace_sanitized.scope import partition
from experiments.common import omphalos_launch as ol
from experiments.common.ace_learning_io import accounting as ledger_accounting
from runtime.campaign_budget import Ledger
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile

from .artifact import ContextArtifact
from .design import families, training_panel

NAME = "ace_thesis_20260918"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
REFERENCE = ROOT / "experiments/campaigns/ace_economy_20260916"
SANITIZED = ROOT / "experiments/campaigns/ace_sanitized_20260917"
CEILING = 50.0
ALLOCATIONS = dict(
    learning=4.0, round1=7.2, round2=4.8, validation=32.0, reserve=2.0
)


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
        ),
        demo_files=(
            *ctx.demo_files,
            *(
                ROOT / f"demos/{n}.demo.yaml"
                for n in (
                    "writer_drafts",
                    "ace_roles",
                    "ace_role_revision",
                    "ace_learning",
                )
            ),
        ),
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
        if self.stage not in ALLOCATIONS or self.stage == "reserve":
            raise ValueError("Unregistered stage")
        if self.role not in ("proof", "reflector", "curator", "reducer"):
            raise ValueError("Unregistered role")
        if (self.role == "proof") == (self.stage == "learning"):
            raise ValueError("Role/stage mismatch")
        if self.seed not in (0, 1) or (self.role != "proof" and self.seed):
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
            else (0.05 if self.role == "reflector" else 0.20)
        )

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if sha(CAMPAIGN / self.input_file) != self.input_sha256:
            raise ValueError("Input provenance drift")
        data = read(self.input_file)
        args = data["args"]
        os.environ.update(
            OMPHALOS_CAMPAIGN_CELL=name(self, None),
            OMPHALOS_CAMPAIGN_STAGE=self.stage,
        )
        if self.role == "proof":
            split = "validation" if self.stage == "validation" else "train"
            if partition(split).get(self.theorem) != args["problem_file"]:
                raise ValueError("Proof outside authorized partition")
            if self.arm.startswith("nonace") and args["playbook"]:
                raise ValueError("Non-ACE must have empty context")
            policy, options = (
                "sanitized_proof_policy",
                dict(controls=data["controls"]),
            )
        else:
            policy, options = "learning_role_policy", dict(dollar_cap=self.cap)
        return dp.RunStrategyArgs(
            strategy={
                "proof": "prove_theorem_grounded",
                "reflector": "reflect_learning_repairs",
                "curator": "write_learning_book_edits",
                "reducer": "write_learning_book_edits",
            }[self.role],
            args=args,
            policy=policy,
            policy_args=dict(
                snapshot_directory=str(
                    CAMPAIGN / "transport" / name(self, None)
                ),
                pause_file=str(CAMPAIGN / "PAUSED"),
                **options,
            ),
            budget=dict(
                price=self.cap,
                num_requests=64 if self.role == "proof" else 7,
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
    artifact: ContextArtifact | None,
    output_tokens: int = 8192,
) -> Job:
    split = "validation" if stage == "validation" else "train"
    return make_job(
        stage,
        arm,
        "proof",
        theorem,
        dict(
            controls=asdict(Controls(output_tokens=output_tokens)),
            artifact_sha256=artifact.sha256() if artifact else None,
            args=dict(
                problem_file=partition(split)[theorem],
                theorem_name=theorem,
                playbook=artifact.rendered()["text"] if artifact else "",
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
            key = name(job, None)
            if key in result and result[key] != job:
                raise ValueError("Cell identity collision")
            result[key] = job
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


def prepare() -> None:
    if not (CAMPAIGN / "protocol.json").exists():
        save(
            "protocol.json",
            dict(
                protocol=__doc__,
                created=datetime.now(timezone.utc).isoformat(),
                ceiling=CEILING,
                allocations=ALLOCATIONS,
                train=training_panel(),
                train_families=families("train"),
                validation_families=families("validation"),
                development_cells=[72, 48],
                validation_cells_max=320,
                learning_max_cells=dict(reflector=12, curator=12, reducer=3),
                selection="Min cost/solve among candidates at historical pooled coverage floor; "
                "ties higher coverage, lower cost, artifact hash. No per-seed veto.",
                round2_source="selected round1 training arm, seed0 only",
                context_bytes=32768,
                permitted_partitions=["trainX", "validationX"],
            ),
        )
    source = (
        ROOT
        / "experiments/campaigns/ace_economy_refinement_20260916/runtime.json"
    )
    save("runtime.json", json.loads(source.read_text()))
    Ledger(CAMPAIGN / "ledger.sqlite3").create(CEILING, ALLOCATIONS)


def source_paths() -> list[Path]:
    reference = json.loads((REFERENCE / "validation_seal.json").read_text())
    paths = [ROOT / p for p in reference]
    paths += list(Path(__file__).parent.glob("*.py"))
    paths += list((ROOT / "experiments/ace_sanitized").glob("*.py"))
    paths += list((ROOT / "experiments/ace_sanitized/templates").glob("*"))
    paths += list((ROOT / "prompts/ace/role_skills_v3").glob("*.md"))
    paths += [
        ROOT / "experiments/common/ace_learning_io.py",
        ROOT / "experiments/economy_refinement/window.py",
        ROOT / "tools/analysis/paired_evaluation.py",
        ROOT / "tests/test_ace_thesis.py",
        CAMPAIGN / "protocol.json",
        CAMPAIGN / "runtime.json",
        CAMPAIGN / "initial_revision.json",
        ROOT / "benchmarks/trainX.txt",
        ROOT / "benchmarks/validationX.txt",
    ]
    paths += [
        CAMPAIGN / "artifacts" / f"{a}{suffix}.json"
        for a in ("x3", "polished", "examples")
        for suffix in ("", "_render")
    ]
    paths += list(context().demo_files)
    paths += [
        ROOT / p
        for split in ("train", "validation")
        for p in partition(split).values()
    ]
    return sorted(set(paths))


def seal() -> None:
    if accounting()["receipts"]:
        raise ValueError("Seal source before any paid work")
    save(
        "seal.json", {str(p.relative_to(ROOT)): sha(p) for p in source_paths()}
    )


def verify() -> None:
    if (CAMPAIGN / "PAUSED").exists():
        raise ValueError("Campaign paused")
    expected = read("seal.json")
    actual = {str(p.relative_to(ROOT)): sha(p) for p in source_paths()}
    if expected != actual:
        raise ValueError(
            "Source drift: "
            + repr([p for p in actual if expected.get(p) != actual[p]])
        )
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
        yaml.load(
            (folder / "result.yaml").read_text(), Loader=yaml.CSafeLoader
        )
        if (folder / "result.yaml").exists()
        else {}
    )
    diagnostic = str(raw.get("diagnostics", "")) + str(
        raw.get("outcome", {}).get("diagnostics", "")
    )
    diagnostic += "".join(p.read_text() for p in folder.glob("exception*.txt"))
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
        raise ValueError("Batch must use one allocation")
    used = sum(
        r["dollars"] for r in a["ledger"]["groups"] if r["stage"] == stage
    )
    needed = sum(
        j.cap
        for j in selected
        if ol.ground_truth(directory(j)) not in ("done", "failed")
    )
    return (
        used + needed <= ALLOCATIONS[stage] + 1e-9
        and a["ledger"]["liability"] + needed <= CEILING + 1e-9
    )


def launch(batch: str, selected: list[Job]) -> None:
    verify()
    if (CAMPAIGN / f"batches/{batch}.json").exists():
        if selected != jobs(batch):
            raise ValueError("Completed batch changed")
        return
    if not fits(selected):
        raise ValueError("Full nominal batch liability does not fit")
    save(f"manifests/{batch}.json", [asdict(j) for j in selected])
    code = 0
    if selected:
        code = subprocess.run(
            [
                sys.executable,
                "-m",
                "experiments.ace_thesis",
                "run-batch",
                batch,
                "run",
                "--max_workers=24",
                "--wait",
            ],
            cwd=ROOT,
            check=False,
        ).returncode
        for job in selected:
            cell_result(job)
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


def run_batch(batch: str) -> None:
    verify()
    selected = jobs(batch)
    if not os.environ.get("OPENAI_API_KEY") or not fits(selected):
        raise ValueError("Credential or full batch liability missing")
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
