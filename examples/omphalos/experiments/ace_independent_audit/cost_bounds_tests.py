"""Offline checks that unknown bills cannot become exact costs or false wins."""

from pathlib import Path
import shutil
import tempfile
from typing import Any
import unittest
from unittest.mock import patch

from . import cost_bounds
from . import fresh
from .analysis import metrics, paired
from .common import CAMPAIGN, read, save, sha


def example(
    theorem: str, cost: float, lower: float | None = None
) -> dict[str, Any]:
    row: dict[str, Any] = dict(
        theorem=theorem,
        seed=0,
        solved=True,
        costs=dict(price=cost),
        counts=dict(requests=1),
        turns=[],
        exact_cost=lower is None,
    )
    if lower is not None:
        row["cost_interval"] = [lower, cost]
    return row


class CostIntervalContract(unittest.TestCase):
    def test_aggregate_exposes_missing_bill(self) -> None:
        result = metrics([example("one", 10, 5), example("two", 10)])
        self.assertEqual(result["cost"], 20)
        self.assertEqual(result["cost_interval"], [15, 20])
        self.assertEqual(result["cost_per_solve_interval"], [7.5, 10])
        self.assertFalse(result["cost_is_exact"])
        self.assertEqual(result["bounded_cost_cells"], 1)

    def test_target_uses_adverse_billing_endpoint(self) -> None:
        base = [example("one", 10, 5), example("two", 10)]
        arm = [example("one", 8), example("two", 8)]
        result = paired(base, arm)
        self.assertAlmostEqual(result["saving"], 0.2)
        self.assertAlmostEqual(result["saving_interval"][0], 1 - 16 / 15)
        self.assertFalse(result["practical_target"])
        self.assertIsNone(result["two_sided_sign_flip_p"])
        self.assertLessEqual(
            result["saving_ci90"][0], result["saving_interval"][0]
        )
        certain_base = [example("one", 10), example("two", 10)]
        uncertain_arm = [example("one", 8, 7), example("two", 8, 7)]
        win = paired(certain_base, uncertain_arm)
        self.assertTrue(win["practical_target"])
        self.assertAlmostEqual(win["saving_interval"][0], 0.2)
        self.assertAlmostEqual(win["saving_interval"][1], 0.3)

    def test_exact_comparisons_keep_exact_representation(self) -> None:
        base = [example("one", 10), example("two", 10)]
        arm = [example("one", 8), example("two", 8)]
        self.assertNotIn("cost_interval", metrics(arm))
        result = paired(base, arm)
        self.assertNotIn("saving_interval", result)
        self.assertIsInstance(result["two_sided_sign_flip_p"], float)
        self.assertTrue(result["practical_target"])

    def test_only_approved_unchanged_receipt_is_accepted(self) -> None:
        # Use an isolated copy of the reviewed evidence; never authorize or
        # modify the live ledger/pause in this test.
        folder = CAMPAIGN / "billing_recovery"
        proposal = read(folder / "bounded_timeout_preparation.json")
        before = proposal["receipt_before"]
        with tempfile.TemporaryDirectory(dir=folder) as temp:
            root = Path(temp)
            prepared = (
                root / "billing_recovery/bounded_timeout_preparation.json"
            )
            approval = root / "billing_recovery/bounded_timeout_approval.json"
            save(prepared, proposal)
            source = root / "resumption.json"
            save(
                source, dict(authorization="Synthetic isolated test approval")
            )
            save(
                approval,
                dict(
                    user_authorization="Synthetic isolated test approval",
                    source_record="resumption.json",
                    source_sha=sha(source),
                    receipt=before["id"],
                    proposal_sha=sha(prepared),
                ),
            )
            certificate = dict(
                proposal["certificate"], liability_approval_sha=sha(approval)
            )
            save(
                root / "terminal_failures" / (before["cell"] + ".json"),
                certificate,
            )
            relative = (
                Path("responses")
                / before["cell"]
                / (before["id"] + ".json.gz")
            )
            (root / relative).parent.mkdir(parents=True)
            shutil.copyfile(CAMPAIGN / relative, root / relative)
            bounded = dict(before, status="bounded_charge")
            with patch.object(cost_bounds, "CAMPAIGN", root):
                self.assertEqual(
                    cost_bounds.receipt_interval(bounded),
                    (0.0, before["reserved"]),
                )
                with self.assertRaises(ValueError):
                    cost_bounds.receipt_interval(before)
                with self.assertRaises(ValueError):
                    cost_bounds.receipt_interval(dict(bounded, charged=0.0))
                approval.unlink()
                with self.assertRaises(FileNotFoundError):
                    cost_bounds.receipt_interval(bounded)

    def test_actual_timeout_prefix_remains_failed_with_interval(self) -> None:
        proposal = read(
            CAMPAIGN / "billing_recovery/bounded_timeout_preparation.json"
        )
        certificate = proposal["certificate"]
        identity, batch = certificate["cell"], certificate["batch"]
        batch_path = CAMPAIGN / "batches" / (batch + ".json")
        terminal_path = CAMPAIGN / "terminal_failures" / (identity + ".json")
        job = next(
            v
            for v in read(batch_path)
            if fresh.c.name(fresh.c.Job(**v), None) == identity
        )

        # Only certificate availability and the already-validated ledger
        # group are simulated. The cache, exception, usage reconstruction,
        # source hashes and failed outcome are the actual immutable evidence.
        def prepared_read(path: Path) -> Any:
            if path == batch_path:
                return [job]
            if path == terminal_path:
                return certificate
            return read(path)

        ledger = {
            identity: dict(
                cost=certificate["cost"],
                cost_interval=certificate["cost_interval"],
                requests=certificate["attempted_api_requests"],
                statuses={"settled": 23, "bounded_charge": 1},
                receipts=certificate["receipts"],
                bounded_receipts=[certificate["unknown_receipt"]],
            )
        }
        with (
            patch.object(fresh, "read", prepared_read),
            patch.object(fresh, "require_closed", side_effect=ValueError),
            patch(
                "experiments.ace_independent_audit.terminal_failure.assert_closed"
            ),
        ):
            rows = fresh.solver_rows(
                batch, ledger, allow_terminal_failures=True
            )
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertFalse(row["solved"])
        self.assertFalse(row["exact_cost"])
        self.assertEqual(row["counts"]["requests"], 24)
        self.assertEqual(row["counts"]["successful_api_responses"], 23)
        self.assertEqual(row["cost_interval"], certificate["cost_interval"])
        self.assertAlmostEqual(row["costs"]["price"], 0.25971182)


if __name__ == "__main__":
    unittest.main()
