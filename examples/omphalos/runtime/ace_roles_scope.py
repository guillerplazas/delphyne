"""Data boundary for the $40 ACE roles campaign, shared by both harnesses.

Install before experiment imports. Prior paid measurements are read-only;
only explicitly listed development sources and the new campaign are allowed.
"""

from runtime.development_only import install as install_base

import json
import os
from pathlib import Path
import sys
from typing import Any

from runtime.paths import OMPHALOS_ROOT as ROOT

NAME = "ace_roles_20260913"
_installed = False


def install() -> None:
    global _installed
    install_base()
    if _installed:
        return
    refs = json.loads(
        (
            ROOT
            / "experiments/campaigns/ace_attribution_20260912/references.json"
        ).read_text()
    )
    terminals = json.loads(
        (
            ROOT
            / "experiments/campaigns/ace_capacity_20260912/creator_terminal_evidence.json"
        ).read_text()
    )
    archives = {
        (ROOT / r["source"] / "configs" / r["name"]).resolve()
        for rows in refs.values()
        for r in rows
    }
    archives.update((ROOT / r["source"]).resolve() for r in terminals)
    allowed = {
        NAME,
        "ace_snippets_20260913",
        "resource_completion_20260913",
        "ace_capacity_20260912",
        "ace_attribution_20260912",
    }
    permitted = {
        (ROOT / line.strip()).resolve()
        for part in ("trainX", "validationX")
        for line in (ROOT / f"benchmarks/{part}.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    mixed = {
        ROOT / p
        for p in (
            "memory/MEMORY.md",
            "HINTS.md",
            "PROGRESS.md",
            "docs/CLOSED_HINTS.md",
            "docs/thesis_decisions.md",
        )
    }
    current = ROOT / "experiments/campaigns" / NAME
    output = ROOT / "experiments/output" / NAME

    def audit(event: str, args: tuple[Any, ...]) -> None:
        if (
            event != "open"
            or not args
            or not isinstance(args[0], (str, bytes))
        ):
            return
        p = Path(os.path.realpath(os.fsdecode(args[0])))
        if not p.is_relative_to(ROOT):
            return
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else 0
        writing = (
            isinstance(mode, str)
            and any(c in mode for c in "wa+")
            or isinstance(flags, int)
            and bool(
                flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            )
        )
        denied = p in mixed
        if p.is_relative_to(ROOT / "miniF2F"):
            denied |= p not in permitted or writing
        if p.is_relative_to(ROOT / "benchmarks"):
            denied |= (
                p.name not in ("trainX.txt", "validationX.txt") or writing
            )
        if p.is_relative_to(ROOT / "experiments/campaigns"):
            denied |= (
                p.relative_to(ROOT / "experiments/campaigns").parts[0]
                not in allowed
            )
            denied |= writing and not p.is_relative_to(current)
        if p.is_relative_to(ROOT / "experiments/output"):
            legacy = ROOT / "experiments/output/ace_snippets_20260913"
            denied |= not (
                p.is_relative_to(output)
                or p.is_relative_to(legacy)
                or any(p.is_relative_to(a) for a in archives)
            )
            denied |= writing and not p.is_relative_to(output)
        if p.is_relative_to(ROOT / "experiments/previous"):
            denied = True
        if denied:
            raise PermissionError(
                "ACE roles development scope denied: " + str(p)
            )

    sys.addaudithook(audit)
    _installed = True
