"""
Chat Completions vs Responses on the *standard* baseline, decomposed.

The agentic loop gained a lot from the Responses API; the standard
baseline appears to lose. That contrast is the interesting part of the
migration, and until now it rested on a single seed, on train, on terra:

    chat completions   10/20   $0.685   59 turns   2,763 input tok/turn
    responses          13/20   $1.349   56 turns  10,202 input tok/turn

Three more solves for double the money, with input per turn up 3.7x
while output actually *falls* and the turn count barely moves. The
mechanism was inferred rather than shown, which is what these four arms
fix. They separate the two things "switching to Responses" bundles:

    A0  chat            control
    A1  responses, reasoning cache OFF          the API switch alone
    A2  responses, cache ON, feedback->tool OFF the cost of resending
                                                reasoning items
    A3  responses, cache ON, feedback->tool ON  the archived config

`reasoning_effort` is omitted on every arm, exactly as both archived
runs have it, so nothing here is about reasoning *level* — only about
the API and its two cache features.

Why the decomposition matters: `use_reasoning_cache` is what resends
earlier reasoning items, and is therefore the suspected cause of the
input inflation. `convert_user_feedback_to_tool` only governs whether
the KV cache survives a user turn, so it can only matter once the cache
is on. Bundling them would leave the report saying "Responses is dearer
on short loops" without being able to say why.

Grid: luna carries the full factorial because at its rates 320 configs
cost ~$1.50; terra runs train only, to show the effect is not an
artefact of a weak model. **Test is deliberately untouched** — this is
a study, not a final confirmation, and that partition's value is that
it has been looked at once per configuration.

Usage:
    python experiments/baseline_api_experiment.py run --max_workers=4
    python experiments/baseline_api_experiment.py --models=gpt-5.6-luna run
    python experiments/baseline_api_experiment.py --arms=chat,resp-nocache run
"""

# pyright: strict

import sys
from dataclasses import dataclass

import miniF2F_bench as mf
import omphalos_launch as ol

import delphyne as dp


@dataclass(frozen=True)
class Arm:
    """One point of the API/cache factorial."""

    label: str
    api: str
    use_reasoning_cache: bool
    convert_user_feedback_to_tool: bool


ARMS: tuple[Arm, ...] = (
    Arm("chat", "chat_completions", False, False),
    Arm("resp-nocache", "responses", False, False),
    Arm("resp-cache", "responses", True, False),
    Arm("resp-cache-cvt", "responses", True, True),
)
"""
The `chat` arm's two cache flags are ignored: `make_model` passes `None`
for both unless the API is `responses`, which is also what stops the
stdlib raising on a reasoning cache it cannot honour.
"""

MODELS: tuple[str, ...] = ("gpt-5.6-luna", "gpt-5.6-terra")

PARTITIONS: tuple[str, ...] = ("train", "validation")

SEEDS: tuple[int, ...] = (0, 1)
"""
Two seeds. The 2026-08-12 decision audit put a number on what one run
can show — identical configurations disagree on 1-3 problems of 20 —
and the effect being measured here is of that order.
"""

# terra is ~10x dearer than luna, so it confirms the effect on train
# rather than paying for the full grid. Keeping this explicit (rather
# than silently skipping) means the asymmetry is visible in the code.
TERRA_PARTITIONS: tuple[str, ...] = ("train",)

_PROBLEMS = {
    "train": mf.TRAIN_PROBLEMS,
    "validation": mf.VALIDATION_PROBLEMS,
}


def _selected(name: str, values: tuple[str, ...]) -> tuple[str, ...]:
    """
    Values named by a `--<name>=a,b` flag, or all of them.

    Parsed here and stripped from `sys.argv` because `run_cli` uses
    `fire`, which knows nothing about these flags. Running one slice at
    a time is what keeps spend checkable between arms.
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


def _configs() -> list[mf.ResponsesStandardConfig]:
    arms = set(_selected("arms", tuple(a.label for a in ARMS)))
    models = _selected("models", MODELS)
    partitions = _selected("partitions", PARTITIONS)
    out: list[mf.ResponsesStandardConfig] = []
    for arm in ARMS:
        if arm.label not in arms:
            continue
        for model in models:
            allowed = (
                TERRA_PARTITIONS if model == "gpt-5.6-terra" else partitions
            )
            for partition in partitions:
                if partition not in allowed:
                    continue
                for seed in SEEDS:
                    for name in _PROBLEMS[partition]:
                        out.append(
                            mf.ResponsesStandardConfig(
                                bench_name=name,
                                model_name=model,
                                temperature=None,
                                max_feedback_cycles=3,
                                seed=seed,
                                loop=False,
                                api=arm.api,
                                reasoning_effort=None,
                                use_reasoning_cache=arm.use_reasoning_cache,
                                convert_user_feedback_to_tool=(
                                    arm.convert_user_feedback_to_tool
                                ),
                            )
                        )
    return out


def _arm_label(cfg: mf.ResponsesStandardConfig) -> str:
    for arm in ARMS:
        if (
            arm.api == cfg.api
            and arm.use_reasoning_cache == cfg.use_reasoning_cache
            and arm.convert_user_feedback_to_tool
            == cfg.convert_user_feedback_to_tool
        ):
            return arm.label
    raise AssertionError(f"config matches no arm: {cfg}")


configs = _configs()


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=mf.ResponsesStandardConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/baseline_api",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__{_arm_label(cfg)}__{cfg.model_name}"
            f"__seed{cfg.seed}"
        ),
    ).run_cli()
