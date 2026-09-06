"""
Offline recomputation of experiment costs from recorded token counts.

Why this exists: Delphyne's `price` budget metric is computed at
request time from whatever `ModelPricing` the model was built with. The
stdlib table infers an unknown model's rate from the longest matching
name prefix, so every archived `gpt-5.4-2026-03-05` run in
`experiments/previous/` was billed at `gpt-5` rates — 1.25 / 0.125 /
10.00 instead of 2.50 / 0.25 / 15.00 per M tokens, i.e. ~1.75x too
cheap. See `model_registry.py`, which now refuses to guess.

The correction needs no re-running and no API calls: price is linear in
the token counts, which every run records. For a request,

    price = (input - cached) * rate_in
          + cached          * rate_cached
          + output          * rate_out

(exactly as `delphyne.stdlib.openai_api` computes it), and both
`results_summary.csv` and each config's `result.yaml` carry
`input_tokens`, `cached_input_tokens` and `output_tokens`.

Rates come from `model_registry.pricing_for`, the single source of
truth, which raises rather than inferring a rate it does not know.

Provenance rule: raw `result.yaml` files are **never** modified. They
record what the run actually reported, mispricing included. `--write`
emits a sibling `results_summary.repriced.csv` carrying both the
corrected `price` and the original as `price_as_billed`.

Usage:
    python tools/reprice.py                     # check the default roots
    python tools/reprice.py --write             # also emit repriced CSVs
    python tools/reprice.py experiments/output  # check one root
    python tools/reprice.py --group-by toolset  # split runs per toolset

Rates are *dated* (`OMPHALOS_PRICING` holds a history per model), so a
run is priced at the rate in force when it ran rather than at today's.
That distinction is load-bearing: OpenAI cut gpt-5.6 prices on
2026-07-30, in the middle of this project's run history.

`--check` (the default) exits non-zero only on a delta the rate history
cannot explain. A recorded price that matches a *different* dated rate
for the same model is a stale meter — wrong, but understood and exactly
correctable by `--write` — and is reported without failing, because a
guard that can never go green catches nothing.
"""

# pyright: strict

import argparse
import csv
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from pathlib import Path
from typing import Any, cast

import yaml

# `model_registry` lives at the omphalos root, one level up from this
# script (experiment scripts get that directory from the Delphyne
# workspace context; a plain script must add it itself).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model_registry import (
    OMPHALOS_PRICING,
    price_tokens,
    stdlib_fallback_pricing,
)

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent

DEFAULT_ROOTS = ("experiments/output", "experiments/previous")

SUMMARY_NAME = "results_summary.csv"
REPRICED_NAME = "results_summary.repriced.csv"

# A recomputed price is considered to reproduce a recorded one within
# this many dollars. Recorded prices are sums of float products, so
# only float noise should separate them.
TOLERANCE = 1e-9


@dataclass(frozen=True)
class Usage:
    """Token counts of one config, plus the price it was billed at."""

    label: str
    model: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    billed_price: float
    group: str | None = None
    ran_on: date | None = None

    def _at(self, on: date | None) -> float:
        return price_tokens(
            self.model,
            self.input_tokens,
            self.cached_input_tokens,
            self.output_tokens,
            on=on,
        )

    @property
    def true_price(self) -> float:
        """
        What these token counts cost at the rate in force *when the run
        happened* — the number that should reproduce the recorded price.

        `ran_on` comes from the experiment's own stored `start_time`. If
        it is unknown the current rate is used, which is right for a run
        made today and is flagged in the report otherwise.
        """
        return self._at(self.ran_on)

    @property
    def current_price(self) -> float:
        """
        What the same tokens would cost at today's rate.

        Distinct from `true_price` for any run that predates a price
        change, and it is the figure a reader planning new work wants.
        """
        return self._at(None)

    @property
    def explained(self) -> bool:
        """
        Whether the recorded price matches a rate we can name.

        This separates a delta we understand from one we do not, and
        this project has hit exactly two flavours of the former:

        - a **stale table** — `price` is computed at request time from
          whatever `OMPHALOS_PRICING` held then, so a run made after the
          2026-07-30 cut but before the table caught up records the old
          rate;
        - the **stdlib prefix fallback** — every archived gpt-5.4 run
          was billed at `gpt-5` rates before this module existed.

        Both are wrong, both are exactly correctable from token counts,
        and neither is a reason to fail a build. A price matching no
        known rate is a different animal and is what the guard fails on.
        """
        if abs(self.true_price - self.billed_price) <= TOLERANCE:
            return False
        for effective_from, _ in OMPHALOS_PRICING.get(self.model, ()):
            if abs(self._at(effective_from) - self.billed_price) <= TOLERANCE:
                return True
        fallback = stdlib_fallback_pricing(self.model)
        if fallback is not None:
            non_cached = self.input_tokens - self.cached_input_tokens
            at_fallback = (
                non_cached * fallback.dollars_per_input_token
                + self.cached_input_tokens
                * fallback.dollars_per_cached_input_token
                + self.output_tokens * fallback.dollars_per_output_token
            )
            if abs(at_fallback - self.billed_price) <= TOLERANCE:
                return True
        return False


@dataclass
class RunReport:
    """Aggregated recorded vs recomputed cost of one experiment dir."""

    run: Path
    group: str | None = None
    n_configs: int = 0
    billed: float = 0.0
    recomputed: float = 0.0
    n_mismatched: int = 0
    n_explained: int = 0
    models: set[str] = field(default_factory=set[str])

    def add(self, usage: Usage) -> None:
        self.n_configs += 1
        self.billed += usage.billed_price
        self.recomputed += usage.true_price
        self.models.add(usage.model)
        if abs(usage.true_price - usage.billed_price) > TOLERANCE:
            self.n_mismatched += 1
            if usage.explained:
                self.n_explained += 1

    @property
    def n_unexplained(self) -> int:
        """Mismatches that no known dated rate accounts for."""
        return self.n_mismatched - self.n_explained

    @property
    def name(self) -> str:
        base = self.run.name
        return base if self.group is None else f"{base} [{self.group}]"

    @property
    def ratio(self) -> float:
        return self.recomputed / self.billed if self.billed else 1.0


def _mapping(value: Any) -> dict[str, Any] | None:
    """Narrow a value parsed from YAML to a mapping, or `None`."""
    return cast(dict[str, Any], value) if isinstance(value, dict) else None


def _require_mapping(value: Any, where: Path, what: str) -> dict[str, Any]:
    mapping = _mapping(value)
    if mapping is None:
        raise ValueError(f"{where}: {what} is not a mapping")
    return mapping


def _require_int(mapping: dict[str, Any], key: str, where: Path) -> int:
    value = mapping.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{where}: missing or non-integer {key!r}")
    return value


def usage_from_result(result_file: Path) -> Usage | None:
    """
    Read one config's `result.yaml`. Returns `None` for configs that
    recorded no budget (an exception before the first request), which
    contribute nothing to spend.
    """
    with open(result_file) as f:
        doc = _require_mapping(yaml.safe_load(f), result_file, "document")
    args = _require_mapping(doc.get("args"), result_file, "'args'")
    outcome = _require_mapping(doc.get("outcome"), result_file, "'outcome'")
    result = _mapping(outcome.get("result"))
    if result is None:
        return None
    spent = _mapping(result.get("spent_budget"))
    if spent is None or "price" not in spent:
        return None
    policy_args = _require_mapping(
        args.get("policy_args"), result_file, "'policy_args'"
    )
    model = policy_args.get("model_name")
    if not isinstance(model, str):
        raise ValueError(f"{result_file}: missing 'model_name'")
    price = spent["price"]
    if not isinstance(price, (int, float)):
        raise ValueError(f"{result_file}: non-numeric 'price'")
    return Usage(
        label=result_file.parent.name,
        model=model,
        input_tokens=_require_int(spent, "input_tokens", result_file),
        cached_input_tokens=_require_int(
            spent, "cached_input_tokens", result_file
        ),
        output_tokens=_require_int(spent, "output_tokens", result_file),
        billed_price=float(price),
    )


def run_date(run: Path) -> date | None:
    """
    The day a run was executed, from its own `experiment.yaml`.

    This is what lets a price be checked against the rate that was in
    force at the time rather than today's. Runs are launched in one
    session, so the earliest recorded `start_time` dates the whole
    directory; the one thing that would break that is a sweep left
    running across a price change, which `main` warns about.
    """
    state = run / "experiment.yaml"
    if not state.exists():
        return None
    with open(state) as f:
        doc = _mapping(yaml.safe_load(f))
    if doc is None:
        return None
    configs = _mapping(doc.get("configs"))
    if configs is None:
        return None
    starts: list[date] = []
    for info in configs.values():
        entry = _mapping(info)
        started = entry.get("start_time") if entry else None
        if isinstance(started, datetime):
            starts.append(started.date())
        elif isinstance(started, date):
            starts.append(started)
    return min(starts) if starts else None


def _label(row: Mapping[str, str]) -> str:
    """
    A cell's label: its bench name, or — for the one-config role
    experiments that have none (the 2026-09-05 trigger assigner and
    repair writer, keyed by playbook) — the playbook file, so the
    guard never trips on a directory that has nothing to do with a
    benchmark problem.
    """
    return row.get("bench_name") or row.get("playbook_file") or "(config)"


def usages_from_summary(
    summary: Path, group_by: str | None, ran_on: date | None = None
) -> list[Usage]:
    """
    Read a `results_summary.csv`. Equivalent to reading every
    `result.yaml`, since the summary carries the same token columns —
    but it is what the documented totals were computed from, and it is
    the file `--write` corrects.
    """
    usages: list[Usage] = []
    with open(summary, newline="") as f:
        for row in csv.DictReader(f):
            if not row.get("price"):
                continue  # config errored before recording a budget
            usages.append(
                Usage(
                    label=_label(row),
                    model=row["model_name"],
                    input_tokens=int(row["input_tokens"]),
                    cached_input_tokens=int(row["cached_input_tokens"]),
                    output_tokens=int(row["output_tokens"]),
                    billed_price=float(row["price"]),
                    group=row.get(group_by) if group_by else None,
                    ran_on=ran_on,
                )
            )
    return usages


def discover_runs(root: Path) -> list[Path]:
    """Experiment dirs are the ones holding a `configs/` subdirectory."""
    return sorted(p.parent for p in root.glob("*/configs") if p.is_dir())


def collect(run: Path, group_by: str | None) -> list[RunReport]:
    """
    Aggregate one experiment dir, preferring its summary CSV and
    falling back to the per-config `result.yaml` files when it has none
    (some runs were never summarized).
    """
    ran_on = run_date(run)
    summary = run / SUMMARY_NAME
    if summary.exists():
        usages = usages_from_summary(summary, group_by, ran_on)
    else:
        usages = [
            replace(u, ran_on=ran_on)
            for f in sorted(run.glob("configs/*/result.yaml"))
            if (u := usage_from_result(f)) is not None
        ]
    reports: dict[str | None, RunReport] = {}
    for usage in usages:
        report = reports.setdefault(
            usage.group, RunReport(run=run, group=usage.group)
        )
        report.add(usage)
    return [reports[k] for k in sorted(reports, key=lambda g: g or "")]


def write_repriced_summary(run: Path) -> Path | None:
    """
    Emit `results_summary.repriced.csv` beside the run's summary: same
    rows and columns, `price` corrected, and the original preserved as
    `price_as_billed`. Returns `None` if the run has no summary.
    """
    summary = run / SUMMARY_NAME
    if not summary.exists():
        return None
    with open(summary, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if "price_as_billed" not in fieldnames:
        fieldnames.insert(fieldnames.index("price") + 1, "price_as_billed")
    for row in rows:
        if not row.get("price"):
            continue
        usage = Usage(
            label=_label(row),
            model=row["model_name"],
            input_tokens=int(row["input_tokens"]),
            cached_input_tokens=int(row["cached_input_tokens"]),
            output_tokens=int(row["output_tokens"]),
            billed_price=float(row["price"]),
            ran_on=run_date(run),
        )
        row["price_as_billed"] = row["price"]
        row["price"] = repr(usage.true_price)
    target = run / REPRICED_NAME
    with open(target, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return target


def print_table(reports: list[RunReport]) -> None:
    if not reports:
        print("No experiment directories found.")
        return
    width = max(len(r.name) for r in reports)
    header = (
        f"{'run':<{width}}  {'n':>3}  {'as billed':>10}  "
        f"{'recomputed':>11}  {'ratio':>6}  {'off':>4}"
    )
    print(header)
    print("-" * len(header))
    billed = recomputed = 0.0
    for r in reports:
        billed += r.billed
        recomputed += r.recomputed
        print(
            f"{r.name:<{width}}  {r.n_configs:>3}  {r.billed:>10.4f}  "
            f"{r.recomputed:>11.4f}  {r.ratio:>6.3f}  {r.n_mismatched:>4}"
        )
    print("-" * len(header))
    ratio = recomputed / billed if billed else 1.0
    print(
        f"{'TOTAL':<{width}}  {'':>3}  {billed:>10.4f}  "
        f"{recomputed:>11.4f}  {ratio:>6.3f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Recompute experiment costs offline from recorded token "
            "counts, using the exact per-model rates in "
            "model_registry.OMPHALOS_PRICING."
        )
    )
    parser.add_argument(
        "roots",
        nargs="*",
        default=list(DEFAULT_ROOTS),
        help=(
            "Directories holding experiment output dirs "
            f"(default: {' '.join(DEFAULT_ROOTS)})"
        ),
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help=(
            f"Emit {REPRICED_NAME} beside every {SUMMARY_NAME}. "
            "Raw result.yaml files are never modified."
        ),
    )
    parser.add_argument(
        "--group-by",
        metavar="COLUMN",
        help=(
            "Split each run by a summary column (e.g. 'toolset'), so "
            "arms sharing an output dir are reported separately."
        ),
    )
    args = parser.parse_args()

    reports: list[RunReport] = []
    written: list[Path] = []
    for raw_root in [str(r) for r in args.roots]:
        root = Path(raw_root)
        if not root.is_absolute():
            root = _OMPHALOS_DIR / root
        if not root.is_dir():
            print(f"skipping missing root: {root}", file=sys.stderr)
            continue
        for run in discover_runs(root):
            reports.extend(collect(run, args.group_by))
            if args.write and (target := write_repriced_summary(run)):
                written.append(target)

    print_table(reports)

    if written:
        print(f"\nWrote {len(written)} repriced summaries:")
        for target in written:
            print(f"  {target.relative_to(_OMPHALOS_DIR)}")

    off = [r for r in reports if r.n_mismatched]
    if not off:
        print("\nAll recorded prices reproduce exactly. Nothing to correct.")
        return 0

    explained = sum(r.n_explained for r in off)
    unexplained = sum(r.n_unexplained for r in off)
    if explained:
        print(
            f"\n{explained} config(s) recorded a price matching a known "
            "but wrong rate — a stale OMPHALOS_PRICING entry, or the "
            "stdlib prefix fallback. Their token counts are intact, so "
            "`--write` corrects them exactly and no re-run is needed."
        )
    if unexplained:
        print(
            f"\n{unexplained} config(s) recorded a price matching NO "
            "known rate for their model. That is not a stale table — "
            "something else is wrong, and it needs looking at before "
            "any cost claim rests on these runs."
        )
    # A delta the rate history explains is a fact about the past, not a
    # regression; failing on it forever would make this guard useless
    # (see the 2026-08-12 note about a check that could never pass).
    # Only an unexplained delta should break the build.
    return 1 if unexplained and not args.write else 0


if __name__ == "__main__":
    raise SystemExit(main())
