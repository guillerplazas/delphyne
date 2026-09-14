"""Context-bound Rocq snippet checks, independent of an agent harness.

Each check is one bounded computation. Fragments are sent verbatim, without
the legacy proof extractor which intentionally discards unfinished tails.
An executed fragment is evidence about one context, not a finished theorem.
"""

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from typing import Literal

import delphyne as dp

from ace import ace_grounded as ag
from ace.ace_evidence import import_signature
from runtime import pytanque_utils as pt
from runtime.admission_events import record
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.tool_budget import ToolLimits, clip_utf8


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


@dataclass(frozen=True)
class SnippetContext:
    problem_file: str
    theorem_name: str
    prefix: tuple[str, ...]
    source: str
    problem_sha256: str
    environment: str
    version: int = 1

    @property
    def identifier(self) -> str:
        return "ctx-" + digest(asdict(self))[:24]


def context_for(
    problem_file: str,
    theorem_name: str,
    prefix: tuple[str, ...] = (),
    source: str = "runtime",
) -> SnippetContext:
    path = ROOT / problem_file
    return SnippetContext(
        problem_file,
        theorem_name,
        prefix,
        source,
        hashlib.sha256(path.read_bytes()).hexdigest(),
        import_signature(problem_file) + repr(pt.DEFAULT_EXTRA_IMPORTS),
    )


@dataclass
class CheckRocqSnippet(dp.AbstractTool[str]):
    """Execute an exact Rocq snippet in a supplied context before reusing it.

    Use a context_id from this conversation; never invent one. Supply complete
    Rocq sentences, without Markdown or Proof/Qed wrappers. Unknown syntax and
    names return Rocq errors. An executed fragment may still leave obligations
    open. Reuse the returned context_id to extend that fragment. A completed
    proof is accepted immediately. Do not repeat identical probes.
    """

    context_id: str
    snippet: str


SnippetStatus = Literal[
    "executed_open", "completed", "rejected", "resource_exhausted", "unknown"
]


@dataclass(frozen=True)
class SnippetReceipt:
    context: SnippetContext
    snippet: str
    status: SnippetStatus
    checked: ag.Checked
    elapsed: float
    rpc_calls: int

    @property
    def identifier(self) -> str:
        # Timing is not part of the evidence identity.
        return (
            "snippet-"
            + digest(
                (
                    self.context.identifier,
                    self.snippet,
                    self.status,
                    asdict(self.checked.feedback),
                )
            )[:24]
        )

    @property
    def executable(self) -> bool:
        return self.status in ("executed_open", "completed")

    def successor(self) -> SnippetContext:
        if not self.executable:
            raise ValueError("Rejected snippet has no successor context")
        return replace(
            self.context, prefix=tuple(self.checked.feedback.proof_so_far)
        )

    def render(self, limit: int = 8192) -> str:
        return clip_utf8(
            json.dumps(
                dict(
                    receipt_id=self.identifier,
                    status=self.status,
                    context_id=self.successor().identifier
                    if self.executable
                    else None,
                    scope="Exact snippet in this source context; no general validity claim",
                    accepted_prefix=self.checked.feedback.proof_so_far,
                    error=self.checked.feedback.error_message,
                    failing_tactic=self.checked.feedback.failing_tactic,
                    remaining_goals=self.checked.feedback.remaining_goals[:4],
                    elapsed=self.elapsed,
                    rpc_calls=self.rpc_calls,
                ),
                ensure_ascii=False,
            ),
            limit,
        )


def check_snippet(
    context: SnippetContext, snippet: str, limits: dict[str, float | int]
) -> SnippetReceipt:
    expected = context_for(
        context.problem_file,
        context.theorem_name,
        context.prefix,
        context.source,
    )
    if expected != context:
        raise ValueError("Snippet context source/environment drift")
    bounds = ToolLimits(**limits)  # type: ignore[arg-type]
    if not snippet.strip() or "```" in snippet:
        fb = pt.Feedback(
            False, 0, "snippet", "Supply raw, nonempty Rocq sentences."
        )
        checked = ag.Checked(fb, "rejected", 0, 0, "")
    else:
        # One raw chunk: no silent removal of malformed trailing input.
        checked = ag.checked_proof(
            context.problem_file,
            context.theorem_name,
            [*context.prefix, snippet],
            bounds,
            assisted=False,
        )
    all_executed = checked.feedback.proof_so_far == [*context.prefix, snippet]
    status: SnippetStatus
    if checked.feedback.success and all_executed:
        status = "completed"
    elif (
        all_executed
        and checked.feedback.failing_tactic == "Qed."
        and checked.outcome in ("incomplete", "rejected")
    ):
        status = "executed_open"
    elif checked.outcome in ("unknown", "resource_exhausted"):
        status = checked.outcome
    else:
        status = "rejected"
    receipt = SnippetReceipt(
        context, snippet, status, checked, checked.elapsed, checked.rpc_calls
    )
    record(
        "snippet",
        status,
        receipt=receipt.identifier,
        context=context.identifier,
        snippet=snippet,
        elapsed=receipt.elapsed,
        rpc_calls=receipt.rpc_calls,
    )
    return receipt


def context_catalog(contexts: tuple[SnippetContext, ...]) -> str:
    return json.dumps(
        [
            dict(
                context_id=c.identifier,
                theorem=c.theorem_name,
                verified_prefix=c.prefix,
                source=c.source,
            )
            for c in contexts
        ],
        ensure_ascii=False,
    )
