"""Offline explanatory appendix for the fixed ACE attribution campaign.

No model calls. Reads only registered development cells, their receipts,
and the two trainX playbook chains. It never changes a treatment or book.
Both harnesses: python -m tools.reports.ace_attribution_diagnosis.
"""

from experiments.ace import ace_attribution_experiment as c
from collections import Counter, defaultdict
from dataclasses import asdict
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, cast

from ace.ace_playbook import Playbook
from ace.ace_evidence import checkable_references, grounding_verdict
from tools.reports.ace_attribution_report import (
    args_of,
    cache_diagnosis,
    directory_for,
    observations,
)


def outcome_head(directory: Path) -> dict[str, Any]:
    """Read result metrics and avoid loading duplicate raw traces."""
    from tools.analysis.cell_records import (
        _result_head,  # pyright: ignore[reportPrivateUsage]
        _field,  # pyright: ignore[reportPrivateUsage]
    )

    head = _result_head(directory / "result.yaml")
    budget = head[head.find("spent_budget:") :]
    return {
        k: float(_field(budget, k) or 0)
        for k in (
            "num_requests",
            "num_completions",
            "input_tokens",
            "cached_input_tokens",
            "output_tokens",
            "rocq_seconds",
            "price",
        )
    }


def event_index() -> dict[str, list[dict[str, Any]]]:
    rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    path = c.CAMPAIGN / "events.jsonl"
    with path.open() as f:
        for line in f:
            event = json.loads(line)
            rows[event["cell"]].append(event)
    return rows


def include_diagnostic_metadata(diags: dict[str, Any]) -> None:
    """Attach registered source/receipt facts to the small diagnostic arms."""
    accounting = c.accounting()
    for key, d in diags.items():
        if "source" in d:
            continue
        panel, arm_or_effort, theorem = key.split("/")
        cfg = (
            c.proof("validation", arm_or_effort, theorem)
            if panel == "swaps"
            else c.proof("training", "terra-none", theorem, arm_or_effort)
        )
        measured = observations([cfg], accounting)[theorem, "0"]
        d["source"] = str(directory_for(cfg).relative_to(c.ROOT))
        d["observation"] = asdict(measured)


def execution_inventory() -> dict[str, Any]:
    """Check actual exported arguments against every registered proof cell."""
    rows: list[dict[str, Any]] = []
    for item in c.read("planned_proofs.json"):
        cfg = c.proof(
            item["partition"], item["arm"], item["theorem"], item["effort"]
        )
        directory = directory_for(cfg)
        actual = args_of(directory)
        expected = cfg.instantiate(None)
        for field in ("strategy", "args", "policy", "policy_args", "budget"):
            assert actual[field] == getattr(expected, field), (
                str(directory),
                field,
            )
        rows.append(
            dict(
                **item,
                source=str(directory.relative_to(c.ROOT)),
                args_match=True,
                result_sha256=c.digest(directory / "result.yaml"),
                cache_sha256=c.digest(directory / "cache.yaml"),
            )
        )
    assert len(rows) == 272
    generator_rows: list[dict[str, Any]] = []
    for batch in c.read("adaptation_plan.json"):
        for step in batch:
            directory = (
                c.ADAPT_OUTPUT
                / "configs"
                / f"step{step['step']:02d}_generator_{step['bench']}"
            )
            args = args_of(directory)
            assert args["policy_args"]["model_name"] == c.TERRA
            generator_rows.append(
                dict(
                    source=str(directory.relative_to(c.ROOT)),
                    result_sha256=c.digest(directory / "result.yaml"),
                    cache_sha256=c.digest(directory / "cache.yaml"),
                )
            )
    assert len(generator_rows) == 40
    return dict(
        new_proof_episodes=len(rows) + len(generator_rows),
        inference=rows,
        adaptation_generators=generator_rows,
        reused_controls=80,
        control_parity_source="preflight.json",
        source_integrity="seal.json plus the explicit amendment hash chain",
    )


def reprice_registered(inventory: dict[str, Any]) -> dict[str, Any]:
    """Reprice exact runs; shallow CLI discovery misses nested main arms."""
    from tools.analysis.reprice import collect

    runs = {
        (c.ROOT / row["source"]).parent.parent
        for row in inventory["inference"]
    } | {c.ADAPT_OUTPUT}
    rows: list[dict[str, Any]] = []
    for run in sorted(runs):
        for r in collect(run, None):
            assert r.n_mismatched == 0, str(run)
            rows.append(
                dict(
                    run=str(run.relative_to(c.ROOT)),
                    configs=r.n_configs,
                    billed=r.billed,
                    recomputed=r.recomputed,
                    mismatches=r.n_mismatched,
                )
            )
    assert sum(r["configs"] for r in rows) == 402
    embeddings = training_accounting()["embeddings"]["cost"]
    total = sum(r["recomputed"] for r in rows) + embeddings
    assert abs(total - c.accounting()["total"]) < 1e-8
    return dict(
        runs=rows,
        generative_configurations=402,
        embedding_cost=embeddings,
        total_including_embeddings=total,
        receipt_total=c.accounting()["total"],
        note="272 inference configurations plus 130 adaptation role configurations. Embeddings reconcile separately from 25 receipts. No global output discovery.",
    )


def profile(diags: dict[str, Any]) -> dict[str, Any]:
    terminal: Counter[str] = Counter()
    first: Counter[str] = Counter()
    on_solved: Counter[str] = Counter()
    on_unsolved: Counter[str] = Counter()
    summary: dict[str, Any] = dict(
        cells=len(diags),
        first_proposal_solves=0,
        no_submission=0,
        requests=0,
        input_tokens=0,
        cached_input_tokens=0,
        output_tokens=0,
        verifier_seconds=0.0,
        first_error={},
        terminal_error={},
    )
    for d in diags.values():
        solved = d.get("observation", {}).get("solved", False)
        failures = [x for x in d["checks"] if not x["success"]]
        if solved and not failures and d["checks"]:
            summary["first_proposal_solves"] += 1
        summary["no_submission"] += d["no_proof_submission"]
        if failures:
            first[failures[0]["category"]] += 1
            if not solved:
                terminal[failures[-1]["category"]] += 1
        for failure in failures:
            (on_solved if solved else on_unsolved)[failure["category"]] += 1
        summary["requests"] += len(d["model_calls"])
        for call in d["model_calls"]:
            for key in (
                "input_tokens",
                "cached_input_tokens",
                "output_tokens",
            ):
                summary[key] += call["usage"].get(key, 0)
        summary["verifier_seconds"] += sum(
            x["elapsed"] or 0 for x in d["checks"]
        )
    return summary | dict(
        first_error=dict(first),
        terminal_error=dict(terminal),
        failed_steps_on_solved=dict(on_solved),
        failed_steps_on_unsolved=dict(on_unsolved),
    )


def pricing_sensitivity(profiles: dict[str, Any]) -> dict[str, Any]:
    """Accounting decomposition; no alternative run or changed receipts."""
    rows: dict[str, Any] = {}
    for key, p in profiles.items():
        scale = 10 if "/terra-" in key else 1
        uncached = p["input_tokens"] - p["cached_input_tokens"]
        components = dict(
            uncached_input=uncached * 0.2 * scale / 1e6,
            cached_input=p["cached_input_tokens"] * 0.02 * scale / 1e6,
            output=p["output_tokens"] * 1.2 * scale / 1e6,
        )
        rows[key] = dict(
            components=components,
            actual_total=sum(components.values()),
            cached_fraction=p["cached_input_tokens"] / p["input_tokens"],
            all_input_at_uncached_rate=(
                p["input_tokens"] * 0.2 * scale / 1e6 + components["output"]
            ),
            caveat="Price sensitivity at identical observed token counts; not a new uncached or smaller-cap experiment.",
        )
    return rows


def comparative_supplement(
    report: dict[str, Any], cases: dict[str, Any]
) -> dict[str, Any]:
    """Expose fixed-panel pairings and secondary model contrasts."""
    from tools.analysis.paired_evaluation import Observation, compare

    families = c.read("protocol.json")["families"]
    models: dict[str, Any] = {}
    for stage in c.STAGES:
        observed = report["partitions"][stage]["observations"]
        models[stage] = {}
        for treatment in ("none", "ace"):
            arms = {
                model: {
                    (n, "0"): Observation(**v)
                    for n, v in observed[f"{model}-{treatment}"].items()
                }
                for model in ("luna", "terra")
            }
            comp = compare(
                arms["luna"],
                arms["terra"],
                list(arms["luna"]),
                families=families,
                cap_a=0.1,
                cap_b=1.0,
            )
            comp.pop("verdict", None)
            comp["gained"] = [
                n
                for n, seed in arms["luna"]
                if arms["terra"][n, seed].solved
                and not arms["luna"][n, seed].solved
            ]
            comp["lost"] = [
                n
                for n, seed in arms["luna"]
                if arms["luna"][n, seed].solved
                and not arms["terra"][n, seed].solved
            ]
            models[stage][treatment] = comp
    swaps: dict[str, Any] = {}
    for n in c.panel("validation"):
        swaps[n] = {
            arm: cases[f"validation/{arm}/{n}"]["observation"]
            for arm in c.ARMS
        }
        swaps[n].update(
            {
                arm: cases[f"swaps/{arm}/{n}"]["observation"]
                for arm in ("luna-terra-book", "terra-luna-book")
            }
        )
    efforts = {
        n: {
            effort: cases[
                f"training/terra-none/{n}"
                if effort == "medium"
                else f"effort/{effort}/{n}"
            ]["observation"]
            for effort in ("low", "medium", "high")
        }
        for n in c.panel("training")
    }
    return dict(
        model_comparisons=models,
        book_swap_grid=swaps,
        effort_grid=efforts,
        caveat="Secondary contrasts and the prespecified small diagnostic panels; no tuning, selection, or multiplicity-adjusted discovery claim.",
    )


def enriched_cases(
    diags: dict[str, Any], events: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    cases: dict[str, Any] = {}
    for key, d in diags.items():
        if "source" not in d:
            continue
        directory = c.ROOT / d["source"]
        args = args_of(directory)
        spent = outcome_head(directory)
        cap = args["budget"]["price"]
        model = args["policy_args"]["model_name"]
        recorded = events.get(directory.name, [])
        invocation = [
            e
            for e in recorded
            if e["kind"] == "model" and e["decision"] == "invoked"
        ]
        failures = [x for x in d["checks"] if not x["success"]]
        terminal = d["checks"][-1] if d["checks"] else None
        # Necessary capacity conditions, deliberately not an inferred
        # unique stop cause. The final rejected barrier was not exported.
        scale = 1 if model == c.LUNA else 10
        money_minimum = (32768 * 0.2 / 1e6 + 32768 * 1.2 / 1e6) * scale
        constraints = dict(
            remaining_dollars=cap - spent["price"],
            remaining_requests=args["budget"]["num_requests"]
            - spent["num_requests"],
            remaining_verifier_seconds=args["budget"].get("rocq_seconds", 300)
            - spent["rocq_seconds"],
            minimum_possible_next_model_reservation=money_minimum,
            cannot_afford_even_empty_next_request=cap - spent["price"]
            < money_minimum,
            cannot_reserve_full_60_second_compute=300 - spent["rocq_seconds"]
            < 60,
            last_observed_model_reservation=invocation[-1]["estimate_dollars"]
            if invocation
            else None,
            stop_cause_limit="Final declined barrier is not exported; capacity checks are not a unique causal stop classification.",
        )
        cases[key] = dict(
            observation=d["observation"],
            spent_budget=spent,
            constraints=constraints,
            source=d["source"],
            first_error=d.get("first_error"),
            terminal_check=terminal,
            failed_checks=len(failures),
            classes=d["classes"],
            no_submission=d["no_proof_submission"],
            tool_counts=dict(
                Counter(t for call in d["model_calls"] for t in call["tools"])
            ),
            empty_responses=sum(
                not x["response_text"] and not x["tools"]
                for x in d["model_calls"]
            ),
            cited_ids=sorted(
                {i for call in d["model_calls"] for i in call["cited_ids"]}
            ),
        )
    return cases


def bullet_source_groups(store: Path) -> dict[str, list[str]]:
    """Earliest batch provenance, not a claim about one causal source."""
    import csv

    with (store / "steps.csv").open() as f:
        rows = list(csv.DictReader(f))
    out: dict[str, list[str]] = {}
    for index in range(4, len(rows) + 1, 4):
        pb = Playbook.load(store / f"playbook_step_{index:02d}.yaml")
        for b in pb.bullets:
            out.setdefault(b.id, [r["bench"] for r in rows[index - 4 : index]])
    return out


def candidate_references(content: str) -> list[str]:
    """Extract identifiers even when they appear inside longer code spans."""
    names = [
        name
        for span in re.findall(r"`([^`]+)`", content)
        for name in re.findall(r"[A-Za-z_][\w']*(?:\.[A-Za-z_][\w']*)*", span)
    ]
    return [
        n
        for n in checkable_references(names)
        if ("." in n or "_" in n) and n.strip("_")
    ]


def book_audit(
    diags: dict[str, Any], *, live_references: bool = False
) -> dict[str, Any]:
    books = {
        "luna": c.ROOT / c.BOOK,
        "terra": c.ROOT / c.read("terra_book.json")["file"],
    }
    stores = {
        "luna": c.ROOT / "experiments/playbooks/ace_adaptation_x3-offline",
        "terra": c.ROOT / f"experiments/playbooks/ace_adaptation_{c.VARIANT}",
    }
    report: dict[str, Any] = {}
    for label, path in books.items():
        pb = Playbook.load(path)
        sources = bullet_source_groups(stores[label])
        checked_file = c.CAMPAIGN / f"{label}_reference_checks_v2.json"
        cached_checks = (
            json.loads(checked_file.read_text())
            if checked_file.exists()
            else None
        )
        if cached_checks is not None:
            assert cached_checks["book_sha256"] == pb.sha256()
        bullets: list[dict[str, Any]] = []
        for b in pb.bullets:
            # Local binders remain visible, but are not misclassified as
            # nonexistent global lemmas by the optional Locate audit.
            reference_candidates = candidate_references(b.content)
            exposure: list[dict[str, Any]] = []
            for key, d in diags.items():
                arm = key.split("/")[1]
                applies = (
                    label == "luna" and arm in ("luna-ace", "terra-luna-book")
                ) or (
                    label == "terra"
                    and arm in ("terra-ace", "luna-terra-book")
                )
                if not applies:
                    continue
                for call in d["model_calls"]:
                    if b.id not in call["cited_ids"]:
                        continue
                    following = next(
                        (
                            x
                            for x in d["checks"]
                            if x["after_request"] >= call["request"]
                        ),
                        None,
                    )
                    exposure.append(
                        dict(
                            cell=key,
                            request=call["request"],
                            following_success=following["success"]
                            if following
                            else None,
                            following_category=following["category"]
                            if following
                            else None,
                            following_tactic=following["tactic"]
                            if following
                            else None,
                        )
                    )
            checks: list[dict[str, Any]] = []
            if cached_checks is not None:
                checks = [
                    x
                    for x in cached_checks["items"][b.id]
                    if x["identifier"] in reference_candidates
                ]
            elif live_references:
                import runtime.pytanque_utils as pt

                for identifier in reference_candidates:
                    for theorem in sources.get(b.id, []):
                        file = c.partition("training")[theorem]
                        answer = pt.query(
                            file, theorem, f"Locate {identifier}."
                        )
                        verdict = grounding_verdict(answer)
                        checks.append(
                            dict(
                                identifier=identifier,
                                source=theorem,
                                verdict=verdict,
                                answer=answer,
                            )
                        )
                        if verdict == "grounded":
                            break
            bullets.append(
                dict(
                    **asdict(b),
                    candidate_global_references=reference_candidates,
                    source_batch=sources.get(b.id, []),
                    reference_checks=checks,
                    explicit_condition=bool(
                        re.search(r"\b(when|if|for|given)\b", b.content, re.I)
                    ),
                    code_spans=re.findall(r"`([^`]+)`", b.content),
                    citations=exposure,
                )
            )
        report[label] = dict(
            file=str(path.relative_to(c.ROOT)),
            sha256=pb.sha256(),
            bullets=len(pb.bullets),
            tokens_estimate=pb.token_estimate(),
            sections=dict(Counter(b.section for b in pb.bullets)),
            never_cited=sum(not x["citations"] for x in bullets),
            items=bullets,
            caveats=[
                "Citation is not successful application or causal benefit",
                "Condition and reference extraction are heuristic candidates, not quality scores",
                "Locate checks availability, not applicability or logical correctness",
                "Earliest source batch contains four trajectories; exact attribution can be ambiguous",
            ],
        )
    return report


def training_accounting() -> dict[str, Any]:
    with sqlite3.connect(c.CAMPAIGN / "ledger.sqlite3") as db:
        raw = db.execute(
            "SELECT cell,model,charged,usage,status FROM receipts WHERE stage='adaptation'"
        ).fetchall()
    totals: dict[str, Any] = {}
    for cell, model, charged, usage, status in raw:
        role = (
            "embeddings"
            if model.startswith("text-embedding")
            else cell.split("_")[1]
        )
        entry = totals.setdefault(
            role,
            dict(
                requests=0,
                cost=0.0,
                input_tokens=0,
                cached_input_tokens=0,
                output_tokens=0,
                cells=[],
            ),
        )
        if cell not in entry["cells"]:
            entry["cells"].append(cell)
        entry["requests"] += 1
        entry["cost"] += charged or 0
        u = json.loads(usage or "{}")
        entry["input_tokens"] += u.get(
            "input_tokens", u.get("total_tokens", 0)
        )
        entry["output_tokens"] += u.get("output_tokens", 0)
        entry["cached_input_tokens"] += u.get("input_tokens_details", {}).get(
            "cached_tokens", 0
        )
        assert status == "settled"
    return totals


def training_evolution() -> dict[str, Any]:
    """Final-book provenance and role reliability, retaining every step."""
    import csv

    output: dict[str, Any] = {}
    for label, variant in (("luna", "x3-offline"), ("terra", c.VARIANT)):
        directory = (
            c.ROOT / "experiments/playbooks" / f"ace_adaptation_{variant}"
        )
        with (directory / "steps.csv").open() as f:
            rows = list(csv.DictReader(f))
        total = {
            key: sum(int(row.get(key) or 0) for row in rows)
            for key in (
                "generator_solved",
                "generator_failed",
                "reflector_failed",
                "curator_failed",
                "curator_fallback",
                "added",
                "deduped",
                "dropped",
                "pruned",
                "merged",
                "tags_helpful",
                "tags_harmful",
            )
        }
        batches = [rows[i : i + 4] for i in range(0, len(rows), 4)]
        output[label] = dict(
            totals=total,
            steps=rows,
            batches=[
                dict(
                    source_theorems=[r["bench"] for r in batch],
                    solves=sum(int(r["generator_solved"] or 0) for r in batch),
                    tokens=int(batch[-1]["tokens_after"]),
                    bullets=int(batch[-1]["bullets_after"]),
                )
                for batch in batches
            ],
            caveat="Helpful/harmful tags are reflector judgments on cited bullets; they are not verifier-proven causal labels.",
        )
    return output


def training_traces(evolution: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for label, variant in (("luna", "x3-offline"), ("terra", c.VARIANT)):
        for row in evolution[label]["steps"]:
            directory = (
                c.ROOT
                / "experiments/output"
                / f"ace_adaptation_{variant}"
                / "configs"
                / f"step{int(row['step']):02d}_generator_{row['bench']}"
            )
            d = cache_diagnosis(directory)
            failed = bool(int(row.get("generator_failed") or 0))
            spent = outcome_head(directory) if not failed else None
            out[f"{label}/{row['bench']}"] = dict(
                **d,
                source=str(directory.relative_to(c.ROOT)),
                observation=dict(
                    solved=bool(int(row["generator_solved"] or 0)),
                    failed=failed,
                ),
                spent_budget=spent,
            )
    return out


def write_appendix(cases: dict[str, Any], report: dict[str, Any]) -> None:
    lines = [
        "# Per-problem ACE attribution appendix",
        "",
        "Every failure and discordant solve is included. Full responses and",
        "verified-state histories are in complete_diagnostics.json; this view",
        "summarizes the first error, terminal state and resource evidence.",
        "",
    ]
    for stage in c.STAGES:
        lines.extend([f"## {stage}", ""])
        for theorem in c.partition(stage):
            selected = {a: cases[f"{stage}/{a}/{theorem}"] for a in c.ARMS}
            if all(d["observation"]["solved"] for d in selected.values()):
                continue
            lines.extend(
                [
                    f"### {theorem}",
                    "",
                    "| Arm | Solved | Cost | Requests | First error | Last error |",
                    "|---|---:|---:|---:|---|---|",
                ]
            )
            for arm, d in selected.items():
                first = cast(dict[str, Any], d["first_error"] or {}).get(
                    "category", "none"
                )
                terminal = cast(dict[str, Any], d["terminal_check"] or {}).get(
                    "category", "no submission"
                )
                lines.append(
                    f"| {arm} | {int(d['observation']['solved'])} | ${d['observation']['cost']:.5f} | {d['spent_budget']['num_requests']:.0f} | {first} | {terminal} |"
                )
            lines.append("")
            for arm, d in selected.items():
                if d["observation"]["solved"]:
                    continue
                first: dict[str, Any] = d["first_error"] or {}
                terminal: dict[str, Any] = d["terminal_check"] or {}
                error = " ".join(
                    str(
                        first.get("error")
                        or "No submitted proof received a failing verifier verdict."
                    ).split()
                )
                last = " ".join(
                    str(
                        terminal.get("error")
                        or terminal.get("outcome")
                        or "No final verifier check."
                    ).split()
                )
                lines.extend(
                    [
                        f"**{arm}.** First: {error[:1000]}",
                        "",
                        f"Last: {last[:1000]}",
                        "",
                    ]
                )
                if terminal.get("tactic"):
                    lines.extend(
                        ["```rocq", str(terminal["tactic"]), "```", ""]
                    )
                constraints = d["constraints"]
                lines.extend(
                    [
                        f"Remaining allowance: ${constraints['remaining_dollars']:.5f}, {constraints['remaining_requests']:.0f} requests, {constraints['remaining_verifier_seconds']:.2f} verifier seconds. Cited advice: {', '.join(d['cited_ids']) or 'none'}. Final declined barriers were not exported; these remaining allowances do not uniquely establish why execution stopped.",
                        "",
                    ]
                )
    (c.CAMPAIGN / "CASE_APPENDIX.md").write_text("\n".join(lines) + "\n")
    with (c.CAMPAIGN / "CASE_APPENDIX.md").open("a") as f:
        f.write("\n## Fixed book-swap and effort diagnostics\n\n")
        for key, d in cases.items():
            if not key.startswith(("swaps/", "effort/")):
                continue
            terminal: dict[str, Any] = d["terminal_check"] or {}
            f.write(
                f"### {key}\n\n"
                f"Solved: {d['observation']['solved']}; cost: "
                f"${d['observation']['cost']:.5f}; requests: "
                f"{d['spent_budget']['num_requests']:.0f}; failing checks: "
                f"{d['failed_checks']}.\n\n"
            )
            if not d["observation"]["solved"]:
                f.write(
                    "Final error: "
                    + str(terminal.get("error") or terminal.get("outcome"))
                    + "\n\n"
                )
                if terminal.get("tactic"):
                    f.write(f"```rocq\n{terminal['tactic']}\n```\n\n")
    path = c.CAMPAIGN / "CASE_APPENDIX.md"
    path.write_text(path.read_text().rstrip() + "\n")


def plots(report: dict[str, Any]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Matplotlib's overload leaves multi-axis ndarray and kwargs untyped.
    plot: Any = plt
    fig, axes = plot.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    colors = {
        "luna-none": "#777777",
        "luna-ace": "#2463aa",
        "terra-none": "#e89b3c",
        "terra-ace": "#32834a",
    }
    for row, stage in enumerate(c.STAGES):
        for col, normalized in enumerate((False, True)):
            ax = axes[row, col]
            for arm, obs in report["partitions"][stage][
                "observations"
            ].items():
                scale = 10 if normalized and arm.startswith("terra") else 1
                costs = [
                    float(v["cost"]) / scale
                    for v in obs.values()
                    if v["solved"] and not v["failed"]
                ]
                caps = sorted(
                    {0.0005, 1.0, *(x for x in costs if 0.0005 <= x <= 1)}
                )
                ax.step(
                    caps,
                    [sum(x <= cap for x in costs) for cap in caps],
                    where="post",
                    label=arm,
                    color=colors[arm],
                )
            ax.set(
                xscale="log",
                xlabel=(
                    "Final spend at Luna token rates ($)"
                    if normalized
                    else "Actual final cell spend ($)"
                ),
                ylabel="Qualified solves / 40",
                title=stage,
                xlim=(0.0005, 1.0),
                ylim=(0, 40),
            )
            ax.grid(alpha=0.2)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle(
        "Retrospective spend qualification; not smaller-cap admission runs",
        fontsize=10,
    )
    fig.savefig(c.CAMPAIGN / "solve_cost_curves.png", dpi=180)
    fig.savefig(c.CAMPAIGN / "solve_cost_curves.pdf")
    plt.close(fig)


def main() -> None:
    import sys

    c.verify()
    report = c.read("complete_report.json")
    diags = c.read("complete_diagnostics.json")
    inventory = execution_inventory()
    c.save("execution_inventory.json", inventory)
    c.save("reprice_registered.json", reprice_registered(inventory))
    include_diagnostic_metadata(diags)
    c.save(
        "supplemental_diagnostics.json",
        {
            k: d
            for k, d in diags.items()
            if k.startswith(("swaps/", "effort/"))
        },
    )
    cases = enriched_cases(diags, event_index())
    profiles = {
        f"{s}/{a}": profile(
            {k: v for k, v in diags.items() if k.startswith(f"{s}/{a}/")}
        )
        for s in c.STAGES
        for a in c.ARMS
    }
    c.save("failure_profiles.json", profiles)
    c.save("pricing_sensitivity.json", pricing_sensitivity(profiles))
    c.save("case_summaries.json", cases)
    c.save(
        "comparative_supplement.json", comparative_supplement(report, cases)
    )
    c.save(
        "book_audit.json",
        book_audit(diags, live_references="--check-references" in sys.argv),
    )
    c.save("training_accounting.json", training_accounting())
    evolution = training_evolution()
    c.save("training_evolution.json", evolution)
    c.save("training_diagnostics.json", training_traces(evolution))
    write_appendix(cases, report)
    plots(report)
    print(json.dumps(profiles, indent=2))


if __name__ == "__main__":
    main()
