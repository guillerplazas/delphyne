"""Registered learning batches and exact trainX evidence preparation."""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any

import delphyne as dp
from pydantic import TypeAdapter

from ace.ace_playbook import Playbook, Bullet, AddOp, BulletTag, merge
from experiments.ace_sanitized.scope import partition
from experiments.common import omphalos_launch as ol
from runtime import pytanque_utils as pt

from . import campaign as c
from .audit import cell, load_yaml
from .common import CAMPAIGN, OUTPUT, ROOT, read, save, sha, digest


@dataclass(frozen=True)
class RoleJob:
    cell: str
    role: str
    input_file: str
    input_sha: str
    model: str
    effort: str

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        path = CAMPAIGN / self.input_file
        if sha(path) != self.input_sha:
            raise ValueError("Role input changed")
        data = read(path)
        os.environ.update(
            OMPHALOS_CAMPAIGN_CELL=self.cell,
            OMPHALOS_CAMPAIGN_STAGE="learning",
        )
        return dp.RunStrategyArgs(
            strategy="audit_" + self.role,
            args=data,
            policy="audit_role_policy",
            policy_args=dict(
                cell=self.cell, model_name=self.model, effort=self.effort
            ),
            budget=dict(num_requests=2),
        )


def role_name(job: RoleJob, _: object) -> str:
    return job.cell


def register_roles(batch: str, jobs: list[RoleJob]) -> None:
    save(
        CAMPAIGN / "role_batches" / f"{batch}.json", [asdict(j) for j in jobs]
    )


def run_roles(batch: str) -> None:
    c.activate()
    jobs = [
        RoleJob(**j) for j in read(CAMPAIGN / "role_batches" / f"{batch}.json")
    ]
    sources = [
        Path(__file__).with_name("learning.py"),
        *Path(__file__).with_name("templates").glob("Audit*.jinja"),
    ]
    if any(j.role.endswith("_v3") for j in jobs):
        from .completion import install

        install()
        sources.extend(
            Path(__file__).with_name(f)
            for f in (
                "learning_v3.py",
                "solver.py",
                "transport.py",
                "accounting.py",
                "completion.py",
            )
        )
        sources.extend(
            [ROOT / "runtime/model_registry.py", ROOT / "ace/ace_playbook.py"]
        )
    save(
        CAMPAIGN / "role_sources" / f"{batch}.json",
        {str(p.relative_to(ROOT)): sha(p) for p in sources},
    )
    ol.OmphalosExperiment(
        config_class=RoleJob,
        configs=jobs,
        context=c.context(),
        output_dir=str((OUTPUT / batch).relative_to(ROOT)),
        config_naming=role_name,
        attempts=1,
        wait_for_slots=True,
        needs_rocq=False,
    ).run_cli()


def launch(batch: str, *, roles: bool = False, workers: int = 16) -> None:
    command = [
        sys.executable,
        "-m",
        "experiments.ace_independent_audit",
        "run-roles" if roles else "run-batch",
        batch,
        "run",
        f"--max_workers={workers}",
        "--wait",
    ]
    log = CAMPAIGN / "logs" / (batch + ".log")
    log.parent.mkdir(exist_ok=True)
    with log.open("a") as stream:
        subprocess.run(
            command,
            cwd=ROOT,
            stdout=stream,
            stderr=subprocess.STDOUT,
            check=True,
        )


def result(batch: str, name: str) -> dict[str, Any]:
    from .completion import require_closed

    require_closed(batch)
    path = OUTPUT / batch / "configs" / name / "result.yaml"
    if not path.exists():
        raise ValueError(f"Missing required result: {batch}/{name}")
    raw = load_yaml(path)
    if raw.get("outcome", {}).get("diagnostics"):
        raise ValueError(f"Platform diagnostics in {batch}/{name}")
    return raw["outcome"]["result"]


def evidence_for(
    batch: str, job: c.Job, *, version: int = 1
) -> dict[str, Any]:
    if job.stage != "train":
        raise ValueError("Learning accepts trainX only")
    directory = OUTPUT / batch / "configs" / c.name(job, None)
    r = cell((str(directory), job.theorem))
    spec = asdict(pt.parse_problem(partition("train")[job.theorem], True))
    if version == 1:
        spec.pop("informal_proof", None)
    trace: list[dict[str, Any]] = []
    baseline = ""
    rows: list[dict[str, Any]] = load_yaml(directory / "cache.yaml")
    for i, row in enumerate(rows):
        req = row["input"]["request"]
        out: dict[str, Any] = row.get("output") or {}
        if req["options"].get("model") == "__compute__":
            continue
        if not baseline:
            baseline = req["chat"][0]["content"]
        trace.append(
            dict(
                index=i,
                replies=out.get("outputs"),
                usage=out.get("usage_info"),
            )
        )
    evidence: dict[str, Any] = dict(
        theorem=job.theorem,
        problem=partition("train")[job.theorem],
        spec=spec,
        baseline_instructions=baseline,
        source=str(directory.relative_to(ROOT)),
        result_sha=r["result_sha"],
        cache_sha=r["cache_sha"],
        solved=r["solved"],
        returned=r["value"],
        counts=r["counts"],
        costs=r["costs"],
        checks=r["checks"],
        trajectory=trace,
    )
    if version >= 2:
        requests = [
            row
            for row in rows
            if row["input"]["request"]["options"].get("model") != "__compute__"
        ]
        evidence["visible_conversation"] = (
            requests[-1]["input"]["request"]["chat"][1:] if requests else []
        )
        evidence["evidence_version"] = version
        evidence["conversation_note"] = (
            "System instructions appear once in baseline_instructions. "
            "The final request retains visible fewshots, problem sketch, "
            "solver messages and tool replies. Final reply and checker "
            "appear in trajectory/checks. Hidden reasoning is not exposed."
        )
    return evidence


def prepare_evidence() -> None:
    jobs = [c.Job(**v) for v in read(CAMPAIGN / "batches/source.json")]
    for j in jobs:
        value = evidence_for("source", j, version=2)
        save(CAMPAIGN / "evidence" / f"{j.arm}_v2__{j.theorem}.json", value)
    print(dict(source_evidence=len(jobs)))


def author_configs() -> list[tuple[str, str, str]]:
    return [
        (f"{short}_{effort}", model, effort)
        for short, model in (
            ("luna", "gpt-5.6-luna"),
            ("terra", "gpt-5.6-terra"),
            ("sol", "gpt-5.6-sol"),
            ("astra", "gpt-6-astra"),
        )
        for effort in ("medium", "high")
    ]


def panel(n: int, seed: int = 20260919) -> list[str]:
    names = list(partition("train"))
    mathd = [t for t in names if t.startswith("mathd_")]
    other = [t for t in names if not t.startswith("mathd_")]
    random.Random(seed).shuffle(mathd)
    random.Random(seed + 1).shuffle(other)
    return [
        t
        for pair in zip(mathd[: n // 2], other[: n // 2], strict=True)
        for t in pair
    ]


def book(raw: dict[str, Any]) -> Playbook:
    return Playbook(
        next_id=raw["next_id"], bullets=[Bullet(**b) for b in raw["bullets"]]
    )


def save_book(path: Path, pb: Playbook, provenance: dict[str, Any]) -> None:
    save(
        path, dict(text=pb.render_prompt(), playbook=asdict(pb), **provenance)
    )


def role_job(
    cell_name: str, role: str, data: dict[str, Any], model: str, effort: str
) -> RoleJob:
    path = CAMPAIGN / "role_inputs" / f"{cell_name}.json"
    save(path, data)
    return RoleJob(
        cell_name,
        role,
        str(path.relative_to(CAMPAIGN)),
        sha(path),
        model,
        effort,
    )


def grow(
    label: str,
    configurations: list[tuple[str, str, str]],
    names: list[str],
    source_prefix: str,
    parser_version: int = 2,
) -> None:
    """One observation at a time; all author configurations see same work."""
    books: dict[str, Playbook] = {
        tag: Playbook() for tag, _, _ in configurations
    }
    for step, theorem in enumerate(names):
        evidence = read(
            CAMPAIGN / "evidence" / f"{source_prefix}__{theorem}.json"
        )
        encoded = json.dumps(evidence, sort_keys=True)
        reflect_batch = f"{label}-{step:02d}-reflect"
        reflect_jobs = [
            role_job(
                f"{label}__{tag}__step{step:02d}__reflect__{theorem}",
                "reflect_v3" if parser_version == 3 else "reflect",
                dict(evidence=encoded, playbook=books[tag].render_markdown()),
                model,
                effort,
            )
            for tag, model, effort in configurations
        ]
        register_roles(reflect_batch, reflect_jobs)
        launch(reflect_batch, roles=True)
        reflections: dict[str, dict[str, Any]] = {}
        curate_jobs: list[RoleJob] = []
        for (tag, model, effort), j in zip(
            configurations, reflect_jobs, strict=True
        ):
            values = result(reflect_batch, j.cell)["values"]
            reflections[tag] = (
                values[0]
                if values
                else dict(
                    diagnosis="No parseable reflection; inspect original evidence",
                    bullet_tags=[],
                )
            )
            curate_jobs.append(
                role_job(
                    f"{label}__{tag}__step{step:02d}__curate__{theorem}",
                    "curate_v3" if parser_version == 3 else "curate",
                    dict(
                        evidence=encoded,
                        reflection=json.dumps(reflections[tag]),
                        playbook=books[tag].render_markdown(),
                    ),
                    model,
                    effort,
                )
            )
        curate_batch = f"{label}-{step:02d}-curate"
        register_roles(curate_batch, curate_jobs)
        launch(curate_batch, roles=True)
        for (tag, _, _), j in zip(configurations, curate_jobs, strict=True):
            values = result(curate_batch, j.cell)["values"]
            delta = (
                values[0]
                if values
                else dict(operations=[], reasoning="Unparseable curation")
            )
            operations = TypeAdapter(list[AddOp]).validate_python(
                delta["operations"]
            )
            tags = TypeAdapter(list[BulletTag]).validate_python(
                reflections[tag]["bullet_tags"]
            )
            outcome = merge(
                books[tag],
                operations,
                tags,
                max_tokens=6000,
                dedup_counts_helpful=False,
            )
            books[tag] = outcome.playbook
            save(
                CAMPAIGN
                / "learning_events"
                / f"{label}__{tag}__{step:02d}.json",
                dict(
                    theorem=theorem,
                    evidence_hash=digest(evidence),
                    reflection=reflections[tag],
                    delta=delta,
                    merge=asdict(outcome),
                ),
            )
            save_book(
                CAMPAIGN / "books" / f"{label}__{tag}__step{step:02d}.json",
                books[tag],
                dict(
                    training_theorems=names[: step + 1],
                    author=tag,
                    source=source_prefix,
                ),
            )
        print(
            json.dumps(
                dict(
                    label=label,
                    completed=step + 1,
                    total=len(names),
                    bullets={k: len(v.bullets) for k, v in books.items()},
                )
            ),
            flush=True,
        )
    for tag, _, _ in configurations:
        save_book(
            CAMPAIGN / "books" / f"{label}__{tag}.json",
            books[tag],
            dict(training_theorems=names, author=tag, source=source_prefix),
        )


def ladder() -> None:
    names = panel(8)
    save(
        CAMPAIGN / "ladder_protocol.json",
        dict(
            configurations=author_configs(),
            train_panel=names,
            calls="8 trajectories x 8 author configurations x 2 roles = 128 role outputs, at most 256 HTTP attempts",
            control="identical source trajectories, starting empty books, merge and work caps",
            selection="paired Luna solver pilot on fixed 12 trainX problems; coverage floor is control minus 1 (scaled 2/40 tolerance rounded up), then total cost; retain full frontier",
            no_solver_model_change=True,
            pilot_panel=panel(12, 20260920),
        ),
    )
    grow("ladder", author_configs(), names, "source_assisted")


def prepare_author_pilot() -> None:
    """Fixed 204 attempts, registered before inspecting any pilot outcome."""
    names = panel(12, 20260920)
    arms = [("author_none", "")]
    for version in ("ladder", "ladder_v2"):
        for tag, _, _ in author_configs():
            filename = f"books/{version}__{tag}.json"
            if not (CAMPAIGN / filename).exists():
                raise ValueError("Author book is not complete: " + filename)
            arms.append((version + "_" + tag, filename))
    jobs: list[c.Job] = []
    for i, theorem in enumerate(names):
        order = arms[i % len(arms) :] + arms[: i % len(arms)]
        for arm, filename in order:
            jobs.append(
                c.Job(
                    "train",
                    arm,
                    theorem,
                    0,
                    filename,
                    sha(CAMPAIGN / filename) if filename else "",
                )
            )
    if len(jobs) != 204:
        raise ValueError("Author pilot arithmetic changed")
    c.register("author_pilot", jobs)
    print(dict(registered=204, author_configurations=8, evidence_versions=2))


def assess_author_pilot() -> None:
    from collections import defaultdict
    from .analysis import metrics, paired
    from .completion import require_closed

    require_closed("author_pilot")

    jobs = [c.Job(**v) for v in read(CAMPAIGN / "batches/author_pilot.json")]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for j in jobs:
        row = cell(
            (str(OUTPUT / "author_pilot/configs" / c.name(j, None)), j.theorem)
        )
        groups[j.arm].append(row)
    baseline = groups["author_none"]
    comparisons = {k: paired(baseline, rows) for k, rows in groups.items()}
    threshold = metrics(baseline)["solves"] - 1
    eligible = [
        (metrics(rows)["cost"], -metrics(rows)["solves"], k)
        for k, rows in groups.items()
        if k.startswith("ladder_v2_") and metrics(rows)["solves"] >= threshold
    ]
    if not eligible:
        # A low-powered pilot cannot veto research. Keep best coverage and
        # lowest cost and disclose the missed exploratory coverage floor.
        eligible = [
            (metrics(rows)["cost"], -metrics(rows)["solves"], k)
            for k, rows in groups.items()
            if k.startswith("ladder_v2_")
        ]
        eligible.sort(key=lambda t: (t[1], t[0]))
    else:
        eligible.sort()
    selected = eligible[0][2].removeprefix("ladder_v2_")
    config = next(v for v in author_configs() if v[0] == selected)
    save(
        CAMPAIGN / "author_selection.json",
        dict(
            selected=config,
            comparisons=comparisons,
            metrics={k: metrics(v) for k, v in groups.items()},
            threshold=threshold,
            basis="Full-conversation v2 candidates only; minimum total cost within pilot coverage tolerance. V1 comparisons diagnose evidence omission. Selection is exploratory; core panels are fresh.",
        ),
    )
    print(json.dumps(dict(selected=config, comparisons=comparisons)))
