"""Synthetic sign-flip checks with an enumerable null distribution."""

from typing import Any

import pytest

from .analysis import paired


def observations(prices: list[float]) -> list[dict[str, Any]]:
    return [
        dict(theorem=f"synthetic_{i}", seed=0, solved=True, costs={"price": p})
        for i, p in enumerate(prices)
    ]


@pytest.mark.parametrize("groups", [1, 2, 5, 6])
def test_sparse_one_direction_sign_flips_include_ties(groups: int) -> None:
    # With k nonzero same-direction cluster differences, exactly two of
    # 2**k sign assignments are as extreme as the observed assignment.
    base = [0.03127193 + i * 0.00110101 for i in range(18)]
    arm = [p - 0.00317391 if i < groups else p for i, p in enumerate(base)]
    result = paired(observations(base), observations(arm))
    assert abs(result["two_sided_sign_flip_p"] - 2 / 2**groups) < 0.005


def test_identical_panels_have_p_one() -> None:
    rows = observations([0.01, 0.12, 0.03210987])
    assert paired(rows, rows)["two_sided_sign_flip_p"] == 1.0


def test_genuinely_different_statistics_are_not_ties() -> None:
    # Four distinct effects, with the observed signed sum zero. Every
    # randomized statistic must be at least as extreme, including zero.
    base = observations([0.03] * 4)
    arm = observations([0.029, 0.028, 0.031, 0.032])
    assert paired(base, arm)["two_sided_sign_flip_p"] == 1.0
