"""
Materialize a demonstration file: evaluate each strategy demo, collect
every *implicit* answer the interpreter had to fabricate (answers
fetched from `using:` sources and `__Computation__` results), and write
them back as explicit `queries:` entries.

The result is a fully self-contained, warning-free demo file: every
LLM answer and every computation result is pinned in the YAML, so
`delphyne check` neither needs the cached command files nor a live
Rocq/pytanque toolchain, and reports zero "implicit answers" warnings.

Usage (from `examples/omphalos`):

    python -m tools.data.materialize_demo demos/agentic.demo.yaml
    python -m tools.data.materialize_demo demos/standard.demo.yaml --drop-using
"""

# pyright: strict

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from delphyne import core_and_base as dp
from delphyne.analysis.demo_interpreter import evaluate_demo
from delphyne.analysis.feedback import ImplicitAnswer, StrategyDemoFeedback
from delphyne.stdlib.execution_contexts import load_execution_context
from delphyne.stdlib.globals import (
    stdlib_globals,
    stdlib_implicit_answer_generators,
)
from delphyne.utils import typing as ty
from delphyne.utils.pretty_yaml import pretty_yaml


def _implicit_to_query_demo(ia: ImplicitAnswer) -> dict[str, Any]:
    """
    Turn an implicit answer into an explicit QueryDemo YAML dict.

    `example: false` is set on every materialized answer so that demo
    entries never leak into few-shot example selection: demos stay
    executable specifications, and benchmark prompts are unaffected.
    (Tool-call-bearing answers would in fact *break* OpenAI few-shot
    injection, which requires tool results right after tool calls.)
    """
    answer: dict[str, Any] = {"answer": ia.answer_content, "example": False}
    if ia.answer_mode is not None:
        answer["mode"] = ia.answer_mode
    if ia.answer_tool_calls:
        answer["call"] = [
            {"tool": tc.tool, "args": tc.args} for tc in ia.answer_tool_calls
        ]
    if ia.answer_justification:
        answer["justification"] = ia.answer_justification
    return {
        "query": ia.query_name,
        "args": ia.query_args,
        "answers": [answer],
    }


def _leading_comment(text: str) -> str:
    """Preserve the leading comment block (YAML round-trips drop it)."""
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            lines.append(line)
        else:
            break
    return "\n".join(lines).rstrip() + "\n\n" if lines else ""


def materialize(file: Path, drop_using: bool) -> None:
    workspace_dir = file.resolve().parent.parent
    context = load_execution_context(workspace_dir, local=file)
    original_text = file.read_text()
    header = _leading_comment(original_text)
    raw: list[dict[str, Any]] = yaml.safe_load(original_text)
    demos = ty.pydantic_load(list[dp.Demo], raw)
    loader = context.object_loader(extra_objects=stdlib_globals())
    changed = False
    for raw_demo, demo in zip(raw, demos):
        if not isinstance(demo, dp.StrategyDemo):
            continue
        feedback = evaluate_demo(
            demo,
            object_loader=loader,
            answer_database_loader=dp.standard_answer_loader(
                workspace_dir, loader
            ),
            implicit_answer_generators=(
                stdlib_implicit_answer_generators(context.data_dirs)
            ),
        )
        assert isinstance(feedback, StrategyDemoFeedback)
        new_entries = [
            _implicit_to_query_demo(ia)
            for answers in feedback.implicit_answers.values()
            for ia in answers
        ]
        if new_entries:
            raw_demo.setdefault("queries", [])
            raw_demo["queries"].extend(new_entries)
            changed = True
            print(
                f"[{demo.demonstration}] materialized "
                f"{len(new_entries)} implicit answer(s)"
            )
        if drop_using and "using" in raw_demo:
            del raw_demo["using"]
            changed = True
    if changed:
        file.write_text(header + pretty_yaml(raw))
        print(f"Rewrote {file}.")
    else:
        print("Nothing to materialize.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument(
        "--drop-using",
        action="store_true",
        help="Remove `using:` sources after materializing.",
    )
    args = parser.parse_args()
    if not args.file.is_file():
        sys.exit(f"No such file: {args.file}")
    materialize(args.file, args.drop_using)
