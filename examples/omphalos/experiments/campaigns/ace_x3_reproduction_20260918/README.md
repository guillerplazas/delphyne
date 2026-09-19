# X3 reproduction investigation — 2026-09-18

This is a new, fixed experiment and a versioned correction to the earlier
thesis accounting. It does not rewrite any old measurement or sealed source.
Only validationX is used; testX and protected challenge data remain closed.

Completed: 320/320 attempts, 320 exact offline replays, 192 successful cells
and 151 distinct freshly compiled proofs. Corrected spend $8.00405126;
corrected cumulative thesis spend $19.70941565. X3 saves 4.78% at 32768
(50/80 versus 46/80), and costs 0.94% more at 8192 (45/80 versus 51/80).
Neither registered 10% target passes. Full interpretation:
[study report](../../../docs/ace_x3_reproduction_study.md).

Both Claude Code and Codex use the same commands from `examples/omphalos`:

```bash
source ~/.config/omphalos/env.sh
python -m experiments.ace_x3_reproduction audit
python -m experiments.ace_x3_reproduction retrieve
python -m experiments.ace_x3_reproduction prepare
python -c 'from experiments.ace_x3_reproduction.verification import preflight; preflight()'
python -m experiments.ace_x3_reproduction run
python -m experiments.ace_x3_reproduction verify
python -m experiments.ace_x3_reproduction report
```

`run` uses the supervised Omphalos launcher: 24 workers, 32 stream slots,
one attempt per registered configuration. Long runs belong in tmux. The
manifest fixes 320 cells: empty/X3 × 8192/32768 × 40 theorems × 2 replicates.
Arm order rotates by theorem and reverses in the second replicate. Replicate
labels do not set a provider sampling seed. No training or artifact selection.

Additional authorization is $20 within the original thesis $50 ceiling:
$18 matrix and $2 infrastructure reserve. The prior study reconstructs to
$11.70536439 including cache writes. `ledger.sqlite3` reserves corrected
tariff liability atomically before every HTTP call. Unknown usage/tier or
network billing pauses dispatch; no automatic retry replaces a bad outcome.
Do not remove a pause or restart an interrupted attempt without an exact,
separately recorded checkpoint continuation. Administrative censoring means
the full experiment has no verdict. Unused money is not extra-run authority.

The proof controller deliberately retains its historical three-category
cost and $0.10 admission rule. The ledger and report use the four-category
tariff. These two quantities have different purposes. Report both raw proof
success and success costing at most $0.10 under the corrected tariff.
Published tariff reconstruction is not invoice verification.

Provider caching remains enabled, with no artificial warmup and fresh local
request caches. Diagnostic comparisons use only the previous completed
response ID, without changing the model's input. `responses/` retains the
original create payload/response, and `transport/` retains exact reasoning
state for replay. Original archive GETs live in `retrieved/`; they omit the
historical encrypted reasoning payload. Do not fabricate those bytes.

Additional read-only investigations can be rerun explicitly:

```bash
python -c 'from experiments.ace_x3_reproduction.history import census; census()'
python -c 'from experiments.ace_x3_reproduction.history import validate_provider_outputs; validate_provider_outputs()'
python -c 'from experiments.ace_x3_reproduction.history import replay_history; replay_history()'
python -c 'from experiments.ace_x3_reproduction.diagnostics import historical_diagnostics; historical_diagnostics()'
python -c 'from experiments.ace_x3_reproduction.audit import other_retrospectives; other_retrospectives()'
python -c 'from experiments.ace_x3_reproduction import campaign as c; from experiments.ace_x3_reproduction.diagnostics import input_stability; c.save("audit/input_stability_v2.json", input_stability(c.read("audit/cells.json")))'
```

Review `audit/accounting.json`, `audit/corrected_comparisons.json`,
`audit/x3_census_v2.json`, `audit/provider_output_validation.json`,
`audit/historical_replay_v2.json`, `audit/historical_kernel.json`, and the
40 exercise dossiers. Earlier draft checks compared omitted YAML defaults
literally or retained per-cell snapshot paths as configuration differences;
the typed/v2 checks supersede those drafts. Source history is in
`audit/source_history_verified.json`: the old budget transport is recovered
exactly; no exact historical `prove_grounded.py` blob was found among its
seven path revisions. Candidate source diffs are not claimed as exact copies.
The `input_stability_v2.json` audit adds actual reasoning-cache lookups and
excludes demonstration misses. Both `admission_tails_v2.json` files normalize
typed defaults to link every admitted tail; their first versions retained
correct affected-cell counts but could not link the raw YAML request hashes.

Fresh `analysis/results.json` contains primary effects, paired uncertainty,
replicates and the cap interaction. `gap_accounting.json` and
`gap_by_theorem.csv` independently decompose the historical dollar gap.
`secondary_metrics.json` explicitly separates cost-per-solve from total spend.
`termination.json` distinguishes monetary/verifier admission stops from proof
errors. Forty Markdown and compressed JSON dossiers cover all 760 compared
historical/previous/new attempts, including every unsuccessful attempt.

`seal.json` fixes paid code, artifact, statements, demonstrations, protocol,
runtime and manifest before execution. Analysis modules evolve separately;
the final review manifest binds their delivered versions and outputs. Large
original caches, response bodies, SQLite ledger and replay snapshots remain
local; integrity hashes do not replace a backup. Keep this campaign directory
and `experiments/output/ace_x3_reproduction_20260918` together for replay.
Compressed JSON exports preserve exact original bytes. The review manifest
binds delivered source and evidence; the raw archive manifest binds local
request caches, receipts, provider responses and transport snapshots.
After verification, reporting and recording `quality.json`, either harness
can reproduce the compact bundle with
`python -m experiments.ace_x3_reproduction.review`. JSON/CSV files larger
than 250 KB are delivered as `.gz`; raw originals remain local. Full replay
requires the raw archive; the compact bundle is a review export, not a
self-contained substitute for that archive.

Run the scoped suite instead of broad targets that can open closed data:

```bash
pytest -q tests/test_x3_reproduction.py
ruff check experiments/ace_x3_reproduction tests/test_x3_reproduction.py
pyright experiments/ace_x3_reproduction tests/test_x3_reproduction.py
make agents-check
```

No default promotion and no automatic thesis claim follow from a successful
test suite. Scientific conclusions require the complete paired matrix,
independent kernel checks, receipt reconciliation and uncertainty estimates.
