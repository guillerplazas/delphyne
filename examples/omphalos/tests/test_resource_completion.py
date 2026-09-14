"""Isolated policies, hard admission, exposure, and real execution/replay."""

# ruff: noqa: E402 -- guard before experiment imports
from runtime.completion_scope import install

install()

from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.models import (
    LLMOutput,
    LLMRequest,
    LLMResponse,
    SystemMessage,
)
from delphyne.stdlib.tasks import run_command
from openai.types.responses import ResponseUsage
import pytest

from experiments import resource_completion_experiment as c
from prove_resource_completion import CompletionResponsesModel
from runtime.campaign_budget import CampaignExhausted, Ledger
from runtime.model_registry import pricing_for


def model(path: Path, cap: int = 4096) -> CompletionResponsesModel:
    return CompletionResponsesModel(
        options={"model": "gpt-5.6-luna", "reasoning_effort": "medium"},
        pricing=pricing_for("gpt-5.6-luna"),
        ledger_file=str(path),
        stage="test",
        estimate_dollars=True,
        output_limit=cap,
        use_reasoning_cache=True,
        convert_user_feedback_to_tool=True,
    )


def test_output_bound_matches_reserved_http_payload(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.sqlite3")
    ledger.create(1, {"test": 1})
    m = model(ledger.path)
    req = LLMRequest(chat=(SystemMessage("hello"),), options={})
    old = model(ledger.path, 32768)
    assert (
        abs(
            old.estimate_budget(req)["price"]
            - m.estimate_budget(req)["price"]
            - 0.0344064
        )
        < 1e-10
    )
    usage = ResponseUsage.model_validate(
        dict(
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            input_tokens_details={"cached_tokens": 0},
            output_tokens_details={"reasoning_tokens": 0},
        )
    )
    response: Any = SimpleNamespace(
        id="offline", usage=usage, model="gpt-5.6-luna", status="completed"
    )
    client = MagicMock()
    client.__enter__.return_value = client
    client.responses.create.return_value = response
    with (
        patch("openai.OpenAI", return_value=client) as factory,
        patch.object(
            CompletionResponsesModel,
            "_parse_response",
            return_value=(None, []),
        ),
    ):
        m.send_request(req, None)
    assert factory.call_args.kwargs["max_retries"] == 0
    assert (
        client.responses.create.call_args.kwargs["max_output_tokens"] == 4096
    )
    with ledger.connect() as db:
        reserved, charged = db.execute(
            "SELECT reserved,charged FROM receipts"
        ).fetchone()
    assert (
        abs(
            reserved
            - m.estimate_budget(req)["price"]
            + 20 * pricing_for("gpt-5.6-luna").dollars_per_input_token
        )
        < 1e-12
    )
    assert charged < reserved
    key = ledger.reserve("test", "fake", 0.1)
    ledger.settle(key, None, {})
    with (
        patch("openai.OpenAI", side_effect=AssertionError("HTTP")),
        pytest.raises(CampaignExhausted),
    ):
        m.send_request(req, None)


def test_registered_isolation_and_attainable_gates() -> None:
    assert sum(c.ALLOCATIONS.values()) == 30
    for stage in ("training", "validation"):
        a, b = (c.batch_configs(f"{stage}_{arm}") for arm in c.ARMS)
        assert len(a) == len(b) == 40
        for x, y in zip(a, b, strict=True):
            xa, ya = x.instantiate(None), y.instantiate(None)
            assert xa.args | {"continuation": True} == ya.args
            assert (
                xa.budget
                == ya.budget
                == dict(price=0.1, num_requests=64, rocq_seconds=300)
            )
    assert c.practical(
        dict(complete=True, solved_a=27, solved_b=28, cost_ratio=1.25)
    )
    assert c.practical(
        dict(complete=True, solved_a=27, solved_b=26, cost_ratio=0.90)
    )
    assert not c.practical(
        dict(complete=True, solved_a=27, solved_b=25, cost_ratio=0.5)
    )
    assert not c.practical(dict(complete=False))
    with pytest.raises(ValueError):
        c.ProofConfig("closed", "test", "A").instantiate(None)


def test_exposure_requires_dispatch_and_executed_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(c, "CAMPAIGN", tmp_path)
    rows = [
        dict(
            kind="estimate_v2",
            decision="estimated",
            structured=True,
            shadow_price_32768=0.07,
        ),
        dict(
            kind="admission_v2",
            decision="admitted",
            admitted=True,
            remaining={"price": 0.05},
        ),
    ]
    path = tmp_path / "events.jsonl"

    def write() -> None:
        path.write_text(
            "\n".join(json.dumps(r | {"cell": "cell"}) for r in rows)
        )

    write()
    assert not c.exposure("cell")["A"] and not c.exposure("cell")["B"]
    rows.append(
        dict(kind="model", decision="invoked", receipt="r", output_limit=4096)
    )
    write()
    assert not c.exposure("cell")["A"]
    rows.append(
        dict(kind="compute", decision="invoked", function="checked_proof")
    )
    write()
    assert c.exposure("cell")["A"] and c.exposure("cell")["B"]


def test_real_structured_continuation_and_exact_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_LEDGER", str(tmp_path / "unused"))
    monkeypatch.setenv("OPENAI_API_KEY", "offline")
    monkeypatch.setenv("OMPHALOS_CAMPAIGN_STAGE", "training")
    monkeypatch.delenv("OMPHALOS_ADMISSION_EVENTS", raising=False)
    args = c.ProofConfig("mathd_numbertheory_48", "training", "B").instantiate(
        None
    )
    args.policy_args["snapshot_directory"] = str(tmp_path / "transport")
    args.cache_file = str(tmp_path / "cache.yaml")
    args.cache_mode = "create"
    args.export_raw_trace = args.export_browsable_trace = args.export_log = (
        False
    )
    ctx = replace(c.context(), cache_root=Path("/"))
    calls: list[LLMRequest] = []

    def answer(m: CompletionResponsesModel, req: LLMRequest) -> LLMResponse:
        calls.append(req)
        content = (
            dp.Structured(dict(mode="suffix", script="simpl in Heq."))
            if req.structured_output
            else "```rocq\nintros b Hb Heq.\n```"
        )
        m.reasoning_allowance += 100
        return LLMResponse(
            [LLMOutput(content)],
            dp.Budget(
                dict(
                    price=0.001,
                    output_tokens=100,
                    num_requests=1,
                    num_completions=1,
                )
            ),
            [],
            "gpt-5.6-luna",
            {},
        )

    with patch.object(
        CompletionResponsesModel,
        "_send_final_request",
        autospec=True,
        side_effect=answer,
    ):
        live = run_command(run_strategy, args, ctx=ctx, add_header=False)
    assert live.result is not None and live.result.success, live.diagnostics
    assert len(calls) == 2 and calls[1].structured_output is not None
    assert "nia." in str(live.result.values[0])
    args.cache_mode = "replay"
    with patch.object(
        CompletionResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("HTTP forbidden"),
    ):
        replay = run_command(run_strategy, args, ctx=ctx, add_header=False)
    assert replay.result is not None and replay.result.success, (
        replay.diagnostics
    )
    assert replay.result.spent_budget == live.result.spent_budget


def test_lazy_import_cannot_open_partitions() -> None:
    import importlib
    import experiments.common.miniF2F_bench as mf

    with patch.object(
        Path, "read_text", side_effect=AssertionError("eager read")
    ):
        importlib.reload(mf)
    with patch.object(
        mf,
        "load_partition",
        return_value={"synthetic": ("fixture", "synthetic")},
    ) as load:
        assert mf.TRAIN_PROBLEMS["synthetic"] == ("fixture", "synthetic")
        assert len(mf.TRAIN_PROBLEMS) == 1
        load.assert_called_once_with("benchmarks/train.txt")
