"""
Where a playbook's effect goes: turn tax, per-request tax, citations.

Three ACE generations moved the failure taxonomy without moving the
solve count (PROGRESS 2026-08-27, 2026-09-02). This tool reads the
recorded cells of a baseline and of any number of playbook arms and
answers, offline and exactly, the questions that explain that:

1. **Turn profile** (`--baseline`, per arm): which error classes the
   prover pays for on the cells it *solves* (the turn tax — every
   failed verdict before the winning proposal) versus which classes a
   cell *dies* on (the terminal and last-five verdicts of unsolved
   cells); the class of the first error of each cell (the only error a
   system-prompt playbook can prevent); and the share of failed
   verdicts that repeat a class already seen in the same cell (what an
   error-keyed hint could still prevent). Classes use
   `failure_analysis.refine_class`, which splits `other`.
2. **Paired cost** (each arm against the baseline, by problem × seed):
   the paired solves sign test; on jointly solved cells the paired
   requests and the paired spend (2 % tie band, median ratio); and the
   per-request decomposition — uncached input, cached input and output
   tokens per request, priced with `model_registry.pricing_for` — that
   says whether an arm saves turns, pays more per turn, or both.
3. **Citation audit** (per arm): every `rocq-NNNNN` id the generator
   wrote in a message, paired with the verdict that followed; per
   bullet, how often it was cited, how often the next verdict still
   failed, and the cells where it was cited on five or more failing
   turns in a row — the evaluation-side harmful-bullet signal of HINTS
   #67(b), which the adaptation-time counters cannot see.
4. **Trigger coverage** (`--triggers`): with a trigger table
   (`ace_triggers`), which failed verdicts of the baseline each bullet
   would have fired on, and which classes no bullet reaches.

Spend is recomputed from token counts (never the archived `price`);
every number is regenerable, `--json` writes them all.

Usage:
    python -m tools.analysis.ace_diagnosis \\
        --baseline experiments/output/x_validation_agentic \\
        --arm experiments/output/ace_x_validation_ace_x5_offline_rv3_agentic \\
        [--arm ...] [--triggers experiments/playbooks/<t>.yaml] [--json out]
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import yaml


from ace.ace_evidence import unknown_identifier  # noqa: E402
from tools.analysis.cell_records import CellRecord, cells_of_run  # noqa: E402
from tools.analysis.decision_audit import MIN_DISCORDANT_FOR_SIG, sign_test  # noqa: E402
from tools.analysis.failure_analysis import (  # noqa: E402
    Verdict,
    load_run,
    refine_class,
)
from runtime.model_registry import pricing_for  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT

TIE = 0.02
"""Relative band inside which two spends count as a tie (as in
`tools/reports/ace_report.py`)."""

PERSISTENT_CITATION = 5
"""A bullet cited on this many consecutive failing turns of one cell is
reported as persistently cited — the `mathd_numbertheory_405` shape."""

_CITE_RE = re.compile(r"rocq-\d{5}")
_CHECK_PREFIXES = ("fun: check_assisted", "fun: check\n", "fun: checked_proof")


#####
##### 1. Turn profile
#####


def cells_of(verdicts: Sequence[Verdict]) -> dict[str, list[Verdict]]:
    """Verdicts grouped by cell, in cache (chronological) order."""
    out: dict[str, list[Verdict]] = defaultdict(list)
    for v in verdicts:
        out[v.config].append(v)
    return dict(out)


@dataclass
class TurnProfile:
    cells: int = 0
    solved_cells: int = 0
    first_try_solves: int = 0
    tax_by_class: Counter[str] = field(default_factory=Counter[str])
    """Failed verdicts on solved cells, by class (the turn tax)."""
    unsolved_by_class: Counter[str] = field(default_factory=Counter[str])
    last5_by_class: Counter[str] = field(default_factory=Counter[str])
    terminal_by_class: Counter[str] = field(default_factory=Counter[str])
    first_error_by_class: Counter[str] = field(default_factory=Counter[str])
    failed_verdicts: int = 0
    repeats_of_class: int = 0
    failed_on_solved: int = 0
    repeats_on_solved: int = 0
    repeats_of_name: int = 0
    heaviest_solved: list[tuple[int, str]] = field(
        default_factory=list[tuple[int, str]]
    )
    """(failed verdicts before the solve, cell) — the ten worst."""

    @property
    def tax_total(self) -> int:
        return sum(self.tax_by_class.values())

    def as_dict(self) -> dict[str, Any]:
        return {
            "cells": self.cells,
            "solvedCells": self.solved_cells,
            "firstTrySolves": self.first_try_solves,
            "taxByClass": dict(self.tax_by_class.most_common()),
            "taxTotal": self.tax_total,
            "unsolvedByClass": dict(self.unsolved_by_class.most_common()),
            "last5ByClass": dict(self.last5_by_class.most_common()),
            "terminalByClass": dict(self.terminal_by_class.most_common()),
            "firstErrorByClass": dict(self.first_error_by_class.most_common()),
            "failedVerdicts": self.failed_verdicts,
            "repeatsOfClass": self.repeats_of_class,
            "failedOnSolved": self.failed_on_solved,
            "repeatsOnSolved": self.repeats_on_solved,
            "repeatsOfName": self.repeats_of_name,
            "heaviestSolved": self.heaviest_solved,
        }


def turn_profile(verdicts: Sequence[Verdict]) -> TurnProfile:
    p = TurnProfile()
    burned: list[tuple[int, str]] = []
    for cell, seq in cells_of(verdicts).items():
        p.cells += 1
        fails = [v for v in seq if not v.success]
        solved = seq[0].solved_run
        if solved:
            p.solved_cells += 1
            if not fails:
                p.first_try_solves += 1
            burned.append((len(fails), cell))
        if fails:
            p.first_error_by_class[fails[0].fine_class] += 1
        seen_cls: set[str] = set()
        seen_name: set[str] = set()
        for v in fails:
            cls = v.fine_class
            name = unknown_identifier(v.error_message or "")
            p.failed_verdicts += 1
            repeat = cls in seen_cls
            if repeat:
                p.repeats_of_class += 1
            if name is not None and name in seen_name:
                p.repeats_of_name += 1
            if solved:
                p.tax_by_class[cls] += 1
                p.failed_on_solved += 1
                if repeat:
                    p.repeats_on_solved += 1
            else:
                p.unsolved_by_class[cls] += 1
            seen_cls.add(cls)
            if name is not None:
                seen_name.add(name)
        if not solved and fails:
            for v in fails[-5:]:
                p.last5_by_class[v.fine_class] += 1
            p.terminal_by_class[fails[-1].fine_class] += 1
    p.heaviest_solved = sorted(burned, reverse=True)[:10]
    return p


#####
##### 2. Paired cost
#####


@dataclass(frozen=True)
class Rates:
    input: float
    cached: float
    output: float

    @staticmethod
    def of(model: str) -> "Rates":
        r = pricing_for(model)
        return Rates(
            r.dollars_per_input_token,
            r.dollars_per_cached_input_token,
            r.dollars_per_output_token,
        )


@dataclass(frozen=True)
class PerRequest:
    """Pooled per-request token and dollar figures over a set of cells."""

    requests: int
    uncached: float
    cached: float
    output: float
    usd_uncached: float
    usd_cached: float
    usd_output: float

    @property
    def usd(self) -> float:
        return self.usd_uncached + self.usd_cached + self.usd_output

    def as_dict(self) -> dict[str, float]:
        return {
            "requests": self.requests,
            "uncachedPerReq": self.uncached,
            "cachedPerReq": self.cached,
            "outputPerReq": self.output,
            "usdPerReq": self.usd,
            "usdUncachedPerReq": self.usd_uncached,
            "usdCachedPerReq": self.usd_cached,
            "usdOutputPerReq": self.usd_output,
        }


def per_request(cells: Iterable[CellRecord]) -> PerRequest:
    n = inp = cch = out = 0
    usd_u = usd_c = usd_o = 0.0
    for c in cells:
        r = Rates.of(c.model)
        n += c.requests
        inp += c.input
        cch += c.cached
        out += c.output
        usd_u += (c.input - c.cached) * r.input
        usd_c += c.cached * r.cached
        usd_o += c.output * r.output
    if n == 0:
        return PerRequest(0, 0, 0, 0, 0, 0, 0)
    return PerRequest(
        n,
        (inp - cch) / n,
        cch / n,
        out / n,
        usd_u / n,
        usd_c / n,
        usd_o / n,
    )


@dataclass
class PairedCost:
    arm: str
    paired_cells: int
    base_solved: int
    arm_solved: int
    base_only: list[str]
    arm_only: list[str]
    p_solves: float
    joint_solved: int
    base_requests: int
    arm_requests: int
    fewer_requests: int
    more_requests: int
    cheaper: int
    dearer: int
    p_cost: float
    median_ratio: float
    base_per_request: PerRequest
    arm_per_request: PerRequest
    cheaper_per_request: int
    dearer_per_request: int
    p_per_request: float
    joint_failed: int
    base_failed_cost: float
    arm_failed_cost: float
    base_first_try: int
    arm_first_try: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "pairedCells": self.paired_cells,
            "baseSolved": self.base_solved,
            "armSolved": self.arm_solved,
            "baseOnly": self.base_only,
            "armOnly": self.arm_only,
            "pSolves": self.p_solves,
            "jointSolved": self.joint_solved,
            "baseRequests": self.base_requests,
            "armRequests": self.arm_requests,
            "fewerRequests": self.fewer_requests,
            "moreRequests": self.more_requests,
            "cheaper": self.cheaper,
            "dearer": self.dearer,
            "pCost": self.p_cost,
            "medianRatio": self.median_ratio,
            "basePerRequest": self.base_per_request.as_dict(),
            "armPerRequest": self.arm_per_request.as_dict(),
            "cheaperPerRequest": self.cheaper_per_request,
            "dearerPerRequest": self.dearer_per_request,
            "pPerRequest": self.p_per_request,
            "jointFailed": self.joint_failed,
            "baseFailedCost": self.base_failed_cost,
            "armFailedCost": self.arm_failed_cost,
            "baseFirstTry": self.base_first_try,
            "armFirstTry": self.arm_first_try,
        }


def _records(run: Path) -> dict[tuple[str, str], CellRecord]:
    out: dict[tuple[str, str], CellRecord] = {}
    for rec in cells_of_run(run):
        assert rec.cell not in out, (
            f"{run.name}: two arms in one directory ({rec.name}); the "
            "diagnosis pairs one arm per directory"
        )
        out[rec.cell] = rec
    assert out, f"{run}: no cells (is experiment.yaml there?)"
    return out


def paired_cost(base_run: Path, arm_run: Path) -> PairedCost:
    base = _records(base_run)
    arm = _records(arm_run)
    keys = sorted(set(base) & set(arm))
    base_only = [
        f"{b}/s{s}"
        for b, s in keys
        if base[(b, s)].solved and not arm[(b, s)].solved
    ]
    arm_only = [
        f"{b}/s{s}"
        for b, s in keys
        if arm[(b, s)].solved and not base[(b, s)].solved
    ]
    joint = [k for k in keys if base[k].solved and arm[k].solved]
    joint_failed = [
        k for k in keys if not base[k].solved and not arm[k].solved
    ]
    cheaper = dearer = 0
    ratios: list[float] = []
    fewer = more = 0
    cheaper_pr = dearer_pr = 0
    for k in joint:
        b, a = base[k], arm[k]
        if b.cost > 0:
            ratios.append(a.cost / b.cost)
            if a.cost < b.cost * (1 - TIE):
                cheaper += 1
            elif a.cost > b.cost * (1 + TIE):
                dearer += 1
        if a.requests < b.requests:
            fewer += 1
        elif a.requests > b.requests:
            more += 1
        if b.requests and a.requests:
            bpr, apr = b.cost / b.requests, a.cost / a.requests
            if apr < bpr * (1 - TIE):
                cheaper_pr += 1
            elif apr > bpr * (1 + TIE):
                dearer_pr += 1
    return PairedCost(
        arm=arm_run.name,
        paired_cells=len(keys),
        base_solved=sum(1 for k in keys if base[k].solved),
        arm_solved=sum(1 for k in keys if arm[k].solved),
        base_only=base_only,
        arm_only=arm_only,
        p_solves=sign_test(len(base_only), len(arm_only)),
        joint_solved=len(joint),
        base_requests=sum(base[k].requests for k in joint),
        arm_requests=sum(arm[k].requests for k in joint),
        fewer_requests=fewer,
        more_requests=more,
        cheaper=cheaper,
        dearer=dearer,
        p_cost=sign_test(dearer, cheaper),
        median_ratio=statistics.median(ratios) if ratios else 1.0,
        base_per_request=per_request(base[k] for k in joint),
        arm_per_request=per_request(arm[k] for k in joint),
        cheaper_per_request=cheaper_pr,
        dearer_per_request=dearer_pr,
        p_per_request=sign_test(dearer_pr, cheaper_pr),
        joint_failed=len(joint_failed),
        base_failed_cost=sum(base[k].cost for k in joint_failed),
        arm_failed_cost=sum(arm[k].cost for k in joint_failed),
        base_first_try=sum(
            1 for k in keys if base[k].solved and base[k].requests <= 1
        ),
        arm_first_try=sum(
            1 for k in keys if arm[k].solved and arm[k].requests <= 1
        ),
    )


#####
##### 3. Citation audit
#####


@dataclass(frozen=True)
class Turn:
    """One generator message and the verdict that followed it, if any."""

    cited: tuple[str, ...]
    verdict_class: str | None
    """`None` when the message was a tool call (no verdict followed)."""
    success: bool


def turns_of_cache(cache: Path) -> list[Turn]:
    from tools.data.ace_review_benchmark import assert_training_allowed

    assert_training_allowed([cache.parent.name.split("__")[0]])
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    raw: Any = yaml.load(cache.read_text(), Loader=loader)
    turns: list[Turn] = []
    pending: tuple[str, ...] | None = None
    for entry in cast(Sequence[Mapping[str, Any]], raw):
        request = cast(
            Mapping[str, Any],
            cast(Mapping[str, Any], entry.get("input") or {}).get("request")
            or {},
        )
        options = cast(Mapping[str, Any], request.get("options") or {})
        chat = cast(Sequence[Mapping[str, Any]], request.get("chat") or ())
        output = cast(Mapping[str, Any] | None, entry.get("output"))
        if output is None or not chat:
            continue
        outputs = cast(
            Sequence[Mapping[str, Any]], output.get("outputs") or ()
        )
        if not outputs:
            continue
        content = str(outputs[0].get("content") or "")
        if options.get("model") != "__compute__":
            if pending is not None:
                turns.append(Turn(pending, None, False))
            pending = tuple(sorted(set(_CITE_RE.findall(content))))
            continue
        body = str(chat[-1].get("content") or "")
        if not body.startswith(_CHECK_PREFIXES):
            continue
        parsed: Any = yaml.load(content, Loader=loader)
        if not isinstance(parsed, dict):
            continue
        record = cast(dict[str, Any], parsed)
        fb = cast(dict[str, Any], record.get("feedback", record))
        success = bool(fb.get("success"))
        cls = (
            None
            if success
            else refine_class(cast(str | None, fb.get("error_message")))
        )
        turns.append(Turn(pending or (), cls, success))
        pending = None
    if pending is not None:
        turns.append(Turn(pending, None, False))
    return turns


@dataclass
class BulletUse:
    cited: int = 0
    proposals: int = 0
    """Citations on a message that was a proposal (a verdict followed)."""
    failed_after: int = 0
    solved_after: int = 0
    cells: set[str] = field(default_factory=set[str])
    persistent_cells: set[str] = field(default_factory=set[str])

    def as_dict(self) -> dict[str, Any]:
        return {
            "cited": self.cited,
            "proposals": self.proposals,
            "failedAfter": self.failed_after,
            "solvedAfter": self.solved_after,
            "cells": len(self.cells),
            "persistentCells": sorted(self.persistent_cells),
        }


@dataclass
class CitationAudit:
    arm: str
    cells: int = 0
    cells_citing: int = 0
    messages: int = 0
    messages_citing: int = 0
    proposals: int = 0
    proposals_citing: int = 0
    failed_after_citing: int = 0
    failed_after_silent: int = 0
    proposals_silent: int = 0
    bullets: dict[str, BulletUse] = field(
        default_factory=lambda: defaultdict(BulletUse)
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "cells": self.cells,
            "cellsCiting": self.cells_citing,
            "messages": self.messages,
            "messagesCiting": self.messages_citing,
            "proposals": self.proposals,
            "proposalsCiting": self.proposals_citing,
            "failedAfterCiting": self.failed_after_citing,
            "proposalsSilent": self.proposals_silent,
            "failedAfterSilent": self.failed_after_silent,
            "bullets": {
                k: v.as_dict()
                for k, v in sorted(
                    self.bullets.items(), key=lambda kv: -kv[1].cited
                )
            },
        }


def citation_audit(run: Path) -> CitationAudit:
    audit = CitationAudit(arm=run.name)
    for cache in sorted(run.glob("configs/*/cache.yaml")):
        cell = cache.parent.name
        turns = turns_of_cache(cache)
        audit.cells += 1
        if any(t.cited for t in turns):
            audit.cells_citing += 1
        streak: Counter[str] = Counter()
        for t in turns:
            audit.messages += 1
            if t.cited:
                audit.messages_citing += 1
            is_proposal = t.verdict_class is not None or t.success
            if is_proposal:
                audit.proposals += 1
                if t.cited:
                    audit.proposals_citing += 1
                    if not t.success:
                        audit.failed_after_citing += 1
                else:
                    audit.proposals_silent += 1
                    if not t.success:
                        audit.failed_after_silent += 1
            for bid in t.cited:
                use = audit.bullets[bid]
                use.cited += 1
                use.cells.add(cell)
                if is_proposal:
                    use.proposals += 1
                    if t.success:
                        use.solved_after += 1
                    else:
                        use.failed_after += 1
            if is_proposal and not t.success:
                for bid in t.cited:
                    streak[bid] += 1
                    if streak[bid] >= PERSISTENT_CITATION:
                        audit.bullets[bid].persistent_cells.add(cell)
                for bid in list(streak):
                    if bid not in t.cited:
                        del streak[bid]
            elif is_proposal:
                streak.clear()
    return audit


#####
##### 3b. Hint audit (hint-on-error arms)
#####


_HINT_MARK = "**Playbook advice for this error**"


@dataclass(frozen=True)
class Transition:
    """A rejection, the hints its feedback carried, and what came next."""

    cell: str
    cls: str
    hints: tuple[str, ...]
    next_cls: str | None
    """Class of the next verdict; `None` = solved (or no next verdict)."""
    next_success: bool


def transitions_of_cache(cache: Path) -> list[Transition]:
    """
    Walk a cell: verdict → feedback message (with or without hints) →
    next verdict. Tool-call rounds between them are skipped; the
    feedback for verdict t is the last user/tool message of the next
    generator request.
    """
    from tools.data.ace_review_benchmark import assert_training_allowed

    assert_training_allowed([cache.parent.name.split("__")[0]])
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    raw: Any = yaml.load(cache.read_text(), Loader=loader)
    events: list[tuple[str, Any]] = []
    for entry in cast(Sequence[Mapping[str, Any]], raw):
        request = cast(
            Mapping[str, Any],
            cast(Mapping[str, Any], entry.get("input") or {}).get("request")
            or {},
        )
        options = cast(Mapping[str, Any], request.get("options") or {})
        chat = cast(Sequence[Mapping[str, Any]], request.get("chat") or ())
        output = cast(Mapping[str, Any] | None, entry.get("output"))
        if output is None or not chat:
            continue
        outputs = cast(
            Sequence[Mapping[str, Any]], output.get("outputs") or ()
        )
        if not outputs:
            continue
        if options.get("model") != "__compute__":
            last = str(chat[-1].get("content") or "")
            if _HINT_MARK in last:
                ids = tuple(
                    dict.fromkeys(
                        _CITE_RE.findall(last[last.index(_HINT_MARK) :])
                    )
                )
                events.append(("feedback", ids))
            elif "Rocq error" in last or "Remaining goals" in last:
                events.append(("feedback", ()))
            continue
        body = str(chat[-1].get("content") or "")
        if not body.startswith(_CHECK_PREFIXES):
            continue
        parsed: Any = yaml.load(
            str(outputs[0].get("content") or ""), Loader=loader
        )
        if not isinstance(parsed, dict):
            continue
        record = cast(dict[str, Any], parsed)
        fb = cast(dict[str, Any], record.get("feedback", record))
        if fb.get("success"):
            events.append(("verdict", None))
        else:
            events.append(
                (
                    "verdict",
                    refine_class(cast(str | None, fb.get("error_message"))),
                )
            )
    out: list[Transition] = []
    cell = cache.parent.name
    i = 0
    while i < len(events):
        kind, val = events[i]
        if kind == "verdict" and val is not None:
            hints: tuple[str, ...] = ()
            j = i + 1
            if j < len(events) and events[j][0] == "feedback":
                hints = cast(tuple[str, ...], events[j][1])
                j += 1
            while j < len(events) and events[j][0] != "verdict":
                j += 1
            if j < len(events):
                nxt = cast(str | None, events[j][1])
                out.append(Transition(cell, str(val), hints, nxt, nxt is None))
            else:
                out.append(Transition(cell, str(val), hints, str(val), False))
        i += 1
    return out


@dataclass
class HintAudit:
    arm: str
    transitions: int = 0
    hinted: int = 0
    hinted_repeat: int = 0
    hinted_success: int = 0
    silent: int = 0
    silent_repeat: int = 0
    silent_success: int = 0
    cells_hinted: set[str] = field(default_factory=set[str])
    by_bullet: dict[str, tuple[int, int, int]] = field(
        default_factory=dict[str, tuple[int, int, int]]
    )
    """id -> (fired, next verdict repeats the class, next solves)."""
    by_class: dict[str, tuple[int, int, int, int]] = field(
        default_factory=dict[str, tuple[int, int, int, int]]
    )
    """class -> (hinted, hinted repeats, silent, silent repeats)."""

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "transitions": self.transitions,
            "hinted": self.hinted,
            "hintedRepeat": self.hinted_repeat,
            "hintedSuccess": self.hinted_success,
            "silent": self.silent,
            "silentRepeat": self.silent_repeat,
            "silentSuccess": self.silent_success,
            "cellsHinted": len(self.cells_hinted),
            "byBullet": {k: list(v) for k, v in self.by_bullet.items()},
            "byClass": {k: list(v) for k, v in self.by_class.items()},
        }


def hint_audit(run: Path) -> HintAudit:
    a = HintAudit(arm=run.name)
    bullet: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    cls: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    for cache in sorted(run.glob("configs/*/cache.yaml")):
        for t in transitions_of_cache(cache):
            a.transitions += 1
            repeat = t.next_cls == t.cls
            if t.hints:
                a.hinted += 1
                a.hinted_repeat += repeat
                a.hinted_success += t.next_success
                a.cells_hinted.add(t.cell)
                cls[t.cls][0] += 1
                cls[t.cls][1] += repeat
                for h in t.hints:
                    bullet[h][0] += 1
                    bullet[h][1] += repeat
                    bullet[h][2] += t.next_success
            else:
                a.silent += 1
                a.silent_repeat += repeat
                a.silent_success += t.next_success
                cls[t.cls][2] += 1
                cls[t.cls][3] += repeat
    a.by_bullet = {
        k: (v[0], v[1], v[2])
        for k, v in sorted(bullet.items(), key=lambda kv: -kv[1][0])
    }
    a.by_class = {
        k: (v[0], v[1], v[2], v[3])
        for k, v in sorted(cls.items(), key=lambda kv: -(kv[1][0] + kv[1][2]))
    }
    return a


def render_hint_audit(a: HintAudit) -> str:
    def rate(n: int, d: int) -> str:
        return f"{n}/{d} ({n / d:.0%})" if d else "-"

    buf = [
        f"--- hints: {a.arm}",
        f"    {a.transitions} rejections in {a.cells_hinted and len(a.cells_hinted)} hinted cells + others;"
        f" hinted {a.hinted}: next verdict repeats the class {rate(a.hinted_repeat, a.hinted)},"
        f" next proposal solves {rate(a.hinted_success, a.hinted)};"
        f" silent {a.silent}: repeats {rate(a.silent_repeat, a.silent)},"
        f" solves {rate(a.silent_success, a.silent)}",
        f"    {'class':24}{'hinted':>7}{'repeat':>7}{'silent':>7}{'repeat':>7}",
        *[
            f"    {c:24}{h:7d}{hr:7d}{s:7d}{sr:7d}"
            for c, (h, hr, s, sr) in a.by_class.items()
        ],
        f"    {'bullet':12}{'fired':>6}{'repeat':>7}{'solve':>6}",
        *[
            f"    {b:12}{f:6d}{r:7d}{sv:6d}"
            for b, (f, r, sv) in a.by_bullet.items()
        ],
    ]
    return "\n".join(buf)


#####
##### 4. Trigger coverage
#####


def trigger_coverage(baseline: Path, triggers_path: Path) -> dict[str, Any]:
    """Which baseline failures each bullet would have fired on
    (`ace_triggers.coverage`, with the recorded goals)."""
    from ace.ace_triggers import TriggerTable, coverage

    table = TriggerTable.load(triggers_path)
    cov = coverage(table, [baseline])
    return {
        "triggers": str(triggers_path),
        "report": cov.render(),
        **cov.as_dict(),
    }


#####
##### Rendering
#####


def _counter_lines(c: Counter[str], total: int, width: int = 24) -> list[str]:
    return [
        f"      {k:{width}}{n:5d}  ({n / total:4.0%})"
        if total
        else f"      {k:{width}}{n:5d}"
        for k, n in c.most_common()
    ]


def render_profile(name: str, p: TurnProfile) -> str:
    buf = [
        f"--- turn profile: {name}",
        f"    {p.cells} cells, {p.solved_cells} solved "
        f"({p.first_try_solves} first-try); failed verdicts "
        f"{p.failed_verdicts}, repeats of a class already seen in the "
        f"cell {p.repeats_of_class} "
        f"({p.repeats_of_class / max(p.failed_verdicts, 1):.0%}), "
        f"repeats of the same unknown name {p.repeats_of_name}",
        f"    turn tax on solved cells: {p.tax_total} failed verdicts "
        f"({p.repeats_on_solved} repeats, "
        f"{p.repeats_on_solved / max(p.failed_on_solved, 1):.0%})",
        *_counter_lines(p.tax_by_class, p.tax_total),
        "    terminal class of unsolved cells:",
        *_counter_lines(
            p.terminal_by_class, sum(p.terminal_by_class.values())
        ),
        "    last five verdicts of unsolved cells:",
        *_counter_lines(p.last5_by_class, sum(p.last5_by_class.values())),
        "    first error of a cell:",
        *_counter_lines(
            p.first_error_by_class, sum(p.first_error_by_class.values())
        ),
        "    heaviest solved cells (failed verdicts before the solve):",
        *[f"      {n:3d}  {cell}" for n, cell in p.heaviest_solved[:6]],
    ]
    return "\n".join(buf)


def _m(x: float) -> str:
    return f"{x * 1000:.2f}m$"


def render_cost(pc: PairedCost) -> str:
    under = (
        f"  [underpowered: fewer than {MIN_DISCORDANT_FOR_SIG} discordant]"
        if len(pc.base_only) + len(pc.arm_only) < MIN_DISCORDANT_FOR_SIG
        else ""
    )
    b, a = pc.base_per_request, pc.arm_per_request
    return "\n".join(
        [
            f"--- paired against baseline: {pc.arm}",
            f"    solves {pc.base_solved} -> {pc.arm_solved} on "
            f"{pc.paired_cells} cells; base-only {len(pc.base_only)}, "
            f"arm-only {len(pc.arm_only)}, p={pc.p_solves:.2f}{under}",
            f"      base-only: {', '.join(pc.base_only) or '-'}",
            f"      arm-only : {', '.join(pc.arm_only) or '-'}",
            f"    first-try solves {pc.base_first_try} -> {pc.arm_first_try}",
            f"    jointly solved {pc.joint_solved}: requests "
            f"{pc.base_requests} -> {pc.arm_requests} (fewer/more "
            f"{pc.fewer_requests}/{pc.more_requests}); spend "
            f"cheaper/dearer {pc.cheaper}/{pc.dearer}, p={pc.p_cost:.2f}, "
            f"median ratio x{pc.median_ratio:.2f}",
            "    per request on jointly solved cells (pooled):",
            f"      base: {_m(b.usd)} = uncached {b.uncached:6.0f} tok "
            f"({_m(b.usd_uncached)}) + cached {b.cached:6.0f} tok "
            f"({_m(b.usd_cached)}) + output {b.output:5.0f} tok "
            f"({_m(b.usd_output)})",
            f"      arm : {_m(a.usd)} = uncached {a.uncached:6.0f} tok "
            f"({_m(a.usd_uncached)}) + cached {a.cached:6.0f} tok "
            f"({_m(a.usd_cached)}) + output {a.output:5.0f} tok "
            f"({_m(a.usd_output)})",
            f"      per-request spend cheaper/dearer "
            f"{pc.cheaper_per_request}/{pc.dearer_per_request}, "
            f"p={pc.p_per_request:.2f}",
            f"    jointly failed {pc.joint_failed}: spend "
            f"${pc.base_failed_cost:.3f} -> ${pc.arm_failed_cost:.3f}",
        ]
    )


def render_citations(c: CitationAudit) -> str:
    buf = [
        f"--- citations: {c.arm}",
        f"    {c.cells_citing}/{c.cells} cells cite a bullet; "
        f"{c.messages_citing}/{c.messages} messages; "
        f"{c.proposals_citing}/{c.proposals} proposals cite "
        f"(failed after citing {c.failed_after_citing}"
        f"/{c.proposals_citing}; failed after a silent proposal "
        f"{c.failed_after_silent}/{c.proposals_silent})",
        f"    {'bullet':12}{'cited':>6}{'props':>6}{'fail':>6}{'solve':>6}"
        f"{'cells':>6}  persistent (>= {PERSISTENT_CITATION} failing turns)",
    ]
    for bid, u in sorted(c.bullets.items(), key=lambda kv: -kv[1].cited):
        buf.append(
            f"    {bid:12}{u.cited:6d}{u.proposals:6d}{u.failed_after:6d}"
            f"{u.solved_after:6d}{len(u.cells):6d}  "
            f"{', '.join(sorted(u.persistent_cells)) or '-'}"
        )
    return "\n".join(buf)


def render_coverage(cov: Mapping[str, Any]) -> str:
    return (
        f"--- trigger coverage of the baseline's failures: {cov['triggers']}\n"
        + str(cov["report"])
    )


#####
##### CLI
#####


def _resolve(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else _OMPHALOS_DIR / p


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Explain where a playbook's effect goes: turn tax by class, "
            "paired requests and per-request spend, citations, trigger "
            "coverage. Offline; no API calls."
        )
    )
    parser.add_argument("--baseline", required=True, help="baseline run")
    parser.add_argument(
        "--arm", action="append", default=[], help="playbook arm run(s)"
    )
    parser.add_argument("--triggers", help="trigger table (ace_triggers)")
    parser.add_argument("--json", metavar="PATH")
    parser.add_argument(
        "--no-citations", action="store_true", help="skip the cache walk"
    )
    parser.add_argument(
        "--hints",
        action="store_true",
        help="audit hint-on-error feedback (triggered arms)",
    )
    args = parser.parse_args()

    base = _resolve(str(args.baseline))
    arms = [_resolve(a) for a in cast(list[str], args.arm)]
    base_verdicts = load_run(base)
    payload: dict[str, Any] = {"baseline": base.name, "arms": {}}

    print("=" * 74)
    print("OMPHALOS ACE DIAGNOSIS")
    print("=" * 74)
    print()
    bp = turn_profile(base_verdicts)
    payload["baselineProfile"] = bp.as_dict()
    print(render_profile(base.name, bp))
    for arm in arms:
        print()
        verdicts = load_run(arm)
        prof = turn_profile(verdicts)
        cost = paired_cost(base, arm)
        entry: dict[str, Any] = {
            "profile": prof.as_dict(),
            "paired": cost.as_dict(),
        }
        print(render_profile(arm.name, prof))
        print()
        print(render_cost(cost))
        if not args.no_citations:
            cit = citation_audit(arm)
            entry["citations"] = cit.as_dict()
            print()
            print(render_citations(cit))
        if args.hints:
            ha = hint_audit(arm)
            entry["hints"] = ha.as_dict()
            print()
            print(render_hint_audit(ha))
        payload["arms"][arm.name] = entry
    if args.triggers:
        cov = trigger_coverage(base, _resolve(str(args.triggers)))
        payload["coverage"] = cov
        print()
        print(render_coverage(cov))
    if args.json:
        target = _resolve(str(args.json))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, indent=1))
        print(f"\nWrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
