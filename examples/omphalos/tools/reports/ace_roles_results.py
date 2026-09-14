"""Development-only ACE role audits and paired reporting; no model calls.

Both harnesses: python -m tools.reports.ace_roles_results audit | report.
Utility review is explicit, arm-free at the item level, and source-clustered.
"""

# ruff: noqa: E402
from runtime.ace_roles_scope import install

install()

from collections import defaultdict
from dataclasses import asdict
from decimal import Decimal
import csv
import gzip
import hashlib
import json
import math
import sys
from typing import Any, cast
from unittest.mock import patch

from delphyne.utils.typing import pydantic_load
import yaml

from ace.ace_playbook import Playbook, merge
from ace.rocq_snippets import SnippetReceipt, check_snippet
from experiments import ace_roles_experiment as c
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from runtime.model_registry import pricing_for


def ident(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True).encode()
    ).hexdigest()[:20]


def recorded_checks(config: c.Config) -> list[SnippetReceipt]:
    path = c.directory(config) / "cache.yaml"
    if not path.exists():
        return []
    rows = yaml.load(path.read_text(), Loader=yaml.CSafeLoader)
    checks: list[SnippetReceipt] = []
    for entry in rows:
        req = entry["input"]["request"]
        if req["options"].get("model") != "__compute__":
            continue
        call = yaml.safe_load(req["chat"][-1]["content"])
        output: dict[str, Any] = entry.get("output") or {}
        outputs: list[dict[str, Any]] = output.get("outputs", [])
        if call.get("fun") == "check_snippet" and outputs:
            checks.append(
                pydantic_load(
                    SnippetReceipt, yaml.safe_load(outputs[0]["content"])
                )
            )
    return checks


def audit() -> None:
    c.verify()
    c.activate("writer_pilot", events=False)
    before = c.accounting()
    book = Playbook.load(c.BOOK)
    items: dict[str, Any] = {}
    owners: dict[str, list[str]] = defaultdict(list)
    cells: list[dict[str, Any]] = []
    reflections: dict[str, Any] = {}
    seen: set[str] = set()
    for cfg in c.all_configs():
        raw = c.cell_result(cfg)
        cell = c.name(cfg, None)
        valid = bool(raw and raw["success"])
        row: dict[str, Any] = dict(
            cell=cell,
            stage=cfg.stage,
            role=cfg.role,
            arm=cfg.arm,
            source=cfg.bench_name,
            valid=valid,
            cost=before["costs"].get(cell, 0),
            tokens=before["tokens"].get(
                cell, dict(input=0, cached=0, output=0)
            ),
            model_requests=raw["spent_budget"].get("num_requests", 0)
            if raw
            else 0,
        )
        if cfg.role in ("curator", "reducer"):
            product = c.writer_product(cfg)
            checks = recorded_checks(cfg)
            row.update(
                checks=len(checks),
                check_statuses=[r.status for r in checks],
                items=[],
            )
            if product:
                merged = merge(
                    book,
                    product.checked.delta.operations,
                    (),
                    dedup_counts_helpful=False,
                    max_tokens=4000,
                )
                rendered = merged.playbook.render_prompt()
                bank = {r.identifier: r for r in product.checked.receipts}
                for op in product.checked.answer.operations:
                    for rid in op.receipts:
                        receipt = bank[rid]
                        if rid not in seen:
                            with patch.object(
                                c.CampaignResponsesModel,
                                "_send_final_request",
                                side_effect=AssertionError(
                                    "Audit forbids HTTP"
                                ),
                            ):
                                verified = check_snippet(
                                    receipt.context,
                                    receipt.snippet,
                                    dict(
                                        seconds=60,
                                        rpc_calls=512,
                                        view_bytes=8192,
                                    ),
                                )
                            if (
                                not verified.executable
                                or verified.identifier != receipt.identifier
                            ):
                                raise ValueError(
                                    "Retained receipt failed exact real-Rocq recheck: "
                                    + rid
                                )
                            seen.add(rid)
                        key = ident([rid, op.explanation])
                        items[key] = dict(
                            source=receipt.context.theorem_name,
                            snippet=receipt.snippet,
                            explanation=op.explanation,
                            context=asdict(receipt.context),
                            status=receipt.status,
                            receipt_id=rid,
                            survives_merge=rid in rendered
                            and receipt.snippet in rendered,
                            source_rechecked=True,
                        )
                        row["items"].append(key)
                        owners[key].append(cell)
                row["decisions"] = [asdict(d) for d in product.decisions]
        elif cfg.role == "reflector":
            key = ident([cell, c.read(cfg.input_file)])
            args = c.read(cfg.input_file)
            reflections[key] = dict(
                source=cfg.bench_name,
                result=raw["values"][0] if valid and raw else None,
                terminal=args["terminal"],
                trajectory=args["trajectory"],
                events=args.get("events", []),
            )
            owners[key].append(cell)
            row["review_id"] = key
        cells.append(row)
    assert c.accounting()["receipts"] == before["receipts"]
    count = len(cells)
    c.save(f"audits/{count}_items.json", items)
    c.save(f"audits/{count}_reflections.json", reflections)
    c.save(f"audits/{count}_owners.json", owners)
    c.save(f"audits/{count}_cells.json", cells)
    c.save(
        f"audits/{count}_checks.json",
        dict(
            paid_calls=0,
            exact_real_rocq_receipts=len(seen),
            total_cells=count,
            all_required_terminal=True,
        ),
    )
    print(
        json.dumps(
            dict(
                cells=count,
                items=len(items),
                reflections=len(reflections),
                receipts_rechecked=len(seen),
                cost=before["total"],
            )
        )
    )


def strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [
            s for v in cast(dict[str, Any], value).values() for s in strings(v)
        ]
    if isinstance(value, list):
        return [s for v in cast(list[Any], value) for s in strings(v)]
    return []


def exposure(config: c.Config, added: list[str]) -> dict[str, Any]:
    requests: list[dict[str, Any]] = []
    for path in sorted(
        (c.CAMPAIGN / "transport" / c.name(config, None)).glob("*.json.gz")
    ):
        raw = json.loads(gzip.decompress(path.read_bytes()))
        # Request-addressed transport snapshots exist only after a response.
        request = raw.get("request", {})
        text = "\n".join(strings(request))
        present = [bullet for bullet in added if bullet in text]
        requests.append(dict(snapshot=path.name, new_bullet_ids=present))
    return dict(
        cell=c.name(config, None),
        requests=requests,
        exposed_requests=sum(bool(r["new_bullet_ids"]) for r in requests),
    )


def paired(
    stage: str, configs: list[c.Config], accounting: dict[str, Any]
) -> dict[str, Any]:
    expected = [
        (n, str(seed))
        for seed in ((0, 1) if stage == "validation" else (0,))
        for n in c.partition(stage)
    ]
    arms: dict[str, dict[tuple[str, str], Observation]] = dict(
        control={}, candidate={}
    )
    if stage == "training":
        for ref in c.read("references.json")[stage]:
            arms["control"][(ref["theorem"], str(ref["seed"]))] = Observation(
                ref["solved"], ref["cost"], ref["failed"]
            )
    for cfg in configs:
        if cfg.stage != stage or cfg.role != "proof":
            continue
        raw = c.cell_result(cfg)
        arms[cfg.arm][(cfg.bench_name, str(cfg.seed))] = Observation(
            bool(raw and raw["success"]),
            accounting["costs"].get(c.name(cfg, None), 0),
            raw is None,
        )
    report = compare(
        arms["control"], arms["candidate"], expected, families=c.family_map()
    )
    if report.get("complete"):
        report["paired_cost_p"] = cost_cluster_p(
            arms["control"],
            arms["candidate"],
            expected,
            families=c.family_map(),
        )
        report["control_type"] = (
            "fresh paired" if stage == "validation" else "historical"
        )
    return report


def economics(metrics: dict[str, Any], preparation: float) -> dict[str, Any]:
    """Preparation is paid once; hypothetical amortization is not evidence."""
    cells = metrics["cells"]
    a, b = metrics["cost_a"], metrics["cost_b"]
    saving = (a - b) / cells
    return dict(
        preparation_cost=preparation,
        control_inference_cost_per_solve=(
            a / metrics["solved_a"] if metrics["solved_a"] else None
        ),
        candidate_inference_cost_per_solve=(
            b / metrics["solved_b"] if metrics["solved_b"] else None
        ),
        candidate_all_in_cost=preparation + b,
        candidate_all_in_cost_per_solve=(
            (preparation + b) / metrics["solved_b"]
            if metrics["solved_b"]
            else None
        ),
        observed_saving_per_problem=saving,
        amortization_problems=(
            math.ceil(
                Decimal(str(preparation))
                * Decimal(cells)
                / (Decimal(str(a)) - Decimal(str(b)))
            )
            if saving > 0
            else None
        ),
        caution="Amortization extrapolates the observed inference saving to future problems; it excludes pilot/benchmark research charges and is not a deployment estimate.",
    )


def mechanism(configs: list[c.Config], accounting: dict[str, Any]) -> None:
    """Role validity and final-book utility have different denominators."""
    groups: dict[str, dict[str, Any]] = {}
    for cfg in configs:
        if cfg.role == "proof":
            continue
        key = "/".join((cfg.stage, cfg.arm, cfg.role))
        row = groups.setdefault(
            key, dict(jobs=0, valid=0, model_requests=0, cost=0.0)
        )
        raw = c.cell_result(cfg)
        row["jobs"] += 1
        row["valid"] += bool(raw and raw["success"])
        row["model_requests"] += (
            raw["spent_budget"].get("num_requests", 0) if raw else 0
        )
        row["cost"] += accounting["costs"].get(c.name(cfg, None), 0)
    if not (c.CAMPAIGN / "book_review.json").exists():
        return
    review = c.read("book_review.json")
    skipped = sorted(
        p.stem.removeprefix("adapt_")
        for p in (c.CAMPAIGN / "skips").glob("adapt_*.json")
    )
    c.save(
        "mechanism.json",
        dict(
            roles=groups,
            skipped_curator_sources=skipped,
            final_added_entries=len(review["added"]),
            final_useful_entries=sum(r["useful"] for r in review["added"]),
            additions_from_unsolved_sources=sum(
                r["source_status"] != "accepted" for r in review["added"]
            ),
            original_book_tokens=review["original_tokens"],
            candidate_book_tokens=review["new_tokens"],
            token_growth_ratio=review["new_tokens"]
            / review["original_tokens"],
            caution="Validity, source execution, novelty, retention, exposure and additional solves are separate outcomes. No causal credit to a particular bullet is inferred.",
        ),
    )


def report() -> None:
    c.verify()
    a = c.accounting()
    configs = c.all_configs()
    mechanism(configs, a)
    proof_configs = [cfg for cfg in configs if cfg.role == "proof"]
    metrics: dict[str, Any] = {}
    for stage in ("training", "validation"):
        if any(cfg.stage == stage for cfg in proof_configs):
            metrics[stage] = paired(stage, configs, a)
    c.save(f"reports/{len(configs)}.json", metrics)
    if (c.CAMPAIGN / "book.json").exists():
        current = Playbook.load(c.CAMPAIGN / "book.yaml")
        old_ids = {b.id for b in Playbook.load(c.BOOK).bullets}
        added = [b.id for b in current.bullets if b.id not in old_ids]
        training_exposure = [
            exposure(cfg, added)
            for cfg in proof_configs
            if cfg.stage == "training"
        ]
        if training_exposure:
            c.save(
                "training_exposure.json",
                dict(
                    new_book_dispatched=any(
                        r["exposed_requests"] for r in training_exposure
                    ),
                    added_ids=added,
                    cells=training_exposure,
                    caution="Exposure is not proof that a particular bullet caused a solve",
                ),
            )
    with (c.CAMPAIGN / "cells.csv").open("w") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "stage",
                "arm",
                "role",
                "theorem",
                "seed",
                "valid_or_solved",
                "qualified_solve",
                "platform_failed",
                "cost",
                "input",
                "cached",
                "output",
            ],
        )
        writer.writeheader()
        for cfg in configs:
            raw = c.cell_result(cfg)
            cost = a["costs"].get(c.name(cfg, None), 0)
            writer.writerow(
                dict(
                    stage=cfg.stage,
                    arm=cfg.arm,
                    role=cfg.role,
                    theorem=cfg.bench_name,
                    seed=cfg.seed,
                    valid_or_solved=bool(raw and raw["success"]),
                    qualified_solve=bool(
                        cfg.role == "proof"
                        and raw
                        and raw["success"]
                        and cost <= 0.10 + 1e-12
                    ),
                    platform_failed=raw is None,
                    cost=cost,
                    **a["tokens"].get(
                        c.name(cfg, None), dict(input=0, cached=0, output=0)
                    ),
                )
            )
    ledger = c.Ledger(c.CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        cursor = db.execute("SELECT * FROM receipts ORDER BY created,id")
        with (c.CAMPAIGN / "receipts.csv").open("w") as stream:
            writer = csv.writer(stream)
            writer.writerow([d[0] for d in cursor.description])
            writer.writerows(cursor.fetchall())
    costs: dict[str, float] = defaultdict(float)
    uncached: dict[str, float] = defaultdict(float)
    input_tokens: dict[str, int] = defaultdict(int)
    cached_tokens: dict[str, int] = defaultdict(int)
    rates = pricing_for("gpt-5.6-luna")
    for cfg in configs:
        key = cfg.stage + "/" + cfg.arm
        cell = c.name(cfg, None)
        costs[key] += a["costs"].get(cell, 0)
        t = a["tokens"].get(cell, dict(input=0, output=0))
        input_tokens[key] += t["input"]
        cached_tokens[key] += t.get("cached", 0)
        uncached[key] += (
            t["input"] * rates.dollars_per_input_token
            + t["output"] * rates.dollars_per_output_token
        )
    c.save(f"accounting/{len(configs)}.json", a)
    c.save(
        f"cost_sensitivity/{len(configs)}.json",
        dict(
            actual=costs,
            uncached_same_tokens=uncached,
            cached_input_fraction={
                key: cached_tokens[key] / count if count else None
                for key, count in input_tokens.items()
            },
            warning="Offline tariff sensitivity, not another admission-policy experiment",
        ),
    )
    lines = [
        "# ACE role campaign results",
        "",
        f"New experimental charges: **${a['total']:.8f} / $40**; {a['receipts']} receipts; {len(a['unresolved'])} unresolved.",
        "",
        "validationX is reused development data. No default changed.",
        "",
    ]
    if (c.CAMPAIGN / "gates.json").exists():
        gate = c.read("gates.json")
        lines.extend(
            [
                "## Role pilots",
                "",
                "| Writer | Valid / 10 | Reducers / 2 | Useful distinct corrections | Cost |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for arm, r in gate["writer"].items():
            lines.append(
                f"| {arm} | {r['valid']} | {r['reducers']} | {r['useful']} | ${r['cost']:.8f} |"
            )
        lines.extend(
            [
                "",
                f"Writer gate: **{gate['advance_writer']}**. New reflector inclusion: **{gate['include_reflector']}**.",
                "",
                "Useful edits are agent-reviewed source-local corrections; local execution is not a complete theorem or evidence of transfer. Related roles and batches are not independent observations.",
                "",
            ]
        )
    if metrics:
        lines.extend(
            [
                "## Flagship comparison",
                "",
                "| Panel | Control solves | Candidate solves | Control cost | Candidate cost |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for stage, m in metrics.items():
            if m.get("complete"):
                lines.append(
                    f"| {stage} | {m['solved_a']}/{m['cells']} | {m['solved_b']}/{m['cells']} | ${m['cost_a']:.8f} | ${m['cost_b']:.8f} |"
                )
            else:
                lines.append(f"| {stage} | Incomplete | No verdict | — | — |")
    else:
        lines.extend(
            [
                "No new proof panel has been dispatched. Historical flagship: trainX 28/40 at $0.68922336; validationX seed 0 27/40 at $0.66722836. These are context, not a fresh candidate comparison.",
                "",
            ]
        )
    (c.CAMPAIGN / "RESULTS.md").write_text("\n".join(lines) + "\n")
    if "validation" in metrics and metrics["validation"].get("complete"):
        m = metrics["validation"]
        gain = m["solved_b"] - m["solved_a"]
        flag = (
            gain >= 2
            and m["cost_ratio"] <= 1.25
            or gain >= -2
            and m["cost_ratio"] <= 0.90
        )
        preparation = costs.get("adaptation/candidate", 0) + costs.get(
            "adaptation/control", 0
        )
        economic = economics(m, preparation)
        c.save(
            "final_decision.json",
            dict(
                practical_tradeoff=flag,
                default_changed=False,
                metrics=m,
                economics=economic,
                total_research_cost=a["total"],
            ),
        )
        ci = m["effect_ci90"]
        cost_ci = m["cost_ratio_ci90"]
        lines.extend(
            [
                "",
                f"Practical trade-off flag: **{flag}**. Coverage difference: {100 * m['effect']:+.1f} percentage points; descriptive 90% family-bootstrap interval [{100 * ci[0]:.1f}, {100 * ci[1]:.1f}]; two-sided paired p={m['p_two_sided']:.5f}.",
                "",
                f"Inference cost ratio: {m['cost_ratio']:.3f}, 90% interval [{cost_ci[0]:.3f}, {cost_ci[1]:.3f}]; paired cost p={m['paired_cost_p']:.5f}. All failed attempts remain in costs and denominators.",
                "",
                f"Book preparation: ${preparation:.8f}; candidate preparation plus validation inference: ${economic['candidate_all_in_cost']:.8f}. Hypothetical preparation break-even: {economic['amortization_problems']} future problems at the observed saving (None means no positive saving). Pilot and evaluation research charges are separate from this preparation calculation.",
                "",
                "See final_decision.json for costs per qualified solve and cells.csv for every problem-seed-arm observation. Statistical support, the practical flag, and changing the default are separate decisions.",
            ]
        )
        (c.CAMPAIGN / "RESULTS.md").write_text("\n".join(lines) + "\n")
        figure(metrics)
    print(
        json.dumps(dict(jobs=len(configs), cost=a["total"], metrics=metrics))
    )


def figure(metrics: dict[str, Any]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plotting: Any = plt  # Matplotlib's variable keyword stubs are incomplete.
    fig, ax = plotting.subplots(figsize=(6.3, 4.2))
    m = metrics["validation"]
    for label, suffix, color in (
        ("Flagship", "a", "#486B91"),
        ("Updated ACE book", "b", "#C46636"),
    ):
        ax.scatter(
            m[f"cost_{suffix}"],
            m[f"solved_{suffix}"],
            s=90,
            label=label,
            color=color,
        )
    ax.set(
        xlabel="Total charged inference cost (USD)",
        ylabel="Qualified solves / 80",
        title="Fresh paired validationX comparison\n40 problems, two seeds; development data",
    )
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(c.CAMPAIGN / f"coverage_cost.{ext}", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    {"audit": audit, "report": report}[sys.argv[1]]()
