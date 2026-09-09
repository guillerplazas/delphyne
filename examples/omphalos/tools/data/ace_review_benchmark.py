"""Freeze the previously unexposed ACE challenge population, before runs.

Selection uses statements and exposure metadata, never outcomes. Include
all unused non-Mathd miniF2F problems; quarantine entire exact/number-
template and contest-variant groups if any member was exposed. These
conservative filters are not a claim of semantic deduplication. Existing
reservations alone do not constitute exposure. Test/validation records
are read for identifiers only, never for their proof failures.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from functools import cache
from pathlib import Path
from typing import Any, cast

import yaml


import experiments.common.miniF2F_bench as mf  # noqa: E402
import runtime.pytanque_utils as pt  # noqa: E402

ROOT = OMPHALOS_ROOT

MANIFEST = ROOT / "benchmarks/ace_challenge_20260908.json"


def sha(data: object) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()


def category(name: str) -> str:
    return "amc" if name.startswith("amc") else name.split("_")[0]


def build() -> dict[str, Any]:
    paths = {
        p.stem: p
        for split in ("valid", "test")
        for p in (ROOT / "miniF2F" / split).rglob("*.v")
    }
    used: set[str] = set(mf._DEMO_PROBLEMS)  # pyright: ignore[reportPrivateUsage]
    provenance: dict[str, str] = {}
    for root in ("experiments/output", "experiments/previous"):
        for state in sorted((ROOT / root).glob("*/experiment.yaml")):
            raw: Any = yaml.load(state.read_text(), Loader=yaml.CSafeLoader)
            states = cast(dict[str, Any], raw if raw is not None else {})
            entries: dict[str, Any] = states.get("configs", {})
            for name, info in entries.items():
                bench = info.get("params", {}).get("bench_name")
                if bench in paths:
                    used.add(bench)
                first = name.split("__")[0]
                if first in paths:
                    used.add(first)
            provenance[str(state.relative_to(ROOT))] = hashlib.sha256(
                state.read_bytes()
            ).hexdigest()
        # Orphaned partial runs must not re-enter the holdout.
        for configs in (ROOT / root).glob("*/configs"):
            for d in configs.iterdir():
                for bench in (d.name.split("__")[0],):
                    if bench in paths:
                        used.add(bench)
                m = re.match(
                    r"step\d+_(?:generator|reflector|curator)_(.*)", d.name
                )
                if m and m[1] in paths:
                    used.add(m[1])
    for file in [
        *ROOT.glob("*.demo.yaml"),
        *(ROOT / "commands").glob("*.exec.yaml"),
    ]:
        text = file.read_text()
        for bench in paths:
            if re.search(rf"(?<![\w]){re.escape(bench)}(?![\w])", text):
                used.add(bench)
        provenance[str(file.relative_to(ROOT))] = hashlib.sha256(
            file.read_bytes()
        ).hexdigest()
    parent = {n: n for n in paths}

    def find(n: str) -> str:
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    groups: dict[str, list[str]] = defaultdict(list)
    for name, path in sorted(paths.items()):
        spec = pt.parse_problem(str(path), True)
        statement = re.sub(r"\s+", " ", spec.theorem_statement).strip()
        template = re.sub(r"\b\d+\b", "NUMBER", statement)
        groups["statement:" + template].append(name)
        # E.g. imo_1964_p1_1 and imo_1964_p1_2 stay together.
        if name.startswith(("imo_", "aime_", "amc")):
            groups["contest:" + re.sub(r"(_p\d+)_\d+$", r"\1", name)].append(
                name
            )
    for members in groups.values():
        for n in members[1:]:
            parent[find(n)] = find(members[0])
    exposed_groups = {find(n) for n in used if n in paths}
    challenge: dict[str, Any] = {}
    reserve: list[str] = []
    quarantined: list[str] = []
    for n, path in sorted(paths.items()):
        if n in used:
            continue
        if find(n) in exposed_groups:
            quarantined.append(n)
        elif n.startswith("mathd_"):
            reserve.append(n)
        else:
            challenge[n] = {
                "file": str(path.relative_to(ROOT)),
                "theorem": n,
                "category": category(n),
                "family": find(n),
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
    counts = Counter(row["category"] for row in challenge.values())
    quotas = {c: int(32 * n / len(challenge)) for c, n in counts.items()}
    order = sorted(
        counts,
        key=lambda c: (-(32 * counts[c] / len(challenge) - quotas[c]), c),
    )
    for c in order[: 32 - sum(quotas.values())]:
        quotas[c] += 1
    terra: list[str] = []
    for c, quota in sorted(quotas.items()):
        candidates = [n for n in challenge if category(n) == c]
        terra.extend(
            sorted(candidates, key=lambda n: sha([20260908, n]))[:quota]
        )
    return {
        "version": 1,
        "role": "confirmation_only",
        "seed": 20260908,
        "rule": "all unexposed non-Mathd, grouped before exclusion",
        "problems": challenge,
        "terra_subset": sorted(terra),
        "reserved_mathd": reserve,
        "quarantined": quarantined,
        "exposed": sorted(used),
        "exposure_sources": provenance,
    }


def load(path: Path = MANIFEST) -> dict[str, Any]:
    raw = json.loads(path.read_text())
    digest = raw.pop("sha256")
    if sha(raw) != digest:
        raise ValueError("challenge manifest was modified")
    raw["sha256"] = digest
    for row in raw["problems"].values():
        if (
            hashlib.sha256((ROOT / row["file"]).read_bytes()).hexdigest()
            != row["source_sha256"]
        ):
            raise ValueError("benchmark statement changed")
    return raw


@cache
def _protected() -> set[str]:
    manifest = load()
    return set(manifest["problems"]) | set(manifest["reserved_mathd"])


def assert_training_allowed(names: list[str]) -> None:
    if MANIFEST.exists():
        overlap = set(names) & _protected()
        if overlap:
            raise ValueError(
                f"protected ACE challenge problems: {sorted(overlap)}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    if MANIFEST.exists():
        result = load()
    else:
        result = build()
        result["sha256"] = sha(result)
        if args.freeze:
            with MANIFEST.open("x") as f:
                f.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "sha256": result["sha256"],
                "challenge": len(result["problems"]),
                "families": len(
                    {r["family"] for r in result["problems"].values()}
                ),
                "categories": dict(
                    Counter(r["category"] for r in result["problems"].values())
                ),
                "terra_subset": len(result["terra_subset"]),
                "reserved_mathd": len(result["reserved_mathd"]),
                "quarantined": result["quarantined"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
