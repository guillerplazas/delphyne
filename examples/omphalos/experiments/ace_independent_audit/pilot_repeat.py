"""Separate pilot-repeat behavior from performance on additional trainX tasks.

Both harnesses: ``python -m experiments.ace_independent_audit.pilot_repeat``.
The selected book is unchanged. This analyzes already paid, completed cells;
it does not select another book or purchase another replicate.
"""

from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import json
from typing import Any

from .analysis import metrics, paired
from .audit import cell, load_yaml
from .common import CAMPAIGN, OUTPUT, REPORT, allowed, now, read, save, sha
from .completion import require_closed
from .fresh import receipts


def inspect(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
    batch, job = item
    if job["stage"] != "train":
        raise ValueError("This diagnostic uses trainX only")
    identity = f"train__{job['arm']}__{job['theorem']}__seed{job['seed']}"
    path = OUTPUT / batch / "configs" / identity
    row = cell((str(path), job["theorem"]))
    cache = load_yaml(path / "cache.yaml")
    request = next(
        r["input"]["request"]
        for r in cache
        if r["input"]["request"]["options"].get("model") != "__compute__"
    )
    return dict(
        {
            k: row[k]
            for k in (
                "theorem",
                "seed",
                "solved",
                "costs",
                "counts",
                "exact_cost",
                "turns",
                "cache_sha",
                "result_sha",
            )
        },
        cell=identity,
        arm=job["arm"],
        first_request=request,
    )


def run() -> None:
    batches = ["author_pilot", "core_pilot_book-part00"]
    batches += [f"online-o{o}-s{s:02d}" for o in (0, 1) for s in range(40)]
    items: list[tuple[str, dict[str, Any]]] = []
    for batch in batches:
        require_closed(batch)
        items.extend(
            (batch, j)
            for j in read(CAMPAIGN / "batches" / (batch + ".json"))
            if j["stage"] == "train"
            and j["arm"] in ("author_none", "ladder_v2_sol_medium", "A0", "P1")
        )
    with ProcessPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(inspect, items))
    if len(rows) != 184:
        raise ValueError("Expected24 original pilot and160 full trainX cells")
    ledger = receipts()
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        paid = ledger[row["cell"]]
        if (
            set(paid["statuses"]) != {"settled"}
            or not row["exact_cost"]
            or paid["requests"] != row["counts"]["requests"]
            or abs(paid["cost"] - row["costs"]["price"]) > 1e-9
        ):
            raise ValueError("Pilot-repeat billing mismatch")
        groups[row["arm"]].append(row)
    pilot = {r["theorem"] for r in groups["author_none"]}
    sources = set(read(CAMPAIGN / "ladder_v2_protocol.json")["train_panel"])
    all_names = {r["theorem"] for r in groups["A0"]}
    subsets = {
        "pilot_12": pilot,
        "additional_28": all_names - pilot,
        "source_8": sources,
        "non_source_32": all_names - sources,
    }
    results: dict[str, Any] = {}
    for label, names in subsets.items():
        base = [r for r in groups["A0"] if r["theorem"] in names]
        arm = [r for r in groups["P1"] if r["theorem"] in names]
        results[label] = dict(
            baseline=metrics(base), p1=metrics(arm), paired=paired(base, arm)
        )
    first_requests: list[dict[str, Any]] = []
    for original_arm, full_arm in (
        ("author_none", "A0"),
        ("ladder_v2_sol_medium", "P1"),
    ):
        indexed = {r["theorem"]: r for r in groups[original_arm]}
        for row in groups[full_arm]:
            if row["theorem"] not in indexed:
                continue
            first_requests.append(
                dict(
                    original_cell=indexed[row["theorem"]]["cell"],
                    repeated_cell=row["cell"],
                    first_request_equal=row["first_request"]
                    == indexed[row["theorem"]]["first_request"],
                )
            )
    save(
        REPORT / "pilot_repeat_diagnosis.json",
        dict(
            original_pilot={
                a: metrics(groups[a])
                for a in ("author_none", "ladder_v2_sol_medium")
            },
            full_train_subsets=results,
            first_requests=first_requests,
            cells=[
                {
                    k: v
                    for k, v in r.items()
                    if k not in ("first_request", "turns")
                }
                for r in rows
            ],
            interpretation="Descriptive post-selection diagnosis. Original pilot has one paid draw per theorem; full trainX has two new draws. Compare repeat behavior on the same12theorems with transfer to the additional28; no new model calls or reselection. Initial request identity does not establish identity of later stochastic outputs or exception-handling paths.",
        ),
    )
    print(json.dumps(results, indent=2))
    print(
        "Identical first requests:",
        sum(r["first_request_equal"] for r in first_requests),
        "/",
        len(first_requests),
    )


def repair() -> None:
    """Test whether one missing symmetry instance explains a failed path."""
    from unittest.mock import patch

    from .verification import compile_one

    theorem = "aime_1988_p8"
    identity = f"train__P1__{theorem}__seed0"
    directory = OUTPUT / "core_pilot_book-part00" / "configs" / identity
    require_closed("core_pilot_book-part00")
    original = cell((str(directory), theorem))
    check = original["checks"][1]
    tactics: list[str] = check["args"]["tactics"]
    if tactics[-1] != "nra." or not tactics[-2].startswith("cbn in H1,"):
        raise ValueError("The failed second proposal changed")
    addition = "pose proof (Hsym 10%nat 4%nat P10 P4) as H11."
    revised = [*tactics[:-2], addition, *tactics[-2:]]
    proposal = dict(
        cell=identity,
        cache_sha=original["cache_sha"],
        result_sha=original["result_sha"],
        original_script="\n".join(tactics),
        added_fact=addition,
        revised_script="\n".join(revised),
        original_failure=check["feedback"].get("error_message"),
    )
    protocol = CAMPAIGN / "pilot_dependency_repair_protocol.json"
    if not protocol.exists():
        save(
            protocol,
            dict(
                registered_at=now(),
                proposal=proposal,
                decision="Keep every original tactic; add only the missing f(10,4)=f(4,10) symmetry instance before the existing normalization and nra. Independently compile against the original trainX statement. Preserve any failed probe and the original unsolved benchmark outcome.",
                paid_calls=0,
            ),
        )
    elif read(protocol)["proposal"] != proposal:
        raise ValueError("The registered dependency repair changed")
    with patch("openai.OpenAI", side_effect=AssertionError("No HTTP")):
        kernel = compile_one(
            (allowed()[theorem][1], theorem, proposal["revised_script"])
        )
    save(
        REPORT / "pilot_dependency_repair.json",
        dict(
            **proposal,
            kernel=kernel,
            protocol_sha=sha(protocol),
            paid_calls=0,
            benchmark_outcomes_changed=0,
            interpretation="A successful probe establishes that the recorded early proof was missing one relational premise, not that nra lacked power to finish it. This is a local hand repair; it is not a new solver sample or a measured learning-policy benefit.",
        ),
    )
    print(
        json.dumps(dict(cell=identity, passed=kernel["passed"], paid_calls=0))
    )


if __name__ == "__main__":
    import sys

    if sys.argv[1:] != ["repair"]:
        run()
    repair()
