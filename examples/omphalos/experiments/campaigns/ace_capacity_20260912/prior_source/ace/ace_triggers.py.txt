"""
Error-keyed playbook injection ("hint on error").

The ACE study's diagnosis (PROGRESS 2026-09-05, `tools/analysis/ace_diagnosis.py`)
found that a playbook rendered into the system prompt saves turns on
the cells the prover solves and loses more than that on the price of
every request: each bullet is resent on every turn of every cell,
including the ~40 % of cells that solve on the first proposal and the
turns whose error no bullet addresses, and the citation ask adds
output tokens on top. This module is the alternative delivery: the
playbook stays out of the prompt, and when the verifier rejects a
proposal, the bullets whose *trigger* matches that rejection are
attached to the feedback message — at most `k`, ranked by how
specifically they match.

A trigger is a small, deterministic matcher per bullet:

- `classes` — failure classes of `tools/analysis/failure_analysis.py`'s
  taxonomy (coarse or fine); a match scores 1.
- `names` — identifiers Rocq reported as not found (`unknown-reference`
  errors only); a match scores 3.
- `patterns` — case-insensitive regular expressions searched in the
  error message and the failing tactic; a match scores 2.
- `goal_patterns` — regular expressions searched in the remaining
  goals. A goal shape never summons a bullet on its own; when a bullet
  carries goal patterns they are a *precondition* (the goal must match,
  or the bullet stays silent — unless one of its `names` matched, which
  is specific enough by itself) and a match adds 1. Measured on the
  trainX verdicts before the first paid cell: read as a mere tie-break,
  the x5 table's four class-keyed bullets rode along on 120 verdicts
  each; read as a precondition, they fire where their goal shape
  occurs (`INR`, `sqrt`, `Ensemble`, …) and 37 % of failed verdicts
  get a hint.

Triggers are written once per frozen playbook by an LLM
(`prove_ace.AssignTriggers`, `experiments/ace/ace_triggers_experiment.py`),
validated against the recorded trainX verdicts (`coverage`: every
regex compiles, every id exists, and the table reports which bullets
never fire), and frozen next to the playbook as a self-contained YAML
(`<playbook stem>.triggers.yaml`, contents included) whose sha256 is
part of every evaluation cell's identity. Selection at evaluation time
is pure Python over the cached verifier verdict — no LLM call, no
extra `compute`, replayable.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import hashlib
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

import yaml


from ace.ace_evidence import unknown_identifier  # noqa: E402
from ace.ace_playbook import Playbook  # noqa: E402
from tools.analysis.failure_analysis import (  # noqa: E402
    FINE_TAXONOMY,
    NEVER_PROPOSED,
    TAXONOMY,
    UNCLASSIFIED,
    _feedback_entries,  # pyright: ignore[reportPrivateUsage]
    classify,
    refine_class,
)

_OMPHALOS_DIR = OMPHALOS_ROOT

DEFAULT_MAX_HINTS = 3
"""Bullets attached to one feedback message, at most."""

MAX_PATTERN_LENGTH = 120
"""A longer regex is almost certainly a pasted error message, not a
matcher; the table refuses it."""

SCORE_NAME = 3
SCORE_PATTERN = 2
SCORE_CLASS = 1
SCORE_GOAL = 1

DEFAULT_SELECTION_RULE = 1
"""
Which `score` semantics a cell runs under; part of every triggered
cell's identity (`ACETriggeredConfig.selection_rule`), so a rule
change can never re-read a recorded table into a different prompt.

1 (2026-09-05, the x5 arm): goal patterns are a precondition when
  present; a pattern or a class match alone can fire.
2 (2026-09-05 evening, after the x6 coverage): classes are *also* a
  precondition when listed — a pattern discriminates within the
  bullet's classes instead of summoning it on any rejection whose
  failing tactic happens to match (the x6 `assert … by` syntax bullet
  fired on 192 trainX rejections of every class under rule 1, 153 of
  them not syntax errors). A name match still bypasses both.
"""

KNOWN_CLASSES: frozenset[str] = frozenset(
    [c.label for c in TAXONOMY]
    + [c.label for c in FINE_TAXONOMY]
    + [UNCLASSIFIED]
)


#####
##### The LLM's output and the frozen table
#####


@dataclass
class TriggerSpec:
    """One row of the trigger assigner's answer (`prove_ace.AssignTriggers`)."""

    id: str
    classes: list[str] = field(default_factory=list[str])
    names: list[str] = field(default_factory=list[str])
    patterns: list[str] = field(default_factory=list[str])
    goal_patterns: list[str] = field(default_factory=list[str])
    rationale: str = ""


@dataclass
class TriggerAssignment:
    reasoning: str
    triggers: list[TriggerSpec]


@dataclass(frozen=True)
class Hint:
    """One bullet attached to a feedback message."""

    id: str
    content: str


@dataclass(frozen=True)
class TriggerEntry:
    bullet_id: str
    section: str
    content: str
    classes: tuple[str, ...]
    names: tuple[str, ...]
    patterns: tuple[str, ...]
    goal_patterns: tuple[str, ...]

    @property
    def armed(self) -> bool:
        """Whether anything can ever fire this entry."""
        return bool(self.classes or self.names or self.patterns)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.bullet_id,
            "section": self.section,
            "content": self.content,
            "classes": list(self.classes),
            "names": list(self.names),
            "patterns": list(self.patterns),
            "goal_patterns": list(self.goal_patterns),
        }


class TriggerError(ValueError):
    pass


@lru_cache(maxsize=4096)
def _compile(pattern: str) -> "re.Pattern[str] | None":
    try:
        return re.compile(pattern, re.I | re.S)
    except re.error:
        return None


def _normalize_name(raw: str) -> str:
    return raw.strip().strip("`'\"").rstrip(".,;:")


@dataclass(frozen=True)
class TriggerTable:
    playbook_sha256: str
    entries: tuple[TriggerEntry, ...]

    @property
    def triggers(self) -> tuple[TriggerEntry, ...]:
        return self.entries

    # --- construction ------------------------------------------------

    @staticmethod
    def build(
        playbook: Playbook, specs: Sequence[TriggerSpec]
    ) -> "TriggerTable":
        """
        Join the assigner's rows onto the playbook, in playbook order.

        Raises `TriggerError` on an unknown bullet id, an unknown
        class, a regex that does not compile or is over
        `MAX_PATTERN_LENGTH`. A bullet the assigner did not mention
        gets an empty (never firing) entry, so the table always covers
        the whole playbook and the omission is visible in `coverage`.
        """
        by_id: dict[str, TriggerSpec] = {}
        for s in specs:
            if s.id in by_id:
                raise TriggerError(f"duplicate trigger row for {s.id}")
            by_id[s.id] = s
        known = {b.id for b in playbook.bullets}
        unknown = sorted(set(by_id) - known)
        if unknown:
            raise TriggerError(f"triggers for unknown bullet ids: {unknown}")
        entries: list[TriggerEntry] = []
        for b in playbook.bullets:
            s = by_id.get(b.id, TriggerSpec(b.id))
            for cls in s.classes:
                if cls not in KNOWN_CLASSES:
                    raise TriggerError(f"{b.id}: unknown class {cls!r}")
            for p in s.patterns + s.goal_patterns:
                if len(p) > MAX_PATTERN_LENGTH:
                    raise TriggerError(f"{b.id}: pattern too long: {p!r}")
                if _compile(p) is None:
                    raise TriggerError(f"{b.id}: invalid regex {p!r}")
            entries.append(
                TriggerEntry(
                    bullet_id=b.id,
                    section=b.section,
                    content=b.content.strip(),
                    classes=tuple(dict.fromkeys(s.classes)),
                    names=tuple(
                        dict.fromkeys(
                            n for n in map(_normalize_name, s.names) if n
                        )
                    ),
                    patterns=tuple(dict.fromkeys(s.patterns)),
                    goal_patterns=tuple(dict.fromkeys(s.goal_patterns)),
                )
            )
        return TriggerTable(playbook.sha256(), tuple(entries))

    # --- serialization ------------------------------------------------

    def dumps(self) -> str:
        """
        Self-contained YAML (bullet contents included): the frozen
        file and the exact string an evaluation cell receives, so a
        cell replays without reading the playbook.
        """
        doc = {
            "playbook_sha256": self.playbook_sha256,
            "triggers": [e.as_dict() for e in self.entries],
        }
        return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)

    @staticmethod
    def loads(text: str) -> "TriggerTable":
        raw: Any = yaml.safe_load(text)
        doc = cast(dict[str, Any], raw or {})
        rows = cast(list[dict[str, Any]], doc.get("triggers") or [])
        entries = tuple(
            TriggerEntry(
                bullet_id=str(r["id"]),
                section=str(r.get("section", "")),
                content=str(r.get("content", "")).strip(),
                classes=tuple(str(c) for c in r.get("classes") or ()),
                names=tuple(str(n) for n in r.get("names") or ()),
                patterns=tuple(str(p) for p in r.get("patterns") or ()),
                goal_patterns=tuple(
                    str(p) for p in r.get("goal_patterns") or ()
                ),
            )
            for r in rows
        )
        return TriggerTable(str(doc.get("playbook_sha256", "")), entries)

    @staticmethod
    def load(path: Path) -> "TriggerTable":
        return TriggerTable.loads(path.read_text())

    def save(self, path: Path) -> None:
        path.write_text(self.dumps())

    def sha256(self) -> str:
        return hashlib.sha256(self.dumps().encode()).hexdigest()

    def entry(self, bullet_id: str) -> TriggerEntry | None:
        for e in self.entries:
            if e.bullet_id == bullet_id:
                return e
        return None


@lru_cache(maxsize=64)
def parse_table(text: str) -> TriggerTable:
    """`TriggerTable.loads`, memoized: the generator strategy parses
    the same table on every feedback turn."""
    return TriggerTable.loads(text)


#####
##### Selection
#####


def score(
    e: TriggerEntry,
    *,
    error_class: str,
    coarse_class: str,
    error_message: str,
    failing_tactic: str,
    goals: Sequence[str],
    rule: int = DEFAULT_SELECTION_RULE,
) -> int:
    if not e.armed:
        return 0
    total = 0
    name = unknown_identifier(error_message)
    name_hit = name is not None and _normalize_name(name) in e.names
    if name_hit:
        total += SCORE_NAME
    haystack = error_message + "\n" + failing_tactic
    if any(
        (rx := _compile(p)) is not None and rx.search(haystack)
        for p in e.patterns
    ):
        total += SCORE_PATTERN
    class_hit = error_class in e.classes or coarse_class in e.classes
    if class_hit:
        total += SCORE_CLASS
    if not total:
        return 0
    if rule >= 2 and e.classes and not class_hit and not name_hit:
        return 0
    if e.goal_patterns:
        goal_text = "\n".join(goals)
        if any(
            (rx := _compile(p)) is not None and rx.search(goal_text)
            for p in e.goal_patterns
        ):
            total += SCORE_GOAL
        elif not name_hit:
            return 0
    return total


def select_ids(
    table: TriggerTable,
    *,
    error_class: str,
    coarse_class: str,
    error_message: str,
    failing_tactic: str,
    goals: Sequence[str],
    k: int = DEFAULT_MAX_HINTS,
    rule: int = DEFAULT_SELECTION_RULE,
) -> list[str]:
    """The ids of the best-matching bullets, highest score first, ties
    by playbook order; empty when nothing matches."""
    scored = [
        (
            score(
                e,
                error_class=error_class,
                coarse_class=coarse_class,
                error_message=error_message,
                failing_tactic=failing_tactic,
                goals=goals,
                rule=rule,
            ),
            i,
            e.bullet_id,
        )
        for i, e in enumerate(table.entries)
    ]
    ranked = sorted((s, i, b) for s, i, b in scored if s > 0)
    ranked.sort(key=lambda t: (-t[0], t[1]))
    return [b for _, _, b in ranked[:k]]


def select_hints(
    table: TriggerTable,
    *,
    error_message: str | None,
    failing_tactic: str | None,
    goals: Sequence[str],
    k: int = DEFAULT_MAX_HINTS,
    rule: int = DEFAULT_SELECTION_RULE,
) -> list[Hint]:
    """Hints for one failed verifier verdict (see `prove_ace`)."""
    if not error_message or error_message == NEVER_PROPOSED:
        return []
    ids = select_ids(
        table,
        error_class=refine_class(error_message),
        coarse_class=classify(error_message),
        error_message=error_message,
        failing_tactic=failing_tactic or "",
        goals=goals,
        k=k,
        rule=rule,
    )
    out: list[Hint] = []
    for i in ids:
        e = table.entry(i)
        if e is not None:
            # One line per bullet: the frozen contents keep the curators'
            # block-scalar line breaks, which would split a list item.
            out.append(Hint(e.bullet_id, " ".join(e.content.split())))
    return out


def render_hints(hints: Sequence[Hint]) -> str:
    """The markdown list the feedback template emits (kept here so a
    test can pin it without rendering a prompt)."""
    return "\n".join(f"- [{h.id}] {h.content}" for h in hints)


#####
##### Validation against recorded verdicts
#####


@dataclass(frozen=True)
class Coverage:
    verdicts: int
    covered: int
    fired: Mapping[str, int]
    """Failed verdicts each bullet would have been attached to."""
    fired_cells: Mapping[str, int]
    by_class: Mapping[str, tuple[int, int]]
    """class -> (failed verdicts, verdicts with at least one hint)."""
    unarmed: tuple[str, ...]
    """Bullets whose entry can never fire."""
    silent: tuple[str, ...]
    """Armed bullets that fired on no recorded verdict."""

    def as_dict(self) -> dict[str, Any]:
        return {
            "verdicts": self.verdicts,
            "covered": self.covered,
            "fired": dict(self.fired),
            "firedCells": dict(self.fired_cells),
            "byClass": {c: list(v) for c, v in self.by_class.items()},
            "unarmed": list(self.unarmed),
            "silent": list(self.silent),
        }

    def render(self) -> str:
        buf = [
            f"    {self.covered}/{self.verdicts} failed verdicts get at "
            f"least one hint; {len(self.unarmed)} bullet(s) unarmed, "
            f"{len(self.silent)} armed but silent",
            f"    {'class':24}{'failed':>8}{'hinted':>8}",
            *[
                f"    {c:24}{n:8d}{h:8d}"
                for c, (n, h) in sorted(
                    self.by_class.items(), key=lambda kv: -kv[1][0]
                )
            ],
            f"    {'bullet':12}{'verdicts':>9}{'cells':>7}",
            *[
                f"    {b:12}{n:9d}{self.fired_cells.get(b, 0):7d}"
                for b, n in sorted(self.fired.items(), key=lambda kv: -kv[1])
            ],
        ]
        if self.unarmed:
            buf.append(f"    unarmed: {', '.join(self.unarmed)}")
        if self.silent:
            buf.append(f"    silent : {', '.join(self.silent)}")
        return "\n".join(buf)


def recorded_rejections(run: Path) -> Iterable[tuple[str, dict[str, Any]]]:
    """`(cell, verdict)` for every failed verdict of a recorded run, with
    the remaining goals (which `failure_analysis.Verdict` drops)."""
    for cache in sorted(run.glob("configs/*/cache.yaml")):
        for fb in _feedback_entries(cache):
            if fb.get("success"):
                continue
            msg = fb.get("error_message")
            if not msg or msg == NEVER_PROPOSED:
                continue
            yield cache.parent.name, fb


def coverage(
    table: TriggerTable,
    runs: Iterable[Path],
    k: int = DEFAULT_MAX_HINTS,
    rule: int = DEFAULT_SELECTION_RULE,
) -> Coverage:
    """Replay the selection over every failed verdict of the runs."""
    fired: Counter[str] = Counter()
    cells: dict[str, set[str]] = {e.bullet_id: set() for e in table.entries}
    failed: Counter[str] = Counter()
    hinted: Counter[str] = Counter()
    total = covered = 0
    for run in runs:
        for cell, fb in recorded_rejections(run):
            msg = str(fb.get("error_message"))
            cls = refine_class(msg)
            total += 1
            failed[cls] += 1
            ids = select_ids(
                table,
                error_class=cls,
                coarse_class=classify(msg),
                error_message=msg,
                failing_tactic=str(fb.get("failing_tactic") or ""),
                goals=[
                    str(g)
                    for g in cast(list[Any], fb.get("remaining_goals") or [])
                ],
                k=k,
                rule=rule,
            )
            if ids:
                covered += 1
                hinted[cls] += 1
            for i in ids:
                fired[i] += 1
                cells[i].add(cell)
    unarmed = tuple(e.bullet_id for e in table.entries if not e.armed)
    silent = tuple(
        e.bullet_id
        for e in table.entries
        if e.armed and fired[e.bullet_id] == 0
    )
    return Coverage(
        verdicts=total,
        covered=covered,
        fired={e.bullet_id: fired[e.bullet_id] for e in table.entries},
        fired_cells={
            e.bullet_id: len(cells[e.bullet_id]) for e in table.entries
        },
        by_class={c: (failed[c], hinted[c]) for c in failed},
        unarmed=unarmed,
        silent=silent,
    )


#####
##### What the assigner is shown
#####


def render_taxonomy() -> str:
    """The class list the trigger assigner may use, one per line."""
    lines = [f"- `{c.label}` — {c.blurb}" for c in TAXONOMY]
    lines += [
        f"- `{c.label}` — {c.blurb} (a finer reading of `other`)"
        for c in FINE_TAXONOMY
    ]
    lines.append(f"- `{UNCLASSIFIED}` — no class matched")
    return "\n".join(lines)


def render_playbook_for_assignment(pb: Playbook) -> str:
    """Bullets with id and section, in playbook order."""
    return "\n".join(
        f"- [{b.id}] ({b.section}) {' '.join(b.content.split())}"
        for b in pb.bullets
    )
