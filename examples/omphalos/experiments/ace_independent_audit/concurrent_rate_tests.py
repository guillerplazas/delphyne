"""HTTP-disabled checks of actual overlapping workers and exact retries."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
from typing import Any, cast
import unittest
from unittest.mock import patch

from delphyne.stdlib.models import LLMRequest, LLMResponse

from . import concurrent_rate as c
from . import concurrent_handoff as handoff
from .rate_recovery_tests import rejection


class Clock:
    def __init__(self) -> None:
        self.value = 100.0

    def advance(self, delay: float) -> None:
        self.value += delay


class ConcurrentRateTests(unittest.TestCase):
    def test_handoff_preserves_recent_serial_usage_from_json_ledger(
        self,
    ) -> None:
        current = time.time()
        receipts = [
            dict(
                id="recent",
                cell="prior",
                created=current - 10,
                status="settled",
                usage=json.dumps(dict(input_tokens=40000, output_tokens=1000)),
            ),
            dict(
                id="old",
                created=current - 90,
                status="settled",
                usage="{}",
            ),
            dict(
                id="rejected",
                created=current - 9,
                status="settled",
                usage=json.dumps(dict(type="RateLimitError")),
            ),
        ]
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(c, "FOLDER", Path(temporary)),
            patch.object(handoff, "ledger_rows", return_value=receipts),
        ):
            handoff.seed_recent_usage()
            state = json.loads((Path(temporary) / "state.json").read_text())
            self.assertEqual(list(state["entries"]), ["recent"])
            self.assertEqual(state["entries"]["recent"]["tokens"], 41000)
            self.assertFalse(state["entries"]["recent"]["active"])

    def test_requests_overlap_but_never_exceed_four(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)

            def work(index: int) -> None:
                gate = c.Gate(folder)
                token = gate.acquire(1000, str(index), "unchanged")
                time.sleep(0.15)
                gate.finish(token, observed=1000)

            with ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(work, range(8)))
            events = [
                json.loads(line)
                for line in (folder / "dispatch_events.jsonl")
                .read_text()
                .splitlines()
            ]
            dispatches = [e for e in events if e["event"] == "dispatch"]
            self.assertEqual(len(dispatches), 8)
            self.assertEqual(max(e["in_flight"] for e in dispatches), 4)
            self.assertEqual(
                [e["event"] for e in events[:4]], ["dispatch"] * 4
            )

    def test_token_capacity_and_completed_usage_correction(self) -> None:
        clock = Clock()
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(c.time, "time", side_effect=lambda: clock.value),
        ):
            gate = c.Gate(Path(temporary))
            tokens = [gate.acquire(100000, "a", str(i)) for i in range(4)]
            gate.finish(tokens[0], observed=150000)
            with gate.state() as state:
                state["waiting"].append("next")
                self.assertFalse(gate.ready(state, "next", 1000))
            clock.advance(61)
            with gate.state() as state:
                self.assertEqual(len(state["entries"]), 3)
                self.assertTrue(gate.ready(state, "next", 100000))
                self.assertFalse(gate.ready(state, "next", 100001))

    def test_returned_usage_releases_unused_token_reservations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            gate = c.Gate(Path(temporary))
            tokens = [gate.acquire(100000, "a", str(i)) for i in range(4)]
            gate.finish(tokens[0], observed=1000)
            with gate.state() as state:
                state["waiting"].append("next")
                self.assertTrue(gate.ready(state, "next", 99000))
                self.assertFalse(gate.ready(state, "next", 99001))

    def test_large_reservation_waits_exclusively_and_does_not_expire_in_flight(
        self,
    ) -> None:
        clock = Clock()
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(c.time, "time", side_effect=lambda: clock.value),
        ):
            gate = c.Gate(Path(temporary))
            token = gate.acquire(450000, "large", "large")
            clock.advance(90)
            with gate.state() as state:
                state["waiting"].append("next")
                self.assertFalse(gate.ready(state, "next", 1000))
            gate.finish(token, observed=430000)
            with gate.state() as state:
                self.assertTrue(gate.ready(state, "next", 1000))

    def test_cooldown_is_shared_and_fifo_prevents_starvation(self) -> None:
        clock = Clock()
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(c.time, "time", side_effect=lambda: clock.value),
        ):
            gate = c.Gate(Path(temporary))
            token = gate.acquire(1000, "a", "a")
            gate.finish(token, observed=None, cooldown=47)
            with gate.state() as state:
                state["waiting"].extend(["first", "second"])
                self.assertFalse(gate.ready(state, "first", 1000))
            clock.advance(47)
            with gate.state() as state:
                self.assertTrue(gate.ready(state, "first", 1000))
                self.assertFalse(gate.ready(state, "second", 1000))

    def test_payload_estimate_ignores_ciphertext_and_preserves_output_cap(
        self,
    ) -> None:
        a = {"encrypted_content": "x", "content": "ordinary text"}
        b = {"encrypted_content": "x" * 200000, "content": "ordinary text"}
        self.assertGreater(c.estimate_payload(a, 100, 32768), 32768 + 100)
        self.assertEqual(
            c.estimate_payload(a, 40000, 32768),
            c.estimate_payload(b, 40000, 32768),
        )
        self.assertGreater(c.estimate_payload(a, 40000, 32768), 40000)

    def exercise(
        self, error: Exception, *, mutate: bool = False
    ) -> tuple[list[Any], list[dict[str, Any]]]:
        calls: list[Any] = []
        result = LLMResponse(
            [], usage_info=dict(input_tokens=1000, output_tokens=100)
        )
        model = cast(
            c.AuditModel,
            SimpleNamespace(
                cell="synthetic",
                reasoning_cache=None,
                reasoning_allowance=0,
                previous_response=lambda: "same-comparison-id",
            ),
        )
        request = LLMRequest(chat=(), options={"model": "gpt-5.6-luna"})

        def send(m: c.AuditModel, req: LLMRequest) -> LLMResponse:
            calls.append((req, m.previous_response()))
            if len(calls) == 1:
                if mutate:
                    m.reasoning_allowance += 1
                raise error
            return result

        clock = Clock()
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with (
                patch.object(c, "FOLDER", folder),
                patch.object(c, "estimate", return_value=32768),
                patch.object(c.AuditModel, "_send_final_request", send),
                patch.object(c.time, "time", side_effect=lambda: clock.value),
                patch.object(c.time, "sleep", side_effect=clock.advance),
                patch.object(c.r.random, "uniform", return_value=0.25),
                patch("openai.OpenAI", side_effect=AssertionError("No HTTP")),
                c.paced_transport(),
            ):
                try:
                    observed = c.AuditModel._send_final_request(model, request)  # pyright: ignore[reportPrivateUsage]
                    self.assertIs(observed, result)
                except Exception as raised:
                    calls.append(raised)
            events = [
                json.loads(line)
                for line in (folder / "dispatch_events.jsonl")
                .read_text()
                .splitlines()
            ]
            state = json.loads((folder / "state.json").read_text())
            self.assertFalse(
                any(e["active"] for e in state["entries"].values())
            )
        return calls, events

    def test_retry_preserves_request_comparison_id_and_response(self) -> None:
        calls, events = self.exercise(rejection())
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], calls[1])
        self.assertEqual(events[1]["cooldown_seconds"], 5.25)
        self.assertEqual(events[0]["request_sha"], events[2]["request_sha"])

    def test_credit_oversized_and_unknown_failures_are_never_retried(
        self,
    ) -> None:
        for error in (
            rejection("credit_balance_exhausted"),
            rejection(requested=500001),
            RuntimeError("unknown transport failure"),
        ):
            calls, events = self.exercise(error)
            self.assertEqual(len(calls), 2)
            self.assertIs(calls[-1], error)
            self.assertEqual(len(events), 2)

    def test_rejected_state_mutation_stops_retries(self) -> None:
        calls, events = self.exercise(rejection(), mutate=True)
        self.assertIsInstance(calls[-1], ValueError)
        self.assertEqual(len(events), 2)


if __name__ == "__main__":
    unittest.main()
