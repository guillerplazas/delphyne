"""Registered decisions and complete-cell reports for the ACE review.

Commands: calibration, selection, final, status. Decision files are
immutable; rerunning an identical decision is allowed. No API calls and
no holdout trajectory inspection. Actual receipts include failed attempts
and uncertain charges at their reserved upper bound.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from datetime import datetime
from typing import Any

import yaml


import experiments.common.minif2f_x as x  # noqa: E402
from ace.ace_playbook import Playbook  # noqa: E402
from tools.data.ace_review_benchmark import load as load_challenge  # noqa: E402
from experiments.ace.ace_review_experiment import CAMPAIGN  # noqa: E402
from runtime.campaign_budget import Ledger  # noqa: E402
from tools.analysis.cell_records import cells_of_run  # noqa: E402
from tools.analysis.paired_evaluation import Cell, Observation, compare  # noqa: E402

ROOT = OMPHALOS_ROOT


def freeze(file: str, data: dict[str, Any]) -> None:
    path = CAMPAIGN / file
    content = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != content:
            raise ValueError(f"refusing to change frozen decision {path}")
        return
    with path.open("x") as out:
        out.write(content)


def panel(
    phase: str,
) -> tuple[dict[str, dict[Cell, Observation]], dict[str, Any]]:
    run = ROOT / f"experiments/output/ace_review_{phase}"
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        receipts = db.execute(
            "SELECT cell,SUM(COALESCE(charged,reserved)),"
            "SUM(status='in_flight'),SUM(status='unknown_charge'),COUNT(*) "
            ",SUM(CASE WHEN status='settled' THEN charged ELSE 0 END) "
            "FROM receipts GROUP BY cell"
        ).fetchall()
    charges = {
        str(r[0]): (float(r[1]), int(r[2]), int(r[3]), int(r[4]), float(r[5]))
        for r in receipts
    }
    arms: dict[str, dict[Cell, Observation]] = defaultdict(dict)
    details: dict[str, Any] = {}
    if not run.exists():
        return {}, {}
    state: Any = yaml.load(
        (run / "experiment.yaml").read_text(), Loader=yaml.CSafeLoader
    )
    for rec in cells_of_run(run):
        exception = run / "configs" / rec.name / "exception.txt"
        if (
            rec.platform_failed
            and exception.exists()
            and any(
                marker in exception.read_text()
                for marker in (
                    "CampaignExhausted",
                    "OPENAI_API_KEY",
                    "AuthenticationError",
                )
            )
        ):
            # Administrative censoring is an incomplete study, not a
            # measured inability of the prover to solve the theorem.
            continue
        cost, pending, unknown, attempts, lower = charges.get(
            rec.name, (0.0, 0, 0, 0, 0.0)
        )
        if pending:
            continue  # Still unsettled, so this is not a completed cell.
        if rec.requests and not attempts:
            raise ValueError(f"missing billing receipts: {rec.name}")
        if rec.cell in arms[rec.arm]:
            raise ValueError(f"duplicate cell {rec.arm} {rec.cell}")
        arms[rec.arm][rec.cell] = Observation(
            rec.solved, cost, rec.platform_failed
        )
        info = state["configs"][rec.name]
        start, end = info.get("start_time"), info.get("end_time")
        duration = (
            (end - start).total_seconds()
            if isinstance(start, datetime) and isinstance(end, datetime)
            else None
        )
        details[rec.name] = dict(
            **rec.as_dict(),
            charged_cost=cost,
            http_attempts=attempts,
            uncertain_attempts=unknown,
            charged_lower_bound=lower,
            last_attempt_seconds=duration,
        )
    return dict(arms), details


def expected(names: list[str], seeds: tuple[int, ...] = (0, 1)) -> list[Cell]:
    return [(name, str(seed)) for name in names for seed in seeds]


def require_complete(result: dict[str, Any]) -> None:
    if not result["complete"]:
        raise ValueError(json.dumps(result))


def calibrated_requests() -> int:
    return int(
        json.loads((CAMPAIGN / "calibration.json").read_text())["requests"]
    )


def calibration() -> dict[str, Any]:
    arms, _ = panel("calibration")
    keys = expected(list(x.TRAINX_PROBLEMS))
    a, b = arms.get("baseline-r32", {}), arms.get("baseline-r64", {})
    result = compare(a, b, keys, alpha=0.05, confidence=0.95)
    require_complete(result)
    seeds: dict[str, Any] = {}
    for seed in (0, 1):
        seeds[str(seed)] = compare(
            a,
            b,
            [c for c in keys if c[1] == str(seed)],
            alpha=0.05,
            confidence=0.95,
        )
    choose64 = result["effect"] >= 0.05 - 1e-12 and all(
        r["effect"] >= 0 for r in seeds.values()
    )
    decision = dict(
        requests=64 if choose64 else 32, paired=result, seeds=seeds
    )
    freeze("calibration.json", decision)
    return decision


def selection() -> dict[str, Any]:
    requests = calibrated_requests()
    arms, details = panel("development")
    keys = expected(list(x.VALIDATIONX_PROBLEMS))
    baseline = arms.get(f"baseline-r{requests}", {})
    comparisons: dict[str, Any] = {}
    for label in ("x3", "repair0", "repair1"):
        comparisons[label] = compare(
            baseline,
            arms.get(f"{label}-r{requests}", {}),
            keys,
            alpha=0.05,
            confidence=0.95,
        )
        require_complete(comparisons[label])
    # Seed1 is a stability replicate, never an alternative deployment seed.
    winner = min(
        ("x3", "repair0"),
        key=lambda a: (
            -comparisons[a]["solved_b"],
            comparisons[a]["cost_b"],
            a != "x3",
        ),
    )
    playbook = (
        "ace_x3_offline.yaml"
        if winner == "x3"
        else "ace_review_repair_s0.yaml"
    )
    sha = Playbook.load(ROOT / "experiments/playbooks" / playbook).sha256()
    stability = compare(
        arms[f"repair0-r{requests}"],
        arms[f"repair1-r{requests}"],
        keys,
        alpha=0.05,
        confidence=0.95,
    )
    decision = dict(
        requests=requests,
        arm=winner,
        playbook=playbook,
        playbook_sha256=sha,
        comparisons=comparisons,
        training_seed_stability=stability,
        development_cells=len(details),
        challenge_sha256=load_challenge()["sha256"],
    )
    freeze("selection.json", decision)
    return decision


def final_report() -> dict[str, Any]:
    selection_data: dict[str, Any] = json.loads(
        (CAMPAIGN / "selection.json").read_text()
    )
    challenge = load_challenge()
    if challenge["sha256"] != selection_data["challenge_sha256"]:
        raise ValueError("challenge changed after selection")
    playbook = ROOT / "experiments/playbooks" / selection_data["playbook"]
    if Playbook.load(playbook).sha256() != selection_data["playbook_sha256"]:
        raise ValueError("selected playbook changed")
    requests = int(selection_data["requests"])
    arms, details = panel("confirmation")
    keys = expected(list(challenge["problems"]))
    families = {n: r["family"] for n, r in challenge["problems"].items()}
    baseline, selected = (
        arms.get(f"baseline-r{requests}", {}),
        arms.get(f"selected-r{requests}", {}),
    )
    primary = compare(
        baseline,
        selected,
        keys,
        families=families,
        alpha=0.05,
        confidence=0.95,
    )
    require_complete(primary)
    terra_arms, terra_details = panel("terra")
    terra_keys = expected(challenge["terra_subset"], (0,))
    reference = compare(
        terra_arms.get("terra-r32", {}),
        selected,
        terra_keys,
        families=families,
        cap_a=0.30,
        cap_b=0.10,
        alpha=0.05,
        confidence=0.95,
    )
    require_complete(reference)
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        adaptation = (
            float(
                db.execute(
                    "SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM receipts WHERE cell LIKE 'review-repair-s0:%'"
                ).fetchone()[0]
            )
            if selection_data["arm"] == "repair0"
            else 0.0
        )
    cheap_mean = reference["cost_b"] / len(terra_keys)
    terra_mean = reference["cost_a"] / len(terra_keys)
    amortization = {
        str(n): dict(
            cost_per_problem=cheap_mean + adaptation / n,
            fraction_of_terra=(cheap_mean + adaptation / n) / terra_mean
            if terra_mean
            else None,
        )
        for n in (100, 1000, 10000)
    }
    result = dict(
        primary=primary,
        terra_reference=reference,
        cost_target_fraction=1 / 3,
        meets_cost_target=reference["cost_ratio"] is not None
        and reference["cost_ratio"] <= 1 / 3,
        selected_adaptation_cost=adaptation,
        adaptation_cost_note="Charged seed0 training, or zero incremental cost when reusing the previously frozen x3 artifact; original x3 training is a sunk cost.",
        amortization=amortization,
        ledger=ledger.summary(),
        selection=selection_data,
        training=training_diagnostics(),
        calibration=json.loads((CAMPAIGN / "calibration.json").read_text()),
        challenge_sha256=challenge["sha256"],
        uncertain_attempts=sum(
            int(d["uncertain_attempts"])
            for d in [*details.values(), *terra_details.values()]
        ),
        latency={
            label: dict(
                median_last_attempt_seconds=statistics.median(durations),
                maximum_last_attempt_seconds=max(durations),
                note="Recorded last-attempt wall time; earlier failed attempts remain in cost but are excluded from this duration.",
            )
            for label in ("baseline", "selected", "terra")
            if (
                durations := [
                    float(d["last_attempt_seconds"])
                    for name, d in {**details, **terra_details}.items()
                    if f"__{label}-" in name
                    and d["last_attempt_seconds"] is not None
                ]
            )
        },
        cells_sha256=hashlib.sha256(
            json.dumps([details, terra_details], sort_keys=True).encode()
        ).hexdigest(),
    )
    freeze("final_report.json", result)
    freeze("final_cells.json", dict(confirmation=details, terra=terra_details))
    return result


def training_diagnostics() -> dict[str, Any]:
    results: dict[str, Any] = {}
    for seed in (0, 1):
        variant = f"review-repair-s{seed}"
        folder = ROOT / f"experiments/output/ace_adaptation_{variant}"
        repairs: list[dict[str, Any]] = (
            yaml.safe_load((folder / "repairs.yaml").read_text()) or []
        )
        with (
            ROOT / f"experiments/playbooks/ace_adaptation_{variant}/steps.csv"
        ).open() as file:
            rows = list(csv.DictReader(file))
        pb = Playbook.load(
            ROOT / f"experiments/playbooks/ace_review_repair_s{seed}.yaml"
        )
        results[str(seed)] = dict(
            original_episodes=len(rows),
            original_solved=sum(int(r["generator_solved"]) for r in rows),
            repair_episodes=len(repairs),
            repaired_theorems=len({r["bench"] for r in repairs}),
            recovered_theorems=len(
                {r["bench"] for r in repairs if r.get("solved")}
            ),
            bullets=len(pb.bullets),
            estimated_tokens=pb.token_estimate(),
            sha256=pb.sha256(),
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("calibration", "selection", "final", "status")
    )
    args = parser.parse_args()
    if args.command == "status":
        result = Ledger(CAMPAIGN / "ledger.sqlite3").summary()
    else:
        result = {
            "calibration": calibration,
            "selection": selection,
            "final": final_report,
        }[args.command]()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
