"""
Pytanque bridge and miniF2F problem parser used by the Delphyne baseline.

Pure Python: no Delphyne imports, so this module can be called from
`dp.compute(...)` boundaries without dragging strategy state in.
"""

from __future__ import annotations

from runtime.paths import OMPHALOS_ROOT

import copy
import os
import re
from collections import OrderedDict
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field, replace as dc_replace
from pathlib import Path
from typing import Literal

from pytanque import PetanqueError, Pytanque, State

import runtime.rocq_server as rocq_server
from runtime.rocq_server import MANAGER, BoundedPytanque, ReplyTooLarge


# Extra `Require Import` lines we silently prepend before invoking
# pytanque, so the agent has access to the standard automation tactics
# (`lia`, `lra`, `nra`, `nia`, `psatz`, `field`). The benchmark .v files
# themselves are left untouched.
DEFAULT_EXTRA_IMPORTS: tuple[str, ...] = (
    "Require Import Lia.",
    "Require Import Lra.",
    "Require Import Psatz.",
    "Require Import Field.",
)


# Soft cap on Rocq query output (Search/Print/Check/About). Search can
# return many KB of lemmas for broad patterns; we truncate and let the
# agent retry with a tighter query.
DEFAULT_QUERY_OUTPUT_CHAR_CAP = 4000


# Anchor for relative problem paths in `.exec.yaml` / experiment configs.
# Using this module's own location means the strategy resolves paths
# the same way regardless of cwd (CLI from anywhere, VSCode extension,
# experiment launcher, etc.).
_WORKSPACE_ROOT = OMPHALOS_ROOT

# Rocq's micromega tactics (lia/nia/nra/psatz) write `.lia.cache` etc.
# into the *cwd of the Rocq process*; every Rocq process is spawned
# with this cwd (see `rocq_server`).
_ROCQ_CACHE_DIR = rocq_server.ROCQ_CACHE_DIR


@contextmanager
def _pytanque_session(abs_file: str) -> Generator[Pytanque]:
    """
    A petanque session for `abs_file` (the augmented path). Transport
    and server lifecycle — private warm `pet-server` per process with
    deadlines, reply caps, memory bounds and recycling, or the archived
    STDIO transport under `OMPHALOS_PET_MODE=stdio` — live in
    `rocq_server`; this module only asks questions through the client.
    """
    with MANAGER.session(abs_file) as client:
        yield client


#####
##### Prefix-state memo
#####

# Rocq proof states are functional and stay valid in the server for
# its whole life, so the state reached by a tactic prefix can be reused
# by the next tool call that replays the same prefix (every tool call
# does: the agent's script grows turn by turn). Keyed by the server
# generation, so a recycle invalidates every entry implicitly. Only
# verified successes are memoised — verdicts are unchanged; what is
# saved is the re-execution (and re-payment of slow tactics).
_PREFIX_MEMO: OrderedDict[tuple[int, str, str, tuple[str, ...]], State] = (
    OrderedDict()
)
PREFIX_MEMO_CAP = 1024
_MEMO_LAST_GEN: list[int] = [-1]


def _memo_purge_stale() -> None:
    """
    Drop entries of dead server generations. A recycle already
    invalidates them implicitly (the generation is in the key), but
    without the purge they kept occupying the LRU and evicting live
    entries — one archived process reached generation 75 against a
    1024-entry cap. Runs only when the generation actually changed.
    """
    gen = MANAGER.generation
    if gen == _MEMO_LAST_GEN[0]:
        return
    _MEMO_LAST_GEN[0] = gen
    for key in [k for k in _PREFIX_MEMO if k[0] != gen]:
        del _PREFIX_MEMO[key]


def _memo_enabled(client: Pytanque) -> bool:
    # STDIO sessions die with their process: nothing to reuse.
    return isinstance(client, BoundedPytanque)


def _memo_key(
    abs_file: str, theorem_name: str, prefix: tuple[str, ...]
) -> tuple[int, str, str, tuple[str, ...]]:
    return (MANAGER.generation, abs_file, theorem_name, prefix)


def _memo_put(
    abs_file: str, theorem_name: str, prefix: tuple[str, ...], state: State
) -> None:
    _memo_purge_stale()
    key = _memo_key(abs_file, theorem_name, prefix)
    _PREFIX_MEMO[key] = state
    _PREFIX_MEMO.move_to_end(key)
    while len(_PREFIX_MEMO) > PREFIX_MEMO_CAP:
        _PREFIX_MEMO.popitem(last=False)


def _memo_longest_prefix(
    abs_file: str, theorem_name: str, tactics: list[str]
) -> tuple[int, State | None]:
    """`(k, state)` for the longest memoised prefix `tactics[:k]`, else `(0, None)`."""
    for k in range(len(tactics), -1, -1):
        key = _memo_key(abs_file, theorem_name, tuple(tactics[:k]))
        state = _PREFIX_MEMO.get(key)
        if state is not None:
            _PREFIX_MEMO.move_to_end(key)
            return k, state
    return 0, None


def prefix_memo_size() -> int:
    """Entries currently memoised (for tests and the timing harness)."""
    return len(_PREFIX_MEMO)


@dataclass
class _Replay:
    """
    Outcome of opening a theorem and replaying a tactic prefix — the
    shared core of `_replay_prefix` (previews) and `_check_against`
    (verification), which used to duplicate the loop.

    Exactly one of these holds: `start_error` (the session could not be
    opened), `failing_index` (a tactic was rejected; `state` is the last
    good state), `finished_at` (previews only: the proof closed after
    that tactic index), or none of them (`state` is the state after the
    whole prefix).
    """

    state: State | None
    succeeded: list[str]
    start_error: str | None = None
    failing_index: int | None = None
    failing_tactic: str | None = None
    error_message: str | None = None
    finished_at: int | None = None


def _open_and_replay(
    client: Pytanque,
    abs_file: str,
    theorem_name: str,
    tactics: list[str],
    *,
    stop_when_finished: bool,
    timeout: int,
) -> _Replay:
    """
    Open `theorem_name` in `abs_file` and run `tactics` in order from
    the longest memoised prefix. With `stop_when_finished` (previews),
    stop as soon as the proof is closed — verification instead runs
    every tactic and lets Rocq reject tactics after the goal is gone,
    exactly as before.
    """
    memo = _memo_enabled(client)
    k, state = (
        _memo_longest_prefix(abs_file, theorem_name, tactics)
        if memo
        else (0, None)
    )
    if state is None:
        try:
            state = client.start(abs_file, theorem_name)
        except PetanqueError as e:
            return _Replay(state=None, succeeded=[], start_error=str(e))
        if memo:
            _memo_put(abs_file, theorem_name, (), state)
        k = 0
    succeeded = list(tactics[:k])
    if stop_when_finished and k > 0 and state.proof_finished:
        return _Replay(state=state, succeeded=succeeded, finished_at=k - 1)
    for i in range(k, len(tactics)):
        tac = tactics[i]
        try:
            state = _run_guarded(client, state, tac, timeout)
        except PetanqueError as e:
            return _Replay(
                state=state,
                succeeded=succeeded,
                failing_index=i,
                failing_tactic=tac,
                error_message=str(e),
            )
        succeeded.append(tac)
        if memo:
            _memo_put(abs_file, theorem_name, tuple(tactics[: i + 1]), state)
        if stop_when_finished and state.proof_finished:
            return _Replay(state=state, succeeded=succeeded, finished_at=i)
    return _Replay(state=state, succeeded=succeeded)


def _resolve(path: str) -> str:
    """Resolve a problem-file path against the omphalos workspace root."""
    p = Path(path)
    if not p.is_absolute():
        p = _WORKSPACE_ROOT / p
    return str(p.resolve())


@dataclass
class ProblemSpec:
    file: str
    theorem_name: str
    theorem_statement: str
    informal_statement: str
    informal_proof: str
    imports: str
    definitions: str = ""
    """
    The declarations the problem file makes *before* its theorem, other
    than imports and scope openings — `Definition`, `Fixpoint`,
    `Notation`, `Module`, ... — exactly as written, comments stripped.
    Empty for the ~90% of miniF2F files that have none, and empty
    whenever `parse_problem` is called with `show_definitions=False`
    (the historical prompt). Defaulted so the materialised demos, whose
    `spec` mappings predate the field, keep parsing.
    """


@dataclass
class Feedback:
    """
    Result of verifying a proof script (see `check`).

    `probe` is only populated by the automation-assisted verifier
    (`check(..., probe_automation=True)`): for each remaining goal, the
    first battery tactic that closes it, or `None` if the battery
    cannot. `auto_finished=True` marks a success where the verifier
    itself closed the remaining goals with battery tactics —
    `proof_so_far` then holds the complete assembled proof.
    """

    success: bool
    failing_index: int | None = None
    failing_tactic: str | None = None
    error_message: str | None = None
    remaining_goals: list[str] = field(default_factory=list[str])
    proof_so_far: list[str] = field(default_factory=list[str])
    finished: bool = False
    probe: list[str | None] | None = None
    auto_finished: bool = False


_HEADER_RE = re.compile(r"\(\*(.*?)\*\)", re.DOTALL)
_THEOREM_RE = re.compile(
    r"^(?:Theorem|Lemma|Example|Corollary)\s+(\w+)\s*([\s\S]*?)\.\s*$",
    re.MULTILINE,
)
_IMPORT_LINE_RE = re.compile(
    r"^\s*(?:From\s+\S+\s+)?(?:Require\s+(?:Import|Export)|Open\s+Scope|Import)\b.*?\.\s*$",
    re.MULTILINE,
)


def _strip_comments(text: str) -> str:
    """Remove `(* ... *)` comments, honouring Rocq's nesting."""
    out: list[str] = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("(*", i):
            depth += 1
            i += 2
        elif depth and text.startswith("*)", i):
            depth -= 1
            i += 2
        else:
            if not depth:
                out.append(text[i])
            i += 1
    return "".join(out)


def _preamble_definitions(preamble: str) -> str:
    """
    Everything a problem file declares before its theorem, minus the
    import/scope lines that `ProblemSpec.imports` already carries.

    Deliberately *not* an allow-list of declaration keywords: an earlier
    version matched `Definition|Fixpoint|Notation|...` and silently
    dropped `Module NS := FSetWeakList.Make(Nat_as_OT).` on
    `amc12a_2003_p23`. Whatever precedes the theorem is in scope when
    the proof is checked, so the model should see all of it.
    """
    text = _IMPORT_LINE_RE.sub("", _strip_comments(preamble))
    paragraphs = [
        "\n".join(line.rstrip() for line in chunk.splitlines()).strip("\n")
        for chunk in re.split(r"\n\s*\n", text)
    ]
    return "\n\n".join(p for p in paragraphs if p.strip())


def _extract_section(header: str, label: str) -> str:
    pattern = re.compile(
        rf"{label}\s*:\s*\n(.*?)(?=\n\s*(?:Informal\s+(?:statement|proof)\s*:|Source\s*:|Split\s*:|$))",
        re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(header)
    if not m:
        return ""
    return m.group(1).strip()


_PARSE_MEMO: dict[tuple[str, bool, int, int], ProblemSpec] = {}
"""Keyed by `(resolved path, show_definitions, size, mtime_ns)`.
`parse_problem` runs in the strategy body, so every strategy *replay*
re-reads and re-regexes the file; the benchmark files are frozen, so
the parse is cached on the file's stat. Entries hold private copies
and hits return fresh copies (`ProblemSpec` fields are all strings)."""


def parse_problem(path: str, show_definitions: bool = False) -> ProblemSpec:
    """
    Parse a miniF2F problem file into a `ProblemSpec`.

    `show_definitions` fills `ProblemSpec.definitions` with the file's
    pre-theorem declarations (see `_preamble_definitions`), which the
    prompt template then renders in its own section. It defaults to
    `False` — the historical behaviour, under which 42 of the 488
    miniF2F files asked for a proof about a symbol the model was never
    shown — because the rendered prompt keys every LLM cache: the frozen
    strategies keep the default and the new pipelines turn it on.
    Verification never depended on it: pytanque loads the real file.
    """
    path = _resolve(path)
    try:
        st = Path(path).stat()
        memo_key = (path, show_definitions, st.st_size, st.st_mtime_ns)
    except OSError:
        memo_key = None
    if memo_key is not None:
        hit = _PARSE_MEMO.get(memo_key)
        if hit is not None:
            return dc_replace(hit)
    spec = _parse_problem_uncached(path, show_definitions)
    if memo_key is not None:
        _PARSE_MEMO[memo_key] = dc_replace(spec)
    return spec


def _parse_problem_uncached(path: str, show_definitions: bool) -> ProblemSpec:
    text = Path(path).read_text()

    header = ""
    header_match = _HEADER_RE.search(text)
    if header_match:
        header = header_match.group(1)

    informal_statement = _extract_section(header, "Informal statement")
    informal_proof = _extract_section(header, "Informal proof")

    thm_match = _THEOREM_RE.search(text)
    if not thm_match:
        raise ValueError(f"No Theorem/Lemma found in {path}")
    theorem_name = thm_match.group(1)
    theorem_statement = thm_match.group(2).strip()

    imports = "\n".join(
        m.group(0).strip() for m in _IMPORT_LINE_RE.finditer(text)
    )
    definitions = ""
    if show_definitions:
        # Only the preamble: a declaration appearing after the theorem
        # belongs to a later theorem in the same file, not to this one.
        definitions = _preamble_definitions(text[: thm_match.start()])

    return ProblemSpec(
        file=path,
        theorem_name=theorem_name,
        theorem_statement=theorem_statement,
        informal_statement=informal_statement,
        informal_proof=informal_proof,
        imports=imports,
        definitions=definitions,
    )


_FENCE_RE = re.compile(r"```(?:rocq|coq)?\s*\n?(.*?)```", re.DOTALL)


def split_into_tactics(script: str) -> list[str]:
    """
    Turn an LLM-emitted proof script into a list of tactic strings (each
    ending in `.`). Defensive against:
      - fenced code blocks (```rocq ... ```)
      - a leading `Proof.` / trailing `Qed.` / `Admitted.` / `Defined.`
      - blank lines and a trailing unterminated fragment.

    Sentences may span several lines (e.g. a long `assert (H : ...)`
    wrapped by the LLM): lines are accumulated until one ends with `.`,
    then flushed as a single tactic. Naive line-wise splitting used to
    drop the head of wrapped sentences and keep dangling fragments,
    producing spurious syntax errors.
    """
    body = script
    fence_match = _FENCE_RE.search(body)
    if fence_match:
        body = fence_match.group(1)

    tactics: list[str] = []
    buffer: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if not buffer and line in {
            "Proof.",
            "Qed.",
            "Admitted.",
            "Defined.",
            "Abort.",
        }:
            continue
        buffer.append(line)
        # `}` closes a focus block and is a complete sentence on its
        # own, so it also terminates the current chunk.
        if line.endswith(".") or line.endswith("}"):
            tactics.append(" ".join(buffer))
            buffer = []
    # A trailing buffer that never reached a `.` is prose or a
    # truncated sentence; drop it (mirrors the old prose handling).
    return tactics


GOALS_OVERFLOW_MARKER = (
    "<goal state too large to transfer: the prover's reply exceeded the "
    "size cap and the server was restarted; simplify the proof state>"
)


def _safe_goals(client: Pytanque, state: State) -> list[str]:
    import runtime.tool_budget as tb

    try:
        goals = client.goals(state)
    except ReplyTooLarge:
        if tb.CURRENT.get() is not None:
            raise
        # A silent `[]` would read as "no goals"; say what happened.
        return [GOALS_OVERFLOW_MARKER]
    except Exception:
        if tb.CURRENT.get() is not None:
            raise
        return []
    out: list[str] = []
    for g in goals or []:
        try:
            # Pytanque goals carry a pretty-printed form in `pp`;
            # the raw dataclass repr is noisy and duplicates it.
            out.append(g.pp if g.pp else str(g))
        except Exception:
            out.append("<unprintable goal>")
    return out


@contextmanager
def _augmented_file(
    file: str, extra_imports: tuple[str, ...]
) -> Generator[str]:
    """
    Yield the path pytanque should be pointed at: the stable copy of
    `file` with `extra_imports` prepended (`rocq_server.augmented_path`
    — outside the miniF2F `_CoqProject` whitelist, byte-identical to
    the temp copies of the archived runs, and stable so the warm server
    reuses its document), or `file` itself if there is nothing to
    prepend.
    """
    yield rocq_server.augmented_path(file, extra_imports)


@dataclass(frozen=True)
class GoalCaps:
    """
    Runaway-goal guard (a *treatment*, pre-registered separately; the
    default everywhere is `None` = the archived behaviour). A failed
    script can leave hundreds of open goals (`repeat constructor` on a
    long `NoDup` left 1128 in one validationX cell); the battery then
    probes every goal (17 tactics × up to 4 s each) and the feedback
    renders every goal (82 KB in one message). With caps, the battery
    probes the first `probe` goals, the feedback lists the first
    `render` goals (each cut at `render_chars` characters) followed by a
    marker line saying how many were hidden and how many were probed.
    Encoded inside the existing `Feedback` fields, so the cached output
    shape is unchanged.
    """

    probe: int = 24
    render: int = 12
    render_chars: int = 2000


GOALS_TRUNCATED_MARKER = (
    "... {hidden} more goal(s) not shown ({shown} of {total} listed); the "
    "automation battery probed the first {probed}. Too many open goals: "
    "prefer tactics that close or merge goals before proceeding."
)


_CHECK_MEMO: OrderedDict[
    tuple[str, str, tuple[str, ...], tuple[str, ...], bool, GoalCaps | None],
    Feedback,
] = OrderedDict()
CHECK_MEMO_CAP = 512


def _check_memo_enabled() -> bool:
    """
    The in-process memo over full verification results, on unless
    `OMPHALOS_CHECK_MEMO=0`. The compute cache keys entries by
    occurrence index, so an agent repeating a byte-identical script
    re-pays the whole verification — 9.4% of the 74.8k archived compute
    calls are such repeats (`tools/analysis/compute_repeat_audit.py`), including
    failing tactics that re-pay `PROOF_TACTIC_TIMEOUT` each time.
    Verdicts are deterministic (the audit found divergence only on
    transport/resource failures, 7 groups in 74.8k calls), and results
    are stored only for calls the transport survived untouched.
    """
    return os.environ.get("OMPHALOS_CHECK_MEMO", "1") != "0"


def check_memo_size() -> int:
    """Entries currently memoised (for tests and the timing harness)."""
    return len(_CHECK_MEMO)


def clear_check_memo() -> None:
    """
    Empty the check-result memo. For tests and harnesses whose point
    is *re-execution* (transport parity, cold-run agreement): a repeat
    served from the memo would make them vacuous.
    """
    _CHECK_MEMO.clear()


def check(
    file: str,
    theorem_name: str,
    tactics: list[str],
    extra_imports: tuple[str, ...] = DEFAULT_EXTRA_IMPORTS,
    probe_automation: bool = False,
    goal_caps: GoalCaps | None = None,
) -> Feedback:
    """
    Open a Pytanque session, replay `tactics` against the theorem,
    attempt a final `Qed.`, and return structured feedback.

    One session per call: keeps lifetime obvious and side-effect free.

    If `extra_imports` is non-empty, pytanque is pointed at a stable
    copy of `file` outside the miniF2F tree with those imports
    prepended (the original is not modified).

    With `probe_automation=True`, verification is *automation-assisted*:
    whenever the script fails or leaves goals open, each remaining goal
    is probed with `AUTOMATION_BATTERY` (results land in
    `Feedback.probe`), and if every goal closes, the verifier finishes
    the proof itself — returning success with `auto_finished=True` and
    the complete assembled script in `proof_so_far`.

    `goal_caps` (treatment, off by default — see `GoalCaps`) bounds how
    many goals the battery probes and how many are reported.

    Repeated byte-identical calls are answered from an in-process memo
    (`_check_memo_enabled`): the verdict for a given (file, theorem,
    script) does not depend on the server, and only results from calls
    with no transport incident (no exception, no recycle, no poisoned
    session, no start failure) are stored.
    """
    file = _resolve(file)
    # A cached complete operation has different resource semantics. Prefix
    # memo remains valid; whole-result memo is disabled for bounded calls.
    import runtime.tool_budget as tb

    memo = _check_memo_enabled() and tb.CURRENT.get() is None
    key = (
        file,
        theorem_name,
        tuple(tactics),
        extra_imports,
        probe_automation,
        goal_caps,
    )
    if memo:
        hit = _CHECK_MEMO.get(key)
        if hit is not None:
            _CHECK_MEMO.move_to_end(key)
            return copy.deepcopy(hit)
    gen_before = MANAGER.generation
    with _augmented_file(file, extra_imports) as run_file:
        fb = _check_against(
            run_file, theorem_name, tactics, probe_automation, goal_caps
        )
    if (
        memo
        and MANAGER.generation == gen_before
        and not (
            fb.error_message is not None
            and (
                "Rocq transport failure" in fb.error_message
                or fb.error_message.startswith("Failed to start session")
            )
        )
    ):
        _CHECK_MEMO[key] = copy.deepcopy(fb)
        _CHECK_MEMO.move_to_end(key)
        while len(_CHECK_MEMO) > CHECK_MEMO_CAP:
            _CHECK_MEMO.popitem(last=False)
    return fb


def check_assisted(
    file: str,
    theorem_name: str,
    tactics: list[str],
    goal_caps: GoalCaps | None = None,
) -> Feedback:
    """
    `check` with automation-assisted verification enabled. Kept as a
    named top-level entry point so strategies can pass it to
    `dp.compute(...)` directly. Strategies pass `goal_caps` only when
    set, so the compute cache keys of archived runs are untouched.
    """
    return check(
        file, theorem_name, tactics, probe_automation=True, goal_caps=goal_caps
    )


def inspect_at(
    file: str,
    theorem_name: str,
    tactics_script: str,
    command: str = "",
    extra_imports: tuple[str, ...] = DEFAULT_EXTRA_IMPORTS,
    char_cap: int = DEFAULT_QUERY_OUTPUT_CHAR_CAP,
) -> str:
    """
    Replay a tactic prefix from the initial proof state of
    `theorem_name` in `file` (without committing), then run an optional
    introspection command (`Search ...`, `Check ...`, ...) *at the
    resulting state* and return a human-readable report.

    Rocq proof state is functional: `client.run(state, tac)` returns a
    new state and leaves the original valid, so this is a true preview.

    - empty `tactics_script` → inspect the theorem's initial state
      (equivalent to the plain `query` bridge);
    - empty `command` → just report the goal state after the prefix;
    - the prefix closes the goal → "PROOF FINISHED" report;
    - a prefix tactic fails → the failing tactic, error message, the
      tactics that succeeded, and the goals at the point of failure.

    Crucially, `Search` results at a non-initial state are filtered by
    the *current* context — after `intros`/`induction`, hypotheses
    (including the induction hypothesis) are in scope, so lemma
    discovery matches the actual stuck subgoal.

    Pytanque errors are caught and rendered as the tool result so the
    agent can self-correct on its next turn instead of crashing.
    """
    file = _resolve(file)
    tactics = split_into_tactics(tactics_script)
    command = command.strip()
    if not tactics and not command:
        return (
            "Nothing to do: both `tactics` and `command` are empty. "
            "Pass a tactic prefix, an introspection command, or both."
        )

    with _augmented_file(file, extra_imports) as run_file:
        return _inspect_against(
            run_file, theorem_name, tactics, command, char_cap
        )


# Cheap closing tactics tried on each remaining subgoal by
# `try_automation` and by the automation-assisted verifier
# (`check(..., probe_automation=True)`). Ordered cheap-and-common
# first. Each entry is a single Rocq sentence.
AUTOMATION_BATTERY: tuple[str, ...] = (
    "assumption.",
    "reflexivity.",
    "easy.",
    "lia.",
    "simpl; lia.",
    "nia.",
    "simpl; nia.",
    "lra.",
    "nra.",
    "field_simplify_eq; nra.",
    "ring.",
    "field.",
    "congruence.",
    "auto with arith.",
    "auto with zarith.",
    "intuition lia.",
    "firstorder.",
)

# Per-tactic cap for battery probes, in seconds. `nia` / `firstorder`
# can diverge on hard goals; a probe that needs more time than this is
# not "cheap automation" anymore. Must be an int: pytanque forwards it
# to Rocq's `Timeout`, which rejects non-integer literals.
AUTOMATION_TACTIC_TIMEOUT = 4

# Per-sentence cap for *replaying* scripts (verification, prefix
# replay, introspection commands), in seconds. Generous on purpose:
# legitimate proposal tactics may be slow, but without any cap a
# single diverging tactic in a sampled proposal parks the pet process
# forever (observed 2026-07-22: one experiment config spun Rocq at
# 100% CPU for 13+ hours; again 2026-08-25 on a bullet-led sentence,
# 40 min before the watchdog). pytanque only wraps `Timeout` around
# sentences that end with `.` and do not start with a bullet, so
# `_run_guarded` splits the leading bullets/braces off — they are pure
# goal-focusing steps that cannot diverge — and runs the remainder
# under the wrapper. Model-authored sentences must go through
# `_run_guarded`, never bare `client.run`.
PROOF_TACTIC_TIMEOUT = 120

_FOCUS_RE = re.compile(r"^\s*([-+*]+|\{|\})\s*(.*)$", re.DOTALL)


def _split_focus(sentence: str) -> tuple[list[str], str]:
    """
    `([focus tokens], remainder)` — the leading bullet/brace tokens of
    a sentence, each a complete Rocq proof step of its own, and what
    is left (possibly empty). `"- { nia. }"` -> `(["-", "{"], "nia. }")`;
    the trailing `}` stays with the remainder, where it is harmless
    (closing a brace cannot diverge).
    """
    focus: list[str] = []
    rest = sentence
    while True:
        m = _FOCUS_RE.match(rest)
        if (
            m is None
            or not m.group(2).strip()
            and m.group(1) not in ("{", "}")
        ):
            break
        if m.group(1) == "}":
            break
        focus.append(m.group(1))
        rest = m.group(2)
        if not rest.strip():
            break
    return focus, rest


def _run_guarded(
    client: "Pytanque", state: "State", sentence: str, timeout: int
) -> "State":
    """
    `client.run` with the timeout actually enforced.

    pytanque turns `timeout=` into a `Timeout {t} {cmd}` wrapper only
    for sentences that end with `.` and do not open with a bullet, so
    a sampled `- nia.` used to run unguarded (and could spin Rocq
    forever). Here the focusing prefix runs on its own — instant by
    construction — and the remaining tactic gets the wrapper.
    """
    focus, rest = _split_focus(sentence)
    if not focus:
        return client.run(state, sentence, timeout=timeout)
    for token in focus:
        state = client.run(state, token, timeout=timeout)
    if rest.strip():
        state = client.run(state, rest, timeout=timeout)
    return state


# Cap on the number of candidates one `try_tactics` call evaluates
# (parity with the 20-tactic batch limit of comparable stepping APIs);
# extras are reported as dropped, not silently ignored.
MAX_TRY_TACTICS_CANDIDATES = 20

# `try_tactics` reports on up to `MAX_TRY_TACTICS_CANDIDATES` outcomes,
# so it gets a larger overall cap than single-command queries, plus a
# per-candidate cap on the goal excerpt so a few verbose goals cannot
# crowd out the other candidates' results.
TRY_TACTICS_OUTPUT_CHAR_CAP = 6000
TRY_TACTICS_GOAL_CHAR_CAP = 500


def try_automation(
    file: str,
    theorem_name: str,
    tactics_script: str,
    extra_imports: tuple[str, ...] = DEFAULT_EXTRA_IMPORTS,
    char_cap: int = DEFAULT_QUERY_OUTPUT_CHAR_CAP,
    tactic_timeout: int = AUTOMATION_TACTIC_TIMEOUT,
) -> str:
    """
    Replay a tactic prefix from the initial proof state of
    `theorem_name` in `file`, then try a battery of cheap closing
    tactics (`AUTOMATION_BATTERY`) on *each* remaining subgoal and
    report which subgoal closes with what.

    One tool call buys up to `len(goals) * len(battery)` Rocq attempts
    — this exploits cheap verifier compute instead of LLM turns. Each
    battery probe runs under `tactic_timeout` so a diverging `nia` /
    `firstorder` cannot stall the session.

    An empty `tactics_script` probes the initial goal directly. A
    failing prefix tactic produces the same failure report as
    `inspect_at`.
    """
    file = _resolve(file)
    tactics = split_into_tactics(tactics_script)

    with _augmented_file(file, extra_imports) as run_file:
        return _automation_against(
            run_file, theorem_name, tactics, char_cap, tactic_timeout
        )


def try_tactics(
    file: str,
    theorem_name: str,
    tactics_script: str,
    candidates: list[str],
    extra_imports: tuple[str, ...] = DEFAULT_EXTRA_IMPORTS,
    char_cap: int = TRY_TACTICS_OUTPUT_CHAR_CAP,
    tactic_timeout: int = AUTOMATION_TACTIC_TIMEOUT,
) -> str:
    """
    Replay a tactic prefix from the initial proof state of
    `theorem_name` in `file` (without committing), then evaluate each
    of `candidates` independently against that same held state and
    report the per-candidate outcome.

    This is the model-directed counterpart of `try_automation`: instead
    of the fixed closing battery, the caller supplies the tactics to
    try — alternative structural openers, competing rewrites, asserts.
    Proof state is functional (`client.run` leaves its input state
    valid), so the prefix is replayed once and every candidate starts
    from the identical state; nothing is ever committed.

    Semantics per candidate:
      - split into sentences with `split_into_tactics`, so a candidate
        may be a short *sequence* ("intros n. induction n.");
      - each sentence runs under `tactic_timeout` (int — see
        `AUTOMATION_TACTIC_TIMEOUT`); sentences act on the whole proof
        state, so goal selectors ("2: lia.") are legal candidates;
      - exact duplicates and empty candidates are skipped without
        spending Rocq calls; at most `MAX_TRY_TACTICS_CANDIDATES` are
        evaluated (extras are reported as dropped).

    A failing prefix produces the same failure report as `inspect_at`;
    a prefix that already closes the proof short-circuits to the
    "PROOF FINISHED" report.
    """
    file = _resolve(file)
    prefix = split_into_tactics(tactics_script)
    if not any(c.strip() for c in candidates):
        return (
            "No candidates to try: `candidates` is empty. Pass a list "
            "of candidate tactics (each sentence ending with `.`)."
        )

    with _augmented_file(file, extra_imports) as run_file:
        return _try_tactics_against(
            run_file,
            theorem_name,
            prefix,
            candidates,
            char_cap,
            tactic_timeout,
        )


def query(
    file: str,
    theorem_name: str,
    command: str,
    extra_imports: tuple[str, ...] = DEFAULT_EXTRA_IMPORTS,
    char_cap: int = DEFAULT_QUERY_OUTPUT_CHAR_CAP,
) -> str:
    """
    Run a Rocq introspection command (`Search ...`, `Check ...`,
    `Print ...`, `About ...`, `SearchPattern ...`) against the initial
    proof state of `theorem_name` in `file`, and return the formatted
    feedback as a string.

    Same session lifecycle as `check`: a fresh STDIO pytanque session
    is opened per call and torn down on exit. The original .v file is
    not modified — extra imports are prepended in a temp copy outside
    the miniF2F tree so the agent's search sees lemmas from Lia / Lra
    / Psatz / Field.

    Pytanque errors (bad syntax, etc.) are caught and returned as the
    feedback string, so the agent can self-correct on its next turn
    instead of crashing the strategy.
    """
    file = _resolve(file)
    with _augmented_file(file, extra_imports) as run_file:
        return _query_against(run_file, theorem_name, command, char_cap)


def _replay_prefix(
    client: Pytanque,
    abs_file: str,
    theorem_name: str,
    tactics: list[str],
    char_cap: int,
) -> tuple[State | None, str | None]:
    """
    Open the theorem and replay a tactic prefix. Returns
    `(state, report)` where exactly one of the two is `None`: a
    non-`None` report is a preformatted error / "PROOF FINISHED"
    string that should be returned to the agent as-is.
    """
    r = _open_and_replay(
        client,
        abs_file,
        theorem_name,
        tactics,
        stop_when_finished=True,
        timeout=PROOF_TACTIC_TIMEOUT,
    )
    if r.start_error is not None:
        return None, f"Failed to open session: {r.start_error}"
    if r.failing_index is not None:
        assert r.state is not None
        assert r.failing_tactic is not None and r.error_message is not None
        return None, _format_try_failure(
            failing_index=r.failing_index,
            failing_tactic=r.failing_tactic,
            error_message=r.error_message,
            succeeded=r.succeeded,
            remaining_goals=_safe_goals(client, r.state),
            char_cap=char_cap,
        )
    if r.finished_at is not None:
        return None, _format_try_proof_finished(
            succeeded=r.succeeded,
            leftover=tactics[r.finished_at + 1 :],
        )
    assert r.state is not None
    return r.state, None


def _inspect_against(
    abs_file: str,
    theorem_name: str,
    tactics: list[str],
    command: str,
    char_cap: int,
) -> str:
    """
    Inner implementation of `inspect_at`: replay the prefix, then run
    the introspection command at the resulting state (if provided) and
    report its output together with the goals at that state.
    """
    with _pytanque_session(abs_file) as client:
        state, report = _replay_prefix(
            client, abs_file, theorem_name, tactics, char_cap
        )
        if report is not None:
            return report
        assert state is not None

        if not command:
            return _format_try_success(
                succeeded=tactics,
                remaining_goals=_safe_goals(client, state),
                char_cap=char_cap,
            )

        try:
            after = client.run(state, command, timeout=PROOF_TACTIC_TIMEOUT)
        except PetanqueError as e:
            return f"Rocq rejected the command: {e}"

        parts: list[str] = []
        if tactics:
            parts.append(
                f"Output of `{command}` after your {len(tactics)}-tactic "
                "prefix (hypotheses at that state are in scope):"
            )
        else:
            parts.append(f"Output of `{command}` at the initial state:")
        parts.append("")
        parts.append(_format_feedback(after, char_cap))
        goals = _safe_goals(client, state)
        if tactics and goals:
            parts.append("")
            parts.append(f"Goals at that state ({len(goals)}):")
            for g in goals:
                parts.append("")
                parts.append("```")
                parts.append(str(g).strip())
                parts.append("```")
        text = "\n".join(parts)
        if len(text) > char_cap:
            text = (
                text[:char_cap].rstrip() + "\n[truncated; refine your query]"
            )
        return text


def _automation_against(
    abs_file: str,
    theorem_name: str,
    tactics: list[str],
    char_cap: int,
    tactic_timeout: int,
) -> str:
    """
    Inner implementation of `try_automation`: replay the prefix, then
    probe each remaining subgoal with the automation battery using goal
    selectors (`2: lia.`), recording the first closing tactic per goal.
    """
    with _pytanque_session(abs_file) as client:
        state, report = _replay_prefix(
            client, abs_file, theorem_name, tactics, char_cap
        )
        if report is not None:
            return report
        assert state is not None

        goals = _safe_goals(client, state)
        n = len(goals)
        if n == 0:
            return (
                "No goals remain after your prefix, but the proof is "
                "not marked finished — submit the prefix and let the "
                "verifier attempt `Qed.`."
            )

        closers = _probe_goals(client, state, n, tactic_timeout)
        return _format_automation_report(tactics, goals, closers, char_cap)


@dataclass
class _CandidateOutcome:
    """Outcome of evaluating one `try_tactics` candidate."""

    candidate: str
    status: Literal["finished", "applied", "error", "skipped"]
    detail: str = ""  # Rocq error / skip reason
    goals_after: list[str] = field(default_factory=list[str])


def _try_tactics_against(
    abs_file: str,
    theorem_name: str,
    prefix: list[str],
    candidates: list[str],
    char_cap: int,
    tactic_timeout: int,
) -> str:
    """
    Inner implementation of `try_tactics`: replay the prefix once, then
    run every candidate off that one held state (pytanque states are
    functional, so candidates never see each other's effects) and
    collect a `_CandidateOutcome` per candidate.
    """
    with _pytanque_session(abs_file) as client:
        state, report = _replay_prefix(
            client, abs_file, theorem_name, prefix, char_cap
        )
        if report is not None:
            return report
        assert state is not None

        base_goals = _safe_goals(client, state)
        n = len(base_goals)
        if n == 0:
            return (
                "No goals remain after your prefix, but the proof is "
                "not marked finished — submit the prefix and let the "
                "verifier attempt `Qed.`."
            )

        kept = candidates[:MAX_TRY_TACTICS_CANDIDATES]
        dropped = len(candidates) - len(kept)
        seen: dict[str, int] = {}
        results: list[_CandidateOutcome] = []
        for cand in kept:
            key = cand.strip()
            if key in seen:
                results.append(
                    _CandidateOutcome(
                        candidate=cand,
                        status="skipped",
                        detail=f"duplicate of candidate #{seen[key]}",
                    )
                )
                continue
            seen[key] = len(results) + 1

            sentences = split_into_tactics(cand)
            if not sentences:
                results.append(
                    _CandidateOutcome(
                        candidate=cand,
                        status="skipped",
                        detail="no complete Rocq sentence (missing the "
                        "final `.`?)",
                    )
                )
                continue

            results.append(
                _run_candidate(client, state, cand, sentences, tactic_timeout)
            )

        return _format_try_tactics_report(
            prefix, n, results, dropped, char_cap
        )


def _run_candidate(
    client: Pytanque,
    state: State,
    candidate: str,
    sentences: list[str],
    tactic_timeout: int,
) -> _CandidateOutcome:
    """
    Run one candidate's sentences sequentially from `state` (which is
    left untouched) and classify the outcome. The `except Exception`
    breadth matches `_probe_goals`: rejections and timeouts both count
    as the candidate failing.
    """
    cur = state
    for j, sentence in enumerate(sentences):
        if getattr(client, "poisoned", False):
            return _CandidateOutcome(
                candidate=candidate,
                status="error",
                detail=rocq_server.TRANSPORT_FAILURE_TEXT.format(
                    kind="earlier failure in this session"
                ),
            )
        try:
            cur = _run_guarded(client, cur, sentence, tactic_timeout)
        except Exception as e:
            detail = str(e)
            if len(sentences) > 1:
                detail = f"at sentence #{j + 1} `{sentence}`: {detail}"
            return _CandidateOutcome(
                candidate=candidate, status="error", detail=detail
            )
        if cur.proof_finished:
            return _CandidateOutcome(candidate=candidate, status="finished")
    return _CandidateOutcome(
        candidate=candidate,
        status="applied",
        goals_after=_safe_goals(client, cur),
    )


def _format_try_tactics_report(
    prefix: list[str],
    n_goals: int,
    results: list[_CandidateOutcome],
    dropped: int,
    char_cap: int,
) -> str:
    where = (
        f"after your {len(prefix)}-tactic prefix"
        if prefix
        else "at the initial state"
    )
    parts: list[str] = [
        f"Tried {len(results)} candidate(s) {where} — {n_goals} open "
        "goal(s) at that state. Nothing was committed.",
        "",
    ]
    for i, r in enumerate(results, 1):
        # Candidates may span lines; collapse whitespace so the
        # one-line-per-candidate layout survives.
        shown = " ".join(r.candidate.split())
        if r.status == "finished":
            parts.append(
                f"#{i} `{shown}` -> PROOF FINISHED: closes every "
                "remaining goal."
            )
        elif r.status == "error":
            parts.append(f"#{i} `{shown}` -> FAILS: {r.detail}")
        elif r.status == "skipped":
            parts.append(f"#{i} `{shown}` -> skipped: {r.detail}")
        else:
            n_after = len(r.goals_after)
            if n_after < n_goals:
                verdict = (
                    f"applies, closes {n_goals - n_after} goal(s) "
                    f"({n_goals} -> {n_after})"
                )
            else:
                verdict = f"applies ({n_goals} -> {n_after} goals)"
            parts.append(f"#{i} `{shown}` -> {verdict}.")
            if r.goals_after:
                head = r.goals_after[0].strip()
                if len(head) > TRY_TACTICS_GOAL_CHAR_CAP:
                    head = (
                        head[:TRY_TACTICS_GOAL_CHAR_CAP].rstrip()
                        + "\n[goal truncated]"
                    )
                parts.append("First resulting goal:")
                parts.append("```")
                parts.append(head)
                parts.append("```")
        parts.append("")

    if dropped > 0:
        parts.append(
            f"{dropped} candidate(s) beyond the "
            f"{MAX_TRY_TACTICS_CANDIDATES}-candidate cap were not "
            "evaluated."
        )
        parts.append("")
    finished = [i for i, r in enumerate(results, 1) if r.status == "finished"]
    if finished:
        parts.append(
            f"Candidate #{finished[0]} finishes the proof — submit "
            "your prefix followed by that candidate as your final "
            "fenced proof body."
        )
    else:
        parts.append(
            "Pick the most promising candidate, then either probe "
            "deeper (TryTactics with the extended prefix) or submit "
            "prefix + candidate as a (partial) proposal."
        )
    text = "\n".join(parts)
    if len(text) > char_cap:
        text = text[:char_cap].rstrip() + "\n[truncated]"
    return text


# Every successful battery probe leaves a proof state in the server,
# which petanque never frees: probing a goal flood (1128 goals in one
# archived cell) grew the server by ~2 GB. The battery therefore checks
# the server's memory budget every few goals and stops probing when it
# is exceeded (the remaining goals count as "not closed", the server is
# recycled before the next session) — a bounded outcome where the old
# regime ended in a watchdog kill or a kernel OOM.
PROBE_RSS_CHECK_EVERY = 8


def _probe_goals(
    client: Pytanque,
    state: State,
    n: int,
    tactic_timeout: int,
    goal_cap: int | None = None,
) -> list[str | None]:
    """
    Try the automation battery on each of the `n` goals of `state`
    (via goal selectors), returning the first closing tactic per goal,
    or `None` for goals the battery cannot close. With `goal_cap`, only
    the first `goal_cap` goals are probed and the list is that short.
    """
    limit = n if goal_cap is None else min(n, goal_cap)
    import runtime.tool_budget as tb

    closers: list[str | None] = []
    for i in range(1, limit + 1):
        op = tb.CURRENT.get()
        if op is not None and op.exhausted:
            break
        if getattr(client, "poisoned", False):
            break
        if (
            i > 1
            and (i - 1) % PROBE_RSS_CHECK_EVERY == 0
            and MANAGER.over_budget()
        ):
            MANAGER.request_recycle("rss during battery")
            break
        found: str | None = None
        for tac in AUTOMATION_BATTERY:
            if op is not None and op.exhausted:
                break
            probe = f"{i}: {tac}" if n > 1 else tac
            try:
                after = client.run(state, probe, timeout=tactic_timeout)
            except Exception:
                continue  # rejected or timed out: try the next one
            if after.proof_finished or len(_safe_goals(client, after)) < n:
                found = tac
                break
        closers.append(found)
    # Goals the battery never reached (memory stop, poisoned session)
    # count as "not closed"; an explicit `goal_cap` keeps the list short
    # so the feedback can say how many were probed.
    while len(closers) < limit:
        closers.append(None)
    return closers


def _apply_closers(
    client: Pytanque,
    state: State,
    closers: list[str],
    tactic_timeout: int,
) -> tuple[State, list[str]] | None:
    """
    Apply one closing tactic per goal, in *descending* goal order so
    earlier closures do not renumber later goals. Returns the final
    state and the exact tactic sentences applied, or `None` if a
    closer unexpectedly fails on replay.
    """
    n = len(closers)
    applied: list[str] = []
    for i in range(n, 0, -1):
        sentence = f"{i}: {closers[i - 1]}" if n > 1 else closers[0]
        try:
            state = _run_guarded(client, state, sentence, tactic_timeout)
        except Exception:
            return None
        applied.append(sentence)
    return state, applied


def _format_automation_report(
    prefix: list[str],
    goals: list[str],
    closers: list[str | None],
    char_cap: int,
) -> str:
    n = len(goals)
    where = (
        f"after your {len(prefix)}-tactic prefix"
        if prefix
        else "at the initial state"
    )
    parts: list[str] = [
        f"Automation probe {where} — {n} goal(s), battery of "
        f"{len(AUTOMATION_BATTERY)} closing tactics per goal:",
        "",
    ]
    for i, (goal, closer) in enumerate(zip(goals, closers), 1):
        if closer is not None:
            parts.append(f"- goal {i}: CLOSED by `{closer}`")
        else:
            parts.append(f"- goal {i}: no battery tactic closes it. Goal:")
            parts.append("```")
            parts.append(str(goal).strip())
            parts.append("```")
    parts.append("")
    if all(c is not None for c in closers):
        parts.append(
            "Every remaining goal closes! Submit your prefix followed "
            "by the closing tactics, using goal selectors in "
            "*descending* goal order (so earlier closures do not "
            "renumber later goals), e.g.:"
        )
        parts.append("```")
        parts.extend(f"{p}" for p in prefix)
        if n == 1:
            parts.append(f"{closers[0]}")
        else:
            for i in range(n, 0, -1):
                parts.append(f"{i}: {closers[i - 1]}")
        parts.append("```")
    else:
        parts.append(
            "Battery tried on each goal: "
            + " ".join(f"`{t}`" for t in AUTOMATION_BATTERY)
        )
        parts.append(
            "Unclosed goals need manual work (rewrites, asserts, case "
            "analysis) before automation can finish them."
        )
    text = "\n".join(parts)
    if len(text) > char_cap:
        text = text[:char_cap].rstrip() + "\n[truncated]"
    return text


def _format_try_proof_finished(
    succeeded: list[str],
    leftover: list[str],
) -> str:
    parts = [
        "PROOF FINISHED: this prefix closes the goal (no remaining subgoals).",
        "",
        "Tactics that ran (in order):",
    ]
    for i, t in enumerate(succeeded, 1):
        parts.append(f"  {i}. {t}")
    if leftover:
        parts.append("")
        parts.append(
            "Note: the following tactics from your input were "
            "not executed because the proof had already closed:"
        )
        for t in leftover:
            parts.append(f"  - {t}")
    parts.append("")
    parts.append(
        "If you want this proof, emit these tactics verbatim as your "
        "final fenced proof body."
    )
    return "\n".join(parts)


def _format_try_success(
    succeeded: list[str],
    remaining_goals: list[str],
    char_cap: int,
) -> str:
    parts: list[str] = []
    parts.append("All previewed tactics applied successfully.")
    parts.append("")
    parts.append("Tactics that ran (in order):")
    for i, t in enumerate(succeeded, 1):
        parts.append(f"  {i}. {t}")
    parts.append("")
    if not remaining_goals:
        parts.append(
            "No remaining goals reported, but the proof has not yet "
            "been marked finished — try `Qed.` in your final proposal."
        )
    else:
        parts.append(f"Remaining goals ({len(remaining_goals)}):")
        for g in remaining_goals:
            parts.append("")
            parts.append("```")
            parts.append(str(g).strip())
            parts.append("```")
    text = "\n".join(parts)
    if len(text) > char_cap:
        text = text[:char_cap].rstrip() + "\n[truncated; tighten preview]"
    return text


def _format_try_failure(
    failing_index: int,
    failing_tactic: str,
    error_message: str,
    succeeded: list[str],
    remaining_goals: list[str],
    char_cap: int,
) -> str:
    parts: list[str] = []
    parts.append(
        f"Preview FAILED at tactic #{failing_index + 1}: `{failing_tactic}`"
    )
    parts.append("")
    parts.append("Rocq error:")
    parts.append("```")
    parts.append(error_message.strip())
    parts.append("```")
    parts.append("")
    if succeeded:
        parts.append("Tactics that succeeded before the failure:")
        for i, t in enumerate(succeeded, 1):
            parts.append(f"  {i}. {t}")
    else:
        parts.append(
            "No tactics succeeded — the very first tactic was rejected."
        )
    parts.append("")
    if remaining_goals:
        parts.append("Goals at the point of failure:")
        for g in remaining_goals:
            parts.append("")
            parts.append("```")
            parts.append(str(g).strip())
            parts.append("```")
    else:
        parts.append("No goal state reported at the point of failure.")
    text = "\n".join(parts)
    if len(text) > char_cap:
        text = text[:char_cap].rstrip() + "\n[truncated; tighten preview]"
    return text


def _query_against(
    abs_file: str,
    theorem_name: str,
    command: str,
    char_cap: int,
) -> str:
    with _pytanque_session(abs_file) as client:
        r = _open_and_replay(
            client,
            abs_file,
            theorem_name,
            [],
            stop_when_finished=False,
            timeout=PROOF_TACTIC_TIMEOUT,
        )
        if r.start_error is not None:
            return f"Failed to open session: {r.start_error}"
        assert r.state is not None
        try:
            state = client.run(r.state, command, timeout=PROOF_TACTIC_TIMEOUT)
        except PetanqueError as e:
            return f"Rocq rejected the command: {e}"
        return _format_feedback(state, char_cap)


def _format_feedback(state: State, char_cap: int) -> str:
    parts: list[str] = []
    for _level, msg in state.feedback or []:
        if msg:
            parts.append(str(msg))
    text = "\n".join(parts).strip()
    if not text:
        return "(Rocq returned no output for this command.)"
    if len(text) > char_cap:
        text = text[:char_cap].rstrip() + "\n[truncated; refine your query]"
    return text


def _check_against(
    abs_file: str,
    theorem_name: str,
    tactics: list[str],
    probe_automation: bool,
    goal_caps: GoalCaps | None = None,
) -> Feedback:
    with _pytanque_session(abs_file) as client:
        r = _open_and_replay(
            client,
            abs_file,
            theorem_name,
            tactics,
            stop_when_finished=False,
            timeout=PROOF_TACTIC_TIMEOUT,
        )
        if r.start_error is not None:
            return Feedback(
                success=False,
                failing_index=None,
                failing_tactic=None,
                error_message=f"Failed to start session: {r.start_error}",
            )
        assert r.state is not None
        if r.failing_index is not None:
            assert r.failing_tactic is not None and r.error_message is not None
            return _failure_feedback(
                client,
                r.state,
                failing_index=r.failing_index,
                failing_tactic=r.failing_tactic,
                error_message=r.error_message,
                proof_so_far=r.succeeded,
                probe_automation=probe_automation,
                goal_caps=goal_caps,
            )
        state = r.state
        proof_so_far = r.succeeded

        try:
            state = client.run(state, "Qed.", timeout=PROOF_TACTIC_TIMEOUT)
        except PetanqueError as e:
            return _failure_feedback(
                client,
                state,
                failing_index=len(tactics),
                failing_tactic="Qed.",
                error_message=str(e),
                proof_so_far=proof_so_far,
                probe_automation=probe_automation,
                goal_caps=goal_caps,
            )

        return Feedback(
            success=True,
            proof_so_far=list(proof_so_far),
            finished=True,
        )


def _cap_goals(
    goals: list[str], probe: list[str | None] | None, caps: GoalCaps
) -> list[str]:
    """
    The `remaining_goals` a capped `Feedback` reports: the first
    `caps.render` goals (each cut at `caps.render_chars`) and, when any
    was hidden, the `GOALS_TRUNCATED_MARKER` as a final entry.
    """
    shown = goals[: caps.render]
    out: list[str] = []
    for g in shown:
        if len(g) > caps.render_chars:
            g = g[: caps.render_chars].rstrip() + "\n[goal truncated]"
        out.append(g)
    if len(goals) > len(shown):
        out.append(
            GOALS_TRUNCATED_MARKER.format(
                hidden=len(goals) - len(shown),
                shown=len(shown),
                total=len(goals),
                probed=len(probe) if probe is not None else 0,
            )
        )
    return out


def _failure_feedback(
    client: Pytanque,
    state: State,
    failing_index: int,
    failing_tactic: str,
    error_message: str,
    proof_so_far: list[str],
    probe_automation: bool,
    goal_caps: GoalCaps | None = None,
) -> Feedback:
    """
    Build the feedback for a failed / incomplete check. `state` is the
    last good state (i.e. after `proof_so_far`). With automation
    probing enabled, each remaining goal is probed with the battery;
    if every goal closes, the closers are applied (descending goal
    order) and `Qed.` is attempted — turning the failure into an
    `auto_finished` success.

    A transport failure while collecting goals or probing (deadline,
    reply cap, server death) is reported in `error_message` instead of
    the Rocq error: the attempt has no verdict, and the cell continues.
    """
    import runtime.tool_budget as tb

    op = tb.CURRENT.get()
    if op is not None:
        op.prefix = list(proof_so_far)
    if isinstance(client, BoundedPytanque) and client.poisoned:
        return Feedback(
            success=False,
            failing_index=failing_index,
            failing_tactic=failing_tactic,
            error_message=rocq_server.TRANSPORT_FAILURE_TEXT.format(
                kind=error_message
            ),
            proof_so_far=list(proof_so_far),
        )
    goals = _safe_goals(client, state)
    if op is not None:
        op.goals = list(goals)
    probe: list[str | None] | None = None
    if probe_automation and goals and not state.proof_finished:
        probe = _probe_goals(
            client,
            state,
            len(goals),
            AUTOMATION_TACTIC_TIMEOUT,
            goal_cap=goal_caps.probe if goal_caps is not None else None,
        )
        closers = [c for c in probe if c is not None]
        # Only a complete, all-closing probe may finish the proof.
        if len(closers) == len(probe) == len(goals):
            finished = _apply_closers(
                client, state, closers, AUTOMATION_TACTIC_TIMEOUT
            )
            if finished is not None:
                fstate, applied = finished
                try:
                    if not fstate.proof_finished:
                        raise PetanqueError(0, "goals remain")
                    client.run(fstate, "Qed.", timeout=PROOF_TACTIC_TIMEOUT)
                    return Feedback(
                        success=True,
                        proof_so_far=[*proof_so_far, *applied],
                        finished=True,
                        auto_finished=True,
                    )
                except PetanqueError:
                    pass  # fall through to ordinary failure feedback
    if goal_caps is not None:
        goals = _cap_goals(goals, probe, goal_caps)
    return Feedback(
        success=False,
        failing_index=failing_index,
        failing_tactic=failing_tactic,
        error_message=error_message,
        remaining_goals=goals,
        proof_so_far=list(proof_so_far),
        finished=state.proof_finished,
        probe=probe,
    )
