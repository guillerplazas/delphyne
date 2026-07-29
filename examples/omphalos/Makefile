.PHONY: test test-standard test-agentic test-probing
.PHONY: test-set1 test-set1-standard test-set1-agentic
.PHONY: test-set2 test-set3 summary-set1 summary-set2 summary-set3
.PHONY: test-probing-set2 test-probing-set3
.PHONY: summary-probing-set2 summary-probing-set3
.PHONY: replay-set1-standard replay-set1-agentic
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

test-set1: test-set1-standard test-set1-agentic

test-set1-standard:
	python experiments/set1_standard_experiment.py run --max_workers=4

test-set1-agentic:
	python experiments/set1_agentic_experiment.py run --max_workers=4

test-set2:
	python experiments/set2_standard_experiment.py run --max_workers=4
	python experiments/set2_agentic_experiment.py run --max_workers=4

test-set3:
	python experiments/set3_standard_experiment.py run --max_workers=4
	python experiments/set3_agentic_experiment.py run --max_workers=4

test-probing-set2:
	python experiments/set2_probing_experiment.py run --max_workers=4

test-probing-set3:
	python experiments/set3_probing_experiment.py run --max_workers=4

replay-set1-standard:
	python experiments/set1_standard_experiment.py replay

replay-set1-agentic:
	python experiments/set1_agentic_experiment.py replay

summary-set1:
	python experiments/set1_standard_experiment.py force-summary --add-timing
	python experiments/set1_agentic_experiment.py force-summary --add-timing

summary-set2:
	python experiments/set2_standard_experiment.py force-summary --add-timing
	python experiments/set2_agentic_experiment.py force-summary --add-timing

summary-set3:
	python experiments/set3_standard_experiment.py force-summary --add-timing
	python experiments/set3_agentic_experiment.py force-summary --add-timing

summary-probing-set2:
	python experiments/set2_probing_experiment.py force-summary --add-timing

summary-probing-set3:
	python experiments/set3_probing_experiment.py force-summary --add-timing

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
