# Ladon session rules

You are running inside **Ladon**, the autonomous overnight improvement
loop of the omphalos project (`examples/omphalos/` in the Delphyne
repository: Hilbert-style theorem proving on miniF2F-Rocq with
`gpt-5.6-luna`, the "luna" canonical pipeline). Nobody is watching.
Never ask a question and never wait for input: when a decision is
yours, make it, write it in `notes.md`, and continue. If you cannot
finish, write what you learned and stop cleanly — an unfinished hint is
recorded as INSPECT; a hint you quietly faked is far worse than one you
abandoned.

## Hard rules (Ladon's guard rejects the arm when any is broken)

- Edit files only under `examples/omphalos/`. Read anything you like
  (the stdlib under `src/delphyne` is readable, never writable).
- **Frozen, never modify**: `benchmarks/*.txt`, `ladon/**` (except your
  own night directory), `tools/decision_audit.py`, `tools/ace_report.py`,
  `tools/cell_records.py`, `tools/reprice.py`, `tools/make_*.py`,
  `tools/test_*.py`, `experiments/minif2f_x.py`,
  `experiments/miniF2F_bench.py`, `experiments/x_*_experiment.py`,
  `experiments/playbooks/`, `experiments/output/` (every directory that
  already exists), `miniF2F/`, `rocq_skills_data/`, `commands/`,
  `pyrightconfig.json`, `delphyne.yaml`, `README.md`, `PROGRESS.md`,
  `HINTS.md`, `LINKS.md`, `CLAUDE.md`, `papers/`, the pricing table in
  `model_registry.py`. `Makefile` and `.gitignore` are append-only.
- Do not create or modify any experiment output directory other than
  the arm and smoke directories Ladon assigned to you.
- **Never launch the full experiment** (ladonX). Ladon launches it
  after your session ends. The only cells you may pay for are the
  smoke: `LADON_SMOKE=1 LADON_SEEDS=0 python experiments/<your script>
  run --max_workers=2 --wait` (three trainX cells, about a cent).
- Never run `git commit`, `git push`, `git add`, `git reset`, `git
  checkout`, `git stash`, `git worktree`; never delete a file you did
  not create tonight; never run `make clean*`, `make
  regen-command-caches`, `make reprice-write`, `make stop`, `pkill`.
- Never read testX results (`experiments/output/x_test_agentic`,
  `experiments/output/ace_x_test_*`); testX is the clean partition and
  its failures are never mined.
- Never edit a Jinja template while a run is live — templates are read
  at render time (`python tools/stop_launches.py list` must print
  nothing before you touch `prompts/`).
- **One change per arm.** Pre-register the metric and the decision
  rule in the arm script's docstring before the smoke runs.

## How omphalos measures (so your pre-registration means something)

- Primary metric: paired solves per (problem, seed) cell against the
  canonical baseline (`experiments/output/x_ladon_agentic`, two seeds,
  80 cells), exact sign test on the discordant cells. Power floor: six
  one-sided discordant cells for p < 0.05; identical configurations
  disagree on 1–3 of 20 cells run to run. Never read pooled sums.
- Secondary metric: spend among the jointly-solved cells (median
  ratio, sign test at a 2 % tie band), costs recomputed from tokens at
  `model_registry.pricing_for` rates. **Budget reduction beats raw
  performance**: a change that solves the same cells for less is a win.
- Ladon's rules (`ladon/verdict.py`): KEEP on established paired
  solves (p < 0.05) or on established cheaper spend (p < 0.05, median
  ratio ≤ 0.90) with no solve deficit; DISCARD on established harm or
  a powered null; INSPECT when the signal is positive but underpowered.
- Per-problem cap `minif2f_x.X_DOLLAR_CAP` (dollars, not requests).
  Definitions are shown (`show_definitions=True`); never A/B it again.

## Conventions

- `# pyright: strict`, ruff at 79 columns, docstring-first modules that
  say *why*. `make pyright` at the repository root and `make test-unit`
  in `examples/omphalos` must pass before you finish.
- New knob: subclass `ladon.bench.LadonConfig` **in your arm script**
  with a defaulted dataclass field, pass it through `instantiate`
  (precedent: `minif2f_x.XAgenticConfig.goal_caps` and
  `experiments/x_goalcap_experiment.py`). Never add fields to the
  frozen config classes.
- Prompt changes: keep the frozen strategies byte-identical — put new
  text behind a new query field or template variable so the archived
  caches replay (the KEEP gate replays the cached smoke suites).
- Bridge changes (`pytanque_utils.py`, `rocq_server.py`): `make
  test-rocq` and `make bridge-parity` must stay green.
- LLM caches are keyed by the rendered prompt and located by config
  directory: prompt changes invalidate them, identifier renames do not.
- Search with `rg --no-ignore` (most of the tree is gitignored); never
  grep a bare substring like `lean` (49k hits in caches).
- Read the launcher's output with `python <script> status`; never
  `cat` a `result.yaml` or `cache.yaml` (they are megabytes) — `head`
  is fine.
- Shell commands run under an allowlist: keep each Bash call a single
  simple command. Shell variables (`$run`, `${x}`), `for`/`while`
  loops and pipes into `tee` are refused by the permission system; put
  loops and captures in a small Python script under your night
  directory instead, and read outputs with `python ... | head`.
