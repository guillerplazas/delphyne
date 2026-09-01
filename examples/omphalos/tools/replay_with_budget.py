"""
Re-run an archived sweep under a tighter budget, entirely from cache.

`tools/budget_ablation.py` predicts what a per-problem dollar cap would
have cost and solved by summing recorded per-request prices. That is
arithmetic on a CSV, and arithmetic can be wrong about semantics: it
assumes the cap bites exactly where `stdlib/streams.stream_with_budget`
would make it bite, and that a shorter run reproduces the longer run's
prefix step for step.

This script removes the assumption by actually executing the capped
configuration through Delphyne -- the real strategy, the real policy,
the real budget machinery -- with `cache_mode="replay"`. In that mode a
request that is not already in the cache raises instead of reaching the
network (`delphyne.utils.caching.CacheMode`), so a clean run is a proof
that **no API call was made**: every request the capped run issued was
one the original run had already issued and paid for.

That is the whole trick. A tighter budget cannot invent new requests,
only stop earlier, so the capped run is a strict prefix of the archived
one and the recorded cache is guaranteed to cover it. Budget ablations
that would otherwise cost a full sweep each become free.

Each config is read back from the experiment's own stored state and
re-instantiated as a real `miniF2F_bench.AgenticConfig` with one field
changed, so the replayed run differs from the archived one in exactly
the budget and nothing else. (That is also why `pyrightconfig.json`
puts `experiments/` on `extraPaths`: pyright only searches a file's own
directory for top-level imports.)

Nothing is written: caches are read-only in this mode, `experiment.yaml`
is never touched, and results are printed -- optionally to a CSV of the
caller's choosing.

Usage:
    python tools/replay_with_budget.py --cap 0.30
    python tools/replay_with_budget.py --cap 0.30 --runs test_agentic
    python tools/replay_with_budget.py --cap 0.30 --csv out.csv
"""

# pyright: strict

import argparse
import csv
import io
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, cast

import yaml

# `model_registry` lives at the omphalos root and `miniF2F_bench` in
# `experiments/`; a plain script has to put both on the path itself
# (mirrors the shim in `tools/reprice.py`). Nothing may sit between
# these lines and the imports below, or E402 fires.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "experiments"))

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command

import miniF2F_bench as mf
from model_registry import price_tokens

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent

SUMMARY_NAME = "results_summary.csv"

DEFAULT_RUNS = ("train_agentic", "validation_agentic", "test_agentic")


@dataclass(frozen=True)
class Replayed:
    """Outcome of one config replayed under a tighter budget."""

    run: str
    bench_name: str
    config_name: str
    model_name: str
    success: bool
    price: float
    num_requests: float
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    recorded_success: bool
    recorded_price: float

    @property
    def repriced(self) -> float:
        """
        Cost of this replay at today's rate.

        `price` cannot serve: a cache replay returns the *recorded*
        `LLMResponse`, budget included, so it reports whatever rate was
        in force when the original request was made. The token counts
        are the durable part, which is why they are carried here.
        """
        return price_tokens(
            self.model_name,
            self.input_tokens,
            self.cached_input_tokens,
            self.output_tokens,
        )

    @property
    def solve_preserved(self) -> bool:
        return self.success or not self.recorded_success


def _spent(result: Any, key: str) -> float:
    """Pull one metric out of a run's reported `spent_budget`."""
    spent = cast(dict[str, float], result.spent_budget)
    return float(spent.get(key, 0.0))


def stored_params(run: str) -> dict[str, dict[str, Any]]:
    """
    The configs an experiment actually ran, keyed by config name.

    `experiment.yaml` is the only faithful source for this. The summary
    CSV looks like it would do -- it has a `num_requests` column -- but
    that column records the requests a config *consumed*, not the budget
    it was given. Rebuilding from it silently rewrites `turn_budget`,
    which is interpolated into the system prompt ("you have roughly N
    assistant turns"), which changes the request hash, which turns every
    replay into a cache miss. The `replay` cache mode catches that
    immediately, which is the second reason to prefer it over a mode
    that would quietly re-issue the request.
    """
    state_file = (
        _OMPHALOS_DIR / "experiments" / "output" / run / "experiment.yaml"
    )
    assert state_file.exists(), f"no experiment.yaml in {run}"
    raw: Any = yaml.safe_load(state_file.read_text())
    configs = cast(dict[str, Any], raw["configs"])
    return {
        name: cast(dict[str, Any], info["params"])
        for name, info in configs.items()
    }


def _rebuild_config(params: dict[str, Any], cap: float) -> mf.AgenticConfig:
    """
    Turn a stored parameter dict back into a real `AgenticConfig`.

    Fields are read out one at a time rather than splatted, so a stored
    config whose shape has drifted from the current dataclass fails
    here with a clear error instead of somewhere inside the strategy.
    """
    temperature = params.get("temperature")
    max_turns = params.get("max_turns")
    return mf.AgenticConfig(
        bench_name=str(params["bench_name"]),
        model_name=str(params["model_name"]),
        temperature=None if temperature is None else float(temperature),
        toolset=str(params["toolset"]),
        num_requests=int(params["num_requests"]),
        seed=int(params["seed"]),
        max_turns=None if max_turns is None else int(max_turns),
        loop=bool(params.get("loop", False)),
        max_dollar_budget=cap,
    )


def replay_config(
    run: str,
    config_name: str,
    params: dict[str, Any],
    cap: float,
    recorded: dict[str, str],
) -> Replayed:
    """
    Replay one archived config with `max_dollar_budget` set to `cap`.

    Every field except the budget comes from the stored config, so the
    replayed run differs from the archived one in exactly one way.
    """
    output_dir = _OMPHALOS_DIR / "experiments" / "output" / run
    config = _rebuild_config(params, cap)
    args = config.instantiate(None)
    args.cache_file = f"configs/{config_name}/cache.yaml"
    args.embeddings_cache_file = f"configs/{config_name}/embeddings.cache.h5"
    # `replay` raises on a cache miss, which is what makes a successful
    # run evidence that nothing was sent to the provider.
    args.cache_mode = "replay"
    args.export_raw_trace = False
    args.export_browsable_trace = False
    args.export_log = False

    context = replace(
        dp.workspace_execution_context(__file__), cache_root=output_dir
    )
    # `run_command` prints a header and status lines; this tool prints
    # its own table, so the command's own chatter is swallowed.
    sink = io.StringIO()
    with redirect_stdout(sink):
        result = run_command(
            command=run_strategy,
            args=args,
            ctx=context,
            add_header=False,
        )
    outcome = cast(Any, result.result)
    return Replayed(
        run=run,
        bench_name=str(params["bench_name"]),
        config_name=config_name,
        model_name=str(params["model_name"]),
        success=bool(outcome.success),
        price=_spent(outcome, dp.DOLLAR_PRICE),
        num_requests=_spent(outcome, dp.NUM_REQUESTS),
        input_tokens=int(_spent(outcome, dp.NUM_INPUT_TOKENS)),
        cached_input_tokens=int(_spent(outcome, dp.NUM_CACHED_INPUT_TOKENS)),
        output_tokens=int(_spent(outcome, dp.NUM_OUTPUT_TOKENS)),
        recorded_success=recorded["success"] == "True",
        recorded_price=float(recorded["price"]),
    )


def replay_run(run: str, model: str, cap: float, seed: int) -> list[Replayed]:
    """Replay every config of one run under the given cap."""
    summary = _OMPHALOS_DIR / "experiments" / "output" / run / SUMMARY_NAME
    assert summary.exists(), f"no summary for {run}"
    rows: dict[str, dict[str, str]] = {}
    with summary.open() as f:
        for row in csv.DictReader(f):
            toolset = row.get("toolset", "rich")
            name = (
                f"{row['bench_name']}__{toolset}__{row['model_name']}"
                f"__seed{row.get('seed', '0')}"
            )
            rows[name] = row

    params = stored_params(run)
    todo = [
        (name, p)
        for name, p in sorted(params.items())
        if p.get("model_name") == model
        and int(p.get("seed", 0)) == seed
        and name in rows
    ]
    out: list[Replayed] = []
    for i, (name, p) in enumerate(todo, start=1):
        print(f"  [{i}/{len(todo)}] {p['bench_name']}", file=sys.stderr)
        out.append(replay_config(run, name, p, cap, rows[name]))
    return out


def report(results: list[Replayed], cap: float) -> str:
    buf: list[str] = []
    buf.append(
        f"Replayed under a ${cap:.2f} per-problem cap, entirely from "
        "cache (cache_mode='replay': a miss would have raised)."
    )
    buf.append("")
    header = (
        f"{'run':22}{'solved':>10}{'was':>7}{'spend':>10}{'was':>10}"
        f"{'delta':>8}"
    )
    buf.append(header)
    buf.append("-" * len(header))
    for run in sorted({r.run for r in results}):
        rows = [r for r in results if r.run == run]
        solved = sum(r.success for r in rows)
        was_solved = sum(r.recorded_success for r in rows)
        spend = sum(r.price for r in rows)
        was_spend = sum(r.recorded_price for r in rows)
        delta = 100 * (spend - was_spend) / was_spend if was_spend else 0
        buf.append(
            f"{run:22}{solved:>7}/{len(rows):<2}{was_solved:>7}"
            f"{spend:>10.3f}{was_spend:>10.3f}{delta:>7.0f}%"
        )
    lost = [r for r in results if not r.solve_preserved]
    buf.append("")
    if lost:
        buf.append(f"Solves lost to the cap ({len(lost)}):")
        for r in lost:
            buf.append(
                f"  {r.run}/{r.bench_name} (needed ${r.recorded_price:.3f})"
            )
    else:
        buf.append("No solve was lost to the cap.")
    return "\n".join(buf)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Replay archived agentic sweeps under a tighter "
            "per-problem dollar cap, using only cached requests."
        )
    )
    parser.add_argument(
        "--cap",
        type=float,
        default=mf.PER_PROBLEM_DOLLAR_CAP,
        help="per-problem dollar cap to replay under",
    )
    parser.add_argument(
        "--runs",
        nargs="*",
        default=list(DEFAULT_RUNS),
        help=f"experiment dirs (default: {' '.join(DEFAULT_RUNS)})",
    )
    parser.add_argument("--model", default=mf.CANONICAL_MODEL)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--csv", metavar="PATH", help="write per-problem results to PATH"
    )
    args = parser.parse_args()

    cap = float(cast(float, args.cap))
    results: list[Replayed] = []
    for run in cast(list[str], args.runs):
        print(f"Replaying {run}...", file=sys.stderr)
        results.extend(
            replay_run(str(run), str(args.model), cap, int(args.seed))
        )

    print(report(results, cap))

    if args.csv:
        target = Path(str(args.csv))
        if not target.is_absolute():
            target = _OMPHALOS_DIR / target
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "run",
                    "bench_name",
                    "success",
                    "price",
                    "repriced",
                    "num_requests",
                    "input_tokens",
                    "cached_input_tokens",
                    "output_tokens",
                    "recorded_success",
                    "recorded_price",
                ]
            )
            for r in results:
                writer.writerow(
                    [
                        r.run,
                        r.bench_name,
                        r.success,
                        f"{r.price:.10f}",
                        f"{r.repriced:.10f}",
                        r.num_requests,
                        r.input_tokens,
                        r.cached_input_tokens,
                        r.output_tokens,
                        r.recorded_success,
                        f"{r.recorded_price:.10f}",
                    ]
                )
        print(f"\nWrote {target.relative_to(_OMPHALOS_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
