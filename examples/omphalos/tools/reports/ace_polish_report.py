"""Train-only preparation and complete-panel readout; no paid calls.

Both harnesses: python -m tools.reports.ace_polish_report prepare|freeze|report.
Cache order proposes transitions; only live Rocq verification admits them.
"""

from collections import Counter, defaultdict
from dataclasses import asdict, replace
from datetime import datetime, timezone
import csv
import io
import json
from pathlib import Path
import re
import sys
from typing import Any

import yaml
from delphyne.utils.typing import pydantic_load

import ace.ace_grounded as ag
from ace.ace_evidence import import_signature, unknown_identifier
from experiments.ace.ace_polish_experiment import (
    CAMPAIGN,
    MECHANISMS,
    ROOT,
    configs,
    digest,
    name,
)
import experiments.common.miniF2F_bench as mf
from runtime.campaign_budget import Ledger
from runtime.model_registry import price_tokens
import runtime.pytanque_utils as pt
from runtime.tool_budget import ToolLimits
from tools.analysis.cell_records import cells_of_run
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from tools.data.prepare_control_cycle_grounded import transitions
from tools.data.prepare_grounded import candidates
from tools.reports.grounded_report import families, write_new


def checks(directory: Path) -> list[dict[str, Any]]:
    path = directory / "cache.yaml"
    if not path.exists():
        return []
    raw: Any = yaml.load(path.read_text(), Loader=yaml.CSafeLoader) or []
    result: list[dict[str, Any]] = []
    for entry in raw:
        chat = entry.get("input", {}).get("request", {}).get("chat", [])
        outputs: Any = (entry.get("output") or dict[str, Any]()).get(
            "outputs", []
        )
        if (
            not chat
            or not outputs
            or not str(chat[-1].get("content", "")).startswith(
                "fun: checked_proof"
            )
        ):
            continue
        response = yaml.load(outputs[0]["content"], Loader=yaml.CSafeLoader)
        result.append(response)
    return result


def source_hashes() -> dict[str, str]:
    paths = {
        ROOT / "delphyne.yaml",
        ROOT / "experiments/ace/ace_polish_experiment.py",
        ROOT / "experiments/ace/ace_bounded_experiment.py",
    }
    for pattern in (
        "prove_*.py",
        "runtime/*.py",
        "ace/*.py",
        "prompts/**/*.jinja",
        "demos/*.demo.yaml",
        "experiments/common/*.py",
    ):
        paths.update(ROOT.glob(pattern))
    paths.update(
        ROOT / f"benchmarks/{part}X.txt" for part in ("train", "validation")
    )
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}


def prepare() -> None:
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    if (CAMPAIGN / "registration.json").exists():
        raise ValueError(
            "already registered; do not reselect from pilot results"
        )
    pool = transitions() + candidates()
    grouped: dict[str, list[ag.TrainingTransition]] = defaultdict(list)
    for e in sorted(
        pool,
        key=lambda e: (
            not bool(e.verified_solution),
            e.theorem_name,
            e.failed_action,
        ),
    ):
        grouped[ag.failure_category(e.error)].append(e)
    ordered = [
        g[i]
        for i in range(max(map(len, grouped.values()), default=0))
        for _, g in sorted(grouped.items())
        if i < len(g)
    ]
    decisions: list[ag.ClaimVerdict] = []
    used: set[tuple[str, str]] = set()
    for e in ordered:
        if len(decisions) >= 24:
            break
        category = ag.failure_category(e.error)
        if (e.theorem_name, category) in used:
            continue
        claim = ag.AdviceClaim(
            f"polish-{len(decisions):02d}",
            ag.decision_kind(pt.Feedback(False, 0, e.failed_action, e.error)),
            f"Local {category} transition; match the supporting types and hypotheses.",
            (),
            e.correction,
            e,
            import_signature(ROOT / e.problem_file),
            unknown_identifier(e.error) or "",
        )
        verdict = ag.validate_claim(claim, ToolLimits(seconds=10))
        if verdict.status == "verified":
            goals = "\n".join(verdict.before_goals)
            symbols = tuple(
                sorted(
                    set(
                        re.findall(
                            r"\b(?:INR|IZR|Z\.\w+|Nat\.\w+|sqrt|ln|sin|cos|Rabs|R|nat|Z|In|Ensemble)\b",
                            goals,
                        )
                    )
                )
            )[:2]
            claim = replace(
                claim,
                symbols=symbols,
                evidence=replace(e, goals=verdict.before_goals),
            )
            verdict = replace(verdict, claim=claim)
            used.add((e.theorem_name, category))
        decisions.append(verdict)
    state = ag.AdaptationState().admit(tuple(decisions))
    artifact = CAMPAIGN / "artifact.json"
    write_new(
        artifact,
        {
            "state": asdict(state),
            "source": "trainX-only reverified transitions",
        },
    )
    demos = [
        {
            "demonstration": c.id,
            "query": "WorkedProofTransition",
            "args": {"claim_id": c.id, "evidence": asdict(c.evidence)},
            "answers": [
                {
                    "answer": "```rocq\n" + "\n".join(c.action) + "\n```",
                    "example": True,
                }
            ],
        }
        for c in state.claims
        if c.symbols or c.trigger_name
    ]
    demo_path = ROOT / "demos/polished.demo.yaml"
    if demo_path.exists():
        raise ValueError("refusing to overwrite demonstrations")
    demo_path.write_text(yaml.safe_dump(demos, sort_keys=False))

    run = ROOT / "experiments/output/ace_control_cycle_tuning"
    records = list(cells_of_run(run))
    inventory: dict[str, Any] = {}
    for row in records:
        history = checks(run / "configs" / row.name)
        matches = sum(
            bool(
                ag.select_matched_advice(
                    state.claims,
                    pydantic_load(pt.Feedback, c["feedback"]),
                    import_signature(ROOT / row.params["problem_file"]),
                )
            )
            for c in history
        )
        inventory[row.bench] = {
            "cell": row.name,
            "solved": row.solved,
            "cost": row.cost,
            "requests": row.requests,
            "outcomes": dict(Counter(c["outcome"] for c in history)),
            "categories": dict(
                Counter(
                    ag.failure_category(
                        c["feedback"].get("error_message") or ""
                    )
                    for c in history
                )
            ),
            "matched_checks": matches,
            "last": history[-1:],
        }
    ordered_records = sorted(records, key=lambda r: (-r.requests, r.bench))
    hard = [r.bench for r in ordered_records if not r.solved]
    late = [r.bench for r in ordered_records if r.solved]
    recovery = (
        sorted(
            hard,
            key=lambda n: (
                -sum(
                    inventory[n]["outcomes"].get(k, 0)
                    for k in ("unknown", "resource_exhausted")
                ),
                n,
            ),
        )[:2]
        + late[:2]
    )
    matched = sorted(
        inventory, key=lambda n: (-inventory[n]["matched_checks"], n)
    )[:4]
    output = late[:2] + hard[:2]
    registration = {
        "api_ceiling": 8,
        "cells": 224,
        "seed_pilots": 0,
        "pilots": dict(zip(MECHANISMS, (recovery, matched, output))),
        "artifact_sha256": digest(artifact),
        "execution_hashes": source_hashes(),
        "families": families(
            dict(mf.load_partition("benchmarks/validationX.txt"))
        ),
        "teacher_episodes": 0,
        "coverage": dict(
            Counter(
                ag.failure_category(c.evidence.error) for c in state.claims
            )
        ),
    }
    write_new(CAMPAIGN / "training_inventory.json", inventory)
    write_new(CAMPAIGN / "registration.json", registration)
    print(
        json.dumps(
            {
                "claims": len(state.claims),
                "coverage": registration["coverage"],
                "pilots": registration["pilots"],
            },
            indent=2,
        )
    )


def charged_cells() -> dict[str, float]:
    with Ledger(CAMPAIGN / "ledger.sqlite3").connect() as db:
        return {
            str(cell): float(cost)
            for cell, cost in db.execute(
                "SELECT cell,SUM(COALESCE(charged,reserved)) FROM receipts GROUP BY cell"
            )
        }


def seal() -> None:
    """Seal final implementation after offline checks, before any payment."""
    path = CAMPAIGN / "ledger.sqlite3"
    if path.exists():
        with Ledger(path).connect() as db:
            if db.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]:
                raise ValueError("cannot reseal after paid execution")
    registration_path = CAMPAIGN / "registration.json"
    data = json.loads(registration_path.read_text())
    data["execution_hashes"] = source_hashes()
    data["sealed_before_payment"] = True
    registration_path.write_text(
        json.dumps(data, sort_keys=True, indent=2) + "\n"
    )


def navigation() -> None:
    """Add executable paths and one unsafe-action rejection to the demos."""
    path = ROOT / "demos/polished.demo.yaml"
    demos: Any = yaml.safe_load(path.read_text())
    if any(d.get("strategy") for d in demos):
        raise ValueError("navigation tests already generated")
    raw = json.loads((CAMPAIGN / "artifact.json").read_text())
    state = pydantic_load(ag.AdaptationState, raw["state"])
    for claim in state.claims:
        demos.append(
            {
                "demonstration": claim.id + "-checked",
                "strategy": "verify_worked_transition",
                "args": {"claim": asdict(claim)},
                "tests": ["run | success"],
                "queries": [
                    {
                        "query": "WorkedProofTransition",
                        "args": {
                            "claim_id": claim.id,
                            "evidence": asdict(claim.evidence),
                        },
                        "answers": [
                            {
                                "answer": "```rocq\n"
                                + "\n".join(claim.action)
                                + "\n```",
                                "example": False,
                            }
                        ],
                    }
                ],
            }
        )
    claim = state.claims[0]
    demos.append(
        {
            "demonstration": "polish-reject-unsafe",
            "strategy": "verify_worked_transition",
            "args": {"claim": asdict(claim)},
            "tests": ["run | failure"],
            "queries": [
                {
                    "query": "WorkedProofTransition",
                    "args": {
                        "claim_id": claim.id,
                        "evidence": asdict(claim.evidence),
                    },
                    "answers": [
                        {"answer": "```rocq\nadmit.\n```", "example": False}
                    ],
                }
            ],
        }
    )
    path.write_text(yaml.safe_dump(demos, sort_keys=False))


def serialization_demos() -> None:
    """Convert existing training role examples to the new typed contracts."""
    path = ROOT / "demos/polished.demo.yaml"
    demos: Any = yaml.safe_load(path.read_text())
    if any(str(d.get("query", "")).endswith("JSON") for d in demos):
        raise ValueError("structured role demos already generated")
    old: Any = yaml.safe_load((ROOT / "demos/grounded.demo.yaml").read_text())
    roles = {
        "ReflectGroundedTransition",
        "CurateGroundedClaim",
        "AuditGroundedClaim",
    }
    count = 0
    for demo in old:
        if demo.get("query") not in roles:
            continue
        data = dict(demo)
        data["demonstration"] = "polish-json-" + demo["demonstration"]
        data["query"] = demo["query"] + "JSON"
        data["answers"] = [
            {
                **answer,
                "answer": yaml.safe_load(
                    answer["answer"]
                    .split("```yaml\n", 1)[1]
                    .rsplit("```", 1)[0]
                ),
            }
            for answer in demo["answers"]
        ]
        demos.append(data)
        count += 1
    path.write_text(yaml.safe_dump(demos, sort_keys=False))
    print("Structured role examples:", count)


def accounting() -> dict[str, Any]:
    """Reconcile each settled receipt with its own dated token usage."""
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,reserved,status,usage FROM receipts"
        ).fetchall()
    checked, exceptions = 0, 0
    unresolved: list[dict[str, Any]] = []
    for key, model, created, charged, reserved, status, usage in rows:
        if charged is None:
            unresolved.append(
                {"receipt": key, "liability": reserved, "status": status}
            )
            continue
        values = json.loads(usage or "{}")
        if "input_tokens" not in values:
            if charged != 0:
                raise ValueError(f"nonzero receipt without usage: {key}")
            exceptions += 1
            continue
        computed = price_tokens(
            model,
            values["input_tokens"],
            values.get("input_tokens_details", {}).get("cached_tokens", 0),
            values["output_tokens"],
            on=datetime.fromtimestamp(created, timezone.utc).date(),
        )
        if abs(computed - charged) > 1e-9:
            raise ValueError(f"receipt/token discrepancy: {key}")
        checked += 1
    return {
        "repriced_receipts": checked,
        "zero_charge_rejections": exceptions,
        "unresolved": unresolved,
        "liability": ledger.summary()["liability"],
    }


def observations(phase: str) -> tuple[dict[str, Observation], dict[str, Any]]:
    costs = charged_cells()
    rows = list(cells_of_run(ROOT / f"experiments/output/ace_polish_{phase}"))
    out: dict[str, Observation] = {}
    details: dict[str, Any] = {}
    for row in rows:
        if row.name not in costs:
            # A genuinely pre-HTTP failure is observable, not imputed from
            # missing accounting on a successful or partially-paid run.
            if not row.platform_failed or row.cost != 0:
                raise ValueError(f"missing receipts: {row.name}")
            cost = 0.0
        else:
            cost = costs[row.name]
        out[row.name] = Observation(
            row.solved and cost <= 0.10, cost, row.platform_failed
        )
        details[row.name] = {
            **row.as_dict(),
            "charged_cost": cost,
            "qualified": out[row.name].solved,
        }
        exception = (
            ROOT
            / f"experiments/output/ace_polish_{phase}/configs"
            / row.name
            / "exception.txt"
        )
        text = exception.read_text() if exception.exists() else ""
        details[row.name]["administratively_censored"] = (
            "CampaignExhausted" in text
        )
        details[row.name]["implementation_failure"] = (
            "AssertionError" in text or "TypeError" in text
        )
    return out, details


def freeze() -> None:
    registration = json.loads((CAMPAIGN / "registration.json").read_text())
    observations_, details = observations("pilots")
    expected = configs("pilots")
    if set(observations_) != {name(c, None) for c in expected}:
        raise ValueError("incomplete pilots; no selection")
    events = [
        json.loads(s)
        for s in (CAMPAIGN / "admission.jsonl").read_text().splitlines()
    ]
    switches: dict[str, bool] = {}
    readout: dict[str, Any] = {}
    for mechanism in MECHANISMS:
        arms = [
            [
                observations_[name(c, None)]
                for c in expected
                if c.arm_label == f"{mechanism}-{side}"
            ]
            for side in ("off", "on")
        ]
        solves = [sum(o.solved for o in arm) for arm in arms]
        costs = [sum(o.cost for o in arm) for arm in arms]
        target = [
            e for e in events if f"__{mechanism}-on-r64__" in e.get("cell", "")
        ]
        exercised = any(
            (e["kind"] == "example" and e["decision"] == "selected")
            if mechanism == "matched_advice"
            else (
                e["kind"] == "recovery"
                and e["decision"] == "admitted"
                and (
                    e.get("reason") == "output_downshift"
                    if mechanism == "output_recovery"
                    else e.get("reason") in ("resource", "stagnation")
                )
            )
            for e in target
        )
        invalid = any(o.failed for arm in arms for o in arm)
        switches[mechanism] = (
            not invalid
            and exercised
            and (
                (solves[1] >= solves[0] and costs[1] < costs[0])
                or (solves[1] > solves[0] and costs[1] <= 1.2 * costs[0])
            )
        )
        readout[mechanism] = {
            "solves": solves,
            "costs": costs,
            "exercised": exercised,
            "selected": switches[mechanism],
            "platform_failure_in_contrast": invalid,
        }
    frozen = {
        **registration,
        "switches": switches,
        "pilot_readout": readout,
        "execution_hashes": source_hashes(),
    }
    frozen["changes_after_pilot"] = [
        path
        for path, digest_ in frozen["execution_hashes"].items()
        if registration["execution_hashes"].get(path) != digest_
    ]
    write_new(CAMPAIGN / "pilot_cells.json", details)
    write_new(CAMPAIGN / "frozen.json", frozen)
    print(json.dumps(readout, indent=2))


def report() -> None:
    obs, details = observations("validation")
    expected_configs = configs("validation")
    family = json.loads((CAMPAIGN / "frozen.json").read_text())["families"]
    expected = [(bench, str(seed)) for seed in (0, 1) for bench in family]
    arms = [
        {
            (c.bench_name, str(c.seed)): obs[name(c, None)]
            for c in expected_configs
            if c.arm_label == arm and name(c, None) in obs
        }
        for arm in ("reference", "candidate")
    ]
    result = compare(
        arms[0], arms[1], expected, families=family, alpha=0.1, confidence=0.9
    )
    if result["complete"]:
        result["cost_p_two_sided"] = cost_cluster_p(
            arms[0], arms[1], expected, family
        )
        result["utility_saving"] = (
            result["cost_ratio"] <= 0.85
            and result["solved_b"] >= result["solved_a"] - 2
        )
        result["utility_coverage"] = (
            result["cost_ratio"] <= 1.2
            and result["solved_b"] >= result["solved_a"] + 4
        )
        result["cost_per_solve"] = [
            result[f"cost_{k}"] / result[f"solved_{k}"]
            if result[f"solved_{k}"]
            else None
            for k in ("a", "b")
        ]
    result["per_seed"] = {
        str(seed): compare(
            arms[0],
            arms[1],
            [c for c in expected if c[1] == str(seed)],
            families=family,
            alpha=0.1,
            confidence=0.9,
        )
        for seed in (0, 1)
    }
    _, training = observations("training")
    result["training"] = {
        "cells": len(training),
        "qualified": sum(c["qualified"] for c in training.values()),
        "cost": sum(c["charged_cost"] for c in training.values()),
    }
    if len(training) != 40 or any(
        c["administratively_censored"]
        for c in [*training.values(), *details.values()]
    ):
        result["complete"] = False
        result["verdict"] = "incomplete_or_administratively_censored"
        result.pop("utility_saving", None)
        result.pop("utility_coverage", None)
    result["campaign"] = Ledger(CAMPAIGN / "ledger.sqlite3").summary()
    result["accounting"] = accounting()
    with Ledger(CAMPAIGN / "ledger.sqlite3").connect() as db:
        cursor = db.execute("SELECT * FROM receipts ORDER BY created,id")
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([column[0] for column in cursor.description])
        writer.writerows(cursor)
        receipts_path = CAMPAIGN / "receipts.csv"
        if (
            receipts_path.exists()
            and receipts_path.read_text()
            != buffer.getvalue().replace("\r\n", "\n")
        ):
            raise ValueError("refusing to replace different receipt export")
        receipts_path.write_text(buffer.getvalue().replace("\r\n", "\n"))
    events = [
        json.loads(line)
        for line in (CAMPAIGN / "admission.jsonl").read_text().splitlines()
    ]
    result["event_counts"] = dict(
        Counter(f"{e['kind']}/{e['decision']}" for e in events)
    )
    result["truncated_requests"] = sum(
        bool(e.get("truncated")) for e in events
    )
    # Arm-level wins do not establish that an optional recovery caused a
    # solve. Report the exercised subset separately, without reselecting.
    result["recovery_readout"] = {
        phase: {
            reason: {
                "cells": len(
                    triggered := {
                        e["cell"]
                        for e in events
                        if e["kind"] == "recovery"
                        and e["decision"] == "admitted"
                        and e.get("reason") == reason
                        and e.get("cell") in rows
                    }
                ),
                "qualified": sum(
                    rows[cell]["qualified"] for cell in triggered
                ),
                "cell_names": sorted(triggered),
            }
            for reason in ("output_downshift", "resource", "stagnation")
        }
        for phase, rows in (("training", training), ("validation", details))
    }
    failure_rows: dict[str, Any] = {}
    for cell, row in details.items():
        if row["qualified"]:
            continue
        history = checks(
            ROOT / "experiments/output/ace_polish_validation/configs" / cell
        )
        local_events = [e for e in events if e.get("cell") == cell]
        last = history[-1] if history else {}
        fb = last.get("feedback", {})
        failure_rows[cell] = {
            "cost": row["charged_cost"],
            "platform_failed": row["platformFailed"],
            "cached_checks": len(history),
            "cached_outcomes": dict(Counter(c["outcome"] for c in history)),
            "last_cached_outcome": last.get("outcome"),
            "last_cached_category": ag.failure_category(
                fb.get("error_message") or ""
            ),
            "last_cached_tactic": fb.get("failing_tactic"),
            "last_cached_error": (fb.get("error_message") or "")[:1200],
            "remaining_goals": len(fb.get("remaining_goals") or []),
            "admission_refusals": [
                e
                for e in local_events
                if e["kind"] == "admission" and e["decision"] == "declined"
            ],
            "recovery_events": [
                e for e in local_events if e["kind"] == "recovery"
            ],
            "stop_events": [e for e in local_events if e["kind"] == "stop"],
        }
    write_new(CAMPAIGN / "failure_audit.json", failure_rows)
    write_new(CAMPAIGN / "validation_cells.json", details)
    write_new(CAMPAIGN / "training_cells.json", training)
    write_new(CAMPAIGN / "final_report.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    {
        "prepare": prepare,
        "navigation": navigation,
        "serialization_demos": serialization_demos,
        "seal": seal,
        "freeze": freeze,
        "report": report,
    }[sys.argv[1]]()
