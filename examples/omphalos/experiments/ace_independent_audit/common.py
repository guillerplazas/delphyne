"""Paths and immutable artifacts for the independent investigation."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.ace_sanitized.scope import partition
from runtime.paths import OMPHALOS_ROOT as ROOT

CAMPAIGN = ROOT / "experiments/campaigns/ace_independent_audit"
OUTPUT = CAMPAIGN / "runs"
REPORT = ROOT / "report/ace_independent_audit"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True).encode()
    ).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save(path: Path, value: Any) -> None:
    """Write once, or verify equality on resumption."""
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != content:
            raise ValueError(f"Immutable artifact changed: {path}")
        return
    with path.open("x") as stream:
        stream.write(content)


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def allowed() -> dict[str, tuple[str, str]]:
    return {
        name: (stage, path)
        for stage in ("train", "validation")
        for name, path in partition(stage).items()
    }
