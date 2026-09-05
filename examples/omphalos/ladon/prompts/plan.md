# Ladon planning session — night $date

You select which `HINTS.md` entries the Ladon loop attempts tonight,
and how. Tonight's budget: at most $max_hints hints, $wallclock_h h of
wall-clock, $$$cap_usd of OpenAI spend. One ladonX arm costs about
$$1.7 and 2.5 h (screen tier 40 cells ≈ 1 h, select tier +40 cells
≈ 1 h, plus the sessions); an offline analysis costs nothing.

## Classes

- **A — offline analysis**: answerable from archived cells and caches
  with the existing tools (`tools/ace_cap_report.py`,
  `tools/budget_ablation.py`, `tools/replay_with_budget.py`,
  `tools/failure_analysis.py`). Zero spend; the outcome is always an
  artifact plus a recommendation (INSPECT).
- **B — knob**: an existing config field, flag, constant or template
  switch reachable by subclassing `ladon.bench.LadonConfig` in the arm
  script (precedent: `experiments/x_goalcap_experiment.py` flips
  `goal_caps`). About 60 turns of a Sonnet session.
- **C — design**: new policy or search logic, a new tool, a new prompt
  block behind a version field, verifier changes. About 120 turns of
  an Opus session. Only when the hint is concrete enough to implement
  in one session and test with one arm.
- **D — structural / with human**: stdlib (`src/delphyne`) changes,
  API migrations, anything touching frozen paths (partitions, the
  statistics and pricing tools, baseline scripts, vendored trees),
  multi-day builds, anything needing a new baseline, anything about
  frontier/terra arms or the original 20-problem partitions. Never
  attempted; reported to Guille.

## Priorities

- Budget reduction beats raw performance: prefer hints whose effect
  would show on the cost secondary, or on solves at luna's cost class.
- The file is newest-first and newer hints carry more nuance, but do
  not skip an older hint that is cheap and decisive.
- Skip hints the ledger below already records, unless the ledger says
  INSPECT and you have a genuinely different angle — and even then
  prefer an untried hint.
- `[upstream]` and `[process]` hints are D or skipped. Hints that need
  a fresh partition or testX are D.
- Hints whose status line says `LADON HUMAN` were judged structural on
  an earlier night; they are listed so you can disagree. Rank one only
  with a concrete reason the earlier verdict missed; otherwise skip it
  without repeating the D reason.
- Independence: no two ranked hints may touch the same file; their
  commits must stand alone.
- Rank a few more than $max_hints so Ladon can skip one that turns out
  infeasible; execution order = your order. **Every ranked entry is a
  different hint** — one entry per hint number, never variants of the
  same hint; when the pool is smaller than that, rank fewer.

## Past Ladon verdicts (ledger, newest last)

$ledger

## Latest PROGRESS.md entry (context)

$progress_head

## Open hints (newest first)

$hints

## Output

Return JSON matching the schema. `ranked`: at most $max_ranked
entries, each with `hint` (number), `class` (A–C only), `expected_effect`
(solves | cost | both | analysis), `arm` (one paragraph: the exact
change and how the arm differs from the baseline), `knob` (class B:
the field/constant), `files` (paths you expect the session to touch,
relative to examples/omphalos), `risk` (low/medium/high),
`est_minutes` (the implement session only), `rationale` (why now, in
one or two sentences). `skipped`: every other open hint with a short
`why`; class D hints go here with `why` starting with `D:`.
