"""Historical proof control with corrected billing and cache diagnostics.

Only HTTP metadata and accounting differ from the sealed proof policy.
The returned Delphyne budget deliberately uses the legacy three-category
formula. Full provider responses are retained before response parsing.
"""

from dataclasses import dataclass, fields
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
from typing import Any, cast, override
from urllib.parse import urlparse

import delphyne as dp
from delphyne.stdlib import openai_api as oa
from delphyne.stdlib.models import LLMRequest, LLMResponse
import openai
from openai import omit
from openai.types.responses import Response
from pydantic import TypeAdapter

from prove_grounded import grounded_examples, grounded_search
from runtime.admission_events import record
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.campaign_pause import CampaignPaused, request_pause
from runtime.model_registry import make_model
from runtime.replay_admission import admission_observer, recorded_prompt
from prove_resource_completion import CompletionResponsesModel

from .accounting import price, reserve


@dataclass(kw_only=True)
class ReproductionModel(CompletionResponsesModel):
    evidence_directory: str
    pause_file: str

    def previous_response(self) -> str | None:
        # Derive diagnostic-only state from the paid prefix, so an exact
        # checkpoint continuation needs no extra hidden replay state.
        with Ledger(Path(self.ledger_file)).connect() as db:
            row = db.execute(
                "SELECT usage FROM receipts WHERE cell=? AND status='settled' "
                "ORDER BY created DESC,id DESC LIMIT 1",
                (self.cell,),
            ).fetchone()
        if row:
            usage = json.loads(row[0])
            if usage.get("status") == "completed":
                return usage.get("response_id")
        return None

    @override
    def _send_final_request(self, req: LLMRequest) -> LLMResponse:
        if Path(self.pause_file).exists():
            raise CampaignPaused("Campaign paused before dispatch")
        if req.num_completions != 1:
            raise ValueError("Expected one completion")
        assert self.pricing is not None
        options = req.options
        assert "model" in options and "max_completion_tokens" in options
        inp, log = oa.translate_chat_for_responses(
            req, self.reasoning_cache, self.convert_user_feedback_to_tool
        )
        payload: dict[str, Any] = dict(
            model=options["model"],
            input=inp,
            temperature=options.get("temperature", omit),
            reasoning={"effort": options["reasoning_effort"]}
            if "reasoning_effort" in options
            else omit,
            max_output_tokens=options["max_completion_tokens"],
            top_logprobs=options.get("top_logprobs", omit),
            tools=[oa._make_responses_tool(t) for t in req.tools] or omit,  # pyright: ignore[reportPrivateUsage]
            text=oa._responses_response_format(  # pyright: ignore[reportPrivateUsage]
                req.structured_output, self.no_json_schema
            ),
            tool_choice=options.get("tool_choice", omit),
            include=["message.output_text.logprobs"]
            if options.get("logprobs", False)
            else [],
            store=True,
        )
        previous = self.previous_response()
        if previous:
            payload["extra_body"] = {
                "prompt_cache_options": {"comparison_response_id": previous}
            }
        day = datetime.now(timezone.utc).date()
        bound_input = self._input_bound(req)
        bound = reserve(bound_input, options["max_completion_tokens"], day)
        ledger = Ledger(Path(self.ledger_file))
        key = ledger.reserve(
            self.stage,
            options["model"],
            bound,
            self.cell,
            halt_on_billing_issue=True,
        )
        evidence: dict[str, Any] = dict(
            receipt=key,
            cell=self.cell,
            request=TypeAdapter(LLMRequest).dump_python(req, mode="json"),
            payload={k: v for k, v in payload.items() if v is not omit},
            input_bound=bound_input,
            reserved=bound,
            started=datetime.now(timezone.utc).isoformat(),
        )
        destination = Path(self.evidence_directory) / (key + ".json.gz")
        destination.parent.mkdir(parents=True, exist_ok=True)

        def persist() -> None:
            with gzip.open(destination, "xt") as stream:
                json.dump(evidence, stream, sort_keys=True)

        try:
            with openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                max_retries=0,
                timeout=600,
            ) as client:
                host = urlparse(str(client.base_url)).hostname
                if host not in (
                    "api.openai.com",
                    "us.api.openai.com",
                    "eu.api.openai.com",
                ):
                    raise ValueError("Unregistered provider endpoint")
                evidence["endpoint"] = str(client.base_url)
                response = cast(Response, client.responses.create(**payload))
        except Exception as ex:
            rejected = isinstance(ex, openai.APIStatusError) and (
                ex.status_code in {400, 401, 403, 404, 422, 429}
            )
            evidence["exception"] = dict(
                type=type(ex).__name__,
                message=str(ex),
                rejected=rejected,
            )
            persist()
            ledger.settle(
                key, 0.0 if rejected else None, evidence["exception"]
            )
            if not rejected:
                request_pause(
                    Path(self.pause_file), "Unresolved request billing"
                )
            # No automatic replacement of a rejected/unfavourable attempt.
            raise
        evidence["response"] = response.to_dict()
        evidence["finished"] = datetime.now(timezone.utc).isoformat()
        persist()
        usage = response.usage
        try:
            if usage is None:
                raise ValueError("Missing usage")
            if usage.input_tokens > bound_input:
                raise ValueError("Input bound violated")
            cost = price(
                usage.to_dict(),
                on=day,
                model=response.model,
                tier=response.service_tier or "unresolved",
                regional=host != "api.openai.com",
            )
        except Exception:
            ledger.settle(key, None, {"response_id": response.id})
            request_pause(Path(self.pause_file), "Unresolved tariff or usage")
            raise
        assert usage is not None
        spent = oa._compute_spent_budget(  # pyright: ignore[reportPrivateUsage]
            1, self.model_class, self.pricing, usage
        )
        if abs(spent["price"] - cost.legacy) > 1e-9:
            ledger.settle(key, cost.corrected, usage.to_dict())
            request_pause(
                Path(self.pause_file), "Legacy controller price drift"
            )
            raise ValueError("Controller price mismatch")
        ledger.settle(
            key,
            cost.corrected,
            dict(
                **usage.to_dict(),
                response_id=response.id,
                model=response.model,
                status=response.status,
                service_tier=response.service_tier,
                endpoint=evidence["endpoint"],
                input_bound=bound_input,
                legacy_price=cost.legacy,
                prompt_cache_diagnostics=evidence["response"].get(
                    "prompt_cache_diagnostics"
                ),
            ),
        )
        self.reasoning_allowance += usage.output_tokens
        record(
            "model",
            "settled",
            receipt=key,
            dollars=cost.corrected,
            legacy_price=cost.legacy,
            status=response.status,
        )
        output, parsed_log = self._parse_response(response, req)
        return LLMResponse(
            [] if output is None else [output],
            dp.Budget(spent),
            [*log, *parsed_log],
            response.model,
            usage.to_dict(),
        )


def reproduction_policy(
    snapshot_directory: str,
    evidence_directory: str,
    pause_file: str,
    output_tokens: int,
) -> dp.Policy[dp.Branch | dp.Compute | dp.Fail, dp.PromptingPolicy]:
    if output_tokens not in (8192, 32768):
        raise ValueError("Unregistered output limit")
    original = make_model(
        "gpt-5.6-luna",
        for_tool_calls=True,
        api="responses",
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    if not isinstance(original, CampaignResponsesModel):
        raise ValueError("Campaign ledger required")
    values = {
        f.name: getattr(original, f.name) for f in fields(original) if f.init
    }
    values.update(output_limit=output_tokens, halt_on_billing_issue=True)
    model = ReproductionModel(
        **values,
        continuation=False,
        evidence_directory=evidence_directory,
        pause_file=pause_file,
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
