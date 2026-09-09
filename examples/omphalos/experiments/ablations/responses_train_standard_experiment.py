"""
Responses-API arm for the *standard* baseline, on the train partition.

This is the arm where the reasoning cache should pay, and for a reason
unrelated to tools. The standard baseline's cost is dominated by output
tokens (75-85%), and 70-85% of those are reasoning tokens. Chat
Completions never returns reasoning items, so on every feedback cycle
the model re-derives its entire chain of thought from scratch; the
Responses API can hand that state back instead, which is what
`use_reasoning_cache` does.

There is a second, quieter effect. Resending reasoning items keeps the
prompt prefix stable, which is what OpenAI's automatic prompt cache
needs. The standard baseline currently sits at a 43-66% cache hit rate
against the agentic baseline's 85-91% -- and the agentic baseline is
only that high *because* its reasoning is switched off, so nothing
perturbs its prefix. Turning reasoning state into something resendable
should close that gap.

`convert_user_feedback_to_tool` is on (the default): the verifier's
feedback arrives as a user message on every cycle, and OpenAI only
persists the KV cache across tool calls following an assistant message,
not across ordinary user turns.

The control is the archived Chat Completions run in
`experiments/output/train_standard` (gpt-5.6-terra, 10/20, $0.857),
which used the same prompts, problems and feedback budget.

Usage:
    python -m experiments.ablations.responses_train_standard_experiment run
"""

# pyright: strict

import experiments.common.miniF2F_bench as mf
import experiments.common.omphalos_launch as ol

import delphyne as dp

configs = [
    mf.ResponsesStandardConfig(
        bench_name=name,
        model_name=mf.CANONICAL_MODEL,
        temperature=None,
        max_feedback_cycles=3,
        seed=0,
        loop=False,
        reasoning_effort=effort,
    )
    for effort in (None,)
    for name in mf.TRAIN_PROBLEMS
]
"""
`reasoning_effort=None` omits the parameter entirely, which is what the
archived Chat Completions run did: it never set an effort and took the
server default. Leaving it unset here keeps the arms differing in the
API and the reasoning cache alone.
"""


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.ResponsesStandardConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/responses_train_standard",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{cfg.reasoning_effort or 'omitted'}"
            f"__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
