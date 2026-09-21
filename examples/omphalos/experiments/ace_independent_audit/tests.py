"""Offline contract tests; never imports a benchmark aggregate or calls HTTP."""

from datetime import date
from pathlib import Path
import tempfile
import unittest
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.environments import DataManager, TemplatesManager

from experiments.ace_sanitized.scope import partition
from prove_ace import ProposeProofScriptACE
from prove_agentic import ProposeProofScriptAgentic
from runtime.model_registry import pricing_for
from runtime.pytanque_utils import ProblemSpec

from .accounting import price
from .campaign import context
from .solver import AuditPlainProof
from .verification import compilation_source
from .robust_solver import checked
from .learning_v3 import outer_yaml
from .completion import completed_config, ground_truth
from runtime.rocq_server import Deadline


class Contracts(unittest.TestCase):
    def test_intermediate_result_is_not_completion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            self.assertEqual(ground_truth(path), "todo")
            (path / "result.yaml").write_text(
                "outcome: {result: {values: []}}\n"
            )
            (path / "cache.yaml").write_text("[]\n")
            self.assertEqual(ground_truth(path), "failed")
            with patch(
                "experiments.ace_independent_audit.completion._original_run_config",
                return_value=("example", True),
            ):
                completed_config(config_dir=path)
            self.assertEqual(ground_truth(path), "done")
            (path / "cache.yaml").write_text("changed\n")
            self.assertEqual(ground_truth(path), "failed")

    def test_nested_rocq_fence_preserves_outer_yaml(self) -> None:
        import yaml

        text = """Explanation.
```yaml
lesson: |
  Use this tactic:
  ```rocq
  nra.
  ```
tags: []
```
"""
        value = yaml.safe_load(outer_yaml(text))
        self.assertEqual(value["tags"], [])
        self.assertIn("```rocq\nnra.\n```", value["lesson"])
        with self.assertRaises(ValueError):
            outer_yaml("```yaml\na: 1\n")

    def test_transport_failure_never_certifies_a_proof(self) -> None:
        with patch(
            "runtime.pytanque_utils.check",
            side_effect=Deadline("synthetic deadline"),
        ):
            for assisted in (False, True):
                feedback = checked(
                    "unused", "example", ["reflexivity."], assisted
                )
                self.assertFalse(feedback.success)
                self.assertFalse(feedback.auto_finished)
                self.assertIn(
                    "not a logical rejection", feedback.error_message or ""
                )

    def test_four_disjoint_categories(self) -> None:
        usage: dict[str, Any] = dict(
            input_tokens=1000,
            output_tokens=100,
            input_tokens_details=dict(
                cached_tokens=400, cache_write_tokens=300
            ),
        )
        actual = price(usage, "gpt-5.6-luna", on=date(2026, 9, 19))
        self.assertAlmostEqual(actual["price"], 0.000263)
        self.assertEqual(actual["ordinary"], 300)
        usage["input_tokens_details"]["cache_write_tokens"] = 700
        with self.assertRaises(ValueError):
            price(usage, "gpt-5.6-luna", on=date(2026, 9, 19))

    def test_missing_write_usage_is_not_zero(self) -> None:
        with self.assertRaises(ValueError):
            price(
                dict(
                    input_tokens=1000,
                    output_tokens=100,
                    input_tokens_details=dict(cached_tokens=100),
                ),
                "gpt-5.6-luna",
                on=date(2026, 9, 19),
            )

    def test_tariff_multipliers_and_dated_rates(self) -> None:
        usage: dict[str, Any] = dict(
            input_tokens=400000,
            output_tokens=1000,
            input_tokens_details=dict(
                cached_tokens=200000, cache_write_tokens=100000
            ),
        )
        actual = price(
            usage,
            "gpt-6-astra",
            on=date(2026, 9, 19),
            tier="priority",
            regional=True,
        )
        expected = (
            ((100000 * 10 + 200000 * 1 + 100000 * 12.5) * 2 + 1000 * 50 * 1.5)
            / 1e6
            * 2
            * 1.1
        )
        self.assertAlmostEqual(actual["price"], expected)
        self.assertAlmostEqual(
            pricing_for(
                "gpt-5.6-sol", date(2026, 9, 18)
            ).dollars_per_input_token,
            5e-6,
        )
        self.assertAlmostEqual(
            pricing_for(
                "gpt-5.6-sol", date(2026, 9, 19)
            ).dollars_per_input_token,
            4e-6,
        )

    def test_empty_book_matches_original_prompts_and_tools(self) -> None:
        templates = TemplatesManager(context().prompt_dirs, DataManager([]))
        spec = ProblemSpec("unused", "example", ": True", "", "", "")
        queries = [
            ProposeProofScriptAgentic(spec, {}, "core", 32),
            ProposeProofScriptACE(
                spec, {}, "core", 32, playbook="", render_version=2
            ),
        ]
        for kind in ("system", "instance"):
            rendered = [
                templates.prompt(
                    query_name=q.query_name(),
                    prompt_kind=kind,
                    template_args=dict(query=q),
                )
                for q in queries
            ]
            self.assertEqual(rendered[0], rendered[1])
        self.assertEqual(
            [t.tool_name() for t in queries[0].advertised_tools()],
            ["ReadSkill", "SearchRocq"],
        )
        plain = AuditPlainProof(spec, {}, "core", 32)
        text = templates.prompt(
            query_name=plain.query_name(),
            prompt_kind="system",
            template_args=dict(query=plain),
        )
        self.assertIn("It never supplies tactics or completes", text)
        self.assertNotIn("finishes the proof for you", text)
        self.assertEqual(
            plain.advertised_tools(), queries[0].advertised_tools()
        )

    def test_scope_rejects_unknown_partition_before_read(self) -> None:
        with self.assertRaises(ValueError):
            partition("forbidden_partition")

    def test_kernel_compilation_retains_binders_and_rejects_holes(
        self,
    ) -> None:
        problem = "Theorem example (n : nat) : n = n.\nProof. Admitted.\n"
        good = compilation_source(problem, "example", "reflexivity.")
        self.assertIn("Theorem example (n : nat)", good)
        self.assertNotIn("Admitted.", good)
        for proof in (
            "admit.",
            "Admitted.",
            "Axiom fake : False.",
            "Unset Guard Checking.",
        ):
            with self.assertRaises(ValueError):
                compilation_source(problem, "example", proof)


if __name__ == "__main__":
    unittest.main()
