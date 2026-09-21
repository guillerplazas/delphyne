# Independent ACE investigation

**Completed September 21, 2026: 2,044/2,044 solver cells, no pending paid work.**
The paid queue finished September 20 at 23:31 Europe/Berlin; numerical
certification finished at 23:43. Final review adds raw O1 diagnosis and a
versioned correction to inclusive sign-flip tie handling. The
[short report](../../report/ace_independent_audit/short_report.md),
[long report](../../report/ace_independent_audit/long_report.md) and
[evidence index](../../report/ace_independent_audit/artifact_index.md)
are the current deliverables. Earlier checkpoint documents remain preserved.

This package reconstructs historical evidence and runs a registered Luna
study using only `trainX` and `validationX`. It never imports the eager mixed
partition loader. Codex and Claude Code use the same commands and artifacts.
Run commands from `examples/omphalos` in the project's Python 3.12 environment.
Rocq and the configured opam switch are needed for proof compilation.

## Scope and result

The solver contract fixes Luna medium, Responses, 32 requests, a $0.10 stopping
allowance, 32,768 output tokens, `ReadSkill` and `SearchRocq`, definitions,
informal sketches and the existing two tool-use demonstrations. Assisted
and plain checking each have an equivalent non-ACE control. Stronger models
operate only in preparation. The spending threshold permits a crossing
request; reported fees are never clipped to it.

The main 1,520-cell study contains 1,280 frozen-book cells and 240 online ACE
cells. Online courses reuse 160 trainX controls from the frozen matrix.
R1 adds 80 trainX cells and O1 adds 160 trainX/validationX cells. Sources (80)
and author pilots (204) bring the registered total to 2,044. The 4,560 lower
budget replays are conditional checks over 1,520 frozen cells, not additional
paid attempts or independent samples.

O1, an adaptive forty-task train curriculum frozen for serving, saves 12.97%
on trainX at the original matched allowance, with 64 versus 63 solves out of
80. On validationX it saves 4.54% with equal 56 solves. O1 at $0.05 versus
ordinary A0 at $0.10 saves 15.69%, with 55 versus 56 solves; ordinary budget
control already contributes 11.86%. The matched-$0.05 ACE contribution is
4.35%. Preparation costs $23.46235 and is reported separately. These are
familiar/development observations with broad uncertainty, not untouched
confirmation. The full research bill is $317.40915825–$317.63155097.

Campaign evidence lives under `experiments/campaigns/ace_independent_audit`;
compact reports live under `report/ace_independent_audit`. Paid caches,
books, source snapshots, protocols and receipts are immutable. A periodic
`result.yaml` alone never establishes completion: the adapter writes a
hash-bound receipt after the worker returns and checks final state/locks.

## Final evidence and safe verification

The full study has 2,040 normal exact replays, four separately certified
terminal-prefix/request checks, and 1,215 distinct compiled proofs covering
all 1,537 solved cells. All returned provider usage is independently repriced.
The historical audit additionally recompiles 3,485 distinct proofs covering
4,953 permitted solved cells. Its 10,110 result cells and 153 exception-only
cells remain separate from this study's denominator.

These commands reuse certified outputs only after validating their hashes;
HTTP is disabled during replay:

```bash
python -m experiments.ace_independent_audit.verification run-completed
python -m experiments.ace_independent_audit.budget_replay run-completed
python -m experiments.ace_independent_audit.status
```

The final analytical review makes no model calls:

```bash
python -m experiments.ace_independent_audit.statistical_review
python -m experiments.ace_independent_audit.final_diagnosis
```

`statistical_review` preserves the original finalized statistics and supplies
reviewed p-values for 263 comparison records. It asserts unchanged costs,
coverage, bootstrap intervals and practical-target decisions. Rounding had
excluded mathematically tied sign assignments; inclusive rtol/atol 1e-12
corrects that. Sparse exact enumerations and six synthetic tests independently
check it. One secondary budget-only family p-value changes materially
(0.000020 to 0.063179; exact reference 0.0625). The headline comparisons and
all p<0.10 classifications are unchanged. `reporting.inputs()` uses this
versioned review; `inputs(reviewed=False)` reproduces the original input view.

`final_diagnosis` reconstructs all 320 A0/O1 cells from raw caches and writes
`final_diagnosis_reviewed.json`, with corrected joint-budget statistics,
selected proof trajectories, rule origins and source hashes. The earlier
`final_diagnosis.json` remains the original pre-correction diagnostic.

`numerical_finalization.json` records the original completed automatic
sequence: fresh analysis, supplements, mechanisms, economics, receipt and
study certification, rate diagnosis, budget tables and figures. Its ten
artifact hashes are preserved. Do not rerun its write-once statistical
finalizers over those originals after the tie correction: use the versioned
review commands above. Historical checkpoint finalizers likewise describe
an earlier ledger and must not be rerun against the completed ledger.

## Preserved incidents and scheduling

One B1 trainX request timed out after 600 seconds without a response ID.
Its failed outcome is retained. The 23 known responses cost $0.03731910 and
its unknown request retains a $0.22239272 upper bound. Its receipt state is
`bounded_charge`, never an invented exact invoice. The reconciliation used
the user's existing API continuation authorization. Every other unknown
receipt still blocks dispatch. Billing intervals propagate to comparisons;
an exact cost p-value is omitted for an affected comparison.

Three context-limit failures preserve their paid prefixes and rejected
requests. No failed attempt was replaced. The separate account-credit
interruption was administratively censored only until its exact continuation:
A2 trainX `amc12b_2004_p3`, replicate one, finished failed after 23 responses
and one zero-charge rejection, costing $0.10516041. Its original eight-response
prefix and first next-request identity are preserved in `quota_recovery/`.

The replacement account's 500,000-TPM limit interrupted 87 original
trajectories: 64 before any response and 23 after 83 paid responses. Every
prefix/next request passed HTTP-disabled replay before continuation. The
first paced runner used serialized HTTP. The user then authorized less
conservative scheduling: four HTTP requests and four proof workers, with a
shared 400,000-token/minute target. `concurrent_rate.py` holds estimates only
while requests are in flight, substitutes actual returned usage, retains
outstanding requests across window boundaries, and applies shared cooldown
only to explicit temporary rate rejections. It does not retry unknown bills,
credit errors or oversized requests as temporary quota errors.

The original batch finished before `run_concurrent_queue.sh` took over the
remaining 160 S1 and 160 O1 cells. A lock-only output directory exposed a
standard-launcher initialization assumption before any API call. The scoped
queue adapter verifies zero receipts/no execution artifacts and initializes
ordinary empty state through the existing serializer. The original error,
repair, scheduling amendments and prior helper sources remain in
`rate_recovery/concurrent/`. No shared launcher source was changed.

Detached tmux sessions preserved the same evidence and completed normally.
There are no active experiment or finalizer sessions to resume. The old
launch scripts are retained as execution provenance; they are not a request
to start another study. Scheduling/account changes can affect cache behavior,
and actual fees remain unadjusted. The final O1 diagnosis includes uncached
fixed-trajectory repricing as sensitivity, not a counterfactual deployment.

## Completed diagnostic modules

All local repairs preserve the benchmark outcomes. A hand repair is evidence
of a valid route, not an autonomous solver success. See the evidence index
for exact artifact names and checks.

- `lcm_repair`, `context_repair`: original failed candidates repaired and
  independently compiled; the LCM also passes the unassisted runtime bridge.
- `goal_flood_probe`, `trace_dossiers`: invalid duplicated list witness,
  verifier-time and feedback-cost analysis; compiled contradiction witness.
- `output_repetition`, `parser_replay`: all 27 capped replies in the original
  seven validation panels, one recovered valid proof, exact controller
  acceptance and the actual next-request saving.
- `pilot_repeat`: identical initial requests on the selected twelve problems,
  unfavorable paid repeats, and one compiled missing-dependency repair.
- `rule_probes`, `rule_repairs`: sixteen synthetic claim checks and the
  completed eighty-cell R1 intervention, with no replacement outcomes.
- `book_signal`, `learning_costs`: rule provenance and preparation fees.
- `learning_cache`: opt-in one-shot author payload helper; its six paid
  diagnostic calls already finished. Do not run its paid action again or
  apply that policy to the solver's reused conversation.
- `reproduction_output_cap_diagnosis.json`: read-only reconstruction of all
  320 allowed historical reproduction cells and their admission estimates.

## Figures, PDF export and review bundle

Figures are standalone PNG/SVG/PDF exports from the audited artifacts.
Recreate them with `python -m experiments.ace_independent_audit.figures final`.
The complete current tables are `serving_results.csv`, `serving_replicates.csv`
and `budget_frontier.csv`; the p-value review supersedes matching old JSON
values. The paired bootstrap plots are unchanged by the tie correction.

From `report/ace_independent_audit`:

```bash
pandoc long_report.md -o long_report.pdf --pdf-engine=xelatex --lua-filter=../../experiments/ace_independent_audit/pdf_tables.lua -V papersize:a4 -V geometry:margin=0.65in -V fontsize=10pt -V 'mainfont:DejaVu Serif' -V 'monofont:DejaVu Sans Mono' -V colorlinks:true
pandoc short_report.md -o short_report.pdf --pdf-engine=xelatex -V papersize:a4 -V geometry:margin=0.65in -V fontsize=10pt -V 'mainfont:DejaVu Serif' -V 'monofont:DejaVu Sans Mono' -V colorlinks:true
```

After narrative/PDF review, `python -m experiments.ace_independent_audit.artifacts`
creates the final receipt CSV, ledger snapshot, raw-evidence hash inventory
and compact review manifest. The initial checkpoint snapshot and the later
credit-checkpoint report archive are included. Multi-gigabyte paid caches
stay local with hashes; no credentials or closed-partition artifacts enter
the bundle. Deliverables are staged without committing. Local HINTS,
PROGRESS, WORKLOG and memory files remain unstaged; user AGENTS edits remain
untouched.

## Scoped checks

Final verification passes 42 explicit offline tests in the files below,
Ruff, the dual-harness invariant check and the repository type-check. The
installed Pyright is 1.1.409; the declared 1.1.406 pin was not changed.

```bash
pytest -q experiments/ace_independent_audit/tests.py experiments/ace_independent_audit/billing_recovery_tests.py experiments/ace_independent_audit/cost_bounds_tests.py experiments/ace_independent_audit/quota_recovery_tests.py experiments/ace_independent_audit/rate_recovery_tests.py experiments/ace_independent_audit/concurrent_rate_tests.py experiments/ace_independent_audit/concurrent_queue_tests.py experiments/ace_independent_audit/statistical_review_tests.py
make agents-check
ruff check experiments/ace_independent_audit
```

From the repository root, `PYTHONPATH=examples/libraries/why3py/src make pyright`
checks all configured code without executing benchmark loaders. The earlier
27-comparison `cost_bounds_regression` certificate remains the historical
parity check for the invoice-interval change; the later intentional p-value
correction is assessed by `statistical_review`, not that old exact-statistics
assertion. Aggregate tests, global repricing and eager legacy loaders are
excluded because they may access closed evaluation data.
