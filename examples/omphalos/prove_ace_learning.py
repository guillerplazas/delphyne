"""Opt-in ACE v3 role learning; sealed v2 strategies remain unchanged.

The control flow deliberately retains v2 checkpoint and application contracts.
Changes are individually switchable for fixed-input mechanism experiments.
"""

from collections.abc import Sequence
from dataclasses import asdict, dataclass, fields
import json
from typing import Any, Literal, Never

import delphyne as dp
from delphyne.stdlib.queries import ExampleSelector, SelectedExample

from ace.ace_playbook import Playbook
from ace.learning_contracts import (
    LearningPlan,
    LearningVerdict,
    LocalObservation,
    observe_local_progress,
    operation_tags,
    source_events_for,
)
from prove_ace_role_revision import JudgeBookEdit
from ace.role_contracts import TrainingEvent, resolve
from ace.role_revision import (
    BookEdit,
    BookPlan,
    EditReview,
    LocalRepair,
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
from prove_grounded import grounded_search
from prove_snippets import example_families
from prove_writer_drafts import UnverifiedSnippetDraft
from runtime import pytanque_utils as pt
from runtime.campaign_budget import CampaignResponsesModel
from runtime.campaign_pause import PauseAwareRoleModel
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
class ReflectLearningRepairs(
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
    current_book: str = ""

    @property
    def skill(self) -> str:
        return (ROOT / "prompts/ace/role_skills_v3/reflector.md").read_text()

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
def reflect_learning_repairs(
    problem_file: str,
    playbook: str,
    trajectory: str,
    terminal: TerminalEvidence,
    events: tuple[TrainingEvent, ...],
    current_book: str = "",
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
                current_book=current_book,
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
        q = ReflectLearningRepairs(
            spec,
            playbook,
            trajectory,
            terminal,
            events,
            tuple(submitted.values()),
            tuple(dialogue),
            turn < 3,
            current_book=current_book,
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
class ProposeLearningEdits(
    dp.Query[
        dp.Response[
            LearningPlan | BookPlan | dp.WrappedParseError,
            CheckAdviceSnippet | FindBookRules,
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
    strict_actions: bool = True
    targeted_demos: bool = False

    @property
    def skill(self) -> str:
        base = (
            ROOT / f"prompts/ace/role_skills_v2/{self.role}.md"
        ).read_text()
        if self.targeted_demos and self.role == "curator":
            base += (
                "\n"
                + (ROOT / "prompts/ace/role_skills_v3/curator.md").read_text()
            )
        return base

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
        return dp.structured_as(
            LearningPlan if self.strict_actions else BookPlan
        ).wrap_errors.response_with(
            CheckAdviceSnippet | FindBookRules if self.allow_tools else Never
        )

    def advertised_tools(self) -> Sequence[type[dp.AbstractTool[Any]]]:
        return [CheckAdviceSnippet, FindBookRules] if self.allow_tools else []


@dataclass
class JudgeLearningEdit(dp.Query[LearningVerdict | dp.WrappedParseError]):
    action: str
    proposed_rule: str
    target: str
    rules: str
    receipts: tuple[SnippetReceipt, ...]
    source_events: tuple[TrainingEvent, ...] = ()
    observations: tuple[LocalObservation, ...] = ()

    @property
    def receipt_evidence(self) -> str:
        return json.dumps(
            [
                dict(
                    receipt=r.identifier,
                    theorem=r.context.theorem_name,
                    context_id=r.context.identifier,
                    verified_prefix_before=r.context.prefix,
                    submitted_snippet=r.snippet,
                    accepted_prefix_after=r.checked.feedback.proof_so_far,
                    status=r.status,
                    whole_theorem_completed=r.status == "completed",
                    error=r.checked.feedback.error_message,
                    failing_tactic=r.checked.feedback.failing_tactic,
                    remaining_focused_goals=r.checked.feedback.remaining_goals,
                )
                for r in self.receipts
            ]
        )

    @property
    def event_evidence(self) -> str:
        return json.dumps([asdict(e) for e in self.source_events])

    @property
    def progress_evidence(self) -> str:
        return json.dumps([asdict(o) for o in self.observations])

    def parser(self) -> Any:
        return dp.structured_as(LearningVerdict).wrap_errors


@dp.strategy
def write_learning_book_edits(
    role: Literal["curator", "reducer"],
    book: Playbook,
    evidence: str,
    contexts: tuple[SnippetContext, ...],
    drafts: tuple[UnverifiedSnippetDraft, ...],
    receipts: tuple[SnippetReceipt, ...] = (),
    source_events: tuple[TrainingEvent, ...] = (),
    strict_actions: bool = True,
    evidence_review: bool = True,
    targeted_demos: bool = False,
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
    observations: dict[str, LocalObservation] = {}
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
                source_events=[asdict(e) for e in source_events],
                strict_actions=strict_actions,
                evidence_review=evidence_review,
                targeted_demos=targeted_demos,
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
        q = ProposeLearningEdits(
            role,
            book,
            evidence,
            tuple(bank.values()),
            drafts,
            tuple(verified.values()),
            tuple(dialogue),
            turn < 3,
            strict_actions=strict_actions,
            targeted_demos=targeted_demos,
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
            if isinstance(answer, LearningPlan):
                answer = answer.legacy()
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
            selected_receipts = tuple(
                resolve(r, "r", tuple(verified.values())) for r in selected
            )
            rules = ProposeLearningEdits(role, review_book, "", (), ()).rules
            if evidence_review:
                for receipt in selected_receipts:
                    if receipt.identifier not in observations:
                        if seconds < 180:
                            observation = yield from dp.compute(
                                observe_local_progress
                            )(
                                receipt,
                                dict(
                                    seconds=min(10.0, 180 - seconds),
                                    rpc_calls=128,
                                    view_bytes=8192,
                                ),
                            )
                            seconds += observation.elapsed
                        else:
                            observation = LocalObservation(
                                receipt.identifier,
                                "unknown",
                                None,
                                None,
                                (),
                                (),
                                "Shared verifier allowance exhausted",
                            )
                        observations[receipt.identifier] = observation
                event_contexts = {
                    r.context.identifier for r in selected_receipts
                }
                draft = resolve(decision.draft, "d", drafts)
                event_contexts.add(draft.context_id)
                reviewed = yield from dp.branch(
                    JudgeLearningEdit(
                        decision.action,
                        decision.content,
                        decision.closest_rule,
                        rules,
                        selected_receipts,
                        source_events_for(event_contexts, source_events),
                        tuple(
                            observations[r.identifier]
                            for r in selected_receipts
                        ),
                    ).using(dp.ambient_pp)
                )
                verdict = (
                    reviewed
                    if isinstance(reviewed, dp.WrappedParseError)
                    else reviewed.legacy()
                )
            else:
                verdict = yield from dp.branch(
                    JudgeBookEdit(
                        decision.action,
                        decision.content,
                        decision.closest_rule,
                        rules,
                        selected_receipts,
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


def learning_examples() -> ExampleSelector:
    def tags(query: dp.AbstractQuery[Any]) -> frozenset[str]:
        # The shared book contains almost every operation tag. Matching it
        # would collapse relevance scores into a constant for every example.
        if isinstance(query, ProposeLearningEdits):
            text = " ".join(
                d.error + " " + d.purpose + " " + " ".join(d.remaining_goals)
                for d in query.drafts
            )
        elif isinstance(query, (JudgeLearningEdit, JudgeBookEdit)):
            text = " ".join(
                r.snippet + " " + (r.checked.feedback.error_message or "")
                for r in query.receipts
            )
        elif isinstance(query, ReflectLearningRepairs):
            text = " ".join(e.error + " " + e.submitted for e in query.events)
        else:
            text = ""
        return operation_tags(text)

    def sources(query: dp.AbstractQuery[Any]) -> set[str]:
        if isinstance(query, ReflectLearningRepairs):
            return {query.spec.theorem_name}
        if isinstance(query, ProposeLearningEdits):
            return {c.theorem_name for c in query.contexts}
        if isinstance(query, (JudgeLearningEdit, JudgeBookEdit)):
            return {r.context.theorem_name for r in query.receipts}
        return set()

    def select(
        env: dp.PolicyEnv, query: dp.AbstractQuery[Any]
    ) -> Sequence[SelectedExample]:
        family = example_families()
        excluded = {family.get(n, n) for n in sources(query)}
        query_tags = tags(query)
        candidates: list[tuple[int, int, Any]] = []
        for i, example in enumerate(
            env.examples.examples_for(type(query).__name__)
        ):
            q = example.query
            if isinstance(query, ProposeLearningEdits) and isinstance(
                q, ProposeLearningEdits
            ):
                if (
                    query.role != q.role
                    or query.strict_actions != q.strict_actions
                    or query.targeted_demos != q.targeted_demos
                ):
                    continue
            if excluded & {family.get(n, n) for n in sources(q)}:
                continue
            score = len(query_tags & tags(q))
            candidates.append((-score, i, example))
        limit = (
            2
            if isinstance(query, JudgeLearningEdit)
            or isinstance(query, ProposeLearningEdits)
            and query.targeted_demos
            else 1
        )
        return [
            SelectedExample(example=e, index=i, similarity=None)
            for _, i, e in sorted(candidates, key=lambda x: (x[0], x[1]))[
                :limit
            ]
        ]

    return ExampleSelector(select)


@dataclass(frozen=True)
class PlanPilot:
    plan: BookPlan | None
    error: str


@dp.strategy
def learning_plan_pilot(
    query: ProposeLearningEdits,
) -> dp.Strategy[dp.Branch, dp.PromptingPolicy, PlanPilot]:
    """One matched decision query; preserve failures without a paid retry."""
    response = yield from dp.branch(query.using(dp.ambient_pp))
    if isinstance(response.parsed, dp.ToolRequests):
        return PlanPilot(
            None, "Decision pilot returned tools instead of a final"
        )
    answer = response.parsed.final
    if isinstance(answer, dp.WrappedParseError):
        return PlanPilot(None, str(answer.error))
    plan = answer.legacy() if isinstance(answer, LearningPlan) else answer
    try:
        validate_plan(
            plan, query.book, query.drafts, query.receipts, query.contexts
        )
    except ValueError as exc:
        return PlanPilot(None, str(exc))
    return PlanPilot(plan, "")


@dp.strategy
def learning_review_pilot(
    query: JudgeLearningEdit,
) -> dp.Strategy[
    dp.Branch, dp.PromptingPolicy, LearningVerdict | dp.WrappedParseError
]:
    return (yield from dp.branch(query.using(dp.ambient_pp)))


def learning_role_policy(
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
        select_examples=learning_examples(),
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
