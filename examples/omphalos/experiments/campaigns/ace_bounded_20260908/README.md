# Bounded ACE follow-up (approved 2026-09-08; execution 2026-09-09)

## User decision — keep as a budgeting win (2026-09-09)

Guille explicitly accepts the 55.5% cost reduction as a win for Omphalos's
budgeting objective and requests keeping and committing the changes. Cost per
qualified solve fell 50.2%, from $0.05442 to $0.02712. Keep this configuration
as the budget-oriented reference and X3 as the coverage comparator. The
original no-fewer-solves gate and statistics below remain unchanged; the
project acceptance decision supersedes the earlier blanket non-promotion.

[Failure analysis and prioritized improvements](FOLLOW_UP.md) cover the fifteen
unsolved cells, four lost solves, one gained solve, conservative monetary
reservations, a confirmed typed Compute-limit defect, and future trainX work.
This analysis incurred **zero new paid calls**. [Acceptance record](acceptance.json).

## Original experimental verdict — complete; strict gate not met

The integrated candidate was **55.5% cheaper but solved three fewer problems**.
It does not meet the registered improvement or quality-preserving saving
criterion. X3 remains the coverage comparator; the user accepts the bounded
configuration as a budgeting win above. No extra validation run was added.

| 40 validationX problems, seed 0 | Historical X3 | Frozen candidate |
|---|---:|---:|
| Qualified solves (actual cost ≤$0.10) | 28/40 | 25/40 |
| Charged API cost, all cells | $1.523789 | $0.678047 |
| Platform failures | 0 | 0 |
| Cells exceeding $0.10 | 7 | 0 |

Solve difference: **−7.5 percentage points**, exact two-sided p=0.375;
descriptive family-bootstrap 90% interval [−17.5, 0] points. There were five
discordant families: one win and four losses for the candidate. This is not
statistical proof of a quality decrease, and it provides no equivalence claim.
Cost ratio: **0.445**, descriptive 90% interval [0.376, 0.534], paired family
sign-flip p≈0.00011 (100,000 fixed-seed Monte Carlo draws, plus-one correction).
The saving is clear on this panel, but the required no-fewer-solves condition
fails. Historical controls and repeated validation remain limitations.

**Campaign API spend: $1.38272072 of the $10 ceiling.** Adaptation $0.00823960,
pilots $0.69643398, validation $0.67804714. Exactly 60 configured episodes/cells
(4 adaptation + 16 pilot + 40 validation); 783 settled HTTP attempts, zero
infrastructure retries, no unknown-charge liability. This does not include
Codex/Claude assistant usage or engineering time. The receipt export and
cached token repricing agree exactly across all 60 cells.

On API arithmetic alone, the observed saving would repay all training cost
in about 34 future problems; this is not a deployment recommendation because
observed solves fell. The learned advice pool was not injected in validation.
Cached diagnostics record 25 accepted proofs, six resource outcomes and 260
prompts with focused decisions; they are distinct records, not event counts.
The sampled legacy bridge-parity check was 18/18, not an exhaustive archive
recheck. No testX or protected challenge proof data was used.

Reproducible evidence: [frozen settings](frozen.json),
[pilot readout](pilot_readout.json), [final statistics](final_report.json),
[validation cells](validation_cells.json), [API receipts](receipts.csv), and
[checks](checks.json). Raw run outputs remain in the three local
`experiments/output/ace_bounded_*` directories.

Use trainX only for adaptation and pilots. Evaluate one frozen integrated
candidate on all 40 validationX problems, seed 0, against x3-r64/seed0 from
ace_review_development (28/40 qualified, $1.523789). No testX or challenge.
The detailed preregistration is the ace_bounded_experiment.py docstring.

API ceiling $10, including retries and unknown-charge reservations:
training/adaptation $2; validation $7.50; retry reserve $0.50. This is a
ceiling, not a spending target. At most 16 pilot prover attempts, four
adaptation episodes, 40 validation cells and four infrastructure retries.
The campaign ledger does not meter Codex/Claude assistant usage.

Register both endpoints: >=5 points more qualified solves, or >=10% lower
paired total cost with no fewer observed solves. Exploratory two-sided
family-clustered p<0.10 and descriptive 90% intervals. Cost sign-flip tests
assume exchangeable paired differences. Reused controls are historical;
results do not establish randomized causality or quality equivalence.
Include failures and retry costs. No verdict for missing/censored cells.
Do not add seeds, retune on validation, or fund a new campaign automatically.

The offline evidence builder replays cached candidate transitions in Rocq;
cached order is not an invocation log. evidence.json was an initial pool
that filled with reference errors. Before any paid run, evidence_v2.json
changed to round-robin category selection; it admitted six reference and
two structural transitions in eight checks. Neither file is overwritten.
Unrepresented failure classes are not claimed as demonstrated coverage.

Both harnesses use the same Python entrypoints, launcher, demos and ledger.
Long runs use tmux after sourcing ~/.config/omphalos/env.sh. Progress notes
and HINTS are maintained at milestones; routine monitoring stays in logs.

Preparation correction (before pilot calls): artifact.json and pilot.json
are unselected drafts from a reader that missed the command-result envelope.
artifact_v2.json and pilot_v2.json correctly merge outcome.result from the
four adaptation episodes. One completed, three stopped on malformed model
YAML; no retries were spent. The completed action duplicates offline evidence,
so the checked pool remains eight claims and the eight pilot problems are
unchanged. Paid adaptation cost: $0.0082396 (seven HTTP attempts).

## Implementation and review map

| Change | Main implementation | Verification |
|---|---|---|
| Atomic advice admission | `ace_grounded.py`: replay prefix, locate references, check the exact action; render only checked action | Mixed valid/invalid clauses and unchanged goals rejected; eight trainX transitions checked in live Rocq |
| Composed adaptation | `prove_grounded.py`: reflector → checked correction → curator → auditor; immutable states, batch and iterate wrappers | Mock-oracle/live-Rocq checks; four paid episodes including three YAML failures |
| Focused decisions | Reference, bridge and structure query types; new grounded demos; current-state inspection | Demos parse; focused routing regression; bridge demos not yet covered by evidence |
| Whole-operation control | `tool_budget.py`, opt-in Rocq bridge integration, shared `rocq_seconds` admission | Zero-budget test, 12/12 bridge tests, 18/18 sampled legacy parity |
| Repair and restart | One local repair, then one new plan; existing seenstate k=4 trigger, no budget reset | Repeated-failure regression stops after 11 proposals under one shared budget |
| Money control | Opt-in `estimate_budget` price bound plus existing process-safe campaign ledger | Positive preflight-price regression; paid contrast in fixed training panel |
| Measurement | Complete cell identities, receipt costs, family sign-flip tests, 90% descriptive intervals | Mixed-arm/seed label and clustered inference regressions |

Default bounds: 60 seconds / 512 RPCs per operation; 300 verifier seconds,
64 model turns and nominal $0.10 per proof; 8KiB rendered feedback view with
explicit goal pagination. This view cap does not bound the full conversation.
Raw goals remain in evidence, and success still requires Rocq acceptance.
The hard $10 campaign ledger covers HTTP attempts and uncertain charges.
The new bounded transport requires socket mode; unavailable socket evidence
is classified explicitly. Legacy STDIO behavior is retained for old policies.

Validation is a historical integrated comparison, not a separate causal test
of each component. Two pilot cases per mechanism cannot establish equivalence
or a reliable population effect. Pilot controls differ across mechanisms as
preregistered in the experiment script. Report diagnostic checks as distinct
cached records, not a complete invocation-event log.

Checks: cached `make test`, local Pyright and Ruff passed; `make reprice`
passed after lifting its finite CSV field allowance to 64MiB for serialized
evidence. Root `make pyright` passes the core and stops in `find_invariants`
on missing `why3py.simple` (17 errors outside this task's scope).

## Completed training pilots

| Mechanism | Off cost | On cost | Qualified solves off/on | Selected |
|---|---:|---:|---:|---|
| admission | $0.003635 | $0.003632 | 2/2 → 2/2 | no; not exercised |
| focused | $0.045587 | $0.027207 | 2/2 → 2/2 | yes |
| money | $0.210711 | $0.079859 | 0/2 → 0/2 | yes |
| restart | $0.187029 | $0.138774 | 0/2 → 1/2 | no; not exercised |

Total training API cost including four adaptation episodes: **$0.70467358**,
325 settled HTTP attempts, no unknown charges or infrastructure retries.
Each contrast covers two different trainX problems; differences across rows
are not comparable treatment effects. Advice and restart had no observed
targeted trigger, so their incidental outcomes do not select those switches.

`frozen.json` selects **money=true, focused=true, admission=false, restart=false**.
Thus validation retains the old X3 playbook with bounded feedback and focused
queries; the learned advice pool is not injected. Execution hashes and family
assignments were frozen before launching validation. The final run has exactly
40 validationX problems at seed 0.
