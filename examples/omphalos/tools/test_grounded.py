"""Meaningful admission, resource, replay and paired-identity regressions."""

import sys
from collections.abc import Iterable
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import ace_grounded as ag  # noqa: E402
import delphyne as dp  # noqa: E402
import pytanque_utils as pt  # noqa: E402
from campaign_budget import CampaignResponsesModel  # noqa: E402
from delphyne.stdlib.models import LLMRequest, SystemMessage  # noqa: E402
from model_registry import pricing_for  # noqa: E402
from prove_grounded import grounded_search  # noqa: E402
import prove_grounded as pg  # noqa: E402
from delphyne.stdlib.mock import fixed_oracle  # noqa: E402
from tool_budget import OperationExhausted, ToolLimits, clip_utf8, operation  # noqa: E402


def test_resource_outcomes() -> None:
    fb = pt.Feedback(
        False, 1, "Qed.", "Attempt to save an incomplete proof", ["goal"]
    )
    assert ag.outcome_of(fb) == "incomplete"
    assert (
        ag.outcome_of(replace(fb, error_message="Stack overflow"))
        == "resource_exhausted"
    )
    assert (
        ag.outcome_of(
            replace(fb, error_message="Rocq transport failure: ConnectionLost")
        )
        == "unknown"
    )
    assert (
        ag.outcome_of(
            replace(
                fb, failing_tactic="apply x.", error_message="Unable to unify"
            )
        )
        == "rejected"
    )
    with operation(ToolLimits(rpc_calls=1)) as op:
        assert op.admit_rpc(100) <= 60
        try:
            op.admit_rpc(1)
        except OperationExhausted:
            pass
        else:
            raise AssertionError("whole-operation RPC allowance not enforced")
    result = clip_utf8("é" * 5000, 512)
    assert len(result.encode()) <= 512 and "truncated" in result
    fb.remaining_goals = ["goal " + str(i) for i in range(100)]
    view = ag.feedback_view(fb, "incomplete", 512)
    assert len(view.encode()) <= 512 and len(fb.remaining_goals) == 100


def test_claim_admission() -> None:
    file = next(
        line
        for line in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if line and not line.startswith("#")
    )
    e = ag.TrainingTransition(
        file,
        Path(file).stem,
        "cell",
        "sha",
        ("intros.",),
        "bad.",
        "unknown",
        ("g",),
        ("lia.",),
    )
    claim = ag.AdviceClaim(
        "a", "reference", "arithmetic", (), e.correction, e, "env"
    )
    before = pt.Feedback(False, 1, "Qed.", "incomplete", ["g"], ["intros."])
    after = pt.Feedback(True, proof_so_far=["intros.", "lia."], finished=True)
    with (
        patch.object(ag, "import_signature", return_value="env"),
        patch.object(pt, "check", side_effect=[before, after]),
    ):
        verdict = ag.validate_claim(claim)
    assert verdict.status == "verified"
    assert not ag.AdaptationState().claims
    successor = ag.AdaptationState().admit((verdict,))
    assert successor.claims == (claim,)
    assert (
        successor.sha256() == ag.AdaptationState().admit((verdict,)).sha256()
    )
    # Valid clause cannot cover an unverified alternative.
    invalid = replace(claim, action=("lia.", "norm_num."))
    assert ag.validate_claim(invalid).status == "rejected"
    with (
        patch.object(ag, "import_signature", return_value="env"),
        patch.object(pt, "check", side_effect=[before, before]),
    ):
        assert ag.validate_claim(claim).status == "rejected"
    with (
        patch.object(ag, "import_signature", return_value="env"),
        patch.object(pt, "check", side_effect=OperationExhausted("deadline")),
    ):
        assert ag.validate_claim(claim).status == "unavailable"
    protected = replace(
        claim, evidence=replace(e, theorem_name="not_a_training_problem")
    )
    try:
        ag.validate_claim(protected)
    except ValueError:
        pass
    else:
        raise AssertionError("training allowlist not enforced")


def test_money_estimate() -> None:
    model = CampaignResponsesModel(
        options={"model": "gpt-5.6-luna", "reasoning_effort": "medium"},
        pricing=pricing_for("gpt-5.6-luna"),
        use_reasoning_cache=True,
        convert_user_feedback_to_tool=True,
        ledger_file="unused",
        stage="unused",
        estimate_dollars=True,
    )
    req = LLMRequest(chat=(SystemMessage("hello"),), options={})
    budget = model.estimate_budget(req)
    assert budget["price"] > 0 and budget[dp.NUM_REQUESTS] == 1
    model.estimate_dollars = False
    assert model.estimate_budget(req)["price"] == 0


@dp.strategy
def _inspect_for_test() -> dp.Strategy[dp.Compute, object, ag.Inspection]:
    return (
        yield from dp.compute(ag.inspect_proof_state)("unused", "unused", "")
    )


def test_compute_admission() -> None:
    env = dp.PolicyEnv(
        object_loader=dp.ObjectLoader.trivial(),
        prompt_dirs=(),
        demonstration_files=(),
        data_dirs=(),
    )
    with patch.object(
        pt, "_open_and_replay", side_effect=AssertionError("not admitted")
    ) as called:
        # No actual Rocq call can start under a zero shared allowance.
        stream = _inspect_for_test().run_toplevel(
            env, grounded_search() & None
        )
        values, _ = stream.collect(budget=dp.BudgetLimit({"rocq_seconds": 0}))
        assert not values and not called.called


def test_one_repair_and_restart_share_budget() -> None:
    file = next(
        line
        for line in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if line and not line.startswith("#")
    )
    queries: list[pg.ProposeProofScriptGrounded] = []

    def oracle(query: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(query, pg.ProposeProofScriptGrounded)
        queries.append(query)
        yield dp.Answer(None, "```rocq\nlia.\n```")

    env = dp.PolicyEnv(
        object_loader=dp.ObjectLoader.trivial(),
        prompt_dirs=(),
        demonstration_files=(),
        data_dirs=(),
    )
    fb = pt.Feedback(False, 0, "lia.", "Cannot find witness", ["|- n = 0"])
    with patch.object(pt, "check", return_value=fb):
        stream = pg.prove_theorem_grounded(file, Path(file).stem).run_toplevel(
            env, grounded_search() & fixed_oracle(oracle)
        )
        values, spent = stream.collect(
            budget=dp.BudgetLimit({dp.NUM_REQUESTS: 64, "rocq_seconds": 300})
        )
    assert not values and spent[dp.NUM_REQUESTS] == 11
    assert len(queries) == 11
    assert "repair only" in queries[5].decision
    assert "prior plan stalled" in queries[6].decision
    assert len(queries[6].prefix) == 1
    assert isinstance(queries[1], pg.ChooseProofBridge)


def test_full_cell_identity() -> None:
    import failure_analysis as fa

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        names = [
            f"same__{arm}__gpt-5.6-luna__seed{seed}"
            for arm, seed in (("a", 0), ("a", 1), ("b", 0))
        ]
        (root / "experiment.yaml").write_text(
            yaml.safe_dump({"configs": {n: {"params": {}} for n in names}})
        )
        for i, name in enumerate(names):
            path = root / "configs" / name
            path.mkdir(parents=True)
            (path / "result.yaml").write_text(
                f"success: {'true' if i == 0 else 'false'}\noutcome: []\nspent_budget: {{}}\n"
            )
            (path / "cache.yaml").write_text("[]")
        result = fa.load_run(root)
        assert {r.config: r.solved_run for r in result} == dict(
            zip(names, (True, False, False))
        )


def test_exploratory_inference() -> None:
    from paired_evaluation import Observation, compare, cost_cluster_p

    cells = [(str(i), "0") for i in range(5)]
    a = {c: Observation(False, 0.08, False) for c in cells}
    b = {c: Observation(True, 0.04, False) for c in cells}
    families = {c[0]: c[0] for c in cells}
    result = compare(a, b, cells, families=families, alpha=0.1, confidence=0.9)
    assert "effect_ci90" in result and "effect_ci95" not in result
    assert result["solved_b"] == 5 and result["cost_ratio"] == 0.5
    assert cost_cluster_p(a, b, cells, families) == 2 / 32
    # Duplicate family members are not five independent observations.
    assert cost_cluster_p(a, b, cells, {c[0]: "same" for c in cells}) == 1


if __name__ == "__main__":
    for name, function in list(globals().items()):
        if name.startswith("test_"):
            function()
            print("ok", name)
