# Sanitized ACE campaign

Authorized September 17, 2026: **$25 new API spend**, trainX/validationX only.
No default promotion. Full rationale, audit and results live in
[the report](../../../docs/ace_sanitized_report.md).

The paid campaign is complete: **514 cells, 5,362 settled receipts,
$8.83303748 spent**. Current exports are `analysis/final_v2/` and
`replays_v2/`. Reporting revision 2 automatically preserves the loaded helper
source; it refreshes old offline certificates with missing helper snapshots.
Earlier reports and certificates are retained as history. No new paid call
is needed for reporting or replay.

Both Codex CLI and Claude Code use the same commands from `examples/omphalos`:

```bash
source ~/.config/omphalos/env.sh
python -m experiments.ace_sanitized prepare
python -m experiments.ace_sanitized prepare-roles
python -m experiments.ace_sanitized seal
python -m experiments.ace_sanitized role-pilots
# Inspect outputs/receipts and record role_safety_review.json.
python -m experiments.ace_sanitized assess-roles
python -m experiments.ace_sanitized adapt
# Inspect every changed rule and record book_audit.json.
python -m experiments.ace_sanitized pilot
python -m experiments.ace_sanitized combination
python -m experiments.ace_sanitized freeze
# Registered amendment, after training selection and before validation:
python -m experiments.ace_sanitized_headroom register
python -m experiments.ace_sanitized benchmark
python -m experiments.ace_sanitized_headroom run
python -m tools.reports.ace_sanitized final
python -m tools.reports.ace_sanitized figure
```

Run paid commands in tmux using the supervised launcher. Each subprocess
uses one supervised attempt, 24 workers and 32 machine-wide slots. Existing
completed batches are idempotent; individual cells are never silently retried.
Manual reviews above are agent audit records, not additional user approvals.

`protocol.json` binds the design; `seal.json` binds runtime sources and role
fixture labels before payment. Individual immutable input files are hashed
in manifests. `freeze.json` binds training selection and the learned book
before validation. Replays block HTTP and require exact result and budget
equality without new paid receipts. `ledger.sqlite3` is the authoritative
spending ledger; exported receipts include dates and recomputed charges.

Training selected incumbent ACE on cost per solve and the 8,192-token cap
on coverage. Two optional control panels are therefore duplicates. The
pre-validation `headroom_protocol.json` uses one freed slot for the same
8,192-token cap with an empty book: exactly 80 additional attempts, funded
only if all $8 worst-case liability fits. The four validation panels share
40 problems and two replicates; the primary comparison is unchanged.
The amendment driver is separately sealed because the paid runtime was
already frozen. No new random seeds or validation-led tuning are introduced.

Never run legacy mixed-scope verifiers, aggregate test/repricing commands or
the eager X-partition loader. The package installs a development-only file
guard before importing experiment code. Historical archives remain intact.

Scoped offline checks, from the same directory:

```bash
pytest -q tests/test_ace_sanitized.py tests/test_ace_sanitized_headroom.py \
  tests/test_ace_sanitized_report.py tests/test_campaign_budget.py
make agents-check
```

Large paid caches, transport snapshots and the live SQLite ledger remain
local in the existing archive locations. Reviewable manifests, immutable
inputs, books, source snapshots, replay certificates, hashes and CSV receipt
exports accompany the report. Reproduction requires those local archives;
the CSV costs can be independently recomputed from dated token counts.
