.PHONY: test test-subset replay-subset summary clean clean-experiments

# Single-problem sanity run via `delphyne run`.
test:
	delphyne run commands/prove_one.exec.yaml --cache --no-header

# Full curated dev-subset sweep via the experiment launcher.
test-subset:
	python experiments/dev_baseline_experiment.py run --max_workers=2

# Re-derive per-config summaries from cached outputs (no LLM calls).
replay-subset:
	python experiments/dev_baseline_experiment.py replay

# Regenerate the aggregate `results_summary.csv` from the cached results.
summary:
	python experiments/dev_baseline_experiment.py force-summary --add-timing

clean: clean-experiments
	rm -rf commands/cache __pycache__ experiments/__pycache__

clean-experiments:
	rm -rf experiments/output
