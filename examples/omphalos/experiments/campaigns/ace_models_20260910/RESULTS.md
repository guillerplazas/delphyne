# ACE model suite results — 2026-09-10

**Retain ACE bounded money + focused.** The campaign completed its registered
selection stage for **$8.71724000**. Neither challenger passed the required
gain of two qualified solves on 24 problems. No winner was frozen, so the
320-cell full trainX/validationX allocation was not spent. This is a no-go
under the registered gate, not proof that these configurations are equivalent.

## Selection on 24 trainX problems

Every arm has all 24 expected cells, one replicate, 24 theorem families.
All proof controls are unchanged. Each candidate uses an offline-warmed
playbook and the Luna-xhigh prover; curation/reduction is Luna-medium and
audit is off. The flagship uses its original playbook and Luna-medium prover.

| Arm | Qualified solves | Inference cost | Cost/solve | Cost ratio | Gate |
|---|---:|---:|---:|---:|---|
| Flagship | 17/24 | $0.371964 | $0.021880 | 1.000 | Reference |
| Luna-medium reflector | 16/24 | $0.361562 | $0.022598 | 0.972 | Fail |
| Luna-xhigh reflector | 18/24 | $0.323741 | $0.017986 | 0.870 | Fail |

The better challenger gains one solve and reduces aggregate inference cost
by 12.96% and cost/solve by 17.80%. It passes both cost gates but needs
19/24 solves to pass selection. The other candidate loses one solve and
worsens cost/solve despite slightly lower total cost.

The better challenger has two wins and one loss versus the flagship.
Descriptive family-cluster inference gives p=1.00 for coverage, with a
90% effect interval of −8.33 to +16.67 percentage points. Its cost ratio
90% interval is 0.758–1.031; paired cost p=0.192. The mean paired saving is
$0.002009/problem (90% interval −$0.000375 to $0.004465). It is cheaper
on 9 problems and dearer on 15: aggregate savings depend on the larger
differences. These analyses were added after selection for uncertainty
reporting; they do not change the registered decision rule or establish
equivalence. See [selection uncertainty](selection_uncertainty.json).

## Prover and offline-role screens

| Luna prover effort | Qualified solves | Total inference cost | Cost/solve |
|---|---:|---:|---:|
| low | 9/16 | $0.321243 | $0.035694 |
| medium | 11/16 | $0.317260 | $0.028842 |
| high | 10/16 | $0.273304 | $0.027330 |
| xhigh | 11/16 | $0.266519 | $0.024229 |

Xhigh tied medium at 16.0% less cost; both advanced. Xhigh gained only
one solve over high, so the prover max gate stayed closed.

All 23 standard offline playbooks were evaluated on the same eight
screening problems with Luna-xhigh proof generation. Entries below are
qualified solves / total downstream inference dollars; offline preparation
is separate. Each arm changes only the named role from the common control.

| Role | Setting | Low | Medium | High | Xhigh |
|---|---|---:|---:|---:|---:|
| Reflector | Luna | 4/8 / $0.1263 | 5/8 / $0.0993 | 4/8 / $0.1417 | 5/8 / $0.1070 |
| Reflector | Terra | 4/8 / $0.1303 | 5/8 / $0.1232 | 4/8 / $0.1372 | 5/8 / $0.1296 |
| Curator | Luna | 5/8 / $0.1338 | 5/8 / $0.0993 | 5/8 / $0.1558 | 4/8 / $0.1214 |
| Curator | Terra | 5/8 / $0.1206 | 4/8 / $0.1362 | 5/8 / $0.1379 | 4/8 / $0.1584 |
| Auditor | Luna | 4/8 / $0.1297 | 5/8 / $0.1139 | 4/8 / $0.1551 | 4/8 / $0.1268 |
| Auditor | Terra | 3/8 / $0.1556 | 5/8 / $0.1657 | 4/8 / $0.1473 | 3/8 / $0.1533 |

The common control (Luna-medium reflector and curator/reducer, audit off)
solved 5/8 for $0.099295. Every role retained that control under the gates;
all three role max gates stayed closed. No new pair/triple recipe was
needed. Two additional eight-cell checks crossed the leading books with
the Luna-medium prover. The two cheapest eligible screening candidates
advanced, including the xhigh-reflector arm despite its losing to the
common control within the reflector sweep. Terra brought no observed
coverage gain on this small panel; this is not a universal model ranking.

## Spend and preparation

| Stage | Actual API cost | Requests, including embeddings |
|---|---:|---:|
| adaptation | $3.07100108 | 276 |
| prover | $1.17832530 | 759 |
| screening | $3.10613818 | 2045 |
| selection | $1.36177544 | 886 |

Total: 336 proof cells, 226 role/grounding cells, 3,966 settled API receipts,
zero platform failures, zero infrastructure retries, zero unknown charges.
The 336 proof cells comprise 64 prover, 184 standard-role screening,
16 cross-check and 72 selection cells. Compatible completed cells are
counted once. No max, final trainX, validationX, testX or protected challenge
cells were added. Estimated full-suite spend was $15–25 with a $30 ceiling;
the no-go rule leaves the unused budget unspent.

Incremental preparation below includes the eight new source trajectories
($0.16293180) and the selected recipe’s role DAG. Historical incumbent
training is shared and sunk. Exploratory sweep spend is separate.

| Candidate reflector | Role DAG | With source | Cost/problem at 100 uses | At 1,000 uses |
|---|---:|---:|---:|---:|
| medium | $0.040082 | $0.203013 | $0.017095 | $0.015268 |
| xhigh | $0.087000 | $0.249932 | $0.015989 | $0.013739 |

Amortization uses this small selection panel’s inference mean; it is not a
measured full-partition deployment cost. Neither recipe is promoted.

## Implementation and evidence

The shared campaign CLI provides hash-pinned configurations, independent
auditor routing, immutable stage manifests, cached role DAGs, monetary
reservations, token-based receipts, conditional expansion, selection and
the gated final benchmark. Original proof defaults are preserved.

Omphalos `make test`, ten new regression tests, Ruff and repricing passed.
New code passes pinned Pyright 1.1.406. Root Pyright has 17 existing
`why3py.simple` errors; the existing adaptation module has 21 identical
errors before and after the auditor-routing change. See [checks](checks.json).

[Protocol](README.md), [selection](selection_report.json),
[final report](final_report.json), [receipts](receipts.csv), and
[scheduling amendment](scheduling_amendment.json) preserve the decision
and accounting. Detailed source caches remain in the frozen output archive.
Any follow-up must use a new registered design; this campaign is complete.
