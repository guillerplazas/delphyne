# Session dropping and compact prompting

This follow-up tests each refinement independently, then their combination,
for ACE and the same non-ACE agent. Reset adds no tool, summary, handoff or
retrieval/failure memory. Existing baseline tools and verified proof state
are unchanged. Neither agent is required to use reset in the final cost/
coverage comparison. The frozen v2 playbook is unchanged.

Authorization: $20 additional inference within the original cumulative $50.
The three earlier campaigns settled at $13.98159180. trainX is authorized
for refinement pilots; validationX is the final development benchmark.
testX and challenge data, including metadata and mixed artifacts, remain
closed. Code quality is checked separately from cost/coverage outcomes.

## Frozen design

- 24 pilot cells: four fixed trainX problems, ACE/non-ACE, baseline/drop/
  compact, seed 0. $3 pilot allocation; $2.40 nominal pilot liability.
- Up to 640 fresh validation cells: 40 problems, two seeds, eight factorial
  configurations. The 20 blocks each contain two problems and every setting
  and seed, in deterministic randomized order. Before each block, its full
  $3.20 nominal liability must fit. Unused pilot allocation transfers to the
  benchmark. A spending ceiling is not a target; incomplete dispatch is
  reported explicitly if the next block does not fit.
- Identical Luna medium Responses, core tools, $.10/problem, 64 requests,
  300 verifier seconds, 32768 output tokens, one supervised attempt.
- Drop after eight new interaction groups and 24000 visible characters,
  only if at least 8192 characters are removed. Retain the last two complete
  interactions and latest checked proposal; clear opaque reasoning. At
  most two drops. Complete theorem and verified prefix remain available.
- Compact system prose and feedback independently. Tool schemas, skills
  index, demonstrations, playbook text, tool execution and proof checking
  remain fixed. Views are capped at 4096 UTF-8 bytes; errors and goals come
  before repeated proof prefixes. Goal aliases require a complete earlier
  definition in the current visible history; after a drop they re-expand.
- The combined treatment applies the reset threshold to compacted history.

Outcomes: all-attempt cost, qualified proofs and cost/proof, with paired
family-clustered 90% intervals and two-sided p<.10 for statistical support.
Ten percent cost reduction is a practical target, not a p-value or per-seed
coverage gate. Report independent effects, interaction and each agent's
cost/coverage frontier. No default promotion or independent held-out claim.

## Reproduction (both agent harnesses)

From `examples/omphalos`, load `~/.config/omphalos/env.sh` for paid work.
Long stages use tmux and the shared supervised launcher, 24 workers/32 slots.

```sh
python -m experiments.ace_economy_refinement_experiment prepare
python -m experiments.ace_economy_refinement_experiment pilot
python -m experiments.economy_refinement.evidence replay pilot
# Inspect pilot outputs and save pilot_review.json before the freeze.
python -m experiments.ace_economy_refinement_experiment freeze
python -m experiments.ace_economy_refinement_experiment benchmark
python -m experiments.economy_refinement.evidence replay final00
# Repeat replay for each completed final block, then export all receipts.
python -m experiments.economy_refinement.evidence export
```

`protocol.json`, manifests and `seal.json` freeze the runtime before any
paid call. `freeze.json` records the pilot decision before validation.
Old sources remain unchanged and their safe validation-only seals still
verify. Analysis code is separate from the runtime seal. Raw request
snapshots and caches stay local; exports bind them with SHA-256 hashes.
Replay blocks HTTP and compares proof values, success and every budget.

The initial 400-cell context audit uses first/last requests ordered by
transport events, never lexicographic snapshot filenames. Its exact source
is preserved in `sources/failure_audit.py.txt`, matching the source hash in
`failure_audit.json`. Those counts describe visible-history mechanisms, not
total billing or a judgment that every repeated lookup was unnecessary.

## Implementation validation

30 scoped tests pass, including exact replay of both paid baseline agents
with both new switches off. Changed code passes Ruff and pinned Pyright
1.1.406; agent instruction symlinks pass `make agents-check`. Root
`PYRIGHT_PYTHON_FORCE_VERSION=1.1.406 make pyright` retains 17 pre-existing
errors from the unavailable `why3py.simple` dependency outside Omphalos.
Global tests, partition checks and global repricing are excluded because
they access closed partitions.
