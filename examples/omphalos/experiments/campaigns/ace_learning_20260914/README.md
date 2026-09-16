# ACE learning campaign — development data only

User-authorized new API ceiling: **$30**. Primary control: completed polished
v2 (`ace_revision_20260913`), reused without new control charges. The generator
is frozen; trainX and validationX are the only benchmark panels. Defaults stay
unchanged. Both Codex and Claude Code use the same supervised Python driver.

Start with the [human report](../../../docs/ace_learning_report.md),
[measured results](RESULTS.md), and [every paired cell](CELL_INSPECTION.md).

## Evidence map

- `authorization.json`, `protocol.json`, `preflight.json`, `seal.json`:
  authorization, decision rules and source/input hashes frozen before dispatch.
- `compatibility.json`: 120 complete historical proof controls, result hashes,
  matching runtime profile, v2 source-seal verification.
- `pilot_registration.json`: exactly 52 fixed role cases, source-family
  exclusion, and pre-call review labels, including four unresolved cases.
- `pilot_sources/`: exact historical query captures and fixed pilot inputs;
  `sources/`: the 40 frozen development histories reused for adaptation.
- `pilot_adjudication.json`, `pilot_decisions.json`: measured local outcomes
  and gate decisions. Schema/review excluded; reflection/curation included.
- `manifests/`, `batches/`, `inputs/`: every new paid episode and its immutable
  inputs, completion status and naming. Invalid outputs stay in denominators.
- `revisions/`, `book_steps/`, `books/`, `audits/`: the book mutation chain,
  frozen candidate and exact independent Rocq receipt rechecks.
- `selection.json`: training decision frozen before validation registration.
- `cells.csv`, `receipts.csv`: cell outcomes and actual token/billing receipts.
- `analysis/metrics.json`, `analysis/economics.json`: family-clustered paired
  results and 90% intervals, preparation and input-cache sensitivity.
- `analysis/pilots.json`, `analysis/reflection_checks/`,
  `analysis/curation_checks/`: role outputs and real offline checks.
- `analysis/paired_inspection.json`, `analysis/cell_inspection.json`,
  `analysis/traces/`: every success/failure with actual model/verifier output,
  accepted prefixes, remaining goals, final admissions, and source log paths.
- `analysis/power_rule_premise.json`: a retained-rule defect documented from
  actual `Check Nat.pow_inj_r`; source execution is not general-rule validity.
- `analysis/dispatched_books.json`, `analysis/raw_inventory.json`,
  `analysis/final_integrity.json`, `replays/`: dispatch exposure, raw checksums,
  receipt/source reconciliation, and exact HTTP-forbidden replay results.

The large raw caches and transport snapshots stay in the immutable local
`experiments/output/ace_learning_20260914/` and campaign `transport/` archives.
The lean staged evidence bundle includes their inventory and paths. Historical
raw controls remain in the v2 archive; neither archive is edited or erased.
The SQLite ledger is the live accounting authority; its final receipt CSV and
repriced summary make the report auditable without duplicating live database
files into Git.

From `examples/omphalos`, after measured work completes:

```sh
python -m experiments.ace_learning_experiment replay
python -m experiments.ace_learning_experiment report
python -m tools.analysis.ace_learning_failures
python -m tools.analysis.ace_learning_artifacts
```

Analysis scripts do not dispatch HTTP. The driver refuses missing required
cells, billing uncertainty and sealed-input drift. Replay requires the raw
local archives. The preparation/dispatch commands and staged tests are detailed
in `docs/ace_learning_implementation.md`.
