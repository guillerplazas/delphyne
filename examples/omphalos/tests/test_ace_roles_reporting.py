"""Offline measurement tests, independent of paid campaign execution."""

# ruff: noqa: E402
from runtime.ace_roles_scope import install

install()

import gzip
import json
from pathlib import Path
from typing import Any

from pytest import MonkeyPatch

from experiments import ace_roles_experiment as c
from tools.reports.ace_roles_results import economics, exposure, paired


def config(arm: str, seed: int = 0) -> c.Config:
    return c.Config("validation", arm, "proof", "example", "", "", seed)


def panel(monkeypatch: MonkeyPatch) -> None:
    def partition(_: str) -> dict[str, str]:
        return {"example": "unused"}

    def result(_: c.Config) -> dict[str, bool]:
        return {"success": True}

    monkeypatch.setattr(c, "partition", partition)
    monkeypatch.setattr(c, "family_map", lambda: {"example": "family"})
    monkeypatch.setattr(c, "cell_result", result)


def test_missing_seed_prevents_verdict(monkeypatch: MonkeyPatch) -> None:
    panel(monkeypatch)
    configs = [config("control"), config("candidate")]
    result = paired("validation", configs, {"costs": {}})
    assert result["complete"] is False
    assert result["missing_a"] == [("example", "1")]
    assert result["missing_b"] == [("example", "1")]


def test_failures_and_crossings_stay_in_panel(
    monkeypatch: MonkeyPatch,
) -> None:
    panel(monkeypatch)
    configs = [
        config(arm, seed)
        for arm in ("control", "candidate")
        for seed in (0, 1)
    ]

    def outcome(cfg: c.Config) -> dict[str, Any] | None:
        return (
            None if cfg.arm == "candidate" and cfg.seed else {"success": True}
        )

    monkeypatch.setattr(c, "cell_result", outcome)
    costs = {c.name(cfg, None): 0.02 for cfg in configs}
    costs[c.name(config("candidate"), None)] = 0.10001
    result = paired("validation", configs, {"costs": costs})
    assert result["complete"] is True
    assert result["cells"] == 2
    assert result["families"] == 1
    assert result["solved_a"] == 2
    assert result["solved_b"] == 0
    assert result["failed_b"] == 1
    assert result["cap_crossings_b"] == 1
    assert abs(result["cost_b"] - 0.12001) < 1e-12


def test_exposure_uses_dispatched_request_only(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(c, "CAMPAIGN", tmp_path)
    cfg = config("candidate")
    directory = tmp_path / "transport" / c.name(cfg, None)
    directory.mkdir(parents=True)
    for i, raw in enumerate(
        [
            {"request": {"chat": [{"content": "rocq-new"}]}, "response": {}},
            {"request": {"chat": []}, "response": {"text": "rocq-new"}},
        ]
    ):
        (directory / f"{i}.json.gz").write_bytes(
            gzip.compress(json.dumps(raw).encode())
        )
    assert exposure(cfg, ["rocq-new"])["exposed_requests"] == 1


def test_preparation_needs_positive_inference_saving() -> None:
    base = dict(cells=80, cost_a=1.0, cost_b=0.8, solved_a=50, solved_b=50)
    result = economics(base, 0.5)
    assert result["candidate_all_in_cost"] == 1.3
    assert result["amortization_problems"] == 200
    assert (
        economics(dict(base, cost_b=1.0), 0.5)["amortization_problems"] is None
    )
    assert (
        economics(dict(base, solved_b=0), 0.5)[
            "candidate_all_in_cost_per_solve"
        ]
        is None
    )
