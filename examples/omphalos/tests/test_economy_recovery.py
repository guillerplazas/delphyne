"""Administrative recovery cannot forgive money, alter prompts or retry refusal."""

import json
from pathlib import Path

import delphyne as dp
from delphyne.stdlib.models import CachedRequest, LLMRequest
from pydantic import TypeAdapter
import pytest

from experiments import ace_economy_refinement_experiment as c
from experiments.economy_refinement import recovery as r
from experiments.economy_refinement import state
from runtime.campaign_budget import Ledger
from runtime.replay_admission import fingerprint


def request(text: str) -> CachedRequest:
    return CachedRequest(
        LLMRequest(chat=(dp.SystemMessage(text),), options={}), 1
    )


def test_complete_prefix_and_exact_next_request_are_required() -> None:
    old, next_request, wrong = (
        request("old"),
        request("next"),
        request("wrong"),
    )
    key = fingerprint(
        TypeAdapter(LLMRequest).dump_python(next_request.request, mode="json")
    )
    guard = r.CheckpointGuard({old}, key)
    with pytest.raises(ValueError, match="diverged"):
        guard.consume(next_request)
    guard.consume(old)
    with pytest.raises(ValueError, match="next request changed"):
        guard.consume(wrong)
    guard.consume(next_request)
    assert guard.reached and not guard.remaining


def test_reconciliation_preserves_money_and_original_receipt(
    tmp_path: Path,
) -> None:
    ledger = Ledger(tmp_path / "ledger.sqlite3")
    ledger.create(20, {"benchmark": 20})
    ident = ledger.reserve("benchmark", "gpt-5.6-luna", 0.1, r.REJECTED)
    ledger.settle(ident, 0.0, {"exception": "BadRequestError"})
    original = r.receipt_record(ledger, ident)
    before = ledger.summary()
    r.reconcile_record(ledger, original, "incident.json")
    r.reconcile_record(ledger, original, "incident.json")
    after = r.receipt_record(ledger, ident)
    assert {k: v for k, v in after.items() if k != "usage"} == {
        k: v for k, v in original.items() if k != "usage"
    }
    assert ledger.summary() == before
    assert (
        json.loads(after["usage"])["reconciled_exception"] == "BadRequestError"
    )
    with ledger.connect() as db:
        saved = db.execute(
            "SELECT original FROM reconciliations WHERE receipt=?", (ident,)
        ).fetchone()[0]
    assert json.loads(saved) == original
    with ledger.connect() as db:
        db.execute("UPDATE receipts SET charged=0.01 WHERE id=?", (ident,))
    with pytest.raises(ValueError, match="audit conflict"):
        r.reconcile_record(ledger, original, "incident.json")


@pytest.mark.parametrize("cost", [None, 0.01])
def test_unknown_or_nonzero_charge_cannot_be_released(
    tmp_path: Path, cost: float | None
) -> None:
    ledger = Ledger(tmp_path / "ledger.sqlite3")
    ledger.create(20, {"benchmark": 20})
    ident = ledger.reserve("benchmark", "gpt-5.6-luna", 0.1)
    ledger.settle(ident, cost, {"exception": "BadRequestError"})
    original = r.receipt_record(ledger, ident)
    with pytest.raises(ValueError, match="zero-charge"):
        r.reconcile_record(ledger, original, "incident.json")
    assert r.receipt_record(ledger, ident) == original


def test_rejected_cell_is_not_eligible_for_resumption() -> None:
    config = r.ResumeConfig(
        "final00",
        "validation",
        True,
        True,
        False,
        "algebra_others_exirrpowirrrat",
        0,
    )
    with pytest.raises(ValueError, match="administrative"):
        config.instantiate(None)


def test_failed_cell_binds_exception_and_preserves_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def folder(_: c.Config) -> Path:
        return tmp_path

    monkeypatch.setattr(c, "directory", folder)
    monkeypatch.setattr(c, "CAMPAIGN", tmp_path)
    (tmp_path / "exception.txt").write_text(
        "BadRequestError: provider rejection"
    )
    (tmp_path / "cache.yaml").write_text("[]\n")
    job = c.Config("final00", "validation", True, True, False, "dummy", 0)
    assert state.cell_result(job) is None
    assert state.terminal_file(job).name == "exception.txt"
    assert {p.name for p in state.archive_files(job)} == {
        "cache.yaml",
        "exception.txt",
    }
