"""Billing, fixed experimental scope and transport/control equivalence."""

# pyright: reportPrivateUsage=false

from dataclasses import fields
from copy import deepcopy
from datetime import date
from math import isclose
import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from openai.types.responses import Response
from pydantic import TypeAdapter
from delphyne.stdlib.models import LLMRequest, UserMessage
from delphyne.stdlib.openai_api import OpenAIResponsesModel

from experiments.ace_x3_reproduction.accounting import price, reserve
from experiments.ace_x3_reproduction import campaign as c
from experiments.ace_x3_reproduction import diagnostics
from experiments.ace_x3_reproduction.transport import ReproductionModel
from experiments.ace_thesis.design import schedule
from experiments.ace_sanitized.scope import partition
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.campaign_pause import CampaignPaused
from runtime.model_registry import make_model
from runtime.replay_admission import fingerprint
from tools.reports.ace_x3_forensics import raw, HISTORY

DAY = date(2026, 9, 18)


def test_admission_links_yaml_omitted_defaults_to_typed_event(
    tmp_path: Path,
) -> None:
    request = dict(
        chat=[dict(role="user", content="proof")],
        options=dict(model="gpt-5.6-luna", max_completion_tokens=8192),
    )
    adapter = TypeAdapter(LLMRequest)
    key = fingerprint(
        adapter.dump_python(adapter.validate_python(request), mode="json")
    )
    estimate = dict(num_requests=1, price=0.01)
    events = [
        dict(
            kind="estimate_v2",
            cell="cell",
            output_limit=8192,
            shadow_price_32768=0.039,
            estimate=estimate,
            request=key,
        ),
        dict(
            kind="admission_v2",
            cell="cell",
            admitted=True,
            estimate=estimate,
            remaining=dict(price=0.03),
        ),
    ]
    path = tmp_path / "events.jsonl"
    path.write_text("\n".join(json.dumps(e) for e in events))
    entry = dict(
        input=dict(request=request),
        output=dict(budget=dict(values=dict(price=0.002))),
    )
    with patch.object(diagnostics, "raw", return_value=[entry]):
        result = diagnostics.admission_tails(
            path,
            [
                dict(
                    cell="cell",
                    theorem="target",
                    label="arm",
                    path="fixture",
                    solved=False,
                )
            ],
        )
    assert result["affected_cells"] == {"arm": 1}
    assert result["tails"][0]["cached_tail_available"]
    assert result["tails"][0]["tail_requests"] == 1
    assert result["tails"][0]["tail_legacy_cost"] == 0.002


def test_cache_rewrite_excludes_demo_misses_and_tracks_lost_hits() -> None:
    chat: list[dict[str, Any]] = [
        dict(role="user", content="demo"),
        dict(role="assistant", answer=dict(content="demo answer")),
        dict(role="user", content="Theorem target : True."),
    ]
    entries: list[dict[str, Any]] = []
    for index in range(3):
        logs = [
            dict(
                message="reasoning_cache_miss",
                metadata=dict(msg_index_in_chat=1),
            )
        ]
        if index:
            logs.append(
                dict(
                    message="reasoning_cache_"
                    + ("hit" if index == 1 else "miss"),
                    metadata=dict(msg_index_in_chat=3),
                )
            )
        if index == 1:
            chat.extend(
                [
                    dict(role="assistant", answer=dict(content="proof")),
                    dict(role="user", content="checker feedback"),
                ]
            )
        if index == 2:
            chat[2]["content"] += " Last verified prefix: ..."
            chat.append(
                dict(role="user", content="Feedback: Theorem target : True.")
            )
        entries.append(
            dict(
                input=dict(
                    request=dict(
                        chat=deepcopy(chat),
                        tools=[],
                        options=dict(model="gpt-5.6-luna"),
                    )
                ),
                output=dict(usage_info=usage(), log_items=logs),
            )
        )
    with patch.object(diagnostics, "raw", return_value=entries):
        result = diagnostics.input_stability(
            [dict(path="fixture", label="arm", cell="cell", theorem="target")]
        )
    phases = result["categories"]["arm"]
    assert phases["first"]["reasoning_misses"] == 0
    assert phases["append"]["reasoning_hits"] == 1
    assert phases["rewrite"]["reasoning_misses"] == 1
    assert phases["rewrite"]["hits_becoming_misses"] == 1
    assert result["changes"][0]["theorem_message_only"]
    assert result["changes"][0]["changed_messages"] == [2]


def usage(
    inp: int = 1000, cached: int = 300, written: int = 600
) -> dict[str, Any]:
    return dict(
        input_tokens=inp,
        output_tokens=100,
        input_tokens_details=dict(
            cached_tokens=cached, cache_write_tokens=written
        ),
    )


def test_disjoint_categories_and_dated_write_premium() -> None:
    cost = price(usage(), on=DAY, tier="default", regional=False)
    assert cost.ordinary == 100
    assert isclose(cost.corrected, 0.000296)
    assert isclose(cost.corrected - cost.legacy, 0.000030)
    assert isclose(
        price(
            usage(), on=date(2026, 7, 29), tier="default", regional=False
        ).corrected,
        cost.corrected * 5,
    )
    for bad in (
        usage(cached=1001),
        usage(written=-1),
        {"input_tokens": 1000, "output_tokens": 100},
    ):
        with pytest.raises(ValueError):
            price(bad, on=DAY, tier="default", regional=False)
    for model, day, tier in (
        ("unknown", DAY, "default"),
        ("gpt-5.6-luna", date(2026, 7, 8), "default"),
        ("gpt-5.6-luna", DAY, "auto"),
    ):
        with pytest.raises(ValueError):
            price(usage(), model=model, on=day, tier=tier, regional=False)


@pytest.mark.parametrize("inp", [1000, 272000, 272001, 500000])
@pytest.mark.parametrize(
    "tier", ["default", "fast", "priority", "flex", "batch"]
)
def test_reservation_bounds_worst_case(inp: int, tier: str) -> None:
    u = usage(inp, 0, inp)
    u["output_tokens"] = 32768
    cost = price(u, on=DAY, tier=tier, regional=True)
    assert cost.corrected <= reserve(inp, 32768, DAY) + 1e-12


def test_scope_and_counterbalanced_complete_matrix() -> None:
    problems = partition("validation")
    rows = schedule(list(problems), list(c.ARMS))
    assert len(rows) == len(set(rows)) == 320
    for n in problems:
        zero = [a for t, seed, a in rows if t == n and seed == 0]
        one = [a for t, seed, a in rows if t == n and seed == 1]
        assert zero == one[::-1]
    for job in (
        ("other", next(iter(problems)), 0),
        (c.ARMS[0], "unregistered", 0),
        (c.ARMS[0], next(iter(problems)), 2),
    ):
        with pytest.raises(ValueError):
            c.Job(*job)


@pytest.mark.parametrize("cap", [8192, 32768])
def test_transport_preserves_payload_estimate_parser_and_legacy_budget(
    cap: int,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OMPHALOS_CAMPAIGN_LEDGER", raising=False)
    monkeypatch.delenv("OMPHALOS_ADMISSION_EVENTS", raising=False)
    original = make_model(
        "gpt-5.6-luna",
        api="responses",
        for_tool_calls=True,
        reasoning_effort="medium",
        convert_user_feedback_to_tool=True,
    )
    assert isinstance(original, OpenAIResponsesModel)
    values = {
        f.name: getattr(original, f.name) for f in fields(original) if f.init
    }
    models: list[CampaignResponsesModel] = []
    for number, cls in enumerate((CampaignResponsesModel, ReproductionModel)):
        ledger = tmp_path / f"ledger{number}.sqlite3"
        Ledger(ledger).create(1, dict(matrix=1))
        extras: dict[str, Any] = (
            dict(
                evidence_directory=str(tmp_path / "evidence"),
                pause_file=str(tmp_path / "PAUSED"),
            )
            if number
            else {}
        )
        models.append(
            cls(
                **values,
                ledger_file=str(ledger),
                stage="matrix",
                cell="test",
                output_limit=cap,
                estimate_dollars=True,
                **extras,
            )
        )
    folder = c.ROOT / c.old.read(HISTORY)[0]["source_paths_a"][0]
    request = TypeAdapter(LLMRequest).validate_python(
        raw(folder / "cache.yaml")[0]["input"]["request"]
    )
    response = Response.model_validate(
        dict(
            id="resp_fixture",
            created_at=1,
            object="response",
            model="gpt-5.6-luna",
            output=[
                dict(
                    type="message",
                    id="msg_fixture",
                    role="assistant",
                    status="completed",
                    content=[
                        dict(
                            type="output_text",
                            text="reflexivity.",
                            annotations=[],
                            logprobs=[],
                        )
                    ],
                )
            ],
            usage={
                **usage(),
                "total_tokens": 1100,
                "output_tokens_details": {"reasoning_tokens": 0},
            },
            status="completed",
            service_tier="default",
            parallel_tool_calls=True,
            tool_choice="auto",
            tools=[],
        )
    )
    sent: list[dict[str, Any]] = []

    def create(**kwargs: Any) -> Response:
        sent.append(kwargs)
        return response

    client = MagicMock()
    client.__enter__.return_value = client
    client.base_url = "https://api.openai.com/v1/"
    client.responses.create.side_effect = create
    with patch("openai.OpenAI", return_value=client):
        assert models[0].estimate_budget(request) == models[1].estimate_budget(
            request
        )
        results = [
            m._send_final_request(m.add_model_defaults(request))
            for m in models
        ]
        assert results[0] == results[1]
        assert sent[0] == sent[1]
        models[1]._send_final_request(models[1].add_model_defaults(request))
    assert sent[2].pop("extra_body") == {
        "prompt_cache_options": {"comparison_response_id": "resp_fixture"}
    }
    assert sent[2] == sent[1]
    assert isclose(
        Ledger(Path(models[0].ledger_file)).summary()["liability"], 0.000266
    )
    assert isclose(
        Ledger(Path(models[1].ledger_file)).summary()["liability"],
        2 * 0.000296,
    )
    assert len(list((tmp_path / "evidence").glob("*.json.gz"))) == 2


@pytest.mark.parametrize("missing", ["usage", "service_tier"])
def test_unresolved_billing_retains_liability_and_blocks_next_dispatch(
    missing: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OMPHALOS_CAMPAIGN_LEDGER", raising=False)
    monkeypatch.delenv("OMPHALOS_ADMISSION_EVENTS", raising=False)
    original = make_model("gpt-5.6-luna", api="responses", for_tool_calls=True)
    assert isinstance(original, OpenAIResponsesModel)
    values = {
        f.name: getattr(original, f.name) for f in fields(original) if f.init
    }
    ledger = tmp_path / "ledger.sqlite3"
    Ledger(ledger).create(1, dict(matrix=1))
    model = ReproductionModel(
        **values,
        ledger_file=str(ledger),
        stage="matrix",
        cell="one",
        output_limit=8192,
        evidence_directory=str(tmp_path / "raw"),
        pause_file=str(tmp_path / "PAUSED"),
    )
    value: dict[str, Any] = dict(
        id="resp_missing",
        created_at=1,
        object="response",
        model="gpt-5.6-luna",
        output=[],
        usage={
            **usage(),
            "total_tokens": 1100,
            "output_tokens_details": {"reasoning_tokens": 0},
        },
        status="completed",
        service_tier="default",
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
    )
    value[missing] = None
    response = Response.model_validate(value)
    client = MagicMock()
    client.__enter__.return_value = client
    client.base_url = "https://api.openai.com/v1/"
    client.responses.create.return_value = response
    request = model.add_model_defaults(
        LLMRequest(chat=(UserMessage("test"),), options={})
    )
    with patch("openai.OpenAI", return_value=client):
        with pytest.raises(ValueError):
            model._send_final_request(request)
        with pytest.raises(CampaignPaused):
            model._send_final_request(request)
    assert client.responses.create.call_count == 1
    summary = Ledger(ledger).summary()
    assert summary["liability"] > 0
    assert summary["groups"][0]["status"] == "unknown_charge"
    assert (tmp_path / "PAUSED").exists()
    assert len(list((tmp_path / "raw").glob("*.json.gz"))) == 1
