"""
The persisted state of a Ladon night (`ladon/nights/<date>/night.yaml`).

Every step of the orchestrator reads this file, does one thing, and
writes it back atomically, so a crash, a usage-limit halt or a
`SIGTERM` at any point leaves a file from which `python -m ladon.cli
resume` continues. The schema is deliberately flat dictionaries under
a few typed fields: the report renders straight from it and a human
can read it in the morning.
"""

# pyright: strict

import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, cast

import yaml

type NightState = Literal[
    "created",
    "preflight_ok",
    "baseline_ok",
    "planned",
    "running",
    "reporting",
    "done",
    "halted",
]

type HintState = Literal[
    "queued",
    "implementing",
    "implemented",
    "guarded",
    "screening",
    "screened",
    "selecting",
    "selected",
    "reverifying",
    "judged",
    "evaluated",
    "recorded",
    "skipped",
]

HINT_ORDER: tuple[HintState, ...] = (
    "queued",
    "implementing",
    "implemented",
    "guarded",
    "screening",
    "screened",
    "selecting",
    "selected",
    "reverifying",
    "judged",
    "evaluated",
    "recorded",
)


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


@dataclass
class HintRun:
    n: int
    title: str
    tag: str
    hint_class: str
    state: str = "queued"
    outcome: str | None = None
    rule: str | None = None
    reason: str | None = None
    tier: str | None = None
    commit: str | None = None
    patch: str | None = None
    script: str | None = None
    output_dir: str | None = None
    smoke_dir: str | None = None
    notes: str | None = None
    fingerprint: str | None = None
    head_before: str | None = None
    plan: dict[str, Any] = field(default_factory=dict[str, Any])
    arm: dict[str, Any] = field(default_factory=dict[str, Any])
    numbers: dict[str, Any] = field(default_factory=dict[str, Any])
    screen: dict[str, Any] = field(default_factory=dict[str, Any])
    select: dict[str, Any] = field(default_factory=dict[str, Any])
    reverify: dict[str, Any] = field(default_factory=dict[str, Any])
    guard: dict[str, Any] = field(default_factory=dict[str, Any])
    gates: dict[str, Any] = field(default_factory=dict[str, Any])
    evaluation: dict[str, Any] = field(default_factory=dict[str, Any])
    sessions: list[dict[str, Any]] = field(
        default_factory=list[dict[str, Any]]
    )
    timeline: dict[str, str] = field(default_factory=dict[str, str])
    claude_cost_usd: float = 0.0
    arm_spend_usd: float = 0.0
    smoke_spend_usd: float = 0.0
    error: str | None = None

    def enter(self, state: HintState) -> None:
        self.state = state
        self.timeline[state] = now_iso()

    @property
    def finished(self) -> bool:
        return self.state in ("recorded", "skipped")


@dataclass
class Night:
    date: str
    state: str = "created"
    halt_reason: str | None = None
    base_sha: str | None = None
    branch: str | None = None
    started_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    dry: bool = False
    budget: dict[str, Any] = field(default_factory=dict[str, Any])
    spent: dict[str, float] = field(
        default_factory=lambda: {
            "usd_openai": 0.0,
            "usd_claude": 0.0,
            "minutes_waited": 0.0,
        }
    )
    claude: dict[str, Any] = field(default_factory=dict[str, Any])
    preflight: dict[str, Any] = field(default_factory=dict[str, Any])
    baseline: dict[str, Any] = field(default_factory=dict[str, Any])
    worktree: dict[str, Any] = field(default_factory=dict[str, Any])
    plan: dict[str, Any] = field(default_factory=dict[str, Any])
    human: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])
    rate_limit_events: list[dict[str, Any]] = field(
        default_factory=list[dict[str, Any]]
    )
    order: list[int] = field(default_factory=list[int])
    hints: dict[int, HintRun] = field(default_factory=dict[int, HintRun])
    timeline: list[dict[str, str]] = field(
        default_factory=list[dict[str, str]]
    )

    def event(self, text: str) -> None:
        self.timeline.append({"at": now_iso(), "event": text})

    def enter(self, state: NightState, reason: str | None = None) -> None:
        self.state = state
        if reason is not None:
            self.halt_reason = reason
        self.event(f"night -> {state}" + (f": {reason}" if reason else ""))

    @property
    def active_hints(self) -> list[HintRun]:
        return [
            self.hints[n] for n in self.order if not self.hints[n].finished
        ]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["hints"] = {int(k): asdict(v) for k, v in self.hints.items()}
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Night":
        hints_raw = cast(dict[Any, dict[str, Any]], d.get("hints", {}))
        hints = {int(k): HintRun(**v) for k, v in hints_raw.items()}
        rest = {k: v for k, v in d.items() if k != "hints"}
        night = cls(**rest)
        night.hints = hints
        return night


def night_dir(date: str, root: Path | None = None) -> Path:
    base = (
        root
        if root is not None
        else Path(__file__).resolve().parent / "nights"
    )
    return base / date


def state_path(date: str, root: Path | None = None) -> Path:
    return night_dir(date, root) / "night.yaml"


def save(night: Night, path: Path) -> None:
    night.updated_at = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".yaml.tmp")
    tmp.write_text(
        yaml.safe_dump(night.to_dict(), sort_keys=False, allow_unicode=True)
    )
    os.replace(tmp, path)


def load(path: Path) -> Night:
    raw: Any = yaml.safe_load(path.read_text())
    return Night.from_dict(cast(dict[str, Any], raw or {}))
