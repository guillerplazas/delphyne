# Applied conservative timeout reconciliation

This proposal concerns one request only: `97e9d18f8d88406d8cd7fe33983f3339`,
B1 on trainX `mathd_algebra_185`, replicate zero. It was prepared and tested,
then applied under the existing recorded API continuation. An unnecessary
additional permission question was withdrawn; no new user reply is claimed.
The immutable preparation and authorization clarification remain preserved.

The first 23 responses cost $0.03731910. Request 24 timed out after 600 seconds.
Its actual charge is unknown and bounded by its fully retained $0.22239272
reservation. The cell's total bill is therefore between $0.03731910 and
$0.25971182. The original failed outcome, exception, request and cache remain
unchanged. All four controller replays reach that exact terminal request
without HTTP. The other 99 batch outcomes have passed exact replay, independent
compilation (73 distinct proofs), and 297 lower-budget scenarios.

The applied command changed this receipt's status from
`unknown_charge` to `bounded_charge`, preserving every other ledger field and
the entire reservation. It cleared only this billing pause. Any later unknown
request still triggers the existing guard. It does not retry the failed cell.
The original 520 unlaunched solver attempts resumed; there are no
remaining paid author calls.

Reports must display the bill interval wherever this cell contributes. No
upper bound may be called an exact invoice, and a cost target must hold at
the adverse endpoint. Comparisons that do not contain this cell retain their
exact billing. The original evidence and this change remain auditable.

Implementation: `experiments/ace_independent_audit/billing_recovery.py`.
Three offline tests verify explicit approval, unchanged retained liability,
and continued blocking for any additional unknown request. Five additional
tests cover cost intervals, the adverse-endpoint target, approval identity,
and the actual timeout prefix. The reporting extension keeps 27 earlier
exact comparisons identical. Scoped Pyright and Ruff pass. The receipt
status alone changed to `bounded_charge`; all amounts and original evidence
remain unchanged. See the campaign
`billing_recovery/authorization_clarification.json` and
`billing_recovery/bounded_timeout_approval.json` for the exact existing
continuation used. The latter filename is retained for continuity and does
not claim per-receipt approval from a new user message.
