"""Real Rocq, provenance, strategy navigation and budget regressions."""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.scripts.demonstrations import check_demo_file
from delphyne.stdlib.mock import fixed_oracle
from delphyne.stdlib.models import LLMRequest
from delphyne.stdlib.openai_api import translate_chat_for_responses
from delphyne.stdlib.queries import create_prompt
import pytest
import yaml

from ace import rocq_snippets as rs
from ace import terminal_evidence as te
from experiments import snippet_experiment as c
from prove_grounded import (
    grounded_search,
    prove_theorem_grounded,
    ProposeProofScriptGrounded,
)
from prove_snippets import (
    SnippetAdvice,
    SnippetAddition,
    WriteCheckedRocqAdvice,
    compile_advice,
    snippet_examples,
    write_checked_rocq_advice,
)
from runtime import pytanque_utils as pt
from runtime.tool_budget import ToolLimits

LIMITS: dict[str, float | int] = dict(
    seconds=10, rpc_calls=128, view_bytes=2048
)
GOOD = "assert (hs : 0 <= (4 * x + 5) * (4 * x + 5)) by apply Rle_0_sqr."
BAD = "have hs : 0 <= (4 * x + 5) * (4 * x + 5) := Rle_0_sqr _."


def context() -> rs.SnippetContext:
    w = json.loads(
        (
            c.ROOT
            / "experiments/campaigns/ace_capacity_20260912/snippet_witness.json"
        ).read_text()
    )
    return rs.context_for(
        w["problem_file"], w["theorem_name"], (w["prefix"],), "test-source"
    )


def test_required_cell_completeness(tmp_path: Path) -> None:
    cfg = c.Config("synthetic", "training", "A")
    result = tmp_path / "result.yaml"
    with patch.object(c, "directory", return_value=tmp_path):
        with pytest.raises(ValueError, match="Missing required"):
            c.cell_result(cfg)
        result.write_text("outcome:\n  result: null\n  diagnostics: []\n")
        assert c.cell_result(cfg) is None
        assert c.product(cfg) is None
        result.write_text(
            "outcome:\n  result: null\n  diagnostics: [CampaignExhausted]\n"
        )
        with pytest.raises(ValueError, match="Administratively censored"):
            c.cell_result(cfg)
        result.unlink()
        (tmp_path / "exception.txt").write_text("worker crashed")
        assert c.cell_result(cfg) is None
        (tmp_path / "exception.txt").write_text("CampaignExhausted")
        with pytest.raises(ValueError, match="Administratively censored"):
            c.cell_result(cfg)


@pytest.mark.parametrize(
    "snippet,expected",
    [
        (BAD, "rejected"),
        (GOOD, "executed_open"),
        (GOOD + " nra.", "completed"),
        (GOOD + " have", "rejected"),
        ("Admitted.", "rejected"),
        ("", "rejected"),
        ("```rocq\n" + GOOD + "\n```", "rejected"),
    ],
)
def test_live_raw_snippet(snippet: str, expected: str) -> None:
    original = context()
    r = rs.check_snippet(original, snippet, LIMITS)
    assert r.status == expected
    assert not r.checked.feedback.auto_finished
    if r.executable:
        assert r.successor().prefix == (*original.prefix, snippet)
        assert r.elapsed == r.checked.elapsed and r.rpc_calls > 0
    else:
        with pytest.raises(ValueError):
            r.successor()


def test_context_binding_and_unavailable() -> None:
    original = context()
    with pytest.raises(ValueError, match="drift"):
        rs.check_snippet(
            replace(original, problem_sha256="forged"), GOOD, LIMITS
        )
    assert (
        rs.check_snippet(replace(original, prefix=()), GOOD, LIMITS).status
        == "rejected"
    )
    limited = rs.check_snippet(
        original, GOOD, dict(seconds=10, rpc_calls=1, view_bytes=2048)
    )
    assert limited.status == "resource_exhausted" and not limited.executable
    with patch.object(
        rs.ag,
        "checked_proof",
        return_value=rs.ag.Checked(
            pt.Feedback(False, error_message="Rocq transport failure"),
            "unknown",
            0.2,
            1,
            "",
        ),
    ):
        assert rs.check_snippet(original, GOOD, LIMITS).status == "unknown"


def test_real_proof_completes_inside_tool() -> None:
    source = context()
    script = "\n".join((*source.prefix, GOOD, "nra."))
    queries: list[dp.AbstractQuery[Any]] = []

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, ProposeProofScriptGrounded)
        queries.append(q)
        initial = q.snippet_contexts[0]
        yield dp.Answer(
            None,
            "",
            tool_calls=(
                dp.ToolCall(
                    "CheckRocqSnippet",
                    dict(context_id=initial.identifier, snippet=script),
                ),
            ),
        )

    env = c.context().policy_env()
    values, spent = (
        prove_theorem_grounded(
            source.problem_file,
            source.theorem_name,
            turn_budget=4,
            admission=False,
            restart=False,
            snippet_tools=True,
        )
        .run_toplevel(env, grounded_search() & fixed_oracle(oracle))
        .collect(budget=dp.BudgetLimit(dict(rocq_seconds=300)))
    )
    assert len(values) == len(queries) == 1
    assert values[0].tracked.value == script and spent["rocq_seconds"] > 0


def test_compute_declined_before_rocq() -> None:
    from prove_snippets import verify_snippet_demo

    source = context()
    with patch.object(
        rs.ag, "checked_proof", side_effect=AssertionError("Must not execute")
    ):
        values, _ = (
            verify_snippet_demo(source, GOOD, "executed_open")
            .run_toplevel(
                c.context().policy_env(), grounded_search() & object()
            )
            .collect(budget=dp.BudgetLimit(dict(rocq_seconds=1)))
        )
    assert not values


def test_repeated_tool_calls_reuse_work_then_require_submission() -> None:
    source = context()
    partial = "\n".join((*source.prefix, GOOD))
    count = 0

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        nonlocal count
        assert isinstance(q, ProposeProofScriptGrounded)
        count += 1
        if count <= 4:
            yield dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "CheckRocqSnippet",
                        dict(
                            context_id=q.snippet_contexts[0].identifier,
                            snippet=partial,
                        ),
                    ),
                ),
            )
        else:
            assert not q.snippet_checks
            assert rs.CheckRocqSnippet not in q.advertised_tools()
            yield dp.Answer(None, "```rocq\n" + partial + "\nnra.\n```")

    with patch.object(rs, "record") as recorded:
        values, _ = (
            prove_theorem_grounded(
                source.problem_file,
                source.theorem_name,
                turn_budget=6,
                admission=False,
                restart=False,
                snippet_tools=True,
            )
            .run_toplevel(
                c.context().policy_env(),
                grounded_search() & fixed_oracle(oracle),
            )
            .collect()
        )
    assert len(values) == 1 and count == 5
    assert recorded.call_count == 1


def test_writer_checks_then_preserves_exact_text() -> None:
    source = context()
    requests: list[WriteCheckedRocqAdvice] = []

    def oracle(q: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(q, WriteCheckedRocqAdvice)
        requests.append(q)
        if len(requests) <= 2:
            yield dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "CheckRocqSnippet",
                        dict(
                            context_id=source.identifier,
                            snippet=BAD if len(requests) == 1 else GOOD,
                        ),
                    ),
                ),
            )
        else:
            receipt = next(r for r in q.receipts if r.executable)
            answer = SnippetAdvice(
                "Use checked syntax",
                (
                    SnippetAddition(
                        "tactics",
                        "Establish square nonnegativity in the source context.",
                        (receipt.identifier,),
                    ),
                ),
                (receipt.identifier,),
            )
            yield dp.Answer(
                None, "```yaml\n" + yaml.safe_dump(asdict(answer)) + "```"
            )

    values, spent = (
        write_checked_rocq_advice("curator", "source", "", (source,))
        .run_toplevel(
            c.context().policy_env(), grounded_search() & fixed_oracle(oracle)
        )
        .collect(budget=dp.BudgetLimit(dict(rocq_seconds=180)))
    )
    assert (
        len(values) == 1 and len(requests) == 3 and spent["rocq_seconds"] > 0
    )
    product = values[0].tracked.value
    assert (
        GOOD in product.delta.operations[0].content
        and BAD not in product.delta.operations[0].content
    )
    receipt = next(r for r in product.receipts if r.executable)
    reduced = compile_advice("reducer", product.answer, (receipt,))
    assert reduced.operations[0].content == product.delta.operations[0].content
    with pytest.raises(ValueError):
        compile_advice(
            "reducer",
            replace(product.answer, retained_receipts=("invented",)),
            (receipt,),
        )
    with pytest.raises(ValueError):
        compile_advice(
            "reducer",
            replace(
                product.answer,
                operations=(
                    SnippetAddition(
                        "tactics", "Use `" + BAD + "`", (receipt.identifier,)
                    ),
                ),
            ),
            (receipt,),
        )
    dropped = compile_advice(
        "reducer",
        SnippetAdvice(
            "Drop redundant advice", dropped_receipts=(receipt.identifier,)
        ),
        (receipt,),
    )
    assert not dropped.operations


def test_last_writer_request_has_no_tools_and_prompts_render() -> None:
    env = c.context().policy_env()
    q = WriteCheckedRocqAdvice(
        "reflector", "receipt", "", (context(),), allow_tools=False
    )
    assert not q.advertised_tools()
    parsed = q.parse_answer(
        dp.Answer(
            None,
            "```yaml\nreasoning: done\noperations: []\nretained_receipts: []\ndropped_receipts: []\n```",
        )
    )
    assert not isinstance(parsed, dp.ParseError)
    chat = create_prompt(
        q, (), {}, None, env.templates, tag_user_feedback_messages=True
    )
    assert chat


def test_demo_navigation_and_family_exclusion() -> None:
    result = check_demo_file(
        c.ROOT / "demos/snippets.demo.yaml", c.context(), c.ROOT
    )
    assert not result.errors, result.errors
    env = c.context().policy_env()
    own = env.examples.examples_for("ProposeProofScriptGroundedSnippets")
    assert len(own) == 2
    for example in own:
        q = example.query
        assert isinstance(q, ProposeProofScriptGrounded)
        chosen = snippet_examples()(env, q)
        assert not any(
            isinstance(e.query, ProposeProofScriptGrounded)
            and e.query.spec.theorem_name == q.spec.theorem_name
            for e in chosen
        )


def test_tool_completed_proof_reaches_terminal_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = context()
    r = rs.check_snippet(source, GOOD + " nra.", LIMITS)
    cell = tmp_path / "cell"
    cell.mkdir()
    call = dict(
        fun="check_snippet",
        args=dict(context=asdict(source), snippet=r.snippet, limits=LIMITS),
    )
    cache = [
        dict(
            input=dict(
                request=dict(
                    options=dict(model="__compute__"),
                    chat=[dict(content=yaml.safe_dump(call))],
                )
            ),
            output=dict(outputs=[dict(content=yaml.safe_dump(asdict(r)))]),
        )
    ]
    (cell / "cache.yaml").write_text(yaml.safe_dump(cache))
    (cell / "result.yaml").write_text(
        yaml.safe_dump(
            dict(
                outcome=dict(
                    result=dict(
                        success=True,
                        values=["\n".join(r.checked.feedback.proof_so_far)],
                    )
                )
            )
        )
    )
    monkeypatch.setattr(te, "ROOT", tmp_path)
    receipt = te.extract_terminal_evidence(cell, source.theorem_name)
    assert receipt.status == "accepted" and receipt.checker == "check_snippet"
    assert (
        not receipt.auto_finished
        and receipt.accepted_script == r.successor().prefix
    )


def test_registered_counts_caps_and_isolation() -> None:
    p = c.read("protocol.json")
    assert (
        len(p["training"]) == 20
        and len(p["validation"]) == 40
        and len(p["sources"]) == 8
    )
    assert abs(sum(p["allocations"].values()) + p["prior_cost"] - 30) < 1e-9
    theorem = p["training"][0]
    a = c.Config(theorem, "training", "A").instantiate(None)
    assert os.environ["OMPHALOS_CAMPAIGN_CELL"] == c.name(
        c.Config(theorem, "training", "A"), None
    )
    old = c.base.proof("training", "luna-ace", theorem).instantiate(None)
    assert a.args == old.args | dict(snippet_tools=True)
    assert a.budget == old.budget
    assert ToolLimits().seconds == 60


def test_registered_proof_prompts_have_closed_tool_conversations() -> None:
    from prove_grounded import ProposeProofScriptGroundedSnippets

    env = c.context().policy_env()
    for stage in ("training", "validation"):
        for theorem in c.read("protocol.json")[stage]:
            source = rs.context_for(c.partition(stage)[theorem], theorem)
            query = ProposeProofScriptGroundedSnippets(
                spec=pt.parse_problem(source.problem_file, True),
                available_skills={},
                snippet_checks=True,
                snippet_contexts=(source,),
            )
            chat = create_prompt(
                query,
                snippet_examples()(env, query),
                {},
                None,
                env.templates,
                tag_user_feedback_messages=True,
            )
            request = LLMRequest(chat=chat, options={})
            items, _ = translate_chat_for_responses(request, None, True)
            wire: list[dict[str, Any]] = json.loads(json.dumps(items))
            calls = [
                i["call_id"] for i in wire if i.get("type") == "function_call"
            ]
            outputs = [
                i["call_id"]
                for i in wire
                if i.get("type") == "function_call_output"
            ]
            assert calls == outputs, (stage, theorem)
