"""ACE roles campaign, authorized by Guille: implement the $40 plan.

Writer pilot: 8 curators + 2 chained reducers x 2 arms, $4 maximum.
Reflection: 8 sources x 2 arms, $.80. One full cached-source adaptation:
40 R x $.05 + 40 C x $.20 + 10 reducers x $.20 <= $12. Train: 40 x $.10.
Final: 40 validation problems x 2 seeds x finalist/reference <= $16.
Contingency $3.20; total ceiling $40 includes every new experimental charge.
No source generators, embeddings, extra seeds, automatic retries or defaults.

Writer gate: >=9/10 valid including both reducers; useful distinct retained
corrections >= control and improvement in validity, utility, or cost/useful.
Reflection inclusion: more useful faithful lessons, no more unsupported
execution claims, <=1.5 cost/useful. Otherwise use existing terminal-v2.
Book gate: useful checked addition survives merge and reaches train requests.
No train effect/p-value gate. Final practical flag: >=2 additional qualified
solves/80 at <=1.25 inference cost OR >=10% saving with <=2 fewer solves.
All-in preparation/amortization reported separately, no automatic promotion.
Family-clustered two-sided p<.10/90% intervals. Failed cells stay denominators;
missing/admin-censored cells prevent verdicts. validationX is development data.

Both harnesses: prepare | demos | preflight | seal | pilots | audit | gates |
adapt | training | validation | report | replay. Only launch/run-batch pays.
"""

# ruff: noqa: E402
from runtime.ace_roles_scope import install

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

from ace.ace_playbook import Playbook, merge
from ace.role_contracts import ReflectedLesson, TrainingEvent, lesson_draft
from ace.rocq_snippets import SnippetContext, context_for
from ace.terminal_evidence import extract_terminal_evidence
from experiments.ace.ace_adaptation import extract_trajectory
from experiments.coverage_cycle_experiment import partition, family_map
from experiments.common import omphalos_launch as ol
from prove_writer_drafts import (
    DraftWriting,
    UnverifiedSnippetDraft,
    reduction_input,
)
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.model_registry import price_tokens, pricing_for
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile

NAME = "ace_roles_20260913"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
BOOK = ROOT / "experiments/playbooks/ace_x3_offline.yaml"
BOOK_SHA = "1e4aec7dbbe80e7a320db17a7c18fe0859bfc00898837c297be248a05dbde067"
ALLOCATIONS = dict(
    writer_pilot=4.0,
    reflection_pilot=0.8,
    adaptation=12.0,
    training=4.0,
    validation=16.0,
    contingency=3.2,
)
OLD = ROOT / "experiments/campaigns/ace_snippets_20260913"
ATTR = ROOT / "experiments/campaigns/ace_attribution_20260912"
SOURCES = (
    "aime_1984_p1",
    "amc12_2000_p1",
    "amc12a_2020_p13",
    "amc12b_2004_p3",
    "imo_1968_p5_1",
    "mathd_algebra_224",
    "mathd_algebra_28",
    "mathd_numbertheory_629",
)
REFLECT_SOURCES = tuple(
    "amc12_2000_p6" if n == "mathd_algebra_224" else n for n in SOURCES
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, sort_keys=True, indent=2) + "\n"
    if path.exists():
        if path.read_text() != text:
            raise ValueError("Immutable artifact changed: " + name)
    else:
        path.write_text(text)


def context() -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    return replace(
        ctx,
        modules=(
            *ctx.modules,
            "prove_ace_roles",
            "prove_writer_receipts",
            "prove_writer_drafts",
            "prove_evidence",
            "prove_resource_completion",
        ),
        demo_files=(
            *ctx.demo_files,
            ROOT / "demos/writer_drafts.demo.yaml",
            ROOT / "demos/ace_roles.demo.yaml",
        ),
    )


@dataclass
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
        if self.arm not in ("control", "candidate") or self.role not in (
            "proof",
            "reflector",
            "curator",
            "reducer",
        ):
            raise ValueError("Unregistered role or arm")
        if self.stage not in ALLOCATIONS or self.stage == "contingency":
            raise ValueError("Unregistered stage")
        if self.seed not in ((0, 1) if self.stage == "validation" else (0,)):
            raise ValueError("Unregistered seed")
        if sha(CAMPAIGN / self.input_file) != self.input_sha256:
            raise ValueError("Input provenance drift")
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        args = read(self.input_file)
        snapshot = str(CAMPAIGN / "transport" / name(self, None))
        if self.role == "proof":
            return dp.RunStrategyArgs(
                strategy="prove_theorem_grounded",
                args=args,
                policy="completion_policy",
                policy_args=dict(arm="reference", snapshot_directory=snapshot),
                budget=dict(price=0.10, num_requests=64, rocq_seconds=300),
            )
        strategy = (
            "reflect_ace_evidence"
            if self.role == "reflector"
            else "write_ace_choices"
        )
        if self.arm == "control":
            strategy = (
                "reflect_on_trajectory_v2"
                if self.role == "reflector"
                else "write_rocq_receipts"
            )
        return dp.RunStrategyArgs(
            strategy=strategy,
            args=args,
            policy="ace_roles_policy",
            policy_args=dict(
                snapshot_directory=snapshot,
                mode=("reflector" if self.role == "reflector" else "writer")
                + ("_control" if self.arm == "control" else ""),
                dollar_cap=self.cap,
            ),
            budget=dict(price=self.cap, num_requests=4, rocq_seconds=180),
        )


def name(c: Config, _: object) -> str:
    return f"{c.stage}__{c.arm}__{c.role}__{c.bench_name}__seed{c.seed}"


def directory(c: Config) -> Path:
    return OUTPUT / c.stage / "configs" / name(c, None)


def make_config(
    stage: str,
    arm: str,
    role: str,
    theorem: str,
    args: dict[str, Any],
    seed: int = 0,
) -> Config:
    filename = f"inputs/{stage}/{arm}_{role}_{theorem}_{seed}.json"
    save(filename, args)
    return Config(
        stage, arm, role, theorem, filename, sha(CAMPAIGN / filename), seed
    )


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
        session_cost=None,
    )


def activate(stage: str, events: bool = True) -> None:
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


def cell_result(c: Config) -> dict[str, Any] | None:
    d = directory(c)
    status = ol.ground_truth(d)
    if status not in ("done", "failed"):
        raise ValueError("Missing required cell: " + name(c, None))
    raw: dict[str, Any] = (
        yaml.safe_load((d / "result.yaml").read_text())
        if (d / "result.yaml").exists()
        else {}
    )
    descriptions = (
        str(raw.get("diagnostics", ""))
        + str(raw.get("outcome", {}).get("diagnostics", ""))
        + "".join(p.read_text() for p in d.glob("exception*.txt"))
    )
    if "CampaignExhausted" in descriptions:
        raise ValueError("Administrative censoring: " + name(c, None))
    return raw.get("outcome", {}).get("result") if status == "done" else None


def writer_product(c: Config) -> DraftWriting | None:
    raw = cell_result(c)
    return (
        pydantic_load(DraftWriting, raw["values"][0])
        if raw and raw["success"] and len(raw["values"]) == 1
        else None
    )


def prepare() -> None:
    Ledger(CAMPAIGN / "ledger.sqlite3").create(40, ALLOCATIONS)
    if accounting()["receipts"]:
        raise ValueError("Preparation cannot run after paid dispatch")
    refs = json.loads((ATTR / "references.json").read_text())
    if Playbook.load(BOOK).sha256() != BOOK_SHA:
        raise ValueError("Flagship book drift")
    for stage in ("training", "validation"):
        if {r["theorem"] for r in refs[stage]} != set(partition(stage)):
            raise ValueError("Incomplete development references")
    save("references.json", refs)
    save(
        "runtime.json",
        json.loads(
            (
                ROOT
                / "experiments/campaigns/ace_capacity_20260912/runtime.json"
            ).read_text()
        ),
    )
    save(
        "protocol.json",
        dict(
            authorization="Guille: Implement the plan",
            ceiling=40,
            allocations=ALLOCATIONS,
            max_jobs=326,
            automatic_retries=False,
            source_generators=0,
            embeddings=0,
            writer_sources=SOURCES,
            reflector_sources=REFLECT_SOURCES,
            book_sha256=BOOK_SHA,
            families=family_map(),
            tariff=asdict(pricing_for("gpt-5.6-luna")),
            price_date=datetime.now(timezone.utc).date().isoformat(),
            protocol=__doc__,
            validation_status="reused development data; two fresh paired seeds",
            defaults_changed=False,
        ),
    )
    diagnostics = json.loads((ATTR / "complete_diagnostics.json").read_text())
    for ref in refs["training"]:
        theorem = ref["theorem"]
        source = ROOT / ref["source"] / "configs" / ref["name"]
        terminal = extract_terminal_evidence(source, theorem)
        events: list[TrainingEvent] = []
        for i, check in enumerate(
            diagnostics[f"training/luna-ace/{theorem}"]["checks"]
        ):
            ctx = context_for(
                terminal.problem_file,
                theorem,
                ()
                if check["success"] and not check["tactic"]
                else tuple(check["verified_prefix"]),
                terminal.cache_sha256,
            )
            events.append(
                TrainingEvent(
                    f"e{i + 1}",
                    ctx,
                    check["tactic"]
                    or (
                        "\n".join(terminal.accepted_script)
                        if check["success"]
                        else ""
                    ),
                    check["outcome"],
                    check["error"] or "",
                    tuple(check["remaining_goals"]),
                )
            )
        save(
            f"sources/{theorem}.json",
            dict(
                problem_file=terminal.problem_file,
                trajectory=extract_trajectory(source, theorem),
                terminal=asdict(terminal),
                events=[asdict(e) for e in events],
                generator_book=Playbook.load(BOOK).render_prompt(),
            ),
        )
    packets = json.loads(
        (OLD / "reducer_study/candidate_packets.json").read_text()
    )
    save("candidate_packets.json", packets)
    save(
        "utility_rubric.json",
        dict(
            source="Existing draft pilot source rubric plus explicit source-local execution checks",
            writer=json.loads(
                (OLD / "writer_pilot/utility_rubric.json").read_text()
            ),
            reflection="Useful = correct execution attribution and a concrete nonredundant reusable operation, or specific justified abstention. Unsupported execution claims count separately. No reward for length or plausible lemma names.",
            scope="Agent review of arm-free item exports; not independent human-blinded adjudication",
            writer_gate="valid>=9/10 and both reducers valid; distinct useful >= control; more valid OR more useful OR lower cost/useful",
            reflection_gate="more useful faithful lessons; unsupported claims <= control; cost/useful <=1.5 control",
        ),
    )
    save(
        "milestones/prepared.json",
        dict(
            experimental_spend=0,
            plan_tests_passed=11,
            terminal_sources=40,
            planning_scope_incident="Initial mixed index/history snippets encountered and excluded; guarded data access thereafter",
        ),
    )


def verify() -> None:
    for file, expected in read("seal.json")["files"].items():
        if sha(ROOT / file) != expected:
            raise ValueError("Sealed source/input drift: " + file)
    a = accounting()
    if (
        a["unresolved"]
        or a["billing_issues"]
        or a["ledger"]["liability"] > 40 + 1e-8
    ):
        raise ValueError("Billing issue; no further admission")


def seal() -> None:
    if not read("offline_checks.json")["passed"] or accounting()["receipts"]:
        raise ValueError("Clean preflight required before sealing")
    paths = [
        Path(__file__),
        BOOK,
        ROOT / "runtime/ace_roles_scope.py",
        ROOT / "ace/role_contracts.py",
        ROOT / "prove_ace_roles.py",
        ROOT / "demos/ace_roles.demo.yaml",
        ROOT / "tests/test_ace_roles.py",
    ]
    for folder, pattern in (
        ("runtime", "*.py"),
        ("ace", "*.py"),
        ("prompts", "*.jinja"),
        ("prompts/ace/role_skills", "*.md"),
    ):
        paths.extend((ROOT / folder).rglob(pattern))
    paths.extend(ROOT.glob("prove*.py"))
    paths.extend((CAMPAIGN / "sources").glob("*.json"))
    paths.extend(
        CAMPAIGN / p
        for p in (
            "protocol.json",
            "references.json",
            "runtime.json",
            "candidate_packets.json",
            "utility_rubric.json",
            "offline_checks.json",
            "terminal_fixture.json",
            "demo_checks.json",
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
    return [Config(**c) for c in read(f"manifests/{key}.json")]


def launch(key: str, jobs: list[Config]) -> None:
    save(f"manifests/{key}.json", [asdict(c) for c in jobs])
    if (CAMPAIGN / f"batches/{key}.json").exists():
        return
    verify()
    if not jobs:
        save(
            f"batches/{key}.json",
            dict(skipped="No candidates; no model calls", states={}),
        )
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
        raise ValueError("Cannot reserve whole required stage")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.ace_roles_experiment",
            "run-batch",
            key,
            "run",
            "--max_workers=24",
            "--wait",
        ],
        cwd=ROOT,
        check=False,
    )
    for c in jobs:
        cell_result(c)
    verify()
    save(
        f"batches/{key}.json",
        dict(
            exit_code=result.returncode,
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


def handoff(
    jobs: list[Config], original_inputs: list[dict[str, Any]], book: str
) -> dict[str, Any]:
    products = [p for c in jobs if (p := writer_product(c)) is not None]
    contexts: dict[str, SnippetContext] = {}
    drafts: dict[str, UnverifiedSnippetDraft] = {}
    for args in original_inputs:
        for raw in args["contexts"]:
            c = pydantic_load(SnippetContext, raw)
            contexts[c.identifier] = c
        for raw in args["drafts"]:
            d = pydantic_load(UnverifiedSnippetDraft, raw)
            drafts[d.draft_id] = d
    args = reduction_input(products, tuple(contexts.values()), book)
    args["drafts"] = tuple(drafts.values())
    evidence = json.loads(args["evidence"])
    evidence.extend(
        dict(
            failed_curator=name(c, None),
            original_drafts=read(c.input_file)["drafts"],
        )
        for c in jobs
        if writer_product(c) is None
    )
    args["evidence"] = json.dumps(evidence)
    return json.loads(json.dumps(args, default=lambda o: asdict(o)))


def reflection_args(
    theorem: str, candidate: bool, fixture: bool = False
) -> dict[str, Any]:
    source = read(
        "terminal_fixture.json" if fixture else f"sources/{theorem}.json"
    )
    args = {k: source[k] for k in ("problem_file", "trajectory", "terminal")}
    args["playbook"] = source["generator_book"]
    if candidate:
        args["events"] = source["events"]
    else:
        args["outcome"] = (
            "SOLVED"
            if source["terminal"]["status"] == "accepted"
            else "UNSOLVED"
        )
    return args


def pilots() -> None:
    verify()
    book = Playbook.load(BOOK).render_prompt()
    for batch_no, packets in enumerate(
        read("candidate_packets.json")["batches"]
    ):
        for arm in ("control", "candidate"):
            jobs: list[Config] = []
            inputs: list[dict[str, Any]] = []
            for row in packets:
                context = pydantic_load(SnippetContext, row["context"])
                draft = UnverifiedSnippetDraft(
                    row["draft_id"],
                    context.identifier,
                    row["proposed_code"],
                    row["purpose"],
                    row["source"],
                    row["error"],
                    tuple(row["remaining_goals"]),
                )
                args = dict(
                    role="curator",
                    evidence=json.dumps(
                        dict(
                            status="unverified historical rejection",
                            source_sha=row["cache_sha256"],
                        )
                    ),
                    playbook=book,
                    contexts=[asdict(context)],
                    drafts=[asdict(draft)],
                    receipts=[],
                )
                inputs.append(args)
                jobs.append(
                    make_config(
                        "writer_pilot",
                        arm,
                        "curator",
                        context.theorem_name,
                        args,
                    )
                )
            launch(f"writer_{arm}_{batch_no}_curators", jobs)
            args = handoff(jobs, inputs, book)
            launch(
                f"writer_{arm}_{batch_no}_reducer",
                [
                    make_config(
                        "writer_pilot",
                        arm,
                        "reducer",
                        f"batch{batch_no}",
                        args,
                    )
                ],
            )
    jobs = [
        make_config(
            "reflection_pilot",
            arm,
            "reflector",
            n,
            reflection_args(n, arm == "candidate", n == "amc12_2000_p6"),
        )
        for n in REFLECT_SOURCES
        for arm in ("control", "candidate")
    ]
    random.Random(20260913).shuffle(jobs)
    launch("reflection_pilot", jobs)


def all_configs() -> list[Config]:
    result: dict[str, Config] = {}
    for p in sorted((CAMPAIGN / "manifests").glob("*.json")):
        for r in json.loads(p.read_text()):
            c = Config(**r)
            result[name(c, None)] = c
    return list(result.values())


def gates() -> None:
    review = read("pilot_review.json")
    a = accounting()
    writer: dict[str, Any] = {}
    reflector: dict[str, Any] = {}
    for arm in ("control", "candidate"):
        jobs = [
            c
            for c in all_configs()
            if c.stage == "writer_pilot" and c.arm == arm
        ]
        if len(jobs) != 10:
            raise ValueError("Incomplete writer pilot")
        valid = [c for c in jobs if writer_product(c) is not None]
        useful = set(review["writer"][arm]["useful_source_corrections"])
        cost = sum(a["costs"].get(name(c, None), 0) for c in jobs)
        writer[arm] = dict(
            valid=len(valid),
            reducers=sum(c.role == "reducer" for c in valid),
            useful=len(useful),
            cost=cost,
            cost_per_useful=cost / len(useful) if useful else None,
        )
        rjobs = [
            c
            for c in all_configs()
            if c.stage == "reflection_pilot" and c.arm == arm
        ]
        if len(rjobs) != 8:
            raise ValueError("Incomplete reflector pilot")
        for c in rjobs:
            cell_result(c)
        r = review["reflector"][arm]
        cost = sum(a["costs"].get(name(c, None), 0) for c in rjobs)
        reflector[arm] = dict(
            useful=len(r["useful_sources"]),
            unsupported=len(r["unsupported_sources"]),
            cost=cost,
        )
    x, b = writer["candidate"], writer["control"]
    improvement = (
        x["valid"] > b["valid"]
        or x["useful"] > b["useful"]
        or (
            x["useful"]
            and b["useful"]
            and x["cost_per_useful"] < b["cost_per_useful"]
        )
    )
    advance = (
        x["valid"] >= 9
        and x["reducers"] == 2
        and x["useful"] >= max(1, b["useful"])
        and improvement
    )
    x, b = reflector["candidate"], reflector["control"]
    reflect = (
        x["useful"] > b["useful"]
        and x["unsupported"] <= b["unsupported"]
        and (
            not b["useful"]
            or x["cost"] / x["useful"] <= 1.5 * b["cost"] / b["useful"]
        )
    )
    save(
        "gates.json",
        dict(
            writer=writer,
            reflector=reflector,
            advance_writer=bool(advance),
            include_reflector=bool(reflect),
            review_sha256=sha(CAMPAIGN / "pilot_review.json"),
            default_changed=False,
        ),
    )


def adaptation() -> None:
    if not read("gates.json")["advance_writer"]:
        save(
            "adaptation_stop.json",
            dict(
                reason="Registered writer gate failed; no book/proof promotion"
            ),
        )
        return
    book = Playbook.load(BOOK)
    include = read("gates.json")["include_reflector"]
    names = list(partition("training"))
    for batch_no in range(10):
        batch = names[batch_no * 4 : batch_no * 4 + 4]
        rjobs = [
            make_config(
                "adaptation",
                "candidate" if include else "control",
                "reflector",
                n,
                reflection_args(n, include),
            )
            for n in batch
        ]
        launch(f"adapt_{batch_no}_reflectors", rjobs)
        cjobs: list[Config] = []
        inputs: list[dict[str, Any]] = []
        for rjob in rjobs:
            source = read(f"sources/{rjob.bench_name}.json")
            events = tuple(
                pydantic_load(TrainingEvent, e) for e in source["events"]
            )
            raw = cell_result(rjob)
            evidence = (
                json.dumps(raw["values"][0])
                if raw and raw["success"]
                else "Reflector failed; inspect original training evidence"
            )
            if include and raw and raw["success"]:
                drafts = lesson_draft(
                    pydantic_load(ReflectedLesson, raw["values"][0]), events
                )
            elif events:
                e = next(
                    (e for e in events if e.status != "accepted"), events[-1]
                )
                drafts = (
                    UnverifiedSnippetDraft(
                        "source-" + rjob.bench_name,
                        e.context.identifier,
                        e.submitted,
                        evidence,
                        e.context.source,
                        e.error,
                        e.goals,
                    ),
                )
            else:
                drafts = ()
            if not drafts:
                save(
                    f"skips/adapt_{rjob.bench_name}.json",
                    dict(
                        reason="No proposed source draft",
                        reflector=name(rjob, None),
                    ),
                )
                continue
            bank = {e.context.identifier: e.context for e in events}
            args = dict(
                role="curator",
                evidence=evidence,
                playbook=book.render_prompt(),
                contexts=[asdict(c) for c in bank.values()],
                drafts=[asdict(d) for d in drafts],
                receipts=[],
            )
            inputs.append(args)
            cjobs.append(
                make_config(
                    "adaptation", "candidate", "curator", rjob.bench_name, args
                )
            )
        launch(f"adapt_{batch_no}_curators", cjobs)
        if not cjobs:
            continue
        reducer = make_config(
            "adaptation",
            "candidate",
            "reducer",
            f"batch{batch_no}",
            handoff(cjobs, inputs, book.render_prompt()),
        )
        launch(f"adapt_{batch_no}_reducer", [reducer])
        product = writer_product(reducer)
        if product:
            merged = merge(
                book,
                product.checked.delta.operations,
                (),
                dedup_counts_helpful=False,
                max_tokens=4000,
            )
            book = merged.playbook
            save(
                f"book_steps/{batch_no}.json",
                dict(product=asdict(product), merge=asdict(merged)),
            )
        else:
            save(
                f"book_steps/{batch_no}.json",
                dict(failed_reducer=name(reducer, None), book_unchanged=True),
            )
    path = CAMPAIGN / "book.yaml"
    if path.exists():
        if Playbook.load(path).sha256() != book.sha256():
            raise ValueError("Frozen book drift")
    else:
        book.save(path)
    save(
        "book.json",
        dict(
            sha256=book.sha256(),
            file_sha256=sha(path),
            changed=book.render_prompt()
            != Playbook.load(BOOK).render_prompt(),
            tokens=book.token_estimate(),
        ),
    )


def proof_args(theorem: str, stage: str, arm: str) -> dict[str, Any]:
    book = BOOK if arm == "control" else CAMPAIGN / "book.yaml"
    if arm != "control" and sha(book) != read("book.json")["file_sha256"]:
        raise ValueError("Candidate book changed")
    return dict(
        problem_file=partition(stage)[theorem],
        theorem_name=theorem,
        playbook=Playbook.load(book).render_prompt(),
        claims=[],
        turn_budget=64,
        limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
        verifier_seconds=300,
        admission=False,
        focused=True,
        restart=False,
    )


def training() -> None:
    if not read("book.json")["changed"]:
        save("training_stop.json", dict(reason="No changed book"))
        return
    launch(
        "training",
        [
            make_config(
                "training",
                "candidate",
                "proof",
                n,
                proof_args(n, "training", "candidate"),
            )
            for n in partition("training")
        ],
    )


def validation() -> None:
    if (
        not read("book_review.json")["useful_checked_additions"]
        or not read("training_exposure.json")["new_book_dispatched"]
    ):
        raise ValueError("Book correctness and training exposure required")
    jobs = [
        make_config(
            "validation",
            arm,
            "proof",
            n,
            proof_args(n, "validation", arm),
            seed,
        )
        for seed in (0, 1)
        for n in partition("validation")
        for arm in ("control", "candidate")
    ]
    random.Random(20260914).shuffle(jobs)
    launch("validation", jobs)


def replay() -> None:
    before = accounting()["receipts"]
    checks: list[dict[str, Any]] = []
    for c in all_configs():
        original = cell_result(c)
        if original is None:
            checks.append(dict(cell=name(c, None), platform_failed=True))
            continue
        activate(c.stage, events=False)
        args = c.instantiate(None)
        args.cache_mode, args.cache_file = (
            "replay",
            str(directory(c) / "cache.yaml"),
        )
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("HTTP forbidden"),
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
            raise ValueError("Exact replay mismatch: " + name(c, None))
        checks.append(dict(cell=name(c, None), passed=True))
    assert before == accounting()["receipts"]
    save(
        f"replays/{len(checks)}.json",
        dict(passed=True, paid_calls=0, cells=checks),
    )


if __name__ == "__main__":
    action = sys.argv.pop(1)
    if action == "run-batch":
        run_batch(sys.argv.pop(1))
    else:
        {
            "prepare": prepare,
            "seal": seal,
            "pilots": pilots,
            "gates": gates,
            "adapt": adaptation,
            "training": training,
            "validation": validation,
            "replay": replay,
            "status": lambda: print(json.dumps(accounting(), indent=2)),
        }[action]()
