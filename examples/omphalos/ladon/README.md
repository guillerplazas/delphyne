# Ladon — the overnight improvement loop

Ladon is omphalos's autoresearch-style loop: while you sleep it takes
hints from `HINTS.md`, implements each as one isolated experiment arm,
measures the arm against the canonical pipeline with the house
statistics, and decides **KEEP / DISCARD / INSPECT / HUMAN**. A KEEP is
committed as a single `Hint N: …` commit signed by you and Ladon;
everything is written to `PROGRESS.md`, `HINTS.md`, a ledger and a
morning report. Nothing needs your input until the morning.

Named after the dragon that never slept while guarding the garden.

## Starting a night

Before bed, from `examples/omphalos` inside a tmux session. On i34-gpu01
this is mandatory: there is no user systemd (`Linger=no`), so the night
falls back to `nohup` and must be started from a tmux that outlives the
SSH session (`tmux new -s ladon`). On the laptop a live tmux also keeps
the WSL VM up:

    make ladon-night                                   # tonight, defaults
    make ladon-night LADON_ARGS="--max_hints=1 --hints=58"   # pinned queue
    make ladon-night LADON_ARGS="--wallclock_h=7 --cap_usd=8"

`ladon-night` detaches (`systemd-run --user`, falling back to `nohup`)
and returns immediately. Follow with `make ladon-status`,
`journalctl --user -u ladon-<date> -f`, or the night's `ladon.log`.
In the morning read `ladon/LATEST_REPORT.md` (a copy of
`ladon/nights/<date>/REPORT.md`).

The first night runs the canonical baseline on `ladonX` (two seeds,
80 cells, ≈ $1.7, ≈ 2 h) before touching any hint. **The Ladon setup
must be committed first**: preflight refuses to start when
`ladon/ladonX.txt` is not in `HEAD`, because the re-verifier checks
out that commit.

Defaults: 3 arms plus 3 free offline analyses, 9 h wall-clock, $12
OpenAI, $25 Claude estimate, 4 Rocq workers. A hint you pin with
`--hints` runs regardless of an earlier INSPECT/HUMAN mark. Every knob is a `--flag` of `python -m ladon.cli night`.

## What one hint costs

| step | who | typical |
|---|---|---|
| implement session | Sonnet (knob) / Opus (design) | 10–30 min, no OpenAI spend beyond a one-cent smoke |
| screen tier (seed 0, 40 cells) | orchestrator | ≈ 1 h, ≈ $0.8 |
| select tier (+ seed 1) | orchestrator | ≈ 1 h, ≈ $0.8 |
| pristine re-verification | orchestrator (git worktree of the base commit) | minutes |
| evaluate session | Sonnet, no tools | 1–2 min |
| KEEP gates + commit | orchestrator | ≈ 5 min |

So a night fits about three arms. Offline hints (class A) cost nothing
and always end as INSPECT with an artifact.

## The decision rule (pre-registered, `ladon/verdict.py`)

Paired per (problem, seed) against `experiments/output/x_ladon_agentic`:

- **KEEP** — paired solves established (two-sided sign test p < 0.05,
  arm ahead), or jointly-solved spend established cheaper (p < 0.05,
  median ratio ≤ 0.90) with no solve deficit.
- **DISCARD** — established harm, established dearer without a solve
  gain, or a powered null (≥ 6 discordant cells, nothing established).
- **INSPECT** — signal present but not settled (net +3 solves or a
  promising cost ratio at p < 0.2), an integrity doubt (a solve the
  pristine verifier rejects, code drift, an incomplete run), or a KEEP
  whose gates failed. Marked **"inspect with Fable"** in `HINTS.md`.
- **HUMAN** — class D (structural, upstream, frozen paths) or an
  infrastructure failure; never implemented by the loop.
- Screen tier: the arm continues to seed 1 unless seed 0 already lost
  four net cells or failed four cells.

testX is never run by Ladon. A KEEP's report asks you to authorise
the one testX look.

## What Ladon may and may not touch

The guard (`ladon/guard.py`) snapshots `examples/omphalos` before every
implement session and rejects the arm if a frozen path changed:
partitions, the statistics and pricing tools and their tests, the
baseline scripts, `minif2f_x.py` / `miniF2F_bench.py`, vendored trees,
cached smoke suites, the local knowledge files, frozen playbooks,
Ladon itself, the pricing table, every pre-existing output directory.
`Makefile` and `.gitignore` are append-only. Sessions cannot commit,
push, reset or delete; the orchestrator does the launching, pairing,
re-verification, gating and committing in plain Python.

A KEEP passes `ruff`, `make pyright`, `make test`, `make reprice`, a
replay of the five cached smoke suites (prompt neutrality), and —
when the bridge was touched — `make test-rocq` and
`make bridge-parity`. A gate failure downgrades to INSPECT and leaves
the patch under the night directory.

## Files

    ladon/
      cli.py             python -m ladon.cli night|resume|status|report|selftest|launch|preflight
      LADON.md           rules appended to every session's system prompt
      prompts/           plan / implement / analysis / evaluate templates, arm template
      ladonX.txt         the selection partition (make_partition.py --check)
      bench.py           LADONX_PROBLEMS, LadonConfig, SMOKE_PROBLEMS
      verdict.py         pairing + decision rules
      guard.py           frozen paths, manifest, patch / revert / commit
      launch.py          arm launches with deadlines
      reverify.py        pristine re-check in a git worktree
      claude_driver.py   claude -p sessions, usage-limit waits
      hints.py           HINTS.md / PROGRESS.md parsing and insertion
      state.py           night.yaml schema
      report.py          REPORT.md and ledger.tsv
      test_ladon.py      make ladon-test (part of make test-unit)
      nights/<date>/     night.yaml, plan.yaml, ladon.log, hints/h<N>/…, REPORT.md
      ledger.tsv         one row per hint per night (never committed)
    experiments/
      x_ladon_experiment.py                  the baseline (frozen)
      ladon_<date>_h<N>_experiment.py        arm scripts (deleted on DISCARD/INSPECT, kept in the patch)
      output/x_ladon_agentic, output/ladon_<date>_h<N>_{agentic,smoke}

## Operating notes

- **Claude Code only** (decision 2026-09-08, when Codex CLI became a
  second harness for the rest of omphalos). `claude_driver.py` is built
  on that CLI's `-p` flag surface, on `--max-budget-usd` for the
  per-session money cap, and on the Max-plan 5 h / 7 d rate windows
  that decide when a night waits; none of it has a measured Codex
  equivalent, and the loop spends real money unattended. A Codex
  session may read Ladon, work on the arms it produced, and run
  `make ladon-status` / `ladon-report` / `ladon-test`, but must not
  start or resume a night. `make ladon-selftest` needs `claude` on
  PATH.
- `make ladon-selftest` (≈ 1 min): preflight, one structured Sonnet
  call, one archived proof re-checked in a pristine worktree.
- `make ladon-dry` (≈ $0.05): a synthetic hint through every
  transition; `PROGRESS.md` / `HINTS.md` edits go to copies under the
  night directory; nothing is committed.
- `make ladon-resume` continues the latest night after a crash, a
  usage-limit halt or a reboot; every step is idempotent.
- Usage limits: a session that hits the Max plan's limit is retried
  after the reset (`rate_limit_event` / "resets in"), up to three hours
  per step; the night halts when the weekly window is 90 % used.
- Models: plan and design (class C) on Opus, knobs and prose on
  Sonnet; override with `--plan_model`, `--design_model`, `--knob_model`.
- Implement sessions run with `bypassPermissions` plus the deny list
  (no commit/push/reset/checkout, no `rm -r`, no `make clean*`), because
  the allowlist mode refused shell loops, variables and pipes and cost
  every session turns; `--strict_permissions` restores the allowlist.
- `--no_analysis` asks the planner for arms only (no class A) — for a
  night meant to exercise the arm-to-commit path.
- Never edit `HINTS.md` while a night is running (Ladon rewrites the
  entry it judges); the rest of the file is untouched.
