"""Complete-cell, family-clustered evaluation with actual-cost cutoffs.

Seeds are replicates within the same theorem, not independent benchmark
problems. Exact sign-flip inference swaps all observations of a family
together. Its integer statistic is the number of additional successes;
dynamic programming computes the exact distribution without enumerating
2**families assignments. Costs include unsuccessful attempts.
"""

# pyright: strict

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
import statistics
from typing import Any, cast

import numpy as np

from cell_records import CellRecord

Cell = tuple[str, str]


@dataclass(frozen=True)
class Observation:
    solved: bool
    cost: float
    failed: bool = False

    @staticmethod
    def from_record(rec: CellRecord) -> "Observation":
        return Observation(rec.solved, rec.cost, rec.platform_failed)


def exact_cluster_p(deltas: Sequence[int]) -> float:
    distribution: Counter[int] = Counter({0: 1})
    for d in deltas:
        if not d:
            continue
        nxt: Counter[int] = Counter()
        for value, count in distribution.items():
            nxt[value + d] += count
            nxt[value - d] += count
        distribution = nxt
    observed = abs(sum(deltas))
    return sum(n for d, n in distribution.items() if abs(d) >= observed) / sum(
        distribution.values()
    )


def compare(
    a: Mapping[Cell, Observation],
    b: Mapping[Cell, Observation],
    expected: Sequence[Cell],
    *,
    families: Mapping[str, str] | None = None,
    cap_a: float = 0.1,
    cap_b: float = 0.1,
    bootstrap_samples: int = 10000,
) -> dict[str, Any]:
    cells = set(expected)
    if len(cells) != len(expected):
        raise ValueError("duplicate expected cells")
    missing_a, missing_b = sorted(cells - a.keys()), sorted(cells - b.keys())
    if missing_a or missing_b:
        return {
            "complete": False,
            "expected": len(cells),
            "missing_a": missing_a,
            "missing_b": missing_b,
            "verdict": "incomplete",
        }
    if not cells:
        raise ValueError("empty comparison")
    if any(
        not np.isfinite(o.cost) or o.cost < 0
        for c in cells
        for o in (a[c], b[c])
    ):
        raise ValueError("missing, negative, or nonfinite cost")
    groups: dict[str, list[Cell]] = defaultdict(list)
    for c in sorted(cells):
        groups[(families or {}).get(c[0], c[0])].append(c)

    def success(o: Observation, cap: float) -> int:
        return int(o.solved and not o.failed and o.cost <= cap + 1e-12)

    blocks: list[list[float]] = []
    deltas: list[int] = []
    for cs in groups.values():
        delta = sum(success(b[c], cap_b) - success(a[c], cap_a) for c in cs)
        deltas.append(delta)
        blocks.append(
            [
                float(delta),
                float(len(cs)),
                sum(b[c].cost - a[c].cost for c in cs),
                sum(a[c].cost for c in cs),
                sum(b[c].cost for c in cs),
            ]
        )
    values = np.asarray(blocks, dtype=float)
    rng = np.random.default_rng(20260908)
    samples = values[
        rng.integers(0, len(blocks), size=(bootstrap_samples, len(blocks)))
    ].sum(axis=1)
    effect_ci = [
        float(cast(Any, np.quantile(samples[:, 0] / samples[:, 1], q)))
        for q in (0.025, 0.975)
    ]
    cost_ci = [
        float(cast(Any, np.quantile(samples[:, 2] / samples[:, 1], q)))
        for q in (0.025, 0.975)
    ]
    ratios = np.divide(
        samples[:, 4],
        samples[:, 3],
        out=np.full(bootstrap_samples, np.nan),
        where=samples[:, 3] > 0,
    )
    ratio_ci = (
        [float(np.nanquantile(ratios, q)) for q in (0.025, 0.975)]
        if np.isfinite(ratios).any()
        else None
    )
    effect = sum(deltas) / len(cells)
    # Percentile bootstrap collapses to [0, 0] with no discordances.
    # It cannot justify excluding a useful effect in that case. Use a
    # conservative weighted Hoeffding bound for exclusion decisions.
    # Independent sampling units are families, each with range [-1, 1].
    weights_sq = sum((len(cs) / len(cells)) ** 2 for cs in groups.values())
    upper95 = min(1.0, effect + math.sqrt(2 * weights_sq * math.log(20)))
    p = exact_cluster_p(deltas)
    verdict = (
        "improvement"
        if effect >= 0.05 - 1e-12 and p < 0.05
        else "useful_gain_not_supported"
        if upper95 < 0.05
        else "inconclusive"
    )
    total_a, total_b = (
        sum(a[c].cost for c in cells),
        sum(b[c].cost for c in cells),
    )
    return {
        "complete": True,
        "cells": len(cells),
        "families": len(groups),
        "theorems": len({c[0] for c in cells}),
        "solved_a": sum(success(a[c], cap_a) for c in cells),
        "solved_b": sum(success(b[c], cap_b) for c in cells),
        "effect": effect,
        "effect_ci95": effect_ci,
        "effect_ci95_method": "family percentile bootstrap (descriptive)",
        "effect_upper95_conservative": upper95,
        "p_two_sided": p,
        "discordant_families": sum(d != 0 for d in deltas),
        "cost_a": total_a,
        "cost_b": total_b,
        "cost_ratio": total_b / total_a if total_a else None,
        "cost_ratio_ci95": ratio_ci,
        "median_paired_cost_difference": statistics.median(
            b[c].cost - a[c].cost for c in cells
        ),
        "cheaper_b_cells": sum(b[c].cost < a[c].cost for c in cells),
        "dearer_b_cells": sum(b[c].cost > a[c].cost for c in cells),
        "mean_cost_difference": (total_b - total_a) / len(cells),
        "mean_cost_difference_ci95": cost_ci,
        "failed_a": sum(a[c].failed for c in cells),
        "failed_b": sum(b[c].failed for c in cells),
        "cap_crossings_a": sum(a[c].cost > cap_a for c in cells),
        "cap_crossings_b": sum(b[c].cost > cap_b for c in cells),
        "verdict": verdict,
    }
