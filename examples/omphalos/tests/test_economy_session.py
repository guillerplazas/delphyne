"""Verify treatment identity, dataset closure and the shared authorization."""

from pathlib import Path
from typing import Any

import pytest

from experiments import ace_economy_session_experiment as session
from experiments import ace_economy_validation as reference
from runtime.campaign_budget import Ledger


def test_non_ace_reset_changes_only_book_and_archive_paths() -> None:
    theorem = next(iter(reference.partition()))
    old = reference.Config("validation", "session", theorem, 0).instantiate(
        None
    )
    new = session.Config(
        "validation", "agentic_session", theorem, 0
    ).instantiate(None)
    assert old.args["playbook"]
    assert {**old.args, "playbook": ""} == new.args
    assert old.strategy == new.strategy and old.policy == new.policy
    assert old.budget == new.budget
    assert new.policy_args["split_session"] is True
    for key in old.policy_args:
        if key not in ("snapshot_directory", "pause_file"):
            assert old.policy_args[key] == new.policy_args[key]


def test_non_ace_control_changes_only_reset_and_archive_paths() -> None:
    theorem = next(iter(reference.partition()))
    old = reference.Config("validation", "agentic", theorem, 1).instantiate(
        None
    )
    new = session.Config(
        "validation", "agentic_session", theorem, 1
    ).instantiate(None)
    assert old.args == new.args
    assert old.policy == new.policy and old.budget == new.budget
    assert old.policy_args["split_session"] is False
    assert new.policy_args["split_session"] is True


@pytest.mark.parametrize("stage", ["test", "testX", "train", "../test"])
def test_forbidden_stage_rejected_before_any_read(
    stage: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_: object) -> None:
        raise AssertionError("Must reject the stage before file access")

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    for action in (session.configs, session.launch, session.run_batch):
        with pytest.raises(ValueError, match="Only validationX"):
            action(stage)
    with pytest.raises(ValueError, match="Only validationX"):
        session.Config(stage, "agentic_session", "any", 0)


def test_shared_authorization_refuses_prior_drift_and_excess_liability(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(session, "CAMPAIGN", tmp_path)
    monkeypatch.setattr(reference, "verify", lambda: None)
    monkeypatch.setattr(session.previous_budget, "verify", lambda: None)

    def no_sources() -> list[Path]:
        return []

    prior: dict[str, float] = {"main": 45}
    own: dict[str, Any] = dict(ledger=dict(liability=5))
    monkeypatch.setattr(session, "source_paths", no_sources)
    monkeypatch.setattr(session, "prior_costs", lambda: prior)
    monkeypatch.setattr(session, "accounting", lambda: own)
    session.save("seal.json", {})
    session.save("protocol.json", dict(prior_settled_costs=prior))
    session.verify()
    own["ledger"]["liability"] = 5.01
    with pytest.raises(ValueError, match="authorization"):
        session.verify()
    own["ledger"]["liability"] = 5
    prior["main"] = 45.01
    with pytest.raises(ValueError, match="spending changed"):
        session.verify()


def test_eight_dollar_ledger_cannot_reserve_more(
    tmp_path: Path,
) -> None:
    from runtime.campaign_budget import CampaignExhausted

    ledger = Ledger(tmp_path / "ledger.sqlite3")
    ledger.create(session.CEILING, {"experiments": session.CEILING})
    receipt = ledger.reserve("experiments", "gpt-5.6-luna", session.CEILING)
    # Pending reservations can free capacity; settled charges cannot.
    ledger.settle(receipt, session.CEILING, {})
    with pytest.raises(CampaignExhausted):
        ledger.reserve("experiments", "gpt-5.6-luna", 0.0001)
