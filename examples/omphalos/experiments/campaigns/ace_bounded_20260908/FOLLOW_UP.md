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

## Admission evidence and open work

The pure reservation probe confirms that a seven-second typed ToolLimits
operation is admitted only with sixty seconds remaining in the measured
implementation. Recorded tails with 34–58 seconds left are consistent with
that mismatch. Other monetary refusals are inferred from traces; they are
not explicit admission events and do not establish recoverable solves.

Unresolved proposals are maintained only in [HINTS](../../../HINTS.md),
#113–119: serialization, representative pilots, demonstration coverage,
resource recovery, admission events, output allowance and typed reservation.
The source diagnosis and original gate remain recorded here; no follow-up
fix was silently applied to the measured implementation.

## Reproduction and interpretation

Run `python -m tools.analysis.grounded_failure_audit` from `examples/omphalos/` with
either harness. [failure_audit.json](failure_audit.json) records file hashes,
all fifteen unsolved cells, the five discordances and the pure reservation
probe. Last/repeated means cache insertion order. The monetary/Compute stop
labels are explicitly **inferred**, not definitive event-log diagnoses.
There is no new inferential test or confirmation claim in this follow-up.

The frozen statistics remain in [final_report.json](final_report.json).
The user acceptance decision is recorded separately in
[acceptance.json](acceptance.json). All requested runtime changes are retained;
the open backlog does not change the benchmarked policy.
