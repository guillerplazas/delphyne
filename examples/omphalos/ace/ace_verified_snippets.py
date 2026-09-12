"""Source-witness checks for executable examples emitted by a reducer.

This is an opt-in reduction contract. A template is checked at explicit
bindings in its source proof, not asserted to work in every future state.
Unchecked paraphrases cannot replace the source-verified executable text.
"""

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import re

from ace import ace_grounded as ag
from ace.ace_evidence import import_signature
from ace.ace_playbook import Bullet, Playbook
from prove_ace import CurationDelta
from experiments.common.ace_pools import POOLS
from runtime import pytanque_utils as pt
from runtime.tool_budget import ToolLimits


@dataclass(frozen=True)
class SnippetWitness:
    identifier: str
    problem_file: str
    theorem_name: str
    source_cell: str
    prefix: str
    template: str
    bindings: dict[str, str]
    suffix: str

    def instantiate(self, template: str) -> str:
        if not self.bindings:
            return template
        pattern = r"\b(?:" + "|".join(map(re.escape, self.bindings)) + r")\b"
        return re.sub(pattern, lambda m: self.bindings[m[0]], template)

    def digest(self) -> str:
        return hashlib.sha256(
            json.dumps(asdict(self), sort_keys=True).encode()
        ).hexdigest()


@dataclass(frozen=True)
class SnippetVerdict:
    source_id: str
    source_sha256: str
    environment: str
    candidate: str
    retained: str
    decision: str
    source_check: ag.Checked
    candidate_check: ag.Checked


@dataclass(frozen=True)
class SnippetBinding:
    """Bind an executable example in one reducer operation to its source."""

    operation: int
    text: str
    source_id: str


def protect_reduction(
    delta: CurationDelta,
    witnesses: dict[str, SnippetWitness],
    bindings: tuple[SnippetBinding, ...],
    limits: ToolLimits = ToolLimits(),
) -> tuple[CurationDelta, tuple[SnippetVerdict, ...]]:
    """An explicit provenance gate before deterministic playbook merging.

    Bindings are required evidence, not guessed from lemma names or citations.
    Unbound prose is outside the verification claim. Returned verdicts must be
    persisted with the reduced delta by the calling adaptation driver.
    """
    operations = list(delta.operations)
    verdicts: list[SnippetVerdict] = []
    for binding in bindings:
        if not 0 <= binding.operation < len(operations):
            raise ValueError("Snippet binding references an absent operation")
        operation = operations[binding.operation]
        if operation.content.count(binding.text) != 1:
            raise ValueError("Snippet binding must identify one exact example")
        verdict = preserve_verified_snippet(
            witnesses[binding.source_id], binding.text, limits
        )
        operations[binding.operation] = replace(
            operation,
            content=operation.content.replace(binding.text, verdict.retained),
        )
        verdicts.append(verdict)
    return replace(delta, operations=operations), tuple(verdicts)


def preserve_verified_snippet(
    witness: SnippetWitness,
    candidate: str,
    limits: ToolLimits = ToolLimits(),
) -> SnippetVerdict:
    if POOLS["trainX"].get(witness.theorem_name) != (
        witness.problem_file,
        witness.theorem_name,
    ):
        raise ValueError("Snippet evidence must come from trainX")

    def check(code: str) -> ag.Checked:
        script = "\n".join(
            (witness.prefix, witness.instantiate(code), witness.suffix)
        )
        return ag.checked_proof(
            witness.problem_file,
            witness.theorem_name,
            pt.split_into_tactics(script),
            limits,
            assisted=False,
        )

    source = check(witness.template)
    if not source.feedback.success:
        raise ValueError("The claimed source snippet does not verify")
    proposed = source if candidate == witness.template else check(candidate)
    accepted = proposed.feedback.success
    return SnippetVerdict(
        witness.identifier,
        witness.digest(),
        import_signature(witness.problem_file),
        candidate,
        candidate if accepted else witness.template,
        "replacement_verified" if accepted else "source_preserved",
        source,
        proposed,
    )


def replace_book_snippet(
    book: Playbook,
    bullet_id: str,
    original: str,
    verdict: SnippetVerdict,
) -> Playbook:
    """Change one explicitly bound example; keep every other byte of content."""
    if (
        verdict.candidate != original
        or not verdict.source_check.feedback.success
    ):
        raise ValueError("Snippet provenance does not match the replacement")
    bullets: list[Bullet] = []
    replaced = False
    for bullet in book.bullets:
        if bullet.id == bullet_id:
            if bullet.content.count(original) != 1:
                raise ValueError("Snippet binding must be unique")
            bullet = replace(
                bullet,
                content=bullet.content.replace(original, verdict.retained),
            )
            replaced = True
        bullets.append(bullet)
    if not replaced:
        raise ValueError("Unknown bullet identifier")
    return replace(book, bullets=bullets)
