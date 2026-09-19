# ACE thesis study — 2026-09-18

The [report](../../../docs/ace_thesis_report.md) gives the conclusions and
limitations. `protocol.json` predates paid requests. `seal.json` binds the
experiment implementation, statements, inputs, demonstrations and templates.
Do not edit sealed files in place. No default configuration is promoted.

Only trainX and validationX are permitted. testX, protected challenge data,
and mixed reports remain closed. ValidationX is reused development data.
This study has its own $50 ledger, independent of all previous campaigns.
Paid work finished at $10.42667544. Selected ACE reaches 51/80 validation
solves at $2.02439902, versus ordinary non-ACE 51/$1.53580888 and matched
non-ACE 49/$2.13028512. The new benchmark meets neither 10% target. Historical
panel-level savings of 14.07% and 10.55% remain separately documented.
`completion.json` records the final checks. The verified exports are in
`analysis/8a0e952bec9d71f5/`, including standalone PDF/PNG figures: all 462
completed jobs replay exactly without paid calls, and all 231 distinct
returned proofs compile independently. Both provider failures remain visible.

Both Claude Code and Codex use the same Python commands, from
`examples/omphalos/`. The executed sequence is:

```bash
python -m experiments.ace_thesis prepare
python -m experiments.ace_thesis prepare-artifacts
python -m experiments.ace_thesis seal
python -m experiments.ace_thesis round1
python -m experiments.ace_thesis adapt
# Inspect revisions, receipts and prerequisites; record round2_audit.json.
python -m experiments.ace_thesis round2
python -m experiments.ace_thesis freeze
python -m experiments.ace_thesis benchmark
```

These commands can dispatch paid requests for unfinished registered jobs.
Use the supervised launcher in tmux, with the existing environment setup.
The registered design is 72 development proof cells, up to 27 learning cells,
48 further development proof cells, and at most 320 validation cells. It
does not authorize additional arms, replications, or a new study after a null
result. Exact completed jobs and immutable artifacts are reused on restart.

Offline verification and reporting:

```bash
python -m experiments.ace_thesis verify
python -m experiments.ace_thesis replay
python -m tools.maintenance.ace_thesis_kernel
python -m tools.reports.ace_thesis_audit
python -m tools.reports.ace_thesis_retrospective
python -m tools.reports.ace_thesis
python -m tools.reports.ace_thesis_figures ANALYSIS_DIRECTORY
```

Run replay only after paid dispatch has stopped: it verifies that the billing
receipt count remains unchanged. Final kernel checking covers every distinct
returned proof and records `Print Assumptions`. It requires the installed Rocq
compiler and benchmark libraries. Report and figure exports preserve their
loaded source and input hashes. New reporting versions write new directories.
The `seed` labels are API replicates, not deterministic provider seeds.
The separately recorded compiler wrapper accepts theorem headers with local
binders; the original checker required a colon immediately after the name.
It preserves the original theorem declaration and every returned proof byte.

`operations/round1_incident.json` documents one provider-rejected request,
which remains an unsolved cell. The separately sealed
`tools/maintenance/ace_thesis_recovery.py` continued only the 44 collateral
administrative pauses, after exact offline checkpoint equality. Original
directories remain in `experiments/output/ace_thesis_20260918/interrupted_round1`;
canonical paths link to the completed continuations. No rejected request was
rewritten or retried. Both the original receipt and its zero-charge
reconciliation are preserved.

`operations/validation_incident.json` records a second provider rejection,
also retained in the denominator. The separately sealed
`tools/maintenance/ace_thesis_validation_recovery.py` applies the same
checkpoint protocol to 27 collateral pauses. Both harnesses use its
`prepare`, `checkpoints`, `reconcile`, `run run --max_workers=24 --wait`,
and `finalize` commands. The rejected request is never retried. Validation
originals remain under `interrupted_validation`; completed canonical paths
link to `resume_validation`. The final panel contains 319 completed jobs and
one provider failure, with no missing or administratively censored cells.

Large raw caches, transport snapshots, per-cell census records and SQLite
ledgers remain local experiment data. Reviewable exports, source hashes,
selected contexts and verification summaries accompany the code. Exact replay
requires those raw archives; the CSV exports alone cannot reproduce a model
conversation. Never mistake an export for a complete raw-data backup.
`kernel_sources.json` preserves the exact UTF-8 compilation units, including
inherited benchmark whitespace, in a compact source bundle. Writing each
`source` string under its `filename` reconstructs the checked `.v` file;
its SHA256 must match `sha256`. The individual `.v` files remain local.
`raw_archive_index.json` hashes all 464 logical cells and an index of the
5,908 transport snapshots. `audit/raw_archive_index.json` binds the larger
historical census. These distinguish reproducible local evidence from the
smaller staged review package without discarding failed attempts.

Scoped checks avoid aggregate targets that import closed partitions:

```bash
pytest -q tests/test_ace_thesis.py tests/test_thesis_reporting.py \
  tests/test_thesis_recovery.py tests/test_economy_recovery.py \
  tests/test_thesis_validation_recovery.py tests/test_thesis_kernel.py \
  tests/test_ace_sanitized.py tests/test_ace_sanitized_headroom.py \
  tests/test_ace_sanitized_report.py
make agents-check
```

The root `make pyright` check is also required; the report records its existing
unrelated `why3py.simple` dependency failures. Run Ruff and scoped Pyright on
changed Python files. No commits are created by this workflow.
