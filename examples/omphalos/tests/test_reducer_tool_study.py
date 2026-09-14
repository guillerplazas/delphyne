"""Free reducer execution and complete demonstration transport regression."""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from dataclasses import replace
import json
from typing import Any

from delphyne.scripts.demonstrations import check_demo_file
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.queries import create_prompt

from tools.reports import reducer_tool_study as study
from prove_snippets import snippet_examples


def test_reducer_checks_and_repairs_before_retaining() -> None:
    outcome = study.exercise("check_repair")
    product = outcome["product"]
    assert product is not None and product.role == "reducer"
    assert [r.status for r in product.receipts] == [
        "rejected",
        "executed_open",
    ]
    assert outcome["tool_calls"] == 2 and len(outcome["queries"]) == 3
    assert outcome["rocq_seconds"] > 0
    content = product.delta.operations[0].content
    assert study.GOOD in content and study.BAD not in content
    assert "Source-local" in content


def test_reducer_abstention_preservation_and_forgery() -> None:
    abstain = study.exercise("abstain")
    assert abstain["product"] is not None
    assert not abstain["product"].delta.operations
    assert abstain["tool_calls"] == 0
    preserved = study.exercise("retain_checked")
    assert preserved["tool_calls"] == 0 and preserved["rocq_seconds"] == 0
    assert study.GOOD in preserved["product"].delta.operations[0].content
    forged = study.exercise("forge")
    assert forged["product"] is None and len(forged["queries"]) == 4
    assert not forged["queries"][-1].allow_tools


def test_reducer_study_demo_has_complete_tool_transport() -> None:
    path = study.c.ROOT / "demos/reducer_snippets.study.demo.yaml"
    ctx = study.c.context()
    feedback = check_demo_file(path, ctx, study.c.ROOT)
    assert not feedback.errors, feedback.errors
    env = replace(ctx, demo_files=(*ctx.demo_files, path)).policy_env()
    examples = env.examples.examples_for("WriteCheckedRocqAdvice")
    assert len(examples) == 1
    example = examples[0]
    # The paid selector deliberately remains unchanged. This new study
    # demonstration needs a future opt-in reducer selector to reach a model.
    assert not snippet_examples()(env, example.query)
    chat = create_prompt(example.query, (example,), {}, None, env.templates)
    items, _ = translate_chat_for_responses(
        LLMRequest(chat=chat, options={}), None, True
    )
    wire: list[dict[str, Any]] = json.loads(json.dumps(items))
    calls = [i["call_id"] for i in wire if i.get("type") == "function_call"]
    outputs = [
        i["call_id"] for i in wire if i.get("type") == "function_call_output"
    ]
    assert calls == outputs
