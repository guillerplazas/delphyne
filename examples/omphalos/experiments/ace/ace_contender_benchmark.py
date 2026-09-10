"""User-authorized comparison of BOTH ACE model contenders, 2026-09-10.

160 fresh cells: trainX/validationX x 40 problems x seed 0 x two contenders.
Reuse 80 existing flagship cells; historical comparison, not concurrent.
Reference: original bounded money+focused. Candidates: Luna-xhigh prover,
medium curator/reducer, audit off, frozen medium/xhigh-reflector books.
No adaptation or interim elimination. Primary: qualified solves <=$0.10;
report total inference cost, cost/solve, paired family 90% intervals and
partition consistency. Two validation-versus-reference accuracy comparisons
use Holm-adjusted p<.10 for statistical support, separately from practical
value. Report any positive coverage gain within the agreed <=1.20 cost
ratio and nonworsening cost/solve, or lower cost with no coverage loss;
no minimum +4-cell gate and no automatic default promotion. Contradictory
partition results and uncertainty remain explicit. No protected outcomes,
additional arms, optional stopping or seeds to chase significance.

This is new authorization, not a rewrite of the previous selection verdict.
Use a $6 subceiling within the original $30; expected additional spend $3-5.
Both harnesses: python -m experiments.ace.ace_contender_benchmark
  prepare | run --max_workers=24 --wait | report | status
"""

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import csv
import json
import os
import random
import sys
from typing import Any, cast
from pathlib import Path
from runtime.model_registry import OmphalosReasoningEffort

import yaml
import delphyne as dp
from delphyne.utils.typing import pydantic_load

from experiments.ace.ace_bounded_experiment import BoundedConfig
from experiments.common import ace_model_campaign as old
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.runtime_profiles import RuntimeProfile
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)

ROOT = old.ROOT
CAMPAIGN = ROOT / "experiments/campaigns/ace_contenders_20260910"
OUTPUT = ROOT / "experiments/output/ace_contenders_20260910"
CEILING = 6.0
ALLOCATIONS = dict(benchmark=5.5, retry=0.5)
ARMS = ("reference", "reflector-medium", "reflector-xhigh")


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: object) -> None:
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    old.write_new(CAMPAIGN / name, value)


@dataclass
class ContenderConfig(BoundedConfig):
    phase: str = "training"

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if asdict(self) not in read("manifest.json"):
            raise ValueError("cell outside frozen authorized benchmark")
        result = super().instantiate(context)
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        return result


def name(c: ContenderConfig, _: object) -> str:
    return f"{c.bench_name}__{c.phase}-{c.arm_label}__{c.model_name}__seed{c.seed}"


def configs() -> list[ContenderConfig]:
    return [pydantic_load(ContenderConfig, c) for c in read("manifest.json")]


def proposed_configs() -> list[ContenderConfig]:
    reg = old.read("registration.json")
    candidates = old.read("selection_report.json")["results"]
    result: list[ContenderConfig] = []
    for phase, problems in (
        ("training", reg["train"]),
        ("validation", reg["validation"]),
    ):
        for bench in problems:
            for seed in (0,):
                for arm, book, effort in (
                    (ARMS[1], candidates[0]["playbook"], "xhigh"),
                    (ARMS[2], candidates[1]["playbook"], "xhigh"),
                ):
                    c = old.proof_config(
                        bench,
                        cast(OmphalosReasoningEffort, effort),
                        book,
                        phase,
                        seed=seed,
                        label=arm,
                    )
                    result.append(pydantic_load(ContenderConfig, asdict(c)))
    random.Random(20260912).shuffle(result)
    return result


def reference_inventory() -> tuple[dict[str, Any], dict[str, str]]:
    """Freeze existing seed-0 controls without choosing by their outcomes."""
    reg = old.read("registration.json")
    train_records = {r.name: r for r in old.cells_of_run(old.OUTPUT / "proof")}
    val_output = ROOT / "experiments/output/ace_polish_validation"
    val_records = {r.name: r for r in old.cells_of_run(val_output)}
    receipt_file = (
        ROOT / "experiments/campaigns/ace_polish_20260909/receipts.csv"
    )
    val_costs: dict[str, float] = defaultdict(float)
    with receipt_file.open() as f:
        for row in csv.DictReader(f):
            if not row["charged"]:
                raise ValueError("unresolved historical reference liability")
            val_costs[row["cell"]] += float(row["charged"])
    train_costs = old.accounting()["costs"]
    result: dict[str, Any] = {}
    hashes = {str(receipt_file.relative_to(ROOT)): old.digest(receipt_file)}
    for phase, panel in (
        ("training", reg["train"]),
        ("validation", reg["validation"]),
    ):
        rows: list[dict[str, Any]] = []
        for bench in panel:
            expected = old.proof_config(
                bench, "medium", reg["incumbent"], phase
            )
            if phase == "training":
                source_phase = (
                    "prover"
                    if bench
                    in reg["panels"]["source"] + reg["panels"]["screen"]
                    else "selection"
                )
                source = old.proof_config(
                    bench, "medium", reg["incumbent"], source_phase
                )
                n = old.proof_name(source, None)
                record, output, costs = (
                    train_records[n],
                    old.OUTPUT / "proof",
                    train_costs,
                )
            else:
                n = f"{bench}__reference-r64__{old.LUNA}__seed0"
                record, output, costs = val_records[n], val_output, val_costs
            actual = pydantic_load(ContenderConfig, record.params)
            a = BoundedConfig.instantiate(actual, None)
            b = BoundedConfig.instantiate(expected, None)
            if actual.admission or actual.polished:
                raise ValueError(
                    "historical control has different proof controls"
                )
            # Both branches that consume claims require admission or polished.
            # The validation archive has a different inactive claim artifact.
            a.args.pop("claims")
            b.args.pop("claims")
            if a != b:
                raise ValueError(
                    f"historical reference policy/prompt mismatch: {n}"
                )
            cost = costs.get(n, 0.0)
            if abs(cost - record.cost) > 1e-7:
                raise ValueError(f"historical receipt/cache mismatch: {n}")
            if record.platform_failed:
                raise ValueError(
                    "historical reference panel contains a platform failure"
                )
            for path in [
                output / "experiment.yaml",
                output / "configs" / n / "result.yaml",
                output / "configs" / n / "cache.yaml",
            ]:
                hashes[str(path.relative_to(ROOT))] = old.digest(path)
            rows.append(
                dict(
                    theorem=bench,
                    seed=0,
                    source=str(output.relative_to(ROOT)),
                    name=n,
                    solved=record.solved,
                    cost=cost,
                    failed=record.platform_failed,
                    effective_config_matches=True,
                )
            )
        result[phase] = rows
    return result, hashes


def prepare() -> None:
    if (CAMPAIGN / "registration.json").exists():
        verify()
        return
    old.verify_hashes(old.execution_hashes())
    previous = old.accounting()
    if previous["unresolved"]:
        raise ValueError("previous campaign charges unresolved")
    spent = sum(previous["costs"].values())
    if spent + CEILING > 30 + 1e-8:
        raise ValueError("combined authorization exceeded")
    cs = proposed_configs()
    assert len(cs) == len({name(c, None) for c in cs}) == 160
    save("manifest.json", [asdict(c) for c in cs])
    references, reference_hashes = reference_inventory()
    save("references.json", references)
    save("runtime.json", old.read("runtime.json"))
    deps = old.source_hashes() | reference_hashes
    deps[str(__file__).removeprefix(str(ROOT) + "/")] = old.digest(
        Path(__file__)
    )
    for path in [
        CAMPAIGN / "manifest.json",
        CAMPAIGN / "references.json",
        CAMPAIGN / "runtime.json",
        old.CAMPAIGN / "selection_report.json",
        old.CAMPAIGN / "final_report.json",
    ]:
        deps[str(path.relative_to(ROOT))] = old.digest(path)
    for c in cs:
        for path in (c.playbook_file, c.problem_file, c.artifact):
            deps[path] = old.digest(ROOT / path)
    save(
        "registration.json",
        dict(
            authorization="Guille explicitly requested full benchmark of BOTH contenders after correcting overly strict pilot gates, 2026-09-10",
            prior_api_spend=spent,
            ceiling=CEILING,
            combined_ceiling=30,
            expected_api_spend=[3, 5],
            allocations=ALLOCATIONS,
            cells=160,
            historical_reference_cells=80,
            arms=ARMS,
            seeds=[0],
            families=old.read("registration.json")["families"],
            dependencies=deps,
            candidates=[
                dict(
                    arm=arm,
                    recipe=x["artifact"]["recipe"],
                    playbook=x["playbook"],
                )
                for arm, x in zip(
                    ARMS[1:], old.read("selection_report.json")["results"]
                )
            ],
            practical_rule="Report positive coverage gain at <=1.20 cost and no worse cost/solve, or lower cost without coverage loss; no fixed minimum solve gain, no automatic promotion",
            statistical_rule="Two primary validation versus-reference coverage comparisons: Holm p<.10; family-clustered 90% descriptive intervals; other comparisons descriptive",
            exposure="TrainX and validationX development data; historical flagship controls; no concurrent randomized or generalization-confirmation claim",
            max_infrastructure_retries=4,
        ),
    )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(CEILING, ALLOCATIONS)


def verify() -> None:
    old.verify_hashes(read("registration.json")["dependencies"])


def accounting() -> dict[str, Any]:
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,usage,cell FROM receipts"
        ).fetchall()
    costs: dict[str, float] = defaultdict(float)
    unresolved: list[str] = []
    for key, model, created, charged, usage, cell in rows:
        if charged is None:
            unresolved.append(key)
            continue
        u = json.loads(usage or "{}")
        if charged or "input_tokens" in u:
            actual = old.price_tokens(
                model,
                u["input_tokens"],
                u.get("input_tokens_details", {}).get("cached_tokens", 0),
                u.get("output_tokens", 0),
                on=datetime.fromtimestamp(created, timezone.utc).date(),
            )
            if abs(actual - charged) > 1e-8:
                raise ValueError("receipt token mismatch")
        costs[cell] += charged
    return dict(
        costs=dict(costs),
        unresolved=unresolved,
        requests=len(rows),
        total=sum(costs.values()),
        ledger=ledger.summary(),
    )


def observations(
    cs: list[ContenderConfig], acct: dict[str, Any]
) -> dict[tuple[str, str], Observation]:
    if acct["unresolved"]:
        raise ValueError("unresolved charges; no verdict")
    records = {r.name: r for r in old.cells_of_run(OUTPUT)}
    result: dict[tuple[str, str], Observation] = {}
    for c in cs:
        n = name(c, None)
        if n not in records:
            raise ValueError(f"missing cell: {n}")
        r = records[n]
        path = OUTPUT / "configs" / n
        for p in path.glob("exception*.txt"):
            if "CampaignExhausted" in p.read_text():
                raise ValueError("administrative censoring; no verdict")
        cost = acct["costs"].get(n, 0)
        prior = sum(
            old.cache_cost(p, c.model_name)
            for p in (path / "attempts").glob("*/cache.yaml")
        )
        if abs(cost - r.cost - prior) > 1e-7:
            raise ValueError(f"receipt/cache mismatch: {n}")
        if r.cell in result:
            raise ValueError("duplicate problem-seed cell")
        for cache in [
            path / "cache.yaml",
            *(path / "attempts").glob("*/cache.yaml"),
        ]:
            if not cache.exists():
                continue
            entries: Any = (
                yaml.load(cache.read_text(), Loader=yaml.CSafeLoader) or []
            )
            for row in entries:
                opts = row["input"]["request"].get("options", {})
                if opts.get("model") in (None, "__compute__"):
                    continue
                if (
                    opts.get("model") != c.model_name
                    or opts.get("reasoning_effort") != c.reasoning_effort
                    or opts.get("max_completion_tokens") != 32768
                ):
                    raise ValueError(f"actual request drift: {n}")
        result[r.cell] = Observation(r.solved, cost, r.platform_failed)
    return result


def holm(ps: list[float]) -> list[float]:
    result = [0.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(sorted(range(len(ps)), key=lambda i: ps[i])):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        result[i] = running
    return result


def report() -> None:
    verify()
    if (CAMPAIGN / "final_report.json").exists():
        print("Benchmark already reported; frozen results retained.")
        return
    acct = accounting()
    cs = configs()
    reports: dict[str, Any] = {}
    reg = read("registration.json")
    for phase in ("training", "validation"):
        arms = {
            arm: observations(
                [c for c in cs if c.phase == phase and c.arm_label == arm],
                acct,
            )
            for arm in ARMS[1:]
        }
        arms[ARMS[0]] = {
            (x["theorem"], "0"): Observation(
                x["solved"], x["cost"], x["failed"]
            )
            for x in read("references.json")[phase]
        }
        metrics = {arm: old.metrics(obs) for arm, obs in arms.items()}
        comparisons: dict[str, Any] = {}
        for arm in ARMS[1:]:
            a, b = arms[ARMS[0]], arms[arm]
            pair = compare(a, b, list(a), families=reg["families"])
            pair.pop("verdict")
            pair["cost_p_two_sided_descriptive"] = cost_cluster_p(
                a, b, list(a), families=reg["families"]
            )
            pair["observed_coverage_gain_with_cost_limits"] = old.eligible(
                metrics[arm], metrics[ARMS[0]], gain=1
            )
            pair["observed_saving_without_coverage_loss"] = (
                metrics[arm]["solves"] >= metrics[ARMS[0]]["solves"]
                and metrics[arm]["cost"] < metrics[ARMS[0]]["cost"]
            )
            comparisons[arm] = pair
        ps = holm([comparisons[arm]["p_two_sided"] for arm in ARMS[1:]])
        if phase == "validation":
            for arm, p in zip(ARMS[1:], ps):
                comparisons[arm]["coverage_p_holm"] = p
                comparisons[arm]["statistical_support_for_coverage_gain"] = (
                    p < 0.10 and comparisons[arm]["effect"] > 0
                )
        reports[phase] = dict(
            metrics=metrics,
            comparisons=comparisons,
            per_seed={
                str(seed): {
                    arm: old.metrics(
                        {k: v for k, v in obs.items() if k[1] == str(seed)}
                    )
                    for arm, obs in arms.items()
                }
                for seed in (0,)
            },
            unique_solved={
                arm: len(
                    {
                        k[0]
                        for k, v in obs.items()
                        if v.solved and not v.failed and v.cost <= 0.1
                    }
                )
                for arm, obs in arms.items()
            },
            reflector_comparison_descriptive=compare(
                arms[ARMS[1]],
                arms[ARMS[2]],
                list(arms[ARMS[1]]),
                families=reg["families"],
            ),
        )
    reports.update(
        accounting=acct,
        combined_api_spend=reg["prior_api_spend"] + acct["total"],
        exposure=reg["exposure"],
        default_changed=False,
    )
    save("final_report.json", reports)
    with (
        Ledger(CAMPAIGN / "ledger.sqlite3").connect() as db,
        (CAMPAIGN / "receipts.csv").open("w") as f,
    ):
        cur = db.execute("SELECT * FROM receipts ORDER BY created,id")
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([d[0] for d in cur.description])
        writer.writerows(cur.fetchall())
    print(json.dumps(reports, indent=2), flush=True)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if command == "prepare":
        prepare()
        return
    if command == "report":
        report()
        return
    if command == "status":
        print(json.dumps(accounting(), indent=2))
        return
    verify()
    if command == "run" and (CAMPAIGN / "final_report.json").exists():
        raise ValueError("completed benchmark; no new calls")
    if any("retry" in a for a in sys.argv):
        raise ValueError(
            "retries require an explicit reviewed infrastructure manifest"
        )
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    Ledger(CAMPAIGN / "ledger.sqlite3").create(CEILING, ALLOCATIONS)
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = "benchmark"
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")
    ol.OmphalosExperiment(
        config_class=ContenderConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs(),
        output_dir=str(OUTPUT.relative_to(ROOT)),
        config_naming=name,
        wait_for_slots=True,
        attempts=1,
    ).run_cli()


if __name__ == "__main__":
    main()
