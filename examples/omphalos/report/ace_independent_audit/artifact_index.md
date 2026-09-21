# Evidence and reproduction index

**Final study: all 2,044 registered solver attempts are complete.** Start with
the [short report](short_report.md) or [full report](long_report.md); PDF exports
are [short](short_report.pdf) and [long](long_report.pdf). The
[package README](../../experiments/ace_independent_audit/README.md) documents
commands usable from either Codex or Claude Code. No paid experiment remains
pending. Only trainX and validationX were used.

## Current results and numerical review

| Artifact | Evidence |
|---|---|
| [Complete serving table](serving_tables.md) | All frozen and online panels, ordinary controls, costs, coverage and intervals |
| [Serving CSV](serving_results.csv) / [replicates](serving_replicates.csv) | Exact panel and replicate totals, including B1's invoice range |
| [Main results](fresh_results.json) / [cells](fresh_cells.json) | Original finalized 1,520-cell benchmark and per-cell hashes |
| [O1 results](adaptive_frozen_results.json) / [cells](adaptive_frozen_cells.json) | Complete 160-cell adaptive-then-frozen follow-up; train 12.97% and validation 4.54% savings |
| [R1 results](rule_repair_results.json) / [cells](rule_repair_cells.json) | Complete eighty-cell manual rule diagnostic, including its direct A2 comparison |
| [Mechanisms](fresh_mechanisms.json) | Request counts, token fees, failure spending, paired theorem contributions, uncached fixed-trajectory sensitivity |
| [Reviewed final diagnosis](final_diagnosis_reviewed.json) | Independent reconstruction of all 320 A0/O1 raw cells, selected proof traces, rule origins, joint-budget statistics and amortization |
| [Budget results](budget_replay_results.json) / [cells](budget_replay_cells.json) | All 4,560 exact controller scenarios, with no new model draws |
| [Budget frontier](budget_frontier.csv) | Full stopping-allowance grid for every frozen arm |
| [Statistical review](statistical_review.json) | Reviewed p-values for 263 current and historical comparison records; inclusive tie correction with all other statistics unchanged |
| [Final economics](final_economics.json) | Selected-recipe preparation, online operating cost, amortization, complete research bill |
| [Online chronology](online_chronology.json) | Eighty score-before-update checks and train-only provenance |
| [Figures](figures/README.md) | Standalone PNG, SVG and PDF figures |

`statistical_review.json` explicitly supersedes the matching p-values in the
original finalized JSON files. It corrects floating-point exclusion of equal
sign-flip statistics. The material change is one secondary ordinary-budget
family p-value, from 0.000020 to 0.063179 (exact enumeration 0.0625). Sixty-two
other p-values increase by one Monte Carlo count. No cost, outcome, bootstrap
interval, practical decision or p<0.10 classification changes. Original
numerical files and the pre-correction `final_diagnosis.json` remain preserved.
The current report-input function selects reviewed serving statistics.

All serving costs include failed attempts. Frozen preparation fees are shown
separately; online update fees are part of operating cost. Budget scenarios
are conditional replays of observed responses and actual cache charges.
TrainX is familiar-workload reuse; validationX is reused development transfer.
The 15.69% joint validation saving compares O1 at $0.05 with ordinary A0 at
$0.10. Ordinary budget control accounts for 11.86%; matched-$0.05 ACE adds
4.35% at equal coverage.

## Completed proof and implementation diagnoses

| Artifact | What was checked |
|---|---|
| [LCM repair](lcm_repair_certification.json) | Original theorem compiles and passes the ordinary unassisted bridge in 1.69 seconds |
| [Context-expansion repairs](context_repair_certification.json) | Two failed induction candidates close with a narrow algebraic ending |
| [Goal-flood probe](goal_flood_probe.json) | 192-goal proposal under bounded, unassisted execution |
| [Goal-flood timing](goal_flood_timing.json) | Completed trajectory, local versus API time, feedback and prompt expansion |
| [Invalid witness proof](goal_flood_witness_certification.json) | Compiled symbolic duplicate witness; unsuccessful concrete probe preserved |
| [Missing-dependency repair](pilot_dependency_repair.json) | One omitted symmetry equation closes the saved second candidate |
| [R1 prime dossier](r1_prime_dossier.json) | Familiar-theorem cost concentration and unchanged A2 advice |
| [Teacher gain dossier](teacher_gain_dossier.json) | All four B2 gains against B0 and rule provenance, without invented bullet causality |
| [Output categories](validation_token_categories.json) | Reasoning versus other output for the original seven validation panels |
| [Capped-output census](output_repetition_diagnosis.json) | All 27 capped replies in those seven panels; 23 blank legacy parses, one valid recovered proof |
| [Provider retrieval check](output_repetition_provider_check.json) | The same 91,617-character repeated response retrieved by its stored response ID |
| [Parser/controller replay](parser_replay_certification.json) | Earlier valid-proof acceptance at four caps; one actual following request avoided |
| [Pilot repeat](pilot_repeat_diagnosis.json) | Same twelve pilot problems under new draws, 48 identical initial-request pairs, unfavorable repeat retained |
| [Rule probes](rule_probe_certification.json) / [repair probes](rule_repair_certification.json) | Sixteen executable claim checks, including failing advice and compiling corrections |
| [Historical output-cap diagnosis](reproduction_output_cap_diagnosis.json) | All 320 allowed reproduction cells and 4,551 admission checks; joint versus matched-cap effects |

These repairs do not replace a benchmark outcome or enter the measured frozen
books. They establish executable mechanisms and local repairs, not autonomous
benchmark successes.

## Learning, scale and preparation

| Artifact | Evidence |
|---|---|
| [Author selection](../../experiments/campaigns/ace_independent_audit/author_selection.json) | Luna/Terra/Sol/Astra authors at medium/high effort; Luna solver throughout |
| [Author ladder economics](../../experiments/campaigns/ace_independent_audit/author_ladder_economics.json) | Paid preparation and pilot selection costs |
| [Preparation detail](preparation_economics.json) | Fixed sources, audit fees, frozen book sizes and deterministic teacher work |
| [Learning fee breakdown](learning_cost_breakdown.json) | Input/output, unused writes and long-context author tariffs |
| [Six-call cache experiment](learning_cache_diagnostic.json) | Actual author-only input fee reduction of 20.0%; no measured book replaced |
| [Rule provenance](book_signal.json) | Fixed-book retained-rule origins and source outcomes |
| [O1 protocol](../../experiments/campaigns/ace_independent_audit/adaptive_frozen_protocol.json) | Order zero selected before curriculum completion; exact source and accounting contract |
| [O1 frozen book](../../experiments/campaigns/ace_independent_audit/books/O1_adaptive_frozen.json) | Final 58-rule, 19,679-character artifact |
| [ACE paper](../../papers/2510.04618v3.pdf) | Local primary publication used for the offline/online and cost-denominator analysis |

## Certification, incidents and billing

| Artifact | Evidence |
|---|---|
| [Full-study certification](study_certification.json) | 2,044 cells; 2,040 normal replays; four terminal checks; 1,215 distinct compiled proofs covering 1,537 solved cells |
| [Receipt certification](receipt_certification.json) | Every returned provider response repriced; one retained timeout bound; 91 rejected zero-charge calls |
| [Numerical completion](numerical_finalization.json) | Original automatic finalization and ten immutable output hashes |
| [Final review checks](final_review_checks.json) | Code validation, report exports, unchanged experimental sources and preserved numerical artifacts |
| [Credit continuation](continuation_diagnosis.json) | Original eight-response prefix retained; 23 final responses plus one rejection, failed at $0.10516041 |
| [Rate continuation](rate_diagnosis.json) | All 87 interrupted original trajectories continued, preserving 83 paid responses and actual cache fees |
| [Timeout reconciliation](billing_recovery_proposal.md) | Failed outcome and full unknown-request liability retained |
| [Concurrency amendment](../../experiments/campaigns/ace_independent_audit/rate_recovery/concurrent/amendment-v3.json) | User-authorized four-request dispatch with unchanged solver treatment |
| [Queue initialization repair](../../experiments/campaigns/ace_independent_audit/rate_recovery/concurrent/initialization_repair.json) | Lock-only directory initialization before any API call, with zero-receipt guards |
| [Final artifact manifest](artifact_manifest.json) / [review files](review_files.json) | Compact deliverable hashes, accounting and inventory of the retained raw corpus |
| [Accounted receipts](accounted_receipts.csv) | Settled invoices versus the explicitly bounded timeout receipt |

The $317.40915825 settled total plus the $0.22239272 unknown-request bound
forms the research-cost interval. The upper endpoint is liability, not an
assertion of an exact invoice. The one bounded B1 train cell remains failed;
no timeout or context failure was replaced. Administrative interruptions were
continued from the exact paid prefix, then scored normally at final outcome.
Scheduling/account changes remain a cache-comparability limitation.

## Historical reconstruction and retained checkpoints

The [audit inventory](audit_inventory.json), [completion](audit_completion.json),
[variant catalogue](all_variants.csv), [solver panels](historical_solver_panels.csv),
[learning roles](historical_learning_roles.csv) and
[matched comparisons](historical_matched_comparisons.csv) reconstruct permitted
individual raw cells rather than accepting old conclusions.
[Continuation reconciliation](historical_continuations.json) and
[reconciled panels](historical_reconciled_panels.csv) remove duplicated recorded
prefixes. [Original-loop comparisons](historical_original_comparisons.json)
remain distinct from later grounded-agent contracts. Their reviewed p-values
are in the versioned statistical review above.

[Historical proof certification](historical_proof_certification.json) covers
3,485 distinct scripts and 4,953 solved permitted cells. The
[monolithic parser check](monolithic_parser_certification.json) examines all
196 saved replies without model calls. Missing cells and preparation failures
remain visible; heterogeneous historical labels are not pooled as equivalent
independent benchmarks.

The [initial checkpoint snapshot](checkpoint_review_snapshot.json) preserves
346 review files, including the original reports. Its 1,019-attempt,
$282.32564758 checkpoint is historical. The later
[credit-checkpoint report archive](credit_checkpoint_reports.json) preserves
the exact narrative documents before final synthesis. Its
[inventory](quota_checkpoint_inventory.json) and
[receipt certificate](quota_checkpoint_receipt_certification.json) document
the 1,623-completed-attempt credit pause; they are not the final study verdict.

Raw `runs/`, `responses/`, learning events and evidence, transport snapshots,
verification and kernel outputs remain local under the campaign tree.
`ledger_final.sqlite3` preserves the closed ledger. The final inventory reads
only this study and the explicitly scoped historical census. No credential,
closed evaluation partition or protected challenge artifact enters the review
bundle. User AGENTS edits and local tracking files remain unstaged.
