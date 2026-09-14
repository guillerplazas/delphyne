# Decision: stop both contenders; retain the evidence and accounting improvements

The registered comparison is complete. Neither contender passes the practical
validation gate, so **no seed-1 follow-up or fresh control was purchased**.
No prover default or frozen book changed. This rejects these configurations
as the next improvement under the agreed gate; it does not establish that
either mechanism could never help another program.

**New experimental charges: $3.61359998; unused ceiling: $26.38640002.**
All 2,156 receipts are settled. There were 160 new cells, zero platform
failures, zero administrative censoring, zero retries, and zero new writing,
adaptation, embedding or paid diagnostic calls. Training spent $1.74751532
of its $8 allocation; validation spent $1.86608466 of $8. Follow-up's $8 and
the $6 contingency remain unused. Codex-session charges are unavailable and
are not represented by this ledger.

The 80 historical control cells were reused across both comparisons, not
repurchased or counted as new spending. Each new panel contains all 40
registered problems at seed 0. ValidationX remains repeatedly reused
development data. There is no fresh confirmation panel here.

## Coverage and cost together

| Validation configuration | Qualified solves | Total cost | Cost per qualified solve | Follow-up gate |
|---|---:|---:|---:|---|
| Historical current program, fixed book | 27/40 | $0.667228 | $0.024712 | Reference |
| A: enforced output allowance 4096 | 26/40 | $1.128138 | $0.043390 | Fails |
| B: existing corrected structured continuation | 23/40 | $0.737946 | $0.032085 | Fails |

A costs 69.1% more and solves one fewer problem. B costs 10.6% more and
solves four fewer. Neither meets gain >=1 at cost ratio <=1.25, or loss <=1
at ratio <=0.90. The optional final 80-cell retention gate was not reached.

Coverage inference uses the registered two-sided p<.10 / 90% interval
convention, with theorem-family clustering and Holm correction for the two
initial coverage claims. A's unadjusted/adjusted p-values are 1.0/1.0; B's
are .21875/.4375. Descriptive coverage-difference intervals are [-7.5, 0]
percentage points for A and [-20, 0] for B. Neither has statistical support
for a coverage improvement. These bootstrap intervals are not a substitute
for the evaluator's conservative exclusion bound or a fresh confirmation.

A's cost ratio is 1.691, with descriptive 90% interval [1.459, 1.961];
B's is 1.106, interval [0.953, 1.292]. The paired cost p-values are about
.00007 and .273 respectively. Cost inference is secondary and conditional
on the paired-sign assumptions; historical controls limit causal claims.
Full registered statistics remain in `reports/`, including all failures,
cap crossings, paired cost differences and uncertainty.

## What the expenditures resolved

1. **More admissible requests did not restore useful coverage here.** A
   demonstrably changes dispatch: across its 80 cells, 227 requests fit the
   smaller bound while their shadow 32768-output bound would fail in the
   observed state. Of these, 152 were followed by an executed proof check.
   Exposure occurred in 11 training and 15 validation cells. This is an
   observed-state reservation comparison, not a counterfactual replay of
   the historical controller's whole trajectory.

   A's training result was 30/40 versus 28/40 at 47.6% greater cost. Both
   extra solves (`amc12_2000_p1`, `imo_1968_p5_1`) were unexposed to the
   measured admission effect. Validation had no additional solves and lost
   `aime_1991_p9`. Only five of the 26 exposed cells solved, and those five
   were already solved by the historical controls. Thus money-denied paths
   cannot be relabeled as recoverable model capability on this evidence.
   There were two truncated A responses across 1,133 requests; truncation
   is recorded rather than silently retried.

   Validation input volume rose from 5.88M to 11.27M tokens. Cache fractions
   were similar: 75.9% for the reference and 74.9% for A. At the registered
   tariff without cache discounts, the same recorded tokens cost $1.469747
   versus $2.646722. A's greater cost therefore persists in this sensitivity
   analysis. Repricing does not simulate another admission policy or
   redefine which historical solves qualify.

2. **The corrected interface reaches real cases, but that does not establish
   a better prover.** B dispatched structured requests that reached assembled
   proof checks in 31 training and 30 validation cells. The already existing
   v2 parser selected the final message on 32 training and 26 validation
   responses. These 58 response events are mechanism observations, not
   58 independent benchmark problems. The repair was reused, not rewritten.

   B's training coverage was 25/40 versus 28/40. Validation gained
   `amc12_2001_p21` but lost five control solves: `aime_1984_p7`,
   `aime_1991_p9`, `amc12_2000_p12`, `amc12a_2008_p4`, and
   `induction_prod1p1onk3le3m1onn`. Its validation cache fraction was 75.4%;
   same-token cost without discounts is $1.712665. Both arms advanced from
   training because their registered gate required correctness/exposure,
   not an early favorable effect or p-value. The validation spending tested
   that remaining uncertainty; neither earns further spending under the gate.

3. **Evidence integrity improved independently of those negative comparisons.**
   The new opt-in reflection contract carries the exact terminal checker
   input, accepted proof, recorded assistance flag and source hashes. All
   33 permitted successful training sources produced bound receipts. The
   accepted `amc12_2000_p6` proof verifies unaided; its recorded proposal
   fails unaided. Legacy outcomes already included the accepted proof: the
   improvement is explicit terminal provenance, not recovery of a wholly
   absent answer. Derived script differences are labeled as such.

   Curator and reducer strategies carry explicit source bindings through
   the existing verification gate via Compute. The invalid `have` rewrite
   of the training square-nonnegativity example is replaced by the verified
   `assert` form, and that binding survives reduction. Required sources
   must be bound or explicitly dropped. Individual checker limits and
   verdicts are preserved; these contracts do not claim to verify unbound
   prose. Multi-episode reflection overrides require explicit future receipt
   binding and are rejected by v2 rather than silently misattributed.

   These are functional correctness improvements. No new book was created,
   and no claim of downstream ACE coverage benefit follows from these tests.

## Retained implementation and next priority

Keep the opt-in evidence contracts, lazy partition access, strict campaign
allowlist, atomic billing-error stop, and exact transport/controller replay
records. Keep A and B available as reproducible experimental configurations;
do not promote them or increase allowances in the default prover.

The next resource-control work should begin offline with repeated state
inspection and ineffective proof transitions, and with the remaining
current-versus-earlier program regression. Extra dispatch capacity alone is
not the leading coverage remedy supported by this campaign. Any further
paid contender, altered gate, new book or seed would need a new agreed plan;
the remaining ceiling is not an instruction to keep spending.

Useful upstream suggestions, not implemented: expose transport-state cache
hooks for opaque reasoning references and admission estimates in Delphyne;
provide a typed Compute-cost interface so domain policies can account for
composite verifier operations without local result-shape conventions.

## Verification, provenance and reproduction

- 80 historical controls replayed without HTTP at their observed request
  counts. This establishes active-query compatibility, not exact historical
  terminal admission: those archives lack the newer transport snapshots.
- All 160 new cells replayed without HTTP, including saved transport state,
  resulting proof, spending and the terminal bounded controller.
- 31 distinct scoped tests passed, including real Rocq, payload/reservation
  consistency, uncertain-charge stops, refusal/multi-message parsing,
  source-witness verification, query delivery and receipt-hash pinning.
- Changed-code and adaptation Pyright checks have zero errors (installed
  version 1.1.409). The separately scoped `find_invariants` check still has
  17 pre-existing why3py-related errors; no upstream code was modified.
  Scoped Ruff and source whitespace checks passed. Tool logs retain their
  original trailing blank lines. Canonical instruction symlinks were checked
  directly; aggregate suites, repricing and memory-index checks were excluded.
- The original 399-file source/input seal was verified after execution.
  Raw new caches, results, transport snapshots and final receipts have a
  separate output inventory. Frozen measurements were not rewritten.
- The strict guard blocked an eager legacy partition read before data was
  returned; imports were made lazy. Incidental legacy outcome comments in
  source were excluded from analysis. Closed partitions/caches, testX,
  protected challenge evidence and the mixed memory index stayed unopened.
- Fresh runs share the pinned 24-worker/32-slot runtime and tariff. Historical
  runtime/opaque admission state is not recreated by query replay. Seed labels
  identify separate executions rather than a provider seed guarantee.

`RESULTS.md` is generated by the sealed campaign runner. `cells.csv`,
`requests.csv`, `mechanism_summary.json`, `output_inventory.json`, and
`export_verification.json` come from the offline reporting helper written
after collection; it does not select arms or change registered gates:

```sh
python -m tools.reports.resource_completion_results
```

Both harnesses run it from `examples/omphalos/`. Implementation and review
artifacts are staged and uncommitted; raw local measurements remain available
at their recorded paths.
