"""The stage adapter preserves real money/stages and excludes rejections."""

from pathlib import Path
from typing import Any

import pytest

from experiments.ace_thesis import campaign as c
from tools.maintenance import ace_thesis_validation_recovery as recovery


def test_stage_view_counts_only_validation_and_exports_real_stages(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    account: dict[str, Any] = dict(
        total=4.0,
        ledger=dict(
            groups=[
                dict(stage="round1", dollars=1.0),
                dict(stage="validation", dollars=3.0),
            ]
        ),
    )
    monkeypatch.setattr(c, "accounting", lambda: account)
    monkeypatch.setattr(c, "CAMPAIGN", tmp_path)
    view = recovery.CampaignView()
    scoped = view.accounting()
    assert (
        sum(
            g["dollars"]
            for g in scoped["ledger"]["groups"]
            if g["stage"] == "round1"
        )
        == 3.0
    )
    view.save("operations/round1_example.json", dict(accounting=scoped))
    assert (
        c.read("operations/validation_example.json")["accounting"] == account
    )
    assert account["ledger"]["groups"][0]["stage"] == "round1"
    assert view.ALLOCATIONS["round1"] == 32.0


def test_archive_mapping_is_limited_to_the_three_protocol_paths() -> None:
    assert (
        recovery.ScopedPath() / "resume_round1"
        == c.OUTPUT / "resume_validation"
    )
    with pytest.raises(ValueError, match="Unexpected"):
        _ = recovery.ScopedPath() / "unregistered"


def test_rejected_validation_cell_never_reaches_instantiation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = recovery.ValidationResumeJob(
        "validation",
        "nonace_ordinary",
        "proof",
        "amc12a_2020_p21",
        "inputs/fixture.json",
        "hash",
        1,
    )
    ident = c.name(job, None)

    def incident(path: str) -> dict[str, Any]:
        assert path == "operations/validation_incident.json"
        return dict(interrupted=[], rejected=ident)

    monkeypatch.setattr(c, "read", incident)
    # Keep the already-sealed helper's globals isolated from other tests.
    monkeypatch.setattr(recovery.protocol, "c", recovery.protocol.c)
    monkeypatch.setattr(
        recovery.protocol, "INCIDENT", recovery.protocol.INCIDENT
    )
    monkeypatch.setattr(
        recovery.protocol, "ResumeJob", recovery.protocol.ResumeJob
    )
    with pytest.raises(ValueError, match="collateral"):
        job.instantiate(None)
