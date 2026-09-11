# ACE mechanisms, 2026-09-10

Guille approved implementation of the balanced $10 plan. New campaign;
previous protocols and verdicts are unchanged. Both harnesses use
`python -m experiments.ace.ace_mechanisms_experiment`.

24 local cells (six fixed trainX states, F/C, full/explicit contract),
144 new trainX cells (S40, C40, R40, E24), and 80 validationX cells for
one selected contender. Reuse 16 E train cells, 40 flagship train cells
and 80 flagship validation cells. No new role calls, playbooks or advice.
No protected outcomes. Maximum 248 new cells, one infrastructure retry
only through a separately frozen cell manifest, never a logical retry.

S: explicit typed suffix/replacement continuation after verified feedback.
C: S plus one checked finite change/set/nra candidate per prefix/action.
R: C plus <=10s cached progress audits and at most one 4096-token recovery
following monetary refusal. Same dollar/request/verifier budgets; no
polished bundle, timeout recovery or restart. E: incumbent book with
xhigh prover only. Core, Responses, $0.10 and 64 requests for full proofs.

Budget allocations: local $0.50, training $4.50, validation $4.50, retry
$0.50. Unused funds stay unused; budget censoring precludes a verdict.
Paid cells run via OmphalosExperiment with frozen runtime profile, ledger,
no automatic retry, and immutable source/manifests. Stage completion precedes
report/selection; no arm elimination based on intermediate outcomes.

Primary: qualified solves at actual charged cost <=$0.10. Compare total
cost and cost/solve on complete panels. A practical improvement is extra
solves at <=20% extra cost and no worse cost/solve, or equal coverage at
lower cost. Rank by coverage, then cost. Otherwise permit one exploratory
trade-off losing <=1 train solve with >=10% improvement in cost and
cost/solve; otherwise stop after training. No minimum multi-solve pilot
hurdle or significance prerequisite. Freeze the winner before both
validation seeds. No automatic default promotion or new combinations.

Report paired theorem-family clustered 90% intervals, two-sided p-values,
per-seed results and actual invocation events. Historical controls are not
concurrent randomized evidence, and validationX remains development data.
Local progress is not full-problem coverage. Canonical checks provide
verification/control evidence, not newly demonstrated ACE learning.

Local full/explicit F and C arms use the same repair phase and ordinary
continuation effort. Explicit replacement is kernel-checked from the initial
state; useful full proof acceptance counts even if the prefix changed.
The historical full-prefix local rubric is retained in full arms.

Commands: prepare; run --stage=local --max_workers=24 --wait; report
--stage=local; likewise training, then validation if selection.json names
an arm. All API spend, including any failed requests, belongs to this ledger.
