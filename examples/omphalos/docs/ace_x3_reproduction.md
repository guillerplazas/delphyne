# Where the historical X3 gain came from — 2026-09-18

**The historical gain is real as a recorded observation. Its general
reproducibility remains unresolved.** The first thesis audit recovered the
aggregate result and its uncertainty. This follow-up reconciles its legacy
ledger, decomposes the saving, examines the decisive proof searches, and
compares the actual requests with the fresh experiment. The fresh X3 arm uses
a different output limit, so it is not an exact replication of that result.

The historical attribution comparison uses all 40 validationX problems,
one replicate each. X3 was run on September 9; non-ACE on September 12.
Non-ACE solved 24/40 at $0.77651210; X3 solved 27/40 at $0.66722836.
That is **14.0737% lower all-attempt inference spend** and **+7.5 coverage
percentage points** (60% to 67.5%, or +12.5% relative coverage). It is not
a +10 percentage-point coverage result. Learning costs are outside this
inference endpoint, as in the [main report](ace_thesis_report.md).

There is already a second X3 replicate in that historical archive, with
the **same playbook and observed configuration on all 40 problems**. It
solved **26/40 at $0.76607986**, only **1.34% cheaper** than the original
non-ACE reference. That comparison reuses the same 24/40 non-ACE draw;
there is no matching second non-ACE replicate, so it is a sensitivity
check rather than another independently controlled comparison. It shows
that the 14.07% observation varied substantially even before the new
configuration. We retain both X3 replicates without replacing the original
registered attribution comparison or pooling a duplicated control.

The old cost is supported by complete exact-cell billing records: 497
settled non-ACE requests and 447 settled X3 requests. Every receipt matches
dated token repricing, and every cell's ledger total matches its cached
token cost. The initial census missed X3's ledger because output directory
`ace_polish_validation` maps to campaign `ace_polish_20260909`, rather than
an identically named campaign. Its `cache_only_cells=40` flag describes a
lookup gap, now resolved; it is not evidence of absent billing records.
The original census remains preserved, with this correction supplied
separately. No historical paid artifact was rewritten.
The second X3 replicate adds 466 settled, exactly repriced receipts, also
reconciled cell by cell: the follow-up exports 1,410 receipts in total.

The accounting decomposition is exact for the observed request paths:

| Historical measure | Non-ACE | X3 |
|---|---:|---:|
| All-attempt charged cost | $0.77651210 | $0.66722836 |
| Same tokens priced without cache discounts | $1.44867800 | $1.46974720 |
| Input tokens | 5,780,014 | 5,876,690 |
| Cached input tokens | 3,734,255 | 4,458,438 |
| Cached fraction of input | 64.61% | 75.87% |
| Output tokens | 243,896 | 245,341 |
| Requests | 497 | 447 |

X3's extra cache discount is $0.13035294, offset by $0.02106920 more
undiscounted token cost, leaving the observed $0.10928374 net saving.
Without discounts, those same traces would cost **1.45% more** under X3.
Thus the aggregate saving depends on cached-input pricing, despite 10.06%
fewer requests. This is an accounting counterfactual, **not a causal cache
ablation**: changing cache availability can change monetary admission and
therefore the executed search. Repeated ACE context can legitimately benefit
from caching. These archives do not isolate that benefit from prefix reuse,
concurrent workloads or the historical run schedule.

There were also concrete proof-search gains. Two problems account for
**58.90% of the net dollar saving**; all three coverage gains account for
64.81%. X3 is cheaper on 28 problems and more expensive on 12, so the table
does not replace the full denominator.

| Problem | Historical non-ACE → X3 | Historical saving | Fresh ordinary non-ACE / matched non-ACE / X3 solves |
|---|---|---:|---|
| `imo_1960_p2` | failed in 24 requests → solved in 6 | $0.03286096 | 2/2 / 2/2 / 2/2 |
| `amc12b_2002_p3` | failed in 20 requests → solved in 5 | $0.03150222 | 2/2 / 2/2 / 2/2 |
| `aime_1991_p9` | failed in 26 requests → solved in 23 | $0.00646206 | 2/2 / 1/2 / 0/2 |

For `imo_1960_p2`, historical non-ACE repeatedly attempted an incomplete
`Qed`. X3 first failed with `field_simplify` and Lean-style `calc` syntax,
then completed explicit inverse cancellation with `Rinv_r` and `nra`.
For `amc12b_2002_p3`, non-ACE hit malformed `change`, failed substitution
and unfinished proof obligations; X3 factored the expression, used primality
and divisibility bounds, and replaced unavailable `omega` with `lia`.
For `aime_1991_p9`, non-ACE stalled on trigonometric/square normalization;
X3 completed inverse cancellation, `sin2_cos2`, explicit `Rsqr` unfolding
and polynomial factorization. These are observed successful trajectories,
not proof that a particular playbook bullet caused the success.

Fresh non-ACE closes the first two historical misses consistently; fresh
X3 loses the third in both replicates. The ordinary baseline also solves
the third twice. Those reversals show why three historical discordant
problems cannot establish a stable coverage advantage. The full per-problem
export retains cheaper failures, expensive successes and losses as well.

The request comparison identifies a material configuration difference:

| Configuration | Historical non-ACE | Historical X3 | Fresh ordinary | Fresh matched | Fresh X3 |
|---|---:|---:|---:|---:|---:|
| Maximum output tokens | 32768 | 32768 | 32768 | 8192 | 8192 |
| Problems × replicates | 40 × 1 | 40 × 1 | 40 × 2 | 40 × 2 | 40 × 2 |
| Inference dollars | 0.77651210 | 0.66722836 | 1.53580888 | 2.13028512 | 2.04055918 |
| Solves | 24 | 27 | 51 | 49 | 52 |

The same X3 playbook text reaches the fresh generator. For every problem,
the complete initial chat and tools match between old non-ACE and each
fresh non-ACE arm, and between old X3 and fresh X3: **120/120 comparisons**.
Model and reasoning options remain Luna/medium. The only initial request
option difference is the output limit for the two 8192-token arms. This
does not establish equality of later adaptive continuations. The new policy
also adds recorded transport, pause handling and admission observations;
it does not add a non-ACE memory or tool. Historical claim objects are
inactive with advice admission and polished control disabled.

The lower cap changes more than maximum answer length. In
`runtime/campaign_budget.py`, the conservative next-request cost includes
the maximum output allowance. At the recorded output tariff, reducing
32768 to 8192 removes **$0.02949120 of output reservation per request**.
That can admit further search under the same nominal $0.10 budget. This
source mechanism is verified; its contribution to the outcome difference
has not been isolated by this follow-up.

In fresh matched runs, X3 saves **4.21%**, with 52 versus 49 solves out of
80. Its cache fraction is 72.12% versus 67.49%: the cache advantage narrows
from 11.26 to 4.62 percentage points. Undiscounted token cost is now 4.05%
higher under X3. The fresh net saving decomposes into $0.26117694 extra
cache discount minus $0.17145100 extra undiscounted token cost. This
accounts for the observed smaller saving without establishing which
change caused it. The selected new artifact's 4.97% saving is a separate
comparison and must not be substituted for X3's 4.21%.

Historical X3's 90% cost-ratio interval is [0.7456, 0.9662], with two-sided
p=0.0498; its coverage p=0.25. The interval supports neither a guaranteed
10% saving nor a stable coverage gain. Fresh X3's saving interval is
approximately [-5.58%, 13.45%], p=0.4904. These are nominal retrospective
development-data comparisons, not held-out confirmation or a formal test
that the old and new effects differ. Sampling variation, scheduling/cache
conditions and changed admission headroom remain entangled.

The defensible wording is: **“X3 achieved 14.07% lower inference spend and
24→27 solves on the historical 40-problem panel. A fresh study with a
lower output cap observed 4.21% saving against its matched control.
Reproduction of the historical configuration remains untested by that
fresh study.”** Claiming “X3 cannot reproduce its gain” goes beyond the
evidence. The remaining controlled-replication question is recorded in
local hint #136; this investigation makes no new paid calls.

Both harnesses reproduce the offline analysis from omphalos with
`python -m tools.reports.ace_x3_forensics`. It reads only explicit
validation cells, checks original raw hashes and reconciles receipts.
The [versioned evidence directory](../experiments/campaigns/ace_thesis_20260918/audit/x3_forensics/17ca3ce54b76afbf/)
contains the exact reporter source, [results](../experiments/campaigns/ace_thesis_20260918/audit/x3_forensics/17ca3ce54b76afbf/results.json),
[40 problem pairs with raw source paths](../experiments/campaigns/ace_thesis_20260918/audit/x3_forensics/17ca3ce54b76afbf/by_theorem.csv),
[1,410 repriced receipts](../experiments/campaigns/ace_thesis_20260918/audit/x3_forensics/17ca3ce54b76afbf/legacy_receipts.csv),
and [120 initial-request comparisons](../experiments/campaigns/ace_thesis_20260918/audit/x3_forensics/17ca3ce54b76afbf/requests.json).
The prior thesis report is retained there before adding the correction.
Original sealed study code, paid archives and analysis exports remain intact;
testX and protected challenge data remain closed.
