"""No-HTTP tests for temporary-rate handling without replacing answers."""

from pathlib import Path
import tempfile
from types import SimpleNamespace
from typing import Any, cast
import unittest
from unittest.mock import call, patch

from delphyne.stdlib.models import LLMRequest, LLMResponse
import httpx
import openai

from . import rate_recovery as r


def rejection(
    code: str = "rate_limit_exceeded",
    *,
    headers: dict[str, str] | None = None,
    requested: int = 10000,
) -> openai.RateLimitError:
    message = (
        "Rate limit reached for gpt-5.6-luna on tokens per min (TPM): "
        f"Limit 500000, Used 500000, Requested {requested}. "
        "Please try again in 1200ms."
    )
    return openai.RateLimitError(
        message,
        response=httpx.Response(
            429,
            headers=headers,
            request=httpx.Request(
                "POST", "https://api.openai.com/v1/responses"
            ),
        ),
        body=dict(code=code, type="tokens", message=message),
    )


class RateRecoveryTests(unittest.TestCase):
    def test_server_minimum_and_invalid_header_fallback(self) -> None:
        with patch.object(r.random, "uniform", return_value=0.25):
            self.assertEqual(
                r.retry_delay(rejection(headers={"retry-after": "47"}), 0),
                47.25,
            )
            self.assertEqual(
                r.retry_delay(
                    rejection(headers={"retry-after-ms": "47000"}), 0
                ),
                47.25,
            )
            self.assertEqual(
                r.retry_delay(
                    rejection(headers={"retry-after": "invalid"}), 0
                ),
                5.25,
            )

    def test_billing_and_oversized_requests_are_not_retried(self) -> None:
        for error in (
            rejection("credit_balance_exhausted"),
            rejection(requested=500001),
        ):
            with self.assertRaises(openai.RateLimitError):
                r.retry_delay(error, 0)

    def test_retry_preserves_request_comparison_id_and_returned_response(
        self,
    ) -> None:
        calls: list[tuple[LLMRequest, str | None]] = []
        response = LLMResponse(
            [], usage_info=dict(input_tokens=1000, output_tokens=100)
        )
        model = cast(
            r.AuditModel,
            SimpleNamespace(
                cell="synthetic",
                reasoning_cache=None,
                reasoning_allowance=0,
                previous_response=lambda: "original-response-id",
            ),
        )
        request = LLMRequest(chat=(), options={"model": "gpt-5.6-luna"})

        def send(m: r.AuditModel, req: LLMRequest) -> LLMResponse:
            calls.append((req, m.previous_response()))
            if len(calls) == 1:
                raise rejection()
            return response

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch.object(r, "FOLDER", root),
                patch.object(r.AuditModel, "_send_final_request", send),
                patch.object(r.time, "sleep") as sleeping,
                patch.object(r.time, "time", return_value=100.0),
                patch.object(r.random, "uniform", return_value=0.25),
                patch(
                    "openai.OpenAI",
                    side_effect=AssertionError("HTTP forbidden"),
                ),
                r.paced_transport(),
            ):
                result = r.AuditModel._send_final_request(model, request)  # pyright: ignore[reportPrivateUsage]
                self.assertIs(result, response)
                self.assertEqual(
                    calls, [(request, "original-response-id")] * 2
                )
                self.assertIn(call(5.25), sleeping.call_args_list)
                again = r.AuditModel._send_final_request(model, request)  # pyright: ignore[reportPrivateUsage]
                self.assertIs(again, response)
                self.assertEqual(len(calls), 3)
            self.assertAlmostEqual(
                float((root / "next_dispatch.txt").read_text()), 100.165
            )

    def test_rejected_transport_state_mutation_is_detected(self) -> None:
        model = cast(
            r.AuditModel,
            SimpleNamespace(
                cell="synthetic",
                reasoning_cache=None,
                reasoning_allowance=0,
                previous_response=lambda: None,
            ),
        )
        request = LLMRequest(chat=(), options={"model": "gpt-5.6-luna"})

        def send(m: r.AuditModel, _request: Any) -> LLMResponse:
            m.reasoning_allowance += 1
            raise rejection()

        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(r, "FOLDER", Path(temporary)),
            patch.object(r.AuditModel, "_send_final_request", send),
            patch.object(r.time, "sleep"),
            r.paced_transport(),
            self.assertRaisesRegex(ValueError, "changed model state"),
        ):
            r.AuditModel._send_final_request(model, request)  # pyright: ignore[reportPrivateUsage]


if __name__ == "__main__":
    unittest.main()
