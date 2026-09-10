"""Live trainX focus/witness checks; no API calls, both harnesses."""

from dataclasses import replace
from delphyne.utils.typing import pydantic_load

import ace.ace_applicability as aa
import ace.ace_grounded as ag
from ace.change_progress import audit_progress
from runtime.tool_budget import ToolLimits
from tools.reports.change_control_report import read


def test_original_not_nested_focus() -> None:
    rows = read("artifact.json")["states"]
    state = pydantic_load(aa.RepairState, rows[1]["state"])
    limits = ToolLimits(seconds=10)
    for suffix, expected in (
        (
            [aa.syntax_form(state.failed_action)[1], "rewrite IH.", "lia."],
            True,
        ),
        (["assert (Hdummy : True).", "{ exact I."], False),
        (["shelve."], False),
        ([aa.syntax_form(state.failed_action)[1]], False),
    ):
        checked = ag.checked_proof(
            state.problem_file,
            state.theorem_name,
            [*state.prefix, *suffix],
            limits,
            assisted=False,
        )
        result = audit_progress(state, checked, limits)
        assert result.useful == expected, (suffix, result)
        if expected:
            assert not audit_progress(
                state, replace(checked, outcome="unknown")
            ).useful


if __name__ == "__main__":
    test_original_not_nested_focus()
    print(
        "ok original focus, nested assertion, shelving, conversion-only, unknown"
    )
