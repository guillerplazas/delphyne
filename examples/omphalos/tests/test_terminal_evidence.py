"""Receipt binding, prompt delivery, and provenance across both ACE roles."""

# ruff: noqa: E402 -- scope before experiment imports
from runtime.completion_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict, replace
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.mock import fixed_oracle
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import pytest
import yaml

from ace.ace_playbook import AddOp
from ace.ace_verified_snippets import SnippetBinding, SnippetWitness
import ace.terminal_evidence as te
from experiments.common.ace_pools import POOLS
from experiments.resource_completion_experiment import ROOT, context
from prove_ace import Reflection, ReflectOnTrajectory
from prove_evidence import (
    BoundCurationDelta,
    CurateCheckedPlaybook,
    ReduceCheckedDeltas,
    ReflectOnTrajectoryV2,
    curate_checked_playbook,
    protect_bound_delta,
    reduce_checked_deltas,
    reflect_on_trajectory_v2,
)
from prove_grounded import grounded_search
from runtime import pytanque_utils as pt
from runtime.tool_budget import ToolLimits


def receipt() -> te.TerminalEvidence:
    return te.extract_terminal_evidence(
        ROOT
        / "experiments/output/ace_adaptation_x3-offline/configs/step33_generator_amc12_2000_p6",
        "amc12_2000_p6",
    )


def test_accepted_terminal_is_distinct_and_reaches_query() -> None:
    r = receipt()
    assert r.status == "accepted" and r.auto_finished
    assert "nia." in r.accepted_script and any(
        "norm_num" in t for t in r.submitted_script
    )
    assert r.sha256() != replace(r, auto_finished=False).sha256()
    answers: list[ReflectOnTrajectoryV2] = []
    reflection = Reflection(
        "received", "none", "automation", "nia", "use checked evidence", []
    )

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, ReflectOnTrajectoryV2)
        answers.append(q)
        yield dp.Answer(
            None, "```yaml\n" + yaml.safe_dump(asdict(reflection)) + "```"
        )

    env = dp.PolicyEnv(object_loader=context().object_loader(extra_objects={}))
    comp = reflect_on_trajectory_v2(
        r.problem_file, "SOLVED", "", "proposed norm_num.", r
    )
    result = comp.run_toplevel(env, dp.dfs() & fixed_oracle(oracle)).collect()
    assert result and answers[0].terminal == r
    jinja = Environment(
        loader=FileSystemLoader([str(p) for p in context().prompt_dirs]),
        undefined=StrictUndefined,
    )
    rendered = jinja.get_template(
        "ReflectOnTrajectoryV2.instance.jinja"
    ).render(query=answers[0])
    assert (
        r.render() in rendered and "outside trajectory truncation" in rendered
    )
    # V2 is additive: the original template and query remain available.
    legacy = ReflectOnTrajectory(
        pt.parse_problem(r.problem_file), "SOLVED", "", "proposed norm_num."
    )
    assert r.render() not in jinja.get_template(
        "ReflectOnTrajectory.instance.jinja"
    ).render(query=legacy)
    with pytest.raises(dp.StrategyException, match="mismatch"):
        reflect_on_trajectory_v2(
            r.problem_file, "SOLVED", "", "", replace(r, theorem_name="wrong")
        ).run_toplevel(env, dp.dfs() & fixed_oracle(oracle)).collect()


def test_receipt_rejects_unbound_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    theorem = "amc12_2000_p6"
    problem, _ = POOLS["trainX"][theorem]
    monkeypatch.setattr(te, "ROOT", tmp_path)
    cell = tmp_path / "cell"
    cell.mkdir()
    result = {"outcome": {"result": {"success": True, "values": ["lia."]}}}
    (cell / "result.yaml").write_text(yaml.safe_dump(result))
    (cell / "cache.yaml").write_text("[]\n")
    with pytest.raises(ValueError, match="no accepted verifier"):
        te.extract_terminal_evidence(cell, theorem)

    call = dict(
        fun="check_assisted",
        args=dict(file=problem, theorem_name=theorem, tactics=["norm_num."]),
    )
    entry = dict(
        input=dict(
            request=dict(
                options=dict(model="__compute__"),
                chat=[dict(content=yaml.safe_dump(call))],
            )
        ),
        output=dict(
            outputs=[
                dict(
                    content=yaml.safe_dump(
                        dict(
                            success=True,
                            proof_so_far=["nia."],
                            auto_finished=True,
                        )
                    )
                )
            ]
        ),
    )
    (cell / "cache.yaml").write_text(yaml.safe_dump([entry]))
    with pytest.raises(ValueError, match="differs"):
        te.extract_terminal_evidence(cell, theorem)


def test_adaptation_config_pins_receipt_without_changing_legacy() -> None:
    from experiments.ace import ace_adaptation as adaptation

    r = receipt()
    trajectory = adaptation.extract_trajectory(
        ROOT / r.source_cell, r.theorem_name
    )
    cfg = adaptation.ACEAdaptStepConfig(
        role="reflector",
        step=0,
        bench_name=r.theorem_name,
        seed=0,
        model_name="gpt-5.6-luna",
        toolset="core",
        reasoning_effort="medium",
        num_requests=1,
        max_dollar_budget=0.1,
        playbook_sha256="unused",
        upstream_sha256=adaptation._sha256(trajectory),  # pyright: ignore[reportPrivateUsage]
        generator_dir=r.source_cell,
        terminal_evidence_version=2,
        terminal_evidence_sha256=r.sha256(),
    )
    with patch.object(
        adaptation.ACEAdaptStepConfig, "_reflector_playbook", return_value=""
    ):
        current = cfg._reflector_args()  # pyright: ignore[reportPrivateUsage]
        assert current.strategy == "reflect_on_trajectory_v2"
        assert current.args["terminal"] == asdict(r)
        with pytest.raises(ValueError, match="drift"):
            replace(cfg, terminal_evidence_sha256="wrong")._reflector_args()  # pyright: ignore[reportPrivateUsage]
        legacy = replace(
            cfg, terminal_evidence_version=0, terminal_evidence_sha256=""
        )
        with patch.object(
            adaptation.ACEAdaptStepConfig,
            "_problem",
            return_value=(r.problem_file, r.theorem_name),
        ):
            old = legacy._reflector_args()  # pyright: ignore[reportPrivateUsage]
        assert old.strategy == "reflect_on_trajectory"
        assert old.args == {
            k: v for k, v in current.args.items() if k != "terminal"
        }


def test_curator_and_reducer_execute_provenance_gate() -> None:
    path = ROOT / "experiments/campaigns/ace_capacity_20260912"
    w = SnippetWitness(
        **json.loads((path / "snippet_witness.json").read_text())
    )
    bad = json.loads((path / "snippet_verification.json").read_text())[
        "candidate"
    ]
    proposed = BoundCurationDelta(
        "preserve evidence",
        (AddOp("ADD", "Rocq", bad),),
        (SnippetBinding(0, bad, w.identifier),),
    )
    kinds: list[str] = []

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, (CurateCheckedPlaybook, ReduceCheckedDeltas))
        kinds.append(type(q).__name__)
        yield dp.Answer(
            None, "```yaml\n" + yaml.safe_dump(asdict(proposed)) + "```"
        )

    env = dp.PolicyEnv(object_loader=context().object_loader(extra_objects={}))
    reflection = Reflection("", "", "", "", "", [])
    policy = grounded_search() & fixed_oracle(oracle)
    curated, _ = (
        curate_checked_playbook("", reflection, (w,))
        .run_toplevel(env, policy)
        .collect()
    )
    assert curated
    reduced, _ = (
        reduce_checked_deltas("", (curated[0].tracked.value,), (w,))
        .run_toplevel(env, policy)
        .collect()
    )
    assert reduced
    assert kinds == ["CurateCheckedPlaybook", "ReduceCheckedDeltas"]
    assert reduced[0].tracked.value.bindings[0].text == w.template
    assert all(
        v.source_check.feedback.success
        for v in reduced[0].tracked.value.verdicts
    )
    with pytest.raises(ValueError, match="provenance"):
        protect_bound_delta(
            replace(proposed, bindings=()), (w,), (w.identifier,), ToolLimits()
        )
    dropped = protect_bound_delta(
        BoundCurationDelta("drop explicitly", (), (), (w.identifier,)),
        (w,),
        (w.identifier,),
        ToolLimits(),
    )
    assert (
        dropped.dropped_sources == (w.identifier,)
        and not dropped.delta.operations
    )
