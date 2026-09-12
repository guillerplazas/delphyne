"""Explicit-inventory analysis of the capacity campaign; no API calls.

Never scan a mixed historical run: each reused cell is named and hashed by
the development-only reference manifest. Continuation costs include the
paid prefix once, while campaign accounting charges only new dispatches.
"""

# ruff: noqa: E402
from runtime.development_only import install

install()

from collections import Counter, defaultdict
from dataclasses import asdict, replace
import json
from pathlib import Path
import re
import sys
from typing import Any, cast

import numpy as np
import yaml

from experiments.ace import ace_capacity_experiment as c
from runtime.model_registry import price_tokens
from tools.analysis import paired_evaluation as paired
from tools.analysis.cell_records import (
    _field,  # pyright: ignore[reportPrivateUsage]
    _result_head,  # pyright: ignore[reportPrivateUsage]
)
from tools.reports.ace_attribution_report import cache_diagnosis


def read_cell(directory: Path, model: str) -> dict[str, Any]:
    status = c.ol.ground_truth(directory)
    exceptions = {
        p.name: p.read_text() for p in directory.glob("exception*.txt")
    }
    administrative = any("CampaignExhausted" in s for s in exceptions.values())
    row: dict[str, Any] = dict(
        source=str(directory.relative_to(c.ROOT)),
        status=status,
        administrative=administrative,
        failed=status == "failed",
        solved=False,
        model=model,
        cost=0.0,
        token_cost=0.0,
        input_tokens=0,
        cached_input_tokens=0,
        output_tokens=0,
        requests=0,
        rocq_seconds=0,
        exceptions=exceptions,
    )
    if status == "done":
        head = _result_head(directory / "result.yaml")
        row["solved"] = _field(head, "success") == "true"
        budget = head[head.find("spent_budget:") :]
        for key in (
            "input_tokens",
            "cached_input_tokens",
            "output_tokens",
            "rocq_seconds",
        ):
            row[key] = float(_field(budget, key) or 0)
        row["requests"] = int(float(_field(budget, "num_completions") or 0))
        row["token_cost"] = price_tokens(
            model,
            int(row["input_tokens"]),
            int(row["cached_input_tokens"]),
            int(row["output_tokens"]),
        )
        row["cost"] = row["token_cost"]
    elif status == "failed" and (directory / "cache.yaml").exists():
        # The launcher preserves the partial cache after a platform failure.
        # Include its paid prefix in token sensitivity and verifier totals.
        entries: list[dict[str, Any]] = yaml.load(
            (directory / "cache.yaml").read_text(), Loader=yaml.CSafeLoader
        )
        totals: Counter[str] = Counter()
        for entry in entries:
            response: dict[str, Any] = entry.get("output") or {}
            values: dict[str, float] = response.get("budget", {}).get(
                "values", {}
            )
            totals.update(values)
        for key in (
            "input_tokens",
            "cached_input_tokens",
            "output_tokens",
            "rocq_seconds",
        ):
            row[key] = totals[key]
        row["requests"] = int(totals["num_completions"])
        row["token_cost"] = price_tokens(
            model,
            int(row["input_tokens"]),
            int(row["cached_input_tokens"]),
            int(row["output_tokens"]),
        )
        row["cost"] = row["token_cost"]
        # Compute elapsed charges live outside the compute cache response.
        # The terminal observer, unlike that response, has the full charge.
        for event in events_by_cell().get(directory.name, []):
            if event["kind"] == "terminal_v2":
                row["rocq_seconds"] = event["spent"].get("rocq_seconds", 0)
    return row


def events_by_cell() -> dict[str, list[dict[str, Any]]]:
    events: dict[str, list[dict[str, Any]]] = defaultdict(list)
    path = c.CAMPAIGN / "events.jsonl"
    if path.exists():
        with path.open() as f:
            for line in f:
                e = json.loads(line)
                events[e["cell"]].append(e)
    return dict(events)


def diagnostics(
    directory: Path, events: list[dict[str, Any]]
) -> dict[str, Any]:
    details = cache_diagnosis(directory)
    details["terminal"] = [e for e in events if e["kind"] == "terminal_v2"]
    details["declined"] = [
        e for e in events if e["kind"] == "admission_v2" and not e["admitted"]
    ]
    details["estimates"] = [e for e in events if e["kind"] == "estimate_v2"]
    details["snapshots"] = dict(
        Counter(e["decision"] for e in events if e["kind"] == "transport")
    )
    if not (directory / "cache.yaml").exists():
        return details
    entries: list[dict[str, Any]] = yaml.load(
        (directory / "cache.yaml").read_text(), Loader=yaml.CSafeLoader
    )
    views: list[dict[str, Any]] = []
    for entry in entries:
        req = entry["input"]["request"]
        if req["options"].get("model") != "__compute__":
            continue
        response: dict[str, Any] = entry.get("output") or {}
        answers: list[dict[str, Any]] = response.get("outputs") or []
        if not answers:
            continue
        text = str(answers[0].get("content", ""))
        if "obligations_status" in text:
            views.append(
                dict(computation=req["chat"][-1]["content"], result=text)
            )
    details["obligation_views"] = views
    return details


def metric(rows: list[dict[str, Any]], cap: float) -> dict[str, Any]:
    complete = all(
        r["status"] in ("done", "failed") and not r["administrative"]
        for r in rows
    )
    total = sum(r["cost"] for r in rows)
    solves = sum(
        r["solved"] and not r["failed"] and r["cost"] <= cap + 1e-8
        for r in rows
    )
    inp = sum(r["input_tokens"] for r in rows)
    cached = sum(r["cached_input_tokens"] for r in rows)
    output = sum(r["output_tokens"] for r in rows)
    return dict(
        complete=complete,
        cells=len(rows),
        qualified_solves=solves,
        raw_solves=sum(r["solved"] for r in rows),
        cost=total,
        cost_per_solve=total / solves if solves else None,
        cap=cap,
        input_tokens=inp,
        cached_input_tokens=cached,
        output_tokens=output,
        requests=sum(r["requests"] for r in rows),
        cached_share=cached / inp if inp else None,
        failed=sum(r["failed"] for r in rows),
        administrative=sum(r["administrative"] for r in rows),
        uncached_cost=sum(
            price_tokens(
                r["model"], int(r["input_tokens"]), 0, int(r["output_tokens"])
            )
            for r in rows
        ),
        luna_rate_cost=sum(
            price_tokens(
                c.old.LUNA,
                int(r["input_tokens"]),
                int(r["cached_input_tokens"]),
                int(r["output_tokens"]),
            )
            for r in rows
        ),
    )


def compare(
    a: list[dict[str, Any]],
    b: list[dict[str, Any]],
    cap_a: float,
    cap_b: float,
) -> dict[str, Any]:
    if any(
        r["status"] not in ("done", "failed") or r["administrative"]
        for r in [*a, *b]
    ):
        return dict(complete=False, verdict="incomplete")
    oa = {
        (r["theorem"], "0"): paired.Observation(
            r["solved"], r["cost"], r["failed"]
        )
        for r in a
    }
    ob = {
        (r["theorem"], "0"): paired.Observation(
            r["solved"], r["cost"], r["failed"]
        )
        for r in b
    }
    expected = sorted(oa)
    result = paired.compare(
        oa,
        ob,
        expected,
        families=c.read("families.json"),
        cap_a=cap_a,
        cap_b=cap_b,
    )
    result["cost_p_two_sided"] = paired.cost_cluster_p(
        oa, ob, expected, c.read("families.json")
    )
    result["gains"] = [
        k[0]
        for k in expected
        if ob[k].solved
        and ob[k].cost <= cap_b
        and not (oa[k].solved and oa[k].cost <= cap_a)
    ]
    result["losses"] = [
        k[0]
        for k in expected
        if oa[k].solved
        and oa[k].cost <= cap_a
        and not (ob[k].solved and ob[k].cost <= cap_b)
    ]
    return result


def interaction(
    groups: dict[str, list[dict[str, Any]]], book: str, level: int = 0
) -> dict[str, Any]:
    models = (c.old.LUNA, c.old.TERRA)
    selected = [groups[f"{m}/{b}"] for m in models for b in ("none", book)]
    if any(
        not metric(
            rows,
            (0.1 if rows[0]["model"] == c.old.LUNA else 1)
            * (2 if level else 1),
        )["complete"]
        for rows in selected
    ):
        return dict(complete=False)
    cells = [{r["theorem"]: r for r in rows} for rows in selected]
    expected = set(cells[0])
    assert all(set(x) == expected for x in cells)
    families = c.read("families.json")
    blocks: dict[str, list[float]] = defaultdict(lambda: [0, 0])
    for theorem in sorted(expected):
        yes = [
            int(
                v[theorem]["solved"]
                and not v[theorem]["failed"]
                and v[theorem]["cost"]
                <= (0.1 if i < 2 else 1) * (2 if level else 1) + 1e-8
            )
            for i, v in enumerate(cells)
        ]
        blocks[families[theorem]][0] += (yes[3] - yes[2]) - (yes[1] - yes[0])
        blocks[families[theorem]][1] += 1
    values = np.asarray(list(blocks.values()))
    rng = np.random.default_rng(20260912)
    samples = values[rng.integers(0, len(values), (10000, len(values)))].sum(
        axis=1
    )
    return dict(
        complete=True,
        effect=float(values[:, 0].sum() / len(expected)),
        ci90=cast(
            Any, np.quantile(samples[:, 0] / samples[:, 1], [0.05, 0.95])
        ).tolist(),
        p_two_sided=paired.exact_cluster_p([int(v[0]) for v in values]),
        cells_per_arm=len(expected),
        families=len(values),
        caveat="Same book across solvers; development data and finite search allowances. Crossover includes historical controls.",
    )


def crossover() -> tuple[dict[str, Any], dict[str, Any]]:
    costs = c.accounting()["cells"]
    all_events = events_by_cell()
    rows: list[dict[str, Any]] = []
    details: dict[str, Any] = {}
    for ref in c.read("references.json"):
        directory = c.ROOT / ref["source"]
        for file, sha in ref["hashes"].items():
            assert c.old.digest(directory / file) == sha
        row = read_cell(directory, ref["model"]) | {
            k: ref[k] for k in ("theorem", "book")
        }
        row["historical"] = True
        rows.append(row)
    for raw in c.read("planned_cross.json"):
        cfg = c.ProofConfig(**raw)
        row = read_cell(cfg.directory(), cfg.model)
        row.update(
            theorem=cfg.theorem,
            book=cfg.book,
            historical=False,
            new_charge=costs.get(cfg.identifier(), 0.0),
        )
        row["cost"] = row["new_charge"]
        rows.append(row)
    groups = {
        f"{m}/{b}": [r for r in rows if r["model"] == m and r["book"] == b]
        for m in (c.old.LUNA, c.old.TERRA)
        for b in ("none", "luna", "terra")
    }
    assert all(
        len(v) == 40 and len({r["theorem"] for r in v}) == 40
        for v in groups.values()
    )
    comparisons: dict[str, Any] = {}
    for model in (c.old.LUNA, c.old.TERRA):
        cap = 0.1 if model == c.old.LUNA else 1
        for a, b in (("none", "luna"), ("none", "terra"), ("luna", "terra")):
            comparisons[f"{model}/{a}->{b}"] = compare(
                groups[f"{model}/{a}"], groups[f"{model}/{b}"], cap, cap
            )
    author_keys = [f"{m}/luna->terra" for m in (c.old.LUNA, c.old.TERRA)]
    if all(comparisons[k].get("complete") for k in author_keys):
        previous = 0.0
        for i, key in enumerate(
            sorted(author_keys, key=lambda k: comparisons[k]["p_two_sided"])
        ):
            previous = max(
                previous, min(1.0, (2 - i) * comparisons[key]["p_two_sided"])
            )
            comparisons[key]["p_holm_book_author"] = previous
    for row in rows:
        key = f"{row['model']}/{row['book']}/{row['theorem']}"
        source = c.ROOT / row["source"]
        details[key] = diagnostics(source, all_events.get(source.name, []))
        details[key]["observation"] = row
    result = dict(
        rows=rows,
        groups={
            k: metric(v, 0.1 if k.startswith(c.old.LUNA) else 1)
            for k, v in groups.items()
        },
        comparisons=comparisons,
        primary_interaction=interaction(groups, "luna"),
        secondary_interaction_terra_book=interaction(groups, "terra"),
    )
    return result, details


def mechanism_rows(
    level: int, costs: dict[str, float]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in c.read("planned_mechanisms.json"):
        cfg = c.ProofConfig(**raw)
        if level and cfg.profile not in ("C", "E"):
            continue
        cfg = replace(cfg, level=level)
        carried = c.CAMPAIGN / "carried" / f"{cfg.identifier()}.json"
        source = (
            c.ROOT / json.loads(carried.read_text())["source"]
            if carried.exists()
            else cfg.directory()
        )
        row = read_cell(source, cfg.model)
        total = sum(
            costs.get(replace(cfg, level=n).identifier(), 0.0)
            for n in range(level + 1)
        )
        row.update(
            theorem=cfg.theorem,
            book=cfg.book,
            profile=cfg.profile,
            level=level,
            cost=total,
            new_charge=costs.get(cfg.identifier(), 0.0),
            carried=carried.exists(),
            identifier=cfg.identifier(),
        )
        rows.append(row)
    return rows


def mechanisms() -> tuple[dict[str, Any], dict[str, Any]]:
    costs = c.accounting()["cells"]
    events = events_by_cell()
    results: dict[str, Any] = {}
    details: dict[str, Any] = {}
    all_rows = {level: mechanism_rows(level, costs) for level in (0, 1, 2)}
    for level, rows in all_rows.items():
        groups = {
            f"{m}/{p}": [
                r for r in rows if r["model"] == m and r["profile"] == p
            ]
            for m in (c.old.LUNA, c.old.TERRA)
            for p in (c.PROFILES if not level else ("C", "E"))
        }
        comparisons: dict[str, Any] = {}
        for model in (c.old.LUNA, c.old.TERRA):
            cap = (0.1 if model == c.old.LUNA else 1) * (2 if level else 1)
            pairs = (
                (("A", "C"), ("B", "D"), ("D", "E"), ("C", "E"))
                if not level
                else (("C", "E"),)
            )
            for a, b in pairs:
                comparisons[f"{model}/{a}->{b}"] = compare(
                    groups[f"{model}/{a}"], groups[f"{model}/{b}"], cap, cap
                )
            if level:
                for p in ("C", "E"):
                    parent = [
                        r
                        for r in all_rows[level - 1]
                        if r["model"] == model and r["profile"] == p
                    ]
                    parent_cap = (0.1 if model == c.old.LUNA else 1) * (
                        2 if level > 1 else 1
                    )
                    comparisons[f"{model}/{p}/continuation"] = compare(
                        parent, groups[f"{model}/{p}"], parent_cap, cap
                    )
        by_book = {
            f"{m}/{b}": groups[f"{m}/{p}"]
            for m in (c.old.LUNA, c.old.TERRA)
            for p, b in (("C", "none"), ("E", "terra-fixed"))
        }
        results[str(level)] = dict(
            rows=rows,
            groups={
                k: metric(
                    v,
                    (0.1 if k.startswith(c.old.LUNA) else 1)
                    * (2 if level else 1),
                )
                for k, v in groups.items()
            },
            comparisons=comparisons,
            interaction=interaction(by_book, "terra-fixed", level),
        )
        for row in rows:
            source = c.ROOT / row["source"]
            d = diagnostics(source, events.get(source.name, []))
            d["observation"] = row
            details[row["identifier"]] = d
    return results, details


def role_audit() -> dict[str, Any]:
    costs = c.accounting()["cells"]
    rows: list[dict[str, Any]] = []
    for raw in c.read("planned_creation.json"):
        cfg = c.RoleConfig(**raw)
        source = c.OUTPUT / "creation/configs" / cfg.identifier()
        row = read_cell(source, cfg.model)
        row.update(
            asdict(cfg),
            output_source=str(source.relative_to(c.ROOT)),
            new_charge=costs.get(cfg.identifier(), 0),
            output=None,
        )
        row["cost"] = row["new_charge"]
        if row["status"] == "done":
            value = (
                c.old.adapt.load_reflection(source)
                if cfg.role == "reflector"
                else c.old.adapt.load_delta(source)
            )
            row["output"] = asdict(value) if value is not None else None
        text = json.dumps(row["output"], ensure_ascii=False)
        frozen_input = c.args_of(c.ROOT / cfg.source)["args"]
        input_text = json.dumps(frozen_input, ensure_ascii=False)
        ids = set(re.findall(r"rocq-\d+", text))
        available_ids = set(
            re.findall(r"rocq-\d+", str(frozen_input.get("playbook", "")))
        )
        row["unbound_citations"] = sorted(ids - available_ids)
        row["output_chars"] = len(text)
        row["input_chars"] = len(input_text)
        row["inline_examples"] = re.findall(r"`([^`\n]+)`", text)
        row["have_assignment_examples"] = [
            s for s in row["inline_examples"] if re.search(r"\bhave\b.*:=", s)
        ]
        row["code_candidates_new_to_input"] = [
            s for s in row["inline_examples"] if s not in input_text
        ]
        rows.append(row)
    assert len(rows) == 200
    groups: dict[str, Any] = {}
    for model in (c.old.LUNA, c.old.TERRA):
        for role in ("reflector", "curator", "reducer"):
            selected = [
                r for r in rows if r["model"] == model and r["role"] == role
            ]
            groups[f"{model}/{role}"] = dict(
                cells=len(selected),
                parsed=sum(r["output"] is not None for r in selected),
                cost=sum(r["cost"] for r in selected),
                requests=sum(r["requests"] for r in selected),
                output_chars=sum(r["output_chars"] for r in selected),
                unbound_citation_cells=sum(
                    bool(r["unbound_citations"]) for r in selected
                ),
                have_assignment_cells=sum(
                    bool(r["have_assignment_examples"]) for r in selected
                ),
            )
    return dict(
        rows=rows,
        groups=groups,
        caveat="Matched role inputs, not a new end-to-end adaptation. Novel code and citations require source checks; heuristic counts alone are not quality verdicts.",
    )


def main() -> None:
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    c.verify()
    cross, cross_details = crossover()
    if not all(g["complete"] for g in cross["groups"].values()):
        raise RuntimeError(
            "Crossover is incomplete; no verdict or frozen report"
        )
    c.save("crossover_report.json", cross)
    c.save("crossover_diagnostics.json", cross_details)
    print(json.dumps(cross["groups"], indent=2))
    if phase == "cross":
        return
    mechanism, mechanism_details = mechanisms()
    if not all(
        g["complete"]
        for level in mechanism.values()
        for g in level["groups"].values()
    ):
        raise RuntimeError(
            "Diagnostic/continuation panel is incomplete; no verdict"
        )
    c.save("mechanism_report_v2.json", mechanism)
    c.save("mechanism_diagnostics_v2.json", mechanism_details)
    c.save("creation_audit.json", role_audit())
    c.save("report_accounting.json", c.accounting())


if __name__ == "__main__":
    main()
