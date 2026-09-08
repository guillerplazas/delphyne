# ACE review — 2026-09-08

The fresh confirmation does **not establish a substantial ACE solve-rate
improvement**: x3 achieved 121/176 budget-qualified solves versus baseline
118/176, a +1.70-point difference (clustered p=0.581), at 4.3% higher cost.
The new iterative-repair artifacts did not beat x3 in development. The
review also corrects measurement rules, updates ACE launch concurrency,
and provides complete billing and reproducible evaluation evidence.

## Follow-up diagnosis from existing data — 2026-09-08

**The previous campaign was too large for the demonstrated mechanism.**
The user reports roughly €200 total including Codex. The $39.02 ledger
covers experiment API liability only; it is not the total cost of this
work. Assistant analysis, repeated narration and supervision were outside
that ledger. Future decisions must budget those costs together, and a
weak mechanism should be investigated on a small set before another full
comparison. The recommendations below are documentation only: no new
experiment, verifier execution, test suite or implementation was run for
this follow-up.

### What the paid trajectories actually show

This audit reads the **320 existing development caches**, keyed by full
problem/arm/model/seed identity, and their frozen
[development cell records](experiments/campaigns/ace_review_20260908/development_cells.json).
It uses the last attempt's distinct cached verifier results; caches are
not complete execution event logs, so repeated cache hits are not counted
as new checks. Five preserved earlier-attempt caches are excluded from
this failure taxonomy; their charges remain in the financial results.
Confirmation is used at aggregate level, without mining its proof
trajectories. Counts below are descriptive, not independent observations
or additional significance tests.

| Recorded rejected checks | Baseline | x3 | Repair seed0 | Repair seed1 |
|---|---:|---:|---:|---:|
| All rejections | 1,081 | 1,061 | 1,092 | 1,173 |
| Open goals at `Qed` | 324 | 293 | 387 | 539 |
| Prover/resource errors | 173 | 163 | 232 | 193 |
| Arithmetic automation cannot find a witness | 90 | 58 | 72 | 67 |
| Syntax errors | 83 | 77 | 64 | 67 |
| Unknown identifiers | 67 | 55 | 74 | 54 |
| Type, unification or rewrite mismatch | 117 | 117 | 108 | 91 |
| Focus/bullet errors | 59 | 49 | 37 | 29 |

The displayed categories do not exhaust all rejections. The legacy
`prover-crash` category includes stack overflows and transport errors;
it does not mean that every recorded event killed a process. Likewise,
`Cannot find witness` also occurs with `lia`, so it should not be read
as exclusively a nonlinear-arithmetic failure.

**The dominant failure is lack of useful progress after feedback.** The
same failing tactic, error text, verified prefix and remaining goals
reappear within a cell on **45.1% / 45.7% / 49.3% / 56.5%** of the four
arms' rejected cached checks. These are repeated feedback fingerprints,
not necessarily identical complete scripts: changing an unexecuted tail
can leave exactly the same failure. The existing system prompt already
asks the prover to change its approach after repeated failure. More prose
has not made that instruction a reliable control mechanism.

Among ultimately unsolved cells, the final recorded rejection was an
incomplete proof in **16/28 baseline, 11/23 x3, 15/25 repair0 and 16/26
repair1** cells. Unknown names and syntax are common, but improving them
alone does not necessarily cross the mathematical obstacle. Unsolved
cells account for **82.3%, 71.2%, 72.5% and 82.2%** of each arm's total
charged cost. Even on the 50 cells that both baseline and x3 solve,
x3 used 382 versus 388 HTTP attempts but cost $0.49068 versus $0.47970.
This conditioned subset is diagnostic only; it is not the primary paired
cost comparison or a causal estimate of an individual bullet's effect.

Concrete recurring mistakes include:

- **Unavailable names:** baseline proposed `norm_num` in 18 distinct
  cells and `omega` in 10; x3 still did so in 15 and 5. Other examples
  include `interval_cases`, `ring_nf` and guessed `Nat.*` lemma names.
  Resolve availability in the actual imported environment; do not blindly
  replace a foreign tactic with `lia` regardless of the goal's type.
- **Wrong domain or normal form:** a `nat` index used where `Z` is
  expected; rewriting with a lemma whose syntactic target is absent;
  using `ring` on a non-ring equation; asking `lia` to establish facts
  about `Int_part` without the necessary bridging lemmas.
- **Proof structure:** closing a brace while its subgoal remains open,
  changing bullet levels before finishing the current branch, or reaching
  `Qed` with a missing case. These require tracking the current proof
  state, not a global mathematical slogan.
- **Resource pathology:** repeated stack overflows at `Qed` and large
  goal exports. The active baseline cache contains feedback with 173
  remaining goals; repair0 has a feedback record of about 3.61 MB. The
  separate 13.27-million-character API failure was in an earlier attempt.

### ACE-specific defects and what to change conceptually

**1. Validate learned claims before promoting them to advice.** There is
a concrete defect in the new seed1 playbook: `rocq-00007` recommends
finishing real arithmetic with `lra` **or `norm_num`**, although the
recorded runtime rejects `norm_num`. The clause appears by
[checkpoint 12](experiments/playbooks/ace_adaptation_review-repair-s1/playbook_step_12.yaml)
and survives in the [final seed1 artifact](experiments/playbooks/ace_review_repair_s1.yaml),
with helpful/harmful counters **8/1**. It was mentioned in 23 development
assistant messages. A partly useful bullet can accumulate positive tags
while retaining an invalid clause. Citation and helpfulness are therefore
insufficient validation. This does not prove that this clause caused the
six seed1 `norm_num` errors, and seed1 was not deployed.

Proposed remedy: store smaller claims with their environment, applicability
conditions, supporting accepted transition and counterexample. Check
object availability using the existing `ace_evidence` grounding machinery,
then validate the actual tactic application in its recorded proof state.
`Locate` alone does not establish that a lemma has the required type or
that an application succeeds. Keep an unverified suggested proof separate
from executable guidance; allow abstention when no verified correction
exists. The earlier v5 grounding experiment was inconclusive, so restoring
that switch alone is not a demonstrated solution. The new issue is
**claim-level applicability and provenance**, including mixed valid/invalid
content inside one bullet.

**2. Separate incorrect proof steps from unavailable evidence.** The
[reflector prompt](prompts/ReflectOnTrajectory.system.jinja) currently says
a rejected step is wrong without exceptions. A timeout, stack overflow or
transport failure does not establish mathematical invalidity. Teaching
from those events as if Rocq had logically refuted a tactic can contaminate
the playbook. Return distinct outcomes for accepted steps, logical/type
rejections, incomplete proofs, resource exhaustion and unknown transport
results. The reflector should identify the first relevant failure and
state whether its proposed correction has actually been checked.

The [reference ACE loop](https://github.com/ace-agent/ace/blob/82709de050e1db6e6ef2f07bcb0393560b94992a/ace/ace.py)
regenerates after reflection and can use a known correct answer. Our
verifier-only setting is legitimate, but the new repairs recovered just
one failure across both runs. Before buying more repair episodes, compare
a failed training transition with an **already verified** successful
transition for the same local obstacle. Do not ask another free-form
reflection to manufacture evidence that is absent.

**3. Make advice influence a named decision, then measure that decision.**
x3 cited bullet IDs in only **62 of 1,745** recorded model messages, one
message in each of 62 cells. The
[instance prompt](prompts/ProposeProofScriptACE.instance.jinja) explicitly
asks for intended bullet IDs before the first action. This is an intent
signal, not a per-step application record. More required self-reporting
would add cost without proving causality.

Proposed remedy: attach the selected advice and its provenance to a
specific choice such as resolving an identifier, normalizing a cast,
choosing an induction invariant or selecting a structural opener. Record
the ensuing verified state change and cost. An environment-grounded
transition becomes a candidate Delphyne demonstration; an unsupported
reflection remains a hypothesis. Rank repeated defects by distinct
problems/families as well as total cost: baseline's 173 resource errors
occur in only 9 cells, while 67 unknown-name errors affect 34 cells.
Raw repetition counts alone can distort the curator's priorities.

**4. Compose reflection and repair as a Delphyne strategy.**
`reflect_on_trajectory` in [prove_ace.py](prove_ace.py) is already a
standalone strategy. The proposed change is to express the encompassing
adaptation cycle as a composed strategy, instead of coordinating its
steps principally in the experiment driver:

**Generate → verify → reflect on failure → repair → verify again.**

The strategy would pass structured feedback and expose reflection,
repair and alternative-plan choices; a repair is accepted only after
verification. Separate inner policies would select generator and
reflector models and allocate a shared budget across those choices.
This makes reflection part of Delphyne's recorded, inspectable decision
process and keeps resource allocation distinct from proof correctness.

Use Delphyne demos to teach the reflector to turn a failed trajectory and
its Rocq-verified training solution into a grounded reflection. Examples
should identify the failed step, explain the verified correction and
state its applicability conditions. The verified solution for the
**current training problem** should also be supplied as query input:
few-shot demonstrations teach how to reflect but do not supply that
problem's ground truth. Demonstration answers are examples, not a
substitute for checking the proposed repair with Rocq.

Start with offline adaptation, where verified training solutions can be
provided without exposing evaluation answers. Deployment can reuse the
resulting playbook without paying for reflection on every problem.
Runtime reflection could later be an optional, explicitly budgeted
choice. This architectural integration improves control and diagnosis;
it does not by itself establish better advice or higher solve rates.
This is a proposal only; no implementation or experiment is authorized
by recording it here.

### Additional Delphyne compositions not yet implemented

The curator, reducer, auditor and reference grounder already exist as
standalone strategies in [prove_ace.py](prove_ace.py). They do not need
to be recreated. The following proposals describe the missing composition
or behavior beyond those existing components.

| Unimplemented proposal | Existing foundation | Proposed Delphyne expression |
|---|---|---|
| **Validate advice before admission.** Check the actual claim in its supporting proof state, not merely whether its referenced names exist. | Typed curation deltas, `ground_references`, deterministic merging and the optional grounding gate already exist. | Compose proposal, availability checking, application verification and acceptance in a strategy. Use `Compute` for Rocq checks and explicit validation outcomes; accept only supported claims and distinguish rejection from unavailable evidence. |
| **Represent playbook evolution as explicit immutable state.** Carry the playbook and supporting evidence through the adaptation workflow. | The experiment driver already manages sequential updates, batches and checkpoints. | Use `iterate` over immutable state snapshots. Each speculative branch returns a proposed successor state; only the selected state is persisted. Preserve the existing batch-start snapshot semantics and resumability. |
| **Teach curator and auditor decisions through targeted demos.** Include justified additions, abstention when evidence is insufficient, and rejection or narrowing after a counterexample. | These roles are typed queries with few-shot policies; prompts already describe desirable behavior. | Add demonstrations attached to the relevant curation/audit query, grounded in recorded training evidence. A demonstration teaches a decision pattern; it does not replace application verification. |
| **Select advice at a specific proof decision.** Associate lessons with reference resolution, cast normalization or invariant selection. | Triggered injection, playbook IDs and example-selection machinery already exist. | Introduce focused typed queries where useful, with query-specific advice construction and matching demonstrations. Selecting playbook advice and selecting few-shot examples remain distinct operations. This extends the earlier retrieval proposal; it is not another insertion-location ablation. |
| **Budget the complete tool operation.** Bound verification and feedback generation, alongside model spending. | Verifier work already uses `Compute`; individual deadlines, goal caps, stream budget interfaces and the campaign ledger exist. | Add operation-level admission/accounting and propagate the remaining allowance through the tool handler. Policies control resource allocation; the strategy preserves proof obligations and distinguishes exhaustion from logical failure. Merely wrapping a function in `Compute` does not impose a budget. |

Prioritize **validated advice admission and whole-operation tool budgets**:
they address defects observed in the existing data. Moving the entire
learning loop into `iterate` is a lower-priority architectural change.
Keep cheap deterministic merging/filtering as ordinary Python. Keep
filesystem persistence, process supervision and the shared billing ledger
outside speculative search; composing strategies must not introduce
duplicate writes, lost updates or unaccounted spending. These remain
unimplemented recommendations, not new experiments or authorization to
refactor the pipeline.

### Delphyne and tooling: prioritized improvement ideas

These proposals retain Delphyne's separation of **strategy, policy and
demonstrations**, rather than putting every decision into the system
prompt. That separation and grounded examples are central to the
[Delphyne paper](https://arxiv.org/abs/2502.05310).

| Priority | Proposed change | Existing Delphyne/Omphalos connection | Evidence needed before broader evaluation |
|---|---|---|---|
| 1 | Detect repeated failed states and return to a useful choice point; preserve a verified prefix when repairing locally, or start a different structural plan when it is exhausted. | `stall.py` already extracts feedback states; `prove_stall.py` demonstrates a replayable stop decision. A parent strategy can expose opener/restart alternatives with `Branch`/`iterate`; a policy allocates one shared budget across them. | Use recorded prefixes first to measure which stops would lose known recoveries. A cached cutoff can estimate savings; it cannot reveal the outcome of an unrun restart. Do not lower the stall threshold blindly. |
| 2 | Put a budget on the **whole** verification/feedback operation and on what is rendered into the prompt. Return a small focused goal view with an explicit path to inspect omitted goals. | `dp.compute` isolates verifier work; `GoalCaps`, `_probe_goals`, `_cap_goals` and the existing server deadlines provide components. Add operation-level accounting around the tool handler, with settings in experiment/cache identity. | Preserve all raw goals and correctness checks; changing a goal view must not make unfinished goals count as solved. Measure automatic completions that would be lost before choosing bounds. |
| 3 | Resolve names and side conditions at the last verified proof state, instead of guessing from a generic global playbook. | `SearchRocq` in the current core toolset queries the initial environment. Existing `InspectAt` can query after a verified prefix; `Check`/`About` expose actual signatures. Use narrowly targeted tool routing, not a wholesale switch to the already-tested richer toolset. | Recorded unknown-name/type failures must become accepted local transitions on a few exposed cases; fewer lookup errors alone is not a solve-rate claim. |
| 4 | Turn useful ACE lessons into small, typed, state-specific queries and demonstrations: resolve reference, choose bridge, propose invariant, then verify. | Tagged `dp.branch` queries and existing example selection can attach an accepted or rejected demonstration to the relevant decision. `dp.interact` can retain a local repair conversation; parent search controls plan alternatives. | Extract examples from accepted training transitions already paid for. Check applicability and contamination before adding demonstrations; keep a record of which query and state they address. |
| 5 | Retrieve only relevant verified advice, and reset stale local history when a plan changes. | Existing trigger selection and playbook IDs are a starting point. Add type/goal-shape and verified-prefix conditions; keep full raw evidence outside the rendered `AnswerPrefix`. | Earlier hint-on-error and rendering changes did not reliably improve solves. A new retrieval scheme needs better verified coverage, not merely a different insertion location. |

The automatic prover work is useful as well as expensive: `auto_finished`
is recorded for **13/52 baseline and 17/57 x3** development successes.
Removing the automation battery would change what the prover can solve.
A per-RPC timeout does not bound `_probe_goals` across every goal and every
tactic; the missing control is at the complete operation. A smaller
rendered view must still retain all proof obligations for kernel checking.

The [context-engineering resource](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-degradation)
provides useful hypotheses about stale, conflicting and excessive context.
Here the evidence directly establishes oversized histories and API/resource
failures; it does **not** establish an exact token threshold at which
reasoning quality degrades. Use structured verified state and provenance
before adding model-written summaries. Any truncation, compression or
restart changes the policy and needs its own bounded assessment.

### Two measurement/tooling corrections before trusting more sweeps

**The older failure-analysis loader mislabels repeated cells.**
`tools/failure_analysis.py:load_run` builds `solved[bench_name]` from the
CSV. With multiple arms and seeds, later rows overwrite earlier outcomes.
Applied to this mixed development directory, that lookup assigns the
wrong solved/unsolved label to **16 of 320 cells**. Consequently it can
corrupt the split between recoverable errors and errors in failed runs.
This follow-up instead used full-name `development_cells.json` records;
the frozen campaign's paired inference already uses full cell identities
and is unaffected. Proposed fix only: use the shared cell-record reader
and explicit arm/seed keys throughout diagnostic tools, and distinguish
cached results from invocation events. No loader was changed here.

**Delphyne already has budget admission; the missing information matters.**
A precise correction to the earlier discussion: `Stream.with_budget`
and `spend_on` can enforce a hard bound when estimates are accurate.
The default `LLM.estimate_budget` estimates request/completion counts,
not dollars, and `_send_request` uses that estimate. The nominal dollar
overshoot is therefore not an inherent inability of Delphyne's stream
abstraction. A future adapter should supply conservative monetary
estimates through that interface and retain the external process-safe
ledger for cross-process liability and unknown charges. Local verifier
CPU work additionally needs its own admission/accounting mechanism; the
current `just_compute` path does not turn a 70-minute operation into
budgeted model requests. See the local source in
`src/delphyne/stdlib/{models,queries,streams,computations}.py`; upstream
changes remain suggestions outside the Omphalos edit scope.

### A conservative way to use the remaining evidence

1. **Finish diagnosis with existing records before funding a candidate.**
   The current evidence supports work on repeated-state control, verified
   advice and bounded tool feedback. It does not support another broad
   playbook-size/curator-strength sweep. No new benchmark partition is
   needed to investigate these defects.
2. **Choose one defect and one candidate.** A future mechanism pilot could
   use 5–8 deliberately selected, already-exposed problems: 10–16 paired
   arm/problem evaluations with one replicate, under a small agreed total
   budget including assistant work. This is a diagnostic proposal, not an
   authorized run or a statistically powered claim of general improvement.
   Stop if the targeted failure persists or the cost simply moves elsewhere.
3. **Make expansion a separate decision.** Only after the intended state
   transition improves should another held-out comparison be considered.
   Reuse existing controls where their environment and budget match; do
   not silently reuse results across changed verifier/prompt semantics.
   Do not keep adding seeds or checking p-values until one is significant.
4. **Keep checks proportional to the change.** Documentation requires no
   model benchmark or test suite. A future focused code fix gets relevant
   deterministic checks and existing cached examples first; a paid
   end-to-end matrix is not a default regression test. Report at completion
   or when a decision is needed, not on a timer.

For reproducibility, the taxonomy uses `failure_analysis.refine_class` on
cached `check`/`check_assisted` outputs. Repetition is exact equality of
`(failing_tactic, error_message, proof_so_far, remaining_goals)` within a
cell. The sorted mapping of the 320 inspected cache paths to SHA-256 hashes
has digest `88044053a9d59f7785aa045f315bf716d43def90f29a9d3462ccf77826d1bacc`.
All original results, caches, playbooks and code remain unchanged by this
follow-up.

## Findings and changes

1. **The new machine supports concurrent experiments.** i34-gpu01 has
   64 physical CPU cores, 128 hardware threads and approximately 220 GiB
   RAM. This pipeline uses CPU Rocq processes and remote API calls; its
   four GPUs do not accelerate the present implementation. The legacy
   four-worker default unnecessarily constrained ACE evaluation launches.
   ACE make targets now inherit the configured stream ceiling unless
   explicitly overridden. The campaign pins a measured profile rather
   than deriving experimental identity from whatever environment happens
   to be present on resume.
   The captured [hardware and software inventory](experiments/campaigns/ace_review_20260908/environment.json)
   includes Rocq 9.0.1, Python 3.12.13 and the installed client versions.

   The CPU-only sweep re-executed the same 192 training bridge calls at
   8/16/24/32 workers: **768/768 outcomes preserved**. Elapsed times were
   35.01/33.95/33.89/34.06 seconds; aggregate peak RSS was
   3.28/6.33/9.19/12.04 GiB. Twenty-four was narrowly fastest. These close
   timings do not establish a general throughput optimum: startup and the
   particular bounded workload dominate this small benchmark. Full
   measurements are in [runtime_benchmark.json](experiments/campaigns/ace_review_20260908/runtime_benchmark.json).

2. **Keep the useful memory protections and caches.** Warm private Rocq
   servers, stable augmented paths, memoization, response-size bounds and
   process recycling address correctness and pathological tactics as well
   as laptop scarcity. An exploratory replay of the archived runaway
   `mathd_algebra_185` call still failed when the server RSS/address-space
   settings were raised from 1.5/3 GiB to 4/6 GiB: 26.02→49.34 seconds and
   roughly 3,049→5,507 MiB peak RSS, with no recovery. That is evidence
   against a blanket increase. Per-prover defaults remain unchanged.

3. **Requests, rather than the nominal dollar cap, usually end failures.**
   Of 26 failed archived baseline validationX cells, 25 exhausted 32
   requests. The X experiments use **$0.10**, whereas the older canonical
   smoke configuration uses $0.05. A dollar stopping rule can admit a
   crossing request: the largest archived baseline cell cost $0.1253.
   Fresh calibration compares 32 and 64 requests on training data; any
   selected ceiling applies equally to the cheap baseline and ACE.

   A request limit also does not bound local CPU work. One fresh
   calibration cell took **49.5 minutes for 30 API calls and $0.104**;
   live logs showed repeated Rocq goal probing between model requests.
   More concurrent workers cannot shorten that serial work. A separate
   bounded-feedback treatment is worth testing; changing it during this
   comparison would confound the registered intervention. See the
   [runtime example](experiments/campaigns/ace_review_20260908/calibration_runtime_example.json).

   A confirmation-time operational snapshot recorded **64.9 minutes since
   the first API dispatch, only 11 calls and $0.071 liability** for one
   still-running cell. No HTTP call was in flight; a Rocq process was
   actively using CPU, 24.9 minutes after the latest dispatch. This is
   runtime metadata, not a partial solve comparison or proof diagnosis.
   The [frozen observation](experiments/campaigns/ace_review_20260908/live_verifier_observation.json)
   makes the long-tail resource problem reviewable without mining held-out
   trajectories.

   The first development pass also encountered API context-window
   exhaustion at the selected 64-request ceiling. Extra requests can run
   into a different resource limit. The registered failed-cell policy
   retains these failures and any fresh-attempt costs; no transcript
   shortening or output-limit change is introduced during the comparison.
   Explicit context and feedback-compute budgets deserve a separate test.
   A later development attempt also produced a tool-result string of
   13,272,517 characters, exceeding the API's 10,485,760-character input
   string ceiling. This is a separate failure from token-window exhaustion.

   Terra also admitted a single request with **509,071 input tokens** and
   681 output tokens, costing **$1.0219922** against its nominal $0.30
   per-problem stopping budget. The campaign ledger reserved enough before
   dispatch and includes the full settled charge. A generous global budget
   does not make the nominal per-problem limit a hard billing ceiling.

4. **The reference performs regeneration after reflection.** The local
   pipeline performed a single reflection followed by curation; its three
   parsing retries were not three attempts to improve a proof. The new
   opt-in variant executes `generator → reflector → fresh generator →
   reflector`, with at most two repair rounds of 16 requests/$0.05 each.
   It stops on verified success and curates from the original plus repair
   evidence. Original training solves are recorded separately from repair
   recovery. Default `repair_rounds=0` preserves every archived variant.
   This is a plausible methodological gap, not proof that it caused the
   old null results. See the [ACE implementation at the reviewed commit](https://github.com/ace-agent/ace/blob/82709de050e1db6e6ef2f07bcb0393560b94992a/ace/ace.py)
   and the local [ACE paper](papers/2510.04618v3.pdf).

   The reference also supports supplying the correct answer to the
   reflector, as well as a mode without that answer. Omphalos supplies
   verifier feedback, not a known proof. This is a legitimate different
   learning setting, and a rejected tactic does not reveal a successful
   proof strategy. Testing verified training solutions as additional
   feedback is a useful separate hypothesis; the current results cannot
   identify feedback richness as their cause. See the
   [reference feedback modes](https://github.com/ace-agent/ace/blob/82709de050e1db6e6ef2f07bcb0393560b94992a/ace/ace.py).

5. **The historical statistical conclusion was too strong.** With two
   repeated seeds, x3 improved 54→57/80 cells, but its three additional
   solves came from only two independent theorems. The paired theorem
   cluster test gives **p=0.50**. Stronger curation, v5 and three epochs
   also fail to establish an improvement; they do not establish that every
   practically useful gain is absent. Complete recomputed results:
   [archived_audit.json](experiments/campaigns/ace_review_20260908/archived_audit.json).

   | Archived ACE artifact | Solves / 80 | Difference from baseline | Theorem-cluster p |
   |---|---:|---:|---:|
   | Baseline | 54 | — | — |
   | x3 | 57 | +3.75 points | 0.50 |
   | x3 without reflection | 57 | +3.75 points | 0.25 |
   | x3 with stronger curation | 55 | +1.25 points | 1.00 |
   | v5 | 53 | −1.25 points | 1.00 |
   | x3, three epochs | 53 | −1.25 points | 1.00 |

6. **A significance minimum is not power.** Five all-favorable independent
   discordances suffice for a one-sided exact p<0.05; six are required
   two-sided. Neither number means that a small study can reliably detect
   +5 percentage points. New inference groups repeated seeds and duplicate
   families together, requires every expected cell, retains platform
   failures, and reports effect/cost uncertainty. Percentile bootstrap
   intervals can collapse to [0,0] when every pair agrees; a conservative
   bound prevents using that artifact to exclude a useful gain. The
   exchangeability and independent-family assumptions remain explicit.
   For illustration, an 88-theorem, one-observation paired study has only
   about 20% power for a true +5-point gain when discordance is 10%
   (13% at 20% discordance); two within-theorem repeats do not simply
   double the number of independent problems. See
   [the power calculation](experiments/campaigns/ace_review_20260908/power_illustration.json).

   For a future study, distinguish the hypothesized true effect from the
   required observed improvement. With 400 independent tasks, a true
   +5-point gain and 10% discordance give about 87% probability of positive
   significance, but only 53% probability of also exceeding the observed
   +5-point cutoff. At the cutoff itself, simply increasing the sample
   cannot make that second probability approach 100%. A scenario with a
   true +8-point gain, 20% discordance and 400 tasks clears both conditions
   about 92% of the time. These are illustrative assumptions, not fitted
   estimates or a revision of the current rule. See
   [future power scenarios](experiments/campaigns/ace_review_20260908/future_power_scenarios.json).

7. **Repeated validation is development.** ValidationX has selected many
   interventions. It is unsuitable as fresh confirmation. A manifest froze
   **88 previously unexposed, non-Mathd challenge problems** before new API
   calls, including a fixed stratified 32-problem Terra subset. Exposure
   checks use recorded identifiers, demonstrations, statement templates and
   contest-family identifiers, without reading held-out proof outcomes.
   Seven unused Mathd statements sharing exposed templates were
   quarantined; another 166 Mathd problems remain reserved. This is a
   conservative duplicate check, not semantic deduplication or a claim
   about model pretraining. Adaptation and failure-mining entry points
   reject the protected population. See the
   [manifest](benchmarks/ace_challenge_20260908.json).

8. **Campaign accounting must include every paid path.** A SQLite ledger
   atomically reserves upper bounds before dispatch. Responses calls and
   embedding cache misses receive receipts; SDK retries are disabled;
   timeout/unknown charges retain their reservation. Receipts identify
   individual cells and adaptation roles, so failed attempts and retries
   enter cost comparisons. A nominal per-problem dollar budget remains a
   stopping rule; the campaign's $50 liability ceiling governs admission.
   The 32,768-token output ceiling applies to all new arms, including
   hidden reasoning, as specified by the
   [Responses API](https://developers.openai.com/api/reference/cli/resources/responses/methods/create).

9. **An advertised retry was ineffective.** The adaptation runner called
   `mark_errors_as_todos()`, but the next supervised launch rebuilt status
   from the still-present `exception.txt` and restored the failure. It now
   uses the launcher's `retry_failed()`, which preserves the exception as
   a dated record and permits a fresh attempt to run. Paid caches are now copied
   into dated attempt directories before the stdlib clears the active cache.
   Campaign input
   drift is refused instead of silently deleting an already paid cell.

10. **Avoid arbitrary threshold inflation.** A larger playbook, looser
    deduplication or a stronger curator is not automatically a better ACE
    implementation. Prior larger/stronger arms did not produce a robust
    solve gain, and some accurate advice harmed proofs. The first new
    treatment retains x3's rendering, 4,000-token guard, models, embedding
    threshold, batching and refinement. The context-engineering resource
    is useful for hypotheses about context quality and evaluating agent
    behavior; its generic thresholds are not Rocq evidence. See its
    [context degradation guidance](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/context-degradation)
    and [evaluation guidance](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/skills/evaluation).

    Completed repair seed1 produced 26 bullets and 2,199 estimated tokens,
    versus x3's 26 bullets and 2,103 tokens, with zero size-compaction
    events. The 4,000-token guard did not force compaction in that run.
    Large complete conversations remain a separate concern: training
    receipts include a generator input of 197,305 tokens and a curator
    input of 93,144 tokens; Terra evaluation reached 509,071 input tokens.
    The playbook cap does not bound tool feedback or the full conversation
    history. The completed receipt audit found still larger inputs in the
    cheap evaluation arms, up to **891,406 tokens** in confirmation.

    The common 32,768-output-token ceiling was reached by **50 requests**:
    25 in development (baseline/x3/repair0/repair1: 8/5/6/6) and 25 in
    confirmation (baseline/x3: 10/15). No training or Terra request reached
    it. These results therefore describe that bounded generation policy;
    they do not establish that the output ceiling is harmless. A separate
    training-set sweep could test its cost/solve trade-off, counting hidden
    reasoning and keeping the same actual-cost qualification rule. Counts
    are frozen in the [threshold audit](experiments/campaigns/ace_review_20260908/threshold_audit.json).

## Fresh study

The registered target is **at least +5 percentage points at actual cheap
prover cost <=$0.10**, with two-sided family-cluster p<0.05. The cost
reference is Terra Responses/core/low, 32 requests/$0.30, evaluated on the
same fixed subset; the desired cheap cost is at most one third of Terra's
mean charged cost. Adaptation cost is amortized separately. Unknown charges
are conservatively scored at their reserved upper bound and reported
separately from receipted token charges.
Request ceilings apply per attempt; registered fresh retries can exceed
that count per cell, and all their charges enter the $0.10 qualification
check. The runner applies its retry rule to API context-limit errors too.
The p-value tests a zero effect. The +5-point requirement is a threshold
on the observed estimate; it does not provide a confidence guarantee that
the true gain is at least five points. That stronger claim would require
a lower confidence bound above five points and a correspondingly larger
study. The current confirmation fails even the registered rule.

Calibration, two adaptation seeds, development selection and final
confirmation are tracked under
[the campaign directory](experiments/campaigns/ace_review_20260908/README.md).
Calibration completed all 160 configurations and selected **64 requests**.
Budget-qualified baseline solves rose **59→66/80** (+8.75 points), with
gains of 3/40 and 4/40 in the two replicates. Total charged cost rose
$2.195→$2.322 (+5.8%). This satisfies the registered calibration rule;
the paired cluster p=0.0625 remains inconclusive as a confirmatory test.
Before applying the cost cutoff, verified proofs rose **63→67/80**
(+5 points); four versus one verified proofs exceeded the conservative
cell-cost threshold. The larger budget-qualified gain therefore combines
proof outcomes with differences in cost qualification.
Six initial transport failures (five client timeouts and one server error)
were retried, preserving their $0.439 uncertain liability. Subsequent
launches restored a 600-second transport
deadline; this mixed pilot history limits causal interpretation of the
calibration. See [calibration.json](experiments/campaigns/ace_review_20260908/calibration.json).

Development completed all **320 cells**, with no residual platform failures,
and selected the existing **x3** playbook under the registered rule.

| Development arm | Verified proofs / 80 | Within $0.10 / 80 | Total conservative cost | Clustered p versus baseline |
|---|---:|---:|---:|---:|
| Baseline, 64 requests | 52 | 52 | $3.180 | — |
| Frozen x3 | 57 | 57 | $2.866 | 0.2344 |
| Repair seed0 | 55 | 52 | $3.250 | 1.0000 |
| Repair seed1, stability only | 54 | 54 | $2.783 | 0.6875 |

x3's development difference is +6.25 points, with a descriptive 95%
cluster bootstrap interval of **−2.5 to +13.75 points**. Its cost ratio to
baseline is 0.901 (95% descriptive interval 0.766–1.067). Neither interval
establishes an improvement. These are development results after selection,
not fresh confirmation. The repair intervention did not earn deployment:
even its 55 raw verified proofs fall below x3's 57, so removing conservative
cost disqualifications alone could not reverse the selection. Seed1 remains
a stability observation, never a substitute deployment candidate.

Development incurred two context-window errors in baseline and three API
errors in repair0 (connection, server, and input-string limit); all five
were retried once, retaining their charges. Repair0 includes $0.158612 of
uncertain liability. The full development cost was **$12.07775284**.
See [selection.json](experiments/campaigns/ace_review_20260908/selection.json)
and [development_cells.json](experiments/campaigns/ace_review_20260908/development_cells.json).

Confirmation completed all **352 configurations**, with no residual platform
failures. The selected x3 playbook and the fresh baseline each ran twice on
the same 88 previously unexposed non-Mathd theorems.

| Confirmation arm | Within $0.10 / 176 | Solve rate | Total conservative cost |
|---|---:|---:|---:|
| Baseline, 64 requests | 118 | 67.05% | $6.662 |
| Selected x3, 64 requests | 121 | 68.75% | $6.949 |

All verified proofs in this panel also satisfied the cost cutoff. The
paired effect is **+1.70 percentage points**, with descriptive 95% family
bootstrap interval **−2.27 to +5.68 points**, exact clustered **p=0.5811**,
and 13 discordant families. The registered +5-point/significance rule is
not met. The interval still includes a useful gain, so this is inconclusive
evidence rather than a proof that ACE cannot help. The conservative upper
bound is wider still (+27.80 points).

The cost ratio is **1.043** (95% descriptive interval 0.937–1.162). The
development cost advantage did not reproduce as a point estimate, and
neither panel establishes a reliable cost difference. One server-error
attempt was retried once, preserving $0.0916874 of uncertain liability.
Even treating that unknown charge as zero leaves the solve comparison
unchanged and x3's observed total cost 2.93% higher. This optimistic
[billing sensitivity](experiments/campaigns/ace_review_20260908/confirmation_billing_sensitivity.json)
does not change the registered score or its conclusion.
The longest completed attempts took **55.7 minutes for baseline and 72.4
minutes for x3**. The registered request and dollar limits do not provide
a useful per-problem latency bound. See
[confirmation.json](experiments/campaigns/ace_review_20260908/confirmation.json).

The fixed Terra comparison completed all **32 cells** without platform
failures. All verified proofs also met their respective cost cutoff.

| Matched reference arm | Budget-qualified solves / 32 | Mean charged cost |
|---|---:|---:|
| Terra, 32 requests / nominal $0.30 | 25 | $0.17173 |
| Selected x3, replicate0 / nominal $0.10 | 22 | $0.04365 |

x3 cost **25.42% of Terra**, with descriptive paired 95% cost-ratio interval
**17.29%–35.69%**. It was cheaper on every matched problem. The point
estimate meets the one-third cost target, but the interval crosses that
threshold. Quality equivalence is not established: the solve difference
is −9.375 points, with descriptive 95% interval −21.875 to +3.125 points
and exact p=0.375. Keep the $1.022 crossing request in the cost comparison;
discarding an inconvenient expensive cell would change the estimand.
Terra's longest attempt took **71.8 minutes**.

Reusing the existing x3 artifact incurs zero **incremental** adaptation
cost in this campaign; its original training is a sunk cost, not free
training. At 100/1,000/10,000 deployment problems the reported incremental
amortized cost consequently remains $0.04365/problem. The $3.316 spent on
the two new repair artifacts is included in the research campaign total.

All **864 evaluation cells**, 80 original training episodes and 31 repair
episodes completed. Final conservative liability is **$39.01643976 of
$50**, comprising $38.32744076 of receipted charges and $0.688999 reserved
for nine attempts with unknown charges. Nothing remains in flight. The
export contains **20,704 receipts**, including embeddings and unsuccessful
requests, and all five audited allocation transfers. Results and billing
are frozen in [final_report.json](experiments/campaigns/ace_review_20260908/final_report.json),
[final_cells.json](experiments/campaigns/ace_review_20260908/final_cells.json),
[receipts.csv](experiments/campaigns/ace_review_20260908/receipts.csv) and
[operational_audit.json](experiments/campaigns/ace_review_20260908/operational_audit.json).
The [effect comparison](experiments/campaigns/ace_review_20260908/effect_comparison.png)
also has a [PDF export](experiments/campaigns/ace_review_20260908/effect_comparison.pdf).

Both repair-training seeds are complete, costing **$3.316 total** including
all roles and embeddings. Each originally solved 32/40 training episodes.
Seed0 recovered none of its eight failures in 16 repair episodes; seed1
recovered one of eight in 15 episodes. The recovered proof used 12 requests
in its first repair round, and the loop correctly stopped there. Their
frozen playbooks contain 27/26 bullets and 2,146/2,199 estimated tokens.
These describe evolving training runs, not held-out improvement. See
[training_summary.json](experiments/campaigns/ace_review_20260908/training_summary.json).
The repair intervention is an additional-compute training treatment;
comparison with the older frozen x3 artifact cannot isolate reflection's
causal contribution from training randomness or extra generator compute.
Only seed0 can be deployed; seed1 is a stability check.
The challenge deliberately excludes Mathd, whereas trainX and validationX
contain 50% competition problems. This measures transfer to a different
task mix; it does not estimate performance on the original miniF2F mixture.
The category filter did **not establish a harder benchmark**: the fresh
baseline solved 67.05% here versus 65% in development. Those samples differ,
so this is not a formal difficulty comparison, but there is no empirical
basis for labeling the challenge harder. A future difficulty tier should
be calibrated independently and frozen before ACE evaluation, without
selecting from this challenge's failures. The remaining fresh population
also limits statistical power.

## Validation and limits

- The complete omphalos `make test` suite passed, including Rocq checks
  and cached demonstrations. The archived x3 adaptation replay hit every
  recorded cache entry. New tests cover incomplete panels, seed clustering,
  actual-cost cutoffs, repair stopping and guidance, protected problems,
  process-safe budget admission, uncertain charges and embedding caching.
- Root `make pyright` passes the core project and stops at the pre-existing
  missing `why3py.simple` dependency in `examples/find_invariants` (17
  cascading errors). That dependency is outside the authorized edit scope.
  The complete omphalos directory passes `pyright .`, including the final
  reporting and plotting additions.
- Final integrity checks matched all 55 recorded execution/analysis
  source hashes, all 125 exposure-source hashes and all 88 challenge
  statement hashes. The portable receipt export reconciles with the
  frozen result and contains no pending billing. See the
  [final source inventory](experiments/campaigns/ace_review_20260908/source_final.json).
- No model tier can be identified as the cause of past decisions from
  these artifacts. The supported findings concern implementation and
  measurement; the fresh comparison does not establish the target gain.
- Revised upstream suggestion after the follow-up source audit: connect
  conservative monetary estimates to the existing `LLM.estimate_budget`
  and `spend_on` interfaces, expose transport retry/timeout controls, and
  preserve external cross-process liability accounting. A new admission
  abstraction is not required just to supply dollar estimates. Omphalos's
  present Responses adapter enforces the shared campaign ceiling. Keep
  these controls on the policy/model side, consistent with the
  [Delphyne paper](https://arxiv.org/abs/2502.05310).
