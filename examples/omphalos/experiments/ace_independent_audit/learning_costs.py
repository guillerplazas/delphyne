"""Separate source evidence, reflection, curation and terminal-audit charges."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from typing import Any
from urllib.parse import urlparse

from .accounting import price
from .common import REPORT, save
from .economics import ledger_rows


def run() -> None:
    groups: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    details: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in ledger_rows():
        cell = row["cell"]
        if cell.startswith("ladder_v2__sol_medium__"):
            arm = "P1"
        elif cell.startswith("full_"):
            arm = cell.split("__")[0].removeprefix("full_")
        else:
            continue
        if row["status"] != "settled":
            raise ValueError("The full preparation has unresolved charges")
        role = (
            "reflect"
            if "__reflect__" in cell
            else "curate"
            if "__curate__" in cell
            else "terminal_audit"
        )
        usage = json.loads(row["usage"])
        value = price(
            usage,
            row["model"],
            on=datetime.fromtimestamp(row["created"], timezone.utc).date(),
            tier=usage["service_tier"],
            regional=urlparse(str(usage["endpoint"])).hostname
            != "api.openai.com",
        )
        if abs(value["price"] - row["charged"]) > 1e-10:
            raise ValueError("Preparation charge did not reconcile")
        groups[arm, role].update(value)
        groups[arm, role]["requests"] += 1
        details[arm].append(
            dict(cell=cell, role=role, receipt=row["id"], **value)
        )
    if set(details) != {"A2", "B1", "B2", "S1", "P1"}:
        raise ValueError("A full preparation recipe is missing")
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    for (arm, _), value in groups.items():
        totals[arm].update(value)
    save(
        REPORT / "learning_cost_breakdown.json",
        dict(
            roles={
                f"{arm}/{role}": dict(value)
                for (arm, role), value in groups.items()
            },
            totals={arm: dict(value) for arm, value in totals.items()},
            requests=dict(details),
            note="Actual recorded provider tariff; fixed recipes only. Source solver fees are reported separately in preparation_economics.json. Terminal audits are included. Token totals are quantities, not cost shares.",
        ),
    )
    print(json.dumps({a: dict(v) for a, v in totals.items()}, indent=2))


if __name__ == "__main__":
    run()
