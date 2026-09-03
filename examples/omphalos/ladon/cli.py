"""
Ladon — the orchestrator of the overnight improvement loop.

    python -m ladon.cli night [--max_hints=3] [--wallclock_h=9] ...
    python -m ladon.cli resume [--date=YYYY-MM-DD]
    python -m ladon.cli status | report | selftest | launch | preflight

A night is a persisted state machine (`ladon/state.py`): preflight,
baseline, plan, then one hint at a time through implement → guard →
screen → select → reverify → judge → evaluate → record, then the
report. Every step re-reads and re-writes `night.yaml`, so `resume`
continues from wherever a crash, a usage-limit halt or a SIGTERM left
things. The language model is used in three narrow places — the plan
session ranks and classifies hints, the implement session writes the
arm, the evaluate session writes the prose — and everything that
decides money or truth (launching, pairing, the sign tests, the
pristine re-check, the frozen-path guard, the gates, the commit) is
plain Python in this package.

Model policy (`MODEL_POLICY`): planning and design-class hints on
Opus, knob-class hints and all evaluation prose on Sonnet. INSPECT
verdicts are never followed up by the loop: they are marked "inspect
with Fable" for a human-driven session (Guille's rule, 2026-09-02).
"""

# pyright: strict

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import textwrap
import time
import traceback
from collections.abc import Callable, Mapping, Sequence
from datetime import date as _date
from datetime import datetime, timedelta
from pathlib import Path
from string import Template
from typing import Any, cast

import fire  # type: ignore
import yaml

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
for _sub in ("", "experiments", "tools"):
    _p = str(_OMPHALOS_DIR / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import omphalos_launch as ol  # noqa: E402
import stop_launches as sl  # noqa: E402

from ladon import bench  # noqa: E402
from ladon import claude_driver as C  # noqa: E402
from ladon import guard  # noqa: E402
from ladon import hints as H  # noqa: E402
from ladon import launch as L  # noqa: E402
from ladon import report as RP  # noqa: E402
from ladon import reverify as RV  # noqa: E402
from ladon import state as S  # noqa: E402
from ladon import verdict as V  # noqa: E402

LADON_DIR = _OMPHALOS_DIR / "ladon"
NIGHTS_DIR = LADON_DIR / "nights"
LEDGER = LADON_DIR / "ledger.tsv"
LATEST = LADON_DIR / "LATEST_REPORT.md"
PROMPTS = LADON_DIR / "prompts"
SYSTEM_FILE = LADON_DIR / "LADON.md"
PROGRESS = _OMPHALOS_DIR / "PROGRESS.md"
HINTS = _OMPHALOS_DIR / "HINTS.md"
BASELINE_SCRIPT = _OMPHALOS_DIR / "experiments" / "x_ladon_experiment.py"
BASELINE_DIR = _OMPHALOS_DIR / bench.BASELINE_DIR
DRY_BASELINE_DIR = _OMPHALOS_DIR / "experiments" / "output" / "x_train_agentic"
COMMANDS_DIR = _OMPHALOS_DIR / "commands"

MODEL_POLICY: dict[str, tuple[str, str, int]] = {
    "plan": ("opus", "high", 25),
    "A": ("sonnet", "medium", 40),
    "B": ("sonnet", "medium", 60),
    "C": ("opus", "high", 120),
    "evaluate": ("sonnet", "medium", 5),
}
"""(model, effort, max turns) per session kind / hint class."""

CLASS_ESTIMATES: dict[str, tuple[float, float]] = {
    "A": (40.0, 0.0),
    "B": (200.0, 2.5),
    "C": (260.0, 3.0),
}
"""(wall-clock minutes end to end, OpenAI dollars) per hint class."""

SESSION_BUDGET_USD = 15.0
SMOKE_MAX_USD = 0.25
SMOKE_MIN_DONE = 3
SMOKE_MIN_SOLVED = 2
BASELINE_TIMEOUT_S = 6 * 3600.0
SEVEN_DAY_HALT = 0.90
"""Halt before the next session when the weekly window is this used."""
LAUNCH_REFUSED_RETRIES = 2
LAUNCH_REFUSED_SLEEP_S = 300.0
EVALUATE_RETRIES = 2
WRAP = 72

ALLOWED_TOOLS: tuple[str, ...] = (
    "Read",
    "Edit",
    "Write",
    "Glob",
    "Grep",
    "WebFetch",
    "Bash(python:*)",
    "Bash(python3:*)",
    "Bash(LADON_SMOKE=1:*)",
    "Bash(cd:*)",
    "Bash(make test-unit:*)",
    "Bash(make test:*)",
    "Bash(make test-rocq:*)",
    "Bash(make bridge-parity:*)",
    "Bash(make pyright:*)",
    "Bash(make reprice:*)",
    "Bash(ruff:*)",
    "Bash(pyright:*)",
    "Bash(rg:*)",
    "Bash(grep:*)",
    "Bash(find:*)",
    "Bash(ls:*)",
    "Bash(cat:*)",
    "Bash(head:*)",
    "Bash(tail:*)",
    "Bash(wc:*)",
    "Bash(sed -n:*)",
    "Bash(diff:*)",
    "Bash(mkdir:*)",
    "Bash(cp:*)",
    "Bash(mv:*)",
    "Bash(echo:*)",
    "Bash(tee:*)",
    "Bash(sort:*)",
    "Bash(uniq:*)",
    "Bash(cut:*)",
    "Bash(awk:*)",
    "Bash(tr:*)",
    "Bash(xargs:*)",
    "Bash(test:*)",
    "Bash(true:*)",
    "Bash(for:*)",
    "Bash(while:*)",
    "Bash(if:*)",
    "Bash(git diff:*)",
    "Bash(git status:*)",
    "Bash(git log:*)",
    "Bash(git show:*)",
    "Bash(git ls-files:*)",
)
DISALLOWED_TOOLS: tuple[str, ...] = (
    "Task",
    "NotebookEdit",
    "Bash(git commit:*)",
    "Bash(git push:*)",
    "Bash(git add:*)",
    "Bash(git reset:*)",
    "Bash(git checkout:*)",
    "Bash(git restore:*)",
    "Bash(git stash:*)",
    "Bash(git worktree:*)",
    "Bash(git rm:*)",
    "Bash(git clean:*)",
    "Bash(rm -rf:*)",
    "Bash(rm -r:*)",
    "Bash(rm -fr:*)",
    "Bash(make clean:*)",
    "Bash(make clean-experiments:*)",
    "Bash(make regen-command-caches:*)",
    "Bash(make reprice-write:*)",
    "Bash(make stop:*)",
    "Bash(pkill:*)",
    "Bash(kill:*)",
    "Bash(killall:*)",
)

PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["ranked", "skipped"],
    "properties": {
        "ranked": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "hint",
                    "class",
                    "expected_effect",
                    "arm",
                    "risk",
                    "rationale",
                ],
                "properties": {
                    "hint": {"type": "integer"},
                    "class": {"type": "string", "enum": ["A", "B", "C", "D"]},
                    "expected_effect": {
                        "type": "string",
                        "enum": ["solves", "cost", "both", "analysis"],
                    },
                    "arm": {"type": "string"},
                    "knob": {"type": "string"},
                    "files": {"type": "array", "items": {"type": "string"}},
                    "risk": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                    },
                    "est_minutes": {"type": "integer"},
                    "rationale": {"type": "string"},
                },
            },
        },
        "skipped": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["hint", "why"],
                "properties": {
                    "hint": {"type": "integer"},
                    "why": {"type": "string"},
                },
            },
        },
    },
}

EVAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "progress_bullet",
        "hints_marker",
        "new_hints",
        "commit_body",
    ],
    "properties": {
        "progress_bullet": {"type": "string"},
        "hints_marker": {"type": "string"},
        "new_hints": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["tag", "title", "body"],
                "properties": {
                    "tag": {"type": "string"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                },
            },
        },
        "commit_body": {"type": "string"},
        "human_note": {"type": "string"},
    },
}


class Halt(Exception):
    """Stop the night now (usage limit, budget, infrastructure)."""


def _now() -> datetime:
    return datetime.now()


def _render(name: str, **values: Any) -> str:
    return Template((PROMPTS / name).read_text()).substitute(**values)


def _yaml_dump(obj: Any) -> str:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)


def _progress_head(text: str, limit: int = 7000) -> str:
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if H.HEADING_RE.match(ln)]
    if not starts:
        return text[:limit]
    end = starts[1] if len(starts) > 1 else len(lines)
    return "\n".join(lines[starts[0] : end])[:limit]


def _progress_examples(text: str, k: int = 2) -> str:
    head = _progress_head(text, limit=200_000).splitlines()
    out: list[str] = []
    i = 0
    while i < len(head) and len(out) < k:
        if head[i].startswith("- **"):
            block = [head[i]]
            i += 1
            while (
                i < len(head)
                and head[i].strip()
                and not head[i].startswith("- ")
            ):
                block.append(head[i])
                i += 1
            out.append("\n".join(block))
        else:
            i += 1
    return "\n\n".join(out)


def _hints_examples(text: str, k: int = 2) -> str:
    lines = text.splitlines()
    picks = [h for h in H.parse_hints(text) if h.status == "open"][:k]
    return "\n\n".join(
        "\n".join(lines[h.first_line : h.last_line + 1]) for h in picks
    )


def _spend(cells: Sequence[Any]) -> float:
    return float(sum(float(getattr(c, "cost", 0.0)) for c in cells))


def _parse_hint_numbers(raw: Any) -> list[int]:
    if raw is None:
        return []
    if isinstance(raw, int):
        return [raw]
    if isinstance(raw, str):
        return [int(x) for x in raw.replace(";", ",").split(",") if x.strip()]
    return [int(x) for x in cast(Sequence[Any], raw)]


#####
##### The night runner
#####


class Ladon:
    def __init__(
        self,
        night: S.Night,
        *,
        root: Path = NIGHTS_DIR,
        no_claude: bool = False,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self.night = night
        self.dir = root / night.date
        self.path = self.dir / "night.yaml"
        self.log_path = self.dir / "ladon.log"
        self.no_claude = no_claude
        self.env = dict(env if env is not None else os.environ)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.system_prompt_flag: C.SystemPromptFlag = cast(
            C.SystemPromptFlag, night.claude.get("system_prompt_flag", "file")
        )

    # ---- plumbing --------------------------------------------------------

    def log(self, msg: str) -> None:
        line = f"[ladon {time.strftime('%H:%M:%S')}] {msg}"
        print(line, flush=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def save(self) -> None:
        self.night.claude["system_prompt_flag"] = self.system_prompt_flag
        S.save(self.night, self.path)

    def hint_dir(self, n: int) -> Path:
        d = self.dir / "hints" / f"h{n}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def budget(self) -> dict[str, Any]:
        return self.night.budget

    @property
    def deadline(self) -> datetime:
        started = datetime.fromisoformat(self.night.started_at)
        return started + timedelta(
            hours=float(self.budget.get("wallclock_h", 9.0))
        )

    def minutes_left(self) -> float:
        return (self.deadline - _now()).total_seconds() / 60.0

    @property
    def max_workers(self) -> int:
        return int(self.budget.get("max_workers", 4))

    @property
    def baseline_dir(self) -> Path:
        return DRY_BASELINE_DIR if self.night.dry else BASELINE_DIR

    def knowledge_file(self, name: str) -> Path:
        """`PROGRESS.md` / `HINTS.md`, or their dry-night copies."""
        real = _OMPHALOS_DIR / name
        if not self.night.dry:
            return real
        copy = self.dir / "dry" / name
        if not copy.exists():
            copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(real, copy)
        return copy

    def arm_names(self, n: int) -> tuple[str, str, str]:
        stem = f"ladon_{self.night.date}_h{n}"
        return (
            f"experiments/{stem}_experiment.py",
            f"experiments/output/{stem}_agentic",
            f"experiments/output/{stem}_smoke",
        )

    # ---- Claude sessions -------------------------------------------------

    def session(
        self, call: C.ClaudeCall, h: S.HintRun | None
    ) -> C.ClaudeResult:
        """Run one session with usage-limit waits; account for it."""
        if self.no_claude:
            raise Halt("no_claude: a session was required")
        self.check_quota()

        def on_wait(res: C.ClaudeResult, delay: float) -> None:
            self.log(
                f"{call.phase}: usage limit hit ({res.utilization});"
                f" waiting {delay / 60:.0f} min"
            )
            self.night.rate_limit_events.append(
                {
                    "at": S.now_iso(),
                    "phase": call.phase,
                    "hint": h.n if h else None,
                    "waited_s": delay,
                    "utilization": res.utilization,
                    "resets_at": res.resets_at,
                }
            )
            self.night.spent["minutes_waited"] += delay / 60.0
            self.save()

        result, flag, _waited = C.run_with_retries(
            call,
            system_prompt_flag=self.system_prompt_flag,
            env=self.env,
            on_wait=on_wait,
        )
        self.system_prompt_flag = flag
        record = {
            "phase": call.phase,
            "model": call.model,
            "effort": call.effort,
            "subtype": result.subtype,
            "rc": result.rc,
            "turns": result.num_turns,
            "cost_usd": result.cost_usd,
            "duration_s": round(result.duration_s),
            "denials": list(result.denials),
            "utilization": result.utilization,
            "log": str(call.log.relative_to(_OMPHALOS_DIR)),
        }
        if h is not None:
            h.sessions.append(record)
            h.claude_cost_usd += result.cost_usd
        else:
            self.night.plan.setdefault("sessions", []).append(record)
        self.night.spent["usd_claude"] += result.cost_usd
        if result.utilization:
            self.night.claude["utilization"] = result.utilization
        self.save()
        if result.rate_limited:
            raise Halt("usage limit: waited the maximum for one step")
        return result

    def check_quota(self) -> None:
        util = cast(dict[str, float], self.night.claude.get("utilization", {}))
        if util.get("seven_day", 0.0) >= SEVEN_DAY_HALT:
            raise Halt(
                f"weekly usage at {util['seven_day']:.0%} — leaving the rest"
                " for daytime work"
            )
        if self.night.spent["usd_claude"] >= float(
            self.budget.get("claude_cap_usd", 25.0)
        ):
            raise Halt("Claude spend estimate reached the night's cap")

    def base_call(
        self, phase: str, kind: str, prompt: str, log: Path, **kw: Any
    ) -> C.ClaudeCall:
        model, effort, turns = MODEL_POLICY[kind]
        overrides = cast(dict[str, Any], self.budget.get("models", {}))
        model = str(overrides.get(kind, model))
        return C.ClaudeCall(
            phase=phase,
            prompt=prompt,
            model=model,
            effort=effort,
            max_turns=turns,
            log=log,
            system_file=SYSTEM_FILE,
            **kw,
        )

    # ---- night steps -----------------------------------------------------

    def run(self) -> int:
        n = self.night
        try:
            if n.state == "created":
                self.preflight()
            if n.state == "preflight_ok":
                self.ensure_baseline()
            if n.state == "baseline_ok":
                self.plan()
            if n.state == "planned":
                n.enter("running")
                self.save()
            if n.state == "running":
                self.run_hints()
                n.enter("reporting")
                self.save()
            if n.state == "reporting":
                n.enter("done")
                self.save()
                self.finish()
        except Halt as e:
            self.log(f"HALT: {e}")
            n.enter("halted", str(e))
            self.save()
            self.finish()
            return 2
        except KeyboardInterrupt:
            self.log("interrupted — state saved; `resume` continues")
            n.event("interrupted")
            self.save()
            return 130
        except Exception as e:  # noqa: BLE001 — recorded, reported
            self.log(
                f"CRASH: {type(e).__name__}: {e}\n{traceback.format_exc()}"
            )
            n.enter("halted", f"{type(e).__name__}: {e}")
            self.save()
            self.finish()
            return 2
        finally:
            self.cleanup_worktree()
        self.log(f"night {n.state}; report: {self.dir / 'REPORT.md'}")
        return 0 if n.state == "done" else 2

    def preflight(self) -> None:
        n = self.night
        checks = preflight_checks(dry=n.dry, no_claude=self.no_claude)
        n.preflight = {"checks": checks, "at": S.now_iso()}
        n.base_sha = guard.head_sha()
        n.branch = guard.current_branch()
        failed = [k for k, v in checks.items() if not v.startswith("ok")]
        for k, v in checks.items():
            self.log(f"preflight {k}: {v}")
        if failed:
            n.enter("halted", "preflight failed: " + ", ".join(failed))
            self.save()
            raise Halt("preflight failed: " + ", ".join(failed))
        n.enter("preflight_ok")
        self.save()

    def ensure_baseline(self) -> None:
        n = self.night
        counts = L.counts(self.baseline_dir)
        n.baseline.update(
            {
                "dir": str(self.baseline_dir.relative_to(_OMPHALOS_DIR)),
                "counts": str(counts),
            }
        )
        if n.dry:
            n.baseline["note"] = (
                "dry night pairs against the archived trainX baseline"
            )
        elif not counts.complete or counts.done < 80:
            self.log(
                f"baseline {counts}; launching {BASELINE_SCRIPT.name} (up to {BASELINE_TIMEOUT_S / 3600:.0f} h)"
            )
            n.event("baseline launch")
            self.save()
            res = L.launch_arm(
                BASELINE_SCRIPT,
                run_dir=self.baseline_dir,
                seeds=(0, 1),
                max_workers=self.max_workers,
                timeout_s=BASELINE_TIMEOUT_S,
                log=self.dir / "baseline.log",
                env=self.env,
                tick=lambda t, c: self.log(f"baseline {t / 60:.0f} min: {c}"),
            )
            counts = res.counts
            # Platform-failed cells (a request timeout, a broken worker)
            # are retried once, as the hint tiers do; a cell that fails
            # twice is a real halt.
            if not res.timed_out and counts.failed and counts.todo == 0:
                self.log(f"baseline {counts}; retrying the failed cell(s)")
                res = L.launch_arm(
                    BASELINE_SCRIPT,
                    run_dir=self.baseline_dir,
                    seeds=(0, 1),
                    max_workers=self.max_workers,
                    timeout_s=BASELINE_TIMEOUT_S,
                    log=self.dir / "baseline.log",
                    env=self.env,
                    retry_errors=True,
                    tick=lambda t, c: self.log(
                        f"baseline retry {t / 60:.0f} min: {c}"
                    ),
                )
                counts = res.counts
            n.baseline["counts"] = str(counts)
            n.baseline["wall_s"] = (
                float(n.baseline.get("wall_s", 0.0)) + res.wall_s
            )
            # Idempotent across resumes: the baseline's cells are charged
            # once, at their current total, never re-added per attempt.
            spend = _spend(V.load_cells(self.baseline_dir))
            n.spent["usd_openai"] += spend - float(
                n.baseline.get("spend_usd", 0.0)
            )
            n.baseline["spend_usd"] = spend
            if res.timed_out or not counts.complete:
                raise Halt(f"baseline incomplete: {counts} (rc={res.rc})")
            n.baseline["note"] = (
                f"run tonight in {float(n.baseline['wall_s']) / 60:.0f} min"
            )
        n.enter("baseline_ok")
        self.save()

    def plan(self) -> None:
        n = self.night
        hints_text = self.knowledge_file("HINTS.md").read_text()
        pinned = _parse_hint_numbers(self.budget.get("hints"))
        open_hints = H.open_hints(hints_text)
        by_n = {h.n: h for h in H.parse_hints(hints_text)}
        max_hints = int(self.budget.get("max_hints", 3))
        ranked: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        if n.dry:
            ranked = [
                {
                    "hint": 0,
                    "class": "B",
                    "expected_effect": "solves",
                    "arm": "dry-night arm: the canonical configuration itself on the smoke cells",
                    "files": [],
                    "risk": "low",
                    "rationale": "exercises every transition without a model",
                    "title": "Dry-night synthetic arm",
                    "tag": "experiment",
                }
            ]
        else:
            pool = (
                [by_n[k] for k in pinned if k in by_n]
                if pinned
                else open_hints
            )
            missing = [k for k in pinned if k not in by_n]
            if missing:
                raise Halt(f"pinned hints not found: {missing}")
            if self.no_claude:
                if not pinned:
                    raise Halt("no_claude requires --hints")
                ranked = [
                    {
                        "hint": h.n,
                        "class": "B",
                        "expected_effect": "both",
                        "arm": h.body[:400],
                        "files": [],
                        "risk": "medium",
                        "rationale": "pinned by hand (no planning session)",
                    }
                    for h in pool
                ]
            else:
                ranked, skipped = self.plan_session(pool, max_hints)
            for entry in ranked:
                hint = by_n[int(entry["hint"])]
                entry["title"] = hint.title
                entry["tag"] = hint.tag
        ranked = self.validate_plan(ranked, by_n, max_hints)
        n.plan = {
            **n.plan,
            "ranked": ranked,
            "skipped": skipped,
            "max_hints": max_hints,
        }
        (self.dir / "plan.yaml").write_text(_yaml_dump(n.plan))
        for entry in ranked:
            k = int(entry["hint"])
            n.hints[k] = S.HintRun(
                n=k,
                title=str(entry.get("title", "")),
                tag=str(entry.get("tag", "")),
                hint_class=str(entry["class"]),
                plan=entry,
            )
            n.order.append(k)
        for entry in skipped:
            why = str(entry.get("why", ""))
            if why.startswith("D:") and int(entry["hint"]) in by_n:
                n.human.append(
                    {"hint": int(entry["hint"]), "why": why[2:].strip()}
                )
                self.mark_hint(
                    int(entry["hint"]),
                    f"LADON HUMAN {n.date} — structural: {why[2:].strip()}",
                )
        heading = H.progress_heading(n.date, "in progress")
        intro = textwrap.fill(
            f"Ladon night started {n.started_at} on `{n.branch}` at"
            f" `{(n.base_sha or '')[:8]}`; baseline `{n.baseline.get('dir')}`"
            f" ({n.baseline.get('counts')}); plan: "
            + ", ".join(f"#{k} ({n.hints[k].hint_class})" for k in n.order)
            + f"; budget {max_hints} hints, {self.budget.get('wallclock_h')} h,"
            f" ${self.budget.get('cap_usd')} OpenAI. Verdicts land below as"
            " they are made; the morning report is"
            f" `ladon/nights/{n.date}/REPORT.md`.",
            WRAP,
        )
        progress = self.knowledge_file("PROGRESS.md")
        progress.write_text(
            H.insert_progress_section(progress.read_text(), heading, intro)
        )
        n.plan["progress_heading"] = heading
        self.log(
            f"plan: {[k for k in n.order]}; human: {[x['hint'] for x in n.human]}"
        )
        n.enter("planned")
        self.save()

    def plan_session(
        self, pool: Sequence[H.Hint], max_hints: int
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        n = self.night
        ledger_rows = RP.read_ledger(LEDGER)
        ledger = (
            "\n".join(
                f"- {r.get('night')}: hint {r.get('hint')} → {r.get('outcome')}"
                f" ({r.get('rule')}): {r.get('note', '')}"
                for r in ledger_rows
            )
            or "- none yet"
        )
        prompt = _render(
            "plan.md",
            date=n.date,
            max_hints=max_hints,
            max_ranked=max_hints + 2,
            wallclock_h=self.budget.get("wallclock_h"),
            cap_usd=self.budget.get("cap_usd"),
            ledger=ledger,
            progress_head=_progress_head(PROGRESS.read_text()),
            hints="\n".join(H.render_hint_context(h) for h in pool),
        )
        (self.dir / "plan_prompt.md").write_text(prompt)
        call = self.base_call(
            "plan",
            "plan",
            prompt,
            self.dir / "plan.jsonl",
            output_format="json",
            tools="Read,Glob,Grep",
            schema=PLAN_SCHEMA,
            add_dirs=(str(guard.REPO / "src"),),
        )
        result = self.session(call, None)
        if result.structured is None:
            call2 = self.base_call(
                "plan",
                "plan",
                prompt,
                self.dir / "plan.jsonl",
                output_format="json",
                tools="Read,Glob,Grep",
                schema=PLAN_SCHEMA,
                add_dirs=(str(guard.REPO / "src"),),
            )
            result = self.session(call2, None)
            if result.structured is None:
                raise Halt(
                    f"plan session returned no structured output ({result.subtype})"
                )
        ranked = cast(
            list[dict[str, Any]], result.structured.get("ranked", [])
        )
        skipped = cast(
            list[dict[str, Any]], result.structured.get("skipped", [])
        )
        return ranked, skipped

    def validate_plan(
        self,
        ranked: Sequence[dict[str, Any]],
        by_n: Mapping[int, H.Hint],
        max_hints: int,
    ) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        seen_files: set[str] = set()
        seen_hints: set[int] = set()
        prefer_a = {
            int(e["hint"])
            for e in ranked
            if str(e.get("class")) == "A" and "hint" in e
        }
        ordered = [e for e in ranked if str(e.get("class")) == "A"] + [
            e for e in ranked if str(e.get("class")) != "A"
        ]
        for entry in ordered:
            try:
                k = int(entry["hint"])
            except (KeyError, TypeError, ValueError):
                continue
            if k in seen_hints:
                self.log(f"plan: dropping a second entry for #{k}")
                continue
            if k in prefer_a and str(entry.get("class")) != "A":
                continue
            seen_hints.add(k)
            if self.night.dry and k == 0:
                out.append(dict(entry))
                continue
            hint = by_n.get(k)
            if hint is None or not hint.open:
                self.log(f"plan: dropping #{k} (not an open hint)")
                continue
            cls = str(entry.get("class", "B"))
            files = [str(f) for f in cast(list[Any], entry.get("files") or [])]
            frozen = [f for f in files if guard.is_frozen(f)]
            if cls == "D" or frozen:
                why = "D: " + (
                    f"would touch frozen {frozen}"
                    if frozen
                    else str(entry.get("rationale", ""))
                )
                self.night.human.append({"hint": k, "why": why[3:]})
                self.mark_hint(
                    k, f"LADON HUMAN {self.night.date} — structural: {why[3:]}"
                )
                continue
            if cls not in ("A", "B", "C"):
                cls = "B"
            overlap = seen_files & set(files)
            if overlap:
                self.log(
                    f"plan: dropping #{k} (shares {sorted(overlap)} with an earlier hint)"
                )
                continue
            seen_files |= set(files)
            e = dict(entry)
            e["class"] = cls
            out.append(e)
            if len(out) >= max_hints + 2:
                break
        return out

    def run_hints(self) -> None:
        n = self.night
        for k in list(n.order):
            h = n.hints[k]
            if h.finished:
                continue
            if h.state == "queued":
                reason = self.cannot_start(h)
                if reason:
                    h.reason = reason
                    h.outcome = None
                    h.enter("skipped")
                    n.event(f"hint {k} skipped: {reason}")
                    self.save()
                    continue
            self.run_hint(h)

    def cannot_start(self, h: S.HintRun) -> str | None:
        n = self.night
        attempted = sum(
            1
            for x in n.hints.values()
            if x.state != "queued" and x.state != "skipped"
        )
        if attempted >= int(self.budget.get("max_hints", 3)):
            return "night's hint quota reached"
        minutes, usd = CLASS_ESTIMATES.get(h.hint_class, CLASS_ESTIMATES["B"])
        if self.minutes_left() < minutes:
            return f"not enough wall-clock left ({self.minutes_left():.0f} min < {minutes:.0f})"
        if n.spent["usd_openai"] + usd > float(
            self.budget.get("cap_usd", 12.0)
        ):
            return "OpenAI cap would be exceeded"
        try:
            self.check_quota()
        except Halt as e:
            return str(e)
        return None

    def run_hint(self, h: S.HintRun) -> None:
        steps: dict[str, Callable[[S.HintRun], None]] = {
            "queued": self.step_implement,
            "implementing": self.step_implement,
            "implemented": self.step_guard,
            "guarded": self.step_screen,
            "screening": self.step_screen,
            "screened": self.step_select,
            "selecting": self.step_select,
            "selected": self.step_reverify,
            "reverifying": self.step_reverify,
            "judged": self.step_evaluate,
            "evaluated": self.step_record,
        }
        while not h.finished:
            step = steps[h.state]
            self.log(f"hint {h.n}: {h.state} -> {step.__name__}")
            try:
                step(h)
            except Halt:
                self.save()
                raise
            except KeyboardInterrupt:
                self.save()
                raise
            except Exception as e:  # noqa: BLE001 — one hint must not end the night
                self.log(
                    f"hint {h.n}: {type(e).__name__}: {e}\n{traceback.format_exc()}"
                )
                h.error = f"{type(e).__name__}: {e}"
                if h.state in ("judged", "evaluated"):
                    # Recording must complete; fall back to the numbers-only record.
                    h.evaluation = h.evaluation or {}
                    if h.state == "judged":
                        h.enter("evaluated")
                    else:
                        h.enter("recorded")
                else:
                    self.judge_now(h, "HUMAN", "infra", h.error)
            self.save()

    def judge_now(
        self, h: S.HintRun, outcome: str, rule: str, reason: str
    ) -> None:
        h.outcome, h.rule, h.reason = outcome, rule, reason
        h.enter("judged")

    # ---- hint steps ------------------------------------------------------

    def step_implement(self, h: S.HintRun) -> None:
        n = self.night
        d = self.hint_dir(h.n)
        script, out_dir, smoke_dir = self.arm_names(h.n)
        h.script, h.output_dir, h.smoke_dir = script, out_dir, smoke_dir
        h.notes = str((d / "notes.md").relative_to(_OMPHALOS_DIR))
        if h.hint_class == "D":
            self.judge_now(
                h, "HUMAN", "structural", "class D is never implemented"
            )
            return
        snap_path = d / "snapshot_before.json"
        if h.state == "queued" or not snap_path.exists():
            before = guard.take()
            snap_path.write_text(json.dumps(_snapshot_to_dict(before)))
            h.head_before = before.head
            h.enter("implementing")
            self.save()
        else:
            before = _snapshot_from_dict(json.loads(snap_path.read_text()))
        arm_yaml = d / "arm.yaml"
        if n.dry:
            self.write_dry_arm(h)
        elif not arm_yaml.exists():
            hints_text = self.knowledge_file("HINTS.md").read_text()
            hint = H.find_hint(hints_text, h.n)
            context = H.render_hint_context(hint) if hint else h.title
            common = dict(
                hint_n=h.n,
                hint_class=h.hint_class,
                date=n.date,
                hint_context=context,
                plan_entry=_yaml_dump(h.plan),
                notes=h.notes,
                arm_yaml=str(arm_yaml.relative_to(_OMPHALOS_DIR)),
                max_turns=MODEL_POLICY[h.hint_class][2],
            )
            if h.hint_class == "A":
                prompt = _render(
                    "analysis.md",
                    hint_dir=str(d.relative_to(_OMPHALOS_DIR)),
                    analysis=str(
                        (d / "analysis.md").relative_to(_OMPHALOS_DIR)
                    ),
                    **common,
                )
            else:
                template = _render(
                    "arm_template.py.txt",
                    hint_n=h.n,
                    title=h.title,
                    date=n.date,
                    script=script,
                    smoke_dir=smoke_dir,
                    output_dir=out_dir,
                )
                prompt = _render(
                    "implement.md",
                    script=script,
                    output_dir=out_dir,
                    smoke_dir=smoke_dir,
                    template=template,
                    **common,
                )
            (d / "implement_prompt.md").write_text(prompt)
            call = self.base_call(
                "implement",
                h.hint_class,
                prompt,
                d / "implement.jsonl",
                permission_mode="bypassPermissions"
                if self.budget.get("yolo")
                else "acceptEdits",
                allowed=ALLOWED_TOOLS,
                disallowed=DISALLOWED_TOOLS,
                max_budget_usd=SESSION_BUDGET_USD,
                add_dirs=(str(guard.REPO / "src"),),
            )
            result = self.session(call, h)
            h.evaluation["implement_subtype"] = result.subtype
            if result.hit_max_turns:
                self.log(f"hint {h.n}: implement session hit its turn cap")
        after = guard.take()
        m = guard.manifest(before, after)
        h.guard = {
            "manifest": _manifest_to_dict(m),
            "violations": guard.violations(
                m,
                allowed_output=lambda name: (
                    name in (Path(out_dir).name, Path(smoke_dir).name)
                ),
                allowed_script=lambda rel: rel == script,
            ),
            "verifier_touched": guard.verifier_touched(m),
        }
        h.fingerprint = guard.fingerprint(m)
        arm = _load_arm(arm_yaml)
        h.arm = arm
        if h.hint_class == "A":
            self.judge_now(
                h, "INSPECT", "analysis", "offline analysis: read the artifact"
            )
            return
        if not arm or not arm.get("ready", False):
            why = str(arm.get("summary") or "no valid arm.yaml / ready: false")
            self.judge_now(h, "INSPECT", "no-arm", why)
            return
        if (
            str(arm.get("script")) != script
            or str(arm.get("output_dir")) != out_dir
        ):
            self.judge_now(
                h,
                "INSPECT",
                "no-arm",
                "arm.yaml names a different script/output dir",
            )
            return
        if not (_OMPHALOS_DIR / script).exists():
            self.judge_now(h, "INSPECT", "no-arm", f"{script} missing")
            return
        h.enter("implemented")

    def write_dry_arm(self, h: S.HintRun) -> None:
        """The dry night's arm: the canonical config on the smoke cells."""
        script, out_dir, smoke_dir = self.arm_names(h.n)
        text = _render(
            "arm_template.py.txt",
            hint_n=h.n,
            title=h.title,
            date=self.night.date,
            script=script,
            smoke_dir=smoke_dir,
            output_dir=out_dir,
        ).replace("tuple(bench.LADONX_PROBLEMS)", "bench.SMOKE_PROBLEMS")
        (_OMPHALOS_DIR / script).write_text(text)
        d = self.hint_dir(h.n)
        (d / "notes.md").write_text(
            "# Dry-night arm\n\nCanonical configuration on the three smoke"
            " cells; no product change.\n\n## New hints\n\n- none\n"
        )
        (d / "arm.yaml").write_text(
            _yaml_dump(
                {
                    "hint": h.n,
                    "class": "B",
                    "title": h.title,
                    "summary": "dry night: baseline configuration on the smoke cells",
                    "script": script,
                    "output_dir": out_dir,
                    "smoke_dir": smoke_dir,
                    "expected_effect": "solves",
                    "touched": [script],
                    "smoke": {
                        "done": 0,
                        "failed": 0,
                        "solved": 0,
                        "spend_usd": 0.0,
                    },
                    "preregistration": "dry night",
                    "ready": True,
                }
            )
        )

    def step_guard(self, h: S.HintRun) -> None:
        violations = cast(list[str], h.guard.get("violations", []))
        if violations:
            self.judge_now(
                h, "DISCARD", "frozen-path", "; ".join(violations)[:500]
            )
            return
        if not self.night.dry:
            smoke_cells = V.load_cells(_OMPHALOS_DIR / str(h.smoke_dir))
            done = [c for c in smoke_cells if not c.platform_failed]
            solved = sum(1 for c in done if c.solved)
            spend = _spend(smoke_cells)
            h.smoke_spend_usd = spend
            self.night.spent["usd_openai"] += spend
            h.arm["smoke_measured"] = {
                "done": len(done),
                "solved": solved,
                "spend_usd": spend,
            }
            if len(done) < SMOKE_MIN_DONE or solved < SMOKE_MIN_SOLVED:
                self.judge_now(
                    h,
                    "INSPECT",
                    "smoke",
                    f"smoke {len(done)} done / {solved} solved of {SMOKE_MIN_DONE}",
                )
                return
            if spend > SMOKE_MAX_USD:
                self.judge_now(
                    h, "INSPECT", "smoke", f"smoke spent ${spend:.2f}"
                )
                return
        h.enter("guarded")

    def _check_drift(self, h: S.HintRun) -> bool:
        m = _manifest_from_dict(cast(dict[str, Any], h.guard["manifest"]))
        current = guard.fingerprint(m)
        if current != h.fingerprint:
            self.judge_now(
                h,
                "INSPECT",
                "code-drift",
                "touched files changed since the session",
            )
            return True
        return False

    def _launch_tier(
        self, h: S.HintRun, seeds: Sequence[int], tier: str
    ) -> L.LaunchResult | None:
        """Run the arm for `seeds`; None when the hint was judged."""
        assert h.script and h.output_dir
        script = _OMPHALOS_DIR / h.script
        run_dir = _OMPHALOS_DIR / h.output_dir
        cells = [(b, str(s)) for s in seeds for b in self.arm_problems()]
        expected = L.expected_seconds(
            self.baseline_dir, cells, self.max_workers
        )
        dry_timeout = self.budget.get("dry_timeout_s")
        timeout = (
            float(dry_timeout) if dry_timeout else expected * L.KILL_FACTOR
        )
        rec: dict[str, Any] = {
            "expected_s": expected,
            "timeout_s": timeout,
            "attempts": [],
            "wall_s": 0.0,
        }
        res: L.LaunchResult | None = None
        retry_errors = False
        outcome = "incomplete"
        for attempt in range(LAUNCH_REFUSED_RETRIES + 1):
            res = L.launch_arm(
                script,
                run_dir=run_dir,
                seeds=seeds,
                max_workers=self.max_workers,
                timeout_s=timeout,
                log=self.hint_dir(h.n) / f"{tier}.log",
                env=self.env,
                retry_errors=retry_errors,
                tick=lambda t, c: self.log(
                    f"hint {h.n} {tier} {t / 60:.0f} min: {c}"
                ),
            )
            rec["attempts"].append(
                {
                    "rc": res.rc,
                    "timed_out": res.timed_out,
                    "wall_s": res.wall_s,
                    "counts": str(res.counts),
                }
            )
            rec["wall_s"] = float(rec["wall_s"]) + res.wall_s
            if res.timed_out:
                outcome = "timeout"
                break
            if res.rc == 3:
                outcome = "refused"
                if attempt < LAUNCH_REFUSED_RETRIES:
                    self.log(
                        f"hint {h.n}: launch refused; retrying in"
                        f" {LAUNCH_REFUSED_SLEEP_S / 60:.0f} min"
                    )
                    time.sleep(LAUNCH_REFUSED_SLEEP_S)
                continue
            if res.counts.todo == 0 and res.counts.failed == 0:
                outcome = "complete"
                break
            if res.counts.failed and attempt < LAUNCH_REFUSED_RETRIES:
                self.log(
                    f"hint {h.n}: {res.counts}; one retry of the failed cells"
                )
                retry_errors = True
                outcome = "incomplete"
                continue
            outcome = "incomplete"
            break
        rec["outcome"] = outcome
        setattr(h, tier, rec)
        if outcome == "timeout":
            self.judge_now(
                h,
                "INSPECT",
                "timeout",
                f"{tier} launch hit its {timeout / 60:.0f} min deadline",
            )
        elif outcome == "refused":
            self.judge_now(
                h,
                "HUMAN",
                "launch-refused",
                "no free Rocq stream slots after retries",
            )
        arm_cells = V.load_cells(run_dir)
        spend = _spend(arm_cells)
        self.night.spent["usd_openai"] += spend - h.arm_spend_usd
        h.arm_spend_usd = spend
        self.save()
        return None if h.state == "judged" else res

    def arm_problems(self) -> Sequence[str]:
        return (
            bench.SMOKE_PROBLEMS
            if self.night.dry
            else tuple(bench.LADONX_PROBLEMS)
        )

    def step_screen(self, h: S.HintRun) -> None:
        if self._check_drift(h):
            return
        h.enter("screening")
        self.save()
        res = self._launch_tier(h, (0,), "screen")
        if res is None:
            return
        paired = self.pair(h, seeds=("0",), trust_solves=True)
        integrity = V.integrity_of(paired)
        verdict = V.judge(
            paired, "screen", integrity, cast(V.HintClass, h.hint_class)
        )
        h.screen["numbers"] = V.as_dict(paired, verdict)
        self.log(
            f"hint {h.n} screen: {V.numbers_line(paired)} -> {verdict.outcome}"
        )
        if verdict.outcome == "DISCARD":
            h.numbers = V.as_dict(paired, verdict)
            h.tier = "screen"
            self.judge_now(h, "DISCARD", verdict.rule, verdict.reason)
            return
        if self.night.dry:
            h.enter("selected")
            return
        h.enter("screened")

    def step_select(self, h: S.HintRun) -> None:
        if self._check_drift(h):
            return
        h.enter("selecting")
        self.save()
        res = self._launch_tier(h, (0, 1), "select")
        if res is None:
            return
        h.enter("selected")

    def pair(
        self, h: S.HintRun, *, seeds: Sequence[str] | None, trust_solves: bool
    ) -> V.Paired:
        a = V.load_cells(self.baseline_dir)
        b = V.load_cells(_OMPHALOS_DIR / str(h.output_dir))
        if trust_solves:
            rev: dict[str, bool] = {c.name: True for c in b}
        else:
            rev = cast(dict[str, bool], h.reverify.get("verified", {}))
        return V.pair(
            a, b, rev, seeds=seeds, problems=tuple(self.arm_problems())
        )

    def step_reverify(self, h: S.HintRun) -> None:
        n = self.night
        h.enter("reverifying")
        self.save()
        assert n.base_sha
        wt = RV.ensure_worktree(n.base_sha)
        n.worktree = {"path": str(wt), "sha": n.base_sha}
        d = self.hint_dir(h.n)
        rep = RV.reverify(
            _OMPHALOS_DIR / str(h.output_dir),
            wt,
            out=d / "reverify.json",
            log=d / "reverify.log",
            env=self.env,
        )
        h.reverify = {
            "checked": rep.checked,
            "failed": list(rep.failed),
            "verified": rep.verified,
            "pristine": rep.meta.get("pytanque_utils"),
        }
        self.log(
            f"hint {h.n} reverify: {rep.checked} checked, {len(rep.failed)} failed"
        )
        seeds = ("0",) if n.dry else None
        paired = self.pair(h, seeds=seeds, trust_solves=False)
        m = _manifest_from_dict(cast(dict[str, Any], h.guard["manifest"]))
        integrity = V.integrity_of(
            paired,
            out_of_scope_diff=bool(m.out_of_scope),
            code_drift=guard.fingerprint(m) != h.fingerprint,
        )
        verdict = V.judge(
            paired, "select", integrity, cast(V.HintClass, h.hint_class)
        )
        h.numbers = V.as_dict(paired, verdict)
        h.tier = "select"
        (d / "verdict.json").write_text(json.dumps(h.numbers, indent=1))
        self.log(
            f"hint {h.n}: {V.numbers_line(paired)} -> {verdict.outcome} ({verdict.rule})"
        )
        self.judge_now(h, verdict.outcome, verdict.rule, verdict.reason)

    def step_evaluate(self, h: S.HintRun) -> None:
        n = self.night
        d = self.hint_dir(h.n)
        needs_prose = h.outcome in ("KEEP", "DISCARD", "INSPECT") and (
            h.numbers or h.hint_class == "A"
        )
        if needs_prose and not self.no_claude:
            m = _manifest_from_dict(
                cast(dict[str, Any], h.guard.get("manifest", {}))
            )
            notes_path = _OMPHALOS_DIR / str(h.notes)
            prompt = _render(
                "evaluate.md",
                hint_n=h.n,
                title=h.title,
                date=n.date,
                hint_class=h.hint_class,
                outcome=h.outcome,
                rule=h.rule,
                reason=h.reason,
                numbers=_numbers_block(h) or _analysis_block(h, d),
                notes=notes_path.read_text()
                if notes_path.exists()
                else "(no notes)",
                diffstat="\n".join(m.touched) or "(no files touched)",
                progress_examples=_progress_examples(PROGRESS.read_text()),
                hints_examples=_hints_examples(HINTS.read_text()),
            )
            (d / "evaluate_prompt.md").write_text(prompt)
            structured: dict[str, Any] | None = None
            for _ in range(EVALUATE_RETRIES):
                call = self.base_call(
                    "evaluate",
                    "evaluate",
                    prompt,
                    d / "evaluate.jsonl",
                    output_format="json",
                    tools="",
                    schema=EVAL_SCHEMA,
                )
                result = self.session(call, h)
                if result.structured is not None:
                    structured = result.structured
                    break
            if structured is not None:
                h.evaluation.update(structured)
        if not h.evaluation.get("new_hints"):
            notes_path = _OMPHALOS_DIR / str(h.notes)
            if notes_path.exists():
                h.evaluation["new_hints"] = _notes_new_hints(
                    notes_path.read_text()
                )
        if "progress_bullet" not in h.evaluation:
            h.evaluation["progress_bullet"] = self.fallback_bullet(h)
        if "hints_marker" not in h.evaluation:
            h.evaluation["hints_marker"] = (h.reason or "")[:120]
        h.enter("evaluated")

    def fallback_bullet(self, h: S.HintRun) -> str:
        nums = h.numbers
        line = (
            f"{nums.get('b_solved')} vs {nums.get('a_solved')} of {nums.get('cells')}"
            f" (arm-only {nums.get('b_only')}, base-only {nums.get('a_only')},"
            f" p={float(nums.get('p_two', 1.0)):.3f}); joint {nums.get('joint')}:"
            f" cheaper {nums.get('cheaper')}, dearer {nums.get('dearer')},"
            f" p={float(nums.get('p_cost', 1.0)):.3f}"
            if nums
            else "no cells measured"
        )
        return (
            f"- **Hint {h.n} — {h.title}** (`{Path(h.output_dir or '').name}`,"
            f" class {h.hint_class}): {h.outcome} by rule {h.rule} — {h.reason}."
            f" {line}. Spend ${h.arm_spend_usd + h.smoke_spend_usd:.2f}."
        )

    def step_record(self, h: S.HintRun) -> None:
        n = self.night
        d = self.hint_dir(h.n)
        m = _manifest_from_dict(
            cast(dict[str, Any], h.guard.get("manifest", {}))
        )
        marker_text = str(
            h.evaluation.get("hints_marker") or h.reason or ""
        ).replace("]", ")")
        if h.outcome == "KEEP":
            h.gates = self.gates(h, m)
            failed = [k for k, v in h.gates.items() if v != "ok"]
            if failed:
                self.log(
                    f"hint {h.n}: gates failed {failed}; downgrading to INSPECT"
                )
                h.outcome, h.rule = "INSPECT", "gates"
                h.reason = f"KEEP downgraded: gates failed {failed}"
            elif n.dry:
                h.reason = (h.reason or "") + " (dry night: not committed)"
            else:
                message = self.commit_message(h)
                (d / "commit_message.txt").write_text(message)
                h.commit = guard.commit(m, message)
                self.log(f"hint {h.n}: committed {(h.commit or '')[:8]}")
        if h.commit is None and not m.empty:
            patch = d / "changes.patch"
            guard.save_patch(m, patch)
            h.patch = str(patch.relative_to(_OMPHALOS_DIR))
            actions = guard.revert(m)
            h.guard["revert"] = actions
            self.log(
                f"hint {h.n}: reverted {len(actions)} path(s); patch at {h.patch}"
            )
            rc = subprocess.run(
                ["make", "test-unit"],
                cwd=_OMPHALOS_DIR,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            ).returncode
            h.guard["test_unit_after_revert"] = "ok" if rc == 0 else f"rc={rc}"
        RP.append_ledger(
            LEDGER if not n.dry else self.dir / "ledger.tsv", n, h
        )
        marker = {
            "KEEP": f"DONE {n.date} by Ladon — KEEP: {marker_text}; commit {(h.commit or '')[:8]}",
            "DISCARD": f"LADON DISCARD {n.date} — {marker_text}",
            "INSPECT": f"LADON INSPECT {n.date} — {marker_text}; inspect with Fable",
            "HUMAN": f"LADON HUMAN {n.date} — {marker_text}",
        }.get(str(h.outcome), f"LADON {h.outcome} {n.date} — {marker_text}")
        if h.n != 0:
            self.mark_hint(h.n, marker)
        new_hints = [
            H.NewHint(
                str(x.get("tag", "experiment")),
                str(x.get("title", "")),
                str(x.get("body", "")),
            )
            for x in cast(
                list[dict[str, Any]], h.evaluation.get("new_hints") or []
            )
            if str(x.get("title", "")).strip()
        ]
        if new_hints:
            hints_file = self.knowledge_file("HINTS.md")
            hints_file.write_text(
                H.append_hints(hints_file.read_text(), n.date, new_hints)
            )
        bullet = textwrap.fill(
            " ".join(str(h.evaluation.get("progress_bullet", "")).split()),
            WRAP,
            subsequent_indent="  ",
            break_long_words=False,
            break_on_hyphens=False,
        )
        progress = self.knowledge_file("PROGRESS.md")
        heading = str(n.plan.get("progress_heading"))
        progress.write_text(
            H.append_to_section(progress.read_text(), heading, bullet)
        )
        h.enter("recorded")
        n.event(f"hint {h.n}: {h.outcome} ({h.rule})")

    def mark_hint(self, k: int, marker: str) -> None:
        hints_file = self.knowledge_file("HINTS.md")
        text = hints_file.read_text()
        if H.find_hint(text, k) is None:
            return
        hints_file.write_text(H.mark_hint(text, k, marker.replace("]", ")")))

    # ---- gates and commit ------------------------------------------------

    def gates(self, h: S.HintRun, m: guard.Manifest) -> dict[str, str]:
        d = self.hint_dir(h.n)
        log = d / "gates.log"
        results: dict[str, str] = {}

        def run(name: str, cmd: Sequence[str], cwd: Path) -> None:
            proc = subprocess.run(
                list(cmd),
                cwd=cwd,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                env=self.env,
            )
            with log.open("a") as f:
                f.write(
                    f"\n## {name}: {' '.join(cmd)} (rc={proc.returncode})\n{proc.stdout}\n{proc.stderr}\n"
                )
            results[name] = (
                "ok" if proc.returncode == 0 else f"rc={proc.returncode}"
            )
            self.log(f"hint {h.n} gate {name}: {results[name]}")

        py = guard.touched_python(m)
        if py:
            run(
                "ruff-format",
                ["ruff", "format", "--check", *py],
                _OMPHALOS_DIR,
            )
            run("ruff-check", ["ruff", "check", *py], _OMPHALOS_DIR)
        run("pyright", ["make", "pyright"], guard.REPO)
        run("test", ["make", "test"], _OMPHALOS_DIR)
        run("reprice", ["make", "reprice"], _OMPHALOS_DIR)
        results["replay"] = self.gate_replay(d, log)
        self.log(f"hint {h.n} gate replay: {results['replay']}")
        if guard.verifier_touched(m):
            run("test-rocq", ["make", "test-rocq"], _OMPHALOS_DIR)
            run("bridge-parity", ["make", "bridge-parity"], _OMPHALOS_DIR)
        return results

    def gate_replay(self, d: Path, log: Path) -> str:
        """
        Prompt neutrality: the five cached smoke suites must replay
        without a single cache miss (`cache_mode: replay` raises on one).
        """
        tmp = d / "replay"
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True)
        shutil.copytree(COMMANDS_DIR / "cache", tmp / "cache")
        failures: list[str] = []
        for exec_yaml in sorted(COMMANDS_DIR.glob("prove_one_*.exec.yaml")):
            text = exec_yaml.read_text()
            lines = text.splitlines(keepends=True)
            for i, ln in enumerate(lines):
                if ln.startswith("args:"):
                    lines.insert(i + 1, "  cache_mode: replay\n")
                    break
            target = tmp / exec_yaml.name
            target.write_text("".join(lines))
            proc = subprocess.run(
                ["delphyne", "run", str(target), "--cache", "--no-header"],
                cwd=_OMPHALOS_DIR,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                env=self.env,
            )
            with log.open("a") as f:
                f.write(
                    f"\n## replay {exec_yaml.name} (rc={proc.returncode})\n{proc.stdout[-3000:]}\n{proc.stderr[-3000:]}\n"
                )
            if proc.returncode != 0 or "Error" in proc.stderr[-2000:]:
                failures.append(exec_yaml.name)
        return "ok" if not failures else "FAIL " + ",".join(failures)

    def commit_message(self, h: S.HintRun) -> str:
        n = self.night
        nums = h.numbers
        body = str(h.evaluation.get("commit_body", "")).strip()
        models = ", ".join(sorted({str(s.get("model")) for s in h.sessions}))
        return (
            f"Hint {h.n}: {h.title} (Ladon {n.date})\n\n"
            f"{body}\n\n"
            f"Result (ladonX, {nums.get('cells')} cells vs x_ladon_agentic):"
            f" {nums.get('b_solved')} vs {nums.get('a_solved')} solves,"
            f" arm-only {nums.get('b_only')} / base-only {nums.get('a_only')},"
            f" p={float(nums.get('p_two', 1.0)):.3f}; jointly solved {nums.get('joint')}:"
            f" cheaper {nums.get('cheaper')}, dearer {nums.get('dearer')},"
            f" median x{float(nums.get('median_ratio') or 1.0):.2f}, p={float(nums.get('p_cost', 1.0)):.3f}."
            f" Pristine re-verification: {h.reverify.get('checked')} checked, 0 failed.\n"
            f"Verdict: KEEP by rule {h.rule} — {h.reason}\n"
            f"Spend: OpenAI ${h.arm_spend_usd + h.smoke_spend_usd:.2f};"
            f" Claude est. ${h.claude_cost_usd:.2f} ({models})\n"
            f"Report: ladon/nights/{n.date}/REPORT.md\n\n"
            "Co-Authored-By: Ladon <noreply@anthropic.com>\n"
        )

    # ---- end of night ----------------------------------------------------

    def finish(self) -> None:
        n = self.night
        kept = sum(1 for h in n.hints.values() if h.outcome == "KEEP")
        started = sum(
            1
            for h in n.hints.values()
            if h.state != "queued" and h.state != "skipped"
        )
        summary = f"{started} hints, {kept} kept, ${n.spent['usd_openai']:.2f}"
        heading = n.plan.get("progress_heading")
        if heading:
            progress = self.knowledge_file("PROGRESS.md")
            new_heading = H.progress_heading(n.date, summary)
            try:
                progress.write_text(
                    H.replace_heading(
                        progress.read_text(), str(heading), new_heading
                    )
                )
                n.plan["progress_heading"] = new_heading
            except KeyError:
                pass
        path = RP.write_report(n, night_dir=self.dir, latest=LATEST)
        self.log(f"report written: {path}")

    def cleanup_worktree(self) -> None:
        wt = self.night.worktree.get("path")
        if wt and self.night.state in ("done", "halted"):
            RV.remove_worktree(Path(str(wt)))


#####
##### Serialisation helpers
#####


def _snapshot_to_dict(s: guard.Snapshot) -> dict[str, Any]:
    return {
        "files": {k: [v.size, v.mtime_ns, v.sha] for k, v in s.files.items()},
        "outputs": s.outputs,
        "blocks": s.blocks,
        "head": s.head,
        "git_status": list(s.git_status),
    }


def _snapshot_from_dict(d: dict[str, Any]) -> guard.Snapshot:
    files = {
        k: guard.FileStat(int(v[0]), int(v[1]), str(v[2]))
        for k, v in cast(dict[str, list[Any]], d["files"]).items()
    }
    return guard.Snapshot(
        files=files,
        outputs=cast(dict[str, str], d["outputs"]),
        blocks=cast(dict[str, str], d["blocks"]),
        head=str(d["head"]),
        git_status=tuple(cast(list[str], d["git_status"])),
    )


def _manifest_to_dict(m: guard.Manifest) -> dict[str, Any]:
    return {
        "modified": list(m.modified),
        "created": list(m.created),
        "deleted": list(m.deleted),
        "git_changes": list(m.git_changes),
        "out_of_scope": list(m.out_of_scope),
        "blocks_changed": list(m.blocks_changed),
        "append_violations": list(m.append_violations),
        "outputs_changed": list(m.outputs_changed),
        "outputs_new": list(m.outputs_new),
        "head_changed": m.head_changed,
        "untracked_modified": list(m.untracked_modified),
        "untracked_deleted": list(m.untracked_deleted),
    }


def _manifest_from_dict(d: dict[str, Any]) -> guard.Manifest:
    def t(key: str) -> tuple[str, ...]:
        return tuple(str(x) for x in cast(list[Any], d.get(key, [])))

    return guard.Manifest(
        modified=t("modified"),
        created=t("created"),
        deleted=t("deleted"),
        git_changes=t("git_changes"),
        out_of_scope=t("out_of_scope"),
        blocks_changed=t("blocks_changed"),
        append_violations=t("append_violations"),
        outputs_changed=t("outputs_changed"),
        outputs_new=t("outputs_new"),
        head_changed=bool(d.get("head_changed", False)),
        untracked_modified=t("untracked_modified"),
        untracked_deleted=t("untracked_deleted"),
    )


def _load_arm(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        raw: Any = yaml.safe_load(path.read_text())
    except yaml.YAMLError:
        return {"summary": "arm.yaml is not valid YAML"}
    return cast(dict[str, Any], raw) if isinstance(raw, dict) else {}


_NOTES_HINT_RE = re.compile(
    r"^-\s*\[(?P<tag>[a-z]+)\]\s*(?P<title>.+?)\s+[—-]\s+(?P<body>.+)$"
)


def _notes_new_hints(notes: str) -> list[dict[str, str]]:
    """`- [tag] Title — body` bullets under `## New hints` in notes.md."""
    out: list[dict[str, str]] = []
    section = notes.split("## New hints", 1)
    if len(section) < 2:
        return out
    block = section[1].split("\n## ", 1)[0]
    current: list[str] = []
    for line in block.splitlines() + [""]:
        if line.startswith("- "):
            if current:
                out.append(_notes_hint_entry(" ".join(current)))
            current = [line.strip()]
        elif line.strip() and current:
            current.append(line.strip())
        elif not line.strip() and current:
            out.append(_notes_hint_entry(" ".join(current)))
            current = []
    return [e for e in out if e.get("title") and e["title"] != "none"]


def _notes_hint_entry(text: str) -> dict[str, str]:
    m = _NOTES_HINT_RE.match(text)
    if m is None:
        return {"tag": "experiment", "title": text[2:80].strip(), "body": ""}
    return {
        "tag": m.group("tag"),
        "title": m.group("title").strip(),
        "body": m.group("body").strip(),
    }


def _analysis_block(h: S.HintRun, d: Path) -> str:
    """For an offline analysis: the artifact itself stands in for numbers."""
    analysis = d / "analysis.md"
    if analysis.exists():
        return (
            "(offline analysis — no paired cells)\n\n"
            + analysis.read_text()[:9000]
        )
    return "(offline analysis — no paired cells, no analysis.md written)"


def _numbers_block(h: S.HintRun) -> str:
    nums = dict(h.numbers)
    cells = cast(list[dict[str, Any]], nums.pop("discordant_cells", []))
    lines = [f"- {k}: {v}" for k, v in nums.items() if k != "verdict"]
    if cells:
        lines.append(
            "- discordant cells (a = baseline solved, b = arm solved):"
        )
        lines += [
            f"    - {c['bench']} seed {c['seed']}: a={c['a']} b={c['b']}"
            for c in cells
        ]
    return "\n".join(lines)


#####
##### Preflight
#####


def preflight_checks(*, dry: bool, no_claude: bool) -> dict[str, str]:
    checks: dict[str, str] = {}
    checks["openai_key"] = (
        "ok"
        if os.environ.get("OPENAI_API_KEY")
        else "FAIL: OPENAI_API_KEY unset"
    )
    checks["anthropic_key_unset"] = (
        "ok"
        if not os.environ.get("ANTHROPIC_API_KEY")
        else "FAIL: ANTHROPIC_API_KEY would outrank the subscription"
    )
    if no_claude:
        checks["claude_auth"] = "ok (skipped: no_claude)"
    else:
        try:
            out = subprocess.run(
                [C.claude_binary(), "auth", "status"],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=60,
                env=C.env_for_claude(),
            ).stdout
            raw: Any = json.loads(out) if out.strip().startswith("{") else {}
            info = cast(dict[str, Any], raw)
            checks["claude_auth"] = (
                f"ok ({info.get('subscriptionType', '?')})"
                if info.get("loggedIn")
                else f"FAIL: {out.strip()[:200]}"
            )
        except Exception as e:  # noqa: BLE001
            checks["claude_auth"] = f"FAIL: {e}"
    rc = subprocess.run(
        ["make", "test-unit"],
        cwd=_OMPHALOS_DIR,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    ).returncode
    checks["test_unit"] = "ok" if rc == 0 else f"FAIL: make test-unit rc={rc}"
    pids = sl.launcher_pids(sl.held_locks())
    checks["no_launches"] = (
        "ok" if not pids else f"FAIL: launches running (pids {pids})"
    )
    dirty = [ln for ln in guard.git_status() if not ln.startswith("??")]
    ladon_only = all(
        ln[3:].strip().startswith(f"{guard.REL}/ladon/") for ln in dirty
    )
    if not dirty:
        checks["git_clean"] = "ok"
    elif dry:
        checks["git_clean"] = f"ok (dry: {len(dirty)} tracked change(s))"
    elif ladon_only:
        # Ladon's own code edited by hand between nights: no arm measures
        # it, and a KEEP commit adds only the session's manifest paths.
        checks["git_clean"] = (
            f"ok ({len(dirty)} uncommitted change(s) inside ladon/)"
        )
    else:
        checks["git_clean"] = f"FAIL: tracked changes present ({len(dirty)})"
    sha = guard.head_sha()
    ladonx_committed = (
        subprocess.run(
            ["git", "cat-file", "-e", f"{sha}:{guard.REL}/ladon/ladonX.txt"],
            cwd=guard.REPO,
            capture_output=True,
            stdin=subprocess.DEVNULL,
        ).returncode
        == 0
    )
    checks["setup_committed"] = (
        "ok"
        if ladonx_committed
        else (
            "ok (dry: not required)"
            if dry
            else "FAIL: commit the Ladon setup first (ladon/ladonX.txt is not in HEAD)"
        )
    )
    avail = _mem_available_mb()
    checks["memory"] = (
        "ok" if avail >= 3000 else f"FAIL: MemAvailable {avail} MB < 3000"
    )
    free_gb = shutil.disk_usage(_OMPHALOS_DIR).free / 2**30
    checks["disk"] = "ok" if free_gb >= 3 else f"FAIL: {free_gb:.1f} GB free"
    checks["pet_server"] = (
        "ok" if shutil.which("pet-server") else "FAIL: pet-server not on PATH"
    )
    checks["baseline_script"] = (
        "ok" if BASELINE_SCRIPT.exists() else "FAIL: baseline script missing"
    )
    guard.git("worktree", "prune", check=False)
    return checks


def _mem_available_mb() -> int:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except OSError:
        pass
    return 0


#####
##### CLI
#####


def _latest_night_dir(root: Path = NIGHTS_DIR) -> Path | None:
    """The most recently written night (by `night.yaml` mtime)."""
    if not root.exists():
        return None
    dirs = [
        d for d in root.iterdir() if d.is_dir() and (d / "night.yaml").exists()
    ]
    if not dirs:
        return None
    return max(dirs, key=lambda d: (d / "night.yaml").stat().st_mtime)


def _install_signals() -> None:
    def handler(signum: int, _frame: Any) -> None:
        raise KeyboardInterrupt(f"signal {signum}")

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)


class LadonCLI:
    """`python -m ladon.cli <command> [--flag=value ...]`."""

    def night(
        self,
        date: str | None = None,
        max_hints: int = 3,
        wallclock_h: float = 9.0,
        cap_usd: float = 12.0,
        claude_cap_usd: float = 25.0,
        hints: Any = None,
        dry: bool = False,
        yolo: bool = False,
        no_claude: bool = False,
        max_workers: int = 4,
        dry_timeout_s: float | None = None,
        plan_model: str | None = None,
        design_model: str | None = None,
        knob_model: str | None = None,
    ) -> int:
        """Start a night (use `resume` to continue an existing one)."""
        _install_signals()
        day = date or _date.today().isoformat()
        if dry:
            day = f"{day}-dry"
        path = S.state_path(day)
        if path.exists():
            print(
                f"{path} exists — use `resume --date={day}`", file=sys.stderr
            )
            return 1
        models = {
            k: v
            for k, v in (
                ("plan", plan_model),
                ("C", design_model),
                ("B", knob_model),
            )
            if v
        }
        night = S.Night(
            date=day,
            dry=dry,
            budget={
                "max_hints": int(max_hints),
                "wallclock_h": float(wallclock_h),
                "cap_usd": float(cap_usd),
                "claude_cap_usd": float(claude_cap_usd),
                "hints": _parse_hint_numbers(hints),
                "yolo": bool(yolo),
                "max_workers": int(max_workers),
                "dry_timeout_s": dry_timeout_s,
                "models": models,
            },
        )
        runner = Ladon(night, no_claude=no_claude)
        runner.save()
        runner.log(f"night {day} created: {night.budget}")
        return runner.run()

    def resume(self, date: str | None = None, no_claude: bool = False) -> int:
        """Continue a night from its persisted state."""
        _install_signals()
        d = (NIGHTS_DIR / date) if date else _latest_night_dir()
        if d is None or not (d / "night.yaml").exists():
            print("no night to resume", file=sys.stderr)
            return 1
        night = S.load(d / "night.yaml")
        if night.state in ("done",):
            print(f"night {night.date} is already {night.state}")
            return 0
        if night.state == "halted":
            night.halt_reason = None
            # Re-enter the last live state: hints keep theirs.
            night.state = "running" if night.order else "created"
            night.event("resumed after halt")
        runner = Ladon(night, no_claude=no_claude)
        runner.log(f"resuming night {night.date} in state {night.state}")
        return runner.run()

    def status(self, date: str | None = None) -> None:
        """State of a night, its hints, the live arm and the slots."""
        d = (NIGHTS_DIR / date) if date else _latest_night_dir()
        if d is None:
            print("no nights yet")
            return
        night = S.load(d / "night.yaml")
        print(
            f"night {night.date}: {night.state}"
            + (f" ({night.halt_reason})" if night.halt_reason else "")
        )
        print(f"  spent: {night.spent}")
        for k in night.order:
            h = night.hints[k]
            line = f"  hint {k} [{h.hint_class}] {h.state:<13} {h.outcome or '':<8} {h.title[:50]}"
            if h.output_dir and h.state in ("screening", "selecting"):
                line += f"  {L.counts(_OMPHALOS_DIR / h.output_dir)}"
            print(line)
        for i, holder in ol.slot_table():
            print(f"  slot {i}: {holder or 'free'}")
        unit = f"ladon-{night.date}"
        active = subprocess.run(
            ["systemctl", "--user", "is-active", unit],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
        ).stdout.strip()
        print(f"  unit {unit}: {active or 'n/a'}")
        print(f"  log: {d / 'ladon.log'}")

    def report(self, date: str | None = None) -> None:
        """(Re)render the morning report of a night and print its path."""
        d = (NIGHTS_DIR / date) if date else _latest_night_dir()
        if d is None:
            print("no nights yet")
            return
        night = S.load(d / "night.yaml")
        print(RP.write_report(night, night_dir=d, latest=LATEST))

    def preflight(self, dry: bool = False, no_claude: bool = False) -> int:
        """Print the preflight table without starting anything."""
        checks = preflight_checks(dry=dry, no_claude=no_claude)
        for k, v in checks.items():
            print(f"{k:<20} {v}")
        return 0 if all(v.startswith("ok") for v in checks.values()) else 1

    def selftest(self, no_claude: bool = False) -> int:
        """Preflight, a one-turn structured Claude call, a pristine re-check."""
        ok = True
        print("== preflight")
        for k, v in preflight_checks(dry=True, no_claude=no_claude).items():
            print(f"  {k:<20} {v}")
        if not no_claude:
            print("== claude probe (structured, one turn)")
            res = C.probe(log=NIGHTS_DIR / "selftest" / "probe.jsonl")
            print(
                f"  rc={res.rc} subtype={res.subtype} structured={res.structured} cost=${res.cost_usd:.4f} util={res.utilization}"
            )
            ok &= res.structured is not None and bool(res.structured.get("ok"))
            print("== --append-system-prompt-file probe")
            call = C.ClaudeCall(
                phase="probe-system",
                prompt="Reply with the single word OK.",
                model="sonnet",
                effort="low",
                max_turns=1,
                log=NIGHTS_DIR / "selftest" / "probe_system.jsonl",
                output_format="json",
                tools="",
                system_file=SYSTEM_FILE,
            )
            res2, flag, _ = C.run_with_retries(call, system_prompt_flag="file")
            print(
                f"  rc={res2.rc} flag={flag} text={res2.text.strip()[:40]!r}"
            )
            ok &= res2.rc == 0
        print("== pristine re-verification of one archived solved cell")
        sha = guard.head_sha()
        wt = RV.ensure_worktree(sha)
        arm = _OMPHALOS_DIR / "experiments" / "output" / "x_validation_agentic"
        jobs = RV.jobs_for(arm)[:1]
        out = NIGHTS_DIR / "selftest" / "reverify.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        jobs_path = out.with_name("reverify_jobs.json")
        jobs_path.write_text(json.dumps([j.as_dict() for j in jobs]))
        proc = subprocess.run(
            [
                sys.executable,
                str(RV.WORKER),
                "--pristine",
                str(wt / guard.REL),
                "--jobs",
                str(jobs_path),
                "--out",
                str(out),
                "--timeout",
                "600",
            ],
            cwd=wt / guard.REL,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            env={
                **os.environ,
                "OMPHALOS_PET_MODE": "socket",
                "OMPHALOS_CHECK_MEMO": "0",
            },
        )
        print(
            f"  worker rc={proc.returncode}: {proc.stdout.strip()[-200:]} {proc.stderr.strip()[-300:]}"
        )
        if out.exists():
            meta = cast(dict[str, Any], json.loads(out.read_text())["meta"])
            print(
                f"  pristine checker: {meta.get('pytanque_utils')}; failed={meta.get('failed')}"
            )
            ok &= not meta.get("failed") and str(
                meta.get("pytanque_utils", "")
            ).startswith(str(wt))
        else:
            ok = False
        RV.remove_worktree(wt)
        print("== SELFTEST", "OK" if ok else "FAILED")
        return 0 if ok else 1

    def launch(self, resume: bool = False, **kw: Any) -> int:
        """Detach a night (systemd-run --user, else nohup) and return."""
        day = str(kw.get("date") or _date.today().isoformat())
        if kw.get("dry"):
            day = f"{day}-dry"
        args = [
            f"--{k}={v}"
            for k, v in kw.items()
            if v is not None and v is not False
        ]
        args += [f"--{k}" for k, v in kw.items() if v is True]
        cmd = [
            sys.executable,
            "-m",
            "ladon.cli",
            "resume" if resume else "night",
            *args,
        ]
        night_dir = NIGHTS_DIR / day
        night_dir.mkdir(parents=True, exist_ok=True)
        unit = f"ladon-{day}"
        env_pairs = [
            f"{k}={os.environ[k]}"
            for k in (
                "OPENAI_API_KEY",
                "PATH",
                "HOME",
                "CLAUDE_CODE_OAUTH_TOKEN",
                "OMPHALOS_MAX_STREAMS",
                "OMPHALOS_PET_MODE",
            )
            if k in os.environ
        ]
        sd = shutil.which("systemd-run")
        if sd:
            proc = subprocess.run(
                [
                    sd,
                    "--user",
                    f"--unit={unit}",
                    "--collect",
                    "-p",
                    f"WorkingDirectory={_OMPHALOS_DIR}",
                    *[f"--setenv={p}" for p in env_pairs],
                    *cmd,
                ],
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
            if proc.returncode == 0:
                print(
                    f"started {unit}: follow with `journalctl --user -u {unit} -f` or `make ladon-status`"
                )
                return 0
            print(
                f"systemd-run failed ({proc.stderr.strip()[:200]}); falling back to nohup"
            )
        out = (night_dir / "ladon.out").open("ab")
        subprocess.Popen(
            ["nohup", *cmd],
            cwd=_OMPHALOS_DIR,
            env=os.environ,
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        print(f"started with nohup: tail -f {night_dir / 'ladon.out'}")
        return 0


def main() -> None:
    fire.Fire(LadonCLI)  # type: ignore[reportUnknownMemberType]


if __name__ == "__main__":
    main()
