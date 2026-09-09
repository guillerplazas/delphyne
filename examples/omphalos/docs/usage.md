# Using and evaluating Omphalos

[README](../README.md) is the entry point. This document owns current
operating instructions; dated results belong in campaign records and
local [PROGRESS](../PROGRESS.md), with proposed changes in [HINTS](../HINTS.md).

## Environment and entrypoints

Use Python 3.12 in the `guille` conda environment, the project's Delphyne
installation, pytanque and the Rocq opam switch. The canonical host is
**i34-gpu01**; its environment is loaded by `~/.config/omphalos/env.sh`.
The switch is `CP.2025.08.0~9.0~2025.08`. Long jobs run in tmux; the laptop
copy is a read-only mirror. Never launch both hosts into the same archive.

Run Make targets and `python -m ...` commands from `examples/omphalos`.
Package entrypoints replace the former flat script paths. Root strategy
names, query names, command YAML paths and experiment output paths are stable.

Claude Code uses the shared AGENTS files through CLAUDE symlinks. Codex reads
`memory/MEMORY.md` at session start; `make codex-setup` installs its checked-in
profile for `codex -p omphalos`. Both harnesses use the same commands below.
Credentials remain in the environment, never in documentation or profiles.
Ladon nights are the explicit Claude-only exception; see
[its instructions](../ladon/AGENTS.md).

## Strategies, policies and demonstrations

`prove_standard` uses full-script proposals with plain verification.
`prove_agentic` exposes tools and an assisted verifier that can complete
routine remaining goals. Toolsets are:

| Toolset | Exploration |
|---|---|
| `core` | ReadSkill and SearchRocq; partial proposals expose verified progress |
| `rich` | ReadSkill, InspectAt and TryAutomation at a reached proof state |
| `probing` | Adds model-proposed candidate tactic probing |

`rich` remains the strategy default for historical compatibility. The
current Luna reference explicitly chooses `core` and reasoning `medium`.
The original Terra reference uses reasoning `low`. Re-evaluate effort when
changing models; the measured optimum did not transfer between tiers.

ACE's reflection, curation, reduction, auditing and reference grounding are
already standalone strategies. Grounded search composes focused reference,
bridge and structure decisions with typed evidence and bounded computation.
An atomic claim is accepted through a Rocq check, not through model approval.
See [ACE findings](ace_review.md) for what the completed studies established.

Delphyne demos are executable specifications and sources of few-shot
examples. The workspace loads `demos/standard.demo.yaml`,
`demos/agentic.demo.yaml` and `demos/grounded.demo.yaml`. Example-marked query
answers are selected through existing `dp.few_shot`/example-selector policies;
long traces are not automatically useful examples. The grounded selectors
attach examples to the relevant typed decision. A demonstration teaches the
role; a verified solution for the current training problem is separate input.

```sh
for demo in demos/*.demo.yaml; do delphyne check "$demo" || break; done
make test-standard
make test-agentic
make test-probing
make test-luna
make test-ace
make test-ace-trig
make test-stall
```

Cached demo smokes are machinery checks, not held-out solve-rate evidence.
The configured prompt directories are listed explicitly in `delphyne.yaml`;
filenames and cross-template includes keep their query-based names.

## Experiment commands and supervision

```sh
# Cached/local checks and offline reports
make test-unit
make test-rocq
make bridge-parity
make bench-rocq
make reprice
python -m tools.analysis.decision_audit
python -m tools.analysis.failure_analysis --help
make ace-x-status
make ladon-status

# Examples of paid launches: only use with a registered panel and budget
make WORKERS=16 sweep-train
python -m experiments.baselines.x_train_experiment run --max_workers=16 --wait
```

All experiment entrypoints use `OmphalosExperiment` in the common package:
per-directory locks, process supervision, machine-wide Rocq stream slots,
retained caches and statuses rebuilt from per-config ground truth. Existing
Make targets retain their arguments. `launch-status SCRIPT=<new script path>`
uses a module invocation; other scripts expose `status`, `rebuild`, `run`
and replay commands through the existing launcher.

Machine-wide capacity is `OMPHALOS_MAX_STREAMS` (the server environment sets
16); ordinary Make targets default to four workers unless overridden.
Registered review configurations retain their measured 24-worker/32-slot
profile. Slots bound concurrent Rocq work; they do not make a sequential
adaptation chain parallel. Do not revive watchdog, pkill or ulimit rituals.

The Rocq bridge uses private warm servers, stable augmented paths, deadlines,
reply bounds, memory limits and prefix/check memoization. `GoalCaps` remains
an explicit off-by-default legacy treatment. Whole-operation `ToolLimits`
in grounded search bounds different work from a single RPC timeout.

## Budgets and cache compatibility

- The Luna smoke stopping budget is $0.05; X configurations use $0.10.
  Request, tool-time, output and monetary allowances have different semantics.
- Legacy dollar stopping limits can admit a crossing request. Delphyne's
  stream admission supports hard bounds when estimates are conservative;
  the default model estimate does not itself supply dollar liability.
- The campaign ledger reserves conservative monetary liability, including
  retries and embeddings. Unknown charges remain charged at their reserved
  bound until resolved. It is separate from the per-problem search policy.
- A smaller stopping budget can be studied as a prefix of a recorded trace.
  A restart, different rendered feedback or different advice cannot be
  inferred from that trace. Exact prior-spend/request thresholds matter.
- Cache identity depends on rendered prompts and configuration directory
  names. Renaming a module is different from renaming a strategy argument or
  changing a serialized configuration default.
- Prove neutral changes using `cache_mode: replay`, which fails on a miss.
  A replay does not re-execute Rocq; use bridge parity for verifier changes.
- Do not edit templates while a running experiment renders them. Keep prompt
  bytes, query contracts and settings pinned until that run is complete.
- Preserve paid outputs, caches, frozen playbooks, campaign manifests and
  historical source snapshots. New source paths/hashes describe a new code
  revision, not rewritten provenance for an old measurement.

## Evaluation and evidence boundaries

| Data | Role |
|---|---|
| Original train/validation/test | Historical frontier and API studies; preserve their recorded configurations and exposure history |
| trainX | Development and adaptation at Luna's cost class |
| validationX | Development/selection after repeated use, not fresh confirmation |
| testX | One explicitly chosen look per headline arm; not a failure-mining pool |
| Frozen ACE challenge | 88 previously unexposed problems at registration; protected against subsequent tuning |
| Frozen Mathd reserve | 166 reserved problems; do not expose through adaptation or diagnostics |
| ladonX | Ladon selection only; its loop does not run testX |

The frozen challenge manifest also identifies 32 Terra comparator problems.
Keep whole theorem families together. Demonstration/training solutions must
not enter protected evaluation prompts; existing example eligibility checks
remain part of the suite. Do not regenerate partitions during routine cleanup.

For future non-Ladon decisions, use **two-sided p<0.10** and report 90%
descriptive intervals, effect sizes, total panel cost, cost per qualified
solve and coverage. Match all expected cells, retain platform failures in the
denominator, and cluster repeated seeds and duplicate theorem families.
Five all-favorable independent discordances can meet this significance
threshold (four one-sided); this is not a statistical-power guarantee.

The original ACE review retains p<0.05/95% intervals and its >=5-point
improvement requirement. The bounded study already used p<0.10/90% intervals.
Historical decisions stay identified by their original rules. Ladon remains
p<0.05 until its deferred grouping correction; see open hint #120.

Use `tools.analysis.paired_evaluation` for new grouped comparisons. Older
reporting scripts expose historical descriptive comparisons; pooling seeds
or reaching a discordance minimum does not establish power or equivalence.
Changing alpha does not change a cost budget or a minimum useful effect.

Prices are recomputed from recorded tokens using dated entries in
`runtime/model_registry.py`. Prepend rate changes; never rewrite old rates.
Distinguish billed-at-the-time costs from later repricing. `make reprice`
must pass; dated-rate differences in its output are expected.

## Verification and local records

Before handing back code, run Ruff on touched Python files, Omphalos
`make test`, direct `pyright -p examples/omphalos` and repository-root
`make pyright`. A failure elsewhere is reported separately rather than
silently changing another example. Verifier changes also need meaningful
bridge-parity cases; a first-three sample may miss multi-goal behavior.

AGENTS is canonical; never replace CLAUDE symlinks with copies. Current
local notes, closed-hint history and shared memory remain untracked.
Tracked files stay tracked after moving. The blanket Git exclude hides new
files, so review intentional new source files explicitly before staging.

HINTS contains unresolved work only. Closing an item moves its numbered
outcome to `docs/CLOSED_HINTS.md`; PROGRESS holds the important dated finding.
Allocate IDs across both files and preserve them on reopening. Neither
harness edits these records during an active Ladon night.
