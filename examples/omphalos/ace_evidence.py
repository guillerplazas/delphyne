"""
Verifier evidence for ACE curation: what the pool actually gets wrong.

The v3 pipeline's Curator saw one Reflector diagnosis at a time and its
Reducer kept the "distinctive" proposals, so the frozen v3 playbook
holds no bullet about the most frequent failure classes on the
adaptation pool — Lean-only tactic names, prover-killing `vm_compute`,
a handful of always-wrong Ltac forms — although each accounts for
hundreds of verifier verdicts (PROGRESS 2026-09-02, causes C1 and C4).

This module turns the run's *own* verifier feedback into a
deterministic **evidence digest**: error classes ranked by how many
problems and verdicts they account for, with the most frequent unknown
identifiers and failing-tactic heads. The contract-4 Curator, the
contract-2 Reducer and the final Auditor read it next to the
Reflector's diagnosis, so "frequent" can compete with "distinctive".
The digest is counted, never written by a model, and everything here
is sorted and capped so the same recorded caches always render the
same text — the driver pins that text into every config that consumed
it, exactly like the v3 `progress` block.

It also carries the pure half of the **grounding gate**: which names
in a proposed bullet can be checked against Rocq, and how a `Locate`
answer is read (`Constant …` / `Ltac …` = exists, `No object …` =
does not, anything the bridge could not run = unknown, which keeps the
bullet). Measured on 2026-09-02 through the dev bridge: `Locate
pow2_sqrt.` → `Constant Stdlib.Reals.R_sqrt.pow2_sqrt`, `Locate nia.`
→ `Ltac Stdlib.micromega.Lia.nia`, `Locate norm_num.` → `No object of
basename norm_num`. Primitive tactic keywords (`assert`, `destruct`,
…) are not objects and answer `No object` too, hence the allow-list.
"""

# pyright: strict

import re
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

_OMPHALOS_DIR = Path(__file__).resolve().parent
if str(_OMPHALOS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(_OMPHALOS_DIR / "tools"))

from failure_analysis import (  # noqa: E402
    TAXONOMY,
    UNCLASSIFIED,
    _feedback_entries,  # pyright: ignore[reportPrivateUsage]
    classify,
)

#####
##### Failed verdicts
#####


@dataclass(frozen=True)
class FailedVerdict:
    """One rejected proposal, reduced to what the digest counts."""

    bench: str
    error_class: str
    failing_tactic: str
    error_message: str


def failed_verdicts(bench: str, cache: Path) -> list[FailedVerdict]:
    """
    Every failed verifier verdict in one generator cell's `cache.yaml`,
    in cache order. Verdicts without an error message (a script that
    applied cleanly but left goals open) carry no mechanical failure
    and are not evidence.
    """
    out: list[FailedVerdict] = []
    for fb in _feedback_entries(cache):
        if fb.get("success"):
            continue
        message = fb.get("error_message")
        if not message:
            continue
        out.append(
            FailedVerdict(
                bench=bench,
                error_class=classify(str(message)),
                failing_tactic=str(fb.get("failing_tactic") or ""),
                error_message=str(message),
            )
        )
    return out


def collect_failures(cells: Mapping[str, Path]) -> list[FailedVerdict]:
    """
    Failed verdicts of several generator cells (`bench -> config
    directory`), benches in sorted order so the result is a function of
    the mapping's *content*. A cell without a cache contributes nothing.
    """
    out: list[FailedVerdict] = []
    for bench in sorted(cells):
        cache = cells[bench] / "cache.yaml"
        if cache.exists():
            out.extend(failed_verdicts(bench, cache))
    return out


#####
##### Extracting the recurring objects
#####


_UNKNOWN_RE = re.compile(
    r"\b(?:reference|variable)\s+(\S+?)\s+was\s+not\s+found", re.S
)


def unknown_identifier(message: str) -> str | None:
    """The `X` of "The reference/variable X was not found", line-wrapped
    or not; `None` for any other message."""
    m = _UNKNOWN_RE.search(message)
    return m.group(1) if m else None


_LEADING_FOCUS_RE = re.compile(r"^(?:[-+*]+|[{}]|\d+:|all:)\s*")


def tactic_head(tactic: str) -> str:
    """
    The shape of a failing tactic, coarse enough to count: its leading
    verb after any bullet, brace or goal selector, plus a marker for the
    three Ltac shapes that recur — `… :=` (`set`/`pose` definitions),
    `… in` (a hypothesis target) and `… by` (an inline sub-proof).
    """
    text = _LEADING_FOCUS_RE.sub("", tactic.strip()).rstrip(".").strip()
    if not text:
        return "(empty)"
    tokens = text.split()
    head = tokens[0]
    rest = " " + " ".join(tokens[1:]) + " "
    if " := " in rest or rest.strip().startswith(":="):
        head += " … :="
    elif " in " in rest:
        head += " … in"
    elif " by " in rest:
        head += " … by"
    return head


#####
##### The digest
#####


@dataclass(frozen=True)
class ClassSummary:
    label: str
    verdicts: int
    problems: int
    names: tuple[tuple[str, int], ...]
    """Unknown identifiers with counts (`unknown-reference` only)."""
    heads: tuple[tuple[str, int, str], ...]
    """Failing-tactic heads with counts and the shortest example."""


_BLURBS: Mapping[str, str] = {c.label: c.blurb for c in TAXONOMY}


def summarize(
    verdicts: Sequence[FailedVerdict],
    *,
    max_classes: int = 8,
    max_items: int = 8,
) -> list[ClassSummary]:
    """
    Classes ranked by `(problems, verdicts)` descending, label ascending
    as the tie-break; within a class, names and heads by count
    descending then text ascending. Pure and order-independent: the
    input is treated as a multiset.
    """
    by_class: dict[str, list[FailedVerdict]] = {}
    for v in verdicts:
        by_class.setdefault(v.error_class, []).append(v)
    ranked = sorted(
        by_class.items(),
        key=lambda kv: (
            -len({v.bench for v in kv[1]}),
            -len(kv[1]),
            kv[0],
        ),
    )[:max_classes]
    out: list[ClassSummary] = []
    for label, vs in ranked:
        names = Counter[str]()
        heads = Counter[str]()
        example: dict[str, str] = {}
        for v in vs:
            if label == "unknown-reference":
                name = unknown_identifier(v.error_message)
                if name:
                    names[name] += 1
            if v.failing_tactic:
                head = tactic_head(v.failing_tactic)
                heads[head] += 1
                shown = " ".join(v.failing_tactic.split())
                current = example.get(head)
                if current is None or (len(shown), shown) < (
                    len(current),
                    current,
                ):
                    example[head] = shown
        out.append(
            ClassSummary(
                label=label,
                verdicts=len(vs),
                problems=len({v.bench for v in vs}),
                names=tuple(
                    sorted(names.items(), key=lambda kv: (-kv[1], kv[0]))[
                        :max_items
                    ]
                ),
                heads=tuple(
                    (h, n, example[h])
                    for h, n in sorted(
                        heads.items(), key=lambda kv: (-kv[1], kv[0])
                    )[:max_items]
                ),
            )
        )
    return out


def _clip(text: str, width: int = 60) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


def render_digest(
    verdicts: Sequence[FailedVerdict],
    *,
    attempts: int,
    max_classes: int = 8,
    max_items: int = 8,
    blurbs: Mapping[str, str] | None = None,
) -> str:
    """
    The evidence block a curation prompt receives, or `""` when there
    is nothing to report (the templates guard on emptiness, so the
    first steps of a run render exactly like a contract-3 prompt would
    have with no evidence). This text is part of LLM prompts and of
    config identity: change it with the care of a template. `blurbs`
    extends the class descriptions (the trigger assigner passes the
    fine classes); the default renders every recorded digest
    byte-identically.
    """
    if not verdicts:
        return ""
    if blurbs is None:
        blurbs = _BLURBS
    lines = [
        f"{attempts} attempt(s) on this pool so far, {len(verdicts)} failed"
        " verifier verdicts (one verdict = one rejected proposal),"
        " most frequent classes first:"
    ]
    for c in summarize(verdicts, max_classes=max_classes, max_items=max_items):
        blurb = blurbs.get(c.label, "unclassified")
        if c.label == UNCLASSIFIED:
            blurb = "no class matched"
        line = (
            f"- {c.label} — {c.verdicts} verdict(s) on {c.problems}"
            f" problem(s) ({blurb})."
        )
        if c.names:
            line += " Names that do not exist here: " + ", ".join(
                f"`{name}` ({n})" for name, n in c.names
            )
            line += "."
        if c.heads:
            line += " Failing tactic heads: " + ", ".join(
                f"`{head}` ({n}; e.g. `{_clip(ex)}`)"
                for head, n, ex in c.heads
            )
            line += "."
        lines.append(line)
    return "\n".join(lines)


#####
##### What the prover is already told
#####


AGENTIC_SYSTEM_TEMPLATE = (
    _OMPHALOS_DIR / "prompts" / "ProposeProofScriptAgentic.system.jinja"
)


def known_guidance(template: Path = AGENTIC_SYSTEM_TEMPLATE) -> str:
    """
    The `## Pitfalls …` section of the agentic system prompt, verbatim.
    A curation prompt that can see it can refuse bullets that merely
    restate it — the contract-3 rule said "do not restate the system
    prompt" to a model that had never seen the system prompt.
    """
    text = template.read_text()
    start = text.index("## Pitfalls")
    end = text.index("## Budget", start)
    return text[start:end].strip()


#####
##### Grounding: which names can be checked, and reading `Locate`
#####


PRIMITIVE_TACTICS: frozenset[str] = frozenset(
    """
    intro intros apply eapply exact eexact refine assert pose set remember
    destruct edestruct induction einduction case inversion injection
    discriminate rewrite erewrite replace change unfold fold simpl cbn cbv
    lazy hnf compute vm_compute native_compute reflexivity symmetry
    transitivity split left right exists eexists constructor econstructor
    specialize generalize revert clear subst intuition tauto easy trivial
    auto eauto congruence contradiction exfalso absurd omega lia nia lra
    nra ring field field_simplify psatz repeat try first solve all do
    idtac fail progress abstract cut enough now assumption eassumption
    admit give_up exact_no_check by in at with as using
    decompose firstorder inversion_clear dependent remember functional
    autorewrite rewrite_strat setoid_rewrite setoid_replace zify nsatz
    ring_simplify field_simplify_eq psatzl lra_Q simplify_eq elim
    eelim apply_fun move rename evar instantiate unshelve shelve
    cycle swap revgoals once exactly_once solve_constraints typeclasses
    """.split()
)
"""
Tactic keywords and vernacular words that are not objects `Locate` can
find (or that exist only as notation): a reference to one of them is
skipped by the gate rather than refused. The micromega tactics are Ltac
objects and would answer `Ltac …`, but only once `Lia`/`Lra`/`Psatz` is
imported — the bridge always imports them, so they are listed here as a
belt-and-braces measure, not because they would fail.
"""

_IDENT_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)*$"
)


def normalize_reference(raw: str) -> str:
    """
    Strip the decoration a model puts around a name in YAML/markdown
    (backticks, quotes, a trailing period or comma). A *trailing* prime
    is part of a Rocq name (`Rle_0_sqr'`) and is kept.
    """
    text = raw.strip().strip('`"').lstrip("'").strip()
    return text.rstrip(".,;:").strip()


def checkable_references(names: Iterable[str]) -> list[str]:
    """
    The subset of `names` the gate can meaningfully send to `Locate`:
    identifier-shaped (possibly module-qualified), not a primitive
    tactic keyword, de-duplicated in first-appearance order.
    """
    out: list[str] = []
    for raw in names:
        name = normalize_reference(raw)
        if not name or name in out:
            continue
        if not _IDENT_RE.match(name):
            continue
        if name in PRIMITIVE_TACTICS:
            continue
        out.append(name)
    return out


GroundingVerdict = Literal["grounded", "missing", "error"]

_BRIDGE_FAILURE_PREFIXES = (
    "Rocq rejected the command",
    "Failed to open session",
    "(Rocq returned no output",
)


def grounding_verdict(locate_output: str) -> GroundingVerdict:
    """
    Read the bridge's answer to `Locate <name>.`: `No object …` means
    the name does not exist in that environment; a bridge or session
    failure is *not* evidence about the name (the bullet is kept and
    the failure counted); anything else names an object.
    """
    text = locate_output.strip()
    if text.startswith("No object"):
        return "missing"
    if text.startswith(_BRIDGE_FAILURE_PREFIXES):
        return "error"
    return "grounded"


def locate_command(name: str) -> str:
    return f"Locate {name}."


#####
##### Which environments to check against
#####


_IMPORT_RE = re.compile(r"^\s*(?:From\s+\S+\s+)?Require\b.*$", re.M)


def import_signature(problem_file: str | Path) -> str:
    """
    The `Require` lines of a problem file, in order — what decides
    which names `Locate` can see. Two files with the same signature
    are the same environment for the gate's purposes.
    """
    path = Path(problem_file)
    if not path.is_absolute():
        path = _OMPHALOS_DIR / path
    lines = [
        " ".join(m.group(0).split())
        for m in _IMPORT_RE.finditer(path.read_text())
    ]
    return "\n".join(lines)


def representative_files(
    pool: Mapping[str, tuple[str, str]],
) -> list[tuple[str, str]]:
    """
    One `(problem_file, theorem_name)` per distinct import signature in
    the pool, in pool order: the environments a pool-level bullet (an
    Auditor addition) is grounded against. A name that resolves in any
    of them exists on this benchmark.
    """
    seen: dict[str, tuple[str, str]] = {}
    for _bench, (file, theorem) in pool.items():
        sig = import_signature(file)
        if sig not in seen:
            seen[sig] = (file, theorem)
    return list(seen.values())
