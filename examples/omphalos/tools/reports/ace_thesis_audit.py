"""Rebuild permitted historical evidence, never read mixed aggregate reports.

Both harnesses: python -m tools.reports.ace_thesis_audit [--limit N].
The optional limit is for debugging, never a claim of exhaustive coverage.
Each cached row binds the analysis source and raw bytes, so resuming cannot
silently reuse a classification after either changes. Legacy costs without
a billing ledger are explicitly cache-based at the recorded/current tariff.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
from typing import Any, cast

import yaml

from experiments.ace_thesis import campaign as c
from experiments.ace_sanitized.scope import partition
from experiments.ace_thesis.artifact import fingerprint
from experiments.ace_thesis.evidence import failure_category
from runtime.model_registry import price_tokens

AUDIT = c.CAMPAIGN / "audit"
EXCLUDE = ("test", "challenge", "confirmation", "ladon", "review_terra")
DEVELOPMENT_ONLY = {
    "ace_roles_20260913",
    "ace_revision_20260913",
    "ace_learning_20260914",
    "ace_sanitized_20260917",
    "ace_attribution_20260912",
    "ace_economy_session_20260916",
    "ace_economy_refinement_20260916",
}


def inventory() -> tuple[list[tuple[Path, str]], list[dict[str, Any]]]:
    allowed = {
        n: stage for stage in ("train", "validation") for n in partition(stage)
    }
    rows: list[tuple[Path, str]] = []
    excluded: list[dict[str, Any]] = []
    for root in sorted((c.ROOT / "experiments/output").iterdir()):
        if not root.is_dir() or root.name == c.NAME:
            continue
        relevant = root.name.startswith(
            (
                "ace_",
                "acet_",
                "x_train",
                "x_validation",
                "coverage_cycle",
                "luna_",
            )
        )
        if not relevant or any(x in root.name.lower() for x in EXCLUDE):
            excluded.append(
                dict(
                    path=str(root.relative_to(c.ROOT)),
                    reason="outside study or protected/mixed root; no contents read",
                )
            )
            continue
        for directory, dirs, _ in os.walk(root):
            dirs[:] = sorted(
                d for d in dirs if not any(x in d.lower() for x in EXCLUDE)
            )
            folder = Path(directory)
            if folder.name != "configs":
                continue
            for label in dirs:
                matches = [
                    n
                    for n in allowed
                    if re.search(
                        r"(?:^|__|_)" + re.escape(n) + r"(?:__|$)", label
                    )
                ]
                if len(matches) == 1:
                    rows.append((folder / label, matches[0]))
                elif root.name in DEVELOPMENT_ONLY or root.name.startswith(
                    (
                        "ace_adaptation_x-",
                        "ace_adaptation_x3-",
                        "ace_adaptation_x4-",
                        "ace_adaptation_x5-",
                    )
                ):
                    rows.append((folder / label, "role-only"))
                else:
                    excluded.append(
                        dict(
                            path=str((folder / label).relative_to(c.ROOT)),
                            reason="cell name does not uniquely establish authorized theorem",
                        )
                    )
            dirs[:] = []
    return rows, excluded


def read_cache(path: Path) -> list[dict[str, Any]]:
    return (
        yaml.load(path.read_text(), Loader=yaml.CSafeLoader)
        if path.exists()
        else []
    )


def audit_cell(folder: Path, theorem: str) -> dict[str, Any]:
    result, cache = folder / "result.yaml", folder / "cache.yaml"
    signatures = {p.name: c.sha(p) for p in (result, cache) if p.exists()}
    signature = fingerprint((signatures, c.sha(Path(__file__))))
    dest = (
        AUDIT
        / "cells"
        / (fingerprint(str(folder.relative_to(c.ROOT))) + ".json")
    )
    if dest.exists():
        saved = json.loads(dest.read_text())
        if saved["analysis_signature"] == signature:
            return saved
    raw: dict[str, Any] = (
        yaml.load(result.read_text(), Loader=yaml.CSafeLoader)
        if result.exists()
        else {}
    )
    params = raw.get("args", {})
    value: dict[str, Any] = raw.get("outcome", {}).get("result") or {}
    records = read_cache(cache)
    total = uncached = 0.0
    inputs = cached = outputs = requests = 0
    models: set[str] = set()
    model_options: dict[str, Any] = {}
    checks: list[dict[str, Any]] = []
    tool_names: set[str] = set()
    exposed: Counter[str] = Counter()
    prompts: list[str] = []
    pricing_issues: list[str] = []
    for entry in records:
        request = entry["input"]["request"]
        options = request["options"]
        output: dict[str, Any] = entry.get("output") or {}
        if options.get("model") == "__compute__":
            call = yaml.load(
                request["chat"][-1]["content"], Loader=yaml.CSafeLoader
            )
            replies: list[dict[str, Any]] = output.get("outputs") or []
            if not replies:
                continue
            returned = yaml.load(
                replies[0]["content"], Loader=yaml.CSafeLoader
            )
            if not isinstance(returned, dict):
                continue
            returned = cast(dict[str, Any], returned)
            returned = returned.get("checked", returned)
            fb = returned.get("feedback", returned)
            if "failing_tactic" not in fb and "proof_so_far" not in fb:
                continue
            error, tactic = (
                fb.get("error_message") or "",
                fb.get("failing_tactic") or "",
            )
            checks.append(
                dict(
                    function=call.get("fun"),
                    submitted=call.get("args", {}).get("tactics"),
                    success=bool(fb.get("success")),
                    outcome=returned.get("outcome", "legacy"),
                    error=error,
                    tactic=tactic,
                    category=failure_category(error, tactic),
                    accepted_prefix=fb.get("proof_so_far", []),
                    goals=fb.get("remaining_goals", []),
                    auto_finished=fb.get("auto_finished"),
                )
            )
            continue
        model = output.get("model_name") or options.get("model")
        if not model:
            pricing_issues.append("missing model")
            continue
        model = str(model)
        models.add(model)
        model_options[fingerprint(options)] = options
        usage: dict[str, Any] = output.get("usage_info") or {}
        inp, out = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        hit = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
        if not usage and output.get("outputs"):
            pricing_issues.append("missing token receipt")
        try:
            total += price_tokens(model, inp, hit, out)
            uncached += price_tokens(model, inp, 0, out)
        except (ValueError, KeyError) as exc:
            pricing_issues.append(str(exc))
        inputs += inp
        cached += hit
        outputs += out
        requests += bool(output.get("outputs"))
        text = json.dumps(request["chat"], sort_keys=True)
        prompts.append(hashlib.sha256(text.encode()).hexdigest())
        for ident in set(re.findall(r"rocq-\d{5}", text)):
            exposed[ident] += 1
        request_tools: list[dict[str, Any]] = request.get("tools") or []
        for tool in request_tools:
            tool_names.add(
                str(
                    tool.get(
                        "name", tool.get("function", {}).get("name", "unknown")
                    )
                )
            )
    exceptions = [p for p in folder.glob("exception*.txt")]
    diagnostic = str(raw.get("diagnostics", "")) + str(
        raw.get("outcome", {}).get("diagnostics", "")
    )
    diagnostic += "\n".join(p.read_text() for p in exceptions)
    admin = any(
        x in diagnostic for x in ("CampaignExhausted", "CampaignPaused")
    )
    args = params.get("args", {})
    book = args.get("playbook", "")
    comparable = {
        k: v
        for k, v in args.items()
        if k not in ("playbook", "problem_file", "theorem_name", "claims")
    }
    comparable.update(
        strategy=params.get("strategy"),
        policy=params.get("policy"),
        policy_args=params.get("policy_args"),
        budget=params.get("budget"),
        models=sorted(models),
        options=list(model_options.values()),
        tools=sorted(tool_names),
    )
    # Strategy/policy differences remain explicit; no automatic assertion
    # that an ACE strategy is equivalent to the non-ACE strategy.
    seed_match = re.search(r"seed(\d+)$", folder.name)
    row = dict(
        path=str(folder.relative_to(c.ROOT)),
        campaign=folder.relative_to(c.ROOT / "experiments/output").parts[0],
        theorem=theorem,
        partition="role-only"
        if theorem == "role-only"
        else ("train" if theorem in partition("train") else "validation"),
        seed=seed_match.group(1) if seed_match else None,
        analysis_signature=signature,
        hashes=signatures,
        status="done" if value else "failed" if exceptions else "missing",
        solved=bool(value.get("success")),
        administrative_censoring=admin,
        cache_cost_current_tariff=total,
        cache_uncached_cost=uncached,
        pricing_issues=pricing_issues,
        requests=requests,
        tokens=dict(input=inputs, cached=cached, output=outputs),
        returned_values=value.get("values", []),
        spent=value.get("spent_budget", {}),
        book_sha256=fingerprint(book),
        book_bytes=len(str(book).encode()),
        comparator=comparable,
        comparator_sha256=fingerprint(comparable),
        prompt_hashes=prompts,
        bullet_prompt_exposure=dict(exposed),
        checks=checks,
        failure_category="solved"
        if value.get("success")
        else (
            "administrative_censoring"
            if admin
            else "platform_failure"
            if not value and exceptions
            else checks[-1]["category"]
            if checks
            else "no_verifier_evidence"
        ),
        diagnostic=diagnostic[:8000],
        retry_artifacts=len(exceptions),
        limitation="Cache costs omit unrecorded failed requests/retries; ledger receipts supersede them. "
        "Prompt presence is exposure, not causal use. Missing manifest means completeness unestablished.",
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(row, sort_keys=True, indent=2) + "\n")
    return row


def receipt_audit(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    campaigns = {r["campaign"] for r in rows}
    for campaign in sorted(campaigns):
        ledger = c.ROOT / "experiments/campaigns" / campaign / "ledger.sqlite3"
        if not ledger.exists():
            continue
        cells = {
            Path(r["path"]).name for r in rows if r["campaign"] == campaign
        }
        # WHERE filters names before rows cross the closed-data boundary.
        with sqlite3.connect(f"file:{ledger}?mode=ro", uri=True) as db:
            for cell in sorted(cells):
                fetched = db.execute(
                    "SELECT id,model,created,charged,status,usage FROM receipts WHERE cell=?",
                    (cell,),
                ).fetchall()
                for ident, model, created, charged, status, encoded in fetched:
                    usage = json.loads(encoded or "{}")
                    inp, out = (
                        usage.get("input_tokens", 0),
                        usage.get("output_tokens", 0),
                    )
                    hit = usage.get("input_tokens_details", {}).get(
                        "cached_tokens", 0
                    )
                    day = datetime.fromtimestamp(created, timezone.utc).date()
                    repriced = (
                        price_tokens(model, inp, hit, out, on=day)
                        if status == "settled"
                        else None
                    )
                    receipts.append(
                        dict(
                            campaign=campaign,
                            cell=cell,
                            receipt=ident,
                            model=model,
                            date=day.isoformat(),
                            charged=charged,
                            repriced=repriced,
                            status=status,
                            match=charged is not None
                            and repriced is not None
                            and abs(charged - repriced) < 1e-8,
                            classification="measured"
                            if repriced is not None
                            else "unknown_liability",
                            usage=usage,
                        )
                    )
    return receipts


def expected_panels(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Explicit manifests only from known development-only experiments."""
    by_folder: dict[Path, dict[str, dict[str, Any]]] = {}
    for row in rows:
        cell = c.ROOT / row["path"]
        by_folder.setdefault(cell.parent.parent, {})[cell.name] = row
    result: list[dict[str, Any]] = []
    for folder, cells in sorted(by_folder.items()):
        root = folder.relative_to(c.ROOT / "experiments/output").parts[0]
        safe = root in DEVELOPMENT_ONLY or root.startswith(
            (
                "ace_x_validation",
                "acet_x_validation",
                "x_validation",
                "x_train_agentic",
                "ace_bounded_",
                "ace_polish_",
                "ace_control_cycle_",
                "ace_adaptation_x-",
                "ace_adaptation_x3-",
                "ace_adaptation_x4-",
                "ace_adaptation_x5-",
            )
        )
        path = folder / "experiment.yaml"
        if not safe or not path.exists():
            result.append(
                dict(
                    path=str(folder.relative_to(c.ROOT)),
                    observed=len(cells),
                    expected=None,
                    complete=None,
                    reason="manifest absent or not allowlisted",
                )
            )
            continue
        manifest: dict[str, Any] = yaml.load(
            path.read_text(), Loader=yaml.CSafeLoader
        )
        configs: dict[str, Any] = manifest["configs"]
        missing = [
            n
            for n in configs
            if n not in cells or cells[n]["status"] == "missing"
        ]
        censored = [
            n for n, row in cells.items() if row["administrative_censoring"]
        ]
        result.append(
            dict(
                path=str(folder.relative_to(c.ROOT)),
                manifest_sha256=c.sha(path),
                expected=len(configs),
                observed=len(cells),
                missing=missing,
                administrative_censoring=censored,
                extra=sorted(cells.keys() - configs.keys()),
                complete=not missing and not censored,
                configs={n: item["params"] for n, item in configs.items()},
            )
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    cells, excluded = inventory()
    AUDIT.mkdir(parents=True, exist_ok=True)
    (AUDIT / "inventory.json").write_text(
        json.dumps(
            dict(
                included=[
                    dict(path=str(p.relative_to(c.ROOT)), theorem=t)
                    for p, t in cells
                ],
                excluded=excluded,
                mixed_reports_read=False,
                protected_data_read=False,
            ),
            indent=2,
        )
        + "\n"
    )
    rows: list[dict[str, Any]] = []
    selected = cells[: args.limit]
    if not 1 <= args.workers <= 12:
        raise ValueError("Use one to twelve audit workers")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i, row in enumerate(
            pool.map(
                audit_cell, (p for p, _ in selected), (t for _, t in selected)
            )
        ):
            rows.append(row)
            if i % 100 == 0:
                print(
                    json.dumps(dict(audited=i + 1, selected=len(cells))),
                    flush=True,
                )
    receipts = receipt_audit(rows)
    (AUDIT / "receipts.json").write_text(json.dumps(receipts, indent=2) + "\n")
    panels = expected_panels(rows)
    (AUDIT / "expected_panels.json").write_text(
        json.dumps(panels, indent=2, default=str) + "\n"
    )
    summary = dict(
        selected=len(cells),
        audited=len(rows),
        complete_inventory=len(rows) == len(cells),
        by_campaign=dict(Counter(r["campaign"] for r in rows)),
        failures=dict(
            Counter(r["failure_category"] for r in rows if not r["solved"])
        ),
        receipts=len(receipts),
        receipt_mismatches=sum(
            not r["match"] for r in receipts if r["status"] == "settled"
        ),
        unresolved_receipts=sum(r["status"] != "settled" for r in receipts),
        expected_panel_completeness="Separate explicit manifests required; directory census alone is insufficient",
    )
    (AUDIT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
