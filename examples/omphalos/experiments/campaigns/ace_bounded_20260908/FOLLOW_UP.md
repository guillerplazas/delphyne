# Budgeting win retained — 2026-09-09

Guille explicitly accepts and keeps this result as a win for Omphalos's
budgeting objective: 25/40 qualified solves for $0.6780 versus X3's 28/40
for $1.5238. Cost per qualified solve fell from $0.05442 to $0.02712
(50.2% lower), alongside the 55.5% reduction in total panel cost.
Retain the frozen money+focused configuration as a budget-oriented reference
and X3 as the coverage comparator. The earlier no-fewer-solves gate still
failed; this user decision changes the project's acceptance decision, not
the recorded statistics or the preregistration. No global defaults changed.

This follow-up analyzes already-paid validationX failures at Guille's request.
The diagnostic script makes no LLM or Rocq calls and adds no seeds or
experiment cells. The small pure Python reservation probe is synthetic.
Existing test-suite verification may run Rocq locally without paid calls. Further work must develop on trainX;
these inspected validation results remain development evidence, not a clean
confirmation set. testX and protected challenge proofs remain untouched.

## What remains expensive or unsuccessful

The fifteen unsolved cells cost $0.52669, **77.7% of validation spend**.
The 200 distinct cached proof checks contain 25 accepted, 132 rejected,
17 incomplete, 20 unknown and six resource-exhausted outcomes. Twenty-two
of the 175 failed-check records repeat the full tactic/error/prefix/goal
fingerprint within their cell. These are cache records, not invocation counts.

The last cached error on five unsolved problems is a transport/resource
error; two end in unification failure and two in an incomplete proof. The
remaining six end in arithmetic applicability, name resolution, syntax,
normal-form or type errors. A legacy `prover-crash` label does not establish
that a process died; the typed unknown/resource outcomes are more precise.

The observed differences from X3 are:

| Problem | X3 cost / qualified | Bounded cost / qualified | Last cached bounded obstacle |
|---|---:|---:|---|
| amc12_2001_p21 | $0.11157 / no | $0.01406 / yes | Accepted proof; one new qualified win |
| imo_1964_p2 | $0.02602 / yes | $0.03932 / no | `ring` cannot handle the attempted square rewrite |
| induction_prod1p1onk3le3m1onn | $0.07836 / yes | $0.03803 / no | Syntax in `field_simplify` |
| mathd_numbertheory_405 | $0.03754 / yes | $0.04122 / no | `reflexivity` leaves a unification mismatch |
| mathd_numbertheory_530 | $0.09789 / yes | $0.03860 / no | Type mismatch applying a multiplication inequality |

The four losses used 18, 12, 11 and 29 requests respectively, below the
64-request cap. Two X3 proofs previously cost more than the new runs spent;
two cost less. Therefore “just give every failure more money” is unsupported:
budget admission, proof choices and the changed feedback/query policy are
confounded in this integrated historical comparison. Extra allowance cannot
be assumed to recover a proof.

## Prioritized next improvements

1. **Fix typed verifier-limit admission before tuning budgets.** The frozen
   `grounded_search` expects `limits` to be a dictionary, but `dp.compute`
   supplies a `ToolLimits` instance. Its estimate therefore falls back to
   60 seconds even when the strategy reduces the next operation's limit.
   The synthetic probe requests seven seconds: a seven-second parent budget
   yields no result; a sixty-second parent budget admits the same zero-work
   computation. Read the actual typed limit and add a regression asserting
   that a short operation fits the remaining shared allowance. Keep the
   operation deadline, RPC cap and charge accounting intact. Three recorded
   stops are consistent with this defect: `imo_1984_p6` has 57.77 seconds
   left, `mathd_numbertheory_37` 43.25, and `mathd_numbertheory_43` 34.10.
   This establishes wasted capacity, not that their proofs would succeed.
   Preserve the measured implementation and introduce the fix as a separately
   identified follow-up; do not rewrite the frozen benchmark sources.

2. **Make output allowance fit the remaining dollar budget.** Twelve stops
   are consistent with declined monetary admission: the final trace exposes
   a candidate space, request count is below 64, and verifier time remains.
   They spend roughly $0.032–$0.043 before stopping. The monetary bound
   reserves up to 32,768 output tokens on every call. In training the maximum
   actually generated was 2,126 tokens, with p95 1,423; validation's maximum
   was 2,942. These counts include reasoning. A smaller, explicit output
   allowance, or a bounded final repair allowance, could admit useful calls
   within the same ceiling. Size it on training data and check truncations
   and lost recoveries. Keep worst-case campaign reservations; empirical
   averages must never replace the hard billing bound.

3. **Log admission decisions and reserve verification before buying a proof.**
   Current stop labels are inferred from trace shape and remaining budgets;
   declined monetary/Compute requests are not explicitly exported. Record
   the budget dimension, estimate, remaining allowance, stage and decision.
   Three unsolved caches end with a paid model answer and no following
   recorded check, consistent with Compute admission declining. Admit or
   earmark the verification allowance before another proposal, so a model
   answer can always be checked. Separate cached reuse from fresh invocation
   events. Validate the audit on an offline replay before another paid pilot.

4. **Act differently on unavailable evidence.** The twenty unknown and six
   resource outcomes are not refutations of the tactics. On numbertheory_43,
   repeated `vm_compute` over `fact 942` closes the server connection; other
   tails repeatedly attempt costly arithmetic. A separate finite recovery
   policy should narrow a computation or change proof representation, instead
   of paying for another substantially identical attempt. Test this on
   training resource failures while retaining actual kernel acceptance.

5. **Repair specific syntax/type/normal-form decisions.** Extract accepted
   training examples for `field_simplify`, square normal forms, inequality
   lemma argument order and branch completion. Current grounded evidence has
   six reference examples and two structure examples, with no demonstrated
   bridge coverage. Preserve verified prefixes and check each proposed local
   transition. Do not inject these named validation problems as demonstrations.

6. **Improve adaptation reliability and pilot coverage.** Three of four role
   episodes failed YAML parsing; constrained serialization deserves an offline
   repair before further adaptation spending. The money pilot used two
   unsolved controls, so “no lost solve” could not test preservation of late
   recoveries. Advice and restart were never exercised. A future small trainX
   panel should include late known recoveries and actual target triggers,
   and predeclare a cost/coverage trade-off appropriate to budgeting. Keep
   the original historical gate outcome and avoid another broad sweep.

## Reproduction and interpretation

Run `python tools/grounded_failure_audit.py` from `examples/omphalos/` with
either harness. [failure_audit.json](failure_audit.json) records file hashes,
all fifteen unsolved cells, the five discordances and the pure reservation
probe. Last/repeated means cache insertion order. The monetary/Compute stop
labels are explicitly **inferred**, not definitive event-log diagnoses.
There is no new inferential test or confirmation claim in this follow-up.

The frozen statistics remain in [final_report.json](final_report.json).
The user acceptance decision is recorded separately in
[acceptance.json](acceptance.json). All requested runtime changes are retained;
future improvements above have not silently changed the benchmarked policy.
