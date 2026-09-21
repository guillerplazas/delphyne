"""Isolate historical prefix replays from subsequently acquired responses."""

from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
import shutil
import tempfile
from typing import Any
from unittest.mock import patch

from delphyne.stdlib.models import CachedRequest
from pydantic import TypeAdapter

from runtime.replay_admission import RecordedCache, fingerprint

from .audit import load_yaml
from .common import CAMPAIGN, sha


@contextmanager
def isolated_snapshots(identity: str, prefix: Path):
    """Expose only transport records represented in the saved cache prefix.

    RecordedCache also restores responses absent from cache.yaml. After a
    continuation finishes, unrestricted snapshots would replay future replies
    past the old interruption. This local copy makes the prefix test stable
    while leaving every original snapshot and paid response unchanged.
    """
    original = RecordedCache.__call__
    before = sha(prefix)
    with tempfile.TemporaryDirectory(
        prefix="prefix-states-", dir=CAMPAIGN
    ) as tmp:
        directory = Path(tmp)
        for row in load_yaml(prefix):
            if (
                row["input"]["request"]["options"].get("model")
                == "__compute__"
            ):
                continue
            adapter = TypeAdapter(CachedRequest)
            encoded = adapter.dump_python(
                adapter.validate_python(row["input"]), mode="json"
            )
            filename = fingerprint(encoded) + ".json.gz"
            source = CAMPAIGN / "transport" / identity / filename
            shutil.copy2(source, directory / filename)

        def answer(cache: RecordedCache, func: Callable[..., Any]) -> Any:
            if cache.model.cell != identity:
                raise ValueError("Prefix snapshot replay escaped its cell")
            return original(replace(cache, directory=directory), func)

        with patch.object(RecordedCache, "__call__", answer):
            yield
    if sha(prefix) != before:
        raise ValueError("A prefix replay changed its original cache")
