"""
Stall rules replayed exactly on recorded runs — the measurement.

A stall rule (`stall.py`) decides, from the verdicts so far, whether
the next request is issued. A run it stops is a prefix of the recorded
run, so for every recorded cell the outcome under any (rule, k) is
known exactly: the spend up to the stopping proposal and whether the
winning proposal came before the stop. No API call, no Rocq.

Usage:
    # the pre-registered selection, on trainX only
    python tools/stall_report.py --tune x_train_agentic
    # apply a rule to runs (solves lost, spend saved, per-cell records)
    python tools/stall_report.py --rule samegoal --k 6 \\
        --check x_validation_agentic --check x_ladon_agentic
    # arm+stall vs baseline+stall, paired by problem × seed
    python tools/stall_report.py --rule samegoal --k 6 \\
        --pair x_validation_agentic ace_x_validation_ace_x3_offline_rv3_agentic
    # parity of a live stall arm with the replay
    python tools/stall_report.py --rule samegoal --k 6 \\
        --parity x_validation_stall_samegoal6_agentic

Reading the cache: entries are chronological; every billed request
carries `output.budget.values`; a `check_assisted` compute entry is the
verdict of the proposal that precedes it. Requests without a verdict
(tool-call rounds) are billed to the next proposal; requests after the
last verdict form a tail that any stop saves. Prices are recomputed
from token counts at today's rates (`model_registry.price_tokens`),
like every other paired readout here.
"""

# pyright: strict

import argparse
import csv
import json
import re
import statistics
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import yaml

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_OMPHALOS_DIR))
sys.path.insert(0, str(_OMPHALOS_DIR / "tools"))

import pytanque_utils as pt  # noqa: E402
from decision_audit import MIN_DISCORDANT_FOR_SIG, sign_test  # noqa: E402
from model_registry import price_tokens  # noqa: E402
from stall import K_GRID, RULES, Rule, VerdictView, stop_after  # noqa: E402
from stall import view_of_feedback  # noqa: E402

_NAME_RE = re.compile(
    r"^(?P<bench>.+?)__(?P<arm>.+?)__(?P<model>.+?)__seed(?P<seed>\d+)$"
)
_CHECK_PREFIXES = ("fun: check_assisted", "fun: check\n")
TIE = 0.02


@dataclass(frozen=True)
class Cell:
    name: str
    bench: str
    seed: str
    model: str
    prices: tuple[float, ...]
    """Spend per proposal (its request plus the tool-call requests
    before it), in order; the last entry may be a verdict-less tail."""
    views: tuple[VerdictView | None, ...]
    """One per proposal: the rejection view, or `None` for the success."""
    solved: bool

    @property
    def cell(self) -> tuple[str, str]:
        return (self.bench, self.seed)

    @property
    def total(self) -> float:
        return sum(self.prices)

    @property
    def proposals(self) -> int:
        return len(self.views)

    def under(self, rule: Rule, k: int) -> tuple[float, bool, int | None]:
        """(spend, solved, stop) under the rule — exact prefix replay."""
        rejected = [v for v in self.views if v is not None]
        stop = stop_after(rejected, rule, k)
        if stop is None:
            return self.total, self.solved, None
        # `stop` rejected verdicts = the first `stop` proposals (a success
        # can only be the last proposal).
        return sum(self.prices[:stop]), False, stop


def _load_cell(cache: Path, solved: bool) -> Cell:
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    raw: Any = yaml.load(cache.read_text(), Loader=loader)
    name = cache.parent.name
    m = _NAME_RE.match(name)
    assert m is not None, f"{name}: not a four-field cell name"
    model = m.group("model")
    prices: list[float] = []
    views: list[VerdictView | None] = []
    pending = 0.0
    for entry in cast(Sequence[Mapping[str, Any]], raw):
        request = cast(
            Mapping[str, Any],
            cast(Mapping[str, Any], entry.get("input") or {}).get("request")
            or {},
        )
        output = cast(Mapping[str, Any] | None, entry.get("output"))
        if output is None:
            continue
        budget = cast(Mapping[str, Any] | None, output.get("budget"))
        if budget is not None:
            values = cast(Mapping[str, Any], budget.get("values") or {})
            if "price" in values:
                pending += price_tokens(
                    model,
                    int(values.get("input_tokens", 0)),
                    int(values.get("cached_input_tokens", 0)),
                    int(values.get("output_tokens", 0)),
                )
            continue
        chat = cast(Sequence[Mapping[str, Any]], request.get("chat") or ())
        if not chat:
            continue
        body = str(chat[-1].get("content") or "")
        if not body.startswith(_CHECK_PREFIXES):
            continue
        outputs = cast(
            Sequence[Mapping[str, Any]], output.get("outputs") or ()
        )
        if not outputs:
            continue
        parsed: Any = yaml.load(
            str(outputs[0].get("content") or ""), Loader=loader
        )
        if not isinstance(parsed, dict):
            continue
        fb = pt.Feedback(**cast(dict[str, Any], parsed))
        prices.append(pending)
        pending = 0.0
        views.append(view_of_feedback(fb))
    if pending > 0:
        prices.append(pending)
    return Cell(
        name=name,
        bench=m.group("bench"),
        seed=m.group("seed"),
        model=model,
        prices=tuple(prices),
        views=tuple(views),
        solved=solved,
    )


def load_run(run: Path) -> dict[tuple[str, str], Cell]:
    summary = run / "results_summary.csv"
    solved: dict[str, bool] = {}
    if summary.exists():
        with summary.open() as f:
            for row in csv.DictReader(f):
                key = f"{row['bench_name']}/{row.get('seed', '')}"
                solved[key] = row["success"] == "True"
    out: dict[tuple[str, str], Cell] = {}
    for cache in sorted(run.glob("configs/*/cache.yaml")):
        m = _NAME_RE.match(cache.parent.name)
        if m is None:
            continue
        key = f"{m.group('bench')}/{m.group('seed')}"
        if key not in solved:
            # No summary row (a failed cell): solved iff result.yaml says so.
            res = cache.parent / "result.yaml"
            ok = res.exists() and "success: true" in res.read_text()[:4096]
            solved[key] = ok
        cell = _load_cell(cache, solved[key])
        out[cell.cell] = cell
    assert out, f"{run}: no cells"
    return out


#####
##### Applying a rule to a run
#####


@dataclass
class RunUnderRule:
    run: str
    rule: str
    k: int
    cells: int = 0
    solved: int = 0
    solved_under: int = 0
    spend: float = 0.0
    spend_under: float = 0.0
    unsolved_spend: float = 0.0
    unsolved_spend_under: float = 0.0
    stopped: int = 0
    lost: list[str] = field(default_factory=list[str])

    @property
    def saved(self) -> float:
        return 1 - self.spend_under / self.spend if self.spend else 0.0

    @property
    def unsolved_saved(self) -> float:
        return (
            1 - self.unsolved_spend_under / self.unsolved_spend
            if self.unsolved_spend
            else 0.0
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "run": self.run,
            "rule": self.rule,
            "k": self.k,
            "cells": self.cells,
            "solved": self.solved,
            "solvedUnder": self.solved_under,
            "spend": self.spend,
            "spendUnder": self.spend_under,
            "saved": self.saved,
            "unsolvedSaved": self.unsolved_saved,
            "stopped": self.stopped,
            "lost": self.lost,
        }


def apply_rule(
    run_name: str, cells: Mapping[tuple[str, str], Cell], rule: Rule, k: int
) -> RunUnderRule:
    r = RunUnderRule(run_name, rule, k)
    for c in cells.values():
        spend, ok, stop = c.under(rule, k)
        r.cells += 1
        r.solved += c.solved
        r.solved_under += ok
        r.spend += c.total
        r.spend_under += spend
        if not c.solved:
            r.unsolved_spend += c.total
            r.unsolved_spend_under += spend
        if stop is not None:
            r.stopped += 1
        if c.solved and not ok:
            r.lost.append(f"{c.bench}/s{c.seed}")
    return r


def grid(
    run_name: str, cells: Mapping[tuple[str, str], Cell]
) -> list[RunUnderRule]:
    return [
        apply_rule(run_name, cells, rule, k) for rule in RULES for k in K_GRID
    ]


def select(rows: Sequence[RunUnderRule]) -> RunUnderRule:
    """
    The pre-registered choice: no solve lost, then the largest spend
    saved, ties to the larger k (the more conservative rule).
    """
    ok = [r for r in rows if not r.lost]
    assert ok, "every (rule, k) loses a solve on the tuning set"
    return max(ok, key=lambda r: (r.saved, r.k))


def render_grid(rows: Sequence[RunUnderRule]) -> str:
    buf = [
        f"--- stall grid on {rows[0].run}: {rows[0].cells} cells, "
        f"{rows[0].solved} solved, spend ${rows[0].spend:.3f}",
        f"    {'rule':10}{'k':>3}{'lost':>6}{'stopped':>9}{'spend':>9}"
        f"{'saved':>8}{'unsolved saved':>16}",
    ]
    for r in rows:
        buf.append(
            f"    {r.rule:10}{r.k:3d}{len(r.lost):6d}{r.stopped:9d}"
            f"{r.spend_under:9.3f}{r.saved:8.0%}{r.unsolved_saved:16.0%}"
        )
    return "\n".join(buf)


def render_check(r: RunUnderRule) -> str:
    return (
        f"--- {r.rule} k={r.k} on {r.run}: solves {r.solved} -> "
        f"{r.solved_under} (lost {len(r.lost)}: {', '.join(r.lost) or '-'}); "
        f"stopped {r.stopped}/{r.cells} cells; spend ${r.spend:.3f} -> "
        f"${r.spend_under:.3f} (saved {r.saved:.0%}; on unsolved cells "
        f"{r.unsolved_saved:.0%})"
    )


#####
##### Pairing two runs under one rule
#####


@dataclass
class PairedUnderRule:
    base: str
    arm: str
    rule: str
    k: int
    paired: int = 0
    base_solved: int = 0
    arm_solved: int = 0
    base_only: int = 0
    arm_only: int = 0
    p_solves: float = 1.0
    base_spend: float = 0.0
    arm_spend: float = 0.0
    cheaper: int = 0
    dearer: int = 0
    p_cost: float = 1.0
    median_ratio: float = 1.0
    joint_cheaper: int = 0
    joint_dearer: int = 0
    p_joint: float = 1.0
    joint_median: float = 1.0

    def as_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)


def pair_under_rule(
    base_name: str,
    base: Mapping[tuple[str, str], Cell],
    arm_name: str,
    arm: Mapping[tuple[str, str], Cell],
    rule: Rule,
    k: int,
) -> PairedUnderRule:
    p = PairedUnderRule(base_name, arm_name, rule, k)
    ratios: list[float] = []
    joint: list[float] = []
    for key in sorted(set(base) & set(arm)):
        bs, bok, _ = base[key].under(rule, k)
        as_, aok, _ = arm[key].under(rule, k)
        p.paired += 1
        p.base_solved += bok
        p.arm_solved += aok
        if bok and not aok:
            p.base_only += 1
        if aok and not bok:
            p.arm_only += 1
        p.base_spend += bs
        p.arm_spend += as_
        if bs > 0:
            r = as_ / bs
            ratios.append(r)
            if r < 1 - TIE:
                p.cheaper += 1
            elif r > 1 + TIE:
                p.dearer += 1
            if bok and aok:
                joint.append(r)
                if r < 1 - TIE:
                    p.joint_cheaper += 1
                elif r > 1 + TIE:
                    p.joint_dearer += 1
    p.p_solves = sign_test(p.base_only, p.arm_only)
    p.p_cost = sign_test(p.dearer, p.cheaper)
    p.p_joint = sign_test(p.joint_dearer, p.joint_cheaper)
    p.median_ratio = statistics.median(ratios) if ratios else 1.0
    p.joint_median = statistics.median(joint) if joint else 1.0
    return p


def render_pair(p: PairedUnderRule) -> str:
    under = (
        "  [underpowered]"
        if p.base_only + p.arm_only < MIN_DISCORDANT_FOR_SIG
        else ""
    )
    return (
        f"--- {p.arm} vs {p.base}, both under {p.rule} k={p.k} "
        f"({p.paired} cells): solves {p.base_solved} -> {p.arm_solved} "
        f"(base-only {p.base_only}, arm-only {p.arm_only}, "
        f"p={p.p_solves:.2f}){under}; spend ${p.base_spend:.3f} -> "
        f"${p.arm_spend:.3f}, cheaper/dearer {p.cheaper}/{p.dearer} "
        f"(p={p.p_cost:.2f}, median x{p.median_ratio:.2f}); jointly "
        f"solved {p.joint_cheaper}/{p.joint_dearer} (p={p.p_joint:.2f}, "
        f"median x{p.joint_median:.2f})"
    )


#####
##### Parity of a live stall arm with the replay
#####


def parity(
    live: Mapping[tuple[str, str], Cell], rule: Rule, k: int
) -> list[str]:
    """
    For a directory produced by `prove_theorem_agentic_stall` under
    (rule, k): every cell must have issued exactly the proposals the
    replay predicts and no request after the predicted stop. Returns
    the violations (empty = parity).
    """
    bad: list[str] = []
    for c in live.values():
        rejected = [v for v in c.views if v is not None]
        stop = stop_after(rejected, rule, k)
        if stop is None:
            continue
        # The stop fires after `stop` rejections; the cell must hold
        # exactly `stop` proposals and no billed tail after the last one.
        if c.proposals != stop or len(c.prices) != stop:
            bad.append(
                f"{c.name}: replay stops after {stop} proposals, cell"
                f" holds {c.proposals} proposals / {len(c.prices)} priced"
                " blocks"
            )
    return bad


#####
##### CLI
#####


def _resolve(raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    if (_OMPHALOS_DIR / raw).exists():
        return _OMPHALOS_DIR / raw
    return _OMPHALOS_DIR / "experiments" / "output" / raw


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stall rules replayed exactly on recorded runs."
    )
    parser.add_argument("--tune", metavar="RUN")
    parser.add_argument("--rule", choices=RULES)
    parser.add_argument("--k", type=int)
    parser.add_argument("--check", action="append", default=[])
    parser.add_argument("--pair", nargs=2, action="append", default=[])
    parser.add_argument("--parity", metavar="RUN")
    parser.add_argument("--json", metavar="PATH")
    args = parser.parse_args()

    payload: dict[str, Any] = {}
    rule: Rule | None = cast(Rule | None, args.rule)
    k: int | None = args.k
    if args.tune:
        cells = load_run(_resolve(str(args.tune)))
        rows = grid(str(args.tune), cells)
        print(render_grid(rows))
        chosen = select(rows)
        print(
            f"\nSELECTED on {args.tune}: {chosen.rule} k={chosen.k} — "
            f"0 solves lost, saves {chosen.saved:.0%} of spend "
            f"({chosen.unsolved_saved:.0%} of unsolved-cell spend)"
        )
        payload["grid"] = [r.as_dict() for r in rows]
        payload["selected"] = chosen.as_dict()
        if rule is None:
            rule, k = cast(Rule, chosen.rule), chosen.k
    if args.check or args.pair or args.parity:
        assert rule is not None and k is not None, "--rule/--k or --tune"
    checks: list[dict[str, Any]] = []
    for name in cast(list[str], args.check):
        r = apply_rule(
            name, load_run(_resolve(name)), cast(Rule, rule), cast(int, k)
        )
        print(render_check(r))
        checks.append(r.as_dict())
    pairs: list[dict[str, Any]] = []
    for base_name, arm_name in cast(list[list[str]], args.pair):
        p = pair_under_rule(
            base_name,
            load_run(_resolve(base_name)),
            arm_name,
            load_run(_resolve(arm_name)),
            cast(Rule, rule),
            cast(int, k),
        )
        print(render_pair(p))
        pairs.append(p.as_dict())
    if args.parity:
        bad = parity(
            load_run(_resolve(str(args.parity))),
            cast(Rule, rule),
            cast(int, k),
        )
        if bad:
            print(f"PARITY FAILED ({len(bad)} cell(s)):")
            for b in bad:
                print(f"  {b}")
        else:
            print(
                f"parity OK: {args.parity} stops exactly where the replay does"
            )
        payload["parity"] = bad
    if checks:
        payload["checks"] = checks
    if pairs:
        payload["pairs"] = pairs
    if args.json:
        target = Path(str(args.json))
        if not target.is_absolute():
            target = _OMPHALOS_DIR / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=1))
        print(f"\nWrote {target}")
    return 1 if payload.get("parity") else 0


if __name__ == "__main__":
    raise SystemExit(main())
