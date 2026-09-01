"""
Pair the `convert_user_feedback_to_tool` arms of `luna_cvt_ablation`.

Reports the metrics pre-registered in that experiment's docstring, in
the order they should be read:

1. **Paired per problem-seed spend** -- the primary metric. A sign test
   on the direction plus the median per-cell ratio.
2. Solves, paired the same way, flagged as underpowered when the
   discordant count cannot reach significance.
3. The pooled totals, printed **last and labelled**, because pooling a
   heavy-tailed cost distribution is what produced the reading this
   experiment exists to check (see the 2026-08-24 correction in
   PROGRESS.md).

Costs are recomputed from token counts at the rates in
`model_registry`, never read from the archived `price` column, so a
stale rate cannot move the verdict.

Reads each config's `result.yaml` rather than `results_summary.csv`:
the directory name identifies the arm unambiguously, whereas the
summary omits a config field equal to its default -- and `True` is the
default for the flag under test.

Usage:
    python tools/cvt_report.py
"""

# pyright: strict

import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from decision_audit import (  # noqa: E402
    MIN_DISCORDANT_FOR_SIG,
    SIGNIFICANCE,
    sign_test,
)
from model_registry import pricing_for  # noqa: E402

RUN = Path("experiments/output/luna_cvt_ablation")

ARMS = {"on": "cvt-on", "off": "cvt-off"}

TIE = 0.02
"""Cells whose two prices differ by less than this count as ties."""

# The fields all sit in the `spent_budget` block near the top of the
# file, well before the raw trace; reading the whole trace would be
# gratuitous.
_HEAD_BYTES = 4000

type Cell = tuple[str, str]  # (bench_name, seed)


def _field(head: str, name: str) -> str:
    m = re.search(rf"\n *{name}: (\S+)", head)
    assert m is not None, f"no `{name}` in result head"
    return m.group(1)


def _load(arm: str) -> dict[Cell, tuple[bool, float]]:
    """`(solved, recomputed dollars)` per problem-seed cell for one arm."""
    configs = RUN / "configs"
    assert configs.exists(), f"no run at {configs}; try `make sweep-luna-cvt`"
    out: dict[Cell, tuple[bool, float]] = {}
    for d in sorted(configs.iterdir()):
        parts = d.name.split("__")
        if len(parts) != 4 or parts[1] != ARMS[arm]:
            continue
        bench, _, model, seed = parts
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
    on, off = _load("on"), _load("off")
    cells = sorted(set(on) & set(off))
    unpaired = set(on) ^ set(off)
    assert cells, "no paired cells; has the sweep finished?"

    print(f"luna, agentic, canonical config -- {len(cells)} paired cells")
    print("  arms: convert_user_feedback_to_tool on vs off")
    if unpaired:
        print(
            f"  {len(unpaired)} unpaired cell(s) dropped: {sorted(unpaired)}"
        )
    print()

    # 1. Primary metric: paired per-cell spend.
    cheaper = dearer = 0
    ratios: list[float] = []
    for c in cells:
        p_on, p_off = on[c][1], off[c][1]
        if p_off < p_on * (1 - TIE):
            cheaper += 1
        elif p_off > p_on * (1 + TIE):
            dearer += 1
        if p_on > 0:
            ratios.append(p_off / p_on)
    p_cost = sign_test(cheaper, dearer)
    print("PRIMARY -- paired per-cell spend (off relative to on)")
    print(
        f"  off cheaper on {cheaper} cells, dearer on {dearer}, "
        f"tied {len(cells) - cheaper - dearer}"
    )
    print(
        f"  median ratio {statistics.median(ratios):.3f} "
        f"(1.000 = no difference)   max {max(ratios):.2f}"
    )
    print(
        f"  sign test p = {p_cost:.3f} -> "
        f"{'DIFFERENCE' if p_cost < SIGNIFICANCE else 'no effect detected'}"
    )

    # 2. Secondary metric: solves.
    on_only = sum(1 for c in cells if on[c][0] and not off[c][0])
    off_only = sum(1 for c in cells if off[c][0] and not on[c][0])
    p_solve = sign_test(on_only, off_only)
    discordant = on_only + off_only
    print("\nSECONDARY -- solves")
    print(
        f"  on {sum(on[c][0] for c in cells)}/{len(cells)}   "
        f"off {sum(off[c][0] for c in cells)}/{len(cells)}"
    )
    print(
        f"  discordant: on only {on_only}, off only {off_only} "
        f"-> p = {p_solve:.3f}"
    )
    if discordant < MIN_DISCORDANT_FOR_SIG:
        print(
            f"  UNDERPOWERED: {discordant} discordant, "
            f"{MIN_DISCORDANT_FOR_SIG} needed to reach p < {SIGNIFICANCE}"
        )

    # 3. Pooled totals, last and labelled.
    t_on = sum(on[c][1] for c in cells)
    t_off = sum(off[c][1] for c in cells)
    print("\nPOOLED (not the result -- see the module docstring)")
    print(
        f"  on ${t_on:.4f}   off ${t_off:.4f}   "
        f"{100 * (t_off - t_on) / t_on:+.1f}%"
    )


if __name__ == "__main__":
    main()
