"""HTTP-forbidden campaign integration; run apart from older scope guards."""

# ruff: noqa: E402
from runtime.ace_revision_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict
import gzip
import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.tasks import run_command
from delphyne.utils.typing import pydantic_load
import pytest
import yaml

from ace.role_contracts import TrainingEvent
from ace.role_revision import (
    LocalRepair,
    NoveltyVerdict,
    ReflectionFinish,
    WriterProduct,
)
from ace.terminal_evidence import TerminalEvidence
from experiments import ace_revision_experiment as c
from prove_ace_role_revision import (
    JudgeBookEdit,
    ProposeBookEdits,
    ReflectLocalRepairs,
    reflect_local_repairs,
    write_reviewed_book_edits,
)
from prove_grounded import grounded_search
from runtime.campaign_budget import CampaignResponsesModel
from tools.reports.ace_revision_results import paired


def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(c, "CAMPAIGN", tmp_path / "campaign")
    monkeypatch.setattr(c, "OUTPUT", tmp_path / "output")
    monkeypatch.setattr(c, "verify", lambda: None)
    c.prepare()


def fixture() -> dict[str, Any]:
    return json.loads((c.PRIOR / "platform_v2/demonstration.json").read_text())


def test_complete_campaign_handoffs_freeze_and_paired_panels(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    isolated(tmp_path, monkeypatch)
    product = pydantic_load(WriterProduct, fixture()["curator"])
    good = product.receipts[0].snippet
    assert product.plan is not None
    plan = product.plan
    observed: list[c.Config] = []

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        if isinstance(q, ReflectLocalRepairs):
            if q.spec.theorem_name == "amc12_2000_p1" and not q.submitted:
                repair = LocalRepair(
                    "e11",
                    "Reverse the helper disequality premise",
                    "Use equality symmetry",
                    "Him is the reversed premise",
                    good,
                )
                yield dp.Answer(
                    None,
                    "",
                    tool_calls=(
                        dp.ToolCall(
                            "SubmitLocalRepair", dict(repair=asdict(repair))
                        ),
                    ),
                )
                return
            answer = ReflectionFinish(
                "done" if q.submitted else "abstain",
                "Scripted preflight disposition",
            )
        elif isinstance(q, ProposeBookEdits):
            if not q.receipts:
                assert len(q.contexts) == 1, (
                    "Unused event contexts must not inflate writer prompts"
                )
                yield dp.Answer(
                    None,
                    "",
                    tool_calls=(
                        dp.ToolCall(
                            "CheckAdviceSnippet",
                            dict(context="c1", snippet=good),
                        ),
                    ),
                )
                return
            answer = plan
        else:
            assert isinstance(q, JudgeBookEdit)
            answer = NoveltyVerdict(
                "new_operation", q.target, "Scripted distinct helper operation"
            )
        yield dp.Answer(None, dp.Structured(asdict(answer)))

    policy = (
        grounded_search() @ dp.elim_messages(show_in_log=False)
    ) & fixed_oracle(oracle)

    def launch(key: str, jobs: list[c.Config]) -> None:
        c.save(f"manifests/{key}.json", [asdict(j) for j in jobs])
        for cfg in jobs:
            observed.append(cfg)
            cfg.instantiate(None)
            args = c.read(cfg.input_file)
            if cfg.role == "reflector":
                strategy = reflect_local_repairs(
                    args["problem_file"],
                    args["playbook"],
                    args["trajectory"],
                    pydantic_load(TerminalEvidence, args["terminal"]),
                    tuple(
                        pydantic_load(TrainingEvent, e) for e in args["events"]
                    ),
                )
                values, spent = strategy.run_toplevel(
                    c.context().policy_env(), policy
                ).collect()
                raw: dict[str, Any] = dict(
                    success=bool(values),
                    values=[asdict(v.tracked.value) for v in values],
                    spent_budget=dict(spent.values),
                )
            elif cfg.role != "proof":
                q = pydantic_load(ProposeBookEdits, args)
                strategy = write_reviewed_book_edits(
                    q.role,
                    q.book,
                    q.evidence,
                    q.contexts,
                    q.drafts,
                    q.receipts,
                )
                values, spent = strategy.run_toplevel(
                    c.context().policy_env(), policy
                ).collect()
                raw = dict(
                    success=bool(values),
                    values=[asdict(v.tracked.value) for v in values],
                    spent_budget=dict(spent.values),
                )
            else:
                # Synthetic proof outcomes exercise panel accounting only.
                # They live under pytest's temporary directory, never a run.
                raw = dict(success=True, values=[], spent_budget={})
                folder = c.CAMPAIGN / "transport" / c.name(cfg, None)
                folder.mkdir(parents=True, exist_ok=True)
                (folder / "offline.json.gz").write_bytes(
                    gzip.compress(
                        json.dumps(
                            dict(
                                request=dict(
                                    chat=[dict(content=args["playbook"])]
                                )
                            )
                        ).encode()
                    )
                )
            folder = c.directory(cfg)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "result.yaml").write_text(
                yaml.safe_dump(dict(outcome=dict(result=raw)))
            )
        c.save(f"batches/{key}.json", dict(offline=True, jobs=len(jobs)))

    monkeypatch.setattr(c, "launch", launch)
    with patch.object(
        CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("Preflight forbids HTTP"),
    ):
        c.adaptation()
        c.audit()
        frozen = c.sha(c.CAMPAIGN / "book.yaml")
        c.proofs("training")
        c.report()
        c.proofs("validation")
        c.report()
    assert c.sha(c.CAMPAIGN / "book.yaml") == frozen
    assert c.accounting()["receipts"] == 0
    assert len([j for j in observed if j.stage == "training"]) == 80
    assert len([j for j in observed if j.stage == "validation"]) == 160
    assert c.read("audit.json")["passed"]
    assert c.read("book.json")["entries"] == 27
    assert c.read("training_exposure.json")["new_book_dispatched"]
    for stage in ("training", "validation"):
        jobs = [j for j in observed if j.stage == stage]
        metrics = paired(stage, jobs, c.accounting())
        assert (
            metrics["complete"] and metrics["control_type"] == "fresh paired"
        )
        assert metrics["cells"] == (40 if stage == "training" else 80)
        for name in {j.bench_name for j in jobs}:
            arms = [
                c.read(j.input_file)
                for j in jobs
                if j.bench_name == name and j.seed == 0
            ]
            assert arms[0].pop("playbook") != arms[1].pop("playbook")
            assert arms[0] == arms[1]


def test_missing_seed_and_administrative_censoring_forbid_verdict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    isolated(tmp_path, monkeypatch)

    def partition(_: str) -> dict[str, str]:
        return {"example": "unused"}

    monkeypatch.setattr(c, "partition", partition)
    monkeypatch.setattr(c, "family_map", lambda: {"example": "example"})
    jobs = [
        c.Config("validation", arm, "proof", "example", "", "")
        for arm in ("control", "candidate")
    ]
    with patch.object(c, "cell_result", return_value=dict(success=True)):
        assert not paired("validation", jobs, dict(costs={}))["complete"]
    folder = c.directory(jobs[0])
    folder.mkdir(parents=True)
    (folder / "result.yaml").write_text(
        yaml.safe_dump(dict(outcome=dict(diagnostics="CampaignPaused")))
    )
    with pytest.raises(ValueError, match="Administrative censoring"):
        c.cell_result(jobs[0])


def test_current_authorization_starts_at_zero_and_preserves_prior_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prior_hash = c.sha(c.PRIOR / "interruption.json")
    isolated(tmp_path, monkeypatch)
    a = c.accounting()
    assert (
        a["total"] == 0 and a["receipts"] == 0 and a["ledger"]["ceiling"] == 40
    )
    assert sum(c.ALLOCATIONS.values()) == 40
    assert (
        c.read("authorization.json")["prior_accounting"]["maximum_accounted"]
        > 4
    )
    assert c.sha(c.PRIOR / "interruption.json") == prior_hash


def test_proof_pause_adapter_preserves_flagship_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    isolated(tmp_path, monkeypatch)
    monkeypatch.setenv(
        "OMPHALOS_CAMPAIGN_LEDGER", str(c.CAMPAIGN / "ledger.sqlite3")
    )
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_STAGE", "training")
    monkeypatch.setenv("OPENAI_API_KEY", "offline")
    monkeypatch.delenv("OMPHALOS_ADMISSION_EVENTS", raising=False)
    theorem = next(iter(c.partition("training")))
    cfg = c.make_config(
        "training",
        "control",
        "proof",
        theorem,
        c.proof_args(theorem, "training", "control"),
    )
    calls: list[LLMRequest] = []

    def dispatch(model: CampaignResponsesModel, req: LLMRequest) -> Any:
        calls.append(req)
        raise RuntimeError("Stop after capturing the first request; no HTTP")

    with patch.object(
        CampaignResponsesModel,
        "_send_final_request",
        autospec=True,
        side_effect=dispatch,
    ):
        for policy in ("completion_policy", "revision_proof_policy"):
            args = cfg.instantiate(None)
            args.policy = policy
            args.policy_args = (
                dict(arm="reference", snapshot_directory=str(tmp_path / "old"))
                if policy == "completion_policy"
                else dict(
                    snapshot_directory=str(tmp_path / "new"),
                    pause_file=str(tmp_path / "PAUSED"),
                )
            )
            args.export_raw_trace = args.export_browsable_trace = (
                args.export_log
            ) = False
            with pytest.raises(RuntimeError, match="Stop after capturing"):
                run_command(
                    run_strategy, args, ctx=c.context(), add_header=False
                )
    assert len(calls) == 2 and calls[0] == calls[1]
    assert c.accounting()["receipts"] == 0


def test_closed_and_interrupted_data_are_inaccessible() -> None:
    for path in (
        c.ROOT / "benchmarks/testX.txt",
        c.ROOT / "experiments/output/ace_roles_20260913/validation/anything",
        c.PRIOR / "reports/160.json",
    ):
        with pytest.raises(PermissionError):
            path.read_text()
