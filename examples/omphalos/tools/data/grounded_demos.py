"""Materialize grounded trainX query examples, with no model calls.

Every positive correction is a freshly checked transition. Resource
abstention is demonstrated by an actual one-RPC operation limit. These
examples teach the new roles only; archived queries keep their examples.
"""

from runtime.paths import OMPHALOS_ROOT

from dataclasses import asdict, replace
import json
from typing import Any
import yaml

import ace.ace_grounded as ag  # noqa: E402
from delphyne.utils.typing import pydantic_load  # noqa: E402
from prove_grounded import GroundedReflection  # noqa: E402
import runtime.pytanque_utils as pt  # noqa: E402
import runtime.skills as sk  # noqa: E402
from runtime.tool_budget import ToolLimits  # noqa: E402

ROOT = OMPHALOS_ROOT


def build() -> None:
    source = (
        ROOT / "experiments/campaigns/ace_bounded_20260908/evidence_v2.json"
    )
    raw = json.loads(source.read_text())
    state = pydantic_load(ag.AdaptationState, raw["state"])
    demos: list[dict[str, Any]] = []

    def add(
        label: str,
        query: str,
        args: dict[str, Any],
        answer: object,
        example: bool = True,
    ) -> None:
        text = (
            answer
            if isinstance(answer, str)
            else "```yaml\n" + yaml.safe_dump(answer, sort_keys=False) + "```"
        )
        demos.append(
            {
                "demonstration": label,
                "query": query,
                "args": args,
                "answers": [{"answer": text, "example": example}],
            }
        )

    for index, claim in enumerate(state.claims[:3]):
        e = claim.evidence
        failed = ag.checked_proof(
            e.problem_file,
            e.theorem_name,
            [*e.prefix, e.failed_action],
            assisted=False,
        )
        solved = (
            ag.checked_proof(
                e.problem_file,
                e.theorem_name,
                list(e.verified_solution),
                assisted=False,
            )
            if e.verified_solution
            else None
        )
        solution = (
            e.verified_solution if solved and solved.feedback.success else ()
        )
        reflection = GroundedReflection(
            e.failed_action,
            "The recorded replacement succeeds at the same verified prefix; its preconditions are local to that state.",
            claim.condition,
            claim.action,
            claim.references,
        )
        add(
            f"grounded_reflection_{index}",
            "ReflectGroundedTransition",
            {
                "evidence": asdict(e),
                "verified_solution": list(solution),
                "feedback": asdict(failed),
            },
            asdict(reflection),
        )
        verdict = next(v for v in state.decisions if v.claim.id == claim.id)
        choice = {
            "keep": True,
            "reason": "The exact action was accepted in the supporting state; retain it only as a local example.",
            "condition": claim.condition,
        }
        add(
            f"grounded_curation_{index}",
            "CurateGroundedClaim",
            {"reflection": asdict(reflection), "verdict": asdict(verdict)},
            choice,
        )
        add(
            f"grounded_audit_{index}",
            "AuditGroundedClaim",
            {"verdict": asdict(verdict), "condition": claim.condition},
            choice,
        )
        # A rejected mixed clause is a counterexample to editorial admission,
        # not a fabricated successful Rocq observation.
        mixed = replace(claim, action=(*claim.action, "norm_num."))
        rejected = ag.validate_claim(mixed)
        add(
            f"grounded_mixed_clause_{index}",
            "AuditGroundedClaim",
            {"verdict": asdict(rejected), "condition": claim.condition},
            {
                "keep": False,
                "reason": "The added alternative has no supporting accepted transition. Keep only the separately verified action.",
                "condition": "",
            },
        )
        if index == 0:
            unavailable = ag.checked_proof(
                e.problem_file,
                e.theorem_name,
                [*e.prefix, e.failed_action],
                limits=ToolLimits(rpc_calls=1),
                assisted=False,
            )
            abstain = GroundedReflection(
                e.failed_action,
                "Verification exhausted its operation allowance; mathematical invalidity is not established.",
                "",
                (),
                (),
                True,
            )
            add(
                "grounded_resource_abstention",
                "ReflectGroundedTransition",
                {
                    "evidence": asdict(e),
                    "verified_solution": [],
                    "feedback": asdict(unavailable),
                },
                asdict(abstain),
            )
        if solution:
            spec = pt.parse_problem(e.problem_file, True)
            args: dict[str, Any] = {
                "spec": asdict(spec),
                "available_skills": sk.list_skills(),
                "toolset": "core",
                "turn_budget": 64,
                "prefix": [],
                "playbook": "",
                "render_version": 3,
                "decision": f"resolve a {claim.kind} decision",
                "verified_prefix": "\n".join(e.prefix),
                "lesson": claim.render(),
            }
            name = {
                "reference": "ResolveProofReference",
                "bridge": "ChooseProofBridge",
                "structure": "ChooseProofStructure",
            }[claim.kind]
            add(
                f"grounded_decision_{index}",
                name,
                args,
                "```rocq\n" + "\n".join(solution) + "\n```",
            )
    target = ROOT / "demos/grounded.demo.yaml"
    target.write_text(
        "# TrainX-only verified examples for the bounded ACE contracts.\n# Generated by tools/data/grounded_demos.py; no paid calls.\n"
        + yaml.safe_dump(demos, sort_keys=False)
    )
    print(f"Wrote {len(demos)} grounded examples")


if __name__ == "__main__":
    build()
