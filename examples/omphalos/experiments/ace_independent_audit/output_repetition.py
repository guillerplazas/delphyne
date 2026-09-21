"""Diagnose capped, repeated proof replies in complete validation panels.

No model calls or benchmark replacements. The candidate extractor accepts
only explicitly typed, complete Rocq/Coq fences, so a closing fence cannot
become a new opener. Kernel checks determine whether any recovered candidate
is a proof; extracting text alone is never a successful benchmark outcome.
"""

from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import gzip
import json
import re
import resource
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.queries import extract_final_block

from .common import CAMPAIGN, REPORT, allowed, digest, read, save, sha
from .economics import ledger_rows
from .verification import compile_one


def complete_proof_blocks(text: str) -> list[str]:
    return re.findall(r"```(?:rocq|coq)[ \t]*\r?\n(.*?)```", text, re.DOTALL)


def compile_candidate(row: dict[str, Any]) -> dict[str, Any]:
    candidate = row["candidate"]
    if candidate is None:
        return dict(receipt=row["receipt"], candidate=False, passed=False)
    try:
        result = compile_one(
            (allowed()[row["theorem"]][1], row["theorem"], candidate)
        )
    except ValueError as error:
        result = dict(passed=False, rejection=str(error))
    return dict(
        receipt=row["receipt"],
        candidate=True,
        kernel=result,
        passed=result["passed"],
    )


def run() -> None:
    destination = REPORT / "output_repetition_diagnosis.json"
    if destination.exists():
        prior = read(destination)
        for row in prior["replies"]:
            if sha(CAMPAIGN / row["response_file"]) != row["response_sha"]:
                raise ValueError("Diagnosed response changed")
        print(json.dumps(dict(cached=True, arms=prior["arms"]), indent=2))
        return
    receipt_rows = [
        r
        for r in ledger_rows()
        if r["stage"] == "solver"
        and r["cell"].startswith("validation__")
        and r["cell"].split("__")[1]
        in {"A0", "A1", "A2", "B0", "B1", "B2", "P1"}
    ]
    if any(r["status"] != "settled" for r in receipt_rows):
        raise ValueError("Unsettled validation receipt")
    arms: dict[str, dict[str, Any]] = defaultdict(
        lambda: dict(
            capped_calls=0,
            capped_charge=0.0,
            capped_output=0,
            raw_characters=0,
            typed_blocks=0,
            legacy_blank=0,
            candidates=0,
        )
    )
    rows: list[dict[str, Any]] = []
    for receipt in receipt_rows:
        usage = json.loads(receipt["usage"])
        if usage.get("status") != "incomplete":
            continue
        _, arm, theorem, _ = receipt["cell"].split("__")
        if allowed().get(theorem, (None,))[0] != "validation":
            raise ValueError("Unexpected diagnostic scope")
        path = (
            CAMPAIGN
            / "responses"
            / receipt["cell"]
            / (receipt["id"] + ".json.gz")
        )
        with gzip.open(path, "rt") as stream:
            raw = json.load(stream)
        response = raw["response"]
        if response["incomplete_details"]["reason"] != "max_output_tokens":
            raise ValueError("Unexpected incomplete-response category")
        text = "\n".join(
            part["text"]
            for message in response["output"]
            if message["type"] == "message"
            for part in message["content"]
            if part["type"] == "output_text"
        )
        blocks = complete_proof_blocks(text)
        legacy = extract_final_block(text)
        row = dict(
            cell=receipt["cell"],
            receipt=receipt["id"],
            theorem=theorem,
            response_file=str(path.relative_to(CAMPAIGN)),
            response_sha=sha(path),
            charge=receipt["charged"],
            usage=response["usage"],
            raw_characters=len(text),
            typed_complete_blocks=len(blocks),
            distinct_typed_blocks=len({digest(b) for b in blocks}),
            most_repeated_typed_block=max(
                Counter(digest(b) for b in blocks).values(), default=0
            ),
            legacy=legacy,
            candidate=blocks[-1] if blocks else None,
            input_sha=digest(raw["payload"]["input"]),
        )
        rows.append(row)
        summary = arms[arm]
        summary["capped_calls"] += 1
        summary["capped_charge"] += receipt["charged"]
        summary["capped_output"] += usage["output_tokens"]
        summary["raw_characters"] += len(text)
        summary["typed_blocks"] += len(blocks)
        summary["legacy_blank"] += int(
            legacy is not None and not legacy.strip()
        )
        summary["candidates"] += bool(blocks)
    protocol = CAMPAIGN / "output_repetition_protocol.json"
    save(
        protocol,
        dict(
            replies=rows,
            paid_calls=0,
            selection="All capped replies from the seven complete validationX panels. Choose the last explicitly typed complete block without editing its tactics. Retain failed kernel checks and all original benchmark outcomes.",
        ),
    )
    limit = 4096 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    with (
        patch("openai.OpenAI", side_effect=AssertionError("No HTTP")),
        ThreadPoolExecutor(max_workers=4) as pool,
    ):
        checks = list(pool.map(compile_candidate, rows))
    save(
        destination,
        dict(
            arms=dict(arms),
            replies=rows,
            kernel_checks=checks,
            recovered_candidates_compiling=sum(r["passed"] for r in checks),
            protocol_sha=sha(protocol),
            paid_calls=0,
            benchmark_outcomes_changed=0,
            limitation="The experiment diagnoses extraction and repeated output. Already incurred generation fees are not recovered. New solver behavior after different feedback, output limits or generation stopping is not simulated by this local parser check.",
        ),
    )
    print(
        json.dumps(
            dict(
                arms=dict(arms),
                replies=len(rows),
                candidates_compiling=sum(r["passed"] for r in checks),
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    run()
