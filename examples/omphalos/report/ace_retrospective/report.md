---
title: "ACE in Omphalos"
subtitle: "Implementation, experiments, costs, and lessons"
date: "12 September 2026"
lang: en
header-includes:
  - |
    \makeatletter
    \renewcommand*{\l@subsection}{\@dottedtocline{2}{1.5em}{3.2em}}
    \makeatother
---

# Reading guide and principal findings

ACE (**Agentic Context Engineering**) is a way of making an LLM application learn from experience **by changing the context it reads**, rather than retraining its weights. In Omphalos, that context is a small, persistent book of proof-engineering advice. A prover attempts a Rocq theorem; a reflector explains the attempt; a curator proposes reusable advice; ordinary Python code merges that advice into the book. Later proof attempts receive the accumulated book. This is a substantial implemented system, with several generations of evaluation and increasingly careful controls. It is not merely an idea in the backlog.[^ace], [^implementation]

The most useful conclusion is that Omphalos has made clearer progress on **controlling the cost of proof search** than on establishing a large, general ACE improvement in proof coverage. The distinction matters for this thesis: control and budgeting are part of the research contribution, rather than incidental infrastructure. There are encouraging ACE comparisons, including a recent matched program ablation in which Luna with its own book solved 27/40 validation problems against 24/40 without the book, at lower recorded cost. That coverage difference remains statistically inconclusive, and its cost interpretation depends strongly on cached-input billing.[^attribution]

The report covers the accessible development history through the September 12, 2026 snapshot. It includes the early ACE replication, the sequence of playbook variants, budgeting and repair experiments, model and effort studies, coverage treatments, and the recent attribution and capacity investigations. The last advisor-meeting date is unspecified, so the chronology starts before ACE and does not invent a “since our last meeting” boundary. The original thesis proposal supplies motivation, but current experiment records determine what was actually implemented and measured.[^proposal]

Two reading routes are useful. For an advisor discussion, start with this section, the baseline lineage, the cost figures, the mistakes chapter, and the closing research assessment. For rebuilding your own understanding, read the foundations and implementation chapters first; the experiment history will then be much easier to interpret. Detailed numerical tables and an inventory of the source records accompany the report. The spreadsheet contains the plotted data, including unsuccessful cells.

## Six conclusions to take into the meeting

1. **The implementation is real and extensive.** It includes generation, reflection, curation, deterministic storage and refinement, offline and online adaptation, ablations, provenance, grounding, and later bounded control mechanisms. The main implementation differences from the paper are identifiable and versioned.
2. **A budget reference was achieved.** The first bounded campaign obtained 25/40 qualified validation solves for $0.6780 against the older X3 comparator's 28/40 for $1.5238. That is 55.5% lower total cost with three fewer solves. Guille explicitly accepted this trade-off; the original no-coverage-loss gate remains failed.[^bounded]
3. **ACE effects depend on the comparator.** Earlier non-ACE, newer non-ACE, and the current flagship are different programs. Comparing them across time is useful history, but it does not isolate the effect of the book. The latest matched within-program ablation is the clearest available ACE comparison.[^lineage]
4. **Stronger models help some proofs but do not automatically make better ACE.** On the full validation crossover, the same Luna book changes Luna's count from 24 to 27 and Terra's from 29 to 29. Terra's own book reaches 30. There is no supported general conclusion that stronger writers or solvers unlock a larger marginal ACE effect.[^capacity]
5. **Several negative experiments tested flawed or ineffective delivery.** Structured-output parsing confounded three mechanism arms. New examples and feedback sometimes never reached the requests that produced the observed gains or losses. A correct local rewrite can also leave the mathematical proof unfinished.[^mechanisms], [^coveragecycle]
6. **An intrinsic model ceiling has not been established.** Exact continuation recovered additional Terra proofs, while the remaining ordinary failures still stopped at monetary admission boundaries. Repetition and incomplete arguments reveal concrete weaknesses of the sampled search paths, but those paths were not allowed unlimited computation.[^capacity]

## A necessary boundary on exhaustiveness

testX remains closed. Its partition, individual outcomes, prompts, traces, reports, and mixed aggregate artifacts have not been used as inputs to this retrospective. Protected challenge evidence is also excluded. Consequently this report does not restate protected confirmation results, reconstruct testX charts, or use restricted failures to formulate new examples. Some older project-wide narratives and HTML reports are excluded because they mix permitted and closed outcomes. The source inventory records these exclusions rather than pretending that every repository document could be read.[^governance]

This boundary leaves substantial evidence: the numerical reconstruction includes 2,400 registered historical development cells, the recent complete model/book crossover, the attribution panels, and the selected continuation study. “Registered cells” is a count of archive entries, including incomplete or superseded records; it is **not** a count of independent theorems, new API calls, or usable experimental observations. Individual chapters explain which records support a comparison.

# Foundations: what the system is trying to learn

## The proof problem

A theorem prover needs to produce an artifact that the proof assistant accepts. Knowing that a mathematical statement is true, or even knowing a good informal proof, is insufficient: the system must express the argument in the available formal language, use the right definitions and library objects, discharge side conditions, and finish all proof obligations. A proof that is almost complete still does not count as a solved theorem.

Rocq provides the formal checking environment. Omphalos proposes tactic scripts, runs them against a theorem, and receives acceptance, error messages, and information about remaining goals. A goal is a statement still to be proved under a local context of hypotheses. A tactic transforms that state. `lia`, for example, addresses a particular arithmetic fragment; it cannot supply an arbitrary missing mathematical invariant. A library lemma can be perfectly valid yet unavailable under the current imports or inapplicable to the exact expression in the goal.[^bridge]

The benchmark is a Rocq translation of miniF2F. Its mathematical questions include competition problems and more routine arithmetic or algebraic tasks. Translation into Rocq changes the formal environment and proof-engineering demands. It does not make published Lean performance a directly comparable score. The benchmark paper is the relevant source for the translation and its limitations; the pinned local files determine the actual tasks used here.[^minif2f]

The original proposal is motivated by Hilbert. The identifiable reference is **Varambally et al., “Hilbert: Recursively Building Formal Proofs with Informal Reasoning,”** whose v2 paper reports 99.2% on miniF2F. The proposal's shorthand “Chen et al.” should be corrected when preparing the thesis bibliography. Hilbert combines informal reasoning, a specialized formal prover, verification, retrieval, and recursive decomposition. The current Omphalos agentic/ACE work is not a demonstrated reproduction of that entire architecture or its benchmark result.[^hilbert], [^proposal]

## Why Delphyne is relevant

Delphyne separates a **strategy**, which says what kinds of steps an application can take, from a **policy**, which decides how to explore those choices and spend resources. Demonstrations provide grounded examples of decisions. The separation allows an experiment to change prompting, search, or a budget without rewriting the meaning of a valid proof. That is the architectural idea behind the thesis's interest in localized control changes.[^delphyne]

In the implementation, `@strategy` and generator-based effect handling express unresolved choices. Query classes describe requests to the model. `Compute` operations execute ordinary computations such as verifier calls. Policies provide LLM sampling, traversal, and budget behavior. An ACE book changes the context of a query; a bounded verifier operation changes an explicit computation; an admission rule changes whether another resource-consuming step is allowed. These are different intervention points, even when they appear together in a single candidate configuration.[^implementation], [^grounded]

This distinction prevents a common attribution error. If a new candidate adds ACE advice, bounded goal views, different request admission, and focused queries, a lower bill is a result of the **whole candidate**. It is not automatically evidence that learned advice caused the improvement. Isolating ACE requires a comparison that holds the rest of the program fixed.

## ACE's central idea

An ordinary prompt is fixed before an experiment. ACE treats part of the prompt as an evolving memory. The memory is structured into individually addressable bullets rather than rewritten as one undifferentiated essay. A bullet might say which lemma handles a specific square representation, warn that a tactic name is absent, or explain a useful order of normalization and arithmetic reasoning. The ambition is to avoid rediscovering the same proof-engineering fact across many tasks.[^ace]

Three roles divide the work. The **Generator** attempts the task using the current book. The **Reflector** reads an account of the attempt and derives lessons from its successes and failures. The **Curator** decides which lessons deserve persistent entries. In the batched Omphalos implementation, a **Reducer** also selects a small number of additions from several curator proposals. These are roles in the application, not necessarily different foundation models.[^ace], [^adaptation]

The book is then updated by deterministic code. An LLM proposes additions; Python assigns identifiers, maintains the structured representation, applies versioned deduplication/refinement rules, and serializes the resulting state. The paper motivates this division partly through *context collapse*: repeatedly asking a model to rewrite an entire accumulated memory can suddenly discard detailed knowledge. A deterministic append-and-refine representation makes preservation more explicit. It does not, by itself, certify that the preserved knowledge is correct.[^ace], [^playbook]

ACE is therefore context learning, not model-weight training. A model can appear better informed on a later task because the application gives it useful text. If the book is removed, the foundation model has not permanently acquired those facts through this procedure. Likewise, content-addressed caching preserves reproducibility; it does not constitute learning by the model.

## Offline, online, warm, and multi-epoch learning

**Offline adaptation** learns from a training pool, freezes the resulting book, and evaluates that fixed artifact elsewhere. The object being evaluated is a particular book hash plus a particular solver configuration. This is the cleanest way to ask whether accumulated experience transfers to another panel.

**Online adaptation** processes an evaluation sequence in order, using each attempt to update the book before the next task. The evolving book is part of the treatment; later tasks have access to more experience. Order matters. One cannot reshuffle the outcomes afterward and treat that as the performance of the same online learner. Online adaptation on a development sequence is useful evidence about that sequence, not a frozen-book holdout experiment.[^adaptation]

A **cold** online run starts with an empty book. A **warm** run starts with a previously learned book. More initial knowledge need not help: it may be poorly matched to the new sequence, increase repeated context cost, or consume the capacity available for useful additions. A **multi-epoch** offline run revisits the same training tasks. More epochs create additional opportunities to learn, but also repeat exposure to the same evidence and do not create new independent evaluation problems.

## What would count as success

There are several distinct success criteria. A book can reduce recurring syntax errors, cut the number of requests, lower the bill, or increase the number of solved theorems. These changes need not occur together. Preventing an early wrong lemma call may simply leave more budget for a later difficult subproblem that still fails.

For this project, the main outcome should be read as a triple: **coverage, total cost, and cost per qualified solve**. Coverage is how many expected tasks were completed under the stated qualification rule. Total cost includes unsuccessful tasks. Cost per solve divides that whole cost by the number of qualified successes. None of these is interchangeable with tokens per successful answer or cost per correct local applicability decision.[^measurement]

# Implementation: from experience to the next proof attempt

![ACE's data flow in Omphalos. The verifier supplies evidence; the language-model roles propose interpretations and additions; deterministic code maintains the persistent book.](figures/pipeline.pdf){width=100%}

## Generator and prompt integration

`ProposeProofScriptACE` extends the agentic proposal query with a rendered playbook and a rendering-version field. The rendered text is carried inside the query, rather than read indirectly from an external book at request time. This makes the query self-contained for caching. The ACE prompt includes the agentic machinery and appends the book section.[^implementation]

The example selector redirects ACE queries to the existing agentic demonstration bucket. Each selected example renders through its own query templates. This design aims to preserve the baseline few-shot messages, making the added book the intended prompt difference in the early comparison. The new query class also gives ACE separate template names and cache identities, protecting the frozen agentic configuration.

The Generator can use the existing library-search and state-inspection tools, along with automation tools permitted by the selected toolset. Proof proposals go through assisted Rocq checking. The returned verified script may include automation that completed a prefix; this detail becomes important when constructing the Reflector's evidence. The model's last proposed text is not always the exact text that the checker ultimately accepted.[^bridge], [^terminal]

An empty book has version-specific behavior. The newer empty rendering emits no book section, supporting a comparison with the unaugmented prompt. The legacy rendering used a placeholder. Therefore “empty book” is not sufficient evidence of identical prompts across every historical version. Rendering version, query class, demonstrations, and conditional instructions also matter.[^playbook]

## Reflector: diagnosis and attribution

The Reflector receives a trajectory and verifier outcome. Its schema separates the error, its proposed root cause, a correct approach, and a key insight. It can label existing bullets helpful, harmful, or neutral. This creates structured evidence for later curation and pruning, but those labels remain model judgments.[^implementation]

The initial implementation inferred bullet attribution from the trajectory rather than changing the prover's output contract to require the paper's generator-side tagging. Later citation-oriented rendering asks the Generator to name relevant bullet identifiers. The v4 treatment restricts Reflector visibility and counter updates to cited bullets. If nothing is cited, those counters do not move. This is more disciplined bookkeeping, but a citation at the start of a response can still describe an intention rather than a tactic actually executed.[^adaptation], [^cycles]

The strongest distinction is between **mention**, **exposure**, **execution**, and **effect**. A bullet may be mentioned without being supplied to a relevant request; it may be supplied but ignored; an associated tactic may execute without causing the eventual solve; and the same theorem may solve without the intervention. The later exposure audits repeatedly demonstrate why these stages must be separated.

## Curator, reducer, and deterministic merge

The Curator proposes ADD operations. Each operation supplies a section and content, and newer contracts add referenced Rocq objects. The main section vocabulary is tactics, lemmas, pitfalls, and strategy. IDs are assigned by the deterministic store. Newer prompts explicitly request YAML block scalars because snippets containing an unquoted colon followed by a space can otherwise break YAML parsing.[^curator], [^playbook]

In the X3 configuration, four training problems share a batch-start book. Their proposed updates are reduced to a small number of additions before merging. The four generators do not each see updates from preceding problems within that batch. The reducer is a consequential learning bottleneck: choosing three additions can discard lessons even when the overall book remains below its token limit. An underfilled book does not imply that no information was lost.[^adaptation], [^attribution]

The deterministic merge normalizes sections, handles duplicates using the selected deduper, assigns stable IDs, and maintains counters. The original lexical similarity rule at 0.90 fired zero times in forty recorded adaptation steps. Later variants add embedding-based similarity, periodic refinement, and harmful-bullet pruning. Whether a mechanism exists in code and whether it fired in an experiment must be reported separately.[^playbook], [^replication]

The current data model also supports a terminal audit that keeps, drops, or rewrites selected entries. This is a distinct operation from the original ADD-only curator contract. The monolithic ablation deliberately replaces the whole book, allowing the context-collapse hypothesis to be tested. These paths coexist to preserve historical identities rather than silently upgrading frozen runs.

## Content-addressed storage and experiment identity

The book store saves canonical YAML under its SHA-256 hash. A config records the exact book and upstream evidence it consumed. Step indices point to those objects; they are not the identity of the content itself. This resolved a concrete batching problem: step-indexed files for later positions in a batch might not yet exist, or might later refer to a different upstream book.[^store]

Canonical serialization and explicit upstream hashes support replay, but do not eliminate all historical hazards. Live template changes can alter future prompts within an already-running experiment. A trailing newline can invalidate old cache keys. Reusing a directory with the same name can retain stale upstream state. The v5 work documents these incidents, including stronger-writer steps that inadvertently used an empty book. A fair retrospective preserves these deviations instead of describing every run as an immaculate controlled experiment.[^v5]

The current implementation contains numerous opt-in controls. Function defaults are not necessarily the flagship settings: an experiment config can explicitly disable features that a strategy's constructor enables by default. The retained bounded reference uses money and focused behavior, while optional validated advice admission, restart, and later polish/mechanism controls remain disabled in the matched attribution study. Reading the function signature alone would misidentify the evaluated program.[^grounded], [^attribution]

## What grounding does and does not establish

The v5 reference gate asks Rocq whether named objects exist in relevant source environments. The Curator is asked to list the objects its advice relies on. Primitive tactic keywords require separate handling because they are not ordinary named library objects. Transport failures are distinguished from a negative lookup.[^evidence]

Reference existence is a weak but useful property. It does not establish that a lemma's hypotheses match the new goal, that a rewrite changes the intended expression, or that the surrounding tactic syntax is accepted. It does not certify a mathematical claim in the explanatory prose. The later Terra `have ... := ...` example is decisive: the referenced square-nonnegativity lemma exists, but the proposed syntax fails in the source environment.[^capacity]

The bounded evidence path goes further by storing a checked transition at a named source state. Executable guidance is derived from the checked action, rather than unconstrained explanatory text. The verified-snippet follow-up can preserve a bound source witness when a reducer's rewrite does not verify. Even that is a source-local certificate. Replaying a snippet successfully once does not establish a universally valid tactic for every superficially similar future goal.[^grounded], [^snippets]

## Resource control as part of the program

The project has several separate limits: model request count, nominal money, output allowance, aggregate verifier time, per-operation time, RPC count, and goal-view size. Stall detection can stop a search based on repeated nonprogress. Recovery and downshift policies can alter what happens near a limit. A campaign ledger separately controls the shared API liability of an experiment.[^budgets]

Earlier dollar limits generally stopped after a request crossed a threshold. They were not hard billing ceilings. The bounded system reserves a possible next operation before dispatch and settles actual usage afterward. That prevents uncontrolled spending, but conservative reservations can also stop a trajectory while money remains. The recent main configurations permit 64 requests and 300 verifier seconds, with 60-second operation reservations and a 32,768-token output allowance. A next request need not actually use that entire allowance for its reservation to matter.[^attribution]

Verifier time is accounted as elapsed operation time, not GPU training time or an estimate of processor instructions. A failed tool operation can consume resources without making mathematical progress. A resource-exhaustion result is not a kernel proof rejection. The reporting layer must keep those concepts apart, even if both lead to an unsolved theorem.

Exact replay also has layers. Replaying cached model answers can establish observed-request compatibility. It does not automatically reconstruct transport-side reasoning state or the decision to reject an unobserved next request. The capacity follow-up adds request-addressed transport snapshots and admission/terminal records, making exact continuation and exact barrier replay possible for the newly instrumented runs.[^replay]

## Paper-to-implementation comparison

| Aspect | ACE reference idea | Omphalos implementation and limit |
|---|---|---|
| Learning object | Evolving context/playbook | Structured Rocq advice with hashes and provenance |
| Supervision | Labels or execution feedback | Rocq execution/verification; no supplied gold proof labels |
| Roles | Generator, Reflector, Curator | Same core roles; explicit batch reducer and optional auditor |
| Updates | Local deltas and grow/refine | Deterministic merge; versioned lexical/semantic dedup and pruning |
| Attribution | Generator feedback on bullets | Initially inferred; later citations and cited-only counters |
| Adaptation | Offline and online | Both implemented; warm starts and repeated epochs tested |
| Verification | Task/environment feedback | Formal proof acceptance plus bounded, imperfect state observations |
| Context scale | Long-context tasks in the paper | Usually much smaller books under strict low-cost proof budgets |
| Caching | Serving-cost mechanism | Measured cached-input billing, with separate uncached repricing |

The mapping is close enough to study ACE mechanisms seriously, but the task, budget, model, and supervision differences prevent a simple “the paper's percentage should reappear here” expectation. This is a domain adaptation and empirical investigation of ACE, with documented deviations, rather than a numerical replication of the paper's AppWorld setting.[^ace], [^implementation]

# Baselines, partitions, and the meaning of a comparison

## There is more than one “baseline”

The early canonical agent uses Luna, the core toolset, medium reasoning effort, and a nominal $0.05 per-problem cap. The X-partition experiments use $0.10, show the problem's own definitions, and initially allow 32 requests. The newer bounded/focused program adds conservative admission and different feedback/control while allowing 64 requests. The all-Terra comparison uses a $1.00 allowance to preserve the nominal token opportunity under the recorded tenfold tariff ratio.[^governance], [^lineage]

These differences explain why a single chronological leaderboard is misleading. The same number of solved problems at a lower bill can be a useful engineering observation even when the interventions differ. It becomes an ACE causal comparison only when the book and its conditional instructions are the changing factor. Historical controls additionally carry provider-time, sampling, and caching differences.

| Seed-0 program | trainX solves / 40 | Train cost | validationX solves / 40 | Validation cost |
|---|---:|---:|---:|---:|
| Earlier agentic X program, no ACE | 33 | $0.777316 | 27 | $0.886961 |
| Current bounded/focused, no ACE | 28 | $0.818211 | 24 | $0.776512 |
| Current bounded/focused, Luna book | 28 | $0.689223 | 27 | $0.667228 |

The earlier non-ACE versus current non-ACE comparison loses five training solves and three validation solves. ACE cannot explain those losses because neither row uses it. The newer book restores three validation solves relative to its matched no-book program. The earlier agentic versus current flagship comparison preserves validation coverage at 24.77% lower recorded cost, but loses training coverage. These are three different questions with three different interpretations.[^lineage]

The attribution audit also corrected the idea that there had been no earlier non-ACE measurements on the X development panels. Those measurements exist, with two seed identifiers per panel. What was missing was a clean removal of ACE from the current bounded program. The audit found no separate documented model revision called “Luna v2.” A program revision should not be renamed into an unsupported model revision.[^lineage]

The baseline's endpoint and feedback format were also investigated before ACE. An August 13 study recorded 480 configurations and a $6.28 bill while separating the Responses endpoint, reasoning-item reuse, and conversion of user feedback into a tool result. Its decomposition retracted an earlier single-seed claim that Responses cost 97% more. On the standard Terra loop, the recorded paired subset cost $1.183 with Chat Completions, $1.098 with Responses without reuse, and $0.962 with reuse. These are historical descriptive figures from the experiment memory, not a newly verified complete-panel estimate. The old analysis restricted some comparisons to 39 completed cells; the current measurement rule instead retains platform failures and refuses a verdict when required cells are missing.[^responses], [^measurement]

That study also exposed a pooling mistake: feedback conversion appeared to add roughly 15% cost for Terra and save roughly 15% for Luna in aggregate, while paired comparisons did not establish either effect. The conversion additionally inserted an instruction, so it changed both representation and prompting. The reusable lesson for ACE is that a serving or prompt change can alter costs without establishing a proof benefit, and a pooled bill can conceal the distribution of per-problem effects.[^responses]

## Dataset roles have changed through use

The original small partitions contain twenty problems apiece. The X development panels contain forty each, with a more demanding mixture of competition and Mathd tasks. The larger panels were introduced because the original sets were insufficiently discriminating for Luna-class pipelines. Forty theorems evaluated with two seeds make eighty problem-seed cells, not eighty independent theorems.[^governance]

trainX supplies adaptation and tuning data. validationX has been reused for many rounds of selection and diagnosis. It is now **development data**. Describing its latest results as fresh out-of-sample confirmation would overstate what the study can show. Training-versus-validation contrasts remain useful descriptions of transfer within development, but repeated consultation weakens strong generalization claims.

The later review introduced a separate protected confirmation design. Its protected outcomes are not reopened here. Only the accessible development component is reported numerically. The study's existence and its distinction between selection and confirmation are relevant to methodology; the closed results are not necessary to explain how ACE or the budgeting mechanisms work.

## A measurement dictionary

| Term | Meaning in this report |
|---|---|
| Theorem/problem | One mathematical benchmark task |
| Cell | One registered problem × seed × configuration observation |
| Episode | One local or full proof attempt; local episodes need not be theorem solves |
| Request | A model completion request; one episode may make many |
| Tool/check event | A verifier or inspection operation; logs may include replay duplicates |
| Raw solve | Recorded proof success, before a monetary qualification threshold |
| Qualified solve | Recorded success satisfying the stated actual-cost or repriced-cost rule |
| Complete panel | Every expected cell has an interpretable terminal outcome and known accounting |
| Platform failure | Experiment/transport failure at the cell level, retained in the denominator |
| Prover-level failure | An operation error within a cell that may continue afterward |
| Cost per solve | Total panel spending, including failures, divided by qualified solves |
| Preparation cost | Generation, reflection, curation, reduction, and recorded embeddings used to build a book |

Local applicability accuracy is a different endpoint from useful continuation, and both differ from full theorem coverage. A system may correctly decide that a syntax change is valid, execute it, and still be unable to prove the theorem. Conversely, a failed applicability decision can be irrelevant to a theorem that the ordinary agent solves by another route.[^applicability], [^change]

## Statistical support, practical value, and selection

The current convention uses two-sided p<0.10 and 90% intervals for statistical support, with repeated seeds and duplicate theorem families clustered together. Historical campaigns retain their original rules. The old six-discordance convention is a minimum for attaining a small exact p-value under favorable circumstances, not a calculation of statistical power. Five independent all-favorable discordances give a two-sided p of 0.0625; three give 0.25.[^measurement]

This matters directly for the latest Luna ACE result. Three gains and no losses look promising and are worth reporting, but three discordant theorems do not establish the coverage effect under the exact test. A descriptive bootstrap interval that happens to exclude zero does not override that result, especially with few discordances at a boundary. Nor does p=0.25 prove that the book has no value.[^attribution]

Practical decisions also depend on experiment cost and the kind of trade-off the researcher wants. The model-screen contender that gained one problem while using less money missed a registered +2-solve gate. Guille correctly objected to treating that gate as a blanket reason not to perform an affordable follow-up. The historical gate remained failed, and a separately authorized benchmark supplied more information. That distinction should be maintained in the thesis: honest preregistration does not require abandoning judgment about worthwhile exploration.[^judgment]

# Experiment history

This chapter reconstructs the sequence from accessible implementation, development archives, memories, protocols, and final campaign reports. The appendix preserves per-seed archive rows and distinguishes incomplete records. The numbers below should be compared within their stated panel and program, not summed into a grand success rate.

## Initial replication: advice changes the work more than the outcome

The first ACE implementation, evaluated in August, used a frozen book on the original twenty-problem validation partition with seeds 0 and 1. Both baseline and ACE solved 32/40 cells, with one gain and one loss. The reconstructed validation bills are approximately $0.444593 for the baseline and $0.505769 for ACE. The original analysis reports a median paired cost ratio of 1.093; that differs from the ratio of aggregate bills because it answers a different statistical question.[^replication], [^archive]

The important mechanism observation was that the playbook roughly halved median output tokens, while increasing cached-context reuse and reducing some unknown-reference failures. It changed how the prover reached its answer without creating a clear coverage advantage. This is entirely plausible: a remembered lemma can replace a long derivation, but the difficult residual tasks may depend on a missing invariant or a formalization step the book does not teach.

The initial no-Reflector ablation produced a similarly sized book with a different composition: more lemma entries and fewer strategic abstractions. The monolithic rewrite ablation did not reproduce context collapse at this small scale. That does not contradict the paper's longer-context example; the local experiment operated far below that example's context length and adaptation horizon. The original larger-pool and three-epoch proposals were initially not completed. Later X-specific multi-epoch experiments are separate variants and should not be confused with those early placeholders.[^replication]

The definition-preamble bug was another lasting result. The problem parser omitted local `Definition` and `Fixpoint` material from the prompt. Supplying it fixed one of eight evaluated cells, without an observed loss. The missing context was a real bug, but the measured improvement was much smaller than an initial diagnosis based on how many failures involved definitions might suggest. A plausible explanation must still survive an intervention.[^replication]

## X partitions and v2: more complete ACE machinery

The X generation introduced larger development panels, semantic deduplication, periodic refinement, harmful-bullet pruning, block-scalar curator output, and IDs without the bookkeeping counters in the Generator's prompt. Cold and warm online adaptation, frozen offline books, repeated epochs, monolithic rewriting, and selective injection were represented as separate treatments.[^adaptation]

The usable v2 offline evaluation totals 54/80 validation solves, the same count as the agentic X baseline. Cold online adaptation reaches 28/40 on each seed against baseline 27/40 on each, while warm online adaptation reaches 26/40 and 24/40. Warm starting therefore did not automatically improve these sequences. The archived frozen three-epoch v2 book reaches 50/80. These are descriptive development outcomes under their respective treatments.[^archive]

Several early directories contain incomplete top-k, no-Reflector, or mislabeled attempts. The retained manifest still lists expected cells even where a result file is absent. The retrospective reports those as incomplete rather than interpreting completed subsets as if they were a full run. Online X3 seed 0 likewise has an unresolved archived cell in this reconstruction; its observed successes are not promoted into a complete-panel verdict.

## X3: reference-oriented curation and batched reduction

X3 adds more explicit references and citations, stronger evidence in curation prompts, and batched reduction. Its one-epoch four-problem-batch book becomes the later reference artifact. The three-epoch X3 arm uses a larger 8,000-token book guard; it is not merely a repeat of the v2 run. The no-Reflector and monolithic arms retain their distinct mechanisms.[^adaptation]

On the complete two-seed validation reconstruction, X3 and no-Reflector each reach 57/80 raw solves; monolithic rewriting reaches 55/80; three epochs reach 53/80; and cited-only X4 reaches 55/80. The no-ACE baseline is 54/80. These differences are small relative to the panel and repeated-selection history. The equal X3/no-Reflector totals do not establish that reflection is useless, but they give no coverage justification for attributing the whole improvement to reflection alone.[^archive]

The results also separate code fidelity from empirical benefit. Adding the mechanisms missing from a first replication can make the implementation more faithful and auditable without increasing solves. X4's cited-only counters provide a better defined attribution channel, yet the subsequent citation audit shows many mentions are initial declarations of intended use. Better bookkeeping does not automatically provide causal credit assignment.[^cycles]

## V5 and stronger writers: targeted repairs to the learning process

The September 2 audit identified several plausible reasons for a weak ACE effect. Frequent mechanical failures were poorly represented in the books. Some advice was dead, contradictory, or dangerous. Deduplication and refinement often did little in practice. The reducer discarded many proposals, and a model-override hook had not covered the reducer. Successful cases suggested that concrete, correctly named lemmas could be more valuable than generic advice.[^v5]

Two treatments followed. The **stronger-writer** arm kept Luna as Generator while using Terra for reflection and curation, including reduction. The **v5** arm added a pool-level failure digest, explicit awareness of guidance already in the system prompt, object grounding, skipped role calls on trivial solves, and a terminal audit. V5 bundles these changes, so its comparison evaluates the bundle rather than separately identifying every component's effect.

The stronger-writer book obtains 55/80 validation solves and v5 obtains 53/80, against 54/80 for no ACE and 57/80 for X3. V5 reduces some unknown-reference and syntax categories without increasing overall coverage. The audit also found correct, grounded advice that repeatedly directed a proof along an unhelpful route. Availability and correctness of an isolated statement are not sufficient to establish usefulness for search.[^v5], [^archive]

The provenance deviations matter. Some stronger-writer adaptation steps used an empty book after stale-directory recovery, and an early v5 curator batch retained an older taxonomy label. These observations limit clean component attribution. They do not erase the work, but they belong beside its results rather than in an invisible implementation footnote.

## Rendering, hint-on-error, and repair-mined advice

The next cycle separated the cost of resending advice from the cost of the behavior the advice induces. A book may reduce the number of requests while making each request more expensive. Citation instructions can also change how much the model writes and how it sequences proof attempts. The first v5 comparison favored rendering version 2 over version 3, with equal coverage and lower paired spending.[^cycles]

That finding was initially generalized too far. On the X3 book, rendering 2 was more expensive than rendering 3 on the paired comparison, reversing the sign. The correct conclusion is **a rendering-by-book interaction in the measured samples**, not a universal rule that removing citation wording saves money. The memory explicitly retracts the earlier general prescription.

Hint-on-error delivery supplies a few selected bullets only after an error instead of including the whole book from the outset. It reduces the repeated input burden, but also removes the opportunity to prevent a first error. The v5 triggered arm reaches 53/80 raw solves against 54/80 baseline. Six extra Terra-written repair bullets were then mined from verifier-accepted repairs. That x6 treatment reaches 56/80 raw solves, while its repeated-syntax metric improves and more of the remaining work shifts to incomplete proofs.[^cycles]

Under this retrospective's fixed-date token-cost qualification, x6 has **55/80** qualified solves: one raw success is above the nominal $0.10 threshold. This is a transparent change of endpoint, not a revision to the archived raw count. It also does not claim complete retry-inclusive billing for these older archives. Both raw and qualified counts are retained in the workbook.[^archive]

## Stall stopping and the deterministic digest table

The stall work asks a budget question: can we stop spending on a search that repeatedly returns to a previously seen failure state? The selected `seenstate k=4` rule uses four consecutive rejected attempts whose error/goal signature was already seen. It is implemented as a pure predicate shared by offline analysis and the live strategy.[^cycles], [^stall]

The historical analysis reports roughly 7% less spending and one fewer validation solve, with a stronger cost saving on a separate development panel. The retained live seed-0 validation archive contains 26/40 solves and $0.794254, against baseline 27/40 and $0.886961. The live comparison and offline truncation answer related but different questions; model sampling can differ even when the stopping predicate's replay parity is established. The retrospective does not combine their percentages.

The deterministic digest-table arm eliminates LLM curation and renders eight short failure-oriented bullets. It reaches 51/80 validation solves against X3 rendering 2's 56/80. The historical paired difference is seven gains and two losses for X3, p=0.18. Thus the descriptive evidence suggests curation can retain useful information absent from the simple table, while remaining too uncertain to establish a general advantage. “No robust ACE uplift” should not be rewritten as “all learned advice is equivalent to a free lookup table.”[^cycles]

![Complete historical two-seed validation arms. The left panel shows raw solved cells; the right includes all cell costs repriced at the fixed snapshot date. These arms share a development panel but differ in book, rendering, and delivery. Incomplete archives are omitted from this figure and listed separately.](figures/historical_matrix.pdf){width=100%}

## Review campaign: the accessible development stage

The review adds stricter campaign accounting, runtime calibration, a 64-request development comparison, repair training, and a separation between development selection and protected confirmation. This retrospective uses the eight complete forty-cell development arm/seed groups, while leaving the protected stages and their mixed final report closed.[^reviewdev]

The development raw counts are baseline 52/80, X3 57/80, repair-book 0 at 55/80, and repair-book 1 at 54/80. For repair-book 0, one raw success falls above the retrospective token threshold, leaving 54/80 under that definition. Costs in the archive are token-based reconstructions, not a substitute for the campaign's full retry-inclusive liability. The repair books do not exceed X3's observed coverage in this stage.

The next bounded campaign's comparator is specifically **X3 seed 0 at 28/40 and $1.52378888**. It is neither the original 32-request X baseline nor the later bounded flagship with 27/40. Confusing these references caused at least one incorrect memory summary, corrected in the subsequent control-cycle record.[^control]

## Bounded ACE: the accepted budgeting result

The bounded follow-up was designed after concern about the cost of the preceding study. It used four adaptation episodes, sixteen trainX pilot cells, and forty frozen validation cells. The selected configuration enables money and focused behavior, with advice admission and restart disabled. Neither advice nor restart triggered in the pilots, so the result does not establish their usefulness.[^bounded]

The validation result is 25/40 qualified solves for $0.67804714 against X3's 28/40 for $1.52378888. The recorded solve p-value is 0.375 and the cost p-value approximately 0.00011. The original rule requiring savings without fewer solves was not satisfied. Guille subsequently accepted the cost/coverage trade-off and retained it as a budget reference. Both facts are part of the final outcome.

The arithmetic makes the trade-off concrete. X3 costs about $0.05442 per qualified solve across this panel; bounded costs about $0.02712. The latter nearly halves cost per solve, but leaves three additional theorems unsolved. Whether that is preferable depends on the application objective. It is a meaningful thesis result about control without being a proof of equal quality.[^bounded]

Adaptation itself exposed reliability issues: only one of four paid episodes completed; three stopped on malformed YAML without retry. Eight checked claims survived offline processing, but no bridge coverage was demonstrated. Total experiment API spending was $1.38272072. The failure audit also confirmed a typed-limit reservation defect: an intended seven-second operation could be reserved as sixty seconds. This was a concrete control bug, distinct from whether the mathematical advice was good.

## Bounded control cycle: recovering coverage at a price

The subsequent control cycle used forty tuning training cells, forty trained training cells, and forty frozen validation cells. It produced 95 training transitions and twelve reverified claims under a 4,096-token artifact cap. The trained program solved 30/40 training problems and 28/40 validation problems.[^control]

Validation cost was $1.02528810: 1.512 times the retained bounded comparator's $0.67804714. It restored three validation solves, so it moves along the cost/coverage trade-off rather than improving both simultaneously. Its registered observed-Pareto rule failed. Against the older X3 comparator, the count ties at 28 while spending is lower; that is a different comparison and should be named explicitly.

The campaign's conservative liability is $2.99915804, including a DNS failure with an unknown-conservative original charge. The surviving working-tree source is missing pieces advertised for this control cycle, and its paid entrypoint was closed to prevent silently rerunning a different implementation into the same archive. The measurements remain evidence of the recorded campaign; full reproducibility from current source alone remains a limitation.

## Polish: useful interfaces without a benchmark win

The polish campaign evaluated matched advice, output downshift, and resource-recovery choices through twenty-four pilots, forty training cells, and 160 fresh paired validation cells: forty theorems, two seeds, two arms. It spent $4.24146774 in settled API calls.[^polish]

The candidate and reference both solved 53/80 validation cells. Candidate cost was $1.51289576 against $1.43330822, a 5.55% increase. Seed 0 lost one solve and cost more; seed 1 gained one solve and cost less. Neither registered utility gate passed. Equal totals and p=1 are not equivalence evidence; they indicate that this study did not establish a useful coverage difference.

Downshift solved none of nine triggered training cells and one of seventeen triggered validation cells; the reference also solved the latter theorem at lower cost. Neither unique candidate validation gain used downshift. Matched demonstrations were selected in twelve validation cells, which is exposure evidence rather than proof of causation. The code remains opt-in, with the earlier money+focused reference retained.

A reporting bug was fixed before the full benchmark: an older reader inspected only the first 64 KiB of a result file, while embedded artifact arguments pushed the real outcome beyond 131 KiB. The corrected reader anchors at the actual command outcome. The mistaken pilot drafts were preserved, and the selected switches did not change. This is exactly why derived reports should be checked against the underlying result structure.

![Three budgeting comparisons, each retaining its own panel size and reference. The bounded result trades three solves for a large cost saving; the control cycle buys them back; polish ties coverage at a somewhat higher bill.](figures/budget_tradeoffs.pdf){width=100%}

## Applicability: deciding when advice is relevant

The applicability study uses twelve saved training states across four arms: ordinary response (R), typed grammar/query control (Q), fixed demonstrations (F), and adaptive example delivery (A). These are **48 local episodes**, not forty-eight theorem-level benchmarks. The arms achieve 1/2/3/2 useful transitions, respectively.[^applicability]

Adaptive delivery repairs four of six positive states and explicitly abstains on four of six negatives, admitting no negative state. Fixed demonstrations repair five of six positives. A is 23.34% cheaper than F but loses a useful transition, so its primary screen fails. The full training and validation stages were not run. A small local bill, $0.05822918, does not support a claim about end-to-end cost per solved theorem.

The finite grammar was also too restrictive: valid separate-sentence suffixes were rejected before the kernel could evaluate them. Eleven offline checks identified the limitation. A post-hoc sensitivity analysis changes Q/F/A useful transitions to 3/4/3 and leaves the ranking against fixed examples unchanged. The primary scores remain frozen. Grammar rejection should not be mislabeled as mathematical invalidity or kernel rejection.

## Checked change and local reasoning-effort probes

The checked-change experiment replaces a learned applicability judgment with an explicit local verification operation where a finite canonical transformation is available. On six training states, correctness rises from 3/6 to 6/6 and useful transitions from 1/6 to 2/6, while primary cost falls from $0.02441020 to $0.01390688. The larger twenty-four-episode campaign costs $0.15247908. This is encouraging control evidence, not an ACE or full-theorem saving.[^change]

Subsequent local effort probes do not give a simple “more reasoning is better” story. Terra low, medium, and high each obtain 4/6 correct decisions. Luna medium obtains 3/6, high 5/6, xhigh 5/6, and max 4/6. High and xhigh make different mistakes. Max uses more tools and more money, yet sometimes inspects the wrong object instead of checking the disputed conversion at the actual state.[^effort]

For example, printing a power definition does not answer whether an `Rsqr` expression is definitionally convertible in the local context. `Check change` is also not a meaningful way to look up a tactic as a library object. These observations suggest a need for correctly targeted checking and representation handling. They do not show that additional generic inspection capability was missing.

## Model/effort suite and the two full contenders

The model suite separates prover effort from writer-role changes. On its sixteen-cell prover screen, low/medium/high/xhigh solve 9/11/10/11, with xhigh lower cost than medium. Twenty-three role books are constructed. The strongest assembled selection candidate uses an xhigh prover and xhigh reflector, reaching 18/24 for $0.32374134 against flagship 17/24 for $0.37196362. Its +1 gain misses the original +2 gate. The complete initial suite costs $8.71724.[^models]

The subsequent judgment correction leads to exactly 160 new full-panel cells: both reflector variants, one seed, trainX and validationX, reusing existing controls. Medium-reflector and xhigh-reflector candidates both use an xhigh prover, medium curation/reduction, and no audit. This is a separately authorized follow-up, not retroactive relabeling of the original gate.[^judgment], [^contenders]

The medium-reflector candidate reaches 26/40 training and 19/40 validation solves. The xhigh-reflector candidate reaches 27/40 and 24/40. Flagship counts are 28/40 and 27/40. Xhigh reflection is the stronger of these two candidates, and saves 15.6% training cost and 12.2% validation cost against the flagship, but loses one and three solves. Follow-up spending is $2.60155656; the combined model-suite/follow-up amount is $11.31879656. It is a measured cost/coverage trade-off, not a coverage upgrade.

## Mechanisms: structured continuation confounded by parsing

The mechanisms campaign compares explicit suffix/replace contracts (S), additional checked changes (C), progress/recovery controls (R), and an effort-only arm using the fixed incumbent book (E). It completes 248 new cells for $3.364201. E's training result, 29/40 at 11.63% lower cost than the reference, justifies the planned validation stage despite inconclusive coverage statistics.[^mechanisms]

Validation E reaches 43/80 against reference 53/80, with 5.07% lower total cost but 17.01% worse cost per solve. This does not support promotion. More importantly, S/C/R's training counts of 22/21/15 include 51 structured parse failures, 33 of which are identical duplicates. The inherited parser concatenated multiple final-answer messages, corrupting the structured contract.

A separate v2 adapter parses the last final message and passes focused offline checks. A saved-answer continuation can close one training case with that fix. The paid benchmark for v2 was not run, and the original outcomes were not rescored. The correct interpretation is “these implemented arms underperformed, with a major parser confound,” rather than “checked continuation and recovery have been experimentally refuted.”

## Fixed-book coverage and four isolated follow-ups

The accessible portions of the first fixed-book coverage campaign compare demonstrations (D) and an exploration treatment (E), with the ACE book unchanged. D/E each solve 26/40 training tasks against reference 28. On validation, D solves 26/40 for $0.62971114, E solves 25/40 for $0.67558288, and the reference solves 27/40 for $0.66722836. The campaign's mixed artifacts and closed evaluation stage are excluded.[^coverage]

The next campaign tests four isolated development changes, exactly one training and one validation run per arm: operation-aware demonstrations (D2), earlier stall-triggered exploration with proof-only suffix turns (E2), finite checked syntax repair (S), and history compaction (H). That is 320 new cells and $6.00834588. All four have fewer validation solves and higher validation cost than the incumbent.[^coveragecycle]

| Treatment | Train solves / 40 | Train cost | Validation solves / 40 | Validation cost |
|---|---:|---:|---:|---:|
| Historical flagship | 28 | $0.689223 | 27 | $0.667228 |
| D2 relevant demonstrations | 27 | $0.730910 | 25 | $0.705429 |
| E2 earlier exploration | 28 | $0.669663 | 24 | $0.785495 |
| S checked syntax | 29 | $0.663597 | 25 | $0.760957 |
| H history compaction | 27 | $0.873451 | 25 | $0.818844 |

S and E2 have encouraging training cost/coverage signals that do not transfer to their frozen validation runs. D2's solve disagreements occur outside the cells that receive its new examples. E2's gains and losses likewise occur outside its live-triggered cells. The syntax arm can repair a valid local form while leaving the theorem unfinished. H shortens the context but produces long, repetitive, often tool-only histories. These are distinct diagnoses; they should not be collapsed into one generic “ACE failed” label.

![Changes relative to each stage's own historical reference. The training savings of S and E2 did not persist on validation. Validation here is reused development data, not a fresh holdout.](figures/coverage_transfer.pdf){width=100%}

# The latest attribution and capacity studies

## Matched ACE removal and all-Terra adaptation

The attribution study addresses the central missing comparison: remove the book from the current bounded/focused program while preserving tools, demonstrations, feedback, effort, and budgets. It also builds an all-Terra book using the same training order and evaluates Terra with and without that book. “All-Terra” includes Generator, Reflector, Curator, and Reducer; the earlier stronger-writer X3 variant kept Luna as Generator.[^attribution]

The study adds 312 proof episodes: 240 main inference episodes, forty Terra adaptation generators, sixteen book-swap episodes, and sixteen effort diagnostics. Eighty compatible Luna ACE observations are reused. Writer-role and embedding calls are separate preparation work. Total new API spending is $38.88507492. This is not the cost of merely applying a frozen book to forty tasks.

| Solver / context | Train solves / 40 | Train cost | Validation solves / 40 | Validation cost | Validation cost / solve |
|---|---:|---:|---:|---:|---:|
| Luna / none | 28 | $0.818211 | 24 | $0.776512 | $0.032355 |
| Luna / Luna book | 28 | $0.689223 | 27 | $0.667228 | $0.024712 |
| Terra / none | 33 | $5.952686 | 29 | $6.610626 | $0.227953 |
| Terra / Terra book | 32 | $5.474728 | 30 | $6.451344 | $0.215045 |

All successful main cells qualify under their respective model allowances. Luna's validation ACE difference is +7.5 percentage points, with three gains and no losses and exact p=0.25. Terra's is +2.5 points, with two gains and one loss and p=1.00. These observations support describing the effects as modest and uncertain. They do not support an equal-quality claim, a universal null, or a large reliably replicated ACE gain.

The secondary no-book model comparison gives Terra five validation gains and no losses, p=0.0625. That meets the nominal 10% threshold for this secondary contrast, without multiplicity correction. It shows useful model scaling under the price-proportional allowances. It does not show a cheap replacement for Luna: Terra with its own book costs 9.67 times as much as Luna with its own book for three more validation solves.

## Full solver-by-book crossover

The capacity follow-up completes the six-way validation crossover. It reuses 176 compatible records and buys 64 missing swaps, making 240 observations over forty theorems. The resulting matrix separates solver model from book author more clearly than comparing only each model with its own book.[^capacity]

| Solver | No book | Luna book | Terra book |
|---|---:|---:|---:|
| Luna solves / 40 | 24 | 27 | 24 |
| Luna total cost | $0.776512 | $0.667228 | $0.734194 |
| Terra solves / 40 | 29 | 29 | 30 |
| Terra total cost | $6.610626 | $6.852274 | $6.451344 |

Fix the Luna book and compare its increment on both solvers. Luna gains three solves, Terra gains none: the difference in increments is −7.5 percentage points, with descriptive 90% interval [−17.5, 0] and exact p=0.375. The observed direction goes against the simple prediction that stronger solving must unlock a larger book benefit. Uncertainty remains too large to establish a negative interaction.

Changing the author of Luna's book from Luna to Terra loses three net validation solves and increases recorded cost by 10.04%. For Terra, its own book adds one solve relative to the Luna book, at somewhat lower cost. Neither establishes a general stronger-author advantage. The first 176 observations are historical controls; source and observed-request compatibility cannot remove differences in provider time or stochastic responses.

## Matched writer jobs and book quality

The follow-up separately supplies identical frozen inputs to both models for forty Reflector jobs, forty Curator jobs, and twenty Reducer jobs per model. This totals **200 role jobs**. Holding input constant matters: otherwise a stronger model's better training trajectory could make its reflection seem better simply because it had better material to reflect on.[^creator]

All jobs eventually produce valid structured output. Luna needs one extra request after returning `bullet_tags: null` instead of a list. Terra has no unbound tags in these jobs; Luna has one unbound neutral citation when the book is empty. Those observations measure output-contract reliability and attribution bookkeeping. They do not, by themselves, rank mathematical or pedagogical quality.

The deeper evidence is mixed. Terra correctly identifies a final `nia` completion where Luna credits an unexecuted `norm_num` ending. But Terra also reproduces invalid `have ... := ...` syntax on the same reducer input on which Luna avoids it. Both models drop or combine potentially useful material under the three-addition allowance. More text, more reasoning tokens, or fewer missing-name mentions is not a sufficient quality metric.

The source audit also corrects overaggressive hallucination counting. A name can appear in a warning, a local binder, a comment, or a source file from another member of the same reduction batch. Checking it only against the first file can produce a false accusation. The additional source-environment checks distinguish actual positive recommendations from warnings and resolve batch-import differences.[^creator]

## Controlled feedback/snippet treatments on eight hard training cases

The diagnostic panel uses eight selected trainX problems, five profiles, and two models: eighty fresh episodes. Profile A has no book and original feedback; B has the original Terra book and original feedback; C adds version-2 goal visibility without a book; D combines that feedback with the original Terra book; E uses version-2 feedback and a source-corrected Terra snippet.[^capacity]

Luna's A/B/C/D/E counts are 3/3/4/3/3 out of eight. Terra's are 3/3/4/6/3. The conspicuous Terra D result looks attractive until exposure is checked: **the added goal-visibility feedback never fires in D**. Across all thirty-two A/C and B/D pairs, first requests are identical, while twenty-five first replies differ. The extra solves cannot be causally credited to information the model never received.

This is one of the most useful lessons in the entire history. A seed identifier names an experiment replicate; it does not make the provider's sampled responses deterministic. Comparing two configurations with the same seed and finding different outcomes is not sufficient evidence that the changing code path caused the difference. Intervention exposure must be demonstrated.

## Exact continuations and additional budget

Only the no-book C and source-corrected E paths are continued. Level 1 doubles money, from $0.10/$1.00 to $0.20/$2.00 for Luna/Terra, keeping request and verifier limits fixed. Level 2 keeps those money limits and doubles requests from 64 to 128 and verifier time from 300 to 600 seconds. Solved and failed paths are carried forward rather than restarted.[^capacity]

| Solver / profile | Initial solves; cost | More money | More requests and verifier time |
|---|---|---|---|
| Luna / no book | 4/8; $0.217615 | 4/8; $0.467413 | 4/8; $0.512939 |
| Luna / corrected book | 3/8; $0.209094 | 3/8; $0.537274 | 3/8; $0.558412 |
| Terra / no book | 4/8; $1.773286 | 6/8; $3.899886 | 6/8; $4.257558 |
| Terra / corrected book | 3/8; $1.970293 | 7/8; $3.935691 | 7/8; $3.935691 |

Terra recovers several hard proofs with more money, while Luna's sampled paths do not add solves. Increasing the request/verifier allowances adds none. Yet all eleven ordinary residual failures at the final level still stop on money admission, and none exhausts the literal 600-second verifier allowance. A twelfth carried path is a platform failure. The experiment therefore does not establish an uncensored intrinsic capacity ceiling.

The final corrected-book advantage over no book is one theorem on Terra and a deficit of one on Luna. The corresponding solver-by-book interaction is a promising descriptive pattern on eight selected problems, with p=0.5. It is not a representative ACE coverage estimate. Terra E's four recovered solves from additional money are similarly important observed behavior, not confirmation of a population effect.

![Measured continuations of the same paid prefixes. Additional money recovered Terra proofs in this selected panel; additional request/verifier allowance recovered no further proofs. Each path cost includes its prefix once.](figures/continuations.pdf){width=100%}

## What this latest study actually achieved

The follow-up adds 173 proof execution records and 200 role jobs. It costs $23.25562298, bringing the attribution/capacity pair to **$62.14069790**, with $12.85930210 left unused from their shared $75 ceiling. The forty-case crossover, matched creator jobs, and exact continuations answer different questions and should not be combined into one “success rate.”[^capacity]

The engineering gains include exact transport/admission replay, bounded visibility of otherwise hidden obligations, and source-bound snippet preservation. The source seal and reference hashes verify; newly instrumented execution records replay to their recorded admission/terminal sequences. One rejected API dispatch is preserved as a failed path rather than silently retried into a success. None of these results automatically changes the flagship default.

# Spending versus problems solved

## Four different meanings of “cost”

**Recorded spending** is the charge attached to the observed experiment. Where request receipts exist, retries and failed attempts belong in that total. **Token repricing** applies an explicit price schedule to recorded token counts; it is useful for consistent comparisons across archives. **Price sensitivity** recomputes a bill under a counterfactual tariff or cache discount. **Preparation amortization** spreads book-building cost over an assumed future workload. These quantities answer different questions.[^pricing], [^attribution]

The local pricing registry stores dated rates. Historical archive columns labelled `price` are not trusted as a universal source of truth. This report fixes token repricing at the snapshot date and labels it separately from receipt-based campaign bills. The numerical appendix records the source and cost basis. No current online price has been retroactively substituted into a historical invoice.

For the recent recorded configuration, Terra's input, cached-input, and output tariffs are ten times Luna's. This explains the model-specific caps. Terra's 32,768-token output reservation alone is approximately $0.393216 at the recorded tariff; an unchanged controller with a $0.10 Terra cap could refuse even to start. That is an admission-policy outcome, not an empirical observation that the first answer would necessarily cost forty cents.[^attribution]

## Whole-panel spending and cumulative coverage

The following curves include every task's recorded inference cost, including unsolved tasks. They process tasks in the fixed validation partition order, accumulating both spending and qualified solves. A flat segment means money was spent without adding a qualified solve. The terminal point is the whole-panel result.

These are **accounting curves for the observed records**, not an online scheduling policy or a claim about the order in which concurrent invoices arrived. A different order would change the intermediate shape. Sorting by observed successful cost would give an artificially favorable sequence that requires knowing the outcome in advance, so it is not used. Preparation cost is separate and discussed below.

![Cumulative spending and qualified solves on the fixed forty-problem validation order. Unsuccessful tasks contribute to the x-axis. The different x-axis ranges preserve the substantial actual-price difference between Luna and Terra.](figures/cumulative_spend.pdf){width=100%}

For Luna, the own-book endpoint has both more solves and a lower recorded bill than the no-book endpoint. For Terra, the own-book endpoint has one more solve and a slightly lower bill than no book. Those are observed within-model trade-offs on the complete panel. They still inherit the statistical and historical-control limitations described above.

## Why a cost-threshold curve is not a smaller-budget experiment

A threshold curve asks: **of the proofs already completed, how many had final recorded cost at most this amount?** At a common $0.10 threshold, Luna's none/Luna-book/Terra-book counts are 24/27/24 and Terra's are 21/20/20. Terra was actually allowed to search under $1.00. Its low-cost completed proofs cannot be reported as the result of running that controller under a $0.10 allowance.[^capacity]

To infer smaller-cap behavior from a recorded prefix, the relevant stopping and admission semantics must be reconstructible. Conservative next-request reservations can reject a request whose eventual bill would have been small. A post-crossing policy and a pre-admission policy can therefore have different counterfactual curves. The exact-continuation study records real extensions; the threshold plot simply qualifies observed final costs.

![Retrospective qualification of observed proofs. The left uses recorded tariffs within a common ten-cent window; the right reprices Terra tokens at Luna rates. The right panel is an accounting sensitivity, not an available cheaper Terra service or a newly executed budget policy.](figures/cost_thresholds.pdf){width=100%}

## Cached-input billing materially changes the conclusion

Luna's own book lowers validation spending from $0.776512 to $0.667228, a 14.07% reduction. But input tokens rise slightly, from about 5.780 million to 5.877 million, and output tokens also rise slightly, from 243,896 to 245,341. Model requests fall from 497 to 447, while cached-input share rises from 64.61% to 75.87%.[^attribution]

At the same observed token counts with **all input charged as uncached**, no-book cost is $1.448678 and own-book cost is $1.469747: a 1.45% increase. Terra's analogous uncached sensitivity is an 8.51% increase. Thus the measured bill saving is real, but it cannot all be attributed to less reasoning or fewer tokens. Context reuse and cache pricing are material parts of the economics.

This does not undermine the practical value of a caching-friendly system. It changes the claim from “the book universally reduces computation” to “under these observed requests and cache discounts, the book lowers the bill.” If a deployment has low cache reuse, a different provider, or different prices, the same token behavior can have a different financial ranking.

![Actual-price crossover and uncached-input sensitivity. The same recorded trajectories have different accounting outcomes when cached input loses its discount. Source values are retained in the workbook.](figures/crossover_and_cache.pdf){width=100%}

## Book creation and amortization

The matched original book-building chains use the same forty training tasks in four-problem batches. Luna's evolving Generator solves 33/40 and Terra's 38/40. Both finish with twenty-six bullets; estimated sizes are 2,103 and 2,426 tokens. Neither chain reaches the 4,000-token guard. Selection at the reducer remains a bottleneck even without global size pressure.[^attribution]

| Preparation role | Luna cost | Terra cost |
|---|---:|---:|
| Generator | $0.711104 | $5.998384 |
| Reflector | $0.150748 | $1.557570 |
| Curator | $0.041454 | $0.412922 |
| Reducer | $0.013618 | $0.130302 |
| Recorded embeddings | Unavailable | $0.0000406 |
| Total recorded preparation | At least $0.916924 | $8.099219 |

Luna's historical embedding bill is not recoverable from these receipts. Reusing an embedding cache does not reveal what the original creation cost, so the missing amount is left unknown. Terra's recorded preparation is approximately 8.83 times Luna's known generative cost. Under Luna token rates its generative bill would be lower, again an accounting sensitivity rather than a price offer.[^preparation]

![Book size and Generator coverage during adaptation. Points occur after four-problem batches. These evolving-book training trajectories use different controller semantics from the final bounded inference evaluation.](figures/book_evolution.pdf){width=100%}

If the measured per-problem inference saving persisted on a future workload, preparation could be spread across many attempts. At 100 tasks, Luna's known preparation adds about $0.00917 per task and Terra's adds $0.08099. At 1,000 tasks the additions are about $0.000917 and $0.00810. The relevant denominator is **attempted problems**, not just future successes.

Using these validation averages, Luna's known preparation would break even on inference spending after roughly 336 future tasks; Terra's after roughly 2,034. These are arithmetic scenarios assuming unchanged workload, coverage, prices, cache behavior, and book usefulness. They exclude engineering and assistant costs; the Luna value is a lower bound because its historical embedding bill is missing. They are not forecasts of external generalization.

![Preparation amortization using the observed validation mean inference bills. The dashed line is no-book inference cost per attempted task. No claim is made that performance or cache behavior remains constant on a new workload.](figures/amortization.pdf){width=100%}

## What the total research bill can and cannot say

Experiment API bills are only part of research cost. Assistant usage, engineering time, local verification resources, and supervision are generally outside the campaign ledgers. No sufficiently complete evidence is available here to price all of those components. Their omission must not be interpreted as zero cost.

The receipt appendix deduplicates request IDs across accessible exports. Reused reference observations have an inference cost when comparing programs but create no new campaign charge. Continuation graphs include their paid prefix once; new-spending ledgers include only newly dispatched work. The attribution/capacity pair's $62.14069790 is not added to its $38.88507492 and $23.25562298 components again.

Older archives can lack complete retry receipts, and the control cycle has conservative unresolved historical liability. Closed campaigns are not read to manufacture a repository-wide total. Consequently the report presents identified campaign bills and a clearly scoped receipt subtotal, rather than a falsely precise “all money ever spent on Omphalos” number. No new experiment API calls were required for this retrospective.

# Mistakes, failure mechanisms, and corrections

## A chain of requirements, not a single ACE switch

For advice to create an extra solve, several things must happen: the relevant experience must be captured correctly; a useful lesson must survive reflection and curation; its code and assumptions must be valid; the appropriate request must receive it; the solver must act on it; that action must advance the proof; and the search must have enough allowance to finish. Failure at any link can erase an otherwise useful contribution.

This is an analytical framework for reading the evidence, not a fitted probabilistic model. The experiments supply examples of failures at almost every link. It explains why improved syntax statistics and a better book can coexist with unchanged theorem coverage. It also gives more useful research questions than treating all failures as “the model is weak.”

## Missing terminal evidence creates incorrect lessons

On the training task `amc12_2000_p6`, the submitted text contains an ending involving enumeration, `omega`, and `norm_num`. The verifier had actually accepted an earlier prefix completed with `nia`. Luna's reflection credits the unexecuted ending, while Terra identifies the accepted completion. A saved witness verifies `nia` and rejects the proposed `norm_num in *` ending.[^terminal]

The immediate lesson is about evidence construction. The Reflector needs the exact final accepted proof and any automation-assistance receipt, not merely a final success Boolean beside the last proposed script. In seven of thirty-three successful source histories, the verified final tactic is absent from the last submitted text. That count is a textual audit flag, not proof of seven identical semantic misattributions.

This issue also qualifies claims about stronger reflection. A better model can sometimes infer the missing explanation, but repairing the evidence contract is more direct than relying on that inference. The existing follow-up hint #130 concerns terminal verified-proof evidence. The report does not generate new advice from protected failures.

## Correct references can accompany invalid executable advice

The Terra reducer introduces `have Hsq : ... := Rle_0_sqr _` into a square-related bullet. The Generator's source proof used valid `assert`, reflection preserved the relevant mathematical diagnosis, and curation retained valid guidance. The reducer is where invalid syntax enters. The referenced lemma exists, so a name-availability gate cannot detect this defect.[^snippets], [^creator]

The source-verified alternative uses `assert (...) by apply Rle_0_sqr`. The follow-up demonstrates that the invalid reducer form can recur even on identical frozen input. Preserving a checked snippet through reduction is therefore a meaningful implementation improvement. It certifies the specific witness and bindings, not future applicability everywhere.

There is also a separate causal question: did that snippet cause a particular lost theorem? A bullet being cited before a rejection is insufficient. The surrounding tactic may differ, the rejection may have another cause, and the model may not execute the example at all. The report retains the concrete syntax defect without inflating it into an explanation for all of Terra's ACE limitations.

## Availability, applicability, and mathematical progress are different

An object lookup establishes whether Rocq knows a name in an environment. A local conversion check establishes whether a specific representation change is accepted at a state. A successful tactic transition may leave important goals open. A completed theorem requires all obligations to be discharged. The applicability and checked-change studies explicitly measure different steps along that ladder.[^applicability], [^change]

The local applicability guard rejected some valid separate-sentence suffixes before kernel checking. Calling those failures “Rocq rejected the proof” would be inaccurate. Conversely, a kernel-accepted syntax repair on an incomplete induction does not demonstrate a useful mathematical bridge. The full coverage cycle includes both accepted repairs that still fail to finish and solve differences in cells without repair exposure.

Useful diagnostics should therefore state the exact observation: grammar accepted, conversion verified, original obligation discharged, proof completed, or cost-qualified solve. Generic fields named `solved_a` in a local analysis can mean correct applicability; they must not be relabeled as theorem solves when copied into a report.

## Empty focused goals do not mean a finished proof

A proof state can have no currently focused goals while unfocused or existential obligations remain. The attribution audit reproduced cases where `Qed` reported incompleteness despite an empty exported goal list. Bounded goal pagination alone could not reveal obligations outside that list. The later visibility interface exposes additional state under the same resource limits.[^attribution], [^visibility]

This is a real observability defect. It can make a model repeatedly try to finish a proof that still has hidden obligations. It does not mean every incomplete proof was caused by hidden goals. The capacity audit is especially valuable because the best-looking feedback treatment never actually emitted the extra feedback in its apparently improved cells.

Success remains anchored to final verifier acceptance. A zero-goal inspection preview, a tool message suggesting completion, or a partially closed prefix must not substitute for that check. The mechanisms study's offline finalization probes retained this distinction and did not award unsupported successes.

## The response parser can prevent a good answer from becoming a candidate

The structured S/C/R arms suffered when multiple final-answer messages were concatenated before JSON parsing. Individually valid objects became an “extra data” error, and no candidate was returned to search. Thirty-three of the fifty-one parsing failures even contained identical duplicated objects.[^mechanisms]

The v2 adapter's last-final-message rule repairs the local contract without silently splicing malformed JSON or selecting an earlier convenient answer. A saved final suffix closes one training theorem offline after the correction. This demonstrates that the parser hid at least one useful already-paid continuation; it does not justify rescoring every parser failure as a solve.

The thesis should report the operational result and the confound together. An implementation that fails before candidate delivery has underperformed in practice. The same experiment gives weak evidence about the underlying usefulness of a correctly delivered continuation mechanism. The corrected adapter still needs its own outcome evidence if a future study chooses to evaluate it.

## History compaction can erase the information that prevents repeated work

The H arm reduces context size yet creates long, repetitive tool histories. Five unsolved training cells submit no proof at all, despite 46, 46, 51, 64, and 64 model requests. Several repeatedly rediscover facts through tools. Historical counterparts made far fewer exact repeats and often submitted actual proof candidates.[^coveragecycle]

This exposes the difference between **per-request cost** and **total search cost**. A shorter prompt can make one request cheaper while causing more requests or destroying the state needed to avoid repeated searches. The relevant memory includes durable tool findings, known failed attempts, verified prefixes, and a route back to proof submission, not merely a compressed transcript length.

The fifty-thousand-scale compaction event count is also not a model-request count. Strategy reification and replay duplicate logging and rendering. Events need deduplication or linkage to actual dispatch before they can support a spend claim. Treating every debug event as a fresh paid request would exaggerate both cost and intervention exposure.

## Concrete persistent mathematical and formalization barriers

The continuation case appendix gives several useful training examples. Luna's AM–GM no-book path repeatedly submits an introduction prefix while leaving the product bound itself unproved. Its extended path accumulates fifty-four incomplete-proof errors and fifty-seven repeated-error attempts over seventy-nine model completions. The missing mathematical argument is visible; a hidden-goal explanation is insufficient.[^capacity]

On `imo_1967_p3`, incomplete product-divisibility induction persists even for Terra. One path reaches the need for an existential multiplier for the successor product, then repeats incomplete construction. This suggests a substantial proof-planning barrier under the current search policy. Because the next request is still money-denied, it does not isolate unrestricted model capability.

On `amc12a_2020_p13`, Terra without a book makes a useful logarithmic reduction and reaches a polynomial identity, but gets stuck on cast normalization and positivity involving `INR 2`. Terra with the corrected book later solves with more money. This is a different failure from not knowing the informal mathematical route: the remaining difficulty is finishing a formal library argument.

On `amc12b_2002_p11`, Luna reaches a small `prime 17` endpoint but leaves a coprimality or focus obligation unfinished. On `mathd_numbertheory_629`, one Luna book-conditioned path has repeated prover-crash-labelled checks and an opaque least-common-multiple equation that the final arithmetic tactic does not exploit. Another Luna context solves the task. These examples discourage blanket claims that a theorem is “beyond Luna” based on one sampled path.

## Budget reservation is a control policy, not a measure of actual effort

A request can be declined with money still available because the controller reserves a whole possible response plus a conservative context/transport bound. In the continuation records, one Luna path has about $0.085742 remaining but needs an estimated $0.086368 for its next request. A Terra path has about $0.798745 remaining against an estimate of $0.813446.[^capacity]

These are reproduced admission decisions, not billing overshoots. Increasing verifier allowance cannot help a request denied on money. More accurate reservations might recover useful opportunity, but that must be investigated without silently weakening the campaign's financial ceiling. The existing hint #131 concerns the conservatism of these bounds.

The earlier seven-versus-sixty-second typed-limit defect is more direct: the code reserved a different allowance from the requested one. It illustrates why typed configuration values must survive serialization and policy plumbing intact. A beautiful high-level budget abstraction does not exempt its adapter from concrete tests of what is reserved and charged.

## Resource errors are not all platform failures

A running cell may receive an out-of-memory tool response, lose a Rocq connection, restart the verifier, and later finish as a recorded unsolved outcome. That is compatible with a report saying there were zero launcher-level failed cells. Similarly, sixteen `prover-crash` labels inside one diagnostic history are not sixteen independent platform-failed episodes.[^attribution], [^capacity]

The capacity study carries one genuine API `invalid_prompt` failure into its final panel. Its paid prefix remains in cost, and there is no retry to replace the failed trajectory. Keeping it in the denominator protects against an optimistic analysis that silently removes the difficult or inconvenient cells.

Infrastructure improvements remain substantial achievements. Private warm Rocq servers, stable augmented paths, reply and time limits, prefix/check memoization, supervised attempts, and stream-slot coordination made the experiments more practical. These changes also alter conditions across historical runs. Prompt replay and bridge parity answer different reproducibility questions; neither should be claimed merely because an aggregate test suite passes.[^platform]

Two historical microbenchmarks give the scale of particular improvements: a stable warm prover reduced a measured interaction from roughly 450–850 ms to 2–3 ms, and avoiding repeated status scans reduced a 240-configuration scan from 15.9 seconds to roughly 4 ms. These are measurements of specific local operations, not end-to-end theorem-proving speedups or API bill savings. The same performance investigation found substantial stream-slot waiting, which limits how directly a local optimization translates into completed experiments.[^platform]

## Reporting mistakes can manufacture an effect

Several corrections are especially relevant to an LLM-assisted research workflow. A fixed-prefix result reader can mistake embedded old evidence for the current outcome. A taxonomy regex can miss a line-wrapped “current environment” error. A grouped report can blend treatment arms, or count only completed results and drop platform failures. A cost table can silently use a prefix-matched wrong model tariff. Each problem changes the evidence before a statistical test even begins.[^replication], [^v5], [^polish], [^pricing]

The tariff problem actually occurred in the pre-ACE history: a model name fell back to a shorter model-family prefix, and the recorded correction changed an older 514-configuration subtotal from $17.36 to $30.32. The memory explicitly says the gpt-5.6 runs were unaffected. The local exact-name guard and dated registry address this failure mode; this retrospective does not add that historical correction to the separate campaign-receipt subtotal or run the global repricing command while testX is closed.[^pricingguard]

The recent capacity report also corrected a derived failed-cell verifier-time field that omitted a Compute charge. The authoritative files have a `_v2` suffix; original hashes and the correction remain preserved. The costs and numerical verdicts did not change. A report should use the corrected field while explaining what changed, rather than silently overwriting the original history.[^capacity]

Two interpretation mistakes deserve equal emphasis. The rendering-2 advantage on one book was generalized and then retracted when another book reversed it. The profitable-looking selection pilot was initially stopped solely because it missed a +2-solve gate, despite a useful smaller gain and saving. The first lesson is to bound a claim by the observed treatment; the second is to distinguish a statistical or preregistered conclusion from an informed decision to buy a bounded follow-up.[^cycles], [^judgment]

## Access and provenance incidents

Earlier development-only work accidentally invoked a status command whose import chain loaded the closed testX partition. The incident was documented; a later attribution wrap-up repeated the status-command mistake, and a maintenance-search exposure was also recorded. The corrections distinguish partition-list access from outcome use. They should not be erased by a later statement that the numerical analysis used development data only.[^incidents]

The present retrospective uses explicit source lists and the development-only guard, and does not run the global partition, repricing, or Ladon-status commands that can cross that boundary. Inaccessible mixed documents are listed as excluded. This reduces the completeness of the historical narrative, but preserves the research boundary you chose to keep.

## A correction register for future writing

| Tempting claim | Evidence-supported formulation |
|---|---|
| “ACE does not work.” | Several tested variants did not establish a coverage benefit; recent matched Luna evidence is promising but inconclusive. |
| “Bounded ACE preserves quality.” | It achieved a large cost saving with three fewer solves in the original comparison; the trade-off was accepted. |
| “There was no non-ACE X baseline.” | Earlier X baselines existed; the missing comparison was the current bounded program with ACE removed. |
| “Terra unlocks ACE.” | Terra helps some proofs, but the full same-book crossover does not show a larger marginal ACE gain. |
| “ACE reduces reasoning cost.” | It lowers some recorded bills; cache discounts can reverse the token-cost interpretation. |
| “The feedback patch caused six solves.” | The best-looking feedback arm did not expose the added feedback in the relevant cells. |
| “Grounding makes the book correct.” | Reference existence is weaker than valid snippets, local applicability, or causal usefulness. |
| “Fewer tokens means cheaper search.” | Compaction reduced context while increasing repetition and total work in the tested arm. |
| “The model hit its intrinsic ceiling.” | The residual continuations remained budget-censored; unrestricted capability was not measured. |
| “All old runs replay exactly.” | Some historical chains drifted; observed-answer replay differs from full transport/admission replay. |
| “The corrected parser would solve all failed cells.” | One saved continuation closes offline; total corrected-arm coverage is unmeasured. |
| “Eighty cells means eighty independent problems.” | Repeated seeds must be clustered within forty theorems and related families. |

# What this means for the thesis

## Contributions that are already defensible

The strongest implemented contribution is a working, instrumented Rocq proving application in which context adaptation and resource control can be varied explicitly. The project has built and evaluated a persistent advice pipeline, maintained frozen artifacts, explored several learning and delivery mechanisms, and developed much better accounting for what a proof attempt actually consumes. These are concrete software and experimental contributions.[^implementation], [^capacity]

The bounded campaign supplies a clear cost/coverage result. The later studies add a richer account of why the frontier is difficult to improve: advice can prevent inexpensive local mistakes without solving the expensive residual mathematical task; conservative admission can terminate useful search; and the evidence shown to a reflector or prover can omit information that matters. A thesis can make these findings valuable by stating the precise conditions under which they were observed.

The latest controlled ACE removal is another useful contribution. It identifies a modest positive Luna validation observation under a matched program, separates it from model scaling, and shows that its recorded cost saving depends on cached-input billing. The full crossover and matched creator jobs then test explanations that a simple own-book comparison cannot separate. The result is a more careful account than either declaring ACE a universal success or writing off the whole idea.

Finally, the correction history itself supports a methodological contribution if presented analytically. Missing terminal evidence, duplicate final-answer parsing, hidden obligations, and exposure-free apparent gains are specific failure modes of evaluating LLM applications. Their diagnosis required tracing observations through the program, not merely asking an LLM to explain a table of scores.

## Claims that remain unestablished

A large general ACE coverage improvement on independent Rocq tasks has not been established by the accessible evidence. ValidationX is development data, and protected outcomes remain outside this report. There is no basis for turning many small, repeatedly selected positive differences into an independent aggregate confirmation.

Nor has the project established that a stronger writer reliably creates a more useful book, that a stronger solver reliably obtains a larger marginal ACE benefit, or that the remaining failures reveal an intrinsic model ceiling. The continuation study is explicitly budget-censored, and its selected eight-case panel is diagnostic rather than representative.

The original proposal also includes an empirical comparison of Delphyne's simplicity and extensibility against a monolithic alternative. Localized interventions demonstrate useful modularity, but they do not alone prove lower engineering effort, better scalability, or simpler code than a comparable alternative implementation. Those claims need explicit measures and an appropriate comparator, or should be stated as an implementation case study rather than a controlled comparative result.[^proposal], [^delphyne]

## The most informative next questions

The following are research directions grounded in existing findings, not additional experiments performed for this report or authorization to spend an unused ceiling.

**First, make the learning evidence complete.** Hint #130 concerns the terminal accepted proof and assistance receipt. A useful investigation would establish that every successful training example provides the actual executed witness and distinguishes it from unexecuted proposed text. This directly addresses a demonstrated source of incorrect lessons, and can begin with offline evidence validation.

**Second, measure admission conservatism.** Hint #131 concerns the difference between reserved next-request cost and actual outcomes under a bounded controller. The question is whether a calibrated, still-safe bound recovers useful opportunity. A convincing result must preserve financial accounting, identify the newly admitted requests, and compare coverage and total spend. Simply increasing every ceiling would confound the intended mechanism with additional resource availability.

**Third, evaluate already-corrected interfaces before rejecting the mechanism.** The v2 final-answer adapter has offline evidence but no clean paid full-panel benchmark in its original campaign. The same caution applies to structured recovery and certain continuation contracts. An affordable follow-up should be justified by mechanism reach and the value of information, while retaining the earlier operational losses in the record.[^mechanisms]

**Fourth, preserve useful state under context limits.** The H diagnosis suggests keeping durable tool findings, verified prefixes, and a reliable final-submission opportunity. The existing compaction result is a reason to study what memory retains, not to assume that either unlimited history or arbitrary shortening is always preferable.[^coveragecycle]

**Fifth, separate exposure from outcomes in every future evaluation.** Each intervention should have an auditable event showing when it actually affected a dispatched request or executed check. The primary theorem-level outcome remains important; exposure data makes its causal interpretation less speculative. This is particularly relevant for demonstration selection, feedback visibility, and recovery controls.

These priorities can be discussed without reopening a protected dataset. If the thesis needs a new independent evaluation, its design, eligibility, and selection rules are a separate research decision. The present report leaves that decision open rather than converting old protected failures into a new development curriculum.

## An advisor-ready account

“We implemented ACE as persistent, structured proof advice learned from Rocq execution feedback. We tested offline and online adaptation, reflection and curation changes, stronger writers, selective advice delivery, and several budget and recovery mechanisms. Early coverage effects were small; the clearest practical win was a bounded controller that substantially reduced cost while sacrificing some coverage. The recent matched ablation gives a promising Luna ACE comparison, but the effect remains uncertain and its bill saving depends on cached-input pricing.”

“We also learned why several plausible improvements did not transfer. Some interventions were not exposed where gains occurred, some were confounded by a response parser, and some repaired syntax without resolving the mathematical proof. Exact continuations show that Terra can recover additional hard cases with more money, but the residual failures remain budget-censored. The thesis contribution is therefore a controlled study of the interaction between learned context, verifier evidence, and resource-aware proof search, with explicit limits on generalization.”

The most useful advisor decisions are which cost/coverage trade-offs the thesis should emphasize, how strongly to frame the implementation contribution versus the ACE hypothesis, and whether any additional independent evaluation is necessary. There is already enough material for a substantive methods and discussion chapter; the report should make that material accessible without concealing the negative findings.

# Reading and evidence guide

## External references

Read the ACE paper's algorithm and prompts alongside the local implementation chapter. The paper's long-context, non-Rocq tasks are useful for understanding the mechanism, while its effect sizes are not local performance targets. Its sections on reflection quality, incremental updates, and serving costs help formulate hypotheses that the Omphalos studies can actually test.[^ace]

Read the Delphyne paper for the separation of strategies, policies, and demonstrations. Then follow one local query and one budgeted Compute through the code. That combination makes the architecture concrete and helps distinguish a framework capability from a claim that has been benchmarked in Omphalos.[^delphyne]

The MiniF2F-in-Rocq paper explains the benchmark translation. Hilbert explains the original recursive informal/formal motivation. Numina-Lean-Agent provides another primary example of an agentic formal-mathematics system, useful for positioning the engineering problem without pooling incompatible benchmark scores.[^minif2f], [^hilbert], [^numina]

Two other supplied papers are particularly relevant. **NLIR** introduces Pétanque and studies natural-language intermediate representations for interaction with Coq, connecting directly to the bridge beneath Omphalos. **Tacq** studies context-aware next-tactic recommendation in Rocq, including extracting notations and dependencies. Tacq is useful when thinking about whether a failure reflects missing environment context rather than a missing general proof strategy. Neither paper's benchmark numbers are pooled with this study.[^nlir], [^tacq]

For neighboring context-learning methods, Reflexion studies verbal feedback and memory rather than weight updates, while GEPA studies reflective prompt evolution. They help distinguish “reflection is useful somewhere” from “this particular persistent book improves this bounded proof program.” Neither is evidence for an unmeasured Omphalos gain. Their relevance here is conceptual and methodological.[^reflexion], [^gepa]

## Internal evidence to read first

Start with the attribution `RESULTS.md` and `LINEAGE.md` to understand which baseline was actually compared. Continue with the capacity `RESULTS.md` and corrected `_v2` numerical reports for the crossover, source-quality audit, and exact continuations. The bounded acceptance record explains why a failed original gate can coexist with an explicitly accepted practical result.[^attribution], [^lineage], [^capacity], [^bounded]

For the mistake analysis, the most informative records are the terminal-evidence and reducer-snippet witnesses, the mechanisms parser audit, and the coverage-cycle training diagnoses. The large case and creator appendices preserve far more detail than belongs in the main narrative. Their structures and section inventories are indexed in the companion source catalogue; representative causal cases are examined in this report rather than claiming that every raw model turn was individually reviewed.

For implementation, follow the ACE query classes, playbook merge/store, adaptation variants, bounded strategy, operation budgets, and replay adapter. The companion implementation index lists classes and functions without importing experiment drivers. The workbook and CSVs link aggregate numbers back to the permitted records used by the offline builder.

## Interpreting the appendices

The historical appendix includes incomplete registrations and superseded directories so that they do not disappear from the story. A blank cost or an “incomplete” status is not a zero-cost result or a negative theorem outcome. Complete archived token totals are distinguished from recent receipt-reconciled campaign bills. The same reference cell can appear in more than one comparison without representing another paid execution.

The source catalogue uses explicit review statuses. Numerical inputs were read and checked by the reporting pipeline. Narrative sources were used for interpretation. Implementation files can be structurally indexed and selectively inspected without a claim of a line-by-line code review. Excluded mixed and protected artifacts are identified by path and reason without opening their content. This is the practical meaning of an exhaustive retrospective within the retained access boundary.

[^ace]: Qizheng Zhang et al. *Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models*. ICLR 2026, arXiv:2510.04618v3, March 29, 2026. [Paper](https://arxiv.org/abs/2510.04618v3); [authors' implementation](https://github.com/ace-agent/ace). Algorithm and prompts also inspected in the supplied local PDF.
[^implementation]: Omphalos, [ACE strategy and queries](../../prove_ace.py), snapshot September 12, 2026. Generator integration, example selection, reflection and curation contracts.
[^proposal]: Guille, [original thesis proposal](../../docs/thesis_proposal.md). Planning document; its aspirational criteria are not completed experimental claims.
[^delphyne]: Jonathan Laurent and André Platzer. *Oracular Programming: A Modular Foundation for Building LLM-Enabled Software*. arXiv:2502.05310v5, March 18, 2026. [Paper](https://arxiv.org/abs/2502.05310v5).
[^minif2f]: Jules Viennot, Guillaume Baudart, Emilio Jesús Gallego Arias, and Marc Lelarge. *MiniF2F in Rocq: Automatic Translation Between Proof Assistants—A Case Study*. arXiv:2503.04763v2, November 24, 2025. [Paper](https://arxiv.org/abs/2503.04763v2); supplied local v2 PDF.
[^hilbert]: Sumanth Varambally, Thomas Voice, Yanchao Sun, Zhifeng Chen, Rose Yu, and Ke Ye. *Hilbert: Recursively Building Formal Proofs with Informal Reasoning*. arXiv:2509.22819v2, March 16, 2026. [Paper](https://arxiv.org/abs/2509.22819v2).
[^bridge]: Omphalos, [Rocq bridge and assisted verification](../../runtime/pytanque_utils.py), snapshot September 12, 2026.
[^adaptation]: Omphalos, [ACE adaptation driver and versioned variants](../../experiments/ace/ace_adaptation.py), inspected statically. Historical runtime contracts are described by the corresponding frozen configurations.
[^playbook]: Omphalos, [playbook representation and deterministic updates](../../ace/ace_playbook.py), with [deduplication implementations](../../ace/ace_dedup.py).
[^curator]: Omphalos, [versioned curator prompt](../../prompts/ace/adaptation/CuratePlaybook.system.jinja), including evidence-first contract 4 and YAML block-scalar requirements.
[^store]: Omphalos, [content-addressed playbook storage](../../ace/ace_store.py).
[^evidence]: Omphalos, [failure digests and reference grounding](../../ace/ace_evidence.py). Reference existence and transport failures have distinct verdicts.
[^grounded]: Omphalos, [bounded/focused strategy](../../prove_grounded.py) and [checked evidence types](../../ace/ace_grounded.py). Actual evaluated switches come from campaign configs.
[^budgets]: Omphalos, [operation limits](../../runtime/tool_budget.py), [control policies](../../runtime/grounded_control.py), and [campaign reservations](../../runtime/campaign_budget.py).
[^replay]: Omphalos, [exact transport/admission replay adapter](../../runtime/replay_admission.py), and capacity [artifact/reproduction guide](../../experiments/campaigns/ace_capacity_20260912/ARTIFACTS.md).
[^visibility]: Omphalos, [version-2 goal visibility](../../ace/ace_goal_visibility.py), with the capacity [exposure audit](../../experiments/campaigns/ace_capacity_20260912/causal_exposure_audit.json).
[^snippets]: Omphalos, [source-bound snippet preservation](../../ace/ace_verified_snippets.py), and capacity [fresh reducer snippet check](../../experiments/campaigns/ace_capacity_20260912/fresh_reducer_snippet_check.json).
[^governance]: Omphalos, [canonical project instructions](../../AGENTS.md), including measurement discipline, current configurations, and the September 11 testX closure. Governance only; protected outcomes are excluded.
[^measurement]: Omphalos, [measurement convention](../../memory/omphalos-measurement-floor.md) and [family-clustered analysis implementation](../../tools/analysis/paired_evaluation.py).
[^responses]: Omphalos, [decomposed Responses API study and retractions](../../memory/omphalos-responses-api-decomposed.md), August 13–24, 2026. Historical complete-case conventions in this record are superseded by the current denominator rule.
[^pricingguard]: Omphalos, [historical pricing correction and exact-name guard](../../memory/omphalos-pricing-guard.md), August 10–17, 2026. File-location references in this memory predate the current runtime/tools layout.
[^judgment]: Omphalos, [experimental-judgment correction](../../memory/omphalos-experiment-judgment.md), September 10–11, 2026.
[^replication]: Omphalos, [initial ACE replication memory](../../memory/omphalos-ace-replication.md), August 24, 2026. This predates testX; numerical discussion here uses original validation evidence only.
[^v5]: Omphalos, [v5 diagnosis, results, and provenance deviations](../../memory/omphalos-ace-v5.md), September 2, 2026.
[^cycles]: Omphalos, [hint-on-error and stall-cycle record](../../memory/omphalos-ace-hint-on-error.md), September 5–8, 2026, including the rendering-effect retraction.
[^stall]: Omphalos, [pure stall rules](../../runtime/stall.py) and [live stall strategy](../../prove_stall.py).
[^archive]: This retrospective's [historical cell export](data/archive_cells.csv) and [per-seed summaries](data/archive_summary.csv), rebuilt from explicitly permitted development manifests and result headers. Source hashes appear in [the numerical source inventory](data/source_inputs.json).
[^reviewdev]: Omphalos, [review development manifest](../../experiments/output/ace_review_development/experiment.yaml), September 8, 2026. Only this development archive is used; protected review stages and mixed final reports remain excluded.
[^bounded]: Omphalos, [bounded campaign report](../../experiments/campaigns/ace_bounded_20260908/final_report.json), [acceptance record](../../experiments/campaigns/ace_bounded_20260908/acceptance.json), and [follow-up](../../experiments/campaigns/ace_bounded_20260908/FOLLOW_UP.md), executed September 9, 2026.
[^control]: Omphalos, [control-cycle report](../../experiments/campaigns/ace_control_cycle_20260909/final_report.json) and [corrected project memory](../../memory/omphalos-ace-control-cycle.md), September 9, 2026.
[^polish]: Omphalos, [polish final report](../../experiments/campaigns/ace_polish_20260909/final_report.json), [follow-up audit](../../experiments/campaigns/ace_polish_20260909/FOLLOW_UP.md), and [retention decision](../../experiments/campaigns/ace_polish_20260909/retention.json), September 9, 2026.
[^applicability]: Omphalos, [applicability final report](../../experiments/campaigns/ace_applicability_20260909/final_report.json) and [follow-up](../../experiments/campaigns/ace_applicability_20260909/FOLLOW_UP.md), September 9, 2026.
[^change]: Omphalos, [checked-change report](../../experiments/campaigns/change_control_20260910/final_report.json) and [follow-up](../../experiments/campaigns/change_control_20260910/FOLLOW_UP.md), September 10, 2026.
[^effort]: Omphalos, [Terra-high diagnostic](../../experiments/campaigns/terra_high_20260910/FOLLOW_UP.md), [Luna-high diagnostic](../../experiments/campaigns/luna_high_20260910/FOLLOW_UP.md), and [Luna xhigh/max diagnostic](../../experiments/campaigns/luna_upper_20260910/FOLLOW_UP.md), September 10, 2026.
[^models]: Omphalos, [model-suite results](../../experiments/campaigns/ace_models_20260910/RESULTS.md), September 10, 2026.
[^contenders]: Omphalos, [two-contender results](../../experiments/campaigns/ace_contenders_20260910/RESULTS.md) and [final metrics](../../experiments/campaigns/ace_contenders_20260910/final_report.json), September 10, 2026.
[^mechanisms]: Omphalos, [mechanisms results](../../experiments/campaigns/ace_mechanisms_20260910/RESULTS.md), [structured parser audit](../../experiments/campaigns/ace_mechanisms_20260910/structured_parse_audit.json), and [offline continuation probe](../../experiments/campaigns/ace_mechanisms_20260910/offline_continuation_probe.json), September 10, 2026.
[^coverage]: Omphalos, fixed-book coverage [training report](../../experiments/campaigns/coverage_20260911/training_report.json) and [validation report](../../experiments/campaigns/coverage_20260911/validation_report.json), September 11, 2026. Mixed campaign artifacts and closed-stage data are excluded.
[^coveragecycle]: Omphalos, [four-treatment coverage results](../../experiments/campaigns/coverage_cycle_20260911/RESULTS.md), [training report](../../experiments/campaigns/coverage_cycle_20260911/training_report.json), [validation report](../../experiments/campaigns/coverage_cycle_20260911/validation_report.json), and arm-specific training diagnoses, September 11, 2026.
[^lineage]: Omphalos, [baseline lineage](../../experiments/campaigns/ace_attribution_20260912/LINEAGE.md) and [historical-to-flagship comparison](../../experiments/campaigns/ace_attribution_20260912/historical_to_flagship.json), September 12, 2026.
[^attribution]: Omphalos, [attribution results](../../experiments/campaigns/ace_attribution_20260912/RESULTS.md), [complete report](../../experiments/campaigns/ace_attribution_20260912/complete_report.json), and frozen protocol, September 12, 2026.
[^capacity]: Omphalos, [capacity follow-up results](../../experiments/campaigns/ace_capacity_20260912/RESULTS.md), [crossover data](../../experiments/campaigns/ace_capacity_20260912/crossover_report.json), and [corrected mechanism data](../../experiments/campaigns/ace_capacity_20260912/mechanism_report_v2.json), September 12, 2026.
[^creator]: Omphalos, capacity [matched creator audit](../../experiments/campaigns/ace_capacity_20260912/creator_quality.json), [contextual reference audit](../../experiments/campaigns/ace_capacity_20260912/creator_contextual_audit.json), and [complete creator appendix](../../experiments/campaigns/ace_capacity_20260912/CREATOR_APPENDIX.md), September 12, 2026.
[^terminal]: Omphalos, [terminal-evidence audit](../../experiments/campaigns/ace_capacity_20260912/creator_terminal_evidence.json) and [Reflector terminal witness](../../experiments/campaigns/ace_capacity_20260912/reflector_terminal_witness.json), September 12, 2026.
[^preparation]: Omphalos, [Luna preparation accounting](../../experiments/campaigns/ace_attribution_20260912/luna_preparation_accounting.json), [Terra preparation accounting](../../experiments/campaigns/ace_attribution_20260912/training_accounting.json), and [training evolution](../../experiments/campaigns/ace_attribution_20260912/training_evolution.json).
[^pricing]: Omphalos, [dated pricing registry](../../runtime/model_registry.py) and [dated-pricing convention](../../memory/omphalos-dated-pricing.md). This report uses recorded/local historical prices, not a claim about a current provider price offer.
[^platform]: Omphalos, [platform-rebuild record](../../memory/omphalos-platform-rebuild.md), [performance record](../../memory/omphalos-perf-pass.md), [Rocq server implementation](../../runtime/rocq_server.py), and [supervised launcher](../../experiments/common/omphalos_launch.py).
[^incidents]: Omphalos, [coverage access incident](../../experiments/campaigns/coverage_cycle_20260911/access_incident.json), capacity [closure correction](../../experiments/campaigns/ace_capacity_20260912/closure_correction.json), and [maintenance exposure note](../../experiments/campaigns/ace_capacity_20260912/closure_maintenance_note.json). These are incident records, not protected outcome inputs.
[^numina]: Junqi Liu et al. *Numina-Lean-Agent: An Open and General Agentic Reasoning System for Formal Mathematics*. arXiv:2601.14027, January 20, 2026. [Paper](https://arxiv.org/abs/2601.14027).
[^reflexion]: Noah Shinn et al. *Reflexion: Language Agents with Verbal Reinforcement Learning*. arXiv:2303.11366, 2023. [Paper](https://arxiv.org/abs/2303.11366).
[^gepa]: Lakshya A. Agrawal et al. *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*. arXiv:2507.19457, 2025. [Paper](https://arxiv.org/abs/2507.19457).
[^nlir]: Laetitia Teodorescu, Guillaume Baudart, Emilio Jesús Gallego Arias, and Marc Lelarge. *NLIR: Natural Language Intermediate Representation for Mechanized Theorem Proving*. MathAI at NeurIPS 2024; HAL deposit January 14, 2025. [Paper](https://hal.science/hal-04886208v1); supplied local PDF.
[^tacq]: Jules Viennot, Guillaume Baudart, Emilio Jesús Gallego Arias, Marc Lelarge, and Theo Stoskopf. *Tacq—Context Aware Tactic Recommendation for Rocq*. JFLA 2026; HAL deposit December 21, 2025. [Paper](https://hal.science/hal-05428141v1); supplied local PDF.
