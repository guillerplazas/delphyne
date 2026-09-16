# ACE role learning: implementation and measured development experiment

The implementation, frozen protocol, raw measurements and case inspection are
in [`ace_learning_20260914`](../experiments/campaigns/ace_learning_20260914/).
The four changes are available as a versioned experimental pipeline; polished
v2 and the generator defaults remain unchanged. This report distinguishes
engineering improvements, local learning yield and downstream proof results.


**The local role improvements did not establish a better end-to-end pipeline.**
The selected reflection/curation candidate gains two training solves, then
loses one validation solve while spending 6.4% less on validation inference.
It misses the preregistered practical gate; both coverage and cost differences
are statistically inconclusive. Keep polished v2 as the reference/default.

| Complete panel | Polished v2 | Candidate B | v2 inference cost | B inference cost |
| --- | ---: | ---: | ---: | ---: |
| trainX, seed 0 | 28/40 | 30/40 | $0.68593736 | $0.65546142 |
| validationX, seeds 0 and 1 | 48/80 | 47/80 | $1.52856742 | $1.43022386 |

Total new API charges: **$2.94148562 / $30**, with **1,736 settled receipts**
and zero unresolved charges. This covers 52 pilot episodes, 82 adaptation
roles and 120 new proof cells; 120 compatible historical v2 proof cells were
reused. No second candidate, extra seeds or fresh controls were added.

Validation has two winning and three losing cells, 45 shared successes and
30 shared failures. The solve-difference 90% interval is **−5 to +2.5 percentage
points**, with family-clustered p=**1.0**. The cost ratio is **0.9357**, with
90% interval **0.8654–1.0079** and paired cost p=**0.1630**. The apparent cost
saving is therefore uncertain. One theorem exchanges a win and a loss across
its two seeds; those measurements are clustered together, not counted as
independent evidence.

## Changes and pilot decisions

The campaign tested 52 new role episodes for **$0.25978644**. Historical v2
query replay supplied matched inputs and controls. All 52 episodes returned
results; raw draft and receipt rechecks used Rocq with HTTP disabled.

| Treatment | Observed comparison | Registered decision |
| --- | --- | --- |
| Action-specific schemas | Valid final decisions 6/12 → 11/12; all six malformed controls fixed, one formerly valid control now requests a tool | Excluded: failed preservation of valid controls |
| Evidence-rich independent review | Correct support **and** allowed novelty 8/12 → 11/12; four additional cases explicitly unscored | Excluded: a newly accepted duplicate was called a new operation |
| Current-book reflection and opportunity comparison | Executable raw drafts 3/9 → 6/9 over the same 12 histories; one new complete proof | Included, with semantic novelty assessed separately |
| Targeted curator guidance and executable demonstrations | Histories with executable repairs 9/12 → 12/12; rejected checks 13/24 → 3/16 | Included; no newly retained unsupported local facts found |

These are exploratory paired pilots, not independent human-labeled evaluation.
The reviewer panel is positive-heavy: all 12 scored examples have supported
local operations. Its four uncertain relevance/generalization cases remain
unscored. Thus its accuracy is not an estimate of general false-acceptance
risk. The negative assertion demonstration and live tests cover an executed
but unproved `assert False`; they are not additional paid evaluation cases.

The schema gate deserves precision. On the AM-GM history, the new response
called another tool while tools were still advertised; the fixed final-query
pilot requires a final decision, so this counts as a regression. This does not
show that the action schema itself is intrinsically worse. Changing the
fixture or relaxing the gate after seeing that answer would invalidate the
registered comparison, so neither was done.

The curation strata were clarified before dispatch: only five old episodes
had **no** executable receipt. The six failure histories therefore mean six
histories containing an actual rejected check; six other histories had only
executable checks. Every case records its stratum and original execution.

See [pilot registration](../experiments/campaigns/ace_learning_20260914/pilot_registration.json),
[adjudication](../experiments/campaigns/ace_learning_20260914/pilot_adjudication.json),
and [frozen decisions](../experiments/campaigns/ace_learning_20260914/pilot_decisions.json).
Candidate A had no passing schema/review treatment and was skipped. Candidate
B contains the passing reflection/curation package, with v2 independent review
and legacy final-plan validation. No post-pilot prompt adjustment was made.

## What the actual role logs show

**Reflector.** The old raw `mathd_numbertheory_48` draft tried
`Nat.le_of_not_gt` and rejected. The new raw draft establishes a multiplication
bound, normalizes `Nat.pow`, and discharges the original local obligation.
For accepted-source `amc12a_2016_p2`, new reflection extracts a complete
natural-power normalization/injectivity proof that passes the kernel; old
reflection abstained. New reflection also avoids the already-covered AM-GM
and `Nat.lcm` proposals, whose old raw drafts reject.

The remaining errors are concrete. In `aime_1990_p4`, the new snippet refers
to `x` before its chosen source context introduces it. In `amc12_2000_p1`, a
second proposed disequality repair has no focused goal. In
`induction_pord1p1on2powklt5on2`, a semicolon chain fails. Current-book prompting
also still chooses the logarithm repair for `amc12a_2020_p13`, overlooking the
known faulty closed-cast recipe. Execution improves without guaranteeing good
opportunity selection or correct source-context selection.

**Curator.** Three previously unsuccessful repair histories now yield checked
local facts. `imo_1983_p6` uses an explicit product with `Rle_0_sqr`, avoiding
the `pow`/`Rsqr` unification mismatch. `amc12_2000_p6` checks `prime_divisors`
and uses the nested disjunction pattern `[H | [H | H]]`; the original local
obligation closes. `aime_1990_p4` checks only the first reciprocal cancellation
and retains that narrow example. The old attempts repeatedly invoked the
unavailable `ring_nf` after a failed full denominator transformation.

Failures persist under the better guidance. The induction curator first
repeats an incompatible bullet before switching to bracketed branches.
`mathd_algebra_206` repeats missing introductions and later uses nonexistent
rule alias `b27`; validation feedback recovers a valid final. Local aliases
must be interpreted against the current query, even when examples use other
books. The curator also sometimes treats a genuinely distinct syntax or focus
operation as an example, losing learning opportunities without inventing a
false fact. Of its 13 new executable receipts, one is `Check prime_divisors.`;
only the other 12 count as mathematical repair receipts.

**Independent reviewer.** Original events and obligation observations fix
several false negatives: the product-bound review actually has a second
receipt closing the original obligation; the `ltac:(lia)` review has an
original rejected `(by lia)` event; the induction review has a recorded
wrong-bullet failure. The old reviewer lacked that evidence or conflated an
open enclosing theorem with a failed local proof.

However, on `imo_1963_p5`, the new reviewer recognizes the verified local
trigonometric repair but calls it `new_operation`, although the existing
orientation rule already covers it. The old verdict was unsupported; the new
verdict overcorrects novelty. This is why separating support and novelty in
the output schema does not, by itself, solve the semantic decision problem.

**Final-plan generation.** Action-specific types eliminate the irrelevant
fields responsible for the six malformed historical finals. They do not
establish semantic validity: one newly valid logarithm update cites a rejected
alternative that is not clearly an instance of the old advice. Another final
still mistakes `executed_open` for lack of a successful local repair. Parsing,
execution, relevance, novelty and downstream transfer remain separate stages.

All these observations have source-bound receipts and outputs in
[pilot evidence](../experiments/campaigns/ace_learning_20260914/analysis/pilots.json),
[reflection checks](../experiments/campaigns/ace_learning_20260914/analysis/reflection_checks/),
and [curation checks](../experiments/campaigns/ace_learning_20260914/analysis/curation_checks/).
The checks execute raw recorded drafts without repairing them first.

## Training result and mechanism evidence

The complete trainX panel improves from **28/40 to 30/40** qualified solves,
with inference cost **$0.68593736 → $0.65546142** (4.44% less). Cost per
qualified solve falls from $0.02449776 to $0.02184871. There are four wins,
two losses, 26 shared successes and eight shared failures. This passes the
registered training expansion rule, so B alone was selected before new
validation dispatch.

The family-paired solve p-value is **0.6875**, with a descriptive 90% coverage
difference interval of **−5 to +15 percentage points**. The cost-ratio interval
is **0.824–1.098**, with paired cost p=0.6067. These results support a bounded
validation run, not a claim of established improvement.

| Training disagreement | Actual log evidence |
| --- | --- |
| Win: `amc12a_2016_p2` | 17 → 3 requests; $0.029603 → $0.002630. v2 expands/rewrites into a shape that no longer matches `Nat.pow_mul_r`; B normalizes common-base powers and applies `Nat.pow_inj_r`. This closely matches new advice, on an adaptation source theorem. |
| Win: `amc12_2000_p1` | 19 → 6 requests. Both encounter reordered-sum unification; B switches to `pose proof (Hsort ... ltac:(nia) ... )` and arithmetic, while v2 ends with the failing direct `apply`. Consistent with the new inline-proof-argument operation. |
| Win: `imo_1963_p5` | 15 → 10 requests. v2 ends after an unavailable `PI_pos` and a final search; B uses `PI_RGT_0` and completes the trig calculation. No new trig rule was retained, so this is not evidence that the new trig reviewer caused the win. |
| Win: `imo_1968_p5_1` | 18 → 14 requests. v2 ends after applying `field` to a non-equality sqrt side condition and querying a lemma; B uses `sqrt_square`, `pow2_sqrt` and `sqrt_pow2`. No isolated added-rule attribution is established. |
| Loss: `amc12_2000_p6` | 14 → 32 requests. v2 finishes a bounded-prime case proof with assistance; B pursues a generic odd-prime argument and tries to apply `Z.even r = false` as a proof of `False`. |
| Loss: `aime_1984_p1` | 13 → 15 requests. v2 derives a direct closed form for the sequence; B takes a longer sum-splitting induction and fails `ring` on unmatched natural indices inside function applications. |

The eight shared failures cover AM-GM induction, integer parity, finite-set
cardinality, recurrence/algebra, `Nat.lcm` case focus, and natural-to-real casts.
The exact final tactics and goal states for all eight appear in
[CELL_INSPECTION.md](../experiments/campaigns/ace_learning_20260914/CELL_INSPECTION.md).
In particular, `mathd_algebra_185` and `mathd_algebra_224` encounter prover
transport failures/timeouts during repeated inversion; these become feedback
and remain unsuccessful cells in the denominator. Every job produced a result;
that does **not** mean every Rocq operation succeeded.

All ten candidate training failures ultimately stop at price admission, at
actual charges around $0.034–$0.042. The next request's conservative bound,
including the unchanged 32,768-token output allowance, exceeds the remaining
budget. This is distinct from spending the full $.10 or running out of 64
requests. Late search results can therefore arrive without room for the next
proposal. This is an observed controller limitation, held fixed in this
adaptation experiment, not an excuse to remove failed cells.

A book was present in the dispatched logical model requests, but request
exposure and workflow similarity do not prove an individual rule caused a
solve. Training is also adaptation data. The two mechanism-aligned wins are
therefore useful diagnoses rather than independent evidence of transfer.

## Full adaptation: pilot gains do not transfer uniformly

The complete adaptation pass costs **$0.59601390**, versus v2's $0.45092992
(32.2% more). Both use the same 40 frozen source histories. New reflection
produces 33 drafts across 32 sources; v2 produced 29. All 40 reflectors finish.
The candidate has 27 complete and five partial curator products, versus v2's
23 complete and six partial products. All ten reducers finish in both passes.

The full curator check yield is nearly unchanged: **28 executable / 50 checks**
versus **29 / 53** in v2. The clear targeted pilot gain therefore does not imply
a comparable gain when the reflector changes the input distribution. These
counts describe execution receipts, not distinct novel mathematical facts.
Legacy schema mistakes also recur because that treatment failed its pilot
gate: malformed drop fields and misplaced failure receipts cause diagnostics;
checkpoints preserve the checked work for reduction.

The final book has **30 entries / 2,447 estimated tokens**, compared with
v2's 27 / 2,224 and the seed's 26 / 2,103. It retains four additions and 13
examples, with no updates. Eighteen retained receipt IDs recheck exactly, and
the revision chain reconstructs the frozen book
`cc04406b4014c436f8baea014cb9dc52810872321b4611e1881e00972bda7af8`.
Stored examples do not change the generator prompt. The additions are:

- Reflexive natural inequalities after `Nat.mul_1_r`, from an unsolved source:
  locally correct, but narrow and unlikely to justify much prompt space.
- Common-base natural-power normalization and exponent injectivity, from an
  accepted source: a substantial verified proof fragment, with an incorrectly
  generalized premise in the retained text.
- Inline `ltac:(lia)` proof arguments, from an accepted source: a concrete
  repair of the recorded parser error.
- Unfolding local rational definitions throughout the context before `nra`,
  from an accepted source: the source fragment completes the theorem.

The power rule says a **positive** base is enough. Actual Rocq output is
`Nat.pow_inj_r : forall a b c : nat, 1 < a -> a ^ b = a ^ c -> b = c`.
Base 1 is positive but is a counterexample to exponent injectivity. Thus a
successful proof at base 10 does not validate that generalization. This defect
was documented before the benchmark finished and the measured book was kept
unchanged; the kernel still checks every proposed theorem proof. See the
[actual lemma observation](../experiments/campaigns/ace_learning_20260914/analysis/power_rule_premise.json).

Relative to v2, the candidate also loses the nonzero-factor rule and the
logarithm-factor positivity correction, because the experiment restarts both
learners from the same seed rather than appending to v2. The faulty inherited
closed-cast recipe survives unchanged. More added text is therefore not a
superset of v2's useful advice. [Book differences](../experiments/campaigns/ace_learning_20260914/analysis/book_difference.json)
and the [role funnel](../experiments/campaigns/ace_learning_20260914/analysis/mechanism.json)
record these gains, omissions and diagnostics.

## Validation successes, failures and costs

The complete validation panel has **47/80** qualified B solves versus **48/80**
for v2. Its five discordant cells are fully inspected:

| Cell | Result | Actual sequence |
| --- | --- | --- |
| `imo_1964_p2`, seed 1 | Loss | v2 derives an explicit sum-of-squares identity with `unfold Rsqr; ring`, then `lra`; B ends with an `nra` failure after constructing related nonnegative products. 14 → 16 requests. |
| `amc12_2001_p21`, seed 1 | Loss | v2 replaces a nonexistent `omega` call with `lia`, enumerates the bounded cases and finishes; B ends with invalid `destruct ...; all: ...` syntax. 26 → 21 requests, but B costs more. |
| `mathd_numbertheory_405`, seed 1 | Win | v2's recurrence-period argument remains improperly focused; B proves shift/residue facts, explicitly distributes modulo over addition with `ltac:(lia)` side conditions, and closes. 11 → 10 requests. The inline proof-argument pattern matches added advice, but an isolated causal effect is unproved. |
| `amc12a_2008_p4`, seed 0 | Loss | B starts by falsely declaring the theorem impossible and repeats that claim through 44 requests; its 16 verifier computations are only proof checks, with no definition inspection. v2 proves the product formula in 14 requests. |
| `amc12a_2008_p4`, seed 1 | Win | B proves the product induction, establishes the denominator nonzero, and finishes in nine requests. v2 ends after 21 requests with a missing `Hd` hypothesis. |

The product failure is more than a syntax issue. B claims `Rprod 501` includes
`k=0`, producing a zero factor, and cites inherited playbook bullet
`rocq-00011`. Actual `Print Rprod` shows base value 1 and a successor step
multiplying by the **successor** index; the zero factor is absent. Both v2 seed
0 and B seed 1 have kernel-accepted proofs. The false impossibility claim is
therefore contradicted by the definition and actual successful runs. This
post-run check is preserved in
[product_definition.json](../experiments/campaigns/ace_learning_20260914/analysis/product_definition.json);
no validation-driven prompt edit or rerun followed it.

The 45 shared successes are included in the report, not merely the disagreements.
Across all B validation successes, 19 finish in one request and 16 use assisted
completion; v2 has 17 and 12 respectively. Those categories can overlap.
The 30 shared failures and all other cells retain their exact final tactics,
remaining goals, final model responses and terminal admission events in the
[complete inspection](../experiments/campaigns/ace_learning_20260914/CELL_INSPECTION.md).
Of B's 33 unsuccessful cells, 27 end at price admission and six at verifier-time
admission, versus v2's 28 and four. There are no missing or administratively
censored cells, and no failed launcher jobs. Recovered prover failures still
occur inside completed unsuccessful jobs and are included in these totals.

| New API expenditure | Dollars |
| --- | ---: |
| 52 local pilot episodes | $0.25978644 |
| Full B adaptation | $0.59601390 |
| 40 training proof cells | $0.65546142 |
| 80 validation proof cells | $1.43022386 |
| **Total** | **$2.94148562** |

Validation inference cost per qualified solve is **$0.03043029**, versus
**$0.03184515** for v2 (4.44% lower). Charging each method its adaptation plus
this panel reverses the comparison: B costs **$2.02623776 / 47 = $0.04311144**
per solve, versus v2's **$1.97949734 / 48 = $0.04123953**. Thus inference savings
have not repaid the higher preparation cost on this panel.

Input-cache sensitivity is material. Pricing the **same measured tokens** as
uncached gives validation costs **$3.3484304 for B versus $3.3559996 for v2**,
only 0.23% apart, compared with the 6.43% observed charged-cost difference.
This counterfactual is not a fresh no-cache experiment, but it shows that the
apparent saving is not robust to removing input-cache discounts. Historical
provider/cache conditions limit interpretation.

At the observed validation saving per cell, amortizing B's entire new
preparation against an already available v2 book would take approximately
**485 proof cells**; amortizing only its extra preparation over v2 would take
**119 cells**. These are descriptive extrapolations with uncertain savings,
not forecasts. Pilot and benchmark research charges and historical source
collection are reported separately from deployment-style preparation. CPU
costs are not included in API dollars. Detailed economics and paired uncertainty
are in [economics.json](../experiments/campaigns/ace_learning_20260914/analysis/economics.json)
and [metrics.json](../experiments/campaigns/ace_learning_20260914/analysis/metrics.json).

## What to carry forward

Keep the current result as an exploratory negative end-to-end comparison,
with useful local improvements. The evidence-backed next work is:

- Test strict final schemas with a preregistered final/tool boundary. The
  six fixed malformed finals and recurring full-adaptation schema errors
  justify this follow-up; the original failed gate stays failed.
- Bind reflection drafts to the exact state where variables are introduced
  and the intended obligation is focused. Add a final context check before
  handing the draft to the curator, retaining the source prefix hash.
- Evaluate support and novelty on a balanced, independently annotated panel.
  Require explicit comparison of the claimed operation and lemma premises;
  the power rule's missing `1 < a` condition is a concrete regression case.
- Investigate a bounded generator rule requiring local definition inspection
  before an impossibility claim, and a budget policy that can reserve a final
  proposal after a late search. The current definition/index mistake and
  observed conservative admission stops motivate separate future treatments.

These remain follow-ups, not post-hoc changes to the measured candidate.
They are recorded in the development-only ACE evidence append in `HINTS.md`.
Neither a null validation result nor a failed pilot gate proves an idea is
worthless; neither permits promoting the current candidate as improved.

## Measurement and reproducibility

The protocol permits up to two books, but only B qualifies here. It starts
from the original X3 seed book and adapts the same 40 source histories in the
same order as v2. The final book is hashed and reconstructed from its revision
chain, and every retained receipt is independently rechecked before proof
benchmarking. The frozen generator/controller is unchanged: Luna medium,
$.10 per problem, 64 requests, 300 verifier seconds, identical tools and
proof arguments. All 120 historical proof arguments match the new adapter;
three representative controls replay exactly with HTTP blocked.

New allocation: pilots $5, adaptation $5, training $8, validation $8,
contingency $4. Total ceiling $30, not a spending target. No paid source
regeneration, embeddings, fresh controls, automatic episode retries, or extra
seeds. Training uses trainX seed 0; selected validation uses validationX seeds
0 and 1. Historical v2 contributes 40 training and 80 validation cells.
Validation is development data after repeated use. testX and protected
challenge data are closed and excluded from new fixtures and evidence.
The initial planning pass consulted the required memory/backlog material before
identifying the stricter mixed-artifact boundary; that material is not used as
experimental evidence. The campaign entry point enforces the narrower
development-only file scope and uses only the completed v2 reference campaign.

The comparison is historical, not randomized concurrently. Source/controller
compatibility cannot prove unchanged provider behavior or cache conditions.
Actual ledger receipts are repriced from token counts; failed cells stay in
the cost/coverage denominators. Missing or administratively censored cells
prohibit a verdict. Cost uncertainty uses paired family clustering; repeated
seeds are not independent theorems. Descriptive 90% intervals and two-sided
p<.10 statistical support are reported separately from practical interest.
The practical validation gate is two extra solves at <=1.25 cost, or >=10%
savings with at most two fewer solves. No automatic default promotion follows.

Preflight: 22 new tests, 19 v2 role tests, 26 scoped coverage tests, six budget
tests, executable demonstration validation, Ruff and pinned Pyright passed.
Root `make pyright` passes the main project, then fails on 17 existing
`why3py.simple` dependency/type errors in `examples/find_invariants`, outside
the authorized edit scope. Aggregate tests/repricing that access closed data
were replaced by scoped checks. New code and commands work from both Codex
and Claude Code.

## Final checks and artifact status

All **254 new episodes** replayed exactly with HTTP disabled, reproducing the
original results and spent budgets and adding zero API calls or charges.
All 240 new/reference proof records have matching ledger and recorded-budget
costs, with complete unique panel keys. Source integrity checks pass for all
235 v2 sealed files and 344 new sealed inputs/source files. All 120 new proof
cells have exact-book exposure in captured model-dispatch requests. See
[replay verification](../experiments/campaigns/ace_learning_20260914/replays/254.json)
and [final integrity](../experiments/campaigns/ace_learning_20260914/analysis/final_integrity.json).

Implementation, demonstrations, protocol, decisions, reports and a lean evidence
bundle are staged and uncommitted. Large raw archives and the live ledger stay
in the workspace, with exported receipts and checksums. Local HINTS/PROGRESS
and the shared memory index were updated by development-only appends.
