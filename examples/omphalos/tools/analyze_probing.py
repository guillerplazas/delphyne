"""
Post-hoc analysis of the "probing" toolset sweeps.

Reads the request caches (`cache.yaml`) and result summaries of the
`{validation,test}_probing` sweeps and their `{validation,test}_agentic`
("rich") controls, reconstructs each config's conversation, and
quantifies how
the `TryTactics` tool was actually used:

  - tool-usage rates per arm (how many configs call any tool at all);
  - TryTactics call anatomy (candidates per call, outcome mix parsed
    from the tool reports, overlap with the free automation battery,
    repeated probing of the same prefix);
  - follow-through (does the model act on a reported winner?);
  - budget/economics (billed requests and price, solved vs unsolved;
    first-request input-token overhead of the probing prompt);
  - per-config conversation outlines for case studies.

Pure read-only analysis: no LLM calls, no Rocq sessions. Run from
anywhere:

    python tools/analyze_probing.py

Outputs a markdown report and one outline file per tool-using config
under `experiments/output/probing_analysis/`.
"""

# pyright: strict

import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pytanque_utils import AUTOMATION_BATTERY  # noqa: E402

_OMPHALOS = Path(__file__).resolve().parent.parent
_OUTPUT = _OMPHALOS / "experiments" / "output"
_ANALYSIS_DIR = _OUTPUT / "probing_analysis"

_INSTANCE_PREFIX = "Prove the following theorem"

# Battery entries normalized for overlap detection (a TryTactics
# candidate duplicating one of these wastes a probe: the verifier and
# TryAutomation already run the battery for free).
_BATTERY_NORM = {" ".join(t.split()) for t in AUTOMATION_BATTERY}


def _norm(s: str) -> str:
    return " ".join(s.split())


@dataclass
class TryTacticsCall:
    """One TryTactics invocation and its parsed report."""

    turn_index: int  # assistant-turn index within the conversation
    prefix: str  # the `tactics` argument, normalized
    candidates: list[str]
    n_fails: int = 0
    n_applies: int = 0
    n_closes: int = 0  # applies with a goal-count drop
    n_finished: int = 0
    n_skipped: int = 0
    battery_overlap: int = 0
    followed_through: bool | None = None  # None = no winner to follow


@dataclass
class ConfigAnalysis:
    """Everything extracted from one config's cache + summary row."""

    name: str
    arm: str  # "probing" | "rich"
    bench: str
    seed: str
    solved: bool
    price: float
    billed_requests: int
    n_proposals: int = 0
    tool_calls: Counter[str] = field(default_factory=Counter[str])
    first_tool_turn: int | None = None
    first_input_tokens: int | None = None
    trytactics: list[TryTacticsCall] = field(
        default_factory=list[TryTacticsCall]
    )
    outline: list[str] = field(default_factory=list[str])


def _load_summary(summary_csv: Path) -> dict[str, dict[str, str]]:
    """Map `{bench}__seed{seed}` to the summary row."""
    rows: dict[str, dict[str, str]] = {}
    with open(summary_csv) as f:
        for r in csv.DictReader(f):
            rows[f"{r['bench_name']}__seed{r['seed']}"] = r
    return rows


def _conversation(chat: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Slice off the system message and the few-shot example pairs: the
    real conversation starts at the *last* instance user message.
    """
    start = 0
    for i, m in enumerate(chat):
        if m["role"] == "user" and str(m.get("content", "")).startswith(
            _INSTANCE_PREFIX
        ):
            start = i
    return chat[start:]


_REPORT_FAILS = re.compile(r"-> FAILS")
_REPORT_APPLIES = re.compile(r"-> applies")
_REPORT_CLOSES = re.compile(r"-> applies, closes|-> PROOF FINISHED")
_REPORT_FINISHED = re.compile(r"-> PROOF FINISHED")
_REPORT_SKIPPED = re.compile(r"-> skipped")


def _parse_report(call: TryTacticsCall, report: str) -> None:
    call.n_fails = len(_REPORT_FAILS.findall(report))
    call.n_applies = len(_REPORT_APPLIES.findall(report))
    call.n_closes = len(_REPORT_CLOSES.findall(report))
    call.n_finished = len(_REPORT_FINISHED.findall(report))
    call.n_skipped = len(_REPORT_SKIPPED.findall(report))
    call.battery_overlap = sum(
        1 for c in call.candidates if _norm(c) in _BATTERY_NORM
    )


def _useful_candidates(call: TryTacticsCall, report: str) -> list[str]:
    """Candidates the report marks as applying or finishing."""
    useful: list[str] = []
    for cand in call.candidates:
        shown = re.escape(_norm(cand))
        if re.search(rf"`{shown}` -> (applies|PROOF FINISHED)", report):
            useful.append(_norm(cand))
    return useful


def _analyze_config(
    cache_file: Path,
    arm: str,
    bench: str,
    seed: str,
    summary_row: dict[str, str],
) -> ConfigAnalysis:
    data: list[dict[str, Any]] = yaml.load(  # pyright: ignore[reportAny]
        open(cache_file), Loader=yaml.CSafeLoader
    )
    cfg = ConfigAnalysis(
        name=cache_file.parent.name,
        arm=arm,
        bench=bench,
        seed=seed,
        solved=summary_row["success"] == "True",
        price=float(summary_row["price"]),
        billed_requests=int(summary_row["num_completions"]),
    )
    if data:
        usage: dict[str, Any] | None = data[0]["output"].get("usage_info")
        if usage is not None:
            cfg.first_input_tokens = int(usage.get("prompt_tokens", 0))

    longest = max(data, key=lambda e: len(e["input"]["request"]["chat"]))
    conv = _conversation(longest["input"]["request"]["chat"])

    # The final billed answer never appears inside a request chat;
    # append it so proposals after the last tool round are counted.
    last_out = data[-1]["output"]["outputs"]
    if last_out:
        conv = conv + [
            {
                "role": "assistant",
                "answer": {
                    "content": last_out[0].get("content", ""),
                    "tool_calls": last_out[0].get("tool_calls") or [],
                },
            }
        ]

    turn = 0
    later_texts: list[tuple[int, str]] = []  # (turn, normalized text)
    call_useful: dict[int, list[str]] = {}  # id(call) -> candidates
    for i, m in enumerate(conv):
        if m["role"] != "assistant":
            continue
        turn += 1
        answer: dict[str, Any] = m["answer"]
        tcs: list[dict[str, Any]] = answer.get("tool_calls") or []
        content = str(answer.get("content") or "")
        if not tcs:
            cfg.n_proposals += 1
            head = _norm(content)[:100]
            cfg.outline.append(f"turn {turn}: PROPOSAL {head}")
            later_texts.append((turn, _norm(content)))
            continue
        for tc in tcs:
            name = str(tc["name"])
            args: dict[str, Any] = tc.get("args") or {}
            cfg.tool_calls[name] += 1
            if cfg.first_tool_turn is None:
                cfg.first_tool_turn = turn
            arg_text = _norm(str(args))
            later_texts.append((turn, arg_text))
            cfg.outline.append(f"turn {turn}: {name} {arg_text[:120]}")
            if name != "TryTactics":
                continue
            raw_cands: list[Any] = args.get("candidates") or []
            call = TryTacticsCall(
                turn_index=turn,
                prefix=_norm(str(args.get("tactics", ""))),
                candidates=[str(c) for c in raw_cands],  # pyright: ignore[reportAny]
            )
            # The matching tool result is the next `tool` message.
            report = ""
            m2: dict[str, Any]
            for m2 in conv[i + 1 :]:
                if m2["role"] == "tool":
                    report = str(m2.get("result", ""))
                    break
            _parse_report(call, report)
            useful = _useful_candidates(call, report)
            cfg.trytactics.append(call)
            if useful:
                # Resolved after the loop, once later_texts is known.
                call.followed_through = False
                call_useful[id(call)] = useful
        # Feedback headline for the outline.
        nxt = conv[i + 1] if i + 1 < len(conv) else None
        if nxt is not None and nxt["role"] == "tool":
            headline = _norm(str(nxt.get("result", "")))[:100]
            cfg.outline.append(f"        -> {headline}")
        elif nxt is not None and nxt["role"] == "user":
            headline = _norm(str(nxt.get("content", "")))[:100]
            cfg.outline.append(f"        <- {headline}")

    # Follow-through: a useful candidate reappears in any later turn.
    for call in cfg.trytactics:
        useful = call_useful.get(id(call))
        if useful is None:
            continue
        for t, text in later_texts:
            if t <= call.turn_index:
                continue
            if any(u in text for u in useful):
                call.followed_through = True
                break
    return cfg


def _analyze_arm(
    output_dir: Path, arm: str, summary_csv: Path
) -> list[ConfigAnalysis]:
    summary = _load_summary(summary_csv)
    out: list[ConfigAnalysis] = []
    for cache_file in sorted(output_dir.glob("configs/*/cache.yaml")):
        cfg_name = cache_file.parent.name
        bench, _toolset, _model, seed_part = cfg_name.rsplit("__", 3)
        seed = seed_part.removeprefix("seed")
        row = summary.get(f"{bench}__seed{seed}")
        if row is None:
            continue  # config not in summary (e.g. failed run)
        out.append(_analyze_config(cache_file, arm, bench, seed, row))
    return out


def _pct(k: int, n: int) -> str:
    return f"{k}/{n} ({100 * k / n:.0f}%)" if n else "0/0"


def _arm_summary(cfgs: list[ConfigAnalysis], label: str) -> list[str]:
    n = len(cfgs)
    solved = [c for c in cfgs if c.solved]
    tool_users = [c for c in cfgs if c.tool_calls]
    tt_users = [c for c in cfgs if c.tool_calls.get("TryTactics")]
    calls: Counter[str] = Counter()
    for c in cfgs:
        calls.update(c.tool_calls)
    lines = [
        f"### {label}",
        "",
        f"- configs: {n}, solved: {_pct(len(solved), n)}, total "
        f"spend ${sum(c.price for c in cfgs):.2f}",
        f"- configs making >=1 tool call: {_pct(len(tool_users), n)}"
        f" (TryTactics: {_pct(len(tt_users), n)})",
        f"- tool calls: {dict(calls) or '{}'}",
        f"- tool-using configs solved: "
        f"{_pct(sum(c.solved for c in tool_users), len(tool_users))}"
        f" vs no-tool configs solved: "
        f"{_pct(sum(c.solved for c in cfgs if not c.tool_calls), n - len(tool_users))}",
    ]
    first = [
        c.first_input_tokens for c in cfgs if c.first_input_tokens is not None
    ]
    if first:
        lines.append(
            f"- first-request input tokens (prompt size): "
            f"mean {sum(first) / len(first):.0f}"
        )
    lines.append("")
    return lines


def _trytactics_summary(cfgs: list[ConfigAnalysis]) -> list[str]:
    all_calls = [t for c in cfgs for t in c.trytactics]
    if not all_calls:
        return ["No TryTactics calls found.", ""]
    n_cands = sum(len(t.candidates) for t in all_calls)
    zero_signal = [
        t for t in all_calls if t.n_applies == 0 and t.n_finished == 0
    ]
    with_winner = [t for t in all_calls if t.followed_through is not None]
    followed = [t for t in with_winner if t.followed_through]
    battery = sum(t.battery_overlap for t in all_calls)
    reprobes = 0
    for c in cfgs:
        seen: Counter[str] = Counter(t.prefix for t in c.trytactics)
        reprobes += sum(v - 1 for v in seen.values())
    lines = [
        "### TryTactics call anatomy (probing arms)",
        "",
        f"- calls: {len(all_calls)} across "
        f"{sum(1 for c in cfgs if c.trytactics)} configs; "
        f"candidates/call: {n_cands / len(all_calls):.1f}",
        f"- outcome mix over {n_cands} candidates: "
        f"fails {sum(t.n_fails for t in all_calls)}, "
        f"applies {sum(t.n_applies for t in all_calls)} "
        f"(of which closes goals "
        f"{sum(t.n_closes for t in all_calls)}), "
        f"finished {sum(t.n_finished for t in all_calls)}, "
        f"skipped {sum(t.n_skipped for t in all_calls)}",
        f"- zero-signal calls (no candidate applies): "
        f"{_pct(len(zero_signal), len(all_calls))}",
        f"- battery-duplicate candidates (free elsewhere): "
        f"{_pct(battery, n_cands)}",
        f"- same-prefix re-probes: {reprobes}",
        f"- follow-through on calls with a useful candidate: "
        f"{_pct(len(followed), len(with_winner))}",
        "",
    ]
    return lines


def main() -> None:
    _ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    arms: dict[str, list[ConfigAnalysis]] = {}
    for partition in ("validation", "test"):
        for arm, dirname in (
            ("probing", f"{partition}_probing"),
            ("rich", f"{partition}_agentic"),
        ):
            d = _OUTPUT / dirname
            arms[f"{partition} {arm}"] = _analyze_arm(
                d, arm, d / "results_summary.csv"
            )

    report: list[str] = ["# Probing sweep analysis", ""]
    for label, cfgs in arms.items():
        report.extend(_arm_summary(cfgs, label))
    probing_cfgs = [
        c for label, cs in arms.items() if "probing" in label for c in cs
    ]
    report.extend(_trytactics_summary(probing_cfgs))

    # Per-config table for tool users.
    report.append("### Tool-using configs (probing)")
    report.append("")
    report.append(
        "| config | solved | reqs | price | tool calls | 1st tool turn |"
    )
    report.append("|---|---|---:|---:|---|---:|")
    for c in probing_cfgs:
        if not c.tool_calls:
            continue
        report.append(
            f"| {c.name} | {'Y' if c.solved else 'n'} | "
            f"{c.billed_requests} | ${c.price:.2f} | "
            f"{dict(c.tool_calls)} | {c.first_tool_turn} |"
        )
    report.append("")

    # Outlines for every tool-using config (both arms), for case
    # studies.
    for cfgs in arms.values():
        for c in cfgs:
            if not c.tool_calls and not (
                c.arm == "rich" and c.bench in _CASE_BENCHES
            ):
                continue
            out = _ANALYSIS_DIR / f"outline_{c.arm}_{c.name}.txt"
            out.write_text(
                f"{c.name} | solved={c.solved} | "
                f"reqs={c.billed_requests} | ${c.price:.2f}\n\n"
                + "\n".join(c.outline)
                + "\n"
            )

    report_file = _ANALYSIS_DIR / "report.md"
    report_file.write_text("\n".join(report))
    print("\n".join(report))
    print(f"\nReport: {report_file}")
    print(f"Outlines: {_ANALYSIS_DIR}/outline_*.txt")


# Benches whose rich-control outlines are also dumped (case studies).
_CASE_BENCHES = {
    "mathd_numbertheory_110",
    "amc12a_2002_p12",
    "imo_1965_p1",
    "aimeI_2000_p7",
    "aimeII_2001_p3",
    "mathd_numbertheory_13",
    "imo_1966_p4",
}


if __name__ == "__main__":
    main()
