"""
ACE context adaptation — offline and online — for the agentic prover.

Replicates, adapted to miniF2F-Rocq, the adaptation arms of ACE
(arXiv:2510.04618): iterate over a problem pool; for each problem run
Generator → Reflector → Curator and fold the Curator's ADD-only delta
into the playbook with the deterministic merge in `ace_playbook`,
refining (dedup + prune) at a fixed cadence. Every LLM call is one
config of a `dp.Experiment`, so every exchange is cached, resumable
and replayable.

Two modes, selected per variant:

- **offline** (paper Table 1 "offline"): adapt on a training pool for
  `epochs` passes (a seeded shuffle per epoch, as the paper does),
  then freeze the final playbook under `experiments/playbooks/` for a
  separate evaluation run (`ace_x_validation_experiment.py`, ...).
- **online** (paper Table 1 "online", Table 3 "offline warmup"): walk
  an *evaluation* partition once, in file order. The Generator run on
  each problem is the evaluation cell — it is stored under
  `experiments/output/ace_online_<variant>_agentic/` with the same
  naming as any frozen-playbook evaluation, so the paired report
  tooling reads it unchanged — and the playbook is updated from that
  attempt before the next problem. `warmup_playbook` starts the chain
  from a frozen offline playbook instead of the empty one.

Ground truth: none exists in this domain and none is needed — the Rocq
verifier's verdict inside the trajectory is the supervision, which is
the paper's "execution feedback, no GT labels" setting for every arm.

**Pre-registration.** Adaptation reads no metric beyond spend. The
evaluation metrics (paired solves per problem-seed cell, exact sign
test; paired spend among jointly-solved cells; error taxonomy; the
offline cap curve) are pre-registered in the evaluation scripts and
computed by `tools/reports/ace_report.py` and companions.

**Replicability.** Config identity includes the sha256 of the exact
playbook a step consumed (and, for the Reflector/Curator, of their
rendered upstream input); playbooks are stored by that hash
(`ace_store.PlaybookStore`), so a config can never silently run against
drifted inputs and a batch of size > 1 sees the batch-start playbook
by construction. `run` resumes at zero spend from cache; `replay`
re-executes every recorded config with `cache_mode="replay"`, which
raises on any cache miss — the determinism proof. The five 2026-08-24
variants (`train`, `train-e3`, `pool`, `noreflect`, `mono`) keep
their identities and renderings byte-for-byte.

Usage:
    python -m experiments.ace.ace_adaptation plan --variant=x-offline
    python -m experiments.ace.ace_adaptation run --variant=x-offline
    python -m experiments.ace.ace_adaptation run --variant=x-offline --limit=2
    python -m experiments.ace.ace_adaptation replay --variant=train
    python -m experiments.ace.ace_adaptation status --variant=train
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import hashlib
import os
import random
import re
import shutil
import uuid
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Literal, cast

import fire  # type: ignore
import yaml

import delphyne as dp
import delphyne.stdlib.answer_loaders as al


import experiments.common.ace_pool as ace_pool  # noqa: E402
import experiments.common.miniF2F_bench as mf  # noqa: E402
import experiments.common.minif2f_x as x  # noqa: E402
from experiments.common.ace_bench import (  # noqa: E402
    ACEAgenticConfig,
    ace_config_name,
    render_cited,
    render_injection,
)
from ace.ace_dedup import (  # noqa: E402
    EmbeddingDeduper,
    JaccardDeduper,
    LexicalDeduper,
)
import experiments.common.omphalos_launch as ol  # noqa: E402
from ace.ace_evidence import (  # noqa: E402
    FailedVerdict,
    checkable_references,
    collect_failures,
    known_guidance,
    render_digest,
    representative_files,
)
from ace.ace_playbook import (  # noqa: E402
    AddOp,
    BulletTag,
    Deduper,
    Playbook,
    apply_audit,
    merge,
    rebuild,
    refine,
)
from ace.ace_store import (  # noqa: E402
    LEGACY_VARIANT,
    PLAYBOOKS_DIR,
    STEPS_SCHEMA_VERSION,
    PlaybookStore,
)
from prove_ace import (  # noqa: E402
    CurationDelta,
    GroundingResult,
    PlaybookAudit,
    PlaybookRewrite,
    Reflection,
)

_OMPHALOS_DIR = OMPHALOS_ROOT

POOLS: Mapping[str, Mapping[str, tuple[str, str]]] = {
    **ace_pool.POOLS,
    **x.PARTITIONS_X,
}
"""Every pool a variant may name: the original partitions, the
adaptation pool, and the X partitions."""

ALL_PROBLEMS: Mapping[str, tuple[str, str]] = {
    **ace_pool.ALL_ADAPT_PROBLEMS,
    **x.ALL_X_PROBLEMS,
}


#####
##### Variants
#####


Mode = Literal["offline", "online"]
DedupKind = Literal["lexical", "jaccard", "embedding"]


ADAPT_MODEL = "gpt-5.6-luna"
ADAPT_TOOLSET = "core"
ADAPT_EFFORT = "medium"
CURATION_ROLES: frozenset[str] = frozenset(
    {"curator", "reducer", "grounder", "auditor"}
)
"""The roles a variant's `curator_model` / `curator_effort` govern."""
GENERATOR_NUM_REQUESTS = 32
ROLE_NUM_REQUESTS = 3
"""Reflector/Curator: 1 shot + up to 2 parse-retries."""
REWRITE_DOLLAR_CAP = 0.04
"""
Cap for the monolithic curator, which emits the WHOLE playbook rather
than a delta: ~12k input + ~3k output is ~$0.006 at luna rates, so
three parse-retries worst-case is ~$0.018. `ROLE_DOLLAR_CAP` would
therefore *bind* on this arm rather than act as a safety net, which
would silently truncate the ablation it exists to measure.
"""
ROLE_DOLLAR_CAP = 0.02
"""
Safety net for one-shot roles. A reflector call is ~10-25k input +
~2k output tokens ≈ $0.005-0.008 at luna rates, so $0.02 is ~3x the
worst expected call, per the sizing convention of the other caps.
"""
TRAJECTORY_MAX_CHARS = 80_000
"""~20k tokens; longer trajectories are cut head+tail with a marker."""
MAX_RETRIES = 2
"""Transient failures (a dropped connection, a Rocq timeout) are
retried this many times before a role is declared failed."""


@dataclass(frozen=True)
class AdaptVariant:
    """
    One adaptation configuration.

    `name` fixes the output directory and the playbook store, so two
    variants can never share a cache. `final_playbook` is named
    explicitly rather than derived, so a rename cannot silently point
    a new run at a frozen file (`_freeze` would refuse, but the intent
    should be visible here); online variants have none — their
    generator cells *are* the result.

    The v1 defaults reproduce the 2026-08-24 runs. The X-partition
    variants set `render_version=2` (ids only in the Generator's
    prompt, empty rendering at the start), `curator_contract=2`
    (block scalars), a deduper that can fire, a refine cadence, and
    `count_dedup_as_helpful=False`.
    """

    name: str
    pool: str
    final_playbook: str | None
    mode: Mode = "offline"
    epochs: int = 1
    shuffle_seed: int | None = None
    reflector: Literal["on", "off"] = "on"
    curator_mode: Literal["incremental", "monolithic"] = "incremental"
    batch_size: int = 1
    warmup_playbook: str | None = None
    injection: str = "full"
    render_version: int = 1
    curator_contract: int = 1
    show_definitions: bool = False
    dedup: DedupKind = "lexical"
    dedup_threshold: float | None = None
    count_dedup_as_helpful: bool = True
    refine_every: int = 0
    prune_harmful: bool = False
    seed: int = 0
    generator_cap: float = mf.LUNA_DOLLAR_CAP
    playbook_max_tokens: int = 4000
    reduce_batch: bool = False
    """With `batch_size > 1`, aggregate the batch's proposed deltas
    through `AggregateCurationDeltas` (the reference's map-reduce)
    instead of merging each delta sequentially."""
    reflector_model: str | None = None
    curator_model: str | None = None
    reflector_scope: Literal["all", "cited"] = "all"
    """
    What the Reflector is shown of the playbook. `"all"`: the whole
    rendering the Generator saw (v1-v3). `"cited"` (v4, the reference's
    attribution channel): only the bullets whose ids the Generator
    named in its own messages — the `render_version >= 3` prompt asks
    for them before the first tool call — and counters move only for
    those bullets (other tags are dropped and counted in
    `tags_dropped`). A Generator that cites nothing moves no counter.
    """
    reflector_effort: str | None = None
    curator_effort: str | None = None
    """
    Per-role overrides of `ADAPT_EFFORT`. Like `reflector_model` /
    `curator_model`, the curator setting covers the whole curation side
    (curator, reducer, grounder, auditor): the reducer *is* a curator
    and the 2026-08 hook silently left it on the default model.
    """
    role_cap: float = ROLE_DOLLAR_CAP
    """
    Per-call dollar cap for the one-shot roles. `ROLE_DOLLAR_CAP` is
    sized for luna; a variant that puts a dearer model on a role must
    scale it, or the safety net binds and truncates the very thing the
    arm measures (the lesson of `REWRITE_DOLLAR_CAP`).
    """
    reducer_contract: int = 1
    grounding: bool = False
    skip_trivial: bool = False
    audit: bool = False
    audit_max_additions: int = 6
    preaudit_playbook: str | None = None
    repair_rounds: int = 0
    repair_requests: int = 16
    repair_cap: float = 0.05
    campaign_runtime: str = ""
    """
    v5 (2026-09-02). `reducer_contract=2` shows the reducer the pool's
    failure digest (needs `curator_contract >= 4`, which computes it).
    `grounding` runs the Rocq gate on every ADD's `references` and
    refuses bullets naming objects Rocq does not know. `skip_trivial`
    spends no Reflector/Curator call on a first-proposal solve.
    `audit` runs `AuditPlaybook` once after the last step, freezing the
    pre-audit playbook under `preaudit_playbook` first so the audit's
    own effect stays measurable. All default off: every recorded
    variant is unchanged.
    """

    def __post_init__(self) -> None:
        if self.repair_rounds < 0 or (
            self.repair_rounds
            and (self.reflector != "on" or self.mode != "offline")
        ):
            raise ValueError(
                "repair requires offline adaptation with reflection"
            )
        assert self.pool in POOLS, (
            f"unknown pool {self.pool!r}; known: {', '.join(POOLS)}"
        )
        if self.reflector_scope == "cited":
            assert self.render_version >= 3 and self.reflector == "on", (
                "reflector_scope='cited' needs the citation ask "
                "(render_version >= 3) and a Reflector"
            )
        if self.mode == "online":
            assert self.epochs == 1 and self.batch_size == 1, (
                "online adaptation is one sequential pass"
            )
            assert self.final_playbook is None, (
                "online variants freeze nothing: the cells are the result"
            )
        else:
            assert self.final_playbook is not None
        if self.grounding or self.audit or self.reducer_contract >= 2:
            assert self.mode == "offline" and self.curator_contract >= 4, (
                "the v5 mechanisms (grounding, audit, reducer contract 2)"
                " need the contract-4 curator and offline mode"
            )
        assert (self.preaudit_playbook is not None) == self.audit, (
            "`preaudit_playbook` is named exactly when `audit` is on"
        )

    def warmup(self) -> Playbook:
        """The frozen playbook an online chain starts from, or empty."""
        if self.warmup_playbook is None:
            return Playbook()
        path = PLAYBOOKS_DIR / self.warmup_playbook
        assert path.exists(), (
            f"warm-up playbook {self.warmup_playbook} is not frozen yet:"
            " run the offline variant that produces it first"
        )
        return Playbook.load(path)

    def role_model(self, role: str) -> str:
        if role == "reflector" and self.reflector_model is not None:
            return self.reflector_model
        if role in CURATION_ROLES and self.curator_model is not None:
            return self.curator_model
        return ADAPT_MODEL

    def role_effort(self, role: str) -> str:
        if role == "reflector" and self.reflector_effort is not None:
            return self.reflector_effort
        if role in CURATION_ROLES and self.curator_effort is not None:
            return self.curator_effort
        return ADAPT_EFFORT


_X_COMMON: dict[str, Any] = dict(
    render_version=2,
    curator_contract=2,
    show_definitions=True,
    dedup="embedding",
    count_dedup_as_helpful=False,
    refine_every=10,
    prune_harmful=True,
    generator_cap=x.X_DOLLAR_CAP,
)
"""
The v2 machinery every X-partition variant shares, so that the
variants below differ from each other in exactly the one thing each
ablates.
"""


_X3_COMMON: dict[str, Any] = dict(
    render_version=3,
    curator_contract=3,
    show_definitions=True,
    dedup="embedding",
    count_dedup_as_helpful=False,
    refine_every=10,
    prune_harmful=True,
    generator_cap=x.X_DOLLAR_CAP,
)
"""v3 = v2 machinery + the 2026-08-25 reference-audit polish."""


_X5_COMMON: dict[str, Any] = dict(
    _X3_COMMON,
    curator_contract=4,
    reducer_contract=2,
    grounding=True,
    skip_trivial=True,
    audit=True,
)
"""
v5 (2026-09-02) = v3 machinery + evidence-first curation: the pool's
verifier-failure digest and the prover's own pitfalls in the Curator
and Reducer prompts (contracts 4 / 2), the Rocq grounding gate on every
ADD, no role calls on trivial solves, and one terminal audit pass.
Built from the diagnosis in PROGRESS 2026-09-02 (causes C1-C4); the
Generator prompt is untouched (render_version 3), so an evaluation cell
differs from an x3 cell in playbook content only.
"""


def _online3(
    name: str,
    pool: str,
    seed: int,
    warmup: str | None,
    scope: Literal["all", "cited"] = "all",
) -> AdaptVariant:
    return AdaptVariant(
        name,
        pool,
        None,
        mode="online",
        warmup_playbook=warmup,
        seed=seed,
        reflector_scope=scope,
        **_X3_COMMON,
    )


def _online(
    name: str, pool: str, seed: int, warmup: str | None
) -> AdaptVariant:
    return AdaptVariant(
        name,
        pool,
        None,
        mode="online",
        warmup_playbook=warmup,
        seed=seed,
        **_X_COMMON,
    )


VARIANTS: Mapping[str, AdaptVariant] = {
    # ---- FROZEN 2026-08-24 generation. Never edit these entries. ----
    "train": AdaptVariant("train", "train", "ace_v1.yaml"),
    "train-e3": AdaptVariant(
        "train-e3", "train", "ace_train_e3.yaml", epochs=3
    ),
    "pool": AdaptVariant(
        "pool", "adapt_pool", "ace_pool_v1.yaml", batch_size=4
    ),
    "noreflect": AdaptVariant(
        "noreflect", "train", "ace_noreflect.yaml", reflector="off"
    ),
    "mono": AdaptVariant(
        "mono", "train", "ace_mono.yaml", curator_mode="monolithic"
    ),
    # ---- X partitions: the paper's experiment matrix. ----
    # E1  offline, one epoch (Table 1 "offline").
    "x-offline": AdaptVariant(
        "x-offline",
        "trainX",
        "ace_x_offline.yaml",
        shuffle_seed=0,
        **_X_COMMON,
    ),
    # E2  offline, three shuffled epochs (Table 3 "multi-epoch").
    "x-offline-e3": AdaptVariant(
        "x-offline-e3",
        "trainX",
        "ace_x_offline_e3.yaml",
        epochs=3,
        shuffle_seed=0,
        **_X_COMMON,
    ),
    # E3  no Reflector (Table 3).
    "x-noreflect": AdaptVariant(
        "x-noreflect",
        "trainX",
        "ace_x_noreflect.yaml",
        reflector="off",
        shuffle_seed=0,
        **_X_COMMON,
    ),
    # E4  monolithic rewrite (Table 18 / Fig. 2, context collapse).
    "x-mono": AdaptVariant(
        "x-mono",
        "trainX",
        "ace_x_mono.yaml",
        curator_mode="monolithic",
        shuffle_seed=0,
        **_X_COMMON,
    ),
    # ---- v3 (2026-08-25 reference-audit polish; versioned prompts). ----
    "x3-offline": AdaptVariant(
        "x3-offline",
        "trainX",
        "ace_x3_offline.yaml",
        shuffle_seed=0,
        batch_size=4,
        reduce_batch=True,
        **_X3_COMMON,
    ),
    "x3-offline-e3": AdaptVariant(
        "x3-offline-e3",
        "trainX",
        "ace_x3_offline_e3.yaml",
        epochs=3,
        shuffle_seed=0,
        playbook_max_tokens=8000,
        batch_size=4,
        reduce_batch=True,
        **_X3_COMMON,
    ),
    "x3-noreflect": AdaptVariant(
        "x3-noreflect",
        "trainX",
        "ace_x3_noreflect.yaml",
        reflector="off",
        shuffle_seed=0,
        batch_size=4,
        reduce_batch=True,
        **_X3_COMMON,
    ),
    "x3-mono": AdaptVariant(
        "x3-mono",
        "trainX",
        "ace_x3_mono.yaml",
        curator_mode="monolithic",
        shuffle_seed=0,
        **_X3_COMMON,
    ),
    # A2 drift gate: batch-1 twin of x3-offline (same seed/order), run
    # with --limit=12 against x3-offline --limit=12 and compared on
    # playbook shape before batching is trusted for the matrix.
    "x3-gate-b1": AdaptVariant(
        "x3-gate-b1",
        "trainX",
        "ace_x3_gate_b1.yaml",
        shuffle_seed=0,
        **_X3_COMMON,
    ),
    # ---- v4 (2026-08-26): the reference's attribution channel. ----
    # x4-offline = x3-offline with reflector_scope="cited": the Reflector
    # sees only the bullets the Generator cited and counters move only
    # for them. Everything else (pool, seed-0 order, batch 4 + reducer,
    # 4k guard, dedup, refine cadence, prompts) is byte-identical to
    # x3-offline, which is the pre-registered pair. Primary: paired
    # solves of the frozen playbook on validationX (seeds 0, 1) against
    # x3-offline's rv3 evaluation and against the baseline, exact sign
    # test, 6-discordant power floor; secondary: paired spend on jointly
    # solved cells, and the counter statistics from steps.csv (tags
    # applied, tags dropped, cited_count). "Attribution helps" only at
    # p < 0.05 one-sided; UNDERPOWERED otherwise. Disclosed a priori:
    # 38 of 143 v3 generator cells cited nothing, so those steps move no
    # counter (as in the reference). Stop above $4 for adaptation + eval.
    "x4-offline": AdaptVariant(
        "x4-offline",
        "trainX",
        "ace_x4_offline.yaml",
        shuffle_seed=0,
        batch_size=4,
        reduce_batch=True,
        reflector_scope="cited",
        **_X3_COMMON,
    ),
    "x4-online-s0": _online3(
        "x4-online-s0", "validationX", 0, None, scope="cited"
    ),
    # ---- 2026-09-02: role strength as its own arm (HINTS #49). ----
    # x3-strong = x3-offline with gpt-5.6-terra as Reflector and as
    # every curation role (curator, reducer), at the same medium effort;
    # the Generator stays luna, so evaluation cells are byte-identical
    # in everything but playbook content. `role_cap` scales the one-shot
    # safety net for terra's ~10x rates (a reflector call is ~$0.05-0.08
    # there; 0.25 ≈ 3x the worst expected call, the standing sizing
    # rule). Pre-registered before the run: primary = paired solves of
    # the frozen playbook on validationX (seeds 0, 1) against the
    # baseline and against `ace_x3_offline`'s rv3 evaluation, exact
    # sign test, six-cell power floor; secondary = spend on jointly
    # solved cells, the error taxonomy (unknown-reference, syntax-error,
    # prover-crash) and the playbook statistics (bullets, tokens, share
    # never tagged); testX only by the standing selection rule. Expected
    # adaptation spend ≈ $3; the 2026-09-02 study stops above $15 total.
    "x3-strong": AdaptVariant(
        "x3-strong",
        "trainX",
        "ace_x3_strong.yaml",
        shuffle_seed=0,
        batch_size=4,
        reduce_batch=True,
        reflector_model="gpt-5.6-terra",
        curator_model="gpt-5.6-terra",
        role_cap=0.25,
        **_X3_COMMON,
    ),
    # ---- 2026-09-02: v5, evidence-first curation (the method arm). ----
    # x5-offline = x3-offline's pool, order, batching, guard, dedup and
    # refine cadence, plus the v5 mechanisms (`_X5_COMMON`). Not a
    # minimal pair — disclosed: it bundles the digest, the grounding
    # gate, trivial-solve skipping and the terminal audit, because the
    # study buys one method arm; the pre-audit playbook is frozen so
    # the audit can be ablated later for one evaluation. Pre-registered
    # before the run, same rules as x3-strong: primary = paired solves
    # of `ace_x5_offline.yaml` on validationX (seeds 0, 1) against the
    # baseline and against `ace_x3_offline`'s rv3 evaluation, exact
    # sign test, six-cell floor; secondary = spend on jointly solved
    # cells, the taxonomy (unknown-reference, syntax-error,
    # prover-crash), the playbook statistics (bullets, tokens, share
    # never tagged, `ungrounded` refusals, audit drops); testX only by
    # the standing selection rule. Expected adaptation spend ≈ $1.5.
    "x5-offline": AdaptVariant(
        "x5-offline",
        "trainX",
        "ace_x5_offline.yaml",
        shuffle_seed=0,
        batch_size=4,
        reduce_batch=True,
        preaudit_playbook="ace_x5_offline_preaudit.yaml",
        **_X5_COMMON,
    ),
    # testX look of the online arm, one chain, cold start — launched
    # only because x3-online-s0 met the pre-registered selection rule
    # on validationX (28 vs 27 paired solves, 2026-08-27). Never re-run.
    "x3-online-testX": _online3("x3-online-testX", "testX", 0, None),
    "x3-online-s0": _online3("x3-online-s0", "validationX", 0, None),
    "x3-online-s1": _online3("x3-online-s1", "validationX", 1, None),
    "x3-online-warm-s0": _online3(
        "x3-online-warm-s0", "validationX", 0, "ace_x3_offline.yaml"
    ),
    "x3-online-warm-s1": _online3(
        "x3-online-warm-s1", "validationX", 1, "ace_x3_offline.yaml"
    ),
    # E5  online, cold start, on validationX — one chain per seed.
    "x-online-s0": _online("x-online-s0", "validationX", 0, None),
    "x-online-s1": _online("x-online-s1", "validationX", 1, None),
    # E6  online with offline warm-up (Table 3) — needs E1 frozen.
    "x-online-warm-s0": _online(
        "x-online-warm-s0", "validationX", 0, "ace_x_offline.yaml"
    ),
    "x-online-warm-s1": _online(
        "x-online-warm-s1", "validationX", 1, "ace_x_offline.yaml"
    ),
}


def _variant(name: str) -> AdaptVariant:
    if name in {"review-repair-s0", "review-repair-s1"}:
        from experiments.ace.ace_review_experiment import campaign_profile

        seed = int(name[-1])
        return replace(
            VARIANTS["x3-offline"],
            name=name,
            seed=seed,
            final_playbook=f"ace_review_repair_s{seed}.yaml",
            repair_rounds=2,
            campaign_runtime=campaign_profile().digest(),
        )
    assert name in VARIANTS, (
        f"unknown variant {name!r}; known: {', '.join(VARIANTS)}"
    )
    return VARIANTS[name]


def _output_dir(variant: str) -> str:
    return f"experiments/output/ace_adaptation_{variant}"


def _online_output_dir(variant: str) -> str:
    return f"experiments/output/ace_online_{variant}_agentic"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


#####
##### Trajectory extraction
#####


def _render_message(m: Mapping[str, Any]) -> str:
    role = m.get("role")
    if role == "user":
        tag = "[VERIFIER FEEDBACK]" if m.get("is_feedback") else "[PROBLEM]"
        return f"{tag}\n{m.get('content', '')}"
    if role == "assistant":
        answer = cast(Mapping[str, Any], m.get("answer") or {})
        return f"[ASSISTANT]\n{answer.get('content') or '(no content)'}"
    if role == "tool":
        call = cast(Mapping[str, Any], m.get("call") or {})
        args = ", ".join(
            f"{k}={v!r}"
            for k, v in cast(Mapping[str, Any], call.get("args") or {}).items()
        )
        return (
            f"[TOOL CALL] {call.get('name')}({args})\n"
            f"[TOOL RESULT]\n{m.get('result', '')}"
        )
    # A role this renderer does not know (a future stdlib message
    # kind): shown rather than dropped, so the Reflector sees the gap.
    return f"[{str(role).upper()}]\n{m.get('content', '')}"


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return (
        text[:half]
        + "\n\n[... TRAJECTORY TRUNCATED (middle elided) ...]\n\n"
        + text[-half:]
    )


def _yaml_load(path: Path) -> Any:
    """
    `yaml.safe_load` with the C loader when available: the driver
    parses multi-MB `cache.yaml` / `result.yaml` files several times
    per step, and the pure-Python loader is ~7x slower on them.
    """
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    with path.open() as f:
        return yaml.load(f, Loader=loader)  # type: ignore[reportUnknownMemberType]


CITED_ID_RE = re.compile(r"rocq-\d{5}")


def _final_chat(
    config_dir: Path, theorem_name: str
) -> tuple[list[dict[str, Any]], str | None]:
    """
    The last cached LLM exchange of a generator cell, sliced from the
    last non-feedback user message that names the theorem, plus the
    final assistant output (`None` when the last turn was a tool call
    with no content). Shared by `extract_trajectory` and
    `cited_bullet_ids`; the rendering is byte-identical to before.
    """
    raw: Any = _yaml_load(config_dir / "cache.yaml")
    entries = cast(list[dict[str, Any]], raw)
    llm = [
        e
        for e in entries
        if cast(list[dict[str, Any]], e["input"]["request"]["chat"])[0]["role"]
        == "system"
    ]
    assert llm, f"no LLM exchanges cached under {config_dir}"
    final = llm[-1]
    chat = cast(list[dict[str, Any]], final["input"]["request"]["chat"])
    marker = f"Theorem {theorem_name}"
    starts = [
        i
        for i, m in enumerate(chat)
        if m["role"] == "user"
        and not m.get("is_feedback")
        and marker in m["content"]
    ]
    assert starts, f"no instance message mentions {marker!r}"
    outputs = cast(list[dict[str, Any]], final["output"]["outputs"])
    last: str | None = None
    if outputs:
        last = cast(str | None, outputs[0].get("content"))
    return chat[starts[-1] :], last if outputs else None


def cited_bullet_ids(
    config_dir: Path, theorem_name: str, known: Collection[str]
) -> list[str]:
    """
    Bullet ids the Generator named in its OWN messages, in first-mention
    order, restricted to `known` (the playbook it saw). Only assistant
    text counts: the playbook itself sits in the system message and
    ids echo in verifier feedback and tool results, none of which is a
    citation. The `render_version >= 3` prompt asks the model to name
    the ids it relies on before its first tool call (or "none apply").
    """
    from tools.data.ace_review_benchmark import assert_training_allowed

    assert_training_allowed([theorem_name])
    chat, last = _final_chat(config_dir, theorem_name)
    texts: list[str] = []
    for m in chat:
        if m.get("role") == "assistant":
            answer = cast(Mapping[str, Any], m.get("answer") or {})
            texts.append(str(answer.get("content") or ""))
    if last:
        texts.append(last)
    seen: list[str] = []
    for text in texts:
        found: list[str] = CITED_ID_RE.findall(text)
        for i in found:
            if i in known and i not in seen:
                seen.append(i)
    return seen


def extract_trajectory(config_dir: Path, theorem_name: str) -> str:
    """
    Render the generator run's trajectory from its `cache.yaml`.

    The cache stores every LLM request with its fully rendered chat.
    Entries are appended in issue order, so the *last* LLM exchange is
    the final state of the conversation and its `output` is the
    model's last message (under `dfs` with `max_depth=None` the loop
    never backtracks, so "last" and "longest" coincide; "last" is the
    one that stays right if that ever changes). The trajectory starts
    at the LAST non-feedback user message mentioning the target
    theorem: that skips the system prompt and few-shot examples, and
    "last" (rather than "unique") also copes with the smoke setup
    where the target coincides with a few-shot problem.

    Responses reasoning items are not stored in the cached chats, so
    the Reflector sees visible content only (documented deviation).
    """
    chat, last = _final_chat(config_dir, theorem_name)
    rendered = [_render_message(m) for m in chat]
    raw: Any = _yaml_load(config_dir / "cache.yaml")
    has_output = bool(
        cast(list[dict[str, Any]], raw)
        and _has_final_output(cast(list[dict[str, Any]], raw))
    )
    if has_output:
        rendered.append(f"[ASSISTANT]\n{last or '(tool call)'}")
    return _truncate("\n\n".join(rendered), TRAJECTORY_MAX_CHARS)


def _has_final_output(entries: list[dict[str, Any]]) -> bool:
    llm = [
        e
        for e in entries
        if cast(list[dict[str, Any]], e["input"]["request"]["chat"])[0]["role"]
        == "system"
    ]
    return (
        bool(cast(list[Any], llm[-1]["output"]["outputs"])) if llm else False
    )


def read_result(config_dir: Path) -> tuple[bool, str]:
    """`(solved, verdict line for the Reflector)` from `result.yaml`."""
    raw: Any = _yaml_load(config_dir / "result.yaml")
    result = cast(dict[str, Any], raw["outcome"]["result"])
    spent = cast(dict[str, Any], result["spent_budget"])
    used = (
        f"(spent {spent.get('num_requests', '?')} requests,"
        f" ${spent.get('price', 0):.4f})"
    )
    if result["success"]:
        values = cast(list[str], result["values"])
        return True, f"SOLVED {used}. The verified proof:\n{values[0]}"
    return False, (
        f"NOT SOLVED {used}: the budget was exhausted without a"
        " verified proof."
    )


def read_outcome(config_dir: Path) -> str:
    return read_result(config_dir)[1]


def read_requests(config_dir: Path) -> int:
    """Requests the generator spent, from `result.yaml`."""
    raw: Any = _yaml_load(config_dir / "result.yaml")
    result = cast(dict[str, Any], raw["outcome"]["result"])
    spent = cast(dict[str, Any], result["spent_budget"])
    return int(spent.get("num_requests", 0))


AUDIT_BENCH = "final"
"""`bench_name` of the terminal auditor and its grounder: they belong
to no problem (`_problem()` is never called on them)."""


#####
##### Configurations
#####


_NO_UID = uuid.UUID(int=0)
"""Naming here is a pure function of the config; the uid is unused."""


def _config_name(cfg: "ACEAdaptStepConfig", _uid: uuid.UUID) -> str:
    suffix = f"_round{cfg.repair_round}" if cfg.repair_round else ""
    return f"step{cfg.step:02d}_{cfg.role}_{cfg.bench_name}{suffix}"


def _config_dir(variant: str, name: str) -> Path:
    return _OMPHALOS_DIR / _output_dir(variant) / "configs" / name


@dataclass
class ACEAdaptStepConfig:
    """
    One adaptation sub-step: a generator, reflector or curator run.

    `playbook_sha256` pins the playbook version the step consumes;
    `upstream_sha256` pins the role-specific rendered input (the
    trajectory for the reflector, the reflection YAML for the
    curator). `instantiate` re-derives those inputs from disk and
    asserts the hashes, so a config can never silently run against
    inputs that drifted from the ones it was created for.

    Every defaulted field reproduces the frozen 2026-08-24 runs, and
    `Experiment` excludes default-valued fields from a config's
    identity, so adding them leaves those configs matched. (Changing
    an existing default is what orphans a run.) The fields after
    `curator_mode` used to be hard-coded in the argument builders —
    they are part of the identity now, so flipping one can never reuse
    a frozen cell.
    """

    role: str  # "generator" | "reflector" | "curator"
    step: int
    bench_name: str
    seed: int
    model_name: str
    toolset: str
    reasoning_effort: str
    num_requests: int
    max_dollar_budget: float
    playbook_sha256: str
    upstream_sha256: str = ""
    variant: str = LEGACY_VARIANT
    reflector: str = "on"
    curator_mode: str = "incremental"
    api: str = "responses"
    convert_user_feedback_to_tool: bool = True
    temperature: float | None = None
    injection: str = "full"
    render_version: int = 1
    curator_contract: int = 1
    show_definitions: bool = False
    max_new_bullets: int = 3
    max_bullets: int = 40
    progress: str = ""
    """
    Pre-rendered budget/progress block for the v3 curator (see
    `_progress_block`); part of identity so a config can never run
    against a different progress context than it was created for.
    """
    generator_dir: str = ""
    """
    Omphalos-relative directory of the generator run this reflector /
    curator reads. Empty = the legacy formula (same experiment, name
    `step{NN}_generator_{bench}`); online variants point it at their
    evaluation cell in another experiment.
    """
    reflector_scope: str = "all"
    """`AdaptVariant.reflector_scope`; part of the reflector's identity."""
    reducer_contract: int = 1
    evidence: str = ""
    known_guidance: str = ""
    """
    v5 curation evidence (pinned like `progress`, so a config can never
    run against a different digest than it was created for): the
    rendered pool-level failure digest and the prover's own pitfalls.
    """
    references: str = ""
    environments: str = ""
    """
    Grounder input: the names to `Locate`, newline-joined, and the
    `problem_file@theorem_name` environments to try, `|`-joined. Both
    are the whole input — nothing is re-derived from another config —
    so identity pins exactly what was checked.
    """
    provenance: str = ""
    audit_max_additions: int = 0
    """Auditor input: the rendered per-bullet provenance block and the
    additions cap."""
    repair_round: int = 0
    episode_guidance: str = ""
    trajectory_override: str = ""
    reflector_dir: str = ""
    repair_evidence: str = ""
    campaign_runtime: str = ""

    # --- inputs ---------------------------------------------------

    def _load_playbook(self) -> Playbook:
        store = PlaybookStore(self.variant)
        if store.has(self.playbook_sha256):
            return store.get(self.playbook_sha256)
        # Legacy addressing: a step file not yet materialized by hash.
        pb = Playbook.load(store.step_path(self.step))
        assert pb.sha256() == self.playbook_sha256, (
            f"playbook file for step {self.step} does not match the"
            f" hash recorded in config {_config_name(self, _NO_UID)!r}"
        )
        return pb

    def _gen_dir(self) -> Path:
        if self.generator_dir:
            return _OMPHALOS_DIR / self.generator_dir
        return _config_dir(
            self.variant, f"step{self.step:02d}_generator_{self.bench_name}"
        )

    def _problem(self) -> tuple[str, str]:
        return ALL_PROBLEMS[self.bench_name]

    def _policy_args(self, max_requests: int | None = None) -> dict[str, Any]:
        args: dict[str, Any] = {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "api": self.api,
            "reasoning_effort": self.reasoning_effort,
        }
        if max_requests is not None:
            args["max_requests"] = max_requests
        return args

    def _budget(self) -> dict[str, float]:
        return {
            dp.NUM_REQUESTS: float(self.num_requests),
            dp.DOLLAR_PRICE: self.max_dollar_budget,
        }

    # --- roles ----------------------------------------------------

    def _generator_args(self) -> dp.RunStrategyArgs:
        problem_file, theorem_name = self._problem()
        pb = self._load_playbook()
        args: dict[str, Any] = {
            "problem_file": problem_file,
            "theorem_name": theorem_name,
            "toolset": self.toolset,
            "turn_budget": self.num_requests,
            "playbook": render_injection(
                pb, self.injection, self.render_version
            ),
        }
        # Only non-default strategy args are passed, so that the frozen
        # generator configs keep their recorded `args` mapping.
        if self.show_definitions:
            args["show_definitions"] = True
        if self.render_version != 1:
            args["render_version"] = self.render_version
        if self.episode_guidance:
            args["episode_guidance"] = self.episode_guidance
        return dp.RunStrategyArgs(
            strategy="prove_theorem_ace",
            args=args,
            policy="prove_theorem_ace_policy",
            policy_args={
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_turns": None,
                "loop": False,
                "api": self.api,
                "reasoning_effort": self.reasoning_effort,
                "convert_user_feedback_to_tool": (
                    self.convert_user_feedback_to_tool
                ),
            },
            budget=self._budget(),
        )

    def _reflector_args(self) -> dp.RunStrategyArgs:
        problem_file, theorem_name = self._problem()
        gen_dir = self._gen_dir()
        trajectory = self.trajectory_override or extract_trajectory(
            gen_dir, theorem_name
        )
        assert _sha256(trajectory) == self.upstream_sha256, (
            f"trajectory for step {self.step} drifted from the hash"
            " recorded at config-creation time"
        )
        return dp.RunStrategyArgs(
            strategy="reflect_on_trajectory",
            args={
                "problem_file": problem_file,
                "outcome": read_outcome(gen_dir),
                "playbook": self._reflector_playbook(),
                "trajectory": trajectory,
            },
            policy="reflect_on_trajectory_policy",
            policy_args=self._policy_args(self.num_requests),
            budget=self._budget(),
        )

    def _reflector_playbook(self) -> str:
        """
        What the reflector is shown: exactly what the generator saw.

        Under `injection="top<k>"` the full markdown would have the
        reflector tagging bullets the generator was never shown (bug
        found by the 2026-08-25 fresh-eyes audit; the reference passes
        only generator-cited bullets). `full`+v1 keeps the archived
        markdown rendering byte-for-byte.
        """
        pb = self._load_playbook()
        if self.reflector_scope == "cited":
            _, theorem_name = self._problem()
            ids = cited_bullet_ids(
                self._gen_dir(), theorem_name, {b.id for b in pb.bullets}
            )
            return render_cited(pb, ids, self.render_version)
        if self.injection == "full" and self.render_version == 1:
            return pb.render_markdown()
        return render_injection(pb, self.injection, self.render_version)

    def _upstream(self) -> tuple[str, str]:
        """
        The curator's evidence and its digest.

        With a Reflector this is the reflection's four insight fields;
        without one it is the raw trajectory (paper Table 3's "ACE w/o
        Reflector"). Either way the digest is asserted against
        `upstream_sha256`.
        """
        if self.reflector == "on":
            refl = load_reflection(self._refl_dir())
            assert refl is not None, "curator scheduled without a reflection"
            digest = reflection_digest(refl)
            return digest, digest
        _, theorem_name = self._problem()
        trajectory = self.trajectory_override or extract_trajectory(
            self._gen_dir(), theorem_name
        )
        return trajectory, trajectory

    def _refl_dir(self) -> Path:
        if self.reflector_dir:
            return _OMPHALOS_DIR / self.reflector_dir
        return _config_dir(
            self.variant, f"step{self.step:02d}_reflector_{self.bench_name}"
        )

    def _curator_args(self) -> dp.RunStrategyArgs:
        evidence, digest = self._upstream()
        assert _sha256(digest) == self.upstream_sha256, (
            f"curator evidence for step {self.step} drifted from the"
            " hash recorded at config-creation time"
        )
        playbook = self._load_playbook().render_markdown()
        contract: dict[str, Any] = (
            {}
            if self.curator_contract == 1
            else {"contract_version": self.curator_contract}
        )

        if self.curator_mode == "monolithic":
            return dp.RunStrategyArgs(
                strategy="rewrite_playbook",
                args={
                    "playbook": playbook,
                    "evidence": evidence,
                    "evidence_kind": (
                        "reflection"
                        if self.reflector == "on"
                        else "trajectory"
                    ),
                    "max_bullets": self.max_bullets,
                },
                policy="rewrite_playbook_policy",
                policy_args=self._policy_args(self.num_requests),
                budget=self._budget(),
            )

        if self.reflector == "off":
            problem_file, _ = self._problem()
            return dp.RunStrategyArgs(
                strategy="curate_from_trajectory",
                args={
                    "problem_file": problem_file,
                    "playbook": playbook,
                    "outcome": read_outcome(self._gen_dir()),
                    "trajectory": evidence,
                    "max_new_bullets": self.max_new_bullets,
                    **contract,
                },
                policy="curate_from_trajectory_policy",
                policy_args=self._policy_args(self.num_requests),
                budget=self._budget(),
            )

        reflection = load_reflection(self._refl_dir())
        assert reflection is not None
        v3: dict[str, Any] = {}
        if self.curator_contract >= 3:
            # The reference feeds its curator the task, the verdict and
            # the budget/progress; without the theorem it cannot apply
            # its own "skip theorem-specific bullets" rule.
            v3 = {
                "theorem": _theorem_text(self._problem()[0]),
                "outcome": read_outcome(self._gen_dir()),
                "progress": self.progress,
            }
        if self.curator_contract >= 4:
            v3["evidence"] = self.evidence
            v3["known_guidance"] = self.known_guidance
        return dp.RunStrategyArgs(
            strategy="curate_playbook",
            args={
                "playbook": playbook,
                "error_identification": reflection.error_identification,
                "root_cause_analysis": reflection.root_cause_analysis,
                "correct_approach": reflection.correct_approach,
                "key_insight": reflection.key_insight
                + (
                    "\n\nVerified episode evidence (distinguish original failure "
                    "from later recovery):\n" + self.repair_evidence
                    if self.repair_evidence
                    else ""
                ),
                "max_new_bullets": self.max_new_bullets,
                **contract,
                **v3,
            },
            policy="curate_playbook_policy",
            policy_args=self._policy_args(self.num_requests),
            budget=self._budget(),
        )

    def _reducer_args(self) -> dp.RunStrategyArgs:
        """
        The batch reducer. Its `upstream_sha256` pins the rendered
        proposals block, rebuilt at instantiate-time from the batch's
        recorded curator outputs (the driver passes their directories
        via `generator_dir`, '|'-joined).
        """
        proposals = _render_proposals(
            [
                _OMPHALOS_DIR / rel
                for rel in self.generator_dir.split("|")
                if rel
            ],
            with_references=self.reducer_contract >= 2,
        )
        assert _sha256(proposals) == self.upstream_sha256, (
            f"reducer proposals for step {self.step} drifted from the"
            " hash recorded at config-creation time"
        )
        v2: dict[str, Any] = {}
        if self.reducer_contract >= 2:
            v2 = {
                "contract_version": self.reducer_contract,
                "evidence": self.evidence,
            }
        return dp.RunStrategyArgs(
            strategy="aggregate_curation_deltas",
            args={
                "playbook": self._load_playbook().render_markdown(),
                "proposals": proposals,
                "max_new_bullets": self.max_new_bullets,
                "progress": self.progress,
                **v2,
            },
            policy="aggregate_curation_deltas_policy",
            policy_args=self._policy_args(self.num_requests),
            budget=self._budget(),
        )

    def _grounder_args(self) -> dp.RunStrategyArgs:
        """
        The grounding gate's Rocq half (`prove_ace.ground_references`):
        no LLM, `Compute` only, one `Locate` per (name, environment)
        until a name resolves. The budget is nominal — nothing is
        spent — and `needs_rocq` is decided by the driver.
        """
        names = [n for n in self.references.split("\n") if n]
        environments = [
            (file, theorem)
            for file, _, theorem in (
                spec.partition("@")
                for spec in self.environments.split("|")
                if spec
            )
        ]
        assert names and environments, (
            "grounder scheduled with nothing to check"
        )
        return dp.RunStrategyArgs(
            strategy="ground_references",
            args={"names": names, "environments": environments},
            policy="ground_references_policy",
            policy_args={},
            budget=self._budget(),
        )

    def _auditor_args(self) -> dp.RunStrategyArgs:
        return dp.RunStrategyArgs(
            strategy="audit_playbook",
            args={
                "playbook": self._load_playbook().render_markdown(),
                "provenance": self.provenance,
                "evidence": self.evidence,
                "known_guidance": self.known_guidance,
                "max_additions": self.audit_max_additions,
            },
            policy="audit_playbook_policy",
            policy_args=self._policy_args(self.num_requests),
            budget=self._budget(),
        )

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if self.campaign_runtime:
            os.environ["OMPHALOS_CAMPAIGN_CELL"] = (
                self.variant + ":" + _config_name(self, _NO_UID)
            )
        if self.role == "generator":
            return self._generator_args()
        if self.role == "reflector":
            return self._reflector_args()
        if self.role == "reducer":
            return self._reducer_args()
        if self.role == "grounder":
            return self._grounder_args()
        if self.role == "auditor":
            return self._auditor_args()
        assert self.role == "curator", f"unknown role {self.role!r}"
        return self._curator_args()


def _render_proposals(
    cur_dirs: "list[Path]", with_references: bool = False
) -> str:
    """
    One `[Sample k]` block per batch member's curator delta. Under
    reducer contract 2 (`with_references`) each proposal also lists its
    `references`, so the reducer can carry them into the final ADDs
    (the x5 smoke run showed it emitting `references: []` for every
    ADD because it had never seen them). The contract-1 rendering is
    byte-identical to the recorded one: it is pinned by every recorded
    reducer's `upstream_sha256`.
    """
    blocks: list[str] = []
    for k, cur_dir in enumerate(cur_dirs):
        delta = load_delta(cur_dir)
        if delta is None or not delta.operations:
            continue
        lines: list[str] = []
        for op in delta.operations:
            lines.append(f"- section: {op.section}\n  content: {op.content}")
            if with_references:
                refs = ", ".join(op.references) if op.references else "[]"
                lines.append(f"  references: {refs}")
        blocks.append(f"[Sample {k}]\n" + "\n".join(lines))
    return "\n\n---\n\n".join(blocks) if blocks else "(no proposals)"


def _theorem_text(problem_file: str) -> str:
    """The theorem statement, for the v3 curator's evidence block."""
    import runtime.pytanque_utils as pt

    spec = pt.parse_problem(problem_file)
    return f"Theorem {spec.theorem_name} {spec.theorem_statement}."


def _progress_block(
    v: AdaptVariant, pb: Playbook, step: int, total: int
) -> str:
    """
    Budget/progress the v3 curator sees (the reference feeds its
    curator the token budget, the training progress and per-section
    playbook stats).
    """
    counts: dict[str, list[int]] = {}
    for b in pb.bullets:
        c = counts.setdefault(b.section, [0, 0, 0])
        c[0] += 1
        c[1] += b.helpful
        c[2] += b.harmful
    lines = [
        f"Playbook: ~{pb.token_estimate()} of {v.playbook_max_tokens}"
        f" budgeted tokens used ({len(pb.bullets)} bullets); additions"
        " beyond the budget are refused deterministically.",
        f"Adaptation progress: step {step + 1} of {total}.",
    ]
    for sec, (n, h, harm) in sorted(counts.items()):
        lines.append(f"  {sec}: {n} bullets (helpful {h}, harmful {harm})")
    return "\n".join(lines)


def load_reflection(refl_dir: Path) -> Reflection | None:
    """The Reflector's parsed output, or `None` if nothing parsed."""
    values = al.load_success_values_from_command_file(
        refl_dir / "result.yaml", Reflection
    )
    if not values:
        return None
    return cast(Reflection, values[0])


def load_delta(cur_dir: Path) -> CurationDelta | None:
    """
    The Curator's parsed delta, or `None` if none parsed.

    `None` is a real outcome, not a crash: a malformed reply on every
    attempt contributes no bullets, which is what an empty delta means.
    `steps.csv` records every occurrence so the parse-failure rate
    stays visible (the v2 contract exists to drive it down).
    """
    values = al.load_success_values_from_command_file(
        cur_dir / "result.yaml", CurationDelta
    )
    if not values:
        return None
    return cast(CurationDelta, values[0])


def load_audit(audit_dir: Path) -> PlaybookAudit | None:
    """The Auditor's parsed output, or `None` if nothing parsed."""
    values = al.load_success_values_from_command_file(
        audit_dir / "result.yaml", PlaybookAudit
    )
    if not values:
        return None
    return cast(PlaybookAudit, values[0])


def load_grounding(ground_dir: Path) -> list[GroundingResult] | None:
    """The grounder's verdicts, or `None` if the run produced none."""
    values = al.load_success_values_from_command_file(
        ground_dir / "result.yaml", list[GroundingResult]
    )
    if not values:
        return None
    return list(cast(list[GroundingResult], values[0]))


def load_rewrite(cur_dir: Path) -> PlaybookRewrite | None:
    """The monolithic Curator's rewrite, or `None` if none parsed."""
    values = al.load_success_values_from_command_file(
        cur_dir / "result.yaml", PlaybookRewrite
    )
    if not values:
        return None
    return cast(PlaybookRewrite, values[0])


def reflection_digest(r: Reflection) -> str:
    """Canonical text of the reflection fields the curator consumes."""
    return "\n---\n".join(
        [
            r.error_identification,
            r.root_cause_analysis,
            r.correct_approach,
            r.key_insight,
        ]
    )


#####
##### Running configs with retries
#####


class RoleRunner[C: dp.ExperimentConfig]:
    """
    Runs configs of one `Experiment` and reports per-config status.

    A config that raises is retried up to `MAX_RETRIES` times
    (`mark_errors_as_todos` + `resume`), which is what a transient
    provider or Rocq hiccup deserves; the caller decides what a
    *persistent* failure means for its role. Statuses are read from the
    experiment's own state file, the established pattern of the report
    tools, because the launcher exposes only global counts.
    """

    def __init__(
        self,
        config_class: type[C],
        output_dir: str,
        naming: Callable[[C, uuid.UUID], str],
        wait: bool = True,
    ) -> None:
        self.config_class = config_class
        self.output_dir = output_dir
        self.naming = naming
        self.wait = wait
        """Queue for Rocq stream slots instead of refusing: a chain
        must survive evaluations holding the slot table."""

    def _experiment(
        self, configs: Sequence[C], needs_rocq: bool = True
    ) -> ol.OmphalosExperiment[C]:
        return ol.OmphalosExperiment(
            config_class=self.config_class,
            context=dp.workspace_execution_context(__file__),
            configs=list(configs),
            output_dir=self.output_dir,
            config_naming=self.naming,
            wait_for_slots=self.wait,
            needs_rocq=needs_rocq,
        )

    def statuses(self, names: Sequence[str]) -> dict[str, str]:
        state_file = _OMPHALOS_DIR / self.output_dir / "experiment.yaml"
        raw: Any = _yaml_load(state_file)
        configs = cast(dict[str, dict[str, Any]], raw["configs"])
        return {n: str(configs[n]["status"]) for n in names}

    def _evict_stale(self, configs: Sequence[C]) -> list[str]:
        """
        Remove the directory of every config that is about to be
        re-registered under an existing name with *different* params.

        The stdlib launcher keys a directory by name and its status
        rebuild trusts a `result.yaml` by name, so when an upstream
        cell is re-run and a downstream config's pinned input hash
        changes, the new config would silently reuse the stale output
        (2026-09-02: this bit three times in one afternoon — the
        x3-strong batch-1 generators, the x5 batch-0 curators and its
        reducer; HINTS #65). Identity is compared the way `Experiment`
        compares it, through `_config_unique_repr`.
        """
        state_file = _OMPHALOS_DIR / self.output_dir / "experiment.yaml"
        if not state_file.exists():
            return []
        from delphyne.stdlib.experiments.experiment_launcher import (
            _config_unique_repr,  # pyright: ignore[reportPrivateUsage]
        )
        from delphyne.utils.typing import pydantic_load

        raw: Any = _yaml_load(state_file)
        stored = cast(dict[str, dict[str, Any]], raw.get("configs") or {})
        evicted: list[str] = []
        for c in configs:
            name = self.naming(c, _NO_UID)
            info = stored.get(name)
            if info is None:
                continue
            old = pydantic_load(self.config_class, info["params"])
            if _config_unique_repr(old) == _config_unique_repr(c):
                continue
            if getattr(c, "campaign_runtime", ""):
                raise ValueError(
                    f"campaign input drift for {name}; use a new variant"
                )
            target = self.config_dir(name)
            if target.exists():
                shutil.rmtree(target)
            evicted.append(name)
            print(
                f"  evicted stale cell {name}: re-registered with different"
                " params (its inputs changed upstream)"
            )
        return evicted

    def run(
        self,
        configs: Sequence[C],
        max_workers: int,
        needs_rocq: bool = True,
    ) -> dict[str, str]:
        """
        Run `configs` (cached no-op when done); return name → status.
        `needs_rocq=False` for the pure-LLM roles (Reflector, Curator,
        Reducer): they take no Rocq stream slot.
        """
        names = [self.naming(c, _NO_UID) for c in configs]
        self._evict_stale(configs)
        exp = self._experiment(configs, needs_rocq).load()
        statuses: dict[str, str] = {}
        for attempt in range(MAX_RETRIES + 1):
            exp.resume(max_workers=max_workers, log_progress=False)
            statuses = self.statuses(names)
            failed = [n for n, s in statuses.items() if s != "done"]
            if any(
                "CampaignExhausted"
                in (self.config_dir(n) / "exception.txt").read_text()
                for n in failed
                if (self.config_dir(n) / "exception.txt").exists()
            ):
                from runtime.campaign_budget import CampaignExhausted

                raise CampaignExhausted(
                    "adaptation allocation exhausted; no artifact frozen"
                )
            if not failed:
                return statuses
            if attempt < MAX_RETRIES:
                print(
                    f"  retrying {len(failed)} failed config(s)"
                    f" ({attempt + 1}/{MAX_RETRIES}): {', '.join(failed)}"
                )
                exp.retry_failed(names=set(failed))
        return statuses

    def config_dir(self, name: str) -> Path:
        return _OMPHALOS_DIR / self.output_dir / "configs" / name

    def replay(self) -> None:
        self._experiment([]).load().replay_all_configs()

    def status(self) -> dict[str, int]:
        return self._experiment([]).load().get_status()


#####
##### Planning the traversal
#####


@dataclass(frozen=True)
class StepPlan:
    step: int
    epoch: int
    pos_in_epoch: int
    bench: str
    batch_id: int


def order_for_epoch(
    order: Sequence[str], epoch: int, shuffle_seed: int | None
) -> list[str]:
    """
    The traversal order of one epoch: file order when `shuffle_seed`
    is `None` (the legacy behaviour), else the `epoch`-th permutation
    drawn from `random.Random(shuffle_seed)` — the paper reshuffles
    per epoch. Deterministic, and every epoch is a permutation.
    """
    if shuffle_seed is None:
        return list(order)
    rng = random.Random(shuffle_seed)
    perm = list(order)
    for _ in range(epoch + 1):
        perm = rng.sample(list(order), len(order))
    return perm


def plan(
    v: AdaptVariant, epochs: int, limit: int | None
) -> list[list[StepPlan]]:
    """The batches of one run, as pure data."""
    order = list(POOLS[v.pool])
    steps: list[StepPlan] = []
    for epoch in range(epochs):
        for pos, bench in enumerate(
            order_for_epoch(order, epoch, v.shuffle_seed)
        ):
            steps.append(StepPlan(len(steps), epoch, pos, bench, 0))
    if limit is not None:
        steps = steps[:limit]
    batches: list[list[StepPlan]] = []
    for i in range(0, len(steps), v.batch_size):
        batch = steps[i : i + v.batch_size]
        batches.append(
            [
                StepPlan(
                    s.step, s.epoch, s.pos_in_epoch, s.bench, len(batches)
                )
                for s in batch
            ]
        )
    return batches


#####
##### Executing a run
#####


@dataclass
class _Roles:
    adapt: RoleRunner[ACEAdaptStepConfig]
    online: RoleRunner[ACEAgenticConfig] | None


def _make_deduper(
    v: AdaptVariant, store: PlaybookStore, replay: bool
) -> Deduper:
    if v.dedup == "lexical":
        return LexicalDeduper(
            v.dedup_threshold
            if v.dedup_threshold is not None
            else LexicalDeduper().threshold
        )
    if v.dedup == "jaccard":
        return JaccardDeduper(
            v.dedup_threshold
            if v.dedup_threshold is not None
            else JaccardDeduper().threshold
        )
    dd = EmbeddingDeduper(
        cache_file=store.embeddings_cache,
        cache_mode="replay" if replay else "read_write",
    )
    if v.dedup_threshold is not None:
        dd.threshold = v.dedup_threshold
    return dd.__enter__()


def _make_step_config(
    v: AdaptVariant,
    role: str,
    s: StepPlan,
    sha: str,
    upstream: str = "",
    generator_dir: str = "",
    reflector_override: str | None = None,
    progress: str = "",
    evidence: str = "",
    guidance: str = "",
    references: str = "",
    environments: str = "",
    provenance: str = "",
    audit_max_additions: int = 0,
) -> ACEAdaptStepConfig:
    generator = role == "generator"
    rewrite = role == "curator" and v.curator_mode == "monolithic"
    return ACEAdaptStepConfig(
        role=role,
        step=s.step,
        bench_name=s.bench,
        seed=v.seed,
        model_name=v.role_model(role),
        toolset=ADAPT_TOOLSET,
        reasoning_effort=v.role_effort(role),
        num_requests=GENERATOR_NUM_REQUESTS
        if generator
        else ROLE_NUM_REQUESTS,
        max_dollar_budget=(
            v.generator_cap
            if generator
            else REWRITE_DOLLAR_CAP
            if rewrite
            else v.role_cap
        ),
        playbook_sha256=sha,
        upstream_sha256=upstream,
        variant=v.name,
        reflector=(
            reflector_override
            if reflector_override is not None
            else v.reflector
        ),
        curator_mode=v.curator_mode,
        injection=v.injection,
        render_version=v.render_version,
        curator_contract=v.curator_contract,
        show_definitions=v.show_definitions,
        progress=progress,
        generator_dir=generator_dir,
        reflector_scope=v.reflector_scope,
        reducer_contract=v.reducer_contract,
        evidence=evidence,
        known_guidance=guidance,
        references=references,
        environments=environments,
        provenance=provenance,
        audit_max_additions=audit_max_additions,
        campaign_runtime=v.campaign_runtime,
    )


def _make_online_config(
    v: AdaptVariant, s: StepPlan, store: PlaybookStore, sha: str
) -> ACEAgenticConfig:
    """The evaluation cell of one online step."""
    return ACEAgenticConfig(
        bench_name=s.bench,
        model_name=ADAPT_MODEL,
        temperature=None,
        toolset=ADAPT_TOOLSET,
        num_requests=GENERATOR_NUM_REQUESTS,
        loop=False,
        seed=v.seed,
        max_dollar_budget=v.generator_cap,
        reasoning_effort=ADAPT_EFFORT,
        playbook_file=store.relpath(sha),
        playbook_sha256=sha,
        injection=v.injection,
        render_version=v.render_version,
        show_definitions=v.show_definitions,
    )


def _freeze(path: Path, pb: Playbook, provenance: Mapping[str, Any]) -> None:
    """
    Write a frozen playbook, refusing to *change* one that exists.

    A frozen playbook is pinned by sha256 inside every evaluation
    config that consumed it. Overwriting one would make every paid run
    that used it unreplayable, so a re-adaptation that drifts must be
    frozen under a new name (the dated-pricing rule: prepend, never
    edit). Re-running an unchanged adaptation is a no-op. A
    `.provenance.yaml` sidecar records how the file was made.
    """
    if path.exists():
        existing = Playbook.load(path)
        assert existing.sha256() == pb.sha256(), (
            f"refusing to overwrite {path.name}: its sha256 would go"
            f" {existing.sha256()[:8]} -> {pb.sha256()[:8]}, which would"
            " invalidate every evaluation run that pinned it. Freeze"
            " this result under a new name instead."
        )
        print(f"Playbook unchanged: {path} (sha {pb.sha256()[:8]})")
        return
    pb.save(path)
    path.with_suffix(".provenance.yaml").write_text(
        yaml.safe_dump(dict(provenance), sort_keys=False)
    )
    print(
        f"Frozen playbook: {path}\n"
        f"  bullets: {len(pb.bullets)}  ~tokens: {pb.token_estimate()}\n"
        f"  sha256: {pb.sha256()}"
    )


def _check_resume_consistency(
    store: PlaybookStore, batches: Sequence[Sequence[StepPlan]]
) -> None:
    """
    A run resumes by re-deriving every step from cache; if the planned
    traversal disagrees with what `steps.csv` recorded (a pool or
    shuffle change), the chain would silently fork. Refuse instead.
    """
    rows = store.read_steps_csv()
    if not rows or int(rows[0].get("schema_version") or 0) < 2:
        return  # legacy or absent record: nothing to compare against
    planned = [s for b in batches for s in b]
    for row, s in zip(rows, planned):
        assert (int(row["step"]), row["bench"]) == (s.step, s.bench), (
            f"steps.csv recorded step {row['step']} = {row['bench']!r} but"
            f" the plan says step {s.step} = {s.bench!r}; the traversal"
            " changed under a recorded run. Use a new variant name."
        )


#####
##### v5 helpers: evidence, the grounding gate, provenance
#####


def _generator_dir(roles: _Roles, step: int, bench: str) -> Path:
    return roles.adapt.config_dir(f"step{step:02d}_generator_{bench}")


class _Evidence:
    """
    The pool-level failure digest, memoized per generator cell: the
    caches are parsed once per run, not once per batch. Rendering is a
    pure function of the cells handed in (`ace_evidence.render_digest`),
    so a resumed run pins the same text into the same configs.
    """

    def __init__(self) -> None:
        self._failures: dict[Path, list[FailedVerdict]] = {}

    def render(self, cells: Sequence[tuple[str, Path]]) -> str:
        verdicts: list[FailedVerdict] = []
        for bench, gen_dir in cells:
            if gen_dir not in self._failures:
                self._failures[gen_dir] = collect_failures({bench: gen_dir})
            verdicts.extend(self._failures[gen_dir])
        return render_digest(verdicts, attempts=len(cells))


def _evidence_cells(
    roles: _Roles,
    rows: Sequence[Mapping[str, object]],
    batch: Sequence[StepPlan],
    gen_dirs: Sequence[Path | None],
) -> list[tuple[str, Path]]:
    """
    The generator cells the digest is computed from: every recorded
    step whose generator ran, in step order, then the current batch's
    non-skipped members. Offline mode only (online generator cells
    live in another experiment and v5 is offline by construction).
    """
    cells: list[tuple[str, Path]] = []
    for row in rows:
        if int(cast(int | str, row.get("generator_failed") or 0)):
            continue
        step = int(cast(int | str, row["step"]))
        bench = str(row["bench"])
        cells.append((bench, _generator_dir(roles, step, bench)))
    for s, d in zip(batch, gen_dirs):
        if d is not None:
            cells.append((s.bench, d))
    return cells


def _render_environments(envs: Sequence[tuple[str, str]]) -> str:
    return "|".join(f"{file}@{theorem}" for file, theorem in envs)


def _batch_environments(
    batch: Sequence[StepPlan], gen_dirs: Sequence[Path | None]
) -> list[tuple[str, str]]:
    """The problems of the batch members that produced a trajectory —
    the environments a batch's bullets are grounded against."""
    return [
        ALL_PROBLEMS[s.bench] for s, d in zip(batch, gen_dirs) if d is not None
    ]


@dataclass
class _GateOutcome:
    """
    What the grounding gate did with a set of ADDs. Ops are addressed
    by `id()` because a batch's deltas are held in memory for exactly
    one merge; `refused` maps an op to the names Rocq did not know,
    `errors` holds ops kept although a reference could not be checked.
    """

    refused: dict[int, list[str]]
    errors: set[int]
    checked: list[GroundingResult]

    def keep(self, ops: Sequence[AddOp]) -> list[AddOp]:
        return [op for op in ops if id(op) not in self.refused]


def _ground(
    v: AdaptVariant,
    roles: _Roles,
    s: StepPlan,
    sha: str,
    ops: Sequence[AddOp],
    environments: Sequence[tuple[str, str]],
) -> list[GroundingResult] | None:
    """
    Run the grounder config for `ops` (one per batch, named by the
    batch's first step). Returns `None` when the grounder failed all
    retries — the gate then keeps everything and records the failure —
    and `[]` when there was nothing to check.
    """
    names = checkable_references(name for op in ops for name in op.references)
    if not names or not environments:
        return []
    references = "\n".join(names)
    rendered_envs = _render_environments(environments)
    cfg = _make_step_config(
        v,
        "grounder",
        s,
        sha,
        upstream=_sha256(references + "\n" + rendered_envs),
        references=references,
        environments=rendered_envs,
    )
    st = roles.adapt.run([cfg], max_workers=1, needs_rocq=True)
    name = _config_name(cfg, _NO_UID)
    if st.get(name) != "done":
        return None
    return load_grounding(roles.adapt.config_dir(name))


def _apply_gate(
    ops: Sequence[AddOp], results: Sequence[GroundingResult] | None
) -> _GateOutcome:
    """
    Refuse every op with a reference Rocq answered `missing`; keep an
    op whose references could not all be checked (a bridge failure is
    not evidence about the name) and count it under `errors`. With
    `results is None` (no grounder output) every op is kept and
    counted as an error if it had anything to check.
    """
    by_name = {r.name: r for r in results or []}
    refused: dict[int, list[str]] = {}
    errors: set[int] = set()
    for op in ops:
        names = checkable_references(op.references)
        missing = [
            n
            for n in names
            if n in by_name and by_name[n].verdict == "missing"
        ]
        if missing:
            refused[id(op)] = missing
            continue
        unchecked = [
            n
            for n in names
            if n not in by_name or by_name[n].verdict == "error"
        ]
        if unchecked:
            errors.add(id(op))
    return _GateOutcome(
        refused=refused, errors=errors, checked=list(results or [])
    )


def _attribute(
    ops: Sequence[AddOp],
    added: Sequence[str],
    not_created: Sequence[str],
) -> list[tuple[str, AddOp]]:
    """
    Pair each id a merge created with the op that created it. `merge`
    creates ids in op order for every op it neither folded (dedup) nor
    refused (size guard); `not_created` lists those ops' contents.
    """
    leftovers = list(not_created)
    ids = iter(added)
    pairs: list[tuple[str, AddOp]] = []
    for op in ops:
        if op.content in leftovers:
            leftovers.remove(op.content)
            continue
        new_id = next(ids, None)
        if new_id is None:
            break
        pairs.append((new_id, op))
    return pairs


def _provenance_record(
    op: AddOp,
    step: int,
    benches: Sequence[str],
    solved: Sequence[bool],
    source: str,
) -> dict[str, Any]:
    return {
        "step": step,
        "benches": list(benches),
        "solved": [bool(x) for x in solved],
        "section": op.section,
        "references": list(op.references),
        "source": source,
    }


def _provenance_block(
    pb: Playbook, prov: Mapping[str, Mapping[str, Any]]
) -> str:
    """One line per bullet for the Auditor: origin, outcome, counters."""
    lines: list[str] = []
    for b in pb.bullets:
        rec = prov.get(b.id)
        if rec is None:
            lines.append(
                f"- [{b.id}] origin not recorded; helpful={b.helpful},"
                f" harmful={b.harmful}"
            )
            continue
        benches = cast(Sequence[str], rec.get("benches") or [])
        solved = cast(Sequence[bool], rec.get("solved") or [])
        origins = (
            ", ".join(
                f"{bn} ({'solved' if sv else 'NOT solved'})"
                for bn, sv in zip(benches, solved)
            )
            or "the whole pool"
        )
        refs = ", ".join(cast(Sequence[str], rec.get("references") or []))
        lines.append(
            f"- [{b.id}] step {rec.get('step')} ({rec.get('source')}), from"
            f" {origins}; helpful={b.helpful}, harmful={b.harmful};"
            f" references: {refs or 'none listed'}"
        )
    return "\n".join(lines)


@dataclass
class RepairEvidence:
    reflection: Reflection | None
    generator_dir: str = ""
    reflector_dir: str = ""
    trajectory: str = ""
    episodes: str = ""
    records: list[dict[str, Any]] = field(default_factory=lambda: [])


def _repair_batch(
    v: AdaptVariant,
    batch: Sequence[StepPlan],
    sha: str,
    roles: _Roles,
    gen_dirs: Sequence[Path | None],
    trajectories: Sequence[str | None],
    reflections: Sequence[Reflection | None],
    *,
    max_workers: int,
) -> list[RepairEvidence]:
    """Reflect -> fresh regeneration -> reflect, stopping on verification.

    The original generator remains the measured training episode. Repairs
    are adaptation work; their evidence and cost are separate. Every round
    has a distinct config identity, and final curation sees every episode.
    """
    result = [RepairEvidence(r) for r in reflections]
    eligible: set[int] = set()
    for i, (directory, trajectory, reflection) in enumerate(
        zip(gen_dirs, trajectories, reflections)
    ):
        if directory is None or trajectory is None or reflection is None:
            continue
        if read_result(directory)[0]:
            continue
        eligible.add(i)
        result[i].episodes = (
            "## Original episode\nOutcome: "
            + read_outcome(directory)
            + "\n"
            + trajectory
        )
    for round_no in range(1, v.repair_rounds + 1):
        if not eligible:
            break
        generators: dict[int, ACEAdaptStepConfig] = {}
        for i in sorted(eligible):
            reflection = result[i].reflection
            assert reflection is not None
            diagnosis = reflection_digest(reflection)
            generators[i] = replace(
                _make_step_config(
                    v, "generator", batch[i], sha, _sha256(diagnosis)
                ),
                repair_round=round_no,
                episode_guidance=diagnosis,
                num_requests=v.repair_requests,
                max_dollar_budget=v.repair_cap,
            )
        statuses = roles.adapt.run(
            list(generators.values()), max_workers=max_workers
        )
        reflectors: dict[int, ACEAdaptStepConfig] = {}
        recovered: set[int] = set()
        for i, cfg in generators.items():
            name = _config_name(cfg, _NO_UID)
            record: dict[str, Any] = dict(
                step=batch[i].step,
                bench=batch[i].bench,
                round=round_no,
                generator=name,
                status=statuses[name],
            )
            result[i].records.append(record)
            if statuses[name] != "done":
                eligible.discard(i)
                continue
            directory = roles.adapt.config_dir(name)
            solved = read_result(directory)[0]
            record["solved"] = solved
            record["requests"] = read_requests(directory)
            if solved:
                recovered.add(i)
            trajectory = extract_trajectory(
                directory, ALL_PROBLEMS[batch[i].bench][1]
            )
            result[i].generator_dir = str(directory.relative_to(_OMPHALOS_DIR))
            result[i].trajectory = trajectory
            result[i].episodes += (
                f"\n\n## Reflection before repair {round_no}\n"
                + cfg.episode_guidance
                + f"\n\n## Repair episode {round_no}\nOutcome: "
                + read_outcome(directory)
                + "\n"
                + trajectory
            )
            reflectors[i] = replace(
                _make_step_config(
                    v,
                    "reflector",
                    batch[i],
                    sha,
                    _sha256(result[i].episodes),
                    result[i].generator_dir,
                ),
                repair_round=round_no,
                trajectory_override=result[i].episodes,
            )
        if reflectors:
            statuses = roles.adapt.run(
                list(reflectors.values()),
                max_workers=max_workers,
                needs_rocq=False,
            )
        for i, cfg in reflectors.items():
            name = _config_name(cfg, _NO_UID)
            reflection = (
                load_reflection(roles.adapt.config_dir(name))
                if statuses[name] == "done"
                else None
            )
            if reflection is None:
                # Never curate a recovered attempt using a stale diagnosis.
                result[i].reflection = None
                eligible.discard(i)
            else:
                result[i].reflection = reflection
                result[i].reflector_dir = str(
                    roles.adapt.config_dir(name).relative_to(_OMPHALOS_DIR)
                )
        eligible -= recovered
    return result


def execute(
    v: AdaptVariant,
    batches: Sequence[Sequence[StepPlan]],
    roles: _Roles,
    deduper: Deduper,
    *,
    max_workers: int,
) -> tuple[Playbook, list[str]]:
    """
    Run the planned batches; return the final playbook and the list of
    playbook hashes *before* each step (the derived step index).
    """
    store = PlaybookStore(v.name)
    store.materialize_legacy_steps()
    _check_resume_consistency(store, batches)
    store.reset_refine_log()
    store.reset_logs()

    pb = v.warmup()
    rows: list[dict[str, object]] = []
    shas_before: list[str] = []
    merged_steps = 0
    evidence_digest = _Evidence()
    prov: dict[str, dict[str, Any]] = {}
    repair_records: list[dict[str, Any]] = []

    for batch in batches:
        sha = store.put(pb)
        label = ", ".join(s.bench for s in batch)
        print(f"=== step(s) {batch[0].step:02d}+{len(batch) - 1}: {label} ===")

        # --- generator -------------------------------------------
        gen_dirs: list[Path | None] = []
        if v.mode == "online":
            assert roles.online is not None
            cfgs_o = [_make_online_config(v, s, store, sha) for s in batch]
            st = roles.online.run(cfgs_o, max_workers=max_workers)
            for c in cfgs_o:
                name = ace_config_name(c, _NO_UID)
                gen_dirs.append(
                    roles.online.config_dir(name)
                    if st[name] == "done"
                    else None
                )
        else:
            cfgs_g = [_make_step_config(v, "generator", s, sha) for s in batch]
            st = roles.adapt.run(cfgs_g, max_workers=max_workers)
            for c in cfgs_g:
                name = _config_name(c, _NO_UID)
                gen_dirs.append(
                    roles.adapt.config_dir(name)
                    if st[name] == "done"
                    else None
                )
        gen_skipped = [d is None for d in gen_dirs]
        for s, skipped in zip(batch, gen_skipped):
            if skipped:
                # A generator cell that failed all retries (e.g. its
                # verification repeatedly blew the memory guard) skips
                # the whole adaptation step: no trajectory exists to
                # learn from. Recorded, never fatal — the reference
                # excludes API-error samples the same way.
                print(
                    f"  step {s.step:02d} {s.bench}: generator failed"
                    " after retries; step skipped"
                )
        gen_rel = [
            "" if d is None else str(d.relative_to(_OMPHALOS_DIR))
            for d in gen_dirs
        ]
        generator_dir = gen_rel if v.mode == "online" else [""] * len(batch)
        trajectories = [
            None
            if d is None
            else extract_trajectory(d, ALL_PROBLEMS[s.bench][1])
            for d, s in zip(gen_dirs, batch)
        ]
        solved = [False if d is None else read_result(d)[0] for d in gen_dirs]
        requests = [0 if d is None else read_requests(d) for d in gen_dirs]
        trivial = [
            v.skip_trivial and d is not None and solved[i] and requests[i] <= 1
            for i, d in enumerate(gen_dirs)
        ]
        for s, is_trivial in zip(batch, trivial):
            if is_trivial:
                print(
                    f"  step {s.step:02d} {s.bench}: solved on the first"
                    " proposal; no Reflector/Curator call (skip_trivial)"
                )
        known_ids = {b.id for b in pb.bullets}
        cited: list[list[str] | None] = [
            None
            if d is None or v.render_version < 3
            else cited_bullet_ids(d, ALL_PROBLEMS[s.bench][1], known_ids)
            for d, s in zip(gen_dirs, batch)
        ]

        # --- reflector -------------------------------------------
        reflections: list[Reflection | None] = [None] * len(batch)
        reflector_failed = [False] * len(batch)
        if v.reflector == "on":
            cfgs_r = [
                _make_step_config(
                    v, "reflector", s, sha, _sha256(t), generator_dir[i]
                )
                for i, (s, t) in enumerate(zip(batch, trajectories))
                if t is not None and not trivial[i]
            ]
            st = roles.adapt.run(
                cfgs_r, max_workers=max_workers, needs_rocq=False
            )
            by_bench = {c.bench_name: c for c in cfgs_r}
            for i, s in enumerate(batch):
                if gen_skipped[i] or trivial[i]:
                    continue
                c = by_bench[s.bench]
                name = _config_name(c, _NO_UID)
                if st[name] == "done":
                    reflections[i] = load_reflection(
                        roles.adapt.config_dir(name)
                    )
                if reflections[i] is None:
                    reflector_failed[i] = True
                    print(
                        f"  {batch[i].bench}: reflector produced nothing usable"
                    )

        repairs = [RepairEvidence(r) for r in reflections]
        if v.repair_rounds:
            repairs = _repair_batch(
                v,
                batch,
                sha,
                roles,
                gen_dirs,
                trajectories,
                reflections,
                max_workers=max_workers,
            )
            for i, repair in enumerate(repairs):
                repair_records.extend(repair.records)
                if repair.generator_dir:
                    generator_dir[i] = repair.generator_dir
                    reflections[i] = repair.reflection
                    trajectories[i] = repair.episodes
            repair_path = _OMPHALOS_DIR / _output_dir(v.name) / "repairs.yaml"
            repair_path.write_text(
                yaml.safe_dump(repair_records, sort_keys=False)
            )

        # --- v5 evidence (curator contract 4) ----------------------
        evidence = guidance = ""
        if v.curator_contract >= 4:
            evidence = evidence_digest.render(
                _evidence_cells(roles, rows, batch, gen_dirs)
            )
            guidance = known_guidance()

        # --- curator ---------------------------------------------
        cfgs_c: list[ACEAdaptStepConfig | None] = []
        curator_fallback = [False] * len(batch)
        for i, s in enumerate(batch):
            if gen_skipped[i] or trivial[i]:
                cfgs_c.append(None)
                continue
            refl = reflections[i]
            if v.reflector == "on" and refl is None:
                # Reflector produced nothing usable. The reference never
                # loses the step (it curates on the raw reflector text);
                # our equivalent is the trajectory-fed curator the
                # no-Reflector ablation already uses. Recorded in
                # steps.csv as `curator_fallback`.
                curator_fallback[i] = True
            traj = trajectories[i]
            assert traj is not None  # skipped members handled above
            digest = reflection_digest(refl) if refl is not None else traj
            cfgs_c.append(
                _make_step_config(
                    v,
                    "curator",
                    s,
                    sha,
                    _sha256(digest),
                    generator_dir[i],
                    reflector_override="off" if curator_fallback[i] else None,
                    progress=(
                        _progress_block(
                            v, pb, s.step, sum(len(b2) for b2 in batches)
                        )
                        if v.curator_contract >= 3
                        else ""
                    ),
                    evidence=evidence,
                    guidance=guidance,
                )
            )
        if v.repair_rounds:
            cfgs_c = [
                replace(
                    c,
                    reflector_dir=repairs[i].reflector_dir,
                    repair_evidence=repairs[i].episodes,
                    trajectory_override=repairs[i].episodes,
                )
                if c is not None
                else None
                for i, c in enumerate(cfgs_c)
            ]
        live = [c for c in cfgs_c if c is not None]
        st = (
            roles.adapt.run(live, max_workers=max_workers, needs_rocq=False)
            if live
            else {}
        )

        # --- reduce (batch > 1 with the reducer): one aggregation ---
        reduced_delta: CurationDelta | None = None
        use_reducer = (
            v.reduce_batch
            and len(batch) > 1
            and v.curator_mode == "incremental"
        )
        if use_reducer:
            live_dirs = [
                roles.adapt.config_dir(_config_name(c, _NO_UID))
                for c in live
                if st.get(_config_name(c, _NO_UID)) == "done"
            ]
            proposals = _render_proposals(
                live_dirs, with_references=v.reducer_contract >= 2
            )
            red_cfg = _make_step_config(
                v,
                "reducer",
                batch[0],
                sha,
                _sha256(proposals),
                "|".join(
                    str(p2.relative_to(_OMPHALOS_DIR)) for p2 in live_dirs
                ),
                progress=(
                    _progress_block(
                        v, pb, batch[0].step, sum(len(b2) for b2 in batches)
                    )
                    if v.curator_contract >= 3
                    else ""
                ),
                evidence=evidence,
            )
            st_r = roles.adapt.run([red_cfg], max_workers=1, needs_rocq=False)
            name_r = _config_name(red_cfg, _NO_UID)
            if st_r.get(name_r) == "done":
                reduced_delta = load_delta(roles.adapt.config_dir(name_r))

        # --- v5 grounding gate (after the reducer, before any merge) --
        member_deltas: list[CurationDelta | None] = [
            load_delta(roles.adapt.config_dir(_config_name(c, _NO_UID)))
            if c is not None and st.get(_config_name(c, _NO_UID)) == "done"
            else None
            for c in cfgs_c
        ]
        proposed = [
            0 if d is None else len(d.operations) for d in member_deltas
        ]
        if use_reducer:
            gate_ops: list[AddOp] = (
                list(reduced_delta.operations)
                if reduced_delta is not None
                else []
            )
        else:
            gate_ops = [
                op
                for d in member_deltas
                if d is not None
                for op in d.operations
            ]
        gate = _GateOutcome(refused={}, errors=set(), checked=[])
        if v.grounding and gate_ops:
            results = _ground(
                v,
                roles,
                batch[0],
                sha,
                gate_ops,
                _batch_environments(batch, gen_dirs),
            )
            gate = _apply_gate(gate_ops, results)
            store.append_log(
                store.grounding_log,
                {
                    "batch": batch[0].batch_id,
                    "step": batch[0].step,
                    "grounder_failed": results is None,
                    "checked": [
                        {
                            "name": r.name,
                            "verdict": r.verdict,
                            "environment": r.environment,
                            "answer": " ".join(r.answer.split())[:160],
                        }
                        for r in gate.checked
                    ],
                    "refused": [
                        {
                            "content": op.content,
                            "missing": gate.refused[id(op)],
                        }
                        for op in gate_ops
                        if id(op) in gate.refused
                    ],
                    "kept_unchecked": len(gate.errors),
                },
            )
            print(
                f"  batch {batch[0].batch_id}: grounding checked"
                f" {len(gate.checked)} name(s), refused {len(gate.refused)}"
                f" ADD(s), {len(gate.errors)} kept unchecked"
                + (" (grounder failed)" if results is None else "")
            )

        # --- merge (sequential, deterministic) -------------------
        for i, s in enumerate(batch):
            if gen_skipped[i]:
                shas_before.append(sha)
                rows.append(
                    {
                        "schema_version": STEPS_SCHEMA_VERSION,
                        "variant": v.name,
                        "mode": v.mode,
                        "step": s.step,
                        "epoch": s.epoch,
                        "pos_in_epoch": s.pos_in_epoch,
                        "batch_id": s.batch_id,
                        "bench": s.bench,
                        "seed": v.seed,
                        "sha256_before": sha,
                        "sha256_after": pb.sha256(),
                        "reflector": v.reflector,
                        "curator_mode": v.curator_mode,
                        "generator_solved": 0,
                        "generator_failed": 1,
                        "bullets_before": len(pb.bullets),
                        "tokens_before": pb.token_estimate(),
                        "added": 0,
                        "deduped": 0,
                        "dropped": 0,
                        "tags_helpful": 0,
                        "tags_harmful": 0,
                        "refined": 0,
                        "pruned": 0,
                        "merged": 0,
                        "compacted": 0,
                        "bullets_after": len(pb.bullets),
                        "tokens_after": pb.token_estimate(),
                        "curator_failed": 0,
                        "curator_fallback": 0,
                        "reflector_failed": 0,
                        "cited_count": "",
                        "tags_dropped": 0,
                        "skipped_trivial": 0,
                        "proposed": 0,
                        "reduced_out": 0,
                        "ungrounded": 0,
                        "grounding_error": 0,
                    }
                )
                merged_steps += 1
                continue
            refl = reflections[i]
            all_tags: list[BulletTag] = (
                refl.bullet_tags if refl is not None else []
            )
            if v.reflector_scope == "cited":
                allowed = set(cited[i] or [])
                tags = [t for t in all_tags if t.id in allowed]
            else:
                tags = all_tags
            tags_dropped = len(all_tags) - len(tags)
            before = (len(pb.bullets), pb.token_estimate())
            curator_failed = False
            cfg = cfgs_c[i]
            cur_dir = (
                roles.adapt.config_dir(_config_name(cfg, _NO_UID))
                if cfg is not None
                and st.get(_config_name(cfg, _NO_UID)) == "done"
                else None
            )
            if v.curator_mode == "monolithic":
                rewritten = load_rewrite(cur_dir) if cur_dir else None
                if rewritten is None:
                    curator_failed = True
                    out = merge(pb, [], tags, deduper=deduper)
                else:
                    tagged = merge(pb, [], tags, deduper=deduper).playbook
                    out = rebuild(tagged, rewritten.bullets)
            elif use_reducer:
                # Tags apply per member; content lands once via the
                # reduced delta after the loop.
                delta = None
                out = merge(pb, [], tags, deduper=deduper)
                curator_failed = (
                    st.get(_config_name(cfg, _NO_UID)) != "done"
                    if cfg is not None
                    else False
                )
            else:
                delta = member_deltas[i]
                if delta is None:
                    # A scheduled curator that produced nothing usable;
                    # a member without a curator (skipped, trivial) is
                    # not a failure.
                    curator_failed = cfg is not None
                    out = merge(pb, [], tags, deduper=deduper)
                else:
                    kept_ops = gate.keep(delta.operations)
                    out = merge(
                        pb,
                        kept_ops,
                        tags,
                        deduper=deduper,
                        dedup_counts_helpful=v.count_dedup_as_helpful,
                        max_tokens=v.playbook_max_tokens,
                    )
                    for new_id, op in _attribute(
                        kept_ops,
                        out.added,
                        [c for _, c in out.deduped] + list(out.dropped),
                    ):
                        prov[new_id] = _provenance_record(
                            op, s.step, [s.bench], [solved[i]], "curator"
                        )
            member_delta = member_deltas[i]
            member_ops: Sequence[AddOp] = (
                [] if member_delta is None else member_delta.operations
            )
            member_refused = sum(
                1 for op in member_ops if id(op) in gate.refused
            )
            member_errors = sum(
                1 for op in member_ops if id(op) in gate.errors
            )
            for w in out.warnings:
                print(f"  merge warning: {w}")
            pb = out.playbook
            merged_steps += 1

            refined = 0
            n_pruned = n_merged = n_compacted = 0
            last_of_epoch = s.pos_in_epoch == len(POOLS[v.pool]) - 1
            if v.refine_every > 0 and (
                merged_steps % v.refine_every == 0 or last_of_epoch
            ):
                r = refine(
                    pb,
                    deduper,
                    prune_harmful=v.prune_harmful,
                    max_tokens=v.playbook_max_tokens,
                )
                refined = 1
                n_pruned, n_merged, n_compacted = (
                    len(r.pruned),
                    len(r.merged),
                    len(r.compacted),
                )
                if r.pruned or r.merged or r.compacted:
                    store.append_refine_log(
                        {
                            "step": s.step,
                            "pruned": [b.id for b in r.pruned],
                            "merged": [list(m) for m in r.merged],
                            "compacted": [b.id for b in r.compacted],
                        }
                    )
                pb = r.playbook
            print(
                f"  step {s.step:02d} {s.bench}: {'solved' if solved[i] else 'unsolved'},"
                f" +{len(out.added)} bullets, {len(out.deduped)} deduped,"
                f" {len(out.dropped)} dropped"
                + (
                    f", refine: -{n_pruned} pruned -{n_merged} merged"
                    f" -{n_compacted} compacted"
                    if refined
                    else ""
                )
                + (
                    f", cited {len(cited[i] or [])}"
                    + (
                        f", {tags_dropped} tag(s) dropped"
                        if tags_dropped
                        else ""
                    )
                    if cited[i] is not None
                    else ""
                )
                + f" -> {len(pb.bullets)} total"
            )
            shas_before.append(sha)
            rows.append(
                {
                    "schema_version": STEPS_SCHEMA_VERSION,
                    "variant": v.name,
                    "mode": v.mode,
                    "step": s.step,
                    "epoch": s.epoch,
                    "pos_in_epoch": s.pos_in_epoch,
                    "batch_id": s.batch_id,
                    "bench": s.bench,
                    "seed": v.seed,
                    "sha256_before": sha,
                    "sha256_after": pb.sha256(),
                    "reflector": v.reflector,
                    "curator_mode": v.curator_mode,
                    "generator_solved": int(solved[i]),
                    "bullets_before": before[0],
                    "tokens_before": before[1],
                    "added": len(out.added),
                    "deduped": len(out.deduped),
                    "dropped": len(out.dropped),
                    "tags_helpful": sum(1 for t in tags if t.tag == "helpful"),
                    "tags_harmful": sum(1 for t in tags if t.tag == "harmful"),
                    "refined": refined,
                    "pruned": n_pruned,
                    "merged": n_merged,
                    "compacted": n_compacted,
                    "bullets_after": len(pb.bullets),
                    "tokens_after": pb.token_estimate(),
                    "curator_failed": int(curator_failed),
                    "curator_fallback": int(curator_fallback[i]),
                    "reflector_failed": int(reflector_failed[i]),
                    "cited_count": (
                        "" if cited[i] is None else len(cited[i] or [])
                    ),
                    "tags_dropped": tags_dropped,
                    "skipped_trivial": int(trivial[i]),
                    "proposed": proposed[i],
                    "reduced_out": 0,
                    "ungrounded": 0 if use_reducer else member_refused,
                    "grounding_error": 0 if use_reducer else member_errors,
                }
            )
        if use_reducer and reduced_delta is not None:
            reduced_ops = gate.keep(reduced_delta.operations)
            out_r = merge(
                pb,
                reduced_ops,
                [],
                deduper=deduper,
                dedup_counts_helpful=v.count_dedup_as_helpful,
                max_tokens=v.playbook_max_tokens,
            )
            for w in out_r.warnings:
                print(f"  reduce warning: {w}")
            print(
                f"  batch {batch[0].batch_id}: reducer +{len(out_r.added)}"
                f" bullets, {len(out_r.deduped)} deduped,"
                f" {len(out_r.dropped)} dropped"
                + (f", {len(gate.refused)} ungrounded" if gate.refused else "")
            )
            pb = out_r.playbook
            live_members = [
                (s.bench, solved[i])
                for i, s in enumerate(batch)
                if gen_dirs[i] is not None
            ]
            for new_id, op in _attribute(
                reduced_ops,
                out_r.added,
                [c for _, c in out_r.deduped] + list(out_r.dropped),
            ):
                prov[new_id] = _provenance_record(
                    op,
                    batch[0].step,
                    [bn for bn, _ in live_members],
                    [sv for _, sv in live_members],
                    "reducer",
                )
            if rows:
                prev_added = rows[-1]["added"]
                assert isinstance(prev_added, int)
                rows[-1]["added"] = prev_added + len(out_r.added)
                rows[-1]["bullets_after"] = len(pb.bullets)
                rows[-1]["tokens_after"] = pb.token_estimate()
                rows[-1]["sha256_after"] = pb.sha256()
                rows[-1]["reduced_out"] = len(reduced_delta.operations)
                rows[-1]["ungrounded"] = len(gate.refused)
                rows[-1]["grounding_error"] = len(gate.errors)

        # Persist after every batch: an interrupted run leaves a short
        # but accurate record, and the step index is pruned of files
        # from any longer earlier run.
        store.put(pb)
        store.write_step_index([*shas_before, pb.sha256()])
        store.write_steps_csv(rows)
        if v.curator_contract >= 4:
            store.write_provenance(prov)
    return pb, shas_before


def _run_audit(
    v: AdaptVariant,
    pb: Playbook,
    store: PlaybookStore,
    roles: _Roles,
    n_steps: int,
) -> tuple[Playbook, dict[str, Any]]:
    """
    The terminal audit (v5): one `AuditPlaybook` call over the finished
    playbook, its provenance, the whole pool's failure digest and the
    prover's pitfalls; the Auditor's additions pass the grounding gate
    against one environment per distinct import signature of the pool;
    `apply_audit` applies the decisions deterministically. Everything
    is logged to `audit.log.yaml`; the caller freezes the result.
    """
    sha = store.put(pb)
    rows = store.read_steps_csv()
    cells = [
        (row["bench"], _generator_dir(roles, int(row["step"]), row["bench"]))
        for row in rows
        if not int(row.get("generator_failed") or 0)
    ]
    evidence = _Evidence().render(cells)
    guidance = known_guidance()
    provenance = _provenance_block(pb, store.read_provenance())
    plan_step = StepPlan(n_steps, 0, 0, AUDIT_BENCH, -1)
    cfg = _make_step_config(
        v,
        "auditor",
        plan_step,
        sha,
        upstream=_sha256(provenance + "\n" + evidence),
        evidence=evidence,
        guidance=guidance,
        provenance=provenance,
        audit_max_additions=v.audit_max_additions,
    )
    st = roles.adapt.run([cfg], max_workers=1, needs_rocq=False)
    name = _config_name(cfg, _NO_UID)
    audit = (
        load_audit(roles.adapt.config_dir(name))
        if st.get(name) == "done"
        else None
    )
    if audit is None:
        print("  audit: the Auditor produced nothing usable; frozen unaudited")
        store.append_log(store.audit_log, {"config": name, "failed": True})
        return pb, {"audit_config": name, "audit_failed": True}
    additions = list(audit.additions)
    results = _ground(
        v,
        roles,
        plan_step,
        sha,
        additions,
        representative_files(POOLS[v.pool]),
    )
    gate = _apply_gate(additions, results)
    kept = gate.keep(additions)
    out = apply_audit(
        pb, audit.decisions, kept, max_tokens=v.playbook_max_tokens
    )
    for w in out.warnings:
        print(f"  audit warning: {w}")
    prov = store.read_provenance()
    for new_id, op in _attribute(kept, out.added, out.refused):
        prov[new_id] = _provenance_record(op, n_steps, [], [], "audit")
    store.write_provenance(prov)
    store.append_log(
        store.audit_log,
        {
            "config": name,
            "playbook_before": sha,
            "playbook_after": out.playbook.sha256(),
            "decisions": [
                {"id": d.id, "action": d.action, "reason": d.reason}
                for d in audit.decisions
            ],
            "dropped": [list(x) for x in out.dropped],
            "rewritten": out.rewritten,
            "added": out.added,
            "ungrounded": [
                {"content": op.content, "missing": gate.refused[id(op)]}
                for op in additions
                if id(op) in gate.refused
            ],
            "size_refused": out.refused,
            "grounder_failed": results is None,
            "warnings": out.warnings,
        },
    )
    print(
        f"  audit: kept {len(out.kept)}, rewrote {len(out.rewritten)},"
        f" dropped {len(out.dropped)}, added {len(out.added)}"
        f" ({len(gate.refused)} addition(s) ungrounded,"
        f" {len(out.refused)} refused by the size guard)"
        f" -> {len(out.playbook.bullets)} bullets,"
        f" ~{out.playbook.token_estimate()} tokens"
    )
    store.put(out.playbook)
    return out.playbook, {
        "audit_config": name,
        "audit_dropped": [i for i, _ in out.dropped],
        "audit_rewritten": out.rewritten,
        "audit_added": out.added,
    }


def _roles(v: AdaptVariant) -> _Roles:
    adapt = RoleRunner(ACEAdaptStepConfig, _output_dir(v.name), _config_name)
    online = (
        RoleRunner(
            ACEAgenticConfig, _online_output_dir(v.name), ace_config_name
        )
        if v.mode == "online"
        else None
    )
    return _Roles(adapt, online)


class CLI:
    """Fire CLI for the adaptation driver."""

    def plan(
        self, variant: str = LEGACY_VARIANT, epochs: int | None = None
    ) -> None:
        """Print the traversal a run would follow. No spend."""
        v = _variant(variant)
        n_epochs = v.epochs if epochs is None else int(epochs)
        for batch in plan(v, n_epochs, None):
            for s in batch:
                print(
                    f"step {s.step:03d}  epoch {s.epoch}  pos {s.pos_in_epoch:02d}"
                    f"  batch {s.batch_id:03d}  {s.bench}"
                )

    def run(
        self,
        variant: str = LEGACY_VARIANT,
        epochs: int | None = None,
        limit: int | None = None,
        max_workers: int | None = None,
    ) -> None:
        """
        Run (or resume) one adaptation variant.

        `epochs` overrides the variant's own value; `limit` caps the
        number of steps for a cheap wiring check (`--limit=1`). The
        final playbook is frozen only on a full, unoverridden run, so
        a partial run can never produce an artifact that looks
        complete. `max_workers` defaults to the batch size.
        """
        v = _variant(variant)
        n_epochs = v.epochs if epochs is None else int(epochs)
        complete = limit is None and epochs is None
        batches = plan(v, n_epochs, limit)
        from tools.data.ace_review_benchmark import assert_training_allowed

        assert_training_allowed([s.bench for b in batches for s in b])
        if v.campaign_runtime:
            from experiments.ace.ace_review_experiment import activate_budget

            activate_budget("adaptation")
            os.environ["OMPHALOS_CAMPAIGN_CELL"] = v.name + ":embeddings"
        store = PlaybookStore(v.name)
        deduper = _make_deduper(v, store, replay=False)
        try:
            pb, _ = execute(
                v,
                batches,
                _roles(v),
                deduper,
                max_workers=max_workers or max(1, v.batch_size),
            )
        finally:
            if isinstance(deduper, EmbeddingDeduper):
                deduper.close()
        if not complete:
            print(
                f"Partial run ({sum(len(b) for b in batches)} step(s),"
                f" epochs={n_epochs}); playbook NOT frozen."
            )
            return
        if v.mode == "online":
            store.final_sha_file.write_text(pb.sha256() + "\n")
            print(f"Online chain complete; final playbook {pb.sha256()[:8]}")
            return
        assert v.final_playbook is not None
        n_steps = sum(len(b) for b in batches)
        provenance: dict[str, Any] = {
            "variant": v.name,
            "mode": v.mode,
            "pool": v.pool,
            "epochs": n_epochs,
            "shuffle_seed": v.shuffle_seed,
            "steps": n_steps,
            "warmup_sha256": (
                v.warmup().sha256() if v.warmup_playbook else None
            ),
            "dedup": v.dedup,
            "refine_every": v.refine_every,
            "prune_harmful": v.prune_harmful,
            "render_version": v.render_version,
            "curator_contract": v.curator_contract,
            "reflector_scope": v.reflector_scope,
            "reducer_contract": v.reducer_contract,
            "grounding": v.grounding,
            "skip_trivial": v.skip_trivial,
            "reflector_model": v.role_model("reflector"),
            "curator_model": v.role_model("curator"),
        }
        if v.repair_rounds:
            provenance.update(
                repair_rounds=v.repair_rounds,
                repair_requests=v.repair_requests,
                repair_cap=v.repair_cap,
                runtime_sha256=v.campaign_runtime,
            )
        if v.audit:
            assert v.preaudit_playbook is not None
            _freeze(
                PLAYBOOKS_DIR / v.preaudit_playbook,
                pb,
                {**provenance, "sha256": pb.sha256(), "stage": "preaudit"},
            )
            pb, audit_info = _run_audit(v, pb, store, _roles(v), n_steps)
            provenance.update(audit_info)
            provenance["preaudit_playbook"] = v.preaudit_playbook
            provenance["stage"] = "audited"
        _freeze(
            PLAYBOOKS_DIR / v.final_playbook,
            pb,
            {**provenance, "sha256": pb.sha256()},
        )

    def replay(self, variant: str = LEGACY_VARIANT) -> None:
        """
        Replay every recorded config with `cache_mode="replay"`, which
        raises on any cache miss, then re-derive the playbook chain
        from those caches. Zero spend, or a loud failure.
        """
        v = _variant(variant)
        PlaybookStore(v.name).materialize_legacy_steps()
        roles = _roles(v)
        roles.adapt.replay()
        if roles.online is not None:
            roles.online.replay()
        print(f"replay of {variant!r}: every recorded config hit the cache")

    def status(self, variant: str = LEGACY_VARIANT) -> None:
        v = _variant(variant)
        roles = _roles(v)
        print("adaptation:", roles.adapt.status())
        if roles.online is not None:
            print("online cells:", roles.online.status())


if __name__ == "__main__":
    fire.Fire(CLI)  # type: ignore
