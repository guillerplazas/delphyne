# Bounded ACE applicability — 2026-09-09

Completed: **48 local episodes, $0.05822918 API, screen failed**. A produces
two useful transitions versus fixed demonstrations’ three. No Stage B or
validation launch; retain bounded money+focused. The guard-coverage
limitation and unchanged no-go sensitivity are in [FOLLOW_UP](FOLLOW_UP.md).

Guille approved implementation and the bounded training stages of the plan.
Training authorization is $2.50; the old polish ceiling is closed. Validation
requires a separate review and a new $4 authorization. No teacher calls or
role episodes; no testX or protected challenge outcomes are used.

This experiment tests adaptive delivery of an identical, training-derived
bank against fixed demonstrations. It does not test automated reflection
against human authoring. Existing syntax evidence and grammar guards are
common to Q/F/A; Q/R measures this query/control bundle, F/Q the fixed bank,
and A/F the relevance/length tradeoff of selecting from that same bank.

## Frozen preparation

`artifact.json` contains five donor examples and twelve saved states with
exact source cells, cache indices, environment signatures and SHA-256 hashes.
`preparation_checks.json` records live unassisted Rocq checks. The three
positive donors execute; both negative donors fail the syntax-only form.
Six panel states accept the registered syntax correction and six do not.
The bank is exposed through `demos/applicability.demo.yaml`, including
materialized navigation checks; the negatives require explicit abstention.

The syntax forms are deliberately finite: parenthesized `change` or `set`,
and removal of bracketed `nra` arguments (posing an existing lemma application
when needed). The model decides whether the exact syntax-only form applies;
a deterministic grammar guard prevents changing the intended mathematics.
It does not apply a rewrite itself. A different normalization, missing-lemma
substitute, fresh assertion, prefix edit or general repair is rejected.
Whitespace between lexical tokens is ignored; changes to tokens or the
registered form are rejected conservatively.

Selection matches tactic form, parser-error shape and relevant state/target
structure. Import signatures are provenance, not global tactic-validity
certificates: `change` and `set` are core grammar across import sets; `nra`
examples require compatible real-arithmetic imports and local state. A named
hypothesis target must occur in the state. Every correction is checked locally.
F receives all five examples; A receives at most one positive and one negative.
The identical demonstration bank fits the 2,048-token guard. Full source
prefixes remain available for verification, while example prompts show the
local state rather than their entire historical proofs.

Four panel states have frozen downstream witnesses: the sqrt equation on
amc12a_2002_p13, the induction branch on amc12a_2003_p1, the lower-bound goal
on imo_1968_p5_1, and the positivity assertion on imo_1983_p6. A set/alias alone
or the large-natural representation change alone is not useful progress.
Witnesses are scoring evidence, never examples or runtime query inputs.

## Registered stages and stopping

`registration.json` enumerates every cell in deterministic shuffled order
(`random.Random(20260910)`) and groups theorem families. `sealed.json` fixes
execution hashes before any paid request. The executable protocol is
`experiments/ace/ace_applicability_experiment.py`.

* A: 12 states × R/Q/F/A × seed 0 = 48 local episodes, at most four
  requests and one proposal each. These receive fresh $0.10 diagnostic
  budgets, not reconstructed historical balances. The initial dialogue is
  the same minimal assistant-proposal/feedback pair in all four arms, not
  a claimed replay of historical reasoning or monetary admission. R keeps
  its ordinary continuation query and can solve directly or execute the
  correction as part of a longer proposal. None are counted as new full
  theorem solves.
* A go: >=5/6 correct positives, >=5/6 explicit negative abstentions, zero
  admitted negatives, >=2 useful families; and either >=2 additional useful
  transitions over F across >=2 families, or equal useful count at >=15%
  lower cost. Missing/censored cells, platform failures or unresolved
  liability prevent expansion. Incidental theorem wins do not replace this
  mechanism gate.
* B only after A passes: the eight distinct panel theorems × R/F/A × seed 0
  = 24 fresh full-theorem cells. Require A triggers on >=3 families and
  useful repairs on >=2 (verified correction retained in the final proof),
  no fewer qualified solves than R and F, and >=15% lower total cost and
  cost/solve than both. Otherwise stop. No extra 40-cell train-only repeat.
* Conditional validation: 40 validationX × seeds 0/1 × A/R = 160 fresh
  cells. Freeze stays unchanged. `validation_approval.json` must explicitly
  identify the sealed hash and $4 approval; no command creates this approval.
  ValidationX is development data. A/F transfer is not independently
  established over the full validation panel.

All runtime cells retain luna, Responses, medium reasoning, temperature unset,
core tools (including the existing grounded inspection facility), a 32,768
output cap, and the incumbent x3 advisory playbook. Full cells use the retained
money+focused controls: 64 requests, $0.10, 60 seconds/512 RPCs per operation,
300 verifier seconds and 8,192-byte views. Syntax repair consumes ordinary
turns; it adds no restart, downshift or recovery allowance. Full verification
keeps the same assisted checker; local episodes use unassisted verification
in every arm to isolate local execution from automatic completion.

R is the retained bounded reference. New F/A controls are opt-in; neither
polished controls nor a new default are promoted. Legacy adaptation defaults
are unchanged. Local query answers and actual computation events are recorded
in policies/Compute operations, not speculative strategy execution.

## Accounting and inference

Allocations: A $1, B $1.25, infrastructure reserve $0.25; training ceiling
$2.50. At most two separately audited infrastructure retries, one per cell,
and zero logical/serialization retries. Broad retry flags and automatic
launcher retries are disabled; this campaign need not use its retry reserve.
The separate conditional validation ledger is capped at $4, for a maximum
$6.50 across both authorizations. No transfers, top-ups or replacement cells.
A stage ceiling may stop a panel early; this gives no verdict. Spending is
not a target. Assistant/engineering costs are not metered by the API ledger.

Reports include all expected cells, unsuccessful attempts and platform
failures. Missing or administratively censored cells prohibit a utility
verdict. Actual token usage is repriced at receipt dates; unknown liabilities
remain reserved and block expansion. Qualified full solves require a complete
verified proof and cumulative charged cost <=$0.10, including retries.
Report total cost, cost per qualified solve and coverage together.

Primary validation metric: paired all-cell total API cost. Practical utility
requires >=15% savings in both total cost and cost/solve, with no observed
coverage loss. Statistical support separately requires family-clustered
**two-sided cost p<0.10**, with descriptive 90% intervals. Repeated states,
seeds and duplicate families stay together. The three Stage A contrasts are
exploratory; A/F is the applicability contrast. Do not treat nonsignificance
or unchanged coverage as equivalence; promotion requires a separate decision.

## Commands (both agent harnesses)

From `examples/omphalos`, after sourcing `~/.config/omphalos/env.sh`:

```bash
python -m tools.reports.ace_applicability_report prepare
python -m tools.data.materialize_demo demos/applicability.demo.yaml
delphyne check demos/applicability.demo.yaml
python -m tools.reports.ace_applicability_report seal
python -m experiments.ace.ace_applicability_experiment --phase=a run --max_workers=8 --wait
python -m tools.reports.ace_applicability_report report_a
# Only if report_a.go is true:
python -m experiments.ace.ace_applicability_experiment --phase=b run --max_workers=8 --wait
python -m tools.reports.ace_applicability_report report_b
```

Paid launches run in tmux through the existing supervised launcher, using
eight workers and the existing sixteen machine slots. Prepare, seal and
reports refuse replacement; raw paid outputs are never edited. Completed
commands are provenance, not instructions to overwrite a historical campaign.
