"""Receipt disposition and complete request regressions; no API calls."""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from collections.abc import Iterable
from typing import Any

import delphyne as dp
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.queries import create_prompt
from delphyne.utils.typing import pydantic_load
import pytest

from ace.rocq_snippets import SnippetReceipt
from experiments import writer_receipt_experiment as c
from prove_grounded import grounded_search
from prove_writer_drafts import DraftAdvice, DraftDecision, draft_examples
from prove_writer_receipts import (
    WriteRocqReceiptAdvice,
    compile_receipt_advice,
    write_rocq_receipts,
)
from tests.test_writer_drafts import answer, draft
from tools.reports import reducer_tool_study as study


def test_known_failed_attempt_can_be_dropped_but_never_retained() -> None:
    row = next(
        r
        for r in c.prior.read("audit_seed0.json")["cells"]
        if r["case"] == "amc12_2000_p1" and r["arm"] == "draft"
    )
    receipts = tuple(
        pydantic_load(SnippetReceipt, r["receipt"]) for r in row["checks"]
    )
    bad = next(r.identifier for r in receipts if not r.executable)
    good = next(r.identifier for r in receipts if r.executable)
    from prove_snippets import SnippetAddition

    valid = DraftAdvice(
        "Keep the checked repair and acknowledge its failed predecessor",
        (SnippetAddition("tactics", "Simplify the source product", (good,)),),
        (good,),
        (bad,),
    )
    delta = compile_receipt_advice("curator", valid, receipts)
    assert len(delta.operations) == 1
    assert (
        next(r.snippet for r in receipts if r.identifier == good)
        in delta.operations[0].content
    )
    with pytest.raises(ValueError):
        compile_receipt_advice(
            "curator",
            DraftAdvice(
                "Invalid",
                (SnippetAddition("tactics", "bad", (bad,)),),
                (bad,),
                (good,),
            ),
            receipts,
        )
    with pytest.raises(ValueError, match="known receipts"):
        compile_receipt_advice(
            "curator",
            DraftAdvice("Invalid", dropped_receipts=("invented",)),
            receipts,
        )
    with pytest.raises(ValueError, match="known receipts"):
        compile_receipt_advice(
            "curator",
            DraftAdvice("Invalid", dropped_receipts=(bad, bad)),
            receipts,
        )


def test_all_ten_revised_requests_have_complete_demo_transport() -> None:
    env = c.context().policy_env()
    for cfg in c.configs():
        q = pydantic_load(WriteRocqReceiptAdvice, cfg.instantiate(None).args)
        chat = create_prompt(
            q, tuple(draft_examples()(env, q)), {}, None, env.templates
        )
        wire, _ = translate_chat_for_responses(
            LLMRequest(chat=chat, options={}), None, True
        )
        calls = [
            i.get("call_id") for i in wire if i.get("type") == "function_call"
        ]
        outputs = [
            i.get("call_id")
            for i in wire
            if i.get("type") == "function_call_output"
        ]
        assert calls == outputs
        assert "Required draft decisions" in q.disposition_catalog


def test_repair_feedback_lists_missing_draft_ids_and_known_receipts() -> None:
    queries: list[WriteRocqReceiptAdvice] = []

    def oracle(query: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(query, WriteRocqReceiptAdvice)
        queries.append(query)
        if len(queries) == 1:
            yield answer(DraftAdvice("Missing decisions"))
        else:
            assert any(
                "square" in str(m) and "Executable IDs" in str(m)
                for m in query.prefix
            )
            yield answer(
                DraftAdvice(
                    "Redundant",
                    decisions=(
                        DraftDecision(
                            "square",
                            "drop",
                            "Already covered in the supplied book",
                        ),
                    ),
                )
            )

    vals, _ = (
        write_rocq_receipts("reducer", "", "", (study.source(),), (draft(),))
        .run_toplevel(
            c.context().policy_env(), grounded_search() & fixed_oracle(oracle)
        )
        .collect()
    )
    assert len(vals) == 1 and len(queries) == 2
