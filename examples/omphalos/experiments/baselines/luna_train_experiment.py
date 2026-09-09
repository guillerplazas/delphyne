"""
Exhaustive luna sweep on train: every reasoning effort x both toolsets.

Why luna is worth a serious look now. OpenAI cut its price by 80% on
2026-07-30, so it is **10x cheaper than terra on every token class**
rather than the 2.5x it was during the 2026-07-21 frontier sweep. That
alone changes the verdict on data already recorded: repriced at current
rates, the archived chat-completions luna run solves 15/20 for $0.378
against terra's 20/20 for $0.901 — five problems fewer, but a better
deal per solve ($0.025 vs $0.045).

And that is luna's *worst* condition. Two things say it should improve:

- It hit its ceiling at a $0.15 cap (15/20 at $0.15, $0.30 and $2.00
  alike), so it was capability-limited, not budget-limited.
- Reasoning is exactly what fixed that failure mode on terra, which
  went 192 turns -> 110 and 18/20 -> 20/20 on the `none` -> `low` step.
  Luna has never been run with reasoning at all: on Chat Completions
  gpt-5.6 refuses tools unless reasoning is off, and the Responses
  migration that lifted the constraint was only ever measured on terra.

If luna under Responses merely matches terra's token volumes, the test
partition costs $0.185 instead of $1.852.

**Both effort and toolset are swept rather than inherited from terra.**
A weaker model may lean on tool support differently, and at luna's rates
240 configs cost a few dollars, so there is no reason to guess. That
also fills a gap in the terra story: terra was only measured at
`none`/`low`/`medium`, where `low -> medium` was already negative, and
whether the curve has a second knee higher up is unknown for any model.

The cap is deliberately loose here. Its real value is *derived* from
this sweep afterwards with `tools/analysis/budget_ablation.py`, which recovers
the whole cap curve from recorded per-request prices — so a cap tight
enough to truncate the high-effort arms would destroy the very data
needed to choose it. Terra's $0.30 would be ~10x too loose at luna's
rates in any case (HINTS #8: caps must track model prices).

Usage:
    python -m experiments.baselines.luna_train_experiment run --max_workers=4
    python -m experiments.baselines.luna_train_experiment --efforts=low,high run
"""

# pyright: strict

import sys

import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp

EFFORTS: tuple[str, ...] = ("none", "low", "medium", "high", "xhigh", "max")
"""
Every level gpt-5.6-luna accepts, confirmed by
`tools/maintenance/probe_responses_api.py` rather than assumed. `"minimal"` is
absent because the provider rejects it; `xhigh` and `max` are reachable
only through `model_registry.OmphalosReasoningEffort`, which is wider
than the stdlib literal.
"""

TOOLSETS: tuple[str, ...] = ("core", "rich")

LOOSE_CAP = 0.10
"""
Several times the scaled equivalent of terra's $0.30 (which at luna's
rates would be ~$0.03), so that even the `max` arm is measured rather
than truncated. Not a recommendation — the cap to ship is whatever
`budget_ablation` reads off this sweep.
"""


def _selected(name: str, values: tuple[str, ...]) -> tuple[str, ...]:
    """
    Values named by a `--<name>=a,b` flag, or all of them.

    Parsed here and stripped from `sys.argv` because `run_cli` uses
    `fire`, which knows nothing about these flags. Being able to run one
    slice at a time is what keeps spend checkable between arms.
    """
    prefix = f"--{name}="
    chosen: set[str] | None = None
    for arg in list(sys.argv[1:]):
        if arg.startswith(prefix):
            chosen = {v.strip() for v in arg[len(prefix) :].split(",")}
            sys.argv.remove(arg)
    if chosen is None:
        return values
    unknown = chosen - set(values)
    assert not unknown, (
        f"unknown {name}: {', '.join(sorted(unknown))}. "
        f"Known: {', '.join(values)}"
    )
    return tuple(v for v in values if v in chosen)


configs = [
    mf.ResponsesAgenticConfig(
        bench_name=name,
        model_name="gpt-5.6-luna",
        temperature=None,
        toolset=toolset,
        num_requests=32,
        loop=False,
        seed=0,
        max_dollar_budget=LOOSE_CAP,
        reasoning_effort=effort,
    )
    for effort in _selected("efforts", EFFORTS)
    for toolset in _selected("toolsets", TOOLSETS)
    for name in mf.TRAIN_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.ResponsesAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/luna_train_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.toolset}-{cfg.reasoning_effort}"
            f"__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
