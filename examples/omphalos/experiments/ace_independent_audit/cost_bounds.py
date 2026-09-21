"""Explicit invoice intervals for the separately reconciled timeout exception.

This module never edits receipts or releases a dispatch pause. A reservation
is a liability bound, not observed usage. Every other unknown receipt remains
an error, and ordinary exact-cost analyses keep their original representation.
"""

from datetime import date
import gzip
import json
import math
from typing import Any

from .accounting import reserve
from .common import CAMPAIGN, read, sha


def receipt_interval(row: dict[str, Any]) -> tuple[float, float]:
    """Validate a settled receipt or the authorized, audited exception."""
    charge = row["charged"]
    if row["status"] == "settled" and charge is not None:
        if not math.isfinite(charge) or charge < 0:
            raise ValueError("Invalid settled charge")
        return charge, charge
    if row["status"] != "bounded_charge":
        raise ValueError("Unresolved billing: " + row["id"])
    folder = CAMPAIGN / "billing_recovery"
    proposal_path = folder / "bounded_timeout_preparation.json"
    approval_path = folder / "bounded_timeout_approval.json"
    proposal, approval = read(proposal_path), read(approval_path)
    before = proposal["receipt_before"]
    original_status = dict(row, status="unknown_charge")
    if (
        not approval["user_authorization"].strip()
        or approval["source_record"] != "resumption.json"
        or approval["source_sha"] != sha(CAMPAIGN / "resumption.json")
        or approval["user_authorization"]
        != read(CAMPAIGN / "resumption.json")["authorization"]
        or approval["proposal_sha"] != sha(proposal_path)
        or approval["receipt"] != row["id"]
        or original_status != before
        or before["status"] != "unknown_charge"
        or charge != row["reserved"]
    ):
        raise ValueError("Receipt does not match its approved liability")
    certificate = read(
        CAMPAIGN / "terminal_failures" / (row["cell"] + ".json")
    )
    expected = dict(
        proposal["certificate"], liability_approval_sha=sha(approval_path)
    )
    if certificate != expected or certificate["unknown_receipt"] != row["id"]:
        raise ValueError("Approved terminal certificate changed")
    path = CAMPAIGN / "responses" / row["cell"] / (row["id"] + ".json.gz")
    if sha(path) != proposal["evidence_sha"]:
        raise ValueError("Bounded receipt evidence changed")
    with gzip.open(path, "rt") as stream:
        raw = json.load(stream)
    if (
        raw["receipt"] != row["id"]
        or raw["cell"] != row["cell"]
        or raw["exception"]["type"] != "APITimeoutError"
        or raw["exception"]["rejected"] is not False
    ):
        raise ValueError("Unexpected bounded transport failure")
    bound = reserve(
        raw["payload"]["model"],
        raw["input_bound"],
        raw["payload"]["max_output_tokens"],
        date.fromisoformat(raw["started"][:10]),
    )
    if charge != bound or certificate["unknown_charge_interval"] != [
        0.0,
        bound,
    ]:
        raise ValueError("Retained reservation differs from tariff bound")
    return 0.0, bound


def interval(row: dict[str, Any]) -> tuple[float, float]:
    """Read a cell or aggregate; the legacy cost field is the upper bound."""
    cost = row["cost"] if "cost" in row else row["costs"].get("price", 0)
    lo, hi = row.get("cost_interval", [cost, cost])
    if (
        not all(math.isfinite(v) for v in (lo, hi, cost))
        or not 0 <= lo <= hi
        or abs(hi - cost) > 1e-8
    ):
        raise ValueError("Malformed invoice interval")
    return lo, hi


def total_interval(rows: list[dict[str, Any]]) -> tuple[float, float]:
    bounds = [interval(row) for row in rows]
    return sum(lo for lo, _ in bounds), sum(hi for _, hi in bounds)
