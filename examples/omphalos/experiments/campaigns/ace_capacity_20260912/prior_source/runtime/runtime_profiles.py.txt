"""Resolved, hashable ACE launch settings; no change to legacy launches."""

# pyright: strict

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import runtime.rocq_server as rs


@dataclass(frozen=True)
class RuntimeProfile:
    name: str
    workers: int
    streams: int
    worker_rlimit_as_mb: int
    rocq: rs.Settings
    transport: str = "socket"

    def digest(self) -> str:
        return hashlib.sha256(
            json.dumps(asdict(self), sort_keys=True).encode()
        ).hexdigest()

    def activate(self) -> None:
        os.environ["OMPHALOS_MAX_STREAMS"] = str(self.streams)
        os.environ["OMPHALOS_WORKER_RLIMIT_AS_MB"] = str(
            self.worker_rlimit_as_mb
        )
        os.environ["OMPHALOS_PET_MODE"] = self.transport
        rs.MANAGER.settings = self.rocq
        # Fork and spawn workers must resolve the same settings.
        overrides = {
            "RPC_DEADLINE_S": self.rocq.rpc_deadline_s,
            "RPC_MARGIN_S": self.rocq.rpc_margin_s,
            "REPLY_CAP_MB": self.rocq.reply_cap_bytes // 2**20,
            "RLIMIT_AS_MB": self.rocq.server_rlimit_as_mb,
            "MAX_RSS_MB": self.rocq.server_max_rss_mb,
            "MAX_SESSIONS": self.rocq.server_max_sessions,
            "SPAWN_TIMEOUT_S": self.rocq.spawn_timeout_s,
            "SUPERVISOR_PERIOD_S": self.rocq.supervisor_period_s,
            "SESSION_MAX_S": self.rocq.session_max_s,
        }
        for key, value in overrides.items():
            os.environ[f"OMPHALOS_PET_{key}"] = str(value)
        os.environ["OMPHALOS_MEM_FLOOR_MB"] = str(self.rocq.memory_floor_mb)
        os.environ["OMPHALOS_MEM_FLOOR_HOG_MB"] = str(
            self.rocq.memory_floor_hog_mb
        )

    @staticmethod
    def load(path: Path) -> "RuntimeProfile":
        raw = json.loads(path.read_text())
        raw["rocq"] = rs.Settings(**raw["rocq"])
        return RuntimeProfile(**raw)


def resolve(workers: int | None = None) -> RuntimeProfile:
    streams = int(os.environ.get("OMPHALOS_MAX_STREAMS", "4"))
    n = workers if workers is not None else streams
    if n < 1 or n > streams:
        raise ValueError(f"workers must be between 1 and {streams}")
    return RuntimeProfile(
        "ace-server" if streams >= 16 else "ace-portable",
        n,
        streams,
        int(os.environ.get("OMPHALOS_WORKER_RLIMIT_AS_MB", "4096")),
        rs.Settings.from_env(),
        rs.pet_mode(),
    )
