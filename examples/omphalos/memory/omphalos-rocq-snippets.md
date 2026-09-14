---
name: omphalos-rocq-snippets
description: "September 13 Rocq snippet campaign: 23/40 vs 27/40, no new book; writer role tests and receipt fix; cumulative $5.26366084/$30"
metadata:
  node_type: memory
  type: project
---

Guille authorized implementing the Rocq snippet tool in both flagship prover
and ACE writers, with a targeted eight-source update and the remaining
original $30 ceiling. After the comparison, Guille explicitly requested a
study of how to make the reducer use it, clarifying that reduction was the
original purpose. That follow-up study was completed offline, without new
API calls. The later authorized writer follow-up is recorded below; no paid variant is currently running.

Start with `experiments/campaigns/ace_snippets_20260913/FINDINGS.md` and
`reducer_study/REPORT.md`. The registered campaign completed 18 writing jobs,
20 trainX tool-A cells and 40 validationX tool-A cells, with 60 historical
controls reused. Training A = 10/20, $0.57996846 vs 12/20, $0.50783622.
Validation A = 23/40, $0.88657336 vs 27/40, $0.66722836. Coverage p=.21875,
Holm p=.65625; observed cost ratio 1.3287. The practical follow-up gate failed,
so no seed-1/fresh-control extension or default promotion occurred.

There was real tool exposure in 9 training and 13 validation cells, including
7 syntax-classified rejections and 4 tool-completed proofs across panels.
This proves the mechanism reaches cases, not a net coverage benefit. Reused
validation is development data; cache fractions and historical controls limit
causal interpretation. New experimental cost $1.51629542; original ledger
cumulative $5.12989540/$30, unspent $24.87010460. Unknown charges: none.
Codex-session costs remain unavailable and separate.

All 18 writers advertised the checker, but each returned after one request
with no tool use or additions. Writing cost $0.04975360. The book is byte-
identical to X3, so B failed its exposure gate and had no proof comparison.
Both reducers received zero candidate operations and zero snippet receipts.
The study found input starvation, confusion about creating initial receipts
and valid open fragments, missing writer demonstrations, and one curator
using the reflector rule. Writer budgets were not exhausted.

Free study artifacts include eight exact historical syntax-error draft
packets, reducer-only proposed instructions, a real-Rocq scripted repair
demonstration, and checks for unchanged receipt reuse, legitimate abstention
and rejection of forged IDs. The study demonstration is not installed in
the paid selector. These exercises do not establish future model adoption.
A future four-job reducer/control pilot could spend at most $0.80, with a
gated four-job repeat for another $0.80. This is a proposal, not a dispatch
authorization; preserve the original campaign's negative result and gates.

Integration problems are preserved: a credential setup failure (4 writers,
20 proofs, zero dispatches), then a demonstration transport failure (19 local
proof failures and one HTTP 400 settled at zero). Both 0/20 proof panels are
retained separately from corrected execution. One of four permitted request
retries was used; no paid response was regenerated. An exact audit migration
preserves the rejected receipt's original row, fixes its legacy cell name and
acknowledges its known zero charge without changing financial protection.
Source seals and all failed setup records remain available. No successful
prover generation preceded the demonstration repair.

31 campaign regression tests plus 3 additional reducer study tests passed;
all 78 corrected jobs and all 60 historical observed request sequences replay.
Six scoped socket/legacy-stdio Rocq parity cases agree; bounded stdio remains
unsupported. Changed Omphalos code type/lint checks pass (Pyright 1.1.409).
The earlier upstream check's 17 why3py failures remain out of scope.

Keep testX, protected challenge data and mixed history/index closed. Install
`runtime.snippet_scope.install()` before campaign imports. Ladon metadata was
read directly; no mixed index/history was opened or updated. Changes and
review artifacts are staged, uncommitted, inside Omphalos. Both agent
harnesses use the same code and instructions.

Related: [[omphalos-resource-completion]], [[omphalos-ace-retrospective]].


2026-09-13 authorized writer follow-up: see
`experiments/campaigns/ace_snippets_20260913/writer_pilot/RESULTS.md`.
Tested 8 curator sources and 2 reducer batches per arm. The first paired stage
used 20 fresh jobs ($0.08033704): controls 8/10 valid outputs, zero checks/edits;
draft v1 5/10 valid, 16 checks and 2 useful curator edits. Its second-seed gate
failed and was not relabeled. The new draft/role/demo contract exposed a receipt
bookkeeping defect: known rejected attempts could not be explicitly dropped.

A separately registered second/final contender repaired that handling while
still rejecting unknown IDs and all nonexecutable retention. Ten fresh v2 jobs
($0.05342840) reused compatible earlier controls. V2: curator 7/8 valid with
2 useful edits; reducer 2/2 valid with 2 useful edits in one batch. Four useful
edit occurrences represent three distinct source corrections. A square tactic
instantiation was valid but redundant and not credited. One curator copied a
wrong receipt ID, then returned malformed YAML; its checked fragment was not
recovered into the output. V2's required 10/10 gate therefore also failed.
There is practical reducer promise, no statistical support, default promotion,
new theorem-coverage evidence, third contender or further paid run.

The repaired opt-in entry is `prove_writer_receipts.write_rocq_receipts`, with
`draft_writer_policy` and shared `reduction_input`. Both harnesses use it.
The next interface candidate is short receipt aliases plus robust final
structured answers; do not spend on it without a new concrete protocol.
The role pilot was independent matched inputs; full chained adaptation remains
unmeasured, although real-Rocq regression covers curator/reducer receipt reuse.
All 30 cells replay exactly, all retained snippets were rechecked, and 32
scoped tests passed with scoped type/lint clean. Original bridge unchanged.

New follow-up cost $0.13376544; original ledger cumulative $5.26366084/$30;
remaining $24.73633916; no unknown charges. Use the latest receipt campaign
accounting for the live ledger: old end-of-campaign snapshots stay frozen.
Scope incident: generic `make agents-check` indirectly read the mixed index for
nonemptiness, without returning its content or using it analytically. Recorded
in writer_pilot/scope_incident.json; avoid that aggregate helper under closure.
testX/protected evidence remained closed. Ladon YAML metadata was read directly;
only targeted safe memory/milestones were updated. No commits.
