"""Numerical report tables derived from the complete certified study."""

from collections import defaultdict
import csv
import math
from typing import Any

from .analysis import metrics
from .common import REPORT, read, save
from .cost_bounds import interval as cost_interval
from .reporting import ARM_NAMES, group_order, inputs


def csv_table(name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Cannot export an empty table")
    with (REPORT / name).open("w", newline="") as stream:
        fields = list(dict.fromkeys(k for row in rows for k in row))
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def interval(pair: list[float]) -> str:
    return f"[{100 * pair[0]:.1f}, {100 * pair[1]:.1f}]"


def serving(data: dict[str, Any]) -> None:
    table: list[dict[str, Any]] = []
    markdown = [
        "## Full-panel serving results",
        "",
        "Each row contains forty problems and two paid replicates. Costs",
        "include every failed attempt. Solves and cost per forty are averages",
        "over the two replicates; the underlying totals are preserved in CSV.",
        "Online rows report solver inference only; their update bills appear",
        "separately. Their two replicates are sequential learning orders,",
        "so theorem-bootstrap intervals are descriptive: they do not model",
        "dependence propagated through the changing book. R1 is a manual",
        "trainX diagnostic. These are reused",
        "development partitions, with no untouched confirmation claim.",
        "",
    ]
    if any("cost_interval" in m for m in data["metrics"].values()):
        markdown += [
            "One trainX B1 timeout has an unknown bill with a retained upper",
            "bound: its cost and saving are ranges. Scalar CSV costs use the",
            "upper liability; affected uncertainty intervals cover both billing",
            "endpoints, and their cost p-values are omitted.",
            "",
        ]
    for stage in ("train", "validation"):
        markdown += [
            "### " + stage + "X",
            "",
            "| Arm | Solved / 40 | Cost / 40 | Cost / solve | Saving vs matched control |",
            "|---|---:|---:|---:|---:|",
        ]
        for key in sorted(data["metrics"], key=group_order):
            if not key.startswith(stage + "/"):
                continue
            arm = key.split("/")[1]
            m = data["metrics"][key]
            cost_lo, cost_hi = cost_interval(m)
            comparison = data["comparisons"].get(key)
            row: dict[str, Any] = dict(
                stage=stage,
                arm=arm,
                description=ARM_NAMES[arm],
                n=m["n"],
                solves=m["solves"],
                mean_solves_per_40=m["solves"] / (m["n"] / 40),
                all_attempt_cost=m["cost"],
                all_attempt_cost_lower=cost_lo,
                all_attempt_cost_upper=cost_hi,
                invoice_exact=cost_lo == cost_hi,
                mean_cost_per_40=m["cost"] / (m["n"] / 40),
                cost_per_solve=m["cost_per_solve"],
                requests=m["requests"],
                failed_cost=m["failed_cost"],
                baseline="",
                solve_difference_per_40="",
                saving="",
                saving_lower="",
                saving_upper="",
                saving_ci90_low="",
                saving_ci90_high="",
                family_saving_ci90_low="",
                family_saving_ci90_high="",
                theorem_cost_sign_flip_p="",
                leave_one_theorem_out_low="",
                leave_one_theorem_out_high="",
                practical_target="",
            )
            saving = "—"
            if comparison is not None:
                pair = comparison["theorem"]
                family = comparison["family"]
                if not pair["complete"] or not family["complete"]:
                    raise ValueError("Incomplete report comparison")
                row.update(
                    baseline=comparison["baseline"],
                    solve_difference_per_40=40 * pair["coverage_delta"],
                    saving=pair["saving"],
                    saving_ci90_low=pair["saving_ci90"][0],
                    saving_ci90_high=pair["saving_ci90"][1],
                    family_saving_ci90_low=family["saving_ci90"][0],
                    family_saving_ci90_high=family["saving_ci90"][1],
                    theorem_cost_sign_flip_p=pair["two_sided_sign_flip_p"],
                    leave_one_theorem_out_low=pair[
                        "leave_one_cluster_out_saving"
                    ][0],
                    leave_one_theorem_out_high=pair[
                        "leave_one_cluster_out_saving"
                    ][1],
                    practical_target=pair["practical_target"],
                )
                saving = f"{100 * pair['saving']:+.1f}%"
                lo, hi = pair.get("saving_interval", [pair["saving"]] * 2)
                row.update(saving_lower=lo, saving_upper=hi)
                if lo != hi:
                    saving = f"[{100 * lo:+.1f}, {100 * hi:+.1f}]%"
            table.append(row)
            cps = m["cost_per_solve"]
            cps_text = "—" if cps is None else f"${cps:.4f}"
            cost_text = f"${row['mean_cost_per_40']:.4f}"
            if cost_lo != cost_hi:
                cost_text = f"${cost_lo / 2:.4f}–${cost_hi / 2:.4f}"
                cps_text = (
                    f"${cost_lo / m['solves']:.4f}–${cost_hi / m['solves']:.4f}"
                    if m["solves"]
                    else "—"
                )
            markdown.append(
                f"| {arm}: {ARM_NAMES[arm]} | {row['mean_solves_per_40']:.1f}"
                f" | {cost_text} | {cps_text} | {saving} |"
            )
        markdown.append("")
    markdown += [
        "### Paired uncertainty",
        "",
        "Intervals are percentages. Theorem clustering retains both",
        "replicates; broader proof-method families provide a sensitivity",
        "analysis. Positive savings mean ACE is cheaper. Intervals and",
        "unadjusted sign-flip p-values describe uncertainty, not a promotion",
        "gate. The CSV also supplies leave-one-theorem-out sensitivity.",
        "",
        "| Partition / arm | Saving | Theorem 90% interval | Family 90% interval |",
        "|---|---:|---:|---:|",
    ]
    for row in table:
        if row["saving"] == "":
            continue
        saving = f"{100 * row['saving']:+.1f}%"
        if row["saving_lower"] != row["saving_upper"]:
            saving = interval([row["saving_lower"], row["saving_upper"]])
        markdown.append(
            f"| {row['stage']}X / {row['arm']} | {saving}"
            f" | {interval([row['saving_ci90_low'], row['saving_ci90_high']])}"
            f" | {interval([row['family_saving_ci90_low'], row['family_saving_ci90_high']])} |"
        )
    csv_table("serving_results.csv", table)
    (REPORT / "serving_tables.md").write_text("\n".join(markdown) + "\n")
    groups: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(
        list
    )
    for row in data["rows"]:
        groups[row["stage"], row["arm"], row["seed"]].append(row)
    replicate_rows: list[dict[str, Any]] = []
    for (stage, arm, seed), rows in sorted(groups.items()):
        m = metrics([dict(r, turns=[]) for r in rows])
        m["large_context_requests"] = sum(
            r["trace_summary"]["long_context_requests"] for r in rows
        )
        if m["n"] != 40:
            raise ValueError("Incomplete replicate in serving table")
        replicate_rows.append(dict(stage=stage, arm=arm, seed=seed, **m))
    csv_table("serving_replicates.csv", replicate_rows)


def budget() -> None:
    data = read(REPORT / "budget_replay_results.json")
    preparation = read(REPORT / "final_economics.json")["recipes"]
    if data["scenarios"] != 4560 or data["paid_calls"] != 0:
        raise ValueError("Budget replay is not complete")
    table: list[dict[str, Any]] = []
    for key, m in sorted(data["metrics"].items()):
        stage, arm, cap_text = key.split("/")
        baseline = "B0" if arm.startswith("B") else "A0"
        same = data["metrics"][f"{stage}/{baseline}/{cap_text}"]
        full = data["metrics"][f"{stage}/{baseline}/0.1"]
        lo, hi = cost_interval(m)
        point = dict(
            stage=stage,
            arm=arm,
            stopping_allowance=float(cap_text),
            n=m["n"],
            solves=m["solves"],
            mean_solves_per_40=m["solves"] / 2,
            all_attempt_cost=m["cost"],
            all_attempt_cost_lower=lo,
            all_attempt_cost_upper=hi,
            invoice_exact=lo == hi,
            mean_cost_per_40=m["cost"] / 2,
            cost_per_solve=m["cost_per_solve"],
            baseline=baseline,
            saving_vs_same_cap=1 - m["cost"] / same["cost"],
            saving_vs_same_cap_interval=[
                1 - hi / same["cost"],
                1 - lo / same["cost"],
            ],
            solve_difference_vs_same_cap=(m["solves"] - same["solves"]) / 2,
            saving_vs_ordinary_ten_cents=1 - m["cost"] / full["cost"],
            saving_vs_ordinary_ten_cents_interval=[
                1 - hi / full["cost"],
                1 - lo / full["cost"],
            ],
            solve_difference_vs_ordinary_ten_cents=(
                m["solves"] - full["solves"]
            )
            / 2,
            dominated_by_a_matched_nonace_budget=False,
        )
        controls = [
            value
            for name, value in data["metrics"].items()
            if name.startswith(f"{stage}/{baseline}/")
        ]
        point["dominated_by_a_matched_nonace_budget"] = any(
            control["cost"] <= lo
            and control["solves"] >= m["solves"]
            and (control["cost"] < lo or control["solves"] > m["solves"])
            for control in controls
        )
        recipe = preparation.get(arm)
        prep_cost = (
            recipe["preparation_cost"]
            if recipe is not None
            else 0.0
            if arm in ("A0", "B0")
            else None
        )
        unit_saving = (same["cost"] - m["cost"]) / m["n"]
        target_margin = (0.9 * same["cost"] - m["cost"]) / m["n"]
        point.update(
            preparation_cost=prep_cost,
            cost_including_preparation_at_measured_n=(
                m["cost"] + prep_cost if prep_cost is not None else None
            ),
            cost_including_preparation_interval=(
                [lo + prep_cost, hi + prep_cost]
                if prep_cost is not None
                else None
            ),
            break_even_problems_at_same_cap=(
                math.ceil(prep_cost / unit_saving)
                if prep_cost is not None and unit_saving > 0
                else None
            ),
            problems_for_ten_percent_total_saving_at_same_cap=(
                math.ceil(prep_cost / target_margin)
                if prep_cost is not None and target_margin > 0
                else None
            ),
        )
        table.append(point)
    csv_table("budget_frontier.csv", table)
    save(
        REPORT / "budget_frontier.json",
        dict(
            rows=table,
            meaning="Conditional on the observed responses and cache charges. Compare both equal stopping allowances and the ordinary baseline's complete budget frontier. A joint ACE+budget gain is not automatically an ACE effect. Preparation payback assumes the same observed average costs recur with a fixed book and no further learning; it is arithmetic, not a guarantee or a forecast for unseen problems. Unknown historical preparation is left null.",
        ),
    )


def run() -> None:
    data = inputs()
    serving(data)
    budget()
    print(
        "Exported complete serving, replicate, uncertainty and budget tables"
    )


if __name__ == "__main__":
    run()
