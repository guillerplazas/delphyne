"""Explicit completion receipts for this campaign's new worker processes.

Delphyne periodically writes intermediate result.yaml files. Their presence
alone cannot establish that a worker returned. Patch only this invocation's
launcher, preserving the existing shared launcher and archived strategies.
"""

import fcntl
from pathlib import Path
from typing import Any, Literal

from delphyne.stdlib.experiments import experiment_launcher as el
from experiments.common import omphalos_launch as ol

from .audit import load_yaml
from .common import OUTPUT, now, read, save, sha

_original_run_config = el._run_config  # pyright: ignore[reportPrivateUsage]


def completed_config(*args: Any, **kwargs: Any) -> tuple[str, bool]:
    name, success = _original_run_config(*args, **kwargs)
    directory = Path(kwargs["config_dir"])
    if success:
        save(
            directory / "completed.json",
            dict(
                cell=name,
                completed_at=now(),
                result_sha=sha(directory / "result.yaml"),
                cache_sha=sha(directory / "cache.yaml"),
            ),
        )
    return name, success


def ground_truth(directory: Path) -> Literal["todo", "done", "failed"]:
    receipt = directory / "completed.json"
    if receipt.exists():
        data = read(receipt)
        if all(
            (directory / filename).exists()
            and sha(directory / filename) == data[key]
            for filename, key in (
                ("result.yaml", "result_sha"),
                ("cache.yaml", "cache_sha"),
            )
        ):
            return "done"
        return "failed"
    if (directory / "result.yaml").exists() or (
        directory / "exception.txt"
    ).exists():
        # Never silently replace a paid, potentially incomplete trajectory.
        return "failed"
    return "todo"


def install() -> None:
    el._run_config = completed_config  # pyright: ignore[reportPrivateUsage]
    ol.ground_truth = ground_truth


def require_closed(batch: str) -> None:
    """Accept legacy final state only after the launcher releases its lock."""
    directory = OUTPUT / batch
    with (directory / ".launch.lock").open("r") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError(f"Batch is still running: {batch}") from exc
        state = load_yaml(directory / "experiment.yaml")
        configs: dict[str, Any] = state["configs"]
        unfinished = [
            name
            for name, info in configs.items()
            if info.get("status") != "done"
            or not info.get("end_time")
            or info.get("interruption_time")
        ]
        if unfinished:
            raise ValueError(f"Batch is not complete: {batch}: {unfinished}")
