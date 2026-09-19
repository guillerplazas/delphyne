"""Exact HTTP-blocked replay and independent fresh-process Rocq checking."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from dataclasses import replace
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
from .artifact import fingerprint


def replay(batch: str) -> None:
    c.verify()
    before = c.accounting()["receipts"]
    jobs = c.jobs(batch)
    if not (c.CAMPAIGN / f"batches/{batch}.json").exists():
        raise ValueError("Replay requires a completed batch")
    path = f"replays/{batch}.json"
    hashes = {
        c.name(j, None): c.sha(c.directory(j) / "result.yaml")
        for j in jobs
        if (c.directory(j) / "result.yaml").exists()
    }
    if (c.CAMPAIGN / path).exists():
        saved = c.read(path)
        if saved["result_hashes"] != hashes or not saved["passed"]:
            raise ValueError("Replay certificate drift")
        return
    rows: list[dict[str, Any]] = []
    for job in jobs:
        original = c.cell_result(job)
        if original is None:
            rows.append(dict(cell=c.name(job, None), platform_failed=True))
            continue
        c.activate(events=False)
        args = job.instantiate(None)
        args.cache_mode = "replay"
        args.cache_file = str(c.directory(job) / "cache.yaml")
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("Replay forbids HTTP"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(c.context(), cache_root=Path("/")),
                add_header=False,
            )
        if (
            out.result is None
            or out.result.success != original["success"]
            or out.result.spent_budget != original["spent_budget"]
            or json.loads(json.dumps(list(out.result.values)))
            != original["values"]
        ):
            raise ValueError("Exact replay mismatch: " + c.name(job, None))
        rows.append(dict(cell=c.name(job, None), passed=True))
    if c.accounting()["receipts"] != before:
        raise ValueError("Replay created a paid receipt")
    c.save(
        path, dict(passed=True, paid_calls=0, cells=rows, result_hashes=hashes)
    )


def compilation_source(problem: str, theorem: str, proof: str) -> str:
    if re.search(
        r"\b(?:Admitted|admit|Axiom|Parameter|Abort)\b|Unset\s+(?:Guard|Positivity|Universe)",
        proof,
    ):
        raise ValueError("Unsafe proof command")
    if not re.search(r"\bTheorem\s+" + re.escape(theorem) + r"\s*:", problem):
        raise ValueError("Wrong source theorem")
    body, count = re.subn(
        r"\bProof\.\s*Admitted\.",
        lambda _: "Proof.\n" + proof + "\nQed.",
        problem,
    )
    if count != 1:
        raise ValueError("Expected exactly one unproved source theorem")
    return (
        "\n".join(DEFAULT_EXTRA_IMPORTS)
        + "\n"
        + body
        + f"\nPrint Assumptions {theorem}.\n"
    )


def compile_proof(item: tuple[str, str, str]) -> dict[str, Any]:
    problem_file, theorem, proof = item
    problem = (c.ROOT / problem_file).read_text()
    source = compilation_source(problem, theorem, proof)
    ident = fingerprint((source, c.sha(Path(__file__))))
    path = c.CAMPAIGN / "kernel" / ("Proof_" + ident + ".v")
    certificate = path.with_suffix(".json")
    if certificate.exists():
        return json.loads(certificate.read_text())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)
    executable = shutil.which("rocq")
    if executable is None:
        raise ValueError("Rocq compiler unavailable")
    try:
        process = subprocess.run(
            [executable, "compile", "-q", str(path)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=path.parent,
        )
        result = dict(
            passed=process.returncode == 0,
            returncode=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
        )
    except subprocess.TimeoutExpired as exc:
        result = dict(passed=False, timeout=True, detail=str(exc))
    result.update(
        theorem=theorem,
        source_sha256=c.sha(path),
        proof_sha256=fingerprint(proof),
        problem_sha256=fingerprint(problem),
        compiler=executable,
        compiler_sha256=c.sha(Path(executable)),
        assumptions="Print Assumptions output retained in stdout",
        independent=True,
        memo_reused=False,
    )
    certificate.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


def kernel() -> None:
    c.verify()
    items: dict[tuple[str, str, str], list[str]] = {}
    for job in c.all_jobs():
        if job.role != "proof":
            continue
        result = c.cell_result(job)
        if result and result["success"]:
            if len(result["values"]) != 1 or not isinstance(
                result["values"][0], str
            ):
                raise ValueError("Unexpected returned proof")
            key = (
                c.read(job.input_file)["args"]["problem_file"],
                job.theorem,
                result["values"][0],
            )
            items.setdefault(key, []).append(c.name(job, None))
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(compile_proof, items))
    c.save(
        "kernel_checks.json",
        dict(
            passed=all(r["passed"] for r in results),
            unique_proofs=len(items),
            cells=sum(len(v) for v in items.values()),
            results=[
                dict(**r, cells=items[item]) for item, r in zip(items, results)
            ],
        ),
    )
    if not all(r["passed"] for r in results):
        raise ValueError("Independent kernel checks contain failures")
