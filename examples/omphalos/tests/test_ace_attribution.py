"""No paid calls or closed data: attribution registration and isolation."""

from dataclasses import asdict, replace
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest
import delphyne as dp
from delphyne.stdlib.queries import create_prompt
from experiments.ace import ace_attribution_experiment as c
from experiments.common.ace_pools import POOLS
from runtime.model_registry import make_model
from runtime.campaign_budget import CampaignResponsesModel
from runtime.campaign_budget import Ledger
import prove_grounded as pg
import runtime.pytanque_utils as pt


def config(model: str = "luna", ace: bool = False) -> c.ProofConfig:
    theorem = next(iter(c.partition("training")))
    return c.proof("training", model + ("-ace" if ace else "-none"), theorem)


def test_adaptation_import_does_not_open_partitions() -> None:
    code = """
from runtime.development_only import install
install()
import sys
def audit(event,args):
    if event == 'open' and args and isinstance(args[0],str):
        if '/benchmarks/' in args[0] and args[0].endswith(('trainX.txt','validationX.txt','testX.txt')):
            raise AssertionError(args[0])
sys.addaudithook(audit)
from experiments.ace import ace_adaptation
assert 'x3-offline' in ace_adaptation.VARIANTS
"""
    subprocess.run([sys.executable, "-c", code], cwd=c.ROOT, check=True)


def test_membership_does_not_load_closed_pool() -> None:
    assert "testX" in POOLS
    assert "unknown" not in POOLS
    with pytest.raises(PermissionError):
        POOLS["testX"]


def test_trainx_guard_does_not_load_protected_manifest() -> None:
    from tools.data import ace_review_benchmark as review

    with patch.object(
        review, "_protected", side_effect=AssertionError("protected read")
    ):
        review.assert_training_allowed(list(c.partition("training")))
        with pytest.raises(AssertionError, match="protected read"):
            review.assert_training_allowed(["unregistered_theorem"])


def test_source_amendment_keeps_seal_and_detects_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(c, "ROOT", tmp_path)
    monkeypatch.setattr(c, "CAMPAIGN", tmp_path / "campaign")
    source = tmp_path / "source.py"
    source.write_text("original\n")
    original = c.digest(source)
    c.save("seal.json", {"source.py": original})
    source.write_text("amended\n")
    c.save(
        "amendments/01.json",
        dict(
            files={"source.py": dict(before=original, after=c.digest(source))}
        ),
    )
    c.verify()
    assert c.read("seal.json") == {"source.py": original}
    source.write_text("unexpected drift\n")
    with pytest.raises(ValueError, match="Sealed source drift"):
        c.verify()
    update = c.read("amendments/01.json")
    update["files"]["source.py"]["before"] = "false history"
    (c.CAMPAIGN / "amendments/01.json").write_text(json.dumps(update))
    with pytest.raises(AssertionError):
        c.verify()


def test_only_book_differs_within_model() -> None:
    no = config().instantiate(None)
    yes = config(ace=True).instantiate(None)
    assert no.policy == yes.policy
    assert no.policy_args == yes.policy_args
    assert no.budget == yes.budget
    assert no.args == (yes.args | {"playbook": ""})


@pytest.mark.parametrize(
    "query_type",
    [
        pg.ProposeProofScriptGrounded,
        pg.ResolveProofReference,
        pg.ChooseProofBridge,
        pg.ChooseProofStructure,
    ],
)
def test_playbook_and_citation_are_absent_from_control(
    query_type: type[pg.ProposeProofScriptGrounded],
) -> None:
    cfg = config()
    spec = pt.parse_problem(cfg.problem_file, True)
    env = c.context().policy_env()
    q = query_type(spec, {}, playbook="")
    without = create_prompt(q, (), {}, None, env.templates)
    with_book = create_prompt(
        replace(q, playbook="UNIQUE_LEARNED_ADVICE"),
        (),
        {},
        None,
        env.templates,
    )
    assert "UNIQUE_LEARNED_ADVICE" not in str(without)
    assert "name the playbook bullet ids" not in str(without)
    assert "UNIQUE_LEARNED_ADVICE" in str(with_book)
    assert (
        q.advertised_tools() == replace(q, playbook="book").advertised_tools()
    )


def test_terra_resource_scaling_and_admission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "OMPHALOS_CAMPAIGN_LEDGER", str(c.CAMPAIGN / "ledger.sqlite3")
    )
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_STAGE", "terra")
    monkeypatch.setenv("OMPHALOS_ESTIMATE_DOLLARS", "1")
    request = dp.LLMRequest(chat=(), options={})
    estimates: list[float] = []
    for model in (c.LUNA, c.TERRA):
        llm = make_model(
            model,
            api="responses",
            for_tool_calls=True,
            reasoning_effort="medium",
        )
        assert isinstance(llm, CampaignResponsesModel)
        estimates.append(llm.estimate_budget(request)["price"])
    assert abs(estimates[1] - 10 * estimates[0]) < 1e-12
    assert 0.1 < estimates[1] < 1.0
    luna = config().instantiate(None)
    terra = config("terra").instantiate(None)
    assert luna.args == terra.args
    assert terra.budget == dict(price=1.0, num_requests=64, rocq_seconds=300)


def test_registered_count_and_balanced_panels() -> None:
    planned = c.read("planned_proofs.json")
    assert len(planned) + 40 == 312
    assert {r["seed"] for r in planned} == {0}
    identities = [
        (r["partition"], r["arm"], r["theorem"], r["effort"]) for r in planned
    ]
    assert len(set(identities)) == len(identities)
    families = c.family_map()
    for stage in c.STAGES:
        panel = c.panel(stage)
        assert len(panel) == len({families[n] for n in panel}) == 8
        assert sum(n.startswith("mathd_") for n in panel) == 4


def test_terra_training_routes_every_role_without_recipe_drift() -> None:
    v = c.training_variant()
    old = c.adapt.VARIANTS["x3-offline"]
    for role in ("generator", "reflector", "curator", "reducer"):
        assert v.role_model(role) == c.TERRA
        assert v.role_effort(role) == "medium"
    for key in (
        "epochs",
        "shuffle_seed",
        "batch_size",
        "reduce_batch",
        "render_version",
        "curator_contract",
        "dedup",
        "refine_every",
        "prune_harmful",
        "playbook_max_tokens",
        "audit",
    ):
        assert getattr(v, key) == getattr(old, key)
    batches = c.adapt.plan(v, 1, None)
    assert len(batches) == 10
    assert sum(len(b) for b in batches) == 40
    assert [[s.bench for s in b] for b in batches] == [
        [s.bench for s in b] for b in c.adapt.plan(old, 1, None)
    ]


def test_invalid_cells_rejected_before_model_construction() -> None:
    base = config()
    for bad in (
        replace(base, seed=1),
        replace(base, model_name=c.TERRA),
        replace(base, playbook_file=c.BOOK),
        replace(base, reasoning_effort="high"),
        replace(base, problem_file="benchmarks/testX.txt"),
    ):
        with pytest.raises(ValueError):
            bad.instantiate(None)


def test_immutable_manifests(tmp_path: Path) -> None:
    with patch.object(c, "CAMPAIGN", tmp_path):
        c.save("manifest.json", {"n": 40})
        c.save("manifest.json", {"n": 40})
        with pytest.raises(ValueError):
            c.save("manifest.json", {"n": 80})


def test_unknown_billing_blocks_further_work(tmp_path: Path) -> None:
    with patch.object(c, "CAMPAIGN", tmp_path):
        ledger = Ledger(tmp_path / "ledger.sqlite3")
        ledger.create(75, c.ALLOCATIONS)
        receipt = ledger.reserve("luna", c.LUNA, 0.05, "failed-request")
        ledger.settle(receipt, None, {"exception": "APITimeoutError"})
        assert c.accounting()["unresolved"] == [receipt]
        with pytest.raises(ValueError):
            c.transfer_unused("luna", "terra")


def test_completed_stage_transfer_preserves_ceiling(tmp_path: Path) -> None:
    with patch.object(c, "CAMPAIGN", tmp_path):
        ledger = Ledger(tmp_path / "ledger.sqlite3")
        ledger.create(75, c.ALLOCATIONS)
        receipt = ledger.reserve("luna", c.LUNA, 0.05, "rejected-request")
        ledger.settle(receipt, 0.0, {"exception": "RateLimitError"})
        c.transfer_unused("luna", "terra")
        c.transfer_unused("luna", "terra")
        with ledger.connect() as db:
            assert (
                db.execute("SELECT COUNT(*) FROM transfers").fetchone()[0] == 1
            )
            import json

            ceiling, allocations = json.loads(
                db.execute("SELECT config FROM settings").fetchone()[0]
            )
        assert ceiling == sum(allocations.values()) == 75


def test_no_frozen_terra_book_no_ace_benchmark() -> None:
    with patch.object(c, "read", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            config("terra", True)


def test_training_configuration_limits_match_plan() -> None:
    v = c.training_variant()
    step = c.adapt.plan(v, 1, None)[0][0]
    for role in ("generator", "reflector", "curator", "reducer"):
        raw = c.adapt._make_step_config(v, role, step, "a" * 64)  # pyright: ignore[reportPrivateUsage]
        typed = c.TrainingConfig(**asdict(raw))
        assert typed.model_name == c.TERRA
        assert typed.num_requests == (32 if role == "generator" else 3)
        assert typed.max_dollar_budget == (1.0 if role == "generator" else 0.2)


def test_reference_audit_includes_names_inside_long_snippets() -> None:
    from tools.reports.ace_attribution_diagnosis import candidate_references

    names = candidate_references(
        "Use `Nat.div_mod_eq x y`, then `assert (x * / x = 1) "
        "by exact (Rinv_r x Hx)`; finish with `nra`."
    )
    assert names == ["Nat.div_mod_eq", "Rinv_r"]
