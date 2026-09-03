# CLAUDE.md — examples/omphalos/ladon

Ladon is the autonomous overnight loop (`README.md` here). Rules for
any interactive session working in or around it:

- **Frozen for the loop, editable by Guille**: everything in this
  directory except `nights/`. Ladon's guard rejects an arm that changes
  Ladon; changes to the loop are made by hand, in daylight.
- **Never edit a night in flight**: `HINTS.md`, `PROGRESS.md`,
  `experiments/output/ladon_*` and `ladon/nights/<date>` are being
  written by the running orchestrator (`make ladon-status`).
- **Commits**: a KEEP commit (`Hint N: …`, co-authored by Ladon) is
  the one standing exception to "leave changes uncommitted — Guille
  commits", authorised 2026-09-02 for Ladon nights only. Interactive
  sessions still never commit.
- **testX** stays a human decision: the report recommends a look; the
  loop never runs it.
- Decision rules live in `verdict.py` and are quoted in `LADON.md`;
  change them in both places, never mid-night.
- Verification before handing back: `make ladon-test` (in `make
  test-unit`), `make pyright` at the repository root, `ruff format` /
  `ruff check` on touched files, `make ladon-selftest` when the Claude
  driver or the re-verifier changed.
