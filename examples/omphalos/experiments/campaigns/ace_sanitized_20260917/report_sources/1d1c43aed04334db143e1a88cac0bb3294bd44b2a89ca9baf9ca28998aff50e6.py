"""Offline audit, exact replay and reporting for sanitized ACE.

Both harnesses: python -m tools.reports.ace_sanitized ACTION [BATCH ...].
The reporting code is outside the sealed runtime and binds its own hash.
It opens only explicitly registered trainX/validationX measurements.
"""

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import date, datetime, timezone
import csv
import io
import json
from pathlib import Path
import re
import statistics
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.policies import prompting_policy
from delphyne.stdlib.tasks import run_command

from experiments.ace_sanitized import campaign as c
from experiments.ace_sanitized import control
from experiments.ace_sanitized.scope import partition
from experiments.ace_sanitized.workflow import frontier, verify_freeze
import prove_economy
from prove_grounded import ProposeProofScriptGrounded
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.model_registry import price_tokens
from runtime.pytanque_utils import parse_problem
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)


def audit() -> None:
    historical = json.loads((c.REFINEMENT / "results.json").read_text())
    values = historical["totals"]
    base = values["agentic"]["cost"]
    rows = [
        dict(
            arm=arm,
            cells=v["cells"],
            solved=v["qualified"],
            coverage_percent=100 * v["qualified"] / v["cells"],
            cost=v["cost"],
            budget_reduction_percent=100 * (1 - v["cost"] / base),
        )
        for arm, v in sorted(values.items())
    ]
    c.save(
        "audit.json",
        dict(
            historical_source_sha256=c.sha(c.REFINEMENT / "results.json"),
            rows=rows,
            report_source_sha256=c.sha(Path(__file__)),
            primary_comparator="ordinary agentic non-ACE, no history dropping",
            attribution="same generic controller with an empty book; report its frontier too",
            findings=[
                "The latest reset is plain dropping, with no added handoff tool. Historical proposals for a non-ACE handoff are rejected.",
                "ACE plus dropping can be evaluated against ordinary agentic use as a full system, but that comparison does not isolate ACE's book contribution.",
                "At matched reset, both solve 52/80; ACE costs 4.23% more. Against ordinary non-ACE, ACE reset gains 5 coverage points at 8.67% more cost.",
                "The last compact treatment bundles shorter instructions and altered feedback. It reduces input per request but induces more requests; its combined drop threshold is also affected by rendering.",
                "Large 32768-token output reservations cause early admission stops; a smaller output allowance is a separate budget intervention, not a free extra problem allowance.",
                "More budget helped both agents historically. Preserve the same per-problem allowance and compare joint cost/coverage rather than crediting generic headroom to ACE.",
                "Opaque reasoning must be cleared when visible context drops. Cached context still costs money; report actual retransmitted input and uncached sensitivity.",
                "The old terminal schema pilot allowed tools in a formerly valid case. The new terminal fixtures disable tools on both sides.",
                "Old v3 restarted from X3 and lost useful v2 repairs. New learning starts with v2. Local numeral evidence does not justify weakening Nat.pow_inj_r's base premise.",
            ],
        ),
    )


def batches() -> list[str]:
    return [p.stem for p in sorted((c.CAMPAIGN / "batches").glob("*.json"))]


def terminal(job: c.Job) -> Path:
    folder = c.directory(job)
    result = folder / "result.yaml"
    if result.exists():
        return result
    files = sorted(folder.glob("exception*.txt"))
    if not files:
        raise ValueError("No terminal evidence: " + c.name(job, None))
    return files[0]


@prompting_policy
def observe_stop[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    normal: dp.PromptingPolicy,
    observations: list[dict[str, Any]],
) -> dp.StreamGen[T]:
    if isinstance(query.query, ProposeProofScriptGrounded):
        observations.append(
            dict(
                groups=len(
                    prove_economy.interaction_groups(query.query.prefix)
                ),
                would_stop=control.repeated_failure(query.query.prefix),
            )
        )
    yield from normal(query, env)


def replay(batch: str) -> None:
    c.verify()
    if batch not in batches():
        raise ValueError("Replay only completed batches")
    jobs = c.jobs(batch)
    destination = f"replays/{batch}.json"
    if (c.CAMPAIGN / destination).exists():
        saved = c.read(destination)
        if not saved["passed"] or saved["paid_calls"]:
            raise ValueError("Invalid replay certificate")
        if set(saved["result_hashes"]) != {c.name(j, None) for j in jobs}:
            raise ValueError("Replay cells changed")
        for job in jobs:
            if (
                c.sha(terminal(job))
                != saved["result_hashes"][c.name(job, None)]
            ):
                raise ValueError("Measurement changed since replay")
        return
    before = c.accounting()["receipts"]
    rows: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    original_control = control.controlled_prompt
    original_recorded = prove_economy.recorded_prompt
    for job in jobs:
        original = c.cell_result(job)
        ident = c.name(job, None)
        hashes[ident] = c.sha(terminal(job))
        if original is None:
            rows.append(dict(cell=ident, platform_failed=True))
            continue
        c.activate(events=False)
        args = job.instantiate(None)
        args.cache_mode = "replay"
        args.cache_file = str(c.directory(job) / "cache.yaml")
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        observations: list[dict[str, Any]] = []

        def wrap_control(*args: Any, **kwargs: Any) -> dp.PromptingPolicy:
            return observe_stop(
                original_control(*args, **kwargs), observations
            )

        def wrap_baseline(*args: Any, **kwargs: Any) -> dp.PromptingPolicy:
            return observe_stop(
                original_recorded(*args, **kwargs), observations
            )

        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Replay forbids HTTP"),
            ),
            patch.object(control, "controlled_prompt", wrap_control),
            patch.object(prove_economy, "recorded_prompt", wrap_baseline),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(c.context(), cache_root=Path("/")),
                add_header=False,
            )
        if (
            out.result is None
            or out.result.success != original["success"]
            or out.result.spent_budget != original["spent_budget"]
            or json.loads(json.dumps(list(out.result.values)))
            != original["values"]
        ):
            raise ValueError("Exact replay mismatch: " + ident)
        rows.append(
            dict(
                cell=ident,
                passed=True,
                stop_observations=observations,
                first_stop_query=next(
                    (i for i, r in enumerate(observations) if r["would_stop"]),
                    None,
                ),
            )
        )
    if c.accounting()["receipts"] != before:
        raise ValueError("Replay created a paid receipt")
    c.verify()
    c.save(
        destination,
        dict(
            passed=True,
            paid_calls=0,
            cells=rows,
            result_hashes=hashes,
            reporting_sha256=c.sha(Path(__file__)),
        ),
    )
    print(
        json.dumps(dict(batch=batch, replayed=len(rows), paid_calls=0)),
        flush=True,
    )


def receipts() -> list[dict[str, Any]]:
    with Ledger(c.CAMPAIGN / "ledger.sqlite3").connect() as db:
        raw = db.execute(
            "SELECT id,cell,model,created,status,charged,usage FROM receipts ORDER BY created,id"
        ).fetchall()
    cells = {c.name(j, None) for j in c.all_jobs()}
    rows: list[dict[str, Any]] = []
    for ident, cell, model, created, status, charged, encoded in raw:
        if status != "settled" or cell not in cells:
            raise ValueError("Unexpected or unsettled receipt")
        usage = json.loads(encoded)
        inp, out = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
        day = datetime.fromtimestamp(created, timezone.utc)
        repriced = price_tokens(model, inp, cached, out, on=day.date())
        if abs(repriced - charged) > 1e-8:
            raise ValueError("Receipt cost mismatch")
        rows.append(
            dict(
                receipt=ident,
                cell=cell,
                model=model,
                created_utc=day.isoformat(),
                input=inp,
                cached=cached,
                output=out,
                reasoning=usage.get("output_tokens_details", {}).get(
                    "reasoning_tokens", 0
                ),
                provider_status=usage.get("status") or "unknown",
                input_bound=usage.get("input_bound"),
                charged=charged,
                repriced=repriced,
                uncached_cost=price_tokens(model, inp, 0, out, on=day.date()),
            )
        )
    return rows


def collect() -> list[dict[str, Any]]:
    a = c.accounting()
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for line in (c.CAMPAIGN / "events.jsonl").open():
        event = json.loads(line)
        if (
            event.get("kind") == "refined_session"
            and event.get("decision") == "reset"
        ):
            counts[event["cell"]]["drops"] += 1
        if event.get("kind") == "model" and event.get("decision") == "invoked":
            counts[event["cell"]]["requests"] += 1
    rec = receipts()
    rows: list[dict[str, Any]] = []
    for job in c.all_jobs():
        result = c.cell_result(job)
        ident = c.name(job, None)
        cost = a["costs"].get(ident, 0)
        paid = [r for r in rec if r["cell"] == ident]
        rows.append(
            dict(
                cell=ident,
                stage=job.stage,
                role=job.role,
                arm=job.arm,
                theorem=job.theorem,
                seed=job.seed,
                strategy_returned_value=bool(result and result["success"]),
                solved=(
                    bool(result and result["success"])
                    if job.role == "proof"
                    else None
                ),
                qualified=(
                    bool(
                        result
                        and result["success"]
                        and cost <= job.cap + 1e-12
                    )
                    if job.role == "proof"
                    else None
                ),
                failed=result is None,
                cost=cost,
                **{
                    k: sum(r[k] for r in paid)
                    for k in (
                        "input",
                        "cached",
                        "output",
                        "reasoning",
                        "uncached_cost",
                    )
                },
                requests=counts[ident]["requests"],
                drops=counts[ident]["drops"],
            )
        )
    return rows


def mechanisms(
    rows: list[dict[str, Any]], rec: list[dict[str, Any]]
) -> dict[str, Any]:
    """Explain actual admission/response limits without changing a run."""
    cells = {r["cell"]: r for r in rows if r["role"] == "proof"}
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with (c.CAMPAIGN / "events.jsonl").open() as stream:
        for line in stream:
            event = json.loads(line)
            if event.get("cell") in cells:
                events[event["cell"]].append(event)
    paid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in rec:
        if receipt["cell"] in cells:
            paid[receipt["cell"]].append(receipt)
    summaries: dict[str, Any] = {}
    for stage, arm in sorted({(r["stage"], r["arm"]) for r in cells.values()}):
        ids = [
            ident
            for ident, r in cells.items()
            if (r["stage"], r["arm"]) == (stage, arm)
        ]
        reasons: Counter[str] = Counter()
        price_spend: list[float] = []
        growth: list[float] = []
        resets: list[dict[str, Any]] = []
        for ident in ids:
            ordered = sorted(events[ident], key=lambda e: e["time"])
            stops = [
                e
                for e in ordered
                if e["kind"] == "terminal_v2" and e["decision"] == "stopped"
            ]
            if len(stops) > 1:
                raise ValueError("Unexpected multiple terminal stops")
            if stops:
                last: dict[str, Any] = stops[0].get("last_admission") or {}
                limiting = last.get("limiting", [])
                reasons["+".join(sorted(limiting)) or "other"] += 1
                if "price" in limiting:
                    price_spend.append(cells[ident]["cost"])
            if len(paid[ident]) >= 2 and paid[ident][0]["input"]:
                growth.append(
                    paid[ident][-1]["input"] / paid[ident][0]["input"]
                )
            for i, event in enumerate(ordered):
                if (
                    event["kind"] == "refined_session"
                    and event["decision"] == "reset"
                ):
                    nxt = next(
                        (
                            e
                            for e in ordered[i + 1 :]
                            if e["kind"] == "estimate_v2"
                        ),
                        None,
                    )
                    resets.append(
                        dict(
                            cell=ident,
                            before_chars=event["before_chars"],
                            after_chars=event["after_chars"],
                            next_reasoning_allowance=None
                            if nxt is None
                            else nxt["reasoning_allowance"],
                        )
                    )
        charges = [r for ident in ids for r in paid[ident]]
        summaries[f"{stage}/{arm}"] = dict(
            cells=len(ids),
            terminal_stop_reasons=dict(reasons),
            median_price_stop_spend=statistics.median(price_spend)
            if price_spend
            else None,
            provider_status_counts=dict(
                Counter(r["provider_status"] for r in charges)
            ),
            max_output_tokens=max((r["output"] for r in charges), default=0),
            median_last_first_input_ratio=statistics.median(growth)
            if growth
            else None,
            input_growth_cells=len(growth),
            resets=resets,
        )
    return summaries


def totals(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for arm in sorted({r["arm"] for r in rows}):
        cells = [r for r in rows if r["arm"] == arm]
        v: dict[str, Any] = {
            k: sum(r[k] for r in cells)
            for k in (
                "qualified",
                "failed",
                "cost",
                "input",
                "cached",
                "output",
                "reasoning",
                "requests",
                "drops",
                "uncached_cost",
            )
        }
        v.update(
            cells=len(cells),
            solved=v["qualified"],
            theorems=len({r["theorem"] for r in cells}),
            solved_theorems=len(
                {r["theorem"] for r in cells if r["qualified"]}
            ),
            observed_replicates=len({r["seed"] for r in cells}),
            coverage_percent=100 * v["qualified"] / len(cells),
            cost_per_solve=v["cost"] / v["qualified"]
            if v["qualified"]
            else None,
            cache_fraction=v["cached"] / v["input"] if v["input"] else None,
            per_seed={
                str(s): dict(
                    cells=sum(r["seed"] == s for r in cells),
                    solved=sum(
                        r["qualified"] for r in cells if r["seed"] == s
                    ),
                    cost=sum(r["cost"] for r in cells if r["seed"] == s),
                )
                for s in sorted({r["seed"] for r in cells})
            },
        )
        v["problem_coverage_at_observed_replicates_percent"] = (
            100 * v["solved_theorems"] / v["theorems"]
        )
        result[arm] = v
    return result


def families(stage: str) -> dict[str, str]:
    problems = partition(stage)
    parent = {n: n for n in problems}

    def find(n: str) -> str:
        while parent[n] != n:
            n = parent[n]
        return n

    templates: dict[str, str] = {}
    for name, file in sorted(problems.items()):
        statement = re.sub(
            r"\b\d+\b",
            "NUMBER",
            " ".join(parse_problem(file, True).theorem_statement.split()),
        )
        keys = [statement]
        if name.startswith(("imo_", "aime_", "amc")):
            keys.append(re.sub(r"(_p\d+)_\d+$", r"\1", name))
        for key in keys:
            if key in templates:
                parent[find(name)] = find(templates[key])
            else:
                templates[key] = name
    return {n: find(n) for n in problems}


def comparison(
    rows: list[dict[str, Any]], left: str, right: str
) -> dict[str, Any]:
    def obs(arm: str) -> dict[tuple[str, str], Observation]:
        return {
            (r["theorem"], str(r["seed"])): Observation(
                r["solved"], r["cost"], r["failed"]
            )
            for r in rows
            if r["arm"] == arm
        }

    a, b = obs(left), obs(right)
    expected = [(t, str(s)) for t in partition("validation") for s in (0, 1)]
    mapping = families("validation")
    pair = compare(a, b, expected, families=mapping)
    if not pair["complete"]:
        raise ValueError("Missing cells preclude a verdict")
    # The generic helper's legacy effect-size verdict is not this study's rule.
    pair.pop("verdict")
    pair.update(
        left=left,
        right=right,
        budget_reduction_percent=100 * (1 - pair["cost_ratio"]),
        budget_reduction_ci90=[
            100 * (1 - v) for v in reversed(pair["cost_ratio_ci90"])
        ],
        coverage_change_points=100 * pair["effect"],
        cost_p_two_sided=cost_cluster_p(a, b, expected, mapping),
    )
    return pair


def export(stage: str = "final") -> None:
    c.verify()
    if stage == "final":
        verify_freeze()
        c.read("benchmark_finished.json")
        if (c.CAMPAIGN / "headroom_protocol.json").exists():
            c.read("headroom_finished.json")
    for batch in batches():
        replay(batch)
    rows = collect()
    rec = receipts()
    a = c.accounting()
    if abs(sum(r["repriced"] for r in rec) - a["total"]) > 1e-8:
        raise ValueError("Export does not reconcile")
    out = c.CAMPAIGN / "analysis" / stage
    out.mkdir(parents=True, exist_ok=True)
    for filename, records in (("cells.csv", rows), ("receipts.csv", rec)):
        with (out / filename).open("w") as stream:
            writer = csv.DictWriter(
                stream, list(records[0]), lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(records)
    proofs = [r for r in rows if r["role"] == "proof"]
    selected = [
        r
        for r in proofs
        if r["stage"] == ("validation" if stage == "final" else "pilots")
    ]
    values = totals(selected) if selected else {}
    pairs = (
        [
            comparison(selected, "agentic", arm)
            for arm in values
            if arm != "agentic"
        ]
        if stage == "final"
        else []
    )
    if "agentic_selected" in values:
        pairs.append(comparison(selected, "agentic_selected", "ace_selected"))
    if "ace_incumbent" in values:
        pairs.append(comparison(selected, "ace_incumbent", "ace_selected"))
    if "agentic_coverage" in values and "ace_coverage" in values:
        pairs.append(comparison(selected, "agentic_coverage", "ace_coverage"))
    for pair in pairs:
        left, right = values[pair["left"]], values[pair["right"]]
        common = min(left["cache_fraction"], right["cache_fraction"])
        costs = [
            price_tokens(
                "gpt-5.6-luna",
                v["input"],
                round(v["input"] * common),
                v["output"],
                on=date(2026, 9, 17),
            )
            for v in (left, right)
        ]
        pair["uncached_budget_reduction_percent"] = 100 * (
            1 - right["uncached_cost"] / left["uncached_cost"]
        )
        pair["common_cache_fraction"] = common
        pair["common_cache_budget_reduction_percent"] = 100 * (
            1 - costs[1] / costs[0]
        )
    learning = sum(r["cost"] for r in rows if r["stage"] == "learning")
    adaptation = sum(r["cost"] for r in rows if r["arm"] == "adapt")
    stopping: list[dict[str, Any]] = []
    for batch in batches():
        for cell in c.read(f"replays/{batch}.json")["cells"]:
            hit = cell.get("first_stop_query")
            if hit is not None:
                after = [r for r in rec if r["cell"] == cell["cell"]][hit:]
                result = next(r for r in rows if r["cell"] == cell["cell"])
                stopping.append(
                    dict(
                        cell=cell["cell"],
                        query=hit,
                        later_observed_solve=result["qualified"],
                        observed_later_cost=sum(r["charged"] for r in after),
                    )
                )
    data = dict(
        stage=stage,
        accounting=a,
        totals=values,
        comparisons=pairs,
        learning_including_role_pilots=learning,
        adaptation_only=adaptation,
        frontier=frontier(values) if values else [],
        stopping=stopping,
        mechanisms=mechanisms(rows, rec) if stage == "final" else None,
        source_sha256=c.sha(Path(__file__)),
        default_promoted=False,
        limitation="trainX tuning; validationX repeatedly used development benchmark; no independent test claim; replicate labels do not set API RNG seeds",
    )
    if stage == "final":
        selected_book = c.read("freeze.json")["treatments"][
            c.read("freeze.json")["primary"]
        ]["book"]
        data["selected_book"] = selected_book
        data["adaptation_inclusive_budget_reduction_percent"] = 100 * (
            1
            - (
                values["ace_selected"]["cost"]
                + (learning if selected_book == "new" else 0)
            )
            / values["agentic"]["cost"]
        )
        data[
            "all_new_learning_charged_to_selected_budget_reduction_percent"
        ] = 100 * (
            1
            - (values["ace_selected"]["cost"] + learning)
            / values["agentic"]["cost"]
        )
    c.save(f"analysis/{stage}/results.json", data)
    source = Path(__file__).read_bytes()
    snapshot = c.CAMPAIGN / "report_sources" / f"{c.sha(Path(__file__))}.py"
    if not snapshot.exists():
        snapshot.parent.mkdir(exist_ok=True)
        snapshot.write_bytes(source)
    archives = {
        c.name(j, None): {
            str(p.relative_to(c.ROOT)): c.sha(p)
            for p in [
                terminal(j),
                c.directory(j) / "cache.yaml",
                c.CAMPAIGN / j.input_file,
                *sorted(
                    (c.CAMPAIGN / "transport" / c.name(j, None)).glob(
                        "*.json.gz"
                    )
                ),
                *sorted(
                    (
                        c.CAMPAIGN
                        / "transport"
                        / c.name(j, None)
                        / "checkpoints"
                    ).glob("step-*.json")
                ),
            ]
            if p.exists()
        }
        for j in c.all_jobs()
    }
    c.save(f"analysis/{stage}/archives.json", archives)
    print(
        json.dumps(
            dict(total=a["total"], cells=len(rows), totals=values), indent=2
        )
    )


def figure() -> None:
    """Standalone scientific figure, with the plotted data in results.json."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = c.read("analysis/final/results.json")
    values: dict[str, dict[str, Any]] = data["totals"]
    labels = {
        "agentic": "Non-ACE · 32,768 cap",
        "agentic_selected": "Matched non-ACE",
        "ace_selected": "ACE · 32,768 cap",
        "ace_incumbent": "Incumbent book",
        "ace_coverage": "ACE · 8,192 cap",
        "agentic_coverage": "Non-ACE · 8,192 cap",
    }
    # Matplotlib's open-ended artist keyword arguments have partial stubs.
    plotting: Any = plt
    fig, ax = plotting.subplots(figsize=(8, 4.5))
    for i, (arm, value) in enumerate(sorted(values.items())):
        ax.scatter(
            value["cost"],
            value["coverage_percent"],
            s=70,
            marker="s" if arm.startswith("agentic") else "o",
            color="#175676" if arm.startswith("agentic") else "#B64632",
        )
        ax.annotate(
            labels.get(arm, arm),
            (value["cost"], value["coverage_percent"]),
            xytext=(8, 9 if i % 2 else -17),
            textcoords="offset points",
            fontsize=9,
        )
    ax.set_xlabel("API cost across all 80 attempts (USD)")
    ax.set_ylabel("Qualified coverage (%)")
    ax.set_title("Sanitized ACE — validationX, two replicates")
    ax.grid(alpha=0.2)
    ax.margins(x=0.3, y=0.4)
    fig.text(
        0.01,
        0.01,
        "Observed points; development benchmark. Paired 90% intervals are in the report.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    for extension in ("png", "pdf"):
        fig.savefig(
            c.CAMPAIGN / f"analysis/final/cost_coverage.{extension}", dpi=180
        )
    plotting.close(fig)
    c.save(
        "analysis/final/figure.json",
        dict(
            results_sha256=c.sha(c.CAMPAIGN / "analysis/final/results.json"),
            source_sha256=c.sha(Path(__file__)),
            labels={arm: labels.get(arm, arm) for arm in values},
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("audit", "replay", "pilot", "final", "figure")
    )
    parser.add_argument("batches", nargs="*")
    args = parser.parse_args()
    if args.action == "audit":
        audit()
    elif args.action == "figure":
        figure()
    elif args.action == "replay":
        for batch in args.batches or batches():
            replay(batch)
    else:
        export(args.action)


if __name__ == "__main__":
    main()
