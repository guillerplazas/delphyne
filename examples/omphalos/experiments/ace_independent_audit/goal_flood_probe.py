"""Count goals from one saved proposal, without automatic search or HTTP.

Both harnesses: ``python -m experiments.ace_independent_audit.goal_flood_probe``.
This diagnostic uses the exact fourteenth P1 response on one validationX
problem. It changes only diagnostic probing/rendering, never a paid worker,
book, cache, benchmark outcome, or source file. The original tactic deadline
and four-gigabyte worker address-space limit are retained.
"""

from dataclasses import asdict
import gzip
import json
import re
import resource
import sqlite3
import time
from unittest.mock import patch

from runtime import pytanque_utils as pt

from .common import CAMPAIGN, REPORT, allowed, now, read, save, sha
from .campaign import activate

CELL = "validation__P1__amc12a_2020_p21__seed0"
THEOREM = "amc12a_2020_p21"


def run() -> None:
    with sqlite3.connect(
        f"file:{CAMPAIGN / 'ledger.sqlite3'}?mode=ro", uri=True
    ) as db:
        receipts = db.execute(
            "SELECT id, status FROM receipts WHERE cell = ? ORDER BY created",
            (CELL,),
        ).fetchall()
    identity, status = receipts[13]
    if status != "settled" or allowed()[THEOREM][0] != "validation":
        raise ValueError("Expected a settled permitted source response")
    path = CAMPAIGN / "responses" / CELL / (identity + ".json.gz")
    result_file = REPORT / "goal_flood_probe.json"
    if result_file.exists():
        prior = read(result_file)
        if prior["response_sha"] != sha(path):
            raise ValueError("The diagnosed response changed")
        print(json.dumps(dict(cached=True, result=prior), indent=2))
        return
    with gzip.open(path, "rt") as stream:
        raw = json.load(stream)
    texts = [
        item["text"]
        for message in raw["response"]["output"]
        if message["type"] == "message"
        for item in message["content"]
        if item["type"] == "output_text"
    ]
    text = "\n".join(texts).strip()
    if not text.startswith("```rocq\n") or not text.endswith("```"):
        raise ValueError("Unexpected saved proof encoding")
    script = text.removeprefix("```rocq\n").removesuffix("```").strip()
    protocol = dict(
        registered_at=now(),
        cell=CELL,
        response_ordinal=14,
        response_file=str(path.relative_to(CAMPAIGN)),
        response_sha=sha(path),
        script=script,
        intervention="Disable automation search; show one goal and the total-count marker. Preserve the exact saved proposal and original tactic deadlines.",
        purpose="Determine whether the ongoing verifier delay is caused by a generated goal flood. This is not a replacement solver attempt or an estimate of a capped solver's coverage/cost.",
        paid_calls=0,
    )
    destination = CAMPAIGN / "goal_flood_probe_protocol.json"
    if not destination.exists():
        save(destination, protocol)
    activate()
    limit = 4096 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    started = time.monotonic()
    try:
        with patch("openai.OpenAI", side_effect=AssertionError("No HTTP")):
            feedback = pt.check(
                allowed()[THEOREM][1],
                THEOREM,
                pt.split_into_tactics(script),
                probe_automation=False,
                goal_caps=pt.GoalCaps(probe=0, render=1, render_chars=1000),
            )
    finally:
        pt.MANAGER.recycle("completed isolated goal-count diagnostic")
    elapsed = time.monotonic() - started
    total = len(feedback.remaining_goals)
    for goal in feedback.remaining_goals:
        match = re.search(r"of (\d+) listed", goal)
        if match:
            total = int(match[1])
    result = dict(
        cell=CELL,
        response_sha=sha(path),
        feedback=asdict(feedback),
        remaining_goal_count=total,
        seconds=elapsed,
        paid_calls=0,
        meaning=__doc__,
    )
    save(result_file, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run()
