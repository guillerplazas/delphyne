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

The benchmark itself lives under `miniF2F/` (paths below are relative
to it; everything else in this directory is the Delphyne side):

```text
miniF2F/
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

Generate the local Rocq make metadata, then build (from `miniF2F/`,
not from this directory — running these at this level would clobber
the project `Makefile`):

```sh
cd miniF2F
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
cd miniF2F
rm -rf _upstream
git clone --depth 1 https://github.com/LLM4Rocq/miniF2F-rocq _upstream
python tools/build_layout.py
rocq makefile -f _CoqProject -o Makefile
make -j
```

(Note `miniF2F/tools/`, the benchmark regeneration script, is distinct
from the top-level `tools/`, which holds offline analysis scripts.)

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
   `"core"` advertises `ReadSkill` + `SearchRocq` and relies on
   **partial proposals** for structural exploration — `check_proof`
   reports the verified prefix and the exact remaining goals whenever
   a script applies cleanly without closing the goal, so a proposal
   doubles as a preview (and wins outright if it happens to close the
   goal). `"rich"` advertises `ReadSkill` + `InspectAt` +
   `TryAutomation` for state-level introspection and automation
   probing on top of the same partial-proposal loop.

   `"rich"` is the strategy default and the toolset every terra
   benchmark was run on, but the **current canonical configuration**
   (`gpt-5.6-luna`, see below) uses `"core"`: the two are
   indistinguishable on solves and `"core"` is cheaper. An archived
   `"core"` command lives in `commands/previous/`.

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
make test                 # all single-problem smoke tests (cached, no API calls)
make test-standard        # single problem, standard baseline
make test-agentic         # single problem, agentic "rich" baseline
make test-probing         # single problem, agentic "probing" baseline
make test-luna            # single problem, canonical luna config (core/medium/$0.05)
make regen-command-caches # refresh the smoke caches (real LLM calls)

make sweep-train          # 20-problem sweep, both baselines (real API)
make sweep-validation     # same on the validation partition
make sweep-test           # same on the test partition
make summary-train        # regenerate results_summary.csv from cache
make reprice              # audit recorded costs offline (no API calls)
```

The sweep targets are `sweep-*`, not `test-*`, so that `make test`
keeps meaning "run the single-problem smoke tests" and does not read
as "run the test partition".

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
`master_arbeit_plan.md`).

## Benchmark partitions & results

Three pairwise-disjoint 20-problem partitions live in `benchmarks/`,
named for the role each one plays:

- `train.txt` — the curated development partition; the baselines were
  iterated against it, so its numbers are in-sample by construction;
- `validation.txt` — the tuning partition; held out of development,
  but one round of infrastructure fixes was mined from its failure
  traces, which makes it partly in-sample;
- `test.txt` — the final evaluation partition; fully out-of-sample,
  never used for any iteration or tuning decision.

> **Naming caveat.** All three partitions are drawn from the miniF2F
> **`valid`** split described above — none of them come from
> `miniF2F/test/`. "train" / "validation" / "test" describe how *we*
> use each partition and are unrelated to miniF2F's own directory
> names. In particular, `benchmarks/test.txt` ⊄ `miniF2F/test/`.

Both baselines run on every partition with one seed, few-shot examples
enabled (see Demonstrations below); the agentic side budgets
`num_requests=32` per problem (one pool for tool calls and proposals,
depth unbounded), the standard side keeps `max_feedback_cycles=3`.
Per-problem dollar caps are deliberately non-binding safety nets:
the request/cycle budget is the controlled variable. Verification is
automation-assisted on the agentic side and plain on the standard
side — a deliberate, documented design choice (the battery is part
of the agentic *system*).

**Models.** Train doubles as a cost/performance frontier over the
gpt-5.6 family (sol / terra / luna; exact pricing in
`model_registry.py`). Validation and test run only the canonical
model, **`gpt-5.6-terra`**, picked by the documented rule (most
agentic successes per dollar on train, ties to the cheaper tier — see
`experiments/frontier_report.py`). Model selection is a tuning
decision, so it is made on train and never on test. One experimental
condition to
know: gpt-5.6 rejects function tools with reasoning on the Chat
Completions API, so all *agentic* requests run with
`reasoning_effort="none"` while standard requests keep the server
default — an API constraint, not a choice (see `model_registry.py`).

Train frontier (20 problems, one seed):

| model | standard | agentic "rich" | agentic spend | agentic $/solve |
|---|---:|---:|---:|---:|
| gpt-5.6-sol | 18 / 20 | 19 / 20 | $1.55 | $0.081 |
| **gpt-5.6-terra** | 10 / 20 | **20 / 20** | $1.13 | **$0.056** |
| gpt-5.6-luna | 8 / 20 | 15 / 20 | $1.89 | $0.126 |

Canonical results, `gpt-5.6-terra`:

| partition | standard | **agentic "rich"** | gap | spend (std / agentic) |
|---|---:|---:|---:|---|
| train (in-sample) | 10 / 20 | **20 / 20** | +10 | $0.86 / $1.13 |
| validation (partly in-sample) | 11 / 20 | **14 / 20** | +3 | $1.43 / $2.97 |
| **test (fully unseen)** | 5 / 20 | **14 / 20** | **+9** | $1.46 / $4.45 |

On every partition the agentic baseline solves a **strict superset**
of the standard baseline's wins. Train numbers are in-sample (the
baselines were iterated against it, under gpt-5.4) and validation is
partly so; **test is the headline result** — the only partition never
touched by any iteration or tuning decision. One seed per config —
run-to-run variance is roughly ±1–2 problems per cell.

Two figures above are easy to misread and worth stating plainly. The
often-quoted **$0.056 per solve is the train number**, where every
problem is solved; out of sample it is $0.318 per solve against the
standard baseline's $0.291. The agentic baseline buys **+9 solves at
roughly equal cost per solve**, not cheaper solves. And **80% of its
test spend goes to the six problems it never solves** — a failed search
costs up to 26× an average success, because context grows with every
turn.

### Cost reduction: binding budgets + the Responses API (2026-08-12)

Two changes, measured separately, both keeping the configuration and
prompts otherwise identical:

| configuration | test | spend | $/solve |
|---|---:|---:|---:|
| as published above | 14 / 20 | $3.56 | $0.254 |
| \+ `$0.30` per-problem dollar cap | 14 / 20 | $2.09 | $0.149 |
| \+ Responses API, `reasoning_effort="low"` | **16 / 20** | **$1.85** | **$0.116** |

**48% less spend and 54% less per solve, with no problem lost.**
All three rows are priced at *current* rates so they are comparable;
the first two runs were billed at the higher pre-2026-07-30 rates
($4.45 and $2.61 as billed). See the pricing note below.
Against the standard baseline the gap on test becomes 5 → 16: eleven
problems gained, none lost, p = 0.001.

- **The cap** is calibrated on train alone — $0.30 is the smallest round
  cap leaving train at 20/20 — and costs no solves on any partition. The
  same calibration rule applied to the *request* budget yields 32, i.e.
  no saving at all: late requests cost several times early ones, so a
  request count is a poor proxy for spend. `make budget-ablation`
  computes the curve from recorded prices; `make budget-replay`
  re-executes it through Delphyne with `cache_mode="replay"`, so the
  numbers are measured rather than projected and no API call is made.
- **The Responses API** matters here for one reason: gpt-5.6 rejects
  function tools on Chat Completions unless reasoning is off, so the
  agentic baseline had *never* been allowed to reason. With
  `effort="low"` it converges in 24% fewer turns and 51% fewer input
  tokens, and spends fewer output tokens than before despite half of
  them being reasoning. It is not that reasoning justifies its cost — it
  is cheaper outright. `make responses-report`.
- **Representing verifier feedback as a tool message does *not* help.**
  Prover feedback is a `user` message by default; real tool results are
  already `tool`-role. `convert_user_feedback_to_tool` rewrites each
  feedback turn into a synthetic tool call plus tool result, so a user
  turn cannot break the KV cache. Measured twice and it does not pay
  here. On the agentic loop the flag is *marginally better off*: terra
  gives 20/20 at $0.635 without it against 20/20 at $0.663 with it, and
  a two-seed luna re-test on the canonical configuration
  (`make sweep-luna-cvt`, 40 paired cells, $0.34) points the same way —
  40/40 solved either way, spend $0.157 off against $0.185 on, off
  cheaper on 26 of 40 cells (median cell ratio 0.742, two-sided
  p = 0.081). Consistent in direction across two models, but **not
  established**: the two luna seeds disagree about where the difference
  even comes from (seed 0 is 16 cheaper / 4 dearer yet only −4% pooled;
  seed 1 is 10 / 10 yet −25% pooled), which is the heavy tail talking
  again. Read it as "the flag is not earning its default", not as a
  measured saving. This loop's prefix cache is already 85–93%
  saturated, so there is little left for it to protect.

  On the standard loop a 4-arm factorial (478 configs) is
  noise in both directions: pooled spend moves −15% on luna and +15% on
  terra, but paired **per problem-seed cell** neither direction
  survives a sign test (luna 31 cheaper / 43 dearer, p = 0.20; terra
  20 / 16, p = 0.62), and the cached-input share is unchanged
  (81.4% → 81.5%). The pooled figures are artifacts of a heavy-tailed
  cost distribution, not an effect. Two caveats for anyone revisiting
  this: the conversion also injects a ~30-token instruction, so
  representation and prompt are confounded; and it is only available on
  the Responses API.

### Migrating to gpt-5.6-luna (2026-08-13)

Once reasoning was available, the cheap model tier became viable. On
validation, `gpt-5.6-luna` with the `core` toolset, `reasoning_effort=
"medium"` and a `$0.05` per-problem cap **matches terra's solve count
exactly at roughly a seventh of the cost**:

| test (clean) | solved | spend | $/solve |
|---|---:|---:|---:|
| standard baseline | 5 / 20 | $1.17 | $0.233 |
| agentic, chat, uncapped *(published)* | 14 / 20 | $3.56 | $0.254 |
| agentic, terra, `low`, $0.30 cap | 16 / 20 | $1.85 | $0.116 |
| **agentic, luna, `medium`, $0.05 cap** | **16 / 20** | **$0.29** | **$0.018** |

Paired per problem, luna and terra are **zero discordant on test** —
luna solves precisely the same sixteen problems and misses precisely the
same four. They are indistinguishable in what they can prove and differ
only in what they charge. Validation agrees: 16/20 on both seeds for
$0.23, against terra's 16/20 for $1.64.

Against the configuration published above that is **+2 problems and 92%
less money**; against the standard baseline, 5 → 16 problems for a
quarter of the spend. The whole luna study — a 240-config effort ×
toolset grid, two-seed validation and one test run — cost **$2.87**.

Three things this measurement settled that are worth carrying:

- **Reasoning is what makes the cheap tier work**, not the price cut.
  Luna without reasoning scores 12–13/20 on train and burns twice the
  turns; with it, 20/20.
- **Optimal reasoning effort is not transferable between model tiers.**
  Terra's optimum is `low` (`low → medium` there costs +22% for no extra
  solves); luna's is `medium` (36% cheaper than `low` at the same
  20/20). Reasoning buys turns, turns are what cost money, and a weaker
  model has more turns to save — so the optimum rises as the model gets
  cheaper. Sweeping every effort level is cheap and the answer does not
  port.
- **A dollar cap has to be re-derived per model.** Luna's is `$0.05`
  against terra's `$0.30`, by the identical rule. Reusing terra's would
  have left luna effectively uncapped.

`make sweep-luna-train` runs the full effort × toolset grid;
`make luna-cap` reads the cap off it. `make sweep-luna-cvt` re-asks the
feedback-as-tool-message question above on this configuration, and
`make cvt-report` pairs the two arms per problem-seed cell.

Honesty line: the +2 solves is **not** statistically confirmed (2
discordant problems, p = 0.50; see the note on sample size below). The
spend reduction is the solid claim; the solve count held or rose
everywhere.

**Prices are dated.** OpenAI cut gpt-5.6 prices on 2026-07-30 (luna
−80%, terra −20%) — in the middle of this project's run history, so a
single rate per model cannot describe it. `OMPHALOS_PRICING` holds a
rate *history* and `pricing_for(model, on=...)` resolves against it.
Two distinct questions get two distinct answers: `make reprice` says
what a run *did* cost (at the rate in force when it ran), while every
table and chart here says what it *does* cost (today's rate), because
comparing arms priced at different rates would fold a price change into
an engineering result.

**Sample size.** `make decision-audit` re-tests this project's
historical design decisions with paired per-problem sign tests. Two numbers from
it are worth carrying: identical configurations disagree on **1–3 of 20
problems**, and an exact sign test needs **6 discordant problems, all
one way**, to reach p < 0.05. A single 20-problem run therefore cannot
establish any change converting fewer than six problems. The
standard-vs-agentic gap clears that bar comfortably; most individual
design increments in this project's history do not.

Two frontier readings worth stating explicitly: the agentic scaffold
lifts the mid-tier terra *above* the flagship's plain-baseline
performance at a fraction of the cost, and the cheapest tier (luna)
is not the cheapest system — it spends the most agentic dollars on
train because failed searches burn the full request budget.

**"probing" toolset ablation** (`TryTactics`): the `"probing"`
toolset extends `"rich"` with `TryTactics(tactics, candidates)` — up
to 20 model-chosen candidate tactics evaluated against a held proof
state in one call, nothing committed (the native analog of a
stepwise-exploration primitive found valuable during development;
implemented purely on pytanque). Two evaluation rounds on the
validation and test partitions, two samples per problem
(`experiments/{validation,test}_probing_experiment.py`); v2 adds
calibration
(probing-only prompt discipline, a materialized TryTactics few-shot
workflow example gated by a toolset-aware example selector):

| sweep | "rich" (control) | probing v1 s0 / s1 | probing v2 s0 / s1 |
|---|---:|---:|---:|
| validation | 14 / 20 | 13 / 12 | 12* / 15 |
| test | 14 / 20 | 14 / 15 | — (aborted) |

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

Outputs land under
`experiments/output/{train,validation,test}_{standard,agentic}/` and
`experiments/output/{validation,test}_probing{,_v2}/`
(gitignored; regenerate with the
`experiments/{train,validation,test}_*_experiment.py` scripts — the
probing scripts now write to the `_v2` dirs; the v1 outputs are
frozen, their prompt predates the calibration). Earlier iterations —
including the final gpt-5.4 sweeps (9/18 train, 7/14 validation, 7/13
test, $7.93 across the six sweeps) — are archived locally under
`experiments/previous/`, whose directory names are deliberately left
at their historical `set{1,2,3}` / `holdout` spellings as a
provenance record (see `experiments/previous/README.txt` for the
mapping).

**A note on cost figures.** Delphyne's `price` metric is computed at
request time from the pricing the model was built with, and the stdlib
table infers an unknown model's rate from the longest matching name
prefix — which billed every archived gpt-5.4 run at `gpt-5` rates,
~1.75x too cheap. `model_registry.py` now refuses to price a
guarded-family name it does not know exactly, and `tools/reprice.py`
recomputes any run's cost offline from its recorded token counts.
Checked with it, **every gpt-5.6 figure on this page reproduces
exactly** (`python tools/reprice.py experiments/output` → zero
deltas); only the archived gpt-5.4 figures needed correcting.

### Demonstrations & few-shot examples

`demos/standard.demo.yaml` and `demos/agentic.demo.yaml` demonstrate
the **same two problems** — `algebra_binomnegdiscrineq_10alt28asqp1`
and `induction_sum_odd` — both chosen from **outside** all three
benchmark partitions (asserted at load time in
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
