"""
ACE (Agentic Context Engineering) pipeline for the agentic baseline.

Implements the three roles of arXiv:2510.04618 on top of the frozen
agentic machinery, without touching it:

- **Generator** — `prove_theorem_ace`: byte-for-byte the canonical
  agentic loop (`prove_agentic.prove_theorem_agentic`), except that
  the proposal query is `ProposeProofScriptACE`, a subclass that
  carries the rendered playbook and renders it as one extra system
  prompt section. Tool handlers, verifier and few-shot examples are
  the agentic ones (the example selector redirects to the
  `ProposeProofScriptAgentic` bucket, and each example renders through
  *its own* query's templates, so the few-shot messages stay
  byte-identical to the frozen baseline's).
- **Reflector** — `ReflectOnTrajectory`: one-shot query over the full
  trajectory of a proof attempt plus the verifier's outcome. Extracts
  the paper's insight schema (error, root cause, correct approach,
  key insight) and tags existing playbook bullets
  helpful/harmful/neutral.
- **Curator** — `CuratePlaybook`: one-shot query emitting incremental
  ADD-only delta operations, merged deterministically by
  `ace_playbook.merge` (never by an LLM — that is the paper's defense
  against context collapse).

Deviations from the paper (also noted in `ace_playbook` and
`PROGRESS.md`): no generator-side bullet tagging (the prover's output
contract stays untouched; the Reflector infers attribution from the
trajectory), lexical instead of embedding-based dedup, and — inherent
to this domain — no ground-truth labels anywhere: the only supervision
is the Rocq verifier, which is exactly the paper's "execution feedback
without GT labels" setting (their Table 1, offline ✗ arm).

Replicability: this module is purely additive. It imports from
`prove_agentic` rather than duplicating or modifying it, defines new
query names (hence new templates, new cache keys), and leaves every
frozen rendering untouched — proven by `make test` + experiment
`replay` staying green.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, cast

import delphyne as dp
from delphyne import Branch, Compute, Strategy, dfs, strategy
from delphyne.stdlib.queries import ExampleSelector, SelectedExample

import runtime.pytanque_utils as pt
import runtime.skills as sk
from ace.ace_evidence import (
    GroundingVerdict,
    grounding_verdict,
    locate_command,
)
from ace.ace_playbook import AddOp, AuditDecision, BulletTag, RewriteBullet
from ace.ace_triggers import (
    DEFAULT_MAX_HINTS,
    DEFAULT_SELECTION_RULE,
    Hint,
    TriggerAssignment,
    parse_table,
    select_hints,
)
from runtime.model_registry import ApiType, OmphalosReasoningEffort, make_model
from prove_agentic import (
    InspectAt,
    ProposeProofScriptAgentic,
    ReadSkill,
    SearchRocq,
    Toolset,
    TryAutomation,
    TryTactics,
    _inspect_at_handler,  # pyright: ignore[reportPrivateUsage]
    _read_skill_handler,  # pyright: ignore[reportPrivateUsage]
    _search_rocq_handler,  # pyright: ignore[reportPrivateUsage]
    _try_automation_handler,  # pyright: ignore[reportPrivateUsage]
    _try_tactics_handler,  # pyright: ignore[reportPrivateUsage]
    check_proof_assisted,
)
from prove_standard import ProofScript

# fmt: off


#####
##### Generator
#####


@dataclass
class ProposeProofScriptACE(ProposeProofScriptAgentic):
    """
    The agentic proposal query, plus a playbook.

    A separate query class rather than a new field on the agentic one:
    `query_name()` derives template names and cache identities from
    the class name, so the frozen `ProposeProofScriptAgentic` prompts
    and caches cannot be perturbed by anything this class does. The
    ACE templates `{% include %}` the agentic ones and append a
    playbook section (see `prompts/ace/generation/ProposeProofScriptACE.system.jinja`).

    `playbook` is the *rendered* playbook (`Playbook.render_markdown`
    for v1, `Playbook.render_prompt` for v2), not a file path: the
    query must be self-contained so that cached runs replay without
    reading external state. Empty string = no playbook section, which
    makes the prompt byte-identical to the agentic baseline's (v2's
    empty rendering; v1 rendered a placeholder line instead).
    """

    playbook: str = ""
    render_version: int = 1
    """
    Which playbook rendering `playbook` holds — 1 shows ids and
    helpful/harmful counters, 2 shows ids only — so the template's
    prose can describe what the model actually sees. Defaulted to 1 so
    every recorded ACE prompt renders byte-identically.
    """


@dataclass
class ProposeProofScriptACERepair(ProposeProofScriptACE):
    """Fresh proof episode conditioned on the preceding reflection."""

    episode_guidance: str = ""


@strategy
def prove_theorem_ace(
    problem_file: str,
    theorem_name: str,
    toolset: Toolset = "core",
    turn_budget: int = 32,
    playbook: str = "",
    show_definitions: bool = False,
    render_version: int = 1,
    goal_caps: pt.GoalCaps | None = None,
    episode_guidance: str = "",
) -> Strategy[Branch, dp.PromptingPolicy, ProofScript]:
    """
    ACE generator: `prove_theorem_agentic` with a playbook.

    The body mirrors `prove_agentic.prove_theorem_agentic` — same
    verifier, same tool handlers — with `ProposeProofScriptACE` as the
    proposal query. Defaults follow the canonical configuration
    (`core`, 32 turns) rather than the agentic strategy's historical
    ones: this strategy has no frozen runs to stay compatible with.
    """
    spec = pt.parse_problem(problem_file, show_definitions)
    available = sk.list_skills()
    script = yield from dp.interact(
        step=lambda prefix, _:
            (ProposeProofScriptACERepair(
                spec, available, toolset, turn_budget, prefix, playbook,
                render_version, episode_guidance,
            ) if episode_guidance else ProposeProofScriptACE(
                spec, available, toolset, turn_budget, prefix, playbook,
                render_version,
            )).using(dp.ambient_pp),
        process=lambda s, _:
            check_proof_assisted(problem_file, theorem_name, s, goal_caps)
              .using(dp.just_compute),
        tools={
            ReadSkill: lambda call:
                _read_skill_handler(call.skill_name).using(dp.just_compute),
            SearchRocq: lambda call:
                _search_rocq_handler(problem_file, theorem_name, call.command)
                  .using(dp.just_compute),
            InspectAt: lambda call:
                _inspect_at_handler(
                    problem_file, theorem_name, call.tactics, call.command
                ).using(dp.just_compute),
            TryAutomation: lambda call:
                _try_automation_handler(
                    problem_file, theorem_name, call.tactics
                ).using(dp.just_compute),
            TryTactics: lambda call:
                _try_tactics_handler(
                    problem_file, theorem_name,
                    call.tactics, call.candidates,
                ).using(dp.just_compute),
        },
    )
    return script


def _ace_examples() -> ExampleSelector:
    """
    Example selector for the ACE proposal query.

    `ProposeProofScriptACE` has its own (empty) example bucket, so this
    selector fetches from the `"ProposeProofScriptAgentic"` bucket
    instead and applies the same filter as
    `prove_agentic._matching_toolset_examples`: toolset-neutral
    examples (empty `prefix`) are kept for every toolset, tool-workflow
    examples only on a toolset match. Each selected example renders
    through its *own* query's templates (`create_prompt` uses the
    example's query instance), so the few-shot messages are
    byte-identical to the agentic baseline's — the playbook section is
    the only prompt difference, by construction.
    """
    def select(
        env: dp.PolicyEnv,
        query: dp.AbstractQuery[Any],
    ) -> Sequence[SelectedExample]:
        examples = env.examples.examples_for("ProposeProofScriptAgentic")
        kept: list[SelectedExample] = []
        for i, ex in enumerate(examples):
            exq = ex.query
            keep = (
                not isinstance(exq, ProposeProofScriptAgentic)
                or not exq.prefix
                or (
                    isinstance(query, ProposeProofScriptAgentic)
                    and exq.toolset == query.toolset
                )
            )
            if keep:
                kept.append(
                    SelectedExample(example=ex, index=i, similarity=None)
                )
        return kept

    return ExampleSelector(select)


@dp.ensure_compatible(prove_theorem_ace)
def prove_theorem_ace_policy(
    model_name: str,
    temperature: float | None = None,
    max_turns: int | None = None,
    loop: bool = False,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    convert_user_feedback_to_tool: bool = True,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    """
    Policy for the ACE generator.

    Identical to `prove_agentic.prove_theorem_agentic_policy` except
    for the example selector (bucket redirect, see `_ace_examples`)
    and the `api` default: this strategy postdates the Responses
    migration and has no Chat Completions archive to protect, so it
    defaults to the canonical API instead of the historical one.
    """
    model = make_model(
        model_name,
        for_tool_calls=True,
        api=api,
        reasoning_effort=reasoning_effort,
        convert_user_feedback_to_tool=convert_user_feedback_to_tool,
    )
    sp = dfs(max_depth=max_turns)
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(
        model,
        temperature=temperature,
        max_requests=1,
        select_examples=_ace_examples(),
        tag_user_feedback_messages=(api == "responses"),
    )
    return sp & pp


#####
##### Reflector
#####


@dataclass
class Reflection:
    """
    The Reflector's output, mirroring the paper's schema (their
    Fig. 10/13): a diagnosis of the trajectory plus per-bullet tags.
    `bullet_tags` may only reference ids present in the rendered
    playbook; unknown ids are ignored (with a warning) at merge time.
    """

    reasoning: str
    error_identification: str
    root_cause_analysis: str
    correct_approach: str
    key_insight: str
    bullet_tags: list[BulletTag]


@dataclass
class ReflectOnTrajectory(dp.Query[Reflection]):
    """
    One-shot Reflector query.

    Inputs are plain strings so the query is self-contained (cache
    keys must not depend on external files): `outcome` is the verdict
    line ("SOLVED ..." / "NOT SOLVED ..."), `playbook` the rendered
    markdown with bullet ids, `trajectory` the rendered transcript of
    the attempt (see `experiments/ace/ace_adaptation.py` for the exact
    rendering). There are no ground-truth labels in this domain; the
    Rocq verifier's feedback inside the trajectory is the only
    supervision (the paper's "offline, no GT labels" setting).
    """

    spec: pt.ProblemSpec
    outcome: str
    playbook: str
    trajectory: str

    __parser__ = dp.last_code_block.yaml


@strategy
def reflect_on_trajectory(
    problem_file: str,
    outcome: str,
    playbook: str,
    trajectory: str,
) -> Strategy[Branch, dp.PromptingPolicy, Reflection]:
    # Takes the problem *file* (like the prover strategies) so that
    # experiment configs only ever pass plain strings; the spec is
    # re-parsed here, deterministically.
    spec = pt.parse_problem(problem_file)
    reflection = yield from dp.branch(
        ReflectOnTrajectory(spec, outcome, playbook, trajectory)
          .using(dp.ambient_pp)
    )
    return reflection


#####
##### Curator
#####


@dataclass
class CurationDelta:
    """The Curator's output: incremental ADD operations only."""

    reasoning: str
    operations: list[AddOp]


@dataclass
class CuratePlaybook(dp.Query[CurationDelta]):
    """
    One-shot Curator query.

    Sees the current playbook and the Reflector's insight fields
    (passed as plain strings so the query — and the experiment configs
    that construct it — stay trivially serializable), and proposes at
    most `max_new_bullets` ADD operations. It never edits or deletes
    existing bullets: merging, dedup and counters are deterministic
    code in `ace_playbook.merge` (the paper's defense against context
    collapse).
    """

    playbook: str
    error_identification: str
    root_cause_analysis: str
    correct_approach: str
    key_insight: str
    max_new_bullets: int = 3
    contract_version: int = 1
    theorem: str = ""
    outcome: str = ""
    progress: str = ""
    """
    v3 evidence (all default-empty so v1/v2 prompts render unchanged):
    the theorem statement the attempt was about, the verifier verdict
    line, and a pre-rendered budget/progress block (playbook tokens
    used of budget, step k of n, per-section counts) — the reference
    implementation feeds its curator all three, and its prompt cannot
    reject "theorem-specific" bullets without seeing the theorem.
    """
    evidence: str = ""
    known_guidance: str = ""
    """
    v4 evidence (contract 4, 2026-09-02; default-empty so v1-v3 prompts
    render unchanged): the pool-level verifier-failure digest
    (`ace_evidence.render_digest`) and the pitfalls section of the
    prover's own system prompt (`ace_evidence.known_guidance`). The
    contract-3 rule "do not restate the system prompt" was addressed
    to a model that had never seen that prompt; and one diagnosis at a
    time cannot tell frequent from distinctive (PROGRESS 2026-09-02,
    causes C1 and C4).
    """
    """
    1 = the original output contract; 2 demands block scalars
    (`content: |`) — an unquoted `: ` inside a plain scalar makes YAML
    read a bullet as a mapping, and that killed a 60-step run at step
    6 (HINTS #45). Versioned rather than edited so the recorded
    curator prompts replay byte-identically.
    """

    __parser__ = dp.last_code_block.yaml


@strategy
def curate_playbook(
    playbook: str,
    error_identification: str,
    root_cause_analysis: str,
    correct_approach: str,
    key_insight: str,
    max_new_bullets: int = 3,
    contract_version: int = 1,
    theorem: str = "",
    outcome: str = "",
    progress: str = "",
    evidence: str = "",
    known_guidance: str = "",
) -> Strategy[Branch, dp.PromptingPolicy, CurationDelta]:
    delta = yield from dp.branch(
        CuratePlaybook(
            playbook,
            error_identification,
            root_cause_analysis,
            correct_approach,
            key_insight,
            max_new_bullets,
            contract_version,
            theorem,
            outcome,
            progress,
            evidence,
            known_guidance,
        ).using(dp.ambient_pp)
    )
    return delta


#####
##### Ablation arms: Curator without a Reflector, and monolithic curation
#####


@dataclass
class CurateFromTrajectory(dp.Query[CurationDelta]):
    """
    Curator that reads the raw trajectory instead of a diagnosis.

    The `reflector="off"` arm (paper Table 3, "ACE w/o Reflector"): the
    Generator's trajectory goes straight to the Curator, collapsing
    ACE's three roles into two. A separate query class rather than
    optional fields on `CuratePlaybook`, because `query_name()` derives
    both the template names and the cache identity from the class name
    — so this arm structurally cannot perturb the frozen incremental
    Curator's renderings.

    Second, unavoidable consequence of dropping the Reflector: nothing
    produces `bullet_tags`, so in this arm counters only ever move
    through `merge`'s dedup path. Recorded here rather than hidden — it
    is part of what the ablation measures.
    """

    spec: pt.ProblemSpec
    playbook: str
    outcome: str
    trajectory: str
    max_new_bullets: int = 3
    contract_version: int = 1

    __parser__ = dp.last_code_block.yaml


@strategy
def curate_from_trajectory(
    problem_file: str,
    playbook: str,
    outcome: str,
    trajectory: str,
    max_new_bullets: int = 3,
    contract_version: int = 1,
) -> Strategy[Branch, dp.PromptingPolicy, CurationDelta]:
    spec = pt.parse_problem(problem_file)
    delta = yield from dp.branch(
        CurateFromTrajectory(
            spec, playbook, outcome, trajectory, max_new_bullets,
            contract_version,
        ).using(dp.ambient_pp)
    )
    return delta


@dataclass
class PlaybookRewrite:
    """A whole-playbook rewrite: every surviving bullet, verbatim."""

    reasoning: str
    bullets: list[RewriteBullet]


@dataclass
class RewritePlaybook(dp.Query[PlaybookRewrite]):
    """
    Regenerate the WHOLE playbook (Dynamic-Cheatsheet cumulative mode).

    The `curator_mode="monolithic"` arm — the paper's key ablation
    (Table 18) and the mechanism behind context collapse (their
    Fig. 2). Any bullet the model omits is deleted; the deterministic
    merge is bypassed entirely.

    Written to be a *fair opponent, not a straw man*: the prompt asks
    explicitly to carry forward everything still useful, and the same
    size guard applies as in the incremental arm (`ace_playbook.
    rebuild`). A rigged rewrite prompt would make the ablation
    worthless. `evidence_kind` records which upstream fed this arm, so
    one query covers both reflector-on and reflector-off.
    """

    playbook: str
    evidence: str
    evidence_kind: Literal["reflection", "trajectory"]
    max_bullets: int = 40

    __parser__ = dp.last_code_block.yaml


@strategy
def rewrite_playbook(
    playbook: str,
    evidence: str,
    evidence_kind: Literal["reflection", "trajectory"],
    max_bullets: int = 40,
) -> Strategy[Branch, dp.PromptingPolicy, PlaybookRewrite]:
    rewritten = yield from dp.branch(
        RewritePlaybook(
            playbook, evidence, evidence_kind, max_bullets
        ).using(dp.ambient_pp)
    )
    return rewritten


@dataclass
class AggregateCurationDeltas(dp.Query[CurationDelta]):
    """
    Reduce independently proposed ADD operations into one final set.

    The reference's batched ("ComBEE-style") design: each batch member
    proposes deltas against the same batch-start playbook; this reducer
    sees all proposals side by side and emits the final ADD list —
    synthesising overlaps, dropping what the playbook already covers.
    Cross-sample redundancy becomes an LLM judgement instead of a
    similarity threshold. Grouping is seeded and deterministic in the
    driver; the reference's unseeded "augmented shuffling" is
    deliberately not reproduced (it is nondeterministic and duplicates
    evidence).
    """

    playbook: str
    proposals: str
    """The proposed operations, rendered one `[Sample k]` block each."""
    max_new_bullets: int = 6
    progress: str = ""
    contract_version: int = 1
    evidence: str = ""
    """
    Contract 2 (2026-09-02): the reducer sees the pool-level failure
    digest and is told that frequent beats distinctive, and it carries
    each proposal's `references` into the final ADDs. Both default so
    the recorded contract-1 prompts render unchanged.
    """

    __parser__ = dp.last_code_block.yaml


@strategy
def aggregate_curation_deltas(
    playbook: str,
    proposals: str,
    max_new_bullets: int = 6,
    progress: str = "",
    contract_version: int = 1,
    evidence: str = "",
) -> Strategy[Branch, dp.PromptingPolicy, CurationDelta]:
    delta = yield from dp.branch(
        AggregateCurationDeltas(
            playbook,
            proposals,
            max_new_bullets,
            progress,
            contract_version,
            evidence,
        ).using(dp.ambient_pp)
    )
    return delta


#####
##### v5 (2026-09-02): the Auditor and the grounding gate
#####


@dataclass
class PlaybookAudit:
    """
    The Auditor's output: a decision per bullet it chose to mention
    (unmentioned bullets are kept — `ace_playbook.apply_audit`) and a
    capped list of additions for uncovered, frequent failure classes.
    """

    reasoning: str
    decisions: list[AuditDecision]
    additions: list[AddOp]


@dataclass
class AuditPlaybook(dp.Query[PlaybookAudit]):
    """
    One-shot terminal audit of a finished playbook.

    Runs once, after the last adaptation step and before the playbook
    is frozen. Sees the playbook *with counters*, a provenance line per
    bullet (origin step and theorem, solved or not, references), the
    pool-level failure digest and the prover's own pitfalls. This is
    the "be more selective" step the v3 study lacked: 15 of its 26
    bullets were never tagged, several contradicted each other or the
    verifier, and nothing ever read the playbook as a whole. It is
    deliberately *not* the monolithic-rewrite ablation: default-keep,
    explicit per-bullet reasons, a single pass, and the pre-audit
    playbook is frozen alongside the audited one.
    """

    playbook: str
    provenance: str
    evidence: str
    known_guidance: str
    max_additions: int = 6

    __parser__ = dp.last_code_block.yaml


@strategy
def audit_playbook(
    playbook: str,
    provenance: str,
    evidence: str,
    known_guidance: str,
    max_additions: int = 6,
) -> Strategy[Branch, dp.PromptingPolicy, PlaybookAudit]:
    audit = yield from dp.branch(
        AuditPlaybook(
            playbook, provenance, evidence, known_guidance, max_additions
        ).using(dp.ambient_pp)
    )
    return audit


@dataclass
class GroundingResult:
    """
    What Rocq said about one referenced name: `grounded` (an object of
    that name exists in `environment`), `missing` (no environment
    knows it) or `error` (the bridge could not answer — not evidence
    either way). `answer` is the last `Locate` output seen.
    """

    name: str
    verdict: GroundingVerdict
    environment: str
    answer: str


@strategy
def ground_references(
    names: list[str],
    environments: list[tuple[str, str]],
) -> Strategy[Compute, object, list[GroundingResult]]:
    """
    The grounding gate's Rocq half: for each name, ask `Locate name.`
    in each `(problem_file, theorem_name)` environment in order and
    stop at the first that knows it. No LLM anywhere — every answer is
    a `dp.compute` over `pytanque_utils.query`, cached and replayable
    exactly like the verifier's `check` calls. Ordering is fixed by the
    inputs, so a resumed run re-derives the same verdicts from cache.
    """
    results: list[GroundingResult] = []
    for name in names:
        verdict: GroundingVerdict = "missing"
        environment = ""
        answer = ""
        for problem_file, theorem_name in environments:
            answer = yield from dp.compute(pt.query)(
                problem_file, theorem_name, locate_command(name)
            )
            environment = problem_file
            verdict = grounding_verdict(answer)
            if verdict == "grounded":
                break
        results.append(GroundingResult(name, verdict, environment, answer))
    return results


#####
##### Hint on error (2026-09-05): error-keyed injection
#####


@dataclass
class ProposeProofScriptACETriggered(ProposeProofScriptACE):
    """
    The agentic proposal query with the playbook delivered *on error*.

    `playbook` stays empty, so the system and instance prompts render
    byte-identically to the agentic baseline's (the first request of a
    cell is the baseline's first request); the only difference is the
    feedback template, which appends the bullets `check_proof_assisted
    _hinted` attached to the verdict. A separate class so the templates
    and the cache namespace are its own — the frozen ACE and agentic
    templates are not touched.
    """


@dataclass
class HintedFeedback(pt.Feedback):
    """A verifier verdict plus the playbook bullets it triggered."""

    hints: list[Hint] = field(default_factory=list[Hint])


@strategy
def check_proof_assisted_hinted(
    problem_file: str,
    theorem_name: str,
    script: ProofScript,
    triggers: str,
    max_hints: int = DEFAULT_MAX_HINTS,
    goal_caps: pt.GoalCaps | None = None,
    selection_rule: int = DEFAULT_SELECTION_RULE,
) -> Strategy[Compute, object, ProofScript | dp.Error]:
    """
    `prove_agentic.check_proof_assisted`, then hint selection.

    The verifier call is the same cached `compute` with the same
    arguments (a hinted cell's verdicts are byte-identical to the
    baseline's for the same script); the selection is pure Python over
    the verdict (`ace_triggers.select_hints`) and travels to the
    prompt inside the error's `meta`. `triggers` is the frozen table's
    own text, so a recorded cell replays without reading any file.
    """
    tactics = yield from dp.compute(pt.split_into_tactics)(script)
    if goal_caps is None:
        feedback = yield from dp.compute(pt.check_assisted)(
            problem_file, theorem_name, tactics
        )
    else:
        feedback = yield from dp.compute(pt.check_assisted)(
            problem_file, theorem_name, tactics, goal_caps=goal_caps
        )
    if feedback.success:
        if feedback.auto_finished:
            return "\n".join(feedback.proof_so_far)
        return script
    hints = select_hints(
        parse_table(triggers),
        error_message=feedback.error_message,
        failing_tactic=feedback.failing_tactic,
        goals=feedback.remaining_goals,
        k=max_hints,
        rule=selection_rule,
    )
    hinted = HintedFeedback(
        success=feedback.success,
        failing_index=feedback.failing_index,
        failing_tactic=feedback.failing_tactic,
        error_message=feedback.error_message,
        remaining_goals=feedback.remaining_goals,
        proof_so_far=feedback.proof_so_far,
        finished=feedback.finished,
        probe=feedback.probe,
        auto_finished=feedback.auto_finished,
        hints=hints,
    )
    if feedback.failing_tactic == "Qed." and feedback.remaining_goals:
        return dp.Error(label="incomplete", meta=hinted)
    return dp.Error(label="feedback", meta=hinted)


@strategy
def prove_theorem_ace_triggered(
    problem_file: str,
    theorem_name: str,
    triggers: str,
    toolset: Toolset = "core",
    turn_budget: int = 32,
    max_hints: int = DEFAULT_MAX_HINTS,
    show_definitions: bool = False,
    goal_caps: pt.GoalCaps | None = None,
    selection_rule: int = DEFAULT_SELECTION_RULE,
) -> Strategy[Branch, dp.PromptingPolicy, ProofScript]:
    """
    ACE generator with the playbook injected on error only.

    `prove_theorem_ace` with an empty playbook, the triggered query and
    the hinted verifier: the prompt carries no playbook, and each
    rejected proposal's feedback carries at most `max_hints` bullets
    whose triggers match the rejection. Same tools, same budget.
    """
    spec = pt.parse_problem(problem_file, show_definitions)
    available = sk.list_skills()
    script = yield from dp.interact(
        step=lambda prefix, _:
            ProposeProofScriptACETriggered(
                spec, available, toolset, turn_budget, prefix, "", 2,
            ).using(dp.ambient_pp),
        process=lambda s, _:
            check_proof_assisted_hinted(
                problem_file, theorem_name, s, triggers, max_hints,
                goal_caps, selection_rule,
            ).using(dp.just_compute),
        tools={
            ReadSkill: lambda call:
                _read_skill_handler(call.skill_name).using(dp.just_compute),
            SearchRocq: lambda call:
                _search_rocq_handler(problem_file, theorem_name, call.command)
                  .using(dp.just_compute),
            InspectAt: lambda call:
                _inspect_at_handler(
                    problem_file, theorem_name, call.tactics, call.command
                ).using(dp.just_compute),
            TryAutomation: lambda call:
                _try_automation_handler(
                    problem_file, theorem_name, call.tactics
                ).using(dp.just_compute),
            TryTactics: lambda call:
                _try_tactics_handler(
                    problem_file, theorem_name,
                    call.tactics, call.candidates,
                ).using(dp.just_compute),
        },
    )
    return script


@dp.ensure_compatible(prove_theorem_ace_triggered)
def prove_theorem_ace_triggered_policy(
    model_name: str,
    temperature: float | None = None,
    max_turns: int | None = None,
    loop: bool = False,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    convert_user_feedback_to_tool: bool = True,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    """`prove_theorem_ace_policy`, verbatim: same model construction,
    same bucket-redirected examples."""
    model = make_model(
        model_name,
        for_tool_calls=True,
        api=api,
        reasoning_effort=reasoning_effort,
        convert_user_feedback_to_tool=convert_user_feedback_to_tool,
    )
    sp = dfs(max_depth=max_turns)
    if loop:
        sp = dp.loop() @ sp
    pp = dp.few_shot(
        model,
        temperature=temperature,
        max_requests=1,
        select_examples=_ace_examples(),
        tag_user_feedback_messages=(api == "responses"),
    )
    return sp & pp


@dataclass
class RepairAddition:
    """A repair bullet with its trigger (`WriteRepairBullets`)."""

    section: str
    content: str
    references: list[str] = field(default_factory=list[str])
    classes: list[str] = field(default_factory=list[str])
    names: list[str] = field(default_factory=list[str])
    patterns: list[str] = field(default_factory=list[str])
    goal_patterns: list[str] = field(default_factory=list[str])
    rationale: str = ""

    def as_add_op(self) -> AddOp:
        return AddOp(
            type="ADD",
            section=self.section,
            content=self.content,
            references=list(self.references),
        )


@dataclass
class RepairBullets:
    reasoning: str
    additions: list[RepairAddition]


@dataclass
class WriteRepairBullets(dp.Query[RepairBullets]):
    """
    One-shot writer of repair bullets (`ace_repairs`): sees the
    existing playbook, the ranked digest of verifier-accepted repairs
    on the adaptation pool, the taxonomy and the prover's own
    pitfalls; answers with at most `max_new_bullets` bullets, each
    with `references` (for the grounding gate) and a trigger.
    """

    playbook: str
    repairs: str
    classes: str
    known_guidance: str = ""
    max_new_bullets: int = 8
    max_patterns: int = 3

    __parser__ = dp.last_code_block.yaml


@strategy
def write_repair_bullets(
    playbook: str,
    repairs: str,
    classes: str,
    known_guidance: str = "",
    max_new_bullets: int = 8,
    max_patterns: int = 3,
) -> Strategy[Branch, dp.PromptingPolicy, RepairBullets]:
    bullets = yield from dp.branch(
        WriteRepairBullets(
            playbook, repairs, classes, known_guidance, max_new_bullets,
            max_patterns,
        ).using(dp.ambient_pp)
    )
    return bullets


@dataclass
class AssignTriggers(dp.Query[TriggerAssignment]):
    """
    One-shot assignment of a trigger to every bullet of a frozen
    playbook (`ace_triggers`): which failure classes, unknown names
    and error/tactic patterns should summon it. Sees the playbook with
    ids, the taxonomy it may use and the pool's failure digest (the
    names Rocq did not know, the failing tactic heads). Run once per
    playbook, by a stronger model than the generator if wanted; the
    answer is validated and frozen by
    `experiments/ace/ace_triggers_experiment.py`.
    """

    playbook: str
    classes: str
    evidence: str
    max_patterns: int = 3

    __parser__ = dp.last_code_block.yaml


@strategy
def assign_triggers(
    playbook: str,
    classes: str,
    evidence: str,
    max_patterns: int = 3,
) -> Strategy[Branch, dp.PromptingPolicy, TriggerAssignment]:
    assignment = yield from dp.branch(
        AssignTriggers(playbook, classes, evidence, max_patterns).using(
            dp.ambient_pp
        )
    )
    return assignment


#####
##### Shared one-shot policy for Reflector and Curator
#####


def _one_shot_policy(
    model_name: str,
    temperature: float | None,
    api: ApiType,
    reasoning_effort: OmphalosReasoningEffort | None,
    max_requests: int,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    """
    dfs over a single query; `max_requests > 1` gives the model fresh
    attempts when a reply fails to parse as the target YAML schema
    (parse errors are logged and retried by `few_shot`, not raised).
    """
    model = make_model(
        model_name,
        api=api,
        reasoning_effort=reasoning_effort,
    )
    return dfs() & dp.few_shot(
        model,
        temperature=temperature,
        max_requests=max_requests,
        tag_user_feedback_messages=(api == "responses"),
    )


@dp.ensure_compatible(reflect_on_trajectory)
def reflect_on_trajectory_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    max_requests: int = 3,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    return _one_shot_policy(
        model_name, temperature, api, reasoning_effort, max_requests
    )


@dp.ensure_compatible(curate_playbook)
def curate_playbook_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    max_requests: int = 3,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    return _one_shot_policy(
        model_name, temperature, api, reasoning_effort, max_requests
    )


@dp.ensure_compatible(curate_from_trajectory)
def curate_from_trajectory_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    max_requests: int = 3,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    return _one_shot_policy(
        model_name, temperature, api, reasoning_effort, max_requests
    )


@dp.ensure_compatible(aggregate_curation_deltas)
def aggregate_curation_deltas_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    max_requests: int = 3,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    return _one_shot_policy(
        model_name, temperature, api, reasoning_effort, max_requests
    )


@dp.ensure_compatible(rewrite_playbook)
def rewrite_playbook_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    max_requests: int = 3,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    return _one_shot_policy(
        model_name, temperature, api, reasoning_effort, max_requests
    )


@dp.ensure_compatible(audit_playbook)
def audit_playbook_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    max_requests: int = 3,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    return _one_shot_policy(
        model_name, temperature, api, reasoning_effort, max_requests
    )


@dp.ensure_compatible(assign_triggers)
def assign_triggers_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    max_requests: int = 3,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    return _one_shot_policy(
        model_name, temperature, api, reasoning_effort, max_requests
    )


@dp.ensure_compatible(write_repair_bullets)
def write_repair_bullets_policy(
    model_name: str,
    temperature: float | None = None,
    api: ApiType = "responses",
    reasoning_effort: OmphalosReasoningEffort | None = None,
    max_requests: int = 3,
) -> dp.Policy[Branch, dp.PromptingPolicy]:
    return _one_shot_policy(
        model_name, temperature, api, reasoning_effort, max_requests
    )


@dp.ensure_compatible(ground_references)
def ground_references_policy() -> dp.Policy[Compute, object]:
    """
    The grounder has no LLM: `Compute` is its only effect, eliminated
    by performing the computations (`dp.just_compute`). The inner
    policy is never consulted.
    """
    return dp.just_compute(cast(object, None))
