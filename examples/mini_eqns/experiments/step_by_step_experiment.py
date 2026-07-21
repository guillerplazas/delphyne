"""
Experiment for the budget-escalation draft-and-repair proof strategy.

Every problem is first attempted by a cheap tier (gpt-5.4 at low
reasoning effort drafting, gpt-5.4-mini repairing, at most 4 LLM
requests, no restart loop). Only problems the cheap tier cannot solve
escalate to the strong tier (gpt-5.4 at medium effort drafting,
gpt-5.4 repairing, restart loop) — in practice, only the two derived
product identities (benchmarks 018 and 019).

For the flat (single-tier) variant this replaces, see runs
`step_by_step_experiment_{10,11,12}` and `prove_step_by_step_policy`.
"""

import delphyne as dp
import mini_eqns_experiments as meq

configs = [
    meq.StepByStepEscalationConfig(
        bench_name=bench_name,
        draft_model_name="gpt-5.4",
        cheap_draft_model_name="gpt-5.4",
        cheap_draft_effort="low",
        cheap_repair_model_name="gpt-5.4-mini",
        cheap_repair_effort="medium",
        cheap_num_completions=2,
        cheap_request_limit=6,
        cheap_dollar_limit=0.04,
        strong_draft_effort="medium",
        strong_repair_model_name="gpt-5.4",
        num_completions=5,
        max_repair_cycles_per_step=4,
        max_total_steps=30,
        max_draft_feedback_cycles=2,
        loop=True,
        max_dollar_budget=0.5,
        seed=seed,
    )
    for bench_name in list(meq.BENCHS.keys())
    for seed in range(1)
]

if __name__ == "__main__":
    dp.Experiment(
        config_class=meq.StepByStepEscalationConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir=f"experiments/report/{dp.path_stem(__file__)}_16",
    ).run_cli()
