# AGENTS.md — examples/omphalos

Complements the repo-root `AGENTS.md` with omphalos-specific rules.
Canonical file for every agent harness; `CLAUDE.md` here is a symlink
to it.
Omphalos is Guille's Master's thesis project (`docs/thesis_proposal.md`):
adapting the Hilbert method to Rocq on miniF2F, and evaluating Delphyne
itself as the implementation platform. **Core domain: the control and
budgeting mechanisms Delphyne offers** — cost, budgets and nuanced
control are the subject of study, not an afterthought.

## Scope, objective, quality (Guille's standing instructions)

- **Scope boundary (critical):** modify code only inside
  `examples/omphalos/`. When a change elsewhere (stdlib, docs, tests)
  would help, outline it as a suggestion instead of implementing it —
  Guille authorizes out-of-scope edits case-by-case (precedent: the
  stdlib `ReasoningEffort` literal fix).
- **Optimization objective:** cost efficiency, nuanced control and
  budget optimization beat raw brute-force performance. Spending more
  reasoning at design time is encouraged exactly when it buys a
  cheaper, more economical runtime solution.
- **Budgeting acceptance (Guille, 2026-09-09):** a substantial cost/coverage
  trade-off can be a project win. Report total cost, cost per qualified solve
  and solve coverage together. Keep explicit user acceptance separate from
  preregistered experimental gates; never relabel a failed gate as passed.
  The bounded money+focused configuration is retained as a budget reference;
  X3 remains a coverage comparator. See the bounded campaign's acceptance.json.
- **Exploration versus promotion (Guille, 2026-09-10):** do not treat a
  missed pilot effect-size gate or inconclusive p-value as proof that an
  idea is bad, or as a blanket veto on further testing. A promising joint
  coverage/cost result can justify a bounded follow-up within the user's
  authorized scope. Distinguish exploratory promise, practical trade-offs,
  statistical support and changing the default; report each separately.
  Set attainable pilot gates for the panel size and decision at hand;
  do not require confirmatory evidence before buying a useful benchmark.
  Preserve prior gates/results honestly, recording new authorization and
  follow-up protocols separately. This does not authorize unlimited sweeps,
  post-hoc relabeling, significance chasing, ignored regressions or automatic
  promotion. Ask when the intended contender or trade-off is ambiguous;
  do not ask again for an already authorized test.
  Make cell arithmetic explicit and respect the requested run count; do
  not silently add seeds or fresh controls when compatible paid references
  can answer the requested comparison. Disclose historical-control limits.
- **Code quality:** production-grade thesis code. No shallow
  solutions, quick hacks or temporary shortcuts.
- **Meaning of quality (Guille, 2026-09-16):** "quality" in the ACE
  economics/advisor request means code and implementation quality. It does
  not impose zero solve-count loss on each replicate. Report cost, coverage
  and cost per solve separately; a replicate losing a proof does not veto
  a promising aggregate result. Keep practical value separate from
  statistical support. The retrospective clarification supersedes the
  mistakenly inferred per-replicate veto in the three economics campaigns;
  preserve their original measurements/gates as history and use
  `tools/reports/ace_economy_reassessment.py` for current interpretations.
  Sound proof checking, complete denominators and spending limits still apply.
- **Reference publication:** the Delphyne paper,
  <https://arxiv.org/pdf/2502.05310> — the standing reference for
  architecture, theoretical foundations and design patterns. Consult
  it (PDF in `papers/`, or fetch it with whatever web tool the harness
  offers) before substantial design work on policies or budgets.

## Agent harnesses (since 2026-09-08)

Both Claude Code and Codex CLI work in this tree; the full rules are in
the repo-root `AGENTS.md`. What matters here:

- Edit `AGENTS.md`, never `CLAUDE.md` (a symlink). `make agents-check`
  guards this and runs inside `make test-unit`.
- Durable facts live in `memory/` (index `memory/MEMORY.md`, format in
  `memory/README.md`). Claude Code loads the index automatically; **a
  Codex session reads it itself before starting work**. Both write new
  entries there.
- Codex setup: `make codex-setup` installs the checked-in profile
  `.codex/config.toml`; then work with `codex -p omphalos` (or
  `codex exec -p omphalos` for one-shot runs). The profile grants
  workspace writes and network (experiments call the OpenAI API), passes
  `OPENAI_API_KEY` through, deliberately withholds the Anthropic
  credentials, and registers rocq-mcp.
- Anything new must work from both harnesses; one-sided pieces are named
  in the root `AGENTS.md` (today: Ladon nights only).

## Canonical configuration

- `gpt-5.6-luna`, `toolset="core"`, `reasoning_effort="medium"`,
  Responses API, `LUNA_DOLLAR_CAP = 0.05` per problem.
  Smoke test: `make test-luna` (cached, no API calls).
- X-partition experiments use `X_DOLLAR_CAP = 0.10`; do not describe
  their measurements as $0.05 runs. The ACE review campaign additionally
  scores successes at actual charged cost <=$0.10, including retries.
- `"rich"` is the *strategy default* and what every terra archive used;
  the toolsets (`core` / `rich` / `probing`) are documented in
  `prove_agentic.py`'s module docstring.
- Re-sweep reasoning effort on every model change — the optimum does
  not port (it rises as the model gets cheaper).

## Measurement discipline (non-negotiable)

- One change per experiment. Pre-register the primary metric and
  decision rule in the script docstring *before* running.
- Match every expected problem-seed cell; keep platform failures in the
  denominator and refuse a verdict on missing or administratively
  censored cells. Cluster repeated seeds and duplicate theorem families
  together for inference (`tools/analysis/paired_evaluation.py`). Seeds are
  repeated measurements, not additional independent theorems.
- For claims of statistical support use two-sided **p<0.10** and 90%
  confidence intervals. These are not mandatory pilot-expansion gates.
  Five all-favorable discordant independent problems are the minimum
  (p=0.0625). This is a significance minimum, **not statistical power**.
  Preserve original campaign gates and verdicts. Ladon keeps its legacy
  p<0.05 rule until hint #120 is addressed; Guille deferred that change. Register a meaningful effect and
  assess uncertainty; identical configs can disagree on 1–3 problems.
- Compare costs on the same complete panel, including failed attempts.
  Report paired cost differences and uncertainty: heavy tails make an
  unexplained aggregate sum unreliable. Nominal dollar budgets stop
  after a crossing request and are not hard billing ceilings. Paid ACE
  review calls, embeddings and retries require `runtime/campaign_budget.py`.
- Partitions: train (tune), validation (check), test (one look per
  headline — never mine its failures for fixes).
- **X partitions (since 2026-08-25):** `benchmarks/{trainX,validationX,
  testX}.txt`, 40 problems each, 50% competition problems, generated by
  `tools/data/make_partitions.py` (`--check` in `make test-unit`), registered
  in `experiments/common/minif2f_x.py`. **Reserved for pipelines at luna's cost
  class** (the canonical config and what is built on it: ACE, two-tier
  policies, ...); the terra/sol frontier and chat-completions arms keep
  the original partitions. Same roles: trainX tunes, validationX selects
  (two seeds), testX gets one look per headline arm. The original
  partitions are saturated (train 20/20; test 16/20 with the same
  sixteen for every luna-class arm) and cannot rank luna-class work.
- **ACE review (2026-09-08):** validationX is development data after
  repeated selection. The frozen `benchmarks/ace_challenge_20260908.json`
  defines 88 previously unexposed challenge problems, 32 fixed Terra
  comparators and 166 reserved Mathd problems. Never feed protected
  problems to adaptation, failure mining, curation or prompt edits.
  Choose and hash the artifact before confirmation; a null result does
  not authorize tuning on its failures. Protocol and accounting are in
  `experiments/campaigns/ace_review_20260908/README.md`.
- Definitions: `show_definitions=True` (`XAgenticConfig` default) renders
  the problem file's own `Definition`/`Fixpoint`/`Notation` preamble;
  the frozen strategies keep it off so archived prompts replay. Never
  A/B it again — measured once (defs arm, +1 of 8 cells).
- Costs: recompute from token counts via `model_registry.pricing_for`;
  never trust the archived `price` column or the stdlib prefix-fallback
  pricing. Rates are dated — prepend new rates, never edit old ones.
  Guard: `make reprice` must exit 0.

## testX closure (Guille, 2026-09-11)

Guille explicitly forbids accessing testX again. This supersedes the older
one-look-per-headline-arm convention above. Do not read its partition,
statements, cached results, reports or mixed aggregate artifacts, and do not
import modules that eagerly load it. New coverage work uses trainX and
validationX only; protected challenge data also remains excluded.
Use the development-only campaign entry point and `make test-coverage-cycle`.
`make ladon-status` also imports the eager X loader: inspect Ladon night
metadata directly instead of importing its CLI while this closure applies.
Aggregate `make test`, partition checks and repricing can access testX: run
explicitly scoped equivalents instead and document the exclusions. Keep
this restriction in both harnesses through this canonical instruction file.

## Running experiments (since 2026-08-26)

**Active authorization, Guille 2026-09-17:** implement the sanitized ACE
audit and refinements with **at most $25 new experiment spend**, independent
of the older $50 campaign. trainX may supply learning and development;
validationX supplies the benchmark (40 problems, two replicates). testX and
protected challenge data remain completely closed. Use
`python -m experiments.ace_sanitized`; both harnesses use this entry point.
Ordinary agentic non-ACE without dropping is the headline comparator;
matched generic controls isolate the playbook contribution. No handoff,
summary, learned retrieval, failure notes or new tools for non-ACE. Report
coverage percent and all-attempt budget reduction; useful trade-offs are
allowed, with uncertainty disclosed. Include bounded playbook learning,
freeze it before validation, preserve sealed archives, and leave changes
staged and uncommitted. No default promotion. The older authorizations below
describe historical campaigns and do not constrain this new trainX work.

**Current campaign scope, Guille 2026-09-16:** the latest correction is
**"Never touch testX"**. It supersedes the earlier permission in this session
and restores the complete closure above, including hashing and mixed
artifacts. The ACE economics/advisor study and matched-budget follow-up
use **validationX exclusively**. No trainX or challenge work. The **same
combined $50 ceiling** covers both campaigns. Topic-based commits are
explicitly requested. Historical sealed protocols retain their original
wording as provenance; their test plans are revoked. Use the validation-only
continuation in `experiments/ace_economy_validation.py`, never the retired
main driver's mixed-scope verifier. This restriction applies to both
harnesses. No held-out confirmation or default promotion is authorized.

The user's subsequent request adds `ace_economy_session_20260916`: exactly
80 non-ACE runs with the frozen session reset on validationX, reusing the
paid ACE-reset controls. The same $50 ceiling covers all three campaigns;
the first two settled at $12.30419518 and make no further paid calls.

The subsequent refinement authorization adds at most **$20 new spend**
within that same cumulative $50 ceiling. Guille then explicitly allowed
**trainX for refinement pilots**; validationX remains the benchmark and
testX remains completely closed. Polish reset and compact prompts/feedback
independently, then test their combination in both ACE and non-ACE.
**Latest correction:** reset means history dropping only. Add no handoff,
summary, lookup memory, failure notes or new tool to non-ACE; the matched
reset treatment adds none to either agent. Preserve existing baseline tool
capabilities. Do not require resetting non-ACE when choosing fair cost/
coverage comparators. Code quality and numeric cost/coverage trade-offs
are separate. Topic commits remain authorized; no default promotion.

- Every experiment script ends in `ol.OmphalosExperiment(...).run_cli()`
  (`experiments/common/omphalos_launch.py`): per-directory launch lock,
  machine-wide Rocq stream slots (`OMPHALOS_MAX_STREAMS`, default 4),
  supervised attempts (a broken pool is killed as a group, statuses
  rebuilt from `configs/*/result.yaml`, attempt retried), per-worker
  address-space limit, lean exports. Launch several experiments at
  once freely; `run --wait` queues for slots, `status` / `rebuild`
  inspect and repair a directory. No watchdog scripts, no `pkill`, no
  `ulimit` prefixes — those rituals are retired.
- Rocq transport: `runtime/rocq_server.py` (private warm `pet-server` per
  process, stable augmented paths under `.rocq_cache/aug/`, deadlines,
  reply cap, RLIMIT_AS, recycling, prefix memo). Socket is the default;
  `OMPHALOS_PET_MODE=stdio` is the archived transport. Any change to
  the bridge must keep `make bridge-parity` at 100 % identical on
  non-crash cells and `make test-rocq` green.
- Runaway-goal caps (`pytanque_utils.GoalCaps`, `XAgenticConfig.
  goal_caps`) are a pre-registered treatment
  (`experiments/ablations/x_goalcap_experiment.py`), off by default — never flip
  the default; `tools/analysis/goal_cap_audit.py` sizes the constants offline.
- Machine (since 2026-09-08): the tree lives on **i34-gpu01**
  (`ssh i34-gpu01`, 64 cores / 219 GB, shared, no sudo) at the same
  absolute path, conda env `guille`, opam switch
  `CP.2025.08.0~9.0~2025.08`; environment via `~/.config/omphalos/env.sh`
  (sets `OMPHALOS_MAX_STREAMS=16`). Long runs and Ladon nights go in tmux
  (no user systemd). `make WORKERS=16 sweep-…` raises the per-launch
  workers (default stays 4). The laptop copy is a read-only mirror after
  the final sync: never launch from both hosts into the same archive.
  ACE X targets inherit `OMPHALOS_MAX_STREAMS` unless `WORKERS` or
  `ACE_X_WORKERS` is explicitly set. New review configurations pin their
  measured runtime profile (24 workers / 32 slots); per-prover memory
  limits remain unchanged. Current setup: `docs/usage.md`.

## Caches

- LLM caches are keyed by rendered prompts and located by config
  *directory paths*. Prompt/query-field changes invalidate them;
  identifier renames do not (strategy-arg names never reach the model).
- Prove prompt-neutrality with `cache_mode: replay` (raises on any
  cache miss) instead of asserting it — and remember replay never
  re-executes Rocq: bridge neutrality is `tools/analysis/bridge_parity.py`.
- Archived outputs are paid measurements: migrate them with scripts
  (`tools/maintenance/rename_toolset.py` is the model), never hand-edit or delete.

## Searching this tree

- Most of it is gitignored AND the whole directory sits in
  `.git/info/exclude`: use `rg --no-ignore`, and remember `git status`
  will NOT show new files here — `git add -f` anything that must be
  committed.
- Grep traps: "cleanly" appears ~49k times in caches (never grep a bare
  substring like `lean`); `_` is a word character, so `__segment__`
  names escape `\b` patterns and need their own regex.

## Untouchables

- `rocq_skills_data/` — vendored repository, never modify.
- `miniF2F/` — benchmark statements, never modify.
- `experiments/output/`, `experiments/previous/` — frozen measurements.
- No functional rocq-mcp references in product files; MCP-discovered
  capabilities count only once reproduced as Delphyne tools.

## Local files (all gitignored / excluded)

- `PROGRESS.md` — dated history. Every major change or milestone gets
  an entry: what changed, and the engineering rationale and trade-offs
  behind the decision. Curate obsolete discussion, preserving consequential
  corrections, denominators and trade-offs. Thesis reasoning belongs in
  `docs/thesis_decisions.md`; do not silently rewrite historical verdicts.
- `HINTS.md` — improvement backlog, newest-first = working priority.
  Contains **open hints only**; consult it when asked "what next". Move
  completed, rejected or merged hints to `docs/CLOSED_HINTS.md`, preserving
  IDs and outcomes. New IDs exceed both files. All improvement suggestions,
  including ACE findings, belong here; other documents link to hint IDs.
  Check Delphyne capabilities first: verified examples are demonstrations.
- `docs/LINKS.md` — references needing further reading or verification. Add anything
  you could not fetch; Guille studies these and feeds them back.
- `papers/` — local store for reference PDFs (see `papers/README.md`).
- `memory/` — durable cross-session facts, shared by both harnesses and
  symlinked from Claude Code's own memory directory (`memory/README.md`).
- `AGENTS.md` (this file) and the root one, each with a `CLAUDE.md`
  symlink beside it.

## Workflow

- Maintain `HINTS.md` and `PROGRESS.md` as part of implementation and
  experimentation, without waiting for a separate reminder. Add new
  evidence-backed hints, record investigated hints with their actual outcome
  (including null or inconclusive), archive closed ones, and link progress.
  Record changes, rationale, checks, benchmark denominators and costs at
  meaningful milestones. Keep the existing Ladon in-flight restriction.
- Experiment supervision has a cost too. Keep commentary concise, avoid
  repeated status narration and rapid polling, and batch routine results
  into the final report. Prefer messages about a substantive finding,
  failure, budget issue or needed decision; comply with mandatory harness
  updates using the minimum useful text. This applies to both harnesses.
- A spending ceiling is not a target. Reuse compatible paid evidence,
  register bounded pilots before launching, and never add runs or seeds
  merely to cross a significance threshold.
- Before handing work back: `make pyright` at the repo root, `make
  test` here, and `ruff format`/`ruff check` on touched files. (`make
  test-unit` includes `agents-check`, the dual-harness invariants.)
- Leave changes staged and uncommitted — Guille commits.

## Ladon (overnight loop, since 2026-09-03)

- `ladon/` runs unattended nights: hint → arm → paired verdict →
  KEEP commit / DISCARD / INSPECT ("inspect with Fable") / HUMAN.
  Rules and frozen surface: `ladon/README.md`, `ladon/AGENTS.md`.
- **Nights run on Claude Code only** (decision 2026-09-08):
  `ladon/claude_driver.py` depends on that CLI's flag surface, its
  `--max-budget-usd` cap and the Max-plan rate windows. A Codex session
  may read Ladon and run `make ladon-status` / `ladon-report` /
  `ladon-test`, but never starts or resumes a night.
- Selection partition `ladon/ladonX.txt` + baseline
  `experiments/output/x_ladon_agentic`; testX is never run by Ladon.
- Never edit `HINTS.md` / `docs/CLOSED_HINTS.md` / `PROGRESS.md` while `make ladon-status`
  shows a night running.
