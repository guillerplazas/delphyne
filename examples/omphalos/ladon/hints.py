"""
Pure parsers and rewriters for `HINTS.md` and `PROGRESS.md`.

Ladon reads the backlog and writes its verdicts back without ever
letting a language model edit the two files directly: the model
returns text, this module places it. That keeps the house conventions
(numbered entries, newest first, status inside the bold title,
3-space continuation indent, corrections appended never deleted) a
property of code rather than of a prompt.

`HINTS.md` entry shape (verified 2026-09-02 on 65 entries):

    67. **[experiment] Title of the hint** (2026-09-02). Body wrapped
       at ~72 columns, continuation lines indented three spaces.

Status lives in leading bracket groups before the tag —
`**[DONE 2026-08-26 — see PROGRESS] [tool] …**` — or as a
`— ✅ DONE` suffix after the closing `**`. Ladon adds its own groups:
`[DONE <date> by Ladon — KEEP: …]`, `[LADON DISCARD <date> — …]`,
`[LADON INSPECT <date> — …; inspect with Fable]`, `[LADON HUMAN …]`.
A marker only ever rewrites the entry's *first line*; every other line
of the file stays byte-identical (the precedent is HINTS #49, whose
marker line is longer than the wrap width).
"""

# pyright: strict

import re
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

ENTRY_RE = re.compile(r"^(?P<n>\d+)\. \*\*")
HEADING_RE = re.compile(r"^## ")
_BRACKET_RE = re.compile(r"^\[(?P<inner>[^\]]*)\]\s*")
_TAG_RE = re.compile(r"^[a-z]+$")
_DONE_RE = re.compile(r"^(DONE|BUILT|✅)\b")
_SUFFIX_DONE_RE = re.compile(r"^\s*—\s*✅")

WRAP_WIDTH = 72
CONTINUATION = "   "

type HintStatus = Literal[
    "open", "partial", "done", "discarded", "inspect", "human"
]


@dataclass(frozen=True)
class Hint:
    n: int
    tag: str
    extra_tags: tuple[str, ...]
    title: str
    status: HintStatus
    annotations: tuple[str, ...]
    body: str
    section: str
    first_line: int
    last_line: int

    @property
    def open(self) -> bool:
        return self.status in ("open", "partial")


@dataclass(frozen=True)
class NewHint:
    tag: str
    title: str
    body: str


def _status_of(annotations: Sequence[str], rest: str) -> HintStatus:
    if _SUFFIX_DONE_RE.match(rest):
        return "done"
    for a in annotations:
        if a.startswith("LADON DISCARD"):
            return "discarded"
        if a.startswith("LADON INSPECT"):
            return "inspect"
        if a.startswith("LADON HUMAN"):
            return "human"
        if _DONE_RE.match(a):
            return "done"
    if any("DONE" in a or "BUILT" in a for a in annotations):
        return "partial"
    return "open"


def _parse_block(
    n: int, lines: Sequence[str], section: str, first: int, last: int
) -> Hint:
    head = lines[0]
    m = ENTRY_RE.match(head)
    assert m is not None
    joined = " ".join(
        [head[m.end() :]] + [ln.strip() for ln in lines[1:] if ln.strip()]
    )
    close = joined.find("**")
    if close < 0:
        title_text, rest = joined, ""
    else:
        title_text, rest = joined[:close], joined[close + 2 :]
    annotations: list[str] = []
    tags: list[str] = []
    cursor = title_text
    while True:
        bm = _BRACKET_RE.match(cursor)
        if bm is None:
            break
        inner = bm.group("inner")
        if _TAG_RE.match(inner):
            tags.append(inner)
        elif tags:
            # A bracket after the tag belongs to the title text.
            break
        else:
            annotations.append(inner)
        cursor = cursor[bm.end() :]
    title = cursor.strip()
    return Hint(
        n=n,
        tag=tags[0] if tags else "",
        extra_tags=tuple(tags[1:]),
        title=title,
        status=_status_of(annotations, rest),
        annotations=tuple(annotations),
        body=rest.strip(" —").strip(),
        section=section,
        first_line=first,
        last_line=last,
    )


def parse_hints(text: str) -> list[Hint]:
    lines = text.splitlines()
    hints: list[Hint] = []
    section = ""
    start: int | None = None
    n = 0

    def flush(end_exclusive: int) -> None:
        nonlocal start
        if start is None:
            return
        last = end_exclusive - 1
        while last > start and not lines[last].strip():
            last -= 1
        hints.append(
            _parse_block(n, lines[start : last + 1], section, start, last)
        )
        start = None

    for i, line in enumerate(lines):
        if HEADING_RE.match(line):
            flush(i)
            section = line[3:].strip()
            continue
        em = ENTRY_RE.match(line)
        if em is not None:
            flush(i)
            start = i
            n = int(em.group("n"))
    flush(len(lines))
    return hints


def open_hints(text: str) -> list[Hint]:
    return [h for h in parse_hints(text) if h.open]


def find_hint(text: str, n: int) -> Hint | None:
    for h in parse_hints(text):
        if h.n == n:
            return h
    return None


def max_number(text: str) -> int:
    return max((h.n for h in parse_hints(text)), default=0)


def mark_hint(text: str, n: int, marker: str) -> str:
    """Prefix `[marker]` into entry `n`'s bold title (first line only)."""
    hint = find_hint(text, n)
    if hint is None:
        raise KeyError(f"hint {n} not found")
    assert "]" not in marker, "a marker must not contain a closing bracket"
    lines = text.splitlines(keepends=True)
    head = lines[hint.first_line]
    m = ENTRY_RE.match(head)
    assert m is not None
    lines[hint.first_line] = f"{head[: m.end()]}[{marker}] {head[m.end() :]}"
    return "".join(lines)


def _wrap_entry(n: int, hint: NewHint) -> str:
    tag = hint.tag if _TAG_RE.match(hint.tag) else "experiment"
    body = " ".join(hint.body.split())
    title = " ".join(hint.title.split())
    return textwrap.fill(
        f"{n}. **[{tag}] {title}** — {body}",
        width=WRAP_WIDTH,
        subsequent_indent=CONTINUATION,
        break_long_words=False,
        break_on_hyphens=False,
    )


def ladon_section_heading(date: str) -> str:
    return f"## From {date} — Ladon night"


def append_hints(text: str, date: str, new: Sequence[NewHint]) -> str:
    """
    Add `new` as the newest entries: under the night's own section
    (created before the first existing section if absent), numbered
    above every existing entry, highest first.
    """
    if not new:
        return text
    top = max_number(text)
    numbers = list(range(top + len(new), top, -1))
    entries = [_wrap_entry(k, h) for k, h in zip(numbers, new)]
    heading = ladon_section_heading(date)
    lines = text.splitlines(keepends=True)
    block = "\n\n".join(entries) + "\n\n"
    for i, line in enumerate(lines):
        if line.rstrip("\n") == heading:
            # Existing night section: insert right after its heading.
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            lines.insert(j, block)
            return "".join(lines)
    for i, line in enumerate(lines):
        if HEADING_RE.match(line):
            lines.insert(i, f"{heading}\n\n{block}")
            return "".join(lines)
    return text.rstrip("\n") + f"\n\n{heading}\n\n{block}"


def render_hint_context(hint: Hint) -> str:
    """What a planning session sees for one hint."""
    tags = " ".join(f"[{t}]" for t in (hint.tag, *hint.extra_tags) if t)
    ann = "".join(f"[{a}] " for a in hint.annotations)
    return (
        f"### Hint {hint.n} {tags} — {hint.title}\n"
        f"Section: {hint.section}\nStatus: {hint.status} {ann}\n\n"
        f"{hint.body}\n"
    )


#####
##### PROGRESS.md
#####


def progress_heading(date: str, summary: str) -> str:
    return f"## {date} — Ladon night: {summary}"


def insert_progress_section(text: str, heading: str, intro: str) -> str:
    """Create a new newest-first entry before the first existing one."""
    block = f"{heading}\n\n{intro.rstrip()}\n\n\n"
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if HEADING_RE.match(line):
            lines.insert(i, block)
            return "".join(lines)
    return text.rstrip("\n") + "\n\n\n" + block


def find_section(text: str, heading: str) -> tuple[int, int] | None:
    """`(start, end_exclusive)` line span of the section with `heading`."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.rstrip() == heading:
            j = i + 1
            while j < len(lines) and not HEADING_RE.match(lines[j]):
                j += 1
            return i, j
    return None


def append_to_section(text: str, heading: str, paragraph: str) -> str:
    """
    Append `paragraph` at the end of the section headed `heading`,
    keeping the blank lines that separate sections.
    """
    span = find_section(text, heading)
    if span is None:
        raise KeyError(f"section not found: {heading}")
    lines = text.splitlines(keepends=True)
    _, end = span
    last = end - 1
    while last > span[0] and not lines[last].strip():
        last -= 1
    lines.insert(last + 1, "\n" + paragraph.rstrip() + "\n")
    return "".join(lines)


def replace_heading(text: str, old: str, new: str) -> str:
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.rstrip() == old:
            lines[i] = new + "\n"
            return "".join(lines)
    raise KeyError(f"heading not found: {old}")
