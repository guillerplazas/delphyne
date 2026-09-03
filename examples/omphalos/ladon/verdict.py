"""
Pairing and the pre-registered decision rules of the Ladon loop.

Everything here is pure: cells in, a verdict out, no I/O beyond the
optional `load_cells` convenience. The rules are constants with names,
because the loop's credibility rests on the rule having been fixed
before any cell was paid — `ladon/LADON.md` quotes them and every
night's `verdict.json` records which rule fired.

Metrics (the house conventions, `examples/omphalos/CLAUDE.md`):

- **Primary**: solves, paired per (problem, seed) cell against the
  baseline; exact sign test on the discordant cells
  (`tools/decision_audit.sign_test`). A platform-failed cell scores
  unsolved (HINTS #59); an arm solve counts only if the pristine
  verifier accepted the recorded proof (`ladon/reverify.py`).
- **Secondary**: spend among the jointly-solved cells, cheaper/dearer
  with a 2 % tie band, median ratio, sign test — the shape of
  `tools/ace_report.py` (lines 143-195), re-implemented here because
  that script keeps it inline in `main()`.
- Never pooled sums: the cost distribution is heavy-tailed and pooled
  signs flip between seeds.

Outcomes: KEEP, DISCARD, INSPECT (signal present, not settled — a
human or a Fable session decides the next look), HUMAN (structural,
never implemented by the loop). A screen-tier judgement (seed 0 only)
returns PROMOTE unless the arm is clearly harmful.
"""

# pyright: strict

import statistics
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
for _sub in ("", "experiments", "tools"):
    _p = str(_OMPHALOS_DIR / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from cell_records import CellRecord, cells_of_run  # noqa: E402
from decision_audit import (  # noqa: E402
    MIN_DISCORDANT_FOR_SIG,
    SIGNIFICANCE,
    sign_test,
)

TIE = 0.02
"""Relative band inside which two jointly-solved cells tie on spend."""

COST_KEEP_MAX_RATIO = 0.90
"""A cost KEEP needs the median jointly-solved ratio at or below this."""

MAX_SOLVE_LOSS_FOR_COST_KEEP = 0
"""
Net discordant solves the cost path may lose (baseline-only minus
arm-only). Zero: budget reduction is the priority, but never at the
price of a solve deficit — a cheaper arm that loses cells is INSPECT.
"""

COST_PROMISING_MAX_RATIO = 0.85
COST_PROMISING_MAX_P = 0.20
"""A cost signal worth another look although it is not established."""

INSPECT_MIN_NET = 3
"""Arm-only minus baseline-only solves that count as a positive signal."""

SCREEN_HARM_NET = 4
"""Screen tier: baseline-only minus arm-only solves that end the arm."""

SCREEN_MAX_PLATFORM_FAILED = 4
SCREEN_MAX_UNPAIRED = 4
SELECT_MAX_PLATFORM_FAILED = 3

type Outcome = Literal["KEEP", "DISCARD", "INSPECT", "HUMAN", "PROMOTE"]
type Tier = Literal["screen", "select"]
type HintClass = Literal["A", "B", "C", "D"]


@dataclass(frozen=True)
class PairedCell:
    bench: str
    seed: str
    a: CellRecord
    b: CellRecord
    b_verified: bool

    @property
    def a_solved(self) -> bool:
        return self.a.solved and not self.a.platform_failed

    @property
    def b_solved(self) -> bool:
        return self.b.solved and not self.b.platform_failed and self.b_verified


@dataclass(frozen=True)
class Primary:
    cells: int
    a_solved: int
    b_solved: int
    a_only: int
    b_only: int
    both: int
    neither: int
    p_two: float
    p_one: float

    @property
    def discordant(self) -> int:
        return self.a_only + self.b_only

    @property
    def powered(self) -> bool:
        return self.discordant >= MIN_DISCORDANT_FOR_SIG

    @property
    def net(self) -> int:
        return self.b_only - self.a_only


@dataclass(frozen=True)
class Secondary:
    joint: int
    cheaper: int
    dearer: int
    tied: int
    median_ratio: float | None
    max_ratio: float | None
    p_cost: float
    a_spend_joint: float
    b_spend_joint: float

    @property
    def established_cheaper(self) -> bool:
        return (
            self.p_cost < SIGNIFICANCE
            and self.cheaper > self.dearer
            and self.median_ratio is not None
            and self.median_ratio <= COST_KEEP_MAX_RATIO
        )

    @property
    def established_dearer(self) -> bool:
        return self.p_cost < SIGNIFICANCE and self.dearer > self.cheaper

    @property
    def promising(self) -> bool:
        return (
            self.cheaper > self.dearer
            and self.median_ratio is not None
            and self.median_ratio <= COST_PROMISING_MAX_RATIO
            and self.p_cost < COST_PROMISING_MAX_P
        )


@dataclass(frozen=True)
class Integrity:
    reverify_failed: int = 0
    arm_platform_failed: int = 0
    unpaired: int = 0
    frozen_violation: bool = False
    out_of_scope_diff: bool = False
    code_drift: bool = False
    launch_timeout: bool = False
    gates_failed: tuple[str, ...] = ()


@dataclass(frozen=True)
class Paired:
    cells: tuple[PairedCell, ...]
    unpaired_a: tuple[str, ...]
    unpaired_b: tuple[str, ...]
    primary: Primary
    secondary: Secondary

    @property
    def unpaired(self) -> int:
        return len(self.unpaired_a) + len(self.unpaired_b)

    @property
    def arm_platform_failed(self) -> int:
        return sum(1 for c in self.cells if c.b.platform_failed)

    @property
    def reverify_failed(self) -> int:
        return sum(
            1
            for c in self.cells
            if c.b.solved and not c.b.platform_failed and not c.b_verified
        )


@dataclass(frozen=True)
class Verdict:
    outcome: Outcome
    rule: str
    reason: str
    tier: Tier


def primary_of(cells: Sequence[PairedCell]) -> Primary:
    a_only = sum(1 for c in cells if c.a_solved and not c.b_solved)
    b_only = sum(1 for c in cells if c.b_solved and not c.a_solved)
    both = sum(1 for c in cells if c.a_solved and c.b_solved)
    return Primary(
        cells=len(cells),
        a_solved=sum(1 for c in cells if c.a_solved),
        b_solved=sum(1 for c in cells if c.b_solved),
        a_only=a_only,
        b_only=b_only,
        both=both,
        neither=len(cells) - a_only - b_only - both,
        p_two=sign_test(a_only, b_only),
        p_one=sign_test(a_only, b_only, one_sided=True),
    )


def secondary_of(cells: Sequence[PairedCell]) -> Secondary:
    joint = [c for c in cells if c.a_solved and c.b_solved]
    cheaper = dearer = 0
    ratios: list[float] = []
    for c in joint:
        pa, pb = c.a.cost, c.b.cost
        if pb < pa * (1 - TIE):
            cheaper += 1
        elif pb > pa * (1 + TIE):
            dearer += 1
        if pa > 0:
            ratios.append(pb / pa)
    return Secondary(
        joint=len(joint),
        cheaper=cheaper,
        dearer=dearer,
        tied=len(joint) - cheaper - dearer,
        median_ratio=statistics.median(ratios) if ratios else None,
        max_ratio=max(ratios) if ratios else None,
        p_cost=sign_test(dearer, cheaper),
        a_spend_joint=sum(c.a.cost for c in joint),
        b_spend_joint=sum(c.b.cost for c in joint),
    )


def pair(
    a_cells: Iterable[CellRecord],
    b_cells: Iterable[CellRecord],
    reverify: Mapping[str, bool] | None = None,
    *,
    seeds: Sequence[str] | None = None,
    problems: Sequence[str] | None = None,
) -> Paired:
    """
    Pair per (bench, seed). `reverify` maps an arm cell *name* to
    whether the pristine verifier accepted its proof; an arm solve
    without an entry counts as unverified (never as verified).
    `seeds` and `problems` restrict both sides to the cells the arm
    registered (the screen tier pairs seed 0 only), so that "unpaired"
    means a registered cell one side lacks, never a baseline cell the
    arm never meant to run.
    """

    def keep(c: CellRecord) -> bool:
        return (seeds is None or c.seed in seeds) and (
            problems is None or c.bench in problems
        )

    a_map = {c.cell: c for c in a_cells if keep(c)}
    b_map = {c.cell: c for c in b_cells if keep(c)}
    keys = sorted(set(a_map) & set(b_map))
    cells = tuple(
        PairedCell(
            bench=k[0],
            seed=k[1],
            a=a_map[k],
            b=b_map[k],
            b_verified=(
                (reverify or {}).get(b_map[k].name, False)
                if b_map[k].solved
                else True
            ),
        )
        for k in keys
    )
    return Paired(
        cells=cells,
        unpaired_a=tuple(
            f"{b}/s{s}" for b, s in sorted(set(a_map) - set(b_map))
        ),
        unpaired_b=tuple(
            f"{b}/s{s}" for b, s in sorted(set(b_map) - set(a_map))
        ),
        primary=primary_of(cells),
        secondary=secondary_of(cells),
    )


def load_cells(run_dir: Path) -> list[CellRecord]:
    return list(cells_of_run(run_dir))


#####
##### Rules
#####


def judge(
    paired: Paired,
    tier: Tier,
    integrity: Integrity,
    hint_class: HintClass = "B",
) -> Verdict:
    p, s = paired.primary, paired.secondary
    if tier == "screen":
        return _screen(paired, integrity)
    # Integrity first: a number that cannot be trusted is not a result.
    if integrity.frozen_violation:
        return Verdict("DISCARD", "frozen-path", "a frozen path changed", tier)
    if integrity.reverify_failed:
        return Verdict(
            "INSPECT",
            "manufactured-solve",
            f"{integrity.reverify_failed} arm solve(s) fail the pristine"
            " verifier",
            tier,
        )
    if integrity.code_drift:
        return Verdict("INSPECT", "code-drift", "code changed mid-run", tier)
    if integrity.out_of_scope_diff:
        return Verdict(
            "INSPECT",
            "out-of-scope",
            "changes outside examples/omphalos",
            tier,
        )
    if integrity.launch_timeout:
        return Verdict(
            "INSPECT", "timeout", "the launch hit its deadline", tier
        )
    if integrity.arm_platform_failed > SELECT_MAX_PLATFORM_FAILED:
        return Verdict(
            "INSPECT",
            "incomplete",
            f"{integrity.arm_platform_failed} platform-failed arm cells",
            tier,
        )
    if integrity.unpaired:
        return Verdict(
            "INSPECT",
            "incomplete",
            f"{integrity.unpaired} unpaired cells",
            tier,
        )
    if hint_class == "D":
        return Verdict("HUMAN", "structural", "class D is never run", tier)
    if hint_class == "A":
        return Verdict(
            "INSPECT", "analysis", "offline analysis: read the artifact", tier
        )
    if p.p_two < SIGNIFICANCE and p.b_only > p.a_only:
        return Verdict(
            "KEEP",
            "solves",
            f"paired solves established (p={p.p_two:.3f})",
            tier,
        )
    if (
        p.a_only - p.b_only <= MAX_SOLVE_LOSS_FOR_COST_KEEP
        and s.established_cheaper
    ):
        return Verdict(
            "KEEP",
            "cost",
            f"jointly-solved spend established cheaper (p={s.p_cost:.3f},"
            f" median x{s.median_ratio:.2f}) with no solve deficit",
            tier,
        )
    if p.p_two < SIGNIFICANCE and p.a_only > p.b_only:
        return Verdict(
            "DISCARD",
            "harm",
            f"paired solves established worse (p={p.p_two:.3f})",
            tier,
        )
    if s.established_dearer and p.b_only <= p.a_only:
        return Verdict(
            "DISCARD",
            "dearer",
            f"established dearer (p={s.p_cost:.3f}) without a solve gain",
            tier,
        )
    if p.net >= INSPECT_MIN_NET:
        return Verdict(
            "INSPECT",
            "underpowered-solves",
            f"+{p.net} net solves at p={p.p_two:.3f}: not settled, not refuted",
            tier,
        )
    if s.promising and p.a_only - p.b_only <= MAX_SOLVE_LOSS_FOR_COST_KEEP:
        return Verdict(
            "INSPECT",
            "underpowered-cost",
            f"median x{s.median_ratio:.2f} at p={s.p_cost:.3f}: not settled",
            tier,
        )
    if s.established_cheaper:
        return Verdict(
            "INSPECT",
            "cheaper-with-deficit",
            f"cheaper (p={s.p_cost:.3f}) but {p.a_only - p.b_only} net solves"
            " lost",
            tier,
        )
    return Verdict(
        "DISCARD",
        "null",
        f"no signal: net {p.net:+d} solves (p={p.p_two:.2f}), cost"
        f" p={s.p_cost:.2f}",
        tier,
    )


def _screen(paired: Paired, integrity: Integrity) -> Verdict:
    p = paired.primary
    if integrity.frozen_violation:
        return Verdict(
            "DISCARD", "frozen-path", "a frozen path changed", "screen"
        )
    if p.a_only - p.b_only >= SCREEN_HARM_NET:
        return Verdict(
            "DISCARD",
            "screen-harm",
            f"{p.a_only - p.b_only} net solves lost on seed 0",
            "screen",
        )
    if integrity.arm_platform_failed >= SCREEN_MAX_PLATFORM_FAILED:
        return Verdict(
            "DISCARD",
            "screen-failures",
            f"{integrity.arm_platform_failed} platform-failed arm cells",
            "screen",
        )
    if integrity.unpaired >= SCREEN_MAX_UNPAIRED:
        return Verdict(
            "DISCARD",
            "screen-unpaired",
            f"{integrity.unpaired} unpaired",
            "screen",
        )
    return Verdict("PROMOTE", "screen", "no clear harm on seed 0", "screen")


def integrity_of(paired: Paired, **flags: Any) -> Integrity:
    """The measured integrity fields plus the caller's flags."""
    return Integrity(
        reverify_failed=paired.reverify_failed,
        arm_platform_failed=paired.arm_platform_failed,
        unpaired=paired.unpaired,
        **flags,
    )


#####
##### Rendering
#####


def numbers_line(paired: Paired) -> str:
    p, s = paired.primary, paired.secondary
    ratio = f"x{s.median_ratio:.2f}" if s.median_ratio is not None else "n/a"
    return (
        f"{p.b_solved} vs {p.a_solved} of {p.cells} (arm-only {p.b_only},"
        f" base-only {p.a_only}, p={p.p_two:.3f}); joint {s.joint}:"
        f" cheaper {s.cheaper}, dearer {s.dearer}, median {ratio},"
        f" p={s.p_cost:.3f}"
    )


def as_dict(paired: Paired, verdict: Verdict | None = None) -> dict[str, Any]:
    p, s = paired.primary, paired.secondary
    out: dict[str, Any] = {
        "cells": p.cells,
        "a_solved": p.a_solved,
        "b_solved": p.b_solved,
        "a_only": p.a_only,
        "b_only": p.b_only,
        "both": p.both,
        "neither": p.neither,
        "p_two": p.p_two,
        "p_one": p.p_one,
        "powered": p.powered,
        "joint": s.joint,
        "cheaper": s.cheaper,
        "dearer": s.dearer,
        "tied": s.tied,
        "median_ratio": s.median_ratio,
        "max_ratio": s.max_ratio,
        "p_cost": s.p_cost,
        "a_spend_joint": s.a_spend_joint,
        "b_spend_joint": s.b_spend_joint,
        "unpaired_a": list(paired.unpaired_a),
        "unpaired_b": list(paired.unpaired_b),
        "arm_platform_failed": paired.arm_platform_failed,
        "reverify_failed": paired.reverify_failed,
        "discordant_cells": [
            {
                "bench": c.bench,
                "seed": c.seed,
                "a": c.a_solved,
                "b": c.b_solved,
            }
            for c in paired.cells
            if c.a_solved != c.b_solved
        ],
    }
    if verdict is not None:
        out["verdict"] = {
            "outcome": verdict.outcome,
            "rule": verdict.rule,
            "reason": verdict.reason,
            "tier": verdict.tier,
        }
    return out
