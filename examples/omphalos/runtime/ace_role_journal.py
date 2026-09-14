"""Durable ACE progress at Delphyne Message nodes, including cached replay.

Strategies emit data; this policy adapter persists it. A declined next
request cannot erase the previous checkpoint. Each cell owns one journal;
replaying a prefix is idempotent and cannot roll its latest state backwards.
Both harnesses use this same adapter, without CLI-specific hooks.
"""

from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
from typing import Any, Never
import uuid

import delphyne as dp
from delphyne.stdlib.policies import (
    PureTreeTransformerFn,
    contextual_tree_transformer,
)
from delphyne.utils.typing import pydantic_load

from ace.role_revision import ReflectionProduct, WriterProduct

CHECKPOINT = "ace_role_checkpoint_v2"


@dataclass(frozen=True)
class RoleCheckpoint:
    episode: str
    step: int
    product: ReflectionProduct | WriterProduct


class RoleJournal:
    def __init__(self, directory: Path):
        self.directory = directory

    def latest(self) -> RoleCheckpoint | None:
        paths = sorted(self.directory.glob("step-*.json"))
        if not paths:
            return None
        return pydantic_load(RoleCheckpoint, json.loads(paths[-1].read_text()))

    def write(self, raw: Any) -> None:
        checkpoint = pydantic_load(RoleCheckpoint, raw)
        if checkpoint.step < 0 or checkpoint.step > 999999:
            raise ValueError("Invalid checkpoint step")
        self.directory.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(raw, sort_keys=True, indent=2) + "\n"
        path = self.directory / f"step-{checkpoint.step:06d}.json"
        with (self.directory / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            previous = self.latest()
            if previous and previous.episode != checkpoint.episode:
                raise ValueError("Journal belongs to a different role episode")
            if path.exists():
                if path.read_text() != encoded:
                    raise ValueError("Checkpoint replay diverged")
                return
            expected = previous.step + 1 if previous else 0
            if checkpoint.step != expected:
                raise ValueError("Checkpoint sequence has a gap")
            temporary = path.with_suffix(f".{uuid.uuid4().hex}.tmp")
            try:
                with temporary.open("x") as out:
                    out.write(encoded)
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)


@contextual_tree_transformer
def checkpoint_roles(
    env: dp.PolicyEnv, policy: Any, directory: str
) -> PureTreeTransformerFn[dp.Message, Never]:
    journal = RoleJournal(Path(directory))

    def transform[N: dp.Node, P, T](
        tree: dp.Tree[dp.Message | N, P, T],
    ) -> dp.Tree[N, P, T]:
        if isinstance(tree.node, dp.Message):
            if tree.node.msg == CHECKPOINT:
                journal.write(tree.node.data)
            else:
                env.log(
                    tree.node.level or "info",
                    tree.node.msg,
                    metadata={"attached": tree.node.data},
                    loc=tree,
                )
            return transform(tree.child(None))
        return tree.transform(tree.node, transform)

    return transform
