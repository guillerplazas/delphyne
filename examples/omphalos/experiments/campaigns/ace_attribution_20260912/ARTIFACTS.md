# Evidence and reproduction

Start with [RESULTS.md](RESULTS.md). The [case appendix](CASE_APPENDIX.md)
is the readable view of every main failure/discordant solve and all new
book-swap/effort trajectories.

| Question | Evidence |
|---|---|
| What was authorized and fixed before calls? | `README.md`, `protocol.json`, `planned_proofs.json`, `adaptation_plan.json`, `seal.json` |
| Which old source and measurements existed? | `LINEAGE.md`, `reference_source/`, `historical_comparison.json`, `historical_to_flagship.json` |
| Are the Luna controls compatible? | `references.json`, `preflight.json` (80 observed-request replays) |
| What happened in each main cell? | `complete_report.json`, `complete_diagnostics.json`, `case_summaries.json` |
| What happened in each small diagnostic cell? | `supplemental_diagnostics.json`, `comparative_supplement.json` |
| What failed and how often? | `failure_profiles.json`, `CASE_APPENDIX.md`; error categories retain original verifier text |
| Why can a run stop before its dollar cap? | `complete_admission_probe.json`, with all observed answers replayed and HTTP disabled |
| How much did caching affect prices? | `pricing_sensitivity.json`, `solve_cost_curves.png`, `solve_cost_curves.pdf` |
| How did each book evolve? | `training_evolution.json`, `training_diagnostics.json`, `training_accounting.json`, `luna_preparation_accounting.json`, `preparation_role_inventory.json` |
| What is in each final book? | `book_audit.json`, `terra_playbook.yaml`, `terra_book.json`; Luna book is `experiments/playbooks/ace_x3_offline.yaml` |
| Are references and snippets valid? | `luna_reference_checks_v2.json`, `terra_reference_checks_v2.json`, `quality_probe_scope.json`, `quality_probe_have*.json` |
| What proves the goal-visibility issue? | `quality_probe_goal_visibility*.json` |
| Were all paid cells executed as registered? | `execution_inventory.json` (arguments and result/cache hashes) |
| Does billing reconcile? | `final_accounting.json`, `receipts.csv`, `reprice_registered.json`, `reprice_registered.log` |
| Why was execution amended? | `EXECUTION_NOTES.md`, `amendments/`, the two `amendment_*_before.json` files |
| What passed and what remains broken? | `scoped_tests_completed.log`, `typecheck_final.log`, `root_typecheck_completed.log`, `adaptation_typecheck_comparison.json`, `verification.json` |

The report JSONs and selected diagnostics are durable review artifacts.
Immutable raw paid caches/results remain in these local roots, with their
exact paths and hashes recorded in the inventory:

* `experiments/output/ace_attribution_20260912/`
* `experiments/output/ace_adaptation_attribution-terra-20260912/`
* Historical controls and Luna preparation: only the exact source paths
  named by `references.json` and `training_diagnostics.json`.

The raw SQLite ledger, event stream, batch completion markers, and launcher
logs remain local in this campaign directory. Receipts are exported as CSV;
no raw cache, book, or historical verdict was overwritten. Intermediate
Luna diagnostics are redundant with the complete diagnostics and remain
available locally. The original failing `campaign.exit` is preserved;
`campaign.resume_01.exit` records the resumed coordinator's completion.

Both Claude Code and Codex can regenerate the offline reports from the
existing frozen outputs, from `examples/omphalos`:

```sh
python -m tools.reports.ace_attribution_report
python -m tools.reports.ace_attribution_diagnosis --check-references
python -m tools.reports.ace_attribution_admission
```

The campaign/report modules install the development-only data guard before
loading experimental contracts. Reference availability probes use local
Rocq only. The admission probe forbids HTTP even on a cache miss. Repricing
in the diagnosis module derives all seven exact runs from the registered
inventory. The generic CLI only discovers immediate children: pointing
it at the top campaign directory misses nested train/validation arms and
a directly named adaptation run. `reprice_registered.json` checks all 402
new generative configurations plus embeddings. Do not substitute a global
output scan.
Historical preflight is the recorded pre-launch check, not a command to
restart after this campaign has already acquired receipts. No new API run
is needed to inspect the study.
