# ACE platform revision: verified mechanisms, inconclusive transfer

The platform now preserves local repairs, checks their exact source context,
separates examples from new advice, and applies reviewed corrections without
losing the existing book. The resulting book has **27 rules and 2224
estimated tokens**, versus the flagship's 26 rules and 2103 tokens.

The complete fresh comparison does **not** establish a better flagship.
Training loses one solve; validation gains one. Both cost intervals include
no change, and the registered validation threshold is missed. Keep the
platform mechanisms available and retain the current flagship default.

## What was failing

The [earlier role campaign](../ace_roles_20260913/FINDINGS.md) exposed four
problems that a JSON-validity pilot did not resolve:

- Executed snippets were treated as evidence of novel advice. Six of eight
  additions repeated guidance already in the book; prompt size grew from
  2103 to 3994 estimated tokens.
- Useful abstentions inflated a review-utility metric without producing
  actionable lessons. Four of the candidate reflector's five useful pilot
  judgments were abstentions.
- All eight retained additions came from completed training proofs.
  Unsolved trajectories could contain useful local work, but the role
  interface and handoffs did not reliably preserve it.
- Append-only retention, generic validation feedback and cancellation
  behavior left avoidable contradictions, lost work and unresolved billing.

These observations motivated the platform work before another paid run.
The old validation is censored at 55/160 result files, has no verdict, and
was not mined for these changes. Accessible development artifacts supplied
the evidence; mixed HINTS/history and closed evaluation data were excluded.

## What changed and what the live run demonstrated

The [implementation guide](../../../docs/ace_role_revision.md) describes
the strategies, policy adapters, tools and contracts. All new code remains
inside Omphalos and is usable from either harness.

| Mechanism | Live evidence or preflight check |
| --- | --- |
| Reflectors submit explicitly unverified local repairs separately from final disposition | All 12 unsolved training sources supplied drafts; one supplied a retained text correction |
| Curators check exact snippets and preserve partial products | 53 new Rocq checks; six invalid final plans preserved their evidence |
| Reducers reuse evidence and separately review novelty | Zero new Rocq checks; 16 review queries; one correction, one new operation, six examples and eight unsupported dispositions |
| Examples remain outside the generator prompt | Six evidence attachments produced no additional rules |
| Corrections replace a particular rule atomically | Rule `rocq-00026` was updated using rejected and repaired snippets in the same source context |
| Message checkpoints survive request exhaustion | Offline budget-stop test recovered a checked repair even without a returned strategy solution |
| Pause stops subsequent admissions and drains existing ones | Mocked in-flight transport settled its actual charge; the next reservation was blocked |
| Sources, inputs and treatment remain frozen | All 235 sealed paths retain their registered hashes |

The automated pass used 40 reflectors, 29 curators and ten reducers;
11 abstentions skipped curation. All reflectors and reducers completed.
Curators completed 23/29 final plans; six partial products had invalid
unused fields on `drop` or non-update actions. This remains a model-facing
contract usability problem. It did not silently discard prior work: the
reducer retained an example from the partial `aime_1988_p3` curator using
its existing receipt. There were no missing role products.

The two text changes were:

1. **Clarify logarithm prerequisites.** The old `ln_mult` rule omitted how
   to establish the separate factor-positivity premises in a source using
   `Rpower`. The revision explicitly uses `unfold Rpower; apply exp_pos`
   for that factor. It came from the unsolved `amc12a_2020_p13` trajectory.
   This repairs an omitted prerequisite, not a false logarithm identity.
2. **Prove a factor nonzero from root equations.** After exposing the
   polynomial equations, assume the factor zero, substitute, and contradict
   a given disequality with `nra`. This came from the accepted
   `mathd_algebra_206` trajectory.

The exact audit reconstructed the final book and re-executed 11 relevant
receipts, including logical rejections used in review. The executed local
fragments still left other goals open. They are not complete proofs of the
source theorems or general-validity certificates for the advice.

Preparation cost **$0.45092992**, compared with $0.31268266 for the earlier
full role pass. This buys more selective, recoverable retention: 121 added
prompt tokens instead of 1891, and one unsolved-source correction instead
of zero. These are descriptive comparisons across implementations, not a
randomized ablation of individual tools or a claim of better proof coverage.

## Fresh paired flagship comparison

Both arms used Luna-medium, core generator tools, bounded/focused proof
control, and $0.10 / 64-request / 300-verifier-second limits. Only the book
differed. There were 80 fresh training jobs and 160 fresh validation jobs;
all completed, with zero platform failures and zero $0.10 cap crossings.
The 80 validation cells per arm are 40 theorems measured twice.

| Panel | Flagship qualified solves | Candidate qualified solves | Flagship inference cost | Candidate inference cost | Candidate / flagship cost |
| --- | ---: | ---: | ---: | ---: | ---: |
| trainX | 29/40 | 28/40 | $0.71128344 | $0.68593736 | 0.9644 |
| validationX, two seeds | 47/80 | 48/80 | $1.55318798 | $1.52856742 | 0.9841 |

On validation, the coverage difference is **+1.25 percentage points**,
with a descriptive family-bootstrap 90% interval of **[-2.5, +5.0] points**
and two-sided paired **p=1.0**. The cost-ratio 90% interval is
**[0.9223, 1.0431]**; paired cost **p=0.6790**. Repeated seeds are clustered
by theorem family. Training is also inconclusive: coverage p=1.0 and cost
ratio interval [0.8766, 1.0610].

The registered practical threshold required either at least two additional
validation solves at no more than 1.25 times cost, or at least 10% savings
with no more than two fewer solves. **Neither condition passed.** This is
not proof that the idea has no value; the measured transfer is too small
to establish the proposed practical improvement. No extra seeds, arms or
retries were added, and no default was changed.

Validation inference cost per qualified solve is **$0.03304655** for the
flagship and **$0.03184515** for the candidate. Including candidate
preparation raises its cost to **$1.97949734**, or **$0.04123953 per solve**.
The observed inference saving would repay preparation after roughly 1466
problem attempts if it persisted. That is a descriptive extrapolation;
the cost interval includes no saving, so it is not an established payback.
The single validation gain cannot be attributed to either individual rule.

The small billing difference is also sensitive to caching. Repricing the
same observed validation tokens without cached-input discounts gives
$3.32679980 for the flagship and $3.35599960 for the candidate, about 0.9%
more for the candidate. This sensitivity does not simulate changed budget
stops or predict coverage under another tariff; see
`cost_sensitivity/319.json`.

The machine-readable [paired reports](reports/319.json) preserve costs,
denominators, uncertainty and economics. [RESULTS.md](RESULTS.md) is the
short numerical record. validationX remains repeatedly used development
data; this is not independent held-out confirmation. testX and the protected
challenge remain closed.

## Which ideas deserve further work

**Keep the role-specific tools and durable handoffs.** Local draft capture,
exact Rocq checking, receipt reuse, reviewed updates and evidence-only
examples solve demonstrated bookkeeping and retention failures. The run
shows these mechanisms working with model outputs, including recovery from
an invalid curator final.

**Prioritize useful learning yield and review quality.** Only two text
changes survived 29 drafts and 53 new checks. All 12 unsolved sources now
reach curation, but just one supplies a text repair. Improve the conditional
action interface and evaluate source-local reviewer decisions separately
from abstentions and downstream coverage. Model novelty judgments remain
fallible; neither exact execution nor a second model query proves transfer.

**Defer additional generator tools.** The measured treatment deliberately
keeps the generator matched. Prior development experiments did not justify
repeating the same snippet/completion expansion, and this run does not test
a new generator tool. Example retrieval can be evaluated separately if a
specific need and bounded mechanism test emerge; adding it here would
confound the book comparison.

These follow-ups are recorded in the development-only append to HINTS.
No hint IDs or historical verdicts were rewritten through the mixed files.

## Verification and spending

Before paid dispatch, **55 scoped tests passed**, including real Rocq,
invalid finals, atomic updates, duplicate folding, budget-stop recovery,
pause settlement, HTTP-forbidden replay, proof-request parity and a complete
synthetic campaign integration test. Pinned Pyright 1.1.406 reported zero
errors on the changed code; Ruff passed. Root type checking still has the
17 pre-existing `why3py.simple` dependency/type errors in `find_invariants`.
Aggregate tests and repricing that can access closed data were excluded;
the campaign's own receipts are repriced from dated token rates.

Paid work is complete at **$4.92990612 / $40**, with **3005 settled receipts,
zero unresolved charges and zero billing issues**. Adaptation cost
$0.45092992, the paired training comparison $1.39722080, and paired
validation $3.08175540. The remaining $35.07009388 is unspent.
The earlier campaign's $1.98787940 confirmed charges and $2.12898800 unknown
upper bound remain in its historical accounting, outside the explicitly
reset authorization. Agent-session billing is unavailable and separate.

All **319 jobs replayed exactly**, matching outcomes, budgets and values,
with HTTP blocked and zero paid calls. The final record is
[replays/319.json](replays/319.json). The final source/input, exposure,
CSV/ledger/report and process-exit checks are in
[final_verification.json](final_verification.json). Both the campaign
process and its Rocq server exited normally.
