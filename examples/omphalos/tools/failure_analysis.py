"""
What the prover actually gets wrong, from recorded runs.

Solve counts say how often a configuration fails; they say nothing about
*how*. This walks the request caches, recovers every verifier verdict,
and buckets the Rocq errors into a taxonomy — so a claim like "luna and
terra fail the same way" can be checked rather than asserted.

**Where the data is.** Every `dp.compute` call is cached like an LLM
request, with a synthetic `__compute__` model and a `fun: <name>` body.
The verifier's `Feedback` dataclass (`pytanque_utils.py:94`) is dumped
verbatim as YAML in the output of the `check` / `check_assisted`
entries, so the structured fields — `failing_tactic`, `error_message`,
`remaining_goals`, `finished` — are recovered directly rather than
scraped back out of the rendered prompt.

**Counting rule.** Every proposal produces one verdict, and a hard
problem produces many near-identical ones, so pooling raw verdicts
mostly counts how long the model was allowed to thrash. Numbers are
therefore reported two ways: `verdicts` (every failed check) and
`problems` (how many distinct benchmark problems ever produced that
class). The second is the one to quote — it does not let a single
stubborn problem dominate a taxonomy.

Failures inside *solved* runs count too: a run that recovers on turn
five still made four mistakes, and excluding them would bias the
taxonomy toward whatever kills a run outright.

One failure mode leaves no verdict at all and so has to be counted
separately: a run that spends its whole budget on tool calls and
**never proposes a proof**. It is reported as `never-proposed`, and it
turns out to be a property of the toolset rather than the model — see
the 2026-08-13 entry in PROGRESS.md.

Usage:
    python tools/failure_analysis.py experiments/output/luna_test_agentic
    python tools/failure_analysis.py <run> <run> --compare
    python tools/failure_analysis.py <run> --examples 3
    python tools/failure_analysis.py <run> --json out.json
"""

# pyright: strict

import argparse
import csv
import json
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import yaml

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent

SUMMARY_NAME = "results_summary.csv"

_CHECK_PREFIXES = ("fun: check_assisted", "fun: check\n")


#####
##### Taxonomy
#####


@dataclass(frozen=True)
class ErrorClass:
    """One bucket of the taxonomy, matched against the Rocq error."""

    label: str
    pattern: str
    blurb: str

    def matches(self, message: str) -> bool:
        return re.search(self.pattern, message, re.I | re.S) is not None


TAXONOMY: tuple[ErrorClass, ...] = (
    # Every multi-word pattern joins its words with `\s+`: Rocq's
    # pretty-printer wraps long messages at ~78 columns, so a verbatim
    # "was not found in the current environment" straddles a line break
    # in a quarter of the recorded caches and used to fall into `other`
    # (2026-09-02 correction; the taxonomy under-reported the largest
    # fixable class by that much).
    ErrorClass(
        "incomplete-proof",
        r"Attempt\s+to\s+save\s+an\s+incomplete\s+proof",
        "every tactic applied but goals were left open at Qed",
    ),
    ErrorClass(
        "no-witness",
        r"Cannot\s+find\s+witness",
        "a nonlinear-arithmetic closer (nia/nra) gave up",
    ),
    ErrorClass(
        "unknown-reference",
        r"(reference|variable)\s.*\swas\s+not\s+found\s+in\s+the\s+current"
        r"\s+environment",
        "reached for a lemma or tactic that does not exist here",
    ),
    ErrorClass(
        "syntax-error",
        r"Syntax\s+error",
        "malformed Rocq sentence",
    ),
    ErrorClass(
        "no-applicable-tactic",
        r"No\s+applicable\s+tactic",
        "a closer was applied to a goal shape it cannot handle",
    ),
    ErrorClass(
        "rewrite-no-match",
        r"Found\s+no\s+subterm\s+matching",
        "rewrite target absent — usually a normal-form mismatch",
    ),
    ErrorClass(
        "already-used",
        r"is\s+already\s+used",
        "re-bound a name already in context",
    ),
    ErrorClass(
        "focus-error",
        r"cannot\s+be\s+unfocused|This\s+proof\s+is\s+focused"
        r"|Wrong\s+bullet",
        "mismatched bullets or braces",
    ),
    ErrorClass(
        "not-convertible",
        r"Not\s+convertible",
        "`change` to a term that is not definitionally equal",
    ),
    ErrorClass(
        "type-mismatch",
        r"Unable\s+to\s+apply\s+lemma|The\s+term\s.*\shas\s+type"
        r"|Illegal\s+application",
        "term does not have the type the goal wants",
    ),
    ErrorClass(
        "timeout",
        r"Timeout|timed\s+out",
        "a tactic exceeded its time budget",
    ),
    ErrorClass(
        "prover-crash",
        r"No\s+response\s+from\s+pet\s+process|transport\s+failure"
        r"|closed\s+the\s+connection|Stack\s+overflow|Out\s+of\s+memory",
        "the prover died on the tactic (vm_compute on a huge term, …)",
    ),
)

UNCLASSIFIED = "other"


def classify(message: str | None) -> str:
    """Bucket one Rocq error message, or `other` if nothing matches."""
    if message == NEVER_PROPOSED:
        return NEVER_PROPOSED
    if not message:
        return UNCLASSIFIED
    for cls in TAXONOMY:
        if cls.matches(message):
            return cls.label
    return UNCLASSIFIED


#####
##### Extraction
#####


NEVER_PROPOSED = "never-proposed"
"""
Pseudo-class for a config that produced no verdict at all: the agent
explored until its budget ran out without ever submitting a proof.
Invisible to an error taxonomy by construction, since a taxonomy can
only classify errors that happened.
"""


@dataclass(frozen=True)
class Verdict:
    """One verifier result recovered from a cache."""

    bench: str
    config: str
    solved_run: bool
    success: bool
    failing_tactic: str | None
    error_message: str | None
    n_remaining_goals: int
    finished: bool

    @property
    def error_class(self) -> str:
        return classify(self.error_message)


def _feedback_entries(cache: Path) -> list[dict[str, Any]]:
    """
    Every `check` / `check_assisted` verdict in one config's cache.

    The `CSafeLoader` matters: these files run to tens of thousands of
    lines and the pure-Python loader makes a whole-sweep pass painful.
    """
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    raw: Any = yaml.load(cache.read_text(), Loader=loader)
    out: list[dict[str, Any]] = []
    for entry in cast(Sequence[Mapping[str, Any]], raw):
        request = cast(
            Mapping[str, Any],
            cast(Mapping[str, Any], entry.get("input") or {}).get("request")
            or {},
        )
        chat = cast(Sequence[Mapping[str, Any]], request.get("chat") or ())
        if not chat:
            continue
        body = str(chat[-1].get("content") or "")
        if not body.startswith(_CHECK_PREFIXES):
            continue
        output = cast(Mapping[str, Any] | None, entry.get("output"))
        if output is None:
            continue
        outputs = cast(
            Sequence[Mapping[str, Any]], output.get("outputs") or ()
        )
        if not outputs:
            continue
        parsed = yaml.load(str(outputs[0].get("content") or ""), Loader=loader)
        if isinstance(parsed, dict):
            out.append(cast(dict[str, Any], parsed))
    return out


def load_run(run: Path, arm: "re.Pattern[str] | None" = None) -> list[Verdict]:
    """
    Recover every verdict in an experiment directory.

    `arm` restricts to configs whose arm segment (the second of the
    four `__`-separated fields in the directory name) matches. Without
    it, a directory holding several arms is read as one population:
    `luna_validation_agentic`, for instance, holds a stale `core-low`
    sweep alongside the canonical `core-medium` one, and blending them
    silently doubles the verdict count of the arm you meant.
    """
    summary = run / SUMMARY_NAME
    assert summary.exists(), f"no {SUMMARY_NAME} in {run}"
    solved: dict[str, bool] = {}
    with summary.open() as f:
        for row in csv.DictReader(f):
            solved[row["bench_name"]] = row["success"] == "True"
    verdicts: list[Verdict] = []
    for cache in sorted(run.glob("configs/*/cache.yaml")):
        config = cache.parent.name
        parts = config.split("__")
        if arm is not None:
            assert len(parts) == 4, (
                f"{config}: an arm filter needs the four-field config "
                "naming convention; this directory does not use it"
            )
            if not arm.fullmatch(parts[1]):
                continue
        bench = parts[0]
        entries = _feedback_entries(cache)
        if not entries:
            verdicts.append(
                Verdict(
                    bench=bench,
                    config=config,
                    solved_run=solved.get(bench, False),
                    success=False,
                    failing_tactic=None,
                    error_message=NEVER_PROPOSED,
                    n_remaining_goals=0,
                    finished=False,
                )
            )
            continue
        for fb in entries:
            verdicts.append(
                Verdict(
                    bench=bench,
                    config=config,
                    solved_run=solved.get(bench, False),
                    success=bool(fb.get("success")),
                    failing_tactic=cast(str | None, fb.get("failing_tactic")),
                    error_message=cast(str | None, fb.get("error_message")),
                    n_remaining_goals=len(
                        cast(list[Any], fb.get("remaining_goals") or [])
                    ),
                    finished=bool(fb.get("finished")),
                )
            )
    return verdicts


#####
##### Reporting
#####


@dataclass
class Tally:
    """Counts for one error class within one run."""

    verdicts: int = 0
    problems: set[str] = field(default_factory=set[str])
    unsolved_problems: set[str] = field(default_factory=set[str])
    examples: list[tuple[str, str, str]] = field(
        default_factory=list[tuple[str, str, str]]
    )


def tally(verdicts: Sequence[Verdict]) -> dict[str, Tally]:
    out: dict[str, Tally] = defaultdict(Tally)
    for v in verdicts:
        if v.success:
            continue
        t = out[v.error_class]
        t.verdicts += 1
        t.problems.add(v.bench)
        if not v.solved_run:
            t.unsolved_problems.add(v.bench)
        if len(t.examples) < 8 and v.error_message:
            t.examples.append(
                (v.bench, v.failing_tactic or "(none)", v.error_message)
            )
    return dict(out)


def _short(message: str, width: int = 96) -> str:
    """One-line form of a Rocq error, with the noise stripped."""
    text = re.sub(r"^\(-?\d+,\s*['\"]?", "", message.strip())
    text = text.replace("Coq: ", "").replace("\\n", " ")
    text = " ".join(text.split())
    return text[:width] + ("…" if len(text) > width else "")


def render_run(run: Path, verdicts: Sequence[Verdict], examples: int) -> str:
    counts = tally(verdicts)
    failed = sum(1 for v in verdicts if not v.success)
    n_problems = len({v.bench for v in verdicts})
    unsolved = {v.bench for v in verdicts if not v.solved_run}
    buf = [
        f"--- {run.name}",
        f"    {n_problems} problems, {len(verdicts)} verdicts "
        f"({failed} failed), {len(unsolved)} problems never solved",
        "",
        f"    {'class':22}{'verdicts':>9}{'problems':>10}{'unsolved':>10}"
        "  what it means",
    ]
    blurbs = {c.label: c.blurb for c in TAXONOMY}
    blurbs[NEVER_PROPOSED] = (
        "budget spent on tool calls; no proof was ever submitted"
    )
    for label, t in sorted(
        counts.items(), key=lambda kv: (-len(kv[1].problems), -kv[1].verdicts)
    ):
        buf.append(
            f"    {label:22}{t.verdicts:>9}{len(t.problems):>10}"
            f"{len(t.unsolved_problems):>10}  {blurbs.get(label, '')}"
        )
    if examples:
        buf.append("")
        for label, t in sorted(
            counts.items(), key=lambda kv: -len(kv[1].problems)
        ):
            for bench, tactic, message in t.examples[:examples]:
                buf.append(f"    [{label}] {bench[:34]}")
                buf.append(f"        tactic: {tactic[:88]}")
                buf.append(f"        error : {_short(message)}")
    return "\n".join(buf)


def render_compare(runs: Sequence[tuple[Path, Sequence[Verdict]]]) -> str:
    """
    Side-by-side taxonomy, plus the set comparison that matters more:
    which problems each configuration never solved.
    """
    buf = ["", "=" * 74, "COMPARISON", "=" * 74, ""]
    labels = [r.name for r, _ in runs]
    header = f"{'class':22}" + "".join(f"{n[:16]:>18}" for n in labels)
    buf.append(header)
    buf.append("-" * len(header))
    tallies = [tally(v) for _, v in runs]
    classes = sorted(
        {c for t in tallies for c in t},
        key=lambda c: (
            -max(len(t[c].problems) if c in t else 0 for t in tallies)
        ),
    )
    for cls in classes:
        row = f"{cls:22}"
        for t in tallies:
            if cls in t:
                row += f"{len(t[cls].problems):>10} probs"
            else:
                row += f"{'—':>18}"
        buf.append(row)

    buf.append("")
    unsolved: list[set[str]] = [
        {v.bench for v in vs if not v.solved_run} for _, vs in runs
    ]
    for name, u in zip(labels, unsolved, strict=True):
        buf.append(f"  never solved by {name}: {len(u)}")
    common: set[str] = set(unsolved[0]) if unsolved else set()
    union: set[str] = set()
    for u in unsolved:
        common &= u
        union |= u
    buf.append(f"  never solved by ALL: {len(common)} -> {sorted(common)}")
    if union - common:
        buf.append(
            f"  solved by some but not others: {sorted(union - common)}"
        )
    else:
        buf.append(
            "  no problem is solved by one and missed by another: these "
            "configurations fail on precisely the same set."
        )
    return "\n".join(buf)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recover every verifier verdict from recorded runs and "
            "bucket the Rocq errors into a taxonomy. No API calls."
        )
    )
    parser.add_argument("runs", nargs="+", help="experiment directories")
    parser.add_argument(
        "--examples",
        type=int,
        default=0,
        metavar="N",
        help="show N verbatim examples per error class",
    )
    parser.add_argument(
        "--arm",
        metavar="REGEX",
        help=(
            "restrict to configs whose arm segment matches, e.g. "
            "--arm 'core-medium|ace-[0-9a-f]{8}-core-medium'"
        ),
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="add a side-by-side table and the unsolved-set comparison",
    )
    parser.add_argument(
        "--json", metavar="PATH", help="also write the tallies as JSON"
    )
    args = parser.parse_args()

    arm = re.compile(str(args.arm)) if args.arm else None
    loaded: list[tuple[Path, list[Verdict]]] = []
    for raw in cast(list[str], args.runs):
        run = Path(raw)
        if not run.is_absolute():
            run = _OMPHALOS_DIR / run
        loaded.append((run, load_run(run, arm)))

    print("=" * 74)
    print("OMPHALOS FAILURE ANALYSIS")
    print("=" * 74)
    for run, verdicts in loaded:
        print()
        print(render_run(run, verdicts, int(args.examples)))
    if args.compare and len(loaded) > 1:
        print(render_compare(loaded))

    if args.json:
        target = Path(str(args.json))
        if not target.is_absolute():
            target = _OMPHALOS_DIR / target
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            run.name: {
                label: {
                    "verdicts": t.verdicts,
                    "problems": sorted(t.problems),
                    "unsolved_problems": sorted(t.unsolved_problems),
                }
                for label, t in tally(verdicts).items()
            }
            for run, verdicts in loaded
        }
        target.write_text(json.dumps(payload, indent=1))
        print(f"\nWrote {target.relative_to(_OMPHALOS_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
