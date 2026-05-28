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
   LLM additionally has two *exploration* tools:
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

   The LLM has three actions in total (propose / `ReadSkill` /
   `SearchRocq`) and splits its request budget across them at its own
   discretion.

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

Per-config outputs land under `experiments/output/dev_standard/`.
The strategy and policy live in `prove_standard.py`; LLM prompts in
`prompts/ProposeProofScript.*.jinja`.

### Agentic baseline

```sh
make test-agentic           # single problem, with tool-call agency
make test-subset-agentic    # 20-problem sweep, agentic version
make replay-subset-agentic
make summary-agentic
```

Per-config outputs land under `experiments/output/dev_agentic/`.
The strategy, policy, and both `ReadSkill` / `SearchRocq` tools live in
`prove_agentic.py`; the introspection-query bridge to pytanque lives in
`pytanque_utils.py:query`. Prompts in
`prompts/ProposeProofScriptAgentic.*.jinja`.

The model still sees both the informal statement *and* the informal
proof sketch from each `.v` header — both baselines are therefore
*with-hints*. Further ablations (`TryTactic` non-destructive tactic
preview, two-stage informal/formal Hilbert split, MathComp retrieval)
are on the thesis roadmap (see `bachelor_arbeit_plan.md`).

Both baselines have a scaffolded full-sweep entry point
(`experiments/full_standard_experiment.py`, `full_agentic_experiment.py`),
ready for scaling beyond the dev subset.

## Checkpoint — dev subset (20 problems, 1 seed)

Snapshot of the current canonical state. Standard baseline outputs in
`experiments/output/dev_standard/`, agentic baseline outputs in
`experiments/output/dev_agentic/`. Both runs use seed 0, model
`gpt-5.4-2026-03-05`, `max_feedback_cycles=6`, and the agentic side has
`num_requests=16` (the standard side does not budget requests
separately).

### Headline

| | standard | **agentic** | Δ |
|---|---:|---:|---|
| pass rate | 6 / 20 (30%) | **9 / 20 (45%)** | +3 / +15pp |
| spend | $0.199 | $0.285 | +$0.087 / +44% |

Per-category split:

| category | n | std | agentic |
|---|---:|---:|---:|
| `algebra` | 6 | 2/6 | **3/6** |
| `mathd/algebra` | 1 | 1/1 | 1/1 |
| `numbertheory` | 3 | 1/3 | **2/3** |
| `mathd/numbertheory` | 2 | 2/2 | 2/2 |
| `induction` | 5 | 0/5 | 0/5 |
| `imo` | 2 | 0/2 | 0/2 |
| `amc` | 1 | 0/1 | **1/1** |

Net of the four agentic wins (`algebra_sqineq_2at2pclta2c2p41pc`,
`algebra_2varlineareq_xpeeq7_2xpeeq3_eeq11_xeqn4`,
`numbertheory_sqmod3in01d`, `amc12_2001_p2`) and the one loss
(`algebra_sqineq_4bap1lt4bsqpap1sq` — passes in standard, the
agentic loop spends its tool budget without converging in this seed),
the gain is +3. `induction` and `imo` are uniformly hard for both
baselines on this subset.

### Tool usage (extracted from the cached `dev_agentic` traces)

`ReadSkill` is the dominant tool — 24 calls across 20 problems
(1.2 per problem on average). `SearchRocq` is selective — 11 calls
across 8 problems.

**Which whitelisted skills actually get read?**
`tactic-patterns` and `proof-templates` account for the overwhelming
majority of `ReadSkill` calls; `compiler-guided-repair` shows up on
the structural-failure traces (per the prompt's
post-failure-escalation rule). The other seven whitelisted skills
(`rocq-phrasebook`, `tactics-reference`, `compilation-errors`,
`coq-stdlib-guide`, `admitted-filling`, `proof-golfing-patterns`,
`axiom-elimination`) saw zero or near-zero reads — the pack is
prunable.

**SearchRocq cohort (correlational, not causal):**

| cohort | win rate |
|---|---|
| problems where `SearchRocq` fired (≥1 call) | **1 / 8** (12%) |
| problems where it did not fire | **8 / 12** (67%) |

Read carefully: this **is not** "SearchRocq caused 7 problems to
fail." The agent only calls `SearchRocq` after a proposal has
failed — so the SR-yes cohort is, by construction, the harder
problems. The right reading is "SearchRocq is currently a marker of
stuckness, with one important exception."

That exception is `numbertheory_sqmod3in01d`: the agent calls
`SearchRocq` for a stdlib modulus lemma, gets `Z.mod_pos_bound`
back, and uses it to close the proof. This is exactly the
"unknown-identifier bottleneck" scenario the tool was built for —
the standard baseline misses this problem entirely. SearchRocq's
value is therefore **category-conditional**: real for lemma-discovery
bottlenecks (numbertheory), neutral-to-negative for tactic-structure
bottlenecks (algebra, induction, imo).

### How agentic is the agent, really?

The agent has three actions: `propose` (final answer in a fenced code
block), `ReadSkill(name)` (load curated markdown into chat history),
`SearchRocq(command)` (run Rocq introspection via pytanque).

| Turn / Decision | Constrained by the prompt? | Real choice? |
|---|---|---|
| First action | Yes — mandatory `ReadSkill` | No (action type fixed) |
| Which skill on first turn | No | Yes — 10-entry whitelist, 4-entry heuristic |
| After a failed proposal | No | Yes — retry / new skill / SearchRocq |
| When to give up | Implicitly via `max_feedback_cycles=6` | Bounded, not chosen |
| Probe proof state | Not available | No (no `TryTactic` yet) |

Honest characterization: the agent is **partially agentic**. More than
a single-shot LLM (three actions, real budget allocation across them,
feedback-driven revision, conditional skill loading), but the agency
is bounded by:

- a mandatory first action — the prompt forces `ReadSkill`,
- prompt-encoded triggers — post-failure `SearchRocq` only on
  unknown-identifier errors, `compiler-guided-repair` only on
  syntax/unification failures,
- no introspection on the proof state — the agent cannot try a tactic
  and observe the resulting goal.

A genuinely agentic comparison point — a ReAct-style loop where the
agent freely interleaves goal-state inspection, lemma search, and
tactic application without prompt-prescribed triggers — would be the
next escalation. Today's agent is the "skilled apprentice" tier:
knows when to look things up, doesn't yet drive the proof assistant.

### What this checkpoint does and doesn't measure

- **Does measure**: pass-rate gap (6 vs 9) on this specific subset;
  which whitelisted skills are actually load-bearing (a small subset
  of the 10); category-conditional value of `SearchRocq`; the
  proportion of agency that is genuinely chosen vs. prompt-forced.
- **Does not measure**: causal contribution of `SearchRocq` (a true
  ablation would isolate that — deferred); variance under a different
  seed (the 7→6 / 11→9 shift between successive runs is within seed
  noise on a 20-problem subset); generalization to the full miniF2F
  valid split.

Next-step candidates on the roadmap:
1. `TryTactic` non-destructive tactic preview — addresses the
   tactic-syntax bottleneck that's killing most of the remaining
   failures (next session).
2. Multi-seed runs to tighten the variance interval around the
   6-vs-9 gap.
3. Full miniF2F valid sweep (244 problems) once the dev result
   stabilizes.

### Demonstrations

End-to-end behaviour for both baselines is exercised by demo files
under `demos/` (registered in `delphyne.yaml`):

- `demos/standard.demo.yaml` — replays the cached standard-baseline
  trace (`commands/cache/prove_one_standard.exec.yaml`) on
  `algebra_sqineq_4bap1lt4bsqpap1sq`. The standard baseline does not
  solve that problem in 4 turns, so the demo uses `tests: - run`
  (no success assertion) — its purpose is to document the
  propose-verify-feedback loop, not the outcome.
- `demos/agentic.demo.yaml` — replays the cached agentic trace
  (`commands/cache/prove_one_agentic.exec.yaml`) on the same problem,
  which the agentic strategy *does* solve in 5 turns using both
  `ReadSkill` and `SearchRocq`. `tests: - run | success` enforces
  the successful outcome. Open the source `.exec.yaml` to see the
  concrete tool-call / tool-result YAML shape that the strategy
  produces at runtime.

## Provenance

- Upstream GitHub: <https://github.com/LLM4Rocq/miniF2F-rocq>
- Upstream snapshot used for this layout:
  `d9480b5e4711a4a8e8334dad3ef2e72c2ec0efdd`
- Upstream dataset: <https://huggingface.co/datasets/LLM4Rocq/miniF2F-rocq>
- Upstream paper:
  [MiniF2F in Rocq: Automatic Translation Between Proof Assistants](https://arxiv.org/abs/2503.04763)
- Upstream license: MIT.
