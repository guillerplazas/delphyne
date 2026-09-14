"""Offline, real-Rocq v2 handoff demonstration from an unsolved train source.

Both harnesses: python -m tools.data.ace_role_revision_demos. No API calls.
"""

# ruff: noqa: E402
from runtime.ace_roles_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict, replace
import json
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.mock import fixed_oracle
from delphyne.utils.typing import pydantic_load
import yaml

from ace.ace_playbook import Playbook
from ace.role_contracts import TrainingEvent
from ace.role_revision import (
    BookPlan,
    EditIntent,
    LocalRepair,
    NoveltyVerdict,
    ReflectionFinish,
    apply_edits,
    apply_product,
    reduction_input,
)
from ace.terminal_evidence import TerminalEvidence
from experiments import ace_roles_experiment as c
from prove_ace_role_revision import (
    JudgeBookEdit,
    ProposeBookEdits,
    ReflectLocalRepairs,
    reflect_local_repairs,
    write_reviewed_book_edits,
)
from prove_grounded import grounded_search

RULE = "When an instantiated helper requires a disequality in the reverse orientation from an available hypothesis, introduce the alleged equality, apply that hypothesis, reverse the equality with symmetry, and finish with the introduced equality. Check which variable pair each helper premise requires."
GOOD_CODE = "- intro E. apply Him. symmetry. exact E."


def context() -> dp.ExecutionContext:
    ctx = c.context()
    demo = c.ROOT / "demos/ace_role_revision.demo.yaml"
    return replace(
        ctx,
        modules=(*ctx.modules, "prove_ace_role_revision"),
        demo_files=(*ctx.demo_files, *((demo,) if demo.exists() else ())),
    )


def source() -> tuple[
    dict[str, Any], tuple[TrainingEvent, ...], TerminalEvidence
]:
    raw = c.read("sources/amc12_2000_p1.json")
    events = tuple(pydantic_load(TrainingEvent, e) for e in raw["events"])
    return raw, events, pydantic_load(TerminalEvidence, raw["terminal"])


def local_repair() -> LocalRepair:
    return LocalRepair(
        "e11",
        "Him has the reverse disequality orientation from the helper premise",
        "Reverse the equality argument before applying Him",
        "The selected helper premise requires m <> i and Him : i <> m is available; preserve the current bullet focus",
        "intro E. apply Him. symmetry. exact E.",
    )


def build() -> None:
    ctx = context()
    book = Playbook.load(c.BOOK)
    raw, events, terminal = source()
    demos: list[dict[str, Any]] = []

    def remember(q: dp.AbstractQuery[Any], answer: Any, title: str) -> None:
        demos.append(
            dict(
                demonstration=title,
                query=q.query_name(),
                args=q.serialize_args(),
                answers=[dict(answer=asdict(answer))],
            )
        )

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        if isinstance(q, ReflectLocalRepairs):
            if not q.prefix:
                yield dp.Answer(
                    None,
                    "",
                    tool_calls=(
                        dp.ToolCall("ReadTrainingEvidence", dict(event="e11")),
                    ),
                )
            elif not q.submitted:
                yield dp.Answer(
                    None,
                    "",
                    tool_calls=(
                        dp.ToolCall(
                            "SubmitLocalRepair",
                            dict(repair=asdict(local_repair())),
                        ),
                    ),
                )
            else:
                final = ReflectionFinish(
                    "done",
                    "Preserve this unverified local repair; the whole theorem remains unsolved",
                )
                remember(q, final, "reflector_preserves_unsolved_local_repair")
                yield dp.Answer(None, dp.Structured(asdict(final)))
        elif isinstance(q, ProposeBookEdits):
            if not q.receipts:
                i = next(
                    i
                    for i, x in enumerate(q.contexts)
                    if x.identifier == q.drafts[0].context_id
                )
                yield dp.Answer(
                    None,
                    "",
                    tool_calls=(
                        dp.ToolCall(
                            "FindBookRules",
                            dict(
                                query="orientation of disequality in helper lemma premises"
                            ),
                        ),
                        dp.ToolCall(
                            "CheckAdviceSnippet",
                            dict(context=f"c{i + 1}", snippet=GOOD_CODE),
                        ),
                    ),
                )
            else:
                i = next(
                    i
                    for i, b in enumerate(q.book.bullets)
                    if b.id == "rocq-00014"
                )
                final = BookPlan(
                    "A missing local helper-premise repair, not a complete source proof",
                    (
                        EditIntent(
                            "d1",
                            "add",
                            f"b{i + 1}",
                            "pitfalls",
                            RULE,
                            "Existing product-bound guidance does not cover reversing a disequality premise",
                            ("r1",),
                        ),
                    ),
                )
                remember(q, final, q.role + "_checked_unsolved_repair")
                yield dp.Answer(None, dp.Structured(asdict(final)))
        elif isinstance(q, JudgeBookEdit):
            final = NoveltyVerdict(
                "new_operation",
                q.target,
                "Existing product-bound guidance addresses arithmetic; it does not explain reversing the exact disequality premise rejected here",
            )
            remember(q, final, "reviewer_accepts_distinct_helper_operation")
            yield dp.Answer(None, dp.Structured(asdict(final)))
        else:
            raise AssertionError(type(q))

    policy = (
        grounded_search() @ dp.elim_messages(show_in_log=False)
    ) & fixed_oracle(oracle)
    with patch.object(
        c.CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("Offline demonstration forbids HTTP"),
    ):
        vals, _ = (
            reflect_local_repairs(
                terminal.problem_file,
                book.render_prompt(),
                raw["trajectory"],
                terminal,
                events,
            )
            .run_toplevel(ctx.policy_env(), policy)
            .collect()
        )
        reflection = vals[0].tracked.value
        curator_args = reduction_input((), (reflection,), book)
        curator_args.update(
            role="curator",
            evidence="Unsolved source; check the local repair and its focus",
        )
        vals, curator_budget = (
            write_reviewed_book_edits(**curator_args)
            .run_toplevel(ctx.policy_env(), policy)
            .collect()
        )
        curator = vals[0].tracked.value
        args = reduction_input((curator,), (reflection,), book)
        vals, reducer_budget = (
            write_reviewed_book_edits(**args)
            .run_toplevel(ctx.policy_env(), policy)
            .collect()
        )
        reducer = vals[0].tracked.value
        assert curator.status == reducer.status == "complete"
        assert (
            curator_budget["rocq_seconds"] > 0
            and reducer_budget["rocq_seconds"] == 0
        )
        assert len(reducer.edits) == 1
        updated, _ = apply_edits(book, reducer.base_sha256, reducer.edits)
        assert len(updated.bullets) == len(book.bullets) + 1
        assert GOOD_CODE not in updated.render_prompt()
        assert terminal.status == "not_solved"
        revision = apply_product(book, reducer)
    # The same source example is redundant once that operation is in the book.
    query = JudgeBookEdit(
        "add",
        RULE,
        f"b{len(updated.bullets)}",
        json.dumps(
            [
                dict(alias=f"b{i + 1}", content=b.content)
                for i, b in enumerate(updated.bullets)
            ]
        ),
        curator.receipts,
    )
    remember(
        query,
        NoveltyVerdict(
            "duplicate",
            query.target,
            "This exact operation is already present; retain the checked example without growing the prompt",
        ),
        "reviewer_routes_repeated_operation_to_example",
    )
    (c.ROOT / "demos/ace_role_revision.demo.yaml").write_text(
        yaml.safe_dump(demos, sort_keys=False, width=79)
    )
    result = dict(
        paid_calls=0,
        source="amc12_2000_p1",
        source_status=terminal.status,
        source_receipt_sha256=terminal.check_sha256,
        reflection=asdict(reflection),
        curator=asdict(curator),
        reducer=asdict(reducer),
        revision=asdict(revision),
        original_tokens=book.token_estimate(),
        revised_tokens=updated.token_estimate(),
        full_proof_not_inserted=True,
        reducer_reused_receipt=True,
        lesson="Scripted end-to-end mechanism demonstration, not an LLM performance measurement",
    )
    # These are regenerable, unsealed scripted fixtures, not paid measurements.
    path = c.CAMPAIGN / "platform_v2/demonstration.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                paid_calls=0,
                source_status=terminal.status,
                added_rule_chars=len(RULE),
                curator_checks=1,
                reducer_checks=0,
            )
        )
    )


if __name__ == "__main__":
    build()
