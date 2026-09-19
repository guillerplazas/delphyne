"""Prospective selection, complete panels and family-aware ordering."""

import hashlib
import re
from typing import Any

from experiments.ace_sanitized.scope import partition
from runtime.pytanque_utils import parse_problem


def families(stage: str) -> dict[str, str]:
    problems = partition(stage)
    parent = {n: n for n in problems}

    def find(n: str) -> str:
        while parent[n] != n:
            n = parent[n]
        return n

    templates: dict[str, str] = {}
    for name, path in sorted(problems.items()):
        statement = re.sub(
            r"\b\d+\b",
            "NUMBER",
            " ".join(parse_problem(path, True).theorem_statement.split()),
        )
        keys = [statement]
        if name.startswith(("imo_", "aime_", "amc")):
            keys.append(re.sub(r"(_p\d+)_\d+$", r"\1", name))
        for key in keys:
            if key in templates:
                parent[find(name)] = find(templates[key])
            else:
                templates[key] = name
    return {n: find(n) for n in problems}


def hash_order(names: list[str]) -> list[str]:
    return sorted(
        names,
        key=lambda n: hashlib.sha256(
            ("ace-thesis-20260918:" + n).encode()
        ).hexdigest(),
    )


def training_panel() -> list[str]:
    mapping = families("train")
    selected: list[str] = []
    seen: set[str] = set()
    for mathd in (False, True):
        group: list[str] = []
        for n in hash_order(list(mapping)):
            if n.startswith("mathd_") != mathd or mapping[n] in seen:
                continue
            group.append(n)
            seen.add(mapping[n])
            if len(group) == 6:
                break
        if len(group) != 6:
            raise ValueError("Insufficient distinct training families")
        selected += group
    return selected


def schedule(
    theorems: list[str], arms: list[str]
) -> list[tuple[str, int, str]]:
    """Rotate arm order by theorem and reverse it in the second replicate."""
    rows: list[tuple[str, int, str]] = []
    for seed in (0, 1):
        for i, theorem in enumerate(hash_order(theorems)):
            offset = i % len(arms)
            order = arms[offset:] + arms[:offset]
            for arm in order if seed == 0 else reversed(order):
                rows.append((theorem, seed, arm))
    return rows


def select(values: dict[str, dict[str, Any]], minimum: int) -> str:
    if not values or len({v["cells"] for v in values.values()}) != 1:
        raise ValueError("Selection requires complete matched panels")
    eligible = [a for a, v in values.items() if v["solved"] >= minimum]
    if not eligible:
        raise ValueError("No candidate preserves the coverage floor")
    return min(
        eligible,
        key=lambda a: (
            values[a]["cost"] / values[a]["solved"]
            if values[a]["solved"]
            else float("inf"),
            -values[a]["solved"],
            values[a]["cost"],
            values[a]["artifact_sha256"],
        ),
    )
