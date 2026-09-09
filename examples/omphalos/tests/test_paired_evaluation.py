"""Tests for incomplete panels, family dependence, and charged cutoffs."""

# pyright: strict

from tools.analysis.paired_evaluation import (
    Observation as O,
    compare,
    exact_cluster_p,
)


def test_clustered() -> None:
    assert exact_cluster_p([2, 2, 2]) == 0.25
    assert exact_cluster_p([1] * 6) == 0.03125
    keys = [(f"p{i}", str(seed)) for i in range(3) for seed in (0, 1)]
    a = dict.fromkeys(keys, O(False, 0.01))
    b = dict.fromkeys(keys, O(True, 0.02))
    result = compare(a, b, keys)
    assert result["p_two_sided"] == 0.25
    assert result["families"] == 3
    assert result["verdict"] == "inconclusive"
    assert not compare(a, {}, keys)["complete"]
    same = compare(a, a, keys)
    assert same["verdict"] == "inconclusive"
    assert same["effect_upper90_conservative"] > 0.05
    b[keys[0]] = O(True, 0.100001)
    b[keys[1]] = O(True, 0.01, failed=True)
    result = compare(a, b, keys)
    assert result["solved_b"] == 4
    assert result["cap_crossings_b"] == 1
    assert result["failed_b"] == 1
    assert result["cost_b"] > 0.1
    families = {f"p{i}": "one" for i in range(3)}
    assert compare(a, b, keys, families=families)["p_two_sided"] == 1


def test_exploratory_threshold_and_historical_override() -> None:
    from tools.analysis.decision_audit import MIN_DISCORDANT_FOR_SIG
    from ladon.verdict import SIGNIFICANCE as LADON_ALPHA

    assert MIN_DISCORDANT_FOR_SIG == 5
    assert LADON_ALPHA == 0.05
    keys = [(f"p{i}", "0") for i in range(5)]
    a = dict.fromkeys(keys, O(False, 0.01))
    b = dict.fromkeys(keys, O(True, 0.01))
    fresh = compare(a, b, keys)
    assert fresh["p_two_sided"] == 0.0625
    assert fresh["verdict"] == "improvement"
    assert "effect_ci90" in fresh
    old = compare(a, b, keys, alpha=0.05, confidence=0.95)
    assert old["verdict"] == "inconclusive" and "effect_ci95" in old
    assert compare(a, b, keys, alpha=0.0625)["verdict"] == "inconclusive"
    assert compare(a, b, keys[:4])["verdict"] == "inconclusive"
    # Replicating seeds must not manufacture independent evidence.
    repeated = [(f"p{i}", str(seed)) for i in range(4) for seed in (0, 1)]
    aa = dict.fromkeys(repeated, O(False, 0.01))
    bb = dict.fromkeys(repeated, O(True, 0.01))
    assert compare(aa, bb, repeated)["verdict"] == "inconclusive"


if __name__ == "__main__":
    test_clustered()
    test_exploratory_threshold_and_historical_override()
    print("paired evaluation tests passed")
