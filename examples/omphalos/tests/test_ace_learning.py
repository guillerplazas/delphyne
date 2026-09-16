"""Observed role failures, real Rocq observations and recovery; no API calls."""

# ruff: noqa: E402
from runtime.ace_learning_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict, replace
import json
from typing import Any, Literal

import delphyne as dp
from delphyne.stdlib.mock import fixed_oracle
from delphyne.utils.typing import pydantic_load
from pydantic import TypeAdapter, ValidationError
import pytest

from ace.learning_contracts import (
    LearningPlan,
    LearningVerdict,
    learning_plan,
    observe_local_progress,
)
from ace.role_contracts import TrainingEvent
from ace.role_revision import (
    BookPlan,
    EditIntent,
    WriterProduct,
    apply_product,
    bind_repair,
    LocalRepair,
)
from ace.rocq_snippets import SnippetReceipt, check_snippet
from experiments import ace_learning_experiment as c
from prove_ace_learning import (
    JudgeLearningEdit,
    ProposeLearningEdits,
    write_learning_book_edits,
)
from prove_grounded import grounded_search


def trig_receipt() -> SnippetReceipt:
    raw = json.loads((c.PRIOR / "revisions/3.json").read_text())
    return next(
        pydantic_load(SnippetReceipt, r)
        for r in raw["writer"]["receipts"]
        if r["context"]["theorem_name"] == "imo_1963_p5"
        and "replace (2 * PI / 7)" in r["snippet"]
    )


@pytest.mark.parametrize(
    "extra",
    [
        dict(receipts=["r1"]),
        dict(content="text"),
        dict(section="pitfalls"),
        dict(failure_receipt="r1"),
        dict(closest_rule="b1"),
    ],
)
def test_drop_has_no_irrelevant_fields(extra: dict[str, Any]) -> None:
    raw = dict(
        reasoning="x",
        decisions=[
            dict(draft="d1", action="drop", reason="Unsupported", **extra)
        ],
    )
    with pytest.raises(ValidationError):
        pydantic_load(LearningPlan, raw)
    schema = TypeAdapter(LearningPlan).json_schema()["$defs"]["DropDraft"]
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"draft", "action", "reason"}


@pytest.mark.parametrize("action", ["add", "update", "example", "drop"])
def test_action_adapter_preserves_internal_contract(
    action: Literal["add", "update", "example", "drop"],
) -> None:
    intent = EditIntent(
        "d1",
        action,
        "" if action == "drop" else "b1",
        "pitfalls" if action in ("add", "update") else "",
        "A compact rule" if action in ("add", "update") else "",
        "Reason",
        () if action == "drop" else ("r2",),
        "r1" if action == "update" else "",
    )  # type: ignore[arg-type]
    plan = BookPlan("reasoning", (intent,))
    encoded = asdict(learning_plan(plan))
    assert pydantic_load(LearningPlan, encoded).legacy() == plan


def test_unknown_review_cannot_authorize_an_edit() -> None:
    assert (
        LearningVerdict("unknown", "new_operation", "b1", "Missing evidence")
        .legacy()
        .relation
        == "unsupported"
    )


def test_live_original_trig_obligation_is_closed_but_theorem_is_open() -> None:
    receipt = trig_receipt()
    rechecked = check_snippet(
        receipt.context,
        receipt.snippet,
        dict(seconds=30, rpc_calls=128, view_bytes=8192),
    )
    assert rechecked.identifier == receipt.identifier
    observed = observe_local_progress(
        receipt, dict(seconds=30, rpc_calls=128, view_bytes=8192)
    )
    assert observed.outcome == "original_obligation_closed"
    assert observed.before and observed.after
    assert len(observed.before.focused_goals) == 1
    assert not observed.after.focused_goals
    assert len(observed.after.existential_names) == 1
    assert observed.discharged and not observed.introduced
    assert receipt.status == "executed_open"


def test_live_open_assertion_is_not_proven_progress() -> None:
    context = trig_receipt().context
    receipt = check_snippet(
        context,
        "assert (Hunproved : False).",
        dict(seconds=30, rpc_calls=128, view_bytes=8192),
    )
    assert receipt.executable
    observed = observe_local_progress(
        receipt, dict(seconds=30, rpc_calls=128, view_bytes=8192)
    )
    assert observed.outcome == "obligations_open"
    assert observed.introduced


def test_live_shelving_is_not_local_completion() -> None:
    context = trig_receipt().context
    receipt = check_snippet(
        context, "shelve.", dict(seconds=30, rpc_calls=128, view_bytes=8192)
    )
    observed = observe_local_progress(
        receipt, dict(seconds=30, rpc_calls=128, view_bytes=8192)
    )
    assert observed.outcome in ("unknown", "not_executed")


def test_live_unavailable_observation_remains_unknown() -> None:
    observed = observe_local_progress(
        trig_receipt(), dict(seconds=30, rpc_calls=1, view_bytes=8192)
    )
    assert observed.outcome == "unknown"
    assert not observed.discharged


def test_source_drift_and_inexact_prefix_are_rejected() -> None:
    receipt = trig_receipt()
    with pytest.raises(ValueError, match="drift"):
        observe_local_progress(
            replace(
                receipt,
                context=replace(receipt.context, problem_sha256="wrong"),
            ),
            dict(seconds=30),
        )
    with pytest.raises(ValueError, match="complete snippet"):
        observe_local_progress(
            replace(receipt, snippet="idtac."), dict(seconds=30)
        )


def test_partial_writer_and_budget_stop_retain_receipts() -> None:
    raw = json.loads((c.PRIOR / "revisions/1.json").read_text())
    product = pydantic_load(WriterProduct, raw["writer"])
    book = pydantic_load(c.Playbook, raw["before"])
    draft = product.drafts[0]
    ctx = next(x for x in product.contexts if x.identifier == draft.context_id)
    receipt = next(
        x
        for x in product.receipts
        if x.context.identifier == ctx.identifier and x.executable
    )

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, ProposeLearningEdits)
        yield dp.Answer(
            None,
            dp.Structured(
                dict(
                    reasoning="bad final",
                    decisions=[
                        dict(
                            draft="d1",
                            action="drop",
                            reason="Drop",
                            receipts=["r1"],
                        )
                    ],
                )
            ),
        )

    policy = (
        grounded_search() @ dp.elim_messages(show_in_log=False)
    ) & fixed_oracle(oracle)
    vals, _ = (
        write_learning_book_edits(
            "curator",
            book,
            "Existing checked receipt",
            (ctx,),
            (draft,),
            (receipt,),
        )
        .run_toplevel(c.context().policy_env(), policy)
        .collect()
    )
    result = vals[0].tracked.value
    assert result.status == "partial" and result.receipts == (receipt,)
    assert result.drafts == (draft,)


def test_live_review_reuses_receipts_and_preserves_atomic_application() -> (
    None
):
    raw = json.loads((c.PRIOR / "sources/amc12a_2020_p13.json").read_text())
    event = pydantic_load(TrainingEvent, raw["events"][3])
    code = "{ assert (Htwo : (2:R) = INR 2) by (cbv [INR]; ring). rewrite Htwo. apply le_INR. lia. }"
    bad = check_snippet(
        event.context,
        event.submitted,
        dict(seconds=30, rpc_calls=128, view_bytes=8192),
    )
    good = check_snippet(
        event.context, code, dict(seconds=30, rpc_calls=128, view_bytes=8192)
    )
    assert bad.status == "rejected" and good.executable
    draft = bind_repair(
        LocalRepair(
            event.identifier,
            "Malformed cast recipe",
            "Use equality bridge",
            "Closed real numeral versus INR",
            code,
        ),
        (event,),
    )
    book = c.Playbook.load(c.BOOK)
    idx = next(i for i, b in enumerate(book.bullets) if b.id == "rocq-00015")
    intent = EditIntent(
        "d1",
        "update",
        f"b{idx + 1}",
        book.bullets[idx].section,
        "Prove the closed real numeral equals its INR form with cbv [INR] and ring; rewrite before le_INR. Direct change need not be convertible.",
        "Repair a demonstrated cast recipe",
        ("r2",),
        "r1",
    )
    plan = learning_plan(BookPlan("Local correction", (intent,)))
    queries: list[str] = []

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        queries.append(q.query_name())
        if isinstance(q, ProposeLearningEdits):
            answer: Any = plan
        else:
            assert isinstance(q, JudgeLearningEdit)
            assert event in q.source_events
            assert len(q.observations) == 2
            answer = LearningVerdict(
                "supported",
                "correction",
                intent.closest_rule,
                "The rejected recipe and checked equality bridge establish the source-local correction",
            )
        yield dp.Answer(None, dp.Structured(asdict(answer)))

    policy = (
        grounded_search() @ dp.elim_messages(show_in_log=False)
    ) & fixed_oracle(oracle)
    values, budget = (
        write_learning_book_edits(
            "reducer",
            book,
            "Source repair",
            (event.context,),
            (draft,),
            (bad, good),
            (event,),
        )
        .run_toplevel(c.context().policy_env(), policy)
        .collect()
    )
    product = values[0].tracked.value
    assert product.status == "complete"
    assert product.receipts == (bad, good)
    assert queries == ["ProposeLearningEdits", "JudgeLearningEdit"]
    assert budget["rocq_seconds"] > 0
    revision = apply_product(book, product)
    assert revision.after.bullets[idx].id == book.bullets[idx].id
    assert len(revision.after.bullets) == len(book.bullets)
    with pytest.raises(ValueError, match="Stale"):
        apply_product(revision.after, product)


def test_generated_demonstrations_parse_and_match_source_exclusion() -> None:
    from delphyne.scripts.demonstrations import check_demo_file
    from prove_ace_learning import learning_examples
    from prove_ace_roles import example_families

    feedback = check_demo_file(
        c.ROOT / "demos/ace_learning.demo.yaml", c.context(), c.ROOT
    )
    assert not feedback.errors and not feedback.warnings
    env = c.context().policy_env()
    families = example_families()
    for case in c.read("pilot_registration.json")["cases"]:
        if case["treatment"] not in ("schema", "review"):
            continue
        query = pydantic_load(
            ProposeLearningEdits
            if case["treatment"] == "schema"
            else JudgeLearningEdit,
            c.read(case["input"])["query"],
        )
        sources = (
            {x.theorem_name for x in query.contexts}
            if isinstance(query, ProposeLearningEdits)
            else {x.context.theorem_name for x in query.receipts}
        )
        selected = learning_examples()(env, query)
        assert selected
        for example in selected:
            q = example.query
            other: set[str] = (
                {x.theorem_name for x in q.contexts}
                if isinstance(q, ProposeLearningEdits)
                else {x.context.theorem_name for x in q.receipts}
                if isinstance(q, JudgeLearningEdit)
                else set()
            )
            assert not (
                {families.get(n, n) for n in sources}
                & {families.get(n, n) for n in other}
            )


def test_matched_proof_controller_and_full_arguments() -> None:
    # The control jobs never dispatch; they exercise the new config adapter
    # and compare every generator input against the 120 compatible sources.
    for stage in ("training", "validation"):
        for job in c.proof_jobs(stage, "control"):
            args = job.instantiate(None)
            old = c.prior_result(stage, "proof", job.bench_name, job.seed)[
                "args"
            ]
            assert args.args == old["args"]
            assert args.strategy == old["strategy"]
            assert args.policy == old["policy"]
            assert args.budget == old["budget"]


def test_new_curator_budget_stop_preserves_checked_work(tmp_path: Any) -> None:
    from runtime.ace_role_journal import RoleJournal, checkpoint_roles

    raw = json.loads((c.PRIOR / "revisions/1.json").read_text())
    product = pydantic_load(WriterProduct, raw["writer"])
    draft = product.drafts[0]
    ctx = next(x for x in product.contexts if x.identifier == draft.context_id)
    receipt = next(
        r
        for r in product.receipts
        if r.context.identifier == ctx.identifier and r.executable
    )

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        yield dp.Answer(
            None,
            "",
            tool_calls=(
                dp.ToolCall(
                    "CheckAdviceSnippet",
                    dict(context="c1", snippet=receipt.snippet),
                ),
            ),
        )

    vals, spent = (
        write_learning_book_edits(
            "curator",
            pydantic_load(c.Playbook, raw["before"]),
            "",
            (ctx,),
            (draft,),
        )
        .run_toplevel(
            c.context().policy_env(),
            (grounded_search() @ checkpoint_roles(str(tmp_path)))
            & fixed_oracle(oracle),
        )
        .collect(budget=dp.BudgetLimit(dict(num_requests=1)))
    )
    latest = RoleJournal(tmp_path).latest()
    assert not vals and spent["num_requests"] == 1
    assert latest is not None and isinstance(latest.product, WriterProduct)
    assert latest.product.status == "partial" and latest.product.plan is None
    assert latest.product.receipts[0].identifier == receipt.identifier


def test_paired_report_refuses_missing_cell() -> None:
    from tools.reports.ace_learning_results import paired

    result = paired("training", "A", [])
    assert not result["complete"] and len(result["missing_b"]) == 40


def test_control_cache_replay_has_no_new_charge() -> None:
    # A success and two different failure paths, with HTTP forbidden by
    # capture; no archived checkpoint writes are permitted.
    from contextlib import redirect_stdout
    from dataclasses import replace
    import io
    from pathlib import Path
    from unittest.mock import patch
    from delphyne.stdlib.commands.run_strategy import run_strategy
    from delphyne.stdlib.tasks import run_command
    from runtime.campaign_budget import CampaignResponsesModel

    before = c.accounting()["receipts"]
    for n in ("imo_1983_p6", "imo_1963_p5", "imo_1968_p5_1"):
        raw = c.prior_result("training", "proof", n)
        args = pydantic_load(dp.RunStrategyArgs, raw["args"])
        args.cache_mode = "replay"
        args.cache_file = str(
            c.prior_directory("training", "proof", n) / "cache.yaml"
        )
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        c.activate("training", events=False)
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("No HTTP"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            outcome = run_command(
                run_strategy,
                args,
                ctx=replace(c.context(), cache_root=Path("/")),
                add_header=False,
            )
        expected = raw["outcome"]["result"]
        assert outcome.result is not None
        assert outcome.result.success == expected["success"]
        assert outcome.result.spent_budget == expected["spent_budget"]
        assert (
            json.loads(json.dumps(list(outcome.result.values)))
            == expected["values"]
        )
    assert c.accounting()["receipts"] == before
