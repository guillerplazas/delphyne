# Preserved rejection and exact administrative continuation

The first validation block encountered one provider HTTP 400
`invalid_prompt` rejection in ACE + drop, seed 0, on
`algebra_others_exirrpowirrrat`. The existing adapter settled that request
at zero charge and the ledger stopped further admission. Two other cells
were then interrupted by that ledger stop: non-ACE drop and non-ACE both,
seed 1, on the same theorem. The block initially held 29 completed runs,
one provider failure and two administrative interruptions.

The provider's explicit error text identifies a policy classifier rejection.
The [official error guidance](https://developers.openai.com/api/docs/guides/error-codes)
directs callers to inspect the specific error detail; it does not establish
the billing for this particular request. Here the adapter had already
recorded zero liability for this HTTP 400. The reconciliation changes no
amount or budget: it preserves the original receipt in an audit table and
an immutable incident record, then marks the error metadata reconciled.
Unknown or nonzero charges cannot pass this procedure, and the global
billing guard stays enabled.

The rejected prompt was neither retried nor rewritten. Its run counts as
one platform failure in the full denominator, including all earlier charges.
Its original exception and cache remain untouched.

The two collateral interruptions resumed from exact cached prefixes in a
new `resume01` archive. A guard requires every previous computation and
model response to replay before the unchanged next request is admitted.
Offline checks for all three interrupted histories matched that request,
opaque reasoning state and spent budget, with HTTP blocked and zero new
receipts. The two continuations keep the original $.10/64-request/300-second
limits and logical cell identities; they add no problem, replicate, prompt,
tool, memory, model setting or solve retry. Replayed resets are suppressed
from new telemetry to avoid counting the same reset twice.

Both continuations finished. Their additional charged cost was
**$0.01170016**, bringing new campaign spending to **$1.91082676** at that
point. Block 00 is complete with 31 normal results and one preserved provider
failure. The ordinary frozen launcher then continued at block 01.

Primary results retain all 40 theorem families and all incident costs.
Before resumption, a secondary operational sensitivity was specified that
excludes this entire affected theorem family from **every** arm and seed.
This identifies whether the operational interruption changes the conclusion
without replacing the primary measurement.

`operations/incident01.json`, `checkpoints01.json`, `recovery_seal01.json`
and `completed01.json` bind the evidence and prospective recovery procedure.
`state.py` resolves the continuation results without overwriting raw archives.
The original runtime source seal remains valid. The initial pilot report's
exact source is preserved at `sources/pilot_report.py.txt`; the final
report adds explicit continuation/failure handling and the sensitivity.

Both harnesses use `python -m experiments.economy_refinement.recovery` for
this recorded incident only. New provider rejections cannot be silently
acknowledged by that command. Forty scoped tests, changed-file pinned
Pyright 1.1.406 and Ruff pass; root type checking still has the 17 unrelated
`why3py.simple` errors. No closed partition was accessed.
