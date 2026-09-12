"""Produce development-only case appendices and resource/price summaries."""

# ruff: noqa: E402
from runtime.development_only import install

install()

from collections import defaultdict
import json
from pathlib import Path
from typing import Any

import yaml

from experiments.ace import ace_capacity_experiment as c
from runtime.model_registry import price_tokens


def short(model: str) -> str:
    return model.rsplit("-", 1)[-1].capitalize()


def describe(d: dict[str, Any]) -> dict[str, Any]:
    row = d["observation"]
    terminal: dict[str, Any] = d["terminal"][-1] if d["terminal"] else {}
    limiting: dict[str, Any] = terminal.get("last_admission") or {}
    last: dict[str, Any] = d.get("last_check") or {}
    classes = d.get("classes", {})
    return dict(
        solved=row["solved"],
        failed=row["failed"],
        cost=row["cost"],
        requests=row["requests"],
        rocq_seconds=row["rocq_seconds"],
        last_category=last.get("category", "no-proof-submission"),
        error_classes=classes,
        feedback_views=len(d["obligation_views"]),
        terminal=(
            "platform_failure"
            if row["failed"]
            else terminal.get("decision", "historical-uninstrumented")
        ),
        limiting=limiting.get("limiting", []),
        pending=terminal.get("pending"),
        remaining=limiting.get("remaining"),
        repeated_error_attempts=sum(
            max(0, n - 1)
            for n in d.get("repeated_failing_tactics", {}).values()
        ),
    )


def feedback_exposure(details: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, d in details.items():
        for view in d["obligation_views"]:
            data = yaml.safe_load(view["result"])
            rows.append(
                dict(cell=key, observation=d["observation"], result=data)
            )
    return rows


def pricing(cross: dict[str, Any]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in cross["rows"]:
        groups[f"{row['model']}/{row['book']}"].append(row)
    result: dict[str, Any] = {}
    for key, rows in groups.items():
        rates: dict[str, list[float]] = {
            "actual": [r["cost"] for r in rows],
            "uncached": [
                price_tokens(
                    r["model"],
                    int(r["input_tokens"]),
                    0,
                    int(r["output_tokens"]),
                )
                for r in rows
            ],
            "luna_rates": [
                price_tokens(
                    c.old.LUNA,
                    int(r["input_tokens"]),
                    int(r["cached_input_tokens"]),
                    int(r["output_tokens"]),
                )
                for r in rows
            ],
        }
        result[key] = {
            kind: dict(
                total=sum(costs),
                cost_per_raw_solve=sum(costs) / sum(r["solved"] for r in rows),
                qualification_curve={
                    str(cap): sum(
                        r["solved"] and not r["failed"] and cost <= cap + 1e-8
                        for r, cost in zip(rows, costs, strict=True)
                    )
                    for cap in (0.02, 0.05, 0.1, 0.2, 0.5, 1.0)
                },
            )
            for kind, costs in rates.items()
        }
    return dict(
        groups=result,
        caveat="Post-hoc repricing of observed trajectories, not reruns at different prices or hard caps. Actual totals include every failed attempt. Luna-rate normalization removes the tariff difference, not token/strategy differences.",
    )


def verify_path_costs(mechanism: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for level, report in mechanism.items():
        for r in report["rows"]:
            # Snapshot/cache usage includes its whole paid prefix; the ledger
            # sums only new charges at each level. These must agree.
            delta = r["token_cost"] - r["cost"]
            if abs(delta) > 1e-8:
                raise ValueError(
                    (r["identifier"], "prefix charge mismatch", delta)
                )
            rows.append(
                dict(
                    cell=r["identifier"],
                    level=int(level),
                    token_cost=r["token_cost"],
                    path_cost=r["cost"],
                    difference=delta,
                )
            )
    return rows


def causal_exposure_audit(details: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model in (c.old.LUNA, c.old.TERRA):
        for theorem in c.read("protocol.json")["diagnostic_panel"]:
            for a, b in (("A", "C"), ("B", "D")):
                da = details[f"{theorem}__{a}-level0__{model}__seed0"]
                db = details[f"{theorem}__{b}-level0__{model}__seed0"]

                def first_request(d: dict[str, Any]) -> dict[str, Any]:
                    entries: list[dict[str, Any]] = yaml.load(
                        (
                            c.ROOT / d["observation"]["source"] / "cache.yaml"
                        ).read_text(),
                        Loader=yaml.CSafeLoader,
                    )
                    return next(
                        e["input"]["request"]
                        for e in entries
                        if e["input"]["request"]["options"].get("model")
                        != "__compute__"
                    )

                first_a, first_b = first_request(da), first_request(db)
                rows.append(
                    dict(
                        model=model,
                        theorem=theorem,
                        contrast=f"{a}->{b}",
                        first_request_equal=first_a == first_b,
                        first_response_equal=da["model_calls"][0][
                            "response_text"
                        ]
                        == db["model_calls"][0]["response_text"],
                        treatment_exposed=bool(db["obligation_views"]),
                        solved_a=da["observation"]["solved"],
                        solved_b=db["observation"]["solved"],
                        caveat="A no-trigger outcome difference is not evidence that added goal feedback caused it.",
                    )
                )
    return rows


def write_cases(
    cross: dict[str, Any],
    mechanism: dict[str, Any],
    details: dict[str, Any],
    cross_details: dict[str, Any],
) -> None:
    lines = [
        "# Capacity follow-up: proof-case appendix",
        "",
        "Every diagnostic observation and every failed/discordant validation observation is listed below. "
        "Full ordered checks, model replies, errors, proof prefixes, token usage, admission events and goal views "
        "are retained in `mechanism_diagnostics_v2.json` and `crossover_diagnostics.json`. "
        "Categories describe observed verifier errors; they do not prove their root cause.",
        "",
        "## Eight-problem outcome matrix",
        "",
        "S = kernel-verified success; F = unsolved; P = platform failure. One seed, eight selected trainX problems.",
        "",
        "| Model/problem | A | B | C | D | E | C money | E money | C search | E search |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for model in (c.old.LUNA, c.old.TERRA):
        for theorem in c.read("protocol.json")["diagnostic_panel"]:
            outcomes: list[str] = []
            for level, profile in (
                (0, "A"),
                (0, "B"),
                (0, "C"),
                (0, "D"),
                (0, "E"),
                (1, "C"),
                (1, "E"),
                (2, "C"),
                (2, "E"),
            ):
                row = next(
                    r
                    for r in mechanism[str(level)]["rows"]
                    if r["model"] == model
                    and r["theorem"] == theorem
                    and r["profile"] == profile
                )
                outcomes.append(
                    "P" if row["failed"] else "S" if row["solved"] else "F"
                )
            lines.append(
                f"| {short(model)} {theorem} | " + " | ".join(outcomes) + " |"
            )
    discordant = {
        t
        for v in cross["comparisons"].values()
        for t in v["gains"] + v["losses"]
    }
    for title, selected in (
        ("Diagnostic and continuation cells", details),
        (
            "Validation failures and discordances",
            {
                k: d
                for k, d in cross_details.items()
                if not d["observation"]["solved"]
                or d["observation"]["theorem"] in discordant
            },
        ),
    ):
        lines.extend(["", "## " + title, ""])
        for key, d in sorted(selected.items()):
            row = d["observation"]
            summary = describe(d)
            lines.extend(
                [
                    "### " + key,
                    "",
                    f"Source: `{row['source']}`. "
                    f"{'Platform failure' if row['failed'] else 'Solved' if row['solved'] else 'Unsolved'}; "
                    f"${row['cost']:.8f}; {row['requests']} completions; {row['rocq_seconds']:.3f} verifier seconds.",
                    "",
                    f"Terminal: `{summary['terminal']}`; limiting dimensions: `{summary['limiting']}`; "
                    f"last category: `{summary['last_category']}`; added goal views: {summary['feedback_views']}. "
                    f"Error counts: `{summary['error_classes']}`.",
                    "",
                ]
            )
            if d.get("first_error"):
                lines.extend(
                    [
                        "First error:",
                        "",
                        "```text",
                        str(d["first_error"]["error"]),
                        "```",
                        "",
                    ]
                )
            last = d.get("last_check")
            if last and not last["success"]:
                lines.extend(
                    [
                        "Last submitted proof checkpoint:",
                        "",
                        "```json",
                        json.dumps(last, indent=2, ensure_ascii=False),
                        "```",
                        "",
                    ]
                )
            if row["failed"]:
                lines.extend(
                    [
                        "Failure is retained at subsequent levels; no remote retry. See the immutable exception file and supervised-completion record.",
                        "",
                    ]
                )
    (c.CAMPAIGN / "CASE_APPENDIX.md").write_text("\n".join(lines) + "\n")


def write_creators() -> None:
    quality = c.read("creator_quality.json")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in quality["items"]:
        grouped[item["source"]].append(item)
    lines = [
        "# Matched creator-output appendix",
        "",
        "100 frozen inputs × two models = 200 role jobs. The inputs are fixed; these outputs were not fed into a new adaptation run. "
        "All generated structured output is reproduced below. Availability and exact-source snippet checks are separate artifacts; "
        "an unavailable name inside a warning is not a hallucinated recommendation.",
        "",
    ]
    for source, items in sorted(grouped.items()):
        lines.extend(
            [
                "## " + Path(source).name,
                "",
                "Frozen input: `" + source + "`.",
                "",
            ]
        )
        for item in sorted(items, key=lambda r: r["model"]):
            lines.extend(
                [
                    "### " + short(item["model"]),
                    "",
                    "Output: `" + item["output_source"] + "`.",
                    "",
                    f"Unbound citations: `{item['unbound_citations']}`.",
                    "",
                    "```json",
                    json.dumps(item["output"], indent=2, ensure_ascii=False),
                    "```",
                    "",
                ]
            )
    (c.CAMPAIGN / "CREATOR_APPENDIX.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    c.verify()
    cross = c.read("crossover_report.json")
    mechanism = c.read("mechanism_report_v2.json")
    details = c.read("mechanism_diagnostics_v2.json")
    cross_details = c.read("crossover_diagnostics.json")
    profiles: dict[str, Any] = {}
    for key, d in details.items():
        profiles[key] = describe(d)
    c.save("failure_profiles_v2.json", profiles)
    c.save("pricing_sensitivity.json", pricing(cross))
    c.save("prefix_cost_conservation.json", verify_path_costs(mechanism))
    c.save("feedback_exposure_v2.json", feedback_exposure(details))
    c.save("causal_exposure_audit.json", causal_exposure_audit(details))
    write_cases(cross, mechanism, details, cross_details)
    write_creators()


if __name__ == "__main__":
    main()
