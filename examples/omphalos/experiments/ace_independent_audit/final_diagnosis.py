"""Final O1 mechanism audit and explicit joint budget comparisons.

Both harnesses: python -m experiments.ace_independent_audit.final_diagnosis
Reads only the completed trainX/validationX study. Reconstructs all 320
A0/O1 cells from raw caches, without invoking a solver or provider. Budget
comparisons use the already certified controller replays, not token clipping.
Cross-budget comparisons are descriptive joint configurations selected after
viewing the registered budget grid; they do not isolate the ACE contribution.
"""

from concurrent.futures import ProcessPoolExecutor
import json
import math
from typing import Any

from .analysis import paired
from .audit import cell
from .common import CAMPAIGN, REPORT, ROOT, read, save, sha
from .families import mapping
from .mechanisms import characterize

DETAIL = {
    "amc12_2000_p6",
    "mathd_algebra_185",
    "mathd_numbertheory_629",
    "aime_1991_p9",
    "mathd_numbertheory_530",
    "mathd_numbertheory_405",
    "amc12_2001_p21",
    "induction_prod1p1onk3le3m1onn",
    "mathd_numbertheory_37",
    "imo_1969_p2",
}


def reconstruct(expected: dict[str, Any]) -> dict[str, Any]:
    raw = cell((str(ROOT / expected["path"]), expected["theorem"]))
    for key in ("cache_sha", "result_sha", "solved", "request_digest"):
        if raw[key] != expected[key]:
            raise ValueError(f"Changed raw cell {expected['cell']}: {key}")
    if not raw["exact_cost"] or raw["counts"] != expected["counts"]:
        raise ValueError("Incomplete usage or changed request count")
    for key, value in raw["costs"].items():
        if not math.isclose(
            value, expected["costs"][key], rel_tol=1e-12, abs_tol=1e-10
        ):
            raise ValueError("Raw token repricing changed")
    trace = characterize(raw)
    if trace != expected["trace_summary"]:
        raise ValueError("Raw trace characterization changed")
    result = dict(
        cell=expected["cell"],
        stage=expected["stage"],
        arm=expected["arm"],
        theorem=raw["theorem"],
        seed=raw["seed"],
        path=raw["path"],
        cache_sha=raw["cache_sha"],
        result_sha=raw["result_sha"],
        solved=raw["solved"],
        costs=raw["costs"],
        requests=raw["counts"]["requests"],
        trace_summary=trace,
        capped_replies=sum(t["output"] == 32768 for t in raw["turns"]),
        capped_reply_cost=sum(
            t["price"] for t in raw["turns"] if t["output"] == 32768
        ),
    )
    if raw["theorem"] in DETAIL:
        result["returned_proofs"] = raw["value"]
        result["checks"] = [
            dict(
                index=c["index"],
                function=c["function"],
                args=c["args"],
                success=c["feedback"].get("success"),
                auto_finished=c["feedback"].get("auto_finished"),
                error_excerpt=str(c["feedback"].get("error_message"))[:1200],
                feedback_characters=len(
                    json.dumps(c["feedback"], sort_keys=True)
                ),
            )
            for c in raw["checks"]
        ]
    return result


def budget_rows(
    rows: list[dict[str, Any]], stage: str, arm: str, cap: float
) -> list[dict[str, Any]]:
    return [
        dict(r, costs=dict(price=r["spent_budget"]["price"]))
        for r in rows
        if r["stage"] == stage and r["arm"] == arm and r["cap"] == cap
    ]


def provenance() -> dict[str, Any]:
    book_path = CAMPAIGN / "books/O1_adaptive_frozen.json"
    book = read(book_path)
    origins: dict[str, Any] = {}
    event_hashes: dict[str, str] = {}
    previous: dict[str, Any] = {}
    for step in range(40):
        path = CAMPAIGN / f"online_events/online-o0-s{step:02d}.json"
        event = read(path)
        event_hashes[path.name] = sha(path)
        before_path = CAMPAIGN / f"books/online-o0-s{step:02d}__A2_before.json"
        before = read(before_path)
        if event["before"]["A2"] != sha(before_path) or before["playbook"][
            "bullets"
        ] != list(previous.values()):
            raise ValueError("Curriculum book chronology changed")
        current = {b["id"]: b for b in event["after"]["A2"]["bullets"]}
        for identity, bullet in current.items():
            if identity not in previous:
                origins[identity] = dict(
                    source_theorem=event["theorem"],
                    step=step,
                    first_content=bullet["content"],
                    event=str(path.relative_to(CAMPAIGN)),
                    subsequent_content_changes=[],
                )
            elif bullet["content"] != previous[identity]["content"]:
                origins[identity]["subsequent_content_changes"].append(
                    dict(step=step, content=bullet["content"])
                )
        previous = current
    if list(previous.values()) != book["playbook"]["bullets"]:
        raise ValueError("Frozen book differs from preselected final state")
    return dict(
        book_sha=sha(book_path),
        rules=[dict(b, origin=origins[b["id"]]) for b in previous.values()],
        event_hashes=event_hashes,
    )


def run() -> None:
    final = read(REPORT / "numerical_finalization.json")
    for filename, digest in final["final_artifacts"].items():
        if sha(REPORT / filename) != digest:
            raise ValueError(f"Finalized evidence changed: {filename}")
    files = (
        "fresh_cells.json",
        "adaptive_frozen_cells.json",
        "budget_replay_cells.json",
        "fresh_mechanisms.json",
        "final_economics.json",
    )
    hashes = {name: sha(REPORT / name) for name in files}
    frozen = read(REPORT / "fresh_cells.json")
    adaptive = read(REPORT / "adaptive_frozen_cells.json")
    selected = [r for r in frozen if r["arm"] == "A0"] + adaptive
    if len(selected) != 320:
        raise ValueError("A0/O1 denominator changed")
    with ProcessPoolExecutor(max_workers=4) as pool:
        raw = list(pool.map(reconstruct, selected))
    print(json.dumps(dict(raw_cells_reconstructed=len(raw))), flush=True)
    mechanisms = read(REPORT / "fresh_mechanisms.json")
    economics = read(REPORT / "final_economics.json")
    replay = read(REPORT / "budget_replay_cells.json")
    joint: dict[str, Any] = {}
    transitions: dict[str, Any] = {}
    for stage in ("train", "validation"):
        full = [r for r in frozen if r["stage"] == stage and r["arm"] == "A0"]
        lower = budget_rows(replay, stage, "A0", 0.05)
        o1 = budget_rows(replay, stage, "O1", 0.05)
        if len(full) != 80 or len(lower) != 80 or len(o1) != 80:
            raise ValueError("Incomplete joint comparison")
        comparisons: dict[str, Any] = {}
        for name, base, arm in (
            ("joint_O1_005_vs_A0_010", full, o1),
            ("budget_only_A0_005_vs_A0_010", full, lower),
            ("matched_O1_005_vs_A0_005", lower, o1),
        ):
            comparisons[name] = dict(
                theorem=paired(base, arm),
                family=paired(base, arm, mapping()),
            )
        base_total = sum(float(r["costs"]["price"]) for r in full)
        lower_total = sum(float(r["costs"]["price"]) for r in lower)
        o1_total = sum(float(r["costs"]["price"]) for r in o1)
        prep = float(economics["recipes"]["O1"]["preparation_cost"])
        saving = (base_total - o1_total) / 80
        ten_margin = (0.9 * base_total - o1_total) / 80
        joint[stage] = dict(
            comparisons=comparisons,
            dollar_decomposition=dict(
                budget_only=base_total - lower_total,
                additional_ACE_at_lower_cap=lower_total - o1_total,
                joint=base_total - o1_total,
            ),
            preparation=prep,
            break_even_problems=math.ceil(prep / saving),
            problems_for_ten_percent_total_saving=math.ceil(prep / ten_margin),
            amortization_assumption="Reuse this book with the observed mean fees indefinitely; point estimate, no guarantee of transfer or equal cache behavior.",
        )
        index = {(r["theorem"], r["seed"]): r for r in full}
        transitions[stage] = [
            dict(
                theorem=r["theorem"],
                seed=r["seed"],
                baseline_solved=index[r["theorem"], r["seed"]]["solved"],
                O1_solved=r["solved"],
                baseline_cost=index[r["theorem"], r["seed"]]["costs"]["price"],
                O1_cost=r["costs"]["price"],
            )
            for r in adaptive
            if r["stage"] == stage
            and r["solved"] != index[r["theorem"], r["seed"]]["solved"]
        ]
    save(
        REPORT / "final_diagnosis_reviewed.json",
        dict(
            paid_calls=0,
            input_hashes=hashes,
            numerical_finalization_sha=sha(
                REPORT / "numerical_finalization.json"
            ),
            raw_cells_reconstructed=len(raw),
            cells=raw,
            O1_rule_provenance=provenance(),
            O1_outcome_changes=transitions,
            joint_budget_comparisons=joint,
            O1_mechanisms={
                stage: dict(
                    baseline=mechanisms["groups"][f"{stage}/A0"],
                    arm=mechanisms["groups"][f"{stage}/O1"],
                    comparison=mechanisms["comparisons"][f"{stage}/O1"],
                )
                for stage in ("train", "validation")
            },
            limitations=[
                "Budget replays are conditional on the recorded responses and actual cache invoices, not new independent model draws.",
                "O1 served in a later block under the replacement account's paced scheduler; comparisons retain temporal and provider-cache limitations.",
                "Uncached repricing holds trajectories fixed and is not a controller simulation or a decomposition of the causal ACE effect.",
                "Rule provenance or similar proof syntax alone does not identify which bullet caused an outcome change.",
                "TrainX is familiar-workload reuse; validationX is reused development transfer. No closed partition is accessed.",
            ],
        ),
    )
    print(
        json.dumps(
            dict(
                raw_cells=len(raw),
                joint_validation=joint["validation"]["comparisons"][
                    "joint_O1_005_vs_A0_010"
                ],
                paid_calls=0,
            )
        )
    )


if __name__ == "__main__":
    run()
