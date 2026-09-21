"""TrainX-only learning roles, kept separate from the Luna solver.

Reflector and Curator are distinct calls; only a deterministic delta merge
updates the playbook. Every role has an explicit model and reasoning effort.
The work allowance (two calls, 16384 output tokens each) is model-independent.
"""

from dataclasses import dataclass

import delphyne as dp

from ace.ace_playbook import AddOp, AuditDecision, BulletTag
from runtime.model_registry import OmphalosReasoningEffort
from runtime.replay_admission import recorded_prompt

from .common import CAMPAIGN
from .solver import audit_model


@dataclass
class Reflection:
    diagnosis: str
    evidence: str
    reusable_lesson: str
    limitations: str
    bullet_tags: list[BulletTag]


@dataclass
class Delta:
    reasoning: str
    operations: list[AddOp]


@dataclass
class Revision:
    reasoning: str
    decisions: list[AuditDecision]


@dataclass
class AuditReflect(dp.Query[Reflection]):
    evidence: str
    playbook: str
    __parser__ = dp.last_code_block.yaml


@dataclass
class AuditCurate(dp.Query[Delta]):
    evidence: str
    reflection: str
    playbook: str
    __parser__ = dp.last_code_block.yaml


@dataclass
class AuditRefine(dp.Query[Revision]):
    evidence: str
    playbook: str
    __parser__ = dp.last_code_block.yaml


@dp.strategy
def audit_reflect(
    evidence: str, playbook: str
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Reflection]:
    return (
        yield from dp.branch(
            AuditReflect(evidence, playbook).using(dp.ambient_pp)
        )
    )


@dp.strategy
def audit_curate(
    evidence: str, reflection: str, playbook: str
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Delta]:
    return (
        yield from dp.branch(
            AuditCurate(evidence, reflection, playbook).using(dp.ambient_pp)
        )
    )


@dp.strategy
def audit_refine(
    evidence: str, playbook: str
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Revision]:
    return (
        yield from dp.branch(
            AuditRefine(evidence, playbook).using(dp.ambient_pp)
        )
    )


def audit_role_policy(
    cell: str, model_name: str, effort: OmphalosReasoningEffort
) -> dp.Policy[dp.Branch, dp.PromptingPolicy]:
    model = audit_model(cell, model_name, effort, 16384)
    normal = dp.few_shot(model, max_requests=2)
    return dp.dfs() & recorded_prompt(
        normal, model, str(CAMPAIGN / "transport" / cell)
    )
