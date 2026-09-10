# Bounded ACE model selection — 2026-09-10

Guille approved implementation and execution of the staged plan, with a
$30 experiment API ceiling. Target spend is $15–25, not a spending target.
Assistant and engineering usage is outside this API ledger.

**Completed: $8.71724, retain the flagship.** The best selection candidate
reached 18/24 versus 17/24 at 12.96% lower inference cost, short of the
registered +2-solve gate. The full trainX/validationX benchmark was therefore
not triggered. See [results](RESULTS.md) and [final report](final_report.json).

Both Codex and Claude use the same entrypoint, from `examples/omphalos`:

```sh
python -m experiments.ace.ace_models_experiment prepare
python -m experiments.ace.ace_models_experiment campaign
python -m experiments.ace.ace_models_experiment status
```

Run the campaign in tmux on i34-gpu01, with the ordinary Omphalos environment
loaded. The orchestrator holds a campaign lock; its immutable batches use
OmphalosExperiment, the measured 24-worker/32-slot runtime profile, and the
shared request-reservation ledger. Pure LLM batches use four workers.
Do not run two campaign orchestrators against the same directory.

## Registered design

The experiment module's docstring and `registration.json` are authoritative.
The deterministic seed-20260910 assignment keeps whole theorem families
and puts 50% competition problems in each trainX panel: 8 source, 8 screen,
24 selection. No new outcome influences assignment. The incumbent already
has historical trainX exposure; none of these is a pristine holdout.

1. Prover: Luna low/medium/high/xhigh on source+screen, incumbent playbook,
   one replicate, at most 64 cells. Rank eligible settings; keep at most two.
   All role evidence comes from the eight new Luna-medium source cells.
2. Roles: eight settings per role (Luna/Terra × low/medium/high/xhigh).
   The common control warms the incumbent playbook with those eight fixed
   trajectories; each arm changes only one role's configuration. Reflectors
   see the book that the source prover actually saw; curators see the working
   batch book. Curator includes reducer. The auditor is independently
   configurable, with an audit-off common control. Up to 23 distinct books
   are evaluated on eight screening problems, up to 184 proof cells.
3. Interactions: pair/triple combinations of selected role settings (at most
   four additional books), then cross the two leading books with the second
   eligible prover effort (at most two additional configurations). Maximum
   48 screening proof cells. At most two distinct eligible challengers and a
   fresh flagship are evaluated on the remaining 24 problems (72 cells).
4. A challenger must gain at least 2/24 qualified solves, have inference
   cost <=1.20× reference, and not worsen cost/solve. Otherwise stop and keep
   the flagship; the protected final allocation is unused.
5. Freeze one eligible winner before the final paired trainX/validationX
   benchmarks: 40 problems × two replicates × two arms per partition, 320
   cells. No changes between partitions/replicates. Practical success is
   >=4/80 additional qualified solves on EACH partition with both cost gates.
   Validation is the primary final inferential comparison: two-sided
   family-cluster p<.10, descriptive 90% intervals. Report practical gates
   separately from statistical support; no independent confirmation claim.

Luna max opens only when xhigh gains >=2 qualified solves over high on the
same role panel with both cost gates. Each role can expand once, no new
replicate; maximum 40 extra prover cells across four roles. Terra max and
Terra proof generation are excluded: the latter's unchanged 32,768-token
output reservation costs $0.393216 before input, beyond the $0.10 problem
budget. No control calibration was approved for this suite.

Proof controls are unchanged: money/focused on, other admission/restart/
polished controls off, 64 requests, 32,768 output limit, existing verifier
and operation budgets. The new playbook parameter defaults to the existing
incumbent, and its content hash is checked. Source and working playbooks,
role inputs, source results/caches, actual model/effort requests, scripts,
prompts, statements and runtime are pinned or audited.

Offline preparation retains the v3 prompt contracts, batch size four,
4,000-token guard, embedding deduplication and end-of-epoch refinement.
The eight-source progress text is common to all variants. A missing parsed
reflection uses the existing trajectory-fed curator fallback; a missing
reducer uses the member deltas. Failures are logged. The auditor uses the
existing default-keep contract and checks proposed additions against source
problem environments. A malformed audit leaves the pre-audit book intact.
Model-generated observations are diagnostics; only downstream qualified
solves select models. A schema-valid or grounded bullet is not evidence of
usefulness. Existing frozen outputs/playbooks are never modified.

## Accounting and stopping

Initial allocations: prover $3, adaptation $5, screening $5, interactions/
selection $4, final benchmark $9, conditional max $2, infrastructure retry $2.
Completed-stage slack can move forward with an audit record, never away
from the benchmark. No cells are added to use spare money.

Every API call, parse retry and embedding request is reserved before
submission. Settled receipts are repriced from tokens, including failed
attempts. Unknown liability stays reserved and prevents a verdict. Up to
four recognized transient infrastructure failures can be explicitly
registered and retried on unchanged cells; broad retries are prohibited.
A partial or administratively censored panel is incomplete, never a null
result. Qualified solves require a verified proof at actual total cell cost
<= $0.10. Cost comparison includes unsolved cells and repeats within theorem
families are not treated as independent observations.

Expected costs: prover $1.2–2; preparation $2–4; playbook screening $3.5–5.5;
interactions/selection $2–3.5; final benchmark $6–8; optional max $0–1.5.
Preparation costs and 100/1,000-problem amortization are reported separately
from the inference-cost gate. No testX, protected challenge or reserved
Mathd outcomes are accessed for adaptation or analysis.

## Validation and results

New attribution/immutability/accounting tests join `make test-unit`.
Preflight includes those tests, Omphalos `make test`, type checks, Ruff and
repricing. Root Pyright's existing 17 `why3py.simple` errors are outside
this campaign's edit scope. Final results and receipts are recorded in [RESULTS.md](RESULTS.md),
[final_report.json](final_report.json) and [receipts.csv](receipts.csv).

## Scheduling amendment

`scheduling_amendment.json` records a scheduling-only change after the 64
prover cells, common playbook/eight screening cells, and the next reflection
batch. The old process stopped at a completed batch boundary: $1.35003882
settled, no requests in flight. Its next batch was rejected before config
registration or HTTP calls; it is not a failed problem measurement.

The remaining standard role books are prepared first and their independent
screening configurations are submitted in one shuffled 24-worker batch.
This avoids serial eight-cell launches occupying the worker pool. Treatments,
role prompts, budgets, panels and gates are unchanged. All completed cells
are reused at their measured cost; original source proof configurations pass
exact parity. The original registration, execution snapshots and first log
remain preserved, and the effective source hashes explicitly include the
amendment. A regression checks the 23 × 8 standard screening matrix and
its single-batch scheduling. Conditional max arms remain gated separately.

Preparation/amortization figures are incremental to the shared historical
incumbent playbook. They include the new source runs and the selected role
DAG; the original playbook training cost is common and sunk, and exploratory
model-selection spend is reported separately in the campaign ledger.
