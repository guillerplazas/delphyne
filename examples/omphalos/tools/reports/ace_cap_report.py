"""
Paired ACE-vs-baseline comparison as a function of the dollar cap.

The round-1 evaluation ran both arms under `LUNA_DOLLAR_CAP` ($0.05)
and found no difference. That cap never binds on a success: the median
solved cell costs ~$0.002, twenty times less, and only the *failures*
ever reach it. So the question the thesis actually cares about — does a
learned playbook pay for itself under a binding budget? — was never
put to either arm.

This tool asks it. A capped run is a strict prefix of a recorded run
(the conversation is deterministic given the cached responses; a cap
only stops it earlier), so the outcome of every cell under every cap is
computable exactly from `tools/budget_ablation.Trace`, with no API
calls. At each cap the two arms are **paired per problem-seed cell**
and the discordant cells are sign-tested, which is what the pooled
counts in `budget_ablation`'s table cannot tell you.

Reading it: the interesting quantity is not any single cap but the
*shape*. A playbook front-loads knowledge, so it should win where only
one or two attempts fit in the budget; it also taxes every request with
extra input tokens, so it should lose where the budget would otherwise
have bought one more attempt. Both effects are visible, and the sign
test says which of them clears the noise floor.

Usage:
    python -m tools.reports.ace_cap_report
    python -m tools.reports.ace_cap_report --json experiments/output/ace_caps.json
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import json
import re
from pathlib import Path


from tools.analysis.budget_ablation import LOG_DOLLAR_CAPS, Trace, load_run  # noqa: E402
from tools.analysis.decision_audit import (
    HISTORICAL_MIN_DISCORDANT as MIN_DISCORDANT_FOR_SIG,
    HISTORICAL_SIGNIFICANCE as SIGNIFICANCE,
    sign_test,
)

BASELINE_RUN = "experiments/output/luna_validation_agentic"
ACE_RUN = "experiments/output/ace_validation_agentic"
MODEL = "gpt-5.6-luna"

BASELINE_SELECT = {"reasoning_effort": "medium", "toolset": "core"}
ACE_SELECT = {"reasoning_effort": "medium", "toolset": "core"}

_NAME_RE = re.compile(
    r"^(?P<bench>.+?)__(?P<arm>.+?)__(?P<model>.+?)__seed(?P<seed>\d+)$"
)

type Cell = tuple[str, str]


def _cells(traces: list[Trace]) -> dict[Cell, Trace]:
    out: dict[Cell, Trace] = {}
    for t in traces:
        m = _NAME_RE.match(t.name)
        assert m is not None, f"unexpected config name {t.name!r}"
        out[(m.group("bench"), m.group("seed"))] = t
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Pair ACE against the baseline at every dollar cap, "
            "offline from recorded per-request prices."
        )
    )
    parser.add_argument("--json", metavar="PATH")
    parser.add_argument(
        "--a-run", default=BASELINE_RUN, help="baseline experiment dir"
    )
    parser.add_argument("--b-run", default=ACE_RUN, help="ACE experiment dir")
    parser.add_argument(
        "--b-arm",
        default=None,
        help=(
            "regex on the ACE config's arm segment (`ace-<sha8>-core-medium`);"
            " selects one playbook when a directory holds several"
        ),
    )
    parser.add_argument("--label", default="validation")
    args = parser.parse_args()

    base = _cells(load_run(str(args.a_run), MODEL, True, BASELINE_SELECT))
    ace_traces = load_run(str(args.b_run), MODEL, True, ACE_SELECT)
    if args.b_arm is not None:
        arm_re = re.compile(str(args.b_arm))
        ace_traces = [
            t
            for t in ace_traces
            if (m := _NAME_RE.match(t.name)) and arm_re.search(m.group("arm"))
        ]
    ace = _cells(ace_traces)
    cells = sorted(set(base) & set(ace))
    assert cells, "no paired cells"

    print(
        f"ACE vs baseline on {args.label}, {len(cells)} paired cells, "
        "as a function of the per-problem dollar cap."
    )
    print("Computed offline from recorded per-request prices.\n")
    header = (
        f"{'cap':>9} | {'base':>5} {'ACE':>5} | {'b-only':>6} "
        f"{'a-only':>6} {'p':>6} | {'ACE spend':>10}"
    )
    print(header)
    print("-" * len(header))

    rows: list[dict[str, float | int | str]] = []
    for cap in LOG_DOLLAR_CAPS:
        b_solved = a_solved = b_only = a_only = 0
        b_spend = a_spend = 0.0
        for c in cells:
            bs, bok = base[c].under_dollar_cap(cap)
            as_, aok = ace[c].under_dollar_cap(cap)
            b_spend += bs
            a_spend += as_
            b_solved += bok
            a_solved += aok
            if bok and not aok:
                b_only += 1
            elif aok and not bok:
                a_only += 1
        p = sign_test(b_only, a_only)
        flag = ""
        if b_only + a_only >= MIN_DISCORDANT_FOR_SIG and p < SIGNIFICANCE:
            flag = "  <- ACE better" if a_only > b_only else "  <- ACE worse"
        print(
            f"{cap:>9.4f} | {b_solved:>5} {a_solved:>5} | {b_only:>6} "
            f"{a_only:>6} {p:>6.3f} | {a_spend / max(b_spend, 1e-12):>9.2f}x"
            f"{flag}"
        )
        rows.append(
            {
                "cap": cap,
                "baseline_solved": b_solved,
                "ace_solved": a_solved,
                "baseline_only": b_only,
                "ace_only": a_only,
                "p": p,
                "baseline_spend": b_spend,
                "ace_spend": a_spend,
            }
        )

    print(
        f"\n`p` is an exact two-sided sign test on the discordant cells."
        f" {MIN_DISCORDANT_FOR_SIG} all-favorable independent discordant cells are"
        f" needed to reach p < {SIGNIFICANCE}, against a noise floor of"
        " 1-3; anything less is a direction, not a result."
    )
    if args.json:
        target = Path(str(args.json))
        if not target.is_absolute():
            target = OMPHALOS_ROOT / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(rows, indent=2))
        print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
