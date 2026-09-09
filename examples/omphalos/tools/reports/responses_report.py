"""
Compare the Responses-API arms against the Chat Completions control.

The comparison has to be careful about two things that a naive table
gets wrong.

**The right control is the capped one.** Every Responses arm runs under
`PER_PROBLEM_DOLLAR_CAP`, so comparing it against the archived
uncapped Chat Completions sweep would credit the API with a saving that
the budget change already delivered. The control here is therefore the
capped replay of that same sweep
(`experiments/output/budget_ablation/replay_cap030.csv`), which is the
identical configuration differing only in API.

**Totals are not evidence.** The 2026-08-12 decision audit found that a
single 20-problem run cannot establish any change converting fewer than
six problems, and that identical configurations disagree on one to
three of them anyway. So arms are compared problem by problem with the
same exact sign test, reusing `decision_audit` rather than
re-implementing it.

Beyond solve counts the report breaks spend into non-cached input,
cached input and output, and pulls `reasoning_tokens` out of each run's
cache. That decomposition is what actually explains a result: the
Responses API is supposed to trade *more* output tokens (reasoning) for
*fewer* turns and a warmer prompt cache, and those three columns show
whether that trade happened.

Usage:
    python -m tools.reports.responses_report
    python -m tools.reports.responses_report --markdown out.md
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import csv
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml


from runtime.model_registry import price_tokens
from tools.analysis.decision_audit import (
    HISTORICAL_MIN_DISCORDANT as MIN_DISCORDANT_FOR_SIG,
    HISTORICAL_SIGNIFICANCE as SIGNIFICANCE,
    Arm,
    Outcome,
    compare,
    load_arm,
)

_OMPHALOS_DIR = OMPHALOS_ROOT

CONTROL_CSV = "experiments/output/budget_ablation/replay_cap030.csv"

AGENTIC_RUN = "experiments/output/responses_train_agentic"
STANDARD_RUN = "experiments/output/responses_train_standard"
VALIDATION_RUN = "experiments/output/responses_validation_agentic"
TEST_RUN = "experiments/output/responses_test_agentic"

WIN_MARGIN = 0.15
"""
Pre-registered: an arm that merely matches the control on solves has to
be at least this much cheaper to count as a win. Fixed before any arm
was run.
"""


@dataclass(frozen=True)
class Breakdown:
    """Where an arm's money went, and how much of it was reasoning."""

    solved: int
    total: int
    spend: float
    non_cached_in: int
    cached_in: int
    output: int
    reasoning: int | None

    @property
    def per_solve(self) -> float:
        return self.spend / self.solved if self.solved else float("nan")

    @property
    def cache_rate(self) -> float:
        total_in = self.non_cached_in + self.cached_in
        return self.cached_in / total_in if total_in else 0.0

    @property
    def reasoning_share(self) -> float:
        if self.reasoning is None or not self.output:
            return float("nan")
        return self.reasoning / self.output


def _reasoning_tokens(run_dir: Path, config: str) -> int | None:
    """
    Reasoning tokens a config spent, summed over its billed requests.

    Not in `results_summary.csv` -- the budget metrics stop at
    input/cached/output -- so it comes from the raw `usage_info` blocks
    the cache preserves. Returns `None` when the field is absent, which
    is what Chat Completions responses look like.
    """
    cache = run_dir / "configs" / config / "cache.yaml"
    if not cache.exists():
        return None
    raw: Any = yaml.safe_load(cache.read_text())
    total = 0
    seen = False
    for entry in cast(Sequence[Mapping[str, Any]], raw):
        output = cast(Mapping[str, Any] | None, entry.get("output"))
        if output is None:
            continue
        usage = cast(Mapping[str, Any] | None, output.get("usage_info"))
        if usage is None:
            continue
        details = cast(
            Mapping[str, Any],
            usage.get("output_tokens_details")
            or usage.get("completion_tokens_details")
            or {},
        )
        if "reasoning_tokens" in details:
            seen = True
            total += int(cast(int, details["reasoning_tokens"]))
    return total if seen else None


def breakdown(run: str, label: str, outcome: Outcome) -> Breakdown:
    """
    Split an arm's spend by token class and count its reasoning tokens.

    `label` is also the middle segment of the config directory name (see
    `config_naming` in the experiment scripts), which is how the raw
    caches are located for the reasoning-token count.
    """
    run_dir = _OMPHALOS_DIR / run
    non_cached = 0
    cached = 0
    output = 0
    reasoning = 0
    saw_reasoning = False
    for name, (inp, cache_tok, out) in outcome.tokens.items():
        non_cached += inp - cache_tok
        cached += cache_tok
        output += out
        config = f"{name}__{label}__{outcome.model[name]}__seed0"
        got = _reasoning_tokens(run_dir, config)
        if got is not None:
            saw_reasoning = True
            reasoning += got
    return Breakdown(
        solved=outcome.n_solved,
        total=outcome.n_problems,
        spend=outcome.repriced,
        non_cached_in=non_cached,
        cached_in=cached,
        output=output,
        reasoning=reasoning if saw_reasoning else None,
    )


@dataclass(frozen=True)
class ControlOutcome:
    """The Chat Completions arm an experiment is judged against."""

    solved: Mapping[str, bool]
    price: Mapping[str, float]
    label: str

    @property
    def n_solved(self) -> int:
        return sum(self.solved.values())

    @property
    def spend(self) -> float:
        return sum(self.price.values())


def load_control(run_filter: str) -> ControlOutcome | None:
    """
    The Chat Completions arm each Responses run should be judged against.

    Agentic arms are compared to the *capped* replay of the archived
    sweep, so the budget change is not double-counted. The standard
    baseline never carried a cap in either arm, so its control is simply
    its archived summary.
    """
    solved: dict[str, bool] = {}
    price: dict[str, float] = {}
    label = "chat (capped)"
    replay = _OMPHALOS_DIR / CONTROL_CSV
    if replay.exists():
        with replay.open() as f:
            for row in csv.DictReader(f):
                if row["run"] != run_filter:
                    continue
                solved[row["bench_name"]] = row["success"] == "True"
                # `repriced` = the replay's tokens at today's rate. The
                # `price` column carries whatever rate the cache
                # recorded, which for a replay is the original run's.
                price[row["bench_name"]] = float(
                    row.get("repriced") or row["price"]
                )
    if not solved:
        label = "chat (archived)"
        archived = _OMPHALOS_DIR / "experiments" / "output" / run_filter
        summary = archived / "results_summary.csv"
        if not summary.exists():
            return None
        with summary.open() as f:
            for row in csv.DictReader(f):
                if row["model_name"] != "gpt-5.6-terra":
                    continue
                solved[row["bench_name"]] = row["success"] == "True"
                price[row["bench_name"]] = price_tokens(
                    row["model_name"],
                    int(row["input_tokens"]),
                    int(row["cached_input_tokens"]),
                    int(row["output_tokens"]),
                )
    if not solved:
        return None
    return ControlOutcome(solved, price, label)


def _as_outcome(control: ControlOutcome) -> Outcome:
    """Wrap the control CSV so `compare` can pair against it."""
    return Outcome(
        arm=Arm("chat_completions (capped)", ""),
        solved=control.solved,
        price=control.price,
        model={k: "gpt-5.6-terra" for k in control.solved},
        tokens={k: (0, 0, 0) for k in control.solved},
    )


def verdict(
    arm: Breakdown, control_solved: int, control_spend: float, p: float
) -> str:
    """
    Apply the rule fixed before the arms were run.

    A win needs either more solves at no extra cost, or the same solves
    at materially less cost. Anything else is reported as what it is --
    and in particular a solve difference that does not clear the sign
    test is reported as *unconfirmed*, never quietly folded into the
    headline. That is the mistake the decision audit was written to
    stop repeating.
    """
    delta = arm.solved - control_solved
    saving = (
        (control_spend - arm.spend) / control_spend if control_spend else 0.0
    )
    money = (
        f"{100 * saving:.0f}% cheaper"
        if saving >= 0
        else f"{-100 * saving:.0f}% dearer"
    )
    if delta > 0:
        confirmed = "confirmed" if p < SIGNIFICANCE else "not confirmed"
        head = f"+{delta} solves ({confirmed})"
        if saving >= 0:
            return f"WIN: {head}, {money}"
        return f"{head}, {money}"
    if delta == 0:
        if saving >= WIN_MARGIN:
            return f"WIN: solves held, {money}"
        return f"solves held, {money}"
    if p < SIGNIFICANCE:
        return f"WORSE: {delta} solves (confirmed), {money}"
    return f"{delta} solves (within noise), {money}"


def collect_arms(run: str) -> list[tuple[str, Outcome]]:
    """Every arm present in a Responses output dir, keyed by its label."""
    summary = _OMPHALOS_DIR / run / "results_summary.csv"
    if not summary.exists():
        return []
    labels: set[str] = set()
    with summary.open() as f:
        for row in csv.DictReader(f):
            effort = row.get("reasoning_effort") or "omitted"
            # A blank cell means the config left the field at its
            # default, which for `convert_user_feedback_to_tool` is
            # True; only the ablation arm writes "False".
            nocvt = (row.get("convert_user_feedback_to_tool") or "") == (
                "False"
            )
            labels.add(f"{effort}{'-nocvt' if nocvt else ''}")
    out: list[tuple[str, Outcome]] = []
    for label in sorted(labels):
        nocvt = label.endswith("-nocvt")
        effort = label.removesuffix("-nocvt")
        select = {
            "reasoning_effort": "" if effort == "omitted" else effort,
            "convert_user_feedback_to_tool": "False" if nocvt else "",
        }
        outcome = load_arm(Arm(label, run, select))
        if outcome is not None:
            out.append((label, outcome))
    return out


def render(runs: Sequence[tuple[str, str]]) -> str:
    buf: list[str] = []
    buf.append("=" * 78)
    buf.append("OMPHALOS RESPONSES-API REPORT")
    buf.append("=" * 78)
    buf.append(
        "Control is the *capped* Chat Completions sweep, so the budget "
        "change is not\ncredited to the API. Arms are paired per problem "
        f"and scored with the same exact\nsign test as the decision "
        f"audit ({MIN_DISCORDANT_FOR_SIG} all-favorable independent discordant problems "
        f"needed for p<{SIGNIFICANCE})."
    )
    for run, control_name in runs:
        control = load_control(control_name)
        arms = collect_arms(run)
        buf.append("")
        buf.append(f"--- {Path(run).name}")
        if not arms:
            buf.append("    (no results yet)")
            continue
        header = (
            f"  {'arm':16}{'solved':>8}{'spend':>9}{'$/solve':>9}"
            f"{'cache':>7}{'reason':>8}{'p':>7}  verdict"
        )
        buf.append(header)
        buf.append("  " + "-" * (len(header) - 2))
        if control is not None:
            buf.append(
                f"  {control.label:16}{control.n_solved:>5}/20"
                f"{control.spend:>9.3f}"
                f"{control.spend / max(control.n_solved, 1):>9.4f}"
                f"{'-':>7}{'-':>8}{'-':>7}  control"
            )
        for label, outcome in arms:
            bd = breakdown(run, label, outcome)
            if control is None:
                buf.append(
                    f"  {label:16}{bd.solved:>5}/{bd.total:<2}"
                    f"{bd.spend:>9.3f}{bd.per_solve:>9.4f}"
                    f"{100 * bd.cache_rate:>6.0f}%"
                    f"{100 * bd.reasoning_share:>7.0f}%"
                    f"{'-':>7}  no control"
                )
                continue
            cmp = compare(_as_outcome(control), outcome)
            buf.append(
                f"  {label:16}{bd.solved:>5}/{bd.total:<2}"
                f"{bd.spend:>9.3f}{bd.per_solve:>9.4f}"
                f"{100 * bd.cache_rate:>6.0f}%"
                f"{100 * bd.reasoning_share:>7.0f}%"
                f"{cmp.p_value:>7.3f}  "
                + verdict(bd, control.n_solved, control.spend, cmp.p_value)
            )
    buf.append("")
    buf.append(
        "cache = share of input tokens served from the prompt cache;\n"
        "reason = share of output tokens spent on reasoning."
    )
    return "\n".join(buf)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the Responses-API arms against the capped Chat "
            "Completions control, per problem and by cost breakdown."
        )
    )
    parser.add_argument(
        "--markdown", metavar="PATH", help="also write markdown to PATH"
    )
    args = parser.parse_args()

    runs = [
        (AGENTIC_RUN, "train_agentic"),
        (STANDARD_RUN, "train_standard"),
        (VALIDATION_RUN, "validation_agentic"),
        (TEST_RUN, "test_agentic"),
    ]
    report = render(runs)
    print(report)

    if args.markdown:
        target = Path(str(args.markdown))
        if not target.is_absolute():
            target = _OMPHALOS_DIR / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"# Omphalos Responses-API report\n\n```\n{report}\n```\n"
        )
        print(f"\nWrote {target.relative_to(_OMPHALOS_DIR)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
