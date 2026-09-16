# Matched ACE attribution with a larger allowance

**Current interpretation:** the user's quality requirement concerns code
and implementation quality; the per-replicate coverage veto is withdrawn.
See [the reassessment](../ace_economy_20260916/reassessment/README.md).
Both harnesses generate current decisions with
`python -m tools.reports.ace_economy_reassessment`. The sealed protocol and
original report command below reproduce historical gate outputs.

**validationX only; never access testX.** The latest scope correction
revokes the unrun draft's optional held-out phase. This protocol was frozen
before any new follow-up cell was dispatched.

The original advisor budget arm produced 53/80 proofs versus 46/80 at
2.144 times cost, a useful coverage-cost trade-off. Its original efficiency
gate is historical, not a rejection of the observed coverage gain. The new
question is whether ACE saves money when **both** agents receive $0.20.
No output cap, prompt, learned book or additional controller changes.

Reuse the 80 ACE validation cells already paid for. Run exactly 80 new
non-ACE validation cells: 40 theorems, two replicates. No extra seed,
contender, held-out phase or automatic paid retry. The original target added
no pooled or per-replicate coverage loss to at least 10% savings; the
clarification removes that automatic veto. Report coverage, cost/solve and
uncertainty separately. This is exploratory
attribution on reused validation data with controls from hours earlier.

The same **combined $50 authorization** covers this and the main campaign.
After all 400 main cells settled at $9.13201958, the follow-up received a
$16 ledger ceiling (80 x $0.20), fitting the remaining authorization. The
main campaign makes no more paid calls. Conservative HTTP reservations
bound liability, and the driver rejects a change in settled main charges.
The spending ceiling is not a target.

Both harnesses run these from `examples/omphalos`:

```sh
python -m experiments.ace_economy_budget_experiment prepare
python -m experiments.ace_economy_budget_experiment validation
python -m experiments.ace_economy_budget_experiment report
python -m tools.analysis.replay_economy --campaign budget --batches validation --assemble
```

Paid work runs in tmux through `launch.sh`, using the same supervised
24-worker/32-slot runtime and one attempt. Completed batches are immutable.
The follow-up verifier uses the validation-only main seal; the obsolete
main verifier is never called. No default changes are made.

Report equal-cap inference cost, qualified coverage, cost/solve, paired
family-clustered 90% intervals, two-sided p-values, uncached sensitivity,
and historical book preparation separately. `results.json` contains the
original pooled observed target. The current report applies the user's
clarification, without a per-replicate veto. The protocol, dated receipts,
cell export and cache replay records retain the evidence.
