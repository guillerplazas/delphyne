"""Explicit development scope for the authorized snippet campaign.

Both harnesses install this before experiment imports. Frozen measurements
are read-only; the existing cumulative ledger alone receives new receipts.
"""

from runtime.completion_scope import install as install_completion

import os
from pathlib import Path
import sys
from typing import Any

from runtime.paths import OMPHALOS_ROOT as ROOT

_installed = False


def install() -> None:
    global _installed
    install_completion()
    if _installed:
        return
    current = ROOT / "experiments/campaigns/ace_snippets_20260913"
    output = ROOT / "experiments/output/ace_snippets_20260913"
    prior = ROOT / "experiments/campaigns/resource_completion_20260913"

    def audit(event: str, args: tuple[Any, ...]) -> None:
        if (
            event != "open"
            or not args
            or not isinstance(args[0], (str, bytes))
        ):
            return
        path = Path(os.path.realpath(os.fsdecode(args[0])))
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
        if not writing:
            return
        allowed_ledger = path.parent == prior and path.name in {
            "ledger.sqlite3",
            "ledger.sqlite3-wal",
            "ledger.sqlite3-shm",
            "ledger.sqlite3-journal",
        }
        if (
            path.is_relative_to(ROOT / "experiments/output")
            and not path.is_relative_to(output)
            or path.is_relative_to(ROOT / "experiments/campaigns")
            and not path.is_relative_to(current)
            and not allowed_ledger
        ):
            raise PermissionError(
                "Snippet campaign: frozen input is read-only"
            )

    sys.addaudithook(audit)
    _installed = True
