"""
Offline ablation of the per-problem budget, from recorded runs.

Why this exists: `num_requests` and `max_dollar_budget` are the two
knobs that decide what a sweep costs, and both were set by judgement
rather than measurement -- the dollar cap explicitly so, as a
"deliberately non-binding" runaway guard (`experiments/common/miniF2F_bench.py`).
Measuring them the obvious way means re-running the benchmark once per
candidate value, which is exactly the kind of spend the project is
trying to avoid.

It is not necessary. A tighter budget does not change *which* requests
a run makes, only *how many*: the conversation is deterministic given
the recorded responses, and a cap simply stops it earlier. So every
capped variant of an existing run is a strict prefix of it, and its cost
is the corresponding prefix sum of the recorded per-request prices.
That makes the whole cap curve computable from
`experiments/output/*/configs/*/cache.yaml` with no API calls at all.

Two details make the numbers exact rather than approximate:

- The simulation reproduces Delphyne's own `with_budget` semantics
  (`stdlib/streams.py`): `estimate_budget` predicts request counts but
  not price, so a dollar limit denies the *next* request once the
  already-spent amount reaches the cap -- the request that crosses the
  line still runs. Stopping one request earlier would understate cost.
- Cache entries with no `budget` block are requests that hit Delphyne's
  own request-dedup cache. They were issued but cost nothing, so they
  are skipped: only billed requests move the cumulative spend.

Both assumptions are checked, not assumed: `--verify` asserts that the
reconstructed per-request prices sum to the run's recorded total and
that their count matches `num_completions`.

Usage:
    python -m tools.analysis.budget_ablation                  # dollar-cap curve
    python -m tools.analysis.budget_ablation --requests       # request-cap curve
    python -m tools.analysis.budget_ablation --markdown out.md
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import csv
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, cast

import yaml

# `model_registry` sits at the omphalos root; nothing may separate this
# line from the imports below, or E402 fires.

from runtime.model_registry import price_tokens

_OMPHALOS_DIR = OMPHALOS_ROOT

SUMMARY_NAME = "results_summary.csv"

DEFAULT_RUNS = (
    "experiments/output/train_agentic",
    "experiments/output/validation_agentic",
    "experiments/output/test_agentic",
)

DEFAULT_MODEL = "gpt-5.6-terra"

DOLLAR_CAPS = (0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 2.00)

LOG_DOLLAR_CAPS = (
    0.0005,
    0.001,
    0.0015,
    0.002,
    0.003,
    0.004,
    0.005,
    0.0075,
    0.010,
    0.015,
    0.020,
    0.030,
    0.040,
    0.050,
    0.075,
    0.10,
    0.30,
    2.00,
)
"""
A log-spaced grid reaching far below `DOLLAR_CAPS`, whose floor
($0.05) is exactly `LUNA_DOLLAR_CAP` — so on any luna run the default
grid is a single point and shows a flat line. The interesting region
for luna is two orders of magnitude lower: the median *solved* cell
costs ~$0.002, so a cap only starts to bind below ~$0.01.
"""

REQUEST_CAPS = (2, 4, 6, 8, 10, 12, 16, 20, 24, 32)

TOLERANCE = 1e-9


@dataclass(frozen=True)
class Trace:
    """
    One config's billed requests, in the order the run issued them.

    `prices[i]` is what the i-th billed request cost. `solved_at` is the
    number of billed requests after which the run succeeded, or `None`
    if it never did -- which is what lets the simulation decide whether
    a given cap would still have found the proof.
    """

    name: str
    prices: Sequence[float]
    solved_at: int | None

    def under_dollar_cap(self, cap: float) -> tuple[float, bool]:
        """
        Spend and outcome had a per-problem dollar cap been in force.

        Mirrors `stdlib/streams.stream_with_budget`: the guard denies a
        request only once the already-spent amount has reached the cap,
        so the crossing request is still paid for.
        """
        spent = 0.0
        issued = 0
        for price in self.prices:
            if spent >= cap:
                break
            spent += price
            issued += 1
        return spent, self.solved_at is not None and issued >= self.solved_at

    def under_request_cap(self, cap: int) -> tuple[float, bool]:
        """Spend and outcome had the request budget been `cap`."""
        issued = min(cap, len(self.prices))
        spent = sum(self.prices[:issued])
        return spent, self.solved_at is not None and issued >= self.solved_at


def _billed_prices(
    cache_file: Path, model: str, on: date | None
) -> list[float]:
    """
    Per-request prices from a run's cache, in issue order.

    Prices are recomputed from each request's own token counts, not
    read from the recorded `price`. Both sit in the cache, but the
    recorded one is whatever `OMPHALOS_PRICING` said at request time,
    and rates have moved since (the 2026-07-30 cut).

    `on=None` — the default — prices at *today's* rate, which is the
    right choice for this tool and for every report: these curves
    compare configurations, and a comparison is only meaningful if both
    arms are priced the same way. Our chat-completions arms ran before
    the cut and the Responses arms after it, so pricing each "as billed"
    would fold a 20% price change into what is supposed to be an
    engineering comparison. `tools/analysis/reprice.py` is the tool that answers
    "what did this actually cost"; this one answers "what does it cost".

    Entries without a `budget` block were served from Delphyne's
    request-dedup cache: issued, but free. Skipping them is what keeps
    the cumulative spend faithful.
    """
    # C loader: these caches reach tens of MB and are parsed per arm.
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    with cache_file.open() as f:
        raw: Any = yaml.load(f, Loader=loader)  # type: ignore[reportUnknownMemberType]
    prices: list[float] = []
    inputs: list[int] = []
    for entry in cast(Iterable[Mapping[str, Any]], raw):
        output = cast(Mapping[str, Any] | None, entry.get("output"))
        if output is None:
            continue
        budget = cast(Mapping[str, Any] | None, output.get("budget"))
        if budget is None:
            continue
        values = cast(Mapping[str, Any], budget.get("values") or {})
        if "price" not in values:
            continue
        inp = int(cast(int, values.get("input_tokens", 0)))
        prices.append(
            price_tokens(
                model,
                inp,
                int(cast(int, values.get("cached_input_tokens", 0))),
                int(cast(int, values.get("output_tokens", 0))),
                on=on,
            )
        )
        inputs.append(inp)
    assert inputs == sorted(inputs), (
        f"{cache_file}: input token counts are not monotonic, so the "
        "cache entries are not in conversation order and prefix sums "
        "would not describe a truncated run"
    )
    return prices


def _config_names(
    run_dir: Path,
) -> tuple[tuple[str, ...], dict[tuple[str, ...], str]]:
    """
    Map a config's identifying parameter values to its directory name.

    Config directory names are built by each experiment's own
    `config_naming`, and those schemes differ — the luna sweep encodes
    `toolset-effort` where the older ones encode just `toolset`.
    Reconstructing the name from summary columns therefore breaks the
    moment a new sweep names things differently. `experiment.yaml` holds
    the real mapping, so it is read instead of guessed.
    """
    state = run_dir / "experiment.yaml"
    assert state.exists(), f"no experiment.yaml in {run_dir}"
    raw: Any = yaml.safe_load(state.read_text())
    configs = cast(Mapping[str, Any], raw["configs"])
    fields = _key_fields(configs)
    out: dict[tuple[str, ...], str] = {}
    for name, info in configs.items():
        params = cast(Mapping[str, Any], info["params"])
        out[_config_key(params, fields)] = name
    assert len(out) == len(configs), (
        f"{run_dir}: the config key is not injective — {len(configs)} "
        f"configs collapse to {len(out)} keys, so per-request prices "
        "would be read from the wrong directory. Add a discriminating "
        "field to the config class."
    )
    return fields, out


_SUMMARY_OVERWRITES = frozenset(
    (
        "num_completions",
        "num_requests",
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "price",
        "success",
        "duration",
    )
)
"""
Summary columns written from the *spent* budget, which shadow any
config parameter of the same name. `num_requests` is the one that
bites: a config's `num_requests` is its budget (32), while the column
records what the run consumed (5). Keying on it would match nothing.
"""


def _key_fields(configs: Mapping[str, Any]) -> tuple[str, ...]:
    """
    The parameter names that identify a config within a run.

    Taken as the union of parameter names across the run rather than a
    fixed list, because each sweep adds its own discriminators: the
    ACE adaptation dir has three roles per (bench, model, toolset,
    effort, seed) and would otherwise collapse three configs onto one
    directory. A parameter equal to its default is absent from
    `experiment.yaml` *and* blank in the summary, so both sides agree
    on `""`.
    """
    names: set[str] = set()
    for info in configs.values():
        names |= set(cast(Mapping[str, Any], info["params"]))
    return tuple(sorted(names - _SUMMARY_OVERWRITES))


def _norm(value: object) -> str:
    """`""` for a missing/default value; numbers compared by value."""
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{float(value):g}"
    text = str(value)
    try:
        return f"{float(text):g}"
    except ValueError:
        return text


def _config_key(
    params: Mapping[str, Any], fields: Sequence[str]
) -> tuple[str, ...]:
    """The fields that together identify one config within a run."""
    return tuple(_norm(params.get(f)) for f in fields)


def load_run(
    run: str,
    model: str,
    verify: bool,
    select: Mapping[str, str] | None = None,
) -> list[Trace]:
    """
    Load every config of one experiment dir as a `Trace`.

    `select` narrows to one arm when a directory holds several (the luna
    sweep holds twelve), so a cap curve describes a single configuration
    rather than a blend of them.
    """
    run_dir = _OMPHALOS_DIR / run
    summary = run_dir / SUMMARY_NAME
    assert summary.exists(), f"no {SUMMARY_NAME} in {run_dir}"
    # `None` = today's rate, so every arm in a comparison is priced the
    # same way regardless of when it ran. See `_billed_prices`.
    ran_on = None
    fields, names = _config_names(run_dir)
    traces: list[Trace] = []
    with summary.open() as f:
        for row in csv.DictReader(f):
            if row["model_name"] != model:
                continue
            if select and any(
                (row.get(k) or "") != v for k, v in select.items()
            ):
                continue
            key = _config_key(row, fields)
            config = names.get(key)
            assert config is not None, (
                f"{run}: no config in experiment.yaml matching {key}"
            )
            cache = run_dir / "configs" / config / "cache.yaml"
            assert cache.exists(), f"missing cache for {config}"
            prices = _billed_prices(cache, model, ran_on)
            n_completions = int(row["num_completions"])
            if verify:
                # Both sides are priced at the rate in force when the
                # run happened, so this stays a genuine integrity check
                # (do the per-request records sum to the config total?)
                # rather than a re-derivation of the same stale number.
                total = price_tokens(
                    model,
                    int(row["input_tokens"]),
                    int(row["cached_input_tokens"]),
                    int(row["output_tokens"]),
                    on=ran_on,
                )
                assert abs(sum(prices) - total) < TOLERANCE, (
                    f"{config}: reconstructed ${sum(prices):.6f} does "
                    f"not match the config total ${total:.6f}"
                )
                assert len(prices) == n_completions, (
                    f"{config}: {len(prices)} billed requests vs "
                    f"{n_completions} recorded completions"
                )
            solved_at = n_completions if row["success"] == "True" else None
            traces.append(Trace(config, prices, solved_at))
    assert traces, f"{run}: no configs for model {model}"
    return traces


@dataclass(frozen=True)
class Point:
    """Aggregate outcome of one run under one budget setting."""

    solved: int
    total: int
    spend: float

    @property
    def per_solve(self) -> float:
        return self.spend / self.solved if self.solved else float("nan")


def evaluate(traces: Sequence[Trace], cap: float, *, requests: bool) -> Point:
    solved = 0
    spend = 0.0
    for trace in traces:
        if requests:
            cost, ok = trace.under_request_cap(int(cap))
        else:
            cost, ok = trace.under_dollar_cap(cap)
        spend += cost
        solved += int(ok)
    return Point(solved, len(traces), spend)


def smallest_lossless_cap(
    traces: Sequence[Trace], caps: Sequence[float], *, requests: bool
) -> float | None:
    """
    Smallest cap in `caps` that costs this run nothing in solves.

    Calibrating on a single partition is the point: the cap has to be
    chosen somewhere, and choosing it where the tuning happens (train)
    is what keeps the validation and test figures honest.
    """
    baseline = evaluate(traces, max(caps), requests=requests).solved
    for cap in sorted(caps):
        if evaluate(traces, cap, requests=requests).solved >= baseline:
            return cap
    return None


def build_table(
    runs: Sequence[str],
    model: str,
    *,
    requests: bool,
    verify: bool,
    select: Mapping[str, str] | None = None,
    caps: Sequence[float] | None = None,
) -> tuple[list[str], dict[str, list[Trace]]]:
    loaded = {run: load_run(run, model, verify, select) for run in runs}
    grid: Sequence[float]
    if requests:
        grid = [float(c) for c in REQUEST_CAPS]
    else:
        grid = list(DOLLAR_CAPS) if caps is None else caps
    unit = "requests" if requests else "$/problem"

    header = f"{'cap':>8} | " + " | ".join(f"{Path(r).name:^24}" for r in runs)
    sub = f"{unit:>8} | " + " | ".join(
        f"{'solved':>6}{'spend':>9}{'$/solve':>9}" for _ in runs
    )
    lines = [header, sub, "-" * len(header)]
    for cap in grid:
        cells: list[str] = []
        for run in runs:
            pt = evaluate(loaded[run], cap, requests=requests)
            cells.append(
                f"{pt.solved:>3}/{pt.total:<2}{pt.spend:>9.3f}"
                f"{pt.per_solve:>9.4f}"
            )
        label = f"{int(cap):>8}" if requests else f"{cap:>8.4f}"
        lines.append(f"{label} | " + " | ".join(cells))
    return lines, loaded


def render(
    runs: Sequence[str],
    model: str,
    *,
    requests: bool,
    verify: bool,
    select: Mapping[str, str] | None = None,
    caps: Sequence[float] | None = None,
) -> str:
    lines, loaded = build_table(
        runs,
        model,
        requests=requests,
        verify=verify,
        select=select,
        caps=caps,
    )
    what = "request budget" if requests else "per-problem dollar cap"
    buf = [
        "=" * len(lines[0]),
        f"OMPHALOS BUDGET ABLATION - {what} ({model})",
        "=" * len(lines[0]),
        "",
        "Every figure below is computed from recorded per-request",
        "prices. No API calls were made.",
        "",
    ]
    buf.extend(lines)
    buf.append("")

    # The same grid the table used, so the calibrated cap is always one
    # of the rows a reader can see rather than a value off a different
    # ladder.
    grid: Sequence[float]
    if requests:
        grid = [float(c) for c in REQUEST_CAPS]
    else:
        grid = list(DOLLAR_CAPS) if caps is None else caps
    tuning = runs[0]
    chosen = smallest_lossless_cap(loaded[tuning], grid, requests=requests)
    if chosen is None:
        return "\n".join(buf)

    label = f"{int(chosen)}" if requests else f"${chosen:.2f}"
    buf.append(
        f"Calibrated on {Path(tuning).name} alone: {label} is the "
        f"smallest {what} that costs it no solves."
    )
    buf.append("Applied unchanged to the other partitions:")
    for run in runs:
        base = evaluate(loaded[run], max(grid), requests=requests)
        capped = evaluate(loaded[run], chosen, requests=requests)
        delta = (
            100 * (capped.spend - base.spend) / base.spend
            if base.spend
            else 0.0
        )
        buf.append(
            f"  {Path(run).name:24} {capped.solved}/{capped.total} "
            f"(was {base.solved}/{base.total})   "
            f"${capped.spend:.3f} (was ${base.spend:.3f}, {delta:+.0f}%)"
            f"   ${capped.per_solve:.4f}/solve"
        )
    return "\n".join(buf)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compute what a tighter per-problem budget would have cost "
            "and solved, from the recorded per-request prices of runs "
            "already on disk. Makes no API calls."
        )
    )
    parser.add_argument(
        "runs",
        nargs="*",
        default=list(DEFAULT_RUNS),
        help=f"experiment dirs (default: {' '.join(DEFAULT_RUNS)})",
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, help="model to filter rows by"
    )
    parser.add_argument(
        "--requests",
        action="store_true",
        help="ablate the request budget instead of the dollar cap",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help=(
            "skip the check that reconstructed prices reproduce each "
            "run's recorded total"
        ),
    )
    parser.add_argument(
        "--select",
        metavar="COL=VAL",
        nargs="*",
        default=[],
        help=(
            "restrict to configs whose summary columns match, e.g. "
            "--select toolset=core reasoning_effort=low"
        ),
    )
    parser.add_argument(
        "--caps",
        default="default",
        help=(
            "cap grid: 'default', 'log' (reaches below the luna cap, "
            "where a cap actually binds), or a comma list of dollars"
        ),
    )
    parser.add_argument(
        "--markdown", metavar="PATH", help="also write markdown to PATH"
    )
    args = parser.parse_args()

    runs = [str(r) for r in cast(list[str], args.runs)]
    select = dict(pair.split("=", 1) for pair in cast(list[str], args.select))
    caps_arg = str(args.caps)
    if caps_arg == "default":
        caps = DOLLAR_CAPS
    elif caps_arg == "log":
        caps = LOG_DOLLAR_CAPS
    else:
        caps = tuple(float(c) for c in caps_arg.split(","))
    report = render(
        runs,
        str(args.model),
        requests=bool(args.requests),
        verify=not bool(args.no_verify),
        select=select or None,
        caps=caps,
    )
    print(report)

    if args.markdown:
        target = Path(str(args.markdown))
        if not target.is_absolute():
            target = _OMPHALOS_DIR / target
        target.parent.mkdir(parents=True, exist_ok=True)
        title = "request budget" if args.requests else "dollar cap"
        target.write_text(
            f"# Omphalos budget ablation — {title}\n\n```\n{report}\n```\n"
        )
        print(f"\nWrote {target.relative_to(_OMPHALOS_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
