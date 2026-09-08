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

**Rates are dated, because prices change under you.** On 2026-07-30
OpenAI cut gpt-5.6-luna by 80% and gpt-5.6-terra by 20% (sol unmoved),
which lands squarely in the middle of this project's run history: the
2026-07-21/22 sweeps were billed at the old rates and the 2026-08-12
Responses arms at the new ones. A single rate per model cannot describe
both, and using one silently overstated every August figure by 20%.

That is the same failure as the gpt-5.4 mispricing seen from the other
side. The exact-match guard catches an *unknown model name*; it cannot
catch a *stale rate for a name it knows*. Dating the entries is what
closes that gap, and it is why `pricing_for` takes an `on` date: a cost
is only meaningful relative to when it was incurred.

Published API rates (dollars per million input / cached-input / output
tokens), newest first per model:

- gpt-5.6-sol:   5.00 / 0.50 / 30.00   (unchanged since launch)
- gpt-5.6-terra: 2.00 / 0.20 / 12.00   from 2026-07-30
                 2.50 / 0.25 / 15.00   before that
- gpt-5.6-luna:  0.20 / 0.02 /  1.20   from 2026-07-30
                 1.00 / 0.10 /  6.00   before that
- gpt-5.4:       2.50 / 0.25 / 15.00

The upstream fix (adding these entries to the stdlib table and dropping
the prefix inference) lives on the `fix/openai-pricing` branch. Even
once it lands, this module stays useful: it is what makes a *missing*
rate an error rather than a plausible-looking number, and the stdlib
table is undated.
"""

# pyright: strict

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Literal, cast

import delphyne as dp
from delphyne.stdlib.models import (
    PER_MILLION,
    LLM,
    ModelPricing,
    ReasoningEffort,
    RequestOptions,
)
from delphyne.stdlib.standard_models import PRICING as STDLIB_PRICING

type OmphalosReasoningEffort = Literal[
    "none", "low", "medium", "high", "xhigh", "max"
]
"""
The reasoning-effort ladder gpt-5.6 actually accepts, measured rather
than assumed (`tools/probe_responses_api.py`; the provider names all six
in its own rejection message).

It differs from the stdlib `ReasoningEffort` at both ends: the stdlib
offers `"minimal"`, which every gpt-5.6 variant *rejects*, and stops at
`"high"`, leaving `"xhigh"` and `"max"` unreachable. Values are `cast`
to the stdlib type where they enter `RequestOptions` — the same pattern
this project used for `"none"` before the stdlib literal was widened.
Widening it again upstream is HINTS #3; nothing here is blocked on that.
"""

type ApiType = Literal["chat_completions", "responses"]
"""
Which OpenAI API a model is reached through.

`"chat_completions"` is what every archived omphalos run used and stays
the default, so those runs keep replaying byte-identically.
`"responses"` unlocks the Responses API, and with it the only way to
give a gpt-5.6 model tools *and* reasoning at the same time.
"""

# fmt: off


_LAUNCH = date(2000, 1, 1)
"""
Stand-in "since forever" date for a rate with no known predecessor. Any
real run postdates it, so it is the terminal entry of every history and
guarantees `pricing_for` always resolves.
"""


def _per_million(inp: float, cached_inp: float, out: float) -> ModelPricing:
    return ModelPricing(
        dollars_per_input_token=inp * PER_MILLION,
        dollars_per_cached_input_token=cached_inp * PER_MILLION,
        dollars_per_output_token=out * PER_MILLION,
    )


PRICE_CUT_2026_07_30 = date(2026, 7, 30)
"""
The day OpenAI cut gpt-5.6 prices (luna -80%, terra -20%, sol unmoved).
Named because several entries below and one guard in `tools/reprice.py`
refer to the same boundary.
"""

OMPHALOS_PRICING: Mapping[str, Sequence[tuple[date, ModelPricing]]] = {
    # gpt-5.6 family — canonical since the 2026-07-21 migration.
    # Each list is ordered newest-first; `pricing_for` picks the first
    # entry whose date is not in the future relative to the query.
    "gpt-5.6-sol": [
        (_LAUNCH, _per_million(5.00, 0.50, 30.00)),
    ],
    "gpt-5.6-terra": [
        (PRICE_CUT_2026_07_30, _per_million(2.00, 0.20, 12.00)),
        (_LAUNCH, _per_million(2.50, 0.25, 15.00)),
    ],
    "gpt-5.6-luna": [
        (PRICE_CUT_2026_07_30, _per_million(0.20, 0.02, 1.20)),
        (_LAUNCH, _per_million(1.00, 0.10, 6.00)),
    ],
    # gpt-5.4 family — the archived sweeps under `experiments/previous/`
    # all ran on the dated snapshot; the bare name is listed so the
    # family rate is documented in one place.
    "gpt-5.4": [(_LAUNCH, _per_million(2.50, 0.25, 15.00))],
    "gpt-5.4-2026-03-05": [(_LAUNCH, _per_million(2.50, 0.25, 15.00))],
}
"""
Exact per-model rate *histories* for every model omphalos has run.

Adding a model to a benchmark sweep means adding its published rate
here first; changing a price means *prepending* a dated entry rather
than editing the old one, so archived runs keep reproducing at the rate
they were actually billed at.
"""

# fmt: on


_GUARDED_FAMILIES = ("gpt-5.4", "gpt-5.5", "gpt-5.6")
"""
Name prefixes for which the stdlib's prefix fallback is *wrong* (they
all resolve to `gpt-5`, which is 2x cheaper). A name starting with one
of these must have an exact `OMPHALOS_PRICING` entry or we refuse to
price it at all.
"""


def _require_exact_pricing(model_name: str, on: date) -> ModelPricing:
    history = OMPHALOS_PRICING.get(model_name)
    if history is None:
        known = ", ".join(sorted(OMPHALOS_PRICING))
        raise ValueError(
            f"No pricing registered for {model_name!r}. Known models: "
            f"{known}. Add the published rate to OMPHALOS_PRICING rather "
            "than letting the stdlib prefix fallback bill it at gpt-5 "
            "rates."
        )
    for effective_from, pricing in history:
        if effective_from <= on:
            return pricing
    earliest = min(d for d, _ in history)
    raise ValueError(
        f"No rate registered for {model_name!r} on {on.isoformat()}: the "
        f"earliest known entry starts {earliest.isoformat()}. A run "
        "cannot predate every rate we know about — check the date, or "
        "add the older published rate."
    )


def current_pricing_date() -> date:
    """
    Today, as the default "as of" for pricing questions.

    Isolated in one function so that "what would this cost now" has a
    single definition, and so tests can point at it.
    """
    return date.today()


def pricing_for(model_name: str, on: date | None = None) -> ModelPricing:
    """
    Resolve a model name to the rate in force on a given date, or raise.

    Used by offline analysis (`tools/reprice.py`) to recompute the cost
    of an archived run from its recorded token counts. Unlike the
    stdlib resolver this never infers a rate from a name prefix: a
    guarded-family name must be in `OMPHALOS_PRICING`, any other name
    must be an *exact* key of the stdlib table, and anything else is an
    error.

    `on` defaults to today, which answers "what would this cost now".
    Pass a run's start date to answer "what did this actually cost" —
    the two diverge across the 2026-07-30 price cut, and conflating them
    is how the August figures came to be overstated by 20%.

    Note that the stdlib table is undated, so non-guarded models resolve
    to a single rate regardless of `on`. That is a known limitation
    rather than an assertion those prices never moved; guarded families
    are the ones this project makes cost claims about.
    """
    if model_name in OMPHALOS_PRICING or model_name.startswith(
        _GUARDED_FAMILIES
    ):
        return _require_exact_pricing(
            model_name, on if on is not None else current_pricing_date()
        )
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


def stdlib_fallback_pricing(model_name: str) -> ModelPricing | None:
    """
    The rate the *stdlib* would infer for this name, or `None`.

    Delphyne resolves an unknown model by longest matching prefix, so
    `gpt-5.4-2026-03-05` silently becomes `gpt-5`. This module exists to
    stop that happening, but the archived gpt-5.4 sweeps were billed
    that way, and reproducing it is what lets `tools/reprice.py` call
    those prices *explained* rather than mysterious.
    """
    candidates = [k for k in STDLIB_PRICING if model_name.startswith(k)]
    if not candidates:
        return None
    inp, cached_inp, out = STDLIB_PRICING[max(candidates, key=len)]
    return _per_million(inp, cached_inp, out)


def price_tokens(
    model_name: str,
    input_tokens: int,
    cached_input_tokens: int,
    output_tokens: int,
    on: date | None = None,
) -> float:
    """
    Cost of a token count at the rate in force on `on` (default today).

    The one place this arithmetic lives. Every analysis tool needs it —
    `reprice`, `budget_ablation`, `decision_audit`, `report_chart_data`
    — and each recomputing it invites exactly the drift this module
    exists to prevent. Mirrors `delphyne.stdlib.openai_api`'s own
    formula, which is what makes a recomputed price comparable with a
    recorded one.
    """
    non_cached = input_tokens - cached_input_tokens
    assert non_cached >= 0, (
        f"{model_name}: cached ({cached_input_tokens}) exceeds input "
        f"({input_tokens})"
    )
    rates = pricing_for(model_name, on=on)
    return (
        non_cached * rates.dollars_per_input_token
        + cached_input_tokens * rates.dollars_per_cached_input_token
        + output_tokens * rates.dollars_per_output_token
    )


def make_model(
    model_name: str,
    *,
    for_tool_calls: bool = False,
    api: ApiType = "chat_completions",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    use_reasoning_cache: bool = True,
    convert_user_feedback_to_tool: bool = True,
) -> LLM:
    """
    Resolve a model name to an LLM with *correct* pricing.

    Guarded-family names (see `_GUARDED_FAMILIES`) must match
    `OMPHALOS_PRICING` exactly: an unknown variant raises instead of
    inheriting gpt-5 rates through the stdlib's prefix fallback. Every
    other name keeps the stdlib behavior, including non-OpenAI
    providers.

    `for_tool_calls` must be set when the model will receive function
    tools (the agentic baseline). It only does anything on Chat
    Completions, where the gpt-5.6 family rejects function tools unless
    `reasoning_effort` is explicitly `"none"`, so tool-bearing gpt-5.6
    requests run *without reasoning* while plain requests keep the
    server default. Every archived agentic number was measured under
    that constraint (`reasoning_tokens: 0` in each cached response), so
    the agentic baseline has never been evaluated with reasoning on.
    The workaround is deliberately not applied to gpt-5.4, which accepts
    tools with reasoning: applying it there would change what a replay
    of an archived run does.

    `api="responses"` is what lifts the constraint. On the Responses API
    tools and reasoning coexist, so `for_tool_calls` stops forcing
    `"none"` and `reasoning_effort` is whatever the caller asks for. Two
    Responses-only features come along with it, both on by default
    because both are needed for the omphalos interact loop to benefit:

    - `use_reasoning_cache` resends the reasoning items the model
      produced on earlier turns instead of making it re-derive them,
      which saves output tokens and keeps the prompt prefix stable.
    - `convert_user_feedback_to_tool` presents verifier feedback as a
      tool result rather than a user message. OpenAI only persists the
      KV cache across tool calls following an assistant message, not
      across ordinary user turns -- and omphalos feedback arrives as a
      user message on every verification round, so without this the
      reasoning cache would be invalidated at each cycle. It requires
      `tag_user_feedback_messages=True` on the prompting policy, which
      is why the policies gate that flag on the API.

    Note that Chat Completions is *not* obviously the worse deal here.
    With reasoning off the prefix never changes, so the archived agentic
    runs already sit at an 85-91% prompt-cache hit rate; the Responses
    API is worth its complexity only if reasoning buys enough
    convergence to pay for the extra output tokens. That is an
    experiment, not an assumption -- see `experiments/responses_*`.
    """
    guarded = model_name in OMPHALOS_PRICING or model_name.startswith(
        _GUARDED_FAMILIES
    )
    options: RequestOptions | None = None
    effort = reasoning_effort
    if (
        effort is None
        and api == "chat_completions"
        and for_tool_calls
        and model_name.startswith("gpt-5.6")
    ):
        effort = "none"
    if effort is not None:
        # `OmphalosReasoningEffort` is wider than the stdlib literal at
        # both ends (see its docstring); the value is validated against
        # the provider, not the type.
        options = {"reasoning_effort": cast(ReasoningEffort, effort)}
    if not guarded:
        return dp.standard_model(
            model_name,
            options,
            api_type=api,
            use_reasoning_cache=(
                use_reasoning_cache if api == "responses" else None
            ),
            convert_user_feedback_to_tool=(
                convert_user_feedback_to_tool if api == "responses" else None
            ),
        )
    # A model built here is about to issue requests, so it is billed at
    # today's rate. Historical rates are for `pricing_for(..., on=...)`
    # and offline analysis of runs that already happened.
    pricing = _require_exact_pricing(model_name, current_pricing_date())
    from campaign_budget import for_campaign

    return for_campaign(
        dp.openai_model(
            model_name,
            options,
            pricing=pricing,
            api_type=api,
            use_reasoning_cache=(
                use_reasoning_cache if api == "responses" else None
            ),
            convert_user_feedback_to_tool=(
                convert_user_feedback_to_tool if api == "responses" else None
            ),
        )
    )
