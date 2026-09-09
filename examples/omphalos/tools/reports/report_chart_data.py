"""
Regenerate the chart data embedded in the cost report.

The report at `report/meeting_report.html` carries its
data inline as JSON, so the published page is a single self-contained
file with no network dependency. That is the right shape for an
artifact and the wrong shape for a number you might have to defend, so
this script is the bridge: it recomputes every series from the recorded
runs and rewrites the JSON blocks in place, leaving the prose untouched.

The report lives in `report/`, not under `experiments/output/`, because
`make clean-experiments` deletes that tree — the page is source, not
output, even though everything in it is derived from output.

Four series are produced.

- **`CURVES`** — the budget/solve frontier. For each partition and each
  API, the per-problem dollar cap is swept and the resulting (spend,
  solved) pair recorded. This reuses the insight behind
  `tools/analysis/budget_ablation.py`: a tighter budget cannot make a run issue
  *different* requests, only fewer, so every capped variant is a strict
  prefix of a recorded run and its cost is a prefix sum of prices
  already on disk. The whole curve costs nothing to compute.
- **`BASELINE`** — the same idea applied to the four-arm API
  comparison, swept over the request budget instead of a dollar cap
  because the standard baseline never issues enough requests for a cap
  to bind. Arms are paired on the cells all of them completed.
- **`EFFORT`** — spend and solves against reasoning effort, per model.
  The two curves bottom out in different places, which is the whole
  argument for re-tuning effort after a price change.
- **`TAXONOMY`** — how many problems each configuration hits each class
  of verifier error on, from `tools/analysis/failure_analysis.py`.

Usage:
    python -m tools.reports.report_chart_data            # rewrite the report
    python -m tools.reports.report_chart_data --print    # dump JSON, touch nothing
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import csv
import json
import re
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, cast

import yaml


from runtime.model_registry import price_tokens

_OMPHALOS_DIR = OMPHALOS_ROOT

REPORT = "report/meeting_report.html"

LEGACY_REPORT = "report/cost_report.html"
"""
The 2026-08-12 report. It stays published as a snapshot and is no
longer regenerated: one generator feeding one live report is what keeps
a figure on a page and the data behind it from drifting apart.
"""

CANONICAL = "gpt-5.6-terra"

CAPS = (
    0.004,
    0.005,
    0.006,
    0.008,
    0.01,
    0.0125,
    0.016,
    0.02,
    0.025,
    0.03,
    0.04,
    0.05,
    0.065,
    0.08,
    0.10,
    0.125,
    0.16,
    0.20,
    0.25,
    0.30,
    0.40,
    0.50,
    0.65,
    0.80,
    1.00,
    1.25,
    1.60,
    2.00,
)
"""
Log-spaced (roughly x1.25 per step) rather than linear, and reaching
down to fractions of a cent.

A linear grid calibrated on terra samples luna's entire operating range
in four points and then spends fourteen more on a curve that has
already saturated -- the cheap arm arrives on the chart as a stub of
overlapping dots. Cost is read in ratios, so the sweep is spaced in
ratios. $0.05 and $0.30 are kept exactly: they are the deployed caps.
"""

type Row = dict[str, str]
type Trace = tuple[list[float], int | None]


def _billed(cache: Path, model: str) -> list[float]:
    """
    Per-request prices from a cache, in issue order.

    Recomputed from token counts at *today's* rate rather than read from
    the recorded `price`. The chat-completions arms ran before the
    2026-07-30 price cut and the Responses arms after it, so quoting
    each as billed would fold a 20% price change into an engineering
    comparison. `tools/analysis/reprice.py` is where "what did it cost" lives.

    Entries with no `budget` block were served from Delphyne's own
    request-dedup cache: issued, but free.
    """
    raw: Any = yaml.safe_load(cache.read_text())
    out: list[float] = []
    for entry in cast(Sequence[dict[str, Any]], raw):
        output = cast(dict[str, Any] | None, entry.get("output"))
        if output is None:
            continue
        budget = cast(dict[str, Any] | None, output.get("budget"))
        if budget is None:
            continue
        values = cast(dict[str, Any], budget.get("values") or {})
        if "price" in values:
            out.append(
                price_tokens(
                    model,
                    int(cast(int, values.get("input_tokens", 0))),
                    int(cast(int, values.get("cached_input_tokens", 0))),
                    int(cast(int, values.get("output_tokens", 0))),
                )
            )
    return out


def _rows(run: str, keep: Callable[[Row], bool]) -> list[Row]:
    path = _OMPHALOS_DIR / "experiments" / "output" / run
    summary = path / "results_summary.csv"
    assert summary.exists(), f"no summary for {run}"
    with summary.open() as f:
        return [r for r in csv.DictReader(f) if keep(r)]


def _traces(
    run: str, keep: Callable[[Row], bool], toolset_seg: str
) -> list[Trace]:
    base = _OMPHALOS_DIR / "experiments" / "output" / run / "configs"
    out: list[Trace] = []
    for r in _rows(run, keep):
        name = f"{r['bench_name']}__{toolset_seg}__{r['model_name']}__seed0"
        cache = base / name / "cache.yaml"
        assert cache.exists(), f"missing cache: {cache}"
        solved_at = (
            int(r["num_completions"]) if r["success"] == "True" else None
        )
        out.append((_billed(cache, r["model_name"]), solved_at))
    return out


def _curve(traces: Sequence[Trace]) -> list[dict[str, float | int]]:
    """
    Spend and solves at each cap, under Delphyne's `with_budget` rule:
    a request is denied only once the already-spent amount reaches the
    cap, so the request that crosses the line still runs.
    """
    pts: list[dict[str, float | int]] = []
    for cap in CAPS:
        spend = 0.0
        solved = 0
        for prices, solved_at in traces:
            used = 0
            acc = 0.0
            for price in prices:
                if acc >= cap:
                    break
                acc += price
                used += 1
            spend += acc
            if solved_at is not None and used >= solved_at:
                solved += 1
        pts.append(
            {"cap": round(cap, 3), "spend": round(spend, 4), "solved": solved}
        )
    return pts


def _any_row(_r: Row) -> bool:
    """Keep every row (the arm occupies its output dir alone)."""
    return True


def _is_terra(r: Row) -> bool:
    return r["model_name"] == CANONICAL


def _is_low(r: Row) -> bool:
    """The winning Responses arm: effort `low`, feedback→tool left on."""
    return (
        r.get("reasoning_effort") == "low"
        and (r.get("convert_user_feedback_to_tool") or "") != "False"
    )


def _is_luna_canonical(r: Row) -> bool:
    """The canonical luna arm: `core`, effort `medium`, first seed."""
    return (
        r.get("reasoning_effort") == "medium"
        and (r.get("seed") or "0") == "0"
        and (r.get("toolset") or "core") == "core"
    )


def build_curves() -> dict[str, dict[str, list[dict[str, float | int]]]]:
    """
    The agentic frontier: three configurations per partition.

    All three are on the chart because the argument is a *frontier* —
    what each configuration buys per dollar — and dropping the cheapest
    one leaves the headline claim unillustrated. Their spends differ by
    more than 10x, which is why the chart draws this on a log axis.
    """
    out: dict[str, dict[str, list[dict[str, float | int]]]] = {}
    responses: dict[str, tuple[str, Callable[[Row], bool]]] = {
        "train": ("responses_train_agentic", _is_low),
        "validation": ("responses_validation_agentic", _any_row),
        "test": ("responses_test_agentic", _any_row),
    }
    for part in ("train", "validation", "test"):
        run, keep = responses[part]
        out[part] = {
            "chat": _curve(_traces(f"{part}_agentic", _is_terra, "rich")),
            "responses": _curve(_traces(run, keep, "low")),
            "luna": _curve(
                _traces(
                    f"luna_{part}_agentic", _is_luna_canonical, "core-medium"
                )
            ),
        }
    return out


def _partition_of() -> dict[str, str]:
    """Map every benchmark problem to the partition it belongs to."""
    out: dict[str, str] = {}
    for part in ("train", "validation", "test"):
        path = _OMPHALOS_DIR / "benchmarks" / f"{part}.txt"
        for raw in path.read_text().splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                out[Path(line).stem] = part
    return out


def _key_of(row: Row) -> tuple[str, ...]:
    """Identity of one config, matching `_config_dir_names`."""
    return (
        row["bench_name"],
        row["model_name"],
        row.get("api") or "",
        row.get("use_reasoning_cache") or "",
        row.get("convert_user_feedback_to_tool") or "",
        row.get("seed") or "",
    )


def _config_dir_names(run_dir: Path) -> dict[tuple[str, ...], str]:
    """
    Map config identity to directory name, read from `experiment.yaml`.

    Directory names come from each experiment's own `config_naming`, so
    reconstructing them from summary columns breaks whenever a new sweep
    names things differently. The stored state is the real mapping.
    """
    state = run_dir / "experiment.yaml"
    if not state.exists():
        return {}
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    raw: Any = yaml.load(state.read_text(), Loader=loader)
    configs = cast(dict[str, Any], raw["configs"])
    out: dict[tuple[str, ...], str] = {}
    for name, info in configs.items():
        prm = cast(dict[str, Any], info["params"])
        # `experiment.yaml` stores real values; the summary blanks any
        # value equal to its default, so normalise to the same shape.
        api = str(prm.get("api", "responses"))
        cache = prm.get("use_reasoning_cache", True)
        convert = prm.get("convert_user_feedback_to_tool", True)
        out[
            (
                str(prm["bench_name"]),
                str(prm["model_name"]),
                "" if api == "responses" else api,
                "" if cache is True else str(cache),
                "" if convert is True else str(convert),
                str(prm.get("seed", "")),
            )
        ] = name
    return out


def _no_nocvt(r: Row) -> bool:
    """Agentic Responses rows that kept the feedback conversion on."""
    return (r.get("convert_user_feedback_to_tool") or "") != "False"


def _baseline_arm(row: Row) -> str:
    """
    Which API arm a `baseline_api` row belongs to.

    A summary omits any field equal to its dataclass default, so a blank
    cell means *default*, not *off* — and the defaults here are
    `api="responses"`, both cache flags `True`. Reading a blank as
    `False` silently collapses all four arms into one, which is exactly
    the mistake this function exists to prevent.
    """
    api = row.get("api") or "responses"
    if api == "chat_completions":
        return "chat"
    cache = (row.get("use_reasoning_cache") or "True") == "True"
    if not cache:
        return "responses (no reasoning cache)"
    convert = (row.get("convert_user_feedback_to_tool") or "True") == "True"
    return (
        "responses (cache + feedback\u2192tool)"
        if convert
        else "responses (cache only)"
    )


BASELINE_ARMS = (
    "chat",
    "responses (no reasoning cache)",
    "responses (cache only)",
    "responses (cache + feedback\u2192tool)",
)


type _Cell = tuple[str, str]
"""One problem at one seed: the unit an arm is paired on."""


def build_baseline() -> dict[str, dict[str, list[dict[str, Any]]]]:
    """
    Baseline API comparison: cost against problems solved, as the
    feedback budget grows from one request to four.

    The standard baseline gets at most `max_feedback_cycles + 1`
    requests, so its curve is naturally indexed by request budget rather
    than by a dollar cap that would never bind.

    Arms are compared only on the problem-seed cells that *all* of them
    completed. Two terra configurations died with
    `context_length_exceeded`, and letting one arm carry 40 cells while
    another carries 39 would put a whole extra problem's spend into one
    curve and read as a cost difference.
    """
    run = "baseline_api"
    path = _OMPHALOS_DIR / "experiments" / "output" / run
    if not (path / "results_summary.csv").exists():
        return {}
    partition = _partition_of()
    names = _config_dir_names(path)

    # (key, arm) -> cell -> trace, where a cell is one problem at one
    # seed and a trace is its per-request prices plus the request index
    # the proof landed on (None if it never did).
    traces: dict[tuple[str, str], dict[_Cell, Trace]] = {}
    for row in _rows(run, _any_row):
        part = partition.get(row["bench_name"])
        if part is None:
            continue
        key = f"{row['model_name'].split('-')[-1]} / {part}"
        arm = _baseline_arm(row)
        cfg = names.get(_key_of(row))
        if cfg is None:
            continue
        cache = path / "configs" / cfg / "cache.yaml"
        if not cache.exists():
            continue
        solved_at = (
            int(row["num_completions"]) if row["success"] == "True" else None
        )
        cell = (row["bench_name"], row["seed"])
        traces.setdefault((key, arm), {})[cell] = (
            _billed(cache, row["model_name"]),
            solved_at,
        )

    keys = sorted({key for key, _ in traces})
    out: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for key in keys:
        arms = [arm for k, arm in traces if k == key]
        common: set[_Cell] | None = None
        for arm in arms:
            cells = set(traces[key, arm])
            common = cells if common is None else common & cells
        assert common
        for arm in arms:
            tr = [traces[key, arm][cell] for cell in sorted(common)]
            pts: list[dict[str, Any]] = []
            for budget in (1, 2, 3, 4):
                spend = 0.0
                solved = 0
                for prices, solved_at in tr:
                    used = min(budget, len(prices))
                    spend += sum(prices[:used])
                    if solved_at is not None and used >= solved_at:
                        solved += 1
                pts.append(
                    {
                        "budget": budget,
                        "spend": round(spend, 5),
                        "solved": solved,
                        "total": len(common),
                    }
                )
            out.setdefault(key, {})[arm] = pts
    return out


def build_effort() -> dict[str, list[dict[str, Any]]]:
    """
    Spend and solves against reasoning effort.

    The point of the chart is that the curves bottom out in different
    places: terra's at `low`, luna's at `medium`. That claim only holds
    up if the *toolset* is held fixed, so both models appear on `rich`
    — the only toolset terra was swept on — and luna's canonical `core`
    sweep is drawn alongside to show the optimum does not move with it.
    """
    order = ["none", "low", "medium", "high", "xhigh", "max"]
    out: dict[str, list[dict[str, Any]]] = {}

    def collect(
        label: str, run: str, keep: Callable[[Row], bool], toolset: str
    ) -> None:
        pts: dict[str, dict[str, Any]] = {}
        for row in _rows(run, keep):
            if (row.get("toolset") or "rich") != toolset:
                continue
            effort = row.get("reasoning_effort") or "omitted"
            p = pts.setdefault(
                effort, {"effort": effort, "spend": 0.0, "solved": 0, "n": 0}
            )
            p["spend"] += price_tokens(
                row["model_name"],
                int(row["input_tokens"]),
                int(row["cached_input_tokens"]),
                int(row["output_tokens"]),
            )
            p["solved"] += int(row["success"] == "True")
            p["n"] += 1
        ranked = sorted(
            pts.values(),
            key=lambda p: (
                order.index(str(p["effort"])) if p["effort"] in order else 99
            ),
        )
        for p in ranked:
            p["spend"] = round(float(p["spend"]), 5)
        if ranked:
            out[label] = ranked

    collect("terra · rich", "responses_train_agentic", _no_nocvt, "rich")
    collect("luna · rich", "luna_train_agentic", _any_row, "rich")
    collect("luna · core", "luna_train_agentic", _any_row, "core")
    return out


def build_taxonomy() -> dict[str, dict[str, int]]:
    """
    Problems affected by each error class, per configuration.

    Problems rather than raw verdicts: a single stubborn problem can
    produce dozens of near-identical verdicts, and counting those would
    measure persistence rather than error variety.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tools.analysis.failure_analysis import load_run, tally

    runs = {
        "standard baseline": "test_standard",
        "agentic terra (rich)": "responses_test_agentic",
        "agentic luna (core)": "luna_test_agentic",
    }
    out: dict[str, dict[str, int]] = {}
    for label, run in runs.items():
        path = _OMPHALOS_DIR / "experiments" / "output" / run
        if not (path / "results_summary.csv").exists():
            continue
        out[label] = {
            cls: len(t.problems) for cls, t in tally(load_run(path)).items()
        }
    return out


def rewrite(report: Path, blocks: dict[str, Any]) -> bool:
    """
    Replace each `const NAME = …;` line in the report's script.

    Only those lines are touched, so prose and styling survive a
    regeneration untouched.
    """
    text = report.read_text()
    original = text
    for name, value in blocks.items():
        payload = json.dumps(value, separators=(",", ":"))
        pattern = re.compile(rf"(const {name} = ).*?(;\n)", re.S)
        assert pattern.search(text), f"{name} not found in {report}"
        text = pattern.sub(
            lambda m: m.group(1) + payload + m.group(2), text, count=1
        )
    if text != original:
        report.write_text(text)
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recompute the cost report's chart data from recorded runs "
            "and rewrite the JSON embedded in the report. No API calls."
        )
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="dump",
        help="print the JSON instead of rewriting the report",
    )
    args = parser.parse_args()

    blocks = {
        "CURVES": build_curves(),
        "BASELINE": build_baseline(),
        "EFFORT": build_effort(),
        "TAXONOMY": build_taxonomy(),
    }
    if args.dump:
        print(json.dumps(blocks, indent=1))
        return 0

    report = _OMPHALOS_DIR / REPORT
    assert report.exists(), f"no report at {report}"
    changed = rewrite(report, blocks)
    print(
        f"{'Updated' if changed else 'No change to'} "
        f"{report.relative_to(_OMPHALOS_DIR)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
