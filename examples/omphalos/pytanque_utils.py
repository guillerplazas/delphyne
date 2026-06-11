"""
Pytanque bridge and miniF2F problem parser used by the Delphyne baseline.

Pure Python: no Delphyne imports, so this module can be called from
`dp.compute(...)` boundaries without dragging strategy state in.
"""

from __future__ import annotations

import os
import re
import secrets
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

from pytanque import PetanqueError, Pytanque, PytanqueMode, State


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
_WORKSPACE_ROOT = Path(__file__).resolve().parent

# Rocq's micromega tactics (lia/nia/nra/psatz) write `.lia.cache` etc.
# into the *cwd of the Rocq process*. The `pet` subprocess inherits the
# cwd it is spawned with, so `_pytanque_session` chdirs here just for
# the spawn — keeping the cache files out of the workspace root.
_ROCQ_CACHE_DIR = _WORKSPACE_ROOT / ".rocq_cache"


@contextmanager
def _pytanque_session() -> Generator[Pytanque]:
    """
    Open a fresh STDIO pytanque session whose `pet` subprocess runs
    with cwd `.rocq_cache/`, so Rocq's tactic cache files accumulate
    there instead of in the workspace root. The original cwd is
    restored as soon as the subprocess is spawned.
    """
    _ROCQ_CACHE_DIR.mkdir(exist_ok=True)
    cwd = os.getcwd()
    os.chdir(_ROCQ_CACHE_DIR)
    try:
        client = Pytanque(mode=PytanqueMode.STDIO)
        client.__enter__()
    finally:
        os.chdir(cwd)
    try:
        yield client
    finally:
        client.__exit__(None, None, None)


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


def _extract_section(header: str, label: str) -> str:
    pattern = re.compile(
        rf"{label}\s*:\s*\n(.*?)(?=\n\s*(?:Informal\s+(?:statement|proof)\s*:|Source\s*:|Split\s*:|$))",
        re.DOTALL | re.IGNORECASE,
    )
    m = pattern.search(header)
    if not m:
        return ""
    return m.group(1).strip()


def parse_problem(path: str) -> ProblemSpec:
    path = _resolve(path)
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

    return ProblemSpec(
        file=path,
        theorem_name=theorem_name,
        theorem_statement=theorem_statement,
        informal_statement=informal_statement,
        informal_proof=informal_proof,
        imports=imports,
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


def _safe_goals(client: Pytanque, state: State) -> list[str]:
    try:
        goals = client.goals(state)
    except Exception:
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


def _materialize_with_extra_imports(
    file: str, extra_imports: tuple[str, ...]
) -> str:
    """
    Write a temp copy of `file` to a fresh directory under the system
    tempdir, with the extra `Require Import` lines prepended. Returns
    the temp path; the caller is responsible for unlinking the file and
    its parent directory.

    The temp file lives *outside* the miniF2F tree to escape the
    `_CoqProject` whitelist: petanque restricts theorem lookup to files
    listed in `_CoqProject`, so a sibling temp file inside the tree
    cannot be opened. The miniF2F problems we run only use stdlib
    imports, so there is no cross-file reference to break.
    """
    src = Path(file).resolve()
    body = src.read_text()
    preamble = "\n".join(extra_imports) + "\n"
    tag = secrets.token_hex(4)
    tmp_dir = Path(tempfile.gettempdir()) / f"omphalos_aug_{tag}"
    tmp_dir.mkdir(parents=True, exist_ok=False)
    dst = tmp_dir / src.name
    dst.write_text(preamble + body)
    return str(dst)


@contextmanager
def _augmented_file(
    file: str, extra_imports: tuple[str, ...]
) -> Generator[str]:
    """
    Yield the path pytanque should be pointed at: a temp copy of `file`
    with `extra_imports` prepended (cleaned up on exit), or `file`
    itself if there is nothing to prepend.
    """
    if not extra_imports:
        yield file
        return
    run_file = _materialize_with_extra_imports(file, extra_imports)
    try:
        yield run_file
    finally:
        try:
            os.unlink(run_file)
            os.rmdir(Path(run_file).parent)
        except OSError:
            pass


def check(
    file: str,
    theorem_name: str,
    tactics: list[str],
    extra_imports: tuple[str, ...] = DEFAULT_EXTRA_IMPORTS,
    probe_automation: bool = False,
) -> Feedback:
    """
    Open a fresh Pytanque STDIO session, replay `tactics` against the
    theorem, attempt a final `Qed.`, and return structured feedback.

    One session per call: keeps lifetime obvious and side-effect free.

    If `extra_imports` is non-empty, a temp copy of `file` is created
    outside the miniF2F tree with those imports prepended (the original
    is not modified); pytanque is pointed at the temp copy.

    With `probe_automation=True`, verification is *automation-assisted*:
    whenever the script fails or leaves goals open, each remaining goal
    is probed with `AUTOMATION_BATTERY` (results land in
    `Feedback.probe`), and if every goal closes, the verifier finishes
    the proof itself — returning success with `auto_finished=True` and
    the complete assembled script in `proof_so_far`.
    """
    file = _resolve(file)
    with _augmented_file(file, extra_imports) as run_file:
        return _check_against(
            run_file, theorem_name, tactics, probe_automation
        )


def check_assisted(
    file: str,
    theorem_name: str,
    tactics: list[str],
) -> Feedback:
    """
    `check` with automation-assisted verification enabled. Kept as a
    named top-level entry point so strategies can pass it to
    `dp.compute(...)` directly.
    """
    return check(file, theorem_name, tactics, probe_automation=True)


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
    try:
        state = client.start(abs_file, theorem_name)
    except PetanqueError as e:
        return None, f"Failed to open session: {e}"

    succeeded: list[str] = []
    for i, tac in enumerate(tactics):
        try:
            state = client.run(state, tac)
        except PetanqueError as e:
            return None, _format_try_failure(
                failing_index=i,
                failing_tactic=tac,
                error_message=str(e),
                succeeded=succeeded,
                remaining_goals=_safe_goals(client, state),
                char_cap=char_cap,
            )
        succeeded.append(tac)

        if state.proof_finished:
            return None, _format_try_proof_finished(
                succeeded=succeeded,
                leftover=tactics[i + 1 :],
            )

    return state, None


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
    with _pytanque_session() as client:
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
            after = client.run(state, command)
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
    with _pytanque_session() as client:
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


def _probe_goals(
    client: Pytanque,
    state: State,
    n: int,
    tactic_timeout: int,
) -> list[str | None]:
    """
    Try the automation battery on each of the `n` goals of `state`
    (via goal selectors), returning the first closing tactic per goal,
    or `None` for goals the battery cannot close.
    """
    closers: list[str | None] = []
    for i in range(1, n + 1):
        found: str | None = None
        for tac in AUTOMATION_BATTERY:
            probe = f"{i}: {tac}" if n > 1 else tac
            try:
                after = client.run(state, probe, timeout=tactic_timeout)
            except Exception:
                continue  # rejected or timed out: try the next one
            if after.proof_finished or len(_safe_goals(client, after)) < n:
                found = tac
                break
        closers.append(found)
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
            state = client.run(state, sentence, timeout=tactic_timeout)
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
    with _pytanque_session() as client:
        try:
            state = client.start(abs_file, theorem_name)
        except PetanqueError as e:
            return f"Failed to open session: {e}"
        try:
            state = client.run(state, command)
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
) -> Feedback:
    proof_so_far: list[str] = []
    with _pytanque_session() as client:
        try:
            state = client.start(abs_file, theorem_name)
        except PetanqueError as e:
            return Feedback(
                success=False,
                failing_index=None,
                failing_tactic=None,
                error_message=f"Failed to start session: {e}",
            )

        for i, tac in enumerate(tactics):
            try:
                state = client.run(state, tac)
            except PetanqueError as e:
                return _failure_feedback(
                    client,
                    state,
                    failing_index=i,
                    failing_tactic=tac,
                    error_message=str(e),
                    proof_so_far=proof_so_far,
                    probe_automation=probe_automation,
                )
            proof_so_far.append(tac)

        try:
            state = client.run(state, "Qed.")
        except PetanqueError as e:
            return _failure_feedback(
                client,
                state,
                failing_index=len(tactics),
                failing_tactic="Qed.",
                error_message=str(e),
                proof_so_far=proof_so_far,
                probe_automation=probe_automation,
            )

        return Feedback(
            success=True,
            proof_so_far=list(proof_so_far),
            finished=True,
        )


def _failure_feedback(
    client: Pytanque,
    state: State,
    failing_index: int,
    failing_tactic: str,
    error_message: str,
    proof_so_far: list[str],
    probe_automation: bool,
) -> Feedback:
    """
    Build the feedback for a failed / incomplete check. `state` is the
    last good state (i.e. after `proof_so_far`). With automation
    probing enabled, each remaining goal is probed with the battery;
    if every goal closes, the closers are applied (descending goal
    order) and `Qed.` is attempted — turning the failure into an
    `auto_finished` success.
    """
    goals = _safe_goals(client, state)
    probe: list[str | None] | None = None
    if probe_automation and goals and not state.proof_finished:
        probe = _probe_goals(
            client, state, len(goals), AUTOMATION_TACTIC_TIMEOUT
        )
        closers = [c for c in probe if c is not None]
        if len(closers) == len(probe):
            finished = _apply_closers(
                client, state, closers, AUTOMATION_TACTIC_TIMEOUT
            )
            if finished is not None:
                fstate, applied = finished
                try:
                    if not fstate.proof_finished:
                        raise PetanqueError(0, "goals remain")
                    client.run(fstate, "Qed.")
                    return Feedback(
                        success=True,
                        proof_so_far=[*proof_so_far, *applied],
                        finished=True,
                        auto_finished=True,
                    )
                except PetanqueError:
                    pass  # fall through to ordinary failure feedback
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
