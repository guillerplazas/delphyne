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
