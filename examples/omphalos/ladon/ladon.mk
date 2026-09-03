# Ladon — the autonomous overnight improvement loop (ladon/README.md).
# Included by the omphalos Makefile; every target runs from that dir.
.PHONY: ladon-night ladon-resume ladon-status ladon-report ladon-selftest
.PHONY: ladon-test ladon-preflight ladon-dry ladon-partition sweep-x-ladon
.PHONY: summary-x-ladon

# Ladon's unit tests join the omphalos `make test-unit` gate.
test-unit: ladon-test

ladon-test:
	python -m ladon.test_ladon
	python -m ladon.make_partition --check

# Start tonight's loop detached (systemd-run --user, else nohup).
# LADON_ARGS="--max_hints=1 --hints=58" pins the queue; see README.
ladon-night:
	python -m ladon.cli launch $(LADON_ARGS)

# Continue the latest night from its persisted state (also detached).
ladon-resume:
	python -m ladon.cli launch --resume $(LADON_ARGS)

ladon-status:
	python -m ladon.cli status $(LADON_ARGS)

ladon-report:
	python -m ladon.cli report $(LADON_ARGS)

ladon-preflight:
	python -m ladon.cli preflight $(LADON_ARGS)

# ~1 min: preflight, one structured Sonnet call, one pristine re-check.
ladon-selftest:
	python -m ladon.cli selftest $(LADON_ARGS)

# A dry night in the foreground: synthetic hint, smoke cells only
# (~$0.05), PROGRESS/HINTS edits on copies, nothing committed.
ladon-dry:
	python -m ladon.cli night --dry $(LADON_ARGS)

ladon-partition:
	python -m ladon.make_partition

# The canonical baseline on ladonX (Ladon launches it itself when
# missing; by hand for a fresh baseline after a canonical change).
sweep-x-ladon:
	python experiments/x_ladon_experiment.py run --max_workers=4 --wait

summary-x-ladon:
	python experiments/x_ladon_experiment.py force_summary --add-timing
