"""Matched ordinary agentic contracts; only context and checking vary."""

from dataclasses import dataclass, fields

import delphyne as dp

from prove_ace import ProposeProofScriptACE, _ace_examples  # pyright: ignore[reportPrivateUsage]
from prove_agentic import (
    ReadSkill,
    SearchRocq,
    _read_skill_handler,  # pyright: ignore[reportPrivateUsage]
    _search_rocq_handler,  # pyright: ignore[reportPrivateUsage]
)
from prove_standard import check_proof
from runtime import pytanque_utils as pt, skills as sk
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import make_model, OmphalosReasoningEffort
from runtime.replay_admission import recorded_prompt, admission_observer

from .common import CAMPAIGN
from .transport import AuditModel


@dataclass
class AuditPlainProof(ProposeProofScriptACE):
    """Original query contract, with accurate plain-verifier instructions."""


@dp.strategy
def audit_plain_solver(
    problem_file: str,
    theorem_name: str,
    playbook: str = "",
    turn_budget: int = 32,
    show_definitions: bool = True,
    render_version: int = 2,
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, str]:
    spec = pt.parse_problem(problem_file, show_definitions)
    available = sk.list_skills()
    return (
        yield from dp.interact(
            step=lambda prefix, _: AuditPlainProof(
                spec,
                available,
                "core",
                turn_budget,
                prefix,
                playbook,
                render_version,
            ).using(dp.ambient_pp),
            process=lambda s, _: check_proof(
                problem_file, theorem_name, s
            ).using(dp.just_compute),
            tools={
                ReadSkill: lambda c: _read_skill_handler(c.skill_name).using(
                    dp.just_compute
                ),
                SearchRocq: lambda c: _search_rocq_handler(
                    problem_file, theorem_name, c.command
                ).using(dp.just_compute),
            },
        )
    )


def audit_model(
    cell: str,
    model_name: str = "gpt-5.6-luna",
    effort: OmphalosReasoningEffort = "medium",
    output_tokens: int = 32768,
) -> AuditModel:
    original = make_model(
        model_name,
        for_tool_calls=True,
        api="responses",
        reasoning_effort=effort,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Independent campaign ledger is required")
    values = {
        f.name: getattr(original, f.name) for f in fields(original) if f.init
    }
    values.update(
        output_limit=output_tokens,
        estimate_dollars=False,
        halt_on_billing_issue=True,
    )
    return AuditModel(
        **values,
        evidence_directory=str(CAMPAIGN / "responses" / cell),
        pause_file=str(CAMPAIGN / "PAUSED"),
    )


def audit_solver_policy(
    cell: str, output_tokens: int = 32768
) -> dp.Policy[dp.Branch, dp.PromptingPolicy]:
    model = audit_model(cell, output_tokens=output_tokens)
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=_ace_examples(),
        tag_user_feedback_messages=True,
    )
    limits = dict(price=0.10, num_requests=32)
    return (
        dp.with_budget(dp.BudgetLimit(limits))
        @ admission_observer(limits)
        @ (
            dp.dfs()
            & recorded_prompt(
                normal, model, str(CAMPAIGN / "transport" / cell)
            )
        )
    )
