"""Historical panels, comparator differences, bullet lineage and failures.

Consumes only the guarded audit's individual permitted records. Registered
historical comparisons are kept separate from the broad descriptive census.
Both harnesses: python -m tools.reports.ace_thesis_retrospective.
"""

from collections import Counter, defaultdict
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import Any

from ace.ace_playbook import Playbook
from experiments.ace_thesis import campaign as c
from experiments.ace_thesis.artifact import fingerprint
from experiments.ace_thesis.design import families
from experiments.ace_sanitized.scope import partition
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from tools.reports.ace_thesis import export_csv


def load() -> list[dict[str, Any]]:
    rows = [
        json.loads(p.read_text())
        for p in sorted((c.CAMPAIGN / "audit/cells").glob("*.json"))
    ]
    if len(rows) != c.read("audit/summary.json")["audited"]:
        raise ValueError("Census row count changed")
    billing = c.read("audit/receipts.json")
    costs: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for receipt in billing:
        costs[(receipt["campaign"], receipt["cell"])].append(receipt)
    for row in rows:
        paid = costs.get((row["campaign"], Path(row["path"]).name), [])
        row["cost"] = (
            sum(r["charged"] for r in paid)
            if paid
            else row["cache_cost_current_tariff"]
        )
        row["cost_source"] = (
            "dated billing receipts"
            if paid
            else "cache tokens, current tariff; unrecorded retries unknown"
        )
        row["unknown_charge"] = any(r["status"] != "settled" for r in paid)
        row["qualified"] = (
            row["solved"]
            and row["status"] == "done"
            and row["cost"] <= 0.1 + 1e-12
        )
    return rows


def arm(row: dict[str, Any]) -> str:
    return re.sub(
        r"__seed\d+$",
        "",
        Path(row["path"]).name.replace(row["theorem"], "THEOREM"),
    )


def canonical(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Respect the older declared continuation, retaining both raw archives."""
    campaign = "ace_economy_refinement_20260916"
    path = (
        c.ROOT
        / "experiments/campaigns"
        / campaign
        / "operations/incident01.json"
    )
    incident = json.loads(path.read_text())
    resumed = set(incident["interrupted_cells"])
    return [
        r
        for r in rows
        if not (
            r["campaign"] == campaign
            and Path(r["path"]).name in resumed
            and "/final00/" in r["path"]
        )
    ]


def panels(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def original_cap(row: dict[str, Any]) -> float:
        budget: dict[str, Any] = row["comparator"].get("budget") or {}
        cap = budget.get("price")
        return float("inf") if cap is None else float(cap)

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    for row in canonical(rows):
        strategy = row["comparator"].get("strategy") or ""
        if strategy.startswith("prove_theorem") and row["seed"] is not None:
            grouped[(row["campaign"], row["partition"], arm(row))].append(row)
    result: list[dict[str, Any]] = []
    for (campaign, split, label), group in sorted(grouped.items()):
        keys = {(r["theorem"], r["seed"]) for r in group}
        seeds = sorted({r["seed"] for r in group})
        expected = {(t, s) for t in partition(split) for s in seeds}
        models = sorted({m for r in group for m in r["comparator"]["models"]})
        result.append(
            dict(
                campaign=campaign,
                partition=split,
                arm=label,
                cells=len(group),
                unique_cells=len(keys),
                expected_for_observed_replicates=len(expected),
                complete_observed_replicates=keys == expected
                and len(keys) == len(group),
                solved=sum(r["qualified"] for r in group),
                raw_completed_solves=sum(
                    r["solved"] and r["status"] == "done" for r in group
                ),
                solved_at_original_price_budget=sum(
                    r["solved"]
                    and r["status"] == "done"
                    and r["cost"] <= original_cap(r) + 1e-12
                    for r in group
                ),
                original_price_budgets=json.dumps(
                    sorted({str(original_cap(r)) for r in group})
                ),
                cost=sum(r["cost"] for r in group),
                failed=sum(r["status"] == "failed" for r in group),
                censored=sum(r["administrative_censoring"] for r in group),
                unknown_charge=sum(r["unknown_charge"] for r in group),
                cache_only_costs=sum(
                    r["cost_source"].startswith("cache") for r in group
                ),
                models=";".join(models),
                book_versions=len({r["book_sha256"] for r in group}),
                note="Descriptive census; consult explicit expected_panels.json for unobserved replicates/configs. $0.10 qualification applied uniformly.",
            )
        )
    return result


def paired(
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
    label: str,
    seeds: tuple[int, ...],
) -> dict[str, Any]:
    expected = [(t, str(s)) for t in partition("validation") for s in seeds]

    def observations(
        rows: list[dict[str, Any]],
    ) -> dict[tuple[str, str], Observation]:
        values = {
            (r["theorem"], r["seed"]): Observation(
                r["qualified"], r["cost"], r["status"] == "failed"
            )
            for r in rows
        }
        if len(values) != len(rows) or any(
            r["administrative_censoring"] or r["unknown_charge"] for r in rows
        ):
            raise ValueError("Duplicate, censored or unpriced historical cell")
        return values

    a, b = observations(left), observations(right)
    mapping = families("validation")
    comparison = compare(a, b, expected, families=mapping)
    if not comparison["complete"]:
        raise ValueError("Historical comparison has missing cells")
    comparison.pop("verdict")
    comparison.update(
        label=label,
        budget_reduction_percent=100 * (1 - comparison["cost_ratio"]),
        coverage_change_points=100 * comparison["effect"],
        cost_p_two_sided=cost_cluster_p(a, b, expected, mapping),
        source_paths_a=[r["path"] for r in left],
        source_paths_b=[r["path"] for r in right],
        comparator_a=left[0]["comparator"],
        comparator_b=right[0]["comparator"],
        cache_only_cells=sum(
            r["cost_source"].startswith("cache") for r in left + right
        ),
        limitation="Retrospective, reused validation; archival controls and provider-cache warmth differ. Not a held-out confirmation.",
    )
    return comparison


def registered_comparisons(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = {r["path"]: r for r in rows}
    attr = c.ROOT / "experiments/campaigns/ace_attribution_20260912"
    refs = json.loads((attr / "references.json").read_text())["validation"]
    inventory = json.loads((attr / "execution_inventory.json").read_text())[
        "inference"
    ]
    ace = [indexed[r["source"] + "/configs/" + r["name"]] for r in refs]
    none = [
        indexed[r["source"]]
        for r in inventory
        if r["partition"] == "validation" and r["arm"] == "luna-none"
    ]
    results = [paired(none, ace, "attribution_X3", (0,))]
    current = canonical(rows)

    def choose(campaign: str, prefix: str) -> list[dict[str, Any]]:
        return [
            r
            for r in current
            if r["campaign"] == campaign
            and r["partition"] == "validation"
            and Path(r["path"]).name.startswith(prefix)
        ]

    results.append(
        paired(
            choose(
                "ace_economy_session_20260916", "validation__agentic_session__"
            ),
            choose("ace_economy_20260916", "validation__session__"),
            "historical_session",
            (0, 1),
        )
    )
    for label, campaign, a, b in (
        ("ordinary_economy", "ace_economy_20260916", "agentic", "ace"),
        (
            "ordinary_refinement",
            "ace_economy_refinement_20260916",
            "agentic",
            "ace",
        ),
        (
            "matched_drop_refinement",
            "ace_economy_refinement_20260916",
            "agentic_reset",
            "ace_reset",
        ),
        (
            "sanitized_32768",
            "ace_sanitized_20260917",
            "agentic",
            "ace_selected",
        ),
        (
            "sanitized_8192",
            "ace_sanitized_20260917",
            "agentic_coverage",
            "ace_coverage",
        ),
    ):
        results.append(
            paired(
                choose(campaign, f"validation__{a}__"),
                choose(campaign, f"validation__{b}__"),
                label,
                (0, 1),
            )
        )
    return results


def bullet_catalog(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    paths = sorted(
        p
        for p in (c.ROOT / "experiments/playbooks").glob("*.yaml")
        if ".provenance." not in p.name
        and ".triggers." not in p.name
        and not any(
            n in p.name.lower() for n in ("test", "challenge", "review_repair")
        )
    )
    paths += [c.REFERENCE / "book.yaml", c.SANITIZED / "book.yaml"]
    entries: list[dict[str, Any]] = []
    for path in paths:
        book = Playbook.load(path)
        versions = {
            fingerprint(book.render_prompt()),
            fingerprint(book.render_markdown()),
        }
        exposed = [r for r in rows if r["book_sha256"] in versions]
        for rule in book.bullets:
            entries.append(
                dict(
                    file=str(path.relative_to(c.ROOT)),
                    file_sha256=c.sha(path),
                    book_sha256=book.sha256(),
                    **asdict(rule),
                    observed_prompt_cells=sum(
                        rule.id in r["bullet_prompt_exposure"] for r in exposed
                    ),
                    observed_prompt_requests=sum(
                        r["bullet_prompt_exposure"].get(rule.id, 0)
                        for r in exposed
                    ),
                    limitation="Exact default-render matches only; alternate rendering/citation wrappers can undercount. Exposure does not establish use or correctness.",
                )
            )
    return entries


def report_directory() -> Path:
    version = fingerprint(
        (
            c.sha(Path(__file__)),
            c.sha(Path(export_csv.__code__.co_filename)),
        )
    )
    return c.CAMPAIGN / "audit/retrospective" / version[:16]


def problem_profiles(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Diagnostic coverage by exercise, never a pooled treatment comparison."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in canonical(rows):
        if (row["comparator"].get("strategy") or "").startswith(
            "prove_theorem"
        ):
            grouped[row["theorem"]].append(row)
    profiles: list[dict[str, Any]] = []
    for theorem, group in sorted(grouped.items()):
        checks = [
            check
            for row in group
            for check in row["checks"]
            if not check["success"]
        ]
        errors = Counter(check["error"] for check in checks if check["error"])
        profiles.append(
            dict(
                theorem=theorem,
                partition=group[0]["partition"],
                archived_proof_cells=len(group),
                archived_successes=sum(r["solved"] for r in group),
                campaigns=len({r["campaign"] for r in group}),
                failed_or_open_checks=len(checks),
                check_categories=json.dumps(
                    Counter(check["category"] for check in checks),
                    sort_keys=True,
                ),
                frequent_errors=json.dumps(errors.most_common(5)),
                evidence=json.dumps(
                    [
                        "audit/cells/" + fingerprint(r["path"]) + ".json"
                        for r in group
                    ]
                ),
                limitation="Unequal treatments, budgets and replication; diagnostic counts only, not a coverage estimate. Old successes are archived outcomes, not fresh compiler certificates.",
            )
        )
    return profiles


def main() -> None:
    rows = load()
    destination = report_directory()
    destination.mkdir(parents=True, exist_ok=True)
    comparison = registered_comparisons(rows)
    export_csv(destination / "panels.csv", panels(rows))
    export_csv(destination / "bullets.csv", bullet_catalog(rows))
    export_csv(destination / "problems.csv", problem_profiles(rows))
    failed = [r for r in rows if not r["solved"]]
    export_csv(
        destination / "failures.csv",
        [
            dict(
                path=r["path"],
                theorem=r["theorem"],
                partition=r["partition"],
                strategy=r["comparator"]["strategy"],
                status=r["status"],
                category=r["failure_category"],
                checks=len(r["checks"]),
                cost=r["cost"],
                cost_source=r["cost_source"],
                unknown_charge=r["unknown_charge"],
                administrative_censoring=r["administrative_censoring"],
                evidence="audit/cells/" + fingerprint(r["path"]) + ".json",
            )
            for r in failed
        ],
    )
    (destination / "comparisons.json").write_text(
        json.dumps(comparison, indent=2) + "\n"
    )
    (destination / "reporting_source.py").write_text(
        Path(__file__).read_text()
    )
    (destination / "csv_exporter_source.py").write_text(
        Path(export_csv.__code__.co_filename).read_text()
    )
    (destination / "summary.json").write_text(
        json.dumps(
            dict(
                raw_cells=len(rows),
                failures=len(failed),
                taxonomy=dict(Counter(r["failure_category"] for r in failed)),
                source_sha256=c.sha(Path(__file__)),
                csv_exporter_sha256=c.sha(
                    Path(export_csv.__code__.co_filename)
                ),
                audit_sha256=c.sha(c.CAMPAIGN / "audit/summary.json"),
            ),
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps(
            [
                dict(
                    label=p["label"],
                    solved=[p["solved_a"], p["solved_b"]],
                    cost=[p["cost_a"], p["cost_b"]],
                    saving=p["budget_reduction_percent"],
                    points=p["coverage_change_points"],
                )
                for p in comparison
            ]
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
