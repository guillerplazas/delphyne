"""Scoped writer contracts, real Rocq, handoff and full request translation."""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from collections.abc import Iterable, Sequence
from dataclasses import asdict, replace
import json
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
import yaml

from ace.rocq_snippets import check_snippet
from experiments import writer_draft_experiment as c
from prove_grounded import grounded_search
from prove_snippets import SnippetAddition, WriteCheckedRocqAdvice
from prove_writer_drafts import (
    DraftAdvice,
    DraftDecision,
    UnverifiedSnippetDraft,
    WriteRocqDraftAdvice,
    draft_examples,
    reduction_input,
    validate_decisions,
    write_rocq_drafts,
)
from tools.reports import reducer_tool_study as study


def draft() -> UnverifiedSnippetDraft:
    return UnverifiedSnippetDraft(
        "square",
        study.source().identifier,
        study.BAD,
        "Square nonnegativity absent from empty book",
        "offline real-Rocq witness",
    )


def answer(advice: DraftAdvice) -> dp.Answer:
    return dp.Answer(
        None, "```yaml\n" + yaml.safe_dump(asdict(advice)) + "```"
    )


def test_repair_and_curator_reducer_handoff() -> None:
    calls: list[WriteRocqDraftAdvice] = []

    def oracle(query: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(query, WriteRocqDraftAdvice)
        calls.append(query)
        if not query.receipts:
            yield dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "CheckRocqSnippet",
                        dict(
                            context_id=study.source().identifier,
                            snippet=study.BAD,
                        ),
                    ),
                ),
            )
        elif not any(r.executable for r in query.receipts):
            yield dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "CheckRocqSnippet",
                        dict(
                            context_id=study.source().identifier,
                            snippet=study.GOOD,
                        ),
                    ),
                ),
            )
        else:
            rid = next(r.identifier for r in query.receipts if r.executable)
            yield answer(
                DraftAdvice(
                    "Checked correction",
                    (
                        SnippetAddition(
                            "tactics", "Source-local square bridge", (rid,)
                        ),
                    ),
                    (rid,),
                    (),
                    (
                        DraftDecision(
                            "square",
                            "retain",
                            "Useful in this empty book",
                            (rid,),
                        ),
                    ),
                )
            )

    with patch.object(
        c.CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("HTTP forbidden"),
    ):
        policy = grounded_search() & fixed_oracle(oracle)
        vals, budget = (
            write_rocq_drafts("curator", "", "", (study.source(),), (draft(),))
            .run_toplevel(c.context().policy_env(), policy)
            .collect(budget=dp.BudgetLimit(dict(rocq_seconds=180)))
        )
        assert len(vals) == 1 and budget["rocq_seconds"] > 0
        product = vals[0].tracked.value
        assert [r.status for r in product.checked.receipts] == [
            "rejected",
            "executed_open",
        ]
        assert len(calls) == 3
        args = reduction_input([product], (study.source(),), "")
        vals, budget = (
            write_rocq_drafts(**args)
            .run_toplevel(c.context().policy_env(), policy)
            .collect(budget=dp.BudgetLimit(dict(rocq_seconds=180)))
        )
        assert len(vals) == 1 and budget["rocq_seconds"] == 0
        assert len(calls) == 4
        assert vals[0].tracked.value.checked.delta == product.checked.delta
        assert vals[0].tracked.value.drafts == product.drafts


def test_decision_contract_rejects_missing_forged_and_wrong_source() -> None:
    source = study.source()
    receipt = check_snippet(
        source, study.GOOD, dict(seconds=60, rpc_calls=512, view_bytes=8192)
    )
    with pytest.raises(ValueError, match="exactly one"):
        validate_decisions(DraftAdvice(""), (draft(),), (receipt,), (source,))
    with pytest.raises(ValueError, match="actual source"):
        a = DraftAdvice(
            "",
            retained_receipts=("invented",),
            decisions=(
                DraftDecision("square", "retain", "reason", ("invented",)),
            ),
        )
        validate_decisions(a, (draft(),), (receipt,), (source,))
    other = replace(receipt, context=replace(source, source="unrelated"))
    with pytest.raises(ValueError, match="actual source"):
        a = DraftAdvice(
            "",
            retained_receipts=(other.identifier,),
            decisions=(
                DraftDecision(
                    "square", "retain", "reason", (other.identifier,)
                ),
            ),
        )
        validate_decisions(a, (draft(),), (other,), (source,))
    dropped = DraftAdvice(
        "Redundant",
        decisions=(
            DraftDecision("square", "drop", "Already in the playbook"),
        ),
    )
    validate_decisions(dropped, (draft(),), (), (source,))


def test_all_initial_requests_and_demos_translate_without_dangling_calls() -> (
    None
):
    path = c.ROOT / "demos/writer_drafts.demo.yaml"
    feedback = check_demo_file(path, c.context(), c.ROOT)
    assert not feedback.errors, feedback.errors
    env = c.context().policy_env()
    rows: list[dict[str, Any]] = []
    for cfg in c.configs(0):
        args = cfg.instantiate(None)
        assert __import__("os").environ["OMPHALOS_CAMPAIGN_CELL"] == c.name(
            cfg, None
        )
        item = args.args
        qtype = (
            WriteRocqDraftAdvice
            if cfg.arm == "draft"
            else WriteCheckedRocqAdvice
        )
        query = pydantic_load(qtype, item)
        examples: Sequence[dp.Example] = (
            draft_examples()(env, query) if cfg.arm == "draft" else []
        )
        chat = create_prompt(query, tuple(examples), {}, None, env.templates)
        wire, _ = translate_chat_for_responses(
            LLMRequest(chat=chat, options={}), None, True
        )
        wire = json.loads(json.dumps(wire))
        calls = [
            i["call_id"] for i in wire if i.get("type") == "function_call"
        ]
        outputs = [
            i["call_id"]
            for i in wire
            if i.get("type") == "function_call_output"
        ]
        assert calls == outputs
        rows.append(
            dict(
                cell=c.name(cfg, None),
                examples=len(examples),
                calls=len(calls),
            )
        )
        if cfg.arm == "draft" and any(
            p["theorem_name"] == "mathd_algebra_28"
            for p in cast(list[dict[str, Any]], item["contexts"])
        ):
            assert not examples
    assert sum(r["examples"] for r in rows) == 8
    assert len(rows) == 20


def test_final_phase_and_forged_decisions_cannot_produce_advice() -> None:
    queries: list[WriteRocqDraftAdvice] = []

    def oracle(query: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(query, WriteRocqDraftAdvice)
        queries.append(query)
        yield answer(DraftAdvice("No decisions supplied"))

    vals, _ = (
        write_rocq_drafts("reducer", "", "", (study.source(),), (draft(),))
        .run_toplevel(
            c.context().policy_env(), grounded_search() & fixed_oracle(oracle)
        )
        .collect()
    )
    assert not vals and len(queries) == 4
    assert not queries[-1].advertised_tools()
