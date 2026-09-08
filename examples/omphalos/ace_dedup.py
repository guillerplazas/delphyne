"""
Near-duplicate detection for ACE playbook bullets.

The paper's grow-and-refine step de-duplicates bullets by semantic
embedding similarity. The first omphalos implementation used a lexical
`SequenceMatcher` at 0.90, which fired exactly zero times in forty
adaptation steps — the "refine" half of grow-and-refine did not exist
in practice. This module makes the deduper a pluggable, pre-registered
choice:

- `LexicalDeduper` — the legacy rule, kept byte-for-byte so the frozen
  adaptation runs still regenerate their step playbooks identically.
- `JaccardDeduper` — token-set overlap on normalised text; catches
  paraphrases that share the tactic and lemma names, no network.
- `EmbeddingDeduper` — cosine similarity of `text-embedding-3-small`
  vectors through the stdlib `EmbeddingModel` + `EmbeddingsCache`, i.e.
  the paper's mechanism. The cache file lives next to the playbooks
  (not under `experiments/output/`, which `make clean-experiments`
  deletes), and `replay` runs it in `"replay"` cache mode so a
  re-derivation that would need a new embedding fails loudly instead
  of silently changing a playbook.

Every deduper answers the same question — "which existing bullet, if
any, is this text a near-duplicate of, and how close?" — so `merge`
and `refine` in `ace_playbook` are agnostic to the choice.
"""

# pyright: strict

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from delphyne.stdlib.embeddings import EmbeddingsCache
from delphyne.utils.caching import CacheMode

from ace_playbook import Bullet

DEFAULT_LEXICAL_THRESHOLD = 0.90
DEFAULT_JACCARD_THRESHOLD = 0.50
DEFAULT_EMBEDDING_THRESHOLD = 0.88
"""
Pre-registered thresholds. The paper sweeps its embedding knob over
50–90% with mild, non-monotone effect (their Table 20); 0.88 cosine on
`text-embedding-3-small` is the top of that range, chosen so that only
bullets a reader would call "the same advice" fold. Jaccard 0.50 on
normalised tokens is deliberately looser because token overlap
underestimates paraphrase similarity.
"""

EMBEDDING_MODEL = "text-embedding-3-small"


class Deduper(Protocol):
    """Finds the closest existing bullet to a candidate text."""

    name: str
    threshold: float
    same_section_only: bool

    def closest(
        self, candidate: str, existing: Sequence[Bullet]
    ) -> tuple[Bullet, float] | None:
        """
        The existing bullet most similar to `candidate` together with
        the similarity, or `None` if nothing reaches `threshold`.
        `existing` is already filtered by section when
        `same_section_only` holds.
        """
        ...


def _normalize(text: str) -> str:
    """Casefold, collapse whitespace, strip a trailing period."""
    collapsed = re.sub(r"\s+", " ", text).strip().casefold()
    return collapsed.removesuffix(".")


@dataclass
class LexicalDeduper:
    """The legacy rule: `SequenceMatcher.ratio()` on normalised text."""

    threshold: float = DEFAULT_LEXICAL_THRESHOLD
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


_STOPWORDS = frozenset(
    """a an the and or of to in on for with by is are be as at from that
    this it its when then than into over use using used via not no do
    does if so which what where while your you before after first""".split()
)
_CODE_SPAN_RE = re.compile(r"`([^`]+)`")
_TOKEN_RE = re.compile(r"[a-z0-9_.']+")


def jaccard_tokens(text: str) -> frozenset[str]:
    """
    Normalised token set: backticked code spans are kept whole (a
    lemma name is one token, not three), everything else is lowercased
    words minus stopwords.
    """
    spans = {s.strip().casefold() for s in _CODE_SPAN_RE.findall(text)}
    rest = _CODE_SPAN_RE.sub(" ", text).casefold()
    words = {w for w in _TOKEN_RE.findall(rest) if w not in _STOPWORDS}
    return frozenset(spans | words)


@dataclass
class JaccardDeduper:
    threshold: float = DEFAULT_JACCARD_THRESHOLD
    name: str = "jaccard"
    same_section_only: bool = False

    def closest(
        self, candidate: str, existing: Sequence[Bullet]
    ) -> tuple[Bullet, float] | None:
        tc = jaccard_tokens(candidate)
        best: tuple[Bullet, float] | None = None
        for b in existing:
            tb = jaccard_tokens(b.content)
            union = len(tc | tb)
            score = len(tc & tb) / union if union else 0.0
            if score >= self.threshold and (best is None or score > best[1]):
                best = (b, score)
        return best


@dataclass
class EmbeddingDeduper:
    """
    Cosine similarity of embeddings, cached on disk.

    `cache_file` is the playbook-side `embeddings.cache.h5`; the deduper
    holds the cache open for its lifetime and saves it on `close()`
    (use it as a context manager). Vectors are L2-normalised once per
    text and memoised in-process.
    """

    cache_file: Path
    cache_mode: CacheMode = "read_write"
    threshold: float = DEFAULT_EMBEDDING_THRESHOLD
    model_name: str = EMBEDDING_MODEL
    name: str = "embedding"
    same_section_only: bool = False
    _vectors: dict[str, NDArray[np.float32]] = field(
        default_factory=lambda: dict[str, NDArray[np.float32]]()
    )
    _cache: EmbeddingsCache | None = None

    def __enter__(self) -> "EmbeddingDeduper":
        if self.cache_file.exists():
            self._cache = EmbeddingsCache.load(
                self.cache_file, self.cache_mode
            )
        else:
            self._cache = EmbeddingsCache({}, self.cache_mode)
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        cache = self._cache
        if cache is None:
            return
        if self.cache_mode not in ("read_only", "replay") and (
            cache.dict or self.cache_file.exists()
        ):
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache.save(self.cache_file)
        self._cache = None

    def _embed(self, texts: Sequence[str]) -> None:
        missing = [t for t in dict.fromkeys(texts) if t not in self._vectors]
        if not missing:
            return
        assert self._cache is not None, (
            "use EmbeddingDeduper as a context manager"
        )
        from campaign_embeddings import embedding_model

        model = embedding_model(self.model_name)
        for text, resp in zip(missing, model.embed(missing, self._cache)):
            v = resp.embedding.astype(np.float32)
            norm = float(np.linalg.norm(v))
            self._vectors[text] = v / norm if norm else v

    def closest(
        self, candidate: str, existing: Sequence[Bullet]
    ) -> tuple[Bullet, float] | None:
        if not existing:
            return None
        self._embed([candidate, *(b.content for b in existing)])
        vc = self._vectors[candidate]
        best: tuple[Bullet, float] | None = None
        for b in existing:
            score = float(np.dot(vc, self._vectors[b.content]))
            if score >= self.threshold and (best is None or score > best[1]):
                best = (b, score)
        return best
