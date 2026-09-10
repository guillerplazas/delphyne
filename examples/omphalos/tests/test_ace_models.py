"""Model-suite attribution, monetary gates and immutable-input regressions."""

from dataclasses import asdict, replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from ace.ace_playbook import Playbook
from experiments.ace.ace_adaptation import VARIANTS
from experiments.ace.ace_bounded_experiment import BoundedConfig, INCUMBENT
from experiments.ace.ace_models_roles import call_config, make_step, proposals
from experiments.common import ace_model_campaign as cm
from tools.analysis.paired_evaluation import Observation


def test_panels_cover_families_and_mix() -> None:
    problems = dict(cm.mf.load_partition("benchmarks/trainX.txt"))
    panels = cm.choose_panels(problems)
    assert panels == cm.choose_panels(problems)
    assert [len(v) for v in panels.values()] == [8, 8, 24]
    assert len({b for p in panels.values() for b in p}) == 40
    fs = cm.families(problems)
    seen: set[str] = set()
    for panel in panels.values():
        families = {fs[n] for n in panel}
        assert not seen & families
        seen.update(families)
        assert (
            sum(n.startswith(("imo_", "aime_", "amc")) for n in panel)
            == len(panel) // 2
        )


def test_role_routing_and_backward_defaults() -> None:
    old = VARIANTS["x3-strong"]
    separate = replace(old, auditor_model=cm.LUNA, auditor_effort="xhigh")
    assert separate.role_model("curator") == cm.TERRA
    assert separate.role_model("reducer") == cm.TERRA
    assert separate.role_model("auditor") == cm.LUNA
    assert separate.role_effort("auditor") == "xhigh"
    assert old.role_model("auditor") == cm.TERRA
    recipe = cm.Recipe(curator=cm.RoleModel(cm.TERRA, "low"))
    assert recipe.model_for("reducer") == recipe.curator
    with pytest.raises(ValueError, match="off"):
        recipe.model_for("auditor")
    with pytest.raises(ValueError, match="Terra max"):
        cm.RoleModel(cm.TERRA, "max")


def test_rendered_role_arguments_change_only_model_effort() -> None:
    book = str(INCUMBENT.relative_to(cm.ROOT))
    baseline = make_step(
        "auditor",
        cm.RoleModel(),
        book,
        "final",
        evidence="fixed evidence",
        provenance="fixed provenance",
    )
    for model in (cm.LUNA, cm.TERRA):
        for effort in cm.EFFORTS:
            changed = replace(
                baseline, model_name=model, reasoning_effort=effort
            )
            a, b = call_config(baseline, []), call_config(changed, [])
            assert a.strategy_args == b.strategy_args
            assert a.dependencies == b.dependencies
            assert b.policy_args["model_name"] == model
            assert b.policy_args["reasoning_effort"] == effort
            assert asdict(changed.instantiate(None))["args"] == a.strategy_args


def test_explicit_incumbent_is_prompt_neutral() -> None:
    artifact = "experiments/campaigns/ace_bounded_20260908/artifact_v2.json"
    bench, (file, _) = next(
        iter(cm.mf.load_partition("benchmarks/trainX.txt").items())
    )
    base = BoundedConfig(
        bench_name=bench,
        problem_file=file,
        model_name=cm.LUNA,
        temperature=None,
        toolset="core",
        seed=0,
        artifact=artifact,
        artifact_sha256=cm.digest(cm.ROOT / artifact),
        num_requests=64,
        money=True,
        focused=True,
        admission=False,
        restart=False,
    )
    explicit = replace(
        base,
        playbook_file=str(INCUMBENT.relative_to(cm.ROOT)),
        playbook_sha256=Playbook.load(INCUMBENT).sha256(),
    )
    assert asdict(base.instantiate(None)) == asdict(explicit.instantiate(None))
    with pytest.raises(ValueError, match="changed"):
        replace(explicit, playbook_sha256="wrong").instantiate(None)


def test_gates_include_failures_and_both_cost_constraints() -> None:
    control = cm.metrics(
        {
            ("a", "0"): Observation(True, 0.02),
            ("b", "0"): Observation(False, 0.03),
        }
    )
    gain = cm.metrics(
        {
            ("a", "0"): Observation(True, 0.02),
            ("b", "0"): Observation(True, 0.04),
        }
    )
    assert cm.eligible(gain, control, gain=1)
    assert not cm.eligible(dict(gain, cost=0.061), control, gain=1)
    assert not cm.eligible(dict(control, cost=0.055), control)
    assert cm.metrics({("a", "0"): Observation(True, 0.101)})["solves"] == 0
    assert (
        cm.metrics({("a", "0"): Observation(True, 0.01, True)})["solves"] == 0
    )
    with pytest.raises(ValueError, match="complete panel"):
        cm.eligible(dict(gain, cells=1), control)


def test_hashes_refuse_mutation(tmp_path: Path) -> None:
    file = tmp_path / "input.txt"
    file.write_text("frozen")
    expected = {"input.txt": cm.digest(file)}
    with patch.object(cm, "ROOT", tmp_path):
        cm.verify_hashes(expected)
        file.write_text("changed")
        with pytest.raises(ValueError, match="drift"):
            cm.verify_hashes(expected)


def test_config_identity_includes_effort_and_upstream() -> None:
    book = str(INCUMBENT.relative_to(cm.ROOT))
    step = make_step("auditor", cm.RoleModel(), book, "final")
    c = call_config(step, [])
    assert cm.role_name(c, None) != cm.role_name(
        replace(c, reasoning_effort="high"), None
    )
    assert cm.role_name(c, None) != cm.role_name(
        replace(c, strategy_args={"evidence": "new"}), None
    )
    assert proposals([]) == "(no proposals)"


def test_benchmark_locked_and_controls_checked() -> None:
    train = dict(cm.mf.load_partition("benchmarks/trainX.txt"))
    bench = next(iter(train))
    reg: dict[str, Any] = dict(
        train=list(train),
        validation=[],
        panels=dict(source=[bench], screen=[], selection=[]),
    )
    c = cm.ModelProofConfig(
        bench_name=bench,
        problem_file=train[bench][0],
        model_name=cm.LUNA,
        temperature=None,
        toolset="core",
        seed=0,
        phase="prover",
        num_requests=64,
        max_dollar_budget=0.10,
        reasoning_effort="medium",
        admission=False,
        restart=False,
        money=True,
        focused=True,
    )
    with patch.object(cm, "read", return_value=reg):
        cm.validate_proof(c)
        with pytest.raises(ValueError, match="controls"):
            cm.validate_proof(replace(c, model_name=cm.TERRA))
        with pytest.raises(ValueError, match="replicate"):
            cm.validate_proof(replace(c, seed=2))
        with pytest.raises(ValueError, match="panel"):
            cm.validate_proof(replace(c, phase="validation"))


def test_embedding_receipts_reconcile(tmp_path: Path) -> None:
    with patch.object(cm, "CAMPAIGN", tmp_path):
        ledger = cm.Ledger(tmp_path / "ledger.sqlite3")
        ledger.create(30, cm.ALLOCATIONS)
        key = ledger.reserve(
            "adaptation", "text-embedding-3-small", 0.01, "embedding-test"
        )
        ledger.settle(key, 100 * 0.02e-6, {"total_tokens": 100})
        result = cm.accounting()
        assert result["unresolved"] == []
        assert abs(result["costs"]["embedding-test"] - 0.000002) < 1e-12


def test_independent_role_screens_share_one_batch() -> None:
    from experiments.ace import ace_models_experiment as driver

    panel = [f"case{i}" for i in range(8)]
    batches: list[list[cm.ModelProofConfig]] = []

    def artifact(recipe: cm.Recipe, **_: Any) -> dict[str, Any]:
        return dict(
            playbook=recipe.key(), recipe=asdict(recipe), role_cells=[]
        )

    def config(
        bench: str, effort: Any, book: str, phase: str
    ) -> cm.ModelProofConfig:
        return cm.ModelProofConfig(
            bench_name=bench,
            model_name=cm.LUNA,
            seed=0,
            temperature=None,
            toolset="core",
            phase=phase,
            reasoning_effort=effort,
            arm_label=book,
            playbook_file=book,
            num_requests=64,
        )

    def evaluate(c: dict[str, Any], *_: Any, **__: Any) -> dict[str, Any]:
        return dict(
            c,
            metrics=dict(
                cells=8,
                cost=0.1,
                solves=5
                if c["artifact"]["recipe"] == asdict(cm.Recipe())
                else 4,
            ),
        )

    def launched(configs: list[cm.ModelProofConfig], _: str) -> None:
        batches.append(configs)

    def candidate_key(c: dict[str, Any]) -> str:
        return str(c["playbook"])

    with (
        patch.object(cm, "read", return_value={"panels": {"screen": panel}}),
        patch.object(cm, "save"),
        patch.object(cm, "proof_config", side_effect=config),
        patch.object(
            cm,
            "launch",
            side_effect=launched,
        ),
        patch.object(driver, "build", side_effect=artifact),
        patch.object(driver, "evaluate", side_effect=evaluate),
        patch.object(driver, "prep_cost", return_value=0.0),
        patch.object(driver, "key", side_effect=candidate_key),
    ):
        _, selected = driver.role_screen("xhigh")
    assert selected == cm.Recipe()
    assert len(batches) == 1 and len(batches[0]) == 23 * 8
    assert len({cm.proof_name(c, None) for c in batches[0]}) == 184
    assert {c.bench_name for c in batches[0]} == set(panel)
