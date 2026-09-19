"""Four disjoint token categories, separate from legacy controller prices.

Rates verified on 2026-09-18 against the official pricing, model and cache
documentation. Historical missing tier/endpoint metadata must be labelled
an assumption by the caller; this is tariff reconstruction, not an invoice.
Never silently interpret a missing cache-write field as zero.
"""

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, cast

from runtime.model_registry import pricing_for

SOURCES = [
    "https://developers.openai.com/api/docs/pricing",
    "https://developers.openai.com/api/docs/models/gpt-5.6-luna",
    "https://developers.openai.com/api/docs/guides/prompt-caching",
    "https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics",
    "https://developers.openai.com/api/docs/changelog",
]
LONG_CONTEXT = 272_000


def rates(model: str, on: date, tier: str) -> tuple[float, float, float]:
    if model != "gpt-5.6-luna" or on < date(2026, 7, 9):
        raise ValueError("No verified four-category tariff for model/date")
    multiplier = {
        "default": 1.0,
        "fast": 2.0,
        "priority": 2.0,
        "flex": 0.5,
        "batch": 0.5,
    }
    if tier not in multiplier:
        raise ValueError("Unresolved service tier: " + str(tier))
    p = pricing_for(model, on=on)
    return tuple(
        value * multiplier[tier]
        for value in (
            p.dollars_per_input_token,
            p.dollars_per_cached_input_token,
            p.dollars_per_output_token,
        )
    )  # pyright: ignore[reportReturnType]


@dataclass(frozen=True)
class Cost:
    input: int
    cached: int
    written: int
    output: int
    ordinary: int
    legacy: float
    corrected: float
    no_cache_fixed_trace: float
    write_premium: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def price(
    usage: dict[str, Any],
    *,
    on: date,
    model: str = "gpt-5.6-luna",
    tier: str,
    regional: bool,
) -> Cost:
    details = usage.get("input_tokens_details", {})
    values = (
        usage.get("input_tokens"),
        details.get("cached_tokens"),
        details.get("cache_write_tokens"),
        usage.get("output_tokens"),
    )
    if any(type(x) is not int or x < 0 for x in values):
        raise ValueError("Missing or invalid billing token category")
    inp, cached, written, output = cast(tuple[int, int, int, int], values)
    if cached + written > inp:
        raise ValueError("Cache categories exceed total input")
    ordinary = inp - cached - written
    base, read, out = rates(model, on, tier)
    input_factor = 2 if inp > LONG_CONTEXT else 1
    output_factor = 1.5 if inp > LONG_CONTEXT else 1
    region_factor = 1.1 if regional else 1
    corrected = (
        (ordinary * base + cached * read + written * base * 1.25)
        * input_factor
        + output * out * output_factor
    ) * region_factor
    old = pricing_for(model, on=on)
    legacy = (
        (inp - cached) * old.dollars_per_input_token
        + cached * old.dollars_per_cached_input_token
        + output * old.dollars_per_output_token
    )
    return Cost(
        inp,
        cached,
        written,
        output,
        ordinary,
        legacy,
        corrected,
        (inp * base * input_factor + output * out * output_factor)
        * region_factor,
        written * base * 0.25 * input_factor * region_factor,
    )


def reserve(input_bound: int, output_limit: int, on: date) -> float:
    """Bound all writes, long context, Fast tier and regional processing.

    The actual tier/endpoint is recorded at settlement. This conservative
    campaign reservation does not enter the legacy proof controller.
    """
    base, _, out = rates("gpt-5.6-luna", on, "fast")
    return 1.1 * (
        input_bound * base * 1.25 * (2 if input_bound > LONG_CONTEXT else 1)
        + output_limit * out * (1.5 if input_bound > LONG_CONTEXT else 1)
    )
