.PHONY: test test-standard test-agentic test-probing test-luna test-ace
.PHONY: test-rocq bridge-parity bench-rocq launch-status stop launches ace-x-status
.PHONY: ace-x3-val-offline ace-x3-val-noreflect ace-x3-val-mono ace-x3-online-s0
.PHONY: ace-x3-online-s1 ace-x3-e3-adapt ace-x3-e3-val ace-x4-adapt ace-x4-val-offline
.PHONY: ace-x4-online-s0 ace-x-matrix ace-x3-test-offline ace-x4-test-offline
.PHONY: ace-x3-strong-adapt ace-x3-strong-val ace-x5-adapt ace-x5-val-offline
.PHONY: ace-x3-strong-test ace-x5-test-offline
.PHONY: sweep-train sweep-train-standard sweep-train-agentic
.PHONY: sweep-validation sweep-test
.PHONY: sweep-probing-validation sweep-probing-test
.PHONY: summary-train summary-validation summary-test
.PHONY: summary-probing-validation summary-probing-test
.PHONY: replay-train-standard replay-train-agentic
.PHONY: reprice reprice-archive reprice-write decision-audit
.PHONY: budget-ablation budget-replay probe-responses responses-report
.PHONY: sweep-responses-train sweep-responses-validation sweep-responses-test
.PHONY: report-data sweep-luna-train luna-cap
.PHONY: sweep-luna-cvt cvt-report
.PHONY: regen-command-caches
.PHONY: ace-adapt ace-eval ace-report ace-test ace-cap ace-failures
.PHONY: ace-adapt-variant defs-arm test-unit ace-report-data
.PHONY: clean clean-experiments

# Parallel streams per launch (memory-bound at 4 on the 7.4 GB WSL box; the
# server has 219 GB, so `make WORKERS=16 sweep-...` or export WORKERS).
WORKERS ?= 4

# Single-problem smoke tests (cached; regenerate with
# `make regen-command-caches` after a prompt / strategy change).
test: test-unit test-rocq test-standard test-agentic test-probing test-luna test-ace test-ace-trig test-stall

# Pure Python: no API calls, no Rocq server. Guards the deterministic
# merge and the generated adaptation pool against silent drift.
test-unit:
	python -m tests.test_grounded
	python -m tests.test_campaign_budget
	python -m tests.test_paired_evaluation
	python -m tests.test_ace_repair_loop
	python -m tests.test_ace_playbook
	python -m tests.test_ace_driver
	python -m tests.test_ace_evidence
	python -m tests.test_ace_triggers
	python -m tests.test_ace_diagnosis
	python -m tests.test_ace_repairs
	python -m tests.test_stall
	python -m tests.test_parse_problem
	python -m tests.test_launch_state
	python -m tests.test_ace_x_eval
	python -m tools.data.make_pool --check
	python -m tools.data.make_partitions --check

# Rocq transport layer (private warm server, deadlines, reply cap,
# recycling, prefix memo): a few seconds of Rocq, no API calls.
test-rocq:
	python -m tests.test_rocq_server

# Byte-for-byte parity of the bridge against archived compute calls
# (`cache_mode: replay` never re-executes Rocq; this does). Doubles as
# the timing benchmark: run with OMPHALOS_PET_MODE=stdio to compare.
bridge-parity:
	python -m tools.analysis.bridge_parity --run $(or $(RUN),x_validation_agentic) \
	  $(if $(CONFIG),--config $(CONFIG),--limit $(or $(LIMIT),3)) --verbose

# Per-call timing of the bridge in every transport mode, on one
# archived cell's compute calls (offline, Rocq only).
bench-rocq:
	python -m tools.analysis.bench_rocq $(if $(CONFIG),--config $(CONFIG),)

# State file vs ground truth, slot table and launch lock of one run
# (SCRIPT=experiments/<script>.py).
launch-status:
	python -m $(subst /,.,$(patsubst %.py,%,$(SCRIPT))) status

# Every X / ACE directory's ground-truth status, lock holders, slots.
ace-x-status:
	python -m tools.maintenance.ace_x_status

# Stop every running launch (frees the RAM within a minute; in-flight
# cells are re-paid on resume) and print the resume commands.
stop:
	python -m tools.maintenance.stop_launches stop

launches:
	python -m tools.maintenance.stop_launches list

test-standard:
	delphyne run commands/prove_one_standard.exec.yaml --cache --no-header

test-agentic:
	delphyne run commands/prove_one_agentic.exec.yaml --cache --no-header

test-probing:
	delphyne run commands/prove_one_probing.exec.yaml --cache --no-header

test-luna:
	delphyne run commands/prove_one_luna.exec.yaml --cache --no-header

test-ace:
	delphyne run commands/prove_one_ace.exec.yaml --cache --no-header

# Hint-on-error generator replayed against a COPY of the luna smoke's
# cache: proves its prompts are byte-identical to the baseline's when
# no hint fires (`cache_mode: replay` in the yaml raises on a miss).
test-ace-trig:
	delphyne run commands/prove_one_ace_triggered.exec.yaml --cache --no-header

regen-ace-trig-cache:
	cp commands/cache/prove_one_luna.exec.yaml commands/cache/prove_one_ace_triggered.exec.yaml

# Stall-rule prover with the rule off, replayed against a COPY of the
# luna smoke's cache: byte-identical prompts when no rule is set.
test-stall:
	delphyne run commands/prove_one_stall.exec.yaml --cache --no-header

regen-stall-cache:
	cp commands/cache/prove_one_luna.exec.yaml commands/cache/prove_one_stall.exec.yaml

# --- benchmark sweeps (real API calls) ---
#
# The benchmark is partitioned into train / validation / test (see
# benchmarks/). These targets are named `sweep-*` rather than `test-*`
# so that `make test` keeps meaning "run the smoke tests" and does not
# collide with the test *partition*.

sweep-train: sweep-train-standard sweep-train-agentic

sweep-train-standard:
	python -m experiments.baselines.train_standard_experiment run --max_workers=$(WORKERS)

sweep-train-agentic:
	python -m experiments.baselines.train_agentic_experiment run --max_workers=$(WORKERS)

sweep-validation:
	python -m experiments.baselines.validation_standard_experiment run --max_workers=$(WORKERS)
	python -m experiments.baselines.validation_agentic_experiment run --max_workers=$(WORKERS)

sweep-test:
	python -m experiments.baselines.test_standard_experiment run --max_workers=$(WORKERS)
	python -m experiments.baselines.test_agentic_experiment run --max_workers=$(WORKERS)

sweep-probing-validation:
	python -m experiments.ablations.validation_probing_experiment run --max_workers=$(WORKERS)

sweep-probing-test:
	python -m experiments.ablations.test_probing_experiment run --max_workers=$(WORKERS)

replay-train-standard:
	python -m experiments.baselines.train_standard_experiment replay

replay-train-agentic:
	python -m experiments.baselines.train_agentic_experiment replay

summary-train:
	python -m experiments.baselines.train_standard_experiment force-summary --add-timing
	python -m experiments.baselines.train_agentic_experiment force-summary --add-timing

summary-validation:
	python -m experiments.baselines.validation_standard_experiment force-summary --add-timing
	python -m experiments.baselines.validation_agentic_experiment force-summary --add-timing

summary-test:
	python -m experiments.baselines.test_standard_experiment force-summary --add-timing
	python -m experiments.baselines.test_agentic_experiment force-summary --add-timing

summary-probing-validation:
	python -m experiments.ablations.validation_probing_experiment force-summary --add-timing

summary-probing-test:
	python -m experiments.ablations.test_probing_experiment force-summary --add-timing

# --- cost auditing (offline, no API calls) ---
#
# Recompute every recorded price from its stored token counts at the
# exact rates in model_registry.OMPHALOS_PRICING.
#
# `reprice` guards experiments/output only, and that scope is the whole
# point: those runs must reproduce to the cent, and this target fails if
# they ever stop doing so. It deliberately excludes experiments/previous,
# whose raw CSVs are left at the rate they were billed at as a
# provenance record (the corrected figures live beside them in
# results_summary.repriced.csv). Pointing the guard at both roots — as
# it used to — made it fail unconditionally, so it could never catch a
# real regression.

reprice:
	python -m tools.analysis.reprice experiments/output

reprice-archive:
	python -m tools.analysis.reprice experiments/previous || true

reprice-write:
	python -m tools.analysis.reprice --write

# Re-audit the design decisions in PROGRESS.md against the archived
# per-problem results: paired sign tests, a noise floor measured from
# the two-seed replicates, and the cost-framed decisions re-derived
# from token counts. Offline, no API calls.

decision-audit:
	python -m tools.analysis.decision_audit \
	  --markdown experiments/output/decision_audit/report.md

# What a tighter per-problem budget would have cost and solved,
# computed from recorded per-request prices. `budget-ablation` is the
# arithmetic; `budget-replay` is the same question put through the real
# strategy, policy and budget machinery with cache_mode=replay, where a
# cache miss raises -- so a clean run proves no API call was made.

budget-ablation:
	python -m tools.analysis.budget_ablation \
	  --markdown experiments/output/budget_ablation/dollar_cap.md
	python -m tools.analysis.budget_ablation --requests --no-verify \
	  --markdown experiments/output/budget_ablation/request_cap.md

budget-replay:
	python -m tools.analysis.replay_with_budget \
	  --csv experiments/output/budget_ablation/replay_cap030.csv

# --- Responses API arms (real API calls) ---
#
# `probe-responses` checks what the provider actually accepts before a
# sweep commits to it. The sweeps run one arm at a time via --arms so
# spend can be checked between them.

probe-responses:
	python -m tools.maintenance.probe_responses_api

sweep-responses-train:
	python -m experiments.ablations.responses_train_experiment run --max_workers=$(WORKERS)
	python -m experiments.ablations.responses_train_standard_experiment run --max_workers=$(WORKERS)

sweep-responses-validation:
	python -m experiments.ablations.responses_validation_experiment run --max_workers=$(WORKERS)

sweep-responses-test:
	python -m experiments.ablations.responses_test_experiment run --max_workers=$(WORKERS)

# --- luna migration (real API calls, but luna is 10x cheaper) ---
#
# `--efforts=` / `--toolsets=` restrict the sweep so spend can be
# checked between arms. The cap in the sweep is deliberately loose; the
# one to ship is derived afterwards from the recorded prices.

sweep-luna-train:
	python -m experiments.baselines.luna_train_experiment run --max_workers=$(WORKERS)

luna-cap:
	python -m tools.analysis.budget_ablation experiments/output/luna_train_agentic \
	  --model gpt-5.6-luna

# Does feedback-as-a-tool-message pay on the canonical agentic loop?
# One arm per value of `convert_user_feedback_to_tool`, everything else
# canonical. ~$0.32. `cvt-report` pairs the arms per problem-seed cell
# -- read that, not the pooled totals.

sweep-luna-cvt:
	python -m experiments.ablations.luna_cvt_ablation run --max_workers=$(WORKERS)

cvt-report:
	python -m tools.reports.cvt_report

# --- ACE on the X partitions (real API calls) ---
#
# Adaptation variants are the paper's experiment matrix
# (experiments/ace/ace_adaptation.py VARIANTS): x-offline, x-offline-e3,
# x-noreflect, x-mono, x-online-s{0,1}, x-online-warm-s{0,1}. Frozen
# playbooks are evaluated with the ace-x-validation / ace-x-test
# targets; online variants evaluate themselves.

ace-x-plan:
	python -m experiments.ace.ace_adaptation plan --variant=$(VARIANT)

ace-x-adapt:
	python -m experiments.ace.ace_adaptation run --variant=$(VARIANT)

ace-x-replay:
	python -m experiments.ace.ace_adaptation replay --variant=$(VARIANT)

ace-x-validation:
	python -m experiments.ace.ace_x_validation_experiment \
	  --playbook=$(PLAYBOOK) --injection=$(or $(INJECTION),full) run --max_workers=$(WORKERS)

ace-x-test:
	python -m experiments.ace.ace_x_test_experiment \
	  --playbook=$(PLAYBOOK) run --max_workers=$(WORKERS)

# --- ACE v3 (reference-audit polish) ---
#
# v3 = versioned prompts (render_version=3, curator contract 3),
# batched offline adaptation with the reducer, per-arm eval dirs.
# Variants: x3-offline, x3-offline-e3, x3-noreflect, x3-mono,
# x3-online[-warm]-s{0,1}, x3-gate-b1. (The per-worker warm Rocq
# server is the default transport since 2026-08-26 — see
# runtime/rocq_server.py; OMPHALOS_PET_MODE=stdio restores the archived one.)

ace-x3-adapt:
	python -m experiments.ace.ace_adaptation run --variant=$(VARIANT)

ace-x3-validation:
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=$(PLAYBOOK) --injection=$(or $(INJECTION),full) run --max_workers=$(WORKERS)

ace-x3-test:
	python -m experiments.ace.ace_x3_test_experiment \
	  --playbook=$(PLAYBOOK) run --max_workers=$(WORKERS)

# --- The ACE-X matrix (2026-08-26 rebuild) ---
#
# Each target is one launch that queues for Rocq stream slots
# (`--wait`); `make -j3 ace-x-matrix` runs the whole matrix unattended
# and is idempotent (done cells are skipped after a status rebuild), so
# it doubles as resume-all after `make stop`. The evaluations render
# each playbook at the version it was adapted under (ace_x_eval reads
# the provenance sidecar) into `_rv{N}` directories. testX targets stay
# OUT of the matrix: one look each, after the validationX readout.
# Explicit WORKERS/ACE_X_WORKERS wins; otherwise ACE uses available slots.
ACE_X_WORKERS ?= $(if $(filter command line environment,$(origin WORKERS)),$(WORKERS),$(or $(OMPHALOS_MAX_STREAMS),$(WORKERS)))

ace-x3-val-offline:
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=ace_x3_offline.yaml run --max_workers=$(ACE_X_WORKERS) --wait

ace-x3-val-noreflect:
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=ace_x3_noreflect.yaml run --max_workers=$(ACE_X_WORKERS) --wait

ace-x3-val-mono:
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=ace_x3_mono.yaml run --max_workers=$(ACE_X_WORKERS) --wait

ace-x3-online-s0:
	python -m experiments.ace.ace_adaptation run --variant=x3-online-s0

ace-x3-online-s1:
	python -m experiments.ace.ace_adaptation run --variant=x3-online-s1

ace-x3-e3-adapt:
	python -m experiments.ace.ace_adaptation run --variant=x3-offline-e3

ace-x3-e3-val: ace-x3-e3-adapt
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=ace_x3_offline_e3.yaml run --max_workers=$(ACE_X_WORKERS) --wait

ace-x4-adapt:
	python -m experiments.ace.ace_adaptation run --variant=x4-offline

ace-x4-val-offline: ace-x4-adapt
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=ace_x4_offline.yaml run --max_workers=$(ACE_X_WORKERS) --wait

ace-x4-online-s0:
	python -m experiments.ace.ace_adaptation run --variant=x4-online-s0

ace-x-matrix: ace-x3-val-offline ace-x3-val-noreflect ace-x3-val-mono \
	ace-x3-online-s0 ace-x3-online-s1 ace-x4-val-offline ace-x4-online-s0 \
	ace-x3-e3-val

# --- 2026-09-02: role strength (x3-strong) and v5 (x5-offline) ---
#
# Two attributable arms (PROGRESS 2026-09-02): x3-strong = x3-offline
# with terra Reflector/Curator/Reducer; x5-offline = x3-offline + the
# evidence-first curation (digest, grounding gate, trivial-solve skip,
# terminal audit; pre-audit playbook frozen too). Both evaluate on
# validationX through the v3 eval script (render_version 3 from the
# provenance sidecar); testX targets stay one look each.

ace-x3-strong-adapt:
	python -m experiments.ace.ace_adaptation run --variant=x3-strong --max_workers=$(ACE_X_WORKERS)

ace-x3-strong-val: ace-x3-strong-adapt
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=ace_x3_strong.yaml run --max_workers=$(ACE_X_WORKERS) --wait

ace-x5-adapt:
	python -m experiments.ace.ace_adaptation run --variant=x5-offline --max_workers=$(ACE_X_WORKERS)

ace-x5-val-offline: ace-x5-adapt
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=ace_x5_offline.yaml run --max_workers=$(ACE_X_WORKERS) --wait

# --- Hint on error (2026-09-05): error-keyed injection of a frozen playbook ---
#
# `ace-triggers` writes and freezes the trigger table of TRIG_PLAYBOOK (one
# terra call, cents); `ace-x-val-trig` evaluates the playbook delivered
# on error only, on validationX (SEEDS, default `0,1`; the protocol runs
# `SEEDS=0` first). `ace-diagnosis` is the offline readout of where a
# playbook's effect goes (turn tax, per-request spend, citations).
TRIG_PLAYBOOK ?= ace_x5_offline.yaml
SEEDS ?= 0,1
ace-triggers:
	python -m experiments.ace.ace_triggers_experiment --playbook=$(TRIG_PLAYBOOK)

ace-x-val-trig:
	python -m experiments.ace.ace_x3_validation_experiment \
	  --playbook=$(TRIG_PLAYBOOK) --injection=triggered --seeds=$(SEEDS) \
	  run --max_workers=$(ACE_X_WORKERS) --wait

# One terra call over the mined repairs of the trainX runs, grounded,
# appended to TRIG_PLAYBOOK and frozen as REPAIR_OUT with its triggers.
REPAIR_OUT ?= ace_x6_repairs.yaml
ace-repairs:
	python -m experiments.ace.ace_repairs_experiment --playbook=$(TRIG_PLAYBOOK) --out=$(REPAIR_OUT)

# Stall rules (2026-09-06): exact offline replay; the live arm is the
# parity proof of the mechanism.
stall-tune:
	python -m tools.reports.stall_report --tune x_train_agentic --check x_validation_agentic --check x_ladon_agentic --json experiments/output/stall/tune_trainX.json

stall-arm:
	python -m experiments.ablations.x_stall_experiment --seeds=$(or $(SEEDS),0) run --max_workers=$(ACE_X_WORKERS) --wait

stall-parity:
	python -m tools.reports.stall_report --rule seenstate --k 4 --parity x_validation_stall_seenstate4_agentic

ace-diagnosis:
	python -m tools.analysis.ace_diagnosis --baseline experiments/output/x_validation_agentic \
	  $(foreach a,$(ARMS),--arm experiments/output/$(a)) \
	  --json experiments/output/ace_diagnosis/validationX.json

ace-x3-strong-test:
	python -m experiments.ace.ace_x3_test_experiment \
	  --playbook=ace_x3_strong.yaml run --max_workers=$(ACE_X_WORKERS) --wait

ace-x5-test-offline:
	python -m experiments.ace.ace_x3_test_experiment \
	  --playbook=ace_x5_offline.yaml run --max_workers=$(ACE_X_WORKERS) --wait

# One look each; never re-run.
ace-x3-test-offline:
	python -m experiments.ace.ace_x3_test_experiment \
	  --playbook=ace_x3_offline.yaml run --max_workers=$(ACE_X_WORKERS) --wait

ace-x4-test-offline:
	python -m experiments.ace.ace_x3_test_experiment \
	  --playbook=ace_x4_offline.yaml run --max_workers=$(ACE_X_WORKERS) --wait

# --- X partitions (real API calls; luna-class pipelines only) ---
#
# trainX/validationX/testX are the 40-problem, competition-heavy
# partitions generated by tools/data/make_partitions.py. Reserved for the
# canonical luna configuration and what is built on it; the frontier
# and chat-completions arms keep the original partitions. The trainX
# sweep runs under a loose cap and `x-cap` derives the cap to ship.

sweep-x-train:
	python -m experiments.baselines.x_train_experiment run --max_workers=$(WORKERS)

x-cap:
	python -m tools.analysis.budget_ablation experiments/output/x_train_agentic \
	  --model gpt-5.6-luna

sweep-x-validation:
	python -m experiments.baselines.x_validation_experiment run --max_workers=$(WORKERS)

sweep-x-test:
	python -m experiments.baselines.x_test_experiment run --max_workers=$(WORKERS)

summary-x-train:
	python -m experiments.baselines.x_train_experiment force-summary --add-timing

summary-x-validation:
	python -m experiments.baselines.x_validation_experiment force-summary --add-timing

summary-x-test:
	python -m experiments.baselines.x_test_experiment force-summary --add-timing

responses-report:
	python -m tools.reports.responses_report \
	  --markdown experiments/output/responses_report/report.md

# Recompute the chart data embedded in the published cost report from
# the recorded runs. Offline; rewrites only the JSON, never the prose,
# so a regeneration that finds nothing to change is a check that the
# figures on the page still match the data behind them.

report-data:
	python -m tools.reports.report_chart_data

# Regenerate the single-problem command caches after a prompt /
# strategy / feedback change (makes real LLM calls).
regen-command-caches:
	rm -rf commands/cache
	delphyne run commands/prove_one_standard.exec.yaml --cache --update --no-header
	delphyne run commands/prove_one_agentic.exec.yaml --cache --update --no-header
	delphyne run commands/prove_one_probing.exec.yaml --cache --update --no-header
	delphyne run commands/prove_one_luna.exec.yaml --cache --update --no-header
	delphyne run commands/prove_one_ace.exec.yaml --cache --update --no-header

# --- ACE (Agentic Context Engineering, arXiv:2510.04618) ---
# Offline adaptation without GT labels, adapted to miniF2F-Rocq.
# `ace-adapt` runs (or resumes, from cache at zero spend) the
# Generator/Reflector/Curator loop over train and freezes
# experiments/playbooks/ace_v1.yaml; `ace-eval` evaluates that frozen
# playbook on validation, seeds {0,1}, against the frozen
# luna_validation_agentic baseline; `ace-report` prints the paired
# verdict offline (pre-registered metrics: see the two experiment
# docstrings). Playbooks live under experiments/playbooks/, NOT
# experiments/output/, so clean-experiments cannot delete a frozen
# playbook whose evaluation runs still reference it.

ace-adapt:
	python -m experiments.ace.ace_adaptation run

ace-eval:
	python -m experiments.ace.ace_validation_experiment run --max_workers=$(WORKERS)

ace-report:
	python -m tools.reports.ace_report

# Offline. Rewrites only the JSON blocks in report/ace_report.html, so
# a run that reports "No change" is a check that the figures on the
# page still match the runs behind them.
ace-report-data:
	python -m tools.reports.ace_report_data

# The out-of-sample look. Pairs against the already-paid
# luna_test_agentic seed-0 cells; see the script docstring for the
# two-looks honesty note.
ace-test:
	python -m experiments.ace.ace_test_experiment run --max_workers=$(WORKERS)

# One adaptation variant (VARIANT=train|train-e3|pool|noreflect|mono).
# Each writes its own output dir and freezes its own playbook, so
# variants can never overwrite one another's artifacts.
ace-adapt-variant:
	python -m experiments.ace.ace_adaptation run --variant=$(VARIANT)

# Offline. The cap curve is the experiment the $0.05 cap never ran:
# a capped run is a strict prefix of a recorded one, so every cell's
# outcome under every cap is exact, and the arms are paired per cell.
ace-cap:
	python -m tools.reports.ace_cap_report \
	  --json experiments/output/budget_ablation/ace_caps.json

# Offline. Does the playbook change *how* the prover fails?
ace-failures:
	python -m tools.analysis.failure_analysis \
	  experiments/output/luna_validation_agentic \
	  experiments/output/ace_validation_agentic \
	  --arm 'core-medium|ace-[0-9a-f]{8}-core-medium' --compare

# Real API calls, ~$0.10, 8 configs. The parser gap: 5 benchmark
# problems reference symbols their prompt never showed, and 4 of them
# are among the 9 the canonical config never solves.
defs-arm:
	python -m experiments.ablations.defs_experiment run --max_workers=$(WORKERS)

# --- housekeeping ---

clean: clean-experiments
	rm -rf commands/cache __pycache__ experiments/__pycache__

clean-experiments:
	rm -rf experiments/output

# --- agent harnesses (AGENTS.md, "Agent harnesses") ---

.PHONY: agents-check codex-setup

# The dual-harness invariants join the omphalos `make test-unit` gate:
# a copy where a symlink belongs breaks them silently.
test-unit: agents-check

agents-check:
	python -m tools.maintenance.agents_check --check

# Install the checked-in Codex profile as ~/.codex/omphalos.config.toml,
# then work with `codex -p omphalos`.
codex-setup:
	python -m tools.maintenance.codex_setup

# Ladon, the overnight improvement loop (ladon/README.md).
-include ladon/ladon.mk
