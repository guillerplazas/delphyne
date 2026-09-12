# ACE attribution and full Terra scaling — 2026-09-12

Guille approved the complete plan and a $75 experimental API ceiling.
Assistant usage is outside this ledger. The ceiling is not a spending target.
No model promotion is automatic. Both Codex and Claude Code use the same
entry point, from `examples/omphalos`:

```sh
python -m experiments.ace.ace_attribution_experiment prepare
python -m experiments.ace.ace_attribution_experiment preflight
python -m experiments.ace.ace_attribution_experiment seal
python -m experiments.ace.ace_attribution_experiment campaign
python -m experiments.ace.ace_attribution_experiment status
```

Use the recorded `launch.sh` in tmux on i34-gpu01. The orchestrator locks
the campaign. Each immutable batch uses OmphalosExperiment, the 24-worker /
32-slot runtime, and request reservations. Training uses at most four workers
per batch; its sequential book evolution is part of the treatment.

## Registered experiment counts

All full panels are 40 theorems, seed 0 only. There are 80 existing Luna ACE
references, 80 new Luna no-ACE cells, 80 Terra no-ACE cells, 80 Terra own-book
cells, 40 Terra adaptation generators, 16 cross-book cells and 16 effort
diagnostics: **312 new proof episodes**. Adaptation also schedules up to
40 reflectors, 40 curators and 10 reducers, each with the existing three-request
parse contract, plus embedding calls. A missing generator may prevent its
downstream roles; such omissions are recorded, not silently replaced.

The eight-theorem swap and effort panels are independently fixed before
results, each with four competition / four Mathd problems and distinct
families. Swaps run both off-diagonal model/book combinations and reuse
their same-model controls. Effort low/high on Terra no-ACE reuse the main
medium cells. Effort diagnostics do not select a setting or expand the grid.

## Treatments

Inference uses the identical grounded strategy: money/focused enabled;
admission/restart/polished and later mechanisms disabled; 64 requests,
32768 output tokens, 300 verifier seconds, 60-second operations, 512 RPCs,
8192-byte views, Responses API, medium reasoning. Removing ACE changes only
the rendered book and its conditional instructions. Demonstrations and tools
are identical. Luna's cap is $0.10; Terra's is $1.00, matching the 10x rate
ratio. The new runner sets the cap explicitly instead of inheriting the
old bounded configuration's hardcoded $0.10.

Luna's frozen X3 book has SHA-256
`1e4aec7dbbe80e7a320db17a7c18fe0859bfc00898837c297be248a05dbde067`.
Its 40-step, one-epoch training was entirely Luna. Terra starts empty and
uses the same X3 order, four-problem batches, generator/reflector/curator/
reducer contracts, merge/refinement implementation, embedding threshold and
4000-token guard. All generative roles are Terra/medium. Training generator
allowance is 32 requests/$1, role allowance three requests/$0.20. These
training dollar limits retain the old post-request stop semantics; the
separate campaign ledger reserves every HTTP attempt before sending it.
The budgeted transport imposes its 32768 output-token limit. No auditor,
extra epoch, warm start or book selection is introduced. Inference starts
only after the final Terra book is frozen.

## Measurement and restrictions

ValidationX is the primary **development** comparison, not a fresh holdout.
TrainX is in-sample for both learned books. Report within-model ACE effects,
model interaction, raw and cost-qualified solves, total cost, cost/solve,
tokens, requests and failure mechanisms. Use theorem-family clustering,
90% intervals and two-sided p<0.10; practical trade-offs and statistical
support remain distinct. Historical Luna controls entail provider/time
confounding even after exact observed-request replay.

`preflight.json` records all 80 control replays, including their cache
hashes and zero paid requests. Replay stops at the recorded request count:
the historical transport advances its reasoning allowance only during live
HTTP dispatch, so ordinary cache replay cannot reproduce an unobserved next
request's admission bound. Every actually observed request, active strategy
input, dollar/verifier cap, outcome and token cost is checked.

The lazy pool adapter makes adaptation imports independent of partition
reads; the development guard is installed before imports. testX and the
protected challenge remain closed. No aggregate test/partition/reprice
command that reads them is used. Source and data hashes are frozen before
paid calls; old results/books are never overwritten.

## Accounting

Initial allocations: Luna $4, Terra adaptation $16, Terra benchmark $40,
swaps $4, effort $6, infrastructure reserve $5. Completed-stage slack may
move forward with ledger records; the total remains $75. No additional
arms or seeds consume spare money. At most four explicitly diagnosed
transient infrastructure retries are permitted; no generic retry loop runs.
Unknown billing blocks dispatch and verdicts. Missing or administratively
censored cells cannot be interpreted as a null effect. Platform failures
remain in complete-panel denominators.

Actual-dollar solve curves are retrospective final-cost qualifications,
not claims about what the admission controller would have done under a
smaller cap. Show Luna-rate-normalized costs separately. Book preparation,
inference and diagnostics are separated; preparation amortization uses
100 and 1000 problems.

## Verification

Initial checkpoint: `23329b09`, author/committer and Signed-off-by
guillerplazas <guille.rplazas@hotmail.com>. Fifty scoped tests passed before
launch; request replay passed for 80/80 references. Root Pyright passes the
core project but has the known 17 missing `why3py.simple` errors in
find_invariants, outside authorized edit scope. New code uses pinned
Pyright 1.1.406 and Ruff. Exact logs accompany the campaign.

Results, receipts and per-cell diagnostics are produced separately from
this preregistration; the original protocol is never relabeled after results.
