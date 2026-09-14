"""Offline writer-pilot audit and gate, shared by Codex and Claude Code.

Commands: audit SEED (real Rocq, no API), finish SEED (requires explicit
per-item utility review). Failed cells stay in the denominator. No paid calls.
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from dataclasses import asdict
import hashlib
import gzip
import json
import sys
from typing import Any
from unittest.mock import patch

import yaml

from ace.ace_playbook import Playbook, merge
from ace.rocq_snippets import SnippetReceipt, check_snippet
from delphyne.utils.typing import pydantic_load
from experiments import writer_draft_experiment as c
from experiments.resource_completion_experiment import token_summary
from tools.reports.snippet_results import cache_tokens


def item_id(receipt: SnippetReceipt, explanation: str) -> str:
    return hashlib.sha256(
        (receipt.identifier + explanation).encode()
    ).hexdigest()[:20]


def audit(seed: int) -> None:
    c.verify()
    c.replay(seed)
    before = c.accounting()["receipts"]
    c.activate(seed, events=False)
    a = c.accounting()
    cells: list[dict[str, Any]] = []
    items: dict[str, Any] = {}
    book = Playbook.load(c.ROOT / c.old.base.BOOK)
    for cfg in c.configs(seed):
        cell = c.name(cfg, None)
        product = c.product(cfg)
        raw = c.cell_result(cfg)
        cache = c.directory(cfg) / "cache.yaml"
        tokens = a["tokens"].get(cell, dict(input=0, cached=0, output=0))
        if cache.exists():
            assert cache_tokens(cache) == tokens
        cost = a["costs"].get(cell, 0)
        assert abs(token_summary([tokens])["dated_tariff_cost"] - cost) < 1e-8
        calls: list[dict[str, Any]] = []
        checks: list[dict[str, Any]] = []
        for path in sorted(
            (c.CAMPAIGN / "transport" / cell).glob("*.json.gz")
        ):
            response = json.loads(gzip.decompress(path.read_bytes()))
            for output in response["response"]["outputs"]:
                calls.extend(
                    t
                    for t in output.get("tool_calls", [])
                    if t["name"] == "CheckRocqSnippet"
                )
        if cache.exists():
            for entry in yaml.safe_load(cache.read_text()):
                request = entry["input"]["request"]
                if request["options"].get("model") != "__compute__":
                    continue
                call = yaml.safe_load(request["chat"][-1]["content"])
                if call.get("fun") == "check_snippet":
                    receipt = pydantic_load(
                        SnippetReceipt,
                        yaml.safe_load(
                            entry["output"]["outputs"][0]["content"]
                        ),
                    )
                    checks.append(
                        dict(
                            receipt=asdict(receipt),
                            identifier=receipt.identifier,
                        )
                    )
        merged = merge(book, product.delta.operations, []) if product else None
        merged_text = (
            merged.playbook.render_prompt() if merged else book.render_prompt()
        )
        eligible: list[str] = []
        if product:
            for op in product.answer.operations:
                for rid in op.receipts:
                    receipt = next(
                        r for r in product.receipts if r.identifier == rid
                    )
                    with patch.object(
                        c.CampaignResponsesModel,
                        "_send_final_request",
                        side_effect=AssertionError("HTTP forbidden"),
                    ):
                        checked = check_snippet(
                            receipt.context,
                            receipt.snippet,
                            dict(seconds=60, rpc_calls=512, view_bytes=8192),
                        )
                    if (
                        checked.identifier != receipt.identifier
                        or not checked.executable
                    ):
                        raise ValueError(
                            "Retained snippet real-Rocq replay failed: " + rid
                        )
                    ident = item_id(receipt, op.explanation)
                    items[ident] = dict(
                        source=receipt.context.theorem_name,
                        context=asdict(receipt.context),
                        snippet=receipt.snippet,
                        explanation=op.explanation,
                        receipt_id=rid,
                        status=receipt.status,
                        real_rocq_replay=True,
                        survives_merge=rid in merged_text
                        and receipt.snippet in merged_text,
                    )
                    if items[ident]["survives_merge"]:
                        eligible.append(ident)
        cases = [d["context_id"] for d in c.read(cfg.writer_input)["drafts"]]
        cells.append(
            dict(
                cell=cell,
                role=cfg.role,
                case=cfg.bench_name,
                arm=cfg.arm,
                seed=seed,
                complete=product is not None,
                cost=cost,
                tokens=tokens,
                model_requests=raw["spent_budget"].get("num_completions", 0)
                if raw
                else 0,
                tool_calls=calls,
                checks=checks,
                eligible_items=eligible,
                draft_contexts=cases,
                answer=asdict(product.answer) if product else None,
                merged_book_sha256=merged.playbook.sha256()
                if merged
                else book.sha256(),
            )
        )
    assert before == c.accounting()["receipts"]
    c.save(
        f"audit_seed{seed}.json",
        dict(cells=cells, items=items, api_calls=0, all_required_cells=20),
    )
    # No arm/cell identity in this utility review surface. Review against the
    # registered source rubric; record judgments without altering measurements.
    c.save(f"review_items_seed{seed}.json", items)


def finish(seed: int) -> None:
    c.verify()
    audit = c.read(f"audit_seed{seed}.json")
    review = c.read(f"utility_review_seed{seed}.json")
    if set(review) != set(audit["items"]):
        raise ValueError("Every retained item requires a utility decision")
    for decision in review.values():
        if (
            not isinstance(decision["useful"], bool)
            or not decision["reason"].strip()
            or not decision["pattern"].strip()
        ):
            raise ValueError(
                "Review needs useful, reason and reusable-pattern key"
            )
    cells = audit["cells"]
    for row in cells:
        # Duplicate generic repairs within a reducer batch count only once.
        row["useful_patterns"] = sorted(
            {
                review[i]["pattern"]
                for i in row["eligible_items"]
                if review[i]["useful"]
            }
        )
        row["useful"] = len(row["useful_patterns"])
    summaries: dict[str, Any] = {}
    for role in ("curator", "reducer"):
        for arm in ("control", "draft"):
            rows = [r for r in cells if r["role"] == role and r["arm"] == arm]
            total = sum(r["cost"] for r in rows)
            useful = sum(r["useful"] for r in rows)
            summaries[role + "/" + arm] = dict(
                required=len(rows),
                completed=sum(r["complete"] for r in rows),
                with_useful=sum(r["useful"] > 0 for r in rows),
                useful=useful,
                cost=total,
                cost_per_useful=total / useful if useful else None,
                checks=sum(len(r["checks"]) for r in rows),
                requested_tool_calls=sum(len(r["tool_calls"]) for r in rows),
                tokens={
                    key: sum(r["tokens"].get(key, 0) for r in rows)
                    for key in ("input", "cached", "output")
                },
            )
    paired: list[dict[str, Any]] = []
    for role in ("curator", "reducer"):
        for batch in range(2):
            names = (
                c.old.SOURCES[4 * batch : 4 * batch + 4]
                if role == "curator"
                else (f"batch{batch}",)
            )
            pair = {
                a: sum(
                    r["useful"]
                    for r in cells
                    if r["role"] == role
                    and r["arm"] == a
                    and r["case"] in names
                )
                for a in ("control", "draft")
            }
            paired.append(dict(role=role, batch=batch, **pair))
    checks_both = all(
        any(
            r["arm"] == "draft"
            and any(
                ch["receipt"]["context"]["theorem_name"]
                in c.old.SOURCES[b * 4 : b * 4 + 4]
                for ch in r["checks"]
            )
            for r in cells
        )
        for b in (0, 1)
    )
    expand = (
        all(r["complete"] for r in cells if r["arm"] == "draft")
        and checks_both
        and any(p["draft"] > p["control"] for p in paired)
        and sum(r["useful"] for r in cells if r["arm"] == "draft") > 0
    )
    c.save(
        f"results_seed{seed}.json",
        dict(
            cells=cells,
            summary=summaries,
            paired_batches=paired,
            accounting=c.accounting(),
            statistical_support=False,
            explanation="two reused source batches, related families and repeated seeds; descriptive pilot only, no default promotion",
        ),
    )
    gate: dict[str, Any] = dict(
        expand=expand if seed == 0 else False,
        mechanism=checks_both,
        paired=paired,
        required_complete=len(cells) == 20,
        no_invalid_retained_code=True,
    )
    if seed == 1:
        earlier = c.read("results_seed0.json")
        all_cells = earlier["cells"] + cells
        costs = {
            a: sum(r["cost"] for r in all_cells if r["arm"] == a)
            for a in ("control", "draft")
        }
        useful = {
            a: sum(r["useful"] for r in all_cells if r["arm"] == a)
            for a in ("control", "draft")
        }
        repeated = any(
            p["draft"] > p["control"] and q["draft"] > q["control"]
            for p, q in zip(earlier["paired_batches"], paired, strict=True)
        )
        efficient = useful["draft"] > 0 and (
            useful["control"] == 0
            or costs["draft"] / useful["draft"]
            <= costs["control"] / useful["control"]
        )
        gate.update(
            retain_exploratory=expand
            and repeated
            and useful["draft"] > useful["control"]
            and efficient,
            repeated_advantage=repeated,
            cost_per_useful_no_worse=efficient,
            costs=costs,
            useful=useful,
        )
    c.save(f"gate_seed{seed}.json", gate)
    print(
        json.dumps(
            dict(
                summary=summaries, gate=gate, cost=c.accounting()["new_total"]
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    command, seed = sys.argv[1], int(sys.argv[2])
    if command == "audit":
        audit(seed)
    elif command == "finish":
        finish(seed)
    else:
        raise ValueError(command)
