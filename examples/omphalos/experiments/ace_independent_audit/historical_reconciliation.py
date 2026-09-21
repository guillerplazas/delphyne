"""Resolve archived continuations without counting replayed calls twice.

Only the independently inventoried trainX/validationX cells are read. A
continuation must declare prefix_cache and contain every saved prefix entry
byte-for-byte after canonical YAML decoding. Independent failed attempts
remain spending evidence. No historical report or mixed ledger is opened.
"""

from collections import Counter, defaultdict
from copy import deepcopy
import json
from typing import Any

from .analysis import historical, metrics
from .audit import load_yaml
from .catalog import label, write_csv
from .common import REPORT, ROOT, digest, save


def entries(row: dict[str, Any]) -> Counter[str]:
    path = ROOT / row["path"] / "cache.yaml"
    return (
        Counter(digest(v) for v in load_yaml(path))
        if path.exists()
        else Counter()
    )


def reconcile(
    rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    final = [r for r in rows if r["config"].get("strategy")]
    if len(rows) == 1:
        return rows[0], dict(kind="single", paths=[rows[0]["path"]])
    if len(final) != 1:
        raise ValueError(
            "Ambiguous archived final result: "
            + str([r["path"] for r in rows])
        )
    chosen = deepcopy(final[0])
    older = [r for r in rows if r is not final[0]]
    policy: dict[str, Any] = chosen["config"].get("policy_args") or {}
    if not policy.get("prefix_cache"):
        raise ValueError(
            "Repeated cell without declared continuation: " + chosen["path"]
        )
    complete = entries(chosen)
    prefix_checks: list[dict[str, Any]] = []
    for row in older:
        prefix = entries(row)
        missing = prefix - complete
        if missing:
            raise ValueError(
                "Continuation omitted or changed archived evidence: "
                + row["path"]
            )
        prefix_checks.append(
            dict(
                path=row["path"],
                entries=sum(prefix.values()),
                requests=row["counts"].get("requests", 0),
                observed_cost=row["costs"].get("price", 0),
                exact_subset=True,
            )
        )
    return chosen, dict(
        kind="declared_exact_prefix_continuation",
        final=chosen["path"],
        declared_prefix=policy["prefix_cache"],
        prefixes=prefix_checks,
        duplicated_cost=sum(r["costs"].get("price", 0) for r in older),
    )


def run() -> None:
    raw = historical()
    exceptions = [
        json.loads(line) for line in (REPORT / "exception_cells.jsonl").open()
    ]
    groups: dict[
        tuple[str, str, str, str, int | None], list[dict[str, Any]]
    ] = defaultdict(list)
    for row in [*raw, *exceptions]:
        strategy = row["config"].get("strategy")
        if strategy and not str(strategy).startswith("prove"):
            continue
        groups[
            row["campaign"],
            row["stage"],
            label(row),
            row["theorem"],
            row["seed"],
        ].append(row)
    panels: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    receipts: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for key, rows in groups.items():
        row, receipt = reconcile(rows)
        panels[key[:3]].append(row)
        selected.append(row)
        if len(rows) > 1:
            receipts.append(dict(key=key, **receipt))
    summary: list[dict[str, Any]] = []
    for (campaign, stage, arm), rows in sorted(panels.items()):
        if not any(r["config"].get("strategy") for r in rows):
            continue
        summary.append(
            dict(
                campaign=campaign,
                stage=stage,
                label=arm,
                platform_errors=sum(
                    r.get("status") == "platform_error" for r in rows
                ),
                **metrics(rows),
            )
        )
    save(
        REPORT / "historical_continuations.json",
        dict(
            groups=receipts,
            removed_duplicate_cost=sum(
                r.get("duplicated_cost", 0) for r in receipts
            ),
            rule="Only explicitly declared continuation caches with exact saved prefix inclusion are deduplicated. No zero-bill inference is made for missing transport metadata.",
        ),
    )
    save(
        REPORT / "historical_selected_paths.json",
        [r["path"] for r in selected],
    )
    write_csv(REPORT / "historical_reconciled_panels.csv", summary)
    print(json.dumps(dict(continuations=len(receipts), panels=len(summary))))


if __name__ == "__main__":
    run()
