# ACE capacity follow-up — completed 2026-09-12

The evidence supports **a mixture of solver ability, finite search allowance,
imperfect training evidence, and playbook-selection effects**. It does not
establish that ACE has reached Luna's intrinsic capacity limit. Terra solves
more problems, and benefits much more from additional money on the selected
hard cases, but the full validation crossover does **not** show that a
stronger solver receives a larger ACE benefit from the same book.

All authorized experiments completed. Follow-up spend was **$23.25562298**;
the two studies together spent **$62.14069790**, leaving **$12.85930210** of
the shared $75 ceiling. There are no outstanding receipts or administratively
censored cells. One API rejection is retained as a platform failure. The
flagship defaults remain unchanged. New implementation and reports are
staged for review, without a new commit.

## What was compared

The preceding [attribution study](../ace_attribution_20260912/RESULTS.md)
identified the pre-ACE lineage, controlled the non-ACE changes, and measured
both trainX and validationX. Its historical code, frozen outputs and numerical
verdicts are preserved. This follow-up addresses the remaining confounds:

| Component | Registered observations | New executions |
|---|---:|---:|
| Validation solver × book crossover | 2 solvers × 3 books × 40 = 240 | 64; 176 compatible references reused |
| Reflector comparison | 40 identical Luna-source inputs × 2 | 80 |
| Curator comparison | 40 identical Luna-source inputs × 2 | 80 |
| Reducer comparison | 10 Luna-source + 10 Terra-source inputs × 2 | 40 |
| Mechanism panel | 8 trainX problems × 5 profiles × 2 solvers | 80 |
| Money continuation | 32 eligible paths | 18; 14 already-solved paths carried |
| Broader-search continuation | The same 32 paths | 11; 20 solved and 1 failed paths carried |

That is **173 new proof execution records and 200 role jobs**, plus 35
continuation observations carried without re-running. Each complete X panel
contains **40 problems, seed 0**. The eight-case panel is deliberately selected
for mechanisms and is not a representative coverage estimate. It does not
replace either full 40-problem panel. There are no extra seeds, new model
families, fresh generator curricula, or post-hoc paid rescue runs.

Both solvers use medium reasoning, the Responses API, the same tools and
examples, a 32,768-token output limit, and the same verifier-operation limits.
Luna's initial proof allowance is $0.10 and Terra's is $1.00, reflecting the
registered tenfold tariff difference. Actual price, token usage, cache shares
and uncached sensitivity are reported separately. Equal nominal dollars
would impose different inference allowances and answer a different question.

The frozen [protocol](protocol.json) specifies a meaningful effect of five
percentage points, two-sided p<0.10 and 90% intervals. Family-clustered
comparisons retain every expected problem and platform failure. Percentile
bootstrap intervals are descriptive: boundary intervals excluding zero do
not override an inconclusive exact paired test. Zero observed discordances
are not evidence of equivalence. Only the two book-author contrasts receive
the preregistered Holm adjustment; the diagnostic comparisons are exploratory.

## Complete validation crossover

Solves qualify at actual total cell cost ≤$0.10 for Luna or ≤$1 for Terra.
All observed successful cells qualify under their own model's allowance.
Costs below include the unsuccessful cells as well.

| Solver | Book | Solves/40 | Total cost | Cost/solve |
|---|---|---:|---:|---:|
| Luna | None | 24 | $0.776512 | $0.032355 |
| Luna | Luna | 27 | $0.667228 | $0.024712 |
| Luna | Terra | 24 | $0.734194 | $0.030591 |
| Terra | None | 29 | $6.610626 | $0.227953 |
| Terra | Luna | 29 | $6.852274 | $0.236285 |
| Terra | Terra | 30 | $6.451344 | $0.215045 |

The primary comparison fixes the Luna book across solvers:

`(Terra + Luna book − Terra no book) − (Luna + Luna book − Luna no book)`

It is **−7.5 percentage points**, descriptive 90% CI **[−17.5, 0]**, exact
p=**0.375**. The observed direction contradicts the simple prediction that
moving to Terra must unlock a larger ACE increment. It does not prove that
the increment is truly negative. Using Terra's book instead gives +2.5
points, CI [−7.5, +12.5], p=1.0.

Changing book author costs Luna three net solves: one gain
(`amc12_2001_p21`) and four losses (`aime_1984_p7`, `aime_1991_p9`,
`amc12a_2008_p4`, `mathd_numbertheory_64`). The effect is −7.5 points,
CI [−17.5, +2.5], raw p=.375, Holm p=.75. Cost rises 10.04%, cost-ratio
CI [0.950, 1.282]. For Terra, its own book adds only `amc12_2001_p21`
relative to the Luna book: +2.5 points, CI [0, +7.5], Holm p=1.0;
cost ratio 0.941, CI [0.862, 1.024]. There is no supported general advantage
to Terra-authored context in this crossover.

Luna's own book versus no book retains the earlier practical result:
three gains, no losses, 14.07% lower total cost. Coverage p=.25 remains
inconclusive; the paired cost test is p=.049, with cost-ratio CI
[0.746, 0.966]. Terra's own book gains two and loses one relative to no
book, at 2.41% lower cost; neither coverage nor cost is statistically
supported. The complete [comparison JSON](crossover_report.json) includes
all gains/losses, paired cost differences and uncertainty.

Historical controls limit this comparison: 176 records predate the 64 new
swaps. Matching prompts, model/options, books, budgets and source hashes
removes known implementation differences; it cannot remove service-time
variation or make sampling deterministic.

## Pricing changes the interpretation of “budget solves”

At a common **$0.10 actual final-cost threshold**, observed qualifying counts
are Luna **24/27/24** and Terra **21/20/20**, for none/Luna-book/Terra-book.
Those are post-hoc qualifications of measured trajectories, not runs under
new $0.10 Terra admission policies.

Under **Luna-rate repricing of Terra's actual tokens**, Terra's three total
costs become **$0.661063 / $0.685227 / $0.645134**, with **29/29/30** solves.
Its higher coverage therefore does not require more total dollars at the
same tariff on this panel. The actual tariff reverses its budget ranking.
This supports the user's concern about model-price comparisons; it does
not imply those lower Terra prices are available.

Cache sensitivity is material. Luna no-book/own-book uncached totals are
**$1.448678 / $1.469747**: the actual 14.07% saving becomes a **1.45% cost
increase**. Terra no-book/own-book uncached totals are **$15.350324 /
$16.657220**, an **8.51% increase**. ACE's repeated context benefits from
cached input pricing, while longer context remains expensive without that
discount. Coverage and actual charged costs remain valid measured outcomes;
the uncached numbers describe a pricing counterfactual, not a new experiment.
See [pricing sensitivity](pricing_sensitivity.json) and the
[standalone figure](capacity_comparison.pdf).

## Controlled fixes and selected hard cases

Profiles isolate changes as follows; all other settings are shared:

| Profile | Book | Feedback |
|---|---|---|
| A | None | Original |
| B | Original Terra book | Original |
| C | None | Version 2 goal visibility |
| D | Original Terra book | Version 2 goal visibility |
| E | Terra book with one source-verified snippet replacement | Version 2 |

The fixed training panel is `mathd_numbertheory_48`, `imo_1967_p3`,
`mathd_algebra_28`, `amc12b_2002_p11`, `amc12a_2020_p13`,
`mathd_numbertheory_629`, `algebra_amgm_sum1toneqn_prod1tonleq1`, and
`aime_1988_p8`.

| Solver | A | B | C | D | E |
|---|---:|---:|---:|---:|---:|
| Luna solves/8 | 3 | 3 | 4 | 3 | 3 |
| Luna total $ | .261377 | .196351 | .217615 | .197459 | .209094 |
| Terra solves/8 | 3 | 3 | 4 | 6 | 3 |
| Terra total $ | 1.981883 | 1.919756 | 1.773286 | 1.562186 | 1.970293 |

**The conspicuous Terra D result is not a demonstrated feedback effect.**
All 32 paired A/C and B/D first requests are identical; 25 first replies
differ. The added goal-visibility code never triggers in D. Its three gains
therefore cannot be attributed to additional information from that code.
Even its exploratory coverage p=.25 does not support a general gain.
The A/C gains also occur on cases without exposure to the new feedback.
Seed 0 controls the registered experiment configuration/order; it does not
guarantee identical Responses sampling. The
[exposure audit](causal_exposure_audit.json) makes this distinction per case.

There are three distinct live goal-visibility exposures across the selected
paths: Luna E on `mathd_numbertheory_48`, Terra C on AM–GM, and Terra E on
`mathd_numbertheory_629` during money continuation. All three reveal actual
unfocused obligations, including a missing `S b = 4` branch, an AM–GM
successor goal and two unfinished contradictions. All eventually solve,
but the experiment does not identify their counterfactual outcome without
the additional view. Replayed/carried appearances in
[feedback exposure](feedback_exposure_v2.json) are not new exposures.

The snippet correction changes exactly one example in the original Terra
book. It preserves every other bullet. Both models solve its source problem,
`mathd_algebra_28`, in every A–E profile. Luna D/E ties at 3/8; Terra D/E
falls from 6/8 to 3/8 (p=.25). The three losses are elsewhere, so this is
not evidence that the verified replacement is wrong or that the invalid
snippet was responsible for prior failures. It is evidence that a local
correctness repair does not automatically yield a coverage improvement.

## Exact continuations separate search limits from fresh attempts

Only C and E continue. Level 1 doubles money to $0.20/$2 while keeping
64 requests and 300 verifier seconds. Level 2 keeps those monetary limits
and raises requests to 128 and verifier seconds to 600. The operation limit
remains 60 seconds/512 RPCs with the same view bounds. The prompt continues
to advertise the original turn allowance, preserving the paid prefix.
Solved and failed paths are carried, never restarted. Costs below include
the prefix once; [cost conservation](prefix_cost_conservation.json) reconciles
that sum with full-path cache usage.

| Solver/profile | Initial solves; cost | More money | More requests/verifier |
|---|---|---|---|
| Luna C, no book | 4/8; $.217615 | 4/8; $.467413 | 4/8; $.512939 |
| Luna E, corrected book | 3/8; $.209094 | 3/8; $.537274 | 3/8; $.558412 |
| Terra C, no book | 4/8; $1.773286 | 6/8; $3.899886 | 6/8; $4.257558 |
| Terra E, corrected book | 3/8; $1.970293 | 7/8; $3.935691 | 7/8; $3.935691 |

Money allows Terra C to recover AM–GM and `mathd_numbertheory_629`;
Terra E additionally recovers `amc12b_2002_p11` and `amc12a_2020_p13`.
Terra E gains four of eight on continuation, exact p=.125; this is an
important observed mechanism result, not confirmatory statistical support.
The corrected-book effect at increased money is −1/8 for Luna and +1/8 for
Terra: interaction **+25 points**, descriptive CI [0, +50], p=.5. That is
a promising small-panel pattern, not a supported general ACE-by-capacity
interaction. The one Terra E advantage over C is `amc12a_2020_p13`.

Increasing request/verifier allowances adds **zero solves**. Initially all
45 unsolved A–E records stop on money admission. At level 1, the 12 remaining
paths comprise seven money stops, four stops with no denied budget item
(the 64-turn limit), and one platform failure. At level 2, all **11 ordinary
unsolved paths stop on money**; the twelfth is the carried platform failure.
None ends by exhausting the 600 verifier seconds. Consequently this is not
an uncensored test of unlimited reasoning ability.

The terminal records show substantial remaining nominal money because
admission reserves an entire possible next response and transport input
bound. For example, Luna's AM–GM no-book path has $.085742 remaining but
the next estimate is $.086368; Terra's unsolved Rpower no-book path has
$.798745 remaining but requires an estimated $.813446. These are reproduced
decisions, not billing overshoots. Doubling verifier time cannot change a
money-denied next request. Raising money without an explicit bound would
not be an appropriate way to assert an intrinsic model ceiling.

## What the persistent failures actually do

The [case appendix](CASE_APPENDIX.md) lists every diagnostic path and every
failed or discordant validation observation. The underlying JSON retains
every check, model reply and final admission estimate. Representative
mechanisms are:

* **AM–GM, Luna:** the C path repeatedly submits only `intros n a Ha Hsum.`
  and leaves the actual product bound untouched. It accumulates 54
  incomplete-proof errors and 57 repeated-error attempts over 79 model
  completions. E instead spends much of its history asking arithmetic
  automation to prove a mathematical step it has not established. The
  missing step is visible; hidden goals do not explain these trajectories.
* **`imo_1967_p3`, both solvers:** incomplete product-divisibility induction
  persists. Terra C ends with an existential multiplier for the successor
  product after 86 completions and 57 incomplete-proof errors. Additional
  turns repeat a partial argument; the final request remains money-denied.
  This suggests a difficult proof-planning barrier under this policy,
  without identifying an unrestricted model limit.
* **`mathd_numbertheory_629`, Luna E:** 16 prover-crash-labelled checks are
  followed by additional work, so those labels are not 16 platform failures.
  Its last finite split tries `subst m; lia` while an opaque `Nat.lcm`
  equation still carries the needed contradiction. Luna C solves the same
  theorem, and Terra C/E recover with continuation: the task is not simply
  beyond Luna under every context.
* **`amc12a_2020_p13`:** Terra C correctly reduces the Rpower equation using
  logarithms and reaches the polynomial identity, then fails on a cast
  normalization/positivity subgoal involving `INR 2`. Terra E solves with
  more money. Luna paths spend requests on syntax, unavailable names and
  rational normalization. Here the distinction between mathematical
  reduction and finishing a formal library argument matters.
* **`amc12b_2002_p11`, Luna:** it reaches the correct small `prime 17`
  endpoint but leaves a coprimality/focus obligation unfinished. This is a
  concrete formal proof-completion problem, not a missing informal answer.
* **API rejection:** Luna E `imo_1967_p3` level 1 receives HTTP 400
  `invalid_prompt` after 31 completed requests. Its $.05478874 full prefix
  is retained, no retry is made, and the failure carries into level 2.
  The complete batch checkpoint and exception hash are preserved in
  [supervised completion](supervised_completion_01.json).

## Playbook creation: stronger is not uniformly more faithful

The role comparison fixes each input, separating writer behavior from a
stronger generator's better training trajectory. It is **not** a new mixed
model adaptation run and does not measure the downstream value of these
new role outputs. The original all-Luna/all-Terra preparation comparison
remains in the preceding report.

| Role | Jobs/model | Luna requests; cost | Terra requests; cost |
|---|---:|---:|---:|
| Reflector | 40 | 41; $.151298 | 40; $1.663716 |
| Curator | 40 | 40; $.040996 | 40; $.388272 |
| Reducer | 20 | 20; $.025360 | 20; $.249314 |

All 200 jobs ultimately produce valid structured output. Luna's one
reflector resampling is caused by `bullet_tags: null` where a list is
required; it is included in cost. Luna emits one unbound neutral tag
`rocq-00001` when the input book is empty. Terra emits no unbound tags in
these jobs. Luna produces 80 curator operations versus Terra's 69, and
52 reducer operations versus 55. These are output counts, not automatic
quality scores.

Three source-level findings explain why a single quality ranking is unsafe:

1. **Terra reintroduces invalid syntax on an identical reducer input.**
   Its new first-batch output invents `have Hsq : ... := Rle_0_sqr _`, just
   as the original Terra adaptation did. The trainX source witness rejects
   this exact new example; the preserved `assert ... by apply Rle_0_sqr`
   verifies. Luna avoids that syntax on the same proposals. The opt-in gate
   checks the actual reducer delta before merging and preserves its bound
   source snippet when replacement verification fails. This certifies the
   recorded bindings and source environment, not arbitrary future use.
2. **Luna can confuse a proposed ending with the verified ending.**
   On `amc12_2000_p6`, the frozen trajectory ends in code containing
   enumeration, `omega` and `norm_num`. The verifier had actually stopped
   earlier and completed the accepted prefix with `nia`. Luna credits the
   unexecuted `norm_num` ending; Terra describes the `nia` ending correctly.
   A source witness verifies `nia` and rejects `norm_num in *`. The input's
   trajectory does not include the final verified receipt, making this
   partly an evidence-construction problem. Seven of 33 successful source
   histories have a final verified tactic absent from their last submitted
   text; that textual check is an audit flag, not proof of seven identical
   semantic errors. See [terminal evidence](creator_terminal_evidence.json).
3. **Compression makes different selection choices.** On the first
   Terra-source reducer batch, Terra keeps completed squares, symbolic
   induction and natural subtraction; Luna keeps completed squares,
   integer-divisibility workflow and symbolic induction. Both drop or
   combine useful material under the same three-bullet allowance. On the
   Luna-source batch, both retain the direct square/rewrite guidance, but
   differ on induction versus subtraction advice. More elaborate reasoning
   does not ensure better selection for later tasks.

The reference audit deliberately separates mentions from recommendations.
All missing-name curator mentions in this scan are warnings or a placeholder,
not positive recommendations. Checking only a reducer's first source file
also falsely flags logarithm and square-root names originating in another
member of its four-problem batch. The additional 57 source checks resolve
those cases; the two remaining unavailable reducer mentions are explicit
warnings about `norm_num` and `exact_mod_cast`. Local binders and comments
are not global lemmas. `Locate` establishes availability only and is not a
general test of tactics or applicability. The invalid Terra `have` example
passes a lemma-existence audit because `Rle_0_sqr` itself exists.

The [complete creator appendix](CREATOR_APPENDIX.md) contains both outputs
for all 100 frozen inputs. [Creator quality](creator_quality.json),
[contextual checks](creator_contextual_audit.json), and the two explicit
snippet witnesses retain the evidence behind these judgments. Neither
output length nor available-name counts justify declaring Terra or Luna
uniformly superior at playbook construction.

## Interpretation and retained work

The simple claim “ACE is weak because Luna cannot use it, and Terra will
unlock it” is **not supported by the full crossover**. A narrower claim is
supported descriptively: Terra completes more of these hard formal proofs
when its search is allowed to continue, while Luna's sampled paths often
repeat partial or ineffective proofs. The eight-case continuation suggests
that useful ACE gains may depend jointly on solver and allowance, but its
one-case final ACE advantage and p=.5 interaction are too uncertain to
generalize.

The preceding report's comparison with the ACE paper remains applicable:
different tasks, models, adaptation and budget settings prevent a direct
numerical reproduction claim. Paper-level average gains do not identify
which bottleneck dominates this Rocq pipeline. The present evidence gives
specific engineering causes rather than attributing the entire gap to one
model's capacity.

Hints **#121, #128 and #129** now have implemented opt-in mechanisms and
recorded evaluations: exact transport/admission replay, bounded unfocused
goal visibility, and source-bound snippet preservation. Their investigations
are closed with these limits recorded; none changes the flagship default.
New follow-ups are indexed only in HINTS: **#130**, include the terminal
verified proof and assistance receipt in reflector evidence; **#131**, assess
the cost of conservative monetary admission bounds. These are bounded
research directions, not authorization for further API spending. The
remaining ceiling was deliberately left unused.

## Verification, provenance and limits

* The prior checkpoint requested by Guille remains commit `23329b09`, with
  Guille's sign-off. This follow-up is staged and uncommitted.
* The 762-file execution seal and all 176 reference hashes verify. New raw
  outputs, original books and prior numerical measurements are untouched.
  The prior source is archived because opt-in runtime additions correctly
  make its old working-tree seal fail.
* Exact HTTP-disabled/Rocq-disabled replay passes for all **372 completed
  new execution records**. The one failed record replays its entire cached
  prefix to the exact rejected dispatch barrier. All **373** recorded
  estimate/admission/terminal sequences match. The remote rejection itself
  is not reissued. The separate 80 historical observed-prefix checks do
  not claim to reconstruct unrecorded historical terminal decisions.
* **49 scoped tests passed** before paid dispatch, including real Rocq
  source checks and a mock-HTTP end-to-end continuation/replay test.
  Pyright 1.1.406 and Ruff pass on the follow-up files. Root `make pyright`
  still reports the same 17 pre-existing `find_invariants/why3py` errors.
  The canonical instruction/symlink check passes. Global tests and repricing
  that eagerly access closed partitions are excluded.
* The initial derived failed-cell verifier-time field omitted the Compute
  charge, although cost and terminal evidence were correct. The authoritative
  reports use `_v2`; [analysis correction](analysis_correction_01.json)
  preserves the original hashes and exact correction. Outcomes, costs and
  statistical comparisons did not change.
* Only trainX/validationX records feed the numerical analysis. ValidationX
  is development data. No new closed-set evaluation was performed. Earlier
  closure incidents and the maintenance-search exposure are explicitly
  documented in [closure correction](closure_correction.json) and
  [maintenance note](closure_maintenance_note.json); this is not a claim of
  zero historical-data exposure.

[ARTIFACTS.md](ARTIFACTS.md) documents exact inventories, replay commands,
local raw storage and reproduction boundaries.
