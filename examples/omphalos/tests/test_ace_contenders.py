"""Protect the user's 160-cell scope and archived-control attribution."""

from dataclasses import asdict, replace
from unittest.mock import patch

import pytest

from experiments.ace import ace_contender_benchmark as b
from experiments.ace.ace_bounded_experiment import BoundedConfig


def test_exactly_two_contenders_one_seed_both_partitions() -> None:
    cs = b.proposed_configs()
    assert len(cs) == len({b.name(c, None) for c in cs}) == 160
    assert {c.seed for c in cs} == {0}
    for phase in ("training", "validation"):
        for arm in b.ARMS[1:]:
            arm_cs = [c for c in cs if c.phase == phase and c.arm_label == arm]
            assert len({c.bench_name for c in arm_cs}) == 40
            assert all(c.reasoning_effort == "xhigh" for c in arm_cs)
    assert not any(c.arm_label == "reference" for c in cs)


def test_frozen_manifest_and_unchanged_proof_arguments() -> None:
    c = b.proposed_configs()[0]
    with patch.object(b, "read", return_value=[asdict(c)]):
        assert c.instantiate(None) == BoundedConfig.instantiate(c, None)
        with pytest.raises(ValueError, match="outside"):
            replace(c, seed=1).instantiate(None)
        with pytest.raises(ValueError, match="outside"):
            replace(c, max_dollar_budget=0.2).instantiate(None)


def test_multiple_comparisons_and_no_artificial_minimum_gain() -> None:
    assert b.holm([0.04, 0.06]) == [0.08, 0.08]
    assert b.holm([1.0, 0.02]) == [1.0, 0.04]
    reference = dict(cells=40, solves=27, cost=0.70)
    candidate = dict(cells=40, solves=28, cost=0.65)
    assert b.old.eligible(candidate, reference, gain=1)
