## Completed forty-problem replicates

These are individual complete replicates, not the registered pooled
two-replicate comparison. Each cost includes all forty attempts.
Positive savings mean lower cost than the matching non-ACE control.
Online rows exclude their separately reported learning fees.

| Partition / arm / replicate | Solves | Cost | Cost / solve | Requests | Saving | 90% interval |
|---|---:|---:|---:|---:|---:|---:|
| train/A0/replicate1 | 32/40 | $0.73607 | $0.02300 | 520 | — | — |
| train/B0/replicate1 | 30/40 | $0.90694 | $0.03023 | 574 | — | — |
| train/R1/replicate0 | 32/40 | $0.70628 | $0.02207 | 476 | — | — |
| train/R1/replicate1 | 34/40 | $0.87545 | $0.02575 | 505 | -18.9% | [-58.7, 10.1] |
| train/online_A2/replicate1 | 31/40 | $0.78697 | $0.02539 | 533 | -6.9% | [-30.0, 11.3] |
| train/online_B1/replicate1 | 32/40 | $0.94524 | $0.02954 | 501 | -4.2% | [-42.9, 25.9] |
| train/online_B2/replicate1 | 31/40 | $0.95302 | $0.03074 | 528 | -5.1% | [-35.5, 19.2] |
| validation/A0/replicate0 | 28/40 | $0.85130 | $0.03040 | 566 | — | — |
| validation/A1/replicate0 | 29/40 | $1.12215 | $0.03869 | 536 | -31.8% | [-82.8, 4.1] |
| validation/A2/replicate0 | 25/40 | $1.09481 | $0.04379 | 590 | -28.6% | [-83.2, 11.3] |
| validation/B0/replicate0 | 25/40 | $0.90755 | $0.03630 | 681 | — | — |
| validation/B1/replicate0 | 26/40 | $1.15579 | $0.04445 | 647 | -27.4% | [-71.2, 7.1] |
| validation/B2/replicate0 | 25/40 | $1.01230 | $0.04049 | 619 | -11.5% | [-42.3, 13.6] |

Intervals cluster by theorem; the CSV also reports broader
proof-method-family intervals. Neither an interval nor a replicate's
solve loss is used as an extra acceptance veto. R1 replicate zero
has no complete matching control at this checkpoint.
