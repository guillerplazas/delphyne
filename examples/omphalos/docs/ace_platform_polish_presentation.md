# ACE platform polish: fixes, failure patterns and playbooks

- **Prepared:** 14 September 2026.
- **Comparison:** flagship X3, the previous role pipeline (v1), and the
  polished role pipeline (v2), with a historical non-ACE reference.
- **Scope:** trainX and validationX. testX and the protected challenge
  remain closed.
- **Main finding:** the pipeline preserves and reviews learning evidence
  more reliably; improved theorem-solving performance remains unproven.

## 1. What changed in the pipeline

- **Reflector:** reads a recorded training event, identifies a local
  obstacle, and saves an explicitly unverified repair.
- **Curator:** checks the proposed repair in its exact Rocq context and
  proposes an addition, correction, example attachment or rejection.
- **Reducer:** compares proposals with existing advice, reuses checked
  evidence, obtains a separate novelty judgment, and produces reviewed edits.
- **Generator:** receives the frozen playbook during proof search. Both
  benchmark arms use the same generator tools, model and controller.
- **Role skills:** short instructions and executable demonstrations guide
  each adaptation role through its particular decisions and tools.
- **Evidence:** a verification receipt records the exact snippet, source
  context and observed result. It establishes what executed locally.

```text
Recorded trajectory
  → Reflector: save a local repair draft
  → Curator: check the repair and propose a disposition
  → Reducer: review novelty and apply justified edits
  → Frozen playbook
  → Generator: use the advice during proof search
```

### Tools and skills by role

- **New in v2:** two model-facing tools, three role skill files, structured
  role outputs, a separate edit-review query, and role demonstrations.
- **Generator — prove the target theorem:**
  - Reuses `ReadSkill` to load Rocq reference material, `SearchRocq` to
    inspect available lemmas and types, and `InspectProofState` to inspect
    a verified proof prefix within bounded output and execution limits.
  - Reuses seven static references: `rocq-phrasebook`, `proof-templates`,
    `tactics-reference`, `tactic-patterns`, `compilation-errors`,
    `compiler-guided-repair` and `coq-stdlib-guide`.
  - Receives the learned playbook as additional prompt context.
  - No new generator reasoning tool or generator skill file was introduced
    in this treatment. The shared pause mechanism applies to both arms.
- **Reflector — extract a repair from recorded experience:**
  - Reuses `ReadTrainingEvidence` from v1 to read an exact recorded event,
    including the submitted code, verified prefix and error.
  - Adds `SubmitLocalRepair` to save the diagnosis, operation,
    prerequisites and raw Rocq code as an explicitly unverified draft.
  - The new reflector skill teaches local learning from unsolved sources
    and separates draft submission from the final `done`/`abstain` choice.
- **Curator — verify evidence and propose a book edit:**
  - Reuses `CheckAdviceSnippet` from v1 to execute raw Rocq sentences in
    the supplied source context and return a verification receipt.
  - Adds `FindBookRules`, shared with the reducer, to find related advice
    through transparent lexical search. Similarity alone does not prove
    that an idea is new.
  - The new curator skill teaches receipt reuse and the four dispositions:
    `add`, `update`, `example` and `drop`.
  - Changed code requires a new check; an unchanged receipt can be reused.
    Each writer allows at most three new checks and 180 aggregate Rocq
    seconds, with a 60-second limit per check.
- **Reducer — decide what should enter the shared book:**
  - Uses `FindBookRules` and `CheckAdviceSnippet`; original drafts and
    receipts remain available after an invalid curator final.
  - The new reducer skill teaches comparison with the closest existing
    rule, compact edits, evidence-only examples and at most three retained
    decisions per batch.
  - Adds `JudgeBookEdit`, a separate model query invoked by the reducer
    strategy to classify proposals as a new operation, correction,
    example, duplicate or unsupported claim.
  - The review sees the checked code, source context, errors and remaining
    goals without the proposer's persuasive rationale. Later reviews see
    earlier accepted edits. The query runs within the reducer role, and
    its verdict can still be wrong.

### Supporting implementation

- **Role contracts:** `ReflectLocalRepairs` and `ProposeBookEdits` produce
  typed outputs that distinguish drafts, final plans and checked evidence.
- **Recovery:** structured products and a durable journal preserve partial
  work; validation checks the ordered review trail before applying edits.
- **Demonstrations:** new executable examples show the reflector–curator–
  reducer handoff and duplicate review. Selection matches the role and
  excludes demonstrations from the source theorem's family.
- **Skill packaging:** the three new skills are project prompt Markdown,
  loaded automatically by the corresponding query. They work with either
  repository harness; the generator references are existing vendored data.
- **Budgeting:** the revision reuses the campaign ledger, request admission,
  model registry and replay recording, and adds cooperative pause handling.
- **Observed benefit:** curators performed 53 checks; reducers reused their
  receipts with zero additional checks. This demonstrates evidence reuse,
  while the benchmark below assesses the resulting book.

## 2. Bugs and implementation failures addressed

- **Work lost after an invalid final answer:**
  - Structured partial products preserve drafts, checked snippets,
    contexts and diagnostics.
  - The next role can use that evidence even when the final plan is invalid.
- **Work lost at a budget stop:**
  - Intermediate products are checkpointed through Delphyne Message nodes.
  - A reducer can recover the latest checkpoint when the strategy returns
    no final solution.
- **Misleading reflector feedback:**
  - The previous reflector could mix a proposed repair with abstention
    and receive an incorrect complaint about the event reference.
  - Draft submission and final disposition are now separate; feedback
    identifies the conflicting fields.
- **Duplicate advice and append-only corrections:**
  - Decisions explicitly distinguish `add`, `update`, `example` and `drop`.
  - A separate query reviews whether the proposal adds a missing operation,
    corrects advice, or merely supplies another example.
  - An update targets an existing rule and requires rejected and repaired
    snippets in the same source context.
- **Duplicates within a batch:**
  - Later reviews see earlier accepted edits.
  - A deterministic check folds exact duplicates into evidence attachments
    without incrementing helpfulness counters.
- **Stale or conflicting edits:**
  - Book and target-rule hashes are checked before application.
  - Conflicting updates or oversized batches are rejected atomically.
  - Updates preserve rule identity, section and existing counters.
- **Repeated evidence and excessive prompt growth:**
  - Handoffs carry a compact plan summary and one evidence catalogue.
  - New rule text is limited to one paragraph and 700 characters.
  - The book has a 4000-estimated-token ceiling; examples stay outside the
    generator prompt.
- **Cancellation leaving requests running:**
  - A shared pause flag blocks subsequent operations.
  - Already admitted requests drain and settle their charges.
  - This replaces reliance on stopping only the launcher process.

## 3. Typical mistakes made by the agents and evaluation

- **Treating execution as novelty:**
  - Another successful `nia` or `vm_compute` example may repeat existing
    advice.
  - Six of the previous eight additions were judged redundant.
- **Packaging a whole proof as a reusable lesson:**
  - Previous additions included long scripts, particular numbers and
    hypothesis names inside prompt text.
  - The revised representation separates the compact operation from its
    worked evidence.
- **Discarding local learning because the theorem is unsolved:**
  - A failed trajectory can still contain a useful local repair.
  - All 12 unsolved training sources produced drafts in the new run.
- **Using abstention as a proxy for learning:**
  - Four of the previous reflector pilot's five “useful” judgments were
    abstentions.
  - Faithful diagnosis, abstention and useful retained advice now receive
    separate counts.
- **Claiming more than the snippet establishes:**
  - A normalization equality can be proved while the intended contradiction
    remains open.
  - Entering an assertion can create another obligation; it does not by
    itself prove that assertion.
  - Reviews must distinguish executed commands, completed local obligations
    and completed theorems.
- **Combining incompatible action fields:**
  - Examples include choosing `drop` while supplying rule text or evidence,
    or attaching a failure receipt to a non-update action.
  - Six curator finals were invalid for these reasons; their partial
    evidence survived.
- **Rejecting useful local progress too aggressively:**
  - A reviewer can demand whole-theorem completion even when the proposed
    lesson concerns a local repair.
  - One recorded trigonometric case appears to show this problem; details
    are below.

## 4. What the live adaptation demonstrated

- **40 reflectors:** all completed; 29 drafts and 11 abstentions.
- **29 curators:** 23 complete final plans and six partial products.
- **10 reducers:** all completed; no role product was missing.
- **53 new Rocq checks:** all performed during curation.
- **Zero new reducer checks:** reducers reused existing receipts.
- **16 separate review judgments:** resulted in one new operation, one
  correction, six evidence-only examples and eight unsupported dispositions.
- **Recovery example:** the reducer retained a logarithmic example from the
  partial `aime_1988_p3` curator using its existing receipt.
- **Learning from failures:** one of the 12 unsolved sources supplied a
  retained text correction; the previous run retained none from unsolved
  sources.
- **Preparation cost:** $0.45092992, versus $0.31268266 for the previous
  full adaptation pass.
- **Interpretation:** these are descriptive mechanism measurements, not a
  randomized ablation of individual tools. Review verdicts remain model
  judgments rather than independent human labels.

## 5. How the playbooks look

| Book | Rules | Estimated prompt tokens | Result of adaptation |
| --- | ---: | ---: | --- |
| Flagship X3 | 26 | 2103 | Starting book |
| Previous learned book, v1 | 34 | 3994 | Eight additions; six judged redundant |
| Polished pipeline's book, v2 | 27 | 2224 | One addition, one correction; six examples outside the prompt |

- Both learned books were generated separately from the same flagship.
- The v2 book is approximately **44% smaller than the previous candidate**
  and **5.8% larger than the flagship**.
- The final v2 book contains 25 unchanged rules, one updated rule and one
  new rule.
- Its sections contain **8 pitfalls, 9 tactics, 8 lemma rules and 2 strategy
  rules**.
- Common subjects include polynomial normalization, recurrence indices,
  natural/real casts, nonzero denominators, logarithms, trigonometric
  rewrites and finite computation.

### The two retained text changes

- **Corrected rule `rocq-00026`: logarithm prerequisites.**
  - Establish positivity of each factor before applying `ln_mult`.
  - For an `Rpower` factor, unfold `Rpower` and use `exp_pos`.
  - Positivity of the enclosing product does not supply the required
    factor-positivity premise.
  - Source: the unsolved `amc12a_2020_p13` trajectory.
- **New rule `rocq-00028`: proving a factor nonzero.**
  - Expose the polynomial equations from multiple root hypotheses.
  - Assume the factor is zero, substitute, and contradict the given
    disequality using arithmetic.
  - Source: the accepted `mathd_algebra_206` trajectory.
- **Six retained examples:** illustrate existing square-nonnegativity,
  induction-rewriting, logarithmic-power and reciprocal techniques without
  adding more prompt text.

## 6. What still needs improvement

- **An old rule for converting whole numbers to real numbers is wrong.**
  - Rule `rocq-00015` suggests `change INR 2 <= INR c`, which Rocq
    rejects as written.
  - A tested fix first proves both forms of `2` are equal,
    then rewrites the goal.
  - The learning run did not save this fix in the playbook.
  - Rule `rocq-00025` warns about this too: old rules also need checking
    for mistakes and contradictions.

  Tested fix:

  ```coq
  assert (Htwo : (2 : R) = INR 2) by (cbv [INR]; ring).
  rewrite Htwo.
  apply le_INR.
  lia.
  ```

- **A likely overly conservative review decision remains.**
  - In reducer batch 3, an `imo_1963_p5` repair executed through `ring`
    and left no focused goals, while the surrounding theorem remained open.
  - The reviewer rejected the proposal while emphasizing incomplete
    whole-proof status.
  - This appears to undervalue a completed local repair; it is an inference
    from the saved receipt and rationale, not a new live verification.
  - A focused review test should distinguish local completion, background
    obligations and global theorem completion.
- **Useful advice can be missed.**
  - The previous candidate's useful natural-power normalization and
    exponent-injectivity lesson is absent from the new book.
  - Compactness alone is insufficient evidence of playbook quality.
- **The action interface still invites malformed combinations.**
  - Conditional action schemas should make irrelevant fields unavailable.
  - Preserve receipt validation and recovery while improving usability.
- **Further generator tools need a separate case.**
  - This experiment measures the learned book under a matched generator.
  - Example retrieval or other generator tools need their own bounded
    mechanism tests and comparison.

## 7. Benchmark and verification

| Panel | Flagship qualified solves | v2 qualified solves | Flagship inference cost | v2 inference cost |
| --- | ---: | ---: | ---: | ---: |
| trainX | 29/40 | 28/40 | $0.71128344 | $0.68593736 |
| validationX, two seeds | 47/80 | 48/80 | $1.55318798 | $1.52856742 |

- Validation gained **one solve** at **1.6% lower inference cost**.
- Coverage is inconclusive: paired two-sided **p=1.0**; descriptive
  family-bootstrap 90% interval **[-2.5, +5.0] percentage points**.
- Validation cost ratio: **0.9841**, with 90% interval **[0.9223, 1.0431]**.
- The 80 validation cells per arm are 40 theorems measured twice;
  inference clusters repeated measurements by theorem family.
- The registered practical threshold was missed: at least two extra solves
  at no more than 1.25 times cost, or at least 10% savings with no more than
  two fewer solves.
- Validation inference cost per solve: **$0.03304655** for the flagship and
  **$0.03184515** for v2; including v2 preparation raises its cost per solve
  to **$0.04123953**.
- The small billing difference is sensitive to caching: repricing the same
  observed tokens without cached-input discounts makes v2 about 0.9% more
  expensive. That sensitivity does not simulate different budget stops.
- **The flagship remains the default.** validationX is reused development
  data; this comparison is not independent held-out confirmation.

Verification and accounting:

- **55 scoped tests passed before paid dispatch**, including recovery,
  atomic updates, pause settlement and campaign integration.
- **11 relevant receipts were rechecked with real Rocq**, including rejected
  snippets used in review.
- **All 319 jobs replayed exactly**, matching outcomes, budgets and values
  with HTTP blocked and zero new charges.
- **235 sealed source paths and 319 input hashes matched**; all 120 candidate
  training/validation cells received the frozen book.
- Scoped Pyright and Ruff passed; root type checking retains 17 pre-existing
  `why3py.simple` errors outside Omphalos.
- Fresh experiment spending: **$4.92990612 of $40**; 3005 settled receipts,
  zero unresolved charges and zero platform failures.
- Earlier charges remain preserved outside the explicitly reset budget.

## 8. Comparison with an equivalent non-ACE method

### The closest equivalent

- **An equivalent non-ACE configuration exists:** run
  `prove_theorem_grounded` with an empty playbook and no adaptation roles.
- It keeps the bounded, focused proof-search loop, static Rocq skills,
  demonstrations, verifier feedback and generator tools described above.
  “Non-ACE” here means no learned cross-problem advice or playbook updates.
- The earlier Luna comparison matched the model and medium reasoning
  setting, 64-request allowance, $0.10 per-theorem cap, 300 aggregate Rocq
  seconds, shown definitions and proof-search settings.
- The older generic agentic baseline also exists, but used 32 requests,
  different feedback and different budget enforcement. Its results mix
  ACE's effect with other platform changes; the empty-book configuration
  provides the closer comparison.

### What the earlier comparison measured

- The 12 September attribution study compared the empty-book configuration
  with historical X3 results on **40 trainX and 40 validationX cells per
  arm**, using replicate identifier 0.
- These are the earlier study's measurements, separate from the fresh
  two-replicate polished-platform benchmark in section 7.

| Panel | Non-ACE qualified solves | X3 qualified solves | Non-ACE inference cost | X3 inference cost |
| --- | ---: | ---: | ---: | ---: |
| trainX | 28/40 | 28/40 | $0.81821062 | $0.68922336 |
| validationX | 24/40 | 27/40 | $0.77651210 | $0.66722836 |

- **Coverage:** X3 gained three validation solves, or 7.5 percentage points;
  the paired two-sided **p=0.25** leaves the improvement inconclusive.
- **Recorded cost:** X3 cost 14.1% less on validation; inference cost per
  solve fell from **$0.03235467 to $0.02471216**.
- **Historical limits:** X3 controls were reused, rather than rerun
  contemporaneously. validationX is repeatedly used development data, and
  trainX supplied the book's learning material.
- **Caching matters:** pricing the same observed tokens without cached-input
  discounts makes X3 1.45% more expensive. This is a billing sensitivity,
  not a fresh uncached experiment or proof of better reasoning efficiency.
- **Preparation matters:** the table includes unsuccessful proof attempts
  but excludes book preparation. Original X3 preparation cost at least
  **$0.91692376 before embeddings**; the v2 pass later added $0.45092992.
  The empty-book method has no learned-book preparation cost.

### What can be said about polished v2 versus non-ACE

- **The polished campaign tested X3 against v2; it did not include a fresh
  empty-book arm.** Its 47/80 versus 48/80 result cannot establish v2's
  advantage over non-ACE.
- For descriptive context, v2's first validation replicate achieved
  **24/40 at $0.74908726**, compared with the historical empty-book result
  of **24/40 at $0.77651210**: equal solve counts and 3.5% lower recorded
  inference cost.
- That cross-campaign comparison does not hold platform version, execution
  date or caching conditions fixed. It is insufficient to claim that the
  polished method improves on non-ACE.
- A direct estimate requires a fresh empty-book arm under the same polished
  policy and matched validation replicates. The current evidence supports
  the platform reliability improvements while leaving the performance
  advantage over non-ACE unresolved.

## 9. Where to find the playbooks and relevant files

All paths below are relative to `examples/omphalos/`. Links resolve from
this Markdown file.

### Playbooks

- **Flagship:**
  [experiments/playbooks/ace_x3_offline.yaml](../experiments/playbooks/ace_x3_offline.yaml).
- **Previous learned book, v1:**
  [experiments/campaigns/ace_roles_20260913/book.yaml](../experiments/campaigns/ace_roles_20260913/book.yaml).
- **Polished pipeline's learned book, v2:**
  [experiments/campaigns/ace_revision_20260913/book.yaml](../experiments/campaigns/ace_revision_20260913/book.yaml).

### Implementation and role skills

- **Platform explanation:** [docs/ace_role_revision.md](ace_role_revision.md).
- **Role strategies, queries, tools and policies:**
  [prove_ace_role_revision.py](../prove_ace_role_revision.py).
- **Reused evidence-reading and snippet-checking tools:**
  [prove_ace_roles.py](../prove_ace_roles.py), backed by the Rocq checker in
  [ace/rocq_snippets.py](../ace/rocq_snippets.py).
- **Typed products, edit validation, evidence reuse and atomic application:**
  [ace/role_revision.py](../ace/role_revision.py).
- **Role instructions:**
  [reflector.md](../prompts/ace/role_skills_v2/reflector.md),
  [curator.md](../prompts/ace/role_skills_v2/curator.md),
  [reducer.md](../prompts/ace/role_skills_v2/reducer.md).
- **Generator and bounded proof-state inspection:**
  [prove_grounded.py](../prove_grounded.py).
- **Reused generator tools and static skill registry:**
  [prove_agentic.py](../prove_agentic.py) and
  [runtime/skills.py](../runtime/skills.py). The seven reference files live
  in [the vendored Rocq references directory](../rocq_skills_data/plugins/rocq/skills/rocq/references/).
- **Durable checkpoints:**
  [runtime/ace_role_journal.py](../runtime/ace_role_journal.py).
- **Cooperative pause:**
  [runtime/campaign_pause.py](../runtime/campaign_pause.py).
- **Campaign data boundary:**
  [runtime/ace_revision_scope.py](../runtime/ace_revision_scope.py).
- **Reused budgeting, request recording and model configuration:**
  [runtime/campaign_budget.py](../runtime/campaign_budget.py),
  [runtime/replay_admission.py](../runtime/replay_admission.py),
  [runtime/model_registry.py](../runtime/model_registry.py).

### Tests and demonstrations

- **Role regression tests, including the cast repair:**
  [tests/test_ace_role_revision.py](../tests/test_ace_role_revision.py).
- **Complete campaign integration and comparison checks:**
  [tests/test_ace_revision_campaign.py](../tests/test_ace_revision_campaign.py).
- **Executable query demonstrations:**
  [demos/ace_role_revision.demo.yaml](../demos/ace_role_revision.demo.yaml).
- **Demonstration builder:**
  [tools/data/ace_role_revision_demos.py](../tools/data/ace_role_revision_demos.py).
- The historical demonstrations are sealed: inspect them and run the
  preserved tests without regenerating the fixtures in place.

### Experiment, results and inspectable evidence

- **Campaign runner and protocol:**
  [experiments/ace_revision_experiment.py](../experiments/ace_revision_experiment.py)
  and [campaign README](../experiments/campaigns/ace_revision_20260913/README.md).
- **Detailed findings:**
  [FINDINGS.md](../experiments/campaigns/ace_revision_20260913/FINDINGS.md).
- **Numerical summary and full paired statistics:**
  [RESULTS.md](../experiments/campaigns/ace_revision_20260913/RESULTS.md)
  and [reports/319.json](../experiments/campaigns/ace_revision_20260913/reports/319.json).
- **Learning yield and retained-edit interpretation:**
  [mechanism.json](../experiments/campaigns/ace_revision_20260913/mechanism.json)
  and [learning_review.json](../experiments/campaigns/ace_revision_20260913/learning_review.json).
- **Trigonometric review case:**
  [revisions/3.json](../experiments/campaigns/ace_revision_20260913/revisions/3.json).
- **Cast failure source; inspect event `e4`:**
  [sources/amc12a_2020_p13.json](../experiments/campaigns/ace_revision_20260913/sources/amc12a_2020_p13.json).
- **Rocq audit, exact replay and final consistency checks:**
  [audit.json](../experiments/campaigns/ace_revision_20260913/audit.json),
  [replays/319.json](../experiments/campaigns/ace_revision_20260913/replays/319.json),
  [final_verification.json](../experiments/campaigns/ace_revision_20260913/final_verification.json).
- **Per-cell results and charged-request records:**
  [cells.csv](../experiments/campaigns/ace_revision_20260913/cells.csv)
  and [receipts.csv](../experiments/campaigns/ace_revision_20260913/receipts.csv).
- **Report generator:**
  [tools/reports/ace_revision_results.py](../tools/reports/ace_revision_results.py).
- **Raw archive locations and replay requirements:**
  [ARTIFACTS.md](../experiments/campaigns/ace_revision_20260913/ARTIFACTS.md).
  The large original caches and transport records remain local; the lean
  export contains their hash inventory and the reviewable evidence.

### Equivalent non-ACE baseline and its evidence

- **Empty-book experiment configuration:**
  [experiments/ace/ace_attribution_experiment.py](../experiments/ace/ace_attribution_experiment.py);
  inspect `ProofConfig.instantiate` and the `luna-none` arm.
- **Matched settings and historical-control provenance:**
  [attribution README](../experiments/campaigns/ace_attribution_20260912/README.md)
  and [LINEAGE.md](../experiments/campaigns/ace_attribution_20260912/LINEAGE.md).
- **Non-ACE versus X3 metrics and paired statistics:**
  [luna_report.json](../experiments/campaigns/ace_attribution_20260912/luna_report.json).
- **Attribution findings, preparation cost and caching sensitivity:**
  [attribution RESULTS.md](../experiments/campaigns/ace_attribution_20260912/RESULTS.md).
- **Historical pre-ACE implementation snapshot:**
  [prove_agentic_preace.py.txt](../experiments/campaigns/ace_attribution_20260912/reference_source/prove_agentic_preace.py.txt).

### Suggested order for a presentation or code walkthrough

- Start with the roles, their tools and skills, and the fixes in sections 1–2.
- Use the playbook comparison and two retained changes to show the effect
  on the generated artifact.
- Show the cast rule and trigonometric review as concrete remaining issues.
- Show the equivalent non-ACE method and its historical results, then the
  fresh X3–v2 benchmark. Explain their different comparison limits and the
  decision to keep the flagship default.
- For a code walkthrough, open the role strategies, then edit validation,
  followed by the regression tests and the final book.
