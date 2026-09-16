"""Matched proof arguments and the joint $50 reservation; no paid calls."""

from pathlib import Path
from typing import Any

import pytest

from experiments import ace_economy_experiment as base
from experiments import ace_economy_budget_experiment as follow
from experiments import ace_economy_validation as scoped
from runtime.campaign_budget import Ledger


def test_larger_budget_non_ace_changes_only_book_and_output_location() -> None:
    theorem = next(iter(base.partition("validation")))
    old = base.Config("validation", "budget", theorem, 0).instantiate(None)
    new = follow.Config("validation", "agentic", theorem, 0).instantiate(None)
    assert old.strategy == new.strategy
    assert old.policy == new.policy
    assert old.budget == new.budget
    assert {**old.args, "playbook": ""} == new.args
    assert old.args["playbook"]
    for key in ("dollar_cap", "split_session"):
        assert old.policy_args[key] == new.policy_args[key]


def test_followup_cannot_repay_ace_validation() -> None:
    theorem = next(iter(base.partition("validation")))
    with pytest.raises(ValueError, match="Reuse"):
        follow.Config("validation", "ace", theorem, 0).instantiate(None)


def test_joint_reservation_rejects_main_overspend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(follow, "CAMPAIGN", tmp_path)
    monkeypatch.setattr(scoped, "verify", lambda: None)
    main: dict[str, Any] = dict(
        total=3,
        costs={"validation__reference": 3},
        unresolved=[],
        billing_issues=[],
    )
    monkeypatch.setattr(base, "accounting", lambda: main)
    follow.save("seal.json", {})
    follow.save("protocol.json", dict(main_development_spend=3))
    ledger = Ledger(tmp_path / "ledger.sqlite3")
    ledger.create(47, {"experiments": 47})
    ledger.reserve("experiments", "gpt-5.6-luna", 47)
    # $3 settled main + $47 hypothetical follow-up liability = $50.
    follow.verify()
    main.update(total=3.01, costs={"validation__reference": 3.01})
    with pytest.raises(ValueError, match="development"):
        follow.verify()


def test_followup_rejects_closed_partition_before_any_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*args: object) -> None:
        raise AssertionError("Must reject the stage before file access")

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    for action in (
        follow.configs,
        follow.launch,
        follow.run_batch,
        follow.panel,
    ):
        with pytest.raises(ValueError, match="Only validationX"):
            action("test")
    with pytest.raises(ValueError, match="Only validationX"):
        follow.Config("test", "agentic", "any", 0)
