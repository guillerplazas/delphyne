# Non-ACE with the same session reset

This user-requested follow-up completes the missing matched control for the
promising ACE reset result: 50/80 proofs at $1.50046594. Use **validationX
only**; never access testX or its metadata, hashes, caches or mixed reports.

Add exactly 80 non-ACE reset runs: the same 40 problems, two replicates,
$0.10 allowance, Luna medium, 64 requests, 300 verifier seconds, 8192-byte
displays and 32768 output tokens. Instantiate the frozen ACE-reset config
and remove only its book, changing output/archive paths for the new run.
The existing reset implementation and thresholds are reused unchanged.

Reuse all 80 ACE-reset cells for the primary comparison and both original
80-cell no-reset controls for the secondary analysis. No extra ACE cells,
seeds, thresholds or automatic retries. The same **combined $50 ceiling**
covers all three economics campaigns. Earlier charges are $12.30419518;
this ledger reserves a maximum of $8 (80 x $0.10), fitting the remainder.
The spending ceiling is not a target; earlier campaigns make no paid calls.

Primary question: does ACE with reset beat non-ACE with the same reset?
The savings target remains at least 10% with no pooled or per-replicate
coverage loss. Secondary question: does the reset improve non-ACE itself?
Report quality, all-attempt cost, cost/solve, paired family-clustered 90%
intervals and two-sided p-values. The practical reset gate requires no
per-replicate quality loss and either 10% savings or two more proofs with
cost/solve at most 1.25x reference. Original campaign gates remain intact.
Reused validation and historical controls limit inference. No default is
promoted, and no held-out confirmation is performed.

From `examples/omphalos`, both Codex and Claude Code use:

```sh
python -m pytest -q tests/test_economy_session.py
python -m experiments.ace_economy_session_experiment prepare
python -m experiments.ace_economy_session_experiment validation
python -m experiments.ace_economy_session_experiment report
python -m experiments.ace_economy_session_experiment export
python -m experiments.ace_economy_session_experiment replay
```

Run the paid phase in tmux through `launch.sh`. It uses the standard
supervised 24-worker/32-slot launcher, one attempt and the existing
conservative HTTP reservation. Completed batches and sealed inputs are
immutable. The new seal includes the existing **validation-only** seals;
the obsolete original mixed-scope verifier is never called.

Exact replay blocks HTTP and compares outcomes, proof values and budgets.
Exports retain dated provider token receipts, all cell outcomes, proof
values and hashes of local raw caches/snapshots. Prices are reconstructed
from dated repository rates, not an independently fetched provider invoice.
