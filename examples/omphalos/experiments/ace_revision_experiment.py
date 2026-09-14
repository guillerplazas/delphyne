"""Polished ACE platform against fresh paired flagship controls.

Guille reset the experimental budget to zero for this new campaign on
2026-09-13, then required platform correctness before paid dispatch.
Ceiling $40: cached-source adaptation <=$12 (40 R x $.05, 40 C x $.20,
10 reducers x $.20); trainX 40 x 2 arms x $.10 = $8; validationX 40 x
2 seeds x 2 arms x $.10 = $16; unused contingency $4. Maximum 330 jobs.
No paid source generators, embeddings, extra arms/seeds or automatic retries.

The treatment is the book produced by the v2 roles. Generator behavior,
model, focused controller and budgets are matched; only the book differs.
Freeze before proof runs. Advance if the book changes and all applied
receipts and review trails audit. Train effect is not an expansion gate.
Primary final metrics: qualified solves at actual cost <=$.10, total
inference cost and cost/solve on the complete 80-cell validation panel.
Practical interest: >=2 extra solves at <=1.25 cost ratio OR >=10% savings
with <=2 fewer solves. Report family-clustered two-sided p<.10 and 90% CIs,
preparation/all-in cost and amortization separately. No automatic promotion.
Missing or administratively censored cells forbid a verdict; platform
failures stay in denominators. Validation is repeatedly used development
data; testX and protected challenge data remain closed.

Both harnesses: prepare | seal | adapt | audit | training | validation |
replay | report | all | status | run-batch. Only launch/run-batch pays.
"""

# ruff: noqa: E402
from runtime.ace_revision_scope import install

install()

from collections import defaultdict
from contextlib import redirect_stdout
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
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
from runtime.ace_role_journal import RoleJournal
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.model_registry import price_tokens, pricing_for
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile

NAME = "ace_revision_20260913"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
PRIOR = ROOT / "experiments/campaigns/ace_roles_20260913"
BOOK = ROOT / "experiments/playbooks/ace_x3_offline.yaml"
BOOK_SHA = "1e4aec7dbbe80e7a320db17a7c18fe0859bfc00898837c297be248a05dbde067"
ALLOCATIONS = dict(
    adaptation=12.0, training=8.0, validation=16.0, contingency=4.0
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


def context() -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    return replace(
        ctx,
        modules=(
            *ctx.modules,
            "prove_ace_roles",
            "prove_ace_role_revision",
            "prove_writer_drafts",
            "prove_writer_receipts",
            "prove_evidence",
            "prove_resource_completion",
        ),
        demo_files=(
            *ctx.demo_files,
            ROOT / "demos/writer_drafts.demo.yaml",
            ROOT / "demos/ace_roles.demo.yaml",
            ROOT / "demos/ace_role_revision.demo.yaml",
        ),
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
            if self.role == "reflector"
            else 0.20
        )

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if self.stage not in (
            "adaptation",
            "training",
            "validation",
        ) or self.arm not in ("control", "candidate"):
            raise ValueError("Unregistered stage or arm")
        if self.role not in ("proof", "reflector", "curator", "reducer"):
            raise ValueError("Unregistered role")
        if self.seed not in ((0, 1) if self.stage == "validation" else (0,)):
            raise ValueError("Unregistered seed")
        if (
            (self.stage == "adaptation") != (self.role != "proof")
            or self.role != "proof"
            and self.arm != "candidate"
        ):
            raise ValueError("Role/stage mismatch")
        if sha(CAMPAIGN / self.input_file) != self.input_sha256:
            raise ValueError("Input provenance drift")
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        snapshot = str(CAMPAIGN / "transport" / name(self, None))
        proof = self.role == "proof"
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded"
            if proof
            else "reflect_local_repairs"
            if self.role == "reflector"
            else "write_reviewed_book_edits",
            args=read(self.input_file),
            policy="revision_proof_policy"
            if proof
            else "role_revision_policy",
            policy_args=dict(
                snapshot_directory=snapshot,
                pause_file=str(CAMPAIGN / "PAUSED"),
                **({} if proof else dict(dollar_cap=self.cap)),
            ),
            budget=dict(
                price=self.cap,
                num_requests=64 if proof else 7,
                rocq_seconds=300 if proof else 180,
            ),
        )


def name(config: Config, _: object) -> str:
    return f"{config.stage}__{config.arm}__{config.role}__{config.bench_name}__seed{config.seed}"


def directory(config: Config) -> Path:
    return OUTPUT / config.stage / "configs" / name(config, None)


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
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    costs: dict[str, float] = defaultdict(float)
    tokens: dict[str, dict[str, int]] = defaultdict(
        lambda: dict(input=0, cached=0, output=0)
    )
    unresolved: list[str] = []
    issues: list[str] = []
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,usage,cell,status FROM receipts"
        ).fetchall()
    for ident, model, created, charged, usage, cell, status in rows:
        if status != "settled" or charged is None:
            unresolved.append(ident)
            continue
        u = json.loads(usage or "{}")
        if "exception" in u:
            issues.append(ident)
        if charged or "input_tokens" in u:
            inp, out = u["input_tokens"], u["output_tokens"]
            cached = u.get("input_tokens_details", {}).get("cached_tokens", 0)
            actual = price_tokens(
                model,
                inp,
                cached,
                out,
                on=datetime.fromtimestamp(created, timezone.utc).date(),
            )
            if abs(actual - charged) > 1e-8:
                raise ValueError("Receipt repricing mismatch")
            for k, v in (("input", inp), ("cached", cached), ("output", out)):
                tokens[cell][k] += v
        costs[cell] += charged
    return dict(
        total=sum(costs.values()),
        costs=dict(costs),
        tokens=dict(tokens),
        receipts=len(rows),
        unresolved=unresolved,
        billing_issues=issues,
        ledger=ledger.summary(),
    )


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
    Ledger(CAMPAIGN / "ledger.sqlite3").create(40, ALLOCATIONS)
    if accounting()["receipts"]:
        raise ValueError("Preparation cannot run after paid dispatch")
    if Playbook.load(BOOK).sha256() != BOOK_SHA:
        raise ValueError("Flagship book drift")
    order = sorted(partition("training"))
    random.Random(202609132).shuffle(order)
    for n in order:
        save(
            f"sources/{n}.json",
            json.loads((PRIOR / f"sources/{n}.json").read_text()),
        )
    save("runtime.json", json.loads((PRIOR / "runtime.json").read_text()))
    save(
        "authorization.json",
        dict(
            user="with the platform changes in place (if they are) you can restart experiments with budget spent set at zero until now. I am really eager to rebenchmark the new polished platform",
            followup="alright, ensure that new platform works correctly before jumping into experimentations",
            new_ceiling=40,
            initial_spent=0,
            prior_record="ace_roles_20260913/interruption.json",
            prior_accounting=json.loads(
                (PRIOR / "interruption.json").read_text()
            ),
            prior_charges_erased=False,
            prior_liability_consumes_new_authorization=False,
        ),
    )
    save(
        "protocol.json",
        dict(
            protocol=__doc__,
            allocations=ALLOCATIONS,
            ceiling=40,
            max_jobs=330,
            order=order,
            original_book_sha256=BOOK_SHA,
            families=family_map(),
            tariff=asdict(pricing_for("gpt-5.6-luna")),
            price_date=datetime.now(timezone.utc).date().isoformat(),
            automatic_retries=False,
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
        or a["ledger"]["liability"] > 40 + 1e-8
    ):
        raise ValueError("Billing requires reconciliation; no more dispatch")


def seal() -> None:
    if accounting()["receipts"] or not read("preflight.json")["passed"]:
        raise ValueError("Clean offline preflight required before sealing")
    paths = [
        Path(__file__),
        BOOK,
        ROOT / "demos/ace_role_revision.demo.yaml",
        ROOT / "tools/reports/ace_revision_results.py",
        ROOT / "tools/analysis/paired_evaluation.py",
    ]
    for folder, pattern in (
        ("runtime", "*.py"),
        ("ace", "*.py"),
        ("prompts", "*.jinja"),
        ("prompts/ace/role_skills", "*.md"),
        ("prompts/ace/role_skills_v2", "*.md"),
    ):
        paths.extend((ROOT / folder).rglob(pattern))
    paths.extend(ROOT.glob("prove*.py"))
    paths.extend(context().demo_files)
    paths.extend((CAMPAIGN / "sources").glob("*.json"))
    paths.extend(
        CAMPAIGN / p
        for p in (
            "authorization.json",
            "protocol.json",
            "runtime.json",
            "preflight.json",
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
            config = Config(**value)
            found[name(config, None)] = config
    return list(found.values())


def launch(key: str, jobs: list[Config]) -> None:
    save(f"manifests/{key}.json", [asdict(c) for c in jobs])
    if (CAMPAIGN / f"batches/{key}.json").exists():
        return
    verify()
    if not jobs:
        save(f"batches/{key}.json", dict(skipped=True, states={}))
        return
    stage = jobs[0].stage
    ledger = accounting()["ledger"]
    used = sum(r["dollars"] for r in ledger["groups"] if r["stage"] == stage)
    needed = sum(
        c.cap
        for c in jobs
        if ol.ground_truth(directory(c)) not in ("done", "failed")
    )
    if used + needed > ledger["allocations"][stage] + 1e-8:
        raise ValueError("Cannot reserve the entire required batch")
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.ace_revision_experiment",
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


def reflection_args(theorem: str) -> dict[str, Any]:
    source = read(f"sources/{theorem}.json")
    return dict(
        problem_file=source["problem_file"],
        playbook=source["generator_book"],
        trajectory=source["trajectory"],
        terminal=source["terminal"],
        events=source["events"],
    )


def writer_args(
    products: tuple[WriterProduct, ...],
    originals: tuple[ReflectionProduct, ...],
    book: Playbook,
    role: str,
) -> dict[str, Any]:
    args = reduction_input(products, originals, book)
    return dict(
        role=role,
        book=asdict(book),
        evidence=args["evidence"],
        contexts=[asdict(c) for c in args["contexts"]],
        drafts=[asdict(d) for d in args["drafts"]],
        receipts=[asdict(r) for r in args["receipts"]],
    )


def adaptation() -> None:
    book = Playbook.load(BOOK)
    order = read("protocol.json")["order"]
    for batch_no in range(10):
        batch = order[batch_no * 4 : batch_no * 4 + 4]
        rjobs = [
            make_config(
                "adaptation", "candidate", "reflector", n, reflection_args(n)
            )
            for n in batch
        ]
        launch(f"adapt_{batch_no}_reflectors", rjobs)
        originals: list[ReflectionProduct] = []
        cjobs: list[Config] = []
        for job in rjobs:
            product = role_product(job)
            if (
                not isinstance(product, ReflectionProduct)
                or not product.drafts
            ):
                save(
                    f"skips/{job.bench_name}.json",
                    dict(
                        reason="No submitted local draft",
                        reflector=name(job, None),
                    ),
                )
                continue
            originals.append(product)
            cjobs.append(
                make_config(
                    "adaptation",
                    "candidate",
                    "curator",
                    job.bench_name,
                    writer_args((), (product,), book, "curator"),
                )
            )
        launch(f"adapt_{batch_no}_curators", cjobs)
        products = tuple(
            p
            for job in cjobs
            if isinstance(p := role_product(job), WriterProduct)
        )
        if not originals:
            save(
                f"book_steps/{batch_no}.json",
                dict(
                    status="no_drafts",
                    before=book.sha256(),
                    after=book.sha256(),
                ),
            )
            continue
        reducer = make_config(
            "adaptation",
            "candidate",
            "reducer",
            f"batch{batch_no}",
            writer_args(products, tuple(originals), book, "reducer"),
        )
        launch(f"adapt_{batch_no}_reducer", [reducer])
        product = role_product(reducer)
        if isinstance(product, WriterProduct) and product.status == "complete":
            revision = apply_product(book, product)
            save(f"revisions/{batch_no}.json", asdict(revision))
            save(
                f"book_steps/{batch_no}.json",
                dict(
                    status="reviewed",
                    before=book.sha256(),
                    after=revision.after.sha256(),
                    edits=[asdict(e) for e in revision.edits],
                ),
            )
            book = revision.after
        else:
            save(
                f"book_steps/{batch_no}.json",
                dict(
                    status="incomplete_reducer",
                    before=book.sha256(),
                    after=book.sha256(),
                    cell=name(reducer, None),
                ),
            )
    path = CAMPAIGN / "book.yaml"
    if path.exists() and Playbook.load(path).sha256() != book.sha256():
        raise ValueError("Frozen candidate book drift")
    if not path.exists():
        book.save(path)
    save(
        "book.json",
        dict(
            sha256=book.sha256(),
            file_sha256=sha(path),
            changed=book.render_prompt()
            != Playbook.load(BOOK).render_prompt(),
            tokens=book.token_estimate(),
            entries=len(book.bullets),
        ),
    )


def audit() -> None:
    verify()
    activate("adaptation", events=False)
    before = accounting()["receipts"]
    seen: set[str] = set()
    current = Playbook.load(BOOK)
    rows: list[dict[str, Any]] = []
    for path in sorted(
        (CAMPAIGN / "revisions").glob("*.json"), key=lambda p: int(p.stem)
    ):
        revision = pydantic_load(BookRevision, json.loads(path.read_text()))
        rebuilt = apply_product(current, revision.writer)
        if asdict(rebuilt) != asdict(revision):
            raise ValueError("Recorded revision does not reconstruct")
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
            receipt = bank[ident]
            with patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Audit forbids HTTP"),
            ):
                checked = check_snippet(
                    receipt.context,
                    receipt.snippet,
                    dict(seconds=60, rpc_calls=512, view_bytes=8192),
                )
            if checked.identifier != receipt.identifier:
                raise ValueError(
                    "Retained source evidence failed exact recheck"
                )
            seen.add(ident)
            rows.append(
                dict(
                    receipt=ident,
                    source=receipt.context.theorem_name,
                    status=checked.status,
                )
            )
        current = revision.after
    if (
        current.sha256() != read("book.json")["sha256"]
        or before != accounting()["receipts"]
    ):
        raise ValueError("Audit changed billing or failed book reconstruction")
    save(
        "audit.json",
        dict(
            passed=True,
            paid_calls=0,
            receipts=rows,
            reconstructed_sha256=current.sha256(),
        ),
    )


def proof_args(theorem: str, stage: str, arm: str) -> dict[str, Any]:
    path = BOOK if arm == "control" else CAMPAIGN / "book.yaml"
    if arm == "candidate" and sha(path) != read("book.json")["file_sha256"]:
        raise ValueError("Candidate book changed")
    return dict(
        problem_file=partition(stage)[theorem],
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


def proof_jobs(stage: str) -> list[Config]:
    if stage not in ("training", "validation"):
        raise ValueError("Only development proof panels are permitted")
    jobs = [
        make_config(stage, arm, "proof", n, proof_args(n, stage, arm), seed)
        for seed in ((0, 1) if stage == "validation" else (0,))
        for n in partition(stage)
        for arm in ("control", "candidate")
    ]
    random.Random(202609133 if stage == "training" else 202609134).shuffle(
        jobs
    )
    return jobs


def proofs(stage: str) -> None:
    if not read("book.json")["changed"] or not read("audit.json")["passed"]:
        raise ValueError(
            "A changed, audited book is required before benchmarking"
        )
    if stage == "validation":
        for job in configs("training"):
            cell_result(job)
        if not read("training_exposure.json")["new_book_dispatched"]:
            raise ValueError(
                "The changed book did not reach training requests"
            )
    launch(stage, proof_jobs(stage))


def replay() -> None:
    verify()
    before = accounting()["receipts"]
    checks: list[dict[str, Any]] = []
    for config in all_configs():
        original = cell_result(config)
        if original is None:
            checks.append(dict(cell=name(config, None), platform_failed=True))
            continue
        activate(config.stage, events=False)
        args = config.instantiate(None)
        args.cache_mode, args.cache_file = (
            "replay",
            str(directory(config) / "cache.yaml"),
        )
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Replay forbids HTTP"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(context(), cache_root=Path("/")),
                add_header=False,
            )
        if (
            out.result is None
            or out.result.success != original["success"]
            or out.result.spent_budget != original["spent_budget"]
            or json.loads(json.dumps(list(out.result.values)))
            != original["values"]
        ):
            raise ValueError("Exact replay mismatch: " + name(config, None))
        checks.append(dict(cell=name(config, None), passed=True))
    assert before == accounting()["receipts"]
    save(
        f"replays/{len(checks)}.json",
        dict(passed=True, paid_calls=0, cells=checks),
    )


def report() -> None:
    from tools.reports.ace_revision_results import report as perform

    perform()


def all_stages() -> None:
    adaptation()
    audit()
    proofs("training")
    report()
    proofs("validation")
    replay()
    report()


if __name__ == "__main__":
    action = sys.argv.pop(1)
    if action == "run-batch":
        run_batch(sys.argv.pop(1))
    else:
        {
            "prepare": prepare,
            "seal": seal,
            "adapt": adaptation,
            "audit": audit,
            "training": lambda: proofs("training"),
            "validation": lambda: proofs("validation"),
            "replay": replay,
            "report": report,
            "all": all_stages,
            "status": lambda: print(json.dumps(accounting(), indent=2)),
        }[action]()
