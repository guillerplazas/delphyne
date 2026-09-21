"""Certified zero-charge administrative requests in completed trajectories."""

from pathlib import Path
from typing import Any

from .common import read


def rejection_events(identity: str, directory: Path) -> list[dict[str, Any]]:
    from .quota_recovery import CELL, FOLDER, administrative_rejections
    from .rate_recovery import rejection_events as rate_events

    events = rate_events(identity, directory)
    if identity == CELL:
        events += [
            dict(
                receipt=receipt,
                before_response=read(FOLDER / "preparation.json")[
                    "successful_responses"
                ]
                + 1,
            )
            for receipt in administrative_rejections(identity, directory)
        ]
    if len({r["receipt"] for r in events}) != len(events):
        raise ValueError("An administrative rejection was counted twice")
    return events
