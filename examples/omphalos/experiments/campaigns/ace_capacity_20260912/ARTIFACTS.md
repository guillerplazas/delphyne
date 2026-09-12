# Capacity follow-up artifacts and reproduction

Start with [RESULTS.md](RESULTS.md), the [proof-case appendix](CASE_APPENDIX.md),
the [matched creator appendix](CREATOR_APPENDIX.md), and the standalone
[PDF](capacity_comparison.pdf)/[PNG](capacity_comparison.png) figure.

All paths below are relative to `examples/omphalos`, unless they name files
in this campaign directory. The entry points work from both Codex and Claude
Code. No harness-specific service is needed for analysis or cached replay.

## Authoritative numerical records

| Artifact | Purpose |
|---|---|
| `protocol.json`, `runtime.json`, `seal.json` | Registered design, execution profile, 762 sealed files |
| `planned_cross.json`, `references.json` | 64 new crossover jobs and 176 explicit compatible references |
| `planned_creation.json` | 200 role jobs on 100 exact frozen inputs |
| `planned_mechanisms.json` | 80 profiles on the fixed eight-case training panel |
| `batches/*.json`, `carried/*.json` | Actual batch manifests/completion checkpoints and carried paths |
| `crossover_report.json` | Full 40-case group metrics, paired uncertainty and primary interaction |
| `crossover_diagnostics.json` | Every crossover observation, model reply and verifier checkpoint |
| `mechanism_report_v2.json` | A–E results and C/E continuations, costs, uncertainty and interactions |
| `mechanism_diagnostics_v2.json` | Full diagnostic/continuation traces and admission metadata |
| `failure_profiles_v2.json` | Per-path error categories, terminal resource cause and remaining allowance |
| `causal_exposure_audit.json` | Identical initial requests, reply differences and actual treatment exposure |
| `feedback_exposure_v2.json` | Exact unfocused goal views, including replayed/carried occurrences |
| `pricing_sensitivity.json` | Actual/uncached/Luna-rate totals and post-hoc cost qualifications |
| `prefix_cost_conservation.json` | Cumulative cache tokens equal the sum of newly paid path segments |
| `creation_audit.json`, `creator_quality.json` | Every creator output, structural checks and availability candidates |
| `creator_reference_checks.json` | Source-context checks; availability does not establish applicability |
| `creator_batch_reference_checks.json`, `creator_contextual_audit.json` | Resolve reducer references in other members of the source batch; retain warnings |
| `creator_terminal_evidence.json`, `reflector_terminal_witness.json` | Verified ending versus submitted ending; explicit `nia`/`norm_num` source check |
| `snippet_witness.json`, `snippet_verification.json` | Original Terra snippet's source-bound failure and valid replacement |
| `fresh_reducer_snippet_check.json`, `reduction_protection.json` | Fresh Terra reducer defect and actual delta protection before merging |
| `fixed_book.json`, `terra_playbook_source_verified.yaml` | Exact one-example replacement and book hashes |
| `final_accounting.json`, `receipts.csv` | New spend, combined liability, and all 2,722 follow-up receipts |
| `verification.json`, `raw_inventory.json`, `artifact_inventory.json` | Checks, raw-file/transport hashes and reviewable-artifact hashes |

`mechanism_report.json`, `mechanism_diagnostics.json`, `failure_profiles.json`
and `feedback_exposure.json` preserve the first derived versions. Use the
`_v2` files. `analysis_correction_01.json` records the single failed-cell
verifier-time omission: Compute timing was absent from its response cache
but present in the terminal observer. The corrected value is 3.4958176855
seconds. Costs, outcomes, comparisons and raw records did not change.

## Raw local storage

Paid output root: `experiments/output/ace_capacity_20260912/`, with
`cross`, `creation`, `mechanisms`, `headroom1` and `headroom2` groups.
There are 373 distinct execution directories: 372 complete, one failed.
The failure directory retains its exception and partial cache. Every file
is listed by relative path, SHA-256 and byte count in `raw_inventory.json`.

Transport sidecars are under this campaign's `transport/` directory. They
contain compressed complete transport-state snapshots, request/response
bindings and reasoning-reference state. They are necessary for exact
continuation admission and cache replay. Preserve them with the raw output
directories. They remain local rather than being committed as large blobs.
`events.jsonl` and `replay_events/` retain the live and replayed event streams.
The small `replay_*.json` and `admission_parity_*.json` summaries are staged.

The ledger remains `experiments/campaigns/ace_attribution_20260912/ledger.sqlite3`:
both studies use the same $75 ceiling. `prior_ledger.sqlite3` is the local
snapshot taken before this follow-up; its 3,939 original receipts are
unchanged. Never run the prior runner's receipt export now: it would replace
that study's frozen CSV with combined receipts. This campaign's inventory
script exports only `capacity-*` receipts to its own CSV.

`prior_source/` contains 135 source snapshots (plain `.txt` suffix) preserving
the preceding implementation. `prior_source_manifest.json` records their
hashes and all original sealed dependencies. Prior books and measurements
remain where the explicit reference manifest names them. Restoring an old
source version must use a separate checkout or review copy; do not overwrite
the active implementation or paid measurements.

## Offline commands

Run from `examples/omphalos`, in the existing Python 3.12 environment:

```sh
PYTHONPATH=. python tools/reports/ace_capacity_replay.py cross
PYTHONPATH=. python tools/reports/ace_capacity_replay.py creation
PYTHONPATH=. python tools/reports/ace_capacity_replay.py mechanisms
PYTHONPATH=. python tools/reports/ace_capacity_replay.py headroom1
PYTHONPATH=. python tools/reports/ace_capacity_replay.py headroom2
PYTHONPATH=. python tools/reports/ace_capacity_replay.py audit
```

These commands disable HTTP and fresh Rocq execution. All 372 complete
records reproduce success and spent-budget fields. The failed record
restores its cached prefix and reaches the exact next dispatch boundary;
the missing rejected-response snapshot ends replay there. It does not
reissue or simulate acceptance of the remote request. The audit compares
all estimate, admission and terminal fields except process/time metadata.
All 373 sequences match. A missing sidecar, request divergence or changed
transport state fails closed.

```sh
PYTHONPATH=. python tools/reports/ace_capacity_report.py
PYTHONPATH=. python tools/reports/ace_capacity_quality.py
PYTHONPATH=. python tools/reports/ace_capacity_synthesis.py
python tools/reports/ace_capacity_plots.py
PYTHONPATH=. python tools/reports/ace_capacity_inventory.py
```

Analysis uses only explicit development manifests. The quality command
reuses saved reference/source checks when present; producing missing checks
uses local Rocq on registered trainX sources, never an API call. Immutable
JSON creation refuses changes. Plot-file metadata and diagnostic logs can
change when regenerated; use the recorded artifact hashes to distinguish
the reviewed export from a new export. The inventory is a final snapshot,
so regenerate it in a new review copy if preceding exports have changed.

`ace_capacity_preflight.py` separately verifies 80 historical observed
prefixes. Those old caches lack the opaque state/declined barriers required
for an exact historical terminal claim; do not conflate that weaker check
with the new transport-aware replays.

## Tests and operational record

`tests_preflight.log` records 49 tests from `test_ace_capacity.py`,
`test_ace_attribution.py`, `test_ace_polish.py`, `test_grounded.py` and
`test_campaign_budget.py`, with `runtime.development_only.install()` run
before pytest imports. They include actual trainX Rocq fixtures, model-state
restoration, denied-budget events, prefix divergence, and a complete
mock-HTTP base/continuation/replay test. `typecheck_completed.log` uses
Pyright 1.1.406 on the follow-up files; `ruff_completed.log` records Ruff.
`root_typecheck_pinned.log` preserves the 17 known upstream errors.
`agents_completed.log` records the canonical-instruction/symlink check.

`campaign.log`/`campaign.exit` preserve the first coordinator execution.
It stopped after a complete 17-done/1-failed money-continuation batch because
the launcher returns nonzero on a platform failure. `supervised_completion_01.json`
checks all statuses, the exception hash and zero outstanding liability, then
accepts that completed batch under the registered failure-in-denominator rule.
`resume_01.sh`, `campaign.resume_01.log` and `campaign.resume_01.exit` preserve
the remaining 11 executions. No prompt change, retry, allowance change,
source amendment or extra experimental cell was introduced by that resume.

Do not run global tests, partition checks, repricing, or Ladon CLI status:
they may eagerly access closed data. Ladon was checked through `night.yaml`
metadata only, with all nights `state: done`, before updating the local
backlog/history. See `closure_correction.json` and
`closure_maintenance_note.json` for the access disclosures; numerical
analysis is restricted to trainX/validationX, without a zero-exposure claim.
