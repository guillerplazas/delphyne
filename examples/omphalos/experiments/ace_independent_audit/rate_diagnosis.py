"""Observed cache charges around the temporary rate-limit interruption.

Run after the registered study has completed. This reads preserved prefixes,
raw provider receipts and continuation certificates; it makes no API calls
and never changes a benchmark outcome or substitutes a warm-cache invoice.
Both harnesses use ``python -m experiments.ace_independent_audit.rate_diagnosis``.
"""

from collections import Counter
from datetime import date, datetime
import json
from typing import Any
from urllib.parse import urlparse

from .accounting import price
from .common import OUTPUT, REPORT, read, save, sha
from .economics import ledger_rows
from .rate_recovery import BATCH, FOLDER, raw_response, rejection_events
from .reporting import inputs


def run() -> None:
    # Require the complete denominator before emitting a final diagnosis.
    inputs()
    preparation = read(FOLDER / "preparation.json")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for receipt in ledger_rows():
        grouped.setdefault(receipt["cell"], []).append(receipt)
    continued: list[dict[str, Any]] = []
    for identity, original in preparation["interrupted"].items():
        folder = FOLDER / "cells" / identity
        for name, expected in original["preserved_hashes"].items():
            if sha(folder / "original" / name) != expected:
                raise ValueError("An original interrupted prefix changed")
        for receipt, expected in original["raw_hashes"].items():
            if sha(raw_response(identity, receipt)[0]) != expected:
                raise ValueError("An original provider receipt changed")
        events = rejection_events(
            identity, OUTPUT / BATCH / "configs" / identity
        )
        if original["rejection"] not in {e["receipt"] for e in events}:
            raise ValueError("Original rejection absent from certification")
        receipts = sorted(grouped[identity], key=lambda r: r["created"])
        first_added = len(original["receipts"])
        if [r["id"] for r in receipts[:first_added]] != original["receipts"]:
            raise ValueError("The original receipt order changed")
        first: dict[str, Any] | None = None
        for receipt in receipts[first_added:]:
            path, raw = raw_response(identity, receipt["id"])
            if "response" not in raw:
                continue
            response = raw["response"]
            costs = price(
                response["usage"],
                response["model"],
                on=date.fromisoformat(raw["started"][:10]),
                tier=response["service_tier"],
                regional=urlparse(str(raw["endpoint"])).hostname
                != "api.openai.com",
            )
            if abs(costs["price"] - receipt["charged"]) > 1e-10:
                raise ValueError("First continued response did not reprice")
            first = dict(
                receipt=receipt["id"],
                raw_sha=sha(path),
                started=raw["started"],
                costs=costs,
                cache_diagnostics=response.get("prompt_cache_diagnostics"),
            )
            break
        if first is None:
            raise ValueError("An interrupted request has no returned response")
        gap = None
        if original["prefix_responses"]:
            previous = raw_response(identity, original["receipts"][-2])[1]
            gap = (
                datetime.fromisoformat(first["started"])
                - datetime.fromisoformat(previous["finished"])
            ).total_seconds()
        continued.append(
            dict(
                cell=identity,
                prefix_responses=original["prefix_responses"],
                prefix_cost=original["prefix_cost"],
                gap_since_previous_response_seconds=gap,
                first_resumed_response=first,
                certified_zero_charge_rejections=len(events),
            )
        )
    paid_prefixes = [r for r in continued if r["prefix_responses"]]
    first_paid = [r["first_resumed_response"] for r in paid_prefixes]
    if len(continued) != 87 or len(paid_prefixes) != 23:
        raise ValueError("The incident denominator changed")
    output = dict(
        preparation_sha=sha(FOLDER / "preparation.json"),
        interrupted_cells=len(continued),
        interrupted_before_any_response=len(continued) - len(paid_prefixes),
        interrupted_after_paid_responses=len(paid_prefixes),
        preserved_paid_responses=sum(r["prefix_responses"] for r in continued),
        preserved_prefix_cost=sum(r["prefix_cost"] for r in continued),
        first_response_after_paid_prefix=dict(
            n=len(first_paid),
            input_tokens=sum(r["costs"]["input"] for r in first_paid),
            cached_tokens=sum(r["costs"]["cached"] for r in first_paid),
            zero_cached_responses=sum(
                r["costs"]["cached"] == 0 for r in first_paid
            ),
            input_cost=sum(r["costs"]["input_cost"] for r in first_paid),
            total_cost=sum(r["costs"]["price"] for r in first_paid),
            diagnostic_types=dict(
                Counter(
                    str(r["cache_diagnostics"].get("type", "missing"))
                    if r["cache_diagnostics"] is not None
                    else "missing"
                    for r in first_paid
                )
            ),
        ),
        cells=continued,
        paid_calls=0,
        interpretation=(
            "These are the observed first-response charges after the rate "
            "interruption. They are included, unchanged, in serving costs. "
            "A nonzero cache hit does not mean all earlier context remained "
            "cached. The first-response input total is not an estimate of "
            "avoidable cost, and it does not bound later behavioral effects "
            "of a budget crossing. The key change, elapsed time and dispatch "
            "schedule were not randomized treatments. No warm-cache "
            "counterfactual or replacement outcome is inferred. The separate "
            "overnight credit interruption is in continuation_diagnosis.json."
        ),
    )
    save(REPORT / "rate_diagnosis.json", output)
    print(
        json.dumps(
            {
                k: output[k]
                for k in (
                    "interrupted_cells",
                    "preserved_paid_responses",
                    "first_response_after_paid_prefix",
                    "paid_calls",
                )
            }
        )
    )


if __name__ == "__main__":
    run()
