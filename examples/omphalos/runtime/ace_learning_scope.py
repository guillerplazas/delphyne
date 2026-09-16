"""Development-only access for ACE learning v3, shared by both harnesses."""

import os
from pathlib import Path
import sys
from typing import Any

from runtime.development_only import install as install_base
from runtime.paths import OMPHALOS_ROOT as ROOT

NAME = "ace_learning_20260914"
PRIOR = "ace_revision_20260913"
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
        path = Path(os.path.realpath(os.fsdecode(args[0])))
        if not path.is_relative_to(ROOT):
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
        denied = path in mixed
        if path.is_relative_to(ROOT / "miniF2F"):
            denied |= path not in permitted or writing
        if path.is_relative_to(ROOT / "benchmarks"):
            denied |= (
                path.name not in ("trainX.txt", "validationX.txt") or writing
            )
        for folder in ("experiments/campaigns", "experiments/output"):
            if path.is_relative_to(ROOT / folder):
                denied |= not (
                    path.is_relative_to(ROOT / folder / NAME)
                    or not writing
                    and path.is_relative_to(ROOT / folder / PRIOR)
                )
        if path.is_relative_to(ROOT / "experiments/previous"):
            denied = True
        if denied:
            raise PermissionError(
                "ACE learning development scope denied: " + str(path)
            )

    sys.addaudithook(audit)
    _installed = True
