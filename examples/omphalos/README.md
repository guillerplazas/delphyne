# Omphalos

Omphalos is a Rocq miniF2F workspace inside Delphyne.

The name comes from the omphalos, the stone at Delphi that marked the center of
the ancient world. Here it marks a smaller center: a focused place where
Delphyne meets Rocq, benchmark problems become machine-checkable proof goals,
and solver work can stay isolated from the rest of the repository.

This directory is intentionally self-contained. The benchmark files, Rocq
project metadata, and regeneration tooling live here; local build output and
temporary upstream checkouts do not belong in version control.

## What This Is

Omphalos contains a categorized copy of the
[LLM4Rocq/miniF2F-rocq](https://github.com/LLM4Rocq/miniF2F-rocq) benchmark.
It has 488 Rocq problems: 244 in `test/` and 244 in `valid/`, grouped by topic.

Each `.v` file contains:

1. A header with the problem name, split, source, informal statement, and
   informal proof.
2. The upstream Rocq imports, theorem statement, and an admitted proof body.

The goal is to provide a clean benchmark surface for experimenting with
Delphyne-guided proof search and human-in-the-loop proof development.

## Layout

```text
.
|-- _CoqProject            Rocq project file and tracked build source of truth
|-- test/                  benchmark test split, categorized by topic
|-- valid/                 miniF2F validation split, categorized by topic
`-- tools/build_layout.py  regeneration script for the benchmark layout
```

The `test/` and `valid/` splits use the same category structure:

```text
aime/
algebra/
amc/
imo/
induction/
mathd/algebra/
mathd/numbertheory/
numbertheory/
```

## Working Locally

Generate the local Rocq make metadata, then build:

```sh
rocq makefile -f _CoqProject -o Makefile
make -j
```

The generated `Makefile`, `Makefile.conf`, `.Makefile.d`, dependency files, and
Rocq build artifacts are ignored. They are local working files, not project
metadata for the Delphyne PR.

To work on a problem, open one of the `.v` files, replace `Admitted.` with a
proof, and type-check that file or the full project.

## Regenerating The Benchmark

Use this only when the upstream Rocq benchmark or the informal HuggingFace data
needs to be refreshed.

```sh
rm -rf _upstream
git clone --depth 1 https://github.com/LLM4Rocq/miniF2F-rocq _upstream
python tools/build_layout.py
rocq makefile -f _CoqProject -o Makefile
make -j
```

`_upstream/` is a temporary local checkout. It is ignored by Git and should be
removed before preparing a PR unless you are actively regenerating the layout.

## Delphyne baselines

This directory ships two Delphyne-based proving systems for miniF2F-Rocq,
both single-stage Hilbert-style loops driven by `dp.interact`:

1. **Standard baseline** (`prove_standard.py`) — the LLM proposes a full
   proof script, [pytanque](https://github.com/LLM4Rocq/pytanque)
   verifies it, the verifier's feedback (failing tactic, error,
   remaining goals) is fed back so the LLM can revise. The LLM has *one*
   action: propose a proof. Skill content (Rocq tactic guidance,
   phrasebook, templates) is baked into the system prompt up front.
2. **Agentic baseline** (`prove_agentic.py`) — same outer loop, but the
   LLM additionally has *exploration* tools:
   - **`ReadSkill(skill_name=...)`** loads a curated Rocq skill
     markdown file under `rocq_skills_data/` into chat history. The
     system prompt only lists *available* skills; their content
     arrives when (and if) the LLM requests it.
   - **`SearchRocq(command=...)`** runs a Rocq introspection command
     (`Search ...`, `Check ...`, `Print ...`, `About ...`,
     `SearchPattern ...`) against the problem's initial proof state
     via pytanque and returns the formatted feedback. This addresses
     the most common failure mode of the standard baseline: the LLM
     guessing a lemma name that doesn't exist. With `SearchRocq` the
     agent can *ask Rocq* before committing to a tactic.
   - **`InspectAt(tactics=..., command=...)`** replays a tactic prefix
     (non-destructively — Rocq proof state is functional) and runs an
     introspection command *at the resulting state*, so `Search` sees
     the hypotheses of the actual stuck subgoal, including induction
     hypotheses. An empty `command` just reports the goals after the
     prefix; an empty prefix inspects the initial state (subsuming
     `SearchRocq`).
   - **`TryAutomation(tactics=...)`** replays a prefix, then tries a
     battery of cheap closing tactics (`lia`, `nra`, `ring`, `easy`,
     ... — see `pytanque_utils.AUTOMATION_BATTERY`) on *each*
     remaining subgoal, with a per-probe timeout, and reports which
     subgoal closes with what. One LLM request buys dozens of Rocq
     attempts.

   The tool repertoire is selected by the `toolset` strategy argument:
   `"lean"` advertises `ReadSkill` + `SearchRocq` and relies on
   **partial proposals** for structural exploration — `check_proof`
   reports the verified prefix and the exact remaining goals whenever
   a script applies cleanly without closing the goal, so a proposal
   doubles as a preview (and wins outright if it happens to close the
   goal). `"rich"` (canonical) advertises `ReadSkill` + `InspectAt` +
   `TryAutomation` for state-level introspection and automation
   probing on top of the same partial-proposal loop. The `"lean"`
   toolset is kept as an ablation lever (its archived command lives
   in `commands/previous/`).

   **Assisted verification.** The agentic verifier
   (`check_proof_assisted`) probes every remaining goal of a failed /
   incomplete proposal with `pytanque_utils.AUTOMATION_BATTERY`,
   reports per-goal closers in the feedback, and finishes the proof
   itself when every remaining goal is routine. The standard baseline
   keeps the plain verifier.

   **Budget semantics.** Every assistant turn — tool round or
   proposal — costs one LLM request, and all turns draw from a single
   `num_requests` pool (the binding constraint; search depth is
   deliberately left unbounded by default via `max_turns=None`). The
   same number is surfaced to the model as `turn_budget` in the
   system prompt, and the model allocates it across exploration and
   proposals at its own discretion.

Prerequisites:

- `rocq` available on your opam switch.
- Conda env `guille` activated (Delphyne + `pytanque` installed).
- An API key for the configured model (default: `gpt-5.6-terra`,
  overridable via `policy_args.model_name`; gpt-5.6 pricing and the
  tool-call `reasoning_effort` workaround live in
  `model_registry.py`).

### Running the baselines

```sh
make test                 # both single-problem smoke tests (cached)
make test-standard        # single problem, standard baseline
make test-agentic         # single problem, agentic "rich" baseline
make regen-command-caches # refresh the smoke caches (real LLM calls)

make test-set1            # 20-problem sweep, both baselines (real API)
make test-set2            # same on the first holdout
make test-set3            # same on the second holdout
make summary-set1         # regenerate results_summary.csv from cache
```

Code map: strategies, queries and policies in `prove_standard.py` /
`prove_agentic.py` (the `ReadSkill` / `SearchRocq` / `InspectAt` /
`TryAutomation` / `TryTactics` tools live there too); model
resolution and gpt-5.6
pricing in `model_registry.py`; the pytanque bridge in
`pytanque_utils.py`; skill loading in `skills.py`; prompts in
`prompts/*.jinja`; experiment configs in
`experiments/miniF2F_bench.py`. `check_proof` reports an
incomplete-but-valid script (all tactics applied, goals remain) as
"incomplete" feedback with the verified prefix and remaining goals,
so both baselines can use partial proposals as previews.

The model sees both the informal statement *and* the informal proof
sketch from each `.v` header — both baselines are therefore
*with-hints*. Further ablations (two-stage informal/formal Hilbert
split, MathComp retrieval, multi-seed runs, full miniF2F sweep via
`experiments/full_*_experiment.py`) are on the thesis roadmap (see
`bachelor_arbeit_plan.md`).

## Benchmark sets & results

Three pairwise-disjoint 20-problem sets drawn from `miniF2F/valid`
live in `benchmarks/`:

- `set1.txt` — the curated development subset (baselines were
  iterated against it);
- `set2.txt` — first holdout (one round of infrastructure fixes was
  mined from its failure traces);
- `set3.txt` — second holdout (fully out-of-sample: never used for
  any iteration).

Both baselines run on every set with one seed, few-shot examples
enabled (see Demonstrations below); the agentic side budgets
`num_requests=32` per problem (one pool for tool calls and proposals,
depth unbounded), the standard side keeps `max_feedback_cycles=3`.
Per-problem dollar caps are deliberately non-binding safety nets:
the request/cycle budget is the controlled variable. Verification is
automation-assisted on the agentic side and plain on the standard
side — a deliberate, documented design choice (the battery is part
of the agentic *system*).

**Models.** Set 1 doubles as a cost/performance frontier over the
gpt-5.6 family (sol / terra / luna; exact pricing in
`model_registry.py`). Sets 2–3 run only the canonical model,
**`gpt-5.6-terra`**, picked by the documented rule (most agentic
successes per dollar on set 1, ties to the cheaper tier — see
`experiments/frontier_report.py`). One experimental condition to
know: gpt-5.6 rejects function tools with reasoning on the Chat
Completions API, so all *agentic* requests run with
`reasoning_effort="none"` while standard requests keep the server
default — an API constraint, not a choice (see `model_registry.py`).

Set 1 frontier (20 problems, one seed):

| model | standard | agentic "rich" | agentic spend | agentic $/solve |
|---|---:|---:|---:|---:|
| gpt-5.6-sol | 18 / 20 | 19 / 20 | $1.55 | $0.081 |
| **gpt-5.6-terra** | 10 / 20 | **20 / 20** | $1.13 | **$0.056** |
| gpt-5.6-luna | 8 / 20 | 15 / 20 | $1.89 | $0.126 |

Canonical results, `gpt-5.6-terra`:

| set | standard | **agentic "rich"** | gap | spend (std / agentic) |
|---|---:|---:|---:|---|
| set 1 (dev) | 10 / 20 | **20 / 20** | +10 | $0.86 / $1.13 |
| set 2 (holdout) | 11 / 20 | **14 / 20** | +3 | $1.43 / $2.97 |
| set 3 (holdout, fully unseen) | 5 / 20 | **14 / 20** | +9 | $1.46 / $4.45 |

On every set the agentic baseline solves a **strict superset** of the
standard baseline's wins. Set 1 numbers are partly in-sample (the
baselines were iterated against it, under gpt-5.4); set 3 is the
cleanest out-of-sample evidence. One seed per config — run-to-run
variance is roughly ±1–2 problems per cell.

Two frontier readings worth stating explicitly: the agentic scaffold
lifts the mid-tier terra *above* the flagship's plain-baseline
performance at a fraction of the cost, and the cheapest tier (luna)
is not the cheapest system — it spends the most agentic dollars on
set 1 because failed searches burn the full request budget.

**"probing" toolset ablation** (`TryTactics`): the `"probing"`
toolset extends `"rich"` with `TryTactics(tactics, candidates)` — up
to 20 model-chosen candidate tactics evaluated against a held proof
state in one call, nothing committed (the native analog of a
stepwise-exploration primitive found valuable during development;
implemented purely on pytanque). Two evaluation rounds on the
holdout sets, two samples per problem
(`experiments/set{2,3}_probing_experiment.py`); v2 adds calibration
(probing-only prompt discipline, a materialized TryTactics few-shot
workflow example gated by a toolset-aware example selector):

| sweep | "rich" (control) | probing v1 s0 / s1 | probing v2 s0 / s1 |
|---|---:|---:|---:|
| set 2 | 14 / 20 | 13 / 12 | 12* / 15 |
| set 3 | 14 / 20 | 14 / 15 | — (aborted) |

*one config unfinished (counted unsolved). The calibration
measurably fixed how the model uses the tool (candidates per call
2.8 → 4.7, zero-signal calls 54% → 24%, adoption 7 → 18 configs,
and v1's robust regression `mathd_numbertheory_110` was recovered
via 9 probe calls) — but solve rates stayed within the ±1–2 noise
band of the control at slightly higher cost (the probing prompt
costs ~15% more input tokens on every request). Verdict per the
pre-registered rule (details and failure-mode study in PROGRESS.md;
analysis tool: `tools/analyze_probing.py`): archived as a measured
negative result for this agent design — under `dfs`/`interact` with
automation-assisted verification and partial-proposal previews, the
tool substitutes for feedback cycles without adding solving power.
`"rich"` remains the canonical toolset; the residual potential of
K-probes-per-request lies in policy-level integration (`bestfs`
fan-out scoring), not prompting.

Outputs land under `experiments/output/set{1,2,3}_{standard,agentic}/`
and `experiments/output/set{2,3}_probing{,_v2}/`
(gitignored; regenerate with the `experiments/set*_experiment.py`
scripts — the probing scripts now write to the `_v2` dirs; the v1
outputs are frozen, their prompt predates the calibration). Earlier iterations — including the final gpt-5.4 sweeps
(set1 9/18, set2 7/14, set3 7/13, billed at gpt-5 fallback rates) —
are archived locally under `experiments/previous/` with per-run
notes.

### Demonstrations & few-shot examples

`demos/standard.demo.yaml` and `demos/agentic.demo.yaml` demonstrate
the **same two problems** — `algebra_binomnegdiscrineq_10alt28asqp1`
and `induction_sum_odd` — both chosen from **outside** all three
benchmark sets (asserted at load time in
`experiments/miniF2F_bench.py`), so demonstrations and evaluation
problems never overlap. The only difference between the baselines'
demos is the agentic elements (tool calls, feedback cycles, assisted
verification). All strategy demos assert `run | success` and are
fully materialized (`tools/materialize_demo.py`), so `delphyne check`
is deterministic and reports zero errors and zero warnings.

Each demo file additionally provides one compact problem → verified
proof pair per demo problem with `example: true`: these enter the
few-shot example database and are injected into every benchmark
prompt. The long materialized traces stay excluded
(`example: false`) — they are regression tests, not prompt content.

To refresh after a prompt/strategy change: `make
regen-command-caches`, restore the `using:` sources in the demo
files, then `python tools/materialize_demo.py <file> --drop-using`.

### Development notes

- Iteration history, checkpoint analyses and per-run insights live in
  `PROGRESS.md` (gitignored, local) and `experiments/previous/*/NOTES.txt`.
- **Pytanque connection**: the bridge uses STDIO mode (a fresh `pet`
  subprocess per verification session). Socket mode (external
  `pet-server`) was considered and deliberately deferred: per-session
  cost is dominated by file compilation, which a persistent server
  does not eliminate, and STDIO needs no server lifecycle management
  under parallel experiment workers. Revisit when scaling to the full
  miniF2F valid split.
- Rocq's micromega tactic caches (`.lia.cache` etc.) accumulate in
  `.rocq_cache/` (gitignored): the `pet` subprocess is spawned with
  its cwd pinned there (`pytanque_utils._pytanque_session`).

## Provenance

- Upstream GitHub: <https://github.com/LLM4Rocq/miniF2F-rocq>
- Upstream snapshot used for this layout:
  `d9480b5e4711a4a8e8334dad3ef2e72c2ec0efdd`
- Upstream dataset: <https://huggingface.co/datasets/LLM4Rocq/miniF2F-rocq>
- Upstream paper:
  [MiniF2F in Rocq: Automatic Translation Between Proof Assistants](https://arxiv.org/abs/2503.04763)
- Upstream license: MIT.
