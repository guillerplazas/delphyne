.PHONY: test test-standard test-agentic test-probing
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
.PHONY: regen-command-caches
.PHONY: clean clean-experiments

# Single-problem smoke tests (cached; regenerate with
# `make regen-command-caches` after a prompt / strategy change).
test: test-standard test-agentic test-probing

test-standard:
	delphyne run commands/prove_one_standard.exec.yaml --cache --no-header

test-agentic:
	delphyne run commands/prove_one_agentic.exec.yaml --cache --no-header

test-probing:
	delphyne run commands/prove_one_probing.exec.yaml --cache --no-header

# --- benchmark sweeps (real API calls) ---
#
# The benchmark is partitioned into train / validation / test (see
# benchmarks/). These targets are named `sweep-*` rather than `test-*`
# so that `make test` keeps meaning "run the smoke tests" and does not
# collide with the test *partition*.

sweep-train: sweep-train-standard sweep-train-agentic

sweep-train-standard:
	python experiments/train_standard_experiment.py run --max_workers=4

sweep-train-agentic:
	python experiments/train_agentic_experiment.py run --max_workers=4

sweep-validation:
	python experiments/validation_standard_experiment.py run --max_workers=4
	python experiments/validation_agentic_experiment.py run --max_workers=4

sweep-test:
	python experiments/test_standard_experiment.py run --max_workers=4
	python experiments/test_agentic_experiment.py run --max_workers=4

sweep-probing-validation:
	python experiments/validation_probing_experiment.py run --max_workers=4

sweep-probing-test:
	python experiments/test_probing_experiment.py run --max_workers=4

replay-train-standard:
	python experiments/train_standard_experiment.py replay

replay-train-agentic:
	python experiments/train_agentic_experiment.py replay

summary-train:
	python experiments/train_standard_experiment.py force-summary --add-timing
	python experiments/train_agentic_experiment.py force-summary --add-timing

summary-validation:
	python experiments/validation_standard_experiment.py force-summary --add-timing
	python experiments/validation_agentic_experiment.py force-summary --add-timing

summary-test:
	python experiments/test_standard_experiment.py force-summary --add-timing
	python experiments/test_agentic_experiment.py force-summary --add-timing

summary-probing-validation:
	python experiments/validation_probing_experiment.py force-summary --add-timing

summary-probing-test:
	python experiments/test_probing_experiment.py force-summary --add-timing

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
	python tools/reprice.py experiments/output

reprice-archive:
	python tools/reprice.py experiments/previous || true

reprice-write:
	python tools/reprice.py --write

# Re-audit the design decisions in PROGRESS.md against the archived
# per-problem results: paired sign tests, a noise floor measured from
# the two-seed replicates, and the cost-framed decisions re-derived
# from token counts. Offline, no API calls.

decision-audit:
	python tools/decision_audit.py \
	  --markdown experiments/output/decision_audit/report.md

# What a tighter per-problem budget would have cost and solved,
# computed from recorded per-request prices. `budget-ablation` is the
# arithmetic; `budget-replay` is the same question put through the real
# strategy, policy and budget machinery with cache_mode=replay, where a
# cache miss raises -- so a clean run proves no API call was made.

budget-ablation:
	python tools/budget_ablation.py \
	  --markdown experiments/output/budget_ablation/dollar_cap.md
	python tools/budget_ablation.py --requests --no-verify \
	  --markdown experiments/output/budget_ablation/request_cap.md

budget-replay:
	python tools/replay_with_budget.py \
	  --csv experiments/output/budget_ablation/replay_cap030.csv

# --- Responses API arms (real API calls) ---
#
# `probe-responses` checks what the provider actually accepts before a
# sweep commits to it. The sweeps run one arm at a time via --arms so
# spend can be checked between them.

probe-responses:
	python tools/probe_responses_api.py

sweep-responses-train:
	python experiments/responses_train_experiment.py run --max_workers=4
	python experiments/responses_train_standard_experiment.py run --max_workers=4

sweep-responses-validation:
	python experiments/responses_validation_experiment.py run --max_workers=4

sweep-responses-test:
	python experiments/responses_test_experiment.py run --max_workers=4

# --- luna migration (real API calls, but luna is 10x cheaper) ---
#
# `--efforts=` / `--toolsets=` restrict the sweep so spend can be
# checked between arms. The cap in the sweep is deliberately loose; the
# one to ship is derived afterwards from the recorded prices.

sweep-luna-train:
	python experiments/luna_train_experiment.py run --max_workers=4

luna-cap:
	python tools/budget_ablation.py experiments/output/luna_train_agentic \
	  --model gpt-5.6-luna

responses-report:
	python tools/responses_report.py \
	  --markdown experiments/output/responses_report/report.md

# Recompute the chart data embedded in the published cost report from
# the recorded runs. Offline; rewrites only the JSON, never the prose,
# so a regeneration that finds nothing to change is a check that the
# figures on the page still match the data behind them.

report-data:
	python tools/report_chart_data.py

# Regenerate the single-problem command caches after a prompt /
# strategy / feedback change (makes real LLM calls).
regen-command-caches:
	rm -rf commands/cache
	delphyne run commands/prove_one_standard.exec.yaml --cache --update --no-header
	delphyne run commands/prove_one_agentic.exec.yaml --cache --update --no-header
	delphyne run commands/prove_one_probing.exec.yaml --cache --update --no-header

# --- housekeeping ---

clean: clean-experiments
	rm -rf commands/cache __pycache__ experiments/__pycache__

clean-experiments:
	rm -rf experiments/output
