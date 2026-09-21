"""Role parsing that preserves nested Rocq fences in YAML block scalars.

Same instructions and schemas as v2. The outer YAML fence, rather than an
inner code example, determines the serialization boundary. Old role queries
and recorded results remain unchanged.
"""

from dataclasses import dataclass
import re

import delphyne as dp
from delphyne.stdlib.queries import get_text

from .learning import (
    AuditReflect,
    AuditCurate,
    AuditRefine,
    Reflection,
    Delta,
    Revision,
)


def outer_yaml(text: str) -> str:
    starts = list(
        re.finditer(r"(?m)^(`{3,}|~{3,})(?:yaml|yml|json)[ \t]*\r?$", text)
    )
    for start in reversed(starts):
        fence = start.group(1)
        after = text[start.end() :].lstrip("\r\n")
        closing = re.search(
            r"(?m)^"
            + re.escape(fence[0])
            + "{"
            + str(len(fence))
            + r",}[ \t]*\r?$",
            after,
        )
        if closing:
            return after[: closing.start()]
    raise ValueError("Expected a complete outer YAML fence at column zero")


@dataclass
class AuditReflectV3(AuditReflect):
    __parser__ = get_text.map(outer_yaml, catch_exn=True).yaml


@dataclass
class AuditCurateV3(AuditCurate):
    __parser__ = get_text.map(outer_yaml, catch_exn=True).yaml


@dataclass
class AuditRefineV3(AuditRefine):
    __parser__ = get_text.map(outer_yaml, catch_exn=True).yaml


@dp.strategy
def audit_reflect_v3(
    evidence: str, playbook: str
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Reflection]:
    return (
        yield from dp.branch(
            AuditReflectV3(evidence, playbook).using(dp.ambient_pp)
        )
    )


@dp.strategy
def audit_curate_v3(
    evidence: str, reflection: str, playbook: str
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Delta]:
    return (
        yield from dp.branch(
            AuditCurateV3(evidence, reflection, playbook).using(dp.ambient_pp)
        )
    )


@dp.strategy
def audit_refine_v3(
    evidence: str, playbook: str
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, Revision]:
    return (
        yield from dp.branch(
            AuditRefineV3(evidence, playbook).using(dp.ambient_pp)
        )
    )
