"""Opt-in draft-aware ACE curator/reducer, shared by both agent harnesses.

Drafts are evidence to inspect, never certificates. Queries choose repairs or
reasoned drops; bounded Compute checks and compile_advice enforce provenance.
The measured v1 writer remains unchanged.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass
import json
from typing import Any, Literal, Never, cast

import delphyne as dp
from delphyne.stdlib.queries import ExampleSelector, SelectedExample

from ace.rocq_snippets import (
    CheckRocqSnippet,
    SnippetContext,
    SnippetReceipt,
    check_snippet,
)
from prove_ace import CurationDelta
from prove_grounded import grounded_search
from prove_snippets import (
    CheckedWriting,
    SnippetAdvice,
    WriteCheckedRocqAdvice,
    compile_advice,
    example_families,
)
from runtime.admission_events import record
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import make_model
from runtime.replay_admission import (
    admission_observer,
    recorded_model,
    recorded_prompt,
)


@dataclass(frozen=True)
class UnverifiedSnippetDraft:
    draft_id: str
    context_id: str
    proposed_code: str
    purpose: str
    source: str
    error: str = ""
    remaining_goals: tuple[str, ...] = ()


@dataclass(frozen=True)
class DraftDecision:
    draft_id: str
    action: Literal["retain", "drop"]
    reason: str
    receipts: tuple[str, ...] = ()


@dataclass(frozen=True)
class DraftAdvice(SnippetAdvice):
    decisions: tuple[DraftDecision, ...] = ()


@dataclass(frozen=True)
class DraftWriting:
    checked: CheckedWriting
    drafts: tuple[UnverifiedSnippetDraft, ...]
    decisions: tuple[DraftDecision, ...]


@dataclass
class WriteRocqDraftAdvice(WriteCheckedRocqAdvice):
    drafts: tuple[UnverifiedSnippetDraft, ...] = ()

    @property
    def draft_catalog(self) -> str:
        return json.dumps([asdict(d) for d in self.drafts])

    def parser(self) -> Any:
        return dp.last_code_block.yaml_as(
            DraftAdvice
        ).wrap_errors.response_with(
            CheckRocqSnippet if self.allow_tools else Never
        )


def validate_decisions(
    answer: DraftAdvice,
    drafts: tuple[UnverifiedSnippetDraft, ...],
    receipts: tuple[SnippetReceipt, ...],
    contexts: tuple[SnippetContext, ...],
) -> None:
    bank = {d.draft_id: d for d in drafts}
    decisions = {d.draft_id: d for d in answer.decisions}
    if (
        len(decisions) != len(answer.decisions)
        or decisions.keys() != bank.keys()
    ):
        raise ValueError(
            "Give exactly one retain/drop decision per supplied draft"
        )
    receipt_bank = {r.identifier: r for r in receipts if r.executable}
    context_bank = {c.identifier: c for c in contexts}
    linked: set[str] = set()
    for ident, decision in decisions.items():
        if not decision.reason.strip():
            raise ValueError("Every draft decision needs a substantive reason")
        if decision.action == "drop":
            if decision.receipts:
                raise ValueError(
                    "A dropped draft cannot claim retained receipts"
                )
            continue
        if not decision.receipts or not set(decision.receipts) <= set(
            answer.retained_receipts
        ):
            raise ValueError("Retained drafts need retained checked receipts")
        source = context_bank[bank[ident].context_id]
        for rid in decision.receipts:
            r = receipt_bank.get(rid)
            if r is None or (
                r.context.problem_file != source.problem_file
                or r.context.source != source.source
                or r.context.prefix[: len(source.prefix)] != source.prefix
            ):
                raise ValueError(
                    "Draft receipt must extend its actual source context"
                )
        linked.update(decision.receipts)
    if linked != set(answer.retained_receipts):
        raise ValueError("Link every retained receipt to a supplied draft")


@dp.strategy
def write_rocq_drafts(
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
            WriteRocqDraftAdvice(
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
            delta = compile_advice(role, answer, tuple(verified.values()))
            validate_decisions(
                answer, drafts, tuple(verified.values()), contexts
            )
        except ValueError as exc:
            dialogue.append(
                dp.FeedbackMessage(
                    "feedback", "invalid_draft_decisions", str(exc)
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


def draft_examples() -> ExampleSelector:
    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        if not isinstance(query, WriteRocqDraftAdvice):
            return []
        families = example_families()
        excluded = {
            families.get(c.theorem_name, c.theorem_name)
            for c in query.contexts
        }
        selected: list[SelectedExample] = []
        for i, example in enumerate(
            env.examples.examples_for("WriteRocqDraftAdvice")
        ):
            eq = example.query
            if (
                isinstance(eq, WriteRocqDraftAdvice)
                and eq.role == query.role
                and not any(
                    families.get(c.theorem_name, c.theorem_name) in excluded
                    for c in eq.contexts
                )
            ):
                selected.append(
                    SelectedExample(example=example, index=i, similarity=None)
                )
        record(
            "draft_example",
            "selected",
            role=query.role,
            count=len(selected[:1]),
        )
        return selected[:1]

    return ExampleSelector(select)


def draft_writer_policy(
    snapshot_directory: str, dollar_cap: float = 0.20
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    model = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(model, CampaignResponsesModel):
        raise ValueError("Draft writer requires campaign ledger")
    model.halt_on_billing_issue, model.output_limit = True, 8192
    recorded = recorded_model(model)
    prompting = dp.few_shot(
        recorded,
        max_requests=1,
        select_examples=draft_examples(),
        tag_user_feedback_messages=True,
    )
    return admission_observer(
        dict(price=dollar_cap, num_requests=4, rocq_seconds=180)
    ) @ (
        grounded_search()
        & recorded_prompt(prompting, recorded, snapshot_directory)
    )


def reduction_input(
    products: Sequence[DraftWriting],
    contexts: tuple[SnippetContext, ...],
    playbook: str,
) -> dict[str, Any]:
    """Preserve drafts plus exact retained receipts across the ACE handoff.

    This is deterministic data preparation, with no model or Rocq execution.
    Receipt-bearing inputs should be persisted and hashed by the campaign.
    """
    drafts: dict[str, UnverifiedSnippetDraft] = {}
    bank = {c.identifier: c for c in contexts}
    kept: dict[str, SnippetReceipt] = {}
    for product in products:
        for draft in product.drafts:
            if draft.draft_id in drafts and drafts[draft.draft_id] != draft:
                raise ValueError("Conflicting source drafts")
            drafts[draft.draft_id] = draft
        for receipt in product.checked.receipts:
            if receipt.identifier in product.checked.answer.retained_receipts:
                kept[receipt.identifier] = receipt
                bank[receipt.context.identifier] = receipt.context
    if any(d.context_id not in bank for d in drafts.values()):
        raise ValueError(
            "Reduction needs each draft's original source context"
        )
    return dict(
        role="reducer",
        evidence=json.dumps(
            [
                dict(
                    answer=asdict(p.checked.answer),
                    decisions=[asdict(d) for d in p.decisions],
                )
                for p in products
            ]
        ),
        playbook=playbook,
        contexts=tuple(bank.values()),
        drafts=tuple(drafts.values()),
        receipts=tuple(kept.values()),
    )
