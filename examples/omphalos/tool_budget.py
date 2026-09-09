"""Opt-in whole-operation Rocq budgets, usable by both agent harnesses.

Contexts belong inside Compute calls, never speculative strategy evaluation.
We account elapsed wall seconds and RPC attempts, not CPU time.
"""

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
import math
import time


@dataclass(frozen=True)
class ToolLimits:
    seconds: float = 60.0
    rpc_calls: int = 512
    view_bytes: int = 8192

    def __post_init__(self) -> None:
        if (
            not math.isfinite(self.seconds)
            or self.seconds <= 0
            or self.rpc_calls < 1
            or self.view_bytes < 512
        ):
            raise ValueError("operation limits must be finite and positive")


class OperationExhausted(RuntimeError):
    """No remaining allowance; this is not a logical rejection."""


@dataclass
class Operation:
    limits: ToolLimits
    started: float = field(default_factory=time.monotonic)
    calls: int = 0
    exhausted: str = ""
    prefix: list[str] = field(default_factory=list[str])
    goals: list[str] = field(default_factory=list[str])

    @property
    def elapsed(self) -> float:
        return max(0.0, time.monotonic() - self.started)

    def remaining(self) -> float:
        left = self.limits.seconds - self.elapsed
        if self.exhausted or left <= 0:
            self.exhausted = self.exhausted or "operation deadline"
            raise OperationExhausted(self.exhausted)
        return left

    def admit_rpc(self, timeout: float) -> float:
        if self.calls >= self.limits.rpc_calls:
            self.exhausted = "operation RPC allowance"
        remaining = self.remaining()
        self.calls += 1
        return min(timeout, remaining)


CURRENT: ContextVar[Operation | None] = ContextVar(
    "rocq_operation", default=None
)


@contextmanager
def operation(limits: ToolLimits) -> Generator[Operation]:
    if CURRENT.get() is not None:
        raise RuntimeError("nested operations must share their parent budget")
    op = Operation(limits)
    token = CURRENT.set(op)
    try:
        yield op
    finally:
        CURRENT.reset(token)


def clamp_timeout(seconds: float) -> float:
    op = CURRENT.get()
    return seconds if op is None else min(seconds, op.remaining())


def clip_utf8(text: str, limit: int) -> str:
    data = text.encode()
    if len(data) <= limit:
        return text
    marker = "\n[view truncated; inspect the verified prefix for more]"
    return (
        data[: max(0, limit - len(marker.encode()))].decode(errors="ignore")
        + marker
    )
