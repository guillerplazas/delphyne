"""Two bounded development rounds followed by one frozen validation panel."""

from copy import deepcopy
from dataclasses import asdict
import json
from typing import Any

from delphyne.utils.typing import pydantic_load

from ace.ace_playbook import Playbook
from ace.rocq_snippets import SnippetReceipt

from . import campaign as c
from .artifact import ContextArtifact, Example, checked_example
from .design import schedule, select
from experiments.ace_sanitized.scope import partition


def store_artifact(label: str, artifact: ContextArtifact) -> None:
    c.save(f"artifacts/{label}.json", asdict(artifact))
    c.save(f"artifacts/{label}_render.json", artifact.rendered())


def artifact(label: str) -> ContextArtifact:
    return ContextArtifact.load(c.CAMPAIGN / f"artifacts/{label}.json")


def prepare_artifacts() -> None:
    x3 = c.ROOT / "experiments/playbooks/ace_x3_offline.yaml"
    store_artifact(
        "x3", ContextArtifact(Playbook.load(x3), lineage=(c.sha(x3),))
    )
    polished = c.REFERENCE / "book.yaml"
    base = ContextArtifact(Playbook.load(polished), lineage=(c.sha(polished),))
    store_artifact("polished", base)
    if (c.CAMPAIGN / "artifacts/examples.json").exists():
        artifact("examples")
        return
    book = deepcopy(base.book)
    rule = next(b for b in book.bullets if b.id == "rocq-00015")
    old = rule.content
    rule.content = rule.content.replace(
        "change INR 2 <= INR c", "change (INR 2 <= INR c)"
    )
    if rule.content == old:
        raise ValueError("Expected historical cast syntax defect")
    examples: list[Example] = []
    for path in sorted((c.SANITIZED / "revisions").glob("*.json")):
        revision = json.loads(path.read_text())
        if "writer" not in revision:
            continue
        receipts = [
            pydantic_load(SnippetReceipt, r)
            for r in revision["writer"]["receipts"]
        ]
        by_id = {r.identifier: r for r in receipts}
        for edit in revision["edits"]:
            if edit["action"] != "example":
                continue
            for ident in edit["receipts"]:
                examples.append(
                    checked_example(
                        edit["target_id"],
                        by_id[ident],
                        str(path.relative_to(c.ROOT)) + ":" + c.sha(path),
                    )
                )
    cast_path = c.SANITIZED / "audits/cast_bound_recipe.json"
    cast = pydantic_load(
        SnippetReceipt, json.loads(cast_path.read_text())["checks"][1]
    )
    examples.append(
        checked_example("rocq-00015", cast, str(cast_path.relative_to(c.ROOT)))
    )
    unique = {e.identifier: e for e in examples}
    revised = ContextArtifact(book, tuple(unique.values()), (base.sha256(),))
    store_artifact("examples", revised)
    c.save(
        "initial_revision.json",
        dict(
            before=base.sha256(),
            after=revised.sha256(),
            edit=dict(rule_id=rule.id, before=old, after=rule.content),
            examples=len(unique),
            evidence_scope="exact trainX contexts only",
            preparation="historical learned examples freshly re-executed; no new API calls",
        ),
    )


def totals(jobs: list[c.Job]) -> dict[str, dict[str, Any]]:
    a = c.accounting()
    if a["unresolved"] or a["billing_issues"]:
        raise ValueError("Unsettled measurements")
    values: dict[str, dict[str, Any]] = {}
    for j in jobs:
        result = c.cell_result(j)
        cost = a["costs"].get(c.name(j, None), 0.0)
        fingerprint = c.read(j.input_file)["artifact_sha256"]
        row = values.setdefault(
            j.arm,
            dict(cells=0, solved=0, cost=0.0, artifact_sha256=fingerprint),
        )
        if row["artifact_sha256"] != fingerprint:
            raise ValueError("Arm contains different artifacts")
        row["cells"] += 1
        row["cost"] += cost
        row["solved"] += int(
            bool(result and result["success"] and cost <= j.cap + 1e-12)
        )
    return values


def round1() -> None:
    arms = ["x3", "polished", "examples"]
    candidates = {a: artifact(a) for a in arms}
    jobs = [
        c.proof_job("round1", arm, t, s, candidates[arm])
        for t, s, arm in schedule(c.read("protocol.json")["train"], arms)
    ]
    if len(jobs) != 72:
        raise ValueError("Round 1 must contain 72 cells")
    c.launch("round1", jobs)
    values = totals(jobs)
    historical = select(
        {a: values[a] for a in ("x3", "polished")},
        max(values[a]["solved"] for a in ("x3", "polished")),
    )
    selected = select(values, values[historical]["solved"])
    c.save(
        "round1_selection.json",
        dict(
            values=values,
            historical=historical,
            selected=selected,
            floor=values[historical]["solved"],
        ),
    )


def round2() -> None:
    prior = c.read("round1_selection.json")["selected"]
    audit = c.read("round2_audit.json")
    if (
        not audit["eligible"]
        or audit["artifact_sha256"] != artifact("round2").sha256()
    ):
        raise ValueError("Review the learned artifact before round 2")
    candidates = {"retained": artifact(prior), "revised": artifact("round2")}
    jobs = [
        c.proof_job("round2", arm, t, s, candidates[arm])
        for t, s, arm in schedule(
            c.read("protocol.json")["train"], list(candidates)
        )
    ]
    if len(jobs) != 48:
        raise ValueError("Round 2 must contain 48 cells")
    c.launch("round2", jobs)
    values = totals(jobs)
    floor = c.read("round1_selection.json")["floor"]
    eligible = any(v["solved"] >= floor for v in values.values())
    selected = select(values, floor) if eligible else "retained"
    c.save(
        "round2_selection.json",
        dict(
            values=values,
            selected=selected,
            historical_floor=floor,
            eligible=eligible,
            artifact="round2" if selected == "revised" else prior,
        ),
    )


def freeze() -> None:
    c.verify()
    chosen = c.read("round2_selection.json")["artifact"]
    historical = c.read("round1_selection.json")["historical"]
    treatments = {
        "nonace_ordinary": dict(artifact=None, output_tokens=32768),
        "nonace_matched": dict(artifact=None, output_tokens=8192),
        "ace_historical": dict(artifact=historical, output_tokens=8192),
        "ace_selected": dict(artifact=chosen, output_tokens=8192),
    }
    hashes = {a: artifact(a).sha256() for a in (chosen, historical)}
    c.save(
        "freeze.json",
        dict(
            treatments=treatments,
            artifacts=hashes,
            source_seal_sha256=c.sha(c.CAMPAIGN / "seal.json"),
            validation=sorted(partition("validation")),
            replicates=[0, 1],
        ),
    )


def verify_freeze() -> dict[str, Any]:
    frozen = c.read("freeze.json")
    if frozen["source_seal_sha256"] != c.sha(c.CAMPAIGN / "seal.json"):
        raise ValueError("Frozen source seal drift")
    for label, expected in frozen["artifacts"].items():
        if artifact(label).sha256() != expected:
            raise ValueError("Frozen context artifact drift")
    if frozen["validation"] != sorted(partition("validation")):
        raise ValueError("Frozen panel drift")
    return frozen


def benchmark() -> None:
    frozen = verify_freeze()
    unique: dict[str, tuple[ContextArtifact | None, int]] = {}
    signatures: dict[tuple[str | None, int], str] = {}
    aliases: dict[str, str] = {}
    for arm, treatment in frozen["treatments"].items():
        item = (
            artifact(treatment["artifact"]) if treatment["artifact"] else None
        )
        signature = (
            item.sha256() if item else None,
            treatment["output_tokens"],
        )
        if signature in signatures:
            aliases[arm] = signatures[signature]
        else:
            unique[arm] = (item, treatment["output_tokens"])
            signatures[signature] = arm
    c.save("panel_aliases.json", aliases)
    jobs = [
        c.proof_job("validation", arm, t, s, *unique[arm])
        for t, s, arm in schedule(frozen["validation"], list(unique))
    ]
    if len(jobs) > 320 or len(jobs) != 80 * len(unique):
        raise ValueError("Unregistered validation panel")
    c.launch("validation", jobs)
    c.save(
        "finished.json",
        dict(
            totals=totals(jobs),
            accounting=c.accounting(),
            default_promoted=False,
        ),
    )
