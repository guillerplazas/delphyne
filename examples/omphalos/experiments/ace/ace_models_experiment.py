"""Approved $30 ACE model suite, preregistered before paid execution.

Source/screen/selection are disjoint trainX panels of 8/8/24 problems,
50% competition, family-preserving randomization seed 20260910. Stage 1:
Luna low/medium/high/xhigh, 16 problems. Stage 2: 23 offline playbooks,
one role at a time, eight screening problems; Terra low through xhigh
only in offline roles. Curator includes reducer, auditor defaults off.
Stage 3: up to four role interactions and two runner-up-prover checks,
then at most two challengers plus flagship on the remaining 24 problems.

Only Luna xhigh gaining >=2 qualified solves over high, with total cost
<=1.20 and no worse cost/solve, opens max on that same panel, once per
role. Selection requires >=2/24 gained solves with those cost constraints.
Freeze one winner, then fresh trainX and validationX: 40 problems, seeds
0/1, two arms (320 cells). Practical gate: gain >=4/80 and both cost gates
on EACH partition. Primary inferential readout is the single frozen
validation comparison, two-sided family-cluster p<.10, descriptive 90% CI.
Training and repeatedly selected validation are development evidence.
No protected challenge, testX, additional seeds or post-freeze adaptation.

All requests, parse retries and embeddings enter the shared ledger.
At most four explicitly registered infrastructure retries; no automatic
logical-failure reruns. Unknown charges and missing/censored panels block
verdicts. Closed-stage slack may move forward, never away from benchmark.
The $30 ceiling is not a target; API costs exclude assistant/engineering.
Both harnesses: python -m experiments.ace.ace_models_experiment prepare
               python -m experiments.ace.ace_models_experiment campaign
               python -m experiments.ace.ace_models_experiment status
Underlying batches end in OmphalosExperiment.run_cli().
"""

from dataclasses import asdict, replace
import csv
import fcntl
import itertools
import json
import random
import sys
from typing import Any, cast

import delphyne as dp
from delphyne.utils.typing import pydantic_load

from experiments.common import ace_model_campaign as cm
import experiments.common.omphalos_launch as ol
from experiments.ace.ace_models_roles import build
from runtime.model_registry import OmphalosReasoningEffort
from tools.analysis.paired_evaluation import compare, cost_cluster_p


def candidate(
    book: str,
    effort: OmphalosReasoningEffort,
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return dict(playbook=book, effort=effort, artifact=artifact)


def key(c: dict[str, Any]) -> str:
    from ace.ace_playbook import Playbook

    return cm.fingerprint(
        [Playbook.load(cm.ROOT / c["playbook"]).sha256(), c["effort"]]
    )[:20]


def prep_cost(c: dict[str, Any]) -> float:
    if c["artifact"] is None:
        return 0.0
    costs = cm.accounting()["costs"]
    return sum(costs.get(n, 0) for n in c["artifact"]["role_cells"])


def rank(c: dict[str, Any]) -> tuple[float, float, float, bool, int, str]:
    m = c["metrics"]
    return (
        -m["solves"],
        m["cost"],
        prep_cost(c),
        c["artifact"] is not None or c["effort"] != "medium",
        (*cm.EFFORTS, "max").index(c["effort"]),
        key(c),
    )


def evaluate(
    c: dict[str, Any], panel: list[str], stage: str, *, phase: str = "prover"
) -> dict[str, Any]:
    configs = [
        cm.proof_config(b, c["effort"], c["playbook"], phase) for b in panel
    ]
    if any(
        not (
            cm.OUTPUT
            / "proof/configs"
            / cm.proof_name(x, None)
            / "result.yaml"
        ).exists()
        for x in configs
    ):
        cm.launch(configs, stage)
    obs = cm.observations(configs)
    return dict(
        c, metrics=cm.metrics(obs), configs=[asdict(x) for x in configs]
    )


def close_stage(stage: str, target: str | None = None) -> None:
    acct = cm.accounting()
    if acct["unresolved"]:
        raise ValueError("cannot close a stage with unresolved charges")
    cm.save(f"closed/{stage}.json", dict(stage=stage))
    if target is None:
        return
    if stage == "benchmark":
        raise ValueError("benchmark allocation is protected")
    ledger = cm.Ledger(cm.CAMPAIGN / "ledger.sqlite3")
    summary = ledger.summary()
    spent = sum(g["dollars"] for g in summary["groups"] if g["stage"] == stage)
    spare = summary["allocations"][stage] - spent
    # Keep an epsilon so allocation values stay positive on resume.
    if spare > 0.01:
        ledger.transfer(
            stage,
            target,
            spare - 0.001,
            f"Completed {stage}; fund only registered {target} cells",
        )


def prover() -> list[dict[str, Any]]:
    reg = cm.read("registration.json")
    panel = reg["panels"]["source"] + reg["panels"]["screen"]
    configs = [
        cm.proof_config(b, e, reg["incumbent"], "prover")
        for b in panel
        for e in cm.EFFORTS
    ]
    random.Random(20260910).shuffle(configs)
    cm.launch(configs, "prover")
    results = [
        evaluate(candidate(reg["incumbent"], e), panel, "prover")
        for e in cm.EFFORTS
    ]
    high, xhigh = results[2:4]
    upper = cm.eligible(xhigh["metrics"], high["metrics"], gain=2)
    cm.save(
        "prover_upper_gate.json",
        dict(open_max=upper, high=high["metrics"], xhigh=xhigh["metrics"]),
    )
    if upper:
        results.append(
            evaluate(candidate(reg["incumbent"], "max"), panel, "upper")
        )
    control = results[1]
    allowed = sorted(
        [c for c in results if cm.eligible(c["metrics"], control["metrics"])],
        key=rank,
    )
    if not allowed:
        allowed = [control]
    selected = allowed[:2]
    cm.save("prover_report.json", dict(results=results, selected=selected))
    close_stage("prover", "adaptation")
    return selected


def role_screen(
    effort: OmphalosReasoningEffort,
) -> tuple[list[dict[str, Any]], cm.Recipe]:
    panel = cm.read("registration.json")["panels"]["screen"]
    base_recipe = cm.Recipe()
    base_artifact = build(base_recipe)
    prepared: dict[tuple[str, str, str], dict[str, Any]] = {}
    for role in cm.ROLES:
        for model, e in itertools.product((cm.LUNA, cm.TERRA), cm.EFFORTS):
            recipe = replace(base_recipe, **{role: cm.RoleModel(model, e)})
            prepared[role, model, e] = build(recipe)
    # All standard role arms are independent once their books are frozen.
    # Group their exact existing configurations in one launcher batch;
    # completed cells remain cached and count at their measured cost.
    configs: dict[str, cm.ModelProofConfig] = {}
    for artifact in [base_artifact, *prepared.values()]:
        for bench in panel:
            c = cm.proof_config(bench, effort, artifact["playbook"], "prover")
            configs[cm.proof_name(c, None)] = c
    batch = list(configs.values())
    random.Random(20260910).shuffle(batch)
    cm.launch(batch, "screening")
    base = evaluate(
        candidate(base_artifact["playbook"], effort, base_artifact),
        panel,
        "screening",
    )
    all_results = [base]
    chosen: dict[str, cm.RoleModel | None] = {}
    for role in cm.ROLES:
        results: list[dict[str, Any]] = [base]
        luna: dict[str, dict[str, Any]] = {}
        for model, e in itertools.product((cm.LUNA, cm.TERRA), cm.EFFORTS):
            artifact = prepared[role, model, e]
            c = evaluate(
                candidate(artifact["playbook"], effort, artifact),
                panel,
                "screening",
            )
            results.append(c)
            if model == cm.LUNA:
                luna[e] = c
        gate = cm.eligible(
            luna["xhigh"]["metrics"], luna["high"]["metrics"], gain=2
        )
        cm.save(
            f"{role}_upper_gate.json",
            dict(
                open_max=gate,
                high=luna["high"]["metrics"],
                xhigh=luna["xhigh"]["metrics"],
            ),
        )
        if gate:
            artifact = build(
                replace(base_recipe, **{role: cm.RoleModel(cm.LUNA, "max")}),
                stage="upper",
            )
            results.append(
                evaluate(
                    candidate(artifact["playbook"], effort, artifact),
                    panel,
                    "upper",
                )
            )
        allowed = [
            c for c in results if cm.eligible(c["metrics"], base["metrics"])
        ]
        winner = min(allowed, key=rank) if allowed else base
        selected_recipe = pydantic_load(
            cm.Recipe, winner["artifact"]["recipe"]
        )
        chosen[role] = getattr(selected_recipe, role)
        cm.save(f"{role}_report.json", dict(results=results, winner=winner))
        all_results.extend(results)
    unique = {key(c): c for c in sorted(all_results, key=rank, reverse=True)}
    recipe = cm.Recipe(
        cast(cm.RoleModel, chosen["reflector"]),
        cast(cm.RoleModel, chosen["curator"]),
        chosen["auditor"],
    )
    cm.save(
        "role_screen_report.json",
        dict(results=list(unique.values()), recipe=asdict(recipe)),
    )
    return list(unique.values()), recipe


def interactions(
    provers: list[dict[str, Any]],
    screened: list[dict[str, Any]],
    selected: cm.Recipe,
) -> list[dict[str, Any]]:
    reg = cm.read("registration.json")
    panel = reg["panels"]["screen"]
    effort = provers[0]["effort"]
    baseline = cm.Recipe()
    results = list(screened)
    built: set[str] = set()
    for toggles in itertools.product((False, True), repeat=3):
        recipe = cm.Recipe(
            **{
                r: getattr(selected if on else baseline, r)
                for r, on in zip(cm.ROLES, toggles)
            }
        )
        if recipe.key() in built:
            continue
        built.add(recipe.key())
        artifact = build(recipe)
        c = candidate(artifact["playbook"], effort, artifact)
        if not any(key(x) == key(c) for x in results):
            results.append(evaluate(c, panel, "selection"))
    # Include unchanged playbook with each retained prover setting.
    for prover_setting in provers:
        results.append(
            evaluate(
                candidate(reg["incumbent"], prover_setting["effort"]),
                panel,
                "selection",
            )
        )
    control = evaluate(
        candidate(reg["incumbent"], "medium"), panel, "selection"
    )
    if len(provers) > 1:
        unique = {key(c): c for c in sorted(results, key=rank, reverse=True)}
        for c in sorted(unique.values(), key=rank)[:2]:
            crossed = candidate(
                c["playbook"], provers[1]["effort"], c["artifact"]
            )
            if not any(key(x) == key(crossed) for x in results):
                results.append(evaluate(crossed, panel, "selection"))
    unique = {key(c): c for c in sorted(results, key=rank, reverse=True)}
    finalists = sorted(
        [
            c
            for c in unique.values()
            if key(c) != key(control)
            and cm.eligible(c["metrics"], control["metrics"])
        ],
        key=rank,
    )[:2]
    cm.save(
        "interaction_report.json",
        dict(
            results=list(unique.values()), control=control, finalists=finalists
        ),
    )
    close_stage("adaptation", "selection")
    close_stage("screening", "selection")
    return finalists


def select(finalists: list[dict[str, Any]]) -> dict[str, Any] | None:
    reg = cm.read("registration.json")
    if not finalists:
        cm.save(
            "selection_report.json",
            dict(
                winner=None,
                reason="No eligible distinct challenger on screening panel",
            ),
        )
        return None
    panel = reg["panels"]["selection"]
    control_candidate = candidate(reg["incumbent"], "medium")
    all_candidates = [control_candidate, *finalists]
    configs = [
        cm.proof_config(b, c["effort"], c["playbook"], "selection")
        for b in panel
        for c in all_candidates
    ]
    random.Random(20260911).shuffle(configs)
    cm.launch(configs, "selection")
    control = evaluate(
        control_candidate, panel, "selection", phase="selection"
    )
    results = [
        evaluate(c, panel, "selection", phase="selection") for c in finalists
    ]
    eligible = [
        c
        for c in results
        if cm.eligible(c["metrics"], control["metrics"], gain=2)
    ]
    winner = min(eligible, key=rank) if eligible else None
    cm.save(
        "selection_report.json",
        dict(control=control, results=results, winner=winner),
    )
    if winner is not None:
        cm.save(
            "frozen.json",
            dict(
                winner=winner,
                execution_hashes=cm.source_hashes(),
                playbook_file_sha256=cm.digest(cm.ROOT / winner["playbook"]),
                registration_sha256=cm.digest(
                    cm.CAMPAIGN / "registration.json"
                ),
            ),
        )
    close_stage("selection", "benchmark")
    return winner


def benchmark(winner: dict[str, Any]) -> dict[str, Any]:
    reg = cm.read("registration.json")
    frozen = cm.read("frozen.json")
    cm.verify_hashes(
        frozen["execution_hashes"]
        | {winner["playbook"]: frozen["playbook_file_sha256"]}
    )
    configs: list[cm.ModelProofConfig] = []
    for phase, panel in (
        ("training", reg["train"]),
        ("validation", reg["validation"]),
    ):
        for b in panel:
            for seed in (0, 1):
                arms = [
                    ("reference", reg["incumbent"], "medium"),
                    ("candidate", winner["playbook"], winner["effort"]),
                ]
                random.Random(f"20260910:{phase}:{b}:{seed}").shuffle(arms)
                for label, book, effort in arms:
                    configs.append(
                        cm.proof_config(
                            b,
                            cast(OmphalosReasoningEffort, effort),
                            book,
                            phase,
                            seed=seed,
                            label=label,
                        )
                    )
    cm.save("benchmark_manifest.json", [asdict(c) for c in configs])
    cm.launch(configs, "benchmark")
    reports: dict[str, Any] = {}
    for phase in ("training", "validation"):
        arms = [
            [c for c in configs if c.phase == phase and c.arm_label == label]
            for label in ("reference", "candidate")
        ]
        a, b = [cm.observations(cs) for cs in arms]
        result = compare(a, b, list(a), families=reg["families"])
        result["cost_p_two_sided"] = cost_cluster_p(
            a, b, list(a), families=reg["families"]
        )
        result["practical_gate"] = cm.eligible(
            cm.metrics(b), cm.metrics(a), gain=4
        )
        result["metrics"] = dict(
            reference=cm.metrics(a), candidate=cm.metrics(b)
        )
        result["per_seed"] = {
            str(s): dict(
                reference=cm.metrics(
                    {k: v for k, v in a.items() if k[1] == str(s)}
                ),
                candidate=cm.metrics(
                    {k: v for k, v in b.items() if k[1] == str(s)}
                ),
            )
            for s in (0, 1)
        }
        result["unique_qualified_theorems"] = {
            label: len(
                {
                    k[0]
                    for k, o in obs.items()
                    if o.solved and not o.failed and o.cost <= 0.10
                }
            )
            for label, obs in (("reference", a), ("candidate", b))
        }
        reports[phase] = result
    reports["practical_gate"] = all(
        reports[p]["practical_gate"] for p in ("training", "validation")
    )
    reports["statistical_support"] = (
        reports["validation"]["p_two_sided"] < 0.10
        and reports["validation"]["effect"] > 0
    )
    reports["winner"] = winner
    reports["verdict"] = (
        "improvement"
        if reports["practical_gate"] and reports["statistical_support"]
        else "retain_incumbent"
    )
    training_cost = prep_cost(winner)
    source_configs = [
        cm.proof_config(b, "medium", reg["incumbent"], "prover")
        for b in reg["panels"]["source"]
    ]
    training_cost += cm.metrics(cm.observations(source_configs))["cost"]
    mu = reports["validation"]["metrics"]["candidate"]["cost"] / 80
    reports["preparation_cost"] = training_cost
    reports["amortized_candidate_cost_per_problem"] = {
        str(n): mu + training_cost / n for n in (100, 1000)
    }
    close_stage("benchmark")
    return reports


def finish(report: dict[str, Any]) -> None:
    report["accounting"] = cm.accounting()
    report["exposure"] = (
        "Development benchmark; no independent generalization claim"
    )
    cm.save("final_report.json", report)
    ledger = cm.Ledger(cm.CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db, (cm.CAMPAIGN / "receipts.csv").open("w") as f:
        cursor = db.execute("SELECT * FROM receipts ORDER BY created,id")
        writer = csv.writer(f)
        writer.writerow([d[0] for d in cursor.description])
        writer.writerows(cursor.fetchall())
    print(json.dumps(report, indent=2), flush=True)


def campaign() -> None:
    cm.prepare()
    with (cm.CAMPAIGN / "campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (cm.CAMPAIGN / "final_report.json").exists():
            print("Campaign already complete; no new calls authorized.")
            return
        provers = prover()
        screened, recipe = role_screen(provers[0]["effort"])
        finalists = interactions(provers, screened, recipe)
        winner = select(finalists)
        if winner is None:
            finish(
                dict(
                    verdict="retain_incumbent",
                    reason="No challenger passed the preregistered selection gate",
                    benchmark_cells=0,
                    selection=cm.read("selection_report.json"),
                )
            )
        else:
            finish(benchmark(winner))


def main() -> None:
    batch = next(
        (a.split("=", 1)[1] for a in sys.argv if a.startswith("--batch=")),
        None,
    )
    if batch is None:
        command = sys.argv[1] if len(sys.argv) > 1 else "status"
        if command == "prepare":
            cm.prepare()
        elif command == "campaign":
            campaign()
        elif command == "status":
            print(json.dumps(cm.accounting(), indent=2))
        else:
            raise ValueError(
                "expected prepare, campaign, status or --batch=..."
            )
        return
    retry_id = next(
        (
            a.split("=", 1)[1]
            for a in sys.argv
            if a.startswith("--retry-manifest=")
        ),
        None,
    )
    sys.argv[:] = [
        a
        for a in sys.argv
        if not a.startswith(("--batch=", "--retry-manifest="))
    ]
    if any("retry" in a for a in sys.argv):
        raise ValueError(
            "broad retries forbidden; use an explicit retry manifest"
        )
    payload = cm.read(f"batches/{batch}.json")
    if payload.get("batch_protocol") != 2:
        raise ValueError(
            "pre-amendment batch: restart campaign at a completed batch boundary"
        )
    if cm.fingerprint(payload)[:24] != batch:
        raise ValueError("batch manifest changed")
    retry: dict[str, Any] | None = None
    if retry_id is not None:
        retry = cast(dict[str, Any], cm.read(f"retries/{retry_id}.json"))
        if retry["batch"] != batch:
            raise ValueError("retry manifest belongs to another batch")
        if (
            sum(
                len(json.loads(p.read_text())["names"])
                for p in (cm.CAMPAIGN / "retries").glob("*.json")
            )
            > 4
        ):
            raise ValueError("too many infrastructure retries")
    cm.activate("retry" if retry is not None else payload["stage"])
    configs = cm.load_configs(payload)
    if payload["kind"] == "proof":
        experiment: ol.OmphalosExperiment[Any] = ol.OmphalosExperiment(
            config_class=cm.ModelProofConfig,
            context=dp.workspace_execution_context(__file__),
            configs=configs,
            output_dir=str((cm.OUTPUT / "proof").relative_to(cm.ROOT)),
            config_naming=cm.proof_name,
            wait_for_slots=True,
            attempts=1,
        )
    else:
        experiment = ol.OmphalosExperiment(
            config_class=cm.ModelRoleConfig,
            context=dp.workspace_execution_context(__file__),
            configs=configs,
            output_dir=str((cm.OUTPUT / "role").relative_to(cm.ROOT)),
            config_naming=cm.role_name,
            wait_for_slots=True,
            attempts=1,
            needs_rocq=any(
                c["role"] == "grounder" for c in payload["configs"]
            ),
        )
    if retry is not None:
        experiment.load()
        experiment.retry_failed(names=set(retry["names"]))
    experiment.run_cli()


if __name__ == "__main__":
    main()
