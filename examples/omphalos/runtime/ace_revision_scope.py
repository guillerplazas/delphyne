"""Development boundary for the newly authorized ACE revision campaign.

The prior campaign supplies only frozen training sources and configuration.
Its interrupted validation outputs are unavailable to this process.
"""

from runtime.development_only import install as install_base

import os
from pathlib import Path
import sys
from typing import Any

from runtime.paths import OMPHALOS_ROOT as ROOT

NAME = "ace_revision_20260913"
_installed = False


def install() -> None:
    global _installed
    install_base()
    if _installed:
        return
    permitted = {
        (ROOT / line.strip()).resolve()
        for part in ("trainX", "validationX")
        for line in (ROOT / f"benchmarks/{part}.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    campaign = ROOT / "experiments/campaigns" / NAME
    output = ROOT / "experiments/output" / NAME
    prior = ROOT / "experiments/campaigns/ace_roles_20260913"
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
        mode, flags = (
            args[1] if len(args) > 1 else None,
            args[2] if len(args) > 2 else 0,
        )
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
            permitted_prior = p.is_relative_to(prior / "sources") or p in {
                prior / "runtime.json",
                prior / "interruption.json",
                prior / "platform_v2/demonstration.json",
            }
            denied |= not (
                p.is_relative_to(campaign) or permitted_prior and not writing
            )
        if p.is_relative_to(ROOT / "experiments/output"):
            denied |= not p.is_relative_to(output)
        if p.is_relative_to(ROOT / "experiments/previous"):
            denied = True
        if denied:
            raise PermissionError(
                "ACE revision development scope denied: " + str(p)
            )

    sys.addaudithook(audit)
    _installed = True
