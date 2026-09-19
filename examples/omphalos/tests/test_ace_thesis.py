"""Prospective design, spending boundaries and exact context contracts."""

from dataclasses import replace
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.environments import DataManager, TemplatesManager
from delphyne.stdlib.tasks import run_command
from delphyne.utils.typing import pydantic_load
import delphyne as dp
import yaml

from experiments.ace_thesis import campaign as c
from experiments.ace_thesis.artifact import ContextArtifact, Example
from experiments.ace_thesis.design import (
    schedule,
    select,
    training_panel,
    families,
)
from experiments.ace_thesis.verify_results import compilation_source
from ace.ace_playbook import Playbook, Bullet
from ace.ace_grounded import Checked
from ace.rocq_snippets import SnippetContext, SnippetReceipt
from runtime.pytanque_utils import Feedback
from runtime.campaign_budget import CampaignResponsesModel
from experiments.ace_sanitized.scope import partition
from prove_grounded import ProposeProofScriptGrounded
from runtime.pytanque_utils import parse_problem


def fixture() -> ContextArtifact:
    context = SnippetContext(
        "source.v", "theorem", (), "fixture", "hash", "env"
    )
    feedback = Feedback(
        False,
        failing_tactic="Qed.",
        proof_so_far=["intros n."],
        remaining_goals=["n:nat |- n=n"],
    )
    receipt = SnippetReceipt(
        context,
        "intros n.",
        "executed_open",
        Checked(feedback, "incomplete", 0.1, 2, ""),
        0.1,
        2,
    )
    example = Example("rocq-00001", receipt, "∀n:nat, n=n", "fixture")
    return ContextArtifact(
        Playbook(2, [Bullet("rocq-00001", "tactics", "Use intros.")]),
        (example,),
    )


def test_context_bound_examples_are_whole_and_utf8_bounded() -> None:
    a = fixture()
    text = a.rendered()["text"]
    assert "executed_open" in text and "intros n." in text
    assert "∀n:nat" in text and "Remaining obligations" in text
    short = a.rendered(len(text.encode()) - 1)
    assert short["text"] == a.book.render_prompt()
    assert short["omitted"] == [a.examples[0].identifier]
    assert "```" not in short["text"]
    assert a.rendered(len(text.encode()))["included"] == [
        a.examples[0].identifier
    ]


def test_examples_require_evidence_and_valid_unique_rule_bindings() -> None:
    a = fixture()
    for examples in (
        (a.examples[0], a.examples[0]),
        (replace(a.examples[0], rule_id="unknown"),),
        (
            replace(
                a.examples[0],
                receipt=replace(a.examples[0].receipt, status="rejected"),
            ),
        ),
    ):
        with pytest.raises(ValueError):
            replace(a, examples=examples).rendered()
    with pytest.raises(ValueError):
        a.rendered(1)


def test_training_selection_is_prospective_balanced_and_distinct() -> None:
    names = training_panel()
    assert names == training_panel() and len(names) == 12
    assert sum(n.startswith("mathd_") for n in names) == 6
    assert len({families("train")[n] for n in names}) == 12


def test_complete_interleaved_panels_reverse_order_in_replicate_two() -> None:
    names = [f"n{i}" for i in range(40)]
    arms = ["none", "historical", "revised", "ordinary"]
    rows = schedule(names, arms)
    assert len(rows) == len(set(rows)) == 320
    for n in names:
        first = [a for t, s, a in rows if t == n and s == 0]
        second = [a for t, s, a in rows if t == n and s == 1]
        assert first == list(reversed(second))


def test_selection_preserves_pooled_coverage_not_every_replicate() -> None:
    values = dict(
        historical=dict(cells=24, solved=16, cost=1.0, artifact_sha256="a"),
        cheaper=dict(cells=24, solved=16, cost=0.8, artifact_sha256="b"),
        loss=dict(cells=24, solved=15, cost=0.4, artifact_sha256="c"),
    )
    assert select(values, 16) == "cheaper"
    with pytest.raises(ValueError):
        select(values, 17)
    values["cheaper"]["cells"] = 23
    with pytest.raises(ValueError):
        select(values, 16)


def test_full_nominal_panel_must_fit_stage_and_fresh_ceiling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    jobs = [
        c.Job("validation", "ace", "proof", f"n{i}", "inputs/x.json", "hash")
        for i in range(320)
    ]
    account: dict[str, Any] = dict(
        unresolved=[], billing_issues=[], ledger=dict(groups=[], liability=0.0)
    )
    monkeypatch.setattr(c, "accounting", lambda: account)

    def pending(_: object) -> str:
        return "pending"

    monkeypatch.setattr(c.ol, "ground_truth", pending)
    assert c.fits(jobs)
    assert not c.fits(jobs + [jobs[0]])
    account["ledger"]["liability"] = 18.01
    assert not c.fits(jobs)
    assert sum(c.ALLOCATIONS.values()) == 50.0


def test_kernel_compilation_replaces_only_the_source_placeholder() -> None:
    original = "Require Import Arith.\nTheorem demo: 1=1.\nProof.\nAdmitted."
    source = compilation_source(original, "demo", "reflexivity.")
    assert "Print Assumptions demo." in source and "Admitted" not in source
    assert "Proof.\nreflexivity.\nQed." in source
    for proof in (
        "admit.",
        "Admitted.",
        "Axiom evil:False.",
        "Unset Guard Checking.",
    ):
        with pytest.raises(ValueError):
            compilation_source(original, "demo", proof)
    with pytest.raises(ValueError):
        compilation_source(original, "wrong", "reflexivity.")


def test_actual_generator_template_exposes_examples_and_preserves_tools() -> (
    None
):
    templates = TemplatesManager(
        [p for p in (c.ROOT / "prompts").rglob("*") if p.is_dir()],
        DataManager(()),
    )
    query = ProposeProofScriptGrounded(
        parse_problem(partition("train")[training_panel()[0]], True),
        {},
        playbook=fixture().rendered()["text"],
    )
    rendered = templates.prompt(
        query_name=query.query_name(),
        prompt_kind="system",
        template_args=dict(query=query, example=False, params={}, mode=None),
    )
    assert fixture().examples[0].identifier in rendered
    assert "intros n." in rendered and "executed_open" in rendered
    assert [t.tool_name() for t in query.advertised_tools()] == [
        t.tool_name() for t in replace(query, playbook="").advertised_tools()
    ]


@pytest.mark.parametrize("arm", ["agentic", "agentic_coverage"])
def test_new_execution_context_replays_ordinary_and_matched_controls(
    arm: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = (
        c.ROOT / "experiments/output/ace_sanitized_20260917/validation/configs"
    )
    cell = next(
        folder.glob(f"validation__{arm}__proof__mathd_numbertheory_33__seed0")
    )
    raw: dict[str, Any] = yaml.load(
        (cell / "result.yaml").read_text(), Loader=yaml.CSafeLoader
    )
    original = raw["outcome"]["result"]
    args = pydantic_load(dp.RunStrategyArgs, raw["args"])
    args.cache_mode = "replay"
    args.cache_file = str(cell / "cache.yaml")
    args.export_raw_trace = args.export_browsable_trace = args.export_log = (
        False
    )
    c.activate(events=False)
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_STAGE", "validation")
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_CELL", "offline-test")
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
