"""
Does showing the problem's own definitions fix the unwinnable prompts?

`pytanque_utils.parse_problem` captured only `Require`/`Import`/`Open
Scope`, so the auxiliary `Definition`/`Fixpoint`/`Notation`
declarations a miniF2F file introduces before its theorem never reached
the model. On those files the prompt asks for a proof about a symbol
the model was never shown — e.g. `choose n k = choose (n-1) k +
choose (n-1) (k-1)` with nothing but `Require Import Arith.` above it.
Verification was unaffected (pytanque loads the real file), which is
why it went unnoticed: it cost prompt fidelity, not correctness.

Scope of the defect, measured over the canonical luna configuration:

- 42 of 488 miniF2F files carry such declarations; **5 of the 60
  benchmark problems** do.
- The canonical configuration has **9 distinct failures** across
  train + validation + test. **4 of them are these problems**
  (`algebra_amgm_prod1toneq1_sum1tongeqn`,
  `numbertheory_nckeqnm1ckpnm1ckm1` on validation;
  `numbertheory_sumkmulnckeqnmul2pownm1`, `imo_1966_p4` on test).

So nearly half of what looked like the capability ceiling may be a
parser gap. This experiment settles it.

**Pre-registered design and decision rule** (written before running):

- One change only: `show_definitions=True`. Model, toolset, effort,
  API, request budget and dollar cap are the canonical ones, and the
  control arm is the *already-paid* baseline run for the same cells
  (`luna_validation_agentic` core-medium seeds {0,1};
  `luna_test_agentic` core-medium seed 0). Nothing is re-run.
- Only the 5 affected problems are run. Every other problem renders a
  byte-identical prompt with the flag on or off, so paying for it
  would buy no information — this is a targeted arm, and the report
  must present it as such rather than as a partition-wide result.
- **Primary: how many of the 4 never-solved affected cells become
  solvable.** This is a directed mechanism test with an a-priori
  argument (the prompt was missing a definition the goal references),
  not a search over arms, so it is read as a count with its cells
  named — never as a partition-level pass-rate claim. The sign test is
  reported for completeness and will be underpowered at n=8; that is
  stated, not hidden.
- Secondary: the 5th problem (`induction_sum2kp1npqsqm1`) is solved
  today *despite* the missing definition. It is included as a control:
  the flag should not break it.

Usage:
    python experiments/defs_experiment.py run --max_workers=4
    python experiments/defs_experiment.py replay
"""

# pyright: strict

from dataclasses import dataclass

import miniF2F_bench as mf
import omphalos_launch as ol

import delphyne as dp

AFFECTED_VALIDATION = (
    "algebra_amgm_prod1toneq1_sum1tongeqn",
    "numbertheory_nckeqnm1ckpnm1ckm1",
    "induction_sum2kp1npqsqm1",
)
AFFECTED_TEST = (
    "numbertheory_sumkmulnckeqnmul2pownm1",
    "imo_1966_p4",
)
"""
The five benchmark problems whose prompt was missing a declaration,
identified by scanning every partition file for a non-empty
pre-theorem preamble (`pytanque_utils._preamble_definitions`). Listed
explicitly rather than recomputed so the arm is a fixed, auditable set.

Provenance note (2026-08-25): this arm was measured with the definitions
appended to the imports block. The prompt now renders them in their own
`## Definitions already in scope` section, so the archived caches of
this experiment no longer replay byte-identically; the recorded results
stand as a measurement of the earlier rendering.
"""


@dataclass
class DefsAgenticConfig(mf.ResponsesAgenticConfig):
    """
    The canonical agentic configuration with `show_definitions` on.

    A subclass rather than a new field on `ResponsesAgenticConfig`,
    following the precedent in `miniF2F_bench.py`: sixteen frozen
    scripts share that class, and keeping their identity space free of
    a knob only this experiment uses is worth one small dataclass.
    """

    show_definitions: bool = True

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        args = super().instantiate(context)
        args.args["show_definitions"] = self.show_definitions
        return args


def _cfg(name: str, seed: int) -> DefsAgenticConfig:
    return DefsAgenticConfig(
        bench_name=name,
        model_name="gpt-5.6-luna",
        temperature=None,
        toolset="core",
        num_requests=32,
        loop=False,
        seed=seed,
        max_dollar_budget=mf.LUNA_DOLLAR_CAP,
        reasoning_effort="medium",
    )


configs = [
    *[_cfg(n, s) for s in (0, 1) for n in AFFECTED_VALIDATION],
    *[_cfg(n, 0) for n in AFFECTED_TEST],
]


if __name__ == "__main__":
    ol.OmphalosExperiment(
        config_class=DefsAgenticConfig,
        context=dp.workspace_execution_context(__file__),
        configs=configs,
        output_dir="experiments/output/defs_agentic",
        config_naming=lambda cfg, _uid: (
            f"{cfg.bench_name}__defs-{cfg.toolset}-{cfg.reasoning_effort}"
            f"__{cfg.model_name}__seed{cfg.seed}"
        ),
    ).run_cli()
