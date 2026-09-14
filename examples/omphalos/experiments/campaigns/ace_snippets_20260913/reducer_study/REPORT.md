# Making Rocq useful to the reducer

The next intervention should fix the reducer's inputs and role instructions,
then test useful checked edits. Increasing its budget is not supported by
this evidence. The completed paid campaign remains unchanged; this follow-up
study used **$0 in API charges** and training evidence only.

## Ranked diagnosis

1. **The handoff removes actionable code before reduction.** Both measured
   reducer batches contained zero curator operations and zero snippet
   receipts. Their source catalogues had 18 and 15 contexts, respectively,
   but the curators passed prose diagnoses rather than explicit candidate
   code and its purpose. A reducer asked to consolidate this input can
   legitimately return an empty result. Checking that final book again would
   not answer whether the reducer can repair invented syntax.
2. **An empty receipt bank was interpreted as a stop condition.** Both
   reducers explain that no checked receipts are available and therefore no
   executable advice can be retained. They do not use the tool to create the
   first receipt. The mathd_algebra_28 source even has an accepted terminal
   proof, yet the distinction between that terminal receipt and the new
   snippet receipt becomes a reason to discard its useful bridge. Several
   responses also treat incomplete source proofs as insufficient evidence
   for fragments, despite the tool explicitly supporting `executed_open`.
3. **Writer demonstrations never reach the writer policy.**
   `snippet_examples()` returns no examples for `WriteCheckedRocqAdvice`.
   The two paid examples teach the prover, not the reducer. The shared system
   prompt presents reflector, curator and reducer rules together. One
   curator explicitly invokes the reflector's empty-operations rule in its
   answer. This is evidence for a reducer-specific prompt, not proof that
   wording alone explains all abstention.
4. **Resource exhaustion does not explain the observed abstention.** All
   18 writing jobs used exactly one model request; all 18 initial requests
   were admitted. There were no writer tool checks or budget declines.
   Reducer spending was $0.00219660 and $0.00149280 against $0.20 each;
   four model turns and three probes were available. Their first-request
   reservations fit easily. No extra allowance is indicated.

These conclusions use the actual writer inputs, responses and dispatch
records, not the validation failures. They establish what the pipeline did;
they do not establish which proposed prompt change a model will respond to.

## Concrete free work completed

`candidate_packets.json` contains the first historical syntax-error check
for each of the original eight training sources, in the same two batches of
four. Each draft retains exact code, error, source context/prefix, goals and
cache hash. All are labelled unverified historical rejections. No candidate
is silently converted into a certificate or a playbook entry. This supplies
reviewable inputs for a future reducer comparison without paying generators
or rewriting the measured curator outputs.

`tools/reports/reducer_tool_study.py` runs four scripted decision sequences
through the existing reducer strategy and real bounded Rocq:

| Exercise | New reducer tool calls | Result |
| --- | ---: | --- |
| Return no advice despite an available draft | 0 | Current contract accepts the empty result. |
| Check invalid `have` form, repair to `assert`, retain | 2 | Rocq rejects the first and accepts the open fragment; only repaired exact text reaches the delta. |
| Retain an inherited checked fragment unchanged | 0 | Exact code survives; no redundant Rocq check is needed. |
| Invent a receipt ID | 0 | Four attempted final answers fail the receipt contract; no delta is returned. |

The exercise creates `demos/reducer_snippets.study.demo.yaml`: a reducer
example with complete tool-call/output history and a checked final addition.
It is deliberately **not installed** in the completed campaign's selector.
Three study tests and the 60-problem request-translation regression pass;
scoped type/lint checks pass. The examples use scripted choices, not new model
responses, so they prove plumbing and provenance rather than improved adoption.

## Recommended implementation

Keep the existing model, request/output/Rocq limits, tool, ledger and merge
logic. Introduce one opt-in reducer variant with these linked changes:

- **Preserve drafts separately from executable deltas.** Add a typed
  `UnverifiedSnippetDraft` carrying `draft_id`, source context, exact code,
  purpose and source hash. Reflector/curator can pass such a draft without
  pretending it is checked. Retain the checked-receipt channel unchanged.
  Supply the reducer with the relevant local goals/types, not only opaque
  IDs or prose summaries. Use existing source records and bounded Compute
  inspection when a fresh state is necessary.
- **Use reducer-only instructions.** The reviewable wording is in
  `proposed_prompt.md`. An empty catalogue is normal; the checker creates
  receipts. A valid open fragment can justify a source-local snippet. For
  each useful new or rewritten fragment, check before retaining; for an
  unchanged checked fragment, reuse its receipt. An unverified status alone
  is not a substantive reason to discard an otherwise useful candidate.
  Permit explicit redundancy/irrelevance/resource-based drops.
- **Make candidate handling explicit.** A versioned query answer should
  contain a decision for each supplied draft: drop with a reason, retain a
  checked receipt, or replace with checked receipt(s). Validate the IDs and
  coverage in the strategy, then reuse `compile_advice` to construct the
  existing `CurationDelta`. A draft never reaches `merge` as executable text.
  A changed retained snippet without a receipt must receive feedback or
  fail; it must not silently revert to unverified prose or code.
- **Select writer demonstrations explicitly.** Reuse Delphyne's
  `ExampleSelector`, with the reducer query family and exclusion of every
  source family represented in the current batch. The study example is
  excluded from the batch containing mathd_algebra_28. Test complete rendered
  request translation, including examples, before dispatch.

Queries choose and repair drafts; strategies enforce the evidence contract;
individual Compute nodes perform Rocq checks; the policy supplies examples
and controls search/budgets. Use the existing `OmphalosExperiment` launcher
and cumulative ledger. No direct model loop, MCP capability, new watchdog or
weaker reservation rule is needed. All changes belong inside Omphalos and
must work identically from Codex and Claude Code. Preserve the measured
writing inputs/book and keep this variant opt-in.

If useful supplied drafts still receive no checks, a later alternative is to
have the reducer propose a typed edit and let the strategy obligatorily check
each changed executable fragment before requesting a repair. That guarantees
verification at the point it matters. Count those automatic Compute checks
separately from model-requested tool calls. Do not merely mandate arbitrary
tool calls to inflate a usage statistic or recheck unchanged receipts.

## Proposed next paid pilot — not launched or authorized by this study

Test one reducer contender against a fresh current-prompt control, using the
same frozen candidate packets, book, source contexts, tool and caps for both.
The contender adds the reducer-specific contract/instructions and applicable
demonstration. The control receives the same candidate data but retains the
current writer instructions and no writer demonstration. This measures the
contender conditional on the repaired handoff; it does not isolate every
component. The two earlier reducer responses are incompatible controls
because their inputs contain no drafts.

- Stage 1: two source batches × two arms × seed 0 = **4 reducer jobs** at
  $0.20 each, **$0.80 maximum**, including $0.40 fresh controls.
- Stage 2, only if the mechanism gate passes: the same two batches × two
  arms × seed 1 = **4 jobs**, another **$0.80 maximum**, including $0.40
  fresh controls. Total at most **$1.60** from the remaining original ceiling.
- Preparation is offline reuse of the eight existing sources. No generator,
  curator, embedding, proof-panel, paid diagnostic or automatic retry charge
  is hidden. Use 4 model turns, 3 probes, 8192 output tokens and 180 Rocq
  seconds per job, with the existing 60-second/512-RPC operation bound.
  Reserve the whole required stage before dispatch. Unknown charges halt.

The primary endpoint is **useful checked new/repaired snippets retained in
the merged output**, with coverage of candidate decisions, correctness,
spending and cost per retained useful snippet. Count calls as a mechanism
measure, not the objective. Pre-label source relevance and redundancy
offline, keep failed jobs in denominators, and require every cell before
comparing. Check retained code exactly in its source context and audit every
rewrite/drop. Do not count repeated receipt reuse as fresh checking.

Expand only if both contender jobs complete, both issue a real relevant Rocq
check, at least one useful checked edit survives merging, there is no invalid
or unbound retained code, and at least one batch improves retained useful
edits over its fresh control without losing correctness in the other. Empty
inputs, all-zero exposure, missing cells, provenance violations or no useful
retained edit stop the pilot. A failed probe followed by a checked repair is
useful exposure; an arbitrary probe with no retained benefit is not a win.

After seed 1, retain the contender as a writing candidate only if the useful
edit advantage repeats in at least one batch, total useful edits increase
over the fresh control, and cost per useful retained edit is no worse (when
the control retains none, report the new cost directly). No book/prover
promotion follows from this small study. Two reused source batches provide
too few independent units for a support claim; seeds are clustered with their
sources, and no extra runs should chase p<0.10. Any later coverage experiment
requires a separately frozen book and protocol on permitted development data.

The present authorized comparison spent $1.51629542 and is closed. This
proposed pilot is a separate future decision; the study itself launches none.
