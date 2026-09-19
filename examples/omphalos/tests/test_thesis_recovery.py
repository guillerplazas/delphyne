"""The operational amendment cannot retry the rejected request."""

import pytest
from typing import Any

from tools.maintenance.ace_thesis_recovery import ResumeJob
from experiments.ace_thesis import campaign as c


def test_only_registered_collateral_pauses_can_resume(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = ResumeJob(
        "round1",
        "examples",
        "proof",
        "imo_1977_p6",
        "inputs/x.json",
        "hash",
        1,
    )
    ident = c.name(job, None)

    def incident(_: str) -> dict[str, Any]:
        return dict(interrupted=[], rejected=ident)

    monkeypatch.setattr(c, "read", incident)
    with pytest.raises(ValueError, match="collateral"):
        job.instantiate(None)
