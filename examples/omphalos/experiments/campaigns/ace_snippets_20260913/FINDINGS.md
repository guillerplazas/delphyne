# Rocq snippets: implemented, exercised, not promoted

The opt-in flagship prover tool works, but its observed coverage/cost trade-off
is unfavorable. The checked-writing variant did not create a different book.
The registered campaign is complete; no seed-1 or fresh-control extension ran.

| Complete panel | Incumbent qualified solves | Tool A qualified solves | Incumbent cost | A cost | Incumbent cost/solve | A cost/solve |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| trainX, 20 problems, seed 0 | 12/20 | 10/20 | $0.50783622 | $0.57996846 | $0.042320 | $0.057997 |
| validationX, 40 problems, seed 0 | 27/40 | 23/40 | $0.66722836 | $0.88657336 | $0.024712 | $0.038547 |

A retained the frozen X3 book, Luna-medium model, $0.10/64-request/300-Rocq-second
limits and existing bounded/focused controller. It added the Rocq snippet tool,
versioned instructions and two source-family-excluded demonstrations. B would
use exactly A's prover with a checked eight-source book update.

Validation coverage difference is -10 percentage points, descriptive 90%
family-bootstrap interval [-20, 0] points, two-sided paired p=0.21875;
the preregistered three-contrast Holm-adjusted p is 0.65625. This does not
establish a coverage regression statistically. Recorded inference cost is
32.9% higher, ratio 90% interval [1.126, 1.609], paired cost p=0.00858.
The mean per-cell cost increase is $0.005484, 90% interval [$0.002310,
$0.008767]. These are paired historical comparisons, not fresh randomized
confirmation. ValidationX remains repeatedly reused development data.

A misses both practical expansion conditions: it loses four solves and costs
more. B fails the changed-book exposure gate. No default or frozen book changed.
The absence of B comparisons is explicit; it is not a zero-effect B verdict.
The two unavailable B p-values are treated as 1 only for conservative Holm
bookkeeping, not as measured tests. Original gates were retained.

## What the tool actually did

`CheckRocqSnippet(context_id, snippet)` runs the complete raw snippet in a
source-bound, unassisted Rocq Compute operation. It distinguishes syntax/type
rejection, valid fragments with remaining obligations, complete Qed-accepted
proofs, resource exhaustion and unavailable evidence. A tool-completed proof
returns immediately; the existing terminal-evidence extractor preserves it.
The strategy enforces the existing financial/verifier budgets, a four-probe
interaction allowance and receipt reuse for identical probes.

| Measured exposure | trainX A | validationX A |
| --- | ---: | ---: |
| Cells with real Rocq snippet execution | 9/20 | 13/40 |
| Model snippet requests | 21 | 35 |
| Distinct checks, including local input rejection | 20 | 35 |
| Rejected checks | 9 | 24 |
| Of those, syntax-classified errors | 2 | 5 |
| Executed open fragments | 9 | 6 |
| Complete proofs returned inside the tool | 2 | 2 |
| Resource-exhausted checks | 0 | 2 |
| Unknown Rocq evidence | 0 | 1 |

One training rejection was the existing proof-bypass guard, before any Rocq
RPC. The other 19 training checks and all 35 validation checks reached Rocq.
There was one repeated training tool request, served from its receipt without
extra Rocq work. Repetition counts come from unique transport responses;
strategy-side event records can recur during Delphyne tree reconstruction.
An unknown Rocq verdict is not an unknown API charge.

The mechanism therefore reaches real cases and catches invented syntax/names.
It does not prevent every erroneous proposal or prove a net coverage benefit.
The two training tool-completed proofs were existing comparator solves;
completion inside the tool must not be equated with additional coverage.

## Writing result and the reducer follow-up

All 18 writing jobs completed: eight reflectors, eight curators and two
reducers. Each received the tool and returned after one model request. None
called it, none created a checked snippet receipt, and none proposed an ADD.
Preparation cost was $0.04975360; the final book is byte-identical to the
incumbent. Thus no B proof requests were dispatched, saving the registered
B training and validation allocations.

Both reducers received zero curator operations and zero checked receipts.
The first had 18 supplied source contexts; the second had 15. Their answers
treated an empty receipt catalogue as a reason to emit no advice. This is
evidence of an ineffective writing workflow, not a tool-availability failure.
The user requested a reducer-focused follow-up study after this task; see
[reducer_study/REPORT.md](reducer_study/REPORT.md) for the free investigation,
scripted Rocq demonstration, and proposed next comparison. No additional
paid variant was launched for that study.

## Spending and limitations

New experimental charges are **$1.51629542**: $0.04975360 writing,
$0.57996846 training and $0.88657336 validation. Together with the previous
$3.61359998, cumulative spending is **$5.12989540 / $30**; the unspent balance
is **$24.87010460**. This is not an instruction to spend the balance.
There are 705 successful billed responses plus one provider-rejected request
settled at $0, all reconciled in 706 new ledger receipts. No paid response
was regenerated, and no source generation, embeddings or paid diagnostics ran.
The original ledger ceiling, pre-dispatch reservations and unknown-liability
guard remain active. Codex-session costs were unavailable and are separate.

Cached-input fractions differ materially: training incumbent/A = 60.1%/46.8%,
validation = 75.9%/59.7%. At the same registered tariff with cache discounts
removed, validation costs would be $1.46974720/$1.61138080, a 9.6% increase.
That is offline tariff sensitivity, not a new admission-policy experiment.
All charged costs include failed attempts. Historical controls lack the
current exact terminal transport/admission reconstruction, although all 60
observed request sequences replayed. Model, book and registered task limits
match; cache state, dates and execution instrumentation are disclosed limits.

## Integration failures preserved, not hidden

Two failed setup panels precede the corrected model comparison. The first
had 4 writer and 20 proof jobs fail before dispatch because tmux lacked the
credential. The second had 19 local proof-request translation failures and
one zero-charge HTTP 400 due to unanswered demonstration tool calls. Each
proof panel retains its **0/20** denominator. Combined with corrected
training, all training execution attempts are 10/60; this operational count
does not estimate the corrected model's coverage. Including validation,
all proof execution attempts are 33/100. The main table explicitly reports
the corrected implementation's complete panels separately.

The original files, seals and repair records remain in `setup_failure_01/`,
`setup_failure_02/`, `seals/`, `setup_repair.json` and `transport_repair.json`.
The HTTP 400 used one of four allowed request retries; its original ledger
row remains in the append-only reconciliation table. Its zero charge never
changed. A wrapper bug that assigned a legacy cell name was corrected before
the first successful prover generation. No successful model outcome was
replaced. The replay tuple/list normalization fix changed only comparison of
wire-equivalent values. No prompt changed after successful prover collection
began. Useful upstream fixes are outlined in `UPSTREAM_SUGGESTIONS.md`.

## Verification and review artifacts

- 31 scoped regression tests pass, including raw malformed tails, unsafe
  proofs, context binding, real proof completion, budgets, receipt preservation,
  duplicate probes, failed-cell handling and all 60 full prompt translations.
- Six real-Rocq cases agree between the bounded socket tool and the legacy
  unassisted stdio checker. Bounded stdio remains unsupported; the bridge and
  its guards were not changed. Both harnesses use the shared socket path.
- All 78 corrected jobs replay with HTTP forbidden, exact transport state,
  budget and wire-equivalent results. The 60 historical observed-request
  replays were repeated after the demonstration repair.
- Scoped Ruff/Pyright checks pass. Pyright installed here is 1.1.409. The
  earlier separately scoped upstream check has 17 pre-existing why3py errors;
  it was not silently repaired. Global tests, partition checks, repricing,
  mixed history/index and Ladon CLI status were excluded. Direct night YAML
  metadata showed all nights done. TestX and protected challenge data stayed closed.

`cells.csv`, `requests.csv`, `snippet_receipts.json`, `writer_provenance.json`,
`mechanism_summary.json`, `reference_tokens.json`, `receipts.csv` and
`export_verification.json` provide the audit trail. `output_inventory.json`
pins raw local results and transport snapshots. Code and review artifacts are
staged and uncommitted; all implementation changes are inside Omphalos.
