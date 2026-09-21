"""Observed cache charges and request counts around the credit interruption.

This is an offline accounting diagnostic, not another model experiment. It
does not substitute a hypothetical warm-cache invoice or a different outcome.
Both harnesses run ``python -m experiments.ace_independent_audit.continuation_diagnosis``.
"""

from datetime import date, datetime
import gzip
import json
from typing import Any
from urllib.parse import urlparse

from .accounting import price
from .budget_replay import attempted_requests
from .common import CAMPAIGN, OUTPUT, REPORT, read, save, sha
from .economics import ledger_rows
from .quota_recovery import BATCH, CELL, FOLDER, administrative_rejections


def run() -> None:
    directory = OUTPUT / BATCH / "configs" / CELL
    rejected = administrative_rejections(CELL, directory)
    certificate = read(FOLDER / "continuation_certificate.json")
    preparation = read(FOLDER / "preparation.json")
    receipts = sorted(
        (r for r in ledger_rows() if r["cell"] == CELL),
        key=lambda r: r["created"],
    )
    responses: list[dict[str, Any]] = []
    for receipt in receipts:
        path = CAMPAIGN / "responses" / CELL / (receipt["id"] + ".json.gz")
        with gzip.open(path, "rt") as stream:
            raw = json.load(stream)
        if receipt["id"] in rejected:
            if not raw["exception"]["rejected"] or receipt["charged"] != 0:
                raise ValueError("The credit rejection changed")
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
            raise ValueError("Continuation receipt did not reprice exactly")
        responses.append(
            dict(
                receipt=receipt["id"],
                source_sha=sha(path),
                started=raw["started"],
                provider_status=response["status"],
                costs=costs,
            )
        )
    prefix_count = int(preparation["successful_responses"])
    first = responses[prefix_count]
    prefix_cost = sum(r["costs"]["price"] for r in responses[:prefix_count])
    continued_cost = sum(r["costs"]["price"] for r in responses[prefix_count:])
    if abs(prefix_cost + continued_cost - certificate["cost"]) > 1e-9:
        raise ValueError("Continuation total does not reconcile")
    replay_path = CAMPAIGN / "budget_replay" / (CELL + ".json")
    replays = read(replay_path)["rows"]
    reference = dict(cell=CELL, administrative_rejections=rejected)
    output = dict(
        cell=CELL,
        continuation_certificate_sha=sha(
            FOLDER / "continuation_certificate.json"
        ),
        prefix_responses=prefix_count,
        prefix_cost=prefix_cost,
        additional_responses=len(responses) - prefix_count,
        additional_cost=continued_cost,
        total_cost=certificate["cost"],
        solved=certificate["solved"],
        all_attempted_requests=len(receipts),
        rejected_zero_charge=rejected,
        first_resumed_response=first,
        gap_since_previous_request_seconds=(
            datetime.fromisoformat(first["started"])
            - datetime.fromisoformat(responses[prefix_count - 1]["started"])
        ).total_seconds(),
        responses=responses,
        budget_replay_sha=sha(replay_path),
        lower_budget_counts=[
            dict(
                cap=r["cap"],
                controller_spent_budget=r["spent_budget"],
                all_attempted_requests=attempted_requests(reference, r),
            )
            for r in replays
        ],
        paid_calls=0,
        interpretation=(
            "The first response after the overnight interruption has zero "
            "cache-read tokens. These observed charges remain in the original "
            "trajectory and all comparisons. The key change and elapsed time "
            "are not isolated interventions. No warm-cache counterfactual, "
            "replacement draw or corrected solve is inferred. The original "
            "response budget counts returned responses; all-attempt metrics "
            "also retain the zero-charge rejection when replay reaches it."
        ),
    )
    save(REPORT / "continuation_diagnosis.json", output)
    print(
        json.dumps(
            {k: output[k] for k in ("cell", "total_cost", "paid_calls")}
        )
    )


if __name__ == "__main__":
    run()
