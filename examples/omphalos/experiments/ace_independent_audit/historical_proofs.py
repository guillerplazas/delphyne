"""Compile every distinct returned historical development proof.

The census distinguishes proof-producing strategies from learning roles.
A parsed curator output is never a solved benchmark theorem. No old report
or claimed success flag substitutes for compiling the returned script.
"""

from concurrent.futures import ThreadPoolExecutor
import json
from typing import Any

from .analysis import historical
from .common import REPORT, ROOT, allowed, digest, save, sha
from .verification import compile_one


def checked(item: tuple[str, str, str]) -> dict[str, Any]:
    try:
        return compile_one(item)
    except Exception as exc:
        return dict(
            passed=False,
            theorem=item[1],
            proof_sha=digest(item[2]),
            error=type(exc).__name__ + ": " + str(exc),
        )


def run() -> None:
    rows = historical()
    selected = [
        r
        for r in rows
        if str(r["config"]["strategy"]).startswith("prove") and r["value"]
    ]
    proofs: dict[tuple[str, str, str], list[str]] = {}
    for row in selected:
        directory = ROOT / row["path"]
        if sha(directory / "result.yaml") != row["result_sha"]:
            raise ValueError("Historical result changed after census")
        for value in row["value"]:
            if not isinstance(value, str):
                raise ValueError("Unknown historical proof return type")
            key = (allowed()[row["theorem"]][1], row["theorem"], value)
            proofs.setdefault(key, []).append(row["path"])
    print(
        json.dumps(
            dict(
                historical_solved_cells=len(selected),
                unique_proofs=len(proofs),
                phase="compiling",
            )
        ),
        flush=True,
    )
    certificates: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for index, (key, result) in enumerate(
            zip(proofs, pool.map(checked, proofs), strict=True), 1
        ):
            row = dict(result, cells=proofs[key])
            certificates.append(row)
            if not result["passed"] or index % 100 == 0:
                print(
                    json.dumps(
                        dict(
                            completed=index,
                            total=len(proofs),
                            theorem=key[1],
                            passed=result["passed"],
                            diagnostic=result.get(
                                "error", result.get("stderr")
                            )
                            if not result["passed"]
                            else None,
                        )
                    ),
                    flush=True,
                )
    failed = [r for r in certificates if not r["passed"]]
    failed_cells = sorted({p for r in failed for p in r["cells"]})
    save(
        REPORT / "historical_proof_certification.json",
        dict(
            solved_result_cells=len(selected),
            unique_proofs=len(proofs),
            compiled=sum(r["passed"] for r in certificates),
            failed_cells=failed_cells,
            certificates=certificates,
            paid_calls=0,
            note="Every distinct string proof returned by a prove* strategy in the allowed raw census. Source statements are read only after exact trainX/validationX membership. Archive repetition may associate several cells with one compiled proof; it creates no extra statistical sample.",
        ),
    )
    print(
        json.dumps(
            dict(
                final=True,
                solved_result_cells=len(selected),
                unique_proofs=len(proofs),
                failures=len(failed),
                failed_cells=len(failed_cells),
                paid_calls=0,
            )
        ),
        flush=True,
    )


if __name__ == "__main__":
    run()
