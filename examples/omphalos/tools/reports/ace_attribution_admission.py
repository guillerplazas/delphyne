"""Offline lower-bound probe of the first unobserved model admission.

Both harnesses: python -m tools.reports.ace_attribution_admission [luna].
This is explanatory analysis after treatment registration, not a new arm.
Every observed response must replay. HTTP dispatch is unconditionally
disabled. We restore cumulative output-token allowance on cached responses;
opaque reasoning items are unavailable and omitted, making the next
serialized-input bound a lower bound on the original live reservation.
An excess over remaining money proves that request cannot be admitted.
Failure to prove an excess does not establish that it could be admitted.
"""

from experiments.ace import ace_attribution_experiment as c
from contextlib import redirect_stdout
from dataclasses import replace
import io
import os
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

from delphyne import Budget
from delphyne.stdlib.models import LLM, LLMRequest, LLMResponse, LLMCache
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from runtime.campaign_budget import CampaignResponsesModel
from tools.reports.ace_attribution_diagnosis import outcome_head


class ProbeComplete(Exception):
    """The next estimate is recorded; never try to answer its request."""


def probe(key: str, source: str) -> dict[str, Any]:
    stage, arm, theorem = key.split("/")
    cfg = c.proof(stage, arm, theorem)
    args = cfg.instantiate(None)
    directory = c.ROOT / source
    spent = outcome_head(directory)
    count = int(spent["num_completions"])
    args.cache_mode = "replay"
    args.cache_file = str(directory / "cache.yaml")
    args.export_raw_trace = False
    args.export_browsable_trace = False
    args.export_log = False
    context = replace(c.context(), cache_root=Path("/"))
    calls = 0
    candidate: dict[str, Any] = {}
    original_estimate = CampaignResponsesModel.estimate_budget

    def send(
        model: CampaignResponsesModel,
        request: LLMRequest,
        cache: LLMCache | None,
    ) -> LLMResponse:
        nonlocal calls
        assert calls < count, "Unobserved answer is forbidden"
        response = LLM.send_request(model, request, cache)
        assert response.budget is not None
        model.reasoning_allowance += int(response.budget["output_tokens"])
        calls += 1
        return response

    def estimate(model: CampaignResponsesModel, request: LLMRequest) -> Budget:
        if calls < count:
            # These admissions are known to have happened. Their exact
            # historical opaque-reference bytes cannot be reconstructed.
            return LLM.estimate_budget(model, request)
        assert model.reasoning_cache is not None
        lower = original_estimate(model, request)
        assert args.budget is not None
        candidate.update(
            next_reservation_lower_bound=lower["price"],
            remaining_money=args.budget["price"] - spent["price"],
            restored_output_allowance=model.reasoning_allowance,
        )
        candidate["proved_money_rejection"] = (
            candidate["next_reservation_lower_bound"]
            > candidate["remaining_money"] + 1e-12
        )
        raise ProbeComplete("Offline diagnostic reached next model request")

    diagnostics = ""
    with (
        patch.object(CampaignResponsesModel, "send_request", send),
        patch.object(CampaignResponsesModel, "estimate_budget", estimate),
        patch.object(
            CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("Offline diagnostic forbids HTTP"),
        ),
        redirect_stdout(io.StringIO()),
    ):
        try:
            outcome = run_command(
                run_strategy, args, ctx=context, add_header=False
            )
            diagnostics = str(outcome.diagnostics)
        except ProbeComplete:
            diagnostics = "Stopped at the first unobserved model estimate"
    return dict(
        source=source,
        observed_requests=count,
        replayed_requests=calls,
        all_observed_requests_replayed=calls == count,
        next_request=candidate or None,
        replay_diagnostics=diagnostics,
        interpretation="A lower-bound rejection is sufficient monetary evidence, not an unrestricted model-capability diagnosis.",
    )


def main(phase: str = "complete") -> None:
    c.verify()
    c.activate("luna")
    os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)
    diags = cast(dict[str, Any], c.read(f"{phase}_diagnostics.json"))
    results: dict[str, Any] = {}
    for key, d in diags.items():
        if "source" not in d or d["observation"]["solved"]:
            continue
        results[key] = probe(key, d["source"])
        print(key, results[key]["next_request"], flush=True)
    c.save(f"{phase}_admission_probe.json", results)


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "complete")
