"""Materialize train-only snippet demonstrations with real Rocq, no API.

Shared entry point: python -m tools.data.snippet_demos
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from dataclasses import asdict
import json
from typing import Any

import delphyne as dp
import yaml

from ace.rocq_snippets import check_snippet, context_for
from ace.terminal_evidence import extract_terminal_evidence
from experiments.ace.ace_attribution_experiment import read as reference_read
from experiments.coverage_cycle_experiment import partition
from prove_grounded import ProposeProofScriptGroundedSnippets
from runtime import pytanque_utils as pt
from runtime.paths import OMPHALOS_ROOT as ROOT


def build() -> None:
    path = (
        ROOT
        / "experiments/campaigns/ace_capacity_20260912/snippet_witness.json"
    )
    witness = json.loads(path.read_text())
    square = context_for(
        witness["problem_file"],
        witness["theorem_name"],
        (witness["prefix"],),
        "train-demo-square",
    )
    raw: list[dict[str, Any]] = yaml.safe_load(
        (ROOT / "demos/applicability.demo.yaml").read_text()
    )
    example = next(
        d
        for d in raw
        if d.get("query") == "DecideSyntaxRepair"
        and d["args"]["state"]["theorem_name"] == "amc12_2000_p6"
    )
    state = example["args"]["state"]
    change = context_for(
        partition("training")["amc12_2000_p6"],
        "amc12_2000_p6",
        tuple(state["prefix"]),
        "train-demo-change",
    )
    pairs = [
        (
            square,
            "have hs : 0 <= (4 * x + 5) * (4 * x + 5) := Rle_0_sqr _.",
            "assert (hs : 0 <= (4 * x + 5) * (4 * x + 5)) by apply Rle_0_sqr.",
        ),
        (
            change,
            state["failed_action"],
            example["answers"][0]["answer"]["correction"],
        ),
    ]
    demos: list[dict[str, Any]] = []
    for index, (context, bad, good) in enumerate(pairs):
        limits: dict[str, float | int] = dict(
            seconds=60, rpc_calls=512, view_bytes=8192
        )
        rejected = check_snippet(context, bad, limits)
        accepted = check_snippet(context, good, limits)
        assert rejected.status == "rejected" and accepted.executable
        tool = dp.ToolCall(
            "CheckRocqSnippet",
            dict(context_id=context.identifier, snippet=bad),
        )
        answer = dp.Answer(None, "", tool_calls=(tool,))
        repaired_call = dp.ToolCall(
            "CheckRocqSnippet",
            dict(context_id=context.identifier, snippet=good),
        )
        if index == 0:
            finished = check_snippet(context, good + " nra.", limits)
        else:
            reference = next(
                r
                for r in reference_read("references.json")["training"]
                if r["theorem"] == context.theorem_name
            )
            terminal = extract_terminal_evidence(
                ROOT / reference["source"] / "configs" / reference["name"],
                context.theorem_name,
            )
            assert terminal.status == "accepted"
            finished = check_snippet(
                context_for(context.problem_file, context.theorem_name),
                "\n".join(terminal.accepted_script),
                limits,
            )
        assert finished.status == "completed", finished.render()
        query = ProposeProofScriptGroundedSnippets(
            spec=pt.parse_problem(context.problem_file, True),
            available_skills={},
            snippet_checks=True,
            snippet_contexts=(context,),
            prefix=(
                dp.OracleMessage("oracle", answer),
                dp.ToolResult("tool", tool, rejected.render()),
                dp.OracleMessage(
                    "oracle", dp.Answer(None, "", tool_calls=(repaired_call,))
                ),
                dp.ToolResult("tool", repaired_call, accepted.render()),
            ),
            verified_prefix="\n".join(context.prefix),
        )
        demos.append(
            dict(
                demonstration=f"snippet_repair_{index}",
                query=query.query_name(),
                args=asdict(query),
                answers=[
                    dict(
                        answer=(
                            "The corrected form executed in Rocq. Finish with the checked proof."
                            if index == 0
                            else "The corrected fragment executed, but that alone does not establish a useful route. Restart from the initial theorem with this separately checked complete parity proof."
                        )
                        + "\n```rocq\n"
                        + "\n".join(finished.checked.feedback.proof_so_far)
                        + "\n```",
                    )
                ],
            )
        )
        for label, snippet, status in (
            ("rejected", bad, "rejected"),
            ("accepted", good, accepted.status),
        ):
            demos.append(
                dict(
                    demonstration=f"snippet_{index}_{label}",
                    strategy="verify_snippet_demo",
                    args=dict(
                        context=asdict(context),
                        snippet=snippet,
                        expected=status,
                    ),
                    tests=["run | success"],
                    queries=[],
                )
            )
    (ROOT / "demos/snippets.demo.yaml").write_text(
        yaml.safe_dump(demos, sort_keys=False, allow_unicode=True)
    )
    print(
        "Built 2 query examples and 4 live Rocq navigation tests; no API calls"
    )


if __name__ == "__main__":
    build()
