# HANDOFF — ACE-X study, complete (updated 2026-08-27 11:00)

Read with `PROGRESS.md` (2026-08-26 entries: the platform rebuild in
the morning, the ACE audit + relaunch in the afternoon) and `HINTS.md`.
The previous HANDOFF's science claims were wrong in one decisive way:
**every "v3" evaluation had scored the v2 playbook** (finding A1), so
"the v3 offline null replicates" was the same playbook measured twice.
Treat the numbers below as the current truth and everything older
about v3 evaluations as void.

## Operating model (the rituals of 2026-08-25 are retired)

- Launch: `python experiments/<script>.py run --max_workers=4 --wait`
  (or the Makefile targets). Several launches at once are fine — they
  queue on the 4 machine-wide Rocq stream slots.
- `make ace-x-status` — every X/ACE directory by arm (sha8 + render
  version): done / failed / todo from ground truth, lock holders, slots.
- `make launches` — who holds what. `make stop` — stop everything
  (frees the RAM within a minute; in-flight cells re-paid on resume)
  and print the resume commands. `make -j3 ace-x-matrix` — re-queue
  the whole matrix (idempotent).
- Never resume the two mis-run directories
  `ace_x_validation_ace_x3_offline_agentic` /
  `…_x3_noreflect_agentic`: they are v2-replicate evidence now; the
  corrected v3 runs live in `…_rv3_agentic` directories (the scripts
  refuse a directory holding another arm's cells).

## State of the matrix (final, 2026-08-27 11:00; `make ace-x-status`)

| arm | dir | state |
|---|---|---|
| E0 testX baseline | `x_test_agentic` | done: 32/40, $0.50 (one look) |
| v3 offline eval (rv3) | `…_x3_offline_rv3_agentic` | done: 57 vs 54, 3–0, 0 failed |
| v3 offline testX | `ace_x_test_ace_x3_offline_rv3_agentic` | done: 32 vs 32, 1–1 |
| v3 noreflect eval | `…_x3_noreflect_rv3_agentic` | done: 57 vs 54, 3–0, 0 failed (after 1 retry) |
| v3 noreflect testX | `ace_x_test_ace_x3_noreflect_rv3_agentic` | done: 31 vs 32, 0–1 |
| v3 mono eval | `…_x3_mono_rv3_agentic` | done: 55 vs 54, 2–1 |
| x3-online-s0 / s1 | `ace_online_x3-online-s{0,1}_agentic` | done: 28 vs 27 (1–0, 2 failed) / 27 vs 27 (0–0) |
| x4-offline adapt → eval | `…_ace_x4_offline_rv3_agentic` | done: 55 vs 54 vs baseline (3–2); 55 vs 57 vs x3 (2–4) → no testX |
| x4-online-s0 | `ace_online_x4-online-s0_agentic` | done: 27 vs 27 (1–1) |
| x3-offline-e3 adapt → eval | `…_ace_x3_offline_e3_rv3_agentic` | done: 53 vs 54 (4–5); vs x3 53 vs 57 (1–5) |
| x3-online-testX | `ace_online_x3-online-testX_agentic` | done: 32 vs 32 (1–1) |

Report published as a private Artifact: https://claude.ai/code/artifact/3de1edac-d97a-43bd-b9d9-070ea11bc3e1 (republish the same file path to update).

## Remaining steps, in order

1. Let the queue drain (`make ace-x-status`). For any eval directory
   with failed cells: one `python experiments/ace_x3_validation_experiment.py
   --playbook=<pb> run --max_workers=4 --retry_errors --wait`; what
   still fails is the recorded outcome (scored unsolved, flagged).
2. Selection readout on validationX (`python tools/ace_x_report_data.py`
   then read `report/ace_x_report.data.json` → `X_PAIRED.validationX`):
   pre-registered rule in `experiments/ace_x_validation_experiment.py`
   — an arm goes to testX only if it beats the baseline on paired
   solves, or at equal solves is cheaper at p<0.05; the v3 offline
   playbook goes regardless (headline arm). x4 goes if it beats x3.
3. testX looks (one each): `make ace-x3-test-offline`; `make
   ace-x4-test-offline` if selected; an online arm on testX only if
   selected — add `x3-online-testX` / `x4-online-testX` to `VARIANTS`
   (`pool="testX"`, seed 0, cold) and run it once.
4. `python tools/ace_x_report_data.py` (regenerates the page's data +
   sidecar; `--check` must exit 0 afterwards); fill the summary prose in
   `report/ace_x_report.html` from the data (tiles, `#summary`,
   `#gen23`); publish as a private Artifact "Omphalos ACE Study" (📘).
5. Records: PROGRESS results block (spend via `make reprice`, expect
   dated-rate deltas, exit 0), README `<!-- ACE-X-RESULTS -->` table,
   HINTS statuses, the memory file, this HANDOFF.
6. Gates: `make test` (omphalos), repo-root `make pyright`, `make
   reprice`, ruff; `git add -f` new files (blanket exclude); NEVER commit.

## Facts a fresh session must not rediscover

- Frozen playbooks: v3 `ace_x3_offline` (26 bullets, `1e4aec7d`),
  `ace_x3_noreflect` (27, `ce233fe0`), `ace_x3_mono` (41, `0e162d51`);
  v2 `ace_x_offline` (49, `1ac8a092`), `ace_x_noreflect` (52,
  `d56da056`), `ace_x_mono` (40, `fa985e70`), `ace_x_offline_e3` (44,
  `07ee107d`). v4/e3 files appear when their adaptations freeze.
- `cache_mode: replay` proves prompt neutrality but never re-executes
  Rocq (`make bridge-parity` does); `ace_adaptation.py replay
  --variant=<v>` proves an adaptation chain re-derives from cache.
- The stdlib launcher persists statuses only at the end of a resume;
  the launch layer rebuilds them from `result.yaml` before/after every
  attempt. Large ACE results are scanned 2 MB deep for `outcome:`.
- Spend: ≈ $48 before today + $0.50 (testX) + the queued matrix
  (≈ $22–25 approved).
