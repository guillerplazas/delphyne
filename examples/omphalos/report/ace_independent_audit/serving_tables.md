## Full-panel serving results

Each row contains forty problems and two paid replicates. Costs
include every failed attempt. Solves and cost per forty are averages
over the two replicates; the underlying totals are preserved in CSV.
Online rows report solver inference only; their update bills appear
separately. Their two replicates are sequential learning orders,
so theorem-bootstrap intervals are descriptive: they do not model
dependence propagated through the changing book. R1 is a manual
trainX diagnostic. These are reused
development partitions, with no untouched confirmation claim.

One trainX B1 timeout has an unknown bill with a retained upper
bound: its cost and saving are ranges. Scalar CSV costs use the
upper liability; affected uncertainty intervals cover both billing
endpoints, and their cost p-values are omitted.

### trainX

| Arm | Solved / 40 | Cost / 40 | Cost / solve | Saving vs matched control |
|---|---:|---:|---:|---:|
| A0: Ordinary assisted | 31.5 | $0.8574 | $0.0272 | — |
| A1: Historical X5 | 33.5 | $0.8181 | $0.0244 | +4.6% |
| A2: Full Sol book | 30.5 | $0.8547 | $0.0280 | +0.3% |
| S1: Full Luna book | 31.5 | $0.8518 | $0.0270 | +0.7% |
| P1: Short Sol pilot book | 29.5 | $0.8725 | $0.0296 | -1.8% |
| O1: Adaptive then frozen | 32.0 | $0.7462 | $0.0233 | +13.0% |
| R1: Three verified rule repairs | 33.0 | $0.7909 | $0.0240 | +7.8% |
| B0: Ordinary plain | 30.5 | $0.9056 | $0.0297 | — |
| B1: Plain-source Sol book | 32.5 | $0.8255–$0.9367 | $0.0254–$0.0288 | [-3.4, +8.8]% |
| B2: Teacher-evidence Sol book | 33.0 | $0.9062 | $0.0275 | -0.1% |
| online_A2: Online assisted | 32.0 | $0.8108 | $0.0253 | +5.4% |
| online_B1: Online plain | 32.0 | $0.8666 | $0.0271 | +4.3% |
| online_B2: Online teacher | 32.0 | $0.8959 | $0.0280 | +1.1% |

### validationX

| Arm | Solved / 40 | Cost / 40 | Cost / solve | Saving vs matched control |
|---|---:|---:|---:|---:|
| A0: Ordinary assisted | 28.0 | $0.8772 | $0.0313 | — |
| A1: Historical X5 | 28.5 | $1.0003 | $0.0351 | -14.0% |
| A2: Full Sol book | 26.0 | $0.9573 | $0.0368 | -9.1% |
| S1: Full Luna book | 27.5 | $0.9780 | $0.0356 | -11.5% |
| P1: Short Sol pilot book | 25.0 | $0.8527 | $0.0341 | +2.8% |
| O1: Adaptive then frozen | 28.0 | $0.8373 | $0.0299 | +4.5% |
| B0: Ordinary plain | 24.5 | $0.9314 | $0.0380 | — |
| B1: Plain-source Sol book | 24.5 | $1.1987 | $0.0489 | -28.7% |
| B2: Teacher-evidence Sol book | 26.0 | $0.9011 | $0.0347 | +3.2% |

### Paired uncertainty

Intervals are percentages. Theorem clustering retains both
replicates; broader proof-method families provide a sensitivity
analysis. Positive savings mean ACE is cheaper. Intervals and
unadjusted sign-flip p-values describe uncertainty, not a promotion
gate. The CSV also supplies leave-one-theorem-out sensitivity.

| Partition / arm | Saving | Theorem 90% interval | Family 90% interval |
|---|---:|---:|---:|
| trainX / A1 | +4.6% | [-16.7, 22.3] | [-16.7, 19.1] |
| trainX / A2 | +0.3% | [-24.4, 20.5] | [-25.1, 20.2] |
| trainX / S1 | +0.7% | [-22.0, 20.9] | [-24.8, 19.1] |
| trainX / P1 | -1.8% | [-25.0, 17.8] | [-28.0, 19.2] |
| trainX / O1 | +13.0% | [-1.5, 26.1] | [-2.9, 24.5] |
| trainX / R1 | +7.8% | [-15.2, 26.8] | [-19.3, 26.5] |
| trainX / B1 | [-3.4, 8.8] | [-35.2, 28.5] | [-31.5, 29.9] |
| trainX / B2 | -0.1% | [-22.0, 20.6] | [-25.9, 26.6] |
| trainX / online_A2 | +5.4% | [-15.3, 22.8] | [-21.4, 21.7] |
| trainX / online_B1 | +4.3% | [-14.8, 20.8] | [-17.8, 22.1] |
| trainX / online_B2 | +1.1% | [-15.9, 16.5] | [-16.9, 17.2] |
| validationX / A1 | -14.0% | [-41.3, 8.2] | [-34.2, 10.0] |
| validationX / A2 | -9.1% | [-42.0, 17.4] | [-23.4, 5.8] |
| validationX / S1 | -11.5% | [-32.4, 8.4] | [-34.5, 7.8] |
| validationX / P1 | +2.8% | [-18.8, 19.5] | [-15.0, 15.8] |
| validationX / O1 | +4.5% | [-10.1, 16.6] | [-4.7, 14.0] |
| validationX / B1 | -28.7% | [-58.2, -4.1] | [-62.8, -0.5] |
| validationX / B2 | +3.2% | [-24.0, 24.9] | [-23.8, 26.7] |
