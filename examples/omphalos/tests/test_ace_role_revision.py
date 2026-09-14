"""Regression tests for observed ACE failures; no paid model calls."""

# ruff: noqa: E402
from runtime.ace_roles_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict, replace
import json
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import delphyne as dp
from delphyne.scripts.demonstrations import check_demo_file
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.queries import create_prompt
from delphyne.utils.typing import pydantic_load
import pytest

from ace.ace_playbook import Playbook
from ace.role_contracts import TrainingEvent
from ace.role_revision import (
    BookPlan,
    EditIntent,
    NoveltyVerdict,
    ReflectionFinish,
    ReflectionProduct,
    WriterProduct,
    apply_edits,
    apply_product,
    approve_edit,
    bind_repair,
    reduction_input,
    rule_examples,
    validate_finish,
    validate_plan,
)
from ace.rocq_snippets import check_snippet
from experiments import ace_roles_experiment as c
from prove_ace_role_revision import (
    JudgeBookEdit,
    ProposeBookEdits,
    ReflectLocalRepairs,
    reflect_local_repairs,
    revision_examples,
    write_reviewed_book_edits,
)
from prove_ace_roles import RoleResponsesModel
from prove_grounded import grounded_search
from runtime.campaign_pause import CampaignPaused, PauseAwareRoleModel
from runtime.ace_role_journal import (
    RoleCheckpoint,
    RoleJournal,
    checkpoint_roles,
)
from runtime.model_registry import pricing_for
from tools.data.ace_role_revision_demos import (
    GOOD_CODE,
    RULE,
    context,
    local_repair,
    source,
)


def demonstration() -> dict[str, Any]:
    return c.read("platform_v2/demonstration.json")


def checked_product() -> WriterProduct:
    return pydantic_load(WriterProduct, demonstration()["curator"])


def test_local_drafts_do_not_require_a_completed_theorem() -> None:
    _, events, terminal = source()
    draft = bind_repair(local_repair(), events)
    assert terminal.status == "not_solved" and draft.proposed_code
    validate_finish(
        ReflectionFinish("done", "Still only an unverified local repair"),
        (draft,),
    )
    with pytest.raises(ValueError, match="choose action=done"):
        validate_finish(
            ReflectionFinish("abstain", "No complete proof"), (draft,)
        )
    with pytest.raises(ValueError, match="event must"):
        bind_repair(replace(local_repair(), event="e999"), events)
    with pytest.raises(ValueError, match="preconditions"):
        bind_repair(replace(local_repair(), preconditions=""), events)


def test_invalid_reflector_final_preserves_the_actual_local_draft() -> None:
    raw, events, terminal = source()
    queries: list[ReflectLocalRepairs] = []

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, ReflectLocalRepairs)
        queries.append(q)
        if not q.submitted:
            yield dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "SubmitLocalRepair",
                        dict(repair=asdict(local_repair())),
                    ),
                ),
            )
        else:
            yield dp.Answer(
                None,
                dp.Structured(
                    asdict(ReflectionFinish("abstain", "No complete theorem"))
                ),
            )

    vals, _ = (
        reflect_local_repairs(
            terminal.problem_file, "", raw["trajectory"], terminal, events
        )
        .run_toplevel(
            context().policy_env(),
            (grounded_search() @ dp.elim_messages(show_in_log=False))
            & fixed_oracle(oracle),
        )
        .collect()
    )
    product = vals[0].tracked.value
    assert product.status == "partial" and len(product.drafts) == 1
    assert product.drafts[0].context_id == events[-1].context.identifier
    assert any("choose action=done" in s for s in product.diagnostics)
    env = context().policy_env()
    rendered = create_prompt(queries[-1], (), {}, None, env.templates)
    assert any("choose action=done" in str(message) for message in rendered)


def test_invalid_curator_final_preserves_checks_for_reducer() -> None:
    current = checked_product()
    book = Playbook.load(c.BOOK)

    def failing(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, ProposeBookEdits)
        if not q.receipts:
            idx = next(
                i
                for i, x in enumerate(q.contexts)
                if x.identifier == q.drafts[0].context_id
            )
            yield dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "CheckAdviceSnippet",
                        dict(context=f"c{idx + 1}", snippet=GOOD_CODE),
                    ),
                ),
            )
        else:
            yield dp.Answer(
                None, dp.Structured(asdict(BookPlan("Incomplete final", ())))
            )

    vals, spent = (
        write_reviewed_book_edits(
            "curator", book, "", current.contexts, current.drafts
        )
        .run_toplevel(
            context().policy_env(),
            (grounded_search() @ dp.elim_messages(show_in_log=False))
            & fixed_oracle(failing),
        )
        .collect()
    )
    failed = vals[0].tracked.value
    assert failed.status == "partial" and failed.plan is None
    assert failed.receipts and failed.receipts[0].executable
    assert spent["rocq_seconds"] > 0
    original = ReflectionProduct(
        "partial", current.drafts, current.contexts, ()
    )
    args = reduction_input((failed,), (original,), book)
    assert (
        args["receipts"] == failed.receipts
        and args["drafts"] == current.drafts
    )
    assert not failed.edits


def test_independent_judgment_routes_duplicate_to_evidence_only() -> None:
    product = checked_product()
    assert product.plan is not None
    d = product.plan.decisions[0]
    book = Playbook.load(c.BOOK)
    verdict = NoveltyVerdict(
        "duplicate", d.closest_rule, "Already covered by the existing rule"
    )
    edit = approve_edit(d, verdict, book, product.receipts)
    assert edit is not None and edit.action == "example" and not edit.content
    after, evidence = apply_edits(book, book.sha256(), (edit,))
    assert after.sha256() == book.sha256() and evidence[0].receipts
    assert (
        approve_edit(
            d, replace(verdict, relation="unsupported"), book, product.receipts
        )
        is None
    )


def test_only_compact_new_rule_enters_prompt() -> None:
    data = demonstration()
    product = pydantic_load(WriterProduct, data["reducer"])
    before = Playbook.load(c.BOOK)
    after, _ = apply_edits(before, product.base_sha256, product.edits)
    assert len(after.bullets) == len(before.bullets) + 1
    assert after.bullets[-1].content == RULE
    assert GOOD_CODE not in after.render_prompt()
    assert after.token_estimate() - before.token_estimate() < 100
    revision = apply_product(before, product)
    assert revision.after.sha256() == after.sha256()
    assert rule_examples(revision, after.bullets[-1].id) == product.receipts
    with pytest.raises(ValueError, match="review trail"):
        apply_product(before, replace(product, edits=()))
    with pytest.raises(ValueError, match="complete reviewed"):
        apply_product(before, replace(product, status="partial"))


def test_budget_stop_keeps_checks_and_reducer_can_finish(
    tmp_path: Path,
) -> None:
    product = checked_product()
    book = Playbook.load(c.BOOK)

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, ProposeBookEdits)
        if not q.receipts:
            idx = next(
                i
                for i, x in enumerate(q.contexts)
                if x.identifier == q.drafts[0].context_id
            )
            yield dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "CheckAdviceSnippet",
                        dict(context=f"c{idx + 1}", snippet=GOOD_CODE),
                    ),
                ),
            )
        else:
            yield dp.Answer(
                None, dp.Structured(asdict(BookPlan("Invalid", ())))
            )

    vals, spent = (
        write_reviewed_book_edits(
            "curator", book, "", product.contexts, product.drafts
        )
        .run_toplevel(
            context().policy_env(),
            (grounded_search() @ checkpoint_roles(str(tmp_path)))
            & fixed_oracle(oracle),
        )
        .collect(budget=dp.BudgetLimit(dict(num_requests=1)))
    )
    assert not vals and spent["num_requests"] == 1
    checkpoint = RoleJournal(tmp_path).latest()
    assert checkpoint is not None and isinstance(
        checkpoint.product, WriterProduct
    )
    partial = checkpoint.product
    assert partial.status == "partial" and partial.plan is None
    assert partial.receipts[0].executable

    def finish(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        if isinstance(q, ProposeBookEdits):
            assert q.receipts and product.plan is not None
            answer = product.plan
        else:
            assert isinstance(q, JudgeBookEdit)
            answer = NoveltyVerdict(
                "new_operation", q.target, "Missing helper-premise operation"
            )
        yield dp.Answer(None, dp.Structured(asdict(answer)))

    vals, spent = (
        write_reviewed_book_edits(**reduction_input((partial,), (), book))
        .run_toplevel(
            context().policy_env(),
            (grounded_search() @ dp.elim_messages(show_in_log=False))
            & fixed_oracle(finish),
        )
        .collect()
    )
    reduced = vals[0].tracked.value
    assert spent["rocq_seconds"] == 0 and reduced.status == "complete"
    assert apply_product(book, reduced).after.bullets[-1].content == RULE


def test_budget_stop_preserves_submitted_reflection(tmp_path: Path) -> None:
    raw, events, terminal = source()

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, ReflectLocalRepairs)
        yield dp.Answer(
            None,
            "",
            tool_calls=(
                dp.ToolCall(
                    "SubmitLocalRepair", dict(repair=asdict(local_repair()))
                ),
            ),
        )

    vals, spent = (
        reflect_local_repairs(
            terminal.problem_file, "", raw["trajectory"], terminal, events
        )
        .run_toplevel(
            context().policy_env(),
            (grounded_search() @ checkpoint_roles(str(tmp_path)))
            & fixed_oracle(oracle),
        )
        .collect(budget=dp.BudgetLimit(dict(num_requests=1)))
    )
    latest = RoleJournal(tmp_path).latest()
    assert not vals and spent["num_requests"] == 1 and latest is not None
    assert isinstance(latest.product, ReflectionProduct)
    assert latest.product.drafts and latest.product.finish is None


def test_checkpoint_replay_cannot_erase_later_work(tmp_path: Path) -> None:
    product = checked_product()
    first = RoleCheckpoint(
        "episode", 0, replace(product, receipts=(), plan=None)
    )
    later = RoleCheckpoint("episode", 1, product)
    journal = RoleJournal(tmp_path)
    journal.write(asdict(first))
    journal.write(asdict(later))
    journal.write(asdict(first))
    assert journal.latest() == later
    with pytest.raises(ValueError, match="diverged"):
        journal.write(asdict(replace(later, product=first.product)))
    with pytest.raises(ValueError, match="different role episode"):
        journal.write(asdict(replace(later, episode="different")))


def test_review_sees_pending_rules_and_folds_another_example() -> None:
    current = checked_product()
    assert current.plan is not None
    book = Playbook.load(c.BOOK)
    first = current.plan.decisions[0]
    drafts = (
        *current.drafts,
        replace(current.drafts[0], draft_id="second-local-instance"),
    )
    second = replace(
        first, draft="d2", content=RULE + " Use symmetric equality."
    )
    reviews: list[JudgeBookEdit] = []

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        if isinstance(q, ProposeBookEdits):
            answer = BookPlan("Two local instances", (first, second))
        else:
            assert isinstance(q, JudgeBookEdit)
            reviews.append(q)
            rules = json.loads(q.rules)
            if len(reviews) == 1:
                assert len(rules) == len(book.bullets)
                answer = NoveltyVerdict(
                    "new_operation", q.target, "Missing operation"
                )
            else:
                assert rules[-1]["content"] == RULE
                answer = NoveltyVerdict(
                    "duplicate",
                    rules[-1]["alias"],
                    "First proposal already provides this operation",
                )
        yield dp.Answer(None, dp.Structured(asdict(answer)))

    vals, spent = (
        write_reviewed_book_edits(
            "reducer", book, "", current.contexts, drafts, current.receipts
        )
        .run_toplevel(
            context().policy_env(),
            (grounded_search() @ dp.elim_messages(show_in_log=False))
            & fixed_oracle(oracle),
        )
        .collect()
    )
    product = vals[0].tracked.value
    revision = apply_product(book, product)
    assert len(reviews) == 2 and spent["rocq_seconds"] == 0
    assert [e.action for e in product.edits] == ["add", "example"]
    assert len(revision.after.bullets) == len(book.bullets) + 1
    assert (
        rule_examples(revision, revision.after.bullets[-1].id)
        == current.receipts
    )


def test_exact_duplicate_backstop_keeps_one_rule_and_all_evidence() -> None:
    product = pydantic_load(WriterProduct, demonstration()["reducer"])
    book = Playbook.load(c.BOOK)
    edit = replace(product.edits[0], target_id="")
    duplicate = replace(edit, receipts=("another-checked-receipt",))
    after, applied = apply_edits(book, book.sha256(), (edit, duplicate))
    assert len(after.bullets) == len(book.bullets) + 1
    assert (
        applied[1].action == "example"
        and applied[1].receipts == duplicate.receipts
    )
    assert applied[0].target_id == applied[1].target_id == after.bullets[-1].id
    assert after.bullets[-1].helpful == 0


def test_actual_cast_rule_repair_is_local_and_atomic() -> None:
    src = c.read("sources/amc12a_2020_p13.json")
    event = pydantic_load(TrainingEvent, src["events"][3])
    bad = check_snippet(
        event.context,
        event.submitted,
        dict(seconds=60, rpc_calls=512, view_bytes=8192),
    )
    good = check_snippet(
        event.context,
        "{ assert (Htwo : (2:R) = INR 2) by (cbv [INR]; ring). rewrite Htwo. apply le_INR. lia. }",
        dict(seconds=60, rpc_calls=512, view_bytes=8192),
    )
    assert bad.status == "rejected" and good.executable
    book = Playbook.load(c.BOOK)
    idx = next(i for i, b in enumerate(book.bullets) if b.id == "rocq-00015")
    target = book.bullets[idx]
    draft = bind_repair(
        replace(local_repair(), event=event.identifier, code=event.submitted),
        (event,),
    )
    intent = EditIntent(
        "d1",
        "update",
        f"b{idx + 1}",
        target.section,
        "For a closed cast boundary, prove the real numeral equals its INR form with cbv [INR] and ring, rewrite using that equality, then apply le_INR and lia. Direct change need not be convertible.",
        "Correct the nonconvertible and malformed change example",
        ("r2",),
        "r1",
    )
    validate_plan(
        BookPlan("", (intent,)), book, (draft,), (bad, good), (event.context,)
    )
    edit = approve_edit(
        intent,
        NoveltyVerdict(
            "correction",
            intent.closest_rule,
            "The old change syntax is rejected; the checked equality bridge addresses that boundary",
        ),
        book,
        (bad, good),
    )
    assert edit is not None
    before = book.sha256()
    after, _ = apply_edits(book, before, (edit,))
    assert book.sha256() == before and len(after.bullets) == len(book.bullets)
    assert after.bullets[idx].id == target.id
    assert (after.bullets[idx].helpful, after.bullets[idx].harmful) == (
        target.helpful,
        target.harmful,
    )
    assert all(
        asdict(a) == asdict(b)
        for i, (a, b) in enumerate(zip(book.bullets, after.bullets))
        if i != idx
    )
    with pytest.raises(ValueError, match="Stale book"):
        apply_edits(after, before, (edit,))
    with pytest.raises(ValueError, match="Conflicting updates"):
        apply_edits(book, before, (edit, edit))
    with pytest.raises(ValueError, match="prompt budget"):
        apply_edits(book, before, (edit,), max_tokens=1)
    with pytest.raises(ValueError, match="same context"):
        validate_plan(
            BookPlan("", (intent,)),
            book,
            (draft,),
            (replace(bad, status="unknown"), good),
            (event.context,),
        )


@pytest.mark.parametrize(
    "content", ["", "x" * 701, "rule\nfull proof", "```rocq nra.```"]
)
def test_prompt_rule_cannot_absorb_a_full_proof(content: str) -> None:
    product = checked_product()
    assert product.plan is not None
    bad = replace(
        product.plan,
        decisions=(replace(product.plan.decisions[0], content=content),),
    )
    with pytest.raises(ValueError):
        validate_plan(
            bad,
            Playbook.load(c.BOOK),
            product.drafts,
            product.receipts,
            product.contexts,
        )


def test_pause_blocks_new_calls_before_reservation(tmp_path: Path) -> None:
    flag = tmp_path / "PAUSED"
    flag.write_text("stop")
    model = PauseAwareRoleModel(
        options={"model": "gpt-5.6-luna"},
        pricing=pricing_for("gpt-5.6-luna"),
        ledger_file=str(tmp_path / "never-created.sqlite3"),
        stage="offline",
        pause_file=str(flag),
        use_reasoning_cache=True,
        convert_user_feedback_to_tool=True,
    )
    req = LLMRequest(chat=(), options={})
    with patch.object(
        RoleResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("No transport allowed"),
    ):
        with pytest.raises(CampaignPaused):
            model._send_final_request(req)  # pyright: ignore[reportPrivateUsage]
    assert not (tmp_path / "never-created.sqlite3").exists()


def test_pause_during_inflight_call_keeps_its_actual_charge(
    tmp_path: Path,
) -> None:
    from types import SimpleNamespace
    from unittest.mock import MagicMock
    from openai.types.responses import ResponseUsage
    from runtime.campaign_budget import Ledger
    from runtime.campaign_pause import request_pause

    flag = tmp_path / "PAUSED"
    ledger = Ledger(tmp_path / "offline.sqlite3")
    ledger.create(1, {"offline": 1})
    model = PauseAwareRoleModel(
        options={"model": "gpt-5.6-luna"},
        pricing=pricing_for("gpt-5.6-luna"),
        ledger_file=str(ledger.path),
        stage="offline",
        pause_file=str(flag),
        use_reasoning_cache=True,
        convert_user_feedback_to_tool=True,
    )
    usage = ResponseUsage.model_validate(
        dict(
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            input_tokens_details={"cached_tokens": 10},
            output_tokens_details={"reasoning_tokens": 12},
        )
    )

    def response(**_: Any) -> Any:
        assert request_pause(flag, "Stop after this admitted call")
        assert not request_pause(flag, "Duplicate pause")
        return SimpleNamespace(
            id="offline", usage=usage, model="gpt-5.6-luna", status="completed"
        )

    client = MagicMock()
    client.__enter__.return_value = client
    client.responses.create.side_effect = response
    with (
        patch("openai.OpenAI", return_value=client),
        patch.object(
            RoleResponsesModel, "_parse_response", return_value=(None, [])
        ),
    ):
        req = LLMRequest(chat=(), options={})
        result = model.send_request(req, None)
        with pytest.raises(CampaignPaused):
            model.send_request(req, None)
    assert client.responses.create.call_count == 1
    assert result.budget and 0 < ledger.summary()["liability"] < 0.001
    with ledger.connect() as db:
        assert db.execute("SELECT status FROM receipts").fetchall() == [
            ("settled",)
        ]


def test_v2_policy_transport_and_checkpoint_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from delphyne.stdlib.commands.run_strategy import run_strategy
    from delphyne.stdlib.models import LLMOutput, LLMResponse
    from delphyne.stdlib.tasks import run_command

    product = checked_product()
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_LEDGER", str(tmp_path / "unused"))
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_STAGE", "offline")
    monkeypatch.setenv("OPENAI_API_KEY", "offline")
    monkeypatch.delenv("OMPHALOS_ADMISSION_EVENTS", raising=False)
    args = dp.RunStrategyArgs(
        strategy="write_reviewed_book_edits",
        args=dict(
            role="curator",
            book=asdict(Playbook.load(c.BOOK)),
            evidence="",
            contexts=[asdict(x) for x in product.contexts],
            drafts=[asdict(d) for d in product.drafts],
        ),
        policy="role_revision_policy",
        policy_args=dict(
            snapshot_directory=str(tmp_path / "transport"),
            pause_file=str(tmp_path / "PAUSED"),
        ),
        cache_file=str(tmp_path / "cache.yaml"),
        cache_mode="create",
        budget={},
        export_raw_trace=False,
        export_browsable_trace=False,
        export_log=False,
    )
    calls: list[LLMRequest] = []

    def dispatch(model: RoleResponsesModel, req: LLMRequest) -> LLMResponse:
        calls.append(req)
        model.reasoning_allowance += 100
        if len(calls) == 1:
            idx = next(
                i
                for i, x in enumerate(product.contexts)
                if x.identifier == product.drafts[0].context_id
            )
            out = LLMOutput(
                "",
                tool_calls=[
                    dp.ToolCall(
                        "CheckAdviceSnippet",
                        dict(context=f"c{idx + 1}", snippet=GOOD_CODE),
                    )
                ],
            )
        else:
            assert product.plan is not None
            out = LLMOutput(dp.Structured(asdict(product.plan)))
        return LLMResponse(
            [out],
            dp.Budget(
                dict(
                    price=0.001,
                    num_requests=1,
                    num_completions=1,
                    output_tokens=100,
                )
            ),
            [],
            "gpt-5.6-luna",
            {},
        )

    ctx = replace(context(), cache_root=Path("/"))
    with patch.object(
        RoleResponsesModel,
        "_send_final_request",
        autospec=True,
        side_effect=dispatch,
    ):
        live = run_command(run_strategy, args, ctx=ctx, add_header=False)
    assert live.result and live.result.success, live.diagnostics
    assert len(calls) == 2 and all(r.structured_output for r in calls)
    journal = RoleJournal(tmp_path / "transport/checkpoints")
    latest = journal.latest()
    assert latest and latest.product.status == "complete"
    args.cache_mode = "replay"
    with patch.object(
        RoleResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("HTTP forbidden"),
    ):
        replay = run_command(run_strategy, args, ctx=ctx, add_header=False)
    assert replay.result and replay.result.success, replay.diagnostics
    assert replay.result.values == live.result.values
    assert replay.result.spent_budget == live.result.spent_budget
    assert journal.latest() == latest


def test_demo_validation_and_rendered_tool_transcripts() -> None:
    ctx = context()
    feedback = check_demo_file(
        c.ROOT / "demos/ace_role_revision.demo.yaml", ctx, c.ROOT
    )
    assert not feedback.errors, feedback.errors
    env = ctx.policy_env()
    for kind in ("ReflectLocalRepairs", "ProposeBookEdits", "JudgeBookEdit"):
        for example in env.examples.examples_for(kind):
            q = example.query
            chat = create_prompt(q, (), {}, None, env.templates)
            wire, _ = translate_chat_for_responses(
                LLMRequest(chat=chat, options={}), None, True
            )
            items = cast(list[dict[str, Any]], wire)
            calls = [
                x["call_id"] for x in items if x.get("type") == "function_call"
            ]
            outputs = [
                x["call_id"]
                for x in items
                if x.get("type") == "function_call_output"
            ]
            assert calls == outputs
            assert not revision_examples()(env, q), (
                "Exclude the same source family"
            )
