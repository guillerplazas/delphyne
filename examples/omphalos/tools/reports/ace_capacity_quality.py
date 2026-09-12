"""Matched creator-output audit with development-only Rocq source checks.

Availability is deliberately recorded separately from recommendation,
applicability and causal usefulness. Mentions of known bad identifiers in
warnings are not counted as hallucinations.
"""

# ruff: noqa: E402
from runtime.development_only import install

install()

from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import json
import re
from typing import Any, cast

from ace.ace_evidence import grounding_verdict
from ace.ace_verified_snippets import SnippetWitness, preserve_verified_snippet
from experiments.ace import ace_capacity_experiment as c
from runtime import pytanque_utils as pt
from experiments.common.ace_pools import POOLS
from tools.reports.ace_attribution_diagnosis import candidate_references
from tools.reports.ace_attribution_report import cache_diagnosis


def strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[Any] = list(cast(dict[str, Any], value).values())
        return [s for v in values for s in strings(v)]
    if isinstance(value, list):
        items = cast(list[Any], value)
        return [s for v in items for s in strings(v)]
    return []


def locate(job: tuple[str, str]) -> dict[str, Any]:
    theorem, identifier = job
    file, _ = POOLS["trainX"][theorem]
    command = (
        f"Print Scope {identifier}."
        if identifier.endswith("_scope")
        else f"Locate {identifier}."
    )
    answer = pt.query(file, theorem, command)
    return dict(
        theorem=theorem,
        identifier=identifier,
        command=command,
        answer=answer,
        verdict=grounding_verdict(answer),
    )


def main() -> None:
    c.verify()
    rows: list[dict[str, Any]] = c.read("creation_audit.json")["rows"]
    items: list[dict[str, Any]] = []
    jobs: set[tuple[str, str]] = set()
    for row in rows:
        raw = c.args_of(c.ROOT / row["source"])["args"]
        # Each registered source is a trainX role job, including reducers.
        name = (c.ROOT / row["source"]).name
        theorem = name.split("_" + row["role"] + "_", 1)[1]
        assert theorem in POOLS["trainX"]
        output = "\n".join(strings(row["output"]))
        input_text = "\n".join(strings(raw))
        candidates = candidate_references(output)
        mentions: list[dict[str, Any]] = []
        for ref in candidates:
            contexts = [s for s in strings(row["output"]) if ref in s]
            mentions.append(
                dict(
                    identifier=ref,
                    contexts=contexts,
                    present_in_input=ref in input_text,
                )
            )
            jobs.add((theorem, ref))
        spans = re.findall(r"`([^`\n]+)`", output)
        items.append(
            dict(
                source=row["source"],
                output_source=row["output_source"],
                theorem=theorem,
                role=row["role"],
                model=row["model"],
                unbound_citations=row["unbound_citations"],
                output=row["output"],
                references=mentions,
                inline_examples=spans,
                examples_absent_from_input=[
                    s for s in spans if s not in input_text
                ],
                input_outcome=raw.get("outcome"),
                operation_count=len(
                    cast(dict[str, Any], row["output"] or {}).get(
                        "operations", []
                    )
                ),
            )
        )
    checks_path = c.CAMPAIGN / "creator_reference_checks.json"
    if checks_path.exists():
        checks = c.read(checks_path.name)
        assert {(r["theorem"], r["identifier"]) for r in checks} == jobs
    else:
        with ProcessPoolExecutor(max_workers=4) as pool:
            checks = list(pool.map(locate, sorted(jobs)))
        c.save(checks_path.name, checks)
    index = {(r["theorem"], r["identifier"]): r for r in checks}
    for item in items:
        for ref in item["references"]:
            ref["source_availability"] = index[
                item["theorem"], ref["identifier"]
            ]
    groups: dict[str, Any] = {}
    for model in (c.old.LUNA, c.old.TERRA):
        for role in ("reflector", "curator", "reducer"):
            selected = [
                r for r in items if r["model"] == model and r["role"] == role
            ]
            refs = [v for r in selected for v in r["references"]]
            groups[f"{model}/{role}"] = dict(
                cells=len(selected),
                operations=sum(r["operation_count"] for r in selected),
                reference_mentions=len(refs),
                source_availability=dict(
                    Counter(v["source_availability"]["verdict"] for v in refs)
                ),
                output_examples=sum(
                    len(r["inline_examples"]) for r in selected
                ),
                examples_absent_from_input=sum(
                    len(r["examples_absent_from_input"]) for r in selected
                ),
            )
    c.save(
        "creator_quality.json",
        dict(
            items=items,
            groups=groups,
            caveats=[
                "Not an automatic hallucination or quality score: many unavailable names are explicitly criticized.",
                "Availability is checked in the named source theorem, not every theorem in a reducer batch.",
                "Exact text novelty is not semantic novelty; existing local names and mathematical templates are not global lemmas.",
                "These frozen single-role jobs do not measure downstream adaptation or proof benefit.",
            ],
        ),
    )
    target = next(r for r in rows if r["have_assignment_examples"])
    witness = SnippetWitness(**c.read("snippet_witness.json"))
    if not (c.CAMPAIGN / "fresh_reducer_snippet_check.json").exists():
        verdict = preserve_verified_snippet(
            witness, target["have_assignment_examples"][0]
        )
        c.save(
            "fresh_reducer_snippet_check.json",
            dict(
                output_source=target["output_source"], verdict=asdict(verdict)
            ),
        )
    contextual_audit(items)
    terminal_evidence()
    print(json.dumps(groups, indent=2))


def contextual_audit(items: list[dict[str, Any]]) -> None:
    plan = c.old.read("adaptation_plan.json")
    jobs: set[tuple[str, str]] = set()
    for item in items:
        if item["role"] != "reducer":
            continue
        batch = next(b for b in plan if b[0]["bench"] == item["theorem"])
        for ref in item["references"]:
            if ref["source_availability"]["verdict"] == "missing":
                jobs.update((s["bench"], ref["identifier"]) for s in batch[1:])
    filename = "creator_batch_reference_checks.json"
    if (c.CAMPAIGN / filename).exists():
        checks = c.read(filename)
        assert {(r["theorem"], r["identifier"]) for r in checks} == jobs
    else:
        with ProcessPoolExecutor(max_workers=4) as pool:
            checks = list(pool.map(locate, sorted(jobs)))
        c.save(filename, checks)
    index = {(r["theorem"], r["identifier"]): r for r in checks}
    contextual: list[dict[str, Any]] = []
    for item in items:
        for ref in item["references"]:
            if ref["source_availability"]["verdict"] != "missing":
                continue
            available: list[str] = []
            if item["role"] == "reducer":
                batch = next(
                    b for b in plan if b[0]["bench"] == item["theorem"]
                )
                available = [
                    s["bench"]
                    for s in batch[1:]
                    if index[s["bench"], ref["identifier"]]["verdict"]
                    == "grounded"
                ]
            contextual.append(
                dict(
                    output_source=item["output_source"],
                    role=item["role"],
                    model=item["model"],
                    theorem=item["theorem"],
                    identifier=ref["identifier"],
                    contexts=ref["contexts"],
                    available_in_other_batch_source=available,
                )
            )
    c.save("creator_contextual_audit.json", contextual)


def terminal_evidence() -> None:
    rows: list[dict[str, Any]] = []
    for cfg in c.read("planned_creation.json"):
        if cfg["role"] != "reflector" or cfg["model"] != c.old.LUNA:
            continue
        source = c.ROOT / cfg["source"].replace("_reflector_", "_generator_")
        theorem = source.name.split("_generator_", 1)[1]
        last = cache_diagnosis(source)["last_check"]
        if not last or not last["success"]:
            continue
        trajectory = c.args_of(c.ROOT / cfg["source"])["args"]["trajectory"]
        rows.append(
            dict(
                theorem=theorem,
                source=str(source.relative_to(c.ROOT)),
                verified_code="\n".join(last["verified_prefix"]),
                last_tactic=last["verified_prefix"][-1],
                final_tactic_visible=last["verified_prefix"][-1]
                in trajectory.split("[ASSISTANT]")[-1],
                final_check=last,
            )
        )
        if (
            theorem == "amc12_2000_p6"
            and not (c.CAMPAIGN / "reflector_terminal_witness.json").exists()
        ):
            witness = SnippetWitness(
                "reflector-final-kernel-receipt",
                POOLS["trainX"][theorem][0],
                theorem,
                str(source.relative_to(c.ROOT)),
                "\n".join(last["verified_prefix"][:-1]),
                "nia",
                {},
                ".",
            )
            verdict = preserve_verified_snippet(witness, "norm_num in *")
            c.save(
                "reflector_terminal_witness.json",
                dict(
                    witness=asdict(witness),
                    verdict=asdict(verdict),
                    frozen_trajectory_tail=trajectory[-4200:],
                ),
            )
    c.save("creator_terminal_evidence.json", rows)


if __name__ == "__main__":
    main()
