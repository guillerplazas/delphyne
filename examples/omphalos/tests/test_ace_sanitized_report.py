"""Offline checks for denominators and diagnostic interpretation."""

import json
import math
from pathlib import Path
from typing import Any

import pytest

from tools.reports import ace_sanitized as r


def test_reporting_source_is_preserved_and_cannot_be_replaced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(r.c, "CAMPAIGN", tmp_path)
    digest = r.preserve_reporting_source()
    snapshot = tmp_path / "report_sources" / f"{digest}.py"
    assert r.c.sha(snapshot) == digest
    assert r.preserve_reporting_source() == digest
    snapshot.write_bytes(b"changed source")
    with pytest.raises(ValueError, match="archive drift"):
        r.preserve_reporting_source()


def test_comparison_includes_failures_and_disqualifies_cap_crossings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def problems(_: str) -> dict[str, str]:
        return {"one": "one", "two": "two"}

    monkeypatch.setattr(r, "partition", problems)
    monkeypatch.setattr(r, "families", problems)
    rows: list[dict[str, Any]] = []
    outcomes = {
        "control": [(True, 0.03), (True, 0.06), (False, 0.01), (True, 0.04)],
        "candidate": [
            (True, 0.11),  # A kernel proof above the cost cap is unqualified.
            (True, 0.02),
            (False, 0.01),  # Failed attempts still contribute their costs.
            (False, 0.01),
        ],
    }
    for arm, values in outcomes.items():
        for i, (solved, cost) in enumerate(values):
            rows.append(
                dict(
                    arm=arm,
                    theorem="one" if i < 2 else "two",
                    seed=i % 2,
                    solved=solved,
                    failed=i == 2,
                    cost=cost,
                )
            )
    comparison = r.comparison(rows, "control", "candidate")
    assert comparison["cells"] == 4
    assert (comparison["solved_a"], comparison["solved_b"]) == (3, 1)
    assert comparison["coverage_change_points"] == -50
    assert math.isclose(comparison["cost_a"], 0.14)
    assert math.isclose(comparison["cost_b"], 0.15)
    assert math.isclose(comparison["budget_reduction_percent"], -100 / 14)
    assert comparison["failed_a"] == comparison["failed_b"] == 1
    assert comparison["cap_crossings_b"] == 1
    assert "verdict" not in comparison  # No inherited effect-size veto.
    with pytest.raises(ValueError, match="Missing cells"):
        r.comparison(rows[:-1], "control", "candidate")


def test_diagnostics_distinguish_admission_from_output_truncation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(r.c, "CAMPAIGN", tmp_path)
    events = [
        dict(
            cell="priced",
            kind="terminal_v2",
            decision="stopped",
            time=4,
            last_admission={"limiting": ["price"]},
        ),
        dict(
            cell="priced",
            kind="estimate_v2",
            decision="estimated",
            time=3,
            reasoning_allowance=0,
        ),
        dict(
            cell="priced",
            kind="refined_session",
            decision="reset",
            time=2,
            before_chars=30000,
            after_chars=9000,
        ),
        dict(
            cell="other",
            kind="terminal_v2",
            decision="stopped",
            time=5,
            last_admission=None,
        ),
    ]
    (tmp_path / "events.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in events)
    )
    rows = [
        dict(cell=cell, role="proof", stage="pilots", arm="drop", cost=cost)
        for cell, cost in (("priced", 0.04), ("other", 0.03))
    ]
    rows.append(dict(cell="role", role="curator", stage="learning"))
    receipts = [
        dict(cell="priced", input=100, output=20, provider_status="completed"),
        dict(cell="priced", input=150, output=30, provider_status="completed"),
        dict(
            cell="other", input=120, output=8192, provider_status="incomplete"
        ),
    ]
    summary = r.mechanisms(rows, receipts)["pilots/drop"]
    assert summary["cells"] == 2
    assert summary["terminal_stop_reasons"] == {"price": 1, "other": 1}
    assert summary["median_price_stop_spend"] == 0.04
    assert summary["provider_status_counts"] == {
        "completed": 2,
        "incomplete": 1,
    }
    assert summary["median_last_first_input_ratio"] == 1.5
    assert summary["input_growth_cells"] == 1
    assert summary["resets"][0]["next_reasoning_allowance"] == 0
