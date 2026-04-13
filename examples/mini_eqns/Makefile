# Makefile for the mini_eqns Delphyne example.
#
# Targets:
#   test                    Run the cached smoke test (alias of full-test).
#   full-test               Run the baseline smoke test with caching enabled.
#   delete-full-test-cache  Remove the cached LLM responses under commands/cache.
#   clean                   Remove git-ignored files (delegates to top-level Makefile).

.PHONY: test full-test delete-full-test-cache clean

test: full-test

full-test:
	delphyne run commands/test_baseline_simple.exec.yaml --cache --filter=[values] --no-header --ensure-no-error

delete-full-test-cache:
	rm -rf commands/cache

clean:
	make -f ../../Makefile clean-ignored
