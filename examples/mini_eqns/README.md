# Proving Math Equalities with Delphyne

This folder is a worked Delphyne example that generates machine-checkable
proofs of simple trigonometric equalities. It is inspired by the _Equations_
environment from the [HyperTree Proof Search paper](https://arxiv.org/pdf/2205.11491)
and ships four strategies of increasing sophistication, a deterministic
SymPy-based checker, and a reproducible experiment harness with a
ready-to-read report notebook.

## Why this example

Each Delphyne example highlights a different part of the framework:
`small` is the minimal introduction, `find_invariants` showcases abduction
and best-first search against an external verifier (Why3), and `leandra`
demonstrates tool use and parallel proof decomposition on top of the Lean
toolchain. This example fills a different niche:

- **It is fully self-contained.** The verifier is ~200 lines of SymPy in
  `checker.py` — no external prover, solver, or toolchain to install. This
  makes it the easiest place to study a complete *verifier-in-the-loop*
  pipeline end to end.
- **It is built around `dp.interact`.** All four strategies use Delphyne's
  conversational-agent pattern, where a deterministic checker participates
  in the search loop and every error message becomes structured feedback to
  the model.
- **It routes different models to different queries.** The strongest
  strategy uses an `IPDict` inner policy to send the *planning* query to a
  strong model and the *repair* query to a cheap configuration — model
  heterogeneity expressed purely at the policy level.
- **It administers budgets explicitly.** The final policy is an
  *escalation ladder*: a cheap tier capped in both LLM requests and
  dollars (`with_budget`, `BudgetLimit`) attempts every problem first, and
  `Policy.or_else` escalates only the failures to a strong tier, under a
  per-problem dollar ceiling. Token costs are measured at official
  per-model prices and reported as budget-vs-solved curves.
- **It is a measured strategy-vs-policy comparison.** The four strategies
  solve the same 22-problem benchmark under the same checker, so the
  experiment harness can answer questions like *"does more search budget
  substitute for a better strategy?"* (spoiler: it does not — see the
  results below).

## What's in this folder

```
mini_eqns/
├── checker.py                     # SymPy-based proof verifier (shared by all strategies)
├── baseline_strategy.py           # Strategy 1: single-shot conversational proof
├── baseline_interactive.py        # Strategy 2: explicit interact loop with checker feedback
├── guided_interactive.py          # Strategy 3: enriched prompts + multi-candidate search
├── step_by_step.py                # Strategy 4: draft & repair (strongest)
├── delphyne.yaml                  # Delphyne configuration
├── prompts/                       # Jinja templates, one subfolder per strategy
│   ├── baseline/
│   ├── baseline_interactive/
│   ├── guided_interactive/
│   └── step_by_step/
├── demos/                         # YAML demonstrations, one per strategy
├── benchmark/htps.txt             # 22 trigonometric identities (HTPS Table 9)
├── experiments/                   # Experiment runners + report notebook
│   ├── baseline_experiment.py
│   ├── guided_experiment.py
│   ├── step_by_step_experiment.py
│   ├── mini_eqns_experiments.py   # Shared experiment config dataclasses
│   ├── plot_budget_curves.py      # Regenerates per-experiment SVG/CSV artifacts
│   └── report/
│       ├── mini_eqns_report.ipynb # Headline results, ready to read
│       ├── build_report_notebook.py
│       └── report_utils.py
├── commands/                      # Delphyne smoke tests (used by `make test`)
├── proofs/                        # Sample proof used by test_checker.py
└── test_checker.py                # Unit tests for the checker
```

## The proof format and checker

Everything in this example revolves around a single machine-checkable proof
format, defined in `checker.py`. A proof is a YAML mapping from step numbers
to (equality, justification) pairs:

```yaml
1:
  - ["cos(pi/2 + x)", "cos(pi/2)*cos(x) - sin(pi/2)*sin(x)"]
  - {rule: cos_add, vars: {x: "pi/2", y: "x"}}
2:
  - ["cos(pi/2)*cos(x) - sin(pi/2)*sin(x)", "-sin(pi/2)*sin(x)"]
  - {rule: cos_halfpi, vars: {}}
3:
  - ["-sin(pi/2)*sin(x)", "-sin(x)"]
  - {rule: sin_halfpi, vars: {}}
4:
  - ["cos(pi/2 + x)", "-sin(x)"]
  - {trans: [1, 2, 3]}
```

Each step is justified by a rewrite rule from a small `TRIG_RULES` table
(with explicit variable substitutions), by symmetry (`sym`), transitivity
(`trans`), or by substituting a previously proved equality (`step`). The
checker validates every step with SymPy, treating `sin` and `cos` as
uninterpreted symbols so that no trigonometric knowledge can leak in.

Proofs are parsed from LLM answers with the stock Delphyne parser
(`dp.last_code_block.yaml_as(ch.Proof)`); Pydantic validates the structure,
so no strategy in this folder implements custom answer parsing.

**Checker robustness.** Early experiments crashed on malformed LLM output:
bracket notation (`[sin(x)]`), caret exponentiation (`cos^2(x)`), and other
unexpected syntaxes bubbled up as uncaught SymPy parse exceptions.
`checker.py` wraps SymPy parsing and converts every parse failure into a
structured `ProofError`, so the feedback loop stays alive and the LLM gets
an actionable message instead of a traceback.

## The four strategies

Each strategy is a self-contained Delphyne module with its own query
classes, prompts, and policy. They all share `checker.py` as the
deterministic ground truth, and each one illustrates a different Delphyne
mechanism.

### 1. `baseline_strategy.py` — single-shot with iterative repair

A single `ProveEqualityAtOnce` query asks the LLM for a complete YAML proof
in one shot. If the checker rejects it, Delphyne's
`few_shot(..., iterative_mode=True)` resends the error as feedback and lets
the model try again in the same conversation.

*Illustrates:* the simplest possible oracular program — one query, one
parser, and a conversational repair loop obtained entirely from the
prompting policy.

### 2. `baseline_interactive.py` — explicit interact loop

Same idea, but written with an explicit `dp.interact` loop: an LLM `step`
that proposes a proof and a `process` strategy that runs the checker as a
`Compute` effect and returns either the proof or a `dp.Error` with feedback.

*Illustrates:* `dp.interact` and the `Compute` effect — separating LLM
sampling from verification makes the search tree legible and lets you wrap
the whole strategy in `dp.loop()` to retry on failure.

### 3. `guided_interactive.py` — enriched prompts + multi-candidate search

Keeps the exact same strategy shape as the interactive baseline but ships a
richer system prompt (common proof patterns) and a policy that requests
several candidate proofs per LLM call (`num_completions > 1`) to broaden
the search under the same feedback budget.

*Illustrates:* the strategy/policy separation — every change relative to
strategy 2 lives in prompts and policy parameters, not in the business
logic. The results below show what such policy-only tuning can and cannot
buy.

### 4. `step_by_step.py` — draft & repair (planner / executor)

The strongest strategy. It splits proving into two phases that communicate
through the checker:

1. **Draft.** A strong model is called **once** to write a *complete proof*
   — directly in the checker's YAML format above. The draft is validated
   structurally (on the parsed, typed `Proof` object: unknown rule names,
   no-op `trans` chains, corrupting variable substitutions) and checked
   once in full. If it already passes, the strategy returns immediately.
2. **Verified replay with repair.** Otherwise, the draft is replayed one
   step at a time. A step that verifies is accepted **for free** — no LLM
   call. When a step fails, a cheaper model is asked to repair *just that
   step*, given the checker's error, the draft, and the verified proof so
   far. If the draft runs out before the proof closes, the same repair
   query extends the proof step by step.

The accepted proof is always renumbered sequentially and draft step
references are translated through an explicit id map, so a repaired step
can never invalidate the already-verified prefix.

*Illustrates:* strategy decomposition with inlined sub-strategies, and
heterogeneous model routing — the policy maps each query to its own model
by name:

```python
return sp & {
    "GenerateProofDraft": draft_pp,   # strong model, medium reasoning
    "RepairProofStep": repair_pp,     # cheap model, low reasoning
}
```

On top of this, `prove_step_by_step_escalation_policy` adds a **budget
escalation ladder** without touching the strategy: the same strategy runs
under a cheap configuration first (low-effort draft, `gpt-5.4-mini`
repairs), capped in both requests and dollars, and only problems the cheap
tier cannot solve escalate to the strong configuration:

```python
cheap_budget = dp.BudgetLimit({
    dp.NUM_REQUESTS: cheap_request_limit,   # at most 6 LLM calls
    dp.DOLLAR_PRICE: cheap_dollar_limit,    # at most $0.04
})
cheap = dp.with_budget(cheap_budget) @ prove_step_by_step_policy(...)
strong = prove_step_by_step_policy(...)
return cheap.or_else(strong)
```

In practice 16–19 of the 22 benchmark equalities never touch the strong
tier; only the hard tail pays for high-effort reasoning.

## Why draft & repair is designed this way

**One format, no intermediate language.** An earlier revision of strategy 4
had the planner emit a *proof sketch* in a custom line-based format
(`1. rule:cos_add vars:{x:"pi/2"} → ...`) that was parsed and validated
with regular expressions and then re-translated into proof steps, one
executor call per step. The sketch contained nearly all the information of
a final proof step — in a second syntax. The redesign removed the
intermediate format entirely: the planner now speaks the checker's language
directly, ~150 lines of regex parsing and banned-phrase matching were
deleted, and validation became ordinary code over typed values. The
experiments confirmed the simplification is also a performance win (see the
results table): a correct draft step no longer needs an executor call to be
re-derived from the plan, so 20 of the 22 benchmark equalities are now
proved by a **single LLM call**.

**The checker is the only judge.** Draft validation rejects exactly three
things, each a checker fact expressed on the typed `Proof` object: rule
names that are not in `TRIG_RULES`, `trans` chains with fewer than two
steps, and variable substitutions that corrupt under SymPy's sequential
substitution semantics. Everything else — including a draft that is simply
*wrong* — is accepted and handed to the verified replay, because the
checker pinpoints the failing step far more precisely than any up-front
validation could.

**Targeted feedback beats generic retries.** The sequential-substitution
check is a good example of why the validation exists at all. SymPy applies
`vars` substitutions in order, so `{x: "y", y: "-y"}` silently turns
`cos(x + y)` into `cos(-2*y)` instead of `cos(y - y)`. The checker's
generic error for the resulting step ("rule application failed") sends a
repair model in circles. The typed validator detects the overlap and
answers with the exact rewrite to use (`{x: "-y", y: "y"}`). In our pilot
runs, this one hint was the difference between benchmark 018 failing at
budget exhaustion (11 requests, $0.26) and being solved in two requests
($0.08).

**A worked failure example.** `demos/step_by_step.demo.yaml` walks through
all three code paths on concrete proofs: a draft that verifies outright
(one LLM call total), a draft whose step 2 cites `sin_halfpi` where
`cos_halfpi` is needed (steps 1, 3 and 4 replay for free; one repair call
fixes step 2), and a draft that stops before the closing `trans` step (the
repair query extends it). The demos double as executable specifications:
`delphyne check demos/step_by_step.demo.yaml` replays them against the real
checker.

## Administering the budget

Token cost on this benchmark is dominated by *reasoning tokens* (over 90%
of the spend), and reasoning-token usage is heavy-tailed: the same model at
the same effort level sometimes burns 10× the typical number of tokens on
an unlucky attempt. The escalation policy turns this from an accident into
an administered quantity, using only policy-level primitives:

- **Tiered spending.** The cheap tier is wrapped in
  `with_budget(BudgetLimit({NUM_REQUESTS: 6, DOLLAR_PRICE: 0.04}))`. The
  dollar cap is not redundant with the request cap — it is what cuts off
  run-away reasoning chains that fit in six requests but not in four
  cents.
- **Escalation via `or_else`.** `cheap.or_else(strong)` runs the strong
  configuration only if the cheap search stream produced no proof. A
  failed cheap attempt wastes at most the tier's dollar cap.
- **A per-problem ceiling.** Each experiment config carries a global
  `max_dollar_budget`, so no single equation can blow up a sweep.

Two empirical lessons from tuning the ladder are worth recording, because
both are easy to get wrong:

1. **Small models are not automatically cheap.** An early variant drafted
   with `gpt-5.4-mini` at `medium` effort. Mini's per-token price is 3.3×
   lower, but small models compensate with much longer reasoning chains
   (we observed single mini calls burning 23k+ reasoning tokens), and with
   `num_completions > 1` *every candidate pays its own reasoning tokens*.
   The winning cheap tier instead drafts with the strong model at *low
   effort* and uses mini only for repairs, with few candidates per round.
2. **Know what your meter measures.** Delphyne's pricing table originally
   predated the gpt-5.4 family, and its `pricing="auto"` prefix fallback
   silently billed every gpt-5.4 model at gpt-5 rates — under-billing
   `gpt-5.4` by 1.5× and over-billing `gpt-5.4-mini` by 2.2×. This both
   distorted which policy looked cheapest and silently ate the dollar
   budgets of escalated problems. The table has since been fixed
   (`delphyne.stdlib.standard_models.PRICING` now carries the official
   gpt-5.4 rates), so plain `dp.standard_model` meters correctly, and the
   report re-meters older single-model runs exactly from their recorded
   token counts. Every reported dollar amount is therefore *actual API
   token counts × official OpenAI rates*, and the consistency of the two
   metering paths was confirmed by re-running the best baseline and guided
   configurations from scratch.

## Benchmark

The 22 trigonometric identities from Table 9 of the HTPS paper, shipped in
`benchmark/htps.txt`:

```
sin(pi/2 + x) = cos(x)
cos(pi/2 - x) = sin(x)
cos(pi + x) = -cos(x)
sin(pi - x) = sin(x)
cos(pi/3) = sin(pi/6)
cos(pi/4) = sin(pi/4)
cos(pi/6) = sin(pi/3)
cos(2*pi + x) = cos(x)
sin(2*pi + x) = sin(x)

cos(x)**2 + sin(x)**2 = 1
cos(x) = cos(x/2)**2 - sin(x/2)**2
sin(x + y) - sin(x - y) = 2*cos(x)*sin(y)
cos(x - y) + cos(x + y) = 2*cos(x)*cos(y)
sin(2*x) = 2*sin(x)*cos(x)
cos(2*x) = 1 - 2*sin(x)**2
cos(2*x) = 2*cos(x)**2 - 1
sin(x) = 2*sin(x/2)*cos(x/2)
cos(x + y)*cos(x - y) = cos(x)**2 - sin(y)**2
sin(x + y)*sin(y - x) = cos(x)**2 - cos(y)**2
sin(x)**3 = (3*sin(x) - sin(3*x))/4
sin(3*x) = 3*sin(x) - 4*sin(x)**3
sin(4*x) = cos(x)*(4*sin(x) - 8*sin(x)**3)
```

To avoid inflating the measured success rate through memorisation, both the
demonstration problems (under `demos/`) and the worked examples embedded in
the prompt templates are deliberately *not* drawn from this benchmark. (The
prompt examples of the earlier sketch-based revision leaked three benchmark
items; this was fixed as part of the redesign.)

## Running things

### Prerequisites

- OpenAI API key in `OPENAI_API_KEY`
- Delphyne installed in dev mode: `pip install -e ".[dev]"` from the repo root

### Smoke tests (no API calls)

```
make test                                  # replays the cached baseline command test
delphyne check demos/step_by_step.demo.yaml  # replays a demo against the local checker
```

The demo check executes the strategy with the recorded LLM answers and the
real SymPy checker, so it catches regressions in prompts, parsing, the
strategy code, and `checker.py`. Each strategy has its own demo file under
`demos/`.

### Running experiments

Each strategy has its own runner under `experiments/`, all sharing
`mini_eqns_experiments.py` for configuration dataclasses:

| Command | What it does |
|---------|--------------|
| `python experiments/baseline_experiment.py run` | Run the baseline sweep |
| `python experiments/guided_experiment.py run` | Run the guided sweep |
| `python experiments/step_by_step_experiment.py run` | Run the draft & repair sweep |
| `python experiments/<name>.py run --max_workers=1` | Sequential (debug) mode |
| `python experiments/<name>.py status` | Progress of an in-flight run |
| `python experiments/<name>.py list` | List all configurations in the sweep |
| `python experiments/<name>.py clean_index` | Reset the sweep's internal index |

Experiment results land under `experiments/report/<experiment_name>/`, with
per-equation result YAML files, a `results_summary.csv`, and a
`budget_vs_solved.svg` / `.csv` pair generated by `plot_budget_curves.py`.

### Report notebook

The headline comparison across all three strategy families lives in
[`experiments/report/mini_eqns_report.ipynb`](experiments/report/mini_eqns_report.ipynb).
It is autogenerated by `experiments/report/build_report_notebook.py` —
re-run that script after changing report data rather than editing the
notebook by hand.

## Results summary

All costs below are in **official per-model dollars** (see *Administering
the budget* above — older runs are re-metered exactly from their recorded
token counts). Ranges are across replicas:

| Strategy | Best configuration | Solved | Total cost |
|----------|--------------------|--------|------------|
| Baseline | `gpt-5.4` / `low` | 19 / 22 | ≈ $1.75 |
| Baseline, saturated (2.5× budget) | `gpt-5.4` / `low` | 20 / 22 | ≈ $4.33 |
| Guided | `gpt-5.4` / `medium` | 19 / 22 | ≈ $3.05 |
| Step-by-step (legacy sketch variant) | `gpt-5.4` sketch + step / `low` | 22 / 22 | ≈ $1.92 |
| Step-by-step (flat draft & repair) | `gpt-5.4` draft `medium` + repair `low` | **22 / 22** | $0.65–0.77 |
| **Step-by-step (budget escalation)** | cheap tier + strong fallback | **22 / 22** | **$0.53–0.82** |

**Takeaway.** The saturate runs (`baseline_experiment_saturate_{1,2,3}`)
show that simply handing the baseline a bigger budget caps out at 20 / 22;
the two remaining identities (both *derived product identities*, benchmarks
018 and 019) fall only to the planner/executor split. The bottleneck is
*strategy*, not *budget*. Draft & repair pushes the same idea further: in
the best flat replica, 20 of the 22 equalities are settled by the single
draft call.

**On the escalation numbers.** Across six escalation replicas
(`step_by_step_experiment_{13..18}`), total cost is statistically on par
with the flat strategy — what changes is the *distribution* of spend and
the degree of control. Two-thirds of the equations now cost under two
cents each (low-effort drafts, mini repairs), every tier is capped in
requests and dollars, and essentially all remaining spend sits on the
hard tail (018, 019, and the occasional run-away reasoning chain), where
it buys actual coverage. The run-to-run spread ($0.53–0.82) is dominated
by heavy-tailed reasoning-token usage on those few problems — a property
of the models, not of the search. The notebook's *Administering the
budget* section records two transferable lessons from tuning this ladder:
small models are not automatically cheap (long reasoning chains, and every
extra completion pays its own reasoning tokens), and cost optimization is
meaningless until the meter itself is right.

## Future work

- **Richer rule set.** The current `TRIG_RULES` table is intentionally
  small. Adding the identities that are currently re-derived in every proof
  (for example an explicit double-angle rule) would let drafts take shorter
  paths — at the cost of making the search space easier to cheat.
- **Broader domains.** Everything in this folder is parametric over the
  rule set and the checker, so porting it to algebraic identities beyond
  trigonometry is mostly a matter of writing a new `*_RULES` table and
  corresponding in-context examples.
