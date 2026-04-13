# Proving Math Equalities with Delphyne

This folder is a worked Delphyne example that generates machine-checkable
proofs of simple trigonometric equalities. It is inspired by the _Equations_
environment from the [HyperTree Proof Search paper](https://arxiv.org/pdf/2205.11491)
and ships four strategies of increasing sophistication, a deterministic
SymPy-based checker, and a reproducible experiment harness with a
ready-to-read report notebook.

## What's in this folder

```
mini_eqns/
├── checker.py                     # SymPy-based proof verifier (shared by all strategies)
├── baseline_strategy.py           # Strategy 1: single-shot conversational proof
├── baseline_interactive.py        # Strategy 2: explicit interact loop with checker feedback
├── guided_interactive.py          # Strategy 3: enriched prompts + targeted feedback
├── step_by_step.py                # Strategy 4: sketch + per-step execution (strongest)
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

## The four strategies

Each strategy is a self-contained Delphyne module with its own query classes,
prompts, and policy. They all share `checker.py` as the deterministic ground
truth.

### 1. `baseline_strategy.py` — single-shot with iterative repair

The simplest strategy: a single `ProveEqualityAtOnce` query asks the LLM for a
complete YAML proof in one shot. If the checker rejects it, Delphyne's
`few_shot(..., iterative_mode=True)` resends the error as feedback and lets the
model try again in the same conversation. Good starting point and illustrates
how far a plain conversational loop can go.

### 2. `baseline_interactive.py` — explicit interact loop

Same idea as the baseline, but written with an explicit `dp.interact` loop and
a `check_equality` strategy that runs the checker as a `Compute` effect. This
separates LLM sampling from verification, which makes the search tree legible
and lets you wrap the strategy in `dp.loop()` to retry on failure.

### 3. `guided_interactive.py` — enriched prompts + multi-candidate search

Keeps the interactive loop but ships a richer system prompt (common proof
patterns: subtraction via negation, double-angle, chaining via `trans`,
working from both sides, evaluating at values) and targeted feedback that
reacts to the specific error the checker returned. The policy also requests
several candidate proofs per LLM call (`num_completions > 1`) to broaden the
search under the same feedback budget.

### 4. `step_by_step.py` — sketch + per-step execution (planner / executor)

The strongest strategy in the example. It splits the proof into two phases:

1. **Sketch phase.** A strong model is called **once** to produce a
   machine-readable proof sketch (a numbered list of allowed moves such as
   `rule:sin_neg`, `step`, `trans:[i,j]`). The sketch is syntactically
   validated by `_validate_sketch` before any step is generated — this catches
   banned macro phrases (*"half-angle"*, *"difference of squares"*),
   single-step `trans` no-ops, and overlapping substitutions before they waste
   budget.
2. **Step phase.** A cheap model is called **once per proof step** with the
   validated sketch in its context. The checker runs between every step, so a
   bad step costs one small-model call, not the whole proof. Sub-lemmas are
   supported via `trans:[ids]`.

This planner / executor split is what lets the example reach **22/22** on the
benchmark — see the results table below.

## Checker robustness

Early experiments crashed on malformed LLM output: bracket notation
(`[sin(x)]`), caret exponentiation (`cos^2(x)`), and various unexpected
syntaxes would bubble up as uncaught SymPy parse exceptions. `checker.py`
wraps SymPy parsing and converts every parse failure into a structured
`ProofError`, so the feedback loop stays alive and the LLM gets an actionable
message instead of a traceback.

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

Two identities are reused in the prompts as in-context examples:

```
cos(pi/3) = sin(pi/6)
2*sin(x/2)*cos(x/2) = sin(x)
```

Demo problems (under `demos/`) are deliberately *not* drawn from this
benchmark, to avoid inflating the measured success rate through memorisation.

## Running things

### Prerequisites

- OpenAI API key in `OPENAI_API_KEY`
- Delphyne installed in dev mode: `pip install -e ".[dev]"` from the repo root

### Smoke test (no API calls)

```
make test              # alias of `make full-test`
make full-test         # runs commands/test_baseline_simple.exec.yaml with cache
```

This replays cached LLM responses and asserts that the baseline strategy
still parses and runs end-to-end. Use it after any change to prompts,
`checker.py`, or strategy modules.

### Running experiments

Each strategy has its own runner under `experiments/`, all sharing
`mini_eqns_experiments.py` for configuration dataclasses:

| Command | What it does |
|---------|--------------|
| `python experiments/baseline_experiment.py run` | Run the baseline sweep |
| `python experiments/guided_experiment.py run` | Run the guided sweep |
| `python experiments/step_by_step_experiment.py run` | Run the step-by-step sweep |
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

From the report notebook (best run in each strategy family):

| Strategy | Best configuration | Solved | Total cost |
|----------|--------------------|--------|------------|
| Baseline | `gpt-5.4` / `low` | 19 / 22 | ≈ $1.14 |
| Guided | `gpt-5.4` / `medium` | 19 / 22 | ≈ $2.00 |
| **Step-by-step** | `gpt-5.4` sketch + `gpt-5.4` step / `low` | **22 / 22** | **≈ $1.13** |

**Takeaway.** The saturate runs (`baseline_experiment_saturate_{1,2,3}`) show
that simply handing the baseline a bigger budget caps out at 20 / 22; the two
remaining identities (both *derived product identities*, benchmarks 018 and
019) fall only to step-by-step. The bottleneck is *strategy*, not *budget*:
one good sketch plus many cheap verified steps beats any amount of retries
on a one-shot proof. The notebook's *Why Step-by-Step Works* section walks
through the reasoning.

## Future work

- **Richer rule set.** The current `TRIG_RULES` table is intentionally small.
  Adding the identities that are currently re-derived every proof (for
  example an explicit double-angle rule or a product-to-sum rule) would let
  the planner take shorter paths — at the cost of making the search space
  easier to cheat.
- **Strategy combinations.** Running step-by-step's sketch phase as a fallback
  for guided (or vice versa) is an obvious next experiment.
- **Broader domains.** Everything in this folder is parametric over the rule
  set and the checker, so porting it to algebraic identities beyond
  trigonometry is mostly a matter of writing a new `*_RULES` table and
  corresponding in-context examples.
