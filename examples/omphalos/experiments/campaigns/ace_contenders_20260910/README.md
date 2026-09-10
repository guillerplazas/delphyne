# Both ACE contenders — 2026-09-10

**Completed: 160/160 new cells for $2.601557.** Xhigh reflection is the
stronger contender: trainX 27/40 vs flagship 28/40, validationX 24/40 vs
27/40, at 15.6%/12.2% lower inference cost. This is a cost/coverage
trade-off, not a coverage upgrade. See [results](RESULTS.md).

Guille explicitly authorized both assembled contenders, then clarified:
**160 new cells; reuse existing flagship results.** One seed (0), forty
trainX and forty validationX problems for each contender. No fresh flagship
cells, second seed, adaptation or screening gate. Original model-suite
measurements and its registered no-go remain historical evidence.

| Arm | Prover | Reflector | Curator/reducer | Auditor |
|---|---|---|---|---|
| Existing flagship | Luna medium | Incumbent recipe | Incumbent recipe | Off |
| Reflector-medium | Luna xhigh | Luna medium | Luna medium | Off |
| Reflector-xhigh | Luna xhigh | Luna xhigh | Luna medium | Off |

Both contender books are reused exactly from ace_models_20260910. Money
and focused are on; admission, restart and polished are off. All token,
request, verifier and operation limits remain unchanged. No new role calls.

Historical trainX controls use the complete incumbent Luna-medium cells
from the model suite (source/screen sixteen, selection twenty-four).
ValidationX uses the complete seed-0 reference arm of ace_polish_validation.
Reference choice is fixed by configuration, partition and seed, not outcome.
Each reference's result/cache, receipt-derived cost and effective arguments
are checked before freezing. The validation archive has a different claims
artifact, but claims are unused with admission and polished both off;
all remaining strategy/policy arguments match exactly. These are historical
controls, not concurrent randomization. No testX or protected outcomes.

New API cost estimate: **$3–5**, subceiling **$6** (benchmark $5.50, reserve
$0.50), within the original $30 combined authorization after $8.71724
already spent. No automatic logical-failure retries. At most four explicitly
recorded infrastructure retries can use the reserve. Unknown charges retain
liability. Censored/missing panels are incomplete, never a negative finding.

Primary outcomes are qualified solves at actual total cost <=$0.10, total
inference cost and cost per qualified solve on each full partition. Report
paired family-clustered 90% descriptive intervals. Two validation coverage
comparisons against flagship use Holm-adjusted p<.10 for statistical support.
TrainX, candidate-to-candidate and cost inference are descriptive. Historical
control limitations and repeated validation development exposure remain
explicit. Do not treat significance as a prerequisite for practical value.

Report any positive coverage gain within <=1.20 cost ratio and no worse
cost/solve, or lower cost with no coverage loss. No fixed +4-solve gate.
Report coverage/cost trade-offs and inconsistent partition outcomes plainly.
The benchmark does not automatically change defaults or buy extra seeds.

Both harnesses use the same CLI from examples/omphalos:

```sh
python -m experiments.ace.ace_contender_benchmark prepare
python -m experiments.ace.ace_contender_benchmark run --max_workers=24 --wait
python -m experiments.ace.ace_contender_benchmark report
python -m experiments.ace.ace_contender_benchmark status
```

Run in tmux on i34-gpu01. The shared Omphalos launcher provides stream slots,
per-directory locking and supervision. The immutable manifest contains
exactly 160 paid configurations; references.json contains eighty reused
observations. Hashes pin playbooks, source code, statements and references.
The accounting ledger reserves each request and reconciles actual tokens.
