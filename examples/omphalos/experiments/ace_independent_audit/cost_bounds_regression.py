"""Reproduce exact-statistics parity from the preserved checkpoint source.

The recorded comparison originally used the staged checkpoint source. Its
identical bytes remain in the immutable review snapshot, so this check does
not depend on the current Git index or import an old campaign entry point.
Only the pure paired-statistics function is evaluated. No model calls.
"""

import ast
from collections import defaultdict
import hashlib
import json
import tarfile
from typing import Any, cast

import numpy as np

from .analysis import paired
from .common import CAMPAIGN, REPORT, read


def run() -> None:
    recorded = read(CAMPAIGN / "cost_bounds_exact_regression.json")
    with tarfile.open(
        REPORT / "checkpoint_review_snapshot.tar.gz", "r:gz"
    ) as archive:
        stream = archive.extractfile(
            "experiments/ace_independent_audit/analysis.py"
        )
        if stream is None:
            raise ValueError("Checkpoint source is missing")
        source = stream.read()
    if hashlib.sha256(source).hexdigest() != recorded["original_analysis_sha"]:
        raise ValueError("Original statistics source changed")
    function = next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name == "paired"
    )
    namespace: dict[str, Any] = dict(
        Any=Any, cast=cast, defaultdict=defaultdict, np=np
    )
    exec(
        compile(
            ast.Module(body=[function], type_ignores=[]),
            "<checkpoint-paired>",
            "exec",
        ),
        namespace,
    )
    original = namespace["paired"]
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in read(REPORT / "checkpoint_cells.json"):
        groups[row["stage"], row["arm"]].append(row)
    checks: list[dict[str, Any]] = []
    for (stage, arm), rows in groups.items():
        if arm in ("A0", "B0"):
            continue
        control = "B0" if arm.removeprefix("online_").startswith("B") else "A0"
        baseline = {
            (r["theorem"], r["seed"]): r for r in groups[stage, control]
        }
        candidate = {(r["theorem"], r["seed"]): r for r in rows}
        keys = baseline.keys() & candidate.keys()
        if len(keys) < 2:
            continue
        before = [r for k, r in baseline.items() if k in keys]
        after = [r for k, r in candidate.items() if k in keys]
        if original(before, after) != paired(before, after):
            raise ValueError("Exact statistics changed: " + stage + "/" + arm)
        checks.append(
            dict(
                stage=stage,
                arm=arm,
                cells=len(keys),
                byte_equivalent_statistics=True,
            )
        )
    if checks != recorded["comparisons"]:
        raise ValueError("Exact-statistics comparison scope changed")
    print(json.dumps(dict(comparisons=len(checks), passed=True, paid_calls=0)))


if __name__ == "__main__":
    run()
