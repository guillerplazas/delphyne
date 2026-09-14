---
title: "Omphalos advisor presentation: rehearsal notes"
date: "13 September 2026"
lang: en
---

The main presentation is **15 minutes: slides 1–12**. Slides B1–B4 are for discussion. The PowerPoint contains the same short speaker notes as the Markdown source; this guide adds likely questions and file visits. All evidence is through September 12. These materials launch no experiments.

Open the PDF or PowerPoint, this guide, and [prepared excerpts](rehearsal_excerpts.md) before rehearsing. The reading document is for your understanding; do not read its paragraphs aloud. In the talk, state the result, explain the comparison, then name the limitation that affects its interpretation.

## 1 · Progress, limits, and next steps — 0:00–0:45

- Lead with controlled spending as the clearest result.
- ACE is implemented and seriously tested; its coverage benefit remains uncertain.
- End the opening with your proposed direction: useful proof-search opportunity and reliable evidence.

**Likely question: “What is the headline?”** A useful accepted budget trade-off and a promising matched Luna ACE result, with concrete explanations for several failed treatments. They are distinct contributions.

## 2 · ACE in our implementation — 0:45–1:35

- Spend less than a minute on ACE itself; the advisor already knows it.
- Point to the local additions: Rocq execution feedback, batched reduction, deterministic storage, explicit Delphyne budgets.
- Explain that a book, a search policy, and an admission rule change different parts of the program.

**Optional file visit A:** [prove_ace.py](../../prove_ace.py), lines 92–112 (`ProposeProofScriptACE`) and 289–309 (`ReflectOnTrajectory`). These show the book in a query and the evidence contract. `Playbook` is at line 150 of [ace_playbook.py](../../ace/ace_playbook.py) if asked about the persistent representation.

From `examples/omphalos`, these commands only display source:

```sh
sed -n '92,112p' prove_ace.py
sed -n '289,309p' prove_ace.py
```

**Likely question: “Did you reproduce the full ACE paper?”** We implemented its context-learning mechanism in a formal-proof setting, with identifiable adaptations. The local models, budgets, supervision, and task differ. This is not a claim to reproduce the paper's numerical benchmark gains.

## 3 · Baseline change — 1:35–2:45

- Read the three validation counts: earlier no book 27; current no book 24; current plus Luna book 27.
- Explain that the older-to-newer no-book loss is independent of ACE.
- The current flagship matches the older validation count at lower cost, but loses training coverage.

**File if asked:** [LINEAGE.md](../../experiments/campaigns/ace_attribution_20260912/LINEAGE.md), the old-versus-current program comparison table. The display figure is already sufficient for the main talk.

**Likely question: “Is the controller making the prover worse?”** The whole newer program loses coverage in that historical no-book comparison. Controller, query, feedback, and verifier-accounting changes are bundled; the data do not isolate one cause. That is a reason to diagnose the difference, not already a causal verdict.

## 4 · Experiment families — 2:45–3:40

- Group experiments into learning, delivery, control, and attribution.
- Do not enumerate every version or quote a cross-campaign leaderboard.
- The repeated lesson is that better local advice or repair does not ensure more completed proofs.

**Likely question: “Did anything improve reliably?”** The accepted budget result is practically useful. Several local defects are reproducible. Large general coverage improvements from the tested ACE variants are unestablished. Promising and inconclusive results should not be rewritten as either a confirmed win or proof of uselessness.

## 5 · Accepted budgeting result — 3:40–4:55

- The comparison is the original bounded campaign against its older X3 reference.
- Spending drops $1.5238→$0.6780; qualified solves drop 28→25 of forty.
- The original no-loss gate failed; the trade-off was subsequently accepted.

**File if asked:** [budget_history.csv](data/budget_history.csv), rows for `ace_bounded_20260908`. The other rows distinguish polish and the later control cycle.

**Likely question: “Was this Pareto improvement?”** No: it sacrifices coverage for lower cost. Whole-panel cost per solve is roughly halved, but that does not erase the three lost proofs. The later control cycle buys back coverage at higher spending, and polish ties coverage at higher spending.

## 6 · Matched Luna ACE — 4:55–6:10

- Hold the current program fixed: no book versus own book.
- Read the counts and costs; then say “three gains, no losses; p=0.25.”
- The recorded bill improves, with cache sensitivity explained shortly.

**Likely question: “Why not call this a positive result?”** It is a promising observed comparison. The small panel, historical reuse, sampling, and inconclusive paired coverage result limit a strong general claim. It can motivate bounded follow-up without automatically changing the default.

## 7 · Solver versus book — 6:10–7:20

- Read the matrix by rows, then hold the Luna-book column fixed.
- Terra is better in absolute coverage; the same book does not give it a larger increment.
- Mention the different allowances and tariffs before comparing costs.

**File if asked:** [crossover.csv](data/crossover.csv). There are six forty-cell groups, with `arm`, `cost`, `qualified_solves`, `cap`, and `uncached_cost` fields.

**Likely question: “Does a better writer help?”** Terra's own book gives Terra 30/40, versus 29/40 without it, while Luna with Terra's book stays at 24/40. Matched writer jobs also reveal quality differences, but those do not establish a general end-to-end gain. The complete crossover is stronger evidence than comparing only each solver with its own book.

## 8 · Spend curves and caching — 7:20–8:55

- X is whole-panel spending so far; Y is qualified proofs so far.
- Unsuccessful attempts move right without moving up.
- The problem order is fixed; the model panels intentionally use different dollar scales.
- Compare endpoints before discussing the curve shape.

**Cache numbers to remember:** Luna's cached-input share changes 64.6%→75.9%. Recorded bills are $0.7765→$0.6672. With all input uncached, the same token counts give $1.4487→$1.4697, a 1.45% increase. The [cache figure](meeting_figures/cache.pdf) is available outside the main deck if useful.

**Likely question: “Are the savings just caching?”** Cache discounts materially affect the saving, and reversing the discount reverses the sign of this cost comparison. Caching is economically useful, but a lower bill does not establish less intrinsic reasoning. No claim is made about unchanged cache behavior on a new workload.

**Likely question: “What about smaller budgets?”** A retrospective cost threshold filters observed successes. A newly enforced smaller allowance can change the path and requires a policy evaluation. These curves are accounting views of existing records.

## 9 · Concrete failure mechanisms — 8:55–10:20

- Wrong lesson: the accepted proof ends with `nia`, but the last proposed ending names other tactics.
- Invalid advice: a reducer introduces a rejected `have` form around an existing lemma; the checked source used `assert`.
- Lost delivery: concatenated final JSON blocks parsing, or a proposed feature never reaches a relevant request.

**Optional file visit B:** open the terminal section of [prepared excerpts](rehearsal_excerpts.md). Its original is [creator_terminal_evidence.json](data/creator_terminal_evidence.json), array entry 0, where `theorem` is `amc12_2000_p6`. Show `final_check.success`, `last_tactic`, and `final_tactic_visible`. The last field is false even though the checked proof succeeded.

**What to say:** “Success plus the last proposed script is not enough to tell the learning role what worked.” The false flag is a textual evidence gap, not a failed proof. Seven flagged histories are not seven established identical causal mistakes.

**Likely question: “Did this cause the benchmark losses?”** The local evidence defects are demonstrated. Their contribution to a particular lost theorem still requires exposure and causal evidence. We do not attribute every failure to these examples.

## 10 · Continued paths and admission — 10:20–11:45

- Selected training cases, not a random new benchmark.
- C means no ACE; E means the corrected own-book context.
- Luna stays at 4/8 and 3/8; Terra improves 4→6 and 3→7 with more money.
- Additional request/verifier allowance adds no further solves, but the remaining ordinary paths still face monetary admission.

**Optional file visit C:** [campaign_budget.py](../../runtime/campaign_budget.py), lines 262–290: `_input_bound` and `estimate_budget`. `Ledger.reserve` begins at line 138 if the advisor asks about campaign-wide accounting. Use the prepared excerpt to avoid scrolling.

```sh
sed -n '262,290p' runtime/campaign_budget.py
```

**What to point out:** the estimate includes a conservative input bound and the allowed output, before dispatch. A next request can be refused while some money remains. The ledger and per-cell policy are different control layers; improving a per-cell opportunity must not remove the campaign's financial protection.

**Likely question: “Why not give the model more money?”** Terra recovered useful proofs, but the thesis values economical control. We should first determine which remaining opportunities can be admitted or redirected productively under a safe budget. Repetition and incomplete arguments also remain visible. An unrestricted model ceiling was not tested.

## 11 · Thesis claims — 11:45–13:00

- Implementation, controlled trade-offs, and concrete failure diagnoses are defensible contributions.
- Broad ACE gains, unrestricted model ceilings, and causal credit for unexposed patches remain unestablished.
- validationX is reused development data. testX stays closed.

**Likely question: “What is the contribution if ACE is inconclusive?”** A working adaptation to Rocq, systematic experiments, a useful budget reference, and an analysis of the interfaces through which learned context, verification, and resource control succeed or fail. The contribution is more specific than a generic ACE leaderboard claim.

## 12 · Next $30 and advisor decisions — 13:00–15:00

- Prioritize admission and proof completion, then terminal evidence and checked snippets.
- Start offline; verify which defects remain in the code.
- Plan at most two isolated contenders with a contingency reserve and compatible paid references.
- Judge coverage and the entire bill together, including failed attempts.

**Ask for direction on:** which cost/coverage trade-offs the thesis should emphasize; how to frame the implementation contribution versus the ACE hypothesis; whether a future independent evaluation is necessary. This does not reopen testX.

**Likely question: “What exactly will $30 buy?”** The next Codex session will propose exact cells, stages, and attainable gates after the offline diagnosis. The ceiling includes all new experimental role calls, embeddings, diagnostics, retries, and failures. It is not an instruction to spend the whole amount, and it does not claim to measure the Codex session's own cost. The complete brief is [next_session_prompt.md](next_session_prompt.md).

## Backups and a short rehearsal routine

- **B1:** exact six-group validation counts, bills, and allowances.
- **B2:** preparation charges and conditional break-even calculations; not a generalization forecast.
- **B3:** denominators, paired/clustered inference, and distinctions among cost measures.
- **B4:** the evidence chain a learning receipt should preserve.

Rehearse once with no file visits and stop after fifteen minutes. Then rehearse each optional visit separately, allowing about thirty seconds to find the highlighted fact. In the meeting, use at most one visit unless the advisor asks for details. All three visits can use the prepared excerpt file, so the talk remains self-contained even if the source tree is inconvenient to navigate.

Do not run model calls, Rocq, global partition/repricing commands, or Ladon status while presenting. The figures and excerpts already contain what is needed. The broader report and workbook remain available for later questions.
