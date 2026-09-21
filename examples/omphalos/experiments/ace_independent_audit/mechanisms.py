"""Cost contributions and observable trace mechanisms, without causal tags.

Counts of checks refer to distinct saved compute records. Reused compute
cache entries need not correspond one-to-one to verifier invocations.
No bullet is declared causal merely because a proof resembles its advice.
"""

from collections import Counter, defaultdict
import json
import re
from typing import Any

from .common import CAMPAIGN, REPORT, read, save
from .cost_bounds import interval, total_interval
from .economics import ledger_rows

ERRORS = (
    ("transport", r"transport failure"),
    ("memory_or_stack", r"stack overflow|out of memory|memoryerror"),
    ("timeout", r"timed? out|timeout|deadline|work.limit"),
    ("syntax", r"syntax error|parser error"),
    (
        "missing_name",
        r"not found|not a defined object|unknown.*(?:reference|tactic)",
    ),
    ("focus", r"focus|no such goal"),
    ("rewrite_shape", r"no.*(?:matching|subterm)|cannot find.*subterm"),
    (
        "type_or_unification",
        r"cannot unify|unable to unify|has type|expected.*type",
    ),
)


def characterize(row: dict[str, Any]) -> dict[str, Any]:
    failures: Counter[str] = Counter()
    sizes: list[int] = []
    for check in row["checks"]:
        feedback = check["feedback"]
        sizes.append(len(json.dumps(feedback, sort_keys=True)))
        if feedback.get("success"):
            continue
        error = str(feedback.get("error_message") or "")
        category = next(
            (
                name
                for name, pattern in ERRORS
                if re.search(pattern, error, re.I)
            ),
            "other_or_incomplete",
        )
        failures[category] += 1
    turns = row["turns"]
    return dict(
        peak_input_tokens=max((t["input"] for t in turns), default=0),
        initial_input_tokens=turns[0]["input"] if turns else 0,
        long_context_requests=sum(t["input"] > 272000 for t in turns),
        serialized_distinct_feedback_characters=sum(sizes),
        largest_serialized_feedback_characters=max(sizes, default=0),
        failure_categories=dict(failures),
    )


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    costs = Counter[str]()
    failures = Counter[str]()
    for row in rows:
        costs.update(row["costs"])
        failures.update(row["trace_summary"]["failure_categories"])
    total = costs["price"]
    failed_cost = sum(r["costs"]["price"] for r in rows if not r["solved"])
    result: dict[str, Any] = dict(
        cells=len(rows),
        cost=total,
        costs=dict(costs),
        cache_fraction=costs["cached"] / costs["input"]
        if costs["input"]
        else None,
        failure_cost_fraction=failed_cost / total if total else None,
        solved_at_or_below_ten_cents=sum(
            r["solved"] and r["costs"]["price"] <= 0.10 + 1e-12 for r in rows
        ),
        crossing_cells=sum(r["costs"]["price"] > 0.10 + 1e-12 for r in rows),
        overshoot_cost=sum(max(0, r["costs"]["price"] - 0.10) for r in rows),
        peak_input_tokens=max(
            r["trace_summary"]["peak_input_tokens"] for r in rows
        ),
        long_context_requests=sum(
            r["trace_summary"]["long_context_requests"] for r in rows
        ),
        distinct_failure_categories=dict(failures),
        initial_input_mean=sum(
            r["trace_summary"]["initial_input_tokens"] for r in rows
        )
        / len(rows),
    )
    lo, hi = total_interval(rows)
    if lo != hi:
        failed_lo, failed_hi = total_interval(
            [r for r in rows if not r["solved"]]
        )
        result.update(
            cost_interval=[lo, hi],
            failure_cost_fraction_interval=[
                failed_lo / hi,
                min(1.0, failed_hi / lo),
            ],
            crossing_cells_interval=[
                sum(interval(r)[0] > 0.10 + 1e-12 for r in rows),
                sum(interval(r)[1] > 0.10 + 1e-12 for r in rows),
            ],
            overshoot_cost_interval=[
                sum(max(0, interval(r)[endpoint] - 0.10) for r in rows)
                for endpoint in (0, 1)
            ],
            billing_note="Scalar costs/crossings include full timeout liability. Invoice intervals are explicit; token/cache/feedback mechanisms describe observed responses only, since the lost response has no usage.",
        )
    return result


def contributions(
    base: list[dict[str, Any]], arm: list[dict[str, Any]]
) -> dict[str, Any]:
    b = {(r["theorem"], r["seed"]): r for r in base}
    a = {(r["theorem"], r["seed"]): r for r in arm}
    if b.keys() != a.keys():
        raise ValueError("Incomplete mechanism comparison")
    outcome_groups: dict[str, dict[str, Any]] = {}
    theorems: dict[str, dict[str, Any]] = {}
    one_request: dict[str, Any] = dict(
        cells=0,
        baseline_input_tokens=0,
        arm_input_tokens=0,
        baseline_input_cost=0.0,
        arm_input_cost=0.0,
        baseline_output_cost=0.0,
        arm_output_cost=0.0,
    )
    for key, br in b.items():
        ar = a[key]
        if all(
            row["solved"] and row["counts"].get("requests") == 1
            for row in (br, ar)
        ):
            one_request["cells"] += 1
            for prefix, row in (("baseline", br), ("arm", ar)):
                one_request[prefix + "_input_tokens"] += row["costs"]["input"]
                one_request[prefix + "_input_cost"] += row["costs"][
                    "input_cost"
                ]
                one_request[prefix + "_output_cost"] += row["costs"][
                    "output_cost"
                ]
        label = (
            "both_solve"
            if br["solved"] and ar["solved"]
            else "both_fail"
            if not br["solved"] and not ar["solved"]
            else "gained"
            if ar["solved"]
            else "lost"
        )
        group = outcome_groups.setdefault(
            label,
            dict(
                cells=0,
                baseline_cost=0.0,
                arm_cost=0.0,
                baseline_requests=0,
                arm_requests=0,
            ),
        )
        group["cells"] += 1
        for prefix, row in (("baseline", br), ("arm", ar)):
            group[prefix + "_cost"] += row["costs"]["price"]
            group[prefix + "_requests"] += row["counts"].get("requests", 0)
            lo, hi = interval(row)
            if lo != hi:
                field = prefix + "_unknown_charge_upper"
                group[field] = group.get(field, 0.0) + hi - lo
        item = theorems.setdefault(
            key[0],
            dict(
                theorem=key[0],
                cells=0,
                baseline_solves=0,
                arm_solves=0,
                baseline_cost=0.0,
                arm_cost=0.0,
                baseline_requests=0,
                arm_requests=0,
                paths=[],
            ),
        )
        item["cells"] += 1
        item["paths"].append(
            dict(seed=key[1], baseline=br["path"], arm=ar["path"])
        )
        for prefix, row in (("baseline", br), ("arm", ar)):
            item[prefix + "_solves"] += int(row["solved"])
            item[prefix + "_cost"] += row["costs"]["price"]
            item[prefix + "_requests"] += row["counts"].get("requests", 0)
            lo, hi = interval(row)
            if lo != hi:
                field = prefix + "_unknown_charge_upper"
                item[field] = item.get(field, 0.0) + hi - lo
    for item in theorems.values():
        item["dollars_saved"] = item["baseline_cost"] - item["arm_cost"]
    for item in [*outcome_groups.values(), *theorems.values()]:
        if not any(k.endswith("unknown_charge_upper") for k in item):
            continue
        for prefix in ("baseline", "arm"):
            hi = item[prefix + "_cost"]
            item[prefix + "_cost_interval"] = [
                hi - item.get(prefix + "_unknown_charge_upper", 0.0),
                hi,
            ]
        item["dollars_saved_interval"] = [
            item["baseline_cost_interval"][0] - item["arm_cost_interval"][1],
            item["baseline_cost_interval"][1] - item["arm_cost_interval"][0],
        ]
        item["billing_note"] = (
            "Scalar costs and ordering use upper liability. The actual bill and saving remain within the stated intervals."
        )
    raw_base = sum(r["costs"]["no_cache"] for r in base)
    raw_arm = sum(r["costs"]["no_cache"] for r in arm)
    result: dict[str, Any] = dict(
        outcome_transitions=outcome_groups,
        both_solve_in_one_request=one_request,
        per_theorem=sorted(
            theorems.values(), key=lambda x: x["dollars_saved"], reverse=True
        ),
        identical_token_uncached_repricing=dict(
            baseline_cost=raw_base,
            arm_cost=raw_arm,
            saving=1 - raw_arm / raw_base,
            limitation="Same observed trajectories repriced without the cache discount. This does not simulate uncached deployment: higher charges could make the controller stop earlier.",
        ),
    )
    if any(interval(r)[0] != interval(r)[1] for r in base + arm):
        result["identical_token_uncached_repricing"].update(
            saving=None,
            scope="Observed responses only. The timeout's missing token usage prevents a complete uncached repricing comparison.",
        )
    return result


def online_phases(rows: list[dict[str, Any]]) -> dict[str, Any]:
    protocol = read(CAMPAIGN / "online_protocol.json")
    positions = {
        (t, order): step
        for order, names in enumerate(protocol["independent_orders"])
        for step, t in enumerate(names)
    }
    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["stage"] == "train" and row["arm"] in (
            "A0",
            "B0",
            "online_A2",
            "online_B1",
            "online_B2",
        ):
            groups[
                row["arm"], positions[row["theorem"], row["seed"]] // 10
            ].append(row)
    receipts = ledger_rows()
    result: dict[str, Any] = {}
    for (arm, phase), rr in groups.items():
        value = aggregate(rr)
        value["solves"] = sum(r["solved"] for r in rr)
        if arm.startswith("online_"):
            short = arm.removeprefix("online_")
            stems = {
                f"online-o{o}-s{step:02d}__{short}__"
                for o in (0, 1)
                for step in range(phase * 10, phase * 10 + 10)
            }
            paid = [
                r
                for r in receipts
                if any(r["cell"].startswith(stem) for stem in stems)
            ]
            if any(r["status"] != "settled" for r in paid):
                raise ValueError("Online learning billing incomplete")
            value["learning_cost"] = sum(r["charged"] for r in paid)
            books = [
                read(
                    CAMPAIGN
                    / "books"
                    / f"online-o{o}-s{step:02d}__{short}_before.json"
                )
                for o in (0, 1)
                for step in range(phase * 10, phase * 10 + 10)
            ]
            value["mean_book_characters"] = sum(
                len(b["text"]) for b in books
            ) / len(books)
        result[f"{arm}/steps{phase * 10 + 1}-{phase * 10 + 10}"] = value
    return result


def run() -> None:
    rows = read(REPORT / "fresh_cells.json")
    if len(rows) != 1520:
        raise ValueError("Final core denominator changed")
    rows += read(REPORT / "rule_repair_cells.json")
    rows += read(REPORT / "adaptive_frozen_cells.json")
    if len(rows) != 1760 or len({r["cell"] for r in rows}) != 1760:
        raise ValueError("Supplemented serving denominator changed")
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["stage"], row["arm"]].append(row)
    paired_groups: dict[str, Any] = {}
    for (stage, arm), rr in groups.items():
        if arm in ("A0", "B0"):
            continue
        baseline = (
            "B0" if arm.removeprefix("online_").startswith("B") else "A0"
        )
        paired_groups[f"{stage}/{arm}"] = contributions(
            groups[stage, baseline], rr
        )
    for stage in ("train", "validation"):
        for baseline, arm in (
            ("A2", "S1"),
            ("A2", "P1"),
            ("B1", "B2"),
            ("A0", "B0"),
        ):
            paired_groups[f"{stage}/{arm}_vs_{baseline}"] = contributions(
                groups[stage, baseline], groups[stage, arm]
            )
        for baseline in ("A2", "P1"):
            paired_groups[f"{stage}/O1_vs_{baseline}"] = contributions(
                groups[stage, baseline], groups[stage, "O1"]
            )
    paired_groups["train/R1_vs_A2"] = contributions(
        groups["train", "A2"], groups["train", "R1"]
    )
    save(
        REPORT / "fresh_mechanisms.json",
        dict(
            groups={
                f"{stage}/{arm}": aggregate(rr)
                for (stage, arm), rr in groups.items()
            },
            comparisons=paired_groups,
            online_phases=online_phases(rows),
            limitations=__doc__,
        ),
    )
    print(json.dumps(dict(cells=len(rows), comparisons=len(paired_groups))))


if __name__ == "__main__":
    run()
