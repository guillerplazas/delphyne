"""Registered independent ACE campaign.

Core matrix: 6 frozen arms x 40 problems x 2 replicates x 2 partitions
= 960 attempts. Sequential trainX: 3 arms x 40 x 2 orders = 240.
Primary: >=10% lower all-attempt tariff cost, accepting <=2 fewer solves
per 40 on average across replicates. Always retain cost/coverage frontier.
Learning cost is separate for frozen books and included for online updates.
No significance veto, protected data, new baseline tools, or default change.
"""

from dataclasses import asdict, dataclass
import os
from pathlib import Path
import random
from typing import Any

import delphyne as dp

from experiments.common import omphalos_launch as ol
from experiments.ace_sanitized.scope import partition
from runtime.campaign_budget import Ledger
from runtime.runtime_profiles import resolve, RuntimeProfile

from .common import CAMPAIGN, OUTPUT, ROOT, read, save, sha
from .accounting import SOURCES


def context() -> dp.ExecutionContext:
    return dp.ExecutionContext(
        workspace_root=ROOT,
        strategy_dirs=[ROOT],
        modules=[
            "prove_standard",
            "prove_agentic",
            "prove_ace",
            "experiments.ace_independent_audit.solver",
            "experiments.ace_independent_audit.learning",
            "experiments.ace_independent_audit.learning_v3",
            "experiments.ace_independent_audit.robust_solver",
        ],
        demo_files=[ROOT / "demos/agentic.demo.yaml"],
        prompt_dirs=[
            ROOT / d
            for d in (
                "experiments/ace_independent_audit/templates",
                "prompts/baselines/agentic",
                "prompts/baselines/standard",
                "prompts/ace/generation",
                "prompts/ace/adaptation",
            )
        ],
    )


@dataclass(frozen=True)
class Job:
    stage: str
    arm: str
    theorem: str
    seed: int
    book_file: str = ""
    book_sha: str = ""
    assisted: bool = True
    output_tokens: int = 32768
    robust: bool = False

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        problems = partition(self.stage)
        if self.theorem not in problems or self.seed not in (0, 1):
            raise ValueError("Unregistered development cell")
        text = ""
        if self.book_file:
            path = CAMPAIGN / self.book_file
            if sha(path) != self.book_sha:
                raise ValueError("Frozen playbook changed")
            text = read(path)["text"]
        cell = name(self, None)
        os.environ.update(
            OMPHALOS_CAMPAIGN_CELL=cell, OMPHALOS_CAMPAIGN_STAGE="solver"
        )
        args: dict[str, Any] = dict(
            problem_file=problems[self.theorem],
            theorem_name=self.theorem,
            turn_budget=32,
            playbook=text,
            show_definitions=True,
            render_version=2,
        )
        if self.robust:
            args["assisted"] = self.assisted
        elif self.assisted:
            args["toolset"] = "core"
        return dp.RunStrategyArgs(
            strategy="audit_robust_solver"
            if self.robust
            else (
                "prove_theorem_ace" if self.assisted else "audit_plain_solver"
            ),
            args=args,
            policy="audit_solver_policy",
            policy_args=dict(cell=cell, output_tokens=self.output_tokens),
            budget=dict(price=0.10, num_requests=32),
        )


def name(job: Job, _: object) -> str:
    return f"{job.stage}__{job.arm}__{job.theorem}__seed{job.seed}"


def activate() -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ.update(
        OMPHALOS_CAMPAIGN_LEDGER=str(CAMPAIGN / "ledger.sqlite3"),
        OMPHALOS_ESTIMATE_DOLLARS="0",
        OMPHALOS_ADMISSION_EVENTS=str(CAMPAIGN / "events.jsonl"),
    )


def register(batch: str, jobs: list[Job]) -> None:
    if len({name(j, None) for j in jobs}) != len(jobs):
        raise ValueError("Duplicate cells")
    save(CAMPAIGN / "batches" / f"{batch}.json", [asdict(j) for j in jobs])


def ordered_jobs(stage: str, arms: list[tuple[str, bool, str]]) -> list[Job]:
    result: list[Job] = []
    for seed in (0, 1):
        names = list(partition(stage))
        random.Random(20260919 + seed).shuffle(names)
        for i, theorem in enumerate(names):
            order = arms if seed == 0 else list(reversed(arms))
            order = order[i % len(order) :] + order[: i % len(order)]
            for arm, assisted, filename in order:
                result.append(
                    Job(
                        stage,
                        arm,
                        theorem,
                        seed,
                        filename,
                        sha(CAMPAIGN / filename) if filename else "",
                        assisted,
                    )
                )
    return result


def prepare() -> None:
    save(
        CAMPAIGN / "protocol.json",
        dict(
            protocol=__doc__,
            version=1,
            date="2026-09-19",
            authorization="User approved plan and unlimited API budget; finite registered batches",
            core_cells=1200,
            frozen_cells=960,
            online_cells=240,
            preliminary="80 source attempts (40 each assisted/plain trainX); role ladder and paired diagnostic pilots registered separately",
            solver="Luna medium Responses, core tools, show definitions, 32 requests, $0.10 stopping budget; 32768 output cap",
            authors=["Luna", "Terra", "Sol", "Astra"],
            scope="trainX/validationX only; no historical reports or mixed aggregates",
            definitions={
                "train": "familiar problems after learning, or pre-update online score",
                "validation": "transfer on reused development benchmark",
            },
            uncertainty="Theorem/family-clustered 90% bootstrap; repeated seeds not independent",
            sources=SOURCES,
            tariff="Four disjoint categories, dated exact models, actual tier/endpoint; no cache warmup",
            administrative_allocation="10000 USD ledger capacity is a safety limit, not an intended spend or old authorization ceiling",
        ),
    )
    if not (CAMPAIGN / "runtime.json").exists():
        save(CAMPAIGN / "runtime.json", asdict(resolve()))
    Ledger(CAMPAIGN / "ledger.sqlite3").create(
        10000, dict(solver=2000, learning=7500, diagnostics=500)
    )
    source = [
        Job("train", arm, theorem, 0, assisted=assisted)
        for theorem in partition("train")
        for arm, assisted in (
            ("source_assisted", True),
            ("source_plain", False),
        )
    ]
    register("source", source)
    print(dict(prepared=True, source_cells=len(source), core_cells=1200))


def run_batch(batch: str) -> None:
    activate()
    jobs = [Job(**v) for v in read(CAMPAIGN / "batches" / f"{batch}.json")]
    if (CAMPAIGN / "PAUSED").exists():
        raise ValueError("Unresolved billing pause")
    # These hashes travel with each fresh batch, never old campaign seals.
    source_hashes = {
        str(p.relative_to(ROOT)): sha(p)
        for p in [
            Path(__file__).parent / f
            for f in (
                "solver.py",
                "transport.py",
                "accounting.py",
                "common.py",
            )
        ]
    }
    if any(j.robust for j in jobs):
        from .completion import install

        install()
        files = [
            ROOT / path
            for path in (
                "experiments/ace_independent_audit/robust_solver.py",
                "experiments/ace_independent_audit/campaign.py",
                "experiments/ace_independent_audit/core.py",
                "experiments/ace_independent_audit/completion.py",
                "prove_ace.py",
                "prove_agentic.py",
                "runtime/pytanque_utils.py",
                "runtime/rocq_server.py",
                "runtime/model_registry.py",
                "runtime/campaign_budget.py",
                "runtime/replay_admission.py",
                "experiments/common/omphalos_launch.py",
                "demos/agentic.demo.yaml",
            )
        ]
        for directory in context().prompt_dirs:
            files.extend(Path(directory).glob("*.jinja"))
        source_hashes.update({str(p.relative_to(ROOT)): sha(p) for p in files})
    save(CAMPAIGN / "batch_sources" / f"{batch}.json", source_hashes)
    ol.OmphalosExperiment(
        config_class=Job,
        configs=jobs,
        context=context(),
        output_dir=str((OUTPUT / batch).relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()
