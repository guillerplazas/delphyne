"""Offline invariants for independent controls, accounting and closure."""

from contextlib import redirect_stdout
from dataclasses import replace
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
from experiments import ace_economy_refinement_experiment as c
from experiments import ace_economy_validation as reference
from experiments.economy_refinement.policy import EconomyTemplates, identity
from experiments.economy_refinement.rendering import (
    compact_query,
    feedback_view,
    fingerprint,
    tool_view,
)
from experiments.economy_refinement.window import RefinedWindow
from prove_economy import interaction_groups
from prove_grounded import ProposeProofScriptGrounded
from runtime import pytanque_utils as pt
from runtime.campaign_budget import (
    CampaignExhausted,
    CampaignResponsesModel,
    Ledger,
)


def query() -> ProposeProofScriptGrounded:
    file = c.partition("train")[c.PILOT_THEOREMS[0]]
    return ProposeProofScriptGrounded(pt.parse_problem(file, True), {})


def checked(goal: str = "n : nat\n|- n = n") -> Checked:
    return Checked(
        pt.Feedback(
            False,
            failing_tactic="lia.",
            error_message="Cannot find witness",
            proof_so_far=["intros n."],
            remaining_goals=[goal],
        ),
        "rejected",
        0.2,
        2,
        "raw feedback " + "x" * 5000,
    )


def history(count: int) -> tuple[dp.AnswerPrefixElement, ...]:
    messages: list[dp.AnswerPrefixElement] = []
    for i in range(count):
        if i == 2:
            messages.extend(
                [
                    dp.OracleMessage(
                        "oracle", dp.Answer(None, "```rocq\nintros n.\n```")
                    ),
                    dp.FeedbackMessage("feedback", "rejected", meta=checked()),
                ]
            )
        else:
            call = dp.ToolCall("SearchRocq", {"command": f"Check name{i}."})
            messages.extend(
                [
                    dp.OracleMessage("oracle", dp.Answer(None, "", (call,))),
                    dp.ToolResult("tool", call, str(i) + "x" * 5000),
                ]
            )
    return tuple(messages)


def test_reset_only_drops_whole_groups_and_can_reset_twice() -> None:
    window = RefinedWindow()
    q = replace(query(), prefix=history(8), verified_prefix="intros n.")
    first, reset = window.apply(q, identity)
    assert reset and window.retained == (2, 6, 7)
    groups = interaction_groups(q.prefix)
    assert interaction_groups(first.prefix) == [groups[i] for i in (2, 6, 7)]
    assert replace(first, prefix=q.prefix) == q  # No added state or memory.
    same, reset = window.apply(q, identity)
    assert not reset and same == first
    q = replace(q, prefix=history(16))
    second, reset = window.apply(q, identity)
    assert reset and window.retained == (2, 14, 15)
    assert replace(second, prefix=q.prefix) == q
    third, reset = window.apply(replace(q, prefix=history(24)), identity)
    assert not reset and window.resets == 2
    assert len(interaction_groups(third.prefix)) == 11
    with pytest.raises(ValueError, match="append-only"):
        window.apply(q, identity)


def test_reset_requires_both_growth_and_meaningful_savings() -> None:
    q = replace(query(), prefix=history(7))
    assert not RefinedWindow().apply(q, identity)[1]
    q = replace(q, prefix=history(8))
    assert not RefinedWindow(threshold_chars=100000).apply(q, identity)[1]
    assert not RefinedWindow(minimum_removed_chars=100000).apply(q, identity)[
        1
    ]


def test_aliases_reexpand_after_drop_and_preserve_raw_evidence() -> None:
    evidence = checked()
    group = (
        dp.OracleMessage("oracle", dp.Answer(None, "```rocq\nlia.\n```")),
        dp.FeedbackMessage("feedback", "rejected", meta=evidence),
    )
    q = replace(query(), prefix=group * 8, verified_prefix="intros n.")
    compact = compact_query(q)
    views = [
        m.meta.view
        for m in compact.prefix
        if isinstance(m, dp.FeedbackMessage) and isinstance(m.meta, Checked)
    ]
    assert "n : nat" in views[0] and "unchanged" in views[1]
    assert all(
        m.meta.feedback is evidence.feedback
        for m in compact.prefix
        if isinstance(m, dp.FeedbackMessage) and isinstance(m.meta, Checked)
    )
    # Combined control uses rendered length: repetition no longer triggers it.
    assert not RefinedWindow().apply(q, compact_query)[1]
    window = RefinedWindow(threshold_chars=1, minimum_removed_chars=1)
    dropped, reset = window.apply(q, compact_query)
    assert reset
    after = [
        m.meta.view
        for m in dropped.prefix
        if isinstance(m, dp.FeedbackMessage) and isinstance(m.meta, Checked)
    ]
    assert "n : nat" in after[0] and "unchanged" not in after[0]
    assert "unchanged" in after[1]


def test_clipping_does_not_create_dangling_goal_aliases() -> None:
    goal = "λ" * 8000
    seen: set[str] = set()
    view = feedback_view(checked(goal), "intros n.", seen)
    assert len(view.encode()) <= 4096
    assert fingerprint(goal) not in seen
    assert "unchanged" not in feedback_view(checked(goal), "intros n.", seen)
    assert (
        "Remaining goals: 1" in view and "Error: Cannot find witness" in view
    )
    broken = "{malformed " + "λ" * 8000
    assert len(tool_view(broken, seen).encode()) <= 4096


def test_tool_view_preserves_status_and_current_goal_before_large_output() -> (
    None
):
    raw = json.dumps(
        dict(
            output="lemma information " * 2000,
            goals=["|- visible_goal"],
            total_goals=5,
            start=0,
            next=4,
            outcome="resource_exhausted",
        )
    )
    view = tool_view(raw, set())
    assert "visible_goal" in view and "resource_exhausted" in view
    assert "Next page: 4" in view and len(view.encode()) <= 4096


def test_compact_system_and_baseline_instances_keep_playbook_and_tools() -> (
    None
):
    # Explicit prompt directories contain no benchmark loader.
    folders = [p for p in (c.ROOT / "prompts").rglob("*") if p.is_dir()]
    original = TemplatesManager(folders, DataManager(()))
    compact = EconomyTemplates(original, True)
    q = replace(
        query(), playbook="UNCHANGED_PLAYBOOK", verified_prefix="intros n."
    )
    args: dict[str, Any] = dict(query=q, example=False, params={}, mode=None)
    old = original.prompt(
        query_name=q.query_name(),
        prompt_kind="system",
        template_args=dict(args),
    )
    new = compact.prompt(
        query_name=q.query_name(),
        prompt_kind="system",
        template_args=dict(args),
    )
    assert len(new) < len(old) * 0.65
    assert q.playbook in new
    assert (
        old.split("## Playbook")[1].split("## Verified state")[0].strip()
        in new
    )
    for tool in q.advertised_tools():
        assert tool.tool_name() in new
    for example in (True, False):
        args["example"] = example
        assert compact.prompt(
            query_name=q.query_name(),
            prompt_kind="instance",
            template_args=dict(args),
        ) == original.prompt(
            query_name=q.query_name(),
            prompt_kind="instance",
            template_args=dict(args),
        )


@pytest.mark.parametrize("ace", [False, True])
def test_config_changes_only_registered_axes(ace: bool) -> None:
    theorem = next(iter(reference.partition()))
    old = reference.Config(
        "validation", "ace" if ace else "agentic", theorem, 0
    ).instantiate(None)
    job = c.Config("final00", "validation", ace, False, False, theorem, 0)
    new = job.instantiate(None)
    assert new.args == old.args and new.budget == old.budget
    for reset, compact in ((True, False), (False, True), (True, True)):
        variant = replace(job, reset=reset, compact=compact).instantiate(None)
        assert variant.args == new.args and variant.budget == new.budget
        assert variant.policy_args["reset"] == reset
        assert variant.policy_args["compact"] == compact


@pytest.mark.parametrize(
    "stage", ["test", "testX", "challenge", "../test", "trainX"]
)
def test_closed_partitions_fail_before_io(
    stage: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_: object) -> None:
        raise AssertionError("No I/O before rejecting scope")

    monkeypatch.setattr(Path, "read_text", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError):
        c.partition(stage)
    with pytest.raises(ValueError):
        c.Config("pilot", stage, False, False, False, "any", 0)
    for action in (c.configs, c.launch, c.run_batch):
        with pytest.raises(ValueError):
            action(stage)


def test_entire_matched_block_must_fit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = [
        c.Config("final00", "validation", a, r, p, n, s)
        for n in ("one", "two")
        for s in (0, 1)
        for a in (False, True)
        for r in (False, True)
        for p in (False, True)
    ]
    account: dict[str, Any] = dict(
        unresolved=[],
        billing_issues=[],
        costs={"validation__old": 13.8},
        ledger=dict(liability=13.8, allocations=dict(benchmark=17)),
    )

    def registered(_: str) -> list[c.Config]:
        return jobs

    def pending(_: Path) -> str:
        return "pending"

    monkeypatch.setattr(c, "configs", registered)
    monkeypatch.setattr(c, "accounting", lambda: account)
    monkeypatch.setattr(c.ol, "ground_truth", pending)
    assert c.admission("final00")
    account["costs"]["validation__old"] += 0.01
    assert not c.admission("final00")
    account["unresolved"] = ["unknown charge"]
    with pytest.raises(ValueError, match="billing"):
        c.admission("final00")


def test_new_ceiling_is_hard_and_stage_transfer_is_accounted(
    tmp_path: Path,
) -> None:
    ledger = Ledger(tmp_path / "ledger.sqlite3")
    ledger.create(c.CEILING, dict(pilot=3, benchmark=17))
    receipt = ledger.reserve("pilot", "gpt-5.6-luna", 0.4)
    ledger.settle(receipt, 0.4, {})
    ledger.transfer("pilot", "benchmark", 2.6, "Unused pilot allocation")
    receipt = ledger.reserve("benchmark", "gpt-5.6-luna", 19.6)
    ledger.settle(receipt, 19.6, {})
    with pytest.raises(CampaignExhausted):
        ledger.reserve("benchmark", "gpt-5.6-luna", 0.0001)


@pytest.mark.parametrize("arm", ["agentic", "ace"])
def test_both_switches_off_exactly_replays_paid_baseline(arm: str) -> None:
    theorem = next(iter(reference.partition()))
    job = reference.Config("validation", arm, theorem, 0)
    original = reference.cell_result(job)
    assert original is not None
    reference.activate(events=False)
    args = job.instantiate(None)
    args.policy = "refined_economy_policy"
    args.policy_args.pop("split_session")
    args.policy_args.pop("dollar_cap")
    args.policy_args.update(reset=False, compact=False)
    args.cache_mode = "replay"
    args.cache_file = str(reference.directory(job) / "cache.yaml")
    args.export_raw_trace = args.export_browsable_trace = args.export_log = (
        False
    )
    with (
        patch.object(
            CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("Offline replay forbids HTTP"),
        ),
        redirect_stdout(io.StringIO()),
    ):
        out = run_command(
            run_strategy,
            args,
            ctx=replace(c.context(), cache_root=Path("/")),
            add_header=False,
        )
    assert out.result is not None
    assert out.result.success == original["success"]
    assert out.result.spent_budget == original["spent_budget"]
    assert (
        json.loads(json.dumps(list(out.result.values))) == original["values"]
    )
