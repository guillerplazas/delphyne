# Evidence and archive layout

The staged evidence includes the protocol, authorization, preflight logs,
source seal, 40 cached training source fixtures, every role/proof input and
manifest, batch completions, full book revisions, final book, Rocq audit,
mechanism analysis, exposure checks, paired reports and accounting exports.
The earlier campaign's source fixtures and scripted v2 demonstration are
also retained because the regression tests use them.

`cells.csv` contains the 319 role/proof jobs, including partial role finals
and unsuccessful proofs. `receipts.csv` preserves all campaign ledger rows
with usage and settlement information. `accounting/319.json` recomputes
charges from dated token prices. The ledger database remains the local
authority; neither its old history nor interrupted requests were erased.

Large raw measurements remain in their existing local locations:

- `transport/`: exact request/response snapshots and role journals.
- `../../output/ace_revision_20260913/`: original result and cache YAML,
  experiment configurations and supervised-launch summaries.
- `events.jsonl`: detailed runtime event stream.

`archive_inventory.json` records hashes and byte counts for those raw files
after completion. They are retained locally, without hand editing or
deletion, and are excluded from the lean staged export. Transient locks,
derived result-scan indexes and SQLite WAL/shared-memory files are not
portable evidence artifacts.

The staged source fixtures are sufficient for the scoped offline tests in
[README.md](README.md). Regenerating a historical report or running exact
full-campaign replay additionally requires the preserved local output and
transport archive. A clone containing only the lean export cannot recreate
paid model responses. Do not rerun paid stages to reconstruct missing
caches, and do not regenerate sealed demonstrations in place.

Both harnesses use the same Python commands from `examples/omphalos`:

```bash
python -m experiments.ace_revision_experiment report
python -m experiments.ace_revision_experiment replay
```

These commands verify the source seal and reconciled ledger. Replay blocks
HTTP and must leave the receipt count unchanged. `replays/319.json` records
the final exact-result, budget and value comparisons; it is distinct from
the real-Rocq receipt audit in `audit.json`.
