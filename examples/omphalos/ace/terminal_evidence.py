"""Train-only terminal receipts derived from immutable verifier records.

This is evidence extraction, not a new verification algorithm. The accepted
script is already present in legacy outcomes; the receipt explicitly binds
it to the submitted Compute input and recorded automation assistance.
"""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from experiments.common.ace_pools import POOLS
from runtime import pytanque_utils as pt
from runtime.paths import OMPHALOS_ROOT as ROOT


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class TerminalEvidence:
    theorem_name: str
    problem_file: str
    source_cell: str
    cache_sha256: str
    result_sha256: str
    checker: str
    check_sha256: str
    status: str
    submitted_script: tuple[str, ...]
    accepted_script: tuple[str, ...]
    auto_finished: bool | None
    common_prefix: tuple[str, ...]
    accepted_tail: tuple[str, ...]
    submitted_tail: tuple[str, ...]
    detail: str
    returned_script: str = ""
    version: int = 2

    def render(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    def sha256(self) -> str:
        return hashlib.sha256(self.render().encode()).hexdigest()


def extract_terminal_evidence(
    directory: Path, theorem_name: str
) -> TerminalEvidence:
    problem_file, _ = POOLS["trainX"][theorem_name]
    directory = directory.resolve()
    source = str(directory.relative_to(ROOT))
    cache, result = directory / "cache.yaml", directory / "result.yaml"
    rows: list[dict[str, Any]] = yaml.load(
        cache.read_text(), Loader=yaml.CSafeLoader
    )
    raw: dict[str, Any] = yaml.load(
        result.read_text(), Loader=yaml.CSafeLoader
    )["outcome"]["result"]
    checks: list[tuple[dict[str, Any], dict[str, Any], str]] = []
    for entry in rows:
        request = entry["input"]["request"]
        if request["options"].get("model") != "__compute__":
            continue
        call = yaml.safe_load(request["chat"][-1]["content"])
        if call.get("fun") not in (
            "check",
            "check_assisted",
            "checked_proof",
            "check_snippet",
        ):
            continue
        args = call["args"]
        snippet = call.get("fun") == "check_snippet"
        if snippet:
            context = args["context"]
            args = dict(
                problem_file=context["problem_file"],
                theorem_name=context["theorem_name"],
                tactics=[*context["prefix"], args["snippet"]],
            )
        if args.get("theorem_name") != theorem_name:
            raise ValueError("Terminal verifier belongs to another theorem")
        if (
            ROOT / args.get("file", args.get("problem_file", ""))
        ).resolve() != (ROOT / problem_file).resolve():
            raise ValueError("Terminal verifier source environment mismatch")
        recorded: dict[str, Any] = entry.get("output") or {}
        outputs: list[dict[str, Any]] = recorded.get("outputs") or []
        if not outputs:
            continue
        output = yaml.safe_load(outputs[0]["content"])
        if snippet:
            output = output["checked"]
        feedback = output.get("feedback", output)
        check_hash = hashlib.sha256(
            json.dumps(entry, sort_keys=True).encode()
        ).hexdigest()
        checks.append(({**call, "args": args}, feedback, check_hash))
    solved = bool(raw["success"])
    if not checks:
        if solved:
            raise ValueError("Solved outcome has no accepted verifier receipt")
        return TerminalEvidence(
            theorem_name,
            problem_file,
            source,
            digest(cache),
            digest(result),
            "",
            "",
            "missing",
            (),
            (),
            None,
            (),
            (),
            (),
            "No terminal proof check was recorded; do not infer a verdict.",
        )
    call, feedback, check_hash = checks[-1]
    if bool(feedback["success"]) != solved:
        raise ValueError("Outcome and terminal verifier disagree")
    submitted = tuple(call["args"]["tactics"])
    accepted = tuple(feedback.get("proof_so_far", ())) if solved else ()
    if solved and (
        len(raw["values"]) != 1
        or tuple(pt.split_into_tactics(str(raw["values"][0])))
        != (
            tuple(pt.split_into_tactics("\n".join(accepted)))
            if call["fun"] == "check_snippet"
            else accepted
        )
    ):
        raise ValueError("Returned proof differs from the accepted receipt")
    common = 0
    if solved:
        for a, b in zip(submitted, accepted):
            if a != b:
                break
            common += 1
    return TerminalEvidence(
        theorem_name,
        problem_file,
        source,
        digest(cache),
        digest(result),
        call["fun"],
        check_hash,
        "accepted" if solved else "not_solved",
        submitted,
        accepted,
        feedback.get("auto_finished"),
        accepted[:common],
        accepted[common:],
        submitted[common:],
        "Tails are a derived textual diff, not an execution trace. "
        "Only accepted_script is certified complete. auto_finished is the "
        "recorded assistance flag; absent pre-assistance details are unknown. "
        "returned_script matches via the existing tactic splitter; accepted_script "
        "preserves the exact checker sequence.",
        returned_script=str(raw["values"][0]) if solved else "",
    )
