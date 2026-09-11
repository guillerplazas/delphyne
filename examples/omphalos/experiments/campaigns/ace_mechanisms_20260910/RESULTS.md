# ACE mechanism campaign results

**Retain bounded money + focused.** All 248 scheduled new cells completed
for **$3.364201**, with 2,329 settled generation requests, no retries, no
unresolved charges, no administrative censoring and no launcher failures.
There were 51 structured-output parsing failures inside mechanism cells;
these remain unsuccessful outcomes in every original score below.

## Full-problem comparison

Costs include failed attempts. Solves require kernel acceptance and actual
charged cost <=$0.10. The inference effort E comparison keeps the incumbent
playbook; it does not include playbook rewarming.

| trainX, seed 0 | Qualified solves | Cost | Cost/solve |
|---|---:|---:|---:|
| Flagship historical reference | 28/40 | $0.68922336 | $0.02461512 |
| S: explicit continuation | 22/40 | $0.45933386 | $0.02087881 |
| C: S + checked syntax | 21/40 | $0.56075226 | $0.02670249 |
| R: C + verified-progress recovery | 15/40 | $0.58072264 | $0.03871484 |
| E: fixed-book xhigh prover | **29/40** | **$0.60903516** | **$0.02100121** |

E's +1 solve and 11.63% cost saving qualified for validation despite
coverage p=1 and an inconclusive cost-ratio interval [0.790,1.004]. This was
an attainable practical follow-up decision, not a claim of confirmation.
The new training invoice was $1.94332454: E includes 16 reused paid cells;
S/C/R each add 40 cells and E adds 24. Reference cells were not repurchased.

| validationX | E solves / cost | Flagship solves / cost |
|---|---|---|
| seed 0 | 21/40 / $0.68108608 | 27/40 / $0.66722836 |
| seed 1 | 22/40 / $0.67954566 | 26/40 / $0.76607986 |
| pooled | **43/80 / $1.36063174** | **53/80 / $1.43330822** |

E lost ten solves while saving 5.07% total cost. Cost/solve rose **17.01%**,
from $0.02704355 to $0.03164260. Coverage difference -12.5 percentage points,
family-clustered two-sided p=.02734375, descriptive 90% interval[-21.25,-5.0]
points. Cost ratio .9493,90% interval[.8486,1.0855], cost p=.5046.
Mean paired cost difference -$.00090846,90% interval[-$.00308073,$.00129440];
median +$.00045104. E was cheaper on 33 cells and dearer on 47. These results
do not justify a default change. Both seeds lose coverage.

The new validation invoice was $1.36063174. All 80 flagship validation
references and 40 flagship train references were reused. Historical controls
are not concurrent randomized controls; validationX is repeatedly used
**development data**, not independent confirmation. No testX or protected
challenge outcome was inspected. Full tables/intervals and cell mappings are
in training_report.json, validation_report.json and references.json.

## Local contract evidence

All 24 local cells completed for $0.06024472 (53 requests).

| Local arm | Useful continuations | Cost |
|---|---:|---:|
| Fixed demonstrations, full prefix | 2/6 | $0.01862014 |
| Fixed demonstrations, explicit edit | 2/6 | $0.01460994 |
| Checked control, full prefix | 2/6 | $0.01594658 |
| Checked control, explicit edit | 3/6 | $0.01106806 |

Explicit edits saved 21.54% with fixed demonstrations and 30.59% with checked
control. The extra checked-control continuation was Rsqr/exact-H, already
valid before conversion. This supports the response interface, not a newly
enabling mathematical bridge. Local continuations are not full benchmark
coverage; original campaign scores have not been reinterpreted.

## The mechanism benchmark exposed a response-parser defect

S/C/R had 16/15/20 terminal structured-output parsing failures respectively:
**51/120 cells**. In 33 cases the concatenated JSON objects were identical;
others contained revised suffix or replacement proposals. A read-only
retrieval of one stored response confirmed separate `final_answer` messages.
Delphyne's inherited Responses parser joins message text before `json.loads`,
turning individually valid objects into `Extra data` errors. It returns no
candidate, so search stops while substantial problem budget may remain.
No additional model answer was generated during this diagnosis.

Consequently S/C/R's published operational results include a substantial
serialization confound. They **do not cleanly reject** explicit continuation,
checked syntax or verified recovery. The actual implementation lost coverage;
we do not claim that removing parsing failures would restore all of it.
Original counts, receipts, source hashes and decision rules remain unchanged.

A separate, opt-in **version-2 local adapter** now chooses the last final
answer message as the proof edit, matching the explicit local response
contract. It preserves reasoning state, usage, request bounds and strict
query validation. It does not splice JSON, fall back to an earlier valid
answer after malformed final JSON, hide refusals, or duplicate tool calls.
Dispatch and receipt settlement remain inherited and occur once.

Four focused tests reproduce the recorded failure, exercise differing final
answers, protect refusal/tool/incomplete paths, and preserve reasoning
reservations and shared execution-context loading. The corrected adapter
has **no paid full-problem benchmark** in this campaign.

One narrowly specified offline probe selected the recorded final message
for mathd_numbertheory_48, assembled its `simpl in Heq.` suffix on the saved
verified prefix, and ran the ordinary Rocq checker. It **closed the theorem**
without another model call. This establishes one useful already-paid
continuation hidden by parsing; it is not a rescored campaign solve or a
prediction of the corrected arm's total coverage. See
stored_response_audit.json, structured_parse_audit.json and
offline_continuation_probe.json.

## Specific remaining failures and mechanism reach

- C checked six candidates: four accepted, two declined. R checked eight:
  three accepted, five declined. Accepted repairs appeared on induction,
  trigonometric and IMO 1983 trajectories, but did not produce a unique C
  or R training solve in the frozen run. C versus S was 21 versus 22 solves
  at 22.08% more cost; parser failures prevent clean mechanism attribution.
- R recorded 10 useful-progress audit events and 76 unestablished events;
  these are events, not independent problems. Two recoveries were admitted,
  on aime_1988_p3 and amc12b_2002_p11. Both remained unsolved. R's large
  deficit also includes 20 parser-stopped cells, so it is not evidence that
  the recovery intervention alone caused those losses.
- Full scripts still encounter wrong bullet depth, malformed `change` and
  `replace`, `norm_num`/`omega`/`positivity` leakage, incompatible INR/power
  representations and invalid induction applications. A canonical syntax
  repair cannot establish a missing lemma or mathematical argument.
- E has 21 of 37 unsolved validation cells with no cached `checked_proof`
  call: the model worked through inspection calls without submitting a
  final proof to the ordinary checker. Other failures include references
  such as `Nat.le_of_mul_le_mul_left`, type mismatches, focus errors and
  expensive natural-number computations. See per-cell inspection/error
  records; the generic `other` category is not a mathematical diagnosis.
- A train-only finalization probe checked the last zero-goal inspection for
  aime_1984_p1 and mathd_numbertheory_629. Both remained incomplete under
  final kernel checking. Zero focused goals cannot justify success or
  recovery without accounting for outstanding obligations.

failure_audit.json contains every compared cell, exact cached last checks,
inspection previews, output errors, gain/loss lists, paired cost deltas and
actual repair/recovery events. Cached checks are not invocation counts.
No validation failure was turned into an adaptation example or prompt edit.

## Implementation and verification

All code changes are in examples/omphalos. The incumbent defaults and
playbook remain intact; no upstream change or commit was made. The new
mechanisms use Delphyne typed queries, executable demonstrations, Compute,
Branch, few-shot policies and shared budget streams. Verifier work reuses
the existing bridge; campaign runs use the standard supervised launcher.

The frozen v1 campaign is reproducible through its recorded inputs and
hashes. V2 is deliberately separate in prove_continuation_v2.py and
runtime/continuation_output.py. Both harnesses can use it programmatically,
or append `prove_continuation_v2` to a future experiment's ExecutionContext:

```python
from dataclasses import replace
context = dp.workspace_execution_context(__file__)
context = replace(context, modules=(*context.modules, "prove_continuation_v2"))
# Use policy="continuation_policy_v2" with the existing S/C/R strategy flags.
# A new paid benchmark requires its own bounded manifest and registration.
```

The shared workspace configuration and measured v1 policy were not changed
by the post-campaign adapter correction. Upstream suggestion only: preserve
message boundaries when interpreting structured Responses output; do not
blindly concatenate multiple final messages into one JSON document.

Omphalos make test passed; the original nine mechanism tests include live
Rocq and executable demonstration checks. V2 adds four focused tests.
Touched-file pinned Pyright 1.1.406 and Ruff passed. Root make pyright retains
the 17 existing why3py.simple-related errors, after core checking passes.
Repricing passed; old recorded-price discrepancies were not rewritten.
Generation receipts reconcile to $3.364201; remaining authorization was not
used to add variants, seeds or repaired-arm reruns. Changes are staged and
uncommitted. Further corrected-mechanism benchmarking remains open in #122;
response-boundary transport work is #125, recovery evidence remains #123.
