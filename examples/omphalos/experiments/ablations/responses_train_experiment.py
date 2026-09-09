"""
Responses-API arms for the agentic baseline, on the train partition.

The question this answers: **is the agentic baseline being handicapped
by having no reasoning?**

Every archived agentic number was measured with `reasoning_effort="none"`
-- not by choice, but because gpt-5.6 rejects function tools on Chat
Completions unless reasoning is switched off entirely. The standard
baseline it beats has always had reasoning on. The Responses API removes
the constraint (verified by `tools/maintenance/probe_responses_api.py`: `low`,
`medium` and `high` are all accepted alongside function tools), so the
comparison can finally be made.

The arms:

    A0  responses, effort "none"    control: isolates the API switch
    A1  responses, effort "low"     does any reasoning help?
    A2  responses, effort "medium"  the interior of the curve
    A1' A1 without feedback->tool   does the caching trick matter?

A0 exists because two things change at once otherwise. Switching API and
switching reasoning on in the same step would leave any difference
unattributable -- the exact mistake the 2026-08-12 decision audit found
running through the whole earlier history of this project.

Every arm carries `PER_PROBLEM_DOLLAR_CAP`, so an arm cannot win by
spending more: the comparison is at matched budget. The hypothesis being
tested is specifically that reasoning *pays for itself* -- cost grows
superlinearly with conversation length, so converging in fewer turns can
be cheaper even though each turn costs more.

Pre-registered decision rule, fixed before any of this was run: an arm
wins only if it improves solves at equal-or-lower spend, or holds solves
at >=15% lower spend, judged by a paired sign test against the noise
floor from `tools/analysis/decision_audit.py` (1-3 problems of 20) rather than by
comparing totals.

Usage:
    python -m experiments.ablations.responses_train_experiment run --max_workers=4
    python -m experiments.ablations.responses_train_experiment --arms=a0-none,a1-low run
    python -m experiments.ablations.responses_train_experiment force-summary

`--arms` restricts the sweep to a subset, so the arms can be run one at
a time and the spend checked between them. All arms share one output
directory regardless, so a later arm still lands beside the earlier ones
and the comparison stays paired.
"""

# pyright: strict

import sys

import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp

ARMS: tuple[tuple[str, str | None, bool], ...] = (
    # (label, reasoning_effort, convert_user_feedback_to_tool)
    ("a0-none", "none", True),
    ("a1-low", "low", True),
    ("a2-medium", "medium", True),
    ("a1x-low-nocvt", "low", False),
)
"""
Note that `"minimal"` is absent on purpose: gpt-5.6 rejects it on the
Responses API (supported values are none/low/medium/high/xhigh/max), as
`tools/maintenance/probe_responses_api.py` establishes. `xhigh` and `max` are also
absent -- the stdlib `ReasoningEffort` literal does not carry them, and
at a $0.30 cap they would exhaust the budget on the first hard problem.
"""


def _label(cfg: mf.ResponsesAgenticConfig) -> str:
    effort = cfg.reasoning_effort or "omitted"
    suffix = "" if cfg.convert_user_feedback_to_tool else "-nocvt"
    return f"{effort}{suffix}"


def _selected_arms() -> tuple[tuple[str, str | None, bool], ...]:
    """
    Arms named by a `--arms=a,b` flag, or all of them.

    The flag is consumed here rather than by `run_cli`, whose `fire`
    CLI has no notion of it, and is stripped from `sys.argv` so the
    subcommand parsing downstream is unaffected.
    """
    prefix = "--arms="
    chosen: set[str] | None = None
    for arg in list(sys.argv[1:]):
        if arg.startswith(prefix):
            chosen = {a.strip() for a in arg[len(prefix) :].split(",")}
            sys.argv.remove(arg)
    if chosen is None:
        return ARMS
    known = {arm for arm, _, _ in ARMS}
    unknown = chosen - known
    assert not unknown, (
        f"unknown arm(s): {', '.join(sorted(unknown))}. "
        f"Known: {', '.join(sorted(known))}"
    )
    return tuple(a for a in ARMS if a[0] in chosen)


configs = [
    mf.ResponsesAgenticConfig(
        bench_name=name,
        model_name=mf.CANONICAL_MODEL,
        temperature=None,
        toolset="rich",
        num_requests=32,
        loop=False,
        seed=0,
        max_dollar_budget=mf.PER_PROBLEM_DOLLAR_CAP,
        reasoning_effort=effort,
        convert_user_feedback_to_tool=convert,
    )
    for _arm, effort, convert in _selected_arms()
    for name in mf.TRAIN_PROBLEMS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.ResponsesAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/responses_train_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{_label(cfg)}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
