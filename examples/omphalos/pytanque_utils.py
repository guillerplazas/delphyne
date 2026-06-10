"""
Pytanque bridge and miniF2F problem parser used by the Delphyne baseline.

Pure Python: no Delphyne imports, so this module can be called from
`dp.compute(...)` boundaries without dragging strategy state in.
"""

# `pytanque` ships no type stubs, so strict mode drowns this module in
# unknown-type reports at the library boundary.
# pyright: basic

from __future__ import annotations

import os
import re
import secrets
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from pytanque import PetanqueError, Pytanque, PytanqueMode


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
    success: bool
    failing_index: int | None = None
    failing_tactic: str | None = None
    error_message: str | None = None
    remaining_goals: list[str] = field(default_factory=list)
    proof_so_far: list[str] = field(default_factory=list)
    finished: bool = False


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

    imports = "\n".join(m.group(0).strip() for m in _IMPORT_LINE_RE.finditer(text))

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
      - blank lines and prose lines that don't end in `.`
    """
    body = script
    fence_match = _FENCE_RE.search(body)
    if fence_match:
        body = fence_match.group(1)

    tactics: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line in {"Proof.", "Qed.", "Admitted.", "Defined.", "Abort."}:
            continue
        if not line.endswith("."):
            continue
        tactics.append(line)
    return tactics


def _safe_goals(client: Pytanque, state) -> list[str]:
    try:
        goals = client.goals(state)
    except Exception:
        return []
    out: list[str] = []
    for g in goals or []:
        try:
            out.append(str(g))
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


def check(
    file: str,
    theorem_name: str,
    tactics: list[str],
    extra_imports: tuple[str, ...] = DEFAULT_EXTRA_IMPORTS,
) -> Feedback:
    """
    Open a fresh Pytanque STDIO session, replay `tactics` against the
    theorem, attempt a final `Qed.`, and return structured feedback.

    One session per call: keeps lifetime obvious and side-effect free.

    If `extra_imports` is non-empty, a temp copy of `file` is created
    next to the original with those imports prepended (the original is
    not modified); pytanque is pointed at the temp copy.
    """
    proof_so_far: list[str] = []
    file = _resolve(file)

    if extra_imports:
        run_file = _materialize_with_extra_imports(file, extra_imports)
    else:
        run_file = file

    try:
        return _check_against(run_file, theorem_name, tactics, proof_so_far)
    finally:
        if extra_imports:
            try:
                os.unlink(run_file)
                os.rmdir(Path(run_file).parent)
            except OSError:
                pass


def try_tactic(
    file: str,
    theorem_name: str,
    tactics_script: str,
    extra_imports: tuple[str, ...] = DEFAULT_EXTRA_IMPORTS,
    char_cap: int = DEFAULT_QUERY_OUTPUT_CHAR_CAP,
) -> str:
    """
    Preview the effect of applying a sequence of tactics to the initial
    proof state of `theorem_name` in `file`, *without committing*.

    Rocq proof state is functional: `client.run(state, tac)` returns a
    new state and leaves the original valid. We open a fresh pytanque
    session, replay the tactics one-by-one from the theorem's initial
    state, and return a human-readable summary of where we landed:

    - all tactics succeeded and the proof finished → "PROOF FINISHED"
      report (this prefix actually closes the goal — emit it as the
      final proof body!);
    - all tactics succeeded, goals remain → the remaining goal state;
    - one tactic failed → the failing tactic, error message, the prefix
      of tactics that succeeded, and the goals at the point of failure.

    No `Qed.` is attempted here — this is preview, not verification.
    Call `check` (via the proposal flow) once you're confident.

    Pytanque errors are caught and rendered as the tool result so the
    agent can self-correct on its next turn instead of crashing.
    """
    file = _resolve(file)
    tactics = split_into_tactics(tactics_script)
    if not tactics:
        return (
            "No tactics to preview. Pass a fenced Rocq block (each "
            "tactic ending with `.`) as the `tactics` argument."
        )

    if extra_imports:
        run_file = _materialize_with_extra_imports(file, extra_imports)
    else:
        run_file = file

    try:
        return _try_tactic_against(run_file, theorem_name, tactics, char_cap)
    finally:
        if extra_imports:
            try:
                os.unlink(run_file)
                os.rmdir(Path(run_file).parent)
            except OSError:
                pass


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

    if extra_imports:
        run_file = _materialize_with_extra_imports(file, extra_imports)
    else:
        run_file = file

    try:
        return _query_against(run_file, theorem_name, command, char_cap)
    finally:
        if extra_imports:
            try:
                os.unlink(run_file)
                os.rmdir(Path(run_file).parent)
            except OSError:
                pass


def _try_tactic_against(
    abs_file: str,
    theorem_name: str,
    tactics: list[str],
    char_cap: int,
) -> str:
    """
    Inner implementation of `try_tactic`. Opens a pytanque STDIO session,
    replays `tactics` from the theorem's initial state, returns a
    formatted string describing the resulting state.
    """
    with Pytanque(mode=PytanqueMode.STDIO) as client:
        try:
            state = client.start(abs_file, theorem_name)
        except PetanqueError as e:
            return f"Failed to open session: {e}"

        succeeded: list[str] = []
        for i, tac in enumerate(tactics):
            try:
                state = client.run(state, tac)
            except PetanqueError as e:
                return _format_try_failure(
                    failing_index=i,
                    failing_tactic=tac,
                    error_message=str(e),
                    succeeded=succeeded,
                    remaining_goals=_safe_goals(client, state),
                    char_cap=char_cap,
                )
            succeeded.append(tac)

            if getattr(state, "proof_finished", False):
                return _format_try_proof_finished(
                    succeeded=succeeded,
                    leftover=tactics[i + 1:],
                )

        return _format_try_success(
            succeeded=succeeded,
            remaining_goals=_safe_goals(client, state),
            char_cap=char_cap,
        )


def _format_try_proof_finished(
    succeeded: list[str],
    leftover: list[str],
) -> str:
    parts = [
        "PROOF FINISHED: this prefix closes the goal "
        "(no remaining subgoals).",
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
        f"Preview FAILED at tactic #{failing_index + 1}: "
        f"`{failing_tactic}`"
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
    with Pytanque(mode=PytanqueMode.STDIO) as client:
        try:
            state = client.start(abs_file, theorem_name)
        except PetanqueError as e:
            return f"Failed to open session: {e}"
        try:
            state = client.run(state, command)
        except PetanqueError as e:
            return f"Rocq rejected the command: {e}"
        return _format_feedback(state, char_cap)


def _format_feedback(state: object, char_cap: int) -> str:
    fb = getattr(state, "feedback", None) or []
    parts: list[str] = []
    for entry in fb:
        try:
            _level, msg = entry
        except (TypeError, ValueError):
            msg = str(entry)
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
    proof_so_far: list[str],
) -> Feedback:
    with Pytanque(mode=PytanqueMode.STDIO) as client:
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
                return Feedback(
                    success=False,
                    failing_index=i,
                    failing_tactic=tac,
                    error_message=str(e),
                    remaining_goals=_safe_goals(client, state),
                    proof_so_far=list(proof_so_far),
                    finished=getattr(state, "proof_finished", False),
                )
            proof_so_far.append(tac)

        try:
            state = client.run(state, "Qed.")
        except PetanqueError as e:
            return Feedback(
                success=False,
                failing_index=len(tactics),
                failing_tactic="Qed.",
                error_message=str(e),
                remaining_goals=_safe_goals(client, state),
                proof_so_far=list(proof_so_far),
                finished=getattr(state, "proof_finished", False),
            )

        return Feedback(
            success=True,
            proof_so_far=list(proof_so_far),
            finished=True,
        )
