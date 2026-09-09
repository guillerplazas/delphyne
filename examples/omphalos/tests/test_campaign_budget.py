"""Admission, uncertain charges, cache neutrality, and HTTP payload tests."""


# pyright: strict

import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

from openai.types.responses import ResponseUsage


from runtime.campaign_budget import (
    CampaignExhausted,
    CampaignResponsesModel,
    Ledger,
)  # noqa: E402
from delphyne.stdlib.models import LLMRequest, SystemMessage  # noqa: E402
from runtime.model_registry import make_model, pricing_for  # noqa: E402


def test_ledger() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Ledger(Path(tmp) / "money.sqlite3")
        ledger.create(1, {"test": 1})
        key = ledger.reserve("test", "fake", 0.4)
        ledger.settle(key, 0.01, {})
        key = ledger.reserve("test", "fake", 0.4)
        ledger.settle(key, None, {})
        assert abs(ledger.summary()["liability"] - 0.41) < 1e-9
        try:
            ledger.reserve("test", "fake", 0.6)
        except CampaignExhausted:
            pass
        else:
            raise AssertionError("unknown charges must consume capacity")

        def call(_: int) -> None:
            key = ledger.reserve("test", "fake", 0.1)
            ledger.settle(key, 0.001, {})

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(call, range(40)))
        assert abs(ledger.summary()["liability"] - 0.45) < 1e-9
        try:
            ledger.create(2, {"test": 2})
        except ValueError:
            pass
        else:
            raise AssertionError("allocation cannot silently change")


def test_transport() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "money.sqlite3"
        ledger = Ledger(file)
        ledger.create(1, {"test": 1})
        model = CampaignResponsesModel(
            options={"model": "gpt-5.6-luna", "reasoning_effort": "medium"},
            pricing=pricing_for("gpt-5.6-luna"),
            use_reasoning_cache=True,
            convert_user_feedback_to_tool=True,
            ledger_file=str(file),
            stage="test",
        )
        req = LLMRequest(chat=(SystemMessage("Hello"),), options={})
        usage = ResponseUsage.model_validate(
            dict(
                input_tokens=100,
                output_tokens=20,
                total_tokens=120,
                input_tokens_details={"cached_tokens": 10},
                output_tokens_details={"reasoning_tokens": 12},
            )
        )
        response: Any = SimpleNamespace(
            id="fake", usage=usage, model="gpt-5.6-luna", status="completed"
        )
        client = MagicMock()
        client.__enter__.return_value = client
        client.responses.create.return_value = response
        with patch("openai.OpenAI", return_value=client) as factory:
            with patch.object(
                CampaignResponsesModel,
                "_parse_response",
                return_value=(None, []),
            ):
                result = model.send_request(req, None)
        assert factory.call_args.kwargs["max_retries"] == 0
        assert (
            client.responses.create.call_args.kwargs["max_output_tokens"]
            == 32768
        )
        assert model.reasoning_allowance == 20
        assert result.budget is not None
        assert ledger.summary()["liability"] < 0.001
        with patch.dict(os.environ, {"OMPHALOS_CAMPAIGN_LEDGER": ""}):
            assert not isinstance(
                make_model("gpt-5.6-luna", api="responses"),
                CampaignResponsesModel,
            )


def test_allocation_transfer() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Ledger(Path(tmp) / "money.sqlite3")
        original = {"pilot": 0.5, "reserve": 0.5}
        ledger.create(1, original)
        key = ledger.reserve("reserve", "fake", 0.4)
        try:
            ledger.transfer("reserve", "pilot", 0.2, "retry capacity")
        except CampaignExhausted:
            pass
        else:
            raise AssertionError("cannot move in-flight liability")
        assert ledger.summary()["transfers"] == []
        ledger.settle(key, 0.1, {})
        ledger.transfer("reserve", "pilot", 0.2, "retry capacity")
        # A resumed launch declares the original allocation. It must not
        # reset the audited transfer or be mistaken for changed consent.
        ledger.create(1, original)
        summary = ledger.summary()
        assert summary["allocations"] == {"pilot": 0.7, "reserve": 0.3}
        assert summary["ceiling"] == 1
        assert summary["liability"] == 0.1
        assert len(summary["transfers"]) == 1
        assert summary["transfers"][0]["reason"] == "retry capacity"


def _reserve_process(path: str) -> bool:
    try:
        ledger = Ledger(Path(path))
        key = ledger.reserve("test", "fake", 0.2)
        assert ledger.summary()["liability"] <= 1.0
        ledger.settle(key, 0.025, {})
        return True
    except CampaignExhausted:
        return False


def test_process_admission() -> None:
    # Independent processes reserve and settle against one shared ledger.
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor

    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "ledger.sqlite3")
        ledger = Ledger(Path(path))
        ledger.create(1.0, {"test": 1.0})
        with ProcessPoolExecutor(
            4, mp_context=mp.get_context("spawn")
        ) as pool:
            assert list(pool.map(_reserve_process, [path] * 16)) == [True] * 16
        assert abs(ledger.summary()["liability"] - 0.4) < 1e-9


def test_uncertain_transport() -> None:
    import httpx
    import openai
    from delphyne.stdlib.models import LLMBusyException

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.sqlite3"
        ledger = Ledger(path)
        ledger.create(1, {"test": 1})
        model = CampaignResponsesModel(
            options={"model": "gpt-5.6-luna"},
            pricing=pricing_for("gpt-5.6-luna"),
            use_reasoning_cache=True,
            convert_user_feedback_to_tool=True,
            ledger_file=str(path),
            stage="test",
        )
        client = MagicMock()
        client.__enter__.return_value = client
        client.responses.create.side_effect = openai.APITimeoutError(
            request=httpx.Request("POST", "https://example.invalid/responses")
        )
        with patch("openai.OpenAI", return_value=client):
            try:
                model.send_request(
                    LLMRequest(chat=(SystemMessage("Hello"),), options={}),
                    None,
                )
            except LLMBusyException:
                pass
            else:
                raise AssertionError("timeout must propagate")
        assert client.responses.create.call_count == 1
        summary = ledger.summary()
        assert summary["liability"] > 0
        assert summary["groups"][0]["status"] == "unknown_charge"


def test_embedding_cache() -> None:
    from runtime.campaign_embeddings import embedding_model
    from delphyne.stdlib.embeddings import EmbeddingsCache

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.sqlite3"
        ledger = Ledger(path)
        ledger.create(1, {"test": 1})
        client = MagicMock()
        client.__enter__.return_value = client
        response: Any = SimpleNamespace(
            usage=SimpleNamespace(
                total_tokens=2, to_dict=lambda: {"total_tokens": 2}
            ),
            data=[SimpleNamespace(index=0, embedding=[1.0, 0.0])],
            model="text-embedding-3-small",
        )
        client.embeddings.create.return_value = response
        with (
            patch.dict(
                os.environ,
                {
                    "OMPHALOS_CAMPAIGN_LEDGER": str(path),
                    "OMPHALOS_CAMPAIGN_STAGE": "test",
                },
            ),
            patch("openai.OpenAI", return_value=client),
        ):
            model = embedding_model("text-embedding-3-small")
            cache = EmbeddingsCache({}, "read_write")
            assert len(model.embed(["Hello"], cache)) == 1
            assert len(model.embed(["Hello"], cache)) == 1
        assert client.embeddings.create.call_count == 1
        assert ledger.summary()["liability"] == 2 * 0.02e-6


if __name__ == "__main__":
    test_ledger()
    test_transport()
    test_allocation_transfer()
    test_process_admission()
    test_uncertain_transport()
    test_embedding_cache()
    print("campaign ledger and transport tests passed")
