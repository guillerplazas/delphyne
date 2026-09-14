"""Explicit data allowlist for the resource-completion campaign.

Install before experiment imports in either harness. The general guard is
retained; this additionally blocks mixed histories and unrelated archives.
"""

# ruff: noqa: E402 -- install the base guard before experiment data access
from runtime.development_only import install as install_development

install_development()

import json
import os
from pathlib import Path
import sys
from typing import Any

from runtime.paths import OMPHALOS_ROOT as ROOT

CAMPAIGN_NAME = "resource_completion_20260913"
_installed = False


def install() -> None:
    global _installed
    if _installed:
        return
    campaign = ROOT / "experiments/campaigns" / CAMPAIGN_NAME
    output = ROOT / "experiments/output" / CAMPAIGN_NAME
    # Explicitly authorized continuation of the same development-only work.
    snippet_name = "ace_snippets_20260913"
    snippet_output = ROOT / "experiments/output" / snippet_name
    refs = json.loads(
        (
            ROOT
            / (
                "experiments/campaigns/ace_attribution_20260912/references.json"
            )
        ).read_text()
    )
    terminal = json.loads(
        (
            ROOT
            / (
                "experiments/campaigns/ace_capacity_20260912/creator_terminal_evidence.json"
            )
        ).read_text()
    )
    archives = {
        (ROOT / r["source"] / "configs" / r["name"]).resolve()
        for rows in refs.values()
        for r in rows
    }
    archives.update((ROOT / r["source"]).resolve() for r in terminal)
    permitted_problems: set[Path] = set()
    for name in ("trainX", "validationX"):
        for line in (ROOT / f"benchmarks/{name}.txt").read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                permitted_problems.add((ROOT / line.strip()).resolve())
    allowed_campaigns = {
        "ace_attribution_20260912",
        "ace_capacity_20260912",
        "ace_mechanisms_20260910",
        CAMPAIGN_NAME,
        snippet_name,
    }
    mixed = {
        ROOT / "memory/MEMORY.md",
        ROOT / "HINTS.md",
        ROOT / "PROGRESS.md",
        ROOT / "docs/CLOSED_HINTS.md",
        ROOT / "docs/thesis_decisions.md",
    }

    def audit(event: str, args: tuple[Any, ...]) -> None:
        if (
            event != "open"
            or not args
            or not isinstance(args[0], (str, bytes))
        ):
            return
        path = Path(os.path.realpath(os.fsdecode(args[0])))
        if not path.is_relative_to(ROOT):
            return
        denied = path in mixed
        if path.is_relative_to(ROOT / "miniF2F"):
            denied |= path.resolve() not in permitted_problems
        if path.is_relative_to(ROOT / "benchmarks"):
            denied |= path.name not in ("trainX.txt", "validationX.txt")
        if path.is_relative_to(ROOT / "experiments/output"):
            denied |= not (
                path.is_relative_to(output)
                or path.is_relative_to(snippet_output)
                or any(path.is_relative_to(p) for p in archives)
            )
        if path.is_relative_to(ROOT / "experiments/previous"):
            denied = True
        if path.is_relative_to(ROOT / "experiments/campaigns"):
            relative = path.relative_to(ROOT / "experiments/campaigns")
            denied |= relative.parts[0] not in allowed_campaigns
        # Frozen input files are read-only even during offline verification.
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 else 0
        writing = (
            (isinstance(mode, str) and any(c in mode for c in "wa+"))
            or isinstance(flags, int)
            and bool(
                flags & (os.O_WRONLY | os.O_RDWR | os.O_TRUNC | os.O_CREAT)
            )
        )
        if writing and (
            any(path.is_relative_to(p) for p in archives)
            or path.is_relative_to(ROOT / "experiments/campaigns")
            and not path.is_relative_to(campaign)
            and not path.is_relative_to(
                ROOT / "experiments/campaigns" / snippet_name
            )
        ):
            denied = True
        if denied:
            raise PermissionError(
                "Resource-completion data scope denied access"
            )

    sys.addaudithook(audit)
    _installed = True
