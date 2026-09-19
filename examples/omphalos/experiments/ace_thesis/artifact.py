"""Immutable, context-bound examples attached to an incremental ACE book.

An executable snippet certifies one recorded context, not a general rule.
Rendering exposes the exact prefix, prerequisites and observed outcome.
The size limit omits whole examples and never cuts a Rocq sentence.
"""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from delphyne.utils.typing import pydantic_load

from ace.ace_playbook import Playbook
from ace.ace_grounded import inspect_proof_state
from ace.rocq_snippets import SnippetReceipt, check_snippet
from experiments.ace_sanitized.scope import partition
from runtime.tool_budget import ToolLimits

CONTEXT_BYTES = 32 * 1024
NOTICE = (
    "\n\n### Checked source examples\n"
    "These examples execute in their recorded source contexts only. "
    "Adapt names and check prerequisites in the current theorem. "
    "executed_open means obligations remain; only completed means the "
    "source theorem was closed by Qed.\n"
)


def fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Example:
    rule_id: str
    receipt: SnippetReceipt
    prerequisite_state: str
    provenance: str

    @property
    def identifier(self) -> str:
        return (
            "example-"
            + fingerprint((self.rule_id, self.receipt.identifier))[:24]
        )

    def render(self) -> str:
        r = self.receipt
        return (
            f"\n[{self.identifier}] Rule {self.rule_id}; "
            f"source {r.context.theorem_name}; receipt {r.identifier}\n"
            f"Verified source prefix:\n```coq\n"
            + "\n".join(r.context.prefix)
            + "\n```\nPrerequisites and goals in that source:\n"
            + self.prerequisite_state
            + f"\nExact checked snippet:\n```coq\n{r.snippet}\n```\n"
            + f"Observed outcome: {r.status}.\n"
            + "Remaining obligations: "
            + json.dumps(
                r.checked.feedback.remaining_goals, ensure_ascii=False
            )
            + "\n"
        )


@dataclass(frozen=True)
class ContextArtifact:
    book: Playbook
    examples: tuple[Example, ...] = ()
    lineage: tuple[str, ...] = ()

    def rendered(self, ceiling: int = CONTEXT_BYTES) -> dict[str, Any]:
        text = self.book.render_prompt()
        if len(text.encode()) > ceiling:
            raise ValueError("Book alone exceeds the context ceiling")
        known = {b.id for b in self.book.bullets}
        ids: set[str] = set()
        included: list[str] = []
        omitted: list[str] = []
        for e in sorted(self.examples, key=lambda e: e.identifier):
            if e.rule_id not in known or not e.receipt.executable:
                raise ValueError("Example lacks an existing rule or evidence")
            if e.identifier in ids:
                raise ValueError("Duplicate example identity")
            ids.add(e.identifier)
            addition = (NOTICE if not included else "") + e.render()
            if len((text + addition).encode()) <= ceiling:
                text += addition
                included.append(e.identifier)
            else:
                omitted.append(e.identifier)
        return dict(
            text=text,
            bytes=len(text.encode()),
            included=included,
            omitted=omitted,
            ceiling=ceiling,
        )

    def sha256(self) -> str:
        return fingerprint(asdict(self))

    @staticmethod
    def load(path: Path) -> "ContextArtifact":
        artifact = pydantic_load(ContextArtifact, json.loads(path.read_text()))
        artifact.rendered()
        return artifact


def checked_example(
    rule_id: str,
    receipt: SnippetReceipt,
    provenance: str,
) -> Example:
    """Re-execute historical evidence and expose the actual local context."""
    ctx = receipt.context
    if partition("train").get(ctx.theorem_name) != ctx.problem_file:
        raise ValueError("Only trainX may supply learned examples")
    fresh = check_snippet(
        ctx,
        receipt.snippet,
        dict(seconds=60, rpc_calls=512, view_bytes=32768),
    )
    if not fresh.executable or fresh.status != receipt.status:
        raise ValueError("Example did not reproduce its execution status")
    pages: list[dict[str, Any]] = []
    start = 0
    while True:
        view = inspect_proof_state(
            ctx.problem_file,
            ctx.theorem_name,
            "\n".join(ctx.prefix),
            start=start,
            limits=ToolLimits(60, 512, 32768),
        )
        if view.outcome != "accepted":
            raise ValueError("Example prerequisites could not be inspected")
        page = json.loads(view.text)
        pages.append(page)
        if page.get("next") is None:
            break
        start = int(page["next"])
    return Example(
        rule_id,
        fresh,
        json.dumps(pages, ensure_ascii=False),
        provenance,
    )
