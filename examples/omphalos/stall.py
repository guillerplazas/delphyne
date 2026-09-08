"""
Stall rules: stop a proof search that has stopped making progress.

Every unsolved cell of the luna baselines runs to the 32-request cap
(25 of 26 on validationX), and those cells are 58–76 % of a run's
spend while the $0.10 dollar cap never binds. A stall rule is a third
budget mechanism next to the request and dollar caps: a pure predicate
over the verifier's verdicts so far, evaluated before each new request
(`prove_stall.prove_theorem_agentic_stall` reads it off the
conversation prefix that `dp.interact` maintains), that ends the search
when the last `k` rejections show no progress under one of four
readings:

- `noadvance` — the failing index never exceeded the best so far (the
  naive rule; blind to a script that grows and fails at `Qed.`);
- `samegoal` — the remaining goal state (count, first conclusion)
  equals the previous verdict's;
- `seenstate` — the (class, count, first conclusion) state was already
  seen earlier in the cell;
- `sameclass` — all of one fine failure class.

Because a stopped run is a prefix of a recorded one, every rule's
effect on every recorded arm is exact offline (`tools/stall_report.py`)
— that is the measurement; a live run only proves the implementation
(parity). This module is pure Python shared by both, so the two cannot
disagree by construction.
"""

# pyright: strict

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import delphyne as dp

_OMPHALOS_DIR = Path(__file__).resolve().parent
if str(_OMPHALOS_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(_OMPHALOS_DIR / "tools"))

import pytanque_utils as pt  # noqa: E402
from failure_analysis import refine_class  # noqa: E402

Rule = Literal["noadvance", "samegoal", "seenstate", "sameclass"]
RULES: tuple[Rule, ...] = ("noadvance", "samegoal", "seenstate", "sameclass")
K_GRID: tuple[int, ...] = tuple(range(3, 11))
"""The pre-registered grid: `tools/stall_report.py --tune` selects one
(rule, k) on trainX; nothing outside it is ever chosen."""


@dataclass(frozen=True)
class VerdictView:
    """What a stall rule may look at, per rejected proposal."""

    cls: str
    n_goals: int
    goal_key: str
    prefix_len: int
    failing_index: int

    @property
    def state(self) -> tuple[str, int, str]:
        return (self.cls, self.n_goals, self.goal_key)

    @property
    def goal_state(self) -> tuple[int, str]:
        return (self.n_goals, self.goal_key)


def goal_key(goal: str) -> str:
    """The conclusion of one rendered goal, whitespace-normalised: the
    text after the last `|-`, or the whole goal when there is none."""
    text = goal.rsplit("|-", 1)[-1] if "|-" in goal else goal
    return " ".join(text.split())


def view_of_feedback(fb: pt.Feedback) -> VerdictView | None:
    """`None` for a success (successes end the search anyway)."""
    if fb.success:
        return None
    goals = fb.remaining_goals or []
    return VerdictView(
        cls=refine_class(fb.error_message),
        n_goals=len(goals),
        goal_key=goal_key(goals[0]) if goals else "",
        prefix_len=len(fb.proof_so_far or []),
        failing_index=(
            fb.failing_index if fb.failing_index is not None else -1
        ),
    )


def views_of_prefix(prefix: Sequence[Any]) -> list[VerdictView]:
    """The verdicts an `interact` prefix carries, in order: every
    feedback message whose meta is a verifier `Feedback`."""
    out: list[VerdictView] = []
    for msg in prefix:
        if not isinstance(msg, dp.FeedbackMessage):
            continue
        meta = msg.meta
        if isinstance(meta, pt.Feedback):
            v = view_of_feedback(meta)
            if v is not None:
                out.append(v)
    return out


def _flags(views: Sequence[VerdictView], rule: Rule) -> list[bool]:
    """Per verdict, whether it counts as *no progress* under `rule`."""
    flags: list[bool] = []
    best = -1
    seen: set[tuple[str, int, str]] = set()
    for i, v in enumerate(views):
        if rule == "noadvance":
            flags.append(v.failing_index <= best)
            best = max(best, v.failing_index)
        elif rule == "samegoal":
            flags.append(i > 0 and v.goal_state == views[i - 1].goal_state)
        elif rule == "seenstate":
            flags.append(v.state in seen)
            seen.add(v.state)
        else:
            flags.append(i > 0 and v.cls == views[i - 1].cls)
    return flags


def stalled(views: Sequence[VerdictView], rule: Rule, k: int) -> bool:
    """Whether the last `k` rejections all show no progress."""
    if k <= 0 or len(views) < k:
        return False
    flags = _flags(views, rule)
    return all(flags[-k:])


def stop_after(views: Sequence[VerdictView], rule: Rule, k: int) -> int | None:
    """
    The number of rejected verdicts after which the rule first fires
    (the search then issues no further request), or `None`. Exactly
    what `stalled` decides step by step, so the offline replay and the
    live strategy agree by construction.
    """
    if k <= 0:
        return None
    flags = _flags(views, rule)
    run = 0
    for i, f in enumerate(flags):
        run = run + 1 if f else 0
        if run >= k:
            return i + 1
    return None
