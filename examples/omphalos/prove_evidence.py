"""Opt-in ACE evidence contracts, shared by Codex and Claude Code.

Include this module in ExecutionContext.modules. No baseline query, book or
paid campaign is upgraded implicitly. Drivers persist returned receipts and
protected deltas before merging them with ace_playbook.merge.
"""

from dataclasses import dataclass

import delphyne as dp

from ace.ace_playbook import AddOp
from ace.ace_verified_snippets import (
    SnippetBinding,
    SnippetVerdict,
    SnippetWitness,
    protect_reduction,
)
from ace.terminal_evidence import TerminalEvidence
from prove_ace import CurationDelta, Reflection, ReflectOnTrajectory
from runtime import pytanque_utils as pt
from runtime.tool_budget import ToolLimits


@dataclass
class ReflectOnTrajectoryV2(ReflectOnTrajectory):
    terminal: TerminalEvidence


@dp.strategy
def reflect_on_trajectory_v2(
    problem_file: str,
    outcome: str,
    playbook: str,
    trajectory: str,
    terminal: TerminalEvidence,
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Reflection]:
    spec = pt.parse_problem(problem_file)
    if terminal.version != 2 or terminal.theorem_name != spec.theorem_name:
        raise ValueError("Terminal evidence/query mismatch")
    from pathlib import Path
    from runtime.paths import OMPHALOS_ROOT

    if (OMPHALOS_ROOT / terminal.problem_file).resolve() != (
        OMPHALOS_ROOT / Path(problem_file)
    ).resolve():
        raise ValueError("Terminal evidence environment mismatch")
    return (
        yield from dp.branch(
            ReflectOnTrajectoryV2(
                spec, outcome, playbook, trajectory, terminal
            ).using(dp.ambient_pp)
        )
    )


@dataclass(frozen=True)
class BoundCurationDelta:
    reasoning: str
    operations: tuple[AddOp, ...]
    bindings: tuple[SnippetBinding, ...]
    dropped_sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProtectedCuration:
    delta: CurationDelta
    bindings: tuple[SnippetBinding, ...]
    verdicts: tuple[SnippetVerdict, ...]
    dropped_sources: tuple[str, ...]


@dataclass
class CurateCheckedPlaybook(dp.Query[BoundCurationDelta]):
    playbook: str
    reflection: Reflection
    witnesses: tuple[SnippetWitness, ...]

    __parser__ = dp.last_code_block.yaml


@dataclass
class ReduceCheckedDeltas(dp.Query[BoundCurationDelta]):
    playbook: str
    deltas: tuple[ProtectedCuration, ...]
    witnesses: tuple[SnippetWitness, ...]

    __parser__ = dp.last_code_block.yaml


def protect_bound_delta(
    proposed: BoundCurationDelta,
    witnesses: tuple[SnippetWitness, ...],
    required_sources: tuple[str, ...],
    limits: ToolLimits,
) -> ProtectedCuration:
    bank = {w.identifier: w for w in witnesses}
    if len(bank) != len(witnesses):
        raise ValueError("Duplicate witness identifiers")
    bound = {b.source_id for b in proposed.bindings}
    dropped = set(proposed.dropped_sources)
    if (
        not (bound | dropped | set(required_sources)) <= bank.keys()
        or bound & dropped
        or not set(required_sources) <= bound | dropped
        or len(dropped) != len(proposed.dropped_sources)
    ):
        raise ValueError("Missing, conflicting or unknown snippet provenance")
    if len({(b.operation, b.text) for b in proposed.bindings}) != len(
        proposed.bindings
    ):
        raise ValueError("Duplicate executable binding")
    delta, verdicts = protect_reduction(
        CurationDelta(proposed.reasoning, list(proposed.operations)),
        bank,
        proposed.bindings,
        limits,
    )
    bindings = tuple(
        SnippetBinding(b.operation, v.retained, b.source_id)
        for b, v in zip(proposed.bindings, verdicts, strict=True)
    )
    return ProtectedCuration(
        delta, bindings, verdicts, proposed.dropped_sources
    )


@dp.strategy
def curate_checked_playbook(
    playbook: str,
    reflection: Reflection,
    witnesses: tuple[SnippetWitness, ...],
    limits: ToolLimits = ToolLimits(),
) -> dp.Strategy[
    dp.Branch | dp.Compute, dp.PromptingPolicy, ProtectedCuration
]:
    proposed = yield from dp.branch(
        CurateCheckedPlaybook(playbook, reflection, witnesses).using(
            dp.ambient_pp
        )
    )
    return (
        yield from dp.compute(protect_bound_delta)(
            proposed, witnesses, tuple(w.identifier for w in witnesses), limits
        )
    )


@dp.strategy
def reduce_checked_deltas(
    playbook: str,
    deltas: tuple[ProtectedCuration, ...],
    witnesses: tuple[SnippetWitness, ...],
    limits: ToolLimits = ToolLimits(),
) -> dp.Strategy[
    dp.Branch | dp.Compute, dp.PromptingPolicy, ProtectedCuration
]:
    required = tuple(sorted({b.source_id for d in deltas for b in d.bindings}))
    proposed = yield from dp.branch(
        ReduceCheckedDeltas(playbook, deltas, witnesses).using(dp.ambient_pp)
    )
    return (
        yield from dp.compute(protect_bound_delta)(
            proposed, witnesses, required, limits
        )
    )
