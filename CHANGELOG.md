# Changelog

## Version 0.8.0 (2025-09-02)

### Changes

- Moved `PolicyEnv` from `core` to the standard library and make `AbstractPolicy` parametric in the policy environment type. As a consequence, the `PolicyEnv.__init__.make_cache` argument can be removed.

### New Features

- Added support for standard library templates (e.g. stdlib/format).
- Parsers can emit formatting hints to be rendered by prompt templates.
- Initial implementation of _universal queries_. See new `guess` export and `test_program.py::test_make_sum_using_guess`.
- Added Gemini Integration.
- Completed a first version of the user documentation.

## Version 0.7.0 (2025-08-22)

- **Breaking:** overhaul of parsers in the standard library. Parsers are now simpler and more composable. In particular, it is now possible to transform parsers by mapping a function to their results or adding validators. Some (partial) upgrading instructions:
  - Replace `raw_yaml` by `get_text.yaml`.
  - Replace `yaml_from_last_code_block` by `last_code_block.yaml`.
  - Replace the `"structured"` parser spec by `structured`.
  - Replace the `"structured"` parser spec by `structured`.
  - Look at the new signature for `Query.__parser__` and at the new methods `Query.parser` and `Query.parser_for`, which replace `Query.query_config`.

## Version 0.6.1 (2025-08-19)

First released version with a full API Reference documentation. From this version on, Delphyne adheres to semantic versioning.