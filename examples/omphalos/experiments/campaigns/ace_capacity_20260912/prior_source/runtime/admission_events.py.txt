"""Small campaign-local adapter for auditable Delphyne budget decisions.

Delphyne remains responsible for admitting ``Barrier`` messages.  This module
only writes facts available at Omphalos's campaign boundary; it never changes
an admission decision or synthesizes a remaining Delphyne budget.
"""

# pyright: strict

import json
import os
import time
from typing import Any

compute_invocations: int = 0


def computation_started(function: str) -> None:
    global compute_invocations
    compute_invocations += 1
    record("compute", "invoked", function=function, cached=False)


def record(kind: str, decision: str, **data: Any) -> None:
    """Append one compact event when the active campaign requested it."""
    target = os.environ.get("OMPHALOS_ADMISSION_EVENTS")
    if not target:
        return
    event = {
        "time": time.time(),
        "pid": os.getpid(),
        "cell": os.environ.get("OMPHALOS_CAMPAIGN_CELL", ""),
        "stage": os.environ.get("OMPHALOS_CAMPAIGN_STAGE", ""),
        "kind": kind,
        "decision": decision,
        **data,
    }
    # One O_APPEND write keeps each short JSON record intact across workers.
    fd = os.open(target, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        os.write(fd, (json.dumps(event, sort_keys=True) + "\n").encode())
    finally:
        os.close(fd)
