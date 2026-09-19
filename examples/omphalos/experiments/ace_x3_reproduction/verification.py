"""Exact replay and fresh compiler checks, with HTTP structurally forbidden."""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import redirect_stdout
from dataclasses import replace
import io
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command

from experiments.ace_thesis import campaign as old
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.replay_admission import fingerprint
from tools.maintenance.ace_thesis_kernel import compilation_source

from . import campaign as c
from .transport import ReproductionModel


def replay_one(
    job: c.Job, folder: Path, snapshots: Path, expected: dict[str, Any]
) -> dict[str, Any]:
    c.activate(events=False)
    args = job.instantiate(None)
    args.policy_args["snapshot_directory"] = str(snapshots)
    args.cache_mode = "replay"
    args.cache_file = str(folder / "cache.yaml")
    args.export_raw_trace = args.export_browsable_trace = args.export_log = (
        False
    )
    with (
        patch.object(
            ReproductionModel,
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
        out = run_command(
            run_strategy,
            args,
            ctx=replace(c.context(), cache_root=Path("/")),
            add_header=False,
        )
    if out.result is None or (
        out.result.success != expected["success"]
        or out.result.spent_budget != expected["spent_budget"]
        or json.loads(json.dumps(list(out.result.values)))
        != expected["values"]
    ):
        raise ValueError(
            "Exact replay mismatch: "
            + c.name(job, None)
            + " "
            + str(out.diagnostics)
        )
    return dict(
        cell=c.name(job, None),
        passed=True,
        cache_sha256=c.sha(folder / "cache.yaml"),
        result_sha256=c.sha(folder / "result.yaml"),
    )


def preflight() -> None:
    """Replay all 240 compatible previous validation trajectories."""
    c.verify_seal()
    mapping = {
        "nonace_ordinary": "none_32768",
        "nonace_matched": "none_8192",
        "ace_historical": "x3_8192",
    }
    rows: list[dict[str, Any]] = []
    for prior in old.jobs("validation"):
        if prior.arm not in mapping:
            continue
        result = old.cell_result(prior)
        job = c.Job(mapping[prior.arm], prior.theorem, prior.seed)
        if result is None:
            rows.append(dict(cell=c.name(job, None), provider_failed=True))
            continue
        rows.append(
            replay_one(
                job,
                old.directory(prior),
                old.CAMPAIGN / "transport" / old.name(prior, None),
                result,
            )
        )
    c.save(
        "preflight.json",
        dict(
            passed=True,
            attempted_cells=240,
            replayed=sum(r.get("passed", False) for r in rows),
            cells=rows,
            paid_calls=0,
        ),
    )
    print(
        json.dumps(
            {k: v for k, v in c.read("preflight.json").items() if k != "cells"}
        )
    )


def compile_proof(item: tuple[str, str, str]) -> dict[str, Any]:
    problem_file, theorem, proof = item
    executable = shutil.which("rocq")
    if executable is None:
        raise ValueError("Rocq compiler unavailable")
    compiler_sha = c.sha(Path(executable))
    source = compilation_source(
        (c.ROOT / problem_file).read_text(), theorem, proof
    )
    ident = fingerprint((source, compiler_sha))
    path = c.CAMPAIGN / "kernel" / ("Proof_" + ident + ".v")
    path.parent.mkdir(parents=True, exist_ok=True)
    certificate = path.with_suffix(".json")
    if certificate.exists():
        result = json.loads(certificate.read_text())
        if (
            result["source_sha256"] != c.sha(path)
            or result["compiler_sha256"] != compiler_sha
        ):
            raise ValueError("Kernel certificate drift")
        return result
    path.write_text(source)
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
        proof_sha256=fingerprint(proof),
        source_sha256=c.sha(path),
        compiler_sha256=compiler_sha,
        compiler=executable,
    )
    certificate.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


def kernel(
    items: dict[tuple[str, str, str], list[str]], filename: str
) -> None:
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = [
            dict(**r, cells=items[item])
            for item, r in zip(items, pool.map(compile_proof, items))
        ]
    c.save(
        filename,
        dict(
            passed=all(r["passed"] for r in rows),
            unique_proofs=len(items),
            cells=sum(len(v) for v in items.values()),
            results=rows,
        ),
    )
    if not all(r["passed"] for r in rows):
        raise ValueError("Fresh kernel verification failed")


def replay_job(job: c.Job) -> dict[str, Any]:
    result = c.cell_result(job)
    filename = "verification/cells/" + c.name(job, None) + ".json"
    hashes = {
        n: c.sha(c.directory(job) / n)
        for n in ("cache.yaml", "result.yaml")
        if (c.directory(job) / n).exists()
    }
    source_hash = c.sha(Path(__file__))
    if (c.CAMPAIGN / filename).exists():
        certificate = c.read(filename)
        if (
            certificate["hashes"] != hashes
            or certificate["source_sha256"] != source_hash
        ):
            raise ValueError("Replay certificate provenance drift")
        return certificate["result"]
    if result is None:
        row = dict(cell=c.name(job, None), provider_failed=True)
    else:
        row = replay_one(
            job,
            c.directory(job),
            c.CAMPAIGN / "transport" / c.name(job, None),
            result,
        )
    if hashes != {n: c.sha(c.directory(job) / n) for n in hashes}:
        raise ValueError("Replay modified an original artifact")
    c.save(
        filename,
        dict(
            result=row, hashes=hashes, source_sha256=source_hash, paid_calls=0
        ),
    )
    return row


def replay_completed() -> None:
    """Certify immutable completed cells while other paid cells are running."""
    c.verify_seal()
    selected = [
        j
        for j in c.jobs()
        if c.ol.ground_truth(c.directory(j)) in ("done", "failed")
    ]
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(replay_job, selected))
    print(
        json.dumps(dict(certified=len(rows), full_verdict=False, paid_calls=0))
    )


def verify() -> None:
    c.verify_seal()
    before = Ledger(c.CAMPAIGN / "ledger.sqlite3").summary()
    items: dict[tuple[str, str, str], list[str]] = {}
    for job in c.jobs():
        result = c.cell_result(job)
        if result is None:
            continue
        if result["success"]:
            args = job.instantiate(None)
            key = (
                str(args.args["problem_file"]),
                job.theorem,
                result["values"][0],
            )
            items.setdefault(key, []).append(c.name(job, None))
    # Separate processes keep PolicyEnv, model state and event routing local.
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(replay_job, c.jobs()))
    if before != Ledger(c.CAMPAIGN / "ledger.sqlite3").summary():
        raise ValueError("Replay changed billing")
    c.save(
        "verification/replay.json", dict(passed=True, cells=rows, paid_calls=0)
    )
    kernel(items, "verification/kernel.json")
    print(
        json.dumps(
            dict(replayed=len(rows), unique_proofs=len(items), passed=True)
        )
    )
