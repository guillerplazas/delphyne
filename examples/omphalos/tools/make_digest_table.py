"""
A deterministic playbook from the digest — the control for curation.

No LLM anywhere: from the recorded rejections of the adaptation pool
(the trainX baseline and the x5 chain's generator cells — the pool
every ACE playbook learned from) build a `Playbook` of at most eight
bullets: one per identifier Rocq reported as not found at least
`--min-count` times, stating that it does not exist here and which
replacements the prover's next accepted proposal used instead
(`ace_repairs.name_replacements`), plus at most two lines for the
fine failure classes the digest never showed a curator (`ring-failure`,
`unify-failure`) with their most frequent accepted replacement heads.
Frozen as `experiments/playbooks/<out>` with a provenance sidecar
(`source: deterministic`), never overwritten with a different hash.

Evaluated like any frozen playbook (`--playbook=ace_digest_table.yaml
--render_version=2`), it answers, paired on the same cells: does the
LLM-curated playbook add anything over what the verifier's own record
yields for free?

Usage:
    python tools/make_digest_table.py [--min-count 3] [--out ace_digest_table.yaml]
"""

# pyright: strict

import argparse
import datetime as dt
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_OMPHALOS_DIR))
sys.path.insert(0, str(_OMPHALOS_DIR / "tools"))

from ace_evidence import tactic_head, unknown_identifier  # noqa: E402
from ace_playbook import Bullet, Playbook  # noqa: E402
from ace_repairs import Repair, mine_run, name_replacements  # noqa: E402
from failure_analysis import (  # noqa: E402
    _feedback_entries,  # pyright: ignore[reportPrivateUsage]
)

PLAYBOOKS_DIR = _OMPHALOS_DIR / "experiments" / "playbooks"
POOL: tuple[tuple[str, str | None], ...] = (
    ("x_train_agentic", None),
    ("ace_adaptation_x5-offline", "_generator_"),
)
FINE_CLASSES = ("ring-failure", "unify-failure")
MAX_BULLETS = 8


def name_counts(runs: list[tuple[Path, str | None]]) -> Counter[str]:
    """How often each unknown identifier was rejected on the pool."""
    counts: Counter[str] = Counter()
    for run, only in runs:
        for cache in run.glob("configs/*/cache.yaml"):
            if only and only not in cache.parent.name:
                continue
            for fb in _feedback_entries(cache):
                if fb.get("success"):
                    continue
                name = unknown_identifier(str(fb.get("error_message") or ""))
                if name:
                    counts[name] += 1
    return counts


def class_replacements(repairs: list[Repair]) -> dict[str, Counter[str]]:
    out: dict[str, Counter[str]] = {c: Counter() for c in FINE_CLASSES}
    for r in repairs:
        if r.fine_class in out and r.after:
            out[r.fine_class][tactic_head(r.after[0])] += 1
    return out


def build(min_count: int) -> tuple[Playbook, dict[str, Any]]:
    runs = [
        (_OMPHALOS_DIR / "experiments" / "output" / name, only)
        for name, only in POOL
    ]
    repairs: list[Repair] = []
    for run, only in runs:
        repairs.extend(mine_run(run, only=only))
    counts = name_counts(runs)
    replacements = name_replacements(repairs)
    bullets: list[Bullet] = []
    prov_names: list[dict[str, Any]] = []
    for name, n in counts.most_common():
        if n < min_count or len(bullets) >= MAX_BULLETS - len(FINE_CLASSES):
            break
        heads = replacements.get(name, Counter()).most_common(3)
        if heads:
            used = ", ".join(f"`{h}` ({c})" for h, c in heads)
            content = (
                f"`{name}` does not exist in this environment (rejected {n}"
                f" times on this benchmark). The replacements that the"
                f" verifier then accepted started with: {used}."
            )
        else:
            content = (
                f"`{name}` does not exist in this environment (rejected {n}"
                " times on this benchmark); use a Rocq stdlib tactic or"
                " lemma instead."
            )
        bullets.append(
            Bullet(
                id=f"rocq-{len(bullets) + 1:05d}",
                section="pitfalls",
                content=content,
            )
        )
        prov_names.append({"name": name, "count": n, "replacements": heads})
    by_class = class_replacements(repairs)
    prov_classes: list[dict[str, Any]] = []
    blurbs = {
        "ring-failure": "`ring` was rejected with 'not a valid ring equation'",
        "unify-failure": "`apply`/`exact` was rejected with 'Unable to unify'",
    }
    for cls in FINE_CLASSES:
        heads = by_class[cls].most_common(3)
        n = sum(by_class[cls].values())
        if not heads:
            continue
        used = ", ".join(f"`{h}` ({c})" for h, c in heads)
        content = (
            f"When {blurbs[cls]}, the replacements the verifier then"
            f" accepted on this benchmark ({n} repairs) started with: {used}."
        )
        bullets.append(
            Bullet(
                id=f"rocq-{len(bullets) + 1:05d}",
                section="pitfalls",
                content=content,
            )
        )
        prov_classes.append(
            {"class": cls, "repairs": n, "replacements": heads}
        )
    pb = Playbook(next_id=len(bullets) + 1, bullets=bullets)
    prov: dict[str, Any] = {
        "source": "deterministic",
        "built": dt.date.today().isoformat(),
        "pool": [f"{n}:{o}" if o else n for n, o in POOL],
        "min_count": min_count,
        "repairs_mined": len(repairs),
        "names": prov_names,
        "classes": prov_classes,
        "render_version": 2,
    }
    return pb, prov


def main() -> int:
    parser = argparse.ArgumentParser(
        description="A deterministic playbook from the digest (no LLM)."
    )
    parser.add_argument("--min-count", type=int, default=3)
    parser.add_argument("--out", default="ace_digest_table.yaml")
    args = parser.parse_args()
    pb, prov = build(int(args.min_count))
    print(pb.render_prompt())
    print(f"\n{len(pb.bullets)} bullets, ~{pb.token_estimate()} tokens")
    target = PLAYBOOKS_DIR / str(args.out)
    if target.exists():
        existing = Playbook.load(target)
        assert existing.sha256() == pb.sha256(), (
            f"refusing to overwrite {target.name}: sha"
            f" {existing.sha256()[:8]} -> {pb.sha256()[:8]}"
        )
        print(f"unchanged: {target.name} ({pb.sha256()[:8]})")
        return 0
    pb.save(target)
    prov["sha256"] = pb.sha256()
    (PLAYBOOKS_DIR / f"{target.stem}.provenance.yaml").write_text(
        yaml.safe_dump(prov, sort_keys=False, allow_unicode=True)
    )
    print(f"frozen {target.name} ({pb.sha256()[:8]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
