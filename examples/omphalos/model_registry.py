"""
Model resolution for the omphalos baselines.

The stdlib pricing table (`delphyne.stdlib.standard_models.PRICING`)
predates the gpt-5.6 family, and its prefix-matching fallback would
silently bill any `gpt-5.6-*` request at `gpt-5` rates — corrupting the
`price` budget metric that every cost figure in this project rests on.
This module is the single source of truth for gpt-5.6 pricing until the
stdlib table catches up, at which point `make_model` collapses back to
`dp.standard_model`.

Prices are the published API rates as of 2026-07 (dollars per million
input / cached-input / output tokens):

- gpt-5.6-sol:   5.00 / 0.50 / 30.00
- gpt-5.6-terra: 2.50 / 0.25 / 15.00
- gpt-5.6-luna:  1.00 / 0.10 /  6.00
"""

import delphyne as dp
from delphyne.stdlib.models import (
    PER_MILLION,
    LLM,
    ModelPricing,
    RequestOptions,
)

# fmt: off


def _per_million(inp: float, cached_inp: float, out: float) -> ModelPricing:
    return ModelPricing(
        dollars_per_input_token=inp * PER_MILLION,
        dollars_per_cached_input_token=cached_inp * PER_MILLION,
        dollars_per_output_token=out * PER_MILLION,
    )


GPT56_PRICING: dict[str, ModelPricing] = {
    "gpt-5.6-sol": _per_million(5.00, 0.50, 30.00),
    "gpt-5.6-terra": _per_million(2.50, 0.25, 15.00),
    "gpt-5.6-luna": _per_million(1.00, 0.10, 6.00),
}


def make_model(model_name: str, *, for_tool_calls: bool = False) -> LLM:
    """
    Resolve a model name to an LLM with *correct* pricing.

    gpt-5.6 names must match `GPT56_PRICING` exactly: an unknown
    variant raises instead of inheriting gpt-5 rates through the
    stdlib's prefix fallback. Every other name (e.g. the archived
    gpt-5.4 runs, for cache replays) keeps the stdlib behavior.

    `for_tool_calls` must be set when the model will receive function
    tools (the agentic baseline). The gpt-5.6 family rejects function
    tools on the Chat Completions API unless `reasoning_effort` is
    explicitly `"none"` (reasoning + tools moved to the Responses API,
    which Delphyne does not support yet), so tool-bearing gpt-5.6
    requests run without reasoning while plain requests keep the
    server-default effort. This asymmetry is a documented experimental
    condition of the gpt-5.6 runs, not a choice.
    """
    if model_name.startswith("gpt-5.6"):
        pricing = GPT56_PRICING.get(model_name)
        if pricing is None:
            known = ", ".join(sorted(GPT56_PRICING))
            raise ValueError(
                f"No pricing registered for {model_name!r}. Known "
                f"gpt-5.6 models: {known}. Add the published rate to "
                "GPT56_PRICING rather than letting the stdlib prefix "
                "fallback bill it at gpt-5 rates."
            )
        options: RequestOptions | None = None
        if for_tool_calls:
            options = {"reasoning_effort": "none"}
        return dp.openai_model(model_name, options, pricing=pricing)
    return dp.standard_model(model_name)
