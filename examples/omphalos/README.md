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
   - **`TryTactic(tactics=...)`** non-destructively previews the
     effect of a tactic prefix on the theorem's initial proof state.
     Rocq proof state is functional, so `client.run(state, tac)`
     returns a fresh state and leaves the original valid.

   The tool repertoire is selected by the `toolset` strategy argument:
   `"full"` advertises all three tools; `"lean"` (the default and
   canonical configuration) drops `TryTactic` and relies on
   **partial proposals** instead — `check_proof` reports the
   verified prefix and the exact remaining goals whenever a script
   applies cleanly without closing the goal, so a proposal doubles as
   a preview (and wins outright if it happens to close the goal).
   The dev experiment runs both toolsets side by side.

   **Budget semantics.** Every assistant turn — tool round or
   proposal — costs one LLM request, and all turns draw from a single
   `num_requests` pool (the binding constraint; search depth is
   deliberately left unbounded by default via `max_turns=None`). The
   same number is surfaced to the model as `turn_budget` in the
   system prompt, and the model allocates it across exploration and
   proposals at its own discretion.

The two systems run on the same `dev_subset.txt`; comparing pass rates
problem-by-problem is the headline ablation this iteration produces.

Prerequisites:

- `rocq` available on your opam switch.
- Conda env `guille` activated (Delphyne + `pytanque` installed).
- An API key for the configured model (default: `gpt-5.4-2026-03-05`,
  overridable via `policy_args.model_name`).

### Standard baseline

```sh
make test-standard          # single problem, sanity check
make test-subset-standard   # 8-problem curated sweep (via dp.Experiment)
make replay-subset-standard # re-derive summary from cache (no LLM calls)
make summary-standard       # regenerate the aggregate results_summary.csv
```

Per-config outputs land under `experiments/output/dev_standard_v2/`
(`dev_standard/` is the archived pre-partial-proposal-feedback run).
The strategy and policy live in `prove_standard.py`; LLM prompts in
`prompts/ProposeProofScript.*.jinja`. Note that `check_proof` reports
an incomplete-but-valid script (all tactics applied, goals remain) as
"incomplete" feedback with the verified prefix and remaining goals, so
even the standard baseline can use partial proposals as previews.

### Agentic baseline

```sh
make test-agentic           # single problem, "full" toolset
make test-agentic-lean      # single problem, "lean" toolset
make test-trytactic         # single problem exercising TryTactic
make test-subset-agentic    # 40-config sweep (20 problems x 2 toolsets)
make replay-subset-agentic
make summary-agentic
make regen-command-caches   # refresh all single-problem caches (real LLM calls)
```

Per-config outputs land under `experiments/output/dev_agentic_toolsets/`
(the `toolset` column in `results_summary.csv` is the comparison axis).
The strategy, policy, and the `ReadSkill` / `SearchRocq` / `TryTactic`
tools all live in `prove_agentic.py`; the pytanque bridges
(`query`, `try_tactic`) live in `pytanque_utils.py`. Prompts in
`prompts/ProposeProofScriptAgentic.*.jinja`.

The model still sees both the informal statement *and* the informal
proof sketch from each `.v` header — both baselines are therefore
*with-hints*. Further ablations (two-stage informal/formal Hilbert
split, MathComp retrieval, multi-seed runs, full miniF2F sweep) are
on the thesis roadmap (see `bachelor_arbeit_plan.md`).

Both baselines have a scaffolded full-sweep entry point
(`experiments/full_standard_experiment.py`, `full_agentic_experiment.py`),
ready for scaling beyond the dev subset.

## Checkpoint — dev subset (20 problems, 1 seed)

Snapshot of the current canonical state, after the agentic-baseline
overhaul (decoupled turn budget, trust-the-model prompt, partial-
proposal feedback, configurable toolset). Outputs: standard baseline in
`experiments/output/dev_standard_v2/`, agentic toolset comparison in
`experiments/output/dev_agentic_toolsets/`. All runs use seed 0 and
model `gpt-5.4-2026-03-05`. The agentic side budgets `num_requests=16`
per problem (tool calls and proposals draw from that one pool; search
depth is unbounded); the standard side keeps `max_feedback_cycles=3`.

What changed relative to the previous checkpoint (archived in
`experiments/output/dev_standard/` and `dev_agentic*/`):

1. **The depth cap is gone.** Previously `dfs(max_depth=7)` silently
   capped *total* assistant turns — tool rounds and proposals
   combined — so the nominal 16-request budget was unreachable and
   every exploration call cannibalized a proposal attempt (archived
   runs all die at exactly 7 requests). Now `num_requests` binds.
2. **Trust-the-model prompt.** The mandatory first `ReadSkill`, the
   per-tool hard caps, and the trigger/anti-trigger lists are gone;
   the model is told its turn budget and decides freely.
3. **Partial proposals are first-class.** `check_proof` distinguishes
   "a tactic failed" from "all tactics applied, goals remain": the
   latter now produces `incomplete` feedback showing the verified
   prefix + remaining goals. A proposal therefore doubles as a state
   probe. Both baselines share this.
4. **Toolset is a config switch.** `"full"` = ReadSkill + SearchRocq +
   TryTactic; `"lean"` = no TryTactic (partial proposals cover
   structural exploration). Both ran on the full dev subset.

### Headline

| | standard (v2) | **agentic "lean"** | agentic "full" |
|---|---:|---:|---:|
| pass rate | 6 / 20 (30%) | **8 / 20 (40%)** | 8 / 20 (40%) |
| spend | $0.173 | **$0.450** | $0.678 |

Both toolsets beat the standard baseline by +2 problems (+33%
relative). They tie on pass rate, and `"lean"` does it at two thirds
of the cost — so **`"lean"` is the canonical agentic baseline** (the
default `toolset` of `prove_theorem_agentic`). For context, archived
single-seed checkpoints of the pre-overhaul agent scored 9/20 (3-tool)
and 7/20 (4-tool); the ±1–2 spread between successive 20-problem runs
is within seed noise, so treat all headline gaps of that size with
caution until the multi-seed runs land.

Per-category split:

| category | n | std (v2) | agentic lean | agentic full |
|---|---:|---:|---:|---:|
| `algebra` | 6 | 1/6 | **4/6** | 3/6 |
| `mathd/algebra` | 1 | 1/1 | 1/1 | 1/1 |
| `numbertheory` | 3 | 1/3 | 2/3 | 2/3 |
| `mathd/numbertheory` | 2 | 2/2 | 1/2 | 2/2 |
| `induction` | 5 | 0/5 | 0/5 | 0/5 |
| `imo` | 2 | 0/2 | 0/2 | 0/2 |
| `amc` | 1 | 1/1 | 0/1 | 0/1 |

The agentic gain is concentrated where the previous checkpoint lost
ground: `algebra` (1/6 standard → 4/6 lean). `induction` and `imo`
remain uniformly unsolved — the bottleneck there is closing the
post-induction goals, not budget or exploration. Notably the union of
the two toolsets is 10/20: `full` uniquely wins
`algebra_2varlineareq_xpeeq7_2xpeeq3_eeq11_xeqn4` and
`mathd_numbertheory_102`, `lean` uniquely wins
`algebra_sqineq_2at2pclta2c2p41pc` and
`algebra_sqineq_36azm9asqle36zsq` — single-seed noise dominates the
full-vs-lean comparison, while the cost gap is systematic.

### Tool usage (true call counts from the cached toolset sweep)

| tool | "full" runs | "lean" runs |
|---|---|---|
| `ReadSkill` | 1 call (1/20 problems) | 0 calls |
| `SearchRocq` | 41 calls (10/20 problems) | 49 calls (8/20 problems) |
| `TryTactic` | 60 calls (12/20 problems) | — (not advertised) |

Two findings:

- **The skill pack is dead weight for this model.** Under the old
  prompt `ReadSkill` fired 20/20 times — because the prompt mandated
  it. With the mandate removed, the model read a skill exactly once
  across 40 runs. It strongly prefers asking Rocq itself
  (`SearchRocq`) and probing goal states (`TryTactic` / partial
  proposals) over reading curated prose. The whitelist was already
  pruned to 7 entries; further investment in skill content is hard to
  justify for this model class.
- **TryTactic still does not pay for itself.** 60 preview calls
  bought zero net wins over `"lean"` and +50% spend. With partial
  proposals returning the same information *and* counting as real
  attempts, a separate preview tool is structurally redundant —
  which is exactly why `"lean"` is the canonical configuration.

### How agentic is the agent now?

The previous checkpoint's honest answer was "mostly agentic": the
first action was prompt-forced, tool triggers were prompt-encoded, and
hard caps bounded each tool. All of that is gone. The model receives
its turn budget, one shared request pool, and per-tool "when it pays
off" guidance — every action choice, including whether to touch the
skill pack at all, is its own. The observed behaviour shift (ReadSkill
20/20 → 1/40) is direct evidence the previous numbers measured prompt
compliance rather than model preference.

Remaining boundedness: a single `dp.interact` loop (no `Branch`
fan-out across candidate proof prefixes). That is the next escalation:
fan out over several openers, score the resulting goal states, and
develop the most promising subtree under `bestfs` — the point where
Delphyne's multi-success search machinery starts paying off beyond
what a linear conversation can express.

### What this checkpoint does and doesn't measure

- **Does measure**: pass-rate gap under matched verification
  semantics (both baselines share the new `check_proof`); the
  full-vs-lean toolset ablation at matched budgets; true tool-call
  frequencies under a non-coercive prompt.
- **Does not measure**: variance (single seed; the dev-subset
  granularity is 5pp per problem); generalization to the full miniF2F
  valid split; the causal value of `SearchRocq` (it fires on the
  harder problems by construction, so cohort win rates are
  confounded).

Next-step candidates on the roadmap:

1. Multi-seed dev runs to put error bars on the 6 / 8 / 8 spread.
2. `Branch` fan-out over candidate openers + `bestfs` policy.
3. Full miniF2F valid sweep (244 problems) via
   `experiments/full_agentic_experiment.py` (already wired for the
   `"lean"` toolset).
4. Budget-scaling curve (`num_requests` ∈ {8, 16, 32}) now that the
   budget actually binds.

### Demonstrations

End-to-end behaviour is exercised by demo entries under
`demos/agentic.demo.yaml` and `demos/standard.demo.yaml` (registered
in `delphyne.yaml`). They replay cached single-problem command files
(refreshed via `make regen-command-caches`):

- `agentic_dev_smoke` — `"full"` toolset on
  `algebra_sqineq_4bap1lt4bsqpap1sq`; solves it in 3 requests and
  asserts `run | success`.
- `agentic_lean_dev_smoke` — `"lean"` toolset on the same problem;
  solves it in 6 requests and asserts `run | success`.
- `agentic_trytactic_dev_smoke` — `"full"` toolset on the induction
  problem `induction_seq_mul2pnp1`; documents a full 16-request
  budget exhaustion (induction remains 0/5), shape only.
- `standard_dev_smoke` — standard baseline on the same algebra
  problem; exhausts its 4-request budget, shape only.

Open the source `.exec.yaml` files to see the concrete tool-call /
tool-result YAML shapes that the strategy produces at runtime.

## Provenance

- Upstream GitHub: <https://github.com/LLM4Rocq/miniF2F-rocq>
- Upstream snapshot used for this layout:
  `d9480b5e4711a4a8e8334dad3ef2e72c2ec0efdd`
- Upstream dataset: <https://huggingface.co/datasets/LLM4Rocq/miniF2F-rocq>
- Upstream paper:
  [MiniF2F in Rocq: Automatic Translation Between Proof Assistants](https://arxiv.org/abs/2503.04763)
- Upstream license: MIT.
