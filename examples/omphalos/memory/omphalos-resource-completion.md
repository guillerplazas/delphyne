---
name: omphalos-resource-completion
description: "September 13 authorized $30 resource/continuation campaign: $3.6136 spent, neither contender advances; opt-in proof receipts and snippet provenance"
metadata:
  node_type: memory
  type: project
---

Guille authorized implementation of the agreed two-contender plan after the
ACE retrospective. The campaign is `experiments/campaigns/resource_completion_20260913/`;
start with `FINDINGS.md`, then `README.md` for the frozen protocol.

Completed 160 new cells: A/B x trainX/validationX x 40, seed 0. Shared 80
historical reference cells. Spent $3.61359998 of $30 in 2,156 settled model
requests, with no platform failures, unknown charges, retries or authoring.
Both validation gates failed, so no seed-1/fresh-control follow-up ran. The
unused $26.38640002 is not a direction to continue spending or alter gates.
Codex-session costs were unavailable and separate from the experimental ledger.

Validation: historical fixed-book current program 27/40 for $0.66722836;
A (actual output cap 4096 throughout) 26/40 for $1.12813834; B (existing
corrected structured continuation) 23/40 for $0.73794632. Holm-adjusted
coverage p-values 1.0 and .4375. Validation is reused development data, not
fresh confirmation. No prover default or frozen book changed.

A created real additional dispatch/proof-check opportunities in 11 train and
15 validation cells, but neither of its two extra training solves was exposed
to the measured admission effect. It gained no validation solves. More
affordable requests cannot be equated with recoverable capability. B's v2
parser actually handled 58 multi-message final responses across the panels;
the functioning repair did not translate into a favorable coverage/cost result.

Follow-up #130 now has opt-in terminal receipts reaching reflection, with
source hashes, proposed versus accepted scripts, and the recorded assistance
flag; legacy outcomes already included accepted proofs. Curator/reducer
contracts preserve explicitly bound checked snippets or record explicit
drops. These were verified offline, not used to create a new paid book.
Multi-episode reflection overrides require a future explicit receipt contract.
Follow-up #131 gained experimental evidence against the blanket 4096-output
intervention; it is not a claim that all admission conservatism is resolved.

31 distinct scoped tests passed; all 80 historical controls and 160 new cells
replayed without HTTP. Historical replay covers observed requests; new replay
also restores opaque transport state and runs the full bounded controller.
Changed Omphalos code and adaptation type-check cleanly. The separately scoped
find_invariants check still has 17 pre-existing why3py-related errors.

Keep testX, protected challenge data, mixed history and memory/MEMORY.md closed.
Install `runtime.completion_scope.install()` before this campaign's imports.
It adds an exact archive/problem allowlist to the development guard. A blocked
eager legacy partition import returned no data; legacy benchmark loading is
now lazy. Incidental legacy-result comments in source were excluded from
analysis. Ladon night metadata was inspected directly; all listed nights were
done. The index was not read or updated; this entry is linked from the safe
retrospective memory instead. Implementation and review artifacts are staged,
uncommitted. Raw local new measurements remain at their recorded paths.

Related: [[omphalos-ace-retrospective]].

Subsequent explicit authorization on September 13 reused this original ledger
for a Rocq snippet tool comparison. That separate campaign spent $1.51629542,
bringing the cumulative total to $5.12989540; this entry's $3.61359998 remains
the earlier campaign snapshot. See [[omphalos-rocq-snippets]] for the measured
result and the user's subsequent reducer-focused offline study. No further
paid variant was launched for that study.
