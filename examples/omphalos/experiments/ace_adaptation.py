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
computed by `tools/ace_report.py` and companions.

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
    python experiments/ace_adaptation.py plan --variant=x-offline
    python experiments/ace_adaptation.py run --variant=x-offline
    python experiments/ace_adaptation.py run --variant=x-offline --limit=2
    python experiments/ace_adaptation.py replay --variant=train
    python experiments/ace_adaptation.py status --variant=train
"""

# pyright: strict

import hashlib
import random
import re
import sys
import uuid
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import fire  # type: ignore
import yaml

import delphyne as dp
import delphyne.stdlib.answer_loaders as al

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ace_pool  # noqa: E402
import miniF2F_bench as mf  # noqa: E402
import minif2f_x as x  # noqa: E402
from ace_bench import (  # noqa: E402
    ACEAgenticConfig,
    ace_config_name,
    render_cited,
    render_injection,
)
from ace_dedup import (  # noqa: E402
    EmbeddingDeduper,
    JaccardDeduper,
    LexicalDeduper,
)
import omphalos_launch as ol  # noqa: E402
from ace_playbook import (  # noqa: E402
    BulletTag,
    Deduper,
    Playbook,
    merge,
    rebuild,
    refine,
)
from ace_store import (  # noqa: E402
    LEGACY_VARIANT,
    PLAYBOOKS_DIR,
    STEPS_SCHEMA_VERSION,
    PlaybookStore,
)
from prove_ace import (  # noqa: E402
    CurationDelta,
    PlaybookRewrite,
    Reflection,
)

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent

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

    def __post_init__(self) -> None:
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
        if role == "curator" and self.curator_model is not None:
            return self.curator_model
        return ADAPT_MODEL


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
    assert name in VARIANTS, (
        f"unknown variant {name!r}; known: {', '.join(VARIANTS)}"
    )
    return VARIANTS[name]


def _output_dir(variant: str) -> str:
    return f"experiments/output/ace_adaptation_{variant}"


def _online_output_dir(variant: str) -> str:
    return f"experiments/output/ace_online_{variant}_agentic"


ADAPT_MODEL = "gpt-5.6-luna"
ADAPT_TOOLSET = "core"
ADAPT_EFFORT = "medium"
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


#####
##### Configurations
#####


_NO_UID = uuid.UUID(int=0)
"""Naming here is a pure function of the config; the uid is unused."""


def _config_name(cfg: "ACEAdaptStepConfig", _uid: uuid.UUID) -> str:
    return f"step{cfg.step:02d}_{cfg.role}_{cfg.bench_name}"


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
        trajectory = extract_trajectory(gen_dir, theorem_name)
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
        trajectory = extract_trajectory(self._gen_dir(), theorem_name)
        return trajectory, trajectory

    def _refl_dir(self) -> Path:
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
        return dp.RunStrategyArgs(
            strategy="curate_playbook",
            args={
                "playbook": playbook,
                "error_identification": reflection.error_identification,
                "root_cause_analysis": reflection.root_cause_analysis,
                "correct_approach": reflection.correct_approach,
                "key_insight": reflection.key_insight,
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
            ]
        )
        assert _sha256(proposals) == self.upstream_sha256, (
            f"reducer proposals for step {self.step} drifted from the"
            " hash recorded at config-creation time"
        )
        return dp.RunStrategyArgs(
            strategy="aggregate_curation_deltas",
            args={
                "playbook": self._load_playbook().render_markdown(),
                "proposals": proposals,
                "max_new_bullets": self.max_new_bullets,
                "progress": self.progress,
            },
            policy="aggregate_curation_deltas_policy",
            policy_args=self._policy_args(self.num_requests),
            budget=self._budget(),
        )

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if self.role == "generator":
            return self._generator_args()
        if self.role == "reflector":
            return self._reflector_args()
        if self.role == "reducer":
            return self._reducer_args()
        assert self.role == "curator", f"unknown role {self.role!r}"
        return self._curator_args()


def _render_proposals(cur_dirs: "list[Path]") -> str:
    """One `[Sample k]` block per batch member's curator delta."""
    blocks: list[str] = []
    for k, cur_dir in enumerate(cur_dirs):
        delta = load_delta(cur_dir)
        if delta is None or not delta.operations:
            continue
        ops = "\n".join(
            f"- section: {op.section}\n  content: {op.content}"
            for op in delta.operations
        )
        blocks.append(f"[Sample {k}]\n{ops}")
    return "\n\n---\n\n".join(blocks) if blocks else "(no proposals)"


def _theorem_text(problem_file: str) -> str:
    """The theorem statement, for the v3 curator's evidence block."""
    import pytanque_utils as pt

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
    ) -> dp.Experiment[C]:
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
        exp = self._experiment(configs, needs_rocq).load()
        statuses: dict[str, str] = {}
        for attempt in range(MAX_RETRIES + 1):
            exp.resume(max_workers=max_workers, log_progress=False)
            statuses = self.statuses(names)
            failed = [n for n, s in statuses.items() if s != "done"]
            if not failed:
                return statuses
            if attempt < MAX_RETRIES:
                print(
                    f"  retrying {len(failed)} failed config(s)"
                    f" ({attempt + 1}/{MAX_RETRIES}): {', '.join(failed)}"
                )
                exp.mark_errors_as_todos()
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
        reasoning_effort=ADAPT_EFFORT,
        num_requests=GENERATOR_NUM_REQUESTS
        if generator
        else ROLE_NUM_REQUESTS,
        max_dollar_budget=(
            v.generator_cap
            if generator
            else REWRITE_DOLLAR_CAP
            if rewrite
            else ROLE_DOLLAR_CAP
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

    pb = v.warmup()
    rows: list[dict[str, object]] = []
    shas_before: list[str] = []
    merged_steps = 0

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
                if t is not None
            ]
            st = roles.adapt.run(
                cfgs_r, max_workers=max_workers, needs_rocq=False
            )
            by_bench = {c.bench_name: c for c in cfgs_r}
            for i, s in enumerate(batch):
                if gen_skipped[i]:
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

        # --- curator ---------------------------------------------
        cfgs_c: list[ACEAdaptStepConfig | None] = []
        curator_fallback = [False] * len(batch)
        for i, s in enumerate(batch):
            if gen_skipped[i]:
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
                )
            )
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
            proposals = _render_proposals(live_dirs)
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
            )
            st_r = roles.adapt.run([red_cfg], max_workers=1, needs_rocq=False)
            name_r = _config_name(red_cfg, _NO_UID)
            if st_r.get(name_r) == "done":
                reduced_delta = load_delta(roles.adapt.config_dir(name_r))

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
                delta = load_delta(cur_dir) if cur_dir else None
                if delta is None:
                    curator_failed = True
                    out = merge(pb, [], tags, deduper=deduper)
                else:
                    out = merge(
                        pb,
                        delta.operations,
                        tags,
                        deduper=deduper,
                        dedup_counts_helpful=v.count_dedup_as_helpful,
                        max_tokens=v.playbook_max_tokens,
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
                }
            )
        if use_reducer and reduced_delta is not None:
            out_r = merge(
                pb,
                reduced_delta.operations,
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
            )
            pb = out_r.playbook
            if rows:
                prev_added = rows[-1]["added"]
                assert isinstance(prev_added, int)
                rows[-1]["added"] = prev_added + len(out_r.added)
                rows[-1]["bullets_after"] = len(pb.bullets)
                rows[-1]["tokens_after"] = pb.token_estimate()
                rows[-1]["sha256_after"] = pb.sha256()

        # Persist after every batch: an interrupted run leaves a short
        # but accurate record, and the step index is pruned of files
        # from any longer earlier run.
        store.put(pb)
        store.write_step_index([*shas_before, pb.sha256()])
        store.write_steps_csv(rows)
    return pb, shas_before


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
        _freeze(
            PLAYBOOKS_DIR / v.final_playbook,
            pb,
            {
                "variant": v.name,
                "mode": v.mode,
                "pool": v.pool,
                "epochs": n_epochs,
                "shuffle_seed": v.shuffle_seed,
                "steps": sum(len(b) for b in batches),
                "sha256": pb.sha256(),
                "warmup_sha256": (
                    v.warmup().sha256() if v.warmup_playbook else None
                ),
                "dedup": v.dedup,
                "refine_every": v.refine_every,
                "prune_harmful": v.prune_harmful,
                "render_version": v.render_version,
                "curator_contract": v.curator_contract,
                "reflector_scope": v.reflector_scope,
            },
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
