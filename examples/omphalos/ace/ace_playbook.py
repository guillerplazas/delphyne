"""
Playbook data model and deterministic merge for the ACE pipeline.

ACE (Agentic Context Engineering, arXiv:2510.04618) represents the
LLM's accumulated experience as a *playbook*: an itemized collection of
bullets, each carrying a stable identifier, a section, a small unit of
reusable content, and helpful/harmful counters. The Curator LLM only
ever proposes incremental *delta operations* (ADD bullets); merging
them into the playbook is the job of this module and is **fully
deterministic, non-LLM code**. That split is the paper's load-bearing
design point: monolithic LLM rewrites of the whole context are what
cause "context collapse" (their Fig. 2), and keeping the merge out of
the model's hands is what prevents it.

Two generations of the grow-and-refine step coexist here, and the
frozen 2026-08-24 runs pin the first:

- **v1 (legacy, `render_markdown` + `LexicalDeduper`).** Lexical
  `SequenceMatcher` dedup at 0.90, which fired zero times in forty
  recorded steps, and counters that were recorded but gated nothing.
  Every archived adaptation run regenerates through this path, so it
  is kept byte-for-byte.
- **v2 (`render_prompt` + a pluggable `Deduper` + `refine`).** The
  paper's mechanism: near-duplicates fold by semantic similarity
  (`ace_dedup.EmbeddingDeduper`, or Jaccard offline), a periodic
  `refine` pass prunes bullets the Reflector has repeatedly tagged
  harmful and merges near-duplicates, and the Generator's prompt shows
  bullet ids but **not** counters — a counter change no longer
  perturbs the prompt, and the Generator has no use for the numbers.
  Counters keep their job on the Reflector/Curator side and in
  `refine`.

Still a documented deviation: no generator-side bullet tagging (the
Reflector infers attribution from the trajectory), and no ground-truth
labels — the Rocq verifier is the supervision.

Determinism contract: `merge` depends only on its arguments (bullet
ids are assigned from `Playbook.next_id`, never from time or
randomness), and YAML serialization uses sorted keys so that
`sha256()` is stable across runs. Experiment configs identify a
playbook by that hash.
"""

# pyright: strict

import hashlib
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Literal, Protocol, cast

import yaml

BULLET_ID_PREFIX = "rocq"
"""Prefix of every bullet id (`rocq-00042`)."""

SECTIONS: tuple[str, ...] = ("tactics", "lemmas", "pitfalls", "strategy")
"""
The playbook's section taxonomy (the Curator prompt lists the same
four). `merge` normalises Curator-emitted section names against this
list and reroutes unknowns to `"strategy"` — the reference
implementation reroutes to a catch-all too, and its AppWorld variant
drops unlisted sections outright. Without this, one hallucinated
section name grows a stray heading and quietly defeats same-section
dedup.
"""


def _normalize_section(raw: str, warnings: list[str]) -> str:
    cand = raw.strip().casefold().replace(" ", "_")
    for known in SECTIONS:
        if cand == known or cand.rstrip("s") == known.rstrip("s"):
            return known
    warnings.append(f"unknown section {raw!r} rerouted to 'strategy'")
    return "strategy"


DEFAULT_DEDUP_THRESHOLD = 0.90
"""
`SequenceMatcher.ratio()` at or above which a candidate bullet is
treated as a duplicate of an existing one in the same section. The
paper sweeps its (embedding-based) dedup knob over 50-90% with mild
effect (their Table 20); 0.90 on normalized text is the top of that
range — only near-verbatim repeats are folded.
"""

DEFAULT_MAX_TOKENS = 4000
"""
Rendered-playbook size guard (their "pruning trigger", Table 21, where
10k-100k tokens are all fine). 4k is far below the point where their
results degrade, and matters here for a reason the paper does not
have: every playbook token is resent on **every turn** of the agentic
loop, under a per-problem dollar cap.
"""


@dataclass
class Bullet:
    """One playbook item. `helpful`/`harmful` count Reflector tags."""

    id: str
    section: str
    content: str
    helpful: int = 0
    harmful: int = 0


@dataclass
class AddOp:
    """
    A Curator delta operation. ADD-only by design (v1).

    `references` (curator contract 4, 2026-09-02) names the Rocq
    objects — lemmas, definitions, Ltac tactics — the bullet relies on,
    so the grounding gate can ask Rocq whether they exist before the
    bullet enters the playbook. Defaulted, so every recorded v1-v3
    delta still parses.
    """

    type: Literal["ADD"]
    section: str
    content: str
    references: list[str] = field(default_factory=lambda: list[str]())


@dataclass
class AuditDecision:
    """
    The Auditor's verdict on one existing bullet (`apply_audit`).
    `content` is read for `rewrite` only.
    """

    id: str
    action: Literal["keep", "drop", "rewrite"]
    reason: str = ""
    content: str = ""


@dataclass
class BulletTag:
    """A Reflector verdict on one existing bullet."""

    id: str
    tag: Literal["helpful", "harmful", "neutral"]


@dataclass
class Playbook:
    """
    An ordered collection of bullets plus the next fresh id number.

    Bullet order is insertion order; rendering groups by section but
    keeps insertion order within each section, so output is stable
    under append-only growth.
    """

    next_id: int = 1
    bullets: list[Bullet] = field(default_factory=lambda: list[Bullet]())

    @staticmethod
    def load(path: Path) -> "Playbook":
        raw: Any = yaml.safe_load(path.read_text())
        assert isinstance(raw, dict), f"malformed playbook file: {path}"
        data = cast(dict[str, Any], raw)
        bullets = [
            Bullet(
                id=str(b["id"]),
                section=str(b["section"]),
                content=str(b["content"]),
                helpful=int(b["helpful"]),
                harmful=int(b["harmful"]),
            )
            for b in cast(list[dict[str, Any]], data.get("bullets", []))
        ]
        return Playbook(next_id=int(data["next_id"]), bullets=bullets)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._canonical_yaml())

    def _canonical_yaml(self) -> str:
        # `sort_keys=True` (the default) makes the dump — and hence
        # `sha256` — independent of dataclass field order.
        return yaml.safe_dump(asdict(self), sort_keys=True)

    def sha256(self) -> str:
        return hashlib.sha256(self._canonical_yaml().encode()).hexdigest()

    def sections(self) -> list[str]:
        """Distinct sections, in first-appearance order."""
        seen: dict[str, None] = {}
        for b in self.bullets:
            seen.setdefault(b.section, None)
        return list(seen)

    def render_markdown(self) -> str:
        """
        Render for prompt injection: one `### section` heading per
        section (first-appearance order), one line per bullet with its
        id and counters, insertion order within the section. This
        exact rendering is part of the LLM prompt, so any change to it
        invalidates ACE caches — change with the same care as a
        template.
        """
        if not self.bullets:
            return "(the playbook is empty so far)"
        lines: list[str] = []
        for section in self.sections():
            lines.append(f"### {section}")
            for b in self.bullets:
                if b.section != section:
                    continue
                lines.append(
                    f"- [{b.id}] (helpful={b.helpful},"
                    f" harmful={b.harmful}) {b.content}"
                )
            lines.append("")
        return "\n".join(lines).rstrip()

    def render_prompt(self) -> str:
        """
        The v2 rendering for the *Generator's* prompt.

        Empty playbook → `""`, so the ACE template's
        `{% if query.playbook %}` guard emits nothing and the prompt is
        byte-identical to the agentic baseline's (adaptation step 0
        and a cold online start are then true baseline cells). Bullets
        carry their id — the Reflector tags by id — but no counters.
        Like `render_markdown`, this text is part of the LLM prompt:
        change it with the care of a template.
        """
        if not self.bullets:
            return ""
        lines: list[str] = []
        for section in self.sections():
            lines.append(f"### {section}")
            for b in self.bullets:
                if b.section == section:
                    lines.append(f"- [{b.id}] {b.content}")
            lines.append("")
        return "\n".join(lines).rstrip()

    def token_estimate(self) -> int:
        """Crude 4-chars-per-token estimate of the rendered size."""
        return len(self.render_markdown()) // 4


@dataclass
class MergeOutcome:
    """
    Result of one deterministic merge.

    Attributes:
        playbook: The merged playbook (a fresh object; inputs are
            never mutated).
        added: Ids of newly created bullets, in creation order.
        deduped: `(existing_id, content)` pairs for ADD ops folded
            into an existing bullet as near-duplicates.
        dropped: Contents of ADD ops refused by the size guard.
        warnings: Human-readable anomalies (e.g. tags for unknown
            ids), recorded rather than raised — reflection noise must
            never abort an adaptation run.
    """

    playbook: Playbook
    added: list[str]
    deduped: list[tuple[str, str]]
    dropped: list[str]
    warnings: list[str]


@dataclass
class RewriteBullet:
    """
    One bullet of a *monolithic* rewrite: no id, no counters.

    The monolithic curator authors the whole playbook in one go, so it
    cannot be trusted with identifiers — ids are re-assigned by
    `rebuild` from the playbook's own counter, never by the model.
    """

    section: str
    content: str


class Deduper(Protocol):
    """Structural twin of `ace_dedup.Deduper` (kept here to avoid a cycle)."""

    name: str
    threshold: float
    same_section_only: bool

    def closest(
        self, candidate: str, existing: Sequence[Bullet]
    ) -> tuple[Bullet, float] | None: ...


def _normalize(text: str) -> str:
    """Casefold, collapse whitespace, strip a trailing period."""
    collapsed = re.sub(r"\s+", " ", text).strip().casefold()
    return collapsed.removesuffix(".")


@dataclass
class _LegacyLexical:
    """`merge`'s built-in v1 rule; identical to `ace_dedup.LexicalDeduper`."""

    threshold: float
    name: str = "lexical"
    same_section_only: bool = True

    def closest(
        self, candidate: str, existing: Sequence[Bullet]
    ) -> tuple[Bullet, float] | None:
        nc = _normalize(candidate)
        for b in existing:
            nb = _normalize(b.content)
            if nb == nc:
                return b, 1.0
            ratio = SequenceMatcher(None, nb, nc).ratio()
            if ratio >= self.threshold:
                return b, ratio
        return None


def _pool(
    deduper: Deduper, bullets: Sequence[Bullet], section: str
) -> list[Bullet]:
    if deduper.same_section_only:
        return [b for b in bullets if b.section == section]
    return list(bullets)


def merge(
    pb: Playbook,
    ops: Sequence[AddOp],
    tags: Sequence[BulletTag],
    *,
    deduper: Deduper | None = None,
    dedup_threshold: float = DEFAULT_DEDUP_THRESHOLD,
    dedup_counts_helpful: bool = True,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> MergeOutcome:
    """
    Deterministically fold one adaptation step into the playbook.

    In order: (1) apply `tags` to existing bullet counters (a tag for
    an unknown id is a warning, not an error — the Reflector infers
    ids from rendered text and can slip); (2) apply `ops` in sequence,
    where an op whose content the `deduper` deems a near-duplicate of
    an existing bullet is folded into that bullet instead of growing
    the playbook — under the v1 rule (`dedup_counts_helpful=True`) the
    fold also increments `helpful`, which conflates "recurred" with
    "helped" and is why v2 variants pass `False`; (3) refuse —
    deterministically, without any LLM rewrite — every ADD that would
    push the rendered playbook past `max_tokens`, recording it in
    `dropped`.

    `deduper=None` selects the legacy lexical rule at `dedup_threshold`,
    so every archived adaptation run regenerates unchanged.
    """
    dd: Deduper = (
        deduper if deduper is not None else _LegacyLexical(dedup_threshold)
    )
    merged = Playbook(
        next_id=pb.next_id,
        bullets=[Bullet(**asdict(b)) for b in pb.bullets],
    )
    warnings: list[str] = []

    by_id = {b.id: b for b in merged.bullets}
    for t in tags:
        target = by_id.get(t.id)
        if target is None:
            warnings.append(f"tag for unknown bullet id {t.id!r} ignored")
            continue
        if t.tag == "helpful":
            target.helpful += 1
        elif t.tag == "harmful":
            target.harmful += 1

    added: list[str] = []
    deduped: list[tuple[str, str]] = []
    dropped: list[str] = []
    for op in ops:
        if op.type != "ADD":  # pyright: ignore[reportUnnecessaryComparison]
            warnings.append(f"non-ADD operation {op.type!r} ignored")
            continue
        section = _normalize_section(op.section, warnings)
        hit = dd.closest(op.content, _pool(dd, merged.bullets, section))
        if hit is not None:
            duplicate, _score = hit
            if dedup_counts_helpful:
                duplicate.helpful += 1
            deduped.append((duplicate.id, op.content))
            continue
        candidate = Bullet(
            id=f"{BULLET_ID_PREFIX}-{merged.next_id:05d}",
            section=section,
            content=op.content,
        )
        merged.bullets.append(candidate)
        if merged.token_estimate() > max_tokens:
            merged.bullets.pop()
            dropped.append(op.content)
            warnings.append(
                f"size guard ({max_tokens} tokens) refused an ADD to"
                f" section {op.section!r}"
            )
            continue
        merged.next_id += 1
        added.append(candidate.id)

    return MergeOutcome(
        playbook=merged,
        added=added,
        deduped=deduped,
        dropped=dropped,
        warnings=warnings,
    )


@dataclass
class RefineOutcome:
    """
    Result of one `refine` pass.

    Attributes:
        playbook: The refined playbook (inputs never mutated).
        pruned: Bullets removed because the Reflector tagged them
            harmful more often than helpful.
        merged: `(kept_id, dropped_id, similarity)` for near-duplicate
            pairs folded together.
        compacted: Bullets removed by the size guard, lowest score first.
    """

    playbook: Playbook
    pruned: list[Bullet]
    merged: list[tuple[str, str, float]]
    compacted: list[Bullet]


def refine(
    pb: Playbook,
    deduper: Deduper,
    *,
    prune_harmful: bool = True,
    min_harmful: int = 2,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> RefineOutcome:
    """
    The paper's "refine" half of grow-and-refine, run proactively.

    (1) If `prune_harmful`, drop every bullet with `harmful > helpful`
    and `harmful >= min_harmful` — one stray tag is noise, a pattern is
    evidence. (2) Walk the survivors in id order and fold each later
    bullet the `deduper` matches to an earlier one into it: the earlier
    id and content are kept (stable prompt prefix) and the counters
    are summed. (3) If the rendering still exceeds `max_tokens`, drop
    bullets by lowest `helpful - harmful` (ties: newest first) until
    it fits. Pure given the deduper; `next_id` is untouched, so ids are
    never reused.
    """
    survivors = [Bullet(**asdict(b)) for b in pb.bullets]
    pruned: list[Bullet] = []
    if prune_harmful:
        keep: list[Bullet] = []
        for b in survivors:
            if b.harmful > b.helpful and b.harmful >= min_harmful:
                pruned.append(b)
            else:
                keep.append(b)
        survivors = keep

    merged: list[tuple[str, str, float]] = []
    kept: list[Bullet] = []
    for b in survivors:
        hit = deduper.closest(b.content, _pool(deduper, kept, b.section))
        if hit is None:
            kept.append(b)
            continue
        target, score = hit
        target.helpful += b.helpful
        target.harmful += b.harmful
        merged.append((target.id, b.id, round(score, 4)))

    refined = Playbook(next_id=pb.next_id, bullets=kept)
    compacted: list[Bullet] = []
    while refined.bullets and refined.token_estimate() > max_tokens:
        victim = min(
            refined.bullets,
            key=lambda b: (
                b.helpful - b.harmful,
                -int(b.id.rsplit("-", 1)[1]),
            ),
        )
        refined.bullets.remove(victim)
        compacted.append(victim)
    return RefineOutcome(
        playbook=refined, pruned=pruned, merged=merged, compacted=compacted
    )


@dataclass
class AuditOutcome:
    """
    Result of `apply_audit`.

    Attributes:
        playbook: The audited playbook (inputs never mutated).
        kept: Ids kept verbatim (explicitly or by default).
        dropped: Ids removed, with the Auditor's reason.
        rewritten: Ids whose content changed, counters preserved.
        added: Ids of the Auditor's additions that fit.
        refused: Contents of additions refused by the size guard.
        warnings: Unknown ids, empty rewrites, duplicate decisions.
    """

    playbook: Playbook
    kept: list[str]
    dropped: list[tuple[str, str]]
    rewritten: list[str]
    added: list[str]
    refused: list[str]
    warnings: list[str]


def apply_audit(
    pb: Playbook,
    decisions: Sequence[AuditDecision],
    additions: Sequence[AddOp],
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> AuditOutcome:
    """
    Apply one terminal audit pass deterministically.

    Unlike `rebuild` (the monolithic ablation, where whatever the model
    omits is deleted), the audit is *default-keep*: a bullet the model
    does not mention survives unchanged, `drop` needs an explicit
    decision, and `rewrite` keeps the id and both counters — so the
    prompt prefix stays stable for every bullet the audit left alone
    and no counter is lost by construction. Additions get fresh ids
    and pass the same size guard as `merge`; `next_id` never reuses an
    id. A second decision on the same id is a warning and ignored.
    """
    by_id = {b.id: Bullet(**asdict(b)) for b in pb.bullets}
    warnings: list[str] = []
    seen: set[str] = set()
    dropped: list[tuple[str, str]] = []
    rewritten: list[str] = []
    for d in decisions:
        if d.id not in by_id:
            warnings.append(
                f"audit decision for unknown bullet id {d.id!r} ignored"
            )
            continue
        if d.id in seen:
            warnings.append(f"duplicate audit decision for {d.id!r} ignored")
            continue
        seen.add(d.id)
        if d.action == "drop":
            del by_id[d.id]
            dropped.append((d.id, d.reason))
        elif d.action == "rewrite":
            content = d.content.strip()
            if not content:
                warnings.append(f"empty rewrite for {d.id!r} ignored; kept")
                continue
            by_id[d.id].content = content
            rewritten.append(d.id)
        elif d.action != "keep":  # pyright: ignore[reportUnnecessaryComparison]
            warnings.append(f"unknown audit action {d.action!r} for {d.id!r}")
    audited = Playbook(
        next_id=pb.next_id,
        bullets=[by_id[b.id] for b in pb.bullets if b.id in by_id],
    )
    kept = [b.id for b in audited.bullets if b.id not in rewritten]
    added: list[str] = []
    refused: list[str] = []
    for op in additions:
        if op.type != "ADD":  # pyright: ignore[reportUnnecessaryComparison]
            warnings.append(f"non-ADD audit addition {op.type!r} ignored")
            continue
        section = _normalize_section(op.section, warnings)
        candidate = Bullet(
            id=f"{BULLET_ID_PREFIX}-{audited.next_id:05d}",
            section=section,
            content=op.content,
        )
        audited.bullets.append(candidate)
        if audited.token_estimate() > max_tokens:
            audited.bullets.pop()
            refused.append(op.content)
            warnings.append(
                f"size guard ({max_tokens} tokens) refused an audit addition"
                f" to section {op.section!r}"
            )
            continue
        audited.next_id += 1
        added.append(candidate.id)
    return AuditOutcome(
        playbook=audited,
        kept=kept,
        dropped=dropped,
        rewritten=rewritten,
        added=added,
        refused=refused,
        warnings=warnings,
    )


def rebuild(
    pb: Playbook,
    bullets: Sequence[RewriteBullet],
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> MergeOutcome:
    """
    Replace the playbook wholesale with an LLM-authored rewrite.

    This is the `curator_mode="monolithic"` ablation — Dynamic
    Cheatsheet's cumulative mode, and the thing ACE's incremental delta
    updates exist to avoid (their Table 18; the context-collapse
    phenomenon of their Fig. 2). Whatever the model omits is *deleted*,
    and helpful/harmful counters are lost by construction, because the
    rewrite carries no ids. That loss is not a defect of this
    implementation: it is precisely the phenomenon the ablation
    measures.

    Ids continue from `pb.next_id` and are never reused, so a bullet
    dropped at step N keeps a distinct identity from any later bullet
    with similar content, and the previous step's file still holds
    everything the rewrite discarded. The same size guard as `merge`
    applies, so the two arms differ only in *who does the merging*.
    """
    rebuilt = Playbook(next_id=pb.next_id, bullets=[])
    added: list[str] = []
    dropped: list[str] = []
    warnings: list[str] = []
    for b in bullets:
        candidate = Bullet(
            id=f"{BULLET_ID_PREFIX}-{rebuilt.next_id:05d}",
            section=b.section,
            content=b.content,
        )
        rebuilt.bullets.append(candidate)
        if rebuilt.token_estimate() > max_tokens:
            rebuilt.bullets.pop()
            dropped.append(b.content)
            warnings.append(
                f"size guard ({max_tokens} tokens) refused a rewrite"
                f" bullet in section {b.section!r}"
            )
            continue
        rebuilt.next_id += 1
        added.append(candidate.id)
    net = len(rebuilt.bullets) - len(pb.bullets)
    counters = sum(1 for b in pb.bullets if b.helpful or b.harmful)
    warnings.append(
        f"monolithic rewrite: {len(pb.bullets)} bullets in,"
        f" {len(rebuilt.bullets)} out (net {net:+d}),"
        f" {counters} counter(s) discarded"
    )
    return MergeOutcome(
        playbook=rebuilt,
        added=added,
        deduped=[],
        dropped=dropped,
        warnings=warnings,
    )
