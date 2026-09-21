"""Real serializer regression for a preexisting handoff lock directory."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from . import concurrent_queue as q


class ConcurrentQueueTests(unittest.TestCase):
    def test_lock_only_initialization_creates_the_original_todo_cells(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "synthetic"
            directory.mkdir()
            (directory / ".launch.lock").touch()
            # Config serialization does not instantiate or inspect a problem.
            jobs = dict(
                one=q.old.c.Job("train", "S1", "synthetic", 0, "", "", True)
            )
            with (
                patch.object(q, "OUTPUT", root),
                patch.object(q.old, "jobs", return_value=jobs),
                patch.object(q, "ledger_rows", return_value=[]),
            ):
                q.initialize_lock_only("synthetic")
                self.assertTrue((directory / "experiment.yaml").exists())
                with self.assertRaisesRegex(ValueError, "only the handoff"):
                    q.initialize_lock_only("synthetic")
                with patch.object(
                    q, "ledger_rows", return_value=[dict(cell="one")]
                ):
                    with self.assertRaisesRegex(ValueError, "already has"):
                        q.initialize_lock_only("synthetic")


if __name__ == "__main__":
    unittest.main()
