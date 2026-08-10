"""
Model resolution and pricing for the omphalos baselines.

Delphyne's `price` budget metric is the quantity every cost claim in
this project rests on, so it must never be an estimate. The stdlib
pricing table (`delphyne.stdlib.standard_models.PRICING`) resolves an
unknown model name through a *longest-prefix* fallback: any
`gpt-5.4-*` or `gpt-5.6-*` name matches the `gpt-5` entry and is
silently billed at 1.25 / 0.125 / 10.00 per M tokens. That is how the
archived gpt-5.4 sweeps under `experiments/previous/` came to be
under-billed by ~1.75x (see `tools/reprice.py`, which corrects them
offline, and the 2026-08-10 entry in `PROGRESS.md`).

This module is therefore the single source of truth for the pricing of
every model omphalos has ever run, and it *refuses* to guess: a name in
a guarded family (`_GUARDED_FAMILIES`) that has no exact entry raises
instead of falling through to the prefix match. Everything outside
those families keeps stdlib behavior unchanged.

Published API rates (dollars per million input / cached-input / output
tokens):

- gpt-5.6-sol:   5.00 / 0.50 / 30.00
- gpt-5.6-terra: 2.50 / 0.25 / 15.00
- gpt-5.6-luna:  1.00 / 0.10 /  6.00
- gpt-5.4:       2.50 / 0.25 / 15.00

The upstream fix (adding these entries to the stdlib table and dropping
the prefix inference) lives on the `fix/openai-pricing` branch. Even
once it lands, this module stays useful: it is what makes a *missing*
rate an error rather than a plausible-looking number.
"""

# pyright: strict

from collections.abc import Mapping

import delphyne as dp
from delphyne.stdlib.models import (
    PER_MILLION,
    LLM,
    ModelPricing,
    RequestOptions,
)
from delphyne.stdlib.standard_models import PRICING as STDLIB_PRICING

# fmt: off


def _per_million(inp: float, cached_inp: float, out: float) -> ModelPricing:
    return ModelPricing(
        dollars_per_input_token=inp * PER_MILLION,
        dollars_per_cached_input_token=cached_inp * PER_MILLION,
        dollars_per_output_token=out * PER_MILLION,
    )


OMPHALOS_PRICING: Mapping[str, ModelPricing] = {
    # gpt-5.6 family — canonical since the 2026-07-21 migration.
    "gpt-5.6-sol": _per_million(5.00, 0.50, 30.00),
    "gpt-5.6-terra": _per_million(2.50, 0.25, 15.00),
    "gpt-5.6-luna": _per_million(1.00, 0.10, 6.00),
    # gpt-5.4 family — the archived sweeps under `experiments/previous/`
    # all ran on the dated snapshot; the bare name is listed so the
    # family rate is documented in one place.
    "gpt-5.4": _per_million(2.50, 0.25, 15.00),
    "gpt-5.4-2026-03-05": _per_million(2.50, 0.25, 15.00),
}
"""
Exact per-model rates for every model omphalos has run. Adding a model
to a benchmark sweep means adding its published rate here first.
"""

# fmt: on


_GUARDED_FAMILIES = ("gpt-5.4", "gpt-5.5", "gpt-5.6")
"""
Name prefixes for which the stdlib's prefix fallback is *wrong* (they
all resolve to `gpt-5`, which is 2x cheaper). A name starting with one
of these must have an exact `OMPHALOS_PRICING` entry or we refuse to
price it at all.
"""


def _require_exact_pricing(model_name: str) -> ModelPricing:
    pricing = OMPHALOS_PRICING.get(model_name)
    if pricing is None:
        known = ", ".join(sorted(OMPHALOS_PRICING))
        raise ValueError(
            f"No pricing registered for {model_name!r}. Known models: "
            f"{known}. Add the published rate to OMPHALOS_PRICING rather "
            "than letting the stdlib prefix fallback bill it at gpt-5 "
            "rates."
        )
    return pricing


def pricing_for(model_name: str) -> ModelPricing:
    """
    Resolve a model name to its exact rate, or raise.

    Used by offline analysis (`tools/reprice.py`) to recompute the cost
    of an archived run from its recorded token counts. Unlike the
    stdlib resolver this never infers a rate from a name prefix: a
    guarded-family name must be in `OMPHALOS_PRICING`, any other name
    must be an *exact* key of the stdlib table, and anything else is an
    error.
    """
    if model_name in OMPHALOS_PRICING or model_name.startswith(
        _GUARDED_FAMILIES
    ):
        return _require_exact_pricing(model_name)
    entry = STDLIB_PRICING.get(model_name)
    if entry is None:
        raise ValueError(
            f"No exact pricing entry for {model_name!r} in either "
            "OMPHALOS_PRICING or the stdlib table. Refusing to infer a "
            "rate from a name prefix: add the published rate to "
            "OMPHALOS_PRICING."
        )
    inp, cached_inp, out = entry
    return _per_million(inp, cached_inp, out)


def make_model(model_name: str, *, for_tool_calls: bool = False) -> LLM:
    """
    Resolve a model name to an LLM with *correct* pricing.

    Guarded-family names (see `_GUARDED_FAMILIES`) must match
    `OMPHALOS_PRICING` exactly: an unknown variant raises instead of
    inheriting gpt-5 rates through the stdlib's prefix fallback. Every
    other name keeps the stdlib behavior, including non-OpenAI
    providers.

    `for_tool_calls` must be set when the model will receive function
    tools (the agentic baseline). The gpt-5.6 family rejects function
    tools on the Chat Completions API unless `reasoning_effort` is
    explicitly `"none"` (reasoning + tools moved to the Responses API),
    so tool-bearing gpt-5.6 requests run without reasoning while plain
    requests keep the server-default effort. This asymmetry is a
    documented experimental condition of the gpt-5.6 runs, not a
    choice. It is deliberately *not* applied to gpt-5.4, which accepts
    tools with reasoning: applying it there would change what a replay
    of an archived run does.
    """
    guarded = model_name in OMPHALOS_PRICING or model_name.startswith(
        _GUARDED_FAMILIES
    )
    if not guarded:
        return dp.standard_model(model_name)
    pricing = _require_exact_pricing(model_name)
    options: RequestOptions | None = None
    if for_tool_calls and model_name.startswith("gpt-5.6"):
        options = {"reasoning_effort": "none"}
    return dp.openai_model(model_name, options, pricing=pricing)
