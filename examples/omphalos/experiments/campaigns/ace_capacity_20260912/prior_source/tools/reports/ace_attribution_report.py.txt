"""Development-only ACE attribution audit and complete-cell reports.

Offline only. Both harnesses invoke the campaign CLI or this module.
All input directories come from its explicit registered manifests.
"""

from experiments.ace import ace_attribution_experiment as c
from collections import Counter, defaultdict
from dataclasses import asdict, replace
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import re
from typing import Any, cast
from unittest.mock import patch

from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from runtime.campaign_budget import CampaignResponsesModel
from tools.analysis.cell_records import cells_of_run, CellRecord
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)
from tools.analysis.failure_analysis import refine_class
import numpy as np
import yaml


def args_of(directory: Path) -> dict[str, Any]:
    lines: list[str] = []
    with (directory / "result.yaml").open() as f:
        for line in f:
            if line.rstrip() == "outcome:":
                break
            lines.append(line)
    return yaml.load("".join(lines), Loader=yaml.CSafeLoader)["args"]


def preflight() -> None:
    """Replay every observed request, never the unobserved next request.

    The historical transport's reasoning reservation is updated only on live
    dispatch, not on cache hits. Capping replay at the recorded request count
    therefore verifies all recorded prompts/Compute calls without confusing a
    cache-only admission underestimate with changed strategy behavior. Active
    strategy arguments and the original dollar/verifier caps are checked
    separately. No HTTP dispatch is possible, including on a cache miss.
    """
    c.activate("luna")
    os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)
    records: dict[str, dict[str, CellRecord]] = {}
    rows: list[dict[str, Any]] = []
    before = c.accounting()
    for stage in c.STAGES:
        for ref in c.read("references.json")[stage]:
            source = ref["source"]
            if source not in records:
                records[source] = {
                    r.name: r for r in cells_of_run(c.ROOT / source)
                }
            original = records[source][ref["name"]]
            directory = c.ROOT / source / "configs" / ref["name"]
            archived = args_of(directory)
            cfg = c.proof(stage, "luna-ace", ref["theorem"])
            args = cfg.instantiate(None)
            # Unused claims do not enter a query with both admission paths
            # disabled. All other active inputs must be identical.
            expected_args = dict(archived["args"])
            expected_args["claims"] = []
            for key in (
                "polished",
                "resource_recovery",
                "matched_advice",
                "output_recovery",
            ):
                if expected_args.get(key) is False:
                    expected_args.pop(key)
            assert expected_args == args.args, (ref["name"], "strategy inputs")
            assert archived["strategy"] == args.strategy
            assert archived["policy"] == args.policy
            assert archived["policy_args"] == args.policy_args
            assert archived["budget"] == args.budget
            assert not original.platform_failed and original.requests > 0
            assert original.solved == ref["solved"]
            assert abs(original.cost - ref["cost"]) < 1e-7
            args.cache_file = f"configs/{ref['name']}/cache.yaml"
            args.cache_mode = "replay"
            args.export_raw_trace = False
            args.export_browsable_trace = False
            args.export_log = False
            args.budget = dict(args.budget or {}) | {
                "num_requests": original.requests
            }
            ctx = replace(c.context(), cache_root=c.ROOT / source)
            with patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError(
                    "Offline preflight cannot dispatch"
                ),
            ):
                with redirect_stdout(io.StringIO()):
                    outcome = run_command(
                        run_strategy, args, ctx=ctx, add_header=False
                    )
            result = cast(Any, outcome.result)
            assert result is not None, outcome
            spent = result.spent_budget
            assert result.success == original.solved, ref["name"]
            assert spent.get("num_completions", 0) == original.requests, (
                ref["name"],
                spent,
            )
            assert abs(spent.get("price", 0) - original.cost) < 1e-7
            rows.append(
                dict(
                    partition=stage,
                    theorem=ref["theorem"],
                    source=source,
                    name=ref["name"],
                    requests=original.requests,
                    cost=original.cost,
                    success=original.solved,
                    replay_passed=True,
                    active_args_match=True,
                    cache_sha256=c.digest(directory / "cache.yaml"),
                )
            )
            if len(rows) % 10 == 0:
                print(f"Replayed {len(rows)}/80 archived controls", flush=True)
    assert c.accounting()["requests"] == before["requests"] == 0
    assert len(rows) == 80
    c.save(
        "preflight.json",
        dict(
            passed=True,
            cells=rows,
            paid_requests=0,
            caveat="Replay capped at observed request count because live-only reasoning reservations are not restored on cache hits; all actual requests and active inputs match.",
        ),
    )


def metrics(
    obs: dict[tuple[str, str], Observation], cap: float
) -> dict[str, Any]:
    solved = sum(
        v.solved and not v.failed and v.cost <= cap + 1e-12
        for v in obs.values()
    )
    total = sum(v.cost for v in obs.values())
    return dict(
        cells=len(obs),
        raw_solves=sum(v.solved and not v.failed for v in obs.values()),
        qualified_solves=solved,
        cost=total,
        cost_per_solve=total / solved if solved else None,
        platform_failures=sum(v.failed for v in obs.values()),
        cap=cap,
    )


def directory_for(cfg: c.ProofConfig) -> Path:
    if cfg.arm.endswith("-book"):
        run = c.OUTPUT / "swaps"
    elif cfg.reasoning_effort != "medium":
        run = c.OUTPUT / "effort"
    else:
        run = (
            c.OUTPUT
            / cfg.partition
            / ("luna-none" if cfg.model_name == c.LUNA else "terra")
        )
    return run / "configs" / c.name(cfg, None)


def observations(
    configs: list[c.ProofConfig], acct: dict[str, Any]
) -> dict[tuple[str, str], Observation]:
    records: dict[Path, dict[str, CellRecord]] = {}
    out: dict[tuple[str, str], Observation] = {}
    for cfg in configs:
        directory = directory_for(cfg)
        run = directory.parent.parent
        if run not in records:
            records[run] = {r.name: r for r in cells_of_run(run)}
        n = c.name(cfg, None)
        if n not in records[run]:
            raise ValueError(f"Missing expected cell {n}")
        r = records[run][n]
        for p in directory.glob("exception*.txt"):
            if "CampaignExhausted" in p.read_text():
                raise ValueError("Administratively censored panel")
        cost = acct["costs"].get(n, 0.0)
        if abs(cost - r.cost) > 1e-7:
            raise ValueError(
                f"Cache and receipt disagree: {n}: {cost} vs {r.cost}"
            )
        out[r.cell] = Observation(r.solved, cost, r.platform_failed)
    if len(out) != len(configs):
        raise ValueError("Duplicate expected cell")
    return out


def interaction(
    obs: dict[str, dict[tuple[str, str], Observation]],
    families: dict[str, str],
) -> dict[str, Any]:
    expected = set(obs["luna-none"])
    assert all(set(v) == expected for v in obs.values())
    groups: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0])
    for cell in sorted(expected):

        def yes(arm: str) -> int:
            o = obs[arm][cell]
            return int(
                o.solved
                and not o.failed
                and o.cost <= (0.1 if arm.startswith("luna") else 1.0) + 1e-12
            )

        d = (yes("terra-ace") - yes("terra-none")) - (
            yes("luna-ace") - yes("luna-none")
        )
        groups[families[cell[0]]][0] += d
        groups[families[cell[0]]][1] += 1
    blocks = np.array(list(groups.values()))
    rng = np.random.default_rng(20260912)
    sampled = blocks[rng.integers(0, len(blocks), (10000, len(blocks)))].sum(
        axis=1
    )
    interval = cast(
        Any, np.quantile(sampled[:, 0] / sampled[:, 1], [0.05, 0.95])
    )
    from tools.analysis.paired_evaluation import exact_cluster_p

    return dict(
        effect=float(blocks[:, 0].sum() / len(expected)),
        ci90=interval.tolist(),
        p_descriptive=exact_cluster_p([int(v[0]) for v in blocks]),
        caveat="Descriptive family sign-flip and bootstrap, with historical Luna controls and different independently trained books.",
    )


def cache_diagnosis(directory: Path) -> dict[str, Any]:
    if not (directory / "cache.yaml").exists():
        return dict(cache_missing=True, checks=[], model_calls=[], classes={})
    entries: list[dict[str, Any]] = yaml.load(
        (directory / "cache.yaml").read_text(), Loader=yaml.CSafeLoader
    )
    checks: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    classes: Counter[str] = Counter()
    latest_request = 0
    for entry in entries:
        req = entry["input"]["request"]
        output: dict[str, Any] = entry.get("output") or {}
        answers: list[dict[str, Any]] = output.get("outputs") or []
        if req["options"].get("model") != "__compute__":
            latest_request += 1
            texts = [str(a.get("content", "")) for a in answers]
            tools = [
                str(t["name"])
                for a in answers
                for t in cast(list[dict[str, Any]], a.get("tool_calls") or [])
            ]
            calls.append(
                dict(
                    request=latest_request,
                    model=req["options"].get("model"),
                    options=req["options"],
                    response_text="\n".join(texts),
                    tools=tools,
                    finish_reasons=[a.get("finish_reason") for a in answers],
                    cited_ids=sorted(
                        set(re.findall(r"rocq-\d+", "\n".join(texts)))
                    ),
                    chat_chars=len(
                        json.dumps(req["chat"], ensure_ascii=False)
                    ),
                    usage=output.get("budget", {}).get("values", {}),
                )
            )
            continue
        payload = str(req["chat"][-1].get("content", ""))
        if (
            not payload.startswith(
                (
                    "fun: checked_proof",
                    "fun: checked_syntax",
                    "fun: check_assisted",
                )
            )
            or not answers
        ):
            continue
        raw: Any = yaml.load(
            str(answers[0].get("content", "")), Loader=yaml.CSafeLoader
        )
        if not isinstance(raw, dict):
            continue
        checked = cast(dict[str, Any], raw)
        raw_fb: Any = checked.get("feedback", checked)
        if not isinstance(raw_fb, dict) or "success" not in raw_fb:
            continue
        fb = cast(dict[str, Any], raw_fb)
        kind = (
            refine_class(fb.get("error_message"))
            if not fb.get("success")
            else "accepted"
        )
        if not fb.get("success") and not fb.get("error_message"):
            kind = "incomplete-proof"
        if not fb.get("success"):
            classes[kind] += 1
        checks.append(
            dict(
                after_request=latest_request,
                category=kind,
                outcome=checked.get("outcome"),
                elapsed=checked.get("elapsed"),
                error=fb.get("error_message"),
                tactic=fb.get("failing_tactic"),
                verified_prefix=fb.get("proof_so_far"),
                remaining_goals=fb.get("remaining_goals"),
                success=fb.get("success"),
            )
        )
    errors = [v for v in checks if not v["success"]]
    exceptions = {
        p.name: p.read_text() for p in directory.glob("exception*.txt")
    }
    return dict(
        checks=checks,
        model_calls=calls,
        classes=dict(classes),
        first_error=errors[0] if errors else None,
        last_check=checks[-1] if checks else None,
        exceptions=exceptions,
        no_proof_submission=not checks,
        repeated_failing_tactics=dict(
            Counter(v["tactic"] for v in errors if v["tactic"])
        ),
        caution="Cache order and taxonomy labels are diagnostics; verifier error labels do not establish infrastructure failure.",
    )


def report(phase: str = "complete") -> None:
    c.verify()
    acct = c.accounting()
    if acct["unresolved"]:
        raise ValueError("Unresolved liability")
    arms = c.ARMS if phase == "complete" else c.ARMS[:2]
    all_diagnostics: dict[str, Any] = {}
    payload: dict[str, Any] = dict(
        phase=phase,
        partitions={},
        new_api_cost=acct["total"],
        limitations=[
            "validationX is repeatedly used development data",
            "Luna controls are historical",
            "trainX is in-sample for each adapted book",
            "seed identifiers distinguish replicates, not provider seeds",
        ],
        default_changed=False,
    )
    families = c.read("protocol.json")["families"]
    for stage in c.STAGES:
        refs = c.read("references.json")[stage]
        obs = {
            "luna-ace": {
                (r["theorem"], "0"): Observation(
                    r["solved"], r["cost"], r["failed"]
                )
                for r in refs
            }
        }
        for arm in arms:
            if arm == "luna-ace":
                continue
            obs[arm] = observations(
                [c.proof(stage, arm, n) for n in c.partition(stage)], acct
            )
        expected = [(n, "0") for n in c.partition(stage)]
        contrasts: dict[str, Any] = {}
        for model in ("luna", "terra") if phase == "complete" else ("luna",):
            cap = 0.1 if model == "luna" else 1.0
            a, b = obs[model + "-none"], obs[model + "-ace"]
            comparison = compare(
                a, b, expected, families=families, cap_a=cap, cap_b=cap
            )
            comparison.pop("verdict", None)
            comparison["cost_p_descriptive"] = cost_cluster_p(
                a, b, expected, families=families
            )
            comparison["gained"] = [
                n for n, s in expected if b[n, s].solved and not a[n, s].solved
            ]
            comparison["lost"] = [
                n for n, s in expected if a[n, s].solved and not b[n, s].solved
            ]
            contrasts[model] = comparison
        block = dict(
            metrics={
                a: metrics(o, 0.1 if a.startswith("luna") else 1.0)
                for a, o in obs.items()
            },
            comparisons=contrasts,
            observations={
                a: {n: asdict(v) for (n, _), v in o.items()}
                for a, o in obs.items()
            },
            curves={
                a: {
                    str(cap): sum(
                        v.solved and not v.failed and v.cost <= cap
                        for v in o.values()
                    )
                    for cap in (
                        0.025,
                        0.05,
                        0.075,
                        0.1,
                        0.2,
                        0.3,
                        0.5,
                        0.75,
                        1.0,
                    )
                }
                for a, o in obs.items()
            },
            curve_interpretation="Retrospective final actual-cost qualification, not smaller-cap policy runs",
            normalized_costs={
                a: sum(v.cost for v in o.values())
                / (1 if a.startswith("luna") else 10)
                for a, o in obs.items()
            },
        )
        if phase == "complete":
            block["interaction"] = interaction(obs, families)
        payload["partitions"][stage] = block
        for arm in arms:
            for theorem in c.partition(stage):
                if arm == "luna-ace":
                    ref = next(r for r in refs if r["theorem"] == theorem)
                    directory = (
                        c.ROOT / ref["source"] / "configs" / ref["name"]
                    )
                else:
                    directory = directory_for(c.proof(stage, arm, theorem))
                key = f"{stage}/{arm}/{theorem}"
                all_diagnostics[key] = dict(
                    source=str(directory.relative_to(c.ROOT)),
                    observation=asdict(obs[arm][theorem, "0"]),
                    **cache_diagnosis(directory),
                )
    if phase == "complete":
        payload["swaps"] = {}
        for model, arm, own in (
            ("luna", "luna-terra-book", "luna-ace"),
            ("terra", "terra-luna-book", "terra-ace"),
        ):
            swapped = observations(
                [c.proof("validation", arm, n) for n in c.panel("validation")],
                acct,
            )
            main = payload["partitions"]["validation"]["observations"][own]
            original = {
                (n, "0"): Observation(**main[n]) for n in c.panel("validation")
            }
            cap = 0.1 if model == "luna" else 1.0
            comp = compare(
                original,
                swapped,
                list(original),
                families=families,
                cap_a=cap,
                cap_b=cap,
            )
            comp.pop("verdict", None)
            payload["swaps"][model] = dict(
                own=metrics(original, cap),
                swapped=metrics(swapped, cap),
                comparison=comp,
            )
            for n in c.panel("validation"):
                all_diagnostics[f"swaps/{arm}/{n}"] = cache_diagnosis(
                    directory_for(c.proof("validation", arm, n))
                )
        payload["effort"] = {}
        for effort in ("low", "medium", "high"):
            o = observations(
                [
                    c.proof("training", "terra-none", n, effort)
                    for n in c.panel("training")
                ],
                acct,
            )
            payload["effort"][effort] = metrics(o, 1.0)
            if effort != "medium":
                for n in c.panel("training"):
                    all_diagnostics[f"effort/{effort}/{n}"] = cache_diagnosis(
                        directory_for(
                            c.proof("training", "terra-none", n, effort)
                        )
                    )
        preparation = sum(
            v
            for k, v in acct["costs"].items()
            if k.startswith("step") or k == "embeddings"
        )
        payload["terra_preparation"] = dict(
            cost=preparation,
            amortized_per_problem={
                str(n): preparation / n for n in (100, 1000)
            },
        )
    c.save(f"{phase}_report.json", payload)
    c.save(f"{phase}_diagnostics.json", all_diagnostics)
    c.export_receipts()
    print(
        json.dumps(
            {s: b["metrics"] for s, b in payload["partitions"].items()},
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    import sys

    report(sys.argv[1] if len(sys.argv) > 1 else "complete")
