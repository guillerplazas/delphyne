.PHONY: pyright clean clean-ignored test full-test full-clean schemas stubs install doc-logo cloc deploy-doc-release deploy-doc-dev prepare-release release

RELEASE_SCRIPT := python scripts/prepare_release.py

TO_CLEAN := \
	-name '__pycache__' -o \
	-name '*.pyc' -o \
	-name '*.pyo' -o \
	-name '*.egg-info' -o \
	-name '.pytest_cache' -o \
	-name '_build' -o \
	-name '.ruff_cache' -o \
	-name '.DS_Store'

SCHEMAS_FOLDER := vscode-ui/resources
STUBS_FOLDER := vscode-ui/src/stubs


# Install Delphyne (and its dependencies) in editable mode.
install:
	pip install -e ".[dev]"


# Perform typechecking for the whole codebase and examples.
pyright:
	@echo "Checking main project"
	pyright
	@echo "\n\nChecking find_invariants"
	pyright examples/find_invariants
	@echo "\n\nChecking mini_eqns"
	pyright examples/mini_eqns


# Run a quick, minimal test suite. These tests should not require additional
# dependencies on top of those specified in Delphyne's pyproject.toml.
test:
	pytest tests
	make -C examples/find_invariants test


# Run a longer test suite. This might require additional dependencies, as
# specified by individual example projects.
full-test: test
	make -C examples/find_invariants full-test
	make -C examples/mini_eqns full-test
	make -C examples/small full-test


# Clean files ignored by git.
clean-ignored:
	find . \( $(TO_CLEAN) \) -exec rm -rf {} +


# Clean all files that are cheap to regenerate.
clean: clean-ignored
	rm -rf build
	rm -rf site
	rm -rf tests/cmd_out
	make -C vscode-ui clean
	make -C examples/libraries/why3py clean
	make -C examples/find_invariants clean
	make -C examples/mini_eqns clean


# Perform a complete cleaning.
full-clean: clean
	make -C examples/libraries/why3py full-clean


# Generate the demo file schema.
# This should only be executed after a change was made to the `Demo` type.
schemas:
	mkdir -p $(SCHEMAS_FOLDER)
	python -m delphyne.server.generate_schemas demo_file > \
	    $(SCHEMAS_FOLDER)/demo-schema.json
	python -m delphyne.server.generate_schemas config_file > \
	    $(SCHEMAS_FOLDER)/config-schema.json


# Generate stubs by using GPT-4 to translate Python types into TypeScript.
# This should only be executed after a change is made to
# the `Demo` or `DemoFeedback` types
stubs:
	python -m delphyne.server.generate_stubs demos > $(STUBS_FOLDER)/demos.ts
	python -m delphyne.server.generate_stubs feedback > $(STUBS_FOLDER)/feedback.ts


# Clean the request cache of the test suite. Using `make test` will regenerate
# the cache, although doing so can take time and require API keys for a number
# of LLM providers.
clean-cache:
	rm -rf tests/cache


# Generate white logos from the black logos (for dark mode themes).
LOGOS_DIR := docs/assets/logos
BLACK_LOGOS := $(wildcard $(LOGOS_DIR)/black/*.png)
WHITE_LOGOS := $(subst /black/,/white/,$(BLACK_LOGOS))
GRAY_LOGOS := $(subst /black/,/gray/,$(BLACK_LOGOS))
$(LOGOS_DIR)/white/%.png: $(LOGOS_DIR)/black/%.png
	convert $< -fill black -colorize 100% -channel RGB -negate +channel $@
$(LOGOS_DIR)/gray/%.png: $(LOGOS_DIR)/black/%.png
	convert $< -fill '#666d77' -colorize 100% $@
doc-logo: $(WHITE_LOGOS) $(GRAY_LOGOS)
	cp $(LOGOS_DIR)/gray/mini.png vscode-ui/media/logo/delphyne.png


# Build and deploy the documentation for the latest stable release.
# Warning: this should only be used if the documentation on the current commit
# is valid for the latest stable release.
deploy-doc-release:
	git fetch origin gh-pages
	mike deploy 0.7 latest --update-aliases --push


# Build and deploy the documentation for the dev version
deploy-doc-dev:
	git fetch origin gh-pages
	mike deploy dev --push


# Prepare a new release.
#
# To make a new release, follow the following steps:
#     1. Bump the version number in `pyproject.toml`
#     2. Run `make prepare-release`
#	  3. Check that the changes are ok using `git diff`
#     4. If so, finalize and push the release using make release``
prepare-release:
	${RELEASE_SCRIPT} prepare `${RELEASE_SCRIPT} current-version`
	@$(MAKE) full-test


# Finalize and push a release (see `prepare-release`).
release:
	@test -z "$$(git status --porcelain)" || (echo "Uncommitted changes found" && exit 1)
	@$(MAKE) deploy-doc-release
	git tag v`${RELEASE_SCRIPT} current-version`
	git push --tags


# Count the number of lines of code
cloc:
	cloc . --exclude-dir=node_modules,out,.vscode-test --include-lang=python,typescript
