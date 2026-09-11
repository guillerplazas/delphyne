"""Version-2 structured continuation transport, shared by both harnesses.

Application policy: the last final answer message supplies the proof edit,
just as the ordinary script parser uses the last code block. Do not join
separate assistant messages into one JSON document. Never choose an earlier
valid message after a malformed final answer, or suppress refusals/tools.
No dispatch, retries, pricing, request schemas or API budgets change here.
"""

from dataclasses import dataclass, fields
from typing import Any

from openai.types.responses import (
    Response,
    ResponseFunctionToolCall,
    ResponseOutputMessage,
    ResponseOutputRefusal,
)
from delphyne.stdlib.models import LLMOutput, LLMRequest, LLMResponseLogItem
from runtime.campaign_budget import CampaignResponsesModel


def final_message_response(
    response: Response, structured: bool
) -> tuple[Response, list[str]]:
    if not structured or response.status != "completed":
        return response, []
    if any(isinstance(i, ResponseFunctionToolCall) for i in response.output):
        return response, []
    messages = [
        i for i in response.output if isinstance(i, ResponseOutputMessage)
    ]
    if any(
        isinstance(p, ResponseOutputRefusal)
        for i in messages
        for p in i.content
    ):
        return response, []
    if len(messages) < 2:
        return response, []
    final = messages[-1]
    # An explicitly marked commentary message is not a final proof edit.
    # With unmarked legacy responses, list order is the local v2 contract.
    if final.phase not in (None, "final_answer"):
        return response, []
    discarded = [i.id for i in messages[:-1]]
    output = [
        i
        for i in response.output
        if not isinstance(i, ResponseOutputMessage) or i is final
    ]
    return response.model_copy(update={"output": output}), discarded


@dataclass(kw_only=True)
class ContinuationResponsesModel(CampaignResponsesModel):
    """Opt-in final-message selection; inherited dispatch settles once."""

    def _parse_response(
        self, response: Response, req: LLMRequest
    ) -> tuple[LLMOutput | None, list[LLMResponseLogItem]]:
        selected, discarded = final_message_response(
            response, req.structured_output is not None
        )
        result, log = super()._parse_response(selected, req)
        if discarded:
            log.insert(
                0,
                LLMResponseLogItem(
                    "info",
                    "continuation_final_message_v2",
                    metadata={
                        "discarded_message_ids": discarded,
                        "selected_message_id": next(
                            i.id
                            for i in reversed(selected.output)
                            if isinstance(i, ResponseOutputMessage)
                        ),
                        "response_id": response.id,
                    },
                ),
            )
        return result, log

    @staticmethod
    def from_model(
        model: CampaignResponsesModel,
    ) -> "ContinuationResponsesModel":
        values: dict[str, Any] = {
            f.name: getattr(model, f.name) for f in fields(model) if f.init
        }
        copied = ContinuationResponsesModel(**values)
        copied.reasoning_allowance = model.reasoning_allowance
        copied.reasoning_cache = model.reasoning_cache
        return copied
