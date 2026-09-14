"""Rocq-backed ACE writing and flagship policies for both agent harnesses.

Queries make proposals; strategies enforce receipt provenance; Compute runs
Rocq. The standard budget stream and campaign ledger admit every operation.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
import json
from typing import Any, Literal, Never, cast

import delphyne as dp
from delphyne.stdlib.queries import ExampleSelector, SelectedExample

from ace.ace_playbook import AddOp
from ace.rocq_snippets import (
    CheckRocqSnippet,
    SnippetContext,
    SnippetReceipt,
    check_snippet,
    context_catalog,
)
from prove_ace import CurationDelta
from prove_ace import _ace_examples  # pyright: ignore[reportPrivateUsage]
from prove_grounded import (
    ProposeProofScriptGrounded,
    grounded_examples,
    grounded_search,
)
from runtime.admission_events import record
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import make_model
from runtime.replay_admission import (
    admission_observer,
    recorded_model,
    recorded_prompt,
)

WriterRole = Literal["reflector", "curator", "reducer"]


@dataclass(frozen=True)
class SnippetAddition:
    section: str
    explanation: str
    receipts: tuple[str, ...]


@dataclass(frozen=True)
class SnippetAdvice:
    reasoning: str
    operations: tuple[SnippetAddition, ...] = ()
    retained_receipts: tuple[str, ...] = ()
    dropped_receipts: tuple[str, ...] = ()


@dataclass(frozen=True)
class CheckedWriting:
    role: WriterRole
    answer: SnippetAdvice
    delta: CurationDelta
    receipts: tuple[SnippetReceipt, ...]


@dataclass
class WriteCheckedRocqAdvice(
    dp.Query[
        dp.Response[SnippetAdvice | dp.WrappedParseError, CheckRocqSnippet]
    ]
):
    role: WriterRole
    evidence: str
    playbook: str
    contexts: tuple[SnippetContext, ...]
    receipts: tuple[SnippetReceipt, ...] = ()
    prefix: dp.AnswerPrefix = ()
    allow_tools: bool = True

    @property
    def context_catalog(self) -> str:
        return context_catalog(self.contexts)

    @property
    def receipt_catalog(self) -> str:
        return json.dumps(
            [
                dict(
                    receipt_id=r.identifier,
                    status=r.status,
                    context_id=r.context.identifier,
                    snippet=r.snippet,
                )
                for r in self.receipts
                if r.executable
            ],
            ensure_ascii=False,
        )

    def parser(
        self,
    ) -> dp.Parser[
        dp.Response[SnippetAdvice | dp.WrappedParseError, CheckRocqSnippet]
    ]:
        if self.allow_tools:
            return dp.last_code_block.yaml_as(
                SnippetAdvice
            ).wrap_errors.response_with(CheckRocqSnippet)
        return cast(
            Any,
            dp.last_code_block.yaml_as(
                SnippetAdvice
            ).wrap_errors.response_with(Never),
        )

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        settings = self.parser().settings.tools
        return settings.tool_types if settings else []


def compile_advice(
    role: WriterRole,
    answer: SnippetAdvice,
    receipts: tuple[SnippetReceipt, ...],
) -> CurationDelta:
    bank = {r.identifier: r for r in receipts if r.executable}
    retained = set(answer.retained_receipts)
    dropped = set(answer.dropped_receipts)
    used = {ident for op in answer.operations for ident in op.receipts}
    if (
        len(answer.operations) > 3
        or len(retained) != len(answer.retained_receipts)
        or len(dropped) != len(answer.dropped_receipts)
        or retained & dropped
        or (retained | dropped) != bank.keys()
        or not used <= retained
        or role != "reflector"
        and retained != used
        or role == "reflector"
        and answer.operations
    ):
        raise ValueError(
            "Every checked receipt must be retained exactly or explicitly dropped"
        )
    operations: list[AddOp] = []
    for op in answer.operations:
        if (
            not op.explanation.strip()
            or not op.receipts
            or len(op.receipts) != len(set(op.receipts))
            or any(
                marker in op.explanation.lower()
                for marker in ("`", "~~~", "<code", "<pre")
            )
            or op.section not in ("tactics", "lemmas", "pitfalls", "strategy")
        ):
            raise ValueError(
                "Use plain explanation plus checked receipt IDs, never inline executable code"
            )
        content = op.explanation
        for ident in op.receipts:
            r = bank[ident]
            content += (
                f"\n\nSource-local example ({r.context.theorem_name}; {ident}). "
                "Valid only in its source context; check adapted names and hypotheses "
                "in the current theorem before reuse.\n```rocq\n"
                + r.snippet
                + "\n```"
            )
        operations.append(AddOp("ADD", op.section, content))
    return CurationDelta(answer.reasoning, operations)


@dp.strategy
def verify_snippet_demo(
    context: SnippetContext, snippet: str, expected: str
) -> dp.Strategy[dp.Compute | dp.Fail, object, str]:
    checked = yield from dp.compute(check_snippet)(
        context, snippet, dict(seconds=60, rpc_calls=512, view_bytes=8192)
    )
    if checked.status != expected:
        yield from dp.fail(label="snippet_demo_verdict_mismatch")
    return checked.status


@dp.strategy
def write_checked_rocq_advice(
    role: WriterRole,
    evidence: str,
    playbook: str,
    contexts: tuple[SnippetContext, ...],
    receipts: tuple[SnippetReceipt, ...] = (),
) -> dp.Strategy[
    dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, CheckedWriting
]:
    from experiments.common.ace_pools import POOLS

    for c in contexts:
        if POOLS["trainX"].get(c.theorem_name) != (
            c.problem_file,
            c.theorem_name,
        ):
            raise ValueError("Writing evidence must be trainX")
    bank = {c.identifier: c for c in contexts}
    verified = {r.identifier: r for r in receipts}
    # Inherited receipts are checked against their source before they can be
    # used. They are persisted inputs, not agent-supplied certificate claims.
    for r in receipts:
        if r.context.identifier not in bank:
            raise ValueError("Receipt context is absent from the source bank")
    dialogue: list[dp.AnswerPrefixElement] = []
    seen: dict[tuple[str, str], SnippetReceipt] = {}
    probes = 0
    spent = 0.0
    for turn in range(4):
        response = yield from dp.branch(
            WriteCheckedRocqAdvice(
                role,
                evidence,
                playbook,
                tuple(bank.values()),
                tuple(verified.values()),
                tuple(dialogue),
                turn < 3 and probes < 3,
            ).using(dp.ambient_pp)
        )
        dialogue.append(dp.OracleMessage("oracle", response.answer))
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                key = (call.context_id, call.snippet)
                if turn == 3 or probes >= 3:
                    text = "Probe limit reached. Return the final YAML answer."
                elif call.context_id not in bank:
                    text = (
                        "Unknown context_id. Choose a supplied source context."
                    )
                elif key in seen:
                    text = seen[key].render()
                    record("snippet", "reused", receipt=seen[key].identifier)
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
                    text = checked.render()
                if probes < 3:
                    probes += 1
                dialogue.append(
                    dp.ToolResult("tool", response.answer.tool_calls[i], text)
                )
            continue
        answer = response.parsed.final
        try:
            if isinstance(answer, dp.WrappedParseError):
                raise ValueError(str(answer.error))
            delta = compile_advice(role, answer, tuple(verified.values()))
        except ValueError as exc:
            dialogue.append(
                dp.FeedbackMessage("feedback", "invalid_receipts", str(exc))
            )
            continue
        record(
            "writer",
            "completed",
            role=role,
            operations=len(delta.operations),
            retained=list(answer.retained_receipts),
            dropped=list(answer.dropped_receipts),
        )
        return CheckedWriting(role, answer, delta, tuple(verified.values()))
    yield from dp.fail(label="writer_contract_unfinished")
    return CheckedWriting(
        role, SnippetAdvice("unreachable"), CurationDelta("", []), ()
    )


def snippet_examples() -> ExampleSelector:
    legacy = grounded_examples()
    base_examples = _ace_examples()

    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        if (
            not isinstance(query, ProposeProofScriptGrounded)
            or not query.snippet_contexts
        ):
            return (
                [
                    SelectedExample(example=e, index=i, similarity=None)
                    for i, e in enumerate(legacy(env, query))
                ]
                if isinstance(query, ProposeProofScriptGrounded)
                else []
            )
        families = example_families()

        chosen: list[SelectedExample] = []
        for i, example in enumerate(
            env.examples.examples_for("ProposeProofScriptGroundedSnippets")
        ):
            if isinstance(example.query, ProposeProofScriptGrounded):
                source = example.query.spec.theorem_name
                if families.get(source, source) != families.get(
                    query.spec.theorem_name, query.spec.theorem_name
                ):
                    chosen.append(
                        SelectedExample(
                            example=example, index=i, similarity=None
                        )
                    )
        record("snippet_example", "selected", count=len(chosen[:2]))
        return [
            *[
                SelectedExample(example=e, index=i, similarity=None)
                for i, e in enumerate(base_examples(env, query))
            ],
            *chosen[:2],
        ]

    return ExampleSelector(select)


@lru_cache(maxsize=1)
def example_families() -> dict[str, str]:
    from experiments.coverage_cycle_experiment import family_map

    return family_map()


def snippet_policy(
    snapshot_directory: str,
    role: str = "proof",
    dollar_cap: float = 0.10,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Snippet experiment requires campaign accounting")
    original.halt_on_billing_issue = True
    original.output_limit = 32768 if role == "proof" else 8192
    model = recorded_model(original)
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=snippet_examples(),
        tag_user_feedback_messages=True,
    )
    return admission_observer(
        dict(
            price=dollar_cap,
            num_requests=64 if role == "proof" else 4,
            rocq_seconds=300 if role == "proof" else 180,
        )
    ) @ (
        grounded_search() & recorded_prompt(normal, model, snapshot_directory)
    )
