# Reassessment after Guille's quality clarification

**ACE with session reset meets the observed 10% inference-cost target.**
Its 50/80 proofs cost $1.50046594, versus non-ACE reset's 50/80 for
$1.67739662: **10.55% less**. Smaller tool displays are also a promising
efficiency improvement. Both were previously penalized by an incorrectly
inferred requirement to preserve proof counts on every replicate.

Guille clarified on 2026-09-16:

> with quality, I meant quality in the code and your implenmenttations.
> Please reasses and correct all the statements and results that have
> been good but have failed this strong criteria

That clarification supersedes the coverage veto in the current assessment.
Quality means robust, maintainable implementations, correct proof checking,
faithful accounting and reproducible evaluation. Coverage remains a useful
outcome, reported with total cost and cost per solve; it is not an automatic
per-replicate acceptance condition. No new benchmark cells, configurations
or paid runs are introduced by this retrospective interpretation change.

| Comparison | Proofs: reference → candidate | Total cost change | Cost/solve change | Corrected interpretation |
| --- | ---: | ---: | ---: | --- |
| Non-ACE reset → ACE reset | 50 → 50 | −10.55% | −10.55% | Observed budget target achieved; promising |
| Plain ACE → ACE reset | 46 → 50 | +1.78% | −6.36% | Leading advisor intervention |
| Plain ACE → smaller displays | 46 → 49 | +1.73% | −4.50% | Promising additional efficiency candidate |
| Plain non-ACE → non-ACE reset | 47 → 50 | +12.11% | +5.38% | Positive coverage-cost trade-off |
| ACE $0.10 → ACE $0.20 | 46 → 53 | +114.44% | +86.11% | Useful coverage headroom, with a substantial cost premium |
| Non-ACE $0.10 → ACE $0.10 | 47 → 46 | −1.47% | +0.67% | Below the 10% savings target |
| Non-ACE $0.20 → ACE $0.20 | 53 → 53 | −0.34% | −0.34% | Below the 10% savings target |

All comparisons contain 80 attempts on the same 40 validationX problems
with two replicates. Costs include unsuccessful attempts. The reset result
was 25/25 ACE proofs versus 24/26 non-ACE; smaller displays gave 23/26 versus
24/22 for plain ACE. These variations stay visible, but no longer turn the
aggregate improvements into failures. The larger budget's old cost/solve
bound also remains historical: its coverage gain is useful even though it
is not an economy improvement. Larger allowances improve non-ACE too, from
47 to 53 proofs; this is not an ACE-specific coverage effect.

**Statistical uncertainty has not changed.** For matched reset, the cost
ratio is 0.894521, 90% CI [0.793087, 1.008002], with two-sided p=0.136499.
The observed savings are practically promising without meeting p<0.10.
We have achieved the target on this panel, not established a general
10% reduction. The smaller-display coverage p is 0.25; the ACE reset
coverage p is 0.359375. Statistical labels describe strength of evidence,
not whether an intervention deserves further consideration. Reused
validation, selection, historical controls and exploratory comparisons
still limit generalization; equal proof counts do not establish equivalence.

Caching also matters. ACE reset has a 76.78% cached-input fraction versus
68.36% for non-ACE reset. Offline repricing of their same token traffic
without caching makes ACE 6.96% more expensive. Historical book preparation
adds at least $1.36785368 before embeddings, requiring separate amortization.
Thus the 10.55% result concerns the observed inference setting.

The three campaign reports and READMEs now use these current interpretations.
Their original JSON gate outputs and sealed drivers remain unchanged as
history. [Current machine-readable results](results.json) explicitly retain
those labels under `legacy_only`; they never use per-replicate coverage as
a veto. This is an authorized retrospective amendment, not a relabeled
preregistration. No default is promoted and no further experiment is scheduled.

Both Codex and Claude Code regenerate the current decisions offline:

```sh
python -m tools.reports.ace_economy_reassessment
python -m pytest -q tests/test_economy_reassessment.py
```

The generator reads six explicitly named validation-only exports, records
their byte hashes, and imports no model, partition loader or experiment
driver. It preserves the original uncertainty estimates. Existing exact
replay certificates cover all 560 paid runs; implementation, accounting and
proof validity requirements remain in force. New reassessment cost is
**$0**. The combined study spend remains **$13.98159180 / $50**.

Twelve focused reassessment tests pass, including withdrawal of the
replicate veto, independent reporting of coverage loss and cost savings,
missing-cell rejection, invalid costs and rejection of unknown sources
before file reads. All three touched Python files pass pinned Pyright
1.1.406 and Ruff; dual-harness invariants pass. Root `make pyright` retains
17 preexisting `why3py.simple` errors outside Omphalos. Global partition
tests and repricing remain excluded. See [verification](checks.json).

Original campaign reports: [main study](../RESULTS.md),
[matched budget](../../ace_economy_budget_20260916/RESULTS.md), and
[matched reset](../../ace_economy_session_20260916/RESULTS.md).
