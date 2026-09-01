"""
Pre-registered treatment: the runaway-goal caps on validationX.

NOT RUN as of 2026-08-26 (Guille's decision: infrastructure first, this
arm only on request). Registered here so the decision rule is fixed
before any cell is paid.

Motivation (measured on the archived validationX/trainX baselines,
`tools/goal_cap_audit.py`): a failed script can leave hundreds of open
goals; the verifier's battery then probes every goal (17 tactics × up
to 4 s each — 5835 goal-slots in one cell) and the feedback renders
every goal (82 KB in one message). Eight of 160 archived cells hit a
>20-goal check, and five of them were solved anyway — so a cap can
cost solves, which is why it is a treatment and not infrastructure.

Arm: the canonical luna configuration (`x_config`) with
`goal_caps=True` (`pytanque_utils.GoalCaps`: probe 24, render 12,
2000 chars per goal, marker line). Control: `x_validation_agentic`,
same seeds, already paid.

Primary metric: paired solves per (problem, seed) cell, exact sign
test on the discordant cells (power floor: 6 one-sided discordant
cells for p<0.05 at n=40 per seed).
Secondary: paired cell wall-clock (p95) and paired price.
Decision rule: adopt the caps as the new default only if solves are
not worse (discordant losses within the 1–3 cell run-to-run noise
floor) and p95 wall-clock drops by at least 2×; otherwise keep the
uncapped verifier and record the numbers.

Usage (when authorised):
    python experiments/x_goalcap_experiment.py run --max_workers=4
"""

# pyright: strict

from dataclasses import replace

import minif2f_x as x
import omphalos_launch as ol

import delphyne as dp

SEEDS = (0, 1)

configs = [
    replace(
        x.x_config(name, seed, max_dollar_budget=x.X_DOLLAR_CAP),
        goal_caps=True,
    )
    for name in x.VALIDATIONX_PROBLEMS
    for seed in SEEDS
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=x.XAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/x_goalcap_validation_agentic",
        config_naming=x.x_config_name,
    ).run_cli()
