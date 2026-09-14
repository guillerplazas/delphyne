"""Approved resource-completion campaign: at most $30, two isolated arms.

A: response cap 4096 instead of 32768. B: existing structured continuation
with final-message v2; cap 32768. Same Luna-medium flagship/book/budgets.
Each arm gets 40 trainX seed-0 cells; correctness and actual exposure alone
gate its 40 validationX seed-0 cells. Reuse 80 historical reference cells.
One validation winner may receive seed 1 (40 cells) plus a fresh matched
seed-1 reference (40). Maximum 240 first-pass cells; allocations 8+8+8+6.
All writing/adaptation/embedding/teacher/paid-diagnostic counts are zero.

Follow-up: >=1 additional solve at <=1.25 cost, OR >=10% savings with <=1
fewer solve. Rank coverage, cost/solve, total cost, then A. Final opt-in
retention: scaled 80-cell gate and fresh seed 1 not worse in both coverage
and cost. No default promotion or significance chasing. Family-clustered
two-sided p<.10 / 90% intervals; Holm-adjust initial contender claims.
Failures remain in the denominator; missing/admin-censored cells and unknown
costs block verdicts. The campaign does not autonomously retry failed cells.

Both harnesses: prepare | preflight | seal | campaign | report | status
Internal supervised batch entry: run-batch KEY run --max_workers=24 --wait.
The source seal must be fixed before payment. No testX/protected data access.
"""

# ruff: noqa: E402 -- the scope guard precedes experiment imports
from runtime.completion_scope import install

install()

from collections import defaultdict
from contextlib import redirect_stdout
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import csv
import fcntl
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
import yaml
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command

from ace.ace_playbook import Playbook
from experiments.ace import ace_attribution_experiment as baseline
from experiments.coverage_cycle_experiment import partition, family_map
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.model_registry import price_tokens, pricing_for
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile
from tools.analysis.cell_records import cells_of_run
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from tools.reports.ace_attribution_report import args_of, cache_diagnosis

CAMPAIGN = ROOT / "experiments/campaigns/resource_completion_20260913"
OUTPUT = ROOT / "experiments/output/resource_completion_20260913"
ALLOCATIONS = dict(training=8.0, validation=8.0, followup=8.0, contingency=6.0)
ARMS = ("A", "B")
BOOK = baseline.BOOK
BOOK_SHA = baseline.BOOK_SHA


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != content:
            raise ValueError(f"Immutable campaign artifact changed: {name}")
    else:
        with path.open("x") as f:
            f.write(content)


def context() -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    return replace(
        ctx,
        modules=(*ctx.modules, "prove_resource_completion", "prove_evidence"),
    )


@dataclass
class ProofConfig:
    bench_name: str
    stage: str
    arm: str
    seed: int = 0

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if self.stage not in ("training", "validation", "followup"):
            raise ValueError("Unregistered stage")
        part = "training" if self.stage == "training" else "validation"
        if (
            self.bench_name not in partition(part)
            or self.arm not in (*ARMS, "reference")
            or self.seed != (1 if self.stage == "followup" else 0)
            or self.arm == "reference"
            and self.stage != "followup"
        ):
            raise ValueError("Unregistered problem/arm/seed")
        if self.stage == "followup" and self.arm not in (
            read("selection.json")["winner"],
            "reference",
        ):
            raise ValueError("Only the selected arm may receive follow-up")
        args = baseline.proof(part, "luna-ace", self.bench_name).instantiate(
            None
        )
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        args.policy = "completion_policy"
        args.policy_args = dict(
            arm=self.arm,
            snapshot_directory=str(CAMPAIGN / "transport" / name(self, None)),
        )
        if self.arm == "B":
            args.args["continuation"] = True
        return args


def name(cfg: ProofConfig, _: object) -> str:
    return f"{cfg.bench_name}__{cfg.stage}-{cfg.arm}__gpt-5.6-luna__seed{cfg.seed}"


def run_dir(stage: str, arm: str) -> Path:
    return OUTPUT / stage if stage == "followup" else OUTPUT / stage / arm


def batch_configs(key: str) -> list[ProofConfig]:
    return [ProofConfig(**r) for r in read(f"manifests/{key}.json")]


def accounting() -> dict[str, Any]:
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    costs: dict[str, float] = defaultdict(float)
    tokens: dict[str, dict[str, int]] = defaultdict(
        lambda: dict(input=0, cached=0, output=0)
    )
    unresolved: list[str] = []
    billing_issues: list[str] = []
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
            billing_issues.append(ident)
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
                raise ValueError(f"Receipt tariff mismatch: {ident}")
            for key, value in (
                ("input", inp),
                ("cached", cached),
                ("output", out),
            ):
                tokens[cell][key] += value
        costs[cell] += charged
    return dict(
        total=sum(costs.values()),
        costs=dict(costs),
        tokens=dict(tokens),
        receipts=len(rows),
        unresolved=unresolved,
        billing_issues=billing_issues,
        ledger=ledger.summary(),
        codex_session_cost=None,
        codex_session_cost_note="Unavailable through the experimental ledger",
    )


def activate(stage: str, events: bool = True) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = stage
    os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )
    else:
        os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)


def prepare() -> None:
    refs = baseline.read("references.json")
    for stage, rows in refs.items():
        if len(rows) != 40 or {r["theorem"] for r in rows} != set(
            partition(stage)
        ):
            raise ValueError("Incomplete historical reference panel")
    if Playbook.load(ROOT / BOOK).sha256() != BOOK_SHA:
        raise ValueError("Frozen playbook drift")
    save("references.json", refs)
    save(
        "runtime.json",
        json.loads(
            (
                ROOT
                / ("experiments/campaigns/ace_capacity_20260912/runtime.json")
            ).read_text()
        ),
    )
    save(
        "protocol.json",
        dict(
            authorization="Guille: Implement the plan; 2026-09-13",
            ceiling=30,
            allocations=ALLOCATIONS,
            arms=list(ARMS),
            max_first_pass_cells=240,
            max_infrastructure_extra_attempts=4,
            automatic_retries=False,
            new_adaptation_calls=0,
            new_embeddings=0,
            new_paid_diagnostics=0,
            reused_seed0_controls=80,
            families=family_map(),
            book=BOOK,
            book_sha256=BOOK_SHA,
            alpha=0.10,
            confidence=0.90,
            default_changed=False,
            training_gate="correctness and actual exposure; no effect-size/p gate",
            followup_gate="gain >=1 at cost ratio <=1.25 OR loss <=1 and ratio <=0.90",
            final_gate="scaled 80-cell gate and seed1 not worse in both cost and coverage",
            selection="qualified coverage, cost/solve, total cost, then A",
            prices=asdict(pricing_for("gpt-5.6-luna")),
            price_date=datetime.now(timezone.utc).date().isoformat(),
            validation_status="repeatedly reused development data",
        ),
    )
    for stage in ("training", "validation"):
        for arm in ARMS:
            save(
                f"manifests/{stage}_{arm}.json",
                [asdict(ProofConfig(n, stage, arm)) for n in partition(stage)],
            )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(30, ALLOCATIONS)


def preflight() -> None:
    if accounting()["receipts"]:
        raise ValueError("Preflight must precede all payment")
    activate("training", events=False)
    rows: list[dict[str, Any]] = []
    original = baseline.read("preflight.json")["cells"]
    for ref in original:
        args = baseline.proof(
            ref["partition"], "luna-ace", ref["theorem"]
        ).instantiate(None)
        directory = ROOT / ref["source"] / "configs" / ref["name"]
        archived = args_of(directory)
        expected_args = dict(archived["args"])
        # Existing compatibility contract: unused advice is never queried.
        if expected_args.get("admission") is not False:
            raise ValueError(
                "Historical advice admission unexpectedly enabled"
            )
        expected_args["claims"] = []
        for key in (
            "polished",
            "resource_recovery",
            "matched_advice",
            "output_recovery",
        ):
            if expected_args.get(key) is False:
                expected_args.pop(key)
        if (
            expected_args != args.args
            or archived["budget"] != args.budget
            or archived["policy"] != args.policy
            or archived["policy_args"] != args.policy_args
            or archived["strategy"] != args.strategy
        ):
            raise ValueError(
                f"Reference configuration mismatch: {ref['name']}"
            )
        args.cache_mode = "replay"
        args.cache_file = str(directory / "cache.yaml")
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        args.budget["num_requests"] = ref["requests"]
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "0"
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Preflight forbids HTTP"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(context(), cache_root=Path("/")),
                add_header=False,
            )
        result = out.result
        if (
            result is None
            or result.success != ref["success"]
            or (
                result.spent_budget.get("num_completions", 0)
                != ref["requests"]
            )
        ):
            raise ValueError((ref["name"], out.diagnostics))
        rows.append(
            dict(
                name=ref["name"],
                partition=ref["partition"],
                requests=ref["requests"],
                success=result.success,
                cache_sha256=digest(directory / "cache.yaml"),
                result_sha256=digest(directory / "result.yaml"),
            )
        )
        if len(rows) % 20 == 0:
            print(f"Reference replay {len(rows)}/80", flush=True)
    if len(rows) != 80 or accounting()["receipts"]:
        raise ValueError("Preflight count/accounting mismatch")
    save(
        "preflight.json",
        dict(
            passed=True,
            cells=rows,
            paid_requests=0,
            limitation="Observed-request replay; no claim of exact historical terminal admission",
        ),
    )


def reference_tokens() -> None:
    """Scoped tariff/cache sensitivity, never an admission counterfactual."""
    if accounting()["receipts"]:
        raise ValueError("Reference token registration precedes payment")
    panels: dict[str, Any] = {}
    for stage in ("training", "validation"):
        cells: dict[str, Any] = {}
        for ref in read("references.json")[stage]:
            path = (
                ROOT / ref["source"] / "configs" / ref["name"] / "cache.yaml"
            )
            entries: list[dict[str, Any]] = yaml.load(
                path.read_text(), Loader=yaml.CSafeLoader
            )
            tokens = dict(input=0, cached=0, output=0)
            for entry in entries:
                if (
                    entry["input"]["request"]["options"].get("model")
                    == "__compute__"
                ):
                    continue
                response: dict[str, Any] = entry.get("output") or {}
                usage = response.get("budget", {}).get("values", {})
                for target, source in (
                    ("input", "input_tokens"),
                    ("cached", "cached_input_tokens"),
                    ("output", "output_tokens"),
                ):
                    tokens[target] += usage.get(source, 0)
            cells[ref["theorem"]] = tokens
        panels[stage] = cells
    save("reference_tokens.json", panels)


def token_summary(cells: list[dict[str, int]]) -> dict[str, Any]:
    totals = {
        key: sum(c.get(key, 0) for c in cells)
        for key in ("input", "cached", "output")
    }
    totals_cost = price_tokens(
        "gpt-5.6-luna", totals["input"], totals["cached"], totals["output"]
    )
    uncached = price_tokens(
        "gpt-5.6-luna", totals["input"], 0, totals["output"]
    )
    return dict(
        **totals,
        dated_tariff_cost=totals_cost,
        no_cache_cost=uncached,
        cache_fraction=totals["cached"] / totals["input"]
        if totals["input"]
        else 0,
    )


def seal() -> None:
    if accounting()["receipts"] or not read("preflight.json")["passed"]:
        raise ValueError("Seal requires free successful preflight")
    if not read("offline_evidence.json")["passed"]:
        raise ValueError("Offline evidence checks must pass")
    paths = {Path(__file__), ROOT / "delphyne.yaml", ROOT / BOOK}
    for folder, pattern in (
        ("runtime", "*.py"),
        ("ace", "*.py"),
        ("prompts", "*.jinja"),
    ):
        paths.update((ROOT / folder).rglob(pattern))
    paths.update(ROOT.glob("prove*.py"))
    paths.update(context().demo_files)
    paths.update(
        ROOT / p
        for p in (
            "experiments/ace/ace_adaptation.py",
            "experiments/ace/ace_attribution_experiment.py",
            "experiments/coverage_cycle_experiment.py",
            "experiments/common/omphalos_launch.py",
            "experiments/common/ace_pools.py",
            "experiments/common/miniF2F_bench.py",
            "tools/analysis/paired_evaluation.py",
            "tools/analysis/cell_records.py",
            "tools/reports/ace_attribution_report.py",
            "tools/reports/resource_completion_evidence.py",
            "tests/test_resource_completion.py",
            "tests/test_terminal_evidence.py",
        )
    )
    for part in ("training", "validation"):
        paths.add(
            ROOT
            / "benchmarks"
            / ("trainX.txt" if part == "training" else "validationX.txt")
        )
        paths.update(ROOT / p for p in partition(part).values())
        for ref in read("references.json")[part]:
            directory = ROOT / ref["source"] / "configs" / ref["name"]
            paths.update(directory / f for f in ("cache.yaml", "result.yaml"))
    paths.update(
        CAMPAIGN / p
        for p in (
            "protocol.json",
            "runtime.json",
            "references.json",
            "preflight.json",
            "offline_evidence.json",
            "tests_preflight.log",
            "typecheck_preflight.log",
            "README.md",
            "reference_tokens.json",
        )
    )
    paths.update((CAMPAIGN / "manifests").glob("*.json"))
    save(
        "seal.json",
        {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)},
    )


def verify() -> None:
    if asdict(pricing_for("gpt-5.6-luna")) != read("protocol.json")["prices"]:
        raise ValueError("Registered tariff changed")
    for path, expected in read("seal.json").items():
        if digest(ROOT / path) != expected:
            raise ValueError(f"Sealed source drift: {path}")


def practical(comparison: dict[str, Any], scale: int = 1) -> bool:
    if not comparison.get("complete"):
        return False
    gain = comparison["solved_b"] - comparison["solved_a"]
    ratio = comparison["cost_ratio"]
    return ratio is not None and (
        gain >= scale
        and ratio <= 1.25 + 1e-12
        or gain >= -scale
        and ratio <= 0.90 + 1e-12
    )


def exposure(cell: str) -> dict[str, Any]:
    events = CAMPAIGN / "events.jsonl"
    estimate: dict[str, Any] = {}
    admission: dict[str, Any] = {}
    dispatched: dict[str, Any] | None = None
    requests: list[dict[str, Any]] = []
    computes = 0
    lines: list[str] = (
        events.read_text().splitlines() if events.exists() else []
    )
    for line in lines:
        row = json.loads(line)
        if row.get("cell") != cell:
            continue
        kind, decision = row["kind"], row["decision"]
        if kind == "estimate_v2":
            estimate = row
        elif kind == "admission_v2":
            admission = row
        elif kind == "model" and decision == "invoked":
            dispatched = dict(
                receipt=row["receipt"],
                structured=estimate.get("structured", False),
                output_limit=row["output_limit"],
                proof_checked=False,
                shadow_denied=(
                    admission.get("admitted", False)
                    and estimate.get("shadow_price_32768", 0)
                    > admission.get("remaining", {}).get("price", float("inf"))
                    + 1e-12
                ),
            )
            requests.append(dispatched)
        elif kind == "compute" and decision == "invoked":
            computes += 1
            if (
                dispatched is not None
                and row.get("function") == "checked_proof"
            ):
                dispatched["proof_checked"] = True
        elif (
            kind == "model"
            and decision == "settled"
            and dispatched is not None
        ):
            dispatched["truncated"] = row["truncated"]
    return dict(
        paid_dispatches=requests,
        actual_computations=computes,
        A=any(r["shadow_denied"] and r["proof_checked"] for r in requests),
        B=any(r["structured"] and r["proof_checked"] for r in requests),
        newly_admitted_requests=sum(r["shadow_denied"] for r in requests),
        truncated_responses=sum(r.get("truncated", False) for r in requests),
    )


def observations(
    key: str,
) -> tuple[dict[tuple[str, str], Observation], dict[str, Any]]:
    configs = batch_configs(key)
    acct = accounting()
    if acct["unresolved"] or acct["billing_issues"]:
        raise ValueError("Unresolved required costs; no verdict")
    directory = run_dir(configs[0].stage, configs[0].arm)
    records = {r.name: r for r in cells_of_run(directory)}
    obs: dict[tuple[str, str], Observation] = {}
    diagnostics: dict[str, Any] = {}
    for cfg in configs:
        cell = name(cfg, None)
        if cell not in records:
            raise ValueError(f"Missing required cell: {cell}")
        record = records[cell]
        source = directory / "configs" / cell
        for p in source.glob("exception*.txt"):
            if "CampaignExhausted" in p.read_text():
                raise ValueError("Administrative censoring; no verdict")
        cost = acct["costs"].get(cell, 0.0)
        if not record.platform_failed and abs(record.cost - cost) > 1e-7:
            raise ValueError(f"Cache/receipt cost mismatch: {cell}")
        # Follow-up contains two arms; caller splits it before comparing.
        obs[(cfg.bench_name, cfg.arm if cfg.stage == "followup" else "0")] = (
            Observation(record.solved, cost, record.platform_failed)
        )
        diagnostics[cell] = dict(
            source=str(source.relative_to(ROOT)),
            observation=asdict(
                obs[
                    (
                        cfg.bench_name,
                        cfg.arm if cfg.stage == "followup" else "0",
                    )
                ]
            ),
            tokens=acct["tokens"].get(cell, {}),
            exposure=exposure(cell),
            cache=cache_diagnosis(source),
        )
    return obs, diagnostics


def comparison(
    a: dict[tuple[str, str], Observation],
    b: dict[tuple[str, str], Observation],
) -> dict[str, Any]:
    families = read("protocol.json")["families"]
    expected = sorted(a)
    result = compare(a, b, expected, families=families)
    if not result["complete"]:
        raise ValueError("Incomplete comparison")
    result["cost_p_two_sided"] = cost_cluster_p(a, b, expected, families)
    for arm in ("a", "b"):
        solved = result[f"solved_{arm}"]
        result[f"cost_per_solve_{arm}"] = (
            result[f"cost_{arm}"] / solved if solved else None
        )
    result["practical_followup_gate"] = practical(
        result, 2 if len(expected) == 80 else 1
    )
    return result


def historical(stage: str) -> dict[tuple[str, str], Observation]:
    return {
        (r["theorem"], "0"): Observation(r["solved"], r["cost"], r["failed"])
        for r in read("references.json")[stage]
    }


def report_batch(key: str) -> dict[str, Any]:
    path = CAMPAIGN / f"reports/{key}.json"
    if path.exists():
        return read(f"reports/{key}.json")
    configs = batch_configs(key)
    obs, diagnostics = observations(key)
    stage, arm = configs[0].stage, configs[0].arm
    result: dict[str, Any]
    if stage == "followup":
        winner = read("selection.json")["winner"]
        a = {(n, "1"): o for (n, ar), o in obs.items() if ar == "reference"}
        b = {(n, "1"): o for (n, ar), o in obs.items() if ar == winner}
        result = dict(fresh_seed1=comparison(a, b))
        old_b, _ = observations(f"validation_{winner}")
        result["combined"] = comparison(
            historical("validation") | a, old_b | b
        )
        fresh = result["fresh_seed1"]
        dominated = (
            fresh["solved_b"] < fresh["solved_a"]
            and fresh["cost_b"] > fresh["cost_a"]
        )
        result["retain_opt_in"] = (
            practical(result["combined"], 2) and not dominated
        )
    else:
        result = comparison(historical(stage), obs)
        result["exposed_cells"] = sum(
            d["exposure"][arm] for d in diagnostics.values()
        )
        result["eligible_validation"] = result["exposed_cells"] > 0
    result["default_changed"] = False
    result["data_status"] = (
        "Repeatedly reused development data; historical seed-0 controls"
    )
    save(f"diagnostics/{key}.json", diagnostics)
    save(f"reports/{key}.json", result)
    return result


def select() -> str | None:
    if (CAMPAIGN / "selection.json").exists():
        return read("selection.json")["winner"]
    reports = {
        arm: report_batch(f"validation_{arm}")
        for arm in ARMS
        if report_batch(f"training_{arm}")["eligible_validation"]
    }
    eligible = [arm for arm, r in reports.items() if practical(r)]
    eligible.sort(
        key=lambda arm: (
            -reports[arm]["solved_b"],
            reports[arm]["cost_per_solve_b"]
            if reports[arm]["cost_per_solve_b"] is not None
            else float("inf"),
            reports[arm]["cost_b"],
            arm,
        )
    )
    winner = eligible[0] if eligible else None
    # Two hypotheses remain the family even if one lacks exposure.
    ranked = sorted(
        (reports.get(a, {}).get("p_two_sided", 1.0), a) for a in ARMS
    )
    adjusted: dict[str, float] = {}
    prior = 0.0
    for index, (p, arm) in enumerate(ranked):
        prior = max(prior, min(1.0, (2 - index) * p))
        adjusted[arm] = prior
    save(
        "selection.json",
        dict(
            winner=winner,
            eligible=eligible,
            coverage_p_holm=adjusted,
            reason="Registered practical gate; no p-value selection threshold",
        ),
    )
    return winner


def export_receipts(label: str) -> None:
    path = CAMPAIGN / f"receipts_{label}.csv"
    with Ledger(CAMPAIGN / "ledger.sqlite3").connect() as db:
        cursor = db.execute("SELECT * FROM receipts ORDER BY created,id")
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow([d[0] for d in cursor.description])
        writer.writerows(cursor)
    if path.exists() and path.read_text() != buf.getvalue():
        raise ValueError("Receipt snapshot changed")
    if not path.exists():
        path.write_text(buf.getvalue())


def replay_batch(key: str) -> None:
    """Replay new transport state and the terminal controller without HTTP."""
    artifact = f"replays/{key}.json"
    if (CAMPAIGN / artifact).exists():
        return
    before = accounting()["receipts"]
    configs = batch_configs(key)
    activate(configs[0].stage, events=False)
    rows: list[dict[str, Any]] = []
    for cfg in configs:
        directory = run_dir(cfg.stage, cfg.arm) / "configs" / name(cfg, None)
        if ol.ground_truth(directory) == "failed":
            rows.append(
                dict(
                    cell=name(cfg, None),
                    platform_failed=True,
                    replay="not applicable; kept in denominator",
                )
            )
            continue
        raw: dict[str, Any] = yaml.load(
            (directory / "result.yaml").read_text(), Loader=yaml.CSafeLoader
        )
        original = raw["outcome"]["result"]
        args = cfg.instantiate(None)
        args.cache_mode = "replay"
        args.cache_file = str(directory / "cache.yaml")
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
            replay = run_command(
                run_strategy,
                args,
                ctx=replace(context(), cache_root=Path("/")),
                add_header=False,
            )
        if replay.result is None or (
            replay.result.success != original["success"]
            or replay.result.spent_budget != original["spent_budget"]
            or list(replay.result.values) != original["values"]
        ):
            raise ValueError(
                f"New transport/controller replay mismatch: {name(cfg, None)}"
            )
        rows.append(
            dict(
                cell=name(cfg, None),
                success=replay.result.success,
                spent_budget=dict(replay.result.spent_budget),
                cache_sha256=digest(directory / "cache.yaml"),
            )
        )
    if accounting()["receipts"] != before:
        raise ValueError("Replay incurred new receipts")
    save(artifact, dict(passed=True, paid_requests=0, cells=rows))


def launch(key: str) -> None:
    verify()
    if (CAMPAIGN / f"batches/{key}.complete.json").exists():
        return
    configs = batch_configs(key)
    stage = configs[0].stage
    acct = accounting()
    if acct["unresolved"] or acct["billing_issues"]:
        raise ValueError("Unresolved liability before stage")
    directory = run_dir(stage, configs[0].arm)
    remaining = sum(
        ol.ground_truth(directory / "configs" / name(c, None))
        not in ("done", "failed")
        for c in configs
    )
    own_used = sum(
        g["dollars"] for g in acct["ledger"]["groups"] if g["stage"] == stage
    )
    if own_used + remaining * 0.10 > ALLOCATIONS[stage] + 1e-8:
        raise ValueError("Complete remaining batch liability does not fit")
    command = [
        sys.executable,
        "-m",
        "experiments.resource_completion_experiment",
        "run-batch",
        key,
        "run",
        "--max_workers=24",
        "--wait",
    ]
    result = subprocess.run(command, cwd=ROOT, check=False)
    statuses = {
        name(c, None): ol.ground_truth(directory / "configs" / name(c, None))
        for c in configs
    }
    if any(s not in ("done", "failed") for s in statuses.values()):
        raise ValueError(
            f"Incomplete supervised batch (exit {result.returncode})"
        )
    replay_batch(key)
    report_batch(key)  # Completeness, administrative and billing checks.
    save(
        f"batches/{key}.complete.json",
        dict(exit_code=result.returncode, statuses=statuses),
    )
    export_receipts(key)


def run_batch(key: str) -> None:
    verify()
    configs = batch_configs(key)
    stage, arm = configs[0].stage, configs[0].arm
    if (
        stage == "validation"
        and not report_batch(f"training_{arm}")["eligible_validation"]
    ):
        raise ValueError("Training exposure gate failed")
    if stage == "followup" and not read("selection.json")["winner"]:
        raise ValueError("No authorized follow-up contender")
    if accounting()["unresolved"] or accounting()["billing_issues"]:
        raise ValueError("Unresolved liability")
    activate(stage)
    ol.OmphalosExperiment(
        config_class=ProofConfig,
        configs=configs,
        context=context(),
        output_dir=str(run_dir(stage, arm).relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def campaign() -> None:
    verify()
    with (CAMPAIGN / "campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for arm in ARMS:
            launch(f"training_{arm}")
        for arm in ARMS:
            if report_batch(f"training_{arm}")["eligible_validation"]:
                launch(f"validation_{arm}")
        winner = select()
        if winner:
            configs = [
                ProofConfig(n, "followup", ar, 1)
                for n in partition("validation")
                for ar in (winner, "reference")
            ]
            random.Random(20260913).shuffle(configs)
            save("manifests/followup.json", [asdict(c) for c in configs])
            launch("followup")
        save("final_accounting.json", accounting())
        export_receipts("final")
        report()


def report() -> None:
    rows: list[str] = []
    for stage in ("training", "validation"):
        ref = historical(stage)
        cost = sum(o.cost for o in ref.values())
        solved = sum(
            o.solved and not o.failed and o.cost <= 0.10 for o in ref.values()
        )
        rows.append(
            f"| {stage} | Historical reference | {solved}/40 | ${cost:.6f} | ${cost / solved:.6f} |"
        )
        for arm in ARMS:
            if not (CAMPAIGN / f"reports/{stage}_{arm}.json").exists():
                continue
            r = read(f"reports/{stage}_{arm}.json")
            cps = r["cost_per_solve_b"]
            rows.append(
                f"| {stage} | {arm} | {r['solved_b']}/40 | ${r['cost_b']:.6f} | {f'${cps:.6f}' if cps is not None else 'undefined'} |"
            )
    acct = accounting()
    selected: dict[str, Any] = (
        read("selection.json")
        if (CAMPAIGN / "selection.json").exists()
        else {}
    )
    text = (
        "# Resource-completion results\n\n"
        "A changes only the enforced output cap to 4096; B evaluates the "
        "existing corrected structured continuation. The frozen book is unchanged.\n\n"
        "| Panel | Arm | Qualified solves | Total cost | Cost/solve |\n"
        "|---|---|---:|---:|---:|\n" + "\n".join(rows) + "\n\n"
        f"New experimental cost: **${acct['total']:.8f} of $30**; "
        f"{acct['receipts']} receipts; {len(acct['unresolved'])} unresolved. "
        "No new adaptation, embeddings or writing roles. Codex-session charges unavailable.\n\n"
        f"Follow-up selection: `{selected.get('winner')}`. "
        "Practical gates and adjusted coverage p-values are in selection.json. "
        "Detailed paired costs, 90% intervals, exposure and failures are in reports/ and diagnostics/.\n\n"
        "ValidationX is repeatedly reused development data. Seed-0 controls "
        "are historical; cache discounts, tariff, runtime and controller "
        "conditions limit comparisons. Any selected follow-up is exploratory "
        "after selection. No default changed and no frozen score was revised.\n"
    )
    cache_rows: list[str] = []
    for stage in ("training", "validation"):
        ref_tokens = read("reference_tokens.json")[stage]
        summaries = {
            "Historical reference": token_summary(list(ref_tokens.values()))
        }
        for arm in ARMS:
            path = CAMPAIGN / f"diagnostics/{stage}_{arm}.json"
            if path.exists():
                summaries[arm] = token_summary(
                    [
                        d["tokens"]
                        for d in read(
                            f"diagnostics/{stage}_{arm}.json"
                        ).values()
                    ]
                )
        for label, summary in summaries.items():
            cache_rows.append(
                f"| {stage} | {label} | {summary['cache_fraction']:.1%} | ${summary['dated_tariff_cost']:.6f} | ${summary['no_cache_cost']:.6f} |"
            )
    if (CAMPAIGN / "diagnostics/followup.json").exists():
        followup_diagnostics = read("diagnostics/followup.json")
        for arm in (selected["winner"], "reference"):
            tokens = [
                d["tokens"]
                for cell, d in followup_diagnostics.items()
                if f"__followup-{arm}__" in cell
            ]
            summary = token_summary(tokens)
            cache_rows.append(
                f"| followup seed1 | {arm} | {summary['cache_fraction']:.1%} | ${summary['dated_tariff_cost']:.6f} | ${summary['no_cache_cost']:.6f} |"
            )
    text += (
        "\nCache sensitivity (same recorded tokens and registered tariff):\n\n"
        "| Panel | Arm | Cached input | Tariff cost | Without cache discount |\n"
        "|---|---|---:|---:|---:|\n" + "\n".join(cache_rows) + "\n\n"
        "This repricing does not simulate a different admission policy. The "
        "hard reservations use uncached input prices in every arm. Seed labels "
        "identify separately cached repeated executions; Responses supplies no "
        "provider seed guarantee. Historical controls used their archived runtime; "
        "all fresh arms use the capacity campaign's pinned profile.\n"
    )
    if (CAMPAIGN / "reports/followup.json").exists():
        r = read("reports/followup.json")
        text += (
            "\nFollow-up:\n\n```json\n" + json.dumps(r, indent=2) + "\n```\n"
        )
    (CAMPAIGN / "RESULTS.md").write_text(text)


def main() -> None:
    action, *rest = sys.argv[1:]
    if action == "run-batch":
        key, *arguments = rest
        sys.argv = [sys.argv[0], *arguments]
        run_batch(key)
    elif action == "status":
        print(json.dumps(accounting(), indent=2))
    elif action in (
        "prepare",
        "preflight",
        "reference_tokens",
        "seal",
        "campaign",
        "report",
    ):
        globals()[action]()
    else:
        raise ValueError("Unknown development-only campaign action")


if __name__ == "__main__":
    main()
