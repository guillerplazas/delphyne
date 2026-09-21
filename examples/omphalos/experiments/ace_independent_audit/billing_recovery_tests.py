"""Offline tests of the prepared, opt-in timeout liability exception."""

from contextlib import ExitStack, redirect_stdout
import io
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from runtime.campaign_budget import CampaignExhausted, Ledger

from . import billing_recovery as recovery
from .common import CAMPAIGN, save


class RecoveryContract(unittest.TestCase):
    def exercise(self, *, approve: bool, extra_unknown: bool = False) -> None:
        with tempfile.TemporaryDirectory(
            dir=CAMPAIGN / "billing_recovery"
        ) as temp:
            root = Path(temp)
            folder = root / "billing_recovery"
            ledger = Ledger(root / "ledger.sqlite3")
            ledger.create(100, {"solver": 100})
            identity = ledger.reserve("solver", "example", 0.25, "example")
            ledger.settle(identity, None, dict(type="APITimeoutError"))
            with ledger.connect() as db:
                db.row_factory = sqlite3.Row
                before = dict(db.execute("SELECT * FROM receipts").fetchone())
            if extra_unknown:
                second = ledger.reserve("solver", "example", 0.2)
                ledger.settle(second, None, dict(type="APITimeoutError"))
            proposal = dict(
                receipt_before=before,
                certificate=dict(
                    hashes={"cache.yaml": "synthetic"},
                    cost=0.3,
                    cost_interval=[0.05, 0.3],
                    unknown_charge_interval=[0.0, 0.25],
                    successful_api_responses=2,
                    attempted_api_requests=3,
                    replays=[dict(cap=cap) for cap in (0.05, 0.075, 0.09)],
                    failure="provider_api_timeout_with_bounded_charge",
                ),
            )
            save(folder / "bounded_timeout_preparation.json", proposal)
            save(root / "PAUSED", dict(reason="Unresolved request billing"))
            save(
                root / "resumption.json",
                dict(authorization="Approved synthetic bound"),
            )
            with self.assertRaises(CampaignExhausted):
                ledger.reserve(
                    "solver", "example", 0.1, halt_on_billing_issue=True
                )
            with ExitStack() as stack:
                stack.enter_context(patch.object(recovery, "CAMPAIGN", root))
                stack.enter_context(patch.object(recovery, "FOLDER", folder))
                stack.enter_context(
                    patch.object(recovery, "RECEIPT", identity)
                )
                stack.enter_context(
                    patch.object(recovery, "prepare", return_value=proposal)
                )
                finalized = stack.enter_context(
                    patch(
                        "experiments.ace_independent_audit.terminal_failure.run"
                    )
                )
                if not approve or extra_unknown:
                    with self.assertRaises(ValueError):
                        recovery.apply(
                            "Approved synthetic bound" if approve else ""
                        )
                    self.assertTrue((root / "PAUSED").exists())
                    finalized.assert_not_called()
                else:
                    with redirect_stdout(io.StringIO()):
                        recovery.apply("Approved synthetic bound")
                    self.assertFalse((root / "PAUSED").exists())
                    finalized.assert_called_once_with(recovery.BATCH)
            with ledger.connect() as db:
                db.row_factory = sqlite3.Row
                after = dict(
                    db.execute(
                        "SELECT * FROM receipts WHERE id=?", (identity,)
                    ).fetchone()
                )
            if approve and not extra_unknown:
                self.assertEqual(after.pop("status"), "bounded_charge")
                before.pop("status")
                self.assertEqual(after, before)
                # The existing ledger still reserves the whole liability,
                # and any subsequent unknown request blocks admission again.
                second = ledger.reserve(
                    "solver", "example", 0.1, halt_on_billing_issue=True
                )
                ledger.settle(second, None, dict(type="APITimeoutError"))
                with self.assertRaises(CampaignExhausted):
                    ledger.reserve(
                        "solver", "example", 0.1, halt_on_billing_issue=True
                    )
            else:
                self.assertEqual(after, before)

    def test_explicit_approval_is_required(self) -> None:
        self.exercise(approve=False)

    def test_bound_retains_liability_and_future_guard(self) -> None:
        self.exercise(approve=True)

    def test_another_unknown_still_blocks_dispatch(self) -> None:
        self.exercise(approve=True, extra_unknown=True)


if __name__ == "__main__":
    unittest.main()
