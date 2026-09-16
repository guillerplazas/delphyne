"""Training-only, source-family-excluded v3 demonstrations and pilot panels."""

from dataclasses import asdict, replace
import json
from typing import Any, Literal, cast

from delphyne.utils.typing import pydantic_load
import yaml

from ace.learning_contracts import (
    LearningVerdict,
    learning_plan,
    observe_local_progress,
)
from ace.role_revision import BookPlan, EditIntent, WriterProduct
from ace.rocq_snippets import check_snippet
from experiments import ace_learning_experiment as c
from prove_ace_learning import JudgeLearningEdit, ProposeLearningEdits
from tools.data.ace_learning_data import (
    capture,
    final_writer,
    review_query,
    sample,
)


# Fixed before new calls. Semantic labels are an agent audit of source
# evidence, not independent human annotation or the previous model verdict.
# Four borderline relevance/generalization cases remain explicitly unscored.
REVIEW_GOLD: dict[str, tuple[list[str], str]] = {
    "batch1_review0": (
        ["example", "duplicate"],
        "The original square subgoal is proved; enclosing bounds remain open.",
    ),
    "batch1_review1": (
        ["correction", "example", "duplicate"],
        "Factor positivity and the rewrite are established. Whether this is a correction or prerequisite clarification is ambiguous.",
    ),
    "batch2_review0": (
        ["example", "duplicate"],
        "Executed change/rewrite matches existing advice; Undo failure does not contradict that advice.",
    ),
    "batch3_review0": (
        ["example", "duplicate"],
        "Original trig obligation discharged, enclosing theorem open; existing orientation advice already covers the operation.",
    ),
    "batch5_review0": (
        ["new_operation"],
        "The recorded wrong-bullet event and repaired base-case closure support the distinct focus lesson.",
    ),
    "batch5_review1": (
        [],
        "Whether choosing a recurrence index from an available premise is useful rather than misleading remains unestablished.",
    ),
    "batch6_review0": (
        ["example", "duplicate"],
        "Closed-power normalization establishes the original logarithm equality locally.",
    ),
    "batch6_review1": (
        ["example", "duplicate"],
        "A reciprocal identity and polynomial fact are established; no complete theorem claim is needed.",
    ),
    "batch6_review2": (
        ["example", "duplicate"],
        "The second receipt closes the original product-bound obligation; inspecting only the first receipt loses this evidence.",
    ),
    "batch7_review0": (
        ["new_operation"],
        "The original by-lia syntax rejection and executed ltac:(lia) instantiation support the syntax distinction.",
    ),
    "batch7_review1": (
        ["example", "duplicate"],
        "The square nonnegativity fact is proved, not merely asserted.",
    ),
    "batch7_review2": (
        [],
        "Natural-index normalization is executed, but the relevance of this partial example to the entire target rule is ambiguous.",
    ),
    "batch8_review0": (
        ["new_operation"],
        "The nonzero-factor fact is proved using root equations and the disequality, beyond merely rewriting the polynomial.",
    ),
    "batch9_review0": (
        [],
        "Odd normal form is proved, but the proposed advice also revises case reasoning; broader evidence support remains ambiguous.",
    ),
    "batch9_review1": (
        ["example", "duplicate"],
        "The square fact is proved while the enclosing upper bound remains open.",
    ),
    "batch9_review2": (
        [],
        "Closed-cast normalization is observed; relevance to a recurrence-specific rule is ambiguous.",
    ),
}


def remember(
    demos: list[dict[str, Any]], title: str, query: Any, answer: Any
) -> None:
    demos.append(
        dict(
            demonstration=title,
            query=query.query_name(),
            args=query.serialize_args(),
            answers=[dict(answer=asdict(answer))],
        )
    )


def translated_demos() -> list[dict[str, Any]]:
    """Keep the legacy demonstration content, adapting only its interface."""
    result: list[dict[str, Any]] = []
    for original in yaml.safe_load(
        (c.ROOT / "demos/ace_role_revision.demo.yaml").read_text()
    ):
        demo = json.loads(json.dumps(original))
        demo["demonstration"] = "v2_" + demo["demonstration"]
        if demo["query"] == "ReflectLocalRepairs":
            demo["query"] = "ReflectLearningRepairs"
            demo["args"]["current_book"] = demo["args"]["playbook"]
        elif demo["query"] == "ProposeBookEdits":
            for strict in (False, True):
                copy = json.loads(json.dumps(demo))
                copy["query"] = "ProposeLearningEdits"
                copy["args"].update(
                    strict_actions=strict, targeted_demos=False
                )
                copy["demonstration"] += "_strict" if strict else "_legacy"
                if strict:
                    copy["answers"][0]["answer"] = asdict(
                        learning_plan(
                            pydantic_load(
                                BookPlan, copy["answers"][0]["answer"]
                            )
                        )
                    )
                result.append(copy)
            continue
        else:
            # The exact old reviewer examples stay in the legacy bucket.
            continue
        result.append(demo)
    return result


def writer_product(theorem: str) -> WriterProduct:
    return pydantic_load(
        WriterProduct,
        c.prior_result("adaptation", "curator", theorem)["outcome"]["result"][
            "values"
        ][0],
    )


def build_pilots_and_demos() -> None:
    cases: list[dict[str, Any]] = []
    demos = translated_demos()
    order: list[str] = c.read("protocol.json")["order"]
    curator_names = [
        n
        for n in order
        if c.prior_directory("adaptation", "curator", n).exists()
    ]
    invalid = sorted(
        n for n in curator_names if writer_product(n).status == "partial"
    )
    valid = sample(
        [n for n in curator_names if n not in invalid],
        6,
        preferred=("amc12a_2020_p13", "mathd_algebra_206"),
    )
    assert len(invalid) == 6
    for theorem in invalid + valid:
        historical = final_writer(theorem)
        query = pydantic_load(
            ProposeLearningEdits,
            dict(
                historical["args"], strict_actions=True, targeted_demos=False
            ),
        )
        path = f"pilot_sources/schema/{theorem}.json"
        c.save(path, dict(query=query.serialize_args()))
        cases.append(
            dict(
                treatment="schema",
                role="schema",
                case=theorem,
                input=path,
                originally_valid=theorem in valid,
                historical_query=historical,
                historical_product_status=writer_product(theorem).status,
            )
        )

    # Extract every paid independent review in original order. Each new
    # review sees exactly its old proposal/book/receipts plus evidence v3.
    review_queries: dict[str, JudgeLearningEdit] = {}
    for batch in range(10):
        historical = [
            q
            for q in capture("reducer", f"batch{batch}")
            if q["query"] == "JudgeBookEdit"
        ]
        for index, record in enumerate(historical):
            key = f"batch{batch}_review{index}"
            path = f"pilot_sources/review/{key}.json"
            if (c.CAMPAIGN / path).exists():
                query = pydantic_load(JudgeLearningEdit, c.read(path)["query"])
            else:
                query = review_query(record["args"])
                c.save(path, dict(query=query.serialize_args()))
            review_queries[key] = query
            relations, reason = REVIEW_GOLD[key]
            cases.append(
                dict(
                    treatment="review",
                    role="review",
                    case=key,
                    input=path,
                    expected_support="supported"
                    if relations
                    else "unresolved",
                    allowed_relations=relations,
                    label_reason=reason,
                    historical_query=record,
                )
            )
    assert len(review_queries) == 16

    # One positive local-completion example and one duplicate example;
    # family exclusion removes each when its own source is evaluated.
    for key, relation in (
        ("batch3_review0", "example"),
        ("batch2_review0", "duplicate"),
    ):
        query = review_queries[key]
        remember(
            demos,
            "review_" + key,
            query,
            LearningVerdict(
                "supported",
                cast(Literal["example", "duplicate"], relation),
                query.target,
                REVIEW_GOLD[key][1],
            ),
        )
    # An executed assertion creates an obligation; this is a real checked
    # negative example, not an invented successful proof or a paid episode.
    original = review_queries["batch3_review0"]
    ctx = original.receipts[0].context
    unchecked = check_snippet(
        ctx,
        "assert (Hunproved : False).",
        dict(seconds=30, rpc_calls=128, view_bytes=8192),
    )
    assert unchecked.executable
    observation = observe_local_progress(
        unchecked, dict(seconds=10, rpc_calls=128, view_bytes=8192)
    )
    assert observation.introduced and observation.outcome == "obligations_open"
    negative = replace(
        original,
        action="add",
        proposed_rule="Prove a contradiction by asserting False; this discharges the trigonometric goal.",
        receipts=(unchecked,),
        observations=(observation,),
    )
    remember(
        demos,
        "review_rejects_unproved_assertion",
        negative,
        LearningVerdict(
            "unsupported",
            "unsupported",
            negative.target,
            "The new False assertion remains unproved, and neither the original goal nor the theorem was discharged.",
        ),
    )

    accepted = [
        n
        for n in order
        if c.read(f"sources/{n}.json")["terminal"]["status"] == "accepted"
    ]
    unsolved = [n for n in order if n not in accepted]
    reflection = sample(unsolved, 6, preferred=("amc12a_2020_p13",)) + sample(
        accepted, 6, preferred=("mathd_numbertheory_48",)
    )
    for theorem in reflection:
        batch = order.index(theorem) // 4
        step = json.loads((c.PRIOR / f"revisions/{batch}.json").read_text())
        book = pydantic_load(c.Playbook, step["before"])
        args = c.reflection_args(theorem, book)
        path = f"pilot_sources/reflection/{theorem}.json"
        c.save(path, args)
        capture("reflector", theorem)
        cases.append(
            dict(
                treatment="reflection",
                role="reflector",
                case=theorem,
                input=path,
                source_accepted=theorem in accepted,
                original=c.prior_result("adaptation", "reflector", theorem)[
                    "outcome"
                ]["result"]["values"][0],
            )
        )

    # A failed repair means a recorded rejected check, even if another
    # attempt in the same episode executed. There are only five episodes
    # with no executable receipt; do not invent a sixth such episode.
    failed = [
        n
        for n in curator_names
        if any(r.status == "rejected" for r in writer_product(n).receipts)
    ]
    successful = [
        n
        for n in curator_names
        if n not in failed
        and any(r.executable for r in writer_product(n).receipts)
    ]
    curator_cases = sample(
        failed, 6, preferred=("aime_1990_p4", "amc12_2000_p6", "imo_1983_p6")
    ) + sample(
        successful,
        6,
        preferred=("imo_1968_p5_1", "amc12a_2002_p13", "mathd_algebra_206"),
    )
    for theorem in curator_cases:
        args = dict(
            c.prior_result("adaptation", "curator", theorem)["args"]["args"]
        )
        args.update(
            source_events=c.read(f"sources/{theorem}.json")["events"],
            strict_actions=False,
            evidence_review=False,
            targeted_demos=True,
        )
        path = f"pilot_sources/curation/{theorem}.json"
        c.save(path, args)
        cases.append(
            dict(
                treatment="curation",
                role="curator",
                case=theorem,
                input=path,
                original=asdict(writer_product(theorem)),
                selection_stratum="rejected_check"
                if theorem in failed
                else "executed_without_rejection",
                originally_executed=any(
                    r.executable for r in writer_product(theorem).receipts
                ),
            )
        )

    # Curator demonstrations are actual checked repair histories. Recheck
    # their receipts before authoring the answer, and preserve the dialogue.
    for theorem in (
        "imo_1968_p5_1",
        "amc12a_2002_p13",
        "mathd_algebra_206",
        "aime_1990_p4",
        "amc12b_2003_p17",
    ):
        record = final_writer(theorem)
        product = writer_product(theorem)
        for receipt in product.receipts:
            rechecked = check_snippet(
                receipt.context,
                receipt.snippet,
                dict(seconds=60, rpc_calls=512, view_bytes=8192),
            )
            if rechecked.identifier != receipt.identifier:
                raise ValueError("Demonstration receipt changed: " + theorem)
        if product.plan is not None:
            plan = product.plan
        else:
            plan = BookPlan(
                "Checks do not establish the proposed repair; preserve evidence and abstain from adding advice.",
                tuple(
                    EditIntent(
                        f"d{i + 1}",
                        "drop",
                        "",
                        "",
                        "",
                        "No supported repair within the available checks",
                        (),
                    )
                    for i in range(len(product.drafts))
                ),
            )
        for strict in (False, True):
            query = pydantic_load(
                ProposeLearningEdits,
                dict(
                    record["args"], strict_actions=strict, targeted_demos=True
                ),
            )
            remember(
                demos,
                f"curator_{theorem}_{strict}",
                query,
                learning_plan(plan) if strict else plan,
            )

    assert len(cases) == 52
    path = c.ROOT / "demos/ace_learning.demo.yaml"
    text = yaml.safe_dump(demos, sort_keys=False, allow_unicode=True, width=79)
    path.write_text(text)
    c.save(
        "pilot_registration.json",
        dict(
            cases=cases,
            count=52,
            selection="Six invalid schema finals + six valid controls; all 16 reviews; six accepted/six unsolved reflectors; six curators with a rejected check/six curators with execution and no rejected checks. Preferred training witnesses plus error-tag coverage and SHA256 order.",
            review_annotation="Agent source audit before paid calls; 12 scored and four unresolved cases; compare both support and allowable novelty. Not independent human labels.",
            gate="A treatment requires targeted improvement, no newly accepted unsupported claim, and complete registered cells. Schema: fewer invalid finals, preserving valid controls. Review: fewer scored errors with no newly invented additions/corrections. Reflection/curation: more verified supported local operations, with semantic novelty and unsupported claims separately adjudicated.",
            demonstration_count=len(demos),
            demonstrations_sha256=c.sha(path),
            same_family_examples_excluded=True,
            paid_source_generation=False,
        ),
    )
