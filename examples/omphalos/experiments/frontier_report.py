"""
Cost/performance frontier report for the set1 gpt-5.6 sweeps.

Reads `experiments/output/set1_{standard,agentic}/results_summary.csv`
(regenerate with `make summary-set1`) and prints, per (model,
baseline): pass rate, total spend, and dollars per solved problem.

It also applies the canonical-model selection rule agreed for this
project: **the canonical model is the tier with the most agentic
successes per dollar on set1, ties going to the cheaper tier.** The
rule intentionally scores economy rather than raw pass rate — budget
control is the point of the thesis — so the report prints the full
table and warns when the pick trails the best pass rate by more than
the ±2-problem run-to-run noise band, which is the signal to revisit
the rule rather than apply it blindly.

Usage:
    python experiments/frontier_report.py
"""

# pyright: strict

import csv
import sys
from dataclasses import dataclass
from pathlib import Path

# `model_registry` lives at the omphalos root, one level up from this
# script (experiment scripts get that directory from the Delphyne
# workspace context; a plain script must add it itself).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import miniF2F_bench as mf
from model_registry import GPT56_PRICING

_OUTPUT_DIR = Path(__file__).resolve().parent / "output"

# Successes-per-dollar comparisons within this band are treated as
# ties (single-seed sampling noise is roughly +/-1-2 problems).
_NOISE_BAND_PROBLEMS = 2


@dataclass
class BaselineStats:
    n_problems: int
    n_solved: int
    spend: float

    @property
    def pass_rate(self) -> float:
        return self.n_solved / self.n_problems

    @property
    def solved_per_dollar(self) -> float:
        return self.n_solved / self.spend if self.spend > 0 else 0.0

    @property
    def dollars_per_solve(self) -> float | None:
        return self.spend / self.n_solved if self.n_solved else None


def load_stats(summary: Path) -> dict[str, BaselineStats]:
    """Aggregate a results_summary.csv per model name."""
    per_model: dict[str, BaselineStats] = {}
    with open(summary) as f:
        for row in csv.DictReader(f):
            stats = per_model.setdefault(
                row["model_name"], BaselineStats(0, 0, 0.0)
            )
            stats.n_problems += 1
            stats.n_solved += row["success"] == "True"
            stats.spend += float(row["price"])
    return per_model


def input_price(model: str) -> float:
    return GPT56_PRICING[model].dollars_per_input_token


def pick_canonical(agentic: dict[str, BaselineStats]) -> str:
    """
    Most agentic successes per dollar, ties to the cheaper tier.

    A tier is only preferred outright if its advantage survives the
    noise band: candidates whose solved-count, when perturbed by the
    band, could not beat the leader's economy are still counted as
    tied, and the cheapest tied tier wins.
    """
    leader = max(
        agentic, key=lambda m: (agentic[m].solved_per_dollar, -input_price(m))
    )
    tied = [
        m
        for m, s in agentic.items()
        if (s.n_solved + _NOISE_BAND_PROBLEMS) / max(s.spend, 1e-9)
        >= agentic[leader].solved_per_dollar
    ]
    return min(tied, key=input_price)


def _fmt_row(model: str, s: BaselineStats) -> str:
    per_solve = (
        f"${s.dollars_per_solve:.3f}" if s.dollars_per_solve else "  --  "
    )
    return (
        f"  {model:<16} {s.n_solved:>2}/{s.n_problems:<3}"
        f" ({s.pass_rate:>4.0%})   ${s.spend:>6.2f}   {per_solve}"
    )


def main() -> None:
    tables: dict[str, dict[str, BaselineStats]] = {}
    for baseline in ("standard", "agentic"):
        summary = _OUTPUT_DIR / f"set1_{baseline}" / "results_summary.csv"
        tables[baseline] = load_stats(summary)
        print(f"\nset1 {baseline}:")
        print(f"  {'model':<16} {'solved':<12} {'spend':>7}   $/solve")
        for model in mf.FRONTIER_MODELS:
            if model in tables[baseline]:
                print(_fmt_row(model, tables[baseline][model]))

    agentic = tables["agentic"]
    canonical = pick_canonical(agentic)
    print("\ncanonical pick (agentic successes/$, ties -> cheaper tier):")
    print(f"  {canonical}")
    best_rate = max(agentic.values(), key=lambda s: s.n_solved)
    gap = best_rate.n_solved - agentic[canonical].n_solved
    if gap > _NOISE_BAND_PROBLEMS:
        print(
            f"  WARNING: trails the best pass rate by {gap} problems "
            f"(> noise band of {_NOISE_BAND_PROBLEMS}) — consider "
            "revisiting the selection rule before adopting this pick."
        )


if __name__ == "__main__":
    main()
