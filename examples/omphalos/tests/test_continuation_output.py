"""Recorded multi-message regression and v2 refusal/budget boundaries."""

from dataclasses import fields
import json
from typing import Any

import delphyne as dp
from delphyne.stdlib.models import LLMRequest, Schema
from delphyne.stdlib.openai_api import OpenAIResponsesModel
from openai.types.responses import (
    Response,
    ResponseOutputMessage,
    ResponseFunctionToolCall,
)

from runtime.continuation_output import (
    ContinuationResponsesModel,
    final_message_response,
)
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import make_model
from runtime.paths import OMPHALOS_ROOT as ROOT


def model() -> ContinuationResponsesModel:
    base = make_model(
        "gpt-5.6-luna", api="responses", reasoning_effort="medium"
    )
    assert isinstance(base, OpenAIResponsesModel)
    args: dict[str, Any] = {
        f.name: getattr(base, f.name) for f in fields(base) if f.init
    }
    return ContinuationResponsesModel.from_model(
        CampaignResponsesModel(
            **args,
            ledger_file="unused",
            stage="offline",
            cell="offline",
            estimate_dollars=True,
        )
    )


def message(text: str, key: str) -> ResponseOutputMessage:
    return ResponseOutputMessage.model_validate(
        dict(
            id=key,
            type="message",
            role="assistant",
            status="completed",
            phase="final_answer",
            content=[
                dict(
                    type="output_text", text=text, annotations=[], logprobs=[]
                )
            ],
        )
    )


def response(*texts: str) -> Response:
    return Response.model_construct(
        id="offline",
        status="completed",
        output=[message(t, str(i)) for i, t in enumerate(texts)],
        usage=None,
    )


def test_last_message_not_concatenation() -> None:
    m = model()
    req = LLMRequest(
        chat=(), options={}, structured_output=Schema("proof_edit", None, {})
    )
    first = '{"mode":"suffix","script":"simpl in Heq."}'
    last = '{"mode":"replace","script":"intros.\\nlia."}'
    original = response(first, last)
    out, logs = m._parse_response(original, req)  # pyright: ignore[reportPrivateUsage]
    assert out and out.content == dp.Structured(json.loads(last))
    assert len(original.output) == 2  # input/provenance unchanged
    assert logs[0].message == "continuation_final_message_v2"
    selected, _ = final_message_response(original, True)
    assert selected.usage is original.usage and selected.id == original.id
    assert m.ledger_file == "unused" and m.cell == "offline"
    # Never fall back to an earlier answer after malformed final JSON.
    bad, _ = m._parse_response(response(first, "broken JSON"), req)  # pyright: ignore[reportPrivateUsage]
    assert bad is None


def test_refusal_tools_incomplete_and_unstructured_unchanged() -> None:
    original = response("{}", "{}")
    for structured, r in (
        (False, original),
        (True, original.model_copy(update={"status": "incomplete"})),
    ):
        same, removed = final_message_response(r, structured)
        assert same is r and not removed
    refusal = ResponseOutputMessage.model_validate(
        dict(
            id="refusal",
            type="message",
            role="assistant",
            status="completed",
            phase="final_answer",
            content=[dict(type="refusal", refusal="No answer")],
        )
    )
    r = original.model_copy(update={"output": [*original.output, refusal]})
    assert final_message_response(r, True)[0] is r
    tool = ResponseFunctionToolCall.model_validate(
        dict(
            id="tool",
            type="function_call",
            name="InspectProofState",
            call_id="call",
            arguments="{}",
            status="completed",
        )
    )
    r = original.model_copy(update={"output": [*original.output, tool]})
    assert final_message_response(r, True)[0] is r


def test_recorded_api_duplicate() -> None:
    fixture = (
        ROOT
        / "experiments/campaigns/ace_mechanisms_20260910/stored_response_audit.json"
    )
    original = Response.model_validate(json.loads(fixture.read_text()))
    req = LLMRequest(
        chat=(), options={}, structured_output=Schema("proof_edit", None, {})
    )
    m = model()
    # Reproduces the inherited parser's actual failure, without dispatch.
    old, _ = CampaignResponsesModel._parse_response(m, original, req)  # pyright: ignore[reportPrivateUsage]
    assert old is None
    result, logs = m._parse_response(original, req)  # pyright: ignore[reportPrivateUsage]
    assert result and result.content == dp.Structured(
        dict(mode="suffix", script="simpl in Heq.")
    )
    assert logs[0].message == "continuation_final_message_v2"


def test_reasoning_reservation_and_context_are_preserved() -> None:
    from dataclasses import replace
    from delphyne.stdlib.execution_contexts import load_execution_context
    from prove_continuation_v2 import continuation_policy_v2

    original = model()
    original.reasoning_allowance = 1234
    copied = ContinuationResponsesModel.from_model(original)
    assert copied.reasoning_allowance == 1234
    assert copied.reasoning_cache is original.reasoning_cache
    assert copied.output_limit == original.output_limit
    context = load_execution_context(ROOT)
    context = replace(
        context, modules=(*context.modules, "prove_continuation_v2")
    )
    assert (
        context.object_loader(extra_objects={}).find_object(
            "continuation_policy_v2"
        )
        is continuation_policy_v2
    )
