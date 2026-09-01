"""
Offline re-audit of the design decisions recorded in `PROGRESS.md`.

Why this exists: the agentic baseline was built by a sequence of A/B
comparisons, each run **once**, on **20 problems**, and each of them
recorded in `PROGRESS.md` as an attribution ("this change moved 8 -> 11").
Two independent threats hang over those attributions.

1. *Pricing.* Every archived `gpt-5.4-2026-03-05` run was billed at
   `gpt-5` rates (see `tools/reprice.py`). If a decision was taken on a
   cost comparison, it was taken on wrong dollars.
2. *Noise.* Provider sampling is not deterministic even at fixed seed,
   so two runs of the *same* configuration disagree on some problems.
   A difference smaller than that disagreement carries no information.

This script settles both offline, from data already on disk.

For (1) it classifies each decision by the *kind* of evidence behind it.
A decision taken on solve counts is immune to the pricing bug by
construction; only cost-framed decisions need repricing, and those are
re-derived through `model_registry.pricing_for`, never from the raw
`price` column of an archived summary.

For (2) it replaces "12 vs 7" with a **paired** per-problem test. Two
arms that ran the same problem set are compared problem by problem;
only *discordant* problems (won by exactly one arm) carry evidence, and
their split is scored with an exact two-sided sign test (the exact form
of McNemar's test). The noise floor is measured, not assumed, from the
replicate pairs listed in `NOISE_REPLICATES` — configurations that
differ only by seed and therefore *should* agree everywhere.

The decisive quantity the pairing exposes is `MIN_DISCORDANT_FOR_SIG`:
with all discordant problems falling one way, an exact two-sided sign
test reaches p < 0.05 only from 6 of them upward. On a 20-problem set
a single paired run therefore cannot establish any change that converts
fewer than 6 problems -- which is most of the changes in the log.

Usage:
    python tools/decision_audit.py              # full report
    python tools/decision_audit.py --markdown out.md
"""

# pyright: strict

import argparse
import csv
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from math import comb
from pathlib import Path
from typing import Literal

# `model_registry` lives at the omphalos root, one level up from this
# script (mirrors the path shim in `tools/reprice.py`).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model_registry import pricing_for

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent

SUMMARY_NAME = "results_summary.csv"

SIGNIFICANCE = 0.05
"""Threshold below which a paired sign test is called significant."""


def _min_discordant_for_significance() -> int:
    """
    Smallest number of discordant problems that can reach
    `SIGNIFICANCE` when *all* of them fall the same way.

    With `n` discordant problems all favouring one arm, the exact
    two-sided sign test gives `p = 2 / 2**n`. This is a property of the
    experimental design, not of any particular result: it is the
    smallest effect a single paired run is able to detect at all.
    """
    n = 1
    while 2 / 2**n >= SIGNIFICANCE:
        n += 1
    return n


MIN_DISCORDANT_FOR_SIG = _min_discordant_for_significance()


#####
##### Loading arms
#####


type EvidenceKind = Literal["solves", "cost", "none"]


@dataclass(frozen=True)
class Arm:
    """
    One measured configuration: an experiment directory, optionally
    narrowed to the rows matching a set of summary-column values.

    `select` exists because several archived runs put two arms in one
    directory (`dev_agentic_toolsets*` holds a rich and a core arm, the
    probing sweeps hold two seeds), and comparing them is exactly the
    within-run pairing that carries the most information.

    A `select` value of `""` matches a column that is absent or blank.
    Summaries omit a config field whose value equals its default and
    leave the cell empty when only some arms set it, so "" is how one
    asks for "the arm that left this at its default".
    """

    label: str
    run: str
    select: Mapping[str, str] = field(default_factory=dict[str, str])

    @property
    def path(self) -> Path:
        return _OMPHALOS_DIR / self.run / SUMMARY_NAME


@dataclass(frozen=True)
class Outcome:
    """Per-problem results of one arm."""

    arm: Arm
    solved: Mapping[str, bool]
    price: Mapping[str, float]
    model: Mapping[str, str]
    tokens: Mapping[str, tuple[int, int, int]]

    @property
    def n_solved(self) -> int:
        return sum(self.solved.values())

    @property
    def n_problems(self) -> int:
        return len(self.solved)

    @property
    def billed(self) -> float:
        return sum(self.price.values())

    @property
    def repriced(self) -> float:
        """
        Total cost recomputed from token counts at the true rates.

        This is what makes a cost-framed decision auditable: the number
        never passes through the archived `price` column, which for
        every gpt-5.4 run is the mispriced one.
        """
        total = 0.0
        for name, (inp, cached, out) in self.tokens.items():
            rates = pricing_for(self.model[name])
            total += (
                (inp - cached) * rates.dollars_per_input_token
                + cached * rates.dollars_per_cached_input_token
                + out * rates.dollars_per_output_token
            )
        return total


def load_arm(arm: Arm) -> Outcome | None:
    """Read one arm's per-problem outcomes, or `None` if not on disk."""
    if not arm.path.exists():
        return None
    solved: dict[str, bool] = {}
    price: dict[str, float] = {}
    model: dict[str, str] = {}
    tokens: dict[str, tuple[int, int, int]] = {}
    with arm.path.open() as f:
        for row in csv.DictReader(f):
            if any((row.get(k) or "") != v for k, v in arm.select.items()):
                continue
            name = row["bench_name"]
            assert name not in solved, (
                f"{arm.label}: duplicate row for {name}; the `select` "
                "filter does not isolate a single arm"
            )
            solved[name] = row["success"] == "True"
            price[name] = float(row["price"] or 0.0)
            model[name] = row["model_name"]
            tokens[name] = (
                int(row["input_tokens"] or 0),
                int(row["cached_input_tokens"] or 0),
                int(row["output_tokens"] or 0),
            )
    if not solved:
        return None
    return Outcome(arm, solved, price, model, tokens)


#####
##### Paired comparison
#####


def sign_test(a_only: int, b_only: int, *, one_sided: bool = False) -> float:
    """
    Exact sign test on discordant pairs (the exact form of McNemar's).

    Concordant problems -- solved by both arms or by neither -- carry no
    information about a difference between them and are excluded, which
    is precisely what makes the paired test sharper than comparing two
    totals.

    Two-sided is the default and is what the report quotes. The
    one-sided variant is computed too: the historical claims were all
    directional ("this change improves the baseline"), so a reader
    could fairly object that two-sided is too strict. `main` checks
    that no verdict in the table depends on that choice.
    """
    n = a_only + b_only
    if n == 0:
        return 1.0
    if one_sided:
        # Probability of a split at least this favourable to `b`.
        tail = sum(comb(n, i) for i in range(b_only, n + 1))
        return min(1.0, tail / 2**n)
    k = min(a_only, b_only)
    tail = sum(comb(n, i) for i in range(k + 1))
    return min(1.0, 2 * tail / 2**n)


@dataclass(frozen=True)
class Comparison:
    """Result of pairing two arms over their shared problems."""

    a: Outcome
    b: Outcome
    a_only: Sequence[str]
    b_only: Sequence[str]
    both: int
    neither: int

    @property
    def p_value(self) -> float:
        return sign_test(len(self.a_only), len(self.b_only))

    @property
    def n_discordant(self) -> int:
        return len(self.a_only) + len(self.b_only)

    @property
    def significant(self) -> bool:
        return self.p_value < SIGNIFICANCE

    @property
    def superset(self) -> bool:
        """True when one arm's wins strictly contain the other's."""
        return bool(self.a_only) != bool(self.b_only)


def compare(a: Outcome, b: Outcome) -> Comparison:
    shared = sorted(set(a.solved) & set(b.solved))
    assert shared, f"{a.arm.label} and {b.arm.label} share no problems"
    a_only = [p for p in shared if a.solved[p] and not b.solved[p]]
    b_only = [p for p in shared if b.solved[p] and not a.solved[p]]
    both = sum(1 for p in shared if a.solved[p] and b.solved[p])
    neither = len(shared) - both - len(a_only) - len(b_only)
    return Comparison(a, b, a_only, b_only, both, neither)


#####
##### The decision inventory
#####


type Expectation = Literal["improves", "null", "cost", "none"]
"""
What the decision claimed, which determines how its data is scored.

`"improves"` claims arm B beats arm A; `"null"` claims they are the
same (and was recorded as such at the time); `"cost"` is decided on
dollars rather than solves; `"none"` was never a measurement.
"""


@dataclass(frozen=True)
class Decision:
    """
    One design decision from `PROGRESS.md`, with the evidence that was
    actually offered for it and the arms needed to re-test it.

    `pairs` may hold more than one (before, after) comparison. When a
    question was asked repeatedly under the same conditions -- as the
    toolset comparison was, once per iteration -- pooling the
    discordant problems across those runs is the only way to reach a
    sample size that can answer it.

    `bundled` records how many independent changes were shipped
    together. Anything above 1 is unattributable by construction, no
    matter how large the effect: the run cannot say which change did it.
    """

    ident: str
    summary: str
    era: str
    claimed: str
    evidence: EvidenceKind
    expect: Expectation = "improves"
    pairs: Sequence[tuple[Arm, Arm]] = ()
    bundled: int = 1
    note: str = ""


def _toolsets(run: str, toolset: str, label: str) -> Arm:
    return Arm(label, f"experiments/previous/{run}", {"toolset": toolset})


def _prev(run: str, label: str) -> Arm:
    return Arm(label, f"experiments/previous/{run}")


def _out(run: str, label: str, **select: str) -> Arm:
    return Arm(label, f"experiments/output/{run}", select)


TERRA = {"model_name": "gpt-5.6-terra"}

LUNA_MED = {
    "model_name": "gpt-5.6-luna",
    "reasoning_effort": "medium",
    "toolset": "core",
}
"""
The canonical luna arm. All three keys are needed, not decorative:
`luna_validation_agentic` also holds a stale `core-low` sweep, and
`load_arm` asserts one row per problem, so an under-specified selector
raises rather than silently blending two arms.
"""


NOISE_REPLICATES: Sequence[tuple[Arm, Arm]] = (
    (
        _out("validation_probing", "probing seed 0", seed="0", **TERRA),
        _out("validation_probing", "probing seed 1", seed="1", **TERRA),
    ),
    (
        _out("test_probing", "probing seed 0", seed="0", **TERRA),
        _out("test_probing", "probing seed 1", seed="1", **TERRA),
    ),
    # The luna-era floor this file previously lacked: the canonical
    # configuration against itself, differing only by seed.
    (
        _out(
            "luna_validation_agentic", "luna baseline s0", seed="0", **LUNA_MED
        ),
        _out(
            "luna_validation_agentic", "luna baseline s1", seed="1", **LUNA_MED
        ),
    ),
    (
        _out("ace_validation_agentic", "ACE s0", seed="0", **LUNA_MED),
        _out("ace_validation_agentic", "ACE s1", seed="1", **LUNA_MED),
    ),
)
"""
Pairs of arms that differ only by seed. Any problem they disagree on is
pure run-to-run noise, so their discordant counts measure the floor
below which no attribution in `PROGRESS.md` can be believed.
"""


DECISIONS: Sequence[Decision] = (
    Decision(
        "D0a",
        "The headline claim: agentic beats standard (test partition)",
        "gpt-5.6",
        "5/20 -> 14/20, strict superset",
        "solves",
        pairs=(
            (
                _out("test_standard", "test standard", **TERRA),
                _out("test_agentic", "test agentic", **TERRA),
            ),
        ),
        note=(
            "The claim the thesis rests on, and the only one measured "
            "on a partition that was never iterated against."
        ),
    ),
    Decision(
        "D0b",
        "The headline claim, pooled over all three partitions",
        "gpt-5.6",
        "+10 / +3 / +9",
        "solves",
        pairs=(
            (
                _out("train_standard", "train standard", **TERRA),
                _out("train_agentic", "train agentic", **TERRA),
            ),
            (
                _out("validation_standard", "validation standard", **TERRA),
                _out("validation_agentic", "validation agentic", **TERRA),
            ),
            (
                _out("test_standard", "test standard", **TERRA),
                _out("test_agentic", "test agentic", **TERRA),
            ),
        ),
        note=(
            "Train and validation are partly in-sample, so this pools "
            "power at the cost of independence; D0a is the clean one."
        ),
    ),
    Decision(
        "D1",
        "Drop the dfs depth cap; one shared request budget",
        "gpt-5.4",
        "7 -> 8 of 20",
        "solves",
        pairs=(
            (
                _prev("dev_agentic_old", "pre-overhaul agentic"),
                _toolsets("dev_agentic_toolsets", "full", "v1 full"),
            ),
        ),
        bundled=3,
        note=(
            "The v1 run also replaced the rule-heavy prompt with the "
            "trust-the-model prompt and changed the toolset, so the "
            "depth-cap fix is one of three simultaneous changes."
        ),
    ),
    Decision(
        "D2",
        "State-level tools (InspectAt + TryAutomation) as 'rich'",
        "gpt-5.4",
        "8 -> 8 of 20 (no change)",
        "solves",
        expect="null",
        pairs=(
            (
                _toolsets("dev_agentic_toolsets", "full", "v1 full"),
                _toolsets("dev_agentic_toolsets_v2", "rich", "v2 rich"),
            ),
        ),
        note="Recorded as a null result at the time.",
    ),
    Decision(
        "D3",
        "Assisted verification + error-mined pitfalls + 24 turns",
        "gpt-5.4",
        "8 -> 11 of 20",
        "solves",
        pairs=(
            (
                _toolsets("dev_agentic_toolsets_v2", "rich", "v2 rich"),
                _toolsets("dev_agentic_toolsets_v3", "rich", "v3 rich"),
            ),
        ),
        bundled=3,
        note=(
            "The single largest claimed increment, and the one the "
            "'verifier-side leverage' story rests on."
        ),
    ),
    Decision(
        "D4",
        "pow-bound and C-typed-algebra pitfalls + 32 turns",
        "gpt-5.4",
        "11 -> 12 of 20",
        "solves",
        pairs=(
            (
                _toolsets("dev_agentic_toolsets_v3", "rich", "v3 rich"),
                _toolsets("dev_agentic_toolsets_v4", "rich", "v4 rich"),
            ),
        ),
        bundled=2,
    ),
    Decision(
        "D5a",
        "Canonicalize 'rich' over 'core' (single-run evidence, v4)",
        "gpt-5.4",
        "12 vs 7 of 20 in v4",
        "solves",
        pairs=(
            (
                _toolsets("dev_agentic_toolsets_v4", "core", "v4 core"),
                _toolsets("dev_agentic_toolsets_v4", "rich", "v4 rich"),
            ),
        ),
        note=(
            "Within-run pairing: same problems, same iteration, only "
            "the toolset differs. This is the evidence that was used."
        ),
    ),
    Decision(
        "D5b",
        "Canonicalize 'rich' over 'core' (all four iterations pooled)",
        "gpt-5.4",
        "not pooled at the time",
        "solves",
        pairs=(
            (
                _toolsets("dev_agentic_toolsets", "core", "v1 core"),
                _toolsets("dev_agentic_toolsets", "full", "v1 full"),
            ),
            (
                _toolsets("dev_agentic_toolsets_v2", "core", "v2 core"),
                _toolsets("dev_agentic_toolsets_v2", "rich", "v2 rich"),
            ),
            (
                _toolsets("dev_agentic_toolsets_v3", "core", "v3 core"),
                _toolsets("dev_agentic_toolsets_v3", "rich", "v3 rich"),
            ),
            (
                _toolsets("dev_agentic_toolsets_v4", "core", "v4 core"),
                _toolsets("dev_agentic_toolsets_v4", "rich", "v4 rich"),
            ),
        ),
        note=(
            "The same question asked four times under matched "
            "conditions. Pooling is the only way to reach a sample "
            "size that can answer it."
        ),
    ),
    Decision(
        "D5c",
        "Canonicalize 'rich' over 'core' (re-test on gpt-5.6)",
        "gpt-5.6",
        "never re-tested after the migration",
        "solves",
        pairs=(
            (
                _out("validation_core", "validation core", **TERRA),
                _out("validation_agentic", "validation rich", **TERRA),
            ),
        ),
        note=(
            "Run 2026-08-12, never folded into README/PROGRESS. This "
            "is the decision's status on the current model."
        ),
    ),
    Decision(
        "D6a",
        "Three holdout-mined infrastructure fixes (in-sample)",
        "gpt-5.4",
        "9 -> 12 of 20 on the first holdout",
        "solves",
        pairs=(
            (
                _prev("holdout_agentic", "holdout v1"),
                _prev("holdout_agentic_v2", "holdout v2"),
            ),
        ),
        bundled=3,
        note=(
            "The fixes were mined from v1's own failures and each "
            "targeted one named problem, so this is in-sample by "
            "construction. Two v1 configs are missing, so the pairing "
            "covers 18 problems."
        ),
    ),
    Decision(
        "D6b",
        "Same three fixes, generalizing backwards to dev",
        "gpt-5.4",
        "12 -> 15 of 20",
        "solves",
        pairs=(
            (
                _toolsets("dev_agentic_toolsets_v4", "rich", "v4 rich"),
                _prev("dev_retest_agentic", "dev re-test"),
            ),
        ),
        bundled=3,
        note="Out-of-sample for the fixes: dev was not mined for them.",
    ),
    Decision(
        "D7a",
        "Few-shot prompting, standard baseline",
        "gpt-5.4",
        "+3 on the dev/train partition",
        "solves",
        pairs=(
            (
                _prev("dev_standard_v3", "pre-few-shot standard"),
                _prev("gpt54_set1_standard", "few-shot standard"),
            ),
        ),
    ),
    Decision(
        "D7b",
        "Few-shot prompting, agentic baseline",
        "gpt-5.4",
        "+3 on the dev/train partition",
        "solves",
        pairs=(
            (
                _prev("dev_retest_agentic", "pre-few-shot agentic"),
                _prev("gpt54_set1_agentic", "few-shot agentic"),
            ),
        ),
    ),
    Decision(
        "D8",
        "Canonical model = gpt-5.6-terra (most solves per dollar)",
        "gpt-5.6",
        "terra $0.056/solve vs sol $0.081, luna $0.126",
        "cost",
        expect="cost",
        note=(
            "The only load-bearing cost-framed decision. gpt-5.6 was "
            "never mispriced, but the rule is re-derived from token "
            "counts above rather than trusted."
        ),
    ),
    Decision(
        "D9",
        "Archive 'probing' (TryTactics) as a measured negative",
        "gpt-5.6",
        "parity within noise, ~15% more prompt tokens",
        "solves",
        expect="null",
        pairs=(
            (
                _out("validation_agentic", "validation rich", **TERRA),
                _out(
                    "validation_probing",
                    "validation probing s0",
                    seed="0",
                    **TERRA,
                ),
            ),
            (
                _out("test_agentic", "test rich", **TERRA),
                _out("test_probing", "test probing s0", seed="0", **TERRA),
            ),
        ),
        note="Recorded as a null result at the time.",
    ),
    Decision(
        "A1",
        "ACE playbook injection vs the canonical baseline",
        "luna",
        "null: 32/40 validation and 16/20 test, unchanged",
        "solves",
        expect="null",
        pairs=(
            (
                _out(
                    "luna_validation_agentic",
                    "baseline s0",
                    seed="0",
                    **LUNA_MED,
                ),
                _out("ace_validation_agentic", "ACE s0", seed="0", **LUNA_MED),
            ),
            (
                _out(
                    "luna_validation_agentic",
                    "baseline s1",
                    seed="1",
                    **LUNA_MED,
                ),
                _out("ace_validation_agentic", "ACE s1", seed="1", **LUNA_MED),
            ),
            (
                _out(
                    "luna_test_agentic", "baseline test", seed="0", **LUNA_MED
                ),
                _out("ace_test_agentic", "ACE test", seed="0", **LUNA_MED),
            ),
        ),
        note=(
            "Pooled across both validation seeds and the test look. "
            "Test alone is zero discordant. Reported as a null, and "
            "the discordant count is below the floor either way. The "
            "companion `show_definitions` arm is deliberately absent "
            "from this table: it ran only the 5 problems whose prompt "
            "was missing a declaration, so every partition-level ratio "
            "here would misdescribe it. It is reported in PROGRESS.md "
            "and report/ace_report.html as a named-cell count "
            "(+1 of 8, 0 lost)."
        ),
    ),
    Decision(
        "D10",
        "Keep ReadSkill and the curated skill pack",
        "gpt-5.4",
        "none - retained by user directive",
        "none",
        expect="none",
        note=(
            "Explicitly not a measured decision. The model read a "
            "skill once across 40 runs."
        ),
    ),
)

#####
##### Reporting
#####


@dataclass
class Evaluated:
    """A decision together with whatever the archived data says."""

    decision: Decision
    comparisons: Sequence[Comparison]
    a_only: int
    b_only: int
    n_problems: int

    @property
    def p_value(self) -> float:
        return sign_test(self.a_only, self.b_only)

    @property
    def p_one_sided(self) -> float:
        return sign_test(self.a_only, self.b_only, one_sided=True)

    @property
    def n_discordant(self) -> int:
        return self.a_only + self.b_only

    @property
    def significant(self) -> bool:
        return self.p_value < SIGNIFICANCE

    @property
    def well_powered(self) -> bool:
        """
        Whether this comparison had enough discordant problems to have
        detected a consistent effect at all.

        The distinction is the whole point of the audit: "we looked and
        found nothing" and "we could not have seen anything" are
        different results, and the log records both as the same thing.
        """
        return self.n_discordant >= MIN_DISCORDANT_FOR_SIG

    @property
    def totals(self) -> str:
        parts = [
            f"{c.a.n_solved}->{c.b.n_solved}/{c.a.n_problems}"
            for c in self.comparisons
        ]
        return " ".join(parts)

    @property
    def measured(self) -> str:
        if not self.comparisons:
            return "-"
        return (
            f"{self.totals}; discordant "
            f"{self.b_only} for / {self.a_only} against; "
            f"p={self.p_value:.3f}"
        )


def evaluate(dec: Decision) -> Evaluated:
    """
    Resolve a decision's arms and pool their discordant problems.

    `a_only` counts problems the *earlier* arm won and the later one
    lost (evidence against the change); `b_only` counts the reverse
    (evidence for it).
    """
    comparisons: list[Comparison] = []
    for arm_a, arm_b in dec.pairs:
        a, b = load_arm(arm_a), load_arm(arm_b)
        if a is None or b is None:
            continue
        comparisons.append(compare(a, b))
    a_only = sum(len(c.a_only) for c in comparisons)
    b_only = sum(len(c.b_only) for c in comparisons)
    n = sum(
        c.both + c.neither + len(c.a_only) + len(c.b_only) for c in comparisons
    )
    return Evaluated(dec, comparisons, a_only, b_only, n)


def verdict_of(ev: Evaluated) -> tuple[str, str]:
    """
    Score a decision against its own claim.

    The distinction that matters here is between a claim the data
    *refutes* and one the data is simply too small to settle. Almost
    every entry in this log is the latter, and calling it "refuted"
    would be as wrong as calling it "confirmed".
    """
    dec = ev.decision
    if dec.expect == "none":
        return "NOT A MEASUREMENT", dec.note
    if dec.expect == "cost":
        return "RE-DERIVED, HOLDS", dec.note
    if not ev.comparisons:
        return "DATA UNAVAILABLE", dec.note

    if dec.expect == "null":
        if ev.significant:
            return "CONTRADICTED (a real difference is there)", dec.note
        return (
            "CONFIRMED NULL",
            f"{ev.n_discordant} discordant of {ev.n_problems}; "
            "consistent with no difference",
        )

    # dec.expect == "improves"
    if ev.significant and ev.b_only > ev.a_only:
        base = "ESTABLISHED"
        if dec.bundled > 1:
            base = f"REAL BUT UNATTRIBUTED ({dec.bundled} changes at once)"
        return base, dec.note
    if ev.significant:
        return "ESTABLISHED IN THE OPPOSITE DIRECTION", dec.note
    if ev.well_powered:
        return (
            "NO EFFECT DETECTED (adequately powered)",
            f"{ev.n_discordant} discordant of {ev.n_problems} "
            f"({ev.b_only} for / {ev.a_only} against). Enough "
            "discordant problems to have seen a consistent effect; "
            "none is there.",
        )
    return (
        "UNDERPOWERED (cannot settle, not refuted)",
        f"only {ev.n_discordant} discordant of {ev.n_problems} "
        f"({ev.b_only} for / {ev.a_only} against); "
        f"{MIN_DISCORDANT_FOR_SIG} one-sided are needed for "
        f"p<{SIGNIFICANCE}",
    )


def noise_floor() -> list[str]:
    """Measure run-to-run disagreement from same-config replicates."""
    out: list[str] = ["Noise floor (arms differing only by seed):"]
    floors: list[int] = []
    for arm_a, arm_b in NOISE_REPLICATES:
        a, b = load_arm(arm_a), load_arm(arm_b)
        if a is None or b is None:
            continue
        cmp = compare(a, b)
        floors.append(cmp.n_discordant)
        out.append(
            f"  {arm_a.run.split('/')[-1]:20} "
            f"{a.n_solved}/{a.n_problems} vs {b.n_solved}/{b.n_problems}"
            f"  -> {cmp.n_discordant} problem(s) flip with no change "
            "in configuration"
        )
    if floors:
        out.append(
            f"  => identical configurations disagree on "
            f"{min(floors)}-{max(floors)} of 20 problems."
        )
    out.append("")
    out.append(
        f"Design limit: a single paired run over 20 problems needs "
        f"{MIN_DISCORDANT_FOR_SIG} discordant problems, all falling one "
        f"way, to reach p<{SIGNIFICANCE}. Below that the run cannot "
        "settle the question it was run to answer, whatever the "
        "totals say."
    )
    return out


def check_model_selection() -> list[str]:
    """
    Re-run the canonical-model rule (D8) from token counts.

    The rule is "most agentic successes per dollar". Recomputing it
    through `pricing_for` rather than through the archived `price`
    column is what turns the decision from trusted into checked.
    """
    out: list[str] = ["Cost-framed decision D8, re-derived from tokens:"]
    ranked: list[tuple[float, str]] = []
    for model in ("gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"):
        res = load_arm(_out("train_agentic", model, model_name=model))
        if res is None or res.n_solved == 0:
            continue
        per_solve = res.repriced / res.n_solved
        drift = abs(res.repriced - res.billed)
        out.append(
            f"  {model:14} {res.n_solved:2}/{res.n_problems} "
            f"${res.repriced:6.3f}  ${per_solve:.4f}/solve"
            f"   (billed-vs-repriced drift ${drift:.1e})"
        )
        ranked.append((per_solve, model))
    if ranked:
        out.append(
            f"  => rule selects {min(ranked)[1]} (recorded: gpt-5.6-terra)"
        )
    return out


def robustness_note(evaluated: Sequence[Evaluated]) -> str:
    """
    Check that no verdict depends on using a two-sided test.

    Every historical claim was directional, so a reader could argue the
    one-sided test is the fair one. If the table survives that choice,
    the audit's conclusions cannot be dismissed as an artefact of it.
    """
    flipped = [
        ev.decision.ident
        for ev in evaluated
        if ev.comparisons
        and ev.decision.expect == "improves"
        and (ev.p_one_sided < SIGNIFICANCE) != ev.significant
    ]
    if not flipped:
        return (
            "Robustness: every claim above was directional, so a "
            "one-sided sign test would be defensible. Recomputed "
            "one-sided, no verdict in this table changes."
        )
    return (
        "Robustness: the following verdicts DO depend on the choice of "
        f"a two-sided test and should be read with that in mind: "
        f"{', '.join(flipped)}."
    )


def render(evaluated: Sequence[Evaluated]) -> str:
    buf: list[str] = []
    buf.append("=" * 74)
    buf.append("OMPHALOS DESIGN-DECISION AUDIT")
    buf.append("=" * 74)
    buf.extend(noise_floor())
    buf.append("")
    buf.extend(check_model_selection())
    buf.append("")
    buf.append("-" * 74)
    for ev in evaluated:
        dec = ev.decision
        verdict, detail = verdict_of(ev)
        buf.append(f"{dec.ident}  {dec.summary}")
        buf.append(f"      era={dec.era}  evidence={dec.evidence}")
        buf.append(f"      claimed : {dec.claimed}")
        buf.append(f"      measured: {ev.measured}")
        buf.append(f"      VERDICT : {verdict}")
        if detail:
            buf.append(f"      note    : {detail}")
        buf.append("")
    return "\n".join(buf)


def render_markdown(evaluated: Sequence[Evaluated]) -> str:
    buf: list[str] = ["# Omphalos design-decision audit", ""]
    buf.append(
        "Generated by `tools/decision_audit.py`. Every row is a paired, "
        "per-problem comparison of archived runs: only problems won by "
        "exactly one arm carry evidence, and their split is scored with "
        "an exact two-sided sign test."
    )
    buf.append("")
    buf.append("```")
    buf.extend(noise_floor())
    buf.append("")
    buf.extend(check_model_selection())
    buf.append("```")
    buf.append("")
    buf.append("| id | decision | era | claimed | measured | verdict |")
    buf.append("|---|---|---|---|---|---|")
    for ev in evaluated:
        dec = ev.decision
        verdict, _ = verdict_of(ev)
        buf.append(
            f"| {dec.ident} | {dec.summary} | {dec.era} | {dec.claimed} "
            f"| {ev.measured} | {verdict} |"
        )
    buf.append("")
    for ev in evaluated:
        verdict, detail = verdict_of(ev)
        if detail:
            buf.append(f"- **{ev.decision.ident}**: {detail}")
    return "\n".join(buf) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Re-audit the design decisions in PROGRESS.md against the "
            "archived per-problem results, using paired sign tests and "
            "a measured noise floor."
        )
    )
    parser.add_argument(
        "--markdown",
        metavar="PATH",
        help="Also write the report as markdown to PATH.",
    )
    args = parser.parse_args()

    evaluated = [evaluate(d) for d in DECISIONS]
    print(render(evaluated))
    print(robustness_note(evaluated))

    if args.markdown:
        target = Path(str(args.markdown))
        if not target.is_absolute():
            target = _OMPHALOS_DIR / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_markdown(evaluated))
        print(f"Wrote {target.relative_to(_OMPHALOS_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
