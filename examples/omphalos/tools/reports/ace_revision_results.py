"""Matched development panels and audited learning yield; no paid calls."""

# ruff: noqa: E402
from runtime.ace_revision_scope import install

install()

from collections import defaultdict
from decimal import Decimal
import csv
import gzip
import json
import math
from typing import Any, cast

from delphyne.utils.typing import pydantic_load

from ace.ace_playbook import Playbook
from ace.role_revision import ReflectionProduct, WriterProduct
from ace.rocq_snippets import SnippetReceipt
from experiments import ace_revision_experiment as c
from runtime.model_registry import pricing_for
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
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
    for cfg in configs:
        if cfg.stage != stage or cfg.role != "proof":
            continue
        raw = c.cell_result(cfg)
        key = (cfg.bench_name, str(cfg.seed))
        if key in arms[cfg.arm]:
            raise ValueError("Duplicate paired cell")
        arms[cfg.arm][key] = Observation(
            bool(raw and raw["success"]),
            accounting["costs"].get(c.name(cfg, None), 0),
            raw is None,
        )
    report = compare(
        arms["control"], arms["candidate"], expected, families=c.family_map()
    )
    if report["complete"]:
        report["paired_cost_p"] = cost_cluster_p(
            arms["control"], arms["candidate"], expected, c.family_map()
        )
        report["control_type"] = "fresh paired"
        delta = report["solved_b"] - report["solved_a"]
        report["registered_practical_interest"] = stage == "validation" and (
            delta >= 2
            and report["cost_ratio"] is not None
            and report["cost_ratio"] <= 1.25
            or delta >= -2
            and report["cost_ratio"] is not None
            and report["cost_ratio"] <= 0.90
        )
    return report


def economics(metrics: dict[str, Any], preparation: float) -> dict[str, Any]:
    a, b, cells = metrics["cost_a"], metrics["cost_b"], metrics["cells"]
    return dict(
        preparation_cost=preparation,
        control_cost_per_solve=a / metrics["solved_a"]
        if metrics["solved_a"]
        else None,
        candidate_cost_per_solve=b / metrics["solved_b"]
        if metrics["solved_b"]
        else None,
        candidate_all_in_cost=b + preparation,
        candidate_all_in_cost_per_solve=(b + preparation) / metrics["solved_b"]
        if metrics["solved_b"]
        else None,
        amortization_problems=math.ceil(
            Decimal(str(preparation))
            * Decimal(cells)
            / (Decimal(str(a)) - Decimal(str(b)))
        )
        if a > b
        else None,
        caution="Descriptive extrapolation of observed inference saving; benchmark research costs are reported separately",
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


def exposure(config: c.Config, book: str) -> dict[str, Any]:
    seen = 0
    snapshots = sorted(
        (c.CAMPAIGN / "transport" / c.name(config, None)).glob("*.json.gz")
    )
    for path in snapshots:
        raw = json.loads(gzip.decompress(path.read_bytes()))
        seen += book.strip() in "\n".join(strings(raw.get("request", {})))
    return dict(
        cell=c.name(config, None),
        snapshots=len(snapshots),
        book_exposures=seen,
    )


def mechanism(
    configs: list[c.Config], accounting: dict[str, Any]
) -> dict[str, Any]:
    roles: dict[str, dict[str, Any]] = {}
    for cfg in configs:
        if cfg.role == "proof":
            continue
        row = roles.setdefault(
            cfg.role,
            dict(
                jobs=0,
                complete=0,
                partial=0,
                absent=0,
                drafts=0,
                checks=0,
                reviews=0,
                cost=0.0,
            ),
        )
        p = c.role_product(cfg)
        row["jobs"] += 1
        row["cost"] += accounting["costs"].get(c.name(cfg, None), 0)
        row[p.status if p else "absent"] += 1
        if isinstance(p, ReflectionProduct):
            row["drafts"] += len(p.drafts)
        elif isinstance(p, WriterProduct):
            inherited = {
                pydantic_load(SnippetReceipt, x).identifier
                for x in c.read(cfg.input_file).get("receipts", [])
            }
            row["checks"] += sum(
                r.identifier not in inherited for r in p.receipts
            )
            row["reviews"] += len(p.reviews)
    edits: list[dict[str, Any]] = []
    for path in sorted((c.CAMPAIGN / "revisions").glob("*.json")):
        raw = json.loads(path.read_text())
        bank = {
            receipt.identifier: receipt
            for r in raw["writer"]["receipts"]
            if (receipt := pydantic_load(SnippetReceipt, r))
        }
        # The full source bank is kept in each revision; these are mechanism
        # descriptions, not an attribution of individual downstream solves.
        for edit in raw["edits"]:
            sources = sorted(
                {bank[rid].context.theorem_name for rid in edit["receipts"]}
            )
            statuses = {
                n: c.read(f"sources/{n}.json")["terminal"]["status"]
                for n in sources
            }
            edits.append(
                dict(
                    **edit,
                    batch=path.stem,
                    sources=statuses,
                    unsolved_source=any(
                        s != "accepted" for s in statuses.values()
                    ),
                )
            )
    before = Playbook.load(c.BOOK)
    after = Playbook.load(c.CAMPAIGN / "book.yaml")
    return dict(
        roles=roles,
        edits=edits,
        original_tokens=before.token_estimate(),
        final_tokens=after.token_estimate(),
        original_entries=len(before.bullets),
        final_entries=len(after.bullets),
        caution="Validity, local execution, reviewed novelty, learning yield and transfer are separate outcomes",
    )


def report() -> None:
    c.verify()
    a = c.accounting()
    configs = c.all_configs()
    metrics: dict[str, Any] = {}
    prep = sum(
        a["costs"].get(c.name(cfg, None), 0)
        for cfg in configs
        if cfg.stage == "adaptation"
    )
    for stage in ("training", "validation"):
        if any(cfg.stage == stage for cfg in configs):
            metrics[stage] = paired(stage, configs, a)
            if metrics[stage]["complete"]:
                metrics[stage]["economics"] = economics(metrics[stage], prep)
    count = len(configs)
    c.save(f"reports/{count}.json", metrics)
    c.save(f"accounting/{count}.json", a)
    c.save("mechanism.json", mechanism(configs, a))
    candidate = Playbook.load(c.CAMPAIGN / "book.yaml").render_prompt()
    exposures = [
        exposure(cfg, candidate)
        for cfg in configs
        if cfg.stage == "training" and cfg.arm == "candidate"
    ]
    if exposures:
        c.save(
            "training_exposure.json",
            dict(
                new_book_dispatched=any(
                    r["book_exposures"] for r in exposures
                ),
                cells=exposures,
            ),
        )
    rates = pricing_for("gpt-5.6-luna")
    sensitivity: dict[str, dict[str, Any]] = defaultdict(
        lambda: dict(
            actual=0.0,
            uncached_same_tokens=0.0,
            input_tokens=0,
            cached_tokens=0,
        )
    )
    with (c.CAMPAIGN / "cells.csv").open("w") as out:
        writer = csv.DictWriter(
            out,
            fieldnames=[
                "stage",
                "arm",
                "role",
                "theorem",
                "seed",
                "success",
                "qualified",
                "platform_failed",
                "cost",
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
                    success=bool(raw and raw["success"]),
                    qualified=bool(
                        cfg.role == "proof"
                        and raw
                        and raw["success"]
                        and cost <= 0.10 + 1e-12
                    ),
                    platform_failed=raw is None,
                    cost=cost,
                )
            )
            t = a["tokens"].get(
                c.name(cfg, None), dict(input=0, cached=0, output=0)
            )
            row = sensitivity[cfg.stage + "/" + cfg.arm]
            row["actual"] += cost
            row["uncached_same_tokens"] += (
                t["input"] * rates.dollars_per_input_token
                + t["output"] * rates.dollars_per_output_token
            )
            row["input_tokens"] += t["input"]
            row["cached_tokens"] += t["cached"]
    c.save(f"cost_sensitivity/{count}.json", sensitivity)
    with c.Ledger(c.CAMPAIGN / "ledger.sqlite3").connect() as db:
        cursor = db.execute("SELECT * FROM receipts ORDER BY created,id")
        with (c.CAMPAIGN / "receipts.csv").open("w") as out:
            writer = csv.writer(out)
            writer.writerow([d[0] for d in cursor.description])
            writer.writerows(cursor.fetchall())
    lines = [
        "# ACE revision: fresh flagship comparison",
        "",
        f"New campaign charges: **${a['total']:.8f} / $40**; {a['receipts']} receipts; {len(a['unresolved'])} unresolved.",
        "",
        "The user reset the budget for this campaign. Earlier charges remain in their historical ledger. validationX is reused development data. No default changed.",
        "",
        "| Panel | Flagship solves | Candidate solves | Flagship cost | Candidate cost |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for stage, row in metrics.items():
        if row["complete"]:
            lines.append(
                f"| {stage} | {row['solved_a']}/{row['cells']} | {row['solved_b']}/{row['cells']} | ${row['cost_a']:.8f} | ${row['cost_b']:.8f} |"
            )
        else:
            lines.append(f"| {stage} | incomplete | no verdict | — | — |")
    lines.extend(
        [
            "",
            f"Preparation cost: ${prep:.8f}. Detailed family-clustered uncertainty, cost/solve, all-in costs and amortization are in `reports/{count}.json`.",
            "",
            "The comparison tests the learned book under a matched generator. It does not isolate each new role tool's contribution.",
        ]
    )
    (c.CAMPAIGN / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(dict(cells=count, total=a["total"], metrics=metrics)))
