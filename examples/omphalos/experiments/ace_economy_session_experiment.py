"""Complete the matched session-reset comparison, validationX exclusively.

Guille requested non-ACE with the same promising reset on 2026-09-16.
Add exactly 80 empty-book reset cells: the same 40 validationX problems,
replicates 0/1, $.10 allowance, 64 requests, 300 Rocq seconds, Luna medium,
32768 output tokens and 8192-byte displays. Reuse all 80 paid ACE-reset
cells and both original 80-cell no-reset controls. No new ACE run, model,
book, prompt, threshold, output cap, adaptation, seed, retry or default.
The reset retains the last two interaction groups and latest checked
proposal, preserves the complete verified proof prefix and theorem, and
clears discarded reasoning carryover after >=8 groups and >=24000 chars.

Primary comparison: ACE reset versus non-ACE reset. Target remains >=10%
total inference savings with no pooled or per-replicate coverage loss.
Report all-attempt cost, qualified proofs, cost/solve, paired family-
clustered 90% intervals and two-sided p<.10; 80 cells are 40 families.
Secondary comparison: non-ACE reset versus the paid plain non-ACE control.
Its practical gate is no per-seed quality loss and either >=10% saving or
>=2 extra proofs with cost/solve <=1.25x reference. This is exploratory
validation, with historical controls and prior selection of the ACE reset;
no independent confirmation, equivalence claim or automatic promotion.
Keep missing/administratively censored cells from producing a verdict;
include platform failures and unsuccessful attempts in the denominator.

The SAME $50 authorization covers all three economics campaigns. Prior
settled cost is $12.30419518. Main and matched-budget campaigns make no
more paid calls; changes to their accounting abort this follow-up. Reserve
only $8 (80 x $.10) in the new ledger, after checking the combined limit.
Every HTTP upper bound is reserved by the unchanged model/controller.
No extra batch or seed is added to spend the remaining authorization.

Both harnesses: prepare, validation (supervised, in tmux), report, export,
replay. The obsolete mixed-scope verifier is never used. Never touch testX.
"""

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
import csv
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any

import delphyne as dp
import yaml

from experiments import ace_economy_budget_experiment as previous_budget
from experiments import ace_economy_validation as reference
from experiments.common import omphalos_launch as ol
from experiments.common.ace_learning_io import accounting as ledger_accounting
from runtime.campaign_budget import Ledger
from runtime.model_registry import price_tokens
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from tools.reports.ace_economy_results import candidate_interest

NAME = "ace_economy_session_20260916"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
CEILING = 8.0
CAP = 0.10


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    encoded = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != encoded:
            raise ValueError("Immutable session artifact changed: " + name)
    else:
        path.write_text(encoded)


@dataclass(frozen=True)
class Config:
    stage: str
    arm: str
    bench_name: str
    seed: int

    def __post_init__(self) -> None:
        if self.stage != "validation":
            raise ValueError("Only validationX is authorized")
        if self.arm != "agentic_session" or self.seed not in (0, 1):
            raise ValueError("Only the registered non-ACE reset cells")

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        # Reuse the frozen implementation verbatim; remove only the book.
        args = reference.Config(
            "validation", "session", self.bench_name, self.seed
        ).instantiate(context)
        args.args["playbook"] = ""
        args.policy_args.update(
            snapshot_directory=str(CAMPAIGN / "transport" / name(self, None)),
            pause_file=str(CAMPAIGN / "PAUSED"),
        )
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        return args


def name(config: Config, _: object) -> str:
    return f"validation__{config.arm}__{config.bench_name}__seed{config.seed}"


def directory(config: Config) -> Path:
    return OUTPUT / "validation/configs" / name(config, None)


def configs(stage: str) -> list[Config]:
    if stage != "validation":
        raise ValueError("Only validationX is authorized")
    return [Config(**v) for v in read("manifests/validation.json")]


def accounting() -> dict[str, Any]:
    return ledger_accounting(CAMPAIGN)


def prior_costs() -> dict[str, float]:
    result: dict[str, float] = {}
    for module in (reference, previous_budget):
        account = module.accounting()
        if account["unresolved"] or account["billing_issues"]:
            raise ValueError("Prior campaigns must be completely settled")
        if any(not k.startswith("validation__") for k in account["costs"]):
            raise ValueError("Unexpected prior campaign scope")
        result[module.NAME] = account["total"]
    return result


def source_paths() -> list[Path]:
    return [
        Path(__file__),
        ROOT / "tests/test_economy_session.py",
        ROOT / "tools/analysis/replay_economy.py",
        ROOT / "tools/analysis/export_economy_receipts.py",
        ROOT / "tools/analysis/paired_evaluation.py",
        reference.CAMPAIGN / "validation_seal.json",
        previous_budget.CAMPAIGN / "seal.json",
        CAMPAIGN / "protocol.json",
        CAMPAIGN / "runtime.json",
        CAMPAIGN / "manifests/validation.json",
    ]


def prepare() -> None:
    reference.verify()
    previous_budget.verify()
    if (CAMPAIGN / "seal.json").exists():
        verify()
        return
    prior = prior_costs()
    if sum(prior.values()) + CEILING > 50 + 1e-8:
        raise ValueError("Full session panel does not fit the joint $50 limit")
    for batch in reference.BATCHES:
        if not (reference.CAMPAIGN / f"batches/{batch}.json").exists():
            raise ValueError("Main campaign must be complete")
    if not (previous_budget.CAMPAIGN / "batches/validation.json").exists():
        raise ValueError("Matched-budget campaign must be complete")
    jobs = [
        Config("validation", "agentic_session", theorem, seed)
        for seed in (0, 1)
        for theorem in reference.partition()
    ]
    random.Random(202609164).shuffle(jobs)
    save("manifests/validation.json", [asdict(job) for job in jobs])
    save(
        "protocol.json",
        dict(
            protocol=__doc__,
            created=datetime.now(timezone.utc).isoformat(),
            authorized_partition="validationX",
            prior_settled_costs=prior,
            prior_future_paid_calls=0,
            new_ceiling=CEILING,
            combined_ceiling=50,
            new_cells=80,
            reused_ace_reset_cells=80,
            reused_no_reset_controls=160,
            book_sha256=reference.original.BOOK_SHA,
            git_head=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            default_promoted=False,
        ),
    )
    save("runtime.json", reference.read("runtime.json"))
    Ledger(CAMPAIGN / "ledger.sqlite3").create(
        CEILING, {"experiments": CEILING}
    )
    save(
        "seal.json",
        {
            str(p.relative_to(ROOT)): reference.original.sha(p)
            for p in source_paths()
        },
    )


def verify() -> None:
    reference.verify()
    previous_budget.verify()
    sealed = read("seal.json")
    if set(sealed) != {str(p.relative_to(ROOT)) for p in source_paths()}:
        raise ValueError("Unexpected path in session campaign seal")
    for path, digest in sealed.items():
        if reference.original.sha(ROOT / path) != digest:
            raise ValueError("Session campaign source drift: " + path)
    prior = prior_costs()
    frozen = read("protocol.json")["prior_settled_costs"]
    if set(prior) != set(frozen) or any(
        abs(cost - frozen[key]) > 1e-8 for key, cost in prior.items()
    ):
        raise ValueError("Prior campaign spending changed after reservation")
    if sum(prior.values()) + accounting()["ledger"]["liability"] > 50 + 1e-8:
        raise ValueError("Combined campaign authorization exceeded")


def activate(*, events: bool = True) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ.update(
        OMPHALOS_CAMPAIGN_LEDGER=str(CAMPAIGN / "ledger.sqlite3"),
        OMPHALOS_CAMPAIGN_STAGE="experiments",
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
        raise ValueError(
            "Missing required session cell: " + name(config, None)
        )
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
        raise ValueError("Administratively censored session cell")
    return raw.get("outcome", {}).get("result") if state == "done" else None


def launch(stage: str) -> None:
    jobs = configs(stage)  # Reject a forbidden stage before any other I/O.
    verify()
    if (CAMPAIGN / "batches/validation.json").exists():
        return
    account = accounting()
    needed = CAP * sum(
        ol.ground_truth(directory(job)) not in ("done", "failed")
        for job in jobs
    )
    if (
        account["unresolved"]
        or account["billing_issues"]
        or account["ledger"]["liability"] + needed > CEILING + 1e-8
    ):
        raise ValueError("The full session batch must fit before dispatch")
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.ace_economy_session_experiment",
            "run-batch",
            "validation",
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
        "batches/validation.json",
        dict(
            exit_code=process.returncode,
            states={
                name(job, None): ol.ground_truth(directory(job))
                for job in jobs
            },
        ),
    )


def run_batch(stage: str) -> None:
    jobs = configs(stage)
    verify()
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher lacks credential")
    activate()
    ol.OmphalosExperiment(
        config_class=Config,
        configs=jobs,
        context=reference.context(),
        output_dir=str((OUTPUT / "validation").relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def report() -> dict[str, Any]:
    verify()
    own, previous = accounting(), reference.accounting()
    if own["unresolved"] or own["billing_issues"]:
        raise ValueError("All session billing must settle before a verdict")
    rows: list[dict[str, Any]] = []
    observations: dict[str, dict[tuple[str, str], Observation]] = {}
    groups = {"agentic": "agentic", "ace": "ace", "ace_session": "session"}
    groups["agentic_session"] = "agentic_session"
    expected = [(n, str(s)) for n in reference.partition() for s in (0, 1)]
    families = reference.original.families("validation")
    for arm, original_arm in groups.items():
        values: dict[tuple[str, str], Observation] = {}
        for theorem, seed in expected:
            if arm == "agentic_session":
                job = Config("validation", arm, theorem, int(seed))
                result, ident, account = cell_result(job), name(job, None), own
            else:
                old = reference.Config(
                    "validation", original_arm, theorem, int(seed)
                )
                result, ident, account = (
                    reference.cell_result(old),
                    reference.name(old, None),
                    previous,
                )
            cost = account["costs"].get(ident, 0)
            solved = bool(result and result["success"])
            values[(theorem, seed)] = Observation(solved, cost, result is None)
            tokens = account["tokens"].get(
                ident, dict(input=0, cached=0, output=0)
            )
            rows.append(
                dict(
                    arm=arm,
                    cell=ident,
                    theorem=theorem,
                    seed=int(seed),
                    solved=solved,
                    qualified=solved and cost <= CAP + 1e-12,
                    failed=result is None,
                    cost=cost,
                    **tokens,
                    uncached_cost=price_tokens(
                        "gpt-5.6-luna",
                        tokens["input"],
                        0,
                        tokens["output"],
                        on=date(2026, 9, 16),
                    ),
                )
            )
        observations[arm] = values
    own_ids = {r["cell"] for r in rows if r["arm"] == "agentic_session"}
    if (
        set(own["costs"]) - own_ids
        or abs(
            sum(r["cost"] for r in rows if r["arm"] == "agentic_session")
            - own["total"]
        )
        > 1e-8
    ):
        raise ValueError("Every new receipt must belong to the full panel")

    def pair(a: str, b: str, seed: str | None = None) -> dict[str, Any]:
        keys = [k for k in expected if seed is None or k[1] == seed]
        left = {k: v for k, v in observations[a].items() if k in keys}
        right = {k: v for k, v in observations[b].items() if k in keys}
        result = compare(
            left, right, keys, families=families, cap_a=CAP, cap_b=CAP
        )
        if not result["complete"]:
            raise ValueError("A matched cell is missing")
        result.update(
            reference=a,
            candidate=b,
            cost_p_two_sided=cost_cluster_p(left, right, keys, families),
            cost_per_solve_a=result["cost_a"] / result["solved_a"]
            if result["solved_a"]
            else None,
            cost_per_solve_b=result["cost_b"] / result["solved_b"]
            if result["solved_b"]
            else None,
            observed_ten_percent_target=result["solved_b"]
            >= result["solved_a"]
            and result["cost_ratio"] <= 0.9,
        )
        if seed is None:
            seeds = [pair(a, b, str(s)) for s in (0, 1)]
            result["per_seed"] = seeds
            result["practical_interest"] = candidate_interest(result, seeds)
            result["observed_ten_percent_target"] = result[
                "observed_ten_percent_target"
            ] and all(r["solved_b"] >= r["solved_a"] for r in seeds)
        return result

    totals: dict[str, Any] = {}
    for arm in groups:
        selected = [r for r in rows if r["arm"] == arm]
        totals[arm] = {
            k: sum(r[k] for r in selected)
            for k in (
                "qualified",
                "failed",
                "cost",
                "input",
                "cached",
                "output",
                "uncached_cost",
            )
        }
        totals[arm]["cells"] = len(selected)
        totals[arm]["cost_per_solve"] = (
            totals[arm]["cost"] / totals[arm]["qualified"]
            if totals[arm]["qualified"]
            else None
        )
    result = dict(
        authorized_partition="validationX",
        totals=totals,
        primary_ace_with_reset=pair("agentic_session", "ace_session"),
        secondary_non_ace_reset_effect=pair("agentic", "agentic_session"),
        historical_ace_reset_effect=pair("ace", "ace_session"),
        new_spend=own["total"],
        prior_spend=sum(prior_costs().values()),
        combined_spend=own["total"] + sum(prior_costs().values()),
        new_cells=80,
        reused_cells=240,
        default_promoted=False,
        limitations="Reused validation and historical controls; primary attribution and secondary control effect are separate questions. Secondary p-values exploratory. Observed equality does not establish equivalence.",
    )
    save("results.json", result)
    with (CAMPAIGN / "cells.csv").open("w") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    return result


def main() -> None:
    action = sys.argv.pop(1) if len(sys.argv) > 1 else ""
    if action == "prepare":
        prepare()
    elif action == "validation":
        launch("validation")
    elif action == "run-batch":
        run_batch(sys.argv.pop(1))
    elif action == "report":
        print(json.dumps(report(), indent=2))
    elif action == "export":
        from tools.analysis.export_economy_receipts import export

        export(sys.modules[__name__], ("validation",))
    elif action == "replay":
        from tools.analysis.replay_economy import assemble, replay_batch

        module = sys.modules[__name__]
        replay_batch(module, "validation")
        assemble(module)
    else:
        raise SystemExit("prepare | validation | report | export | replay")


if __name__ == "__main__":
    main()
