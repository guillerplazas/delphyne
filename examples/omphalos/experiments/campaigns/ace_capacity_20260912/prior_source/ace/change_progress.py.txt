"""Conservative, offline focused-obligation scoring; never a runtime tool.

A closed fresh nested assertion or a shelved goal earns no useful progress.
Unrecognized focus/evar manipulation is unscored unless the full proof checks.
"""

from dataclasses import dataclass
import re

import ace.ace_applicability as aa
import ace.ace_grounded as ag
import runtime.pytanque_utils as pt
import runtime.rocq_server as rs
from runtime.paths import OMPHALOS_ROOT
from runtime.tool_budget import ToolLimits, operation


@dataclass(frozen=True)
class ProgressAudit:
    useful: bool
    outcome: str
    reason: str
    elapsed: float
    rpc_calls: int
    closed_at: int | None = None


# These can hide, reorder or postpone obligations without proving them.
_FOCUS = re.compile(
    r"\b(?:shelve|shelve_unifiable|give_up|admit|Admitted|Abort|"
    r"Focus|Unfocus|Unshelve|cycle|swap|rotate|evar|instantiate|"
    r"existential|Grab|abstract)\b|(?:^|[;{}])\s*(?:[-+*]+\s|\d+\s*:|all\s*:)",
    re.M,
)


def audit_progress(
    state: aa.RepairState,
    checked: ag.Checked,
    limits: ToolLimits = ToolLimits(seconds=10),
) -> ProgressAudit:
    """Replay the verified suffix, looking for closure at original depth.

    Whole-proof success is checked independently by the ordinary checker.
    Partial evidence must retain the exact prefix. Each tactic is inspected,
    so nested focus cannot disappear between snapshots unnoticed.
    """
    if checked.outcome in ("unknown", "resource_exhausted"):
        return ProgressAudit(False, checked.outcome, "unavailable", 0, 0)
    proof = checked.feedback.proof_so_far
    if proof[: len(state.prefix)] != list(state.prefix):
        return ProgressAudit(False, "unsupported", "changed prefix", 0, 0)
    if checked.feedback.success and checked.outcome == "accepted":
        return ProgressAudit(True, "accepted", "full proof checked", 0, 0)
    suffix = proof[len(state.prefix) :]
    if not suffix:
        return ProgressAudit(False, "incomplete", "no continuation", 0, 0)
    text = "\n".join(suffix)
    if _FOCUS.search(text) or "(*" in text:
        return ProgressAudit(
            False, "unsupported", "ambiguous focus/evar manipulation", 0, 0
        )
    focus_depth = int(suffix[0].lstrip().startswith("{"))
    depth = 0
    with operation(limits) as op:
        try:
            file = str((OMPHALOS_ROOT / state.problem_file).resolve())
            augmented = rs.augmented_path(file, pt.DEFAULT_EXTRA_IMPORTS)
            with rs.MANAGER.session(augmented) as client:
                replay = pt._open_and_replay(  # pyright: ignore[reportPrivateUsage]
                    client,
                    augmented,
                    state.theorem_name,
                    list(state.prefix),
                    stop_when_finished=False,
                    timeout=pt.PROOF_TACTIC_TIMEOUT,
                )
                if replay.state is None or replay.failing_index is not None:
                    raise ValueError("original prefix did not replay")
                current = replay.state
                before = client.run(current, "Show Existentials.")
                original_evars = set(
                    re.findall(
                        r"Existential\s+\d+\s*=\s*(\?[^\s:]+)",
                        "\n".join(t for _, t in before.feedback),
                    )
                )
                for index, tactic in enumerate(suffix):
                    tokens = aa.syntax_tokens(tactic)
                    depth += tokens.count("{") - tokens.count("}")
                    current = pt._run_guarded(  # pyright: ignore[reportPrivateUsage]
                        client, current, tactic, pt.PROOF_TACTIC_TIMEOUT
                    )
                    goals = client.goals(current)
                    if not goals and depth <= focus_depth:
                        # Fresh unresolved existentials must not masquerade
                        # as closure, even when the focused goals are empty.
                        existential = client.run(current, "Show Existentials.")
                        output = "\n".join(t for _, t in existential.feedback)
                        remaining_evars = set(
                            re.findall(
                                r"Existential\s+\d+\s*=\s*(\?[^\s:]+)", output
                            )
                        )
                        if not remaining_evars < original_evars:
                            return ProgressAudit(
                                False,
                                "unsupported",
                                "unresolved existentials",
                                op.elapsed,
                                op.calls,
                            )
                        return ProgressAudit(
                            True,
                            "verified",
                            "original focus discharged",
                            op.elapsed,
                            op.calls,
                            len(state.prefix) + index,
                        )
        except Exception as exc:
            return ProgressAudit(
                False, "unavailable", str(exc), op.elapsed, op.calls
            )
        return ProgressAudit(
            False,
            "incomplete",
            "no verified focus closure",
            op.elapsed,
            op.calls,
        )
