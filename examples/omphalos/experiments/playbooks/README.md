# Frozen ACE playbooks

Artifacts of `experiments/ace_adaptation.py` (ACE context adaptation,
arXiv:2510.04618, adapted to miniF2F-Rocq — see that script's
docstring for the method and deviations).

## Layout

One directory per adaptation variant (`ace_adaptation_<variant>/`;
the 2026-08-24 `train` run predates variants and owns the unsuffixed
`ace_adaptation/`), managed by `ace_store.PlaybookStore`:

- `by_hash/<sha256>.yaml` — **the source of truth**: every playbook
  state a step consumed, stored under its content hash, write-once.
  A config pins the playbook it ran with by this hash, so a batch of
  size > 1 sees the batch-start playbook by construction and a rerun
  can never resolve a config against drifted content.
- `playbook_step_NN.yaml` — derived index: the state BEFORE global
  step NN (step 00 = empty, or the warm-up playbook). Regenerated on
  every run; files from a longer earlier run are deleted.
- `steps.csv` — per-step structural record, schema v2 (`epoch`,
  `pos_in_epoch`, `sha256_before/after`, `generator_solved`, dedup /
  refine counts, `curator_failed`, `reflector_failed`). Spend is
  deliberately absent — it lives in the experiment's
  `results_summary.csv`.
- `refine.log.yaml` — which bullets each refine pass pruned, merged
  or compacted.
- `embeddings.cache.h5` — the `EmbeddingDeduper`'s cache. Part of the
  record: `replay` runs it in replay mode and fails on a miss.
- `final.sha256` — online variants only: the last playbook of the
  chain (online variants freeze nothing; their generator cells are
  the result).

Frozen playbooks at the top level, each with a `.provenance.yaml`
sidecar (variant, pool, epochs, shuffle seed, dedup, refine cadence,
warm-up hash):

- `ace_v1.yaml` — one epoch on train, 2026-08-24 (v1 machinery);
  pinned by 60 paid evaluation configs.
- `ace_noreflect.yaml` — the no-Reflector ablation on train, v1.
- `ace_x_offline.yaml`, `ace_x_offline_e3.yaml`, `ace_x_noreflect.yaml`,
  `ace_x_mono.yaml` — the X-partition matrix (trainX, v2 machinery),
  consumed by `experiments/ace_x_{validation,test}_experiment.py`.

**Never edit a frozen playbook in place.** Its sha256 is part of every
evaluation config's identity; `_freeze` refuses to overwrite one whose
hash would change. A re-adaptation produces a new file and a new
evaluation run, exactly like the dated-pricing rule (prepend, never
edit).

This directory sits OUTSIDE `experiments/output/` on purpose:
`make clean-experiments` deletes that tree wholesale, and a frozen
playbook must outlive the caches of the runs that produced it.

- `ace_x3_offline.yaml` — v3 offline (sha `1e4aec7d`, 26 bullets):
  trainX, one shuffled epoch, batch 4 + reducer, render_version 3 /
  curator contract 3, 2026-08-25/26. Evaluated at rv3 in
  `ace_x_validation_ace_x3_offline_rv3_agentic` (the earlier
  `…x3_offline_agentic` directory scored the v2 playbook — see
  PROGRESS 2026-08-26 afternoon, finding A1).
- `ace_x3_noreflect.yaml` — v3 no-Reflector (sha `ce233fe0`, 27).
- `ace_x3_mono.yaml` — v3 monolithic rewrite (sha `0e162d51`, 41;
  `next_id` 639: 638 bullets created and mostly discarded across 40
  rewrites).
- `ace_x3_offline_e3.yaml` — v3, 3 epochs at the 8k guard (frozen by
  `make ace-x3-e3-val` when its adaptation completes).
- `ace_x4_offline.yaml` — v4: `x3-offline` + `reflector_scope="cited"`
  (the reference's attribution channel), frozen by `make
  ace-x4-val-offline`. `steps.csv` schema 3 adds `cited_count` and
  `tags_dropped`.
- Hashes of the other frozen files (migrated from HANDOFF.md, 2026-09-02):
  v2 `ace_x_offline.yaml` (sha `1ac8a092`, 49 bullets),
  `ace_x_noreflect.yaml` (`d56da056`, 52), `ace_x_mono.yaml`
  (`fa985e70`, 40), `ace_x_offline_e3.yaml` (`07ee107d`, 44); v3
  `ace_x3_offline_e3.yaml` (`d0d7ce24`, 54, 120 steps); v4
  `ace_x4_offline.yaml` (`f1dd5c3a`, 27). Every sidecar carries the
  full sha256.

## 2026-09-02 — role strength and v5 (evidence-first curation)

- `ace_x3_strong.yaml` — `x3-offline` with gpt-5.6-terra as Reflector
  and as every curation role (curator, reducer); the Generator stays
  luna (HINTS #49's minimal pair). Frozen 2026-09-02 (sha `b596e7df`,
  28 bullets, ~2.4k tokens).
- `ace_x5_offline_preaudit.yaml` / `ace_x5_offline.yaml` — v5: the
  playbook after the 40th step, and the same playbook after the one
  terminal `AuditPlaybook` pass (default-keep, per-bullet reasons,
  grounded additions). Both carry a provenance sidecar; the audited
  one records `preaudit_playbook`, `audit_config` and what the audit
  dropped / rewrote / added.
- New per-variant sidecars under `ace_adaptation_<variant>/`:
  `bullets.provenance.yaml` (per bullet: step, origin problems and
  whether they were solved, section, references, source — curator /
  reducer / audit; kept out of the playbook YAML so frozen hashes
  never move), `grounding.log.yaml` (per batch: every `Locate`
  verdict and every refused ADD with the names Rocq did not know) and
  `audit.log.yaml`. `steps.csv` is schema 4 (`skipped_trivial`,
  `proposed`, `reduced_out`, `ungrounded`, `grounding_error`).

