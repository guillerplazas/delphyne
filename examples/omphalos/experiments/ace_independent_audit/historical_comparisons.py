"""Matched historical comparisons from reconciled individual cells.

The table keeps ordinary agentic, bounded grounded, and online contracts
separate. A reset control is used only for its explicit factorial contrast;
it is never substituted for the ordinary baseline by convenience.
"""

from collections import defaultdict
from copy import deepcopy
import json
from typing import Any

from .analysis import historical, metrics, normalized, paired
from .catalog import label, write_csv
from .common import REPORT, digest, read, save
from .families import mapping


def contract(row: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(normalized(row["config"], row["theorem"]))
    value["strategy_args"].pop("playbook", None)
    value["policy"] = {
        "continued_economy_policy": "refined_economy_policy",
        "continued_thesis_policy": "sanitized_proof_policy",
    }.get(value.get("policy"), value.get("policy"))
    return value


def build() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    chosen = set(read(REPORT / "historical_selected_paths.json"))
    raw = historical() + [
        json.loads(line) for line in (REPORT / "exception_cells.jsonl").open()
    ]
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    for r in raw:
        if r["path"] in chosen:
            groups[r["campaign"], r["stage"], label(r)].append(r)

    def pick(campaign: str, stage: str, marker: str) -> list[dict[str, Any]]:
        found = [
            v
            for (c, s, name), v in groups.items()
            if c == campaign
            and s == stage
            and marker in name
            and len({r["theorem"] for r in v}) == 40
        ]
        if len(found) != 1:
            raise ValueError(
                "Ambiguous historical panel: " + str((campaign, stage, marker))
            )
        return found[0]

    pairs: list[
        tuple[str, list[dict[str, Any]], list[dict[str, Any]], str]
    ] = []
    for stage in ("train", "validation"):
        campaign = "ace_attribution_20260912"
        pairs.append(
            (
                f"attribution_terra/{stage}",
                pick(campaign, stage, "__terra-none-"),
                pick(campaign, stage, "__terra-ace-"),
                "Historical stronger-solver diagnostic; not an eligible Luna deployment.",
            )
        )
    c = "ace_economy_20260916"
    plain = pick(c, "validation", "__agentic__")
    for arm in ("ace", "session", "views"):
        pairs.append(
            (
                f"economy/{arm}_vs_ordinary",
                plain,
                pick(c, "validation", f"__{arm}__"),
                "Bounded grounded solver; session/views additionally change policy controls.",
            )
        )
    pairs.extend(
        [
            (
                "economy/budget_matched",
                pick(
                    "ace_economy_budget_20260916", "validation", "__agentic__"
                ),
                pick(c, "validation", "__budget__"),
                "Same $0.20 nominal stopping allowance; separate paid launch, compatible contract.",
            ),
            (
                "economy/session_matched",
                pick(
                    "ace_economy_session_20260916",
                    "validation",
                    "__agentic_session__",
                ),
                pick(c, "validation", "__session__"),
                "Both use the same session reset; separate paid launch.",
            ),
        ]
    )
    c = "ace_economy_refinement_20260916"
    for suffix in ("", "_compact", "_reset", "_reset_compact"):
        pairs.append(
            (
                "refinement/matched" + suffix,
                pick(c, "validation", f"__agentic{suffix}__"),
                pick(c, "validation", f"__ace{suffix}__"),
                "Matched factorial controls; retained platform failures count as unsolved.",
            )
        )
    for arm in ("ace_compact", "ace_reset", "ace_reset_compact"):
        pairs.append(
            (
                f"refinement/{arm}_vs_ordinary",
                pick(c, "validation", "__agentic__"),
                pick(c, "validation", f"__{arm}__"),
                "Whole-pipeline contrast against ordinary bounded grounded agentic.",
            )
        )
    c = "ace_sanitized_20260917"
    for base, arm in (
        ("agentic", "ace_selected"),
        ("agentic_coverage", "ace_coverage"),
        ("agentic", "ace_coverage"),
    ):
        pairs.append(
            (
                f"sanitized/{arm}_vs_{base}",
                pick(c, "validation", f"__{base}__"),
                pick(c, "validation", f"__{arm}__"),
                "32768 versus8192 output cap is explicit in the contract check.",
            )
        )
    c = "ace_thesis_20260918"
    for base in ("nonace_ordinary", "nonace_matched"):
        for arm in ("ace_historical", "ace_selected"):
            pairs.append(
                (
                    f"thesis/{arm}_vs_{base}",
                    pick(c, "validation", f"__{base}__"),
                    pick(c, "validation", f"__{arm}__"),
                    "Exact interrupted prefixes deduplicated; ordinary output cap32768, matched andACE8192.",
                )
            )
    c = "ace_x3_reproduction_20260918"
    for cap in (32768, 8192):
        pairs.append(
            (
                f"reproduction/{cap}",
                pick(c, "validation", f"none_{cap}__"),
                pick(c, "validation", f"x3_{cap}__"),
                "Despite the reproduction name, archived executable strategy is the bounded grounded solver, not original32-request agentic.",
            )
        )
    original = pick("x_validation_agentic", "validation", "__core-medium__")
    for variant in ("x-online", "x-online-warm", "x3-online"):
        arm = [
            r
            for seed in (0, 1)
            for r in pick(
                f"ace_online_{variant}-s{seed}_agentic", "validation", "__ace-"
            )
        ]
        pairs.append(
            (
                "historical_online/" + variant,
                original,
                arm,
                "Inference only; evolving playbooks, separate historical baseline, adaptation fees excluded from this serving-cost comparison.",
            )
        )
    results: list[dict[str, Any]] = []
    compact: list[dict[str, Any]] = []
    for name, base, arm, note in pairs:
        bc = {digest(contract(r)) for r in base if r["config"].get("strategy")}
        ac = {digest(contract(r)) for r in arm if r["config"].get("strategy")}
        result: dict[str, Any] = dict(
            comparison=name,
            baseline=metrics(base),
            arm=metrics(arm),
            same_contract_except_book=bc == ac and len(bc) == 1,
            platform_errors=sum(
                r.get("status") == "platform_error" for r in [*base, *arm]
            ),
            theorem=paired(base, arm),
            family=paired(base, arm, mapping()),
            note=note,
        )
        results.append(result)
        if result["theorem"]["complete"]:
            v = result["theorem"]
            compact.append(
                dict(
                    comparison=name,
                    n=v["n"],
                    baseline_solves=v["baseline_solves"],
                    arm_solves=v["arm_solves"],
                    baseline_cost=v["baseline_cost"],
                    arm_cost=v["arm_cost"],
                    saving=v["saving"],
                    ci_low=v["saving_ci90"][0],
                    ci_high=v["saving_ci90"][1],
                    practical_target=v["practical_target"],
                    same_contract_except_book=result[
                        "same_contract_except_book"
                    ],
                    platform_errors=result["platform_errors"],
                )
            )
    return results, compact


def run() -> None:
    results, compact = build()
    save(REPORT / "historical_matched_comparisons.json", results)
    write_csv(REPORT / "historical_matched_comparisons.csv", compact)
    print(json.dumps(dict(comparisons=len(results))))


if __name__ == "__main__":
    run()
