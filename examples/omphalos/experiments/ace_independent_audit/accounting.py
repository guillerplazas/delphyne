"""Explicit tariff reconstruction; cache reads/writes are disjoint.

Official model and prompt-cache documentation checked 2026-09-19.
Historical missing cache-write or service-tier data is reported, not guessed.
"""

from datetime import date
from typing import Any, cast

from runtime.model_registry import pricing_for

MODELS = ("gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol", "gpt-6-astra")
TIERS = {
    "default": 1.0,
    "fast": 2.0,
    "priority": 2.0,
    "flex": 0.5,
    "batch": 0.5,
}
SOURCES = [
    f"https://developers.openai.com/api/docs/models/{m}" for m in MODELS
]
SOURCES.extend(
    [
        "https://developers.openai.com/api/docs/guides/prompt-caching",
        "https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics",
    ]
)


def price(
    usage: dict[str, Any],
    model: str,
    *,
    on: date,
    tier: str = "default",
    regional: bool = False,
) -> dict[str, Any]:
    p = pricing_for(model, on)
    details = usage.get("input_tokens_details", {})
    values = [
        usage.get("input_tokens"),
        details.get("cached_tokens"),
        details.get("cache_write_tokens"),
        usage.get("output_tokens"),
    ]
    if any(type(v) is not int or v < 0 for v in values):
        raise ValueError("Missing or invalid token usage")
    inp, cached, written, output = cast(
        tuple[int, int, int, int], tuple(values)
    )
    if cached + written > inp:
        raise ValueError("Cache categories exceed input")
    ordinary = inp - cached - written
    long_input = 2 if inp > 272000 else 1
    long_output = 1.5 if inp > 272000 else 1
    factor = TIERS[tier] * (1.1 if regional else 1)
    input_cost = (
        (
            ordinary * p.dollars_per_input_token
            + cached * p.dollars_per_cached_input_token
            + written * 1.25 * p.dollars_per_input_token
        )
        * long_input
        * factor
    )
    output_cost = output * p.dollars_per_output_token * long_output * factor
    return dict(
        input=inp,
        cached=cached,
        written=written,
        output=output,
        ordinary=ordinary,
        price=input_cost + output_cost,
        input_cost=input_cost,
        output_cost=output_cost,
        write_premium=written
        * 0.25
        * p.dollars_per_input_token
        * long_input
        * factor,
        no_cache=(
            inp * p.dollars_per_input_token * long_input
            + output * p.dollars_per_output_token * long_output
        )
        * factor,
    )


def reserve(model: str, inp: int, out: int, on: date) -> float:
    p = pricing_for(model, on)
    return 2.2 * (
        inp * p.dollars_per_input_token * 1.25 * (2 if inp > 272000 else 1)
        + out * p.dollars_per_output_token * (1.5 if inp > 272000 else 1)
    )
