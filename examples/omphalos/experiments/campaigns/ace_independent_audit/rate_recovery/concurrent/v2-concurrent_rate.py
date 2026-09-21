"""Shared admission for four overlapping, unchanged solver HTTP requests.

Scheduling amendment only. No solver, output cap, receipt, retry eligibility,
or registered cell changes. Both harnesses use concurrent_handoff to switch
at a completed batch boundary. The original rate_recovery stays immutable.

The admission estimate uses local visible-payload tokenization plus the
existing hidden-reasoning allowance and a margin. It is not a provider token
count or billing bound. Reservations and observed usage share a 60s window;
uncompleted requests retain their reservation even beyond that window.
Explicit temporary TPM errors impose a shared server-respecting cooldown.
"""

from collections.abc import Generator
from contextlib import contextmanager
import fcntl
import json
import math
import os
from pathlib import Path
import time
from typing import Any, cast
from unittest.mock import patch
import uuid

from delphyne.stdlib import openai_api as oa
from delphyne.stdlib.models import LLMRequest, LLMResponse
import openai
from pydantic import TypeAdapter
import tiktoken

from runtime.campaign_pause import request_pause
from runtime.replay_admission import transport_state

from . import rate_recovery as r
from .common import digest, now
from .transport import AuditModel

FOLDER = r.FOLDER / "concurrent"
MAX_IN_FLIGHT = 4
TOKENS_PER_MINUTE = 400000
WINDOW_SECONDS = 60.0
POLL_SECONDS = 0.25


def visible(value: Any) -> Any:
    """Encrypted reasoning bytes are not model input text to tokenize."""
    if isinstance(value, dict):
        return {
            k: visible(v)
            for k, v in cast(dict[str, Any], value).items()
            if k not in {"encrypted_content", "id"}
        }
    if isinstance(value, list):
        return [visible(v) for v in cast(list[Any], value)]
    return value


def estimate_payload(
    payload: Any, reasoning_allowance: int, output_limit: int
) -> int:
    encoded = json.dumps(visible(payload), ensure_ascii=False)
    tokens = len(
        tiktoken.get_encoding("o200k_base").encode(
            encoded, disallowed_special=()
        )
    )
    # Output-cap reservations are retained: provider TPM is not necessarily
    # actual billed usage. Do not optimize the experimental output limit.
    return max(
        output_limit, math.ceil(1.15 * tokens) + reasoning_allowance + 1024
    )


def estimate(model: AuditModel, request: LLMRequest) -> int:
    assert "max_completion_tokens" in request.options
    inp, _ = oa.translate_chat_for_responses(
        request, model.reasoning_cache, model.convert_user_feedback_to_tool
    )
    tools = [oa._make_responses_tool(t) for t in request.tools]  # pyright: ignore[reportPrivateUsage]
    fmt = oa._responses_response_format(  # pyright: ignore[reportPrivateUsage]
        request.structured_output, model.no_json_schema
    )
    allowance = (
        model.reasoning_allowance if model.reasoning_cache is not None else 0
    )
    return estimate_payload(
        [inp, tools, fmt],
        allowance,
        request.options["max_completion_tokens"],
    )


class Gate:
    """Cross-process admission; never hold the state lock during HTTP."""

    def __init__(self, folder: Path = FOLDER):
        self.folder = folder
        folder.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def state(self) -> Generator[dict[str, Any]]:
        with (self.folder / "state.lock").open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            path = self.folder / "state.json"
            state: dict[str, Any] = (
                json.loads(path.read_text())
                if path.exists()
                else dict(entries={}, waiting=[], cooldown_until=0.0)
            )
            current = time.time()
            state["entries"] = {
                k: v
                for k, v in state["entries"].items()
                if v["active"] or v["started"] > current - WINDOW_SECONDS
            }
            yield state
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(state, sort_keys=True) + "\n")
            temporary.replace(path)

    def event(self, **value: Any) -> None:
        # Called only with the state lock, so records cannot interleave.
        with (self.folder / "dispatch_events.jsonl").open("a") as stream:
            stream.write(json.dumps(dict(at=now(), **value)) + "\n")

    @staticmethod
    def ready(state: dict[str, Any], token: str, amount: int) -> bool:
        entries = list(state["entries"].values())
        return (
            state["waiting"][0] == token
            and time.time() >= state["cooldown_until"]
            and sum(e["active"] for e in entries) < MAX_IN_FLIGHT
            # An estimate above the soft target gets an exclusive slot
            # once the window empties. Do not deadlock or locally reject
            # a request whose real provider token count is still unknown.
            and sum(e["tokens"] for e in entries)
            + min(amount, TOKENS_PER_MINUTE)
            <= TOKENS_PER_MINUTE
        )

    def acquire(self, amount: int, cell: str, request_sha: str) -> str:
        if amount <= 0:
            raise ValueError("A token reservation must be positive")
        token = uuid.uuid4().hex
        with self.state() as state:
            state["waiting"].append(token)
        while True:
            with self.state() as state:
                if self.ready(state, token, amount):
                    state["waiting"].pop(0)
                    state["entries"][token] = dict(
                        active=True,
                        started=time.time(),
                        tokens=amount,
                        cell=cell,
                        request_sha=request_sha,
                        pid=os.getpid(),
                    )
                    self.event(
                        event="dispatch",
                        reservation=token,
                        **state["entries"][token],
                        in_flight=sum(
                            e["active"] for e in state["entries"].values()
                        ),
                    )
                    return token
            time.sleep(POLL_SECONDS)

    def finish(
        self,
        token: str,
        *,
        observed: int | None,
        error: str | None = None,
        cooldown: float = 0,
    ) -> None:
        with self.state() as state:
            entry = state["entries"][token]
            if not entry["active"]:
                raise ValueError("Reservation was already settled")
            entry["active"] = False
            entry["tokens"] = max(entry["tokens"], observed or 0)
            state["cooldown_until"] = max(
                state["cooldown_until"], time.time() + cooldown
            )
            self.event(
                event="returned",
                reservation=token,
                cell=entry["cell"],
                request_sha=entry["request_sha"],
                elapsed_seconds=time.time() - entry["started"],
                reserved_tokens=entry["tokens"],
                observed_tokens=observed,
                error=error,
                cooldown_seconds=cooldown,
            )


@contextmanager
def paced_transport() -> Generator[None]:
    """Reuse exact transport/retry semantics, replacing admission only."""
    original = AuditModel._send_final_request  # pyright: ignore[reportPrivateUsage]

    def send(model: AuditModel, request: LLMRequest) -> LLMResponse:
        encoded = TypeAdapter(LLMRequest).dump_python(request, mode="json")
        request_sha = digest(encoded)
        before = digest(transport_state(model))
        previous = model.previous_response()
        amount = estimate(model, request)
        gate = Gate(FOLDER)
        started: float | None = None
        with patch.object(model, "previous_response", return_value=previous):
            for attempt in range(13):
                token = gate.acquire(amount, model.cell, request_sha)
                if started is None:
                    started = time.time()
                try:
                    response = original(model, request)
                except openai.RateLimitError as error:
                    try:
                        delay = r.retry_delay(error, attempt)
                    except openai.RateLimitError:
                        gate.finish(
                            token, observed=None, error=str(error.code)
                        )
                        raise
                    gate.finish(
                        token,
                        observed=None,
                        error=str(error.code),
                        cooldown=delay,
                    )
                    if digest(transport_state(model)) != before or (
                        TypeAdapter(LLMRequest).dump_python(
                            request, mode="json"
                        )
                        != encoded
                    ):
                        raise ValueError(
                            "A rejected dispatch changed model state"
                        )
                    if attempt == 12 or time.time() + delay - started > 900:
                        request_pause(
                            Path(model.pause_file),
                            "Temporary rate retry allowance exhausted; preserve the exact trajectory",
                        )
                        raise
                    # acquire() observes this same shared cooldown and
                    # reserves each actual HTTP retry separately.
                    time.sleep(delay)
                except Exception as error:
                    gate.finish(
                        token, observed=None, error=type(error).__name__
                    )
                    raise
                else:
                    usage = response.usage_info or {}
                    gate.finish(
                        token,
                        observed=usage.get("input_tokens", 0)
                        + usage.get("output_tokens", 0),
                    )
                    return response
        raise AssertionError("Unreachable rate-retry exhaustion")

    with patch.object(AuditModel, "_send_final_request", send):
        yield
