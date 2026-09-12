# ACE attribution, controller limits, and Terra scaling

> Closure correction (capacity follow-up, 2026-09-12): prior wrap-up ran `make ladon-status`, whose imports loaded testX. The earlier no-access claim was inaccurate. No test outcomes were used in this attribution analysis. See [the correction](../ace_capacity_20260912/closure_correction.json); original verification metadata is preserved alongside it.

Study date: 2026-09-12. This report concerns trainX and validationX only.
The original protocol, source seal, and two execution amendments are retained.
The main panels show modest ACE effects and higher Terra coverage at substantially
higher actual cost. Controller and feedback limitations remain material.

## What was missing in the earlier analysis

We **had measured non-ACE on both X development panels**. The archived
`x_train_agentic` and `x_validation_agentic` runs contain 40 problems for
each of seed identifiers 0 and 1. The actual missing comparison was a
matched ablation of the *current bounded/focused program*.

The last Git version before ACE is `3162a40c90655949c94753aa74094e2b67ccf960`
(August 24). It already uses Luna after the August 13 migration. The next
commit, `7bbb556f1`, introduces ACE along with X experiments and platform
changes; its September 1 commit date groups work done August 24–27.
The repository does not establish a separate model revision called
“Luna v2.” The exact [pre-ACE source](reference_source/prove_agentic_preace.py.txt)
and [provenance](reference_source/provenance.json) are retained.

| Seed-0 historical program | trainX | validationX |
|---|---:|---:|
| Earlier non-ACE agentic X program | 33/40, $0.777316 | 27/40, $0.886961 |
| Current bounded/focused flagship | 28/40, $0.689223 | 27/40, $0.667228 |
| Current bounded/focused minus ACE | 28/40, $0.818211 | 24/40, $0.776512 |

The earlier non-ACE program used 32 requests and stopped after crossing
the monetary limit. The current program allows 64 requests, uses focused
reference/bridge/structure choices, conservatively admits model and
verifier operations, and provides bounded typed feedback, an explicit
verified prefix, and `InspectProofState`. Both X configurations show local
definitions. The still earlier pre-X command hid definitions and used a
$0.05 cap, so restoring that command would introduce further confounding.

Thus the old baseline's 33→28 train and 27→24 validation change cannot be
attributed to ACE: both rows are non-ACE. It also cannot isolate one
controller component, because several components and runtime dates changed
together. The old-to-current flagship comparison preserves validation
coverage while reducing recorded cost 24.77%, but loses five train solves.
[LINEAGE.md](LINEAGE.md), [historical_comparison.json](historical_comparison.json),
and [historical_to_flagship.json](historical_to_flagship.json) retain every
gain, loss, cost, and paired comparison. The archived second seeds are
descriptive history; they were not used to expand this study.

## Controlled implementation and interpretation

Within each model, the new no-ACE arm executes the current flagship with
the book and its conditional instructions removed. Strategy, tool
implementations, demonstrations, focused policy, feedback, proof state,
and all budgets are otherwise identical. Admission/restart/polished and
later mechanisms remain disabled. Every one of the 80 reused Luna ACE
controls passed argument, cache, observed-request, outcome, and cost
parity checks without an API request; see [preflight.json](preflight.json).

Main panels have **40 theorems per arm per partition, seed 0 only**.
The campaign schedules 240 fresh main inference episodes, 40 Terra
adaptation generators, 16 book swaps, and 16 effort diagnostics: **312
new proof episodes**, plus 80 reused Luna ACE controls. Reflection,
curation, reduction, and embeddings are preparation work, counted
separately. The eight-theorem diagnostic panels were fixed by an
outcome-independent hash before launch, with four Mathd and four
competition problems and distinct families. No extra seed, training
epoch, auditor, warm start, book selection, or automatic model promotion
was added.

Both main models use medium reasoning, 64 requests, a 32768 output-token
allowance per request, 300 aggregate verifier seconds, 60-second
operations, 512 RPCs, and 8192-byte state views. Luna's cap is $0.10 and
Terra's is $1.00. At the recorded prices, Terra input/cached-input/output
rates are exactly ten times Luna's: $2/$0.20/$12 versus
$0.20/$0.02/$1.20 per million tokens. This preserves the monetary
controller's nominal token allowance when changing the model. See the official
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Terra](https://developers.openai.com/api/docs/models/gpt-5.6-terra) model pages.
Equal dollar budgets and equal token opportunity answer different
questions; the cost curves below expose that trade-off without silently
changing either treatment.

TrainX is in-sample for both books. ValidationX is repeatedly used
**development data**, not a fresh holdout. Luna's ACE controls are
historical, so provider/time and cache conditions can differ despite
observed-request parity. Seed identifiers name independently sampled
replicates; they are not provider-enforced deterministic seeds. The
protocol uses theorem-family clustering, 90% intervals, and two-sided
p<0.10, while treating the small diagnostic panels descriptively.

## Main results

| Model / context | trainX solves | Train cost | validationX solves | Validation cost | Validation cost / solve |
|---|---:|---:|---:|---:|---:|
| Luna / none | 28/40 | $0.818211 | 24/40 (60.0%) | $0.776512 | $0.032355 |
| Luna / Luna book | 28/40 | $0.689223 | 27/40 (67.5%) | $0.667228 | $0.024712 |
| Terra / none | 33/40 | $5.952686 | 29/40 (72.5%) | $6.610626 | $0.227953 |
| Terra / Terra book | 32/40 | $5.474728 | 30/40 (75.0%) | $6.451344 | $0.215045 |

All main raw solves qualify at their registered model cap. There are no
exported platform-failed cells or per-cell cap crossings. Costs include unsolved cells;
cost/solve divides the whole panel bill by its qualified solves.

**ACE's within-model effect is modest.** On Luna validation, ACE gains
three problems and loses none: +7.5 percentage points, exact paired p=0.25.
The descriptive family bootstrap interval is [+2.5, +15] points; its
exclusion of zero with only three discordant pairs does not override the
exact test. On Luna train, four gains cancel four losses: zero net effect,
90% interval [−12.5, +12.5], p=1.00.

Terra's ACE effect is +2.5 points on validation (two gains, one loss;
90% interval [−5, +10], p=1.00) and −2.5 on train (two gains, three losses;
interval [−12.5, +7.5], p=1.00). Validation gains are
`mathd_numbertheory_405` and `amc12_2001_p21`; the loss is
`mathd_numbertheory_303`. Terra's train gains are the AM–GM theorem and
`aime_1984_p1`; losses are `imo_1977_p6`, `imo_1983_p6`, and
`amc12b_2002_p11`.

ACE's validation increment is five points smaller on Terra than Luna.
That interaction has a 90% interval [−15, +5] and descriptive p=0.6875.
Train interaction is −2.5 points, interval [−17.5, +15], p=1.00. These
results provide no statistical support that stronger models increase
ACE's marginal benefit, and they do not establish equivalence or harm.

**Recorded cost savings and reasoning efficiency differ.** Luna ACE reduces
train cost 15.76% and validation cost 14.07%; validation cost/solve falls
23.62%. Family cost tests give descriptive p=0.00323 and 0.04981,
respectively, subject to the historical-control limitation. Terra ACE
reduces train cost 8.03% and validation cost 2.41%, but the respective
90% cost-ratio intervals [0.807, 1.046] and [0.876, 1.082] include no saving.
Its validation cost/solve falls 5.66%.

On Luna validation, ACE actually uses slightly more input tokens
(5.877M versus 5.780M) and output tokens (245341 versus 243896), while
reducing requests 497→447. Cached-input share rises 64.61%→75.87%.
Repricing these identical token counts with all input uncached gives
$1.448678 without ACE and $1.469747 with ACE: a 1.45% increase instead
of the observed saving. This is a price sensitivity, not a new uncached
experiment. The recorded bill is valid, but attributing all its reduction
to better reasoning would be misleading.

The secondary no-ACE model comparison gives Terra five validation gains
and no losses: +12.5 points, 90% interval [+5, +22.5], exact paired p=0.0625.
The gains are `aime_1991_p9`, `amc12b_2002_p3`, `imo_1960_p2`,
`mathd_numbertheory_303`, and `mathd_numbertheory_37`. This supports useful
model scaling in this system at the nominal 10% threshold; it is a
secondary contrast without multiplicity correction. With each model's own
book, Terra gains three and loses none, p=0.25. Neither train model
contrast meets p<0.10. These results concern delivered performance under
price-proportional caps, with sampling and cache behavior still present;
they do not isolate unrestricted intrinsic model capacity.

Terra with its own book improves validation coverage by three solves over
Luna with its own book, at 9.67 times total inference cost and 8.70 times
cost/solve. At Luna token rates, Terra's validation costs become $0.661063
without ACE and $0.645134 with ACE. These normalized figures also retain
each run's observed cache behavior; they are not measurements of identical
caching conditions or equal compute efficiency. Terra validation cached-input
shares are 79.21% without ACE and 81.98% with it. At the same observed token
counts with all input uncached, its costs would be $15.350324 and $16.657220:
ACE would cost 8.51% more. Both models' actual validation savings therefore
depend on cache billing; the stronger model's normalized bill should not
be interpreted as uniformly lower token use.

The [cost curves](solve_cost_curves.png) and [exportable PDF](solve_cost_curves.pdf)
show actual and Luna-rate-normalized final spend separately. At a common
$0.10 retrospective threshold, 21 Terra no-ACE and 20 Terra ACE validation
solves have final cost below the threshold, versus 24 and 27 for Luna.
Terra was allowed to start and continue under $1.00: this qualification
must not be presented as a run of the current controller at $0.10.
Detailed pairs, family intervals, costs, and observations are in
[complete_report.json](complete_report.json).

## Errors, admission, and the apparent capability ceiling

The principal Luna benefit is more directed proof search on some problems,
with regressions elsewhere. Across train and validation, first failing
checks mentioning an unknown reference fall from 14 without ACE to six
with ACE; first syntax failures fall from 15 to six. Solves with no prior
failed proof check increase from 8→14 on train and 9→12 on validation.
These are trajectory descriptions, not independent statistical trials.

Three validation gains illustrate useful guidance:

* `imo_1960_p2`: no-ACE makes 24 model calls and 12 failed checks; ACE
  makes six calls and two failed checks before succeeding. It cites
  square, reciprocal, and square-root advice and explicitly exposes the
  inverse and polynomial identities.
* `aime_1991_p9`: no-ACE makes 26 calls and 17 failed checks; ACE makes
  23 calls and 11 failed checks, then closes the rational factorization.
  Both runs still require substantial repair.
* `amc12b_2002_p3`: no-ACE makes 20 calls and eight failed checks; ACE
  makes five calls and one failed check, recovering from `omega` through
  an arithmetic/prime-factor argument.

Unsolved cells do not establish an unrestricted model ceiling. The
controller reserves a full possible output before making a request and
incorporates accumulated context and reasoning allowance. Luna's minimum
framing/output reservation is about $0.045875; Terra's is $0.458752.
At Terra prices the 32768-token output allowance alone reserves $0.393216,
so this configuration cannot even start at a $0.10 cap. That is a property
of the controller and price schedule, not a measurement that Terra would
actually spend that amount on its first answer.

The recorded cache omits final declined barriers and opaque serialized
reasoning references. The offline admission probe therefore replays every
observed answer, restores accumulated output allowance, and computes a
**lower bound** on the next reservation with HTTP disabled. If that lower
bound exceeds remaining money, the rejection is proven. Otherwise the
case remains indeterminate. It does not invent an unobserved continuation.

On the 53 unsolved Luna trajectories, 38 prove a monetary rejection,
nine remain indeterminate, and six return without reaching another model
request after spending 240.8–264.4 verifier seconds. Those six have less
than the required 60-second operation reservation remaining. There is no
need to exhaust the literal request count or spend the last cent to stop.
The complete probe replays all 89 unsolved main trajectories:

| Solver | Unsolved histories | Proven next monetary rejection | Indeterminate lower bound | Returns without next model request |
|---|---:|---:|---:|---:|
| Luna | 53 | 38 | 9 | 6 |
| Terra | 36 | 19 | 15 | 2 |

The two additional Terra returns are `mathd_numbertheory_43` with ACE
(242.27 verifier seconds) and `imo_1984_p6` without ACE (243.71 seconds).
Thus 57 histories have sufficient monetary-stop evidence and eight have
less than a full operation allowance remaining. This does not assert
that further attempts would solve any of them. The other 24 remain
indeterminate under the conservative lower-bound audit.

A second, independently reproduced defect affects the usefulness of
feedback. In two failed validation runs, `Qed` reports an incomplete proof
while the exported goal list is empty. Replaying the states locally and
issuing `Show.` reveals four unfocused goals for `amc12b_2002_p3` and a
nonzero-denominator obligation for `imo_1960_p2`. `Show Existentials.`
confirms them. The current bounded inspection allowlist excludes `Show`;
paginating the focused goal list cannot reveal an unfocused obligation.
The failure is an observability gap in the interface. It can mislead a
capable solver into repeated completion attempts. The
[initial](quality_probe_goal_visibility.json) and
[follow-up](quality_probe_goal_visibility_followup.json) probes retain
the exact scripts, including an unsuccessful `Show Unfocused.` probe.
Neither the runtime nor the experiment's prompts were changed in response.

Terra also reduces local errors with ACE: across its two main panels,
first unknown-reference failures fall 15→7, first syntax failures 13→2,
and solves without a prior failing check rise 18→21. Yet complex repairs
still fail. In `imo_1983_p6`, ACE first proposes an incorrect polynomial
identity, then eventually calls nonexistent `Rmult_le_0`. In
`imo_1977_p6`, it builds a substantial descent argument but ends at a
`lia` assertion whose predecessor-positivity premise is not established.
In `amc12b_2002_p11`, it derives the prime arithmetic structure but leaves
a final `prime 17` obligation after `native_compute`. These are concrete
mathematical/API/completion failures, not evidence of a broken worker.

The Terra validation loss, `mathd_numbertheory_303`, spends 29 calls on
modular constraints and list membership, receives only two failing proof
checks, and ends on an unfinished modulus-bound subproof. Its gains show
more substantial successful construction: a joint induction establishes
Fibonacci periodicity modulo seven in `mathd_numbertheory_405`, while
`amc12_2001_p21` narrows factors through a gcd argument before finite
exclusion. On trainX, Terra ACE closes the AM–GM theorem with an exponential
upper-bound invariant after 32 calls, although both adaptation generators
had missed it. The final Terra book has no dedicated AM–GM bullet, so
that solve cannot be simplistically credited to retrieval of an exact
training recipe.

Operation-level resource failures also remain. On Terra ACE
`mathd_numbertheory_43`, `native_compute` reports Rocq out-of-memory;
subsequent feedback records a closed connection, a restart, and attempts
with no verifier verdict. On `aime_1991_p6`, `simpl in Hsum` triggers a
60-second no-reply/restart, and the final attempt uses unsupported
`norm_num` syntax. These cells complete as recorded unsolved outcomes,
so the zero platform-failed-cell count must not be read as zero runtime
failures. More model capacity cannot by itself repair an exhausted prover
or make a missing tactic available.

Terra’s evolving adaptation chain yields 38 generator solves, while its
final frozen book yields 32 solves in the bounded/focused evaluation. These
use different sampled trajectories, evolving versus final context, and
different loops: training retains 32 requests and the
older post-crossing allowance, whereas inference uses conservative
reservations and bounded feedback. The gap motivates controller diagnosis;
it is not a paired estimate of one controller feature's causal cost.

The [per-problem appendix](CASE_APPENDIX.md) includes every main-panel
failure and discordant solve, and all 32 new diagnostic trajectories.
`complete_diagnostics.json` retains model responses, tool usage, citations,
verified-prefix/check histories, and errors; raw frozen caches retain the
full original exchange. `case_summaries.json` adds remaining allowances.
Error categories summarize verifier text; a label such as “prover-crash”
does not by itself mean the experiment had a platform-failed cell.

## Playbook creation and content quality

Both books were built from an empty context on the same 40 trainX problems,
one shuffled epoch, four-problem batches, three-query role contracts,
the same curator/reducer contracts, refinement every ten steps, embedding
threshold 0.88, and a 4000-token guard. Terra replaces **all four
generative roles**. The older `ace_x3_strong.yaml` used Luna generators
with stronger reflection/curation/reduction; it is not this all-Terra
treatment. The new transport explicitly limits outputs to 32768 tokens;
the old Luna training transport did not expose that limit, but its longest
observed output was 4042 tokens. No recorded Luna response exceeds the
new limit. Historical/provider-time conditions still limit strict
attribution of preparation differences.

| Preparation measure | Luna X3 | Terra |
|---|---:|---:|
| Generator solves | 33/40 | 38/40 |
| Generator requests | 511 | 396 |
| Solves without a preceding failed proof check | 9 | 9 |
| Generator cost | $0.711104 | $5.998384 |
| Reflection cost | $0.150748 | $1.557570 |
| Curation cost | $0.041454 | $0.412922 |
| Reduction cost | $0.013618 | $0.130302 |
| Total generative preparation | $0.916924 | $8.099178 |
| Recorded embedding cost | Not recoverable from these receipts | $0.0000406 |
| Retained bullets / estimated tokens | 26 / 2103 | 26 / 2426 |
| Added / pruned bullets | 27 / 1 | 26 / 0 |
| Reflector helpful / harmful tags | 23 / 8 | 31 / 6 |

Terra improves generator coverage through recovery, rather than increasing
the count of immediately successful first proposals. It solves five of
Luna's seven generator failures; both still miss
`algebra_amgm_sum1toneqn_prod1tonleq1` and `imo_1967_p3`. It uses 22.5%
fewer generator requests, about 29.7% fewer input tokens, and 7.6% fewer
output tokens. There are no generator platform failures, final reflector
or curator failures, or curator fallbacks. Luna has one extra curation
request inside the permitted parse contract. Helpful/harmful tags remain
reflector opinions about cited advice, not verifier-proven causal labels.

Terra's complete preparation costs $8.099219, about 8.83 times Luna's
recorded generative preparation. At Luna token rates, Terra's generative
bill is about 11.7% lower. The missing historical embedding bill is not
estimated from a reusable embedding cache. Preparation amortization adds
about $0.0810 or $0.00810 per Terra problem over 100 or 1000 problems;
Luna adds at least $0.00917 or $0.000917. These are arithmetic scenarios,
not forecasts that a trainX book transfers unchanged to another workload.

The Terra book is 15.4% longer but still far below the 4000-token guard.
Neither training chain merges or drops bullets for length. The curator's
maximum of three additions per four-problem batch still limits which
experiences survive. A stronger model does not remove that information
selection bottleneck.

Terra tends to write longer procedural advice: symbolic recurrence
invariants, concrete recurrence instantiation, power/logarithm
normalization, and explicit sign/factor arguments. Luna retains three
AM–GM-related cautions and specific Ensemble, trigonometric, and square-root
guidance absent from Terra's final book. Terra also retains generic
`intros; nra` and closed-reflexivity advice, which may add less information
than a rare library-specific repair. This is a content comparison, not a
numerical quality score.

Availability checks extracted identifiers from every backtick span,
including longer snippets. They cover 39 Luna and 30 Terra
bullet/reference pairs after excluding underscore placeholders. Candidate
global references resolve in a recorded source-batch environment.
`R_scope` is a valid scope, confirmed with `Print Scope`, rather than a
missing constant. Availability does **not** establish applicability,
correct side conditions, useful selection, or valid surrounding syntax.

One concrete Terra defect demonstrates that distinction. Final bullet
`rocq-00001` suggests `have hs : ... := Rle_0_sqr _`, which is unsupported
in the source theorem's environment. The same proof succeeds using
`assert (...) by apply Rle_0_sqr`. The training generator used valid
`assert`; reflection correctly diagnosed the square/product mismatch;
curation retained valid guidance; **the reducer introduced `have`**.
The bad example survives into the frozen book. The exact
[verification probe](quality_probe_have.json) and
[role-by-role lineage](quality_probe_have_lineage.json) are included.
This is one verified defect, not an estimate of either whole book's
error rate. Neither book was repaired or reselected after seeing it. The defective
bullet is cited ten times across nine evaluation cells, with three next
checks accepted and seven rejected. That mixture neither validates the
snippet nor establishes it caused the rejections. All 26 Luna bullets
and 25 of 26 Terra bullets receive at least one citation across their
own-book and swap exposures; Terra's whole-comparison `%nat` advice is
uncited. Citation coverage remains a usage observation.

The fixed eight-theorem validation swap panel gives:

| Solver | No book (reused) | Luna book | Terra book |
|---|---:|---:|---:|
| Luna | 4/8, $0.183204 | 4/8, $0.194585 | 3/8, $0.193974 |
| Terra | 5/8, $1.749170 | 4/8, $2.039438 | 4/8, $1.902074 |

Luna with the Terra book rescues no old failure and loses
`amc12a_2008_p4`. It uses 48 model calls and 23 failing checks, beginning
with a mismatched `S_INR` rewrite and ending with an incomplete recursive
product proof. It cites Terra's closed-form and field guidance, rather
than the audited bad `have` snippet. Terra solves the same four problems
with either book; both miss `mathd_numbertheory_303`, which Terra without
a book solves. With Luna's book, that trajectory ends on malformed `}.`
syntax after 23 calls.

This panel gives no evidence that replacing Luna's book with stronger
model-authored advice resolves the bottleneck. Eight problems cannot
establish equal book quality, overall superiority, or a causal explanation
for the full-panel interaction. The verified bad snippet remains a
content defect even when a particular regression does not execute it.
There is no basis here to promote Terra's book over Luna's.

The separate fixed eight-theorem train panel compares Terra no-ACE effort:

| Effort | Solves | Panel cost | Cost / solve |
|---|---:|---:|---:|
| Low | 5/8 | $1.251119 | $0.250224 |
| Medium (reused main cells) | 6/8 | $1.507862 | $0.251310 |
| High | 6/8 | $1.217219 | $0.202870 |

Both low and high solve `mathd_numbertheory_629`, which medium misses.
Both miss `amc12b_2002_p11`, which medium solves; low additionally misses
`amc12b_2004_p3`. Thus high matches medium's count through a different
set of solves, at 19.28% less recorded cost. The high-effort prime problem
makes 26 model calls without submitting a proof. Low effort on
`amc12b_2004_p3` ends with a verifier deadline; low/high runs on
`mathd_numbertheory_629` recover from an initial prover-crash-labelled
check and succeed after 23/15 model calls. This small panel shows no
monotonic “more effort fixes the limit” pattern. It does not select a new
effort setting or authorize another grid.

`book_audit.json` contains every final bullet, source batch, reference
check, and citation's following verifier result. A citation can be broad,
irrelevant, or followed by unrelated work; it is not counted as causal
benefit. `training_evolution.json`, `training_diagnostics.json`, and the
separate preparation accounting files retain all 40 steps for each model.

## Comparison with the ACE paper

The [ACE paper](https://arxiv.org/abs/2510.04618) reports average gains of
10.6 points on agent benchmarks and 8.6 on finance tasks. Its evaluation
uses different tasks (including AppWorld, FiNER, and Formula), a different
base model, and broader context adaptation settings. Those numbers are
useful motivation, not an expected threshold for Rocq proofs under this
admission controller. Here the observable outcome includes library
grounding, tactics, proof-state visibility, verifier reservations, cached
input pricing, and a small one-epoch book. A smaller observed gain neither
refutes the paper nor identifies Luna capacity as its cause. The matched
ablation and model/book swaps are the relevant local tests.

## Execution, evidence, and next decision

All 312 new proof episodes and all 90 additional generative preparation
jobs completed. The resumed coordinator exited 0. The 3939 new API
receipts are settled: 3914 generative calls and 25 embedding calls.
There are no missing, administratively censored, or exported
platform-failed cells, no unknown charges, and no extra experimental
retry episodes.

| New campaign component | Actual API cost |
|---|---:|
| Luna no-ACE main panels | $1.59472272 |
| All-Terra adaptation, including embeddings | $8.09921860 |
| Terra main panels, both arms | $24.48938340 |
| Book swaps | $2.23341200 |
| Effort diagnostics | $2.46833820 |
| **Total** | **$38.88507492 / $75 ceiling** |

Historical Luna ACE inference costs $1.35645172 across both panels and
historical Luna preparation costs at least $0.91692376; those reused costs
are reported but were not paid again. The campaign leaves $36.11492508
of its ceiling unused. Assistant/harness usage is outside this API ledger.

The original source seal remains intact with two explicit amendment links.
First, a legacy training-citation helper attempted to open the protected
challenge manifest; the audit hook denied access before returning bytes.
The helper now accepts the authorized trainX allowlist. Four completed
Terra generators were reused on resume without another proof episode.
Second, completed-stage slack was forwarded to the diagnostic stages so
simultaneous maximum-output reservations would fit. Neither amendment
changed a model, prompt, book, individual cap, worker count, or panel.
The original failing exit record is retained. testX and the protected
challenge remain closed.

All 272 new inference exports match registered strategy/policy/budget
arguments; all 130 preparation role exports identify Terra, including the
40 generators. The [role inventory](preparation_role_inventory.json) also
records their result/cache hashes. Inference result/cache hashes
are recorded in [execution_inventory.json](execution_inventory.json).
[Registered repricing](reprice_registered.json) checks all seven exact run
directories: 402 generative configurations plus embedding receipts reproduce
the ledger total with zero mismatches. The generic repricing CLI's shallow
discovery initially found only the two diagnostic runs; that partial log
is retained and the registered-run check closes the coverage gap without
opening the global output archive.

Validation: 53 scoped tests pass, Ruff checks/format checks pass on touched
Python, and pinned Pyright 1.1.406 passes the new modules. Root
`make pyright` still stops on the same 17 `find_invariants/why3py` errors
outside this task's authorized scope. The touched legacy adaptation module
has the same 21 diagnostics as checkpoint `23329b09`. Full global tests
and repricing were not used because they open closed datasets; the scoped
checks and their limits are recorded in [verification.json](verification.json).
Dual-harness instruction/memory invariants pass. The cost figures were
rendered and visually inspected.

**Decision:** keep the flagship and its Luna book unchanged. There is
practical evidence for Luna ACE's local repair and recorded-cost benefits,
but no statistically supported ACE coverage improvement in either model.
Terra demonstrates useful additional no-ACE coverage at a substantially
higher actual bill; it does not make ACE's increment larger. Its stronger
training trajectories do not yield a uniformly better book or a successful
transfer to Luna. The combined evidence supports the pricing part of the
hypothesis, while leaving an unrestricted Luna capability ceiling
unestablished.

The next useful engineering work is to expose unfocused obligations and
record final admission decisions, then independently verify executable
book snippets after reduction. Those are concrete observed defects with
local reproductions. A later registered comparison can isolate admission
and feedback changes before attributing residual misses to model capacity.
No such runtime/book change or extra paid comparison was made in this
study. The complete evidence map and offline reproduction commands are in
[ARTIFACTS.md](ARTIFACTS.md).

The prior work was committed as requested in `23329b0983a7f62564d29529a50005cce63c409c`,
with author/committer and Signed-off-by
`guillerplazas <guille.rplazas@hotmail.com>`. The new study remains staged
for review. Local progress, hints, and cross-session memory remain local.
