# Completed Luna attribution panel

Both panels contain 40 theorems and one replicate (seed 0). All 80 new
no-ACE episodes finished without infrastructure failure, at $1.59472272.
All 80 historical ACE references passed strict observed-request replay.

| Panel | No ACE solves | ACE solves | No ACE cost | ACE cost | ACE cost change |
|---|---:|---:|---:|---:|---:|
| trainX | 28/40 | 28/40 | $0.81821062 | $0.68922336 | −15.76% |
| validationX | 24/40 | 27/40 | $0.77651210 | $0.66722836 | −14.07% |

All current-panel solves qualify at $0.10. Validation cost per solve falls
from $0.032355 to $0.024712, a 23.62% reduction. The three validation gains
are `imo_1960_p2`, `aime_1991_p9`, and `amc12b_2002_p3`; there are no losses.
The paired coverage test has p=0.25: this is exploratory practical evidence,
not statistical support for a coverage gain. The descriptive family bootstrap
interval is +2.5 to +15 percentage points; its discrete percentile behavior
does not override the exact paired test. Training has four gains and four
losses, a zero net effect and −12.5 to +12.5-point descriptive interval.

ACE's paired mean cost change is −$0.002732 per validation problem
(90% interval −$0.005110 to −$0.000627; descriptive cost sign-flip p=0.0498).
Historical controls retain provider/time confounding. ValidationX has also
been repeatedly used for selection. Neither caveat disappears after replay.

The traces support a reduction in avoidable repair work. Requests fall from
439 to 388 on trainX and 497 to 447 on validationX; solves with no preceding
failed proof check rise from 8 to 14 and from 9 to 12. Across both panels,
first unknown-reference errors fall from 14 to 6 and first syntax errors
from 15 to 6. These counts describe trajectories, not a causal attribution
to individual bullets. Some ACE failures still spend many checks on witness,
proof-structure, arithmetic and resource problems.

The older X agentic baseline scored 33/40 and 27/40 in seed 0. Today's
no-book bounded/focused loop scores 28/40 and 24/40. This compound historical
contrast cannot isolate which control change caused the difference.
The matched ablation does show that removing ACE does not recover the older
baseline's coverage. The wider control architecture must remain part of the
explanation. See LINEAGE.md and historical_comparison.json.

The Terra adaptation and paired inference runs are still in progress.
No default has changed. Full results will be recorded in RESULTS.md.


The token-cost decomposition adds a material limit to the cost interpretation.
Validation ACE input is 5,876,690 versus 5,780,014 tokens without ACE, and
output is 245,341 versus 243,896. Cached-input fractions are 75.87% versus
64.61%. At the same observed token counts but charging every input token at
the uncached rate, costs would be $1.4697472 and $1.4486780: ACE is 1.45%
more expensive under that price sensitivity. The recorded $0.66722836
versus $0.77651210 remains the actual accounting result. This historical
comparison cannot isolate advice-driven cache reuse from provider/time/cache
conditions. Training still has lower output usage with ACE; its uncached-rate
sensitivity is $1.2575190 versus $1.2803698. No new uncached experiment was run.
See luna_pricing_sensitivity.json.
