# ACE review campaign — 2026-09-08

The experiment docstring registered the rules before API calls began.
This file records the approved protocol and how either agent harness can
resume it. All commands run from `examples/omphalos`. Paid work runs in
tmux; its shell must first `source ~/.config/omphalos/env.sh` because an
existing tmux server may predate the API environment.

**Completed on 2026-09-08 at 22:56 local time.** All 864 evaluation cells
and both training seeds finished. Confirmation: x3 121/176 versus baseline
118/176, +1.70 points, clustered p=0.5811; the registered gain was not
established. Matched Terra reference: 22/32 versus 25/32 solves, at 25.42%
of Terra's cost (95% descriptive ratio interval 17.29%–35.69%). Final
liability: **$39.01643976**, including $0.688999 of unknown charges, with
no in-flight receipts. See [the review](../../../ACE_REVIEW.md),
[final report](final_report.json), [billing audit](operational_audit.json)
and [effect plot](effect_comparison.png). The scripts below are retained
for reproducibility; completion does not authorize a new tuning round on
the protected outcomes.

## Protocol

- Total liability ceiling: **$50**, including failed attempts, retries,
  embeddings and in-flight reservations. Stage allocations are calibration
  $4, adaptation $8, development $8, confirmation $18, Terra $7,
  contingency $5. Never reinterpret an interrupted study as a null result.
- Hardware: CPU-only replay of 192 fixed training bridge calls at
  8/16/24/32 workers. Choose fastest with identical outputs and peak RSS
  below 75% of initially available memory. `runtime_benchmark.json` and
  `runtime.json` record the measurement and resolved settings. The selected
  launch size is 24; machine slot ceiling 32. Ordinary ACE make targets
  inherit the configured stream ceiling (16 on this server).
- All new generator arms use Luna Responses, core tools, medium reasoning,
  definitions shown and a nominal $0.10 stopping rule. The primary score
  counts only verified proofs whose **actual charged cost** is <=$0.10.
  Crossing requests remain charged; unsuccessful attempts remain in cost
  and solve denominators. A shared 32,768 output-token ceiling makes
  per-request reservations possible. Hidden SDK retries are disabled.
- Request ceilings apply per attempt. A cell can exceed that request
  count across the registered fresh retries; its qualification cost
  includes every attempt.
- Calibration: fresh baseline, 32 versus 64 requests, all 40 trainX
  theorems and two replicates. Use 64 only if it gains at least 5 percentage
  points overall and loses nothing in either replicate.
- Adaptation: `review-repair-s0` and `review-repair-s1` retain x3's models,
  prompts, 4,000-token playbook guard, embedding threshold, batch size 4,
  traversal, reduction and refinement. After an unsuccessful episode,
  perform up to two fresh reflection-conditioned generator episodes,
  each 16 requests/$0.05, stopping on verified success. Reflect over the
  original plus repairs and curate from that evidence. Seed0 is the
  precommitted deployable artifact; seed1 checks training stability.
- Development: fresh baseline, frozen x3, repair seed0 and repair seed1;
  validationX, two replicates, calibrated common request ceiling.
  Select between x3 and repair seed0 by budget-qualified verified solves,
  then lower charged cost, then incumbent. Seed1 is never substituted for
  a luckier artifact.
- Confirmation: baseline versus the selected frozen ACE artifact, all 88
  previously unexposed challenge theorems, two replicates. Exact paired
  sign-flip test clusters all seeds and duplicate-family members together.
  Improvement requires >=5 percentage points and two-sided p<0.05.
  Descriptive cluster bootstrap intervals accompany effects and costs;
  a conservative bound guards against falsely excluding +5 points when
  the bootstrap degenerates. With 88 problems this study may be inconclusive.
- Terra reference: Responses, core tools, low reasoning, 32 requests,
  nominal $0.30, one replicate on the fixed stratified 32-theorem subset.
  Compare against ACE's precommitted replicate0 on exactly those theorems.
  Cost target: at most one third of Terra's mean charged cost. Report
  training amortization at 100/1,000/10,000 deployment problems.
- The challenge and 166 reserved Mathd problems cannot feed adaptation or
  failure mining. The manifest records statement hashes, exposure metadata
  and template/family filtering. "Unexposed" refers to this project's work,
  not a claim about model pretraining. ValidationX is development data.

## Resume and report

```bash
source ~/.config/omphalos/env.sh
python experiments/ace_review_experiment.py --phase=calibration run --wait
python tools/ace_review_report.py calibration
python experiments/ace_adaptation.py run --variant=review-repair-s0 --max_workers=4
python experiments/ace_adaptation.py run --variant=review-repair-s1 --max_workers=4
# calibration.json selected 64 requests for all cheap evaluation arms.
python experiments/ace_review_experiment.py --phase=development --requests=64 run --wait
python tools/ace_review_report.py selection
python experiments/ace_review_experiment.py --phase=confirmation run --wait
python experiments/ace_review_experiment.py --phase=terra run --wait
python tools/ace_review_report.py final
python tools/export_ace_review.py
python tools/plot_ace_review.py
python tools/ace_review_report.py status
```

If a stage allocation is exhausted, a resume can explicitly use
`--budget_stage=contingency` (before `run`) within the remaining contingency
allocation ($3 after the audited transfer below).
This changes accounting allocation only; it preserves cell identities,
request limits, caches and all receipts. Never draw on a different stage
implicitly.

Add `--retry_errors` to an evaluation launch only when resuming recorded
infrastructure errors. Their exception records and paid receipts survive.
The adaptation driver also retries through `retry_failed()`, which preserves
exceptions and rebuilds launcher state. The launcher starts a fresh
attempt and removes the active cache; `retry_failed()` now preserves that
cache under `configs/<cell>/attempts/<timestamp>/` first. All attempt
charges remain in the ledger. The former `mark_errors_as_todos()`
was undone by the launcher's ground-truth rebuild.

`calibration.json`, `selection.json`, `final_report.json` and
`final_cells.json` are immutable decisions/results. `ledger.sqlite3` is the
billing record; unknown charges retain their full reservation. Never delete
in-flight records to free money. Do not copy a live SQLite database without
its WAL: use SQLite's backup API for a portable snapshot.
After completion, `export_ace_review.py` reads a consistent transaction
and freezes every receipt in LF-terminated `receipts.csv`, with allocation
transfers, token-size summaries and exception classifications in
`operational_audit.json`. It rejects pending billing or any mismatch with
the final report. Neither export reads proof trajectories.
`plot_ace_review.py` renders the frozen development and confirmation
effects with descriptive cluster intervals and exact p values as
`effect_comparison.png` and `.pdf`. It uses Matplotlib (3.11.0 in this
environment), makes no model calls and refuses to change an existing
figure. Development and confirmation are clearly separated in the plot.

The frozen x3 artifact is an incumbent, not a contemporaneously retrained
no-repair control. Thus a repair-artifact improvement does not isolate the
causal effect of reflection from additional adaptation compute or training
randomness. The final baseline comparison measures the deployed ACE pipeline.

For a later CPU diagnostic, use `python tools/bench_ace_runtime.py --output
experiments/campaigns/ace_runtime_followup` with a new directory. The tool
refuses to replace the frozen runtime files. Later sweeps also record
per-chunk durations and a workload digest; these fields were added after
the original measurement and do not alter its selected campaign profile.

## Execution notes

The first calibration launch encountered a missing API credential in the
pre-existing tmux server environment. All 160 configurations failed before
any HTTP request; liability was $0. A source-environment launch with
`--retry_errors` preserved those exceptions and resumed the same cells.
No proof outcomes were available from the failed launch.

At 16:38 local time, $2 of unused contingency was explicitly transferred
to calibration (calibration $6, contingency $3; total still $50). The
fixed 160-cell panel and all per-cell budgets were unchanged. The transfer
was made before allocation exhaustion to avoid censoring late cells or
forcing administrative restarts. Transfers are atomic, audited in SQLite,
and cannot move committed or in-flight money. The original allocation
remains pinned for safe resume.

After calibration completed at $4.51740896 liability and selected 64
requests, $1.40 of its unused allocation was transferred to development
(calibration $4.60, development $9.40; total still $50). This supports the
fixed 320-cell development panel without an administrative restart and
does not change the selection rule.

Once both training seeds and their final playbooks were complete at
$3.31574694 liability, $4.50 of unused adaptation capacity was transferred
to development (adaptation $3.50, development $13.90; total still $50).
The two complete training ledgers are exported as `training_steps_s0.json`
and `training_steps_s1.json`, preserving their original CSV cell values
and source hashes. The generated CRLF CSV files remain unchanged locally.

Development finished all 320 cells at $12.07775284 liability and selected
frozen x3: 57/80 budget-qualified solves versus baseline 52, repair seed0
52 and repair seed1 54. The development x3 comparison remains inconclusive
(clustered p=0.234375). Once this decision was frozen, $1.70 of unused
development capacity was transferred to confirmation (development $12.20,
confirmation $19.70; total still $50). The 352-cell confirmation panel
started at 19:59 local time, using the selected 64-request ceiling.

Confirmation finished at 21:44 local, including one server-error retry,
at $13.61031742 liability. It found 118/176 budget-qualified baseline
solves and 121/176 for x3 (+1.70 points, clustered p=0.5810546875):
inconclusive. After this complete comparison was frozen, $3 of unused
confirmation capacity was transferred to the fixed Terra reference to
support its larger per-request reservations (confirmation $16.70,
Terra $10; total still $50). This is an accounting transfer, not an
increase in any cell's request limit or nominal dollar stopping rule.

A cache-preservation fix was added after observing that the stdlib removes
active caches on retries. No adaptation retry had occurred when it was
added. This affects retained evidence, not prompts or retry search logic.

The initial admission adapter explicitly used a 180-second HTTP deadline.
The first full calibration pass encountered five client timeouts and one
server error. Subsequent launches restore the OpenAI SDK's usual
600-second deadline. This changes
transport reliability, not model prompts, request budgets or Rocq bounds.
The initial calibration/training processes retain their loaded deadline;
new launches use 600 seconds. Earlier unknown charges remain liabilities.
All completed outcomes and failed-attempt receipts are retained. The
calibration is an operational pilot as well as a request-budget check;
its mixed transport history is a limitation. Development and confirmation
use the restored deadline for both arms.

The registered runner gives recorded evaluation errors, including API
context-window exhaustion, at most two further complete attempts,
uniformly across arms, with every attempt charged to its cell.
Residual failures stay in solve denominators. Admission failures make a
panel incomplete rather than producing a quality verdict.

`python -u tools/continue_ace_review.py` resumes the campaign after the
three initial tmux launches. It waits for calibration, applies at most
two fresh retries to recorded errors, freezes calibration, runs development controls
while repair training finishes, waits for each artifact, selects once,
and runs confirmation plus Terra. It uses the existing supervised launcher
for all work and an exclusive coordinator lock. It stops on budget
admission failure and never changes allocations itself. Start it in tmux
after sourcing the server environment.
