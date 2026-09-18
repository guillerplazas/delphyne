"""Offline tests for the sanitized campaign's boundaries and controls."""

from contextlib import redirect_stdout
from dataclasses import asdict, replace
import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.environments import DataManager, TemplatesManager
from delphyne.stdlib.tasks import run_command
import pytest

from ace.ace_grounded import Checked
from experiments.ace_sanitized import campaign as c
from experiments.ace_sanitized.control import (
    Controls,
    ProofTemplates,
    repeated_failure,
)
from experiments.ace_sanitized.scope import partition
from experiments.ace_sanitized.views import (
    bounded_query,
    checked_view,
    inspection_view,
)
from experiments.ace_sanitized.workflow import frontier
from experiments.economy_refinement.window import RefinedWindow
from prove_economy import interaction_groups
from prove_grounded import ProposeProofScriptGrounded
from runtime import pytanque_utils as pt
from runtime.campaign_budget import CampaignResponsesModel


def query() -> ProposeProofScriptGrounded:
    return ProposeProofScriptGrounded(
        pt.parse_problem(partition("train")[c.PILOT_THEOREMS[0]], True), {}
    )


def evidence(goal: str = "n : nat\n|- n = n") -> Checked:
    return Checked(
        pt.Feedback(
            False,
            failing_tactic="lia.",
            failing_index=1,
            error_message="Cannot find witness",
            proof_so_far=["intros n."],
            remaining_goals=[goal],
        ),
        "rejected",
        0.2,
        2,
        "raw view " + "x" * 5000,
    )


def failed_group(
    proof: str = "intros n. lia.",
    checked: Checked | None = None,
) -> tuple[dp.AnswerPrefixElement, ...]:
    return (
        dp.OracleMessage("oracle", dp.Answer(None, proof)),
        dp.FeedbackMessage("feedback", "failure", meta=checked or evidence()),
    )


def tool_group(result: str) -> tuple[dp.AnswerPrefixElement, ...]:
    call = dp.ToolCall("SearchRocq", {"command": "Check plus."})
    return (
        dp.OracleMessage("oracle", dp.Answer(None, "", (call,))),
        dp.ToolResult("tool", call, result),
    )


def test_one_plain_drop_retains_raw_evidence_and_never_regenerates_memory() -> (
    None
):
    groups = [
        failed_group() if i == 2 else tool_group(str(i) + "x" * 5000)
        for i in range(8)
    ]
    original = replace(
        query(),
        prefix=tuple(m for g in groups for m in g),
        verified_prefix="intros n.",
    )
    window = RefinedWindow(max_resets=1)
    dropped, reset = window.apply(original, lambda q: q)
    assert reset and interaction_groups(dropped.prefix) == [
        list(groups[i]) for i in (2, 6, 7)
    ]
    assert replace(dropped, prefix=original.prefix) == original
    # Subsequent presentation does not influence the raw-history trigger.
    bounded = bounded_query(dropped)
    assert bounded.verified_prefix == original.verified_prefix
    later = replace(original, prefix=(*original.prefix, *original.prefix))
    assert not window.apply(later, lambda q: q)[1]
    assert window.resets == 1


def test_stop_requires_identical_proposal_goals_and_checked_status() -> None:
    group = failed_group()
    assert not repeated_failure(group * 3)
    assert repeated_failure(group * 4)
    assert not repeated_failure(group * 3 + failed_group("different proof"))
    assert not repeated_failure(
        group * 3 + failed_group(checked=evidence("other goal"))
    )
    for outcome in ("unknown", "resource_exhausted", "accepted"):
        assert not repeated_failure(
            group * 3
            + failed_group(checked=replace(evidence(), outcome=outcome))
        )
    assert not repeated_failure(group * 3 + tool_group("new evidence") + group)
    assert repeated_failure(
        tool_group("old") + group * 3 + tool_group("old") + group
    )


def test_views_are_bounded_without_mutating_raw_proof_evidence() -> None:
    raw = evidence("λ" * 10000)
    q = replace(
        query(),
        prefix=failed_group(checked=raw) * 2,
        verified_prefix="intros n.",
    )
    compact = bounded_query(q)
    for message in compact.prefix:
        if isinstance(message, dp.FeedbackMessage):
            assert isinstance(message.meta, Checked)
            assert message.meta.feedback is raw.feedback
            assert len(message.meta.view.encode()) <= 4096
            assert "Cannot find witness" in message.meta.view
            assert "Remaining goals: 1" in message.meta.view
    assert "unchanged" not in checked_view(evidence(), "intros n.")
    raw_tool = json.dumps(
        dict(
            output="x" * 10000,
            goals=["current goal"],
            total_goals=5,
            start=0,
            next=4,
            outcome="unknown",
        )
    )
    shown = inspection_view(raw_tool)
    assert len(shown.encode()) <= 4096
    assert (
        "current goal" in shown and "unknown" in shown and "next: 4" in shown
    )
    call = dp.ToolCall("ReadSkill", {"name": "example"})
    msg = dp.ToolResult("tool", call, "skill" * 1600)
    assert bounded_query(replace(q, prefix=(msg,))).prefix == (msg,)


def test_concise_prompt_retains_book_tools_and_original_instances() -> None:
    folders = [p for p in (c.ROOT / "prompts").rglob("*") if p.is_dir()]
    original = TemplatesManager(folders, DataManager(()))
    concise = ProofTemplates(original)
    q = replace(query(), playbook="FROZEN_BOOK")
    args: dict[str, Any] = dict(query=q, example=False, params={}, mode=None)
    old = original.prompt(
        query_name=q.query_name(),
        prompt_kind="system",
        template_args=dict(args),
    )
    new = concise.prompt(
        query_name=q.query_name(),
        prompt_kind="system",
        template_args=dict(args),
    )
    assert len(new) < len(old) * 0.65 and q.playbook in new
    for tool in q.advertised_tools():
        assert tool.tool_name() in new
    for example in (True, False):
        args["example"] = example
        assert concise.prompt(
            query_name=q.query_name(),
            prompt_kind="instance",
            template_args=dict(args),
        ) == original.prompt(
            query_name=q.query_name(),
            prompt_kind="instance",
            template_args=dict(args),
        )


@pytest.mark.parametrize("stage", ["test", "testX", "challenge", "../test"])
def test_invalid_partition_rejected_before_any_io(
    stage: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_: object) -> None:
        raise AssertionError("No protected read")

    monkeypatch.setattr(Path, "read_text", forbidden)
    with pytest.raises(ValueError):
        partition(stage)


def test_whole_panel_liability_and_cost_coverage_frontier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = [
        c.Job(
            "validation",
            "ace",
            "proof",
            f"n{i}",
            "inputs/fixture.json",
            "hash",
        )
        for i in range(80)
    ]
    account: dict[str, Any] = dict(
        unresolved=[],
        billing_issues=[],
        ledger=dict(
            liability=17,
            allocations=dict(validation=20),
            groups=[dict(stage="validation", dollars=12)],
        ),
    )
    monkeypatch.setattr(c, "accounting", lambda: account)

    def pending(_: Path) -> str:
        return "pending"

    monkeypatch.setattr(c.ol, "ground_truth", pending)
    assert c.fits(jobs)
    account["ledger"]["liability"] += 0.001
    assert not c.fits(jobs)
    account["unresolved"] = ["uncertain charge"]
    with pytest.raises(ValueError, match="billing"):
        c.fits(jobs)
    values = dict(
        cheap=dict(cells=8, solved=4, cost=1),
        coverage=dict(cells=8, solved=6, cost=2),
        dominated=dict(cells=8, solved=3, cost=1.5),
    )
    assert frontier(values) == ["cheap", "coverage"]


@pytest.mark.parametrize("arm", ["agentic", "ace"])
def test_disabled_controls_exactly_replay_paid_reference(arm: str) -> None:
    # This module exposes only validation artifacts, never an eager X loader.
    from experiments import ace_economy_validation as reference

    theorem = next(iter(partition("validation")))
    job = reference.Config("validation", arm, theorem, 0)
    original = reference.cell_result(job)
    assert original is not None
    reference.activate(events=False)
    args = job.instantiate(None)
    args.policy = "sanitized_proof_policy"
    args.policy_args.pop("split_session")
    args.policy_args.pop("dollar_cap")
    args.policy_args["controls"] = asdict(Controls())
    args.cache_mode = "replay"
    args.cache_file = str(reference.directory(job) / "cache.yaml")
    args.export_raw_trace = args.export_browsable_trace = args.export_log = (
        False
    )
    with (
        patch.object(
            CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("HTTP forbidden"),
        ),
        redirect_stdout(io.StringIO()),
    ):
        result = run_command(
            run_strategy,
            args,
            ctx=replace(c.context(), cache_root=Path("/")),
            add_header=False,
        ).result
    assert result is not None
    assert result.success == original["success"]
    assert result.spent_budget == original["spent_budget"]
    assert json.loads(json.dumps(list(result.values))) == original["values"]
