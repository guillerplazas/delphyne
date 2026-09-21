"""Trace retained rules back to the scored source that first introduced them.

Origin is provenance, not a causal assertion that a rule would solve its
source or that terminal rewrites preserve every original detail.
"""

from collections import Counter, defaultdict
import json
from typing import Any

from .common import CAMPAIGN, REPORT, read, save
from .fresh import receipts, solver_rows


def run() -> None:
    sources = solver_rows("source", receipts())
    indexed = {(r["arm"], r["theorem"]): r for r in sources}
    recipes: dict[str, Any] = {}
    for arm in ("A2", "B1", "B2", "S1", "P1"):
        prefix = "ladder_v2__sol_medium__" if arm == "P1" else f"full_{arm}__"
        origins: dict[str, dict[str, Any]] = {}
        warnings: Counter[str] = Counter()
        operations: Counter[str] = Counter()
        tags: Counter[str] = Counter()
        seen_sources: set[str] = set()
        for path in sorted((CAMPAIGN / "learning_events").glob(prefix + "*")):
            event = read(path)
            if "merge" not in event:
                continue
            seen_sources.add(event["theorem"])
            merged = event["merge"]
            for key in ("added", "deduped", "dropped"):
                operations[key] += len(merged[key])
            warnings.update(merged.get("warnings", []))
            for tag in event["reflection"]["bullet_tags"]:
                tags[tag["tag"]] += 1
            for identity in merged["added"]:
                if identity in origins:
                    raise ValueError("A stable rule ID was added twice")
                origins[identity] = dict(
                    theorem=event["theorem"],
                    event=str(path.relative_to(CAMPAIGN)),
                    evidence_hash=event["evidence_hash"],
                )
        filename = (
            "ladder_v2__sol_medium.json"
            if arm == "P1"
            else arm + "_frozen.json"
        )
        frozen = read(CAMPAIGN / "books" / filename)
        source_arm = (
            "source_plain" if arm.startswith("B") else "source_assisted"
        )
        groups: dict[str, dict[str, Any]] = defaultdict(
            lambda: dict(
                source_theorems=0,
                source_cost=0.0,
                final_bullets=0,
                final_content_characters=0,
            )
        )
        source_classes: dict[str, str] = {}
        for theorem in sorted(seen_sources):
            source = indexed[source_arm, theorem]
            category = (
                "one_request_success"
                if source["solved"] and source["counts"].get("requests") == 1
                else "multiple_request_success"
                if source["solved"]
                else "failed_source"
            )
            source_classes[theorem] = category
            groups[category]["source_theorems"] += 1
            groups[category]["source_cost"] += source["costs"]["price"]
        rules: list[dict[str, Any]] = []
        for bullet in frozen["playbook"]["bullets"]:
            origin = origins[bullet["id"]]
            category = source_classes[origin["theorem"]]
            group = groups[category]
            group["final_bullets"] += 1
            group["final_content_characters"] += len(bullet["content"])
            rules.append(
                dict(
                    id=bullet["id"],
                    category=category,
                    content=bullet["content"],
                    **origin,
                )
            )
        recipes[arm] = dict(
            source_classes=dict(groups),
            growth_operations=dict(operations),
            growth_tags=dict(tags),
            growth_warnings=dict(warnings),
            retained_rules=rules,
        )
    save(
        REPORT / "book_signal.json",
        dict(
            recipes=recipes,
            meaning=__doc__,
            limitations="The categories describe source outcomes, not rule correctness or utility. A failed overall source can contain a verified useful intermediate step. Final contents can have been rewritten by a terminal auditor. No inference of bullet use or causal effect is made.",
        ),
    )
    print(
        json.dumps(
            {a: r["source_classes"] for a, r in recipes.items()}, indent=2
        )
    )


if __name__ == "__main__":
    run()
