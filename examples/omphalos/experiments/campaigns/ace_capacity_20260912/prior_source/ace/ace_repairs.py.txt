"""
Repair mining: advice from the verifier's own ground truth.

A Reflector narrates one trajectory and a Curator distils it; both
are LLM readings of what went wrong. The recorded caches hold
something better for the frequent, mechanical classes: for every
rejected proposal the prover fixed on its next attempt, the pair
*(failing tactic, what replaced it)* is a repair the verifier accepted.
Mining those pairs over a pool ranks, per failure class (fine
taxonomy included — `ring-failure`, `unify-failure`, … never reached a
digest before), what actually fixes the class on this benchmark, with
verbatim examples. `experiments/ace/ace_repairs_experiment.py` hands the
ranked digest to a stronger model (`prove_ace.WriteRepairBullets`)
that writes at most a few bullets *with their triggers*, passes them
through the grounding gate and appends them to a frozen playbook.

Only adaptation-pool caches are mined (trainX); never a selection or
test partition.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import difflib
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml


from ace.ace_evidence import tactic_head, unknown_identifier  # noqa: E402
from tools.analysis.failure_analysis import (  # noqa: E402
    FINE_TAXONOMY,
    TAXONOMY,
    classify,
    refine_class,
)

_OMPHALOS_DIR = OMPHALOS_ROOT

_CHECK_PREFIXES = ("fun: check_assisted", "fun: check\n", "fun: checked_proof")

Outcome = Literal["solved", "advanced"]


@dataclass(frozen=True)
class Attempt:
    """One proposal and its verdict, as recorded."""

    tactics: tuple[str, ...]
    success: bool
    failing_index: int | None
    failing_tactic: str | None
    error_message: str | None
    goals: tuple[str, ...]


@dataclass(frozen=True)
class Repair:
    bench: str
    cell: str
    fine_class: str
    coarse_class: str
    unknown_name: str | None
    failing_tactic: str
    error_message: str
    before: tuple[str, ...]
    """The rejected tactic block (starts at the failing tactic)."""
    after: tuple[str, ...]
    """What the next accepted proposal put in its place."""
    outcome: Outcome
    goal: str
    """The first remaining goal at the rejection (conclusion line)."""

    @property
    def key(self) -> tuple[str, str]:
        """Grouping key: class and the failing tactic's head (or the
        unknown name for `unknown-reference`)."""
        if self.fine_class == "unknown-reference" and self.unknown_name:
            return (self.fine_class, f"`{self.unknown_name}`")
        return (self.fine_class, f"`{tactic_head(self.failing_tactic)}`")


#####
##### Reading a cell
#####


def attempts_of_cache(cache: Path) -> list[Attempt]:
    from tools.data.ace_review_benchmark import assert_training_allowed

    assert_training_allowed([cache.parent.name.split("__")[0]])
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    raw: Any = yaml.load(cache.read_text(), Loader=loader)
    out: list[Attempt] = []
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
        call: Any = yaml.load(body, Loader=loader)
        fb: Any = yaml.load(
            str(outputs[0].get("content") or ""), Loader=loader
        )
        if isinstance(fb, dict) and "feedback" in fb:
            fb = cast(dict[str, Any], fb)["feedback"]
        if not isinstance(call, dict) or not isinstance(fb, dict):
            continue
        args = cast(
            dict[str, Any], cast(dict[str, Any], call).get("args") or {}
        )
        fbd = cast(dict[str, Any], fb)
        tactics = tuple(str(t) for t in args.get("tactics") or ())
        idx = fbd.get("failing_index")
        out.append(
            Attempt(
                tactics=tactics,
                success=bool(fbd.get("success")),
                failing_index=int(idx) if idx is not None else None,
                failing_tactic=cast(str | None, fbd.get("failing_tactic")),
                error_message=cast(str | None, fbd.get("error_message")),
                goals=tuple(str(g) for g in fbd.get("remaining_goals") or ()),
            )
        )
    return out


def _conclusion(goal: str) -> str:
    for line in reversed(goal.splitlines()):
        if "|-" in line:
            return line.split("|-", 1)[1].strip()
    return goal.strip().splitlines()[-1] if goal.strip() else ""


def _replacement(
    old: Sequence[str], new: Sequence[str], idx: int
) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    """
    The diff block of `old → new` that covers `old[idx]` (the failing
    tactic). `None` when the failing tactic survived unchanged — the
    prover changed something else, which is not a repair of *this*
    rejection.
    """
    sm = difflib.SequenceMatcher(a=list(old), b=list(new), autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert" and i1 == idx:
            # Something was put in front of the failing tactic, which
            # then survived: the repair is "prepare, then the same".
            return (old[idx],), tuple(new[j1:j2]) + (old[idx],)
        if i1 <= idx < i2:
            return tuple(old[i1:i2]), tuple(new[j1:j2])
    return None


_GIVE_UP = ("admit", "give_up", "Admitted")


def _gives_up(tactics: Sequence[str]) -> bool:
    return any(
        t.strip().lstrip("-+*{ ").split(".")[0].strip() in _GIVE_UP
        for t in tactics
    )


def repairs_of_cell(
    bench: str, cell: str, attempts: Sequence[Attempt]
) -> list[Repair]:
    out: list[Repair] = []
    for a, b in zip(attempts, attempts[1:], strict=False):
        if a.success or a.failing_index is None or not a.failing_tactic:
            continue
        if not a.error_message or a.failing_tactic == "Qed.":
            continue
        if b.success:
            outcome: Outcome = "solved"
        elif b.failing_index is not None and b.failing_index > a.failing_index:
            outcome = "advanced"
        else:
            continue
        rep = _replacement(a.tactics, b.tactics, a.failing_index)
        if rep is None:
            continue
        before, after = rep
        if not after or before == after or _gives_up(after):
            continue
        out.append(
            Repair(
                bench=bench,
                cell=cell,
                fine_class=refine_class(a.error_message),
                coarse_class=classify(a.error_message),
                unknown_name=unknown_identifier(a.error_message),
                failing_tactic=a.failing_tactic,
                error_message=a.error_message,
                before=before,
                after=after,
                outcome=outcome,
                goal=_conclusion(a.goals[0]) if a.goals else "",
            )
        )
    return out


def mine_run(run: Path, only: str | None = None) -> list[Repair]:
    """
    Every repair in a recorded run. `only` restricts to cells whose
    name contains it (the adaptation directories hold generator,
    reflector and curator cells side by side: `only="_generator_"`).
    """
    out: list[Repair] = []
    for cache in sorted(run.glob("configs/*/cache.yaml")):
        cell = cache.parent.name
        if only and only not in cell:
            continue
        bench = cell.split("__")[0]
        if cell.startswith("step") and "_generator_" in cell:
            bench = cell.split("_generator_", 1)[1]
        out.extend(repairs_of_cell(bench, cell, attempts_of_cache(cache)))
    return out


#####
##### Ranking and rendering
#####


@dataclass(frozen=True)
class RepairGroup:
    fine_class: str
    trigger: str
    """The unknown name or the failing tactic head."""
    repairs: int
    problems: int
    solved: int
    after_heads: tuple[tuple[str, int], ...]
    examples: tuple[tuple[str, str, str], ...]
    """(before, after, goal) — shortest first."""


def _short(tactics: Sequence[str], width: int = 110) -> str:
    text = " ".join(" ".join(t.split()) for t in tactics)
    return text if len(text) <= width else text[: width - 1] + "…"


def group_repairs(
    repairs: Sequence[Repair], *, max_groups: int = 16, max_examples: int = 3
) -> list[RepairGroup]:
    by_key: dict[tuple[str, str], list[Repair]] = defaultdict(list)
    for r in repairs:
        by_key[r.key].append(r)
    ranked = sorted(
        by_key.items(),
        key=lambda kv: (
            -len({r.bench for r in kv[1]}),
            -len(kv[1]),
            kv[0],
        ),
    )[:max_groups]
    out: list[RepairGroup] = []
    for (cls, trig), rs in ranked:
        heads = Counter[str]()
        for r in rs:
            heads[tactic_head(r.after[0])] += 1
        shown: list[tuple[str, str, str]] = []
        seen: set[str] = set()
        for r in sorted(
            rs, key=lambda r: len(_short(r.before) + _short(r.after))
        ):
            ex = (_short(r.before), _short(r.after), _short([r.goal], 80))
            if ex[0] + ex[1] in seen:
                continue
            seen.add(ex[0] + ex[1])
            shown.append(ex)
            if len(shown) >= max_examples:
                break
        out.append(
            RepairGroup(
                fine_class=cls,
                trigger=trig,
                repairs=len(rs),
                problems=len({r.bench for r in rs}),
                solved=sum(1 for r in rs if r.outcome == "solved"),
                after_heads=tuple(
                    sorted(heads.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
                ),
                examples=tuple(shown),
            )
        )
    return out


_BLURBS: Mapping[str, str] = {
    c.label: c.blurb for c in TAXONOMY + FINE_TAXONOMY
}


def render_repairs(
    repairs: Sequence[Repair],
    *,
    cells: int,
    max_groups: int = 16,
    max_examples: int = 3,
) -> str:
    """
    The digest a bullet writer receives: one paragraph per group,
    frequent first, each with the replacements that were accepted and
    verbatim examples. Part of an LLM prompt and of a config identity —
    change with the care of a template.
    """
    if not repairs:
        return ""
    groups = group_repairs(
        repairs, max_groups=max_groups, max_examples=max_examples
    )
    lines = [
        f"{cells} recorded attempts, {len(repairs)} repairs the verifier"
        " accepted (a rejected tactic replaced by one the next proposal"
        " got past), most widespread first:"
    ]
    for g in groups:
        blurb = _BLURBS.get(g.fine_class, "no class matched")
        lines.append(
            f"- {g.fine_class} at {g.trigger} — {g.repairs} repair(s) on"
            f" {g.problems} problem(s), {g.solved} finishing the proof"
            f" ({blurb}). Accepted replacements start with: "
            + ", ".join(f"`{h}` ({n})" for h, n in g.after_heads)
            + "."
        )
        for before, after, goal in g.examples:
            goal_part = f" [goal: `{goal}`]" if goal else ""
            lines.append(f"    `{before}` → `{after}`{goal_part}")
    return "\n".join(lines)


def name_replacements(repairs: Iterable[Repair]) -> dict[str, Counter[str]]:
    """unknown name → what the next accepted proposal used instead."""
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for r in repairs:
        if r.unknown_name and r.after:
            out[r.unknown_name][tactic_head(r.after[0])] += 1
    return dict(out)
