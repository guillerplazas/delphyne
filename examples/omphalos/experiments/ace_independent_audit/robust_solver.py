"""Fresh, matched solver contract with typed transport failure feedback.

Ordinary templates, tools and proof acceptance remain unchanged. A Rocq
transport exception cannot count as a proof; it becomes explicit feedback
instead of aborting a paid trajectory. Frozen source/pilot strategies keep
their original behavior. No generic token, goal or history limits are added.
"""

import delphyne as dp

from prove_ace import ProposeProofScriptACE
from prove_agentic import (
    ReadSkill,
    SearchRocq,
    _read_skill_handler,  # pyright: ignore[reportPrivateUsage]
    _search_rocq_handler,  # pyright: ignore[reportPrivateUsage]
)
from runtime import pytanque_utils as pt, skills as sk
from runtime.rocq_server import TransportError

from .solver import AuditPlainProof


def checked(
    file: str, theorem_name: str, tactics: list[str], assisted: bool
) -> pt.Feedback:
    try:
        return pt.check(file, theorem_name, tactics, probe_automation=assisted)
    except TransportError as exc:
        return pt.Feedback(
            success=False,
            error_message=f"Verifier transport failure ({type(exc).__name__}): {exc}. This is not a logical rejection; no proof was certified.",
        )


@dp.strategy
def checked_script(
    file: str, theorem_name: str, script: str, assisted: bool
) -> dp.Strategy[dp.Compute, object, str | dp.Error]:
    tactics = yield from dp.compute(pt.split_into_tactics)(script)
    feedback = yield from dp.compute(checked)(
        file, theorem_name, tactics, assisted
    )
    if feedback.success:
        return (
            "\n".join(feedback.proof_so_far)
            if feedback.auto_finished
            else script
        )
    if feedback.failing_tactic == "Qed." and feedback.remaining_goals:
        return dp.Error(label="incomplete", meta=feedback)
    return dp.Error(label="feedback", meta=feedback)


@dp.strategy
def audit_robust_solver(
    problem_file: str,
    theorem_name: str,
    assisted: bool,
    playbook: str = "",
    turn_budget: int = 32,
    show_definitions: bool = True,
    render_version: int = 2,
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, str]:
    spec = pt.parse_problem(problem_file, show_definitions)
    available = sk.list_skills()
    query_type = ProposeProofScriptACE if assisted else AuditPlainProof
    return (
        yield from dp.interact(
            step=lambda prefix, _: query_type(
                spec,
                available,
                "core",
                turn_budget,
                prefix,
                playbook,
                render_version,
            ).using(dp.ambient_pp),
            process=lambda script, _: checked_script(
                problem_file, theorem_name, script, assisted
            ).using(dp.just_compute),
            tools={
                ReadSkill: lambda call: _read_skill_handler(
                    call.skill_name
                ).using(dp.just_compute),
                SearchRocq: lambda call: _search_rocq_handler(
                    problem_file, theorem_name, call.command
                ).using(dp.just_compute),
            },
        )
    )
