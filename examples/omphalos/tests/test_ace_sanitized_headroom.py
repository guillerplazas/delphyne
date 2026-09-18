"""Offline safety checks for the matched headroom comparison amendment."""

from dataclasses import asdict
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from experiments import ace_sanitized_headroom as h
from experiments.ace_sanitized.control import Controls


def test_registration_refuses_an_opened_validation_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(h.c, "OUTPUT", tmp_path)
    monkeypatch.setattr(h.c, "verify", lambda: None)
    read_selection = Mock(side_effect=AssertionError("Already too late"))
    monkeypatch.setattr(h, "verify_freeze", read_selection)
    (tmp_path / "validation").mkdir()
    with pytest.raises(ValueError, match="before opening"):
        h.register()
    read_selection.assert_not_called()


@pytest.mark.parametrize("coverage_funded", [False, True])
def test_unfunded_panel_never_becomes_a_partial_benchmark(
    coverage_funded: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    controls = asdict(Controls(output_tokens=8192))
    protocol = dict(
        source_sha256="sealed",
        freeze_sha256="sealed",
        arm="agentic_coverage",
        controls=controls,
    )
    records: dict[str, Any] = {
        "headroom_protocol.json": protocol,
        "benchmark_finished.json": {
            "panels": [("ace_coverage", {})] if coverage_funded else []
        },
    }

    def sealed(_: Path) -> str:
        return "sealed"

    monkeypatch.setattr(h.c, "verify", lambda: None)
    monkeypatch.setattr(h.c, "sha", sealed)
    monkeypatch.setattr(h.c, "read", records.__getitem__)
    monkeypatch.setattr(h.c, "save", records.__setitem__)
    monkeypatch.setattr(h.c, "accounting", lambda: {"total": 24})
    jobs = [object() for _ in range(80)]
    build_panel = Mock(return_value=jobs)
    launch = Mock(return_value=False)
    monkeypatch.setattr(h, "panel", build_panel)
    monkeypatch.setattr(h.c, "launch", launch)

    h.run()

    result = records["headroom_finished.json"]
    assert result["completed"] is False and not result.get("cells", 0)
    if coverage_funded:
        build_panel.assert_called_once_with(
            "agentic_coverage", dict(controls=controls, book="empty")
        )
        launch.assert_called_once_with("matched_headroom", jobs)
        assert len(jobs) == 80 and "$8" in result["reason"]
    else:
        build_panel.assert_not_called()
        launch.assert_not_called()
