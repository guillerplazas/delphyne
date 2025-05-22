"""
Testing the demonstration interpreter with _expect tests_.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

import delphyne as dp
from delphyne import analysis
from delphyne.analysis import feedback as fb
from delphyne.utils import typing as ty
from delphyne.utils.yaml import dump_yaml

STRATEGY_FILE = "example_strategies"
TESTS_FOLDER = Path(__file__).parent
CONTEXT = analysis.DemoExecutionContext([TESTS_FOLDER], [STRATEGY_FILE])


def check_object_included(small: object, big: object, path: str = "expect"):
    def error():
        return f"Mismatch at '{path}':\n    Expected: {small}\n    Got: {big}"

    match small:
        case "__any__":
            pass
        case "__empty__":
            assert isinstance(big, (list, tuple)) and not big, error()
        case list() | tuple():
            assert isinstance(big, (list, tuple)), error()
            small = cast(Sequence[Any], small)
            big = cast(Sequence[Any], big)
            assert len(small) <= len(big)
            for i, (small_elt, big_elt) in enumerate(zip(small, big)):
                check_object_included(small_elt, big_elt, f"{path}[{i}]")
        case dict():
            assert isinstance(big, dict), error()
            small = cast(dict[Any, Any], small)
            big = cast(dict[Any, Any], big)
            for k in small:
                assert k in big, error()
                check_object_included(small[k], big[k], f"{path}[{repr(k)}]")
        case _:
            assert small == big, error()


@dataclass
class DemoExpectTest(dp.StrategyDemo):
    expect: object = None

    def check(self, ctx: analysis.DemoExecutionContext):
        feedback, trace = analysis.evaluate_strategy_demo_and_return_trace(
            self, ctx, dp.stdlib_globals()
        )
        if trace is not None:
            print(dump_yaml(dp.ExportableTrace, trace.export()))
        print(dump_yaml(fb.StrategyDemoFeedback, feedback))
        feedback_serialized = ty.pydantic_dump(
            fb.StrategyDemoFeedback, feedback, exclude_defaults=False
        )
        if self.expect is not None:
            check_object_included(self.expect, feedback_serialized)


def load_demo(demo_label: str) -> DemoExpectTest | dp.QueryDemo:
    DEMO_FILE = Path(__file__).parent / f"{STRATEGY_FILE}.demo.yaml"
    demos_json = yaml.safe_load(open(DEMO_FILE, "r").read())
    demos = ty.pydantic_load(list[DemoExpectTest | dp.QueryDemo], demos_json)
    for demo in demos:
        if demo_label and demo_label == demo.demonstration:
            return demo
    else:
        assert False, f"Not found: {demo_label}"


@pytest.mark.parametrize(
    "demo_label",
    [
        "make_sum_demo",
        "make_sum_selectors",
        "make_sum_at",
        "make_sum_stuck",
        "make_sum_test_parse_error",
        "trivial_strategy",
        "buggy_strategy",
        "strategy_not_found",
        "invalid_arguments",
        "unknown_query",
        "invalid_answer",
        "synthetize_fun_demo",
        "test_iterate",
        "test_generate_pairs",
        "comp_result_in_cache",
        "comp_result_outside_cache",
        "tool_use",
    ],
)
def test_server(demo_label: str):
    demo = load_demo(demo_label)
    print("\n")
    assert isinstance(demo, DemoExpectTest)
    demo.check(CONTEXT)


@pytest.mark.parametrize(
    "name, valid",
    [
        ("MakeSum_demo", True),
        ("Unknown_query", False),
        ("structured_output", True),
    ],
)
def test_query_demo(name: str, valid: bool):
    demo = load_demo(name)
    assert isinstance(demo, dp.QueryDemo)
    extra = dp.stdlib_globals()
    ret = analysis.evaluate_standalone_query_demo(demo, CONTEXT, extra)
    has_errors = ret.diagnostics or ret.answer_diagnostics
    if valid:
        assert not has_errors
    else:
        assert has_errors


if __name__ == "__main__":
    # Entry point for the debugger (see "Debug Server Tests" configuration).
    test_server("test_iterate")
