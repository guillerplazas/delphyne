# ACE studies: findings and interpretation

Curated 2026-09-09 from the completed review and bounded follow-up.
This document owns the results and their limits. Unresolved proposals are
centralized in local [HINTS](../HINTS.md); completed outcomes are indexed in
[CLOSED_HINTS](CLOSED_HINTS.md). The original registered campaign protocols
and machine-readable evidence remain in their campaign directories.

## Fresh review: improvement was not established

The selected x3 artifact achieved **121/176 qualified solves versus 118/176**
for a fresh baseline on 88 previously unexposed non-Mathd theorems, two seeds.
The effect was **+1.70 points**, exact family-cluster p=0.5811, descriptive
95% interval −2.27 to +5.68 points. Its total cost was 4.3% higher.
The registered >=5-point, two-sided p<0.05 rule failed. The interval still
includes useful effects; this is inconclusive evidence, not proof that ACE
cannot help. The current p<0.10 convention does not alter this conclusion.

| Confirmation arm | Qualified solves | Conservative cost |
|---|---:|---:|
| Fresh baseline, 64 requests | 118/176 | $6.662 |
| Selected x3, 64 requests | 121/176 | $6.949 |

All verified proofs also met the $0.10 actual-cost cutoff. The cost ratio
was 1.043, descriptive 95% interval 0.937–1.162. The optimistic treatment
of one uncertain charge does not change the solve comparison. Longest
completed attempts were 55.7 minutes for baseline and 72.4 minutes for x3:
request and nominal dollar limits did not provide a useful latency bound.

Sources: [protocol](../experiments/campaigns/ace_review_20260908/README.md),
[confirmation](../experiments/campaigns/ace_review_20260908/confirmation.json),
[billing sensitivity](../experiments/campaigns/ace_review_20260908/confirmation_billing_sensitivity.json).

## Selection, calibration and accounting

Calibration selected 64 requests operationally: 59→66/80 budget-qualified
baseline solves, grouped p=0.0625, and cost $2.195→$2.322. Raw verified
proofs rose 63→67/80; changed cost qualification contributes to the larger
qualified gain. Six initial transport failures retained about $0.439 of
uncertain liability; later launches restored the 600-second transport
limit. This mixed pilot history limits causal attribution.

Development completed all 320 cells and selected frozen x3:

| Development arm | Verified / 80 | Qualified / 80 | Cost | Grouped p versus baseline |
|---|---:|---:|---:|---:|
| Baseline, 64 requests | 52 | 52 | $3.180 | — |
| x3 | 57 | 57 | $2.866 | 0.2344 |
| Repair seed 0 | 55 | 52 | $3.250 | 1.0000 |
| Repair seed 1, stability only | 54 | 54 | $2.783 | 0.6875 |

The observed development cost advantage did not reproduce in confirmation.
Repair seed 1 was a stability check, not an alternative deployment candidate.
Training originally solved 32/40 episodes per repair seed, then recovered
0/8 and 1/8 failures, respectively. Both artifacts together cost about
$3.316, including roles and embeddings. Comparing additional repair compute
against an older frozen artifact does not isolate reflection itself.

The matched Terra comparison had 32 problems: x3 solved 22 versus Terra's
25, at mean cost $0.04365 versus $0.17173. x3 cost 25.42% of Terra, but the
95% ratio interval 17.29–35.69% crossed the one-third target. Solve difference
p=0.375; quality equivalence was not established. Retain the expensive
crossing request in the full-panel comparison.

The full campaign completed 864 evaluation cells, 80 original training
episodes and 31 repair episodes. Conservative liability was
**$39.01643976 of $50**: $38.32744076 receipted and $0.688999 reserved for
nine unknown charges, with no work left in flight. There were 20,704
receipts, including failures and embeddings. This covers experiment API
liability, not assistant usage or engineering time. Reusing x3 meant zero
incremental adaptation cost in this campaign; its earlier training was not
free.

Sources: [calibration](../experiments/campaigns/ace_review_20260908/calibration.json),
[selection](../experiments/campaigns/ace_review_20260908/selection.json),
[training](../experiments/campaigns/ace_review_20260908/training_summary.json),
[final report](../experiments/campaigns/ace_review_20260908/final_report.json),
[operational audit](../experiments/campaigns/ace_review_20260908/operational_audit.json).

## Bounded follow-up: an accepted budgeting trade-off

The integrated grounded money+focused candidate completed one frozen
validationX seed-0 panel: **25/40 qualified solves for $0.67804714**, versus
X3's **28/40 for $1.52378888**. Cost fell 55.5%; cost per qualified solve
fell 50.2%. The one-win/four-loss comparison gives grouped solve p=0.375;
family cost p≈0.00011, ratio 0.445 with descriptive 90% interval 0.376–0.534.

The registered no-fewer-solves saving gate failed. Guille explicitly accepted
and retained the configuration as a budgeting win, keeping X3 as the coverage
comparator. This is a separate utility decision, not a retroactive passed
gate or a proven ACE solve improvement.

All four adaptation episodes, sixteen pilot cells and forty validation cells
cost **$1.38272072** in total, with 783 settled HTTP attempts and no unresolved
charges or infrastructure retries. Three training role episodes failed YAML
parsing; the accepted evidence pool had six reference and two structure
examples, no demonstrated bridge coverage. Advice and restart did not trigger
in the pilot. These limit claims about the contribution of grounded advice.

Sources: [bounded protocol](../experiments/campaigns/ace_bounded_20260908/README.md),
[final report](../experiments/campaigns/ace_bounded_20260908/final_report.json),
[user acceptance](../experiments/campaigns/ace_bounded_20260908/acceptance.json),
[failure diagnosis](../experiments/campaigns/ace_bounded_20260908/FOLLOW_UP.md).

## What the diagnosis established

Full conversation/tool output, rather than playbook size alone, caused the
largest resource failures. A recorded tool result exceeded thirteen million
characters, while individual operations could continue for tens of minutes
between model calls. Automatic completion also contributed useful solves;
removing the battery would change coverage. A single RPC timeout does not
bound the complete verification/feedback operation.

Grounded follow-up work already implemented typed outcomes, whole-operation
limits, conservative monetary admission, focused queries, checked training
claims and role demonstrations. The older diagnostic loader now uses full
cell identities. They are no longer missing-component proposals.

The bounded failure audit confirmed a typed-limit admission mismatch with a
pure seven-second-versus-sixty-second reservation probe. Monetary refusals
and paid-answer-without-check tails remain inferred where explicit admission
events were absent. Neither observation proves that more budget would recover
those proofs. Cache entries are not invocation counts.

Delphyne already supports policy-side budget admission and query-specific
demonstrations. The remaining upstream budget issue is obtaining appropriate
monetary estimates and transport/retry accounting, not inventing budget
composition. A demonstration teaches a decision; a current training problem's
verified solution is separate evidence. Existing typed composition should be
extended at the demonstrated gap rather than recreated.

The backlog owns the corresponding actions: the implemented bounded work
has closure records #113–119 (resource recovery #116 remains open), with
#67/#94/#95/#110 for applicable advice and examples, #103/#109 for
search/context control, #104 for upstream accounting, and #107/#111 for
evaluation design. New polish follow-ups are #121–123. Historical closed
capabilities have closure records rather than duplicate future-work lists here.

## Evidence boundaries

validationX is development data after repeated selection. The challenge
excludes Mathd, while trainX/validationX contain a different mixture; it is a
transfer study, not an estimate for the original miniF2F population. Its
67.05% fresh-baseline rate versus 65% in development does not establish that
the category filter made the benchmark harder. Protected outcomes remain
closed to tuning and demonstration construction.

Repeated seeds stay grouped by theorem/family. The +5-point threshold is a
requirement on the observed estimate; p tests zero effect, not a guarantee
that the true gain is at least five points. Historical rules remain pinned;
future non-Ladon decisions use p<0.10 with the same grouping discipline.
Current commands and archive conventions are in [usage](usage.md).

## Bounded ACE polish (2026-09-09)

The follow-up implements the concrete bounded-control findings as an
opt-in pipeline, retaining the original money+focused configuration as
the fresh benchmark reference. Delphyne's `with_budget`, spending streams
and query-specific example selection provide admission and composition;
the local adapter records their decisions rather than deciding separately.

Typed `ToolLimits` now supply the actual verifier reservation. A zero-cost
sequential preflight prevents purchasing an answer when its verification
cannot be admitted. An optional 4096-token continuation after refusal and
an optional resource/stagnation repair share one recovery allowance; neither
resets money, time or turn budgets. Resource/unknown outcomes are not logical
refutations. Separate structured adaptation queries preserve legacy YAML
contracts while avoiding the observed serialization failure mode.

Twenty-four training transitions were reverified locally and exposed as
Delphyne demonstrations, including executable navigation checks. Thirteen
existing role examples were converted offline. No stronger-model authoring
was needed and no teacher calls were charged. The examples span more failure
categories, but a verified local correction is not a verified general tactic
or a full solution to the current problem.

The 24-cell training pilot selected matched advice and output downshift.
Resource recovery exposed two Responses dialogue-formatting failures, so its
contrast was invalidated and the mechanism remains disabled. The formatter
was repaired and regression-tested before the final freeze, without extra
paid pilot cells. An independent result-reader defect hid outcomes behind
large command arguments; corrected reporting preserved the same selections.
Both erroneous drafts remain archived, and no raw paid output was edited.

Protocol, hashes and checks: [polish campaign](../experiments/campaigns/ace_polish_20260909/README.md).

The frozen candidate solved **26/40 trainX problems for $0.76279972**.
Fresh paired validationX (40 problems, two seeds) tied **53/80 versus
53/80**, at **$1.51289576 versus $1.43330822**: 5.55% more total cost and
cost per solve ($0.02854520 versus $0.02704355). Seed 0 lost one solve at
20.13% more cost; seed 1 gained one at 7.14% less cost. Neither registered
practical gate passed. Family-clustered solve p=1.0, cost p=0.35545;
descriptive 90% effect interval [-2.5, +2.5] points and cost-ratio interval
[0.9604, 1.1648]. This is inconclusive, not evidence of equivalence.

**Retain original bounded money+focused as the recommended budget reference.**
The polished controls remain available but are not promoted. All 224 cells
cost **$4.24146774 API**, with 2,749 settled requests, no unknown charges,
teacher calls, retries or per-cell cost crossings. The two invalid pilot
cells remain in the record; full training/validation had no experiment
platform failures or administrative censoring.

Downshift led to zero solves in nine triggered training cells and one in
17 validation cells; that theorem also solved in the reference at half
the cost. Neither unique candidate validation win used it. Matched examples
were selected 20 times across 12 validation cells, yet syntax leakage,
sqrt/cast normalization and expensive natural-number computation remain.
Eleven of the candidate's 27 unsolved cells contain a cached resource or
unknown outcome; these are not logical rejections. Five explicit verifier
exhaustions and monetary refusals in 24 candidate cells now make stopping
more auditable, but do not establish that more spending would help.

Detailed paired discordances, failure evidence and targeted follow-ups:
[polish assessment](../experiments/campaigns/ace_polish_20260909/FOLLOW_UP.md).
The backlog prioritizes stronger recovery signals (#123), tactic-specific
syntax examples (#122), narrow normalization guidance (#94/#110), and
large-natural representation work (#72). No validation-triggered retuning,
extra seeds, testX or protected-challenge mining was performed.


## Bounded applicability mechanism screen (2026-09-09)

The training-only four-arm screen completed 48 saved-state episodes for
$0.05822918, with 60 settled requests and no platform failures, retries or
unknown liability. Ordinary continuation / typed query / fixed examples /
selected examples yielded 1/2/3/2 useful local transitions. Selection was
23.34% cheaper than fixed examples but lost one useful transition, repaired
only 4/6 positives and explicitly abstained on 4/6 negatives. The registered
screen failed: no 24-cell end-to-end training stage or 160-cell validation
comparison was launched. Bounded money+focused remains the reference.

A post-run Rocq audit found that the finite syntax guard rejected a valid
suffix in each typed arm. Primary measurements remain unchanged; sensitivity
gives 3/4/3 useful transitions for typed/fixed/selected and still fails the
abstention and benefit gates. This limits the negative claim to the registered
applicability/delivery mechanism; these local episodes do not estimate full
proof coverage, establish automated-reflection value, or exhaust ACE.
See the [completed screen](../experiments/campaigns/ace_applicability_20260909/FOLLOW_UP.md)
and HINTS #122 for the remaining semantic-guard and applicability questions.
