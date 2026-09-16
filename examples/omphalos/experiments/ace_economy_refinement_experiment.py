"""Independent reset/presentation refinements and a fair ACE factorial.

Authorized September 16, 2026: at most $20 additional inference, within
the original $50 cumulative ceiling. trainX pilots only, validationX
benchmark only. testX and challenge inputs, metadata and caches stay closed.

Pilot: four fixed trainX problems x two agents x baseline/reset/compact,
seed 0 = 24 fresh $.10 cells ($2.40 nominal), with $3 reserved. At most six
targeted correction reruns require a separately frozen amendment; no sweep.
Inspect implementation failures, then freeze the two treatments before any
validation call. Transfer unused pilot allocation to the benchmark.

Benchmark: 40 validation problems x seeds 0/1 x ACE on/off x reset on/off x
compact on/off = 640 fresh cells. Dispatch 20 randomized matched blocks of
two theorems (32 cells, full $3.20 nominal liability must fit before each).
Stop between blocks if another cannot fit; publish the actual denominator
and administrative truncation, never silently call a partial panel complete.
Every run: Luna medium Responses, core tools, frozen v2 book or empty,
$.10, 64 requests, 300 verifier seconds, 32768 output tokens; attempts=1.

Reset: >=8 new groups, >=24000 visible chars, >=8192 chars removed;
last two interaction groups + latest checked proposal; at most two resets,
opaque reasoning cleared. User correction: plain history dropping only;
no handoff, summary, new tool, lookup memory or failure notes for either agent.
Compact: shorter system instructions, unchanged playbook/demo/tool semantics,
4096-byte feedback/tool views, duplicate goals referenced only when their
complete definition remains in visible history. Combined triggers on its
rendered history. No new resources or changes to proof correctness.

Primary outcomes: all-attempt cost, qualified proof coverage, cost/proof.
Report each agent's own reset effect and cost/coverage frontier, matched
ACE comparisons and reset/presentation interactions. Ten percent cost
reduction remains an effect-size target; greater coverage is independently
useful. No per-seed solve veto, p-value acceptance gate or default promotion.
Use paired theorem-family clustered 90% intervals and two-sided p<.10 for
statistical support only, with multiplicity/selection caveats. Failures stay
in denominators; missing/admin-censored cells cannot produce a full verdict.

Both harnesses: prepare; pilot; inspect the pilot report; freeze; benchmark;
report. Run the long stages in tmux with the common supervised launcher.
"""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
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
from experiments import ace_economy_budget_experiment as budget_reference
from experiments import ace_economy_session_experiment as session_reference
from experiments import ace_economy_validation as reference
from experiments.common import omphalos_launch as ol
from experiments.common.ace_learning_io import accounting as ledger_accounting
from runtime.campaign_budget import Ledger
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile

NAME = "ace_economy_refinement_20260916"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
CEILING = 20.0
CAP = 0.10
PILOT_THEOREMS = (
    "imo_1967_p3",
    "aime_1988_p3",
    "mathd_algebra_185",
    "mathd_numbertheory_221",
)
FINAL_BATCHES = tuple(f"final{i:02d}" for i in range(20))
BATCHES = ("pilot", *FINAL_BATCHES)
sha = reference.original.sha


def read(filename: str) -> Any:
    return json.loads((CAMPAIGN / filename).read_text())


def save(filename: str, value: Any) -> None:
    path = CAMPAIGN / filename
    encoded = json.dumps(value, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != encoded:
            raise ValueError("Immutable artifact changed: " + filename)
    else:
        path.write_text(encoded)


def partition(stage: str) -> dict[str, str]:
    if stage not in ("train", "validation"):
        raise ValueError("Only trainX and validationX are authorized")
    rows = [
        line.strip()
        for line in (ROOT / "benchmarks" / f"{stage}X.txt")
        .read_text()
        .splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    problems = {Path(row).stem: row for row in rows}
    if len(rows) != 40 or len(problems) != 40:
        raise ValueError("Expected 40 unique authorized theorems")
    if any(
        Path(row).is_absolute()
        or ".." in Path(row).parts
        or not row.startswith("miniF2F/")
        or not row.endswith(".v")
        for row in rows
    ):
        raise ValueError("Invalid partition path")
    return problems


@dataclass(frozen=True)
class Config:
    batch: str
    stage: str
    ace: bool
    reset: bool
    compact: bool
    bench_name: str
    seed: int

    def __post_init__(self) -> None:
        if self.stage not in ("train", "validation"):
            raise ValueError("Only trainX and validationX are authorized")
        if self.batch not in BATCHES:
            raise ValueError("Unregistered batch")
        pilot = self.batch == "pilot"
        if (
            self.stage != ("train" if pilot else "validation")
            or self.seed not in ((0,) if pilot else (0, 1))
            or (pilot and self.reset and self.compact)
            or (pilot and self.bench_name not in PILOT_THEOREMS)
        ):
            raise ValueError("Unregistered treatment or pilot cell")

    @property
    def arm(self) -> str:
        return (
            ("ace" if self.ace else "agentic")
            + ("_reset" if self.reset else "")
            + ("_compact" if self.compact else "")
        )

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        problems = partition(self.stage)
        if self.bench_name not in problems:
            raise ValueError("Theorem outside authorized partition")
        book = reference.CAMPAIGN / "book.yaml"
        if sha(book) != reference.original.BOOK_SHA:
            raise ValueError("Frozen v2 playbook changed")
        os.environ.update(
            OMPHALOS_CAMPAIGN_CELL=name(self, None),
            OMPHALOS_CAMPAIGN_STAGE=(
                "pilot" if self.batch == "pilot" else "benchmark"
            ),
        )
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args=dict(
                problem_file=problems[self.bench_name],
                theorem_name=self.bench_name,
                playbook=Playbook.load(book).render_prompt()
                if self.ace
                else "",
                claims=[],
                turn_budget=64,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
                verifier_seconds=300,
                admission=False,
                focused=True,
                restart=False,
            ),
            policy="refined_economy_policy",
            policy_args=dict(
                snapshot_directory=str(
                    CAMPAIGN / "transport" / name(self, None)
                ),
                pause_file=str(CAMPAIGN / "PAUSED"),
                reset=self.reset,
                compact=self.compact,
            ),
            budget=dict(price=CAP, num_requests=64, rocq_seconds=300),
        )


def name(config: Config, _: object) -> str:
    return (
        f"{config.stage}__{config.arm}__{config.bench_name}__seed{config.seed}"
    )


def directory(config: Config) -> Path:
    return OUTPUT / config.batch / "configs" / name(config, None)


def configs(batch: str) -> list[Config]:
    if batch not in BATCHES:
        raise ValueError("Unregistered batch")
    return [Config(**v) for v in read(f"manifests/{batch}.json")]


def context() -> dp.ExecutionContext:
    ctx = reference.context()
    return replace(
        ctx, modules=(*ctx.modules, "experiments.economy_refinement.policy")
    )


def accounting() -> dict[str, Any]:
    return ledger_accounting(CAMPAIGN)


def prior_costs() -> dict[str, float]:
    costs: dict[str, float] = {}
    for module in (reference, budget_reference, session_reference):
        account = module.accounting()
        if account["unresolved"] or account["billing_issues"]:
            raise ValueError("Prior billing must be settled")
        costs[module.NAME] = account["total"]
    return costs


def source_paths() -> list[Path]:
    package = ROOT / "experiments/economy_refinement"
    paths = [
        Path(__file__),
        ROOT / "tests/test_economy_refinement.py",
        ROOT / "benchmarks/trainX.txt",
        reference.CAMPAIGN / "validation_seal.json",
        budget_reference.CAMPAIGN / "seal.json",
        session_reference.CAMPAIGN / "seal.json",
        CAMPAIGN / "protocol.json",
        CAMPAIGN / "runtime.json",
    ]
    paths.extend(
        package / filename
        for filename in (
            "__init__.py",
            "rendering.py",
            "window.py",
            "policy.py",
        )
    )
    paths.extend((package / "templates").glob("*.jinja"))
    problems = partition("train")
    paths.extend(ROOT / problems[theorem] for theorem in PILOT_THEOREMS)
    paths.extend(CAMPAIGN / f"manifests/{batch}.json" for batch in BATCHES)
    return sorted(paths)


def prepare() -> None:
    session_reference.verify()
    if (CAMPAIGN / "seal.json").exists():
        verify()
        return
    prior = prior_costs()
    if sum(prior.values()) + CEILING > 50 + 1e-8:
        raise ValueError("New ceiling exceeds cumulative authorization")
    for theorem in PILOT_THEOREMS:
        if theorem not in partition("train"):
            raise ValueError("Pilot outside trainX")
    rng = random.Random(202609165)
    pilot = [
        Config("pilot", "train", ace, reset, compact, theorem, 0)
        for theorem in PILOT_THEOREMS
        for ace in (False, True)
        for reset, compact in ((False, False), (True, False), (False, True))
    ]
    rng.shuffle(pilot)
    save("manifests/pilot.json", [asdict(job) for job in pilot])
    theorems = list(partition("validation"))
    rng.shuffle(theorems)
    for index, batch in enumerate(FINAL_BATCHES):
        jobs = [
            Config(batch, "validation", ace, reset, compact, theorem, seed)
            for theorem in theorems[2 * index : 2 * index + 2]
            for seed in (0, 1)
            for ace in (False, True)
            for reset in (False, True)
            for compact in (False, True)
        ]
        rng.shuffle(jobs)
        save(f"manifests/{batch}.json", [asdict(job) for job in jobs])
    save(
        "protocol.json",
        dict(
            protocol=__doc__,
            created=datetime.now(timezone.utc).isoformat(),
            authorized_partitions=["trainX", "validationX"],
            pilot_cells=24,
            benchmark_cells=640,
            additional_correction_cells=0,
            prior_settled_costs=prior,
            prior_future_paid_calls=0,
            new_ceiling=CEILING,
            combined_ceiling=50,
            book_sha256=reference.original.BOOK_SHA,
            git_head=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            default_promoted=False,
        ),
    )
    save("runtime.json", reference.read("runtime.json"))
    Ledger(CAMPAIGN / "ledger.sqlite3").create(
        CEILING, {"pilot": 3.0, "benchmark": 17.0}
    )
    save(
        "seal.json", {str(p.relative_to(ROOT)): sha(p) for p in source_paths()}
    )


def verify() -> None:
    session_reference.verify()
    sealed = read("seal.json")
    if set(sealed) != {str(p.relative_to(ROOT)) for p in source_paths()}:
        raise ValueError("Unexpected refinement seal path")
    for path, digest in sealed.items():
        if sha(ROOT / path) != digest:
            raise ValueError("Refinement source drift: " + path)
    prior, frozen = prior_costs(), read("protocol.json")["prior_settled_costs"]
    if set(prior) != set(frozen) or any(
        abs(cost - frozen[key]) > 1e-8 for key, cost in prior.items()
    ):
        raise ValueError("Prior campaign spending changed")
    liability = accounting()["ledger"]["liability"]
    if (
        liability > CEILING + 1e-8
        or liability + sum(prior.values()) > 50 + 1e-8
    ):
        raise ValueError("Experiment authorization exceeded")


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
    if any(k in diagnostics for k in ("CampaignExhausted", "CampaignPaused")):
        raise ValueError(
            "Administratively censored cell: " + name(config, None)
        )
    return raw.get("outcome", {}).get("result") if state == "done" else None


def admission(batch: str) -> bool:
    jobs = configs(batch)
    account = accounting()
    if account["unresolved"] or account["billing_issues"]:
        raise ValueError("Resolve billing before another block")
    needed = CAP * sum(
        ol.ground_truth(directory(job)) not in ("done", "failed")
        for job in jobs
    )
    stage = "pilot" if batch == "pilot" else "benchmark"
    # At a block boundary every receipt must be settled, so cost is liability.
    spent = sum(
        cost
        for cell, cost in account["costs"].items()
        if cell.startswith("train__" if stage == "pilot" else "validation__")
    )
    return (
        spent + needed <= account["ledger"]["allocations"][stage] + 1e-8
        and account["ledger"]["liability"] + needed <= CEILING + 1e-8
    )


def launch(batch: str) -> bool:
    jobs = configs(batch)
    verify()
    if (CAMPAIGN / f"batches/{batch}.json").exists():
        return True
    if batch != "pilot" and not (CAMPAIGN / "freeze.json").exists():
        raise ValueError("Inspect pilots and freeze before benchmarking")
    if not admission(batch):
        save(
            "administrative_stop.json",
            dict(
                next_batch=batch,
                reason="Full nominal block does not fit",
                accounting=accounting(),
            ),
        )
        return False
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.ace_economy_refinement_experiment",
            "run-batch",
            batch,
            "run",
            "--max_workers=24",
            "--wait",
        ],
        cwd=ROOT,
        check=False,
    )
    for job in jobs:
        cell_result(job)
    verify()
    save(
        f"batches/{batch}.json",
        dict(
            exit_code=process.returncode,
            states={
                name(job, None): ol.ground_truth(directory(job))
                for job in jobs
            },
        ),
    )
    return True


def run_batch(batch: str) -> None:
    jobs = configs(batch)
    verify()
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher lacks credential")
    if batch != "pilot" and not (CAMPAIGN / "freeze.json").exists():
        raise ValueError("Treatments not frozen")
    if not admission(batch):
        raise ValueError("Full block does not fit")
    activate()
    ol.OmphalosExperiment(
        config_class=Config,
        configs=jobs,
        context=context(),
        output_dir=str((OUTPUT / batch).relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def freeze() -> None:
    verify()
    if (CAMPAIGN / "freeze.json").exists():
        return
    if not (CAMPAIGN / "pilot_review.json").exists():
        raise ValueError("Record the implementation pilot review first")
    if not read("replays/pilot.json")["passed"]:
        raise ValueError("Pilot replay failed")
    for job in configs("pilot"):
        cell_result(job)
    account = accounting()
    if account["unresolved"] or account["billing_issues"]:
        raise ValueError("Pilot billing must settle")
    unused = account["ledger"]["allocations"]["pilot"] - account["total"]
    if unused > 1e-8:
        Ledger(CAMPAIGN / "ledger.sqlite3").transfer(
            "pilot",
            "benchmark",
            unused,
            "Pilot complete; no correction reruns",
        )
    save(
        "freeze.json",
        dict(
            created=datetime.now(timezone.utc).isoformat(),
            source_seal_sha256=sha(CAMPAIGN / "seal.json"),
            pilot_review_sha256=sha(CAMPAIGN / "pilot_review.json"),
            choices="Both independent refinements and their factorial combination",
            benchmark_tuning=False,
            accounting=accounting(),
        ),
    )


def benchmark() -> None:
    verify()
    if not (CAMPAIGN / "freeze.json").exists():
        raise ValueError("Freeze treatments first")
    for batch in FINAL_BATCHES:
        if not launch(batch):
            break
    save(
        "benchmark_finished.json",
        dict(
            complete=all(
                (CAMPAIGN / f"batches/{b}.json").exists()
                for b in FINAL_BATCHES
            ),
            accounting=accounting(),
        ),
    )


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "run-batch":
        selected = sys.argv[2]
        sys.argv = [sys.argv[0], *sys.argv[3:]]
        run_batch(selected)
    elif action == "prepare":
        prepare()
    elif action == "verify":
        verify()
    elif action == "pilot":
        launch("pilot")
    elif action == "freeze":
        freeze()
    elif action == "benchmark":
        benchmark()
    else:
        raise SystemExit(
            "prepare | verify | pilot | freeze | benchmark | run-batch BATCH ..."
        )
