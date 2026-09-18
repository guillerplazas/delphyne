"""Registered pilot selection and complete-panel benchmark dispatch."""

from dataclasses import asdict
import random
from typing import Any

from ace.ace_playbook import Playbook

from . import campaign as c
from .control import Controls
from .scope import partition


def totals(jobs: list[c.Job]) -> dict[str, dict[str, Any]]:
    account = c.accounting()
    if account["unresolved"] or account["billing_issues"]:
        raise ValueError("Unsettled measurements")
    result: dict[str, dict[str, Any]] = {}
    for job in jobs:
        value = c.cell_result(job)
        cost = account["costs"].get(c.name(job, None), 0)
        row = result.setdefault(job.arm, dict(cells=0, solved=0, cost=0.0))
        row["cells"] += 1
        row["cost"] += cost
        row["solved"] += bool(
            value and value["success"] and cost <= job.cap + 1e-12
        )
    for row in result.values():
        row["coverage_percent"] = 100 * row["solved"] / row["cells"]
        row["cost_per_solve"] = (
            row["cost"] / row["solved"] if row["solved"] else None
        )
    return result


def frontier(values: dict[str, dict[str, Any]]) -> list[str]:
    if not values or len({v["cells"] for v in values.values()}) != 1:
        raise ValueError("A frontier requires a complete matched panel")
    return sorted(
        a
        for a, v in values.items()
        if not any(
            w["solved"] >= v["solved"]
            and w["cost"] <= v["cost"]
            and (w["solved"] > v["solved"] or w["cost"] < v["cost"])
            for b, w in values.items()
            if b != a
        )
    )


def combination() -> None:
    values = totals(c.jobs("pilot"))
    if set(values) != set(c.ISOLATED) or any(
        v["cells"] != 8 for v in values.values()
    ):
        raise ValueError("Incomplete isolated pilot")
    eligible = frontier(values)
    controls = Controls(
        output_tokens=8192 if "output" in eligible else 32768,
        drop="drop" in eligible,
        concise="concise" in eligible,
        views="views" in eligible,
    )
    book_source = "new" if "book" in eligible else "incumbent"
    c.save(
        "combination.json",
        dict(
            isolated=values,
            frontier=eligible,
            controls=asdict(controls),
            book=book_source,
            stopping="offline audit only; no paid stop treatment",
        ),
    )
    # Avoid paying for a configuration already measured on the same panel.
    equivalent = next(
        (
            arm
            for arm, value in c.ISOLATED.items()
            if value == controls and (arm == "book") == (book_source == "new")
        ),
        None,
    )
    if equivalent:
        c.save("combination_reuse.json", dict(arm=equivalent))
        return
    book = Playbook.load(
        (c.CAMPAIGN if book_source == "new" else c.REFERENCE) / "book.yaml"
    )
    jobs = [
        c.proof_job("pilots", "combination", t, 0, controls, book)
        for t in c.PILOT_THEOREMS
    ]
    if not c.launch("combination", jobs):
        raise ValueError("Complete combination pilot does not fit")


def freeze() -> None:
    c.verify()
    if (c.CAMPAIGN / "freeze.json").exists():
        verify_freeze()
        return
    jobs = c.jobs("pilot")
    if (c.CAMPAIGN / "batches/combination.json").exists():
        jobs += c.jobs("combination")
    elif not (c.CAMPAIGN / "combination_reuse.json").exists():
        raise ValueError("Complete the combination decision first")
    values = totals(jobs)
    eligible = frontier(values)
    primary = min(
        eligible,
        key=lambda a: (
            values[a]["cost_per_solve"]
            if values[a]["solved"]
            else float("inf"),
            -values[a]["solved"],
            values[a]["cost"],
            a,
        ),
    )
    coverage = min(
        eligible, key=lambda a: (-values[a]["solved"], values[a]["cost"], a)
    )

    def treatment(arm: str) -> dict[str, Any]:
        if arm == "combination":
            combined = c.read("combination.json")
            return dict(controls=combined["controls"], book=combined["book"])
        return dict(
            controls=asdict(c.ISOLATED[arm]),
            book="new" if arm == "book" else "incumbent",
        )

    c.save(
        "freeze.json",
        dict(
            primary=primary,
            coverage=coverage,
            frontier=eligible,
            treatments={a: treatment(a) for a in values},
            pilot=values,
            book_file_sha256=c.sha(c.CAMPAIGN / "book.yaml"),
            source_seal_sha256=c.sha(c.CAMPAIGN / "seal.json"),
            validation_theorems=sorted(partition("validation")),
            replicates=[0, 1],
            book_audit_sha256=c.sha(c.CAMPAIGN / "book_audit.json"),
        ),
    )
    c.transfer_unused("learning", "validation")
    c.transfer_unused("pilots", "validation")
    c.transfer_unused("reserve", "validation")


def verify_freeze() -> dict[str, Any]:
    frozen = c.read("freeze.json")
    if frozen["book_file_sha256"] != c.sha(c.CAMPAIGN / "book.yaml"):
        raise ValueError("Frozen book drift")
    if frozen["source_seal_sha256"] != c.sha(c.CAMPAIGN / "seal.json"):
        raise ValueError("Frozen implementation drift")
    if frozen["book_audit_sha256"] != c.sha(c.CAMPAIGN / "book_audit.json"):
        raise ValueError("Frozen book audit drift")
    return frozen


def panel(arm: str, treatment: dict[str, Any]) -> list[c.Job]:
    book = (
        None
        if treatment["book"] == "empty"
        else Playbook.load(
            (c.CAMPAIGN if treatment["book"] == "new" else c.REFERENCE)
            / "book.yaml"
        )
    )
    return [
        c.proof_job(
            "validation", arm, t, seed, Controls(**treatment["controls"]), book
        )
        for t in sorted(partition("validation"))
        for seed in (0, 1)
    ]


def benchmark() -> None:
    frozen = verify_freeze()
    selected = frozen["treatments"][frozen["primary"]]
    ordinary = dict(controls=asdict(Controls()), book="empty")
    jobs = panel("agentic", ordinary) + panel("ace_selected", selected)
    random.Random(20260917).shuffle(jobs)
    if not c.launch("core", jobs):
        raise ValueError("Entire core validation panel does not fit")
    completed = [("agentic", ordinary), ("ace_selected", selected)]
    extras = [
        (
            "agentic_selected",
            dict(controls=selected["controls"], book="empty"),
        ),
        (
            "ace_incumbent",
            dict(controls=selected["controls"], book="incumbent"),
        ),
        ("ace_coverage", frozen["treatments"][frozen["coverage"]]),
    ]
    decisions: list[dict[str, Any]] = []
    for label, treatment in extras:
        reuse = next((a for a, v in completed if v == treatment), None)
        if reuse:
            decisions.append(dict(arm=label, reused=reuse))
            continue
        jobs = panel(label, treatment)
        random.Random(20260917).shuffle(jobs)
        if c.launch(label, jobs):
            completed.append((label, treatment))
            decisions.append(dict(arm=label, cells=80))
        else:
            decisions.append(
                dict(arm=label, skipped="Entire $8 liability does not fit")
            )
    c.save(
        "benchmark_finished.json",
        dict(
            panels=completed,
            extra_decisions=decisions,
            accounting=c.accounting(),
            default_promoted=False,
        ),
    )
