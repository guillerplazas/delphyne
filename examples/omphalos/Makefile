.PHONY: test test-standard test-agentic
.PHONY: test-subset test-subset-standard test-subset-agentic
.PHONY: replay-subset-standard replay-subset-agentic
.PHONY: summary-standard summary-agentic
.PHONY: clean clean-experiments

# Default-aliases preserve muscle memory from the first iteration:
# `make test` and `make test-subset` continue to run the standard baseline.
test: test-standard
test-subset: test-subset-standard

# --- standard baseline (single-stage Hilbert, no tool calls) ---

test-standard:
	delphyne run commands/prove_one_standard.exec.yaml --cache --no-header

test-subset-standard:
	python experiments/dev_standard_experiment.py run --max_workers=2

replay-subset-standard:
	python experiments/dev_standard_experiment.py replay

summary-standard:
	python experiments/dev_standard_experiment.py force-summary --add-timing

# --- agentic baseline (LLM may call ReadSkill on demand) ---

test-agentic:
	delphyne run commands/prove_one_agentic.exec.yaml --cache --no-header

test-subset-agentic:
	python experiments/dev_agentic_experiment.py run --max_workers=2

replay-subset-agentic:
	python experiments/dev_agentic_experiment.py replay

summary-agentic:
	python experiments/dev_agentic_experiment.py force-summary --add-timing

# --- housekeeping ---

clean: clean-experiments
	rm -rf commands/cache __pycache__ experiments/__pycache__

clean-experiments:
	rm -rf experiments/output
