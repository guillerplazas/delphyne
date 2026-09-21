"""Isolate one discarded valid proof using the actual controller and Rocq.

The sole change is extracting the last complete typed proof from one recorded
reply instead of an empty fence gap. Earlier replies and the original paid
cache remain immutable. Any model cache miss fails with HTTP disabled. The
new proof check executes locally; this is a conditional diagnostic, not a
replacement outcome or a fresh benchmark sample.
"""

from contextlib import redirect_stdout
from dataclasses import replace
import gzip
import io
import json
from pathlib import Path
import resource
import shutil
import tempfile
from typing import Any
from unittest.mock import patch

from delphyne.stdlib import queries
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command

from runtime.campaign_budget import CampaignResponsesModel

from . import campaign as c
from .audit import load_yaml
from .common import CAMPAIGN, OUTPUT, REPORT, digest, read, save, sha
from .economics import ledger_rows
from .output_repetition import complete_proof_blocks
from .transport import AuditModel

CELL = "validation__A0__imo_1964_p2__seed1"
RECEIPT = "0588fc58fced4c11872f70567958975a"


def run() -> None:
    diagnosis = read(REPORT / "output_repetition_diagnosis.json")
    source = next(r for r in diagnosis["replies"] if r["receipt"] == RECEIPT)
    check = next(
        r for r in diagnosis["kernel_checks"] if r["receipt"] == RECEIPT
    )
    raw_path = CAMPAIGN / source["response_file"]
    if not check["passed"] or sha(raw_path) != source["response_sha"]:
        raise ValueError("The independently compiled source changed")
    with gzip.open(raw_path, "rt") as stream:
        raw = json.load(stream)
    text = "\n".join(
        part["text"]
        for message in raw["response"]["output"]
        if message["type"] == "message"
        for part in message["content"]
        if part["type"] == "output_text"
    )
    original_extract = queries.extract_final_block
    legacy = original_extract(text)
    if legacy is None or legacy.strip():
        raise ValueError(
            "The original parser no longer returns an empty proof"
        )
    candidate = complete_proof_blocks(text)[-1]
    matches = [
        (entry["batch"], c.Job(**encoded))
        for entry in read(CAMPAIGN / "core_schedule.json")["batches"]
        for encoded in read(CAMPAIGN / "batches" / (entry["batch"] + ".json"))
        if c.name(c.Job(**encoded), None) == CELL
    ]
    if len(matches) != 1:
        raise ValueError("Expected one registered ordinary baseline cell")
    batch, job = matches[0]
    directory = OUTPUT / batch / "configs" / CELL
    hashes = {n: sha(directory / n) for n in ("cache.yaml", "result.yaml")}
    protocol_path = CAMPAIGN / "parser_replay_protocol.json"
    save(
        protocol_path,
        dict(
            cell=CELL,
            receipt=RECEIPT,
            batch=batch,
            hashes=hashes,
            raw_response_sha=sha(raw_path),
            candidate_sha=digest(candidate),
            caps=[0.10, 0.09, 0.075, 0.05],
            change="Only this exact recorded reply uses its last complete typed proof. Every preceding parsed reply, model response and request remains fixed; new local verifier computation is allowed. A model cache miss fails without HTTP.",
            selection="The sole compiling candidate among all27 capped validation replies, selected after the complete parser/kernel diagnostic. This is an explanatory conditional experiment, not a new efficacy estimate.",
        ),
    )
    target = REPORT / "parser_replay_certification.json"
    if target.exists():
        prior = read(target)
        if prior["protocol_sha"] != sha(protocol_path):
            raise ValueError("Parser replay protocol changed")
        print(json.dumps(prior, indent=2))
        return
    c.activate()
    limit = 4096 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    rows: list[dict[str, Any]] = []
    for cap in (0.10, 0.09, 0.075, 0.05):
        changes: list[str] = []

        def extract(value: str) -> str | None:
            if value == text:
                changes.append(digest(candidate))
                return candidate
            return original_extract(value)

        with tempfile.TemporaryDirectory(
            prefix="parser-replay-", dir=CAMPAIGN
        ) as temp:
            copied = Path(temp) / "cache.yaml"
            shutil.copyfile(directory / "cache.yaml", copied)
            args = job.instantiate(None)
            args.budget = dict(price=cap, num_requests=32)
            args.cache_mode = "read_write"
            args.cache_file = str(copied)
            args.export_raw_trace = args.export_browsable_trace = (
                args.export_log
            ) = False
            with (
                patch.object(queries, "extract_final_block", extract),
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
                patch(
                    "openai.OpenAI",
                    side_effect=AssertionError("HTTP forbidden"),
                ),
                redirect_stdout(io.StringIO()),
            ):
                output = run_command(
                    run_strategy,
                    args,
                    ctx=replace(c.context(), cache_root=Path("/")),
                    add_header=False,
                )
            if output.result is None or output.diagnostics:
                raise ValueError(f"Parser replay failed: {output.diagnostics}")
            result = output.result
            if result.values and list(result.values) != [candidate]:
                raise ValueError("Unexpected proof synthesized during replay")
            rows.append(
                dict(
                    cap=cap,
                    solved=bool(result.values),
                    spent_budget=dict(result.spent_budget),
                    corrected_extractions=len(changes),
                    paid_calls=0,
                )
            )
    if hashes != {n: sha(directory / n) for n in hashes}:
        raise ValueError("Parser replay altered paid evidence")
    receipts = sorted(
        [r for r in ledger_rows() if r["cell"] == CELL],
        key=lambda r: r["created"],
    )
    if any(r["status"] != "settled" for r in receipts):
        raise ValueError("Diagnostic baseline has unresolved billing")
    prefix = receipts[
        : next(i for i, r in enumerate(receipts) if r["id"] == RECEIPT) + 1
    ]
    observed = load_yaml(directory / "result.yaml")["outcome"]["result"]
    full = next(r for r in rows if r["cap"] == 0.10)
    if (
        not full["solved"]
        or abs(
            full["spent_budget"]["price"] - sum(r["charged"] for r in prefix)
        )
        > 1e-9
        or full["spent_budget"]["num_requests"] != len(prefix)
    ):
        raise ValueError(
            "Recovered proof did not stop at its original paid prefix"
        )
    result = dict(
        cell=CELL,
        receipt=RECEIPT,
        protocol_sha=sha(protocol_path),
        observed_cost=sum(r["charged"] for r in receipts),
        observed_requests=len(receipts),
        observed_solved=bool(observed["values"]),
        conditional_cost=full["spent_budget"]["price"],
        conditional_requests=full["spent_budget"]["num_requests"],
        avoidable_following_cost=sum(
            r["charged"] for r in receipts[len(prefix) :]
        ),
        replays=rows,
        paid_calls=0,
        benchmark_outcomes_changed=0,
        interpretation="The actual controller admits and accepts the unedited recovered proof with one fewer model request on this saved ordinary-baseline trajectory. Its original capped reply is still fully charged. This isolated parser effect is not ACE credit and does not predict all downstream behavior under a generally changed parser.",
    )
    save(target, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run()
