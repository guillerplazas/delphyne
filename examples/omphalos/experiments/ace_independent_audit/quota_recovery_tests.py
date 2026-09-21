"""HTTP-disabled checks for preserving a credit-interrupted trajectory."""

from dataclasses import replace
import importlib
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
from typing import Any
import unittest
from unittest.mock import patch

from delphyne.stdlib.tasks import run_command
from delphyne.stdlib.models import LLMRequest

from . import quota_recovery as q
from .common import CAMPAIGN, sha
from .prefix_snapshots import isolated_snapshots
from .transport import AuditModel


class QuotaContinuationTests(unittest.TestCase):
    def test_launcher_restores_prefix_without_changing_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prefix = root / "saved.yaml"
            prefix.write_text("preserved paid prefix\n")
            args = SimpleNamespace(
                policy_args={"cell": q.CELL},
                cache_file="working.yaml",
                cache_mode="create",
                budget={"price": 0.1, "num_requests": 32},
            )
            q.restore_launcher_prefix(
                args, SimpleNamespace(cache_root=root), prefix
            )
            self.assertEqual(sha(root / "working.yaml"), sha(prefix))
            self.assertEqual(args.cache_mode, "read_write")
            self.assertEqual(args.budget, {"price": 0.1, "num_requests": 32})
            with self.assertRaisesRegex(ValueError, "cache initialization"):
                q.restore_launcher_prefix(
                    args, SimpleNamespace(cache_root=root), prefix
                )

    def test_launcher_refuses_another_cell(self) -> None:
        args = SimpleNamespace(policy_args={"cell": "other"})
        with self.assertRaisesRegex(ValueError, "another cell"):
            q.restore_launcher_prefix(args, None, Path("must-not-be-opened"))

    def test_actual_prefix_and_altered_next_request(self) -> None:
        prefix = q.FOLDER / "original" / "cache.yaml"
        with isolated_snapshots(q.CELL, prefix):
            result = q.offline_prefix(0.10, prefix)
        self.assertTrue(result["prefix_consumed"])
        self.assertEqual(result["paid_calls"], 0)
        rejected = q.raw_rejection()
        rejected["request"]["options"]["max_completion_tokens"] += 1
        with (
            isolated_snapshots(q.CELL, prefix),
            patch.object(q, "raw_rejection", return_value=rejected),
            self.assertRaisesRegex(
                ValueError, "first resumed request diverged"
            ),
        ):
            q.offline_prefix(0.10, prefix)

    def test_first_dispatch_keeps_original_comparison_response(self) -> None:
        """Exercise the paid adapter path with its transport replaced by a sentinel."""
        prefix = q.FOLDER / "original" / "cache.yaml"
        rejected = q.raw_rejection()
        previous = rejected["payload"]["extra_body"]["prompt_cache_options"][
            "comparison_response_id"
        ]
        captured: list[str | None] = []

        def fake_send(model: AuditModel, request: LLMRequest) -> None:
            captured.append(model.previous_response())
            raise q.PrefixReached

        rs = importlib.import_module("delphyne.stdlib.commands.run_strategy")
        q.c.activate()
        with tempfile.TemporaryDirectory(dir=CAMPAIGN) as tmp:
            root = Path(tmp)
            copied = root / "cache.yaml"
            shutil.copy2(prefix, copied)
            args = q.job().instantiate(None)
            args.cache_file = str(copied)
            args.cache_mode = "read_write"
            args.export_raw_trace = args.export_browsable_trace = (
                args.export_log
            ) = False
            events: list[dict[str, Any]] = []
            with (
                isolated_snapshots(q.CELL, prefix),
                patch.dict(
                    os.environ,
                    OMPHALOS_ADMISSION_EVENTS=str(root / "test_events.jsonl"),
                ),
                patch.object(q, "FOLDER", root),
                patch.object(q.AuditModel, "_send_final_request", fake_send),
                patch(
                    "openai.OpenAI",
                    side_effect=AssertionError("HTTP forbidden"),
                ),
                q.continuation_adapter(
                    prefix,
                    rejected["request"],
                    offline=False,
                    events=events,
                    previous_response_id=previous,
                ),
                self.assertRaises(q.PrefixReached),
            ):
                run_command(
                    rs.run_strategy,
                    args,
                    ctx=replace(q.c.context(), cache_root=Path("/")),
                    add_header=False,
                )
            self.assertEqual(captured, [previous])
            self.assertTrue(events[0]["prefix_consumed"])
            self.assertTrue((root / "first_request_guard.json").exists())


if __name__ == "__main__":
    unittest.main()
