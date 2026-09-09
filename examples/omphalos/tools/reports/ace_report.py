"""
Pair the ACE-playbook validation arm against the frozen baseline.

Reports the metrics pre-registered in
`experiments/ace/ace_validation_experiment.py`, in reading order:

1. **Paired solves** — the primary metric. Exact sign test on the
   discordant problem-seed cells (two-sided quoted, one-sided also
   shown since the pre-registered direction is "ACE solves more"),
   with the power floor stated explicitly: fewer than
   `MIN_DISCORDANT_FOR_SIG` discordant cells is reported as
   UNDERPOWERED, not as a verdict.
2. **Paired per-cell spend among jointly-solved cells** — the
   secondary, thesis-relevant metric (does the playbook's input tax
   buy fewer turns under the same $0.05 cap?). Sign test with a 2%
   tie band plus the median ratio.
3. The pooled totals, printed **last and labelled** (pooling this
   heavy-tailed cost distribution manufactures effects; PROGRESS.md
   2026-08-24).

Costs are recomputed from token counts at `model_registry` rates,
never read from the archived `price` column.

Arms:
- baseline: `experiments/output/luna_validation_agentic`,
  `core-medium` seeds {0, 1} (frozen, not re-run);
- ACE: `experiments/output/ace_validation_agentic`, the
  `ace-<sha8>-core-medium` configs, same seeds.

Usage:
    python -m tools.reports.ace_report
"""


# pyright: strict

import argparse
import re
import statistics
from pathlib import Path


from tools.analysis.decision_audit import (
    HISTORICAL_MIN_DISCORDANT as MIN_DISCORDANT_FOR_SIG,
    HISTORICAL_SIGNIFICANCE as SIGNIFICANCE,
    sign_test,
)
from runtime.model_registry import pricing_for  # noqa: E402

BASELINE_RUN = Path("experiments/output/luna_validation_agentic")
ACE_RUN = Path("experiments/output/ace_validation_agentic")

BASELINE_ARM = "core-medium"
ACE_ARM_RE = re.compile(r"^ace-[0-9a-f]{8}(?:-k\d+)?-core-medium$")

TIE = 0.02
"""Cells whose two prices differ by less than this count as ties."""

# The fields sit in the `spent_budget` block, which follows the
# success values (proof scripts can run to a few KB) but precedes any
# trace data; 64KB safely covers the former without reading the
# latter. `re.search` returns the FIRST match, so per-request budget
# blocks deeper in the file cannot shadow the spent totals.
_HEAD_BYTES = 65536

type Cell = tuple[str, str]  # (bench_name, seed)


def _field(head: str, name: str) -> str:
    m = re.search(rf"\n *{name}: (\S+)", head)
    assert m is not None, f"no `{name}` in result head"
    return m.group(1)


def _load(
    run: Path, arm_matches: "re.Pattern[str]"
) -> dict[Cell, tuple[bool, float]]:
    """`(solved, recomputed dollars)` per problem-seed cell."""
    configs = run / "configs"
    assert configs.exists(), f"no run at {configs}"
    out: dict[Cell, tuple[bool, float]] = {}
    for d in sorted(configs.iterdir()):
        parts = d.name.split("__")
        if len(parts) != 4:
            continue
        bench, arm, model, seed = parts
        if not arm_matches.fullmatch(arm):
            continue
        result = d / "result.yaml"
        if not result.exists():
            continue
        with result.open() as f:
            head = f.read(_HEAD_BYTES)
        inp = int(_field(head, "input_tokens"))
        cached = int(_field(head, "cached_input_tokens"))
        rates = pricing_for(model)
        cost = (
            (inp - cached) * rates.dollars_per_input_token
            + cached * rates.dollars_per_cached_input_token
            + int(_field(head, "output_tokens"))
            * rates.dollars_per_output_token
        )
        out[(bench, seed)] = (_field(head, "success") == "true", cost)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Pair two arms per problem-seed cell and report the "
            "pre-registered metrics. Offline; makes no API calls."
        )
    )
    parser.add_argument("--a-run", default=str(BASELINE_RUN))
    parser.add_argument("--a-arm", default=BASELINE_ARM)
    parser.add_argument("--a-label", default="baseline")
    parser.add_argument("--b-run", default=str(ACE_RUN))
    parser.add_argument("--b-arm", default=ACE_ARM_RE.pattern)
    parser.add_argument("--b-label", default="ACE")
    args = parser.parse_args()

    a_label, b_label = str(args.a_label), str(args.b_label)
    base = _load(Path(str(args.a_run)), re.compile(str(args.a_arm)))
    ace = _load(Path(str(args.b_run)), re.compile(str(args.b_arm)))
    cells = sorted(set(base) & set(ace))
    unpaired = set(base) ^ set(ace)
    assert cells, "no paired cells; has the ACE eval finished?"

    print(
        f"{b_label} vs {a_label} -- {len(cells)} paired cells"
        f"\n  A: {Path(str(args.a_run)).name} [{args.a_arm}]"
        f"\n  B: {Path(str(args.b_run)).name} [{args.b_arm}]"
    )
    if unpaired:
        print(
            f"  {len(unpaired)} unpaired cell(s) dropped: {sorted(unpaired)}"
        )
    print()

    # 1. Primary metric: paired solves.
    base_only = sum(1 for c in cells if base[c][0] and not ace[c][0])
    ace_only = sum(1 for c in cells if ace[c][0] and not base[c][0])
    discordant = base_only + ace_only
    p2 = sign_test(base_only, ace_only)
    p1 = sign_test(base_only, ace_only, one_sided=True)
    print("PRIMARY -- paired solves")
    print(
        f"  {a_label} {sum(base[c][0] for c in cells)}/{len(cells)}   "
        f"{b_label} {sum(ace[c][0] for c in cells)}/{len(cells)}"
    )
    print(
        f"  discordant: {a_label} only {base_only}, {b_label} only"
        f" {ace_only} -> two-sided p = {p2:.3f}"
        f" (one-sided, {b_label} better: {p1:.3f})"
    )
    if discordant < MIN_DISCORDANT_FOR_SIG:
        print(
            f"  UNDERPOWERED: {discordant} discordant cell(s),"
            f" {MIN_DISCORDANT_FOR_SIG} needed to reach"
            f" p < {SIGNIFICANCE}; identical configs disagree on 1-3"
            " cells run-to-run"
        )

    # 2. Secondary metric: spend among jointly-solved cells.
    joint = [c for c in cells if base[c][0] and ace[c][0]]
    cheaper = dearer = 0
    ratios: list[float] = []
    for c in joint:
        p_base, p_ace = base[c][1], ace[c][1]
        if p_ace < p_base * (1 - TIE):
            cheaper += 1
        elif p_ace > p_base * (1 + TIE):
            dearer += 1
        if p_base > 0:
            ratios.append(p_ace / p_base)
    p_cost = sign_test(dearer, cheaper)
    print(
        f"\nSECONDARY -- spend among the {len(joint)} jointly-solved"
        f" cells ({b_label} relative to {a_label})"
    )
    print(
        f"  {b_label} cheaper on {cheaper}, dearer on {dearer}, "
        f"tied {len(joint) - cheaper - dearer}"
    )
    if ratios:
        print(
            f"  median ratio {statistics.median(ratios):.3f} "
            f"(1.000 = no difference)   max {max(ratios):.2f}"
        )
    print(
        f"  sign test p = {p_cost:.3f} -> "
        f"{'DIFFERENCE' if p_cost < SIGNIFICANCE else 'no effect detected'}"
    )

    # 3. Pooled totals, last and labelled.
    t_base = sum(base[c][1] for c in cells)
    t_ace = sum(ace[c][1] for c in cells)
    print("\nPOOLED (not the result -- see the module docstring)")
    print(
        f"  {a_label} ${t_base:.4f}   {b_label} ${t_ace:.4f}   "
        f"{100 * (t_ace - t_base) / t_base:+.1f}%"
    )


if __name__ == "__main__":
    main()
