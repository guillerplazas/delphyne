"""Control-flow tests for verified repair, independent episodes and leakage."""

# pyright: strict

import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import ace_adaptation as ad  # noqa: E402
from ace_review_benchmark import assert_training_allowed, load  # noqa: E402
from prove_ace import Reflection  # noqa: E402


def test_repair_loop() -> None:
    v = replace(ad.VARIANTS["x3-offline"], repair_rounds=2)
    batch = ad.plan(v, 1, 3)[0]
    originals = [ROOT / f"original{i}" for i in range(3)]
    seen: list[ad.ACEAdaptStepConfig] = []
    refl = Reflection(
        "reason", "wrong name", "cause", "check the lemma", "insight", []
    )

    def directory(name: str) -> Path:
        return ROOT / name

    def run(configs: list[ad.ACEAdaptStepConfig], **_: Any) -> dict[str, str]:
        seen.extend(configs)
        return {ad._config_name(c, ad._NO_UID): "done" for c in configs}  # pyright: ignore[reportPrivateUsage]

    def solved(path: Path) -> tuple[bool, str]:
        # One original solve, one first-repair solve, one second-repair solve.
        yes = (
            path == originals[2]
            or "round2" in path.name
            or (batch[0].bench in path.name and "round1" in path.name)
        )
        return yes, "solved" if yes else "unsolved"

    roles: Any = SimpleNamespace(
        adapt=SimpleNamespace(run=run, config_dir=directory)
    )

    def outcome(path: Path) -> str:
        return solved(path)[1]

    def trajectory(path: Path, _: str) -> str:
        return "trajectory:" + path.name

    with (
        patch.object(ad, "read_result", side_effect=solved),
        patch.object(ad, "read_outcome", side_effect=outcome),
        patch.object(ad, "read_requests", return_value=16),
        patch.object(
            ad,
            "extract_trajectory",
            side_effect=trajectory,
        ),
        patch.object(ad, "load_reflection", return_value=refl),
    ):
        evidence = ad._repair_batch(  # pyright: ignore[reportPrivateUsage]
            v,
            batch,
            "sha",
            roles,
            originals,
            ["initial"] * 3,
            [refl] * 3,
            max_workers=4,
        )
    generators = [c for c in seen if c.role == "generator"]
    assert len(generators) == 3
    assert all(
        c.num_requests == 16 and c.max_dollar_budget == 0.05
        for c in generators
    )
    assert all("check the lemma" in c.episode_guidance for c in generators)
    assert len({ad._config_name(c, ad._NO_UID) for c in seen}) == len(seen)  # pyright: ignore[reportPrivateUsage]
    assert len(evidence[0].records) == 1 and len(evidence[1].records) == 2
    assert evidence[2].records == []
    assert "Original episode" in evidence[1].episodes
    assert "Repair episode 2" in evidence[1].episodes
    assert all(
        c.upstream_sha256 == ad._sha256(c.trajectory_override)  # pyright: ignore[reportPrivateUsage]
        for c in seen
        if c.role == "reflector"
    )  # pyright: ignore[reportPrivateUsage]
    assert not ad.VARIANTS["x3-offline"].repair_rounds


def test_protection() -> None:
    assert_training_allowed(list(ad.POOLS["trainX"]))
    manifest = load()
    problem = next(iter(cast(dict[str, Any], manifest["problems"])))
    try:
        assert_training_allowed([problem])
    except ValueError:
        pass
    else:
        raise AssertionError("holdout must be rejected by training")


if __name__ == "__main__":
    test_repair_loop()
    test_protection()
    print("ACE repair loop and holdout protection tests passed")
