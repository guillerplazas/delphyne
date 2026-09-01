"""
Smoke-probe the Responses API before spending a sweep on it.

Three things about the Responses migration are assumptions until a real
request is sent, and each of them would silently ruin an experiment
rather than fail it:

1. **Which `reasoning_effort` values are legal.** `"none"` is accepted
   on Chat Completions (it is how the archived agentic runs got tools at
   all) but the Responses API may reject it. The `"none"` arm is meant
   to be the control that isolates the API switch from the reasoning
   change, so if it is illegal the control has to be redefined as
   "reasoning parameter omitted" -- and that is a fact to establish
   before the sweep, not after.
2. **Whether tools and reasoning actually coexist.** The entire reason
   for this migration. A request carrying both is sent here.
3. **Whether reasoning tokens are billed as claimed.** The probe prints
   the usage breakdown so the cost model can be checked against reality
   rather than against the docs.

Each probe is one short request on a throwaway prompt, so the whole
script costs well under a cent.

Usage:
    python tools/probe_responses_api.py
"""

# pyright: strict

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import delphyne as dp
from delphyne.stdlib.models import LLMRequest, Schema

from model_registry import OmphalosReasoningEffort, make_model

EFFORTS: tuple[OmphalosReasoningEffort | Literal["minimal"], ...] = (
    "none",
    "minimal",
    "low",
    "medium",
    "high",
    "xhigh",
    "max",
)
"""
Every level the provider might accept, including `"minimal"` — which is
in the *stdlib* literal but which gpt-5.6 rejects. Probing a value we
expect to fail is the point: the failure is the documentation.
"""

PROMPT = "Reply with the single word: ok"

TOOL = Schema(
    name="report_number",
    description="Report a single number back to the caller.",
    schema={
        "properties": {"value": {"title": "Value", "type": "integer"}},
        "required": ["value"],
        "title": "report_number",
        "type": "object",
    },
)


@dataclass
class ProbeResult:
    label: str
    ok: bool
    detail: str


def _usage(resp: Any) -> str:
    usage = cast(dict[str, Any] | None, resp.usage_info)
    budget = cast(dict[str, float], resp.budget.values)
    if usage is None:
        return "no usage reported"
    out_details = cast(
        dict[str, Any], usage.get("output_tokens_details") or {}
    )
    in_details = cast(dict[str, Any], usage.get("input_tokens_details") or {})
    return (
        f"in={usage.get('input_tokens')} "
        f"cached={in_details.get('cached_tokens')} "
        f"out={usage.get('output_tokens')} "
        f"reasoning={out_details.get('reasoning_tokens')} "
        f"price=${budget.get(dp.DOLLAR_PRICE, 0.0):.6f}"
    )


def probe(
    model_name: str,
    effort: OmphalosReasoningEffort | Literal["minimal"] | None,
    *,
    with_tools: bool,
) -> ProbeResult:
    label = (
        f"effort={effort or 'omitted':8} "
        f"tools={'yes' if with_tools else 'no ':3}"
    )
    try:
        model = make_model(
            model_name,
            api="responses",
            reasoning_effort=cast(OmphalosReasoningEffort, effort),
        )
        # `_send_final_request` reads its options off the request, not
        # off the model, so they are spelled out here rather than
        # reached for through the abstract `LLM` interface.
        options: dp.RequestOptions = {"model": model_name}
        if effort is not None:
            options["reasoning_effort"] = cast(dp.ReasoningEffort, effort)
        request = LLMRequest(
            chat=(dp.UserMessage(PROMPT),),
            options=options,
            num_completions=1,
            tools=(TOOL,) if with_tools else (),
        )
        resp = model.send_request(request, None)
    except Exception as e:  # noqa: BLE001 - the point is to see it
        return ProbeResult(label, False, f"{type(e).__name__}: {e}")
    return ProbeResult(label, True, _usage(resp))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Send one short Responses-API request per reasoning-effort "
            "level, with and without tools, and report what the "
            "provider accepts and how it bills it."
        )
    )
    parser.add_argument("--model", default="gpt-5.6-terra")
    args = parser.parse_args()
    model_name = str(args.model)

    print(f"Probing the Responses API with {model_name}\n")
    results: list[ProbeResult] = []
    for with_tools in (False, True):
        for effort in (*EFFORTS, None):
            res = probe(model_name, effort, with_tools=with_tools)
            results.append(res)
            mark = "ok  " if res.ok else "FAIL"
            print(f"  {mark} {res.label}  {res.detail}")

    legal = [r.label for r in results if r.ok]
    print(f"\n{len(legal)}/{len(results)} probes accepted.")
    tool_efforts = [
        r.label.split()[0].split("=")[1]
        for r in results
        if r.ok and "tools=yes" in r.label
    ]
    if tool_efforts:
        print(
            "Reasoning efforts accepted alongside function tools: "
            + ", ".join(tool_efforts)
        )
    else:
        print(
            "No reasoning effort was accepted with tools -- the "
            "premise of the Responses migration does not hold."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
