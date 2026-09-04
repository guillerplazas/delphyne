"""
The morning report and the append-only ledger.

`REPORT.md` is what Guille reads first: a short summary, one row per
hint with the numbers the verdict was made on, the items that need a
human (structural hints, INSPECT verdicts to look at with Fable, gate
failures, testX looks to authorise), the usage-limit waits, and the
timeline. `ledger.tsv` is the autoresearch `results.tsv`: one row per
hint per night, tab-separated so descriptions may contain commas, and
never committed.
"""

# pyright: strict

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ladon.state import HintRun, Night

LEDGER_COLUMNS: tuple[str, ...] = (
    "night",
    "hint",
    "tag",
    "class",
    "outcome",
    "rule",
    "title",
    "a_solved",
    "b_solved",
    "a_only",
    "b_only",
    "p_two",
    "p_one",
    "joint",
    "cheaper",
    "dearer",
    "median_ratio",
    "p_cost",
    "arm_spend_usd",
    "claude_cost_usd",
    "wall_min",
    "reverify_failed",
    "commit",
    "output_dir",
    "note",
)


def _fmt(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v).replace("\t", " ").replace("\n", " ")


def _wall_min(h: HintRun) -> float:
    return (
        float(h.screen.get("wall_s", 0.0)) / 60
        + float(h.select.get("wall_s", 0.0)) / 60
    )


def ledger_row(night: Night, h: HintRun) -> str:
    n = h.numbers
    values: dict[str, Any] = {
        "night": night.date,
        "hint": h.n,
        "tag": h.tag,
        "class": h.hint_class,
        "outcome": h.outcome,
        "rule": h.rule,
        "title": h.title,
        "a_solved": n.get("a_solved"),
        "b_solved": n.get("b_solved"),
        "a_only": n.get("a_only"),
        "b_only": n.get("b_only"),
        "p_two": n.get("p_two"),
        "p_one": n.get("p_one"),
        "joint": n.get("joint"),
        "cheaper": n.get("cheaper"),
        "dearer": n.get("dearer"),
        "median_ratio": n.get("median_ratio"),
        "p_cost": n.get("p_cost"),
        "arm_spend_usd": h.arm_spend_usd,
        "claude_cost_usd": h.claude_cost_usd,
        "wall_min": _wall_min(h),
        "reverify_failed": n.get("reverify_failed"),
        "commit": h.commit,
        "output_dir": h.output_dir,
        "note": h.evaluation.get("hints_marker") or h.reason,
    }
    return "\t".join(_fmt(values[c]) for c in LEDGER_COLUMNS)


def append_ledger(path: Path, night: Night, h: HintRun) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8") as f:
        if new:
            f.write("\t".join(LEDGER_COLUMNS) + "\n")
        f.write(ledger_row(night, h) + "\n")


def read_ledger(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    cols = lines[0].split("\t")
    return [dict(zip(cols, ln.split("\t"))) for ln in lines[1:] if ln.strip()]


#####
##### REPORT.md
#####


def _p(v: Any) -> str:
    return f"{float(v):.3f}" if isinstance(v, (int, float)) else "–"


def _ratio(v: Any) -> str:
    return f"×{float(v):.2f}" if isinstance(v, (int, float)) else "–"


def _outcome_counts(hints: Sequence[HintRun]) -> dict[str, int]:
    out: dict[str, int] = {}
    for h in hints:
        key = h.outcome or h.state
        out[key] = out.get(key, 0) + 1
    return out


def render_report(night: Night, *, night_dir: Path) -> str:
    hints = [night.hints[n] for n in night.order]
    counts = _outcome_counts(hints)
    keeps = [h for h in hints if h.outcome == "KEEP"]
    lines: list[str] = []
    lines.append(f"# Ladon night {night.date} — morning report")
    lines.append("")
    lines.append(
        f"State: **{night.state}**"
        + (f" ({night.halt_reason})" if night.halt_reason else "")
        + f". Base commit `{(night.base_sha or '')[:8]}` on"
        f" `{night.branch or '?'}`; started {night.started_at}, last update"
        f" {night.updated_at}."
    )
    lines.append("")
    summary = (
        ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "none"
    )
    lines.append(
        f"- **Hints**: {len(hints)} planned — {summary}."
        + (
            " Kept: "
            + ", ".join(f"#{h.n} (`{(h.commit or '')[:8]}`)" for h in keeps)
            if keeps
            else ""
        )
    )
    lines.append(
        f"- **Spend**: OpenAI ${night.spent.get('usd_openai', 0.0):.2f}"
        f" (cap ${night.budget.get('cap_usd', 0)}), Claude est."
        f" ${night.spent.get('usd_claude', 0.0):.2f}; waited"
        f" {night.spent.get('minutes_waited', 0.0):.0f} min on usage limits."
    )
    base = night.baseline
    if base:
        lines.append(
            f"- **Baseline** `{base.get('dir', '')}`: {base.get('counts', '')}"
            + (f" ({base.get('note')})" if base.get("note") else "")
        )
    if night.dry:
        lines.append(
            "- **DRY NIGHT**: PROGRESS/HINTS edits went to copies under"
            " `nights/<date>/dry/`; nothing was committed."
        )
    lines.append("")
    lines.append("## Verdicts")
    lines.append("")
    lines.append(
        "| hint | class | outcome | rule | solves a→b | arm-only / base-only |"
        " p₂ | joint cheaper/dearer | median | p_cost | arm $ | claude $ |"
        " wall | commit / patch |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for h in hints:
        n = h.numbers
        ref = (
            f"`{h.commit[:8]}`"
            if h.commit
            else (f"`{Path(h.patch).name}`" if h.patch else "")
        )
        lines.append(
            f"| #{h.n} {h.title[:48]} | {h.hint_class} | **{h.outcome or h.state}** |"
            f" {h.rule or ''} | {n.get('a_solved', '–')}→{n.get('b_solved', '–')} |"
            f" {n.get('b_only', '–')} / {n.get('a_only', '–')} | {_p(n.get('p_two'))} |"
            f" {n.get('joint', '–')}: {n.get('cheaper', '–')}/{n.get('dearer', '–')} |"
            f" {_ratio(n.get('median_ratio'))} | {_p(n.get('p_cost'))} |"
            f" {h.arm_spend_usd:.2f} | {h.claude_cost_usd:.2f} | {_wall_min(h):.0f} min |"
            f" {ref} |"
        )
    lines.append("")
    for h in hints:
        lines.append(f"### Hint {h.n} — {h.title}")
        lines.append("")
        lines.append(
            f"Class {h.hint_class}, state `{h.state}`, outcome **{h.outcome or '–'}**"
            f" ({h.rule or '–'}): {h.reason or ''}"
        )
        if h.error:
            lines.append(f"- Error: {h.error}")
        if h.arm.get("summary"):
            lines.append(f"- Arm: {h.arm.get('summary')}")
        if h.evaluation.get("progress_bullet"):
            lines.append("")
            lines.append(str(h.evaluation["progress_bullet"]))
        if h.evaluation.get("human_note"):
            lines.append(f"- For Guille: {h.evaluation['human_note']}")
        if h.reverify:
            lines.append(
                f"- Reverify: {h.reverify.get('checked', 0)} checked,"
                f" {len(h.reverify.get('failed', []))} failed"
            )
        if h.guard.get("violations"):
            lines.append(
                "- Guard violations: " + "; ".join(h.guard["violations"])
            )
        if h.gates:
            failed = [k for k, v in h.gates.items() if v != "ok"]
            lines.append(
                "- Gates: "
                + (
                    "all passed"
                    if not failed
                    else "FAILED " + ", ".join(failed)
                )
            )
        paths = [
            p
            for p in (
                h.script,
                h.output_dir,
                h.notes,
                h.patch,
                h.arm.get("analysis"),
            )
            if p and (night_dir.parent.parent.parent / str(p)).exists()
        ]
        if paths:
            lines.append("- Files: " + ", ".join(f"`{p}`" for p in paths))
        lines.append("")
    lines.append("## Human items")
    lines.append("")
    items: list[str] = []
    for h in keeps:
        items.append(
            f"- **testX look to authorise** for hint #{h.n} (commit"
            f" `{(h.commit or '')[:8]}`): the KEEP rests on ladonX only."
        )
    for h in hints:
        if h.outcome == "INSPECT":
            items.append(
                f"- **Inspect with Fable**: hint #{h.n} — {h.reason or ''}"
                + (f" Patch: `{h.patch}`." if h.patch else "")
            )
        if h.outcome == "HUMAN":
            items.append(f"- **With human**: hint #{h.n} — {h.reason or ''}")
        if h.gates and any(v != "ok" for v in h.gates.values()):
            items.append(f"- **Gate failure** on hint #{h.n}: {h.gates}")
    for item in night.human:
        items.append(
            f"- **Structural (class D)**: hint #{item.get('hint')} — {item.get('why', '')}"
        )
    if night.state == "halted":
        items.append(f"- **Night halted**: {night.halt_reason}")
    lines += items or ["- none"]
    lines.append("")
    if night.rate_limit_events:
        lines.append("## Usage-limit events")
        lines.append("")
        for ev in night.rate_limit_events:
            lines.append(
                f"- {ev.get('at')}: {ev.get('phase')} (hint {ev.get('hint')}) —"
                f" waited {float(ev.get('waited_s', 0)) / 60:.0f} min;"
                f" utilisation {ev.get('utilization')}"
            )
        lines.append("")
    lines.append("## Timeline")
    lines.append("")
    for ev in night.timeline:
        lines.append(f"- {ev.get('at')}: {ev.get('event')}")
    lines.append("")
    lines.append(
        f"Artifacts: `{night_dir}` (night.yaml, plan.yaml, hints/h<N>/…)."
    )
    return "\n".join(lines) + "\n"


def write_report(night: Night, *, night_dir: Path, latest: Path) -> Path:
    text = render_report(night, night_dir=night_dir)
    path = night_dir / "REPORT.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    latest.write_text(text)
    return path
