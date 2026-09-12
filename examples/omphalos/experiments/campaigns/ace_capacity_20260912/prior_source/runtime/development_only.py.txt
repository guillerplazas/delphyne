"""Opt-in process guard for the authorized development-only campaign.

Install before importing experiment modules. Shared by both harnesses;
ordinary and archived runners remain unchanged.
"""

import os
from pathlib import Path
import re
import sys
from typing import Any

_installed = False


def forbidden(path: str) -> bool:
    normalized = os.path.abspath(path).replace("\\", "/")
    return (
        "testX" in normalized
        or "/experiments/output/" in normalized
        and "/test/" in normalized
        or bool(re.search(r"/campaigns/[^/]+/test[_.]", normalized))
        or "/benchmarks/ace_challenge_" in normalized
        or "/coverage_20260911/" in normalized
        and Path(normalized).name
        in {
            "events.jsonl",
            "registration.json",
            "output_inventory.json",
            "final_accounting.json",
            "demo_bank.json",
            "RESULTS.md",
        }
    )


def install() -> None:
    global _installed
    if _installed:
        return

    def audit(event: str, args: tuple[Any, ...]) -> None:
        if event == "open" and args and isinstance(args[0], (str, bytes)):
            path = os.fsdecode(args[0])
            if forbidden(path):
                raise PermissionError(
                    "Development-only campaign: protected data access denied"
                )
        if (
            event == "import"
            and args
            and args[0] == "experiments.common.minif2f_x"
        ):
            raise PermissionError("Eager X-partition import is forbidden")

    sys.addaudithook(audit)
    _installed = True
