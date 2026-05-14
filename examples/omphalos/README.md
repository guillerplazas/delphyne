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
   LLM additionally has a `ReadSkill` tool. It chooses which skill
   markdown files under `rocq_skills_data/` to load on demand. The
   system prompt only lists *available* skills; their content arrives
   in chat history when (and if) the LLM requests it. The LLM now has
   two actions, and decides how to split its request budget across
   reading skills and proposing proofs.

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

Per-config outputs land under `experiments/output/dev_standard_experiment_1/`.
The strategy and policy live in `prove_standard.py`; LLM prompts in
`prompts/ProposeProofScript.*.jinja`.

### Agentic baseline

```sh
make test-agentic           # single problem, with tool-call agency
make test-subset-agentic    # 8-problem sweep, agentic version
make replay-subset-agentic
make summary-agentic
```

Per-config outputs land under `experiments/output/dev_agentic_experiment/`.
The strategy and policy live in `prove_agentic.py`; the `ReadSkill` tool
is defined there. Prompts in `prompts/ProposeProofScriptAgentic.*.jinja`.

The model still sees both the informal statement *and* the informal
proof sketch from each `.v` header — both baselines are therefore
*with-hints*. Further ablations (`SearchRocq` / `TryTactic` tools,
two-stage informal/formal Hilbert split, MathComp retrieval) are on the
thesis roadmap (see `bachelor_arbeit_plan.md`).

Both baselines have a scaffolded full-sweep entry point
(`experiments/full_standard_experiment.py`, `full_agentic_experiment.py`),
ready for scaling beyond the dev subset.

## Provenance

- Upstream GitHub: <https://github.com/LLM4Rocq/miniF2F-rocq>
- Upstream snapshot used for this layout:
  `d9480b5e4711a4a8e8334dad3ef2e72c2ec0efdd`
- Upstream dataset: <https://huggingface.co/datasets/LLM4Rocq/miniF2F-rocq>
- Upstream paper:
  [MiniF2F in Rocq: Automatic Translation Between Proof Assistants](https://arxiv.org/abs/2503.04763)
- Upstream license: MIT.
