"""Prepare v3 pilot inputs by exact, HTTP-forbidden v2 query replay.

Run before sealing. New fixtures are written only to the new campaign;
historical caches, journals and demonstrations remain byte-for-byte intact.
"""

# ruff: noqa: E402
from runtime.ace_learning_scope import install

install()

from contextlib import redirect_stdout
from dataclasses import asdict, replace
import hashlib
import io
import json
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from delphyne.utils.typing import pydantic_load

from ace.learning_contracts import observe_local_progress, operation_tags
from ace.role_contracts import TrainingEvent
from ace.role_revision import NoveltyVerdict
from ace.rocq_snippets import SnippetReceipt
from experiments import ace_learning_experiment as c
from prove_ace_role_revision import (
    JudgeBookEdit,
    ProposeBookEdits,
    ReflectLocalRepairs,
)
from prove_ace_learning import JudgeLearningEdit
from runtime.ace_role_journal import RoleJournal
from runtime.campaign_budget import CampaignResponsesModel


def capture(role: str, theorem: str) -> list[dict[str, Any]]:
    path = f"pilot_sources/captured/{role}_{theorem}.json"
    if (c.CAMPAIGN / path).exists():
        return c.read(path)
    raw = c.prior_result("adaptation", role, theorem)
    args = pydantic_load(dp.RunStrategyArgs, raw["args"])
    args.cache_mode = "replay"
    args.cache_file = str(
        c.prior_directory("adaptation", role, theorem) / "cache.yaml"
    )
    args.export_raw_trace = args.export_browsable_trace = args.export_log = (
        False
    )
    seen: dict[str, dict[str, Any]] = {}
    original = dp.PromptingPolicy.__call__

    def observe(
        self: dp.PromptingPolicy,
        query: dp.AttachedQuery[Any],
        env: dp.PolicyEnv,
    ) -> dp.Stream[Any]:
        def stream() -> dp.StreamGen[Any]:
            for message in original(self, query, env):
                if isinstance(message, dp.Solution) and isinstance(
                    query.query,
                    (ProposeBookEdits, ReflectLocalRepairs, JudgeBookEdit),
                ):
                    q = query.query
                    key = hashlib.sha256(
                        json.dumps(q.serialize_args(), sort_keys=True).encode()
                    ).hexdigest()
                    value = message.tracked.value
                    answer = (
                        asdict(cast(Any, value))
                        if isinstance(
                            value,
                            (
                                NoveltyVerdict,
                                dp.Response,
                                dp.WrappedParseError,
                            ),
                        )
                        else str(value)
                    )
                    seen[key] = dict(
                        query=q.query_name(),
                        args=q.serialize_args(),
                        answer=answer,
                    )
                yield message

        return dp.Stream(stream)

    c.activate("pilots", events=False)
    before = c.accounting()["receipts"]

    def discard_checkpoint(_self: RoleJournal, _raw: Any) -> None:
        pass

    with (
        patch.object(
            CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("Capture forbids HTTP"),
        ),
        patch.object(RoleJournal, "write", discard_checkpoint),
        patch.object(dp.PromptingPolicy, "__call__", observe),
        redirect_stdout(io.StringIO()),
    ):
        outcome = run_command(
            run_strategy,
            args,
            ctx=replace(c.context(learning_demos=False), cache_root=Path("/")),
            add_header=False,
        )
    expected = raw["outcome"]["result"]
    if (
        outcome.result is None
        or outcome.result.success != expected["success"]
        or outcome.result.spent_budget != expected["spent_budget"]
        or json.loads(json.dumps(list(outcome.result.values)))
        != expected["values"]
    ):
        raise ValueError(
            "Historical query capture did not replay exactly: " + theorem
        )
    if c.accounting()["receipts"] != before:
        raise ValueError("Offline capture changed paid receipts")
    values = list(seen.values())
    c.save(path, values)
    return values


def final_writer(theorem: str) -> dict[str, Any]:
    return [
        q
        for q in capture("curator", theorem)
        if q["query"] == "ProposeBookEdits"
    ][-1]


def review_query(raw: dict[str, Any]) -> JudgeLearningEdit:
    receipts = tuple(pydantic_load(SnippetReceipt, r) for r in raw["receipts"])
    names = {r.context.theorem_name for r in receipts}
    contexts = {r.context.identifier for r in receipts}
    events = tuple(
        pydantic_load(TrainingEvent, e)
        for n in sorted(names)
        for e in c.read(f"sources/{n}.json")["events"]
        if pydantic_load(TrainingEvent, e).context.identifier in contexts
    )
    observations = tuple(
        observe_local_progress(
            r, dict(seconds=10, rpc_calls=128, view_bytes=8192)
        )
        for r in receipts
    )
    return JudgeLearningEdit(
        raw["action"],
        raw["proposed_rule"],
        raw["target"],
        raw["rules"],
        receipts,
        events,
        observations,
    )


def sample(
    names: list[str], count: int, *, preferred: tuple[str, ...] = ()
) -> list[str]:
    """Fixed class coverage, with explicitly documented source witnesses first."""
    remaining = sorted(
        names,
        key=lambda n: hashlib.sha256(
            ("ace-learning-20260914/" + n).encode()
        ).hexdigest(),
    )
    chosen = [n for n in preferred if n in remaining][:count]
    covered: set[str] = set()
    for n in chosen:
        covered.update(
            operation_tags(json.dumps(c.read(f"sources/{n}.json")["events"]))
        )
    while len(chosen) < count:
        candidates = [n for n in remaining if n not in chosen]
        if not candidates:
            raise ValueError("Insufficient distinct training sources")
        n = max(
            candidates,
            key=lambda n: len(
                operation_tags(
                    json.dumps(c.read(f"sources/{n}.json")["events"])
                )
                - covered
            ),
        )
        chosen.append(n)
        covered.update(
            operation_tags(json.dumps(c.read(f"sources/{n}.json")["events"]))
        )
    return chosen


def compatibility() -> None:
    old = json.loads((c.PRIOR / "seal.json").read_text())
    checked = {p: c.sha(c.ROOT / p) == h for p, h in old["files"].items()}
    if not all(checked.values()):
        raise ValueError("Historical v2 source seal changed")
    inputs: list[dict[str, Any]] = []
    for stage in ("training", "validation"):
        for seed in (0, 1) if stage == "validation" else (0,):
            for theorem in c.partition(stage):
                raw = c.prior_result(stage, "proof", theorem, seed)
                args = raw["args"]
                if args["policy"] != "revision_proof_policy" or args[
                    "budget"
                ] != dict(price=0.10, num_requests=64, rocq_seconds=300):
                    raise ValueError("Historical proof controller mismatch")
                if (
                    args["args"]["playbook"]
                    != c.Playbook.load(c.PRIOR / "book.yaml").render_prompt()
                ):
                    raise ValueError("Historical cell did not use v2 book")
                result = raw["outcome"]["result"]
                source = (
                    c.prior_directory(stage, "proof", theorem, seed)
                    / "result.yaml"
                )
                inputs.append(
                    dict(
                        stage=stage,
                        theorem=theorem,
                        seed=seed,
                        path=str(source.relative_to(c.ROOT)),
                        sha256=c.sha(source),
                        success=result["success"],
                        budget=result["spent_budget"],
                    )
                )
    c.save(
        "compatibility.json",
        dict(
            passed=True,
            sealed_paths=len(checked),
            source_checks=checked,
            reference_cells=inputs,
            runtime_matches=json.loads((c.PRIOR / "runtime.json").read_text())
            == c.read("runtime.json"),
            limit="Configuration/source compatibility, not proof of unchanged provider internals or caching conditions; historical comparison",
        ),
    )


def build() -> None:
    if (c.CAMPAIGN / "seal.json").exists() or c.accounting()["receipts"]:
        raise ValueError("Do not regenerate sealed or measured fixtures")
    if (c.CAMPAIGN / "pilot_registration.json").exists():
        if (
            c.sha(c.ROOT / "demos/ace_learning.demo.yaml")
            != c.read("pilot_registration.json")["demonstrations_sha256"]
        ):
            raise ValueError("Prepared demonstrations changed")
        return
    compatibility()
    from tools.data.ace_learning_fixtures import build_pilots_and_demos

    build_pilots_and_demos()


if __name__ == "__main__":
    build()
