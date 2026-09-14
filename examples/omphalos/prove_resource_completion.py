"""Isolated resource/continuation policies for both agent harnesses.

Proof logic stays in prove_theorem_grounded. This policy changes either
the enforced response allowance or the existing continuation interface.
Recording preserves the parser, opaque reasoning state and parent budget.
"""

from dataclasses import dataclass, fields
from typing import Any

import delphyne as dp
from delphyne.stdlib.models import (
    LLMOutput,
    LLMRequest,
    LLMResponseLogItem,
)
from openai.types.responses import Response
from pydantic import TypeAdapter

from prove_continuation import examples as continuation_examples
from prove_grounded import grounded_examples, grounded_search
from runtime.admission_events import record
from runtime.continuation_output import ContinuationResponsesModel
from runtime.campaign_budget import CampaignResponsesModel
from runtime.model_registry import make_model
from runtime.replay_admission import (
    admission_observer,
    fingerprint,
    recorded_prompt,
    transport_state,
)


@dataclass(kw_only=True)
class CompletionResponsesModel(ContinuationResponsesModel):
    """Recording is orthogonal to final-message selection and dispatch."""

    continuation: bool = False
    halt_on_billing_issue: bool = True

    def estimate_budget(self, req: LLMRequest) -> dp.Budget:
        estimate = super().estimate_budget(req)
        full = self.add_model_defaults(req)
        assert self.pricing is not None
        inp = self._input_bound(full)
        record(
            "estimate_v2",
            "estimated",
            request=fingerprint(
                TypeAdapter(LLMRequest).dump_python(full, mode="json")
            ),
            estimate=dict(estimate.values),
            input_bound=inp,
            output_limit=full.options.get(
                "max_completion_tokens", self.output_limit
            ),
            reasoning_allowance=self.reasoning_allowance,
            transport_state=fingerprint(transport_state(self)),
            shadow_price_32768=(
                inp * self.pricing.dollars_per_input_token
                + 32768 * self.pricing.dollars_per_output_token
            ),
            structured=full.structured_output is not None,
        )
        return estimate

    def _parse_response(
        self, response: Response, req: LLMRequest
    ) -> tuple[LLMOutput | None, list[LLMResponseLogItem]]:
        output, log = (
            super()._parse_response(response, req)
            if self.continuation
            else CampaignResponsesModel._parse_response(self, response, req)
        )
        record(
            "completion_response",
            "delivered" if output is not None else "no_output",
            response_id=response.id,
            structured=req.structured_output is not None,
            corrected_final_message=any(
                item.message == "continuation_final_message_v2" for item in log
            ),
        )
        return output, log


def completion_policy(
    arm: str,
    snapshot_directory: str,
    model_name: str = "gpt-5.6-luna",
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    if arm not in ("A", "B", "reference") or model_name != "gpt-5.6-luna":
        raise ValueError("Unregistered completion policy")
    original = make_model(
        model_name,
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Completion experiments require campaign accounting")
    values: dict[str, Any] = {
        f.name: getattr(original, f.name) for f in fields(original) if f.init
    }
    values["output_limit"] = 4096 if arm == "A" else 32768
    values["halt_on_billing_issue"] = True
    model = CompletionResponsesModel(**values, continuation=arm == "B")
    normal = dp.few_shot(
        model,
        max_requests=1,
        select_examples=(
            continuation_examples() if arm == "B" else grounded_examples()
        ),
        tag_user_feedback_messages=True,
    )
    return admission_observer(
        dict(price=0.10, num_requests=64, rocq_seconds=300)
    ) @ (
        grounded_search() & recorded_prompt(normal, model, snapshot_directory)
    )
