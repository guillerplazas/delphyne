"""Receipt-disposition repair for the opt-in draft writer.

Rejected attempts may be explicitly dropped, never retained. Unknown IDs still
fail. The first paid writer implementation remains frozen in its own module.
"""

from dataclasses import asdict, dataclass, replace
from typing import Literal, cast

import delphyne as dp

from ace.rocq_snippets import SnippetReceipt, SnippetContext, check_snippet
from prove_snippets import CheckedWriting, SnippetAdvice
from prove_writer_drafts import (
    DraftWriting,
    UnverifiedSnippetDraft,
    validate_decisions,
)
from runtime.admission_events import record
from prove_ace import CurationDelta
from prove_snippets import compile_advice
from prove_writer_drafts import DraftAdvice, WriteRocqDraftAdvice


@dataclass
class WriteRocqReceiptAdvice(WriteRocqDraftAdvice):
    @property
    def disposition_catalog(self) -> str:
        executable = [r.identifier for r in self.receipts if r.executable]
        rejected = [r.identifier for r in self.receipts if not r.executable]
        return (
            f"Executable IDs (retain or drop exactly once): {executable}\n"
            f"Failed attempt IDs (optional drop only, never retain): {rejected}\n"
            f"Required draft decisions: {[d.draft_id for d in self.drafts]}"
        )


def compile_receipt_advice(
    role: str, answer: DraftAdvice, receipts: tuple[SnippetReceipt, ...]
) -> CurationDelta:
    known = {r.identifier for r in receipts}
    drops = answer.dropped_receipts
    if len(set(drops)) != len(drops) or not set(drops) <= known:
        raise ValueError(
            "Dropped IDs must be known receipts, without duplicates"
        )
    executable = {r.identifier for r in receipts if r.executable}
    filtered = replace(
        answer, dropped_receipts=tuple(i for i in drops if i in executable)
    )
    if role not in ("curator", "reducer"):
        raise ValueError("Unsupported writing role")
    return compile_advice(role, filtered, receipts)


@dp.strategy
def write_rocq_receipts(
    role: Literal["curator", "reducer"],
    evidence: str,
    playbook: str,
    contexts: tuple[SnippetContext, ...],
    drafts: tuple[UnverifiedSnippetDraft, ...],
    receipts: tuple[SnippetReceipt, ...] = (),
) -> dp.Strategy[
    dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, DraftWriting
]:
    from experiments.common.ace_pools import POOLS

    if role not in ("curator", "reducer"):
        raise ValueError("Draft writing supports curator/reducer")
    bank = {c.identifier: c for c in contexts}
    if any(
        POOLS["trainX"].get(c.theorem_name) != (c.problem_file, c.theorem_name)
        for c in contexts
    ):
        raise ValueError("Writing evidence must be trainX")
    if len({d.draft_id for d in drafts}) != len(drafts) or any(
        d.context_id not in bank
        or not d.proposed_code.strip()
        or not d.source.strip()
        for d in drafts
    ):
        raise ValueError(
            "Drafts require unique IDs, raw code and supplied source contexts"
        )
    if any(r.context.identifier not in bank for r in receipts):
        raise ValueError("Inherited receipt has no source context")
    verified = {r.identifier: r for r in receipts}
    seen = {(r.context.identifier, r.snippet): r for r in receipts}
    dialogue: list[dp.AnswerPrefixElement] = []
    probes, spent = 0, 0.0
    for turn in range(4):
        response = yield from dp.branch(
            WriteRocqReceiptAdvice(
                role,
                evidence,
                playbook,
                tuple(bank.values()),
                tuple(verified.values()),
                tuple(dialogue),
                turn < 3 and probes < 3,
                drafts,
            ).using(dp.ambient_pp)
        )
        dialogue.append(dp.OracleMessage("oracle", response.answer))
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                key = (call.context_id, call.snippet)
                if turn == 3 or probes >= 3:
                    result = "Probe limit reached; return final YAML."
                elif call.context_id not in bank:
                    result = (
                        "Unknown context ID; choose a supplied source context."
                    )
                elif key in seen:
                    result = seen[key].render()
                else:
                    checked = yield from dp.compute(check_snippet)(
                        bank[call.context_id],
                        call.snippet,
                        dict(
                            seconds=min(60.0, 180.0 - spent),
                            rpc_calls=512,
                            view_bytes=8192,
                        ),
                    )
                    spent += checked.elapsed
                    seen[key] = checked
                    verified[checked.identifier] = checked
                    if checked.executable:
                        successor = checked.successor()
                        bank[successor.identifier] = successor
                    result = checked.render()
                probes += 1
                dialogue.append(
                    dp.ToolResult(
                        "tool", response.answer.tool_calls[i], result
                    )
                )
            continue
        answer = response.parsed.final
        try:
            if isinstance(answer, dp.WrappedParseError):
                raise ValueError(str(answer.error))
            answer = cast(DraftAdvice, answer)
            delta = compile_receipt_advice(
                role, answer, tuple(verified.values())
            )
            validate_decisions(
                answer, drafts, tuple(verified.values()), contexts
            )
        except ValueError as exc:
            dialogue.append(
                dp.FeedbackMessage(
                    "feedback",
                    "invalid_draft_decisions",
                    str(exc)
                    + "\n"
                    + WriteRocqReceiptAdvice(
                        role,
                        evidence,
                        playbook,
                        tuple(bank.values()),
                        tuple(verified.values()),
                        drafts=drafts,
                    ).disposition_catalog,
                )
            )
            continue
        record(
            "draft_writer",
            "completed",
            role=role,
            operations=len(delta.operations),
            decisions=[asdict(d) for d in answer.decisions],
        )
        return DraftWriting(
            CheckedWriting(role, answer, delta, tuple(verified.values())),
            drafts,
            answer.decisions,
        )
    yield from dp.fail(label="draft_writer_contract_unfinished")
    return DraftWriting(
        CheckedWriting(
            role, SnippetAdvice("unreachable"), CurationDelta("", []), ()
        ),
        drafts,
        (),
    )
