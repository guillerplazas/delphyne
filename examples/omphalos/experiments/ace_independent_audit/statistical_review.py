"""Versioned final review of inclusive sign-flip ties, with no model calls.

Original finalized statistics remain immutable. This artifact supplies
reviewed comparisons and lists every p-value correction, asserting parity
of all costs, coverage, bootstrap intervals and practical-target decisions.
Both harnesses: python -m experiments.ace_independent_audit.statistical_review
"""

from collections import defaultdict
import itertools
import json
import math
import re
from typing import Any, cast

from .analysis import historical, normalized, paired
from .common import REPORT, ROOT, digest, read, save, sha
from .families import mapping
from .final_diagnosis import budget_rows
from .historical_comparisons import build
from .reporting import inputs

PKEY = "two_sided_sign_flip_p"


def same(a: Any, b: Any) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        ad = cast(dict[Any, Any], a)
        bd = cast(dict[Any, Any], b)
        return ad.keys() == bd.keys() and all(same(ad[k], bd[k]) for k in ad)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        aa = cast(list[Any] | tuple[Any, ...], a)
        bb = cast(list[Any] | tuple[Any, ...], b)
        return len(aa) == len(bb) and all(
            same(x, y) for x, y in zip(aa, bb, strict=True)
        )
    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
        return math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12)
    return a == b


def exact_budget_reference(
    base: list[dict[str, Any]],
    arm: list[dict[str, Any]],
    families: dict[str, str],
) -> dict[str, Any]:
    indexed = {(r["theorem"], r["seed"]): r for r in arm}
    differences: dict[str, float] = defaultdict(float)
    for r in base:
        theorem: str = r["theorem"]
        partner = indexed[theorem, r["seed"]]
        differences[families.get(theorem, theorem)] += (
            partner["costs"]["price"] - r["costs"]["price"]
        )
    nonzero = [d for d in differences.values() if abs(d) > 1e-12]
    if len(nonzero) > 20:
        raise ValueError("Exact reference is limited to sparse comparisons")
    observed = abs(math.fsum(nonzero))
    extreme = sum(
        abs(math.fsum(s * d for s, d in zip(signs, nonzero, strict=True)))
        >= observed - 1e-12
        for signs in itertools.product((-1, 1), repeat=len(nonzero))
    )
    return dict(
        nonzero_clusters=len(nonzero),
        assignments=2 ** len(nonzero),
        inclusive_extreme_assignments=extreme,
        exact_p=extreme / 2 ** len(nonzero),
    )


def run() -> None:
    source_names = (
        "fresh_results.json",
        "rule_repair_results.json",
        "adaptive_frozen_results.json",
        "budget_replay_results.json",
        "final_diagnosis.json",
        "historical_matched_comparisons.json",
        "historical_original_comparisons.json",
    )
    data = inputs(reviewed=False)
    rows = data["rows"]
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[r["stage"], r["arm"]].append(r)
    reviewed: dict[str, Any] = {}
    changes: list[dict[str, Any]] = []

    def record(name: str, old: dict[str, Any], new: dict[str, Any]) -> None:
        if not same(
            {k: v for k, v in old.items() if k != PKEY},
            {k: v for k, v in new.items() if k != PKEY},
        ):
            raise ValueError("Non-p-value statistics differ: " + name)
        reviewed[name] = new
        if old.get(PKEY) != new.get(PKEY):
            changes.append(
                dict(name=name, original=old.get(PKEY), reviewed=new.get(PKEY))
            )

    for key, value in data["comparisons"].items():
        stage, label = key.split("/")
        arm = label.split("_vs_")[0]
        for level, families in (("theorem", None), ("family", mapping())):
            record(
                f"serving/{key}/{level}",
                value[level],
                paired(
                    groups[stage, value["baseline"]],
                    groups[stage, arm],
                    families,
                ),
            )
    replay = read(REPORT / "budget_replay_cells.json")
    references = {r["cell"]: r for r in rows}
    budget_groups: dict[tuple[str, str, float], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for rr in replay:
        ref = references[rr["cell"]]
        budget_groups[rr["stage"], rr["arm"], rr["cap"]].append(
            dict(
                ref,
                costs=dict(price=rr["spent_budget"]["price"]),
                solved=rr["solved"],
            )
        )
    for (stage, arm), values in groups.items():
        if not arm.startswith("online_"):
            budget_groups[stage, arm, 0.10] = values
    for key, value in read(REPORT / "budget_replay_results.json")[
        "comparisons"
    ].items():
        stage, arm, cap = key.split("/")
        baseline = "B0" if arm.startswith("B") else "A0"
        for level, families in (("theorem", None), ("family", mapping())):
            record(
                f"budget/{key}/{level}",
                value[level],
                paired(
                    budget_groups[stage, baseline, float(cap)],
                    budget_groups[stage, arm, float(cap)],
                    families,
                ),
            )
    joint = read(REPORT / "final_diagnosis.json")["joint_budget_comparisons"]
    exact: dict[str, Any] = {}
    for stage in ("train", "validation"):
        full = groups[stage, "A0"]
        lower = budget_rows(replay, stage, "A0", 0.05)
        o1 = budget_rows(replay, stage, "O1", 0.05)
        for key, base, arm in (
            ("joint_O1_005_vs_A0_010", full, o1),
            ("budget_only_A0_005_vs_A0_010", full, lower),
            ("matched_O1_005_vs_A0_005", lower, o1),
        ):
            for level, families in (("theorem", None), ("family", mapping())):
                record(
                    f"joint/{stage}/{key}/{level}",
                    joint[stage]["comparisons"][key][level],
                    paired(base, arm, families),
                )
        for level, families in (("theorem", {}), ("family", mapping())):
            exact[f"budget_only/{stage}/{level}"] = exact_budget_reference(
                full, lower, families
            )
    original = read(REPORT / "historical_matched_comparisons.json")
    recomputed, _ = build()
    for old, new in zip(original, recomputed, strict=True):
        if old["comparison"] != new["comparison"]:
            raise ValueError("Historical comparison selection changed")
        for level in ("theorem", "family"):
            record(
                f"historical_matched/{old['comparison']}/{level}",
                old[level],
                new[level],
            )
    raw = historical()
    base = [r for r in raw if r["campaign"] == "x_validation_agentic"]
    original = read(REPORT / "historical_original_comparisons.json")
    for old in original:
        arm = [
            r
            for r in raw
            if r["campaign"] == old["campaign"]
            and r["stage"] == "validation"
            and re.sub(
                r"seed[_-]?\d+",
                "seed*",
                r["path"]
                .rsplit("/", 1)[-1]
                .replace(r["theorem"], "{theorem}"),
            )
            == old["label"]
            and digest(normalized(r["config"], r["theorem"]))
            == old["identity"]
        ]
        record(
            "historical_original/" + old["campaign"] + "/" + old["identity"],
            {
                k: v
                for k, v in old.items()
                if k not in ("campaign", "identity", "label")
            },
            paired(base, arm),
        )
    save(
        REPORT / "statistical_review.json",
        dict(
            paid_calls=0,
            input_hashes={name: sha(REPORT / name) for name in source_names},
            analysis_sha=sha(
                ROOT / "experiments/ace_independent_audit/analysis.py"
            ),
            method="Same seeded 50000-draw sign-flip test, with inclusive ties at rtol=1e-12/atol=1e-12. No p-value replaces an unknown-invoice interval. Exact sparse budget enumerations independently check the tie correction.",
            comparisons_reviewed=len(reviewed),
            all_other_statistics_unchanged=True,
            p_value_changes=changes,
            exact_budget_references=exact,
            comparisons=reviewed,
            prior_artifacts="Original numerical-finalization and checkpoint artifacts remain preserved. Reviewed p-values in this file supersede original values under their explicit comparison keys.",
        ),
    )
    print(
        json.dumps(
            dict(comparisons=len(reviewed), changes=changes, exact=exact)
        )
    )


if __name__ == "__main__":
    run()
