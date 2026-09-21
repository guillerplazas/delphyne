"""Complete descriptive census from directly parsed development cells.

Archive labels organize tables; executable contracts and book hashes identify
treatments. Learning outputs are never counted as solved benchmark problems.
Exception-only cells and archived attempts remain visible.
"""

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
from typing import Any

from .analysis import historical, metrics, normalized
from .common import REPORT, digest, save
from experiments.ace_sanitized.scope import partition


def logical_path(path: str) -> str:
    return re.split(r"/(?:\.attempts|attempts)/", path)[0]


def label(row: dict[str, Any]) -> str:
    path = logical_path(row["path"])
    leaf = path.rsplit("/", 1)[-1].replace(row["theorem"], "{theorem}")
    leaf = re.sub(r"seed[_-]?\d+", "seed*", leaf)
    if row["campaign"].startswith("ace_online_"):
        leaf = re.sub(r"ace-[0-9a-f]{8}", "ace-<evolving>", leaf)
    return leaf


def compact_config(config: dict[str, Any], theorem: str) -> dict[str, Any]:
    result = normalized(config, theorem)
    sa: dict[str, Any] = result.get("strategy_args") or {}
    for field in (
        "playbook",
        "claims",
        "evidence",
        "trajectory",
        "reflection",
    ):
        value = sa.get(field)
        if value:
            sa[field] = dict(sha=digest(value), chars=len(str(value)))
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run() -> None:
    raw = historical()
    exceptions = [
        json.loads(line) for line in (REPORT / "exception_cells.jsonl").open()
    ]
    # An attempt archive is spending evidence, never an extra theorem replicate.
    attempts = [
        r for r in [*raw, *exceptions] if logical_path(r["path"]) != r["path"]
    ]
    primary = [
        r for r in [*raw, *exceptions] if logical_path(r["path"]) == r["path"]
    ]
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    roles: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in primary:
        strategy = row["config"].get("strategy")
        if strategy and not str(strategy).startswith("prove"):
            roles[
                (row["campaign"], strategy, ";".join(sorted(row["models"])))
            ].append(row)
        else:
            groups[(row["campaign"], row["stage"], label(row))].append(row)
    panels: list[dict[str, Any]] = []
    manifests: list[dict[str, Any]] = []
    for (campaign, stage, arm), rows in sorted(groups.items()):
        known = [r for r in rows if r["config"].get("strategy")]
        # Exception-only learning roles cannot be assigned a proof contract.
        if not known and any(
            t in arm for t in ("curator", "reflector", "reducer", "schema")
        ):
            continue
        configs = {
            digest(normalized(r["config"], r["theorem"])): compact_config(
                r["config"], r["theorem"]
            )
            for r in known
        }
        by_cell = Counter((r["theorem"], r["seed"]) for r in rows)
        seeds = sorted({r["seed"] for r in rows if r["seed"] is not None})
        expected = {(t, s) for t in partition(stage) for s in seeds}
        actual = set(by_cell)
        complete = (
            bool(seeds) and actual == expected and max(by_cell.values()) == 1
        )
        m = metrics(rows)
        row = dict(
            campaign=campaign,
            stage=stage,
            label=arm,
            strategy=";".join(
                sorted({r["config"]["strategy"] for r in known})
            ),
            models=";".join(
                sorted({model for r in rows for model in r["models"]})
            ),
            configurations=len(configs),
            seed_values=";".join(map(str, seeds)),
            full_partition=complete,
            expected_full_partition_cells=len(expected),
            missing_full_partition_cells=len(expected - actual),
            duplicated_theorem_seed_cells=sum(n > 1 for n in by_cell.values()),
            platform_errors=sum(
                r.get("status") == "platform_error" for r in rows
            ),
            **m,
        )
        panels.append(row)
        manifests.append(
            dict(
                **row,
                contracts=configs,
                cells=[r["path"] for r in rows],
                missing=sorted(expected - actual),
            )
        )
    learning: list[dict[str, Any]] = []
    for (campaign, role, models), rows in sorted(roles.items()):
        learning.append(
            dict(
                campaign=campaign,
                role=role,
                models=models,
                outputs=len(rows),
                parsed_outputs=sum(bool(r["value"]) for r in rows),
                requests=sum(r["counts"].get("requests", 0) for r in rows),
                normalized_cost=sum(r["costs"].get("price", 0) for r in rows),
                reasoning_tokens=sum(
                    r["counts"].get("reasoning_tokens", 0) for r in rows
                ),
            )
        )
    duplicates: dict[str, list[str]] = defaultdict(list)
    for row in raw:
        if row["cache_sha"]:
            duplicates[row["cache_sha"]].append(row["path"])
    save(
        REPORT / "historical_catalog.json",
        dict(
            observed_result_cells=len(raw),
            observed_exception_only_cells=len(exceptions),
            archive_attempt_cells=[r["path"] for r in attempts],
            solver_panels=manifests,
            learning=learning,
            exception_types=dict(
                Counter(r["exception"].splitlines()[-1] for r in exceptions)
            ),
            byte_identical_caches=[
                v for v in duplicates.values() if len(v) > 1
            ],
            caveats=[
                "Current normalized tariff, not historical invoices. No aggregate reports used.",
                "An expected full partition is a descriptive reference; small registered pilots are not automatically incomplete experiments.",
                "Multiple contract hashes require inspection before treating a label as one controlled treatment.",
                "Exception-only cells with unknown strategy remain unclassified unless a same-label result supplies the contract; never infer an unobserved model or zero-bill certainty.",
                "Historical per-cell finality cannot be certified from a result file alone. Complete archived panels support retrospective description; explicit completion receipts certify new core measurements.",
            ],
        ),
    )
    write_csv(REPORT / "historical_solver_panels.csv", panels)
    write_csv(REPORT / "historical_learning_roles.csv", learning)
    print(
        json.dumps(
            dict(
                panels=len(panels),
                full_partition=sum(r["full_partition"] for r in panels),
                learning_groups=len(learning),
                archived_attempts=len(attempts),
            )
        )
    )


if __name__ == "__main__":
    run()
