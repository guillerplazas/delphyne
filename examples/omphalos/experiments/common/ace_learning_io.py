"""Accounting and exact replay for the ACE learning campaign.

These routines retain the v2 accounting/replay semantics and take an
explicit campaign object, avoiding imports of a sealed campaign driver.
"""

from collections import defaultdict
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import datetime, timezone
import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.model_registry import price_tokens


def accounting(campaign: Path) -> dict[str, Any]:
    ledger = Ledger(campaign / "ledger.sqlite3")
    costs: dict[str, float] = defaultdict(float)
    tokens: dict[str, dict[str, int]] = defaultdict(
        lambda: dict(input=0, cached=0, output=0)
    )
    unresolved: list[str] = []
    issues: list[str] = []
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,usage,cell,status FROM receipts"
        ).fetchall()
    for ident, model, created, charged, usage, cell, status in rows:
        if status != "settled" or charged is None:
            unresolved.append(ident)
            continue
        u = json.loads(usage or "{}")
        if "exception" in u:
            issues.append(ident)
        if charged or "input_tokens" in u:
            inp, out = u["input_tokens"], u["output_tokens"]
            cached = u.get("input_tokens_details", {}).get("cached_tokens", 0)
            actual = price_tokens(
                model,
                inp,
                cached,
                out,
                on=datetime.fromtimestamp(created, timezone.utc).date(),
            )
            if abs(actual - charged) > 1e-8:
                raise ValueError("Receipt repricing mismatch")
            for k, v in (("input", inp), ("cached", cached), ("output", out)):
                tokens[cell][k] += v
        costs[cell] += charged
    return dict(
        total=sum(costs.values()),
        costs=dict(costs),
        tokens=dict(tokens),
        receipts=len(rows),
        unresolved=unresolved,
        billing_issues=issues,
        ledger=ledger.summary(),
    )


def replay(c: Any) -> None:
    c.verify()
    before = accounting(c.CAMPAIGN)["receipts"]
    checks: list[dict[str, Any]] = []
    for config in c.all_configs():
        original = c.cell_result(config)
        if original is None:
            checks.append(
                dict(cell=c.name(config, None), platform_failed=True)
            )
            continue
        c.activate(config.stage, events=False)
        args = config.instantiate(None)
        args.cache_mode, args.cache_file = (
            "replay",
            str(c.directory(config) / "cache.yaml"),
        )
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Replay forbids HTTP"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(c.context(), cache_root=Path("/")),
                add_header=False,
            )
        if (
            out.result is None
            or out.result.success != original["success"]
            or out.result.spent_budget != original["spent_budget"]
            or json.loads(json.dumps(list(out.result.values)))
            != original["values"]
        ):
            raise ValueError("Exact replay mismatch: " + c.name(config, None))
        checks.append(dict(cell=c.name(config, None), passed=True))
    assert before == accounting(c.CAMPAIGN)["receipts"]
    c.save(
        f"replays/{len(checks)}.json",
        dict(passed=True, paid_calls=0, cells=checks),
    )
