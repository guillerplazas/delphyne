"""Development-only ACE v3 measurements, pilot evidence and paired reports.

Derived reports may be regenerated. Inputs, manifests, decisions, sources,
receipts and raw outputs stay immutable. Missing cells prohibit selection.
"""

# ruff: noqa: E402
from runtime.ace_learning_scope import install

install()

from collections import defaultdict
from dataclasses import asdict
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from delphyne.utils.typing import pydantic_load

from ace.role_revision import WriterProduct
from ace.rocq_snippets import SnippetReceipt
from experiments import ace_learning_experiment as c
from experiments.common.ace_learning_io import accounting
from runtime.model_registry import pricing_for
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)


def write(path: str, value: Any) -> None:
    target = c.CAMPAIGN / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def trace(folder: Path, book: str = "") -> dict[str, Any]:
    """Only actual model requests count as exposure; compute is separate."""
    path = folder / "cache.yaml"
    rows: list[dict[str, Any]] = (
        yaml.safe_load(path.read_text()) if path.exists() else []
    )
    calls: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    tools: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        request, response = row["input"]["request"], row["output"]
        if response.get("model_name") == "gpt-5.6-luna":
            rendered = yaml.safe_dump(request, allow_unicode=True)
            # Compare the literal strings before YAML wrapping/escaping.
            exposed = (
                any(
                    book.strip() in str(m.get("content", ""))
                    for m in request["chat"]
                )
                if book
                else False
            )
            calls.append(
                dict(
                    cache_index=index,
                    book_exposed=exposed,
                    output=response["outputs"],
                    request_sha256=hashlib.sha256(
                        rendered.encode()
                    ).hexdigest(),
                )
            )
        elif request.get("options", {}).get("model") == "__compute__":
            arg = yaml.safe_load(request["chat"][0]["content"])
            outputs = response.get("outputs", [])
            result = yaml.safe_load(outputs[0]["content"]) if outputs else None
            item = dict(
                cache_index=index,
                function=arg.get("fun"),
                args=arg.get("args"),
                result=result,
            )
            tools.append(item)
            if arg.get("fun") == "checked_proof":
                checks.append(item)
    return dict(
        requests=len(calls),
        book_exposures=sum(x["book_exposed"] for x in calls),
        model_calls=calls,
        proof_checks=checks,
        computations=tools,
        cache=str(path.relative_to(c.ROOT)),
        cache_sha256=c.sha(path) if path.exists() else None,
    )


def proof_rows() -> list[dict[str, Any]]:
    old, new = accounting(c.PRIOR), c.accounting()
    rows: list[dict[str, Any]] = []
    rates = pricing_for("gpt-5.6-luna")
    specs: list[tuple[str, str, str, int, c.Config | None]] = []
    for stage in ("training", "validation"):
        for seed in (0, 1) if stage == "validation" else (0,):
            specs.extend(
                (stage, "v2", n, seed, None) for n in c.partition(stage)
            )
    specs.extend(
        (j.stage, j.arm, j.bench_name, j.seed, j)
        for j in c.all_configs()
        if j.role == "proof"
    )
    for stage, arm, theorem, seed, cfg in specs:
        if cfg:
            raw = c.cell_result(cfg)
            ledger, cell, folder = new, c.name(cfg, None), c.directory(cfg)
            book = c.read(cfg.input_file)["playbook"]
        else:
            cell = f"{stage}__candidate__proof__{theorem}__seed{seed}"
            folder = c.prior_directory(stage, "proof", theorem, seed)
            if c.ol.ground_truth(folder) not in ("done", "failed"):
                raise ValueError("Missing historical control: " + cell)
            original = c.prior_result(stage, "proof", theorem, seed)
            raw = original["outcome"]["result"]
            ledger, book = old, original["args"]["args"]["playbook"]
        cost = ledger["costs"].get(cell, 0)
        tokens = ledger["tokens"].get(cell, dict(input=0, cached=0, output=0))
        success = bool(raw and raw["success"])
        rows.append(
            dict(
                stage=stage,
                arm=arm,
                theorem=theorem,
                seed=seed,
                success=success,
                qualified=success and raw is not None and cost <= 0.1 + 1e-12,
                platform_failed=raw is None,
                cost=cost,
                cost_per_cell_uncached=tokens["input"]
                * rates.dollars_per_input_token
                + tokens["output"] * rates.dollars_per_output_token,
                tokens=tokens,
                result=str((folder / "result.yaml").relative_to(c.ROOT)),
                result_sha256=c.sha(folder / "result.yaml")
                if (folder / "result.yaml").exists()
                else None,
                spent_budget=raw["spent_budget"] if raw else {},
                book=book,
                folder=str(folder),
            )
        )
    return rows


def paired(stage: str, arm: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    expected = [
        (n, str(s))
        for s in ((0, 1) if stage == "validation" else (0,))
        for n in c.partition(stage)
    ]
    observed: dict[str, dict[tuple[str, str], Observation]] = {
        "v2": {},
        arm: {},
    }
    for row in rows:
        if row["stage"] != stage or row["arm"] not in observed:
            continue
        key = (row["theorem"], str(row["seed"]))
        if key in observed[row["arm"]]:
            raise ValueError("Duplicate proof cell")
        observed[row["arm"]][key] = Observation(
            row["success"], row["cost"], row["platform_failed"]
        )
    a, b = observed["v2"], observed[arm]
    result = compare(a, b, expected, families=c.family_map())
    if result["complete"]:
        result["paired_cost_p"] = cost_cluster_p(
            a, b, expected, c.family_map()
        )
        result["cost_per_qualified_solve_a"] = (
            result["cost_a"] / result["solved_a"]
            if result["solved_a"]
            else None
        )
        result["cost_per_qualified_solve_b"] = (
            result["cost_b"] / result["solved_b"]
            if result["solved_b"]
            else None
        )
        delta = result["solved_b"] - result["solved_a"]
        result["registered_practical_interest"] = stage == "validation" and (
            (delta >= 2 and result["cost_ratio"] <= 1.25)
            or (delta >= -2 and result["cost_ratio"] <= 0.90)
        )
        result["historical_control"] = True
    return result


def select() -> dict[str, Any]:
    """Freeze training choice before reading new validation results."""
    c.verify()
    if any(j.stage == "validation" for j in c.all_configs()):
        raise ValueError("Selection is closed after validation registration")
    rows = proof_rows()
    metrics: dict[str, Any] = {}
    for arm in ("A", "B"):
        if (c.CAMPAIGN / f"manifests/training_{arm}.json").exists():
            metrics[arm] = paired("training", arm, rows)
    if any(not m["complete"] for m in metrics.values()):
        raise ValueError("Training panel incomplete")
    coverage = [
        a
        for a, m in metrics.items()
        if m["solved_b"] >= m["solved_a"] and m["cost_ratio"] <= 1.25
    ]
    economy = [
        a
        for a, m in metrics.items()
        if m["solved_b"] >= m["solved_a"] - 1 and m["cost_ratio"] <= 0.9
    ]
    eligible = sorted(
        set(coverage + economy),
        key=lambda a: (-metrics[a]["solved_b"], metrics[a]["cost_b"]),
    )
    primary = (
        sorted(
            coverage,
            key=lambda a: (-metrics[a]["solved_b"], metrics[a]["cost_b"]),
        )[0]
        if coverage
        else sorted(economy, key=lambda a: metrics[a]["cost_b"])[0]
        if economy
        else None
    )
    selection = dict(
        primary=primary,
        validation_arms=[primary] if primary else [],
        secondary_candidates=[a for a in eligible if a != primary],
        training_metrics=metrics,
        rule=c.read("protocol.json")["protocol"],
        selected_before_new_validation=True,
    )
    c.save("selection.json", selection)
    return selection


def secondary() -> bool:
    """Only after the selected complete panel and all adaptation/training."""
    selection = c.read("selection.json")
    if not selection["secondary_candidates"]:
        return False
    if not (
        c.CAMPAIGN / f"batches/validation_{selection['primary']}.json"
    ).exists():
        raise ValueError("Primary validation must finish before rollover")
    for arm in ("A", "B"):
        if (c.CAMPAIGN / f"books/{arm}.json").exists() and not any(
            (c.CAMPAIGN / p).exists()
            for p in (
                f"batches/training_{arm}.json",
                f"training_{arm}.skipped.json",
            )
        ):
            raise ValueError("Earlier stages are not finished")
    if not c.fund_second_validation():
        return False
    arm = selection["secondary_candidates"][0]
    c.save(
        "secondary_validation.json",
        dict(
            arm=arm,
            registered_before_dispatch=True,
            decision="Preregistered rollover; eligibility determined on training, independent of validation outcomes",
        ),
    )
    return True


def pilot_evidence() -> list[dict[str, Any]]:
    jobs = {
        j.bench_name + "/" + j.arm: j
        for j in c.all_configs()
        if j.stage == "pilots"
    }
    rows: list[dict[str, Any]] = []
    for case in c.read("pilot_registration.json")["cases"]:
        job = jobs.get(case["case"] + "/" + case["treatment"])
        if job is None:
            continue
        raw = c.cell_result(job)
        row = dict(
            registration=case,
            cell=c.name(job, None),
            result=raw,
            cost=c.accounting()["costs"].get(c.name(job, None), 0),
        )
        if job.role in ("reflector", "curator"):
            product = c.role_product(job)
            row["product"] = asdict(product) if product else None
            row["executed_receipts"] = (
                [r.identifier for r in product.receipts if r.executable]
                if isinstance(product, WriterProduct)
                else []
            )
        value: dict[str, Any] = (
            raw["values"][0] if raw and raw["values"] else {}
        )
        if job.role == "schema":
            row["valid_final"] = bool(value.get("plan"))
        if job.role == "review":
            row["scored"] = case["expected_support"] != "unresolved"
            row["correct"] = (
                row["scored"]
                and value.get("support") == "supported"
                and value.get("relation") in case["allowed_relations"]
            )
        rows.append(row)
    write("analysis/pilots.json", rows)
    return rows


def mechanism() -> dict[str, Any]:
    roles: dict[str, dict[str, Any]] = {}
    a = c.accounting()
    for cfg in c.all_configs():
        if cfg.stage != "adaptation":
            continue
        key = cfg.arm + "/" + cfg.role
        row = roles.setdefault(
            key,
            dict(
                jobs=0,
                complete=0,
                partial=0,
                absent=0,
                drafts=0,
                checks=0,
                rejected=0,
                executed=0,
                reviews=0,
                cost=0.0,
                diagnostics=[],
            ),
        )
        p = c.role_product(cfg)
        row["jobs"] += 1
        row["cost"] += a["costs"].get(c.name(cfg, None), 0)
        row[p.status if p else "absent"] += 1
        if p:
            row["drafts"] += len(p.drafts)
        if isinstance(p, WriterProduct):
            inherited = {
                pydantic_load(SnippetReceipt, x).identifier
                for x in c.read(cfg.input_file).get("receipts", [])
            }
            fresh = [r for r in p.receipts if r.identifier not in inherited]
            row["checks"] += len(fresh)
            row["rejected"] += sum(r.status == "rejected" for r in fresh)
            row["executed"] += sum(r.executable for r in fresh)
            row["reviews"] += len(p.reviews)
            row["diagnostics"].extend(
                dict(cell=c.name(cfg, None), message=d) for d in p.diagnostics
            )
    edits: list[dict[str, Any]] = []
    for path in sorted((c.CAMPAIGN / "revisions").rglob("*.json")):
        raw = json.loads(path.read_text())
        bank = {
            pydantic_load(SnippetReceipt, r).identifier: r
            for r in raw["writer"]["receipts"]
        }
        for edit in raw["edits"]:
            names = sorted(
                {bank[r]["context"]["theorem_name"] for r in edit["receipts"]}
            )
            edits.append(
                dict(
                    arm=path.parent.name,
                    batch=path.stem,
                    edit=edit,
                    sources={
                        n: c.read(f"sources/{n}.json")["terminal"]["status"]
                        for n in names
                    },
                    revision=str(path.relative_to(c.ROOT)),
                )
            )
    return dict(roles=roles, edits=edits)


def report() -> None:
    c.verify()
    a = c.accounting()
    rows = proof_rows()
    metrics: dict[str, Any] = {}
    for stage in ("training", "validation"):
        for arm in ("A", "B"):
            if any(r["stage"] == stage and r["arm"] == arm for r in rows):
                metrics[stage + "/" + arm] = paired(stage, arm, rows)
    proof_detail: list[dict[str, Any]] = []
    for row in rows:
        evidence = trace(Path(row["folder"]), row["book"])
        key = f"{row['stage']}_{row['arm']}_{row['theorem']}_{row['seed']}"
        detail = {k: v for k, v in row.items() if k not in ("book", "folder")}
        detail.update(
            requests=evidence["requests"],
            book_exposures=evidence["book_exposures"],
            trace_file=f"analysis/traces/{key}.json",
        )
        write(detail["trace_file"], evidence)
        proof_detail.append(detail)
    write("analysis/proof_cells.json", proof_detail)
    with (c.CAMPAIGN / "cells.csv").open("w") as out:
        fields = [
            "stage",
            "arm",
            "theorem",
            "seed",
            "success",
            "qualified",
            "platform_failed",
            "cost",
            "cost_per_cell_uncached",
            "requests",
            "book_exposures",
            "result",
            "trace_file",
        ]
        writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(proof_detail)
    pilot_evidence()
    funnel = mechanism()
    write("analysis/mechanism.json", funnel)
    sensitivity: dict[str, dict[str, float]] = defaultdict(
        lambda: dict(actual=0.0, uncached_same_tokens=0.0)
    )
    for row in rows:
        s = sensitivity[row["stage"] + "/" + row["arm"]]
        s["actual"] += row["cost"]
        s["uncached_same_tokens"] += row["cost_per_cell_uncached"]
    prep = {
        arm: sum(
            a["costs"].get(c.name(j, None), 0)
            for j in c.all_configs()
            if j.stage == "adaptation" and j.arm == arm
        )
        for arm in ("A", "B")
    }
    totals = dict(
        new_charges=a["total"],
        ceiling=30,
        receipts=a["receipts"],
        unresolved=a["unresolved"],
        billing_issues=a["billing_issues"],
        preparation=prep,
        original_preparation_cost=0.45092992,
        note="Marginal adaptation excludes reused v2 reflector/source costs; historical preparation is a separate sunk resource, not a new charge.",
    )
    write("analysis/metrics.json", metrics)
    write("analysis/accounting.json", a)
    write(
        "analysis/economics.json", dict(totals=totals, sensitivity=sensitivity)
    )
    lines = [
        "# ACE learning campaign: measured results",
        "",
        f"New API charges: **${a['total']:.8f} / $30**; {a['receipts']} receipts, {len(a['unresolved'])} unresolved.",
        "",
        "Historical v2 controls: 40 trainX cells, 80 validationX cells. Validation is development data. Generator/controller unchanged; only learned books differ. No default promotion.",
        "",
        "| Panel/arm | v2 solves | Candidate solves | v2 cost | Candidate cost | Solve p |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, m in metrics.items():
        lines.append(
            f"| {key} | {m['solved_a']}/{m['cells']} | {m['solved_b']}/{m['cells']} | ${m['cost_a']:.6f} | ${m['cost_b']:.6f} | {m['p_two_sided']:.4f} |"
            if m["complete"]
            else f"| {key} | incomplete | no verdict | — | — | — |"
        )
    lines.extend(
        [
            "",
            "Every proof cell, including failures, is in [cells.csv](cells.csv). Raw-request and verifier evidence is indexed in [proof_cells.json](analysis/proof_cells.json). Family-clustered 90% intervals and cost tests are in [metrics.json](analysis/metrics.json); pilot judgments and role products are in [pilots.json](analysis/pilots.json).",
            "",
            "[Mechanism](analysis/mechanism.json) lists retained edits with source receipts. [Economics](analysis/economics.json) separates preparation and uncached-token sensitivity. Exposure proves that a book was dispatched; it does not prove that a rule caused a solve.",
        ]
    )
    (c.CAMPAIGN / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(dict(new_charges=a["total"], metrics=metrics)))
