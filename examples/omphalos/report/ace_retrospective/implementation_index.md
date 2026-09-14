# Implementation index

Static parsing only; experiment modules are not imported. Descriptions are source docstrings and may refer to historical behavior. The main report distinguishes implementation from measured effects.

## ace/__init__.py

Omphalos ace modules.


## ace/ace_applicability.py

Syntax-only applicability contracts; shared by both agent harnesses.

- `RepairState` (line 20):
- `RepairDecision` (line 32):
- `RepairExample` (line 40):
- `syntax_form` (line 49): A deliberately finite grammar, not an arbitrary tactic translator.
- `eligible` (line 87):
- `syntax_tokens` (line 95): Ignore whitespace between tokens, never inside names or strings.
- `supported_decision` (line 111):
- `signature` (line 121): Route by grammar, target location and state domain, never theorem ID.
- `error_shape` (line 146):
- `select_ids` (line 151):
- `check_repair` (line 187):
- `executed` (line 214):
- `checked_application` (line 225): Same assisted verifier as the reference; record only real computations.

## ace/ace_dedup.py

Near-duplicate detection for ACE playbook bullets.

- `Deduper` (line 60): Finds the closest existing bullet to a candidate text.
- `_normalize` (line 79): Casefold, collapse whitespace, strip a trailing period.
- `LexicalDeduper` (line 86): The legacy rule: `SequenceMatcher.ratio()` on normalised text.
- `jaccard_tokens` (line 116): Normalised token set: backticked code spans are kept whole (a lemma name is one token, not three), everything else is lowercased words minus stopwords.
- `JaccardDeduper` (line 129):
- `EmbeddingDeduper` (line 149): Cosine similarity of embeddings, cached on disk.

## ace/ace_evidence.py

Verifier evidence for ACE curation: what the pool actually gets wrong.

- `FailedVerdict` (line 60): One rejected proposal, reduced to what the digest counts.
- `failed_verdicts` (line 69): Every failed verifier verdict in one generator cell's `cache.yaml`, in cache order. Verdicts without an error message (a script that applied cleanly but left goals open) carry no mechanical failure and are not evidence.
- `collect_failures` (line 97): Failed verdicts of several generator cells (`bench -> config directory`), benches in sorted order so the result is a function of the mapping's *content*. A cell without a cache contributes nothing.
- `unknown_identifier` (line 121): The `X` of "The reference/variable X was not found", line-wrapped or not; `None` for any other message.
- `tactic_head` (line 131): The shape of a failing tactic, coarse enough to count: its leading verb after any bullet, brace or goal selector, plus a marker for the three Ltac shapes that recur — `… :=` (`set`/`pose` definitions), `… in` (a hypothesis target) and `… by` (an inline sub-proof).
- `ClassSummary` (line 159):
- `summarize` (line 172): Classes ranked by `(problems, verdicts)` descending, label ascending as the tie-break; within a class, names and heads by count descending then text ascending. Pure and order-independent: the input is treated as a multiset.
- `_clip` (line 236):
- `render_digest` (line 240): The evidence block a curation prompt receives, or `""` when there is nothing to report (the templates guard on emptiness, so the first steps of a run render exactly like a contract-3 prompt would have with no evidence). This text is part of LLM prompts and of config identity: change it with the care of a template. `blurbs` extends the class descriptions (the trigger assigner passes the fine classes); the default renders every recorded digest byte-identically.
- `known_guidance` (line 301): The `## Pitfalls …` section of the agentic system prompt, verbatim. A curation prompt that can see it can refuse bullets that merely restate it — the contract-3 rule said "do not restate the system prompt" to a model that had never seen the system prompt.
- `normalize_reference` (line 352): Strip the decoration a model puts around a name in YAML/markdown (backticks, quotes, a trailing period or comma). A *trailing* prime is part of a Rocq name (`Rle_0_sqr'`) and is kept.
- `checkable_references` (line 362): The subset of `names` the gate can meaningfully send to `Locate`: identifier-shaped (possibly module-qualified), not a primitive tactic keyword, de-duplicated in first-appearance order.
- `grounding_verdict` (line 390): Read the bridge's answer to `Locate <name>.`: `No object …` means the name does not exist in that environment; a bridge or session failure is *not* evidence about the name (the bullet is kept and the failure counted); anything else names an object.
- `locate_command` (line 405):
- `import_signature` (line 417): The `Require` lines of a problem file, in order — what decides which names `Locate` can see. Two files with the same signature are the same environment for the gate's purposes.
- `representative_files` (line 433): One `(problem_file, theorem_name)` per distinct import signature in the pool, in pool order: the environments a pool-level bullet (an Auditor addition) is grounded against. A name that resolves in any of them exists on this benchmark.

## ace/ace_goal_visibility.py

Version 2 feedback for incomplete proofs with no focused goals.

- `inspect_obligations` (line 23):
- `checked_proof_v2` (line 98):
- `inspect_proof_state_v2` (line 144):

## ace/ace_grounded.py

Typed, state-checked ACE evidence and bounded verifier computations.

- `outcome_of` (line 57):
- `Checked` (line 73):
- `feedback_view` (line 81):
- `checked_proof` (line 99):
- `Inspection` (line 142):
- `inspect_proof_state` (line 149):
- `TrainingTransition` (line 232):
- `assert_training_transition` (line 245):
- `AdviceClaim` (line 261):
- `ClaimVerdict` (line 282):
- `validate_claim` (line 292):
- `decision_kind` (line 379):
- `select_advice` (line 391):
- `select_matched_advice` (line 411): Select one same-class example with explicit goal-symbol evidence.
- `failure_category` (line 437):
- `recent_progress` (line 452):
- `AdaptationState` (line 467):

## ace/ace_playbook.py

Playbook data model and deterministic merge for the ACE pipeline.

- `_normalize_section` (line 71):
- `Bullet` (line 100): One playbook item. `helpful`/`harmful` count Reflector tags.
- `AddOp` (line 111): A Curator delta operation. ADD-only by design (v1).
- `AuditDecision` (line 129): The Auditor's verdict on one existing bullet (`apply_audit`). `content` is read for `rewrite` only.
- `BulletTag` (line 142): A Reflector verdict on one existing bullet.
- `Playbook` (line 150): An ordered collection of bullets plus the next fresh id number.
- `MergeOutcome` (line 251): Result of one deterministic merge.
- `RewriteBullet` (line 275): One bullet of a *monolithic* rewrite: no id, no counters.
- `Deduper` (line 288): Structural twin of `ace_dedup.Deduper` (kept here to avoid a cycle).
- `_normalize` (line 300): Casefold, collapse whitespace, strip a trailing period.
- `_LegacyLexical` (line 307): `merge`'s built-in v1 rule; identical to `ace_dedup.LexicalDeduper`.
- `_pool` (line 328):
- `merge` (line 336): Deterministically fold one adaptation step into the playbook.
- `RefineOutcome` (line 426): Result of one `refine` pass.
- `refine` (line 445): The paper's "refine" half of grow-and-refine, run proactively.
- `AuditOutcome` (line 507): Result of `apply_audit`.
- `apply_audit` (line 530): Apply one terminal audit pass deterministically.
- `rebuild` (line 615): Replace the playbook wholesale with an LLM-authored rewrite.

## ace/ace_repairs.py

Repair mining: advice from the verifier's own ground truth.

- `Attempt` (line 51): One proposal and its verdict, as recorded.
- `Repair` (line 63):
- `attempts_of_cache` (line 93):
- `_conclusion` (line 147):
- `_replacement` (line 154): The diff block of `old → new` that covers `old[idx]` (the failing tactic). `None` when the failing tactic survived unchanged — the prover changed something else, which is not a repair of *this* rejection.
- `_gives_up` (line 179):
- `repairs_of_cell` (line 186):
- `mine_run` (line 225): Every repair in a recorded run. `only` restricts to cells whose name contains it (the adaptation directories hold generator, reflector and curator cells side by side: `only="_generator_"`).
- `RepairGroup` (line 249):
- `_short` (line 261):
- `group_repairs` (line 266):
- `render_repairs` (line 318): The digest a bullet writer receives: one paragraph per group, frequent first, each with the replacements that were accepted and verbatim examples. Part of an LLM prompt and of a config identity — change with the care of a template.
- `name_replacements` (line 356): unknown name → what the next accepted proposal used instead.

## ace/ace_store.py

Content-addressed storage for ACE playbooks and their step records.

- `steps_dir` (line 109):
- `PlaybookStore` (line 115): All on-disk playbook state of one adaptation variant.

## ace/ace_triggers.py

Error-keyed playbook injection ("hint on error").

- `TriggerSpec` (line 117): One row of the trigger assigner's answer (`prove_ace.AssignTriggers`).
- `TriggerAssignment` (line 129):
- `Hint` (line 135): One bullet attached to a feedback message.
- `TriggerEntry` (line 143):
- `TriggerError` (line 169):
- `_compile` (line 174):
- `_normalize_name` (line 181):
- `TriggerTable` (line 186):
- `parse_table` (line 299): `TriggerTable.loads`, memoized: the generator strategy parses the same table on every feedback turn.
- `score` (line 310):
- `select_ids` (line 352): The ids of the best-matching bullets, highest score first, ties by playbook order; empty when nothing matches.
- `select_hints` (line 386): Hints for one failed verifier verdict (see `prove_ace`).
- `render_hints` (line 418): The markdown list the feedback template emits (kept here so a test can pin it without rendering a prompt).
- `Coverage` (line 430):
- `recorded_rejections` (line 479): `(cell, verdict)` for every failed verdict of a recorded run, with the remaining goals (which `failure_analysis.Verdict` drops).
- `coverage` (line 492): Replay the selection over every failed verdict of the runs.
- `render_taxonomy` (line 553): The class list the trigger assigner may use, one per line.
- `render_playbook_for_assignment` (line 564): Bullets with id and section, in playbook order.

## ace/ace_verified_snippets.py

Source-witness checks for executable examples emitted by a reducer.

- `SnippetWitness` (line 23):
- `SnippetVerdict` (line 46):
- `SnippetBinding` (line 58): Bind an executable example in one reducer operation to its source.
- `protect_reduction` (line 66): An explicit provenance gate before deterministic playbook merging.
- `preserve_verified_snippet` (line 97):
- `replace_book_snippet` (line 137): Change one explicitly bound example; keep every other byte of content.

## ace/change_progress.py

Conservative, offline focused-obligation scoring; never a runtime tool.

- `ProgressAudit` (line 19):
- `audit_progress` (line 37): Replay the verified suffix, looking for closure at original depth.

## experiments/ace/__init__.py

Omphalos experiments ace modules.


## experiments/ace/ace_adaptation.py

ACE context adaptation — offline and online — for the agentic prover.

- `AdaptVariant` (line 172): One adaptation configuration.
- `_online3` (line 380):
- `_online` (line 399):
- `_variant` (line 617):
- `_output_dir` (line 636):
- `_online_output_dir` (line 640):
- `_sha256` (line 644):
- `_render_message` (line 653):
- `_truncate` (line 676):
- `_yaml_load` (line 687): `yaml.safe_load` with the C loader when available: the driver parses multi-MB `cache.yaml` / `result.yaml` files several times per step, and the pure-Python loader is ~7x slower on them.
- `_final_chat` (line 701): The last cached LLM exchange of a generator cell, sliced from the last non-feedback user message that names the theorem, plus the final assistant output (`None` when the last turn was a tool call with no content). Shared by `extract_trajectory` and `cited_bullet_ids`; the rendering is byte-identical to before.
- `cited_bullet_ids` (line 738): Bullet ids the Generator named in its OWN messages, in first-mention order, restricted to `known` (the playbook it saw). Only assistant text counts: the playbook itself sits in the system message and ids echo in verifier feedback and tool results, none of which is a citation. The `render_version >= 3` prompt asks the model to name the ids it relies on before its first tool call (or "none apply").
- `extract_trajectory` (line 769): Render the generator run's trajectory from its `cache.yaml`.
- `_has_final_output` (line 799):
- `read_result` (line 811): `(solved, verdict line for the Reflector)` from `result.yaml`.
- `read_outcome` (line 829):
- `read_requests` (line 833): Requests the generator spent, from `result.yaml`.
- `_config_name` (line 855):
- `_config_dir` (line 860):
- `ACEAdaptStepConfig` (line 865): One adaptation sub-step: a generator, reflector or curator run.
- `_render_proposals` (line 1288): One `[Sample k]` block per batch member's curator delta. Under reducer contract 2 (`with_references`) each proposal also lists its `references`, so the reducer can carry them into the final ADDs (the x5 smoke run showed it emitting `references: []` for every ADD because it had never seen them). The contract-1 rendering is byte-identical to the recorded one: it is pinned by every recorded reducer's `upstream_sha256`.
- `_theorem_text` (line 1315): The theorem statement, for the v3 curator's evidence block.
- `_progress_block` (line 1323): Budget/progress the v3 curator sees (the reference feeds its curator the token budget, the training progress and per-section playbook stats).
- `load_reflection` (line 1348): The Reflector's parsed output, or `None` if nothing parsed.
- `load_delta` (line 1358): The Curator's parsed delta, or `None` if none parsed.
- `load_audit` (line 1375): The Auditor's parsed output, or `None` if nothing parsed.
- `load_grounding` (line 1385): The grounder's verdicts, or `None` if the run produced none.
- `load_rewrite` (line 1395): The monolithic Curator's rewrite, or `None` if none parsed.
- `reflection_digest` (line 1405): Canonical text of the reflection fields the curator consumes.
- `RoleRunner` (line 1422): Runs configs of one `Experiment` and reports per-config status.
- `StepPlan` (line 1570):
- `order_for_epoch` (line 1578): The traversal order of one epoch: file order when `shuffle_seed` is `None` (the legacy behaviour), else the `epoch`-th permutation drawn from `random.Random(shuffle_seed)` — the paper reshuffles per epoch. Deterministic, and every epoch is a permutation.
- `plan` (line 1596): The batches of one run, as pure data.
- `_Roles` (line 1629):
- `_make_deduper` (line 1634):
- `_make_step_config` (line 1658):
- `_make_online_config` (line 1721): The evaluation cell of one online step.
- `_freeze` (line 1743): Write a frozen playbook, refusing to *change* one that exists.
- `_check_resume_consistency` (line 1775): A run resumes by re-deriving every step from cache; if the planned traversal disagrees with what `steps.csv` recorded (a pool or shuffle change), the chain would silently fork. Refuse instead.
- `_generator_dir` (line 1800):
- `_Evidence` (line 1804): The pool-level failure digest, memoized per generator cell: the caches are parsed once per run, not once per batch. Rendering is a pure function of the cells handed in (`ace_evidence.render_digest`), so a resumed run pins the same text into the same configs.
- `_evidence_cells` (line 1824): The generator cells the digest is computed from: every recorded step whose generator ran, in step order, then the current batch's non-skipped members. Offline mode only (online generator cells live in another experiment and v5 is offline by construction).
- `_render_environments` (line 1849):
- `_batch_environments` (line 1853): The problems of the batch members that produced a trajectory — the environments a batch's bullets are grounded against.
- `_GateOutcome` (line 1864): What the grounding gate did with a set of ADDs. Ops are addressed by `id()` because a batch's deltas are held in memory for exactly one merge; `refused` maps an op to the names Rocq did not know, `errors` holds ops kept although a reference could not be checked.
- `_ground` (line 1880): Run the grounder config for `ops` (one per batch, named by the batch's first step). Returns `None` when the grounder failed all retries — the gate then keeps everything and records the failure — and `[]` when there was nothing to check.
- `_apply_gate` (line 1915): Refuse every op with a reference Rocq answered `missing`; keep an op whose references could not all be checked (a bridge failure is not evidence about the name) and count it under `errors`. With `results is None` (no grounder output) every op is kept and counted as an error if it had anything to check.
- `_attribute` (line 1950): Pair each id a merge created with the op that created it. `merge` creates ids in op order for every op it neither folded (dedup) nor refused (size guard); `not_created` lists those ops' contents.
- `_provenance_record` (line 1974):
- `_provenance_block` (line 1991): One line per bullet for the Auditor: origin, outcome, counters.
- `RepairEvidence` (line 2023):
- `_repair_batch` (line 2032): Reflect -> fresh regeneration -> reflect, stopping on verification.
- `execute` (line 2157): Run the planned batches; return the final playbook and the list of playbook hashes *before* each step (the derived step index).
- `_run_audit` (line 2756): The terminal audit (v5): one `AuditPlaybook` call over the finished playbook, its provenance, the whole pool's failure digest and the prover's pitfalls; the Auditor's additions pass the grounding gate against one environment per distinct import signature of the pool; `apply_audit` applies the decisions deterministically. Everything is logged to `audit.log.yaml`; the caller freezes the result.
- `_roles` (line 2864):
- `CLI` (line 2876): Fire CLI for the adaptation driver.

## experiments/ace/ace_applicability_experiment.py

Registered applicability campaign, usable from Codex and Claude Code.

- `ApplicabilityConfig` (line 44):
- `name` (line 105):
- `configs` (line 114):
- `authorize` (line 150):
- `main` (line 170):

## experiments/ace/ace_attribution_experiment.py

Approved ACE attribution and complete Terra scaling study (2026-09-12).

- `digest` (line 72):
- `fingerprint` (line 76):
- `read` (line 82):
- `save` (line 86): Create immutable campaign evidence, accepting identical resumes.
- `context` (line 99):
- `panel` (line 104):
- `ProofConfig` (line 128):
- `name` (line 176):
- `proof` (line 183):
- `validate_proof` (line 205):
- `prepare` (line 243):
- `seal` (line 307):
- `verify` (line 358):
- `activate` (line 373):
- `accounting` (line 382):
- `export_receipts` (line 422):
- `transfer_unused` (line 433): Move only completed-stage slack, once; never increase authorization.
- `TrainingConfig` (line 465):
- `training_name` (line 487):
- `TerraVariant` (line 491):
- `training_variant` (line 496):
- `launch` (line 514):
- `TrainingRunner` (line 572):
- `train_book` (line 597):
- `run_batch` (line 641):
- `campaign` (line 680):
- `main` (line 723):

## experiments/ace/ace_bounded_experiment.py

Approved $10 ACE follow-up, trainX then ONE validationX seed-0 arm.

- `digest` (line 54):
- `activate` (line 58):
- `load_claims` (line 69):
- `BoundedConfig` (line 78):
- `name` (line 169):
- `GroundedAdaptConfig` (line 174):
- `adapt_name` (line 200):
- `configs` (line 204):
- `main` (line 273):

## experiments/ace/ace_capacity_experiment.py

Registered ACE capacity follow-up, approved 2026-09-12.

- `save` (line 85):
- `read` (line 96):
- `context` (line 100):
- `register_budget` (line 105): Allocate unused existing money atomically; retain the single ceiling.
- `activate` (line 157):
- `book` (line 164):
- `ProofConfig` (line 179):
- `RoleConfig` (line 288):
- `prepare` (line 332):
- `seal` (line 516):
- `verify` (line 562):
- `accounting` (line 568):
- `launch` (line 595):
- `forward_unused` (line 650):
- `campaign` (line 665):
- `main` (line 728):

## experiments/ace/ace_contender_benchmark.py

User-authorized comparison of BOTH ACE model contenders, 2026-09-10.

- `read` (line 58):
- `save` (line 62):
- `ContenderConfig` (line 68):
- `name` (line 79):
- `configs` (line 83):
- `proposed_configs` (line 87):
- `reference_inventory` (line 114): Freeze existing seed-0 controls without choosing by their outcomes.
- `prepare` (line 204):
- `verify` (line 270):
- `accounting` (line 274):
- `observations` (line 307):
- `holm` (line 355):
- `report` (line 364):
- `main` (line 458):

## experiments/ace/ace_control_cycle_experiment.py

Registered 120-cell bounded ACE control cycle (trainX, trainX, validationX).

- `activate` (line 43):
- `CycleConfig` (line 55):
- `config_name` (line 65):
- `frozen` (line 72):
- `configs` (line 76):
- `main` (line 126):

## experiments/ace/ace_mechanisms_experiment.py

Approved $10 mechanism campaign, 2026-09-10; both agent harnesses.

- `read` (line 60):
- `save` (line 64):
- `MechanismConfig` (line 70):
- `name` (line 122):
- `proof_config` (line 126):
- `hash_paths` (line 144):
- `effective` (line 148):
- `prepare` (line 154):
- `verify` (line 320):
- `accounting` (line 332):
- `configs` (line 368):
- `observations` (line 375):
- `historical` (line 421):
- `select` (line 430):
- `report` (line 464):
- `main` (line 611):

## experiments/ace/ace_models_experiment.py

Approved $30 ACE model suite, preregistered before paid execution.

- `candidate` (line 51):
- `key` (line 59):
- `prep_cost` (line 67):
- `rank` (line 74):
- `evaluate` (line 86):
- `close_stage` (line 108):
- `prover` (line 131):
- `role_screen` (line 168):
- `interactions` (line 256):
- `select` (line 322):
- `benchmark` (line 375):
- `finish` (line 474):
- `campaign` (line 489):
- `main` (line 513):

## experiments/ace/ace_models_roles.py

Train-only ACE role experiments on fixed bounded-generator evidence.

- `sha` (line 36):
- `put` (line 40):
- `Step` (line 52):
- `dependencies` (line 67):
- `call_config` (line 71):
- `execute` (line 86):
- `make_step` (line 102):
- `proposals` (line 131):
- `build` (line 145):

## experiments/ace/ace_polish_experiment.py

Preregistered $8 bounded ACE polish campaign (both agent harnesses).

- `read` (line 51):
- `PolishConfig` (line 56):
- `name` (line 65):
- `configs` (line 69):
- `verify_sources` (line 142):
- `main` (line 148):

## experiments/ace/ace_repairs_experiment.py

Repair bullets: extend a frozen playbook with advice mined from the
verifier's accepted repairs (`ace_repairs`), and freeze the result
with its trigger table.

- `RepairWriterConfig` (line 79): The one-shot writer call; digest and guidance pinned into identity.
- `config_name` (line 149):
- `_take_flag` (line 159):
- `_run` (line 169):
- `main` (line 183):

## experiments/ace/ace_review_experiment.py

Registered ACE review campaign (2026-09-08), fresh controls only.

- `campaign_profile` (line 58):
- `activate_budget` (line 62):
- `ReviewConfig` (line 71): Fresh identity space: explicit theorem, partition and runtime.
- `name` (line 100):
- `configs_for` (line 107):
- `take_flag` (line 192):
- `experiment` (line 203):
- `main` (line 219):

## experiments/ace/ace_triggers_experiment.py

Build and freeze the trigger table of a frozen playbook (hint on error).

- `TriggerAssignConfig` (line 69): The one-shot assigner call. `evidence` and `classes` are pinned into the identity (like the curators' `evidence`), so the config can never run against a different digest than it was created for.
- `config_name` (line 117):
- `pool_digest` (line 125): The pool's failure digest with the fine classes (`refine_class`), which the adaptation-time digest deliberately lacks: the assigner may key a bullet on `ring-failure` or `unify-failure`.
- `_take_flag` (line 154):
- `load_assignment` (line 164):
- `main` (line 173):

## experiments/ace/ace_validation_experiment.py

Evaluate the frozen ACE playbook on validation (paired vs baseline).


## experiments/ace/ace_x3_validation_experiment.py

A frozen v3 ACE playbook on validationX, paired against the baseline.


## experiments/ace/ace_x_validation_experiment.py

A frozen ACE playbook on validationX, paired against the baseline.


## experiments/ace/change_control_experiment.py

Approved 2026-09-10: six trainX states, seed 0; no full problems.

- `ChangeConfig` (line 36):
- `name` (line 77):
- `configs` (line 85):
- `authorize` (line 121):
- `main` (line 131):

## experiments/ace/luna_effort_experiment.py

2026-09-10 user-authorized high-effort extension; six trainX resets.

- `configs` (line 42):
- `check_freeze` (line 53):
- `prepare` (line 61):
- `report` (line 100):
- `main` (line 246):

## experiments/ace/luna_upper_effort_experiment.py

2026-09-10 user-authorized Luna xhigh/max; twelve trainX resets.

- `UpperConfig` (line 44):
- `configs` (line 52):
- `check_freeze` (line 66):
- `prepare` (line 74):
- `report` (line 117):
- `main` (line 288):

## experiments/ace/terra_effort_experiment.py

2026-09-10 user-authorized high-effort extension; six trainX resets.

- `configs` (line 43):
- `check_freeze` (line 51):
- `prepare` (line 59):
- `report` (line 98):
- `main` (line 244):

## experiments/common/omphalos_launch.py

Reliable launching of omphalos experiments (a layer over `dp.Experiment`).

- `_env_int` (line 91):
- `default_max_streams` (line 96):
- `slot_dir` (line 100):
- `worker_rlimit_as_mb` (line 109):
- `resume_attempts` (line 113):
- `LaunchRefused` (line 117): A lock or slot could not be acquired; nothing was started.
- `_now` (line 121):
- `_log` (line 125):
- `original_cmdline` (line 129): The process's command line as launched. `sys.argv` is not it: experiment scripts strip their own flags before `fire` runs.
- `lock_note` (line 145): What a lock file records about its holder, after `pid= host= at=`: the experiment directory, extras, the cwd and — LAST, since it contains spaces — the full command line, so `tools/maintenance/stop_launches.py` can print exact resume commands.
- `parse_holder` (line 160): Inverse of the lock-file line: `pid`, `host`, `at`, `dir`, ..., `cmd`.
- `_holder` (line 179):
- `_try_lock` (line 186): Non-blocking exclusive `flock`; returns the fd (kept open) or None.
- `launch_lock` (line 212): Exclusive launch on `output_dir`; refuses if another launch holds it.
- `slot_table` (line 227): `(slot, holder-or-None)` for every slot (holder = probe by flock).
- `stream_slots` (line 243): Hold `n` of the `max_streams` machine-wide slots for the duration.
- `_queue_dir` (line 328):
- `_take_ticket` (line 334):
- `_live_tickets` (line 340):
- `_rank` (line 359):
- `_is_head` (line 366):
- `WorkerSetupArgs` (line 376):
- `_worker_common` (line 385): Runs in the attempt process; the result is pickled to workers.
- `_worker_init` (line 396): Pool-worker initializer (top-level: pickled by name).
- `_yaml_load` (line 419):
- `_ResultScanCache` (line 428): Stats of `result.yaml` files already verified complete, one sidecar per experiment directory. A result file is written once, at completion, and never touched again, so a file whose `(size, mtime_ns)` matches a verified entry needs no re-parse — before the cache, every `rebuild_statuses` pass fully YAML-parsed every ≤4 MB result of every config, `done` ones included (measured 15 s for a 240-config directory, ≥2 passes per resume, O(resumes × configs) over an adaptation chain). A corrupt or missing sidecar simply means a cold scan; entries are dropped when their file changes.
- `_scan_cache_for` (line 479): The per-directory cache for `<out>/configs/<name>/result.yaml`.
- `save_scan_caches` (line 493): Persist every dirty scan cache (atomic per-file `os.replace`).
- `_result_is_complete` (line 499): `result.yaml` is written once, at completion, so its presence means "done" — unless a killed worker left it truncated. Small files are parsed; large ones (traces) are checked for the closing structure to avoid minute-long parses. Verified-complete verdicts are cached against the file's stat (`_ResultScanCache`).
- `_result_is_complete_uncached` (line 524):
- `ground_truth` (line 539):
- `StatusDelta` (line 548):
- `rebuild_statuses` (line 562): Reconcile `experiment.yaml` with the per-config files. With `write`, a timestamped backup is kept next to the state file.
- `group_members` (line 601):
- `kill_group` (line 622): SIGTERM then SIGKILL the group; returns the number of survivors.
- `_Tee` (line 637):
- `_raise_interrupt` (line 654):
- `_install_stop_signals` (line 658): `make stop` speaks SIGINT/SIGTERM. A launch started as a background job from a non-interactive shell inherits SIGINT ignored, so both signals are (re)bound to raise `KeyboardInterrupt` in the launcher — the path that forwards the stop to the attempt group and lets the stdlib save its state.
- `_attempt_main` (line 673): Body of the supervised child: its own session, stdlib `resume`.
- `OmphalosExperiment` (line 706): `dp.Experiment` with locks, slots, supervised attempts and rebuilds.
- `OmphalosCLI` (line 907): The stdlib CLI plus `--wait`, `--dry`, `status`, `rebuild`, `slots`.
- `configs_of` (line 1007): The configs registered on `exp` (empty when none).

## prove_ace.py

ACE (Agentic Context Engineering) pipeline for the agentic baseline.

- `ProposeProofScriptACE` (line 92): The agentic proposal query, plus a playbook.
- `ProposeProofScriptACERepair` (line 122): Fresh proof episode conditioned on the preceding reflection.
- `prove_theorem_ace` (line 129): ACE generator: `prove_theorem_agentic` with a playbook.
- `_ace_examples` (line 187): Example selector for the ACE proposal query.
- `prove_theorem_ace_policy` (line 228): Policy for the ACE generator.
- `Reflection` (line 272): The Reflector's output, mirroring the paper's schema (their Fig. 10/13): a diagnosis of the trajectory plus per-bullet tags. `bullet_tags` may only reference ids present in the rendered playbook; unknown ids are ignored (with a warning) at merge time.
- `ReflectOnTrajectory` (line 289): One-shot Reflector query.
- `reflect_on_trajectory` (line 312):
- `CurationDelta` (line 335): The Curator's output: incremental ADD operations only.
- `CuratePlaybook` (line 343): One-shot Curator query.
- `curate_playbook` (line 398):
- `CurateFromTrajectory` (line 437): Curator that reads the raw trajectory instead of a diagnosis.
- `curate_from_trajectory` (line 466):
- `PlaybookRewrite` (line 485): A whole-playbook rewrite: every surviving bullet, verbatim.
- `RewritePlaybook` (line 493): Regenerate the WHOLE playbook (Dynamic-Cheatsheet cumulative mode).
- `rewrite_playbook` (line 519):
- `AggregateCurationDeltas` (line 534): Reduce independently proposed ADD operations into one final set.
- `aggregate_curation_deltas` (line 567):
- `PlaybookAudit` (line 594): The Auditor's output: a decision per bullet it chose to mention (unmentioned bullets are kept — `ace_playbook.apply_audit`) and a capped list of additions for uncovered, frequent failure classes.
- `AuditPlaybook` (line 607): One-shot terminal audit of a finished playbook.
- `audit_playbook` (line 633):
- `GroundingResult` (line 649): What Rocq said about one referenced name: `grounded` (an object of that name exists in `environment`), `missing` (no environment knows it) or `error` (the bridge could not answer — not evidence either way). `answer` is the last `Locate` output seen.
- `ground_references` (line 664): The grounding gate's Rocq half: for each name, ask `Locate name.` in each `(problem_file, theorem_name)` environment in order and stop at the first that knows it. No LLM anywhere — every answer is a `dp.compute` over `pytanque_utils.query`, cached and replayable exactly like the verifier's `check` calls. Ordering is fixed by the inputs, so a resumed run re-derives the same verdicts from cache.
- `ProposeProofScriptACETriggered` (line 699): The agentic proposal query with the playbook delivered *on error*.
- `HintedFeedback` (line 714): A verifier verdict plus the playbook bullets it triggered.
- `check_proof_assisted_hinted` (line 721): `prove_agentic.check_proof_assisted`, then hint selection.
- `prove_theorem_ace_triggered` (line 779): ACE generator with the playbook injected on error only.
- `prove_theorem_ace_triggered_policy` (line 835): `prove_theorem_ace_policy`, verbatim: same model construction, same bucket-redirected examples.
- `RepairAddition` (line 867): A repair bullet with its trigger (`WriteRepairBullets`).
- `RepairBullets` (line 889):
- `WriteRepairBullets` (line 895): One-shot writer of repair bullets (`ace_repairs`): sees the existing playbook, the ranked digest of verifier-accepted repairs on the adaptation pool, the taxonomy and the prover's own pitfalls; answers with at most `max_new_bullets` bullets, each with `references` (for the grounding gate) and a trigger.
- `write_repair_bullets` (line 915):
- `AssignTriggers` (line 933): One-shot assignment of a trigger to every bullet of a frozen playbook (`ace_triggers`): which failure classes, unknown names and error/tactic patterns should summon it. Sees the playbook with ids, the taxonomy it may use and the pool's failure digest (the names Rocq did not know, the failing tactic heads). Run once per playbook, by a stronger model than the generator if wanted; the answer is validated and frozen by `experiments/ace/ace_triggers_experiment.py`.
- `assign_triggers` (line 954):
- `_one_shot_policy` (line 973): dfs over a single query; `max_requests > 1` gives the model fresh attempts when a reply fails to parse as the target YAML schema (parse errors are logged and retried by `few_shot`, not raised).
- `reflect_on_trajectory_policy` (line 999):
- `curate_playbook_policy` (line 1012):
- `curate_from_trajectory_policy` (line 1025):
- `aggregate_curation_deltas_policy` (line 1038):
- `rewrite_playbook_policy` (line 1051):
- `audit_playbook_policy` (line 1064):
- `assign_triggers_policy` (line 1077):
- `write_repair_bullets_policy` (line 1090):
- `ground_references_policy` (line 1103): The grounder has no LLM: `Compute` is its only effect, eliminated by performing the computations (`dp.just_compute`). The inner policy is never consulted.

## prove_grounded.py

Composed grounded ACE strategies, with policies and examples separated.

- `grounded_search` (line 35): DFS with resource admission for Compute, under the parent budget.
- `InspectProofState` (line 101): Inspect a verified prefix with bounded output. Use start=4, 8, ... for omitted goals. Optional command: Search, Check, About or Locate. Supply complete Rocq sentences in tactics and command.
- `ProposeProofScriptGrounded` (line 113):
- `ResolveProofReference` (line 151): Choose a reference whose availability and type match this state.
- `ChooseProofBridge` (line 156): Choose a cast, normal-form or side-condition bridge, then verify.
- `ChooseProofStructure` (line 161): Choose an invariant, case split or structural opener, then verify.
- `_last_feedback` (line 165):
- `_no_branch_metadata` (line 169):
- `prove_theorem_grounded` (line 174):
- `grounded_examples` (line 692):
- `prove_theorem_grounded_policy` (line 733):
- `GroundedReflection` (line 790):
- `WorkedProofTransition` (line 800):
- `verify_worked_transition` (line 807): Navigation check tying a demonstration answer to live Rocq evidence.
- `ReflectGroundedTransition` (line 829):
- `AdmissionChoice` (line 837):
- `CurateGroundedClaim` (line 844):
- `AuditGroundedClaim` (line 851):
- `ReflectGroundedTransitionJSON` (line 858):
- `CurateGroundedClaimJSON` (line 863):
- `AuditGroundedClaimJSON` (line 868):
- `adapt_grounded_transition` (line 873):
- `adapt_grounded_batch` (line 956):
- `_adaptation_iteration` (line 974):
- `adapt_grounded` (line 992):
- `adapt_grounded_policy` (line 1006):
- `grounded_training_policy` (line 1012):
- `_reflector_policy` (line 1020):
- `_curator_policy` (line 1024):
- `_auditor_policy` (line 1028):
- `_iteration_policy` (line 1032):

## prove_stall.py

The agentic prover with a stall rule: a third budget mechanism.

- `_stall` (line 54): The step that ends the search: no candidate, no request.
- `_fail_policy` (line 66):
- `prove_theorem_agentic_stall` (line 71): `prove_theorem_agentic` plus the stall rule described in `runtime/stall.py`.
- `prove_theorem_agentic_stall_policy` (line 131): `prove_agentic.prove_theorem_agentic_policy`, verbatim (the Responses default, like the ACE policies: no chat archive).

## runtime/__init__.py

Omphalos runtime modules.


## runtime/admission_events.py

Small campaign-local adapter for auditable Delphyne budget decisions.

- `computation_started` (line 18):
- `record` (line 24): Append one compact event when the active campaign requested it.

## runtime/campaign_budget.py

Opt-in, process-safe admission and receipts for paid ACE campaigns.

- `CampaignExhausted` (line 36): No more requests can be admitted within a campaign allocation.
- `Ledger` (line 40):
- `CampaignResponsesModel` (line 244): Responses transport with one visible, reserved HTTP attempt.
- `for_campaign` (line 416): Wrap only explicitly opted-in Responses campaigns.

## runtime/campaign_embeddings.py

Budgeted embedding calls for ACE, with the ordinary cache unchanged.

- `CampaignEmbeddingModel` (line 29):
- `embedding_model` (line 78):

## runtime/continuation_output.py

Version-2 structured continuation transport, shared by both harnesses.

- `final_message_response` (line 23):
- `ContinuationResponsesModel` (line 56): Opt-in final-message selection; inherited dispatch settles once.

## runtime/development_only.py

Opt-in process guard for the authorized development-only campaign.

- `forbidden` (line 16):
- `install` (line 37):

## runtime/grounded_control.py

Opt-in bounded ACE controls built on Delphyne spending streams.

- `DecisionControl` (line 27):
- `limited_prompt` (line 35):
- `claim_recovery` (line 61):
- `controlled_prompt` (line 74):
- `observe_budget` (line 111): Record the final parent decision, including pending reservations.

## runtime/model_registry.py

Model resolution and pricing for the omphalos baselines.

- `_per_million` (line 103):
- `_require_exact_pricing` (line 160):
- `current_pricing_date` (line 182): Today, as the default "as of" for pricing questions.
- `pricing_for` (line 192): Resolve a model name to the rate in force on a given date, or raise.
- `stdlib_fallback_pricing` (line 231): The rate the *stdlib* would infer for this name, or `None`.
- `price_tokens` (line 248): Cost of a token count at the rate in force on `on` (default today).
- `make_model` (line 278): Resolve a model name to an LLM with *correct* pricing.

## runtime/paths.py

Stable paths shared by Omphalos packages and both agent harnesses.


## runtime/pytanque_utils.py

Pytanque bridge and miniF2F problem parser used by the Delphyne baseline.

- `_pytanque_session` (line 59): A petanque session for `abs_file` (the augmented path). Transport and server lifecycle — private warm `pet-server` per process with deadlines, reply caps, memory bounds and recycling, or the archived STDIO transport under `OMPHALOS_PET_MODE=stdio` — live in `rocq_server`; this module only asks questions through the client.
- `_memo_purge_stale` (line 89): Drop entries of dead server generations. A recycle already invalidates them implicitly (the generation is in the key), but without the purge they kept occupying the LRU and evicting live entries — one archived process reached generation 75 against a 1024-entry cap. Runs only when the generation actually changed.
- `_memo_enabled` (line 105):
- `_memo_key` (line 110):
- `_memo_put` (line 116):
- `_memo_longest_prefix` (line 127): `(k, state)` for the longest memoised prefix `tactics[:k]`, else `(0, None)`.
- `prefix_memo_size` (line 140): Entries currently memoised (for tests and the timing harness).
- `_Replay` (line 146): Outcome of opening a theorem and replaying a tactic prefix — the shared core of `_replay_prefix` (previews) and `_check_against` (verification), which used to duplicate the loop.
- `_open_and_replay` (line 168): Open `theorem_name` in `abs_file` and run `tactics` in order from the longest memoised prefix. With `stop_when_finished` (previews), stop as soon as the proof is closed — verification instead runs every tactic and lets Rocq reject tactics after the goal is gone, exactly as before.
- `_resolve` (line 221): Resolve a problem-file path against the omphalos workspace root.
- `ProblemSpec` (line 230):
- `Feedback` (line 250): Result of verifying a proof script (see `check`).
- `_strip_comments` (line 284): Remove `(* ... *)` comments, honouring Rocq's nesting.
- `_preamble_definitions` (line 304): Everything a problem file declares before its theorem, minus the import/scope lines that `ProblemSpec.imports` already carries.
- `_extract_section` (line 323):
- `parse_problem` (line 342): Parse a miniF2F problem file into a `ProblemSpec`.
- `_parse_problem_uncached` (line 371):
- `split_into_tactics` (line 411): Turn an LLM-emitted proof script into a list of tactic strings (each ending in `.`). Defensive against:   - fenced code blocks (```rocq ... ```)   - a leading `Proof.` / trailing `Qed.` / `Admitted.` / `Defined.`   - blank lines and a trailing unterminated fragment.
- `_safe_goals` (line 461):
- `_augmented_file` (line 487): Yield the path pytanque should be pointed at: the stable copy of `file` with `extra_imports` prepended (`rocq_server.augmented_path` — outside the miniF2F `_CoqProject` whitelist, byte-identical to the temp copies of the archived runs, and stable so the warm server reuses its document), or `file` itself if there is nothing to prepend.
- `GoalCaps` (line 502): Runaway-goal guard (a *treatment*, pre-registered separately; the default everywhere is `None` = the archived behaviour). A failed script can leave hundreds of open goals (`repeat constructor` on a long `NoDup` left 1128 in one validationX cell); the battery then probes every goal (17 tactics × up to 4 s each) and the feedback renders every goal (82 KB in one message). With caps, the battery probes the first `probe` goals, the feedback lists the first `render` goals (each cut at `render_chars` characters) followed by a marker line saying how many were hidden and how many were probed. Encoded inside the existing `Feedback` fields, so the cached output shape is unchanged.
- `_check_memo_enabled` (line 536): The in-process memo over full verification results, on unless `OMPHALOS_CHECK_MEMO=0`. The compute cache keys entries by occurrence index, so an agent repeating a byte-identical script re-pays the whole verification — 9.4% of the 74.8k archived compute calls are such repeats (`tools/analysis/compute_repeat_audit.py`), including failing tactics that re-pay `PROOF_TACTIC_TIMEOUT` each time. Verdicts are deterministic (the audit found divergence only on transport/resource failures, 7 groups in 74.8k calls), and results are stored only for calls the transport survived untouched.
- `check_memo_size` (line 551): Entries currently memoised (for tests and the timing harness).
- `clear_check_memo` (line 556): Empty the check-result memo. For tests and harnesses whose point is *re-execution* (transport parity, cold-run agreement): a repeat served from the memo would make them vacuous.
- `check` (line 565): Open a Pytanque session, replay `tactics` against the theorem, attempt a final `Qed.`, and return structured feedback.
- `check_assisted` (line 641): `check` with automation-assisted verification enabled. Kept as a named top-level entry point so strategies can pass it to `dp.compute(...)` directly. Strategies pass `goal_caps` only when set, so the compute cache keys of archived runs are untouched.
- `inspect_at` (line 658): Replay a tactic prefix from the initial proof state of `theorem_name` in `file` (without committing), then run an optional introspection command (`Search ...`, `Check ...`, ...) *at the resulting state* and return a human-readable report.
- `_split_focus` (line 752): `([focus tokens], remainder)` — the leading bullet/brace tokens of a sentence, each a complete Rocq proof step of its own, and what is left (possibly empty). `"- { nia. }"` -> `(["-", "{"], "nia. }")`; the trailing `}` stays with the remainder, where it is harmless (closing a brace cannot diverge).
- `_run_guarded` (line 779): `client.run` with the timeout actually enforced.
- `try_automation` (line 814): Replay a tactic prefix from the initial proof state of `theorem_name` in `file`, then try a battery of cheap closing tactics (`AUTOMATION_BATTERY`) on *each* remaining subgoal and report which subgoal closes with what.
- `try_tactics` (line 846): Replay a tactic prefix from the initial proof state of `theorem_name` in `file` (without committing), then evaluate each of `candidates` independently against that same held state and report the per-candidate outcome.
- `query` (line 901): Run a Rocq introspection command (`Search ...`, `Check ...`, `Print ...`, `About ...`, `SearchPattern ...`) against the initial proof state of `theorem_name` in `file`, and return the formatted feedback as a string.
- `_replay_prefix` (line 929): Open the theorem and replay a tactic prefix. Returns `(state, report)` where exactly one of the two is `None`: a non-`None` report is a preformatted error / "PROOF FINISHED" string that should be returned to the agent as-is.
- `_inspect_against` (line 972): Inner implementation of `inspect_at`: replay the prefix, then run the introspection command at the resulting state (if provided) and report its output together with the goals at that state.
- `_automation_against` (line 1031): Inner implementation of `try_automation`: replay the prefix, then probe each remaining subgoal with the automation battery using goal selectors (`2: lia.`), recording the first closing tactic per goal.
- `_CandidateOutcome` (line 1065): Outcome of evaluating one `try_tactics` candidate.
- `_try_tactics_against` (line 1074): Inner implementation of `try_tactics`: replay the prefix once, then run every candidate off that one held state (pytanque states are functional, so candidates never see each other's effects) and collect a `_CandidateOutcome` per candidate.
- `_run_candidate` (line 1143): Run one candidate's sentences sequentially from `state` (which is left untouched) and classify the outcome. The `except Exception` breadth matches `_probe_goals`: rejections and timeouts both count as the candidate failing.
- `_format_try_tactics_report` (line 1184):
- `_probe_goals` (line 1273): Try the automation battery on each of the `n` goals of `state` (via goal selectors), returning the first closing tactic per goal, or `None` for goals the battery cannot close. With `goal_cap`, only the first `goal_cap` goals are probed and the list is that short.
- `_apply_closers` (line 1324): Apply one closing tactic per goal, in *descending* goal order so earlier closures do not renumber later goals. Returns the final state and the exact tactic sentences applied, or `None` if a closer unexpectedly fails on replay.
- `_format_automation_report` (line 1348):
- `_format_try_proof_finished` (line 1404):
- `_format_try_success` (line 1431):
- `_format_try_failure` (line 1461):
- `_query_against` (line 1503):
- `_format_feedback` (line 1528):
- `_check_against` (line 1541):
- `_cap_goals` (line 1601): The `remaining_goals` a capped `Feedback` reports: the first `caps.render` goals (each cut at `caps.render_chars`) and, when any was hidden, the `GOALS_TRUNCATED_MARKER` as a final entry.
- `_failure_feedback` (line 1627): Build the feedback for a failed / incomplete check. `state` is the last good state (i.e. after `proof_so_far`). With automation probing enabled, each remaining goal is probed with the battery; if every goal closes, the closers are applied (descending goal order) and `Qed.` is attempted — turning the failure into an `auto_finished` success.

## runtime/replay_admission.py

Opt-in, exact Responses replay state and terminal budget evidence.

- `PrefixGuard` (line 45):
- `PrefixCache` (line 59):
- `fingerprint` (line 75):
- `transport_state` (line 81):
- `restore_state` (line 94):
- `RecordedResponsesModel` (line 107):
- `recorded_model` (line 129):
- `RecordedCache` (line 140):
- `recorded_prompt` (line 215):
- `admission_observer` (line 240): Observe the enclosing Delphyne budget after it decides each barrier.

## runtime/rocq_server.py

Transport and lifecycle for the Rocq (petanque) bridge.

- `pet_mode` (line 79): Transport selected by `OMPHALOS_PET_MODE`, read at call time so a worker initializer can set it after import. Default: `socket`.
- `_env_int` (line 92):
- `_env_float` (line 97):
- `Settings` (line 103): Bounds for the private server. Every field has an environment override (`OMPHALOS_PET_*`) so launches can tune them without code changes; `configure` sets them programmatically.
- `TransportError` (line 181): A failure of the *channel* to Rocq rather than of Rocq itself. A `PetanqueError` subclass so every existing `except PetanqueError` in the bridge renders it as tool feedback.
- `Deadline` (line 198):
- `ReplyTooLarge` (line 202):
- `ConnectionLost` (line 206):
- `ServerUnavailable` (line 210):
- `BoundedPytanque` (line 226): Socket-mode `Pytanque` with a byte cap on replies and a deadline on every RPC. Any transport failure poisons the client (it must not be reused: the server may still be computing the old request) and is reported to `on_failure` before being raised.
- `augmented_path` (line 393): The path pytanque is pointed at for `file` with `extra_imports` prepended: a copy under `AUG_DIR/<digest>/<name>`, byte-identical to the temp copy the previous implementation wrote (same preamble, same line numbers, same error messages), but *stable*: the same inputs map to the same path, so a warm server reuses its document.
- `_Server` (line 446):
- `ServerStats` (line 459):
- `_which` (line 471): `shutil.which`, cached: `_spawn` used to re-scan PATH per spawn.
- `_free_port` (line 476):
- `mem_available_mb` (line 482): `MemAvailable` from /proc/meminfo, in MB (None off Linux).
- `_rss_mb` (line 494):
- `PetServerManager` (line 505): Owner of this process's private `pet-server`. `session()` is the only entry point the bridge uses; everything else is lifecycle.
- `_stdio_session` (line 825): One fresh `pet` subprocess, cwd `.rocq_cache/` (archived transport).
- `configure` (line 848): `MANAGER.configure`, exported for worker initializers.

## runtime/runtime_profiles.py

Resolved, hashable ACE launch settings; no change to legacy launches.

- `RuntimeProfile` (line 15):
- `resolve` (line 61):

## runtime/skills.py

Rocq skill-pack index and loader for the agentic baseline.

- `list_skills` (line 54): Return `{skill_name: one-line description}` for every whitelisted reference. The description is the first non-empty, non-heading line of the file (truncated). Used to render the available-skills table in the agentic system prompt.
- `read_skill` (line 67): Return the full markdown content of a whitelisted skill, or a clear error string if the name is unknown or the file is missing. The return value is shown verbatim to the LLM as the `ReadSkill` tool result, so error strings should be self-explanatory.
- `_description` (line 85):

## runtime/stall.py

Stall rules: stop a proof search that has stopped making progress.

- `VerdictView` (line 53): What a stall rule may look at, per rejected proposal.
- `goal_key` (line 71): The conclusion of one rendered goal, whitespace-normalised: the text after the last `|-`, or the whole goal when there is none.
- `view_of_feedback` (line 78): `None` for a success (successes end the search anyway).
- `views_of_prefix` (line 94): The verdicts an `interact` prefix carries, in order: every feedback message whose meta is a verifier `Feedback`.
- `_flags` (line 109): Per verdict, whether it counts as *no progress* under `rule`.
- `stalled` (line 128): Whether the last `k` rejections all show no progress.
- `stop_after` (line 136): The number of rejected verdicts after which the rule first fires (the search then issues no further request), or `None`. Exactly what `stalled` decides step by step, so the offline replay and the live strategy agree by construction.

## runtime/tool_budget.py

Opt-in whole-operation Rocq budgets, usable by both agent harnesses.

- `ToolLimits` (line 16):
- `OperationExhausted` (line 31): No remaining allowance; this is not a logical rejection.
- `Operation` (line 36):
- `operation` (line 69):
- `clamp_timeout` (line 80):
- `clip_utf8` (line 85):

## tools/analysis/__init__.py

Omphalos tools analysis modules.


## tools/analysis/ace_diagnosis.py

Where a playbook's effect goes: turn tax, per-request tax, citations.

- `cells_of` (line 90): Verdicts grouped by cell, in cache (chronological) order.
- `TurnProfile` (line 99):
- `turn_profile` (line 143):
- `Rates` (line 192):
- `PerRequest` (line 208): Pooled per-request token and dollar figures over a set of cells.
- `per_request` (line 236):
- `PairedCost` (line 262):
- `_records` (line 321):
- `paired_cost` (line 333):
- `Turn` (line 413): One generator message and the verdict that followed it, if any.
- `turns_of_cache` (line 422):
- `BulletUse` (line 474):
- `CitationAudit` (line 495):
- `citation_audit` (line 531):
- `Transition` (line 587): A rejection, the hints its feedback carried, and what came next.
- `transitions_of_cache` (line 598): Walk a cell: verdict → feedback message (with or without hints) → next verdict. Tool-call rounds between them are skipped; the feedback for verdict t is the last user/tool message of the next generator request.
- `HintAudit` (line 681):
- `hint_audit` (line 716):
- `render_hint_audit` (line 752):
- `trigger_coverage` (line 782): Which baseline failures each bullet would have fired on (`ace_triggers.coverage`, with the recorded goals).
- `_counter_lines` (line 801):
- `render_profile` (line 810):
- `_m` (line 839):
- `render_cost` (line 843):
- `render_citations` (line 882):
- `render_coverage` (line 903):
- `_resolve` (line 915):
- `main` (line 920):

## tools/analysis/ace_power.py

Exact illustrative power for independent paired binary observations.

- `power` (line 18):

## tools/analysis/analyze_probing.py

Post-hoc analysis of the "probing" toolset sweeps.

- `_norm` (line 56):
- `TryTacticsCall` (line 61): One TryTactics invocation and its parsed report.
- `ConfigAnalysis` (line 77): Everything extracted from one config's cache + summary row.
- `_load_summary` (line 97): Map `{bench}__seed{seed}` to the summary row.
- `_conversation` (line 106): Slice off the system message and the few-shot example pairs: the real conversation starts at the *last* instance user message.
- `_parse_report` (line 127):
- `_useful_candidates` (line 138): Candidates the report marks as applying or finishing.
- `_analyze_config` (line 148):
- `_analyze_arm` (line 259):
- `_pct` (line 275):
- `_arm_summary` (line 279):
- `_trytactics_summary` (line 312):
- `main` (line 352):

## tools/analysis/bench_ace_runtime.py

CPU-only concurrency sweep on a fixed, archived trainX workload.

- `replay` (line 45):
- `main` (line 57):

## tools/analysis/bench_rocq.py

Per-call timing of the Rocq bridge, per transport mode (offline).

- `_worker` (line 43): Child body: replay every bridge call of one cache, print JSON.
- `main` (line 87):

## tools/analysis/bridge_parity.py

Byte-for-byte parity of the Rocq bridge against archived compute calls.

- `Outcome` (line 76):
- `_loader` (line 84):
- `_compute_entries` (line 88): `(fun, args, archived_output)` for every bridge compute entry.
- `_normalise_paths` (line 112):
- `_classify` (line 117):
- `run_config` (line 142):
- `main` (line 159):

## tools/analysis/budget_ablation.py

Offline ablation of the per-problem budget, from recorded runs.

- `Trace` (line 108): One config's billed requests, in the order the run issued them.
- `_billed_prices` (line 146): Per-request prices from a run's cache, in issue order.
- `_config_names` (line 205): Map a config's identifying parameter values to its directory name.
- `_key_fields` (line 256): The parameter names that identify a config within a run.
- `_norm` (line 274): `""` for a missing/default value; numbers compared by value.
- `_config_key` (line 289): The fields that together identify one config within a run.
- `load_run` (line 296): Load every config of one experiment dir as a `Trace`.
- `Point` (line 361): Aggregate outcome of one run under one budget setting.
- `evaluate` (line 373):
- `smallest_lossless_cap` (line 386): Smallest cap in `caps` that costs this run nothing in solves.
- `build_table` (line 403):
- `render` (line 438):
- `main` (line 504):

## tools/analysis/cell_records.py

Ground-truth cell records of an experiment directory (no CSV needed).

- `CellRecord` (line 48):
- `_field` (line 80):
- `_result_head` (line 85):
- `_price` (line 98):
- `_done_record` (line 107):
- `_failed_record` (line 138): A platform-failed cell: unsolved; spend from the surviving cache.
- `cells_of_run` (line 185):

## tools/analysis/compute_repeat_audit.py

Audit repeated identical compute calls in archived experiment caches.

- `_compute_entries` (line 35): `(request_content, output_repr)` for every `__compute__` entry.
- `audit_dir` (line 59): `(calls, repeated_calls, divergent_groups, divergent_names)`.
- `main` (line 81):

## tools/analysis/decision_audit.py

Offline re-audit of the design decisions recorded in `PROGRESS.md`.

- `_min_discordant_for_significance` (line 72): Smallest number of discordant problems that can reach `SIGNIFICANCE` when *all* of them fall the same way.
- `Arm` (line 100): One measured configuration: an experiment directory, optionally narrowed to the rows matching a set of summary-column values.
- `Outcome` (line 126): Per-problem results of one arm.
- `load_arm` (line 167): Read one arm's per-problem outcomes, or `None` if not on disk.
- `sign_test` (line 202): Exact sign test on discordant pairs (the exact form of McNemar's).
- `Comparison` (line 230): Result of pairing two arms over their shared problems.
- `compare` (line 258):
- `Decision` (line 284): One design decision from `PROGRESS.md`, with the evidence that was actually offered for it and the arms needed to re-test it.
- `_toolsets` (line 311):
- `_prev` (line 315):
- `_out` (line 319):
- `Evaluated` (line 705): A decision together with whatever the archived data says.
- `evaluate` (line 761): Resolve a decision's arms and pool their discordant problems.
- `verdict_of` (line 783): Score a decision against its own claim.
- `noise_floor` (line 843): Measure run-to-run disagreement from same-config replicates.
- `check_model_selection` (line 875): Re-run the canonical-model rule (D8) from token counts.
- `robustness_note` (line 904): Check that no verdict depends on using a two-sided test.
- `render` (line 932):
- `render_markdown` (line 956):
- `main` (line 988):

## tools/analysis/failure_analysis.py

What the prover actually gets wrong, from recorded runs.

- `ErrorClass` (line 70): One bucket of the taxonomy, matched against the Rocq error.
- `classify` (line 199): Bucket one Rocq error message, or `other` if nothing matches.
- `refine_class` (line 211): `classify`, then the finer `FINE_TAXONOMY` reading of `other`.
- `Verdict` (line 242): One verifier result recovered from a cache.
- `_feedback_entries` (line 263): Every `check` / `check_assisted` verdict in one config's cache.
- `load_run` (line 300): Recover every verdict in an experiment directory.
- `Tally` (line 372): Counts for one error class within one run.
- `tally` (line 383):
- `_short` (line 402): One-line form of a Rocq error, with the noise stripped.
- `render_run` (line 410):
- `render_compare` (line 452): Side-by-side taxonomy, plus the set comparison that matters more: which problems each configuration never solved.
- `main` (line 504):

## tools/analysis/goal_cap_audit.py

Offline audit for the runaway-goal treatment (`pytanque_utils.GoalCaps`).

- `CheckStats` (line 39):
- `_loader` (line 47):
- `scan_config` (line 51):
- `_solved` (line 82):
- `main` (line 98):

## tools/analysis/grounded_failure_audit.py

Read-only analysis of the completed bounded campaign, without APIs/Rocq.

- `digest` (line 32):
- `zero_work` (line 36):
- `short_compute` (line 41):
- `reservation_probe` (line 45):
- `main` (line 62):

## tools/analysis/paired_evaluation.py

Complete-cell, family-clustered evaluation with actual-cost cutoffs.

- `Observation` (line 27):
- `exact_cluster_p` (line 37):
- `compare` (line 53):
- `cost_cluster_p` (line 188): Two-sided paired sign-flip test on family cost differences.

## tools/analysis/replay_with_budget.py

Re-run an archived sweep under a tighter budget, entirely from cache.

- `Replayed` (line 76): Outcome of one config replayed under a tighter budget.
- `_spent` (line 114): Pull one metric out of a run's reported `spent_budget`.
- `stored_params` (line 120): The configs an experiment actually ran, keyed by config name.
- `_rebuild_config` (line 146): Turn a stored parameter dict back into a real `AgenticConfig`.
- `replay_config` (line 169): Replay one archived config with `max_dollar_budget` set to `cap`.
- `replay_run` (line 224): Replay every config of one run under the given cap.
- `report` (line 253):
- `main` (line 290):

## tools/analysis/reprice.py

Offline recomputation of experiment costs from recorded token counts.

- `Usage` (line 92): Token counts of one config, plus the price it was billed at.
- `RunReport` (line 174): Aggregated recorded vs recomputed cost of one experiment dir.
- `_mapping` (line 211): Narrow a value parsed from YAML to a mapping, or `None`.
- `_require_mapping` (line 216):
- `_require_int` (line 223):
- `usage_from_result` (line 230): Read one config's `result.yaml`. Returns `None` for configs that recorded no budget (an exception before the first request), which contribute nothing to spend.
- `run_date` (line 269): The day a run was executed, from its own `experiment.yaml`.
- `_label` (line 300): A cell's label: its bench name, or — for the one-config role experiments that have none (the 2026-09-05 trigger assigner and repair writer, keyed by playbook) — the playbook file, so the guard never trips on a directory that has nothing to do with a benchmark problem.
- `usages_from_summary` (line 311): Read a `results_summary.csv`. Equivalent to reading every `result.yaml`, since the summary carries the same token columns — but it is what the documented totals were computed from, and it is the file `--write` corrects.
- `discover_runs` (line 340): Experiment dirs are the ones holding a `configs/` subdirectory.
- `collect` (line 345): Aggregate one experiment dir, preferring its summary CSV and falling back to the per-config `result.yaml` files when it has none (some runs were never summarized).
- `write_repriced_summary` (line 378): Emit `results_summary.repriced.csv` beside the run's summary: same rows and columns, `price` corrected, and the original preserved as `price_as_billed`. Returns `None` if the run has no summary.
- `print_table` (line 415):
- `main` (line 442):

## tools/reports/__init__.py

Omphalos tools reports modules.


## tools/reports/ace_applicability_report.py

Immutable preparation and complete-panel applicability reports; no API calls.

- `digest` (line 58):
- `read` (line 62):
- `source` (line 66):
- `check_state` (line 111):
- `prepare` (line 138):
- `seal` (line 305):
- `stage_a_gate` (line 342):
- `accounting` (line 408):
- `report` (line 459):

## tools/reports/ace_attribution_admission.py

Offline lower-bound probe of the first unobserved model admission.

- `ProbeComplete` (line 30): The next estimate is recorded; never try to answer its request.
- `probe` (line 34):
- `main` (line 112):

## tools/reports/ace_attribution_diagnosis.py

Offline explanatory appendix for the fixed ACE attribution campaign.

- `outcome_head` (line 27): Read result metrics and avoid loading duplicate raw traces.
- `event_index` (line 50):
- `include_diagnostic_metadata` (line 60): Attach registered source/receipt facts to the small diagnostic arms.
- `execution_inventory` (line 77): Check actual exported arguments against every registered proof cell.
- `reprice_registered` (line 130): Reprice exact runs; shallow CLI discovery misses nested main arms.
- `profile` (line 165):
- `pricing_sensitivity` (line 213): Accounting decomposition; no alternative run or changed receipts.
- `comparative_supplement` (line 236): Expose fixed-panel pairings and secondary model contrasts.
- `enriched_cases` (line 308):
- `bullet_source_groups` (line 372): Earliest batch provenance, not a claim about one causal source.
- `candidate_references` (line 386): Extract identifiers even when they appear inside longer code spans.
- `book_audit` (line 400):
- `training_accounting` (line 523):
- `training_evolution` (line 562): Final-book provenance and role reliability, retaining every step.
- `training_traces` (line 608):
- `write_appendix` (line 634):
- `plots` (line 731):
- `main` (line 791):

## tools/reports/ace_attribution_report.py

Development-only ACE attribution audit and complete-cell reports.

- `args_of` (line 33):
- `preflight` (line 43): Replay every observed request, never the unobserved next request.
- `metrics` (line 148):
- `directory_for` (line 167):
- `observations` (line 181):
- `interaction` (line 209):
- `cache_diagnosis` (line 249):
- `report` (line 352):

## tools/reports/ace_cap_report.py

Paired ACE-vs-baseline comparison as a function of the dollar cap.

- `_cells` (line 62):
- `main` (line 71):

## tools/reports/ace_capacity_inventory.py

Verify explicit experiment records, reconcile receipts and hash artifacts.

- `hashes` (line 36):
- `main` (line 46):

## tools/reports/ace_capacity_plots.py

Standalone research figures from frozen capacity-study reports.

- `main` (line 14):

## tools/reports/ace_capacity_preflight.py

HTTP-forbidden compatibility checks before the capacity campaign.

- `main` (line 21):

## tools/reports/ace_capacity_quality.py

Matched creator-output audit with development-only Rocq source checks.

- `strings` (line 29):
- `locate` (line 41):
- `main` (line 59):
- `contextual_audit` (line 172):
- `terminal_evidence` (line 221):

## tools/reports/ace_capacity_replay.py

Exact HTTP- and Rocq-disabled replay of registered new measurements.

- `replay` (line 31):
- `main` (line 160):
- `audit_admissions` (line 215): Compare every estimate, budget decision and terminal against live.

## tools/reports/ace_capacity_report.py

Explicit-inventory analysis of the capacity campaign; no API calls.

- `read_cell` (line 34):
- `events_by_cell` (line 111):
- `diagnostics` (line 122):
- `metric` (line 157):
- `compare` (line 203):
- `interaction` (line 255):
- `crossover` (line 304):
- `mechanism_rows` (line 373):
- `mechanisms` (line 407):
- `role_audit` (line 472):
- `main` (line 538):

## tools/reports/ace_capacity_synthesis.py

Produce development-only case appendices and resource/price summaries.

- `short` (line 19):
- `describe` (line 23):
- `feedback_exposure` (line 53):
- `pricing` (line 64):
- `verify_path_costs` (line 111):
- `causal_exposure_audit` (line 134):
- `write_cases` (line 176):
- `write_creators` (line 292):
- `main` (line 332):

## tools/reports/ace_mechanisms_audit.py

Read-only failure/trigger audit of the approved mechanism panels.

- `checks_of` (line 24):
- `summarize` (line 51):
- `main` (line 146):

## tools/reports/ace_polish_report.py

Train-only preparation and complete-panel readout; no paid calls.

- `checks` (line 47):
- `source_hashes` (line 71):
- `prepare` (line 92):
- `charged_cells` (line 266):
- `seal` (line 276): Seal final implementation after offline checks, before any payment.
- `navigation` (line 292): Add executable paths and one unsafe-action rejection to the demos.
- `serialization_demos` (line 350): Convert existing training role examples to the new typed contracts.
- `accounting` (line 386): Reconcile each settled receipt with its own dated token usage.
- `observations` (line 425):
- `freeze` (line 463):
- `report` (line 535):

## tools/reports/ace_report.py

Pair the ACE-playbook validation arm against the frozen baseline.

- `_field` (line 69):
- `_load` (line 75): `(solved, recomputed dollars)` per problem-seed cell.
- `main` (line 107):

## tools/reports/ace_report_data.py

Regenerate the data blocks embedded in `report/ace_report.html`.

- `_cells` (line 63): `(bench, seed) -> {solved, cost, output, input, cached}`.
- `build_paired` (line 92): Per-cell baseline-vs-ACE costs, plus the paired statistics.
- `_trace_cells` (line 158):
- `build_caps` (line 167): Solves and spend against the per-problem dollar cap, both arms, paired per cell. Exact: a capped run is a prefix of a recorded one.
- `build_taxonomy` (line 204): Rocq error classes by problems affected, both arms.
- `build_adapt` (line 222): Playbook size per adaptation step, per variant.
- `build_defs` (line 276): The definitions-visible arm against its paid control cells.
- `rewrite` (line 302): Replace each `const NAME = ...;` line in the report's script.
- `main` (line 324):

## tools/reports/ace_review_report.py

Registered decisions and complete-cell reports for the ACE review.

- `freeze` (line 36):
- `panel` (line 47):
- `expected` (line 117):
- `require_complete` (line 121):
- `calibrated_requests` (line 126):
- `calibration` (line 132):
- `selection` (line 157):
- `final_report` (line 208):
- `training_diagnostics` (line 313):
- `main` (line 343):

## tools/reports/ace_x_report_data.py

Chart data for `report/ace_x_report.html` — the ACE v2 study on the X
partitions, plus the solves-vs-cost evolution of the agentic prover.

- `_cost` (line 94):
- `_rows` (line 106):
- `_config_names` (line 114): `bench__...` directory name per (bench, seed) via experiment.yaml.
- `_cells_of` (line 123): `arm -> (bench, seed) -> {solved, cost, input, cached, output, requests, platformFailed}` for every recorded cell of the run whose arm matches, from ground truth (`cell_records`): done cells and platform-failed cells (scored unsolved), never `todo` ones.
- `_records_of` (line 142):
- `_traces` (line 155):
- `_curve` (line 172):
- `build_evolution` (line 231): Solves vs spend at every cap, per generation, original test set.
- `_playbook_labels` (line 253): sha8 -> frozen playbook file name.
- `_arm_label` (line 263):
- `_provenance_rv` (line 271):
- `_qualified_label` (line 280): Label of an evaluated arm: the playbook stem (+ `(topK)`), then ` · rv{N}` when the cells were rendered at a version other than the one the playbook was adapted under, then ` · replicate{i}` when the same (playbook, rv, injection) was already labelled from an earlier directory — an identical-config rerun, which is noise-floor evidence, not a new arm.
- `_x_arms` (line 309): Every arm on one X partition: `label -> {cells, kind}`.
- `_partition` (line 351):
- `_serialise_cells` (line 360):
- `build_x_arms` (line 376):
- `_pair` (line 399): Paired readout. Platform-failed cells count as unsolved (the conservative reading); `dropFailed` repeats the readout on the cells that completed on both sides (the pre-2026-08-26 behaviour), so a reader can see whether the failures moved anything.
- `build_x_paired` (line 481):
- `build_x_caps` (line 496):
- `build_x_adapt` (line 557):
- `build_x_taxonomy` (line 629):
- `_tally` (line 666):
- `build_x_cost` (line 677): Adaptation spend by role per variant; evaluation-stage tokens.
- `_find_pair` (line 746):
- `_delta` (line 751):
- `_adapt_stats` (line 764):
- `_collapse` (line 768):
- `_paper_row` (line 783):
- `_direction` (line 803): `(assessment, status)` of one paired arm against the paper's sign.
- `_gap` (line 822): Compare two arms' deltas vs baseline: `(text, assessment, status)`.
- `build_x_paper` (line 843): The paper's experiment matrix mapped onto our arms, computed from the paired blocks. Rows whose arm has not run say so (`pending`); rows we deliberately do not run say so (`not-run`); rows that are a property of the implementation rather than an experiment are `disclosed`.
- `build_x_audit` (line 1058): The 2026-08-26 audit of our implementation against the reference.
- `_family` (line 1256):
- `_partition_files` (line 1262):
- `_baseline_solves` (line 1271):
- `build_bench` (line 1296): Composition of the original 20-problem partitions and the 40-problem X partitions (family counts, competition share) with the canonical luna baseline's solves on each — the motivation for the X partitions.
- `build_meta` (line 1375):
- `rewrite` (line 1390):
- `build_all` (line 1406):
- `main` (line 1423):

## tools/reports/change_control_report.py

Frozen trainX preparation and accounting; no model/API calls.

- `digest` (line 51):
- `read` (line 55):
- `prepare` (line 59):
- `seal` (line 199):
- `receipt_rows` (line 243):
- `result_of` (line 266):
- `paired` (line 293):
- `primary_gate` (line 325):
- `holm` (line 346):
- `report` (line 357):
- `main` (line 585):

## tools/reports/control_cycle_report.py

Offline readout for the registered bounded ACE control cycle.

- `receipts` (line 27):
- `historical` (line 37):
- `main` (line 50):

## tools/reports/coverage_audit.py

Compact failure observations, not new evaluation or automatic repairs.

- `audit` (line 18):

## tools/reports/coverage_cycle_audit.py

Read only allowlisted development panels; no aggregate archive scans.

- `cached` (line 26):
- `preflight` (line 53):
- `audit` (line 128):

## tools/reports/cvt_report.py

Pair the `convert_user_feedback_to_tool` arms of `luna_cvt_ablation`.

- `_field` (line 59):
- `_load` (line 65): `(solved, recomputed dollars)` per problem-seed cell for one arm.
- `main` (line 93):

## tools/reports/export_ace_review.py

Export the completed ACE review's billing and operational evidence.

- `write_frozen` (line 26):
- `exception_class` (line 35):
- `main` (line 53):

## tools/reports/freeze_control_cycle.py

Freeze the train-derived artifact and output limit before candidate runs.

- `digest` (line 23):
- `successful_output_limit` (line 27):
- `main` (line 42):

## tools/reports/frontier_report.py

Cost/performance frontier report for the train-partition gpt-5.6
sweeps.

- `BaselineStats` (line 46):
- `load_stats` (line 64): Aggregate a results_summary.csv per model name.
- `input_price` (line 78):
- `pick_canonical` (line 82): Most agentic successes per dollar, ties to the cheaper tier.
- `_fmt_row` (line 103):
- `main` (line 113):

## tools/reports/grounded_report.py

Prepare, freeze and report the bounded ACE campaign; never calls an API.

- `write_new` (line 32):
- `panel` (line 41):
- `receipts` (line 116):
- `observations` (line 127):
- `diagnostics` (line 151):
- `execution_hashes` (line 197):
- `freeze` (line 225):
- `families` (line 310):
- `final` (line 336):

## tools/reports/plot_ace_review.py

Render frozen ACE results as a thesis-ready PNG/PDF effect figure.

- `main` (line 25):

## tools/reports/report_chart_data.py

Regenerate the chart data embedded in the cost report.

- `_billed` (line 115): Per-request prices from a cache, in issue order.
- `_rows` (line 150):
- `_traces` (line 158):
- `_curve` (line 174): Spend and solves at each cap, under Delphyne's `with_budget` rule: a request is denied only once the already-spent amount reaches the cap, so the request that crosses the line still runs.
- `_any_row` (line 201): Keep every row (the arm occupies its output dir alone).
- `_is_terra` (line 206):
- `_is_low` (line 210): The winning Responses arm: effort `low`, feedback→tool left on.
- `_is_luna_canonical` (line 218): The canonical luna arm: `core`, effort `medium`, first seed.
- `build_curves` (line 227): The agentic frontier: three configurations per partition.
- `_partition_of` (line 256): Map every benchmark problem to the partition it belongs to.
- `_key_of` (line 268): Identity of one config, matching `_config_dir_names`.
- `_config_dir_names` (line 280): Map config identity to directory name, read from `experiment.yaml`.
- `_no_nocvt` (line 315): Agentic Responses rows that kept the feedback conversion on.
- `_baseline_arm` (line 320): Which API arm a `baseline_api` row belongs to.
- `build_baseline` (line 356): Baseline API comparison: cost against problems solved, as the feedback budget grows from one request to four.
- `build_effort` (line 435): Spend and solves against reasoning effort.
- `build_taxonomy` (line 484): Problems affected by each error class, per configuration.
- `rewrite` (line 511): Replace each `const NAME = …;` line in the report's script.
- `main` (line 533):

## tools/reports/responses_report.py

Compare the Responses-API arms against the Chat Completions control.

- `Breakdown` (line 76): Where an arm's money went, and how much of it was reasoning.
- `_reasoning_tokens` (line 103): Reasoning tokens a config spent, summed over its billed requests.
- `breakdown` (line 137): Split an arm's spend by token class and count its reasoning tokens.
- `ControlOutcome` (line 172): The Chat Completions arm an experiment is judged against.
- `load_control` (line 188): The Chat Completions arm each Responses run should be judged against.
- `_as_outcome` (line 235): Wrap the control CSV so `compare` can pair against it.
- `verdict` (line 246): Apply the rule fixed before the arms were run.
- `collect_arms` (line 283): Every arm present in a Responses output dir, keyed by its label.
- `render` (line 313):
- `main` (line 374):

## tools/reports/stall_report.py

Stall rules replayed exactly on recorded runs — the measurement.

- `Cell` (line 68):
- `_load_cell` (line 103):
- `load_run` (line 166):
- `RunUnderRule` (line 197):
- `apply_rule` (line 240):
- `grid` (line 261):
- `select` (line 269): The pre-registered choice: no solve lost, then the largest spend saved, ties to the larger k (the more conservative rule).
- `render_grid` (line 279):
- `render_check` (line 294):
- `PairedUnderRule` (line 310):
- `pair_under_rule` (line 336):
- `render_pair` (line 380):
- `parity` (line 403): For a directory produced by `prove_theorem_agentic_stall` under (rule, k): every cell must have issued exactly the proposals the replay predicts and no request after the predicted stop. Returns the violations (empty = parity).
- `_resolve` (line 434):
- `main` (line 443):
