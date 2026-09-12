"""Opt-in, exact Responses replay state and terminal budget evidence.

The request cache remains Delphyne's cache. A policy-local adapter restores
the transport side effects which a cache hit otherwise skips. Snapshots are
versioned, request-addressed, and also retain the response so an interrupted
worker cannot lose a settled response before Delphyne flushes its cache.
No monkey patch or override of LLM.send_request is required.
"""

from collections.abc import Callable, Sequence
from copy import copy
from dataclasses import dataclass, field, fields
import gzip
import hashlib
import json
import os
from pathlib import Path
from typing import Any, override

import delphyne as dp
from delphyne.core.streams import Barrier, Spent
from delphyne.stdlib import openai_api as oa
from delphyne.stdlib.models import (
    CachedRequest,
    LLMCache,
    LLMRequest,
    LLMResponse,
)
from delphyne.stdlib.policies import prompting_policy
from delphyne.stdlib.streams import Stream, stream_transformer
from delphyne.utils.caching import Cache
from pydantic import TypeAdapter

from runtime.admission_events import record
from runtime.campaign_budget import CampaignResponsesModel

_REQUEST = TypeAdapter(CachedRequest)
_RESPONSE = TypeAdapter(LLMResponse)
_REASONING = TypeAdapter(
    list[tuple[oa.ReasoningCacheKey, Sequence[oa.ReasoningMessage]]]
)


@dataclass
class PrefixGuard:
    remaining: set[CachedRequest] = field(
        default_factory=lambda: set[CachedRequest]()
    )

    def consume(self, request: CachedRequest) -> None:
        if request not in self.remaining and self.remaining:
            raise ValueError(
                "Continuation diverged before replaying its full prefix"
            )
        self.remaining.discard(request)


@dataclass(frozen=True)
class PrefixCache(Cache[CachedRequest, LLMResponse]):
    guard: PrefixGuard

    @override
    def __call__(
        self, func: Callable[[CachedRequest], LLMResponse]
    ) -> Callable[[CachedRequest], LLMResponse]:
        cached = super().__call__(func)

        def answer(request: CachedRequest) -> LLMResponse:
            self.guard.consume(request)
            return cached(request)

        return answer


def fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def transport_state(model: CampaignResponsesModel) -> dict[str, Any]:
    reasoning = (
        list(model.reasoning_cache.cache.dict.items())
        if model.reasoning_cache is not None
        else []
    )
    return dict(
        reasoning_enabled=model.reasoning_cache is not None,
        allowance=model.reasoning_allowance,
        reasoning=_REASONING.dump_python(reasoning, mode="json"),
    )


def restore_state(
    model: CampaignResponsesModel, state: dict[str, Any]
) -> None:
    if state["reasoning_enabled"] != (model.reasoning_cache is not None):
        raise ValueError("Reasoning-cache configuration drift")
    model.reasoning_allowance = int(state["allowance"])
    if model.reasoning_cache is not None:
        values = _REASONING.validate_python(state["reasoning"])
        model.reasoning_cache.cache.dict.clear()
        model.reasoning_cache.cache.dict.update(values)


@dataclass(kw_only=True)
class RecordedResponsesModel(CampaignResponsesModel):
    @override
    def estimate_budget(self, req: LLMRequest) -> dp.Budget:
        estimate = super().estimate_budget(req)
        full = self.add_model_defaults(req)
        record(
            "estimate_v2",
            "estimated",
            request=fingerprint(
                TypeAdapter(LLMRequest).dump_python(full, mode="json")
            ),
            estimate=dict(estimate.values),
            input_bound=self._input_bound(full),
            output_limit=full.options.get(
                "max_completion_tokens", self.output_limit
            ),
            reasoning_allowance=self.reasoning_allowance,
            transport_state=fingerprint(transport_state(self)),
        )
        return estimate


def recorded_model(model: CampaignResponsesModel) -> RecordedResponsesModel:
    if model.reasoning_allowance or (
        model.reasoning_cache is not None and model.reasoning_cache.cache.dict
    ):
        raise ValueError("Install recording before the first request")
    return RecordedResponsesModel(
        **{f.name: getattr(model, f.name) for f in fields(model) if f.init}
    )


@dataclass(frozen=True)
class RecordedCache(Cache[CachedRequest, LLMResponse]):
    model: CampaignResponsesModel
    directory: Path
    guard: PrefixGuard | None = None

    @override
    def __call__(
        self, func: Callable[[CachedRequest], LLMResponse]
    ) -> Callable[[CachedRequest], LLMResponse]:
        def answer(request: CachedRequest) -> LLMResponse:
            if self.guard is not None:
                self.guard.consume(request)
            raw_request = _REQUEST.dump_python(request, mode="json")
            key = fingerprint(raw_request)
            path = self.directory / f"{key}.json.gz"
            before = transport_state(self.model)
            if path.exists():
                with gzip.open(path, "rt") as f:
                    saved = json.load(f)
                if saved["version"] != 1 or saved["request"] != raw_request:
                    raise ValueError("Replay snapshot/request mismatch")
                if saved["before"] != fingerprint(before):
                    raise ValueError("Replay transport state diverged")
                response = _RESPONSE.validate_python(saved["response"])
                if request in self.dict:
                    if (
                        _RESPONSE.dump_python(self.dict[request], mode="json")
                        != saved["response"]
                    ):
                        raise ValueError("Request cache and snapshot disagree")
                    response = self.dict[request]
                restore_state(self.model, saved["after"])
                if self.mode not in ("read_only", "replay", "off"):
                    self.dict[request] = response
                record(
                    "transport",
                    "restored",
                    request=key,
                    state=fingerprint(saved["after"]),
                    newly_billed=0.0,
                )
                return response
            if request in self.dict or self.mode == "replay":
                raise ValueError("Exact replay requires a transport snapshot")
            response = func(request)
            saved = dict(
                version=1,
                request=raw_request,
                before=fingerprint(before),
                after=transport_state(self.model),
                response=_RESPONSE.dump_python(response, mode="json"),
            )
            self.directory.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(f".tmp-{os.getpid()}")
            with temporary.open("xb") as raw:
                os.chmod(temporary, 0o600)
                with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as f:
                    f.write(json.dumps(saved, sort_keys=True).encode())
                raw.flush()
                os.fsync(raw.fileno())
            os.replace(temporary, path)
            if self.mode not in ("read_only", "replay", "off"):
                self.dict[request] = response
            record(
                "transport",
                "saved",
                request=key,
                state=fingerprint(saved["after"]),
            )
            return response

        return answer


@prompting_policy
def recorded_prompt[T](
    query: dp.AttachedQuery[T],
    env: dp.PolicyEnv,
    normal: dp.PromptingPolicy,
    model: CampaignResponsesModel,
    directory: str,
) -> dp.StreamGen[T]:
    local = copy(env)
    original = env.cache or LLMCache(Cache({}, "read_write"))
    local.cache = LLMCache(
        RecordedCache(
            original.cache.dict,
            original.cache.mode,
            model,
            Path(directory),
            original.cache.guard
            if isinstance(original.cache, PrefixCache)
            else None,
        )
    )
    local.cache.num_seen = original.num_seen
    yield from normal(query, local)


@stream_transformer
def admission_observer[T](
    stream: Stream[T],
    env: dp.PolicyEnv,
    limits: dict[str, float],
) -> dp.StreamGen[T]:
    """Observe the enclosing Delphyne budget after it decides each barrier.

    The finally block also exports termination on close/exception; it does not
    change admission. Denied reservations remain zero until their Spent arrives.
    """
    spent = dp.Budget.zero()
    pending: dict[Any, dp.Budget] = {}
    last: dict[str, Any] | None = None
    solved = False
    try:
        for message in stream:
            if isinstance(message, dp.Solution):
                solved = True
            yield message
            if isinstance(message, Barrier):
                reserved = sum(pending.values(), start=dp.Budget.zero())
                remaining = {
                    key: cap - spent[key] - reserved[key]
                    for key, cap in limits.items()
                }
                last = dict(
                    estimate=dict(message.budget.values),
                    spent=dict(spent.values),
                    reserved=dict(reserved.values),
                    remaining=remaining,
                    limiting=[
                        k
                        for k, v in remaining.items()
                        if message.budget[k] > v + 1e-12
                    ],
                    admitted=message.allow,
                )
                record(
                    "admission_v2",
                    "admitted" if message.allow else "declined",
                    **last,
                )
                pending[message.id] = (
                    message.budget if message.allow else dp.Budget.zero()
                )
            elif isinstance(message, Spent):
                spent += message.budget
                pending.pop(message.barrier_id, None)
            else:
                solved = True
    finally:
        record(
            "terminal_v2",
            "solved" if solved else "stopped",
            spent=dict(spent.values),
            last_admission=last,
            pending=len(pending),
        )
