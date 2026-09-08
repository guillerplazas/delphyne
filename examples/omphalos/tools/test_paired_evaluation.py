"""Tests for incomplete panels, family dependence, and charged cutoffs."""

# pyright: strict

from paired_evaluation import Observation as O, compare, exact_cluster_p


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
    assert same["effect_upper95_conservative"] > 0.05
    b[keys[0]] = O(True, 0.100001)
    b[keys[1]] = O(True, 0.01, failed=True)
    result = compare(a, b, keys)
    assert result["solved_b"] == 4
    assert result["cap_crossings_b"] == 1
    assert result["failed_b"] == 1
    assert result["cost_b"] > 0.1
    families = {f"p{i}": "one" for i in range(3)}
    assert compare(a, b, keys, families=families)["p_two_sided"] == 1


if __name__ == "__main__":
    test_clustered()
    print("paired evaluation tests passed")
