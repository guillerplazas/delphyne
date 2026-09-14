# Draft-aware Rocq advice for ACE writers

`prove_writer_drafts.py` provides an opt-in curator/reducer for the Luna/X3
flagship. It reuses `CheckRocqSnippet`, the same Rocq bridge and receipt renderer,
the existing playbook delta compiler and deterministic merge. The old writer
and frozen X3 baseline are unchanged.

Use this path when candidate code is worth checking or repairing before it
enters the playbook. A draft records its exact source context, rejected code,
error, goals and purpose. It remains explicitly unverified. A writer may repair
and check it, retain an inherited receipt unchanged, or drop it with a reason.
The strategy requires one decision per draft and binds retained receipts to
the correct source. Only the exact checked text is rendered as executable code.
A source-local check can leave obligations open; it does not establish the
mathematical truth of a new assertion or the portability of an example.

The policy selects one role-matched demonstration when its source family is
absent from the current inputs. It retains the ordinary four-request,
three-probe, 180-second writer allowance and pre-dispatch financial reservation.
This is one bundled intervention; its comparison does not identify separate
prompt, decision-contract and demonstration effects.

For a new supervised campaign, register `prove_writer_drafts` in its execution
context and add `demos/writer_drafts.demo.yaml`. Use strategy
`write_rocq_drafts` and policy `draft_writer_policy`, passing the campaign
snapshot directory and per-cell dollar cap. Arguments are `role`, `evidence`,
`playbook`, `contexts`, `drafts`, and optional trusted `receipts`. Persist and
hash source inputs using the campaign machinery before dispatch.

To pass curator outputs to reduction, call `reduction_input(products,
contexts, playbook)`. This deterministic helper carries every original draft,
curator decision, source context and retained receipt into the reducer input.
No model or verifier call occurs during the handoff. The reducer can reuse an
unchanged receipt without a new probe; changed text requires a new receipt.
The real-Rocq regression test executes this complete handoff. The paid pilot
compares roles independently on matched inputs, so it does not establish the
quality of a full chained adaptation or improve theorem solve coverage.

Both Codex and Claude Code use these Python strategies and the same supervised
launcher. See `experiments/campaigns/ace_snippets_20260913/writer_pilot/README.md`
for the bounded comparison commands, gates and accounting. Install the
snippet development guard before experiment imports and keep closed evidence
out of the pipeline. Never switch baseline defaults on the strength of this
small writer pilot alone.

The first paid pilot exposed a receipt-disposition failure. The repaired entry
point is `prove_writer_receipts.write_rocq_receipts`, with the same
`draft_writer_policy` and shared `reduction_input` helper. Add
`prove_writer_receipts` to the execution context alongside the draft module.
Its `WriteRocqReceiptAdvice` query names executable receipts separately from
failed attempts. Known failed attempts may appear in dropped_receipts; they
can never enter retained_receipts or an operation. Unknown identifiers still
fail validation. Repair feedback lists the exact available IDs and required
draft decisions. The original module stays available to replay the first
comparison; the repaired comparison lives under writer_pilot/receipt_repair/.
