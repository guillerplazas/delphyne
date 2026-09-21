"""Final-only cell reconciliation and analysis of the registered fresh study."""

from collections import defaultdict
import json
import sqlite3
from typing import Any

from . import campaign as c
from .analysis import metrics, paired
from .audit import cell
from .common import CAMPAIGN, OUTPUT, REPORT, read, save
from .completion import require_closed
from .cost_bounds import receipt_interval
from .families import mapping
from .mechanisms import characterize


def receipts() -> dict[str, dict[str, Any]]:
    with sqlite3.connect(CAMPAIGN / "ledger.sqlite3") as db:
        db.row_factory = sqlite3.Row
        rows = [dict(row) for row in db.execute("SELECT * FROM receipts")]
    result: dict[str, dict[str, Any]] = defaultdict(
        lambda: dict(cost=0.0, requests=0, statuses={}, receipts=[])
    )
    for row in rows:
        group = result[row["cell"]]
        group["statuses"][row["status"]] = (
            group["statuses"].get(row["status"], 0) + 1
        )
        group["receipts"].append(row["id"])
        group["requests"] += 1
        if row["charged"] is not None:
            group["cost"] += row["charged"]
        if row["status"] == "bounded_charge":
            lo, hi = receipt_interval(row)
            group.setdefault("bounded_receipts", []).append(row["id"])
            group["unknown_charge_upper"] = (
                group.get("unknown_charge_upper", 0.0) + hi - lo
            )
    for group in result.values():
        if "bounded_receipts" in group:
            group["cost_interval"] = [
                group["cost"] - group["unknown_charge_upper"],
                group["cost"],
            ]
    return result


def solver_rows(
    batch: str,
    ledger: dict[str, dict[str, Any]],
    *,
    allow_terminal_failures: bool = False,
) -> list[dict[str, Any]]:
    try:
        require_closed(batch)
    except ValueError:
        if not allow_terminal_failures:
            raise
        from .terminal_failure import assert_closed

        assert_closed(batch)
    jobs = [c.Job(**v) for v in read(CAMPAIGN / "batches" / f"{batch}.json")]
    rows: list[dict[str, Any]] = []
    for job in jobs:
        identity = c.name(job, None)
        directory = OUTPUT / batch / "configs" / identity
        row = cell((str(directory), job.theorem))
        paid = ledger.get(
            identity, dict(cost=0.0, requests=0, statuses={}, receipts=[])
        )
        bounded = False
        terminal = row["status"] == "platform_error"
        if not terminal and paid["requests"] != row["counts"].get(
            "requests", 0
        ):
            from .administrative import rejection_events

            events = rejection_events(identity, directory)
            rejected = [event["receipt"] for event in events]
            if not rejected or not set(rejected) <= set(paid["receipts"]):
                raise ValueError("Unreconciled administrative request")
            row["counts"]["successful_api_responses"] = row["counts"][
                "requests"
            ]
            row["counts"]["requests"] += len(rejected)
            row["counts"]["rejected_requests"] = len(rejected)
            row["administrative_rejections"] = rejected
            row["administrative_rejection_positions"] = events
            row["continuation_note"] = (
                "The same trajectory continued after explicitly certified "
                "zero-charge administrative rejections. Requests, payloads "
                "and prior paid prefixes reconcile exactly; no prior model "
                "response was resampled."
            )
        if terminal:
            if not allow_terminal_failures:
                raise ValueError("Terminal failure requires explicit auditing")
            from .terminal_failure import hashes

            certificate = read(
                CAMPAIGN / "terminal_failures" / (identity + ".json")
            )
            if certificate["hashes"] != hashes(directory):
                raise ValueError("Terminal failure evidence changed")
            row["counts"]["successful_api_responses"] = row["counts"][
                "requests"
            ]
            row["counts"]["requests"] = certificate["attempted_api_requests"]
            row["counts"]["rejected_requests"] = certificate[
                "rejected_zero_charge"
            ]
            row["terminal_failure"] = certificate["failure"]
            row["exception_sha"] = certificate["hashes"]["exception.txt"]
            if "cost_interval" in certificate:
                if (
                    not row["exact_cost"]
                    or abs(
                        row["costs"]["price"]
                        - certificate["known_prefix_cost"]
                    )
                    > 1e-9
                    or paid.get("bounded_receipts")
                    != [certificate["unknown_receipt"]]
                    or any(
                        abs(a - b) > 1e-9
                        for a, b in zip(
                            paid["cost_interval"],
                            certificate["cost_interval"],
                            strict=True,
                        )
                    )
                ):
                    raise ValueError("Bounded terminal costs do not reconcile")
                bounded = True
                row["cost_interval"] = certificate["cost_interval"]
                row["costs"]["price"] = certificate["cost_interval"][1]
                row["costs"]["unknown_charge_upper"] = certificate[
                    "unknown_charge_interval"
                ][1]
                row["exact_cost"] = False
                row["billing_note"] = (
                    "One reconciled timeout has unknown usage and a retained "
                    "liability bound. Price is the upper endpoint, not an "
                    "exact charge; all observed usage is reconciled."
                )
        permitted = {"settled", "bounded_charge"} if bounded else {"settled"}
        if set(paid["statuses"]) - permitted:
            raise ValueError("Unresolved billing: " + identity)
        if not row["exact_cost"] and not bounded:
            raise ValueError("Incomplete usage: " + identity)
        if abs(row["costs"].get("price", 0) - paid["cost"]) > 1e-9:
            raise ValueError("Receipt/cache mismatch: " + identity)
        if paid["requests"] != row["counts"].get("requests", 0):
            raise ValueError(
                "All-attempt request count differs from cache: " + identity
            )
        if job.robust and not terminal:
            receipt = read(directory / "completed.json")
            if (
                receipt["result_sha"] != row["result_sha"]
                or receipt["cache_sha"] != row["cache_sha"]
            ):
                raise ValueError("Completion receipt changed: " + identity)
        row.update(arm=job.arm, batch=batch, cell=identity, ledger=paid)
        rows.append(row)
    return rows


def core_rows() -> list[dict[str, Any]]:
    ledger = receipts()
    batches = [
        entry["batch"]
        for entry in read(CAMPAIGN / "core_schedule.json")["batches"]
    ]
    batches += [
        f"online-o{order}-s{step:02d}"
        for order in (0, 1)
        for step in range(40)
    ]
    rows = [
        row
        for batch in batches
        for row in solver_rows(
            batch,
            ledger,
            allow_terminal_failures=(
                CAMPAIGN / "terminal_failures" / (batch + ".json")
            ).exists(),
        )
    ]
    expected = [
        c.name(c.Job(**v), None)
        for parent in ("core_frozen", "core_scaling", "core_pilot_book")
        for v in read(CAMPAIGN / "batches" / f"{parent}.json")
    ]
    protocol = read(CAMPAIGN / "online_protocol.json")
    for order in (0, 1):
        for step, theorem in enumerate(protocol["independent_orders"][order]):
            event = read(
                CAMPAIGN
                / "online_events"
                / f"online-o{order}-s{step:02d}.json"
            )
            if event["theorem"] != theorem:
                raise ValueError("Online chronology changed")
            for arm in ("A0", "B0", "online_A2", "online_B1", "online_B2"):
                expected.append(
                    c.name(c.Job("train", arm, theorem, order), None)
                )
    if len(rows) != 1520 or len(set(expected)) != 1520:
        raise ValueError("Core/follow-up denominator changed")
    if sorted(r["cell"] for r in rows) != sorted(expected):
        raise ValueError("Missing or duplicate expected cell")
    return rows


def summarize() -> None:
    rows = core_rows()
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["stage"], row["arm"]].append(row)
    comparisons: dict[str, Any] = {}
    for (stage, arm), values in groups.items():
        if arm in ("A0", "B0"):
            continue
        base = "B0" if arm.removeprefix("online_").startswith("B") else "A0"
        comparisons[f"{stage}/{arm}"] = dict(
            baseline=base,
            theorem=paired(groups[stage, base], values),
            family=paired(groups[stage, base], values, mapping()),
        )
    for stage in ("train", "validation"):
        for base, arm in (
            ("A2", "S1"),
            ("B1", "B2"),
            ("A0", "B0"),
            ("A2", "P1"),
        ):
            comparisons[f"{stage}/{arm}_vs_{base}"] = dict(
                baseline=base,
                theorem=paired(groups[stage, base], groups[stage, arm]),
                family=paired(
                    groups[stage, base], groups[stage, arm], mapping()
                ),
            )
    compact = [
        dict(
            {
                k: v
                for k, v in row.items()
                if k not in ("checks", "config", "value", "turns")
            },
            trace_summary=characterize(row),
        )
        for row in rows
    ]
    save(REPORT / "fresh_cells.json", compact)
    save(
        REPORT / "fresh_results.json",
        dict(
            cells=len(rows),
            core_cells=1200,
            author_followup=160,
            short_book_followup=160,
            metrics={
                f"{stage}/{arm}": metrics(values)
                for (stage, arm), values in groups.items()
            },
            comparisons=comparisons,
            note="Frozen inference costs only here. Add recorded preparation for amortization and current-update roles for online operational totals. Reused development data, not untouched confirmation.",
        ),
    )
    print(
        json.dumps(dict(cells=len(rows), groups=len(groups), reconciled=True))
    )


if __name__ == "__main__":
    summarize()
