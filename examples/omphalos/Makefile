.PHONY: test test-standard test-agentic test-probing
.PHONY: sweep-train sweep-train-standard sweep-train-agentic
.PHONY: sweep-validation sweep-test
.PHONY: sweep-probing-validation sweep-probing-test
.PHONY: summary-train summary-validation summary-test
.PHONY: summary-probing-validation summary-probing-test
.PHONY: replay-train-standard replay-train-agentic
.PHONY: reprice reprice-write
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
# exact rates in model_registry.OMPHALOS_PRICING. `reprice` is a guard:
# it fails if any run's recorded prices do not reproduce.

reprice:
	python tools/reprice.py

reprice-write:
	python tools/reprice.py --write

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
