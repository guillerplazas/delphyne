"""
Driving `claude -p` sessions from the orchestrator.

Every Ladon session is a fresh, non-interactive Claude Code run with
an explicit model, effort, turn cap, permission mode and tool lists,
its own appended system prompt (`ladon/LADON.md`) and its transcript
teed to disk. Nothing is resumed: a session hands its state over in
files (`arm.yaml`, `notes.md`), which is cheaper on a subscription
than re-reading a long context after an hour-long experiment and
makes every step replayable.

What the driver knows about the Max plan, from the docs and the
installed binary (2.1.258, 2026-09-02): a `-p` run that hits a usage
limit ends with "You've hit your … limit" and a non-zero exit; the
stream carries `rate_limit_event`s with `five_hour` / `seven_day`
utilisation and `resets_at` (epoch seconds); `--bare` must never be
used (it ignores the subscription login); an `ANTHROPIC_API_KEY` in
the environment would silently outrank the subscription; the Bash
tool's default timeouts (2 / 10 min) are shorter than a Rocq smoke.
Seen on 2026-09-03: the windows arrive as `rate_limit_info.
unifiedWindows.{five_hour,seven_day}.{utilization,resetsAt}` in
stream-json (camelCase), and not at all in `--output-format json`.
"""

# pyright: strict

import json
import os
import re
import shutil
import subprocess
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent

type OutputFormat = Literal["json", "stream-json"]
type SystemPromptFlag = Literal["file", "inline"]

RATE_LIMIT_RE = re.compile(r"hit your .{0,60}?limit", re.I)
RESETS_IN_RE = re.compile(
    r"resets? in\s*(?:(\d+)\s*h(?:ours?)?)?\s*(?:(\d+)\s*m(?:in(?:utes?)?)?)?",
    re.I,
)
BACKOFF_FIRST_S = 20 * 60.0
BACKOFF_CAP_S = 3 * 3600.0
"""Cumulative waiting allowed for one step before the night halts."""

BASH_TIMEOUTS = {
    "BASH_DEFAULT_TIMEOUT_MS": "1800000",
    "BASH_MAX_TIMEOUT_MS": "7200000",
}
STRIP_ENV = ("ANTHROPIC_API_KEY",)
STRIP_ENV_PREFIXES = ("CLAUDE",)
KEEP_ENV = ("CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_CODE_MAX_RETRIES")
"""
A Ladon session must not believe it is nested inside the session that
launched the night (`CLAUDECODE`, `CLAUDE_CODE_SESSION_ID`,
`CLAUDE_CODE_MESSAGING_*`, `CLAUDE_EFFORT`, ...), so every `CLAUDE*`
variable is dropped except the two that configure the child itself:
`CLAUDE_CODE_OAUTH_TOKEN` is how an unattended run authenticates with
the subscription (`claude setup-token`).
"""


@dataclass(frozen=True)
class ClaudeCall:
    phase: str
    prompt: str
    model: str
    effort: str
    max_turns: int
    log: Path
    cwd: Path = _OMPHALOS_DIR
    output_format: OutputFormat = "stream-json"
    permission_mode: str = "acceptEdits"
    allowed: tuple[str, ...] = ()
    disallowed: tuple[str, ...] = ()
    tools: str | None = None
    system_file: Path | None = None
    schema: Mapping[str, Any] | None = None
    max_budget_usd: float | None = None
    add_dirs: tuple[str, ...] = ()
    strict_mcp: bool = True
    resume_session: str | None = None
    """Continue an earlier session (its `session_id`) instead of starting."""


@dataclass(frozen=True)
class ClaudeResult:
    rc: int
    subtype: str
    text: str
    structured: dict[str, Any] | None
    cost_usd: float
    num_turns: int
    session_id: str
    duration_s: float
    rate_limited: bool
    resets_at: float | None
    utilization: dict[str, float] = field(default_factory=dict[str, float])
    denials: tuple[str, ...] = ()
    stderr_tail: str = ""
    argv_error: str = ""

    @property
    def ok(self) -> bool:
        return self.rc == 0 and self.subtype == "success"

    @property
    def hit_max_turns(self) -> bool:
        return self.subtype == "error_max_turns"

    @property
    def hit_budget(self) -> bool:
        return self.subtype == "error_max_budget_usd"


def claude_binary() -> str:
    path = shutil.which("claude")
    if path is None:
        raise RuntimeError("`claude` is not on PATH")
    return path


def env_for_claude(base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = {
        k: v
        for k, v in (base if base is not None else os.environ).items()
        if k in KEEP_ENV
        or (k not in STRIP_ENV and not k.startswith(STRIP_ENV_PREFIXES))
    }
    env.update(BASH_TIMEOUTS)
    return env


def build_argv(
    call: ClaudeCall, *, system_prompt_flag: SystemPromptFlag = "file"
) -> list[str]:
    argv = [
        claude_binary(),
        "-p",
        call.prompt,
        "--model",
        call.model,
        "--effort",
        call.effort,
        "--max-turns",
        str(call.max_turns),
        "--permission-mode",
        call.permission_mode,
        "--output-format",
        call.output_format,
    ]
    if call.resume_session:
        argv += ["--resume", call.resume_session]
    if call.output_format == "stream-json":
        argv.append("--verbose")
    if call.tools is not None:
        argv += ["--tools", call.tools]
    if call.allowed:
        argv += ["--allowedTools", ",".join(call.allowed)]
    if call.disallowed:
        argv += ["--disallowedTools", ",".join(call.disallowed)]
    if call.system_file is not None:
        if system_prompt_flag == "file":
            argv += ["--append-system-prompt-file", str(call.system_file)]
        else:
            argv += ["--append-system-prompt", call.system_file.read_text()]
    if call.schema is not None:
        argv += ["--json-schema", json.dumps(dict(call.schema))]
    if call.max_budget_usd is not None:
        argv += ["--max-budget-usd", f"{call.max_budget_usd:.2f}"]
    for d in call.add_dirs:
        argv += ["--add-dir", d]
    if call.strict_mcp:
        argv.append("--strict-mcp-config")
    assert "--bare" not in argv
    return argv


def _walk_rate_limits(obj: Any, into: dict[str, Any]) -> None:
    """Collect `five_hour` / `seven_day` windows wherever they appear."""
    if isinstance(obj, dict):
        d = cast(dict[str, Any], obj)
        for key in ("five_hour", "seven_day"):
            win = d.get(key)
            if isinstance(win, dict):
                into[key] = cast(dict[str, Any], win)
        for v in d.values():
            _walk_rate_limits(v, into)
    elif isinstance(obj, list):
        for v in cast(list[Any], obj):
            _walk_rate_limits(v, into)


def _utilization(win: Mapping[str, Any]) -> float | None:
    for key in ("utilization", "used_percentage"):
        v = win.get(key)
        if isinstance(v, (int, float)):
            f = float(v)
            return f / 100.0 if key == "used_percentage" else f
    return None


def parse_stream(
    lines: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """The final `result` message and the last rate-limit windows seen."""
    result: dict[str, Any] | None = None
    windows: dict[str, Any] = {}
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            msg: Any = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(msg, dict):
            continue
        d = cast(dict[str, Any], msg)
        _walk_rate_limits(d, windows)
        if d.get("type") == "result":
            result = d
    return result, windows


def parse_json_output(
    text: str,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    windows: dict[str, Any] = {}
    try:
        raw: Any = json.loads(text)
    except json.JSONDecodeError:
        return parse_stream(text.splitlines())
    if isinstance(raw, list):
        items = cast(list[Any], raw)
        _walk_rate_limits(items, windows)
        results = [
            cast(dict[str, Any], m)
            for m in items
            if isinstance(m, dict)
            and cast(dict[str, Any], m).get("type") == "result"
        ]
        return (results[-1] if results else None), windows
    if isinstance(raw, dict):
        d = cast(dict[str, Any], raw)
        _walk_rate_limits(d, windows)
        return d, windows
    return None, windows


def _result_text(result: Mapping[str, Any] | None) -> str:
    if result is None:
        return ""
    r = result.get("result")
    return r if isinstance(r, str) else ""


def _structured(result: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if result is None:
        return None
    s = result.get("structured_output")
    if isinstance(s, dict):
        return cast(dict[str, Any], s)
    # Some builds put the JSON in `result` when a schema was given.
    text = _result_text(result).strip()
    if text.startswith("{"):
        try:
            parsed: Any = json.loads(text)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, dict):
            return cast(dict[str, Any], parsed)
    return None


def run(
    call: ClaudeCall,
    *,
    system_prompt_flag: SystemPromptFlag = "file",
    env: Mapping[str, str] | None = None,
) -> ClaudeResult:
    argv = build_argv(call, system_prompt_flag=system_prompt_flag)
    call.log.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    lines: list[str] = []
    with call.log.open("a", encoding="utf-8") as log:
        log.write(
            f"# ladon {call.phase} model={call.model} effort={call.effort}"
            f" max_turns={call.max_turns} at {time.strftime('%F %T')}\n"
        )
        proc = subprocess.Popen(
            argv,
            cwd=call.cwd,
            env=env_for_claude(env),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert proc.stdout is not None and proc.stderr is not None
        for line in proc.stdout:
            log.write(line)
            lines.append(line)
        stderr = proc.stderr.read()
        rc = proc.wait()
        if stderr.strip():
            log.write(f"# stderr:\n{stderr}\n")
    duration = time.monotonic() - started
    if call.output_format == "stream-json":
        result, windows = parse_stream(lines)
    else:
        result, windows = parse_json_output("".join(lines))
    text = _result_text(result)
    util: dict[str, float] = {}
    resets_at: float | None = None
    for key, win in windows.items():
        u = _utilization(win)
        if u is not None:
            util[key] = u
        ra = win.get("resets_at", win.get("resetsAt"))
        if isinstance(ra, (int, float)) and (u is None or u >= 1.0):
            resets_at = (
                float(ra) if resets_at is None else min(resets_at, float(ra))
            )
    limited = rc != 0 and (
        bool(RATE_LIMIT_RE.search(text + "\n" + stderr))
        or any(u >= 1.0 for u in util.values())
    )
    argv_error = ""
    if rc != 0 and re.search(r"unknown option|error: unknown", stderr, re.I):
        argv_error = stderr.strip().splitlines()[0] if stderr.strip() else ""
    denials = ()
    if result is not None and isinstance(
        result.get("permission_denials"), list
    ):
        denials = tuple(
            str(cast(dict[str, Any], d).get("tool_name", d))
            for d in cast(list[Any], result["permission_denials"])
        )
    return ClaudeResult(
        rc=rc,
        subtype=str((result or {}).get("subtype", "no_result")),
        text=text,
        structured=_structured(result),
        cost_usd=float((result or {}).get("total_cost_usd", 0.0) or 0.0),
        num_turns=int((result or {}).get("num_turns", 0) or 0),
        session_id=str((result or {}).get("session_id", "")),
        duration_s=duration,
        rate_limited=limited,
        resets_at=resets_at,
        utilization=util,
        denials=denials,
        stderr_tail=stderr[-2000:],
        argv_error=argv_error,
    )


def wait_seconds(
    result: ClaudeResult, attempt: int, now: float | None = None
) -> float:
    """How long to sleep before retrying a rate-limited step."""
    t = time.time() if now is None else now
    if result.resets_at is not None and result.resets_at > t:
        return min(result.resets_at - t + 60.0, BACKOFF_CAP_S)
    m = RESETS_IN_RE.search(result.text + "\n" + result.stderr_tail)
    if m and (m.group(1) or m.group(2)):
        hours = int(m.group(1) or 0)
        mins = int(m.group(2) or 0)
        return min(hours * 3600.0 + mins * 60.0 + 60.0, BACKOFF_CAP_S)
    return min(BACKOFF_FIRST_S * (2**attempt), BACKOFF_CAP_S)


def run_with_retries(
    call: ClaudeCall,
    *,
    system_prompt_flag: SystemPromptFlag,
    env: Mapping[str, str] | None = None,
    on_wait: Callable[[ClaudeResult, float], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[ClaudeResult, SystemPromptFlag, float]:
    """
    Run `call`, waiting through usage limits (cumulative cap
    `BACKOFF_CAP_S`) and falling back from the hidden
    `--append-system-prompt-file` flag to the inline one on an argv
    error. Returns the result, the flag that worked and the seconds
    waited.
    """
    waited = 0.0
    attempt = 0
    flag = system_prompt_flag
    while True:
        result = run(call, system_prompt_flag=flag, env=env)
        if (
            result.argv_error
            and flag == "file"
            and call.system_file is not None
        ):
            flag = "inline"
            continue
        if not result.rate_limited:
            return result, flag, waited
        delay = wait_seconds(result, attempt)
        if waited + delay > BACKOFF_CAP_S:
            return result, flag, waited
        if on_wait is not None:
            on_wait(result, delay)
        sleep(delay)
        waited += delay
        attempt += 1


def probe(model: str = "sonnet", log: Path | None = None) -> ClaudeResult:
    """One-turn structured call: proves auth, model access and schema."""
    call = ClaudeCall(
        phase="probe",
        prompt='Reply with the JSON object {"ok": true, "model": "<your model>"}.',
        model=model,
        effort="low",
        max_turns=1,
        log=log or (_OMPHALOS_DIR / "ladon" / "nights" / "probe.jsonl"),
        output_format="json",
        tools="",
        schema={
            "type": "object",
            "required": ["ok"],
            "properties": {
                "ok": {"type": "boolean"},
                "model": {"type": "string"},
            },
        },
    )
    return run(call)
