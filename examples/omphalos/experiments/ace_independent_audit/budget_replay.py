"""Lower stopping budgets on exact saved trajectories, with HTTP forbidden.

This is a deterministic controller experiment, not new model samples.
Only completed frozen cells participate. The original $0.10 inner policy
is retained and an outer $0.05, $0.075 or $0.09 budget uses Delphyne's real
barrier admission. Repricing or truncating an array of costs would not
capture whether a crossing request's subsequent proof check is admitted.
No prompt, output limit, model response or verifier result is changed.
"""

from concurrent.futures import ProcessPoolExecutor
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

from runtime.campaign_budget import CampaignResponsesModel

from . import campaign as c
from .analysis import metrics, paired
from .common import CAMPAIGN, OUTPUT, REPORT, now, read, save, sha
from .completion import require_closed
from .transport import AuditModel
from .workflow import result

CAPS = (0.05, 0.075, 0.09)


def register() -> None:
    path = CAMPAIGN / "budget_replay_protocol.json"
    if path.exists():
        return
    save(
        path,
        dict(
            registered_at=now(),
            reference_cap=0.10,
            lower_caps=CAPS,
            cells=1280,
            replay_scenarios=3840,
            arms=["A0", "A1", "A2", "B0", "B1", "B2", "S1", "P1"],
            scope="Both development partitions, two replicates; frozen books only. Online controls supply frozen A0/B0 train cells.",
            estimand="Exact original controller with a smaller outer spending allowance, preserving observed cached responses and actual cache charges. Each arm gets the same cap. Also compare the cost/coverage frontier across caps.",
            limitations="Conditional on the recorded trajectories, responses and cache behavior; not independent evidence of model reproducibility and not a new test sample. A stopping allowance is not a hard billing ceiling.",
            security="HTTP disabled, immutable paid cache hashes, no new calls or proof synthesis; retained proofs must equal the original certified proof.",
            decision="Describe cost/coverage and cost per solve; target at least10% lower cost with at most2 lost solves per40, averaged over replicates. No significance gate or replacement attempts.",
        ),
    )


def register_supplement() -> None:
    path = CAMPAIGN / "budget_replay_supplement.json"
    if path.exists():
        return
    save(
        path,
        dict(
            registered_at=now(),
            arms={"R1": 80, "O1": 160},
            lower_caps=CAPS,
            cells=240,
            replay_scenarios=720,
            overall_frozen_cells=1520,
            overall_replay_scenarios=4560,
            paid_calls=0,
            meaning="Apply the same original budget-replay protocol to the separately registered rule-repair and adaptive-frozen follow-ups. These conditional controller replays are not new solver samples.",
        ),
    )


def replay_cell(item: tuple[str, dict[str, Any]]) -> list[dict[str, Any]]:
    batch, encoded = item
    job = c.Job(**encoded)
    if job.arm.startswith("online_"):
        raise ValueError(
            "Changing online stopping would change later learning"
        )
    c.activate()
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
        CAMPAIGN / "budget_replay_events.jsonl"
    )
    identity = c.name(job, None)
    directory = OUTPUT / batch / "configs" / identity
    if (CAMPAIGN / "terminal_failures" / (identity + ".json")).exists():
        from .terminal_failure import hashes as terminal_hashes

        hashes = terminal_hashes(directory)
    else:
        hashes = {
            name: sha(directory / name)
            for name in ("result.yaml", "cache.yaml")
        }
    certificate = CAMPAIGN / "budget_replay" / (identity + ".json")
    if certificate.exists():
        prior = read(certificate)
        if prior["hashes"] != hashes:
            raise ValueError("Budget replay input changed")
        return prior["rows"]
    expected = result(batch, identity)
    rows: list[dict[str, Any]] = []
    for cap in CAPS:
        args = job.instantiate(None)
        args.budget = dict(price=cap, num_requests=32)
        args.cache_mode = "replay"
        args.cache_file = str(directory / "cache.yaml")
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                AuditModel,
                "_send_final_request",
                side_effect=AssertionError("HTTP forbidden"),
            ),
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("HTTP forbidden"),
            ),
            patch(
                "openai.OpenAI", side_effect=AssertionError("HTTP forbidden")
            ),
            redirect_stdout(io.StringIO()),
        ):
            output = run_command(
                run_strategy,
                args,
                ctx=replace(c.context(), cache_root=Path("/")),
                add_header=False,
            )
        if output.result is None or output.diagnostics:
            raise ValueError(
                f"Budget replay failed: {identity}: {output.diagnostics}"
            )
        replay = output.result
        if replay.values and list(replay.values) != expected["values"]:
            raise ValueError("Budget replay synthesized a different proof")
        if (
            replay.spent_budget.get("price", 0)
            > expected["spent_budget"].get("price", 0) + 1e-9
        ):
            raise ValueError("Smaller budget increased observed expenditure")
        rows.append(
            dict(
                cell=identity,
                arm=job.arm,
                stage=job.stage,
                theorem=job.theorem,
                seed=job.seed,
                cap=cap,
                solved=bool(replay.values),
                spent_budget=dict(replay.spent_budget),
                paid_calls=0,
            )
        )
    if hashes != {name: sha(directory / name) for name in hashes}:
        raise ValueError("Budget replay changed a paid artifact")
    save(certificate, dict(hashes=hashes, batch=batch, rows=rows))
    return rows


def run_completed() -> None:
    register()
    register_supplement()
    batches = [
        entry["batch"]
        for entry in read(CAMPAIGN / "core_schedule.json")["batches"]
    ]
    batches += [
        f"online-o{order}-s{step:02d}"
        for order in (0, 1)
        for step in range(40)
    ]
    batches += ["rule_repairs", "adaptive_frozen"]
    items: list[tuple[str, dict[str, Any]]] = []
    skipped: list[str] = []
    for batch in batches:
        try:
            require_closed(batch)
        except (ValueError, FileNotFoundError):
            if not (
                CAMPAIGN / "terminal_failures" / (batch + ".json")
            ).exists():
                skipped.append(batch)
                continue
            from .terminal_failure import assert_closed

            assert_closed(batch)
        for encoded in read(CAMPAIGN / "batches" / f"{batch}.json"):
            if not encoded["arm"].startswith("online_"):
                items.append((batch, encoded))
    with ProcessPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(replay_cell, items))
    print(
        json.dumps(
            dict(
                eligible_cells=len(items),
                completed_scenarios=sum(map(len, results)),
                pending_batches=len(skipped),
                paid_calls=0,
            )
        ),
        flush=True,
    )


def attempted_requests(
    reference: dict[str, Any], replay: dict[str, Any]
) -> int:
    """Retain an observed administrative rejection if replay reaches it.

    The controller budgets successful responses. All-attempt reporting also
    counts certified zero-charge administrative rejections preceding a
    response reached by this replay. It changes no stopping decision.
    """
    requests = int(
        replay.get(
            "attempted_requests",
            replay["spent_budget"].get("num_requests", 0),
        )
    )
    rejected = reference.get("administrative_rejections")
    if not rejected:
        return requests
    events = reference.get("administrative_rejection_positions")
    successful = replay["spent_budget"].get("num_requests", 0)
    if events is not None:
        if [event["receipt"] for event in events] != rejected:
            raise ValueError("Administrative rejection identities differ")
        return requests + sum(
            event["before_response"] <= successful for event in events
        )
    # Compatibility for the separately recorded one-cell credit diagnostic.
    from .quota_recovery import CELL, FOLDER, RECEIPT

    if reference["cell"] != CELL or rejected != [RECEIPT]:
        raise ValueError("Unrecognized administrative rejection in replay")
    prefix = read(FOLDER / "preparation.json")
    if successful > prefix["successful_responses"]:
        requests += len(rejected)
    return requests


def finalize() -> None:
    from collections import defaultdict

    from .families import mapping

    original = [
        r
        for r in read(REPORT / "fresh_cells.json")
        if not r["arm"].startswith("online_")
    ]
    if len(original) != 1280:
        raise ValueError("Frozen reference denominator changed")
    original += read(REPORT / "rule_repair_cells.json")
    original += read(REPORT / "adaptive_frozen_cells.json")
    if len(original) != 1520:
        raise ValueError("Supplemented frozen denominator changed")
    groups: dict[tuple[str, str, float], list[dict[str, Any]]] = defaultdict(
        list
    )
    compact: list[dict[str, Any]] = []
    for reference in original:
        prior = read(
            CAMPAIGN / "budget_replay" / (reference["cell"] + ".json")
        )
        expected_hashes: dict[str, Any] = {
            "result.yaml": reference["result_sha"],
            "cache.yaml": reference["cache_sha"],
        }
        if reference.get("terminal_failure"):
            expected_hashes["exception.txt"] = reference["exception_sha"]
        if prior["hashes"] != expected_hashes:
            raise ValueError("Budget replay does not match final reference")
        for rr in prior["rows"]:
            row = dict(reference)
            row.update(
                solved=rr["solved"],
                costs=dict(price=rr["spent_budget"].get("price", 0)),
                counts=dict(requests=attempted_requests(reference, rr)),
                turns=[],
            )
            groups[row["stage"], row["arm"], rr["cap"]].append(row)
            compact.append(
                dict(rr, attempted_requests=row["counts"]["requests"])
            )
        full = dict(reference, turns=[])
        groups[full["stage"], full["arm"], 0.10].append(full)
    comparisons: dict[str, Any] = {}
    for (stage, arm, cap), values in groups.items():
        base = "B0" if arm.startswith("B") else "A0"
        if arm not in ("A0", "B0"):
            reference = groups[stage, base, cap]
            comparisons[f"{stage}/{arm}/{cap:g}"] = dict(
                theorem=paired(reference, values),
                family=paired(reference, values, mapping()),
            )
    save(REPORT / "budget_replay_cells.json", compact)
    save(
        REPORT / "budget_replay_results.json",
        dict(
            cells=1520,
            scenarios=len(compact),
            paid_calls=0,
            metrics={
                f"{stage}/{arm}/{cap:g}": {
                    key: value
                    for key, value in metrics(values).items()
                    if key
                    in (
                        "n",
                        "theorems",
                        "solves",
                        "coverage",
                        "cost",
                        "cost_per_solve",
                        "failed_cost",
                        "requests",
                        "max_cell_cost",
                        "cost_interval",
                        "cost_per_solve_interval",
                        "failed_cost_interval",
                        "bounded_cost_cells",
                        "unknown_charge_upper",
                        "cost_is_exact",
                        "billing_note",
                    )
                }
                for (stage, arm, cap), values in groups.items()
            },
            comparisons=comparisons,
            interpretation=read(CAMPAIGN / "budget_replay_protocol.json"),
            supplement=read(CAMPAIGN / "budget_replay_supplement.json"),
        ),
    )
    print(
        json.dumps(dict(finalized=True, scenarios=len(compact), paid_calls=0))
    )


if __name__ == "__main__":
    import sys

    actions = {
        "register": register,
        "register-supplement": register_supplement,
        "run-completed": run_completed,
        "finalize": finalize,
    }
    if len(sys.argv) != 2 or sys.argv[1] not in actions:
        raise SystemExit("Use register, run-completed, or finalize")
    actions[sys.argv[1]]()
