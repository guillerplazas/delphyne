"""Exact replay with HTTP disabled and independent Rocq compilation."""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import redirect_stdout
from dataclasses import replace
import fcntl
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command

from runtime.campaign_budget import CampaignResponsesModel
from runtime.pytanque_utils import DEFAULT_EXTRA_IMPORTS

from . import campaign as c
from .common import CAMPAIGN, OUTPUT, ROOT, allowed, digest, read, save, sha
from .completion import require_closed
from .transport import AuditModel
from .workflow import result


def replay_one(item: tuple[str, c.Job]) -> dict[str, Any]:
    batch, job = item
    c.activate()
    # Keep replay events separate from paid admission evidence.
    import os

    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
        CAMPAIGN / "replay_events.jsonl"
    )
    folder = OUTPUT / batch / "configs" / c.name(job, None)
    expected = result(batch, c.name(job, None))
    certificate = (
        CAMPAIGN / "verification" / batch / (c.name(job, None) + ".json")
    )
    hashes = {n: sha(folder / n) for n in ("cache.yaml", "result.yaml")}
    if certificate.exists():
        prior = read(certificate)
        if prior["hashes"] != hashes:
            raise ValueError("Replay input changed")
        return prior
    args = job.instantiate(None)
    args.cache_mode = "replay"
    args.cache_file = str(folder / "cache.yaml")
    args.export_raw_trace = args.export_browsable_trace = args.export_log = (
        False
    )
    with (
        patch.object(
            AuditModel,
            "_send_final_request",
            side_effect=AssertionError("HTTP forbidden"),
        ),
        patch.object(
            CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("HTTP forbidden"),
        ),
        patch("openai.OpenAI", side_effect=AssertionError("HTTP forbidden")),
        redirect_stdout(io.StringIO()),
    ):
        output = run_command(
            run_strategy,
            args,
            ctx=replace(c.context(), cache_root=Path("/")),
            add_header=False,
        )
    if output.result is None or (
        output.result.success != expected["success"]
        or output.result.spent_budget != expected["spent_budget"]
        or list(output.result.values) != expected["values"]
    ):
        raise ValueError(
            "Exact replay mismatch: "
            + c.name(job, None)
            + str(output.diagnostics)
        )
    if hashes != {n: sha(folder / n) for n in hashes}:
        raise ValueError("Replay changed an input artifact")
    row = dict(
        cell=c.name(job, None), hashes=hashes, passed=True, paid_calls=0
    )
    save(certificate, row)
    return row


def compilation_source(problem: str, theorem: str, proof: str) -> str:
    if re.search(
        r"\b(?:Admitted|admit|Axiom|Parameter|Abort)\b|Unset\s+(?:Guard|Positivity|Universe)",
        proof,
    ):
        raise ValueError("Unsafe proof command")
    if not re.search(
        r"\bTheorem\s+" + re.escape(theorem) + r"\s*(?=[:({])", problem
    ):
        raise ValueError("Source theorem mismatch")
    source, count = re.subn(
        r"\bProof\.\s*Admitted\.",
        lambda _: "Proof.\n" + proof + "\nQed.",
        problem,
    )
    if count != 1:
        raise ValueError("Expected one unproved source theorem")
    return (
        "\n".join(DEFAULT_EXTRA_IMPORTS)
        + "\n"
        + source
        + f"\nPrint Assumptions {theorem}.\n"
    )


def compile_one(item: tuple[str, str, str]) -> dict[str, Any]:
    problem, theorem, proof = item
    if allowed().get(theorem, (None, None))[1] != problem:
        raise ValueError("Compilation outside allowed development data")
    executable = shutil.which("rocq")
    if executable is None:
        raise ValueError("Rocq unavailable")
    compiler_sha = sha(Path(executable))
    source = compilation_source((ROOT / problem).read_text(), theorem, proof)
    identity = digest([source, compiler_sha])
    path = CAMPAIGN / "kernel" / f"Proof_{identity}.v"
    path.parent.mkdir(exist_ok=True, parents=True)
    # Independent batch and historical audits can encounter the same proof.
    with path.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        return compile_locked(
            path, source, executable, compiler_sha, theorem, proof
        )


def compile_locked(
    path: Path,
    source: str,
    executable: str,
    compiler_sha: str,
    theorem: str,
    proof: str,
) -> dict[str, Any]:
    certificate = path.with_suffix(".json")
    if certificate.exists():
        row = read(certificate)
        if (
            row["source_sha"] != sha(path)
            or row["compiler_sha"] != compiler_sha
        ):
            raise ValueError("Compilation certificate changed")
        return row
    path.write_text(source)
    try:
        proc = subprocess.run(
            [executable, "compile", "-q", str(path)],
            cwd=path.parent,
            capture_output=True,
            text=True,
            timeout=300,
        )
        row: dict[str, Any] = dict(
            passed=proc.returncode == 0,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
    except subprocess.TimeoutExpired:
        row = dict(passed=False, timeout=True)
    row.update(
        theorem=theorem,
        source_sha=sha(path),
        compiler_sha=compiler_sha,
        proof_sha=digest(proof),
    )
    save(certificate, row)
    return row


def verify_batch(batch: str) -> None:
    require_closed(batch)
    jobs = [c.Job(**j) for j in read(CAMPAIGN / "batches" / f"{batch}.json")]
    with ProcessPoolExecutor(max_workers=8) as pool:
        replays = list(pool.map(replay_one, [(batch, j) for j in jobs]))
    proofs: dict[tuple[str, str, str], list[str]] = {}
    for j in jobs:
        values = result(batch, c.name(j, None))["values"]
        for value in values:
            key = (allowed()[j.theorem][1], j.theorem, str(value))
            proofs.setdefault(key, []).append(c.name(j, None))
    with ThreadPoolExecutor(max_workers=8) as pool:
        checks = [
            dict(**r, cells=proofs[k])
            for k, r in zip(proofs, pool.map(compile_one, proofs), strict=True)
        ]
    save(
        CAMPAIGN / "verification" / f"{batch}.json",
        dict(replays=replays, kernel=checks),
    )
    if not all(r["passed"] for r in checks):
        raise ValueError("Independent compiler failed")
    print(
        json.dumps(
            dict(
                batch=batch,
                replayed=len(replays),
                unique_proofs=len(checks),
                passed=True,
            )
        )
    )


def verify_completed() -> None:
    batches = [
        entry["batch"]
        for entry in read(CAMPAIGN / "core_schedule.json")["batches"]
    ]
    batches += [
        f"online-o{order}-s{step:02d}"
        for order in (0, 1)
        for step in range(40)
    ]
    batches += ["rule_repairs", "adaptive_frozen"]
    for batch in batches:
        if (CAMPAIGN / "verification" / f"{batch}.json").exists():
            continue
        try:
            require_closed(batch)
        except (ValueError, FileNotFoundError):
            continue
        verify_batch(batch)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit(
            "Use python -m experiments.ace_independent_audit.verification BATCH"
        )
    if sys.argv[1] == "run-completed":
        verify_completed()
    else:
        verify_batch(sys.argv[1])
