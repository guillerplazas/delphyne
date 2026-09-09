"""Prepare, freeze and report the bounded ACE campaign; never calls an API."""

from runtime.paths import OMPHALOS_ROOT

from dataclasses import asdict
import csv
import io
import json
from pathlib import Path
import re
import sys
from typing import Any
import yaml

import ace.ace_grounded as ag  # noqa: E402
from experiments.ace.ace_bounded_experiment import CAMPAIGN, digest  # noqa: E402
from runtime.campaign_budget import Ledger  # noqa: E402
from tools.analysis.cell_records import cells_of_run  # noqa: E402
from delphyne.utils.typing import pydantic_load  # noqa: E402
import experiments.common.miniF2F_bench as mf  # noqa: E402
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)  # noqa: E402
from tools.data.prepare_grounded import candidates  # noqa: E402
import runtime.pytanque_utils as pt  # noqa: E402

ROOT = OMPHALOS_ROOT


def write_new(path: Path, data: object) -> None:
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != text:
            raise ValueError(f"refusing to replace frozen file: {path}")
    else:
        path.write_text(text)


def panel() -> None:
    evidence = json.loads((CAMPAIGN / "evidence_v2.json").read_text())
    state = pydantic_load(ag.AdaptationState, evidence["state"])
    for path in sorted(
        (ROOT / "experiments/output/ace_bounded_adapt/configs").glob(
            "*/result.yaml"
        )
    ):
        document: Any = yaml.load(path.read_text(), Loader=yaml.CSafeLoader)
        raw: Any = document["outcome"]["result"]
        if raw.get("success") and raw.get("values"):
            learned = pydantic_load(ag.AdaptationState, raw["values"][0])
            state = state.admit(learned.decisions)
    # Merge duplicate checked actions deterministically without model calls.
    unique: dict[tuple[str, str, tuple[str, ...], str], ag.AdviceClaim] = {}
    for claim in state.claims:
        unique[
            (claim.environment, claim.kind, claim.action, claim.trigger_name)
        ] = claim
    state = ag.AdaptationState(
        tuple(unique.values()), state.decisions, state.step
    )
    artifact = CAMPAIGN / "artifact_v2.json"
    write_new(artifact, {"state": asdict(state), "source": "trainX only"})
    trained = {c.evidence.theorem_name for c in state.claims}
    allowed = mf.load_partition("benchmarks/trainX.txt")
    records = {
        r.bench: r
        for r in cells_of_run(
            ROOT / "experiments/output/ace_review_calibration"
        )
        if r.arm == "baseline-r64" and r.seed == "0"
    }
    pool = candidates()
    references = {
        e.theorem_name
        for e in pool
        if ag.decision_kind(pt.Feedback(False, 0, e.failed_action, e.error))
        == "reference"
    }
    cases: list[dict[str, str]] = []
    used = set(trained)
    for mechanism in ("money", "admission", "focused", "restart"):
        eligible = [n for n in allowed if n not in used and n in records]
        eligible.sort(
            key=lambda n: (
                0
                if (
                    n in references
                    if mechanism in {"admission", "focused"}
                    else not records[n].solved
                )
                else 1,
                -records[n].cost
                if mechanism in {"money", "restart"}
                else records[n].cost,
                n,
            )
        )
        for bench in eligible[:2]:
            cases.append({"bench": bench, "mechanism": mechanism})
            used.add(bench)
    if len(cases) != 8:
        raise ValueError("insufficient independent pilot cases")
    write_new(
        CAMPAIGN / "pilot_v2.json",
        {
            "artifact": str(artifact.relative_to(ROOT)),
            "artifact_sha256": digest(artifact),
            "cases": cases,
        },
    )
    print(json.dumps({"claims": len(state.claims), "pilot_cases": cases}))


def receipts() -> dict[str, float]:
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        return {
            str(name): float(cost)
            for name, cost in db.execute(
                "SELECT cell,SUM(COALESCE(charged,reserved)) FROM receipts GROUP BY cell"
            )
        }


def observations(phase: str) -> dict[str, tuple[tuple[str, str], Observation]]:
    charged = receipts()
    run = ROOT / f"experiments/output/ace_bounded_{phase}"
    out: dict[str, tuple[tuple[str, str], Observation]] = {}
    for record in cells_of_run(run):
        directory = run / "configs" / record.name
        for error in directory.glob("exception*.txt"):
            if "CampaignExhausted" in error.read_text():
                raise ValueError(
                    "campaign-censored cell; no comparative verdict"
                )
        if record.requests and record.name not in charged:
            raise ValueError(f"missing billing receipts: {record.name}")
        out[record.name] = (
            record.cell,
            Observation(
                record.solved,
                charged.get(record.name, 0.0),
                record.platform_failed,
            ),
        )
    return out


def diagnostics(phase: str, name: str) -> dict[str, Any]:
    cache = (
        ROOT
        / f"experiments/output/ace_bounded_{phase}/configs/{name}/cache.yaml"
    )
    output: dict[str, Any] = {
        "seconds": 0.0,
        "focused": 0,
        "restart": 0,
        "advice": 0,
        "resource": 0,
        "verified": 0,
    }
    if not cache.exists():
        return output
    raw: list[dict[str, Any]] = (
        yaml.load(cache.read_text(), Loader=yaml.CSafeLoader) or []
    )
    for entry in raw:
        request = entry.get("input", {}).get("request", {})
        chat = request.get("chat", [])
        if not chat:
            continue
        outputs = (entry.get("output") or dict[str, Any]()).get("outputs", [])
        if request.get("options", {}).get("model") == "__compute__":
            if outputs and str(chat[-1].get("content", "")).startswith(
                ("fun: checked_proof", "fun: inspect_proof_state")
            ):
                result: Any = yaml.load(
                    outputs[0]["content"], Loader=yaml.CSafeLoader
                )
                output["seconds"] += float(result.get("elapsed", 0))
                output["resource"] += (
                    result.get("outcome") == "resource_exhausted"
                )
                output["verified"] += bool(
                    result.get("feedback", {}).get("success")
                )
        else:
            text = "\n".join(str(m.get("content", "")) for m in chat)
            output["focused"] += "Focus decision:" in text
            output["restart"] += "prior plan stalled" in text
            output["advice"] += "Verified local example:" in text
    return output


def execution_hashes() -> dict[str, str]:
    paths = [
        ROOT / p
        for p in (
            "ace/ace_grounded.py",
            "prove_grounded.py",
            "runtime/tool_budget.py",
            "runtime/campaign_budget.py",
            "runtime/rocq_server.py",
            "runtime/pytanque_utils.py",
            "runtime/model_registry.py",
            "delphyne.yaml",
            "demos/grounded.demo.yaml",
            "experiments/ace/ace_bounded_experiment.py",
        )
    ]
    for prefix in (
        "ProposeProofScriptGrounded",
        "ResolveProofReference",
        "ChooseProofBridge",
        "ChooseProofStructure",
    ):
        paths.extend((ROOT / "prompts").rglob(prefix + ".*.jinja"))
    paths.extend((ROOT / "prompts").rglob("ProposeProofScriptACE.*.jinja"))
    paths.extend((ROOT / "prompts").rglob("ProposeProofScriptAgentic.*.jinja"))
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(paths))}


def freeze() -> None:
    if (
        json.loads((CAMPAIGN / "pilot_execution_hashes.json").read_text())
        != execution_hashes()
    ):
        raise ValueError("execution sources changed during pilots")
    data = json.loads((CAMPAIGN / "pilot_v2.json").read_text())
    records = observations("pilot")
    by_cell_arm = {
        (name.split("__")[0], name.split("__")[1]): (name, obs)
        for name, (_, obs) in records.items()
    }
    switches: dict[str, bool] = {}
    readout: dict[str, Any] = {}
    for mechanism in ("money", "admission", "focused", "restart"):
        problems = [
            r["bench"] for r in data["cases"] if r["mechanism"] == mechanism
        ]
        rows: list[dict[str, Any]] = []
        for bench in problems:
            pair: list[dict[str, Any]] = []
            for arm in ("off", "on"):
                key = (bench, f"{mechanism}-{arm}-r64")
                if key not in by_cell_arm:
                    raise ValueError(f"missing pilot cell {key}")
                name, obs = by_cell_arm[key]
                pair.append(
                    {
                        "qualified": obs.solved
                        and not obs.failed
                        and obs.cost <= 0.1,
                        "cost": obs.cost,
                        "diagnostics": diagnostics("pilot", name),
                    }
                )
            rows.append({"bench": bench, "off": pair[0], "on": pair[1]})
        before = sum(r["off"]["cost"] for r in rows)
        after = sum(r["on"]["cost"] for r in rows)
        no_loss = all(
            not r["off"]["qualified"] or r["on"]["qualified"] for r in rows
        )
        metric = {
            "focused": "focused",
            "restart": "restart",
            "admission": "advice",
        }.get(mechanism)
        exercised = (
            after < before
            if metric is None
            else any(r["on"]["diagnostics"][metric] for r in rows)
        )
        keep = no_loss and after <= before and exercised
        switches[mechanism] = keep
        readout[mechanism] = {
            "keep": keep,
            "exercised": exercised,
            "cost_off": before,
            "cost_on": after,
            "rows": rows,
        }
    write_new(CAMPAIGN / "pilot_readout.json", readout)
    write_new(
        CAMPAIGN / "frozen.json",
        {
            "switches": switches,
            "artifact": data["artifact"],
            "artifact_sha256": data["artifact_sha256"],
            "execution_hashes": execution_hashes(),
            "validation": "validationX",
            "seed": 0,
            "alpha": 0.1,
            "confidence": 0.9,
            "comparator": "ace_review_development/x3-r64/seed0",
            "comparator_sha256": digest(
                ROOT
                / "experiments/campaigns/ace_review_20260908/development_cells.json"
            ),
            "families": families(
                dict(mf.load_partition("benchmarks/validationX.txt"))
            ),
        },
    )
    print(json.dumps({"selected_switches": switches, "validation_cells": 40}))


def families(problems: dict[str, tuple[str, str]]) -> dict[str, str]:
    parent = {n: n for n in problems}

    def find(n: str) -> str:
        while parent[n] != n:
            n = parent[n]
        return n

    templates: dict[str, str] = {}
    for name, (file, _) in sorted(problems.items()):
        statement = re.sub(
            r"\b\d+\b",
            "NUMBER",
            " ".join(pt.parse_problem(file, True).theorem_statement.split()),
        )
        keys = [statement]
        if name.startswith(("imo_", "aime_", "amc")):
            keys.append(re.sub(r"(_p\d+)_\d+$", r"\1", name))
        for key in keys:
            if key in templates:
                parent[find(name)] = find(templates[key])
            else:
                templates[key] = name
    return {n: find(n) for n in problems}


def final() -> None:
    frozen = json.loads((CAMPAIGN / "frozen.json").read_text())
    if frozen["execution_hashes"] != execution_hashes():
        raise ValueError("execution sources changed after freeze")
    problems = dict(mf.load_partition("benchmarks/validationX.txt"))
    expected = [(n, "0") for n in problems]
    source = (
        ROOT
        / "experiments/campaigns/ace_review_20260908/development_cells.json"
    )
    prior = json.loads(source.read_text())
    if digest(source) != frozen["comparator_sha256"]:
        raise ValueError("historical comparator changed after freeze")
    control = {
        (name.split("__")[0], "0"): Observation(
            row["solved"], row["charged_cost"], row["platformFailed"]
        )
        for name, row in prior.items()
        if "__x3-r64__" in name and name.endswith("__seed0")
    }
    observed = observations("validation")
    treatment = {cell: obs for cell, obs in observed.values()}
    family = frozen["families"]
    result = compare(
        control,
        treatment,
        expected,
        families=family,
        alpha=0.1,
        confidence=0.9,
    )
    if not result["complete"]:
        write_new(CAMPAIGN / "incomplete_report.json", result)
        print(json.dumps(result, indent=2))
        return
    result["cost_p_two_sided"] = cost_cluster_p(
        control, treatment, expected, family
    )
    result["exploratory_saving"] = (
        result["cost_ratio"] <= 0.9
        and result["solved_b"] >= result["solved_a"]
        and result["cost_p_two_sided"] < 0.1
    )
    result["alpha"], result["confidence"] = 0.1, 0.9
    result["comparator_sha256"] = digest(source)
    result["analysis_sha256"] = digest(Path(__file__))
    cached_cost = sum(
        r.cost
        for r in cells_of_run(
            ROOT / "experiments/output/ace_bounded_validation"
        )
    )
    result["billing_reconciliation"] = {
        "cached_usage_repriced": cached_cost,
        "receipts_minus_cached_usage": result["cost_b"] - cached_cost,
        "note": "Receipt costs include every attempt; any gap must be explained before a spending claim.",
    }
    result["campaign"] = Ledger(CAMPAIGN / "ledger.sqlite3").summary()
    charged = receipts()
    adaptation = sum(v for name, v in charged.items() if "__adapt__" in name)
    pilots = sum(
        v
        for name, v in charged.items()
        if "__adapt__" not in name and "__integrated-r64__" not in name
    )
    saved_per_problem = (result["cost_a"] - result["cost_b"]) / len(expected)
    result["upfront_api_cost"] = {"adaptation": adaptation, "pilots": pilots}
    result["break_even_problems"] = {
        "adaptation_only": adaptation / saved_per_problem
        if saved_per_problem > 0
        else None,
        "all_training": (adaptation + pilots) / saved_per_problem
        if saved_per_problem > 0
        else None,
        "scope": "API costs only; assumes the observed saving persists and excludes assistant/engineering costs",
    }
    result["diagnostics"] = {
        name: diagnostics("validation", name) for name in observed
    }
    result["interpretation"] = (
        "Exploratory development comparison against a historical control; not independent confirmation or quality equivalence. Cached diagnostics count distinct records, not invocation events."
    )
    write_new(
        CAMPAIGN / "validation_cells.json",
        {
            name: {"cell": cell, **asdict(obs), "family": family[cell[0]]}
            for name, (cell, obs) in observed.items()
        },
    )
    with Ledger(CAMPAIGN / "ledger.sqlite3").connect() as db:
        cursor = db.execute(
            "SELECT id,stage,cell,model,created,reserved,charged,status,usage FROM receipts ORDER BY created,id"
        )
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow([column[0] for column in cursor.description])
        writer.writerows(cursor)
        csv_path = CAMPAIGN / "receipts.csv"
        contents = output.getvalue().encode()
        if csv_path.exists() and csv_path.read_bytes() != contents:
            raise ValueError("refusing to replace frozen receipts")
        if not csv_path.exists():
            csv_path.write_bytes(contents)
    write_new(CAMPAIGN / "final_report.json", result)
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in {"diagnostics", "campaign"}
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    {"panel": panel, "freeze": freeze, "final": final}[sys.argv[1]]()
