"""Free reducer study: recorded inputs plus scripted real-Rocq exercises.

No claim about a model's future tool adoption. No API execution. The example
is deliberately not registered in the completed paid campaign's selector.
Both harnesses: python -m tools.reports.reducer_tool_study
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from collections.abc import Iterable
from dataclasses import asdict
import json
import os
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.mock import fixed_oracle
from delphyne.utils.typing import pydantic_load
import yaml

from ace import rocq_snippets as rs
from experiments import snippet_experiment as c
from prove_grounded import grounded_search
from prove_snippets import (
    CheckedWriting,
    SnippetAdvice,
    SnippetAddition,
    WriteCheckedRocqAdvice,
    write_checked_rocq_advice,
)

BAD = "have hs : 0 <= (4 * x + 5) * (4 * x + 5) := Rle_0_sqr _."
GOOD = "assert (hs : 0 <= (4 * x + 5) * (4 * x + 5)) by apply Rle_0_sqr."


def source() -> rs.SnippetContext:
    witness = json.loads(
        (
            c.ROOT
            / "experiments/campaigns/ace_capacity_20260912/snippet_witness.json"
        ).read_text()
    )
    return rs.context_for(
        witness["problem_file"],
        witness["theorem_name"],
        (witness["prefix"],),
        "reducer-study",
    )


def answer(advice: SnippetAdvice) -> dp.Answer:
    return dp.Answer(
        None,
        "```yaml\n" + yaml.safe_dump(asdict(advice), sort_keys=False) + "```",
    )


def retain(receipt: rs.SnippetReceipt) -> SnippetAdvice:
    return SnippetAdvice(
        "Retain the source-local fragment checked by Rocq; it leaves the theorem open.",
        (
            SnippetAddition(
                "tactics",
                "Expose square nonnegativity in this source context before arithmetic.",
                (receipt.identifier,),
            ),
        ),
        (receipt.identifier,),
    )


def exercise(mode: str) -> dict[str, Any]:
    """Run a fixed decision script through the real reducer strategy."""
    os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)
    context = source()
    inherited: tuple[rs.SnippetReceipt, ...] = ()
    if mode == "retain_checked":
        inherited = (
            rs.check_snippet(
                context, GOOD, dict(seconds=60, rpc_calls=512, view_bytes=8192)
            ),
        )
    evidence = json.dumps(
        dict(
            unverified_candidates=[
                dict(
                    draft_id="square_nonnegative",
                    context_id=context.identifier,
                    proposed_code=BAD,
                    purpose="Expose a square nonnegativity fact; check before retaining.",
                    source="trainX mathd_algebra_28 syntax witness",
                    status="unverified",
                )
            ],
            note="An empty checked-receipt catalogue is expected initially: the tool creates the first receipt. A checked open fragment is sufficient syntax evidence; it is not a completed theorem.",
        )
    )
    queries: list[WriteCheckedRocqAdvice] = []
    answers: list[dp.Answer] = []

    def oracle(query: dp.AbstractQuery[Any]) -> Iterable[dp.Answer]:
        assert isinstance(query, WriteCheckedRocqAdvice)
        queries.append(query)
        if mode == "check_repair" and len(queries) <= 2:
            proposed = dp.Answer(
                None,
                "",
                tool_calls=(
                    dp.ToolCall(
                        "CheckRocqSnippet",
                        dict(
                            context_id=context.identifier,
                            snippet=BAD if len(queries) == 1 else GOOD,
                        ),
                    ),
                ),
            )
        elif mode == "abstain":
            proposed = answer(
                SnippetAdvice("No checked receipt supplied; abstain.")
            )
        elif mode == "forge":
            proposed = answer(
                SnippetAdvice(
                    "Try to retain without checking",
                    (
                        SnippetAddition(
                            "tactics", "Unsupported candidate", ("invented",)
                        ),
                    ),
                    ("invented",),
                )
            )
        else:
            receipt = next(r for r in query.receipts if r.executable)
            proposed = answer(retain(receipt))
        answers.append(proposed)
        yield proposed

    with patch.object(
        c.CampaignResponsesModel,
        "_send_final_request",
        side_effect=AssertionError("Reducer study forbids API calls"),
    ):
        values, spent = (
            write_checked_rocq_advice(
                "reducer",
                evidence,
                "",
                (context,),
                inherited,
            )
            .run_toplevel(
                c.context().policy_env(),
                grounded_search() & fixed_oracle(oracle),
            )
            .collect(budget=dp.BudgetLimit(dict(rocq_seconds=180)))
        )
    product: CheckedWriting | None = (
        values[0].tracked.value if values else None
    )
    tool_calls = sum(len(a.tool_calls) for a in answers)
    return dict(
        mode=mode,
        product=product,
        queries=queries,
        answers=answers,
        tool_calls=tool_calls,
        rocq_seconds=spent["rocq_seconds"],
    )


def prepare_candidates() -> None:
    """Preserve exact historical drafts, without granting them certificates."""
    diagnostics = c.base.read("complete_diagnostics.json")
    candidates: list[dict[str, Any]] = []
    for theorem in c.SOURCES:
        source_record = c.read(f"sources/{theorem}.json")
        check = next(
            r
            for r in diagnostics["training/luna-ace/" + theorem]["checks"]
            if r["category"] == "syntax-error"
        )
        context = next(
            pydantic_load(rs.SnippetContext, raw)
            for raw in source_record["contexts"]
            if tuple(raw["prefix"]) == tuple(check["verified_prefix"])
        )
        candidates.append(
            dict(
                draft_id="historical-syntax-" + theorem,
                context_id=context.identifier,
                context=asdict(context),
                proposed_code=check["tactic"],
                status="unverified_historical_rejection",
                error=check["error"],
                remaining_goals=check["remaining_goals"],
                purpose="Consider a source-local correction only if it provides useful nonredundant advice.",
                cache_sha256=source_record["cache_sha256"],
                source=source_record["source"],
                after_request=check["after_request"],
            )
        )
    c.save(
        "reducer_study/candidate_packets.json",
        dict(
            selection="First historical syntax-error check for each of the eight preregistered training sources; no new model output",
            batches=[candidates[:4], candidates[4:]],
            no_candidate_is_a_checked_receipt=True,
            api_calls=0,
        ),
    )


def main() -> None:
    prepare_candidates()
    if (c.CAMPAIGN / "reducer_study/offline.json").exists():
        print("Frozen offline study already exists; no API or Rocq rerun")
        return
    c.verify()
    before = c.accounting()
    inputs: list[dict[str, Any]] = []
    for batch in (0, 1):
        cfg = c.configs(f"writing_{batch}_reducer")[0]
        data = c.read(cfg.writer_input)
        result = c.cell_result(cfg)
        assert result is not None
        product = c.product(cfg)
        assert product is not None
        inputs.append(
            dict(
                batch=batch,
                contexts=len(data["contexts"]),
                inherited_receipts=len(data["receipts"]),
                input_operations=sum(
                    len(a["operations"]) for a in json.loads(data["evidence"])
                ),
                answer=asdict(product.answer),
                spent=result["spent_budget"],
            )
        )
    outcomes = [
        exercise(m)
        for m in ("abstain", "check_repair", "retain_checked", "forge")
    ]
    repaired = outcomes[1]
    query, final = repaired["queries"][-1], repaired["answers"][-1]
    demo = [
        dict(
            demonstration="reducer_checks_unverified_draft",
            query="WriteCheckedRocqAdvice",
            args=asdict(query),
            answers=[dict(answer=final.content)],
        )
    ]
    demo_path = c.ROOT / "demos/reducer_snippets.study.demo.yaml"
    with demo_path.open("x") as stream:
        yaml.safe_dump(demo, stream, sort_keys=False, allow_unicode=True)
    assert c.accounting() == before
    c.save(
        "reducer_study/offline.json",
        dict(
            api_calls=0,
            scope="trainX only; actual reducer inputs plus scripted decisions, not model-adoption evidence",
            actual_reducer_inputs=inputs,
            exercises=[
                dict(
                    mode=o["mode"],
                    success=o["product"] is not None,
                    product=asdict(o["product"]) if o["product"] else None,
                    tool_calls=o["tool_calls"],
                    query_turns=len(o["queries"]),
                    rocq_seconds=o["rocq_seconds"],
                )
                for o in outcomes
            ],
            study_demo=str(demo_path.relative_to(c.ROOT)),
            demo_sha256=c.sha(demo_path),
            accounting_unchanged=True,
        ),
    )
    print("Reducer study: four scripted exercises, real Rocq, zero API calls")


if __name__ == "__main__":
    main()
