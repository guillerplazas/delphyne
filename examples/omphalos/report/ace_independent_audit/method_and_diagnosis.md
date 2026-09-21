## What is being reproduced

The thesis target is **at least 10% lower total inference cost than the equivalent ordinary agentic pipeline**, allowing up to two fewer solved problems per forty on average. Cost includes unsuccessful attempts. Learning and preparation are reported separately for a frozen playbook, and included in operating cost for online learning. A coverage improvement is also valuable; there is no requirement that every replicate individually avoid losing a problem.

This is an adaptation of ACE to Rocq, rather than an exact reproduction of its original benchmark. The local reference is [ACE, version 3](../../papers/2510.04618v3.pdf), also available [from the authors on arXiv](https://arxiv.org/abs/2510.04618). Section 4.1 distinguishes two experiments:

- Offline: learn the context on training problems, freeze it, and evaluate on other problems.
- Online: solve the current problem with the current context, record its score, then learn from that problem before proceeding. All compared methods see the same order.

Therefore **benchmarking trainX is appropriate**. A frozen book tested on its training problems measures familiar-workload reuse. An empty-start online curriculum measures performance before learning from the current sample. These are different claims and are reported separately. ValidationX measures development transfer; its repeated historical use means it is not an untouched confirmation set. No closed evaluation partition, protected challenge problem, or mixed results artifact was opened for this investigation.

The paper's main experiments use the same DeepSeek-V3.1 model for Generator, Reflector, and Curator, with maximum five epochs and five reflection rounds (§4.2). Its fine-grained cost study uses one epoch and one reflection round (Appendix A.3). Its stronger-Reflector ablation varies only that role: FiNER accuracy is 70.7 for the base model, 76.6 with GPT-OSS reflection, 78.3 with DeepSeek reflection, and 78.5 with GPT-5.1 reflection (Table 16). Our scaling experiment keeps **Luna as the solver** and varies the models used for reflection, curation, and terminal auditing together. It tests the authorized stronger-author recipe, not the paper's isolated Reflector ablation.

The paper does not establish a universal 10% serving-cost reduction against ordinary ReAct. Table 14 reports 27,460,411 input tokens, 289,802 output tokens, and 2,430 rollouts for Base ReAct, versus 58,623,267, 270,652, and 2,354 for ACE over 160 evaluation queries. Its printed percentage comparisons are against GEPA. The prominent adaptation savings in Table 4 are also against GEPA or Dynamic Cheatsheet. The 82.6% figure in §4.7 is **input-billing savings from caching relative to charging raw input tokens**, not total-cost savings against the ordinary agent. These distinctions determine the right denominator; they do not invalidate the thesis objective.

## Experimental contracts

All new benchmark solving uses Luna, medium reasoning, the Responses API, a 32-request allowance, a $0.10 stopping budget, and a 32,768 output-token limit. The two tools are `ReadSkill` and `SearchRocq`. The current problem's informal proof sketch and definitions are available, and the original two fixed tool-use demonstrations are retained. The baseline is therefore not theorem-only prompting. Empty ACE context renders exactly the ordinary agentic system and instance prompts; an offline contract test verifies this equality.

| Arm | Solver/checker | Playbook preparation |
|---|---|---|
| A0 | Original assisted verifier | No playbook |
| A1 | Same as A0 | Historical X5, rendering version 2 |
| A2 | Same as A0 | Forty fixed assisted trajectories; Sol authors; five terminal audit batches |
| S1 | Same as A0 | Same trajectories/order/procedure as A2; Luna authors |
| P1 | Same as A0 | The actual eleven-bullet Sol book selected by the eight-source author pilot |
| B0 | Plain verifier | No playbook |
| B1 | Same as B0 | Forty fixed plain trajectories; Sol authors; five terminal audit batches |
| B2 | Same as B0 | Same plain trajectories, augmented with training-only automatic completion evidence |
| R1 | Same as A0 | A2 with three manually audited tactic claims repaired; trainX diagnostic only |
| O1 | Same as A0 | Final book from the first adaptive online curriculum, frozen after forty updates |

The assisted verifier can supply closing tactics. The plain verifier checks the submitted proof and supplies no completion. B2's extra completion work happens **after collecting a training trajectory** and never improves a benchmark score directly. The A and B comparisons each have their own matching non-ACE control. The comparison A0 versus B0 studies the effect of assistance itself.

The initial frozen matrix contains eight arms × forty problems × two replicates × two partitions: 1,280 attempts. Three additional online ACE arms each run forty problems in two independently shuffled trainX orders: 240 attempts. Their no-ACE controls are the same 160 trainX A0/B0 attempts already included in the frozen matrix. That study contains **1,520 attempts**, with no duplicate controls. The original core is 1,200; S1 and P1 are separately registered 160-attempt follow-ups. Two subsequent diagnostics add eighty R1 trainX cells and 160 O1 trainX/validationX cells, reusing the same controls. Source collection adds eighty cells and the author pilot adds 204, for **2,044 registered solver cells overall**. Deterministic cache replays and synthetic tactic probes are separate checks, not extra independent benchmark samples.

The `seed0` and `seed1` names identify independent paid replicates and online orders; they are not a promise of deterministic provider seeding. Pairing matches theorem and replicate. Confidence intervals resample forty theorem clusters, retaining both replicates together; a second analysis uses broader proof-method families. The latter are deliberately conservative groups, not claims that all their members are duplicate statements. None of the eighty allowed statements was an exact duplicate under the inspected numeral/single-letter normalization.

The practical target is evaluated separately from statistical support. A 90% interval and a two-sided sign-flip result describe uncertainty; neither is a veto on an exploratory follow-up. Selection among several candidate books makes the author pilot exploratory, even when its unadjusted interval is favorable. The reports show both the complete cost/coverage trade-off and individual problem contributions.

### Important differences from the paper

The full offline preparation uses fixed source trajectories to isolate author and teacher changes. Its Generator does not solve each subsequent training problem with the evolving book. The online track separately tests that interaction. Consequently, helpful/harmful tags in fixed-source preparation are retrospective judgments about compatibility with a trace, not direct observations that the Generator used an evolving bullet.

The implementation uses deterministic incremental ADD merges with lexical deduplication and source-linked terminal revisions. It does not reproduce the paper's embedding-based deduplication or Generator-side bullet attribution. The nominal book cap is a 6,000-token **character-based estimate**, not an exact tokenizer limit. No full-training ADD reached that cap, and lexical deduplication merged zero bullets in each of the four full recipes. Terminal auditors receive checks, returned scripts, reflections, and deltas grouped into five batches of eight sources. Reflectors and curators receive the fuller version-2 evidence, including the informal sketch and visible tool conversation. These input contracts must not be described as identical.

P1 versus A0 changes only learned context at inference. P1 versus A2 compares complete preparation recipes: source count, curriculum order, and terminal refinement all differ. A favorable P1 result alone is not a causal estimate of shortening a forty-source book.

O1 addresses the distinction between fixed-source learning and adaptive training directly. It takes the final assisted book from online order zero, selected before either curriculum finished, and evaluates it as a frozen artifact. This is a one-epoch adaptive Generator/Reflector/Curator preparation recipe. Its comparisons with A2 or P1 include differences in source trajectories, order, and terminal auditing; they do not isolate only Generator adaptation. R1 is a manual rule-quality intervention, not an autonomous learning recipe. S1, P1, R1, and O1 reuse earlier compatible controls and were dispatched in later blocks, so their comparisons also retain temporal and provider-cache limitations. Raw-token repricing is reported as a sensitivity analysis, not as a simulated uncached deployment.

## What the historical evidence actually shows

The census was reconstructed from **10,110 permitted raw result cells across 81 archives**, plus 153 exception-only cells. It did not use old verdicts or handoff conclusions. The 848 descriptive solver labels include small pilots and evolving books; they are not 848 complete independent benchmarks. The full census, executable contracts, missing cells, learning-role groups, and matched comparisons are linked in the artifact index.

Seventy-three interrupted cells had explicit continuation policies whose final caches contained every saved prefix entry exactly. Those prefixes were replayed, not purchased twice. Naively summing both archives adds $0.64806857 of duplicate recorded calls. The reconciled analysis removes that duplication while preserving the interrupted files. It makes no zero-bill assumption about missing transport metadata.

Historical dollar figures are recomputed at the common September 19 tariff, including cache writes, rather than copied from archived `price` columns. They are normalized comparison costs, not reconstructed historical invoices. Fresh experiment figures are checked against raw provider responses and the new ledger. Failed calls and failed problems remain in the relevant accounting and denominators.

### Several different baselines had become mixed together

The original experiments used `prove_theorem_agentic`/`prove_theorem_ace`, two core tools, and 32 requests. Later experiments used `prove_theorem_grounded`, 64 requests, `InspectProofState`, focused decision prompts, bounded goal views, and 300 seconds of verifier work. Those later ACE/non-ACE pairs can be valid within their own contract, but they do not reproduce the original agentic experiment simply because a campaign name contains “X3 reproduction.”

This distinction changes the interpretation of apparently promising numbers. The historical session-matched comparison has 50/80 solves on each side and 11.19% lower ACE inference cost; its theorem-cluster 90% interval is −0.32% to 21.44%. Against that campaign's ordinary non-reset baseline, the same ACE-session configuration saves only 1.05%, while improving 47 to 50 solves. Both results matter. Selecting the more expensive reset control as the sole headline comparator would answer a different question.

After exact-prefix reconciliation, the September 18 thesis-selected book has 51/80 solves at $2.25622. Its output-cap-matched non-ACE control has 49/80 at $2.41161: 6.44% savings. The ordinary 32,768-output-token control has 51/80 at $1.71575, making that ACE recipe 31.50% more expensive. Thus the apparently small output cap did not make this solver cheaper. In the later X3 reproduction, the matched 32,768-cap comparison is 46 to 50 solves and 4.78% savings; the 8,192-cap comparison is 51 to 45 solves and 0.94% higher cost.

Earlier code also imposed zero loss in each replicate in some economy gates. That requirement is visible in the experiment source and is stricter than the user's objective. This investigation preserves those original protocols as history, but evaluates the requested average trade-off. Removing a mistaken gate does not turn a measured 1–6% saving into 10%; it does prevent discarding useful candidates merely because one replicate loses a proof.

### The cost problem is dominated by unsuccessful trajectories

For the original validation baseline, 26 failed attempts cost $1.24767213 of $1.77504503 total: **70.3% of all inference spending**. X3 rendering version 2 solves two more attempts, but its 24 failures cost $1.75294794 and its total rises to $2.32188362.

Two X3 failures alone cost about $0.6946. The `amc12a_2019_p21` replicate reaches 778,447 input tokens in one request and emits roughly 1.04 million characters of verifier feedback; the `mathd_numbertheory_37` replicate reaches 522,325 input tokens and roughly 1.68 million feedback characters. The ordinary baseline also has an expensive `amc12a_2020_p21` trajectory, costing $0.20795 and reaching 451,768 input tokens. Repeated expanded proof states accumulate in the conversation and can cross the long-context tariff boundary. This is a trajectory-control problem as well as a playbook-size problem.

Prompt caching is already effective. The original baseline serves 90.28% of input tokens from cache, X3 rv2 89.25%, and X5 rv2 93.28%. Their input bills are $1.01021, $1.52152, and $0.95146 respectively. X5 reads about 20% more raw input than the baseline but pays less for input. Conversely, the successful Sol pilot has a slightly lower cache fraction than its control, 90.97% versus 92.45%, while reducing cumulative input from 4.093 million to 1.255 million tokens and output from 95,510 to 52,328 tokens. The measured pilot gain accompanies shorter trajectories, not improved cache hit rate.

The $0.10 allowance is a stopping threshold checked between requests, not a hard bill ceiling. A single crossing request can overshoot it. Costs are not clipped at ten cents in these results.

## Implementation defects and controlled diagnostics

### Serialization failures were being mistaken for learning behavior

The two monolithic historical adaptations contain eighty rewrite steps and 196 model replies. Only 35 steps produced a usable result. All 161 invalid replies encountered the same YAML error class: unquoted scalar text containing a colon in Rocq syntax, such as an assertion type annotation. An offline transformation that quotes only unquoted single-line `content` scalars makes all 196 saved replies parse and all eighty steps usable. The 35 originally valid parsed values remain identical.

This experiment uses no new model calls and does not change any archived score. It establishes that these ablations cannot cleanly attribute their outcome to conceptual “context collapse”: much of their learning pipeline never accepted the returned text. It does not establish the coverage an adaptively rerun monolithic learner would have obtained.

The new author ladder exposed a second parser problem: the old last-code-block extraction sometimes selected an indented Rocq fence inside a YAML block scalar. The version-3 parser recognizes the outer column-zero serialization fence. On all 266 saved author replies it recovers 266 valid outputs versus 254 for the old parser, preserving all 254 common valid values. The failed extractions caused ten extra requests and two wholly lost role outputs. The full preparation and online study use the repaired parser; the earlier pilot books remain the artifacts actually produced, so their parser failures remain a limitation when comparing author capability.

The census also finds 54 historical curator exceptions caused by a template expecting a missing `theorem` field. They are concentrated in the early offline-three-epoch and warm-online adaptations. They are preparation failures, not evidence that a correctly executed ACE update was ineffective. The current versioned role queries and templates have explicit input contracts; sealed historical strategies and caches are preserved.

### Stronger authors help with some errors, but still need verification

All four full preparations completed eighty reflection/curation outputs plus five terminal audits. Sol's A2, B1, and B2 growth phases produced no unknown-ID merge warnings. Luna's S1 emitted seventy bullet tags, of which 42 referenced nonexistent IDs and were ignored by the deterministic merge. This measures structured-reference reliability under the shared prompt contract, not general model capability. The prompt requests bullet IDs but could state the restriction to existing IDs more explicitly. The matched S1/A2 benchmark measures the resulting books' practical value.

Ten synthetic Rocq probes independently check specific learned claims:

- `nra` proves a simple variable square nonnegative, but fails on the tested affine and product-square expressions. Explicit `Rle_0_sqr` proofs close both compound cases. The old square advice is too general as phrased, while its fallback is useful.
- In the same Rocq file, `About vm_compute` reports no defined object and `vm_compute; reflexivity` successfully proves a closed equality. Object introspection does not test whether a built-in tactic is available. A new Sol reflection and terminal rationale made precisely this mistaken inference.
- The rejected unparenthesized `set x := ...` form has a working parenthesized `set (x := ...)` counterpart. The historical named-`pose` workaround is valid too; it must not be called false merely because another repair exists.
- `field` alone does not prove the tested logarithmic denominator identity. Rewriting the power logarithm and then using `ring` does. Here the learned algebraic repair is substantively wrong for the stated transcendental relation.

These checks distinguish safe but overly broad guidance, incorrect causal explanations, and actually failing repair advice. They also show why a larger author model alone does not certify a rule's correctness. The report does not infer bullet-level causal effects from a solver merely producing a proof consistent with the book.

Six additional synthetic checks expose a more direct failure in the new long book. A2 bullet 58 prescribes `unfold Same_set; intro x; split`. In this library, `Same_set` unfolds to a conjunction of two inclusions. The prescribed sequence fails with “No product even after head-reduction”; splitting before introducing the element compiles. A2 bullet 24 prescribes an untargeted `Rabs_right` rewrite. Under precisely its advertised assumptions, that rewrite fails because it first tries to establish the unknown sign of the left-hand variable. Targeting the right-hand expression with `rewrite (Rabs_right c) by lra` works. A quantified positive-multiplication example also shows that bullet 9's blanket warning against `nra` is too broad, while its explicit monotonicity lemma remains a useful fallback. The sixth check confirms the short P1 book's product-form square assertion.

The provenance of the set-equality error is particularly informative. The assisted `mathd_algebra_224` source run failed after 32 requests. Its reflector offered an unverified repair, the curator described it as directly established by verifier evidence, and the terminal auditor retained it with an incorrect causal explanation. Luna's S1 book contains the same tactic-order error. B1 and B2 instead prescribe the correct split-first sequence: their shared plain source also failed overall, but it had successfully passed this intermediate repair. Thus an unsuccessful trajectory can contain useful verified progress, while an author's explanation of a failed step can still be false. Correctly checking the final proof does not automatically validate the lesson extracted from it.

R1 freezes those three A2 repairs and measures their joint effect on all forty trainX problems with two replicates. Its 80-cell diagnostic separates the claim “these recipes are corrected” from the separate empirical claim “the corrections make this solver cheaper or more successful.” The original paid books and outcomes remain intact. Early drafts of these six probes omitted the domain imports; those missing-symbol failures are preserved and explicitly excluded. The sixteen reported probes use the appropriate imports.

### Completion and accounting must be explicit

During this investigation, a preliminary author assessment was made too early because Delphyne periodically writes intermediate `result.yaml` files. The provisional conclusion favored Luna; the completed pilot favors Sol. The premature artifacts are preserved in an incident directory. The prematurely queued online launches made zero API calls and consumed no benchmark attempts.

The correction is implemented in a campaign-local launcher adapter: a completion receipt is written only after the worker returns, and it hashes both result and cache. Analysis also requires the launch lock to be released and final experiment state to be complete. Source and pilot results have exact HTTP-disabled replay certificates and independent Rocq compilation certificates; the same certification is applied to the final study. Existing shared and sealed launchers were not silently rewritten. A general completion-receipt interface is an out-of-scope suggestion for Delphyne itself.

## What the author and teacher pilots establish

The author study holds eight trainX source trajectories fixed and compares Luna, Terra, Sol, and Astra at medium and high reasoning. The first evidence encoding omitted the informal sketch and tool replies. A second encoding restores the solver's visible inputs and conversation. Both sets of books and their matched twelve-problem pilot evaluations are retained: seventeen arms including the no-book control, 204 attempts total.

With full-input evidence, Sol-medium solves 11/12 at $0.11395045, versus the ordinary control's 9/12 at $0.26757794: **57.41% lower inference cost**. Luna-medium solves 10/12 at $0.15631995. Sol-high is worse than Sol-medium in this pilot, and Astra-high costs more while matching Sol-medium's eleven solves. More model capacity or more reasoning is not monotonically better.

Three pilot problems overlap the eight source trajectories. On the remaining nine, the control solves six at $0.24992996 and the Sol book solves eight at $0.10605873, a 57.56% saving. This reduces the concern that the pilot result is entirely familiar-problem recall, but the pilot remains selected, small, and exploratory. P1 freezes that actual 3,986-character, eleven-bullet book before its full trainX/validationX follow-up.

The per-problem traces explain the pilot difference. On `amc12a_2002_p13`, the control exhausts 32 requests and 23 checks without a proof; Sol's book leads to a checked product-zero factorization in fourteen requests and seven checks. On `mathd_numbertheory_629`, the control fails after 32 requests, while the Sol-book trajectory solves in eighteen using explicit closed LCM replacements after still encountering stack overflows. On `amc12b_2004_p3`, both paths bound exponents and split cases, but Sol's book uses eight requests versus thirteen. Its accepted script contains seventy verifier-supplied `easy` closures: these are genuine checked assistance, not seventy subgoals independently solved by Luna. Easy one-request problems can instead pay extra prompt cost. Here and in the trace tables, “checks” counts distinct cached compute records; cache reuse means this is not necessarily every invocation or every low-level Rocq request.

The training-only completion teacher performs 339 checks on the forty fixed plain trajectories, finds eleven independently rechecked and kernel-compiled scripts on nine theorems, and encounters six work-limited checks. **None of its successful completions comes from a source theorem the plain solver ultimately failed.** It can expose shorter completions and useful intermediate repairs, but this measured teacher did not supply new solved examples for the hardest failures. B1/B2 therefore tests a specific limited source of supervision, not an unlimited oracle.

The retained-rule provenance also identifies a mismatch between training effort and the economic objective. A2's seven failed source problems consume $0.39363 of $0.75239 source spending (52.3%), but introduce twelve of its 57 retained rules and only 19.2% of their content characters. Five one-request successes consume $0.00231 and introduce five rules. B1's nine failures account for 59.9% of source cost and fourteen of 53 retained rules. The short P1 book's eleven rules all originate in seven multi-request successes; its eighth, one-request source contributes no rule. These are source-allocation measurements, not estimates of rule usefulness. They support testing a learning objective that explicitly targets expensive recoverable trajectories, while the compiled set-equality example shows why failed-source lessons still need executable evidence.

## Preparation economics

| Recipe | Source collection | Author and audit calls | Total preparation | Frozen bullets / characters |
|---|---:|---:|---:|---:|
| A2: full Sol, assisted | $0.75239 | $20.40788 | $21.16027 | 57 / 21,079 |
| S1: full Luna, assisted | $0.75239 | $1.00297 | $1.75536 | 57 / 18,938 |
| B1: full Sol, plain | $0.99151 | $26.58647 | $27.57798 | 53 / 18,669 |
| B2: full Sol, teacher evidence | $0.99151 | $43.72839 | $44.71990 | 61 / 21,174 |
| P1: short Sol pilot book | $0.07698 | $2.02092 | $2.09790 | 11 / 3,986 |

These are deployment-recipe costs: each includes the sources it needs. The investigation reuses source trajectories, so adding all table rows would double-count the study bill. If suitable source trajectories already exist, the incremental preparation charge is the author/audit column. The teacher has zero additional LLM API cost for its deterministic proof work, but its longer evidence increases author input cost; measured completion/check/compilation time is reported separately without inventing a machine-dollar tariff.

B2's larger fee has a measurable mechanism. Its authors read 7,511,433 input tokens versus B1's 4,961,585, and two B2 requests cross the 272,000-token tariff boundary, with a maximum of 466,925 tokens. Their output counts are almost unchanged: 88,614 versus 88,940. B2's billed input rises from B1's $24.80767 to $41.91091. The extra teacher evidence therefore increases both volume and, for two requests, the per-token tariff; it is not primarily extra author output reasoning.

### A completed preparation-cost repair

Every full preparation and the selected short-book recipe records **zero cache-read tokens**. Almost all author input instead incurs the cache-write rate. A2 pays $3.72109 in unused write premium, B1 $4.96133, and B2 $8.38197. These are 18.2%, 18.7%, and 19.2% of their respective author bills. Their single-message learning inputs change between calls, and there is no reusable explicit breakpoint inside those messages. Current caching operates at eligible boundaries; explicit mode with no breakpoints avoids writing such one-shot inputs. See the [provider's cache-boundary and explicit-mode specification](https://developers.openai.com/api/docs/guides/prompt-caching#how-caching-works).

A separately registered six-call experiment reuses A2's exact reflection/curation inputs at training steps ten and thirty, plus terminal auditors zero and four. Only the cache mode changes. All six input-token counts remain identical, all six outputs parse under their original role schema, and all six have zero cache reads and writes. Input fees fall from $2.463747 to $1.971012: **20.0% lower**. Total fees fall from $2.674107 to $2.171732, or **18.8% lower**; output-token variation is reported separately. This is an actual paid experiment, not hypothetical repricing. Its generated lessons are diagnostic outputs and do not replace the frozen study books.

The opt-in `learning_cache.one_shot_payload` helper implements this change. It is appropriate for these one-call author requests, whose full preparations needed no parsing retries. It is not applied to the multi-turn solver, which benefits substantially from cached conversation history, or presented as a solver-cost victory. A future author recipe that regularly retries or reuses the same context must account for that reuse before choosing this policy. The original measured preparation fees above remain the actual fees paid; they are not retroactively discounted.

The final economics table uses observed inference savings per problem to calculate both ordinary payback and the workload size needed for 10% savings **including preparation**. Those projections assume the measured workload distribution recurs with the same frozen book. They are not guarantees of savings on arbitrary new theorems. Online reporting includes every learning update, including the last one, rather than presenting solver-only savings as the whole operating bill.
