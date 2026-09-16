"""Replay completed batches while other paid batches run, with HTTP blocked.

Only the replay process's receipts are checked: another supervised process
may legitimately settle new calls concurrently. Result hashes bind each
certificate to its immutable measurement. `--assemble` combines complete
batch certificates without paying or repeating already verified cells.
Both harnesses use this CLI with campaign main or budget.
"""

import argparse
from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command

from experiments import ace_economy_experiment as base
from experiments import ace_economy_validation as scoped
from runtime.campaign_budget import CampaignResponsesModel, Ledger


def own_receipts(campaign: Path) -> int:
    with Ledger(campaign / "ledger.sqlite3").connect() as db:
        return int(
            db.execute(
                "SELECT COUNT(*) FROM receipts WHERE pid=?", (os.getpid(),)
            ).fetchone()[0]
        )


def replay_batch(module: Any, batch: str) -> None:
    module.verify()
    if not (module.CAMPAIGN / f"batches/{batch}.json").exists():
        raise ValueError("Only completed batches may be replayed")
    destination = f"replays/{batch}.json"
    if (module.CAMPAIGN / destination).exists():
        return
    before = own_receipts(module.CAMPAIGN)
    checks: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    for config in module.configs(batch):
        original = module.cell_result(config)
        ident = module.name(config, None)
        if original is None:
            checks.append(dict(cell=ident, platform_failed=True))
            continue
        module.activate(events=False)
        args = config.instantiate(None)
        args.cache_mode, args.cache_file = (
            "replay",
            str(module.directory(config) / "cache.yaml"),
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
            result = run_command(
                run_strategy,
                args,
                ctx=replace(base.context(), cache_root=Path("/")),
                add_header=False,
            )
        if (
            result.result is None
            or result.result.success != original["success"]
            or result.result.spent_budget != original["spent_budget"]
            or json.loads(json.dumps(list(result.result.values)))
            != original["values"]
        ):
            raise ValueError("Replay mismatch: " + ident)
        checks.append(dict(cell=ident, passed=True))
        hashes[ident] = base.sha(module.directory(config) / "result.yaml")
    if own_receipts(module.CAMPAIGN) != before:
        raise ValueError("Replay process created a paid receipt")
    module.verify()
    module.save(
        destination,
        dict(passed=True, paid_calls=0, result_hashes=hashes, cells=checks),
    )
    print(
        json.dumps(dict(batch=batch, replayed=len(checks), paid_calls=0)),
        flush=True,
    )


def assemble(module: Any) -> None:
    module.verify()
    checks: list[dict[str, Any]] = []
    batches = scoped.BATCHES if module.NAME == scoped.NAME else ("validation",)
    for batch in batches:
        saved = module.read(f"replays/{batch}.json")
        if not saved["passed"] or saved["paid_calls"]:
            raise ValueError("Invalid batch replay certificate")
        by_id = {v["cell"]: v for v in saved["cells"]}
        jobs = module.configs(batch)
        if set(by_id) != {module.name(job, None) for job in jobs}:
            raise ValueError("Replay certificate has the wrong cells")
        for job in jobs:
            ident = module.name(job, None)
            if (
                by_id[ident].get("passed")
                and base.sha(module.directory(job) / "result.yaml")
                != saved["result_hashes"][ident]
            ):
                raise ValueError("Result changed since exact replay")
            checks.append(by_id[ident])
    module.save("replay.json", dict(passed=True, paid_calls=0, cells=checks))
    print(
        json.dumps(
            dict(campaign=module.NAME, replayed=len(checks), paid_calls=0)
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--campaign", choices=("main", "budget"), default="main"
    )
    parser.add_argument("--batches", nargs="+", default=[])
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()
    module: Any = scoped
    if args.campaign == "budget":
        from experiments import ace_economy_budget_experiment

        module = ace_economy_budget_experiment
    allowed = (
        set(scoped.BATCHES) if args.campaign == "main" else {"validation"}
    )
    if not set(args.batches) <= allowed:
        raise ValueError("Unregistered batch")
    for batch in args.batches:
        replay_batch(module, batch)
    if args.assemble:
        assemble(module)


if __name__ == "__main__":
    main()
