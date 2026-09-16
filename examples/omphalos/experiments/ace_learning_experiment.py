"""ACE v3: isolated role pilots, then frozen-book development comparisons.

User approved 2026-09-14: implement the proposed plan, new $30 total API
ceiling; adaptation first; polished v2 primary; reuse compatible controls.
Allocations: pilots $5, adaptation $5, training $8, validation $8, reserve $4.
52 new pilot episodes: 12 schema finals, 16 reviews, 12 reflectors, 12 curators.
Each pilot changes one role mechanism on fixed training inputs; archived
outputs and exact query replays are the controls. No automatic paid retries.
Only treatments with a documented targeted improvement and no newly accepted
unsupported claims enter the candidates. A contains passing schema/review;
B adds passing reflection/curator demonstrations. Missing or uncertain
adjudications cannot silently pass. Pilot thresholds are exploratory.

Both candidate books start at the same X3 book and use the same frozen 40
trainX source histories/order as v2. No paid source generation or embeddings.
The resulting book is the only generator treatment. Identical books are
benchmarked once. Maximum 80 new trainX cells (two books, seed 0), then 160
validationX cells (two books, seeds 0 and 1); 120 unique v2 proof cells reused.
Select primary on training before validation: highest qualified coverage
among candidates at <=1.25 v2 cost, ties by cost; otherwise >=10% savings
with at most one fewer solve. No eligible candidate means no validation.
Second validation requires its full $8 plus $2 contingency; transfer only
unused earlier allocations after their work is complete. No extra seeds.

Primary final metrics: qualified solves at actual charged cost <=$.10,
complete-panel cost and cost/solve. Practical validation threshold: >=2 extra
cells at <=1.25 cost OR >=10% savings with <=2 fewer cells. Two-sided p<.10,
90% intervals, and theorem-family clustering describe statistical support
separately. Reused validation is development, not held-out confirmation.
Report preparation/all-in cost and historical-control/caching limitations.
Missing or administrative censoring forbids a verdict; platform failures
remain in denominators. testX, challenge, censored v1 validation stay closed.
No defaults are changed. Both harnesses use this module and supervised CLI.
"""

# ruff: noqa: E402
from runtime.ace_learning_scope import install

install()

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
from unittest.mock import patch

import delphyne as dp
from delphyne.utils.typing import pydantic_load
import yaml

from ace.ace_playbook import Playbook
from ace.role_contracts import resolve
from ace.role_revision import (
    BookRevision,
    ReflectionProduct,
    WriterProduct,
    apply_product,
    reduction_input,
)
from ace.rocq_snippets import check_snippet
from experiments.coverage_cycle_experiment import family_map, partition
from experiments.common import omphalos_launch as ol
from experiments.common.ace_learning_io import accounting as ledger_accounting
from runtime.ace_role_journal import RoleJournal
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.model_registry import pricing_for
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile

NAME = "ace_learning_20260914"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
PRIOR = ROOT / "experiments/campaigns/ace_revision_20260913"
PRIOR_OUTPUT = ROOT / "experiments/output/ace_revision_20260913"
BOOK = ROOT / "experiments/playbooks/ace_x3_offline.yaml"
ALLOCATIONS = dict(
    pilots=5.0, adaptation=5.0, training=8.0, validation=8.0, contingency=4.0
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    encoded = json.dumps(value, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != encoded:
            raise ValueError("Immutable campaign artifact changed: " + name)
    else:
        path.write_text(encoded)


def context(*, learning_demos: bool = True) -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    demos = [
        ROOT / "demos/writer_drafts.demo.yaml",
        ROOT / "demos/ace_roles.demo.yaml",
        ROOT / "demos/ace_role_revision.demo.yaml",
    ]
    extra = ROOT / "demos/ace_learning.demo.yaml"
    if learning_demos and extra.exists():
        demos.append(extra)
    return replace(
        ctx,
        modules=(
            *ctx.modules,
            "prove_ace_roles",
            "prove_ace_role_revision",
            "prove_ace_learning",
            "prove_writer_drafts",
            "prove_writer_receipts",
            "prove_evidence",
            "prove_resource_completion",
        ),
        demo_files=(*ctx.demo_files, *demos),
    )


@dataclass(frozen=True)
class Config:
    stage: str
    arm: str
    role: str
    bench_name: str
    input_file: str
    input_sha256: str
    seed: int = 0

    @property
    def cap(self) -> float:
        return (
            0.10
            if self.role == "proof"
            else 0.05
            if self.role in ("reflector", "schema", "review")
            else 0.20
        )

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if self.stage not in (
            "pilots",
            "adaptation",
            "training",
            "validation",
        ):
            raise ValueError("Unregistered stage")
        if self.role not in (
            "proof",
            "reflector",
            "curator",
            "reducer",
            "schema",
            "review",
        ):
            raise ValueError("Unregistered role")
        if self.seed not in ((0, 1) if self.stage == "validation" else (0,)):
            raise ValueError("Unregistered seed")
        if (self.role == "proof") != (
            self.stage in ("training", "validation")
        ):
            raise ValueError("Role/stage mismatch")
        if self.arm not in (
            "A",
            "B",
            "control",
            "schema",
            "review",
            "reflection",
            "curation",
        ):
            raise ValueError("Unregistered arm")
        if sha(CAMPAIGN / self.input_file) != self.input_sha256:
            raise ValueError("Input provenance drift")
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        snapshot = str(CAMPAIGN / "transport" / name(self, None))
        strategy = {
            "proof": "prove_theorem_grounded",
            "reflector": "reflect_learning_repairs",
            "curator": "write_learning_book_edits",
            "reducer": "write_learning_book_edits",
            "schema": "learning_plan_pilot",
            "review": "learning_review_pilot",
        }[self.role]
        return dp.RunStrategyArgs(
            strategy=strategy,
            args=read(self.input_file),
            policy="revision_proof_policy"
            if self.role == "proof"
            else "learning_role_policy",
            policy_args=dict(
                snapshot_directory=snapshot,
                pause_file=str(CAMPAIGN / "PAUSED"),
                **({} if self.role == "proof" else dict(dollar_cap=self.cap)),
            ),
            budget=dict(
                price=self.cap,
                num_requests=64
                if self.role == "proof"
                else 1
                if self.role in ("schema", "review")
                else 7,
                rocq_seconds=300 if self.role == "proof" else 180,
            ),
        )


def name(config: Config, _: object) -> str:
    return f"{config.stage}__{config.arm}__{config.role}__{config.bench_name}__seed{config.seed}"


def directory(config: Config) -> Path:
    return OUTPUT / config.stage / "configs" / name(config, None)


def prior_directory(
    stage: str, role: str, theorem: str, seed: int = 0
) -> Path:
    return (
        PRIOR_OUTPUT
        / stage
        / "configs"
        / f"{stage}__candidate__{role}__{theorem}__seed{seed}"
    )


def prior_result(
    stage: str, role: str, theorem: str, seed: int = 0
) -> dict[str, Any]:
    return yaml.safe_load(
        (
            prior_directory(stage, role, theorem, seed) / "result.yaml"
        ).read_text()
    )


def make_config(
    stage: str,
    arm: str,
    role: str,
    theorem: str,
    args: dict[str, Any],
    seed: int = 0,
) -> Config:
    path = f"inputs/{stage}/{arm}_{role}_{theorem}_{seed}.json"
    save(path, args)
    return Config(stage, arm, role, theorem, path, sha(CAMPAIGN / path), seed)


def accounting() -> dict[str, Any]:
    return ledger_accounting(CAMPAIGN)


def activate(stage: str, *, events: bool = True) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ.update(
        OMPHALOS_CAMPAIGN_LEDGER=str(CAMPAIGN / "ledger.sqlite3"),
        OMPHALOS_CAMPAIGN_STAGE=stage,
        OMPHALOS_ESTIMATE_DOLLARS="1",
    )
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )
    else:
        os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)


def cell_result(config: Config) -> dict[str, Any] | None:
    folder = directory(config)
    state = ol.ground_truth(folder)
    if state not in ("done", "failed"):
        raise ValueError("Missing required cell: " + name(config, None))
    raw: dict[str, Any] = (
        yaml.safe_load((folder / "result.yaml").read_text())
        if (folder / "result.yaml").exists()
        else {}
    )
    diagnostics = (
        str(raw.get("diagnostics", ""))
        + str(raw.get("outcome", {}).get("diagnostics", ""))
        + "".join(p.read_text() for p in folder.glob("exception*.txt"))
    )
    if any(
        tag in diagnostics for tag in ("CampaignExhausted", "CampaignPaused")
    ):
        raise ValueError("Administrative censoring: " + name(config, None))
    return raw.get("outcome", {}).get("result") if state == "done" else None


def role_product(config: Config) -> ReflectionProduct | WriterProduct | None:
    raw = cell_result(config)
    if raw and raw["success"] and len(raw["values"]) == 1:
        return pydantic_load(
            ReflectionProduct if config.role == "reflector" else WriterProduct,
            raw["values"][0],
        )
    checkpoint = RoleJournal(
        CAMPAIGN / "transport" / name(config, None) / "checkpoints"
    ).latest()
    return checkpoint.product if checkpoint else None


def prepare() -> None:
    Ledger(CAMPAIGN / "ledger.sqlite3").create(30, ALLOCATIONS)
    if accounting()["receipts"]:
        raise ValueError("Preparation is closed after paid dispatch")
    old = json.loads((PRIOR / "protocol.json").read_text())
    for theorem in old["order"]:
        save(
            f"sources/{theorem}.json",
            json.loads((PRIOR / f"sources/{theorem}.json").read_text()),
        )
    save("runtime.json", json.loads((PRIOR / "runtime.json").read_text()))
    save(
        "authorization.json",
        dict(
            user="Implement the plan.",
            decisions=dict(
                new_ceiling=30,
                reference="polished v2",
                scope="adaptation first",
                controls="reuse compatible controls",
            ),
            prior_charges_erased=False,
            initial_new_spend=0,
            automatic_retries=False,
        ),
    )
    save(
        "protocol.json",
        dict(
            protocol=__doc__,
            ceiling=30,
            allocations=ALLOCATIONS,
            order=old["order"],
            families=family_map(),
            tariff=asdict(pricing_for("gpt-5.6-luna")),
            price_date=datetime.now(timezone.utc).date().isoformat(),
            original_book_sha256=Playbook.load(BOOK).sha256(),
            control_book_sha256=Playbook.load(PRIOR / "book.yaml").sha256(),
            max_new_proof_cells=240,
            reused_proof_cells=120,
            max_pilot_episodes=52,
            defaults_changed=False,
        ),
    )


def verify() -> None:
    if (CAMPAIGN / "PAUSED").exists():
        raise ValueError("Campaign is paused")
    for path, expected in read("seal.json")["files"].items():
        if sha(ROOT / path) != expected:
            raise ValueError("Sealed source/input drift: " + path)
    a = accounting()
    if (
        a["unresolved"]
        or a["billing_issues"]
        or a["ledger"]["liability"] > 30 + 1e-8
    ):
        raise ValueError("Billing requires reconciliation before dispatch")


def seal() -> None:
    if accounting()["receipts"] or not read("preflight.json")["passed"]:
        raise ValueError("Passing offline preflight required before sealing")
    paths = [Path(__file__), BOOK, PRIOR / "book.yaml", ROOT / "delphyne.yaml"]
    for folder, pattern in (
        ("runtime", "*.py"),
        ("ace", "*.py"),
        ("prompts", "*.jinja"),
        ("prompts/ace", "*.md"),
    ):
        paths.extend((ROOT / folder).rglob(pattern))
    paths.extend(ROOT.glob("prove*.py"))
    paths.extend(context().demo_files)
    paths.extend((CAMPAIGN / "sources").glob("*.json"))
    paths.extend((CAMPAIGN / "pilot_sources").rglob("*.json"))
    paths.extend(
        ROOT / f
        for f in (
            "experiments/common/ace_learning_io.py",
            "tools/data/ace_learning_data.py",
            "tools/data/ace_learning_fixtures.py",
            "tools/reports/ace_learning_results.py",
            "tools/analysis/paired_evaluation.py",
        )
    )
    paths.extend(
        CAMPAIGN / p
        for p in (
            "authorization.json",
            "protocol.json",
            "runtime.json",
            "preflight.json",
            "pilot_registration.json",
            "compatibility.json",
        )
    )
    save(
        "seal.json",
        dict(
            files={
                str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))
            }
        ),
    )


def configs(key: str) -> list[Config]:
    return [Config(**x) for x in read(f"manifests/{key}.json")]


def all_configs() -> list[Config]:
    found: dict[str, Config] = {}
    for path in sorted((CAMPAIGN / "manifests").glob("*.json")):
        for value in json.loads(path.read_text()):
            cfg = Config(**value)
            found[name(cfg, None)] = cfg
    return list(found.values())


def stage_used(stage: str) -> float:
    return sum(
        r["dollars"]
        for r in accounting()["ledger"]["groups"]
        if r["stage"] == stage
    )


def launch(key: str, jobs: list[Config]) -> None:
    verify()
    if (CAMPAIGN / f"batches/{key}.json").exists():
        return
    if not jobs:
        save(f"manifests/{key}.json", [])
        save(f"batches/{key}.json", dict(skipped=True, states={}))
        return
    stage = jobs[0].stage
    needed = sum(
        c.cap
        for c in jobs
        if ol.ground_truth(directory(c)) not in ("done", "failed")
    )
    a = accounting()["ledger"]
    if (
        stage_used(stage) + needed > a["allocations"][stage] + 1e-8
        or a["liability"] + needed > 30 + 1e-8
    ):
        raise ValueError("Cannot reserve the entire required batch")
    save(f"manifests/{key}.json", [asdict(c) for c in jobs])
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.ace_learning_experiment",
            "run-batch",
            key,
            "run",
            "--max_workers=24",
            "--wait",
        ],
        cwd=ROOT,
        check=False,
    )
    for config in jobs:
        cell_result(config)
    verify()
    save(
        f"batches/{key}.json",
        dict(
            exit_code=completed.returncode,
            states={
                name(c, None): ol.ground_truth(directory(c)) for c in jobs
            },
        ),
    )


def run_batch(key: str) -> None:
    verify()
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher lacks credential")
    jobs = configs(key)
    activate(jobs[0].stage)
    ol.OmphalosExperiment(
        config_class=Config,
        configs=jobs,
        context=context(),
        output_dir=str((OUTPUT / jobs[0].stage).relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def pilots() -> None:
    registration = read("pilot_registration.json")
    for treatment in ("schema", "review", "reflection", "curation"):
        jobs = [
            make_config(
                "pilots",
                treatment,
                row["role"],
                row["case"],
                read(row["input"]),
            )
            for row in registration["cases"]
            if row["treatment"] == treatment
        ]
        launch("pilot_" + treatment, jobs)


def reflection_args(theorem: str, book: Playbook) -> dict[str, Any]:
    source = read(f"sources/{theorem}.json")
    return dict(
        problem_file=source["problem_file"],
        playbook=source["generator_book"],
        trajectory=source["trajectory"],
        terminal=source["terminal"],
        events=source["events"],
        current_book=book.render_prompt(),
    )


def writer_args(
    products: tuple[WriterProduct, ...],
    originals: tuple[ReflectionProduct, ...],
    book: Playbook,
    role: str,
    selected: dict[str, bool],
) -> dict[str, Any]:
    args = reduction_input(products, originals, book)
    theorems = {c.theorem_name for c in args["contexts"]}
    return dict(
        role=role,
        book=asdict(book),
        evidence=args["evidence"],
        contexts=[asdict(c) for c in args["contexts"]],
        drafts=[asdict(d) for d in args["drafts"]],
        receipts=[asdict(r) for r in args["receipts"]],
        source_events=[
            e
            for n in sorted(theorems)
            for e in read(f"sources/{n}.json")["events"]
        ],
        strict_actions=selected["schema"],
        evidence_review=selected["review"],
        targeted_demos=selected["curation"],
    )


def adaptation(arm: str) -> None:
    verify()
    if arm not in ("A", "B"):
        raise ValueError("Only two registered candidate books")
    selected: dict[str, bool] = dict(read("pilot_decisions.json")["selected"])
    if arm == "A":
        selected.update(reflection=False, curation=False)
    if arm == "B" and not selected["reflection"] and not selected["curation"]:
        save(
            "books/B.skipped.json",
            dict(reason="No additional treatment passed", identical_to="A"),
        )
        return
    if not any(selected.values()):
        save(
            f"books/{arm}.skipped.json",
            dict(reason="No treatment passed local evaluation"),
        )
        return
    book = Playbook.load(BOOK)
    order = read("protocol.json")["order"]
    for batch_no in range(10):
        batch = order[batch_no * 4 : batch_no * 4 + 4]
        originals: list[ReflectionProduct] = []
        if selected["reflection"]:
            jobs = [
                make_config(
                    "adaptation", arm, "reflector", n, reflection_args(n, book)
                )
                for n in batch
            ]
            launch(f"adapt_{arm}_{batch_no}_reflectors", jobs)
            originals = [
                p
                for j in jobs
                if isinstance(p := role_product(j), ReflectionProduct)
            ]
        else:
            for n in batch:
                value = prior_result("adaptation", "reflector", n)["outcome"][
                    "result"
                ]["values"][0]
                originals.append(pydantic_load(ReflectionProduct, value))
            save(
                f"reuse/{arm}_{batch_no}_reflectors.json",
                dict(
                    sources=[
                        str(
                            prior_directory(
                                "adaptation", "reflector", n
                            ).relative_to(ROOT)
                        )
                        for n in batch
                    ],
                    marginal_cost=0,
                ),
            )
        originals = [p for p in originals if p.drafts]
        jobs: list[Config] = []
        for product in originals:
            theorem = product.contexts[0].theorem_name
            jobs.append(
                make_config(
                    "adaptation",
                    arm,
                    "curator",
                    theorem,
                    writer_args((), (product,), book, "curator", selected),
                )
            )
        launch(f"adapt_{arm}_{batch_no}_curators", jobs)
        finished = [role_product(j) for j in jobs]
        products = tuple(p for p in finished if isinstance(p, WriterProduct))
        if not originals:
            save(
                f"book_steps/{arm}/{batch_no}.json",
                dict(
                    status="no_drafts",
                    before=book.sha256(),
                    after=book.sha256(),
                ),
            )
            continue
        reducer = make_config(
            "adaptation",
            arm,
            "reducer",
            f"batch{batch_no}",
            writer_args(products, tuple(originals), book, "reducer", selected),
        )
        launch(f"adapt_{arm}_{batch_no}_reducer", [reducer])
        product = role_product(reducer)
        if isinstance(product, WriterProduct) and product.status == "complete":
            revision = apply_product(book, product)
            save(f"revisions/{arm}/{batch_no}.json", asdict(revision))
            save(
                f"book_steps/{arm}/{batch_no}.json",
                dict(
                    status="reviewed",
                    before=book.sha256(),
                    after=revision.after.sha256(),
                ),
            )
            book = revision.after
        else:
            save(
                f"book_steps/{arm}/{batch_no}.json",
                dict(
                    status="incomplete_reducer",
                    before=book.sha256(),
                    after=book.sha256(),
                ),
            )
    path = CAMPAIGN / f"books/{arm}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and Playbook.load(path).sha256() != book.sha256():
        raise ValueError("Frozen candidate book drift")
    if not path.exists():
        book.save(path)
    save(
        f"books/{arm}.json",
        dict(
            sha256=book.sha256(),
            file_sha256=sha(path),
            tokens=book.token_estimate(),
            entries=len(book.bullets),
            selected=selected,
            changed=book.render_prompt()
            != Playbook.load(PRIOR / "book.yaml").render_prompt(),
        ),
    )


def audit(arm: str) -> None:
    verify()
    activate("adaptation", events=False)
    seen: set[str] = set()
    current = Playbook.load(BOOK)
    rows: list[dict[str, Any]] = []
    for path in sorted(
        (CAMPAIGN / f"revisions/{arm}").glob("*.json"),
        key=lambda p: int(p.stem),
    ):
        revision = pydantic_load(BookRevision, json.loads(path.read_text()))
        if asdict(apply_product(current, revision.writer)) != asdict(revision):
            raise ValueError("Revision did not reconstruct")
        bank = {r.identifier: r for r in revision.writer.receipts}
        retained = {r for e in revision.edits for r in e.receipts}
        assert revision.writer.plan is not None
        retained.update(
            resolve(
                d.failure_receipt, "r", revision.writer.receipts
            ).identifier
            for d in revision.writer.plan.decisions
            if d.failure_receipt
        )
        for ident in sorted(retained - seen):
            r = bank[ident]
            with patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Audit forbids HTTP"),
            ):
                checked = check_snippet(
                    r.context,
                    r.snippet,
                    dict(seconds=60, rpc_calls=512, view_bytes=8192),
                )
            if checked.identifier != r.identifier:
                raise ValueError("Retained receipt failed exact recheck")
            seen.add(ident)
            rows.append(
                dict(
                    receipt=ident,
                    theorem=r.context.theorem_name,
                    status=checked.status,
                )
            )
        current = revision.after
    if current.sha256() != read(f"books/{arm}.json")["sha256"]:
        raise ValueError("Final book differs from audited revisions")
    save(
        f"audits/{arm}.json",
        dict(
            passed=True,
            paid_calls=0,
            reconstructed=current.sha256(),
            receipts=rows,
        ),
    )


def proof_jobs(stage: str, arm: str) -> list[Config]:
    if stage not in ("training", "validation"):
        raise ValueError("Only development panels")
    path = (
        PRIOR / "book.yaml"
        if arm == "control"
        else CAMPAIGN / f"books/{arm}.yaml"
    )
    if (
        arm != "control"
        and sha(path) != read(f"books/{arm}.json")["file_sha256"]
    ):
        raise ValueError("Frozen book changed")
    jobs: list[Config] = []
    for seed in (0, 1) if stage == "validation" else (0,):
        for theorem, problem in partition(stage).items():
            args = dict(
                problem_file=problem,
                theorem_name=theorem,
                playbook=Playbook.load(path).render_prompt(),
                claims=[],
                turn_budget=64,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
                verifier_seconds=300,
                admission=False,
                focused=True,
                restart=False,
            )
            jobs.append(make_config(stage, arm, "proof", theorem, args, seed))
    random.Random(202609140 if stage == "training" else 202609141).shuffle(
        jobs
    )
    return jobs


def proofs(stage: str, arm: str) -> None:
    verify()
    if arm != "control":
        if not read(f"audits/{arm}.json")["passed"]:
            raise ValueError("Audit required")
        if not read(f"books/{arm}.json")["changed"]:
            save(
                f"{stage}_{arm}.skipped.json",
                dict(reason="Book identical to v2"),
            )
            return
        if (
            arm == "B"
            and (CAMPAIGN / "books/A.json").exists()
            and read("books/B.json")["sha256"]
            == read("books/A.json")["sha256"]
        ):
            save(
                f"{stage}_{arm}.skipped.json",
                dict(reason="Book identical to A", identical_to="A"),
            )
            return
    if stage == "validation" and arm != "control":
        selection = read("selection.json")
        secondary = CAMPAIGN / "secondary_validation.json"
        selected_secondary = (
            json.loads(secondary.read_text())["arm"]
            if secondary.exists()
            else None
        )
        if (
            arm not in selection["validation_arms"]
            and arm != selected_secondary
        ):
            raise ValueError("Arm was not selected before validation")
    launch(f"{stage}_{arm}", proof_jobs(stage, arm))


def fund_second_validation() -> bool:
    """Registered rollover, preserving $2 for unresolved/contingent charges."""
    verify()
    a = accounting()["ledger"]
    if 30 - a["liability"] < 10 - 1e-8:
        return False
    available = a["allocations"]["validation"] - stage_used("validation")
    needed = max(0.0, 8.0 - available)
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    for source in ("pilots", "adaptation", "training", "contingency"):
        allocation = ledger.summary()["allocations"][source]
        amount = min(
            needed,
            max(
                0.0,
                allocation
                - stage_used(source)
                - (2.0 if source == "contingency" else 0.0),
            ),
        )
        if amount > 1e-9:
            ledger.transfer(
                source,
                "validation",
                amount,
                "Preregistered completed-stage savings for second full validation panel",
            )
            needed -= amount
    return needed <= 1e-8


def main() -> None:
    action = sys.argv.pop(1)
    if action == "run-batch":
        run_batch(sys.argv.pop(1))
    elif action in ("adapt", "audit"):
        {"adapt": adaptation, "audit": audit}[action](sys.argv.pop(1))
    elif action in ("training", "validation"):
        proofs(action, sys.argv.pop(1))
    elif action == "replay":
        from experiments.common.ace_learning_io import replay

        replay(sys.modules[__name__])
    elif action == "report":
        from tools.reports.ace_learning_results import report

        report()
    elif action in ("select", "secondary"):
        from tools.reports.ace_learning_results import select, secondary

        print(json.dumps({"select": select, "secondary": secondary}[action]()))
    elif action == "data":
        from tools.data.ace_learning_data import build

        build()
    else:
        {
            "prepare": prepare,
            "seal": seal,
            "pilots": pilots,
            "status": lambda: print(json.dumps(accounting(), indent=2)),
        }[action]()


if __name__ == "__main__":
    main()
