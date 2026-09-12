"""HTTP-forbidden compatibility checks before the capacity campaign."""

# ruff: noqa: E402
from runtime.development_only import install

install()

from contextlib import redirect_stdout
from dataclasses import replace
import io
import os
from typing import Any, cast
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from experiments.ace import ace_capacity_experiment as c
from runtime.campaign_budget import CampaignResponsesModel


def main() -> None:
    before = c.accounting()
    c.activate("cross")
    rows: list[dict[str, Any]] = []
    # This verifies observed requests only. Old missing transport state
    # remains unavailable; terminal parity is established by new snapshots.
    original = c.old.read("preflight.json")["cells"]
    for ref in original:
        cfg = c.old.proof(ref["partition"], "luna-ace", ref["theorem"])
        args = cfg.instantiate(None)
        args.args.update(feedback_version=1, prompt_turn_budget=64)
        args.cache_mode = "replay"
        args.cache_file = f"configs/{ref['name']}/cache.yaml"
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        args.budget["num_requests"] = ref["requests"]
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "0"
        ctx = replace(c.context(), cache_root=c.ROOT / ref["source"])
        with patch.object(
            CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("HTTP forbidden"),
        ):
            with redirect_stdout(io.StringIO()):
                result = run_command(
                    run_strategy, args, ctx=ctx, add_header=False
                )
        outcome = cast(Any, result.result)
        if outcome is None or outcome.success != ref["success"]:
            raise ValueError((ref["name"], result.diagnostics))
        if outcome.spent_budget.get("num_completions", 0) != ref["requests"]:
            raise ValueError((ref["name"], "observed request mismatch"))
        rows.append(
            dict(
                theorem=ref["theorem"],
                partition=ref["partition"],
                requests=ref["requests"],
                success=outcome.success,
            )
        )
        if len(rows) % 20 == 0:
            print(f"Observed-request parity {len(rows)}/80", flush=True)
    assert len(rows) == 80
    assert c.accounting()["total_spend"] == before["total_spend"]
    tests = (c.CAMPAIGN / "tests_preflight.log").read_text()
    types = (c.CAMPAIGN / "typecheck_preflight.log").read_text()
    assert "failed" not in tests and "passed" in tests
    assert "0 errors, 0 warnings" in types
    c.save(
        "preflight.json",
        dict(
            passed=True,
            paid_requests=0,
            historical_observed_request_parity=rows,
            historical_limitation="No exact terminal claim for old snapshots; estimates disabled while replaying the known prefix",
            new_transport="Full policy/Rocq interrupted-continuation and HTTP-disabled exact replay tests pass",
            tests_log_sha256=c.old.digest(c.CAMPAIGN / "tests_preflight.log"),
            typecheck_log_sha256=c.old.digest(
                c.CAMPAIGN / "typecheck_preflight.log"
            ),
            source_archive=c.old.digest(
                c.CAMPAIGN / "prior_source_manifest.json"
            ),
        ),
    )


if __name__ == "__main__":
    main()
