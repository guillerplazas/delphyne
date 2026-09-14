"""Opt-in v2 ACE platform. Offline development precedes any paid campaign.

Local repairs are submitted independently of the final reflection. Writer
failures return their evidence; a separate query reviews novelty before a
small book edit is eligible. Historical v1 queries and prompts stay frozen.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass, fields
import json
from typing import Any, Literal, Never

import delphyne as dp
from delphyne.stdlib.queries import ExampleSelector, SelectedExample

from ace.ace_playbook import Playbook
from ace.role_contracts import TrainingEvent, resolve
from ace.role_revision import (
    BookEdit,
    BookPlan,
    EditReview,
    LocalRepair,
    NoveltyVerdict,
    ReflectionFinish,
    ReflectionProduct,
    WriterProduct,
    approve_edit,
    apply_edits,
    bind_repair,
    fingerprint,
    nearest_rules,
    validate_finish,
    validate_plan,
)
from ace.rocq_snippets import SnippetContext, SnippetReceipt, check_snippet
from ace.terminal_evidence import TerminalEvidence
from prove_ace_roles import (
    CheckAdviceSnippet,
    ReadTrainingEvidence,
    WriteACEChoices,
    validate_inputs,
)
from prove_grounded import grounded_examples, grounded_search
from prove_snippets import example_families
from prove_writer_drafts import UnverifiedSnippetDraft
from runtime import pytanque_utils as pt
from runtime.campaign_budget import CampaignResponsesModel
from runtime.campaign_pause import PauseAwareProofModel, PauseAwareRoleModel
from runtime.ace_role_journal import (
    CHECKPOINT,
    RoleCheckpoint,
    checkpoint_roles,
)
from runtime.model_registry import make_model
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.replay_admission import admission_observer, recorded_prompt


@dataclass
class SubmitLocalRepair(dp.AbstractTool[str]):
    """Preserve a source-bound, explicitly unverified local repair draft."""

    repair: LocalRepair


@dataclass
class ReflectLocalRepairs(
    dp.Query[
        dp.Response[
            ReflectionFinish | dp.WrappedParseError,
            ReadTrainingEvidence | SubmitLocalRepair,
        ]
    ]
):
    spec: pt.ProblemSpec
    playbook: str
    trajectory: str
    terminal: TerminalEvidence
    events: tuple[TrainingEvent, ...]
    submitted: tuple[UnverifiedSnippetDraft, ...] = ()
    prefix: dp.AnswerPrefix = ()
    allow_tools: bool = True

    @property
    def skill(self) -> str:
        return (ROOT / "prompts/ace/role_skills_v2/reflector.md").read_text()

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
        return dp.structured_as(ReflectionFinish).wrap_errors.response_with(
            ReadTrainingEvidence | SubmitLocalRepair
            if self.allow_tools
            else Never
        )

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        return (
            [ReadTrainingEvidence, SubmitLocalRepair]
            if self.allow_tools
            else []
        )


@dp.strategy
def reflect_local_repairs(
    problem_file: str,
    playbook: str,
    trajectory: str,
    terminal: TerminalEvidence,
    events: tuple[TrainingEvent, ...],
) -> dp.Strategy[
    dp.Branch | dp.Message, dp.PromptingPolicy, ReflectionProduct
]:
    spec = pt.parse_problem(problem_file)
    if (
        terminal.version != 2
        or terminal.problem_file != problem_file
        or terminal.theorem_name != spec.theorem_name
    ):
        raise ValueError("Terminal evidence source mismatch")
    if len({e.identifier for e in events}) != len(events) or any(
        e.context.problem_file != problem_file for e in events
    ):
        raise ValueError("Training event source mismatch")
    contexts = tuple(
        {e.context.identifier: e.context for e in events}.values()
    )
    validate_inputs(contexts, (), ())
    submitted: dict[str, UnverifiedSnippetDraft] = {}
    dialogue: list[dp.AnswerPrefixElement] = []
    diagnostics: list[str] = []
    step = 0
    episode = fingerprint(
        json.dumps(
            dict(
                role="reflector",
                source=problem_file,
                playbook=playbook,
                terminal=asdict(terminal),
                events=[asdict(e) for e in events],
            ),
            sort_keys=True,
        )
    )

    def progress(
        finish: ReflectionFinish | None = None,
    ) -> dp.Strategy[dp.Message, object, ReflectionProduct]:
        nonlocal step
        product = ReflectionProduct(
            "complete" if finish else "partial",
            tuple(submitted.values()),
            contexts,
            tuple(diagnostics),
            finish,
        )
        yield from dp.message(
            CHECKPOINT, asdict(RoleCheckpoint(episode, step, product))
        )
        step += 1
        return product

    yield from progress()
    for turn in range(4):
        q = ReflectLocalRepairs(
            spec,
            playbook,
            trajectory,
            terminal,
            events,
            tuple(submitted.values()),
            tuple(dialogue),
            turn < 3,
        )
        response = yield from dp.branch(q.using(dp.ambient_pp))
        dialogue.append(dp.OracleMessage("oracle", response.answer))
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                try:
                    if turn == 3:
                        raise ValueError(
                            "Return the final disposition; no tools remain"
                        )
                    if isinstance(call, SubmitLocalRepair):
                        draft = bind_repair(call.repair, events)
                        if (
                            draft.draft_id not in submitted
                            and len(submitted) >= 3
                        ):
                            raise ValueError(
                                "At most three distinct repair drafts"
                            )
                        submitted[draft.draft_id] = draft
                        result = json.dumps(
                            dict(
                                draft_id=draft.draft_id,
                                status="unverified",
                                message="Preserved for the curator even if a later final answer is invalid",
                            )
                        )
                    else:
                        event = next(
                            (e for e in events if e.identifier == call.event),
                            None,
                        )
                        if event is None:
                            raise ValueError(
                                "Unknown event; use a supplied e-number"
                            )
                        result = json.dumps(asdict(event))
                except ValueError as ex:
                    result = str(ex)
                dialogue.append(
                    dp.ToolResult(
                        "tool", response.answer.tool_calls[i], result
                    )
                )
                yield from progress()
            continue
        try:
            finish = response.parsed.final
            if isinstance(finish, dp.WrappedParseError):
                raise ValueError(str(finish.error))
            validate_finish(finish, tuple(submitted.values()))
        except ValueError as ex:
            diagnostics.append(str(ex))
            dialogue.append(
                dp.FeedbackMessage("feedback", "invalid_disposition", str(ex))
            )
            yield from progress()
            continue
        return (yield from progress(finish))
    diagnostics.append(
        "Four-turn allowance exhausted; submitted repairs preserved"
    )
    return (yield from progress())


@dataclass
class FindBookRules(dp.AbstractTool[str]):
    """Retrieve similar existing rules to compare before proposing an edit.

    Lexical retrieval is a navigation aid, not a novelty certificate.
    """

    query: str


@dataclass
class ProposeBookEdits(
    dp.Query[
        dp.Response[
            BookPlan | dp.WrappedParseError, CheckAdviceSnippet | FindBookRules
        ]
    ]
):
    role: Literal["curator", "reducer"]
    book: Playbook
    evidence: str
    contexts: tuple[SnippetContext, ...]
    drafts: tuple[UnverifiedSnippetDraft, ...]
    receipts: tuple[SnippetReceipt, ...] = ()
    prefix: dp.AnswerPrefix = ()
    allow_tools: bool = True

    @property
    def skill(self) -> str:
        return (
            ROOT / f"prompts/ace/role_skills_v2/{self.role}.md"
        ).read_text()

    @property
    def catalog(self) -> str:
        return WriteACEChoices(
            self.role,
            self.evidence,
            "",
            self.contexts,
            self.drafts,
            self.receipts,
        ).catalog

    @property
    def rules(self) -> str:
        return json.dumps(
            [
                dict(
                    alias=f"b{i + 1}",
                    id=b.id,
                    section=b.section,
                    content=b.content,
                )
                for i, b in enumerate(self.book.bullets)
            ]
        )

    def parser(self) -> Any:
        return dp.structured_as(BookPlan).wrap_errors.response_with(
            CheckAdviceSnippet | FindBookRules if self.allow_tools else Never
        )

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        return [CheckAdviceSnippet, FindBookRules] if self.allow_tools else []


@dataclass
class JudgeBookEdit(dp.Query[NoveltyVerdict | dp.WrappedParseError]):
    action: str
    proposed_rule: str
    target: str
    rules: str
    receipts: tuple[SnippetReceipt, ...]

    @property
    def receipt_evidence(self) -> str:
        return json.dumps(
            [
                dict(
                    theorem=r.context.theorem_name,
                    context_id=r.context.identifier,
                    verified_prefix_before=r.context.prefix,
                    submitted_snippet=r.snippet,
                    status=r.status,
                    error=r.checked.feedback.error_message,
                    failing_tactic=r.checked.feedback.failing_tactic,
                    remaining_goals=r.checked.feedback.remaining_goals,
                )
                for r in self.receipts
            ]
        )

    def parser(self) -> Any:
        return dp.structured_as(NoveltyVerdict).wrap_errors


@dp.strategy
def write_reviewed_book_edits(
    role: Literal["curator", "reducer"],
    book: Playbook,
    evidence: str,
    contexts: tuple[SnippetContext, ...],
    drafts: tuple[UnverifiedSnippetDraft, ...],
    receipts: tuple[SnippetReceipt, ...] = (),
) -> dp.Strategy[
    dp.Branch | dp.Compute | dp.Message, dp.PromptingPolicy, WriterProduct
]:
    validate_inputs(contexts, drafts, receipts)
    bank = {c.identifier: c for c in contexts}
    verified = {r.identifier: r for r in receipts}
    seen = {(r.context.identifier, r.snippet): r for r in receipts}
    dialogue: list[dp.AnswerPrefixElement] = []
    diagnostics: list[str] = []
    probes, seconds = 0, 0.0
    plan: BookPlan | None = None
    edits: list[BookEdit] = []
    reviews: list[EditReview] = []
    step = 0
    episode = fingerprint(
        json.dumps(
            dict(
                role=role,
                book=book.sha256(),
                evidence=evidence,
                contexts=[asdict(c) for c in contexts],
                drafts=[asdict(d) for d in drafts],
                receipts=[asdict(r) for r in receipts],
            ),
            sort_keys=True,
        )
    )

    def progress(
        complete: bool = False,
    ) -> dp.Strategy[dp.Message, object, WriterProduct]:
        nonlocal step
        product = WriterProduct(
            role,
            "complete" if complete else "partial",
            book.sha256(),
            drafts,
            tuple(bank.values()),
            tuple(verified.values()),
            plan,
            tuple(edits),
            tuple(diagnostics),
            tuple(reviews),
        )
        yield from dp.message(
            CHECKPOINT, asdict(RoleCheckpoint(episode, step, product))
        )
        step += 1
        return product

    yield from progress()
    for turn in range(4):
        q = ProposeBookEdits(
            role,
            book,
            evidence,
            tuple(bank.values()),
            drafts,
            tuple(verified.values()),
            tuple(dialogue),
            turn < 3,
        )
        response = yield from dp.branch(q.using(dp.ambient_pp))
        dialogue.append(dp.OracleMessage("oracle", response.answer))
        if isinstance(response.parsed, dp.ToolRequests):
            for i, call in enumerate(response.parsed.tool_calls):
                try:
                    if turn == 3:
                        raise ValueError(
                            "Return final decisions; no tools remain"
                        )
                    if isinstance(call, FindBookRules):
                        result = json.dumps(nearest_rules(book, call.query))
                    else:
                        ctx = resolve(call.context, "c", q.contexts)
                        key = (ctx.identifier, call.snippet)
                        if key not in seen:
                            if probes >= 3 or seconds >= 180:
                                raise ValueError(
                                    "New-probe allowance exhausted; reuse an existing receipt"
                                )
                            checked = yield from dp.compute(check_snippet)(
                                ctx,
                                call.snippet,
                                dict(
                                    seconds=min(60.0, 180 - seconds),
                                    rpc_calls=512,
                                    view_bytes=8192,
                                ),
                            )
                            probes += 1
                            seconds += checked.elapsed
                            verified[checked.identifier] = checked
                            seen[key] = checked
                            if checked.executable:
                                nxt = checked.successor()
                                bank[nxt.identifier] = nxt
                        checked = seen[key]
                        result = json.dumps(
                            dict(
                                receipt=f"r{list(verified).index(checked.identifier) + 1}",
                                context=(
                                    f"c{list(bank).index(checked.successor().identifier) + 1}"
                                    if checked.executable
                                    else call.context
                                ),
                                status=checked.status,
                                error=checked.checked.feedback.error_message,
                                goals=checked.checked.feedback.remaining_goals[
                                    :4
                                ],
                            )
                        )
                except ValueError as ex:
                    result = str(ex)
                dialogue.append(
                    dp.ToolResult(
                        "tool", response.answer.tool_calls[i], result
                    )
                )
                yield from progress()
            continue
        try:
            answer = response.parsed.final
            if isinstance(answer, dp.WrappedParseError):
                raise ValueError(str(answer.error))
            validate_plan(
                answer,
                book,
                drafts,
                tuple(verified.values()),
                tuple(bank.values()),
            )
        except ValueError as ex:
            diagnostics.append(str(ex))
            dialogue.append(
                dp.FeedbackMessage("feedback", "invalid_edit_plan", str(ex))
            )
            yield from progress()
            continue
        plan = answer
        yield from progress()
        break
    complete = plan is not None
    review_book = book
    if plan is not None and role == "reducer":
        for decision in plan.decisions:
            if decision.action == "drop":
                continue
            # The reviewer sees checked evidence and rules, not the proposer's
            # persuasive rationale. Every retained decision consumes one review.
            selected = (
                *decision.receipts,
                *(
                    (decision.failure_receipt,)
                    if decision.failure_receipt
                    else ()
                ),
            )
            verdict = yield from dp.branch(
                JudgeBookEdit(
                    decision.action,
                    decision.content,
                    decision.closest_rule,
                    ProposeBookEdits(role, review_book, "", (), ()).rules,
                    tuple(
                        resolve(r, "r", tuple(verified.values()))
                        for r in selected
                    ),
                ).using(dp.ambient_pp)
            )
            try:
                if isinstance(verdict, dp.WrappedParseError):
                    raise ValueError(str(verdict.error))
                edit = approve_edit(
                    decision, verdict, review_book, tuple(verified.values())
                )
                if edit is not None:
                    review_book, bound = apply_edits(
                        review_book, review_book.sha256(), (edit,)
                    )
                    edits.extend(bound)
                reviews.append(EditReview(decision.draft, verdict))
            except ValueError as ex:
                diagnostics.append(str(ex))
                reviews.append(
                    EditReview(
                        decision.draft,
                        None
                        if isinstance(verdict, dp.WrappedParseError)
                        else verdict,
                        str(ex),
                    )
                )
                complete = False
            yield from progress()
    if plan is None:
        diagnostics.append(
            "Invalid final plan; drafts and all checked receipts preserved"
        )
    return (yield from progress(complete))


def revision_examples() -> ExampleSelector:
    def sources(query: dp.AbstractQuery[Any]) -> set[str]:
        if isinstance(query, ReflectLocalRepairs):
            return {query.spec.theorem_name}
        if isinstance(query, ProposeBookEdits):
            return {c.theorem_name for c in query.contexts}
        if isinstance(query, JudgeBookEdit):
            return {r.context.theorem_name for r in query.receipts}
        return set()

    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        family = example_families()
        excluded = {family.get(n, n) for n in sources(query)}
        selected: list[SelectedExample] = []
        limit = 2 if isinstance(query, JudgeBookEdit) else 1
        for i, example in enumerate(
            env.examples.examples_for(type(query).__name__)
        ):
            if (
                isinstance(query, ProposeBookEdits)
                and isinstance(example.query, ProposeBookEdits)
                and query.role != example.query.role
            ):
                continue
            if not excluded & {
                family.get(n, n) for n in sources(example.query)
            }:
                selected.append(
                    SelectedExample(example=example, index=i, similarity=None)
                )
                if len(selected) == limit:
                    break
        return selected

    return ExampleSelector(select)


def role_revision_policy(
    snapshot_directory: str, pause_file: str, dollar_cap: float = 0.20
) -> dp.Policy[
    dp.Branch | dp.Compute | dp.Fail | dp.Message, dp.PromptingPolicy
]:
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )

    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Role revision requires campaign accounting")
    original.halt_on_billing_issue, original.output_limit = True, 8192
    model = PauseAwareRoleModel(
        **{
            f.name: getattr(original, f.name)
            for f in fields(original)
            if f.init
        },
        pause_file=pause_file,
    )
    prompting = dp.few_shot(
        model,
        max_requests=1,
        select_examples=revision_examples(),
        tag_user_feedback_messages=True,
    )
    limits = dict(price=dollar_cap, num_requests=7, rocq_seconds=180)
    return (
        dp.with_budget(dp.BudgetLimit(limits))
        @ admission_observer(limits)
        @ (
            (
                grounded_search()
                @ checkpoint_roles(snapshot_directory + "/checkpoints")
            )
            & recorded_prompt(prompting, model, snapshot_directory)
        )
    )


def revision_proof_policy(
    snapshot_directory: str, pause_file: str
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    """Flagship proof behavior, with a shared cooperative campaign pause."""
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Proof comparison requires campaign accounting")
    values = {
        f.name: getattr(original, f.name) for f in fields(original) if f.init
    }
    values.update(output_limit=32768, halt_on_billing_issue=True)
    model = PauseAwareProofModel(
        **values, pause_file=pause_file, continuation=False
    )
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=grounded_examples(),
        tag_user_feedback_messages=True,
    )
    limits = dict(price=0.10, num_requests=64, rocq_seconds=300)
    return (
        dp.with_budget(dp.BudgetLimit(limits))
        @ admission_observer(limits)
        @ (
            grounded_search()
            & recorded_prompt(normal, model, snapshot_directory)
        )
    )
