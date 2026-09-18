"""Deny protected data before importing any experiment or reading a seal."""

import os
from pathlib import Path
import sys
from typing import Any

from runtime.development_only import install as install_base
from runtime.paths import OMPHALOS_ROOT as ROOT

_installed = False


def partition(stage: str) -> dict[str, str]:
    if stage not in ("train", "validation"):
        raise ValueError("Only trainX and validationX are authorized")
    rows = [
        line.strip()
        for line in (ROOT / "benchmarks" / f"{stage}X.txt")
        .read_text()
        .splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(rows) != 40 or len({Path(row).stem for row in rows}) != 40:
        raise ValueError("Expected 40 unique development problems")
    if any(
        not row.startswith("miniF2F/")
        or not row.endswith(".v")
        or ".." in Path(row).parts
        for row in rows
    ):
        raise ValueError("Invalid development problem path")
    return {Path(row).stem: row for row in rows}


def install() -> None:
    global _installed
    if _installed:
        return
    install_base()
    permitted = {
        (ROOT / path).resolve()
        for stage in ("train", "validation")
        for path in partition(stage).values()
    }

    def audit(event: str, args: tuple[Any, ...]) -> None:
        if (
            event != "open"
            or not args
            or not isinstance(args[0], (str, bytes))
        ):
            return
        path = Path(os.path.realpath(os.fsdecode(args[0])))
        if path.is_relative_to(ROOT / "miniF2F") and path not in permitted:
            raise PermissionError("Only development statements may be opened")
        if path.is_relative_to(ROOT / "benchmarks") and path.name not in (
            "trainX.txt",
            "validationX.txt",
        ):
            raise PermissionError("Only development partitions may be opened")
        # This source module reads all three partitions at import time.
        if path.name in ("minif2f_x.py", "minif2f_x.cpython-312.pyc"):
            raise PermissionError("Eager X loader is forbidden")

    sys.addaudithook(audit)
    _installed = True
