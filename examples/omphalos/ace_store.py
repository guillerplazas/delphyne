"""
Content-addressed storage for ACE playbooks and their step records.

Why content addressing. The first driver addressed the playbook a step
consumed by *step index* (`playbook_step_NN.yaml`), but a step file is
only written after the previous step's merge — so a batch of size four
handed steps N+1..N+3 files that did not exist yet, and on a rerun
files whose hash no longer matched the recorded config. The `pool`
variant died on its second config for exactly this reason. Every
config already pins the playbook it ran with by sha256; storing the
playbook *under that hash* makes the pin the address, and the batch
semantics of the paper (every member sees the batch-start context)
fall out for free.

Layout, per variant directory (`experiments/playbooks/ace_adaptation_
<variant>/`, unsuffixed for the legacy `train` run):

    by_hash/<sha256>.yaml     source of truth, write-once
    playbook_step_NN.yaml     derived index: state BEFORE global step NN;
                              regenerated each run, stale files pruned
    steps.csv                 per-step structural record (schema v2)
    refine.log.yaml           what each refine pass pruned/merged
    embeddings.cache.h5       the EmbeddingDeduper's cache (with the
                              playbooks, so it outlives clean-experiments)
    final.sha256              online variants: the last playbook
"""

# pyright: strict

import csv
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import yaml

from ace_playbook import Playbook

_OMPHALOS_DIR = Path(__file__).resolve().parent
PLAYBOOKS_DIR = _OMPHALOS_DIR / "experiments" / "playbooks"

LEGACY_VARIANT = "train"
"""
The first adaptation run predates variants and owns the unsuffixed
step-playbook directory. Frozen: a variant may change the directory it
writes to, never the one the legacy run already wrote.
"""

STEPS_SCHEMA_VERSION = 4

STEP_COLUMNS: tuple[str, ...] = (
    "schema_version",
    "variant",
    "mode",
    "step",
    "epoch",
    "pos_in_epoch",
    "batch_id",
    "bench",
    "seed",
    "sha256_before",
    "sha256_after",
    "reflector",
    "curator_mode",
    "generator_solved",
    "generator_failed",
    "bullets_before",
    "tokens_before",
    "added",
    "deduped",
    "dropped",
    "tags_helpful",
    "tags_harmful",
    "refined",
    "pruned",
    "merged",
    "compacted",
    "bullets_after",
    "tokens_after",
    "curator_failed",
    "curator_fallback",
    "reflector_failed",
    "cited_count",
    "tags_dropped",
    "skipped_trivial",
    "proposed",
    "reduced_out",
    "ungrounded",
    "grounding_error",
)
"""
Schema 3 (2026-08-26) appends `cited_count` (bullet ids the generator
named in its own messages, render_version >= 3) and `tags_dropped`
(reflector tags outside the cited set, discarded under
`reflector_scope="cited"`). Schema 4 (2026-09-02) appends the
accounting the v3 record lacked: `skipped_trivial` (no Reflector /
Curator on a first-proposal solve), `proposed` (ADDs the step's
curator emitted), `reduced_out` (ADDs the batch reducer kept, on the
batch's last row — the reducer discarded 62 % of proposals in x3
without any column showing it), `ungrounded` (ADDs refused because a
referenced name does not exist in Rocq) and `grounding_error` (ADDs
kept because the bridge could not answer). Readers accept schema >= 2;
a resumed run rewrites the whole file at the current schema.
"""


def steps_dir(variant: str) -> Path:
    if variant == LEGACY_VARIANT:
        return PLAYBOOKS_DIR / "ace_adaptation"
    return PLAYBOOKS_DIR / f"ace_adaptation_{variant}"


class PlaybookStore:
    """All on-disk playbook state of one adaptation variant."""

    def __init__(self, variant: str) -> None:
        self.variant = variant
        self.dir = steps_dir(variant)
        self.by_hash = self.dir / "by_hash"

    # --- content-addressed playbooks -------------------------------

    def path(self, sha: str) -> Path:
        return self.by_hash / f"{sha}.yaml"

    def relpath(self, sha: str) -> str:
        """Omphalos-relative path, for `ACEAgenticConfig.playbook_file`."""
        return str(self.path(sha).relative_to(_OMPHALOS_DIR))

    def has(self, sha: str) -> bool:
        return self.path(sha).exists()

    def put(self, pb: Playbook) -> str:
        """Store `pb` under its hash; a no-op if already present."""
        sha = pb.sha256()
        target = self.path(sha)
        if target.exists():
            assert Playbook.load(target).sha256() == sha, (
                f"{target} does not hash to its own name"
            )
            return sha
        pb.save(target)
        return sha

    def get(self, sha: str) -> Playbook:
        pb = Playbook.load(self.path(sha))
        assert pb.sha256() == sha, f"{self.path(sha)} is corrupt"
        return pb

    def materialize_legacy_steps(self) -> int:
        """
        Copy every `playbook_step_NN.yaml` into `by_hash/`. Idempotent;
        returns the number of files newly stored. Run once per variant
        so archived configs resolve through the hash like new ones.
        """
        n = 0
        for f in sorted(self.dir.glob("playbook_step_*.yaml")):
            pb = Playbook.load(f)
            if not self.has(pb.sha256()):
                self.put(pb)
                n += 1
        return n

    # --- derived step index ---------------------------------------

    def step_path(self, step: int) -> Path:
        return self.dir / f"playbook_step_{step:02d}.yaml"

    def write_step_index(self, shas: Sequence[str]) -> None:
        """
        `playbook_step_NN.yaml` = the playbook before step NN, for
        NN in `range(len(shas))`; every file with a higher NN is a
        leftover from a longer earlier run and is deleted.
        """
        for step, sha in enumerate(shas):
            target = self.step_path(step)
            content = self.path(sha).read_text()
            if not target.exists() or target.read_text() != content:
                target.write_text(content)
        for f in self.dir.glob("playbook_step_*.yaml"):
            n = int(f.stem.rsplit("_", 1)[1])
            if n >= len(shas):
                f.unlink()

    # --- records --------------------------------------------------

    @property
    def steps_csv(self) -> Path:
        return self.dir / "steps.csv"

    def write_steps_csv(self, rows: Sequence[Mapping[str, object]]) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        with self.steps_csv.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(STEP_COLUMNS))
            writer.writeheader()
            for row in rows:
                writer.writerow({c: row.get(c, "") for c in STEP_COLUMNS})

    def read_steps_csv(self) -> list[dict[str, str]]:
        if not self.steps_csv.exists():
            return []
        with self.steps_csv.open(newline="") as f:
            return list(csv.DictReader(f))

    @property
    def refine_log(self) -> Path:
        return self.dir / "refine.log.yaml"

    def append_refine_log(self, event: Mapping[str, Any]) -> None:
        events: list[Any] = []
        if self.refine_log.exists():
            loaded: Any = yaml.safe_load(self.refine_log.read_text())
            events = cast(list[Any], loaded or [])
        events.append(dict(event))
        self.refine_log.write_text(yaml.safe_dump(events, sort_keys=False))

    def reset_refine_log(self) -> None:
        if self.refine_log.exists():
            self.refine_log.unlink()

    # --- v5 sidecars (2026-09-02) ---------------------------------

    @property
    def provenance_file(self) -> Path:
        """`bullets.provenance.yaml`: where every bullet came from."""
        return self.dir / "bullets.provenance.yaml"

    def read_provenance(self) -> dict[str, dict[str, Any]]:
        if not self.provenance_file.exists():
            return {}
        loaded: Any = yaml.safe_load(self.provenance_file.read_text())
        return cast(dict[str, dict[str, Any]], loaded or {})

    def write_provenance(
        self, records: Mapping[str, Mapping[str, Any]]
    ) -> None:
        """
        Whole-file rewrite, keys sorted by bullet id: the record is
        derived from the run and regenerated on every resume, like the
        step index. Kept OUT of the playbook YAML on purpose — a new
        `Bullet` field would change every frozen playbook's sha256.
        """
        self.dir.mkdir(parents=True, exist_ok=True)
        ordered = {k: dict(records[k]) for k in sorted(records)}
        self.provenance_file.write_text(
            yaml.safe_dump(ordered, sort_keys=False)
        )

    @property
    def grounding_log(self) -> Path:
        return self.dir / "grounding.log.yaml"

    @property
    def audit_log(self) -> Path:
        return self.dir / "audit.log.yaml"

    def append_log(self, path: Path, event: Mapping[str, Any]) -> None:
        events: list[Any] = []
        if path.exists():
            loaded: Any = yaml.safe_load(path.read_text())
            events = cast(list[Any], loaded or [])
        events.append(dict(event))
        self.dir.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(events, sort_keys=False))

    def reset_logs(self) -> None:
        """A run re-derives its logs from scratch, like the refine log."""
        for path in (self.grounding_log, self.audit_log):
            if path.exists():
                path.unlink()

    @property
    def embeddings_cache(self) -> Path:
        return self.dir / "embeddings.cache.h5"

    @property
    def final_sha_file(self) -> Path:
        return self.dir / "final.sha256"
