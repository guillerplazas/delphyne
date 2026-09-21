"""Preparation, online operating cost, and amortization from paid receipts."""

from collections import Counter
import json
import math
import sqlite3
from typing import Any

from .common import CAMPAIGN, REPORT, read, save
from .cost_bounds import interval, receipt_interval


def ledger_rows() -> list[dict[str, Any]]:
    with sqlite3.connect(CAMPAIGN / "ledger.sqlite3") as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute("SELECT * FROM receipts")]


def paid(rows: list[dict[str, Any]]) -> dict[str, Any]:
    bounds = [receipt_interval(r) for r in rows]
    result: dict[str, Any] = dict(
        requests=len(rows),
        cost=sum(hi for _, hi in bounds),
        models=dict(Counter(r["model"] for r in rows)),
    )
    lower = sum(lo for lo, _ in bounds)
    if lower != result["cost"]:
        result.update(
            cost_interval=[lower, result["cost"]],
            cost_is_exact=False,
            bounded_receipts=[
                r["id"] for r in rows if r["status"] == "bounded_charge"
            ],
            settled_receipts=sum(r["status"] == "settled" for r in rows),
            billing_note="Cost is retained upper liability; cost_interval bounds the unknown invoice. Settled receipt charges are exact.",
        )
    return result


def preparation() -> None:
    rows = ledger_rows()
    protocol = read(CAMPAIGN / "full_learning_protocol.json")
    pilot_names = read(CAMPAIGN / "ladder_v2_protocol.json")["train_panel"]
    recipes: dict[str, Any] = {}
    for arm in ("A2", "B1", "B2", "S1", "P1"):
        source_arm = (
            "source_plain" if arm.startswith("B") else "source_assisted"
        )
        names = pilot_names if arm == "P1" else protocol["order"]
        sources = {f"train__{source_arm}__{t}__seed0" for t in names}
        source = paid([r for r in rows if r["cell"] in sources])
        prefix = "ladder_v2__sol_medium__" if arm == "P1" else f"full_{arm}__"
        authors = paid([r for r in rows if r["cell"].startswith(prefix)])
        book_file = (
            "ladder_v2__sol_medium.json"
            if arm == "P1"
            else f"{arm}_frozen.json"
        )
        book = read(CAMPAIGN / "books" / book_file)
        refined: Counter[str] = Counter()
        for path in (CAMPAIGN / "learning_events").glob(
            f"full_{arm}__*terminal*"
        ):
            event = read(path)
            refined.update(
                {
                    k: len(v)
                    for k, v in event["applied"].items()
                    if k != "playbook"
                }
            )
        recipes[arm] = dict(
            source=source,
            authors=authors,
            preparation_cost=source["cost"] + authors["cost"],
            incremental_if_sources_already_available=authors["cost"],
            source_theorems=len(names),
            bullets=len(book["playbook"]["bullets"]),
            characters=len(book["text"]),
            refinement_operations=dict(refined),
        )
    completion = [
        check
        for theorem in protocol["order"]
        for check in read(
            CAMPAIGN / "evidence" / f"teacher_plain_v2__{theorem}.json"
        )["training_only_completion"]
    ]
    save(
        REPORT / "preparation_economics.json",
        dict(
            recipes=recipes,
            completion_teacher=dict(
                checks=len(completion),
                measured_seconds=sum(c.get("seconds", 0) for c in completion),
                api_cost=0,
                note="Measured wall time of completion/check/compilation operations, not billed CPU time; machine cost is not priced.",
            ),
            note="Per-recipe preparation includes its required fixed Luna source trajectories and all author/refinement requests. The study reuses sources across recipes; do not sum these per-recipe totals to obtain the study bill. P1 uses the selected eight-source v2 Sol book without the later forty-source refinement. Historical A1 preparation is not silently assigned zero.",
        ),
    )
    print(json.dumps(recipes, indent=2))


def finalize() -> None:
    rows = ledger_rows()
    overall = paid(rows)
    results = read(REPORT / "fresh_results.json")
    prep = read(REPORT / "preparation_economics.json")["recipes"]
    adaptive = read(REPORT / "adaptive_frozen_results.json")
    repaired = read(REPORT / "rule_repair_results.json")
    for stage, values in adaptive["metrics"].items():
        results["metrics"][f"{stage}/O1"] = values
    results["metrics"]["train/R1"] = repaired["metrics"]
    adaptive_book = read(CAMPAIGN / "books/O1_adaptive_frozen.json")
    prep["O1"] = dict(
        source=adaptive["preparation"]["source"],
        authors=adaptive["preparation"]["authors"],
        preparation_cost=adaptive["preparation"]["total_cost"],
        source_theorems=40,
        bullets=len(adaptive_book["playbook"]["bullets"]),
        characters=len(adaptive_book["text"]),
        note="One adaptive curriculum, order0, including all40 Generator trajectories and subsequent learning calls. No extra terminal audits.",
    )
    repaired_book = read(CAMPAIGN / "books/R1_verified_rules.json")
    prep["R1"] = dict(
        **prep["A2"],
        note="Same paid A2 preparation, followed by three manual rule repairs and zero-API synthetic checks. Human review and machine time are not assigned a monetary tariff.",
    )
    prep["R1"]["characters"] = len(repaired_book["text"])
    amortization: dict[str, Any] = {}
    for stage in ("train", "validation"):
        for arm, recipe in prep.items():
            if f"{stage}/{arm}" not in results["metrics"]:
                continue
            baseline = "B0" if arm.startswith("B") else "A0"
            base = results["metrics"][f"{stage}/{baseline}"]
            current = results["metrics"][f"{stage}/{arm}"]
            unit_saving = (base["cost"] - current["cost"]) / base["n"]
            unit_target_margin = (0.9 * base["cost"] - current["cost"]) / base[
                "n"
            ]
            prep_cost = recipe["preparation_cost"]
            amortization[f"{stage}/{arm}"] = dict(
                baseline=baseline,
                inference_saving_per_problem=unit_saving,
                preparation_cost=prep_cost,
                break_even_problems=math.ceil(prep_cost / unit_saving)
                if unit_saving > 0
                else None,
                problems_for_ten_percent_total_saving=math.ceil(
                    prep_cost / unit_target_margin
                )
                if unit_target_margin > 0
                else None,
                cost_including_prep_at_measured_n=current["cost"] + prep_cost,
                saving_including_prep_at_measured_n=1
                - (current["cost"] + prep_cost) / base["cost"],
                assumptions="Observed panel-average serving costs recur; same fixed book and no further learning. Point estimates, not guaranteed future returns.",
            )
            lo, hi = interval(current)
            if lo != hi:
                amortization[f"{stage}/{arm}"].update(
                    inference_saving_per_problem_interval=[
                        (base["cost"] - hi) / base["n"],
                        (base["cost"] - lo) / base["n"],
                    ],
                    cost_including_prep_at_measured_n_interval=[
                        lo + prep_cost,
                        hi + prep_cost,
                    ],
                    saving_including_prep_at_measured_n_interval=[
                        1 - (hi + prep_cost) / base["cost"],
                        1 - (lo + prep_cost) / base["cost"],
                    ],
                    billing_note="Unknown timeout bill retained as an interval; scalar costs and payback use its conservative upper liability.",
                )
    online: dict[str, Any] = {}
    for arm in ("A2", "B1", "B2"):
        learning = paid(
            [
                r
                for r in rows
                if r["cell"].startswith("online-o")
                and f"__{arm}__" in r["cell"]
            ]
        )
        inference = results["metrics"][f"train/online_{arm}"]
        baseline = results["metrics"][
            "train/" + ("B0" if arm.startswith("B") else "A0")
        ]
        total = inference["cost"] + learning["cost"]
        online[arm] = dict(
            learning=learning,
            inference=inference,
            operational_cost=total,
            operational_cost_per_solve=total / inference["solves"]
            if inference["solves"]
            else None,
            baseline_cost=baseline["cost"],
            operational_saving=1 - total / baseline["cost"],
            note="All forty updates per order, including the terminal update, are paid operational cost. No frozen-training fee is added to an empty-start online curriculum.",
        )
    stages = {
        s: paid([r for r in rows if r["stage"] == s])
        for s in sorted({r["stage"] for r in rows})
    }
    save(
        REPORT / "final_economics.json",
        dict(
            overall=overall,
            stages=stages,
            recipes=prep,
            amortization=amortization,
            online=online,
            note="The overall bill includes source collection, discarded learning variants, parser/evidence diagnostics, author selection, and all registered benchmarks. Recipe payback does not pretend this whole research expenditure recurs at deployment.",
        ),
    )
    print(json.dumps(overall))


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["preparation"]:
        preparation()
    elif sys.argv[1:] == ["finalize"]:
        finalize()
    else:
        raise SystemExit("Use preparation or finalize")
