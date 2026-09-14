# Advisor presentation · rehearsal guide

The PowerPoint contains 24 main slides and seven backups. Every essential answer is visible on a slide. Speaker notes add nuance; file visits are optional.

## A 15–20 minute route

Use slides **1, 3, 4, 9, 10, 11, 13, 14, 15, 16, 19, 20, 21, 22, 24**. Keep the complete history tables and the exact-cost backups available for discussion. Do not rush all 31 slides into fifteen minutes.

## A complete discussion

Allow roughly 30–40 minutes for slides 1–24, including questions. Backup titles state the question they answer.

## Before opening the code

- All paths below are relative to `examples/omphalos/`.
- Use symbol search; another session is working on runtime code, so line numbers may move.
- Do not run an experiment, a benchmark loader, or a global test command during the presentation.

## Optional visits

1. `prove_ace.py`: `prove_theorem_ace`, `reflect_on_trajectory`, `curate_playbook`, `aggregate_curation_deltas`.
2. `ace/ace_playbook.py`: `merge` and `refine`; `ace/ace_store.py`: `PlaybookStore.put`.
3. `experiments/campaigns/ace_attribution_20260912/RESULTS.md`: search `Generator solves` and `evolving adaptation` for 38/40 and the controller caveat.
4. `runtime/campaign_budget.py`: `CampaignResponsesModel.estimate_budget` and `Ledger.reserve`.
5. `report/ace_retrospective/data/creator_terminal_evidence.json`: entry 0, `final_check`, `last_tactic`, `final_tactic_visible`.

## Keep these distinctions explicit

- 38/40 is evolving-book training generation; 32/40 is frozen-book training evaluation; 30/40 is validation.
- The six-solve training gap has several changed conditions. It is not six causally attributed admission failures.
- X3 28/40 in the original bounded campaign is a different reference from the later 27/40 flagship.
- Historical 80-cell results are two replicate identifiers on forty problems, not eighty independent problems.
- The 13 September resource-completion cycle is complete. The other active session is not assigned results here.

\newpage

## Slide-by-slide cues

### 01 · ACE, control and the cost of a proof

- Strong control result; modest ACE signal; concrete explanations for lost opportunity.

Open with the three numbers. They belong to different comparisons. Never present 38/40 as validation performance. This is a complete reading deck; use the rehearsal route for a shorter talk.

### 02 · The questions this update answers

- Separate implementation fidelity, local correctness, coverage and economic value.

Use these questions as a map. Each is answered visibly later; no claim depends on speaker notes or a live file visit.

### 03 · Our ACE loop, in one slide

- The Reducer is a local batching component; the deterministic merge owns the stored state.

The advisor knows ACE. Spend at most 45 seconds here. Emphasize the local Reducer and the separation between the evolving book and frozen inference.

### 04 · Where each ACE element lives in the code

- All paths are relative to examples/omphalos; search by symbol because active code can move lines.

Optional visit 1: prove_ace.py; compare the four strategies and their policy functions. Visit 2: ace/ace_playbook.py merge; then ace/ace_store.py PlaybookStore.put. Mapping describes the measured architecture, not unbenchmarked work in the other session.

### 05 · What counts as a solve—and what is capped?

- A nominal allowance, a request reservation and the eventual bill are different quantities.

Do not conflate the original canonical $0.05 setting with X experiments. The slide deliberately gives the settings behind the principal comparisons. testX and protected challenge outcomes remain excluded.

### 06 · Development cycles 1/4 · replication and X3

- For X rows, 80 cells = the same 40 validationX problems at two replicate identifiers.

These are development reconstructions, not independent repeated confirmations. Early incomplete top-k, no-Reflector and online archives are not scored as complete panels. All later X counts use their explicitly named versions; v2 three epochs scored 50/80.

### 07 · Development cycles 2/4 · better advice and delivery

- Advice can be correct, cheaper to send, or more traceable without completing more theorems.

The stronger-writer treatment still uses Luna as Generator. The later all-Terra training chain is different. x6 has one raw success above the retrospective $0.10 qualification threshold. Old cost exports do not necessarily contain every retry receipt.

### 08 · Development cycles 3/4 · control and local checks

- Local episodes, theorem cells and campaign bills have different denominators.

Applicability primary screen stopped; no full train/validation benchmark followed. Checked-change correctness improved 3/6 to 6/6. The control-cycle archived source has reconstruction limitations; do not quietly rerun it as the same experiment.

### 09 · Development cycles 4/4 · coverage and attribution

- Completed cycles are preserved as evidence; the latest losing variants are not the new default.

The September 13 row is a completed snapshot, not a report on the other active session. Costs and controller details appear later. The ledger and archival scores are left unchanged.

### 10 · The strongest result is a budget trade-off

- Both use a nominal $0.10/problem allowance; the controller changes what gets admitted.

The comparator is the older review X3 seed-0 run, not the latest 27/40 flagship. Total cost includes failed attempts. Categorical bars show measured alternatives; there is no interpolated budget-response curve.

### 11 · A changed baseline explains part of the confusion

- All use Luna and $0.10/problem; controller, feedback and runtime lineage still differ.

The first arrow is a historical program comparison, not a paired single-feature ablation. The second is the intended book intervention within the bounded program, still subject to historical/provider conditions. File: experiments/campaigns/ace_attribution_20260912/LINEAGE.md.

### 12 · Luna’s book helps here—but the signal is small

- Luna / medium / $0.10 per problem / 64 requests / 300 verifier seconds.

Do not say ACE is proved effective, proved ineffective, or equivalent. The whole-panel count is more informative than a count of cherry-picked repaired cases. Cache economics are separated later.

### 13 · The full crossover separates solver from book

- Each cell is 40 validationX problems; costs include failures and exclude book preparation.

Rows are solver models, columns are frozen books. Luna cap $0.10; Terra $1.00. Same-book interaction −7.5 percentage points, paired p=0.375. Own-Terra book increment p=1.0. Reused records do not become independent theorems.

### 14 · What the Luna / Terra experiment changes

- The study does not establish that model scale unlocks ACE; an intrinsic model ceiling also remains unproven.

Avoid a categorical statement that Terra cannot benefit. The same-book interaction has p=0.375 and the own-Terra difference p=1.0. Small gains and the study design limit conclusions.

### 15 · Yes: Terra achieved 38/40 during book creation

- 38 → 32 compares two training executions; 30/40 is a different partition, not another measured decline.

Terra is used for all four generative roles. One shuffled pass, four-problem batches, final book 26 bullets / 2426 estimated tokens. The two training-generation misses were algebra_amgm_sum1toneqn_prod1tonleq1 and imo_1967_p3. Source: training_evolution.json and training_accounting.json in ace_attribution_20260912.

### 16 · Why did 38 become 32? What we know—and do not

- The gap motivates diagnosis; it does not show that the finished book destroyed six proofs.

Same nominal Terra generator allowance $1.00, different stopping semantics. Do not assign a numerical share of the six-solve gap to the controller, compression or sampling without a matched intervention.

### 17 · Creating a book is a real up-front expense

- Preparation and inference are separate bills; generation is the largest preparation component.

The bars are additive costs, not a learning curve. Luna final size 2103 estimated tokens; Terra 2426. Breakeven uses assumed future workloads and belongs in the backup question.

### 18 · Spent versus solved: the actual recorded staircase

- Luna endpoints: 24 / $0.7765 vs 27 / $0.6672. Terra: 29 / $6.6106 vs 30 / $6.4513.

Two model-specific dollar scales avoid squeezing Luna into an unreadable sliver. Step plots preserve discrete solve increments. Do not smooth these observations or imply the task order is an optimized execution policy.

### 19 · Cache discounts change the economic conclusion

- The saving is real at the observed tariff; it cannot all be attributed to less computation.

This counterfactual reprices the same trajectories; it does not rerun the models or change admission behavior. Bar pairs deliberately replace straight-line trajectories between unrelated price scenarios.

### 20 · Four failure mechanisms behind weak transfer

- Capture → validate → retain → expose → use → finish. A failure anywhere can erase the benefit.

Terminal witness: amc12_2000_p6. The missing-text flag alone does not prove every affected training lesson was wrong. Syntax acceptance is not full theorem success; exposure is not causal attribution.

### 21 · More allowance recovered Terra proofs, then stalled

- The final plateau is not evidence of an unrestricted model-capability ceiling.

C = no ACE; E = corrected own-book context. Level 0 caps Luna $0.10 / Terra $1.00. Level 1 doubles money to $0.20 / $2.00 while retaining 64 requests / 300s. Level 2 retains that money and gives 128 requests / 600s. Costs in backups include each prefix once.

### 22 · 13 September: the first completion fixes did not win

- A reduces the response cap from 32,768 to 4,096 tokens. Completed cycle; ongoing code work is unscored.

These are historical seed-0 controls and fresh candidate trajectories. Validation is reused development data. The frozen book is unchanged. Output cap is a model-response limit including reasoning, not the final visible proof length.

### 23 · Are failed ideas inherited by later experiments?

- Optional treatments are isolated by switches; shared-code behavior still deserves regression checks.

This is an assessment of inspected configuration and history, not a proof of complete behavioral equivalence. Raw BoundedConfig defaults differ from the reference’s explicit admission=False / restart=False settings. No code is changed by preparing this presentation.

### 24 · The thesis claim and the advisor decisions

- Evaluate improvements by completed proofs and the whole bill, with mechanism exposure recorded.

Close with decisions, not a promise that the active code work will succeed. The original $30 proposal has begun; the completed first cycle is already included. No new budget or experiment is requested by this deck.

### 25 · What are the exact crossover costs and caps?

- Luna / medium / $0.10 cap; Terra / medium / $1.00 cap; 64 requests and 300 verifier seconds.

Exact source: report/ace_retrospective/data/crossover.csv. Own-book p-values: Luna 0.25; Terra 1.0. The full crossover tests solver/book combinations, not a general scaling law.

### 26 · Which historical books improved coverage?

- Two replicate identifiers on 40 validationX problems; separate books and delivery methods.

Directly labeled horizontal bars show categorical treatments. Bills were repriced from tokens at the audited snapshot; they are not guaranteed complete historical retry receipts. Incomplete arms are excluded, not silently counted as full panels.

### 27 · How can a run stop while money remains?

- Unused money is not automatically spendable; looser admission must still respect financial protection.

Illustrative recorded continuation: remaining $0.085742, next reservation $0.086368. This is $0.000626 over the balance. File: runtime/campaign_budget.py, CampaignResponsesModel.estimate_budget and Ledger.reserve. Do not make all reservations unsafe just to admit more calls.

### 28 · When would preparing the book pay for itself?

- This is arithmetic under fixed assumptions, not a prediction of external generalization.

Break-even = known preparation cost divided by observed per-attempt inference saving. Values are rounded upward to whole attempted tasks. No extrapolated straight-line chart is needed to convey these conditional figures.

### 29 · Which evidence should an ACE lesson retain?

- File to inspect: report/ace_retrospective/data/creator_terminal_evidence.json, entry 0.

Other fields and full paths are in rehearsal_excerpts.md. Seven of 33 source successes have a missing terminal-tactic text flag; this is not seven established identical causal errors.

### 30 · Why is +3 solves not yet a supported gain?

- Do not buy extra seeds merely to cross a significance threshold; testX stays closed.

Five independent all-favorable discordances give exact two-sided p=0.0625. This is a minimum for attainable significance, not a power calculation. Small samples and historical controls warrant restrained interpretation.

### 31 · Which files should I rehearse before presenting?

- Read-only rehearsal; no experiment launch, partition loader or live model call is needed.

A short presentation route and file checklist are in advisor_rehearsal.md / advisor_rehearsal.pdf. The older rehearsal_notes files describe the previous sixteen-slide deck.
