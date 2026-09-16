"""Scope checks must reject forbidden work before reading any input."""

from pathlib import Path

import pytest

from experiments import ace_economy_validation as scoped


@pytest.mark.parametrize("stage", ["test", "testX", "train", "trainX"])
def test_scope_rejected_before_read(
    stage: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*args: object) -> None:
        raise AssertionError("Scope rejection must precede all file reads")

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError, match="Only validationX"):
        scoped.partition(stage)
    with pytest.raises(ValueError, match="Only validationX"):
        scoped.Config(stage, "ace", "any", 0)
    with pytest.raises(ValueError, match="Unregistered"):
        scoped.configs(stage)


def test_seal_rejects_unexpected_path_before_hash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def paths() -> list[Path]:
        return []

    def seal(_: str) -> dict[str, str]:
        return {"forbidden": "abc"}

    monkeypatch.setattr(scoped, "source_paths", paths)
    monkeypatch.setattr(scoped, "read", seal)

    def forbidden(*args: object) -> None:
        raise AssertionError("Must not open an unexpected seal entry")

    monkeypatch.setattr(scoped.original, "sha", forbidden)
    with pytest.raises(ValueError, match="unauthorized"):
        scoped.verify()
