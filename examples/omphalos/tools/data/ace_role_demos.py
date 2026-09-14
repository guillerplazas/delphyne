"""Create executable ACE role examples with fixed choices and real Rocq.

Both harnesses: python -m tools.data.ace_role_demos. No paid model calls.
"""

# ruff: noqa: E402
from runtime.ace_roles_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict, replace
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.mock import fixed_oracle
from delphyne.utils.typing import pydantic_load
import yaml

from ace.role_contracts import ReflectedLesson, TrainingEvent
from ace.rocq_snippets import context_for
from ace.terminal_evidence import extract_terminal_evidence
from experiments import ace_roles_experiment as c
from prove_ace_roles import (
    WriteACEChoices,
    ReflectACEEvidence,
    write_ace_choices,
)
from prove_grounded import grounded_search
from prove_writer_drafts import UnverifiedSnippetDraft
from runtime import pytanque_utils as pt


def build() -> None:
    ctx = c.context()
    ctx = replace(
        ctx, demo_files=tuple(p for p in ctx.demo_files if p.exists())
    )
    old = yaml.safe_load(
        (c.ROOT / "demos/writer_drafts.demo.yaml").read_text()
    )[0]
    draft = pydantic_load(UnverifiedSnippetDraft, old["args"]["drafts"][0])
    from ace.rocq_snippets import SnippetContext

    source = pydantic_load(SnippetContext, old["args"]["contexts"][0])
    good = next(
        r["snippet"]
        for r in old["args"]["receipts"]
        if r["status"] in ("completed", "executed_open")
    )
    demos: list[dict[str, Any]] = []
    for role in ("curator", "reducer"):
        queries: list[WriteACEChoices] = []
        final: dict[str, Any] = {}

        def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
            assert isinstance(q, WriteACEChoices)
            queries.append(q)
            if not q.receipts:
                yield dp.Answer(
                    None,
                    "",
                    tool_calls=(
                        dp.ToolCall(
                            "CheckAdviceSnippet",
                            dict(context="c1", snippet=good),
                        ),
                    ),
                )
            else:
                final.update(
                    reasoning="Preserve the checked source-local correction; its introduced assertion remains an obligation until discharged.",
                    decisions=[
                        dict(
                            draft="d1",
                            action="retain",
                            reason="The empty demonstration book lacks this square bridge",
                            section="tactics",
                            explanation="Expose square nonnegativity with the source's real-valued x before arithmetic; adapt and check bindings in another goal.",
                            receipts=["r1"],
                        )
                    ],
                )
                yield dp.Answer(None, dp.Structured(final))

        with patch.object(
            c.CampaignResponsesModel,
            "_send_final_request",
            side_effect=AssertionError("Demo authoring forbids HTTP"),
        ):
            vals, budget = (
                write_ace_choices(
                    role,
                    "Historical rejected have syntax",
                    "",
                    (source,),
                    (draft,),
                )
                .run_toplevel(
                    ctx.policy_env(), grounded_search() & fixed_oracle(oracle)
                )
                .collect()
            )
        assert len(vals) == 1 and budget["rocq_seconds"] > 0
        demos.append(
            dict(
                demonstration=role + "_checked_local_alias",
                query="WriteACEChoices",
                args=asdict(queries[-1]),
                answers=[dict(answer=final)],
            )
        )

    terminal = extract_terminal_evidence(
        c.ROOT
        / "experiments/output/ace_adaptation_x3-offline/configs/step33_generator_amc12_2000_p6",
        "amc12_2000_p6",
    )
    source = context_for(
        terminal.problem_file,
        terminal.theorem_name,
        terminal.common_prefix,
        terminal.cache_sha256,
    )
    event = TrainingEvent(
        "e1",
        source,
        "\n".join(terminal.submitted_tail),
        "accepted_assisted_witness",
        "Submitted tail differs from accepted tail; the diff is not an execution trace",
        (),
    )
    lesson = ReflectedLesson(
        "The terminal accepted proof ends in nia; do not credit the proposed norm_num ending.",
        "e1",
        "Use the recorded accepted completion instead of the proposed unexecuted ending",
        "arithmetic completion",
        "the exact supplied accepted prefix and original hypotheses",
        "\n".join(terminal.accepted_tail),
        "",
    )
    query = ReflectACEEvidence(
        pt.parse_problem(terminal.problem_file),
        "Source book unavailable in this standalone attribution fixture; make no bullet attribution",
        "The submitted ending differs from the terminal accepted witness.",
        terminal,
        (event,),
    )
    demos.append(
        dict(
            demonstration="reflector_uses_terminal_witness",
            query="ReflectACEEvidence",
            args=asdict(query),
            answers=[dict(answer=asdict(lesson))],
        )
    )
    (c.ROOT / "demos/ace_roles.demo.yaml").write_text(
        yaml.safe_dump(demos, sort_keys=False, width=79)
    )
    c.save(
        "terminal_fixture.json",
        dict(
            problem_file=terminal.problem_file,
            trajectory=query.trajectory,
            terminal=asdict(terminal),
            events=[asdict(event)],
            generator_book=query.playbook,
        ),
    )
    c.save(
        "demo_checks.json",
        dict(
            paid_calls=0,
            real_rocq_writer_paths=2,
            families=[draft.draft_id, terminal.theorem_name],
        ),
    )


if __name__ == "__main__":
    build()
