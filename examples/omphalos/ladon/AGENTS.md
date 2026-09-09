# AGENTS.md — examples/omphalos/ladon

Ladon is the autonomous overnight loop (`README.md` here). Canonical
file for every agent harness; `CLAUDE.md` here is a symlink to it.
Rules for any interactive session working in or around it:

- **Nights run on Claude Code only** (decision 2026-09-08, the single
  deliberate exception to the dual-harness rule in the root
  `AGENTS.md`). `claude_driver.py` is built on that CLI's `-p` flag
  surface (`--max-turns`, `--permission-mode`, `--allowedTools`, the
  `stream-json` result envelope), on `--max-budget-usd` for the
  per-session money cap, and on the Max-plan 5 h / 7 d rate windows that
  decide when a night waits. None of that has a Codex equivalent that
  has been measured, and the loop spends real money unattended, so it
  was left alone rather than half-ported. A Codex session may read
  Ladon, run `make ladon-status` / `ladon-report` / `ladon-test`, and
  work on the arms Ladon produced — but never starts or resumes a
  night, and never edits the driver expecting Codex to run it.
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
  driver or the re-verifier changed (that one needs `claude` on PATH).
