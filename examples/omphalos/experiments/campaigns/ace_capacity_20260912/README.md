# ACE capacity follow-up — 2026-09-12

Completed: see [RESULTS.md](RESULTS.md), [CASE_APPENDIX.md](CASE_APPENDIX.md),
[CREATOR_APPENDIX.md](CREATOR_APPENDIX.md), and [ARTIFACTS.md](ARTIFACTS.md).
Follow-up spend $23.25562298; combined spend $62.14069790/$75. No default
promotion. The authoritative mechanism reports have the `_v2` suffix.

Approved follow-up to the completed attribution study. The frozen protocol
is `protocol.json`; full X panels contain 40 problems and every run uses
seed 0. Only Luna and Terra are authorized. The follow-up spends at most
$36.11492508, through the original campaign's single $75 ledger.

The model/book crossover reuses 176 observations and adds 64 missing swaps.
Matched creation probes make 200 role jobs on frozen inputs, without a new
generator curriculum. Eight selected trainX problems receive five matched
configurations per solver (80 episodes). The 32 no-book/corrected-book cells
are eligible for money-only and then broader-search continuation. Solved
cells are carried forward, and every continuation replays its paid prefix.

Use the same entry point from either agent harness, from `examples/omphalos`:

```sh
python -m experiments.ace.ace_capacity_experiment status
python -m experiments.ace.ace_capacity_experiment campaign
```

`launch.sh` runs the campaign in a supervised tmux session. Each batch uses
`OmphalosExperiment`, 24 workers and the registered 32-stream runtime profile.
All generative requests reserve through the shared ledger. Stage transfers
move unused capacity without increasing the total ceiling.

`prior_source_manifest.json`, `prior_source/`, and `prior_ledger.sqlite3`
preserve the preceding sealed state. The original study's live source seal
will correctly detect the opt-in additions in the working tree; use the
archived source when reproducing that version. Its frozen measurements and
books are unchanged. `closure_correction.json` corrects the earlier no-access
claim; `prior_verification.json` preserves the original verification document.

`runtime/replay_admission.py` records transport state and exact admission
decisions outside prompts. Raw snapshots stay local under `transport/` and
are referenced by hashes in the final artifact inventory. Source-bound
snippet checks certify the recorded witness only, not arbitrary future use.

testX and protected challenge data remain excluded. Use the development-only
guard before imports and explicit source inventories for analysis. Never
invoke global partition checks, global repricing, or Ladon CLI status here.

The flagship remains the reference. Diagnostic results on eight selected
training problems do not establish representative coverage or an intrinsic
model ceiling. Any missing/admin-censored panel has no experimental verdict.
