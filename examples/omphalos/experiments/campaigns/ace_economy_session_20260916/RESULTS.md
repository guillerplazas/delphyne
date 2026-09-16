# Matched session reset: ACE versus non-ACE

**With the same session reset, ACE solves 50/80 for $1.50046594; non-ACE
solves 50/80 for $1.67739662. ACE is 10.55% cheaper on this pooled panel.**
This is the first matched comparison in this study whose pooled inference
cost reaches the intended 10% reduction while matching the total proof
count. The complete preregistered gate still fails: ACE loses one proof on
one replicate. The cost difference is also statistically inconclusive.

The requested 80 new non-ACE runs completed in approximately **12m 50s**.
New API cost is **$1.67739662**; all three economics campaigns together have
spent **$13.98159180 / $50**, leaving **$36.01840820**. No additional ACE run
was purchased. All new runs use validationX, with zero platform failures,
missing cells, cap crossings or unresolved charges. testX remains closed.

| Configuration ($0.10 allowance) | Proofs | All-attempt cost | Cost / proof |
| --- | ---: | ---: | ---: |
| Non-ACE, no reset | 47/80 | $1.496212 | $0.031834 |
| ACE, no reset | 46/80 | $1.474255 | $0.032049 |
| Non-ACE, same reset **(new)** | 50/80 | $1.677397 | $0.033548 |
| ACE, same reset | 50/80 | $1.500466 | $0.030009 |

Each row contains the same 40 validationX problems with two replicates.
The new row was compared to existing paid controls; these are 40 theorem
families, not 80 independent problems. Model, tools, monetary allowance,
output allowance, verifier limits and reset algorithm are identical between
the two reset arms. Their only proof-search input difference is the frozen
v2 playbook. The thresholds remain eight interaction groups and 24,000
visible history characters, with the full checked proof prefix retained.

**Primary comparison: ACE reset versus non-ACE reset.**
The total cost ratio is **0.894521**, with family-clustered 90% CI
**[0.793087, 1.008002]** and two-sided cost **p=0.136499**. The interval spans
no saving, and p is above the registered 0.10 threshold. The per-attempt
mean cost difference is -$0.002212, 90% CI [-$0.004607, +$0.000145].
Observed pooled coverage is identical; coverage p=1.0 and the descriptive
90% effect interval is [-6.25, +6.25] percentage points. Equal counts do not
establish statistical equivalence.

| Replicate | Non-ACE reset proofs | ACE reset proofs | Non-ACE cost | ACE cost |
| --- | ---: | ---: | ---: | ---: |
| 0 | 24/40 | 25/40 | $0.826125 | $0.796955 |
| 1 | 26/40 | 25/40 | $0.851272 | $0.703511 |

ACE costs less on both replicates, but the coverage changes are +1 and -1.
Thus the **pooled cost/coverage criterion passes descriptively**, while the
**original no-per-replicate-loss gate fails**. Neither its gate nor the
older no-reset verdicts are relabeled. This remains promising exploratory
validation evidence; no default is promoted.

**Secondary comparison: does resetting help non-ACE?**
The reset raises observed coverage from 47/80 to 50/80, while cost rises
**12.11%** and cost/proof rises **5.38%**. Per-replicate coverage goes from
24/23 to 24/26, meeting the practical quality/cost gate. Coverage p=0.5;
cost p=0.130499, cost-ratio 90% CI [0.989106, 1.255222]. The reset's benefit
in this empty-book run is more observed proofs at greater expense.
For comparison, the earlier ACE reset improved 46 to 50 proofs for 1.78%
more cost, with inconclusive coverage p=0.359375.

**Measured mechanism and limits.**
The new non-ACE arm resets 35/80 conversations, removing a median 20,618
visible characters per reset; the ACE arm reset 32/80. Final declined
requests cite money in 25 cases and verifier time in five. These diagnostics
do not grant additional resources or modify the complete proof state.

ACE reset uses 560,861 output tokens versus non-ACE reset's 639,045. Its
cached-input fraction is 76.78% versus 68.36%. Dollar decomposition is:

| Reset arm | Fresh input | Cached input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| Non-ACE | $0.748796 | $0.161746 | $0.766854 | $1.677397 |
| ACE | $0.621795 | $0.205638 | $0.673033 | $1.500466 |

Caching matters to the economics. Repricing the same token traffic with
zero cached tokens gives ACE $3.351209 versus non-ACE $3.133113: ACE would
cost 6.96% more under that sensitivity. This is an offline price calculation,
not an uncached experiment. Historical playbook preparation still adds at
least $1.36785368 before embeddings and must be amortized separately.
The $50 experiment accounting includes only new calls, without recharging
old controls or historical preparation.

ValidationX was reused for development and for selecting the ACE reset
among earlier interventions; the fresh non-ACE control was run later. Those
selection, timing and caching limitations prevent a confirmatory claim.
The result supports studying this configuration further, while preserving
both the original quality gate and the uncertainty estimates. No additional
arms, seeds or data partitions were added to pursue significance.

[Full statistics](results.json), [all 320 matched/reused cells](cells.csv),
[diagnostics](analysis/diagnostics.json), [dated new receipts](analysis/receipts.csv),
[new outcomes and full proof values](analysis/outcomes.json), and
[archive hashes](analysis/archives.json) preserve the evidence. The original
three paid controls remain in the [main campaign](../ace_economy_20260916/RESULTS.md).
Raw caches, transport snapshots and ledgers remain locally archived.

Eight focused tests pass, covering treatment identity, scope rejection and
the joint budget. Both new Python files pass pinned Pyright 1.1.406 and Ruff;
dual-harness invariants pass. Root `make pyright` retains 17 preexisting
`why3py.simple` errors outside Omphalos. Global partition tests and repricing
were excluded to preserve the closed dataset. The initial preflight budget
fixture correction is recorded in [the pre-dispatch revision](preflight_revision.json),
with zero paid calls before the correction and no runtime/treatment change.

The [exact replay certificate](replay.json) checks all 80 new outcomes,
proof values and budget states with HTTP blocked. The 240 reused control
cells already passed replay in the main campaign. Receipt repricing is
scoped to the allowed campaigns and matches their dated token records.
