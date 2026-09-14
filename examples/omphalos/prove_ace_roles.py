"""Opt-in ACE roles: short references, typed decisions, bounded evidence.

Shared Python strategies, policies and demonstrations work from both Codex
and Claude Code. The frozen generator and earlier writer queries are intact.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass, fields
import json
from typing import Any, Literal, Never

import delphyne as dp
from delphyne.stdlib.queries import ExampleSelector, SelectedExample

from ace.role_contracts import (
    ReflectedLesson,
    TrainingEvent,
    WriterChoices,
    compile_choices,
    lesson_draft,
    resolve,
)
from ace.rocq_snippets import SnippetContext, SnippetReceipt, check_snippet
from ace.terminal_evidence import TerminalEvidence
from prove_grounded import grounded_search
from prove_snippets import CheckedWriting, example_families
from prove_writer_drafts import (
    DraftWriting,
    UnverifiedSnippetDraft,
    draft_examples,
)
from runtime import pytanque_utils as pt
from runtime.admission_events import record
from runtime.campaign_budget import CampaignResponsesModel
from runtime.continuation_output import ContinuationResponsesModel
from runtime.model_registry import make_model
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.replay_admission import (
    RecordedResponsesModel,
    admission_observer,
    recorded_model,
    recorded_prompt,
)


@dataclass
class CheckAdviceSnippet(dp.AbstractTool[str]):
    """Check complete raw Rocq sentences in a supplied c-number context.

    A successful open fragment only certifies execution in that context.
    A changed fragment needs a new check. Reuse unchanged r-number receipts.
    """

    context: str
    snippet: str


@dataclass
class WriteACEChoices(
    dp.Query[
        dp.Response[WriterChoices | dp.WrappedParseError, CheckAdviceSnippet]
    ]
):
    role: Literal["curator", "reducer"]
    evidence: str
    playbook: str
    contexts: tuple[SnippetContext, ...]
    drafts: tuple[UnverifiedSnippetDraft, ...]
    receipts: tuple[SnippetReceipt, ...] = ()
    prefix: dp.AnswerPrefix = ()
    allow_tools: bool = True

    @property
    def skill(self) -> str:
        return (ROOT / f"prompts/ace/role_skills/{self.role}.md").read_text()

    @property
    def catalog(self) -> str:
        contexts = {
            c.identifier: f"c{i + 1}" for i, c in enumerate(self.contexts)
        }
        return json.dumps(
            dict(
                contexts=[
                    dict(
                        alias=f"c{i + 1}",
                        theorem=c.theorem_name,
                        prefix=c.prefix,
                    )
                    for i, c in enumerate(self.contexts)
                ],
                drafts=[
                    dict(
                        alias=f"d{i + 1}",
                        context=contexts[d.context_id],
                        code=d.proposed_code,
                        purpose=d.purpose,
                        error=d.error,
                        recorded_goals=d.remaining_goals,
                    )
                    for i, d in enumerate(self.drafts)
                ],
                receipts=[
                    dict(
                        alias=f"r{i + 1}",
                        context=contexts[r.context.identifier],
                        status=r.status,
                        code=r.snippet,
                    )
                    for i, r in enumerate(self.receipts)
                ],
            ),
            ensure_ascii=False,
        )

    def parser(self) -> Any:
        return dp.structured_as(WriterChoices).wrap_errors.response_with(
            CheckAdviceSnippet if self.allow_tools else Never
        )

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        return [CheckAdviceSnippet] if self.allow_tools else []


def validate_inputs(
    contexts: tuple[SnippetContext, ...],
    drafts: tuple[UnverifiedSnippetDraft, ...],
    receipts: tuple[SnippetReceipt, ...],
) -> None:
    from experiments.common.ace_pools import POOLS

    bank = {c.identifier: c for c in contexts}
    if len(bank) != len(contexts) or any(
        POOLS["trainX"].get(c.theorem_name) != (c.problem_file, c.theorem_name)
        for c in contexts
    ):
        raise ValueError("Unique trainX source contexts required")
    if len({d.draft_id for d in drafts}) != len(drafts) or any(
        d.context_id not in bank
        or not d.proposed_code.strip()
        or not d.source.strip()
        for d in drafts
    ):
        raise ValueError("Unique, source-bound nonempty drafts required")
    if len({r.identifier for r in receipts}) != len(receipts) or any(
        bank.get(r.context.identifier) != r.context for r in receipts
    ):
        raise ValueError(
            "Inherited receipts require their exact source contexts"
        )


@dp.strategy
def write_ace_choices(
    role: Literal["curator", "reducer"],
    evidence: str,
    playbook: str,
    contexts: tuple[SnippetContext, ...],
    drafts: tuple[UnverifiedSnippetDraft, ...],
    receipts: tuple[SnippetReceipt, ...] = (),
) -> dp.Strategy[
    dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy, DraftWriting
]:
    validate_inputs(contexts, drafts, receipts)
    bank = {c.identifier: c for c in contexts}
    verified = {r.identifier: r for r in receipts}
    seen = {(r.context.identifier, r.snippet): r for r in receipts}
    dialogue: list[dp.AnswerPrefixElement] = []
    probes, spent = 0, 0.0
    for turn in range(4):
        query = WriteACEChoices(
            role,
            evidence,
            playbook,
            tuple(bank.values()),
            drafts,
            tuple(verified.values()),
            tuple(dialogue),
            turn < 3 and probes < 3,
        )
        response = yield from dp.branch(query.using(dp.ambient_pp))
        dialogue.append(dp.OracleMessage("oracle", response.answer))
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                try:
                    if turn == 3 or probes >= 3:
                        raise ValueError(
                            "Probe allowance exhausted; return final decisions"
                        )
                    # Resolve all calls against the catalogue the model actually saw.
                    context = resolve(call.context, "c", query.contexts)
                    key = (context.identifier, call.snippet)
                    if key in seen:
                        checked = seen[key]
                    else:
                        checked = yield from dp.compute(check_snippet)(
                            context,
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
                    rid = list(verified).index(checked.identifier) + 1
                    successor_alias = (
                        f"c{list(bank).index(checked.successor().identifier) + 1}"
                        if checked.executable
                        else None
                    )
                    result = json.dumps(
                        dict(
                            receipt=f"r{rid}",
                            status=checked.status,
                            successor_context=successor_alias,
                            error=checked.checked.feedback.error_message,
                            recorded_goals=checked.checked.feedback.remaining_goals[
                                :4
                            ],
                            scope="Exact source execution only; open fragments do not prove introduced assertions.",
                        ),
                        ensure_ascii=False,
                    )
                except ValueError as exc:
                    result = str(exc)
                probes += 1
                dialogue.append(
                    dp.ToolResult(
                        "tool", response.answer.tool_calls[i], result
                    )
                )
            continue
        try:
            answer = response.parsed.final
            if isinstance(answer, dp.WrappedParseError):
                raise ValueError(str(answer.error))
            advice, delta = compile_choices(
                role, answer, drafts, tuple(verified.values()), contexts
            )
        except ValueError as exc:
            dialogue.append(
                dp.FeedbackMessage("feedback", "invalid_choices", str(exc))
            )
            continue
        record(
            "ace_roles_writer",
            "completed",
            role=role,
            operations=len(delta.operations),
            decisions=len(advice.decisions),
        )
        return DraftWriting(
            CheckedWriting(role, advice, delta, tuple(verified.values())),
            drafts,
            advice.decisions,
        )
    yield from dp.fail(label="ace_role_contract_unfinished")
    raise AssertionError("unreachable")


@dataclass
class ReadTrainingEvidence(dp.AbstractTool[str]):
    """Read an exact e-number event from this training source. No new search."""

    event: str


@dataclass
class ReflectACEEvidence(
    dp.Query[
        dp.Response[
            ReflectedLesson | dp.WrappedParseError, ReadTrainingEvidence
        ]
    ]
):
    spec: pt.ProblemSpec
    playbook: str
    trajectory: str
    terminal: TerminalEvidence
    events: tuple[TrainingEvent, ...]
    prefix: dp.AnswerPrefix = ()
    allow_tools: bool = True

    @property
    def skill(self) -> str:
        return (ROOT / "prompts/ace/role_skills/reflector.md").read_text()

    @property
    def event_index(self) -> str:
        return json.dumps(
            [
                dict(
                    event=e.identifier,
                    status=e.status,
                    submitted=e.submitted[:400],
                    error=e.error[:400],
                )
                for e in self.events
            ]
        )

    def parser(self) -> Any:
        return dp.structured_as(ReflectedLesson).wrap_errors.response_with(
            ReadTrainingEvidence if self.allow_tools else Never
        )

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        return [ReadTrainingEvidence] if self.allow_tools else []


@dp.strategy
def reflect_ace_evidence(
    problem_file: str,
    playbook: str,
    trajectory: str,
    terminal: TerminalEvidence,
    events: tuple[TrainingEvent, ...],
) -> dp.Strategy[dp.Branch | dp.Fail, dp.PromptingPolicy, ReflectedLesson]:
    spec = pt.parse_problem(problem_file)
    if (
        terminal.theorem_name != spec.theorem_name
        or terminal.problem_file != problem_file
        or terminal.version != 2
    ):
        raise ValueError("Terminal evidence source mismatch")
    if len({e.identifier for e in events}) != len(events) or any(
        e.context.problem_file != problem_file for e in events
    ):
        raise ValueError("Training event source mismatch")
    dialogue: list[dp.AnswerPrefixElement] = []
    for turn in range(4):
        response = yield from dp.branch(
            ReflectACEEvidence(
                spec,
                playbook,
                trajectory,
                terminal,
                events,
                tuple(dialogue),
                turn < 3,
            ).using(dp.ambient_pp)
        )
        dialogue.append(dp.OracleMessage("oracle", response.answer))
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                event = next(
                    (e for e in events if e.identifier == call.event), None
                )
                result = (
                    json.dumps(asdict(event), ensure_ascii=False)
                    if event
                    else "Unknown event; choose an e-number in the supplied index."
                )
                dialogue.append(
                    dp.ToolResult(
                        "tool", response.answer.tool_calls[i], result
                    )
                )
            continue
        try:
            answer = response.parsed.final
            if isinstance(answer, dp.WrappedParseError):
                raise ValueError(str(answer.error))
            lesson_draft(answer, events)
        except ValueError as exc:
            dialogue.append(
                dp.FeedbackMessage("feedback", "invalid_lesson", str(exc))
            )
            continue
        return answer
    yield from dp.fail(label="ace_reflector_unfinished")
    raise AssertionError("unreachable")


def role_examples() -> ExampleSelector:
    legacy = draft_examples()

    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        if not isinstance(query, (WriteACEChoices, ReflectACEEvidence)):
            return [
                SelectedExample(example=e, index=i, similarity=None)
                for i, e in enumerate(legacy(env, query))
            ]
        families = example_families()
        sources = (
            {c.theorem_name for c in query.contexts}
            if isinstance(query, WriteACEChoices)
            else {query.spec.theorem_name}
        )
        excluded = {families.get(s, s) for s in sources}
        for i, example in enumerate(
            env.examples.examples_for(type(query).__name__)
        ):
            eq = example.query
            if isinstance(query, WriteACEChoices) and isinstance(
                eq, WriteACEChoices
            ):
                same = eq.role == query.role
                represented = {
                    families.get(c.theorem_name, c.theorem_name)
                    for c in eq.contexts
                }
            elif isinstance(query, ReflectACEEvidence) and isinstance(
                eq, ReflectACEEvidence
            ):
                same = True
                represented = {
                    families.get(eq.spec.theorem_name, eq.spec.theorem_name)
                }
            else:
                continue
            if same and not represented & excluded:
                return [
                    SelectedExample(example=example, index=i, similarity=None)
                ]
        return []

    return ExampleSelector(select)


@dataclass(kw_only=True)
class RoleResponsesModel(RecordedResponsesModel, ContinuationResponsesModel):
    """Keep recording and final-message parsing in the same model instance."""


def ace_roles_policy(
    snapshot_directory: str, mode: str, dollar_cap: float
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("ACE role policies require campaign accounting")
    original.halt_on_billing_issue, original.output_limit = True, 8192
    model = (
        RoleResponsesModel(
            **{
                f.name: getattr(original, f.name)
                for f in fields(original)
                if f.init
            }
        )
        if mode in ("writer", "reflector")
        else recorded_model(original)
    )
    prompting = dp.few_shot(
        model,
        max_requests=1,
        select_examples=role_examples(),
        tag_user_feedback_messages=True,
    )
    return admission_observer(
        dict(price=dollar_cap, num_requests=4, rocq_seconds=180)
    ) @ (
        grounded_search()
        & recorded_prompt(prompting, model, snapshot_directory)
    )
