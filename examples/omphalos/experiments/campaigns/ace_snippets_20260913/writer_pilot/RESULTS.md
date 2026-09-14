# Curator/reducer Rocq tool comparison

The reducer benefited most from the repaired writer interface: both reducer
jobs produced valid final output, and one batch retained two useful checked
corrections. Fresh current-prompt controls and the first draft variant retained
none. Curator useful-edit coverage remained 2/8; valid curator outputs improved
from 5/8 to 7/8 after the interface repair. This is development evidence about
writing, not evidence of improved theorem-solving coverage.

| Writer/variant | Valid outputs | Cases with useful retained edits | Useful edit occurrences | Executed Rocq checks | API cost |
|---|---:|---:|---:|---:|---:|
| Curator, fresh control | 7/8 | 0/8 | 0 | 0 | $0.01668706 |
| Curator, draft v1 | 5/8 | 2/8 | 2 | 10 | $0.03414768 |
| Curator, receipt v2 | 7/8 | 2/8 | 2 | 10 | $0.03513056 |
| Reducer, fresh control | 1/2 | 0/2 | 0 | 0 | $0.00946518 |
| Reducer, draft v1 | 0/2 | 0/2 | 0 | 6 | $0.02003712 |
| Reducer, receipt v2 | 2/2 | 1/2 | 2 | 6 | $0.01829784 |

There were 30 newly dispatched writer cells: twenty in the paired v1 stage,
then ten v2 cells reusing the compatible ten control and ten v1 cells. All 30
required cells reached terminal status; unfinished strategy outputs stay in
the denominator. There were no missing cells, administrative censoring,
unknown charges, failed transports or paid retries in these two stages.

The four useful v2 edit occurrences represent three distinct source corrections:
finite-sum unfolding, an explicit numeral/cast bridge, and product-hypothesis
normalization. The cast bridge appears in both a curator and a reducer output;
these are repeated observations, not independent discoveries. A retained
square/product instantiation was checked successfully but judged redundant
with the book and received no utility credit. Open fragments certify local
execution, not completion of their source theorem or all introduced obligations.

## What changed and why

1. The original writer policy selected no writer demonstrations; a shared prompt
   mixed role rules, and candidate code disappeared before reduction. Draft v1
   gives curators/reducers explicit unverified candidate records, role-specific
   instructions, one applicable source-family-excluded demonstration and a
   required retain/drop decision per draft. Its 16 actual checks versus zero
   controls demonstrate changed model behavior. More calls alone did not pass
   the gate: three curators and both reducers failed final receipt bookkeeping.
2. Those five v1 failures exposed a concrete interface defect. Agents listed
   known rejected attempts among dropped receipts; the existing compiler only
   allowed executable IDs there. V2 allows known failed attempts to be dropped,
   keeps them impossible to retain, and supplies the exact receipt/draft IDs in
   repair feedback. Unknown and duplicated IDs still fail. V2 requested 17 tool
   calls and executed 16 checks; one repeated request reused its receipt and
   did not count as new checking.
3. The remaining v2 failure, amc12b_2004_p3 curator, copied an incorrect receipt
   ID and then returned malformed YAML. Its valid checked snippet was not
   silently recovered or counted. A next isolated interface improvement would
   use short local aliases bound to immutable receipt identities and a robust
   structured final-answer channel. No third contender was implemented or run.

`reduction_input` also preserves typed drafts, source contexts, decisions and
exact retained curator receipts across the handoff. A scripted real-Rocq test
executes curator repair followed by reducer reuse with no extra probe. The paid
roles here were tested independently on identical source packets; chained
adaptation quality and downstream book/prover benefit remain unmeasured.

## Gates and interpretation

The registered v1 second-seed gate **failed** because only 5/10 contender jobs
produced valid outputs. Its seed1 manifest remains undispatched. A separate
protocol then registered v2 as the second and final contender in the user's
authorized writer test; the v1 measurements and failed gate were preserved.

V2 produced 9/10 valid outputs, increased useful occurrences from two to four,
and lowered cost per useful occurrence from $0.02709240 to $0.01335710. For
reducers alone, the observed v2 cost was $0.00914892 per useful correction;
controls/v1 had zero useful corrections, so their ratios are undefined.
The registered v2 retention gate required **10/10 valid outputs**, so it also
**failed** despite the practical improvement. No default promotion, extra seed
or theorem proof panel follows. Keep the implementation available as an opt-in
candidate and preserve these limitations.

Only two reused source batches underlie these role comparisons. Family/source
and repeated-role dependencies prevent treating seeds or the four edit
occurrences as independent confirmations. Exploratory paired cost calculations
cluster the sources by their fixed batch, separately by role. For v2 minus v1,
the total curator cost difference is +$0.00098288 (coarse 90% interval
[-$0.00346286, +$0.00542862], two-sided sign-flip p=1.0); reducer cost difference
is -$0.00173928 ([-$0.00254454, -$0.00093402], p=0.5). Two blocks are insufficient
for p<0.10; these intervals are highly coarse. No statistical support is claimed.
The full calculations are in receipt_repair/cost_uncertainty.json.

Controls were fresh for v1, then reused for v2 minutes later with identical
source-input hashes, X3 book, model, tariff and controller/probe/request caps.
V2 changes prompts, so it does not claim prompt neutrality. Cache fractions
vary materially: across both roles, controls cached about 39.3% of input,
v1 32.4%, and v2 17.3%. Costs use every settled dated-tariff receipt, including
unfinished jobs; cheaper hypothetical cache conditions are not substituted.
Utilities were judged on the arm-free review-item export using the prewritten
source rubric. This was agent review, not independent human-blinded evaluation.

## Spending and checks

The first stage charged $0.08033704 and v2 $0.05342840: **$0.13376544 new** for
this writing-role follow-up, including controls and all unfinished outputs.
The same original ledger now totals **$5.26366084 / $30**, leaving
**$24.73633916**. No allocations or financial protection were weakened; the
$4.38640002 contingency allocation is untouched. Source generators, embeddings,
paid diagnostics, retries and proof panels cost zero because none were launched.
Codex-session costs remain unavailable and separate. Initial adaptation/book
costs remain in prior historical accounting; this follow-up adds no new book
promotion. Its total research cost per four final useful edit occurrences is
$0.03344136, or $0.04458848 per three distinct source corrections; these are
writing-study ratios, not cost per qualified theorem solve.

All 30 exact controller/transport replays passed with API dispatch forbidden.
Every retained source snippet was checked again with real Rocq before review.
There are 32 passing explicitly scoped regression tests (29 initial, 3 added
for receipt repair), full initial translation checks for 20+10 requests and
both demonstration queries, and scoped Ruff/Pyright checks with zero errors.
The bridge and its budgets were unchanged. Prior out-of-scope why3py type
failures (17, recorded by the earlier campaign) were not repaired. Installed
Pyright is 1.1.409; repository instructions request 1.1.406.

The generic harness check indirectly read memory/MEMORY.md only to test
nonemptiness; no contents were displayed or used analytically. This access
mistake is documented in scope_incident.json. Subsequent checks used the
explicit guard and targeted symlink checks. testX and protected evidence stayed
closed. No mixed history was updated; milestones and the known safe memory
entry carry this result. Changes are staged and uncommitted inside Omphalos.
Both Codex and Claude Code use the same opt-in modules, demonstrations and
supervised campaign commands.
