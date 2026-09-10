"""Train-only ACE role experiments on fixed bounded-generator evidence.

The v3 contracts, batch size four, 4K guard and embedding deduper are
retained. A terminal audit uses its existing contract and grounding gate.
All role calls are content addressed; upstream outputs are never selected
for luck and never overwritten. Both agent harnesses use the same driver.
"""

from dataclasses import asdict, dataclass
import hashlib
import os
from pathlib import Path
from typing import Any, cast

from ace.ace_dedup import EmbeddingDeduper
from ace.ace_evidence import (
    checkable_references,
    collect_failures,
    known_guidance,
    render_digest,
)
from ace.ace_playbook import Playbook, apply_audit, merge, refine
from experiments.ace.ace_adaptation import (
    ACEAdaptStepConfig,
    extract_trajectory,
    load_audit,
    load_delta,
    load_grounding,
    load_reflection,
    reflection_digest,
)
from experiments.common import ace_model_campaign as cm
from runtime.model_registry import OmphalosReasoningEffort


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def put(pb: Playbook) -> str:
    path = cm.CAMPAIGN / "artifacts/by_hash" / f"{pb.sha256()}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if Playbook.load(path).sha256() != pb.sha256():
            raise ValueError("playbook content address drift")
    else:
        pb.save(path)
    return str(path.relative_to(cm.ROOT))


@dataclass
class Step(ACEAdaptStepConfig):
    pinned_playbook: str = ""

    def _load_playbook(self) -> Playbook:
        pb = Playbook.load(cm.ROOT / self.pinned_playbook)
        if pb.sha256() != self.playbook_sha256:
            raise ValueError("role playbook changed")
        return pb

    def _reflector_playbook(self) -> str:
        # Source generators all saw the unchanged incumbent, even when
        # a later curation batch has already changed its working book.
        return Playbook.load(cm.INCUMBENT).render_prompt()


def dependencies(paths: list[Path]) -> dict[str, str]:
    return {str(p.relative_to(cm.ROOT)): cm.digest(p) for p in paths}


def call_config(step: Step, paths: list[Path]) -> cm.ModelRoleConfig:
    args = step.instantiate(None)
    return cm.ModelRoleConfig(
        role=step.role,
        model_name=step.model_name,
        reasoning_effort=cast(OmphalosReasoningEffort, step.reasoning_effort),
        strategy=args.strategy,
        strategy_args=cast(dict[str, Any], args.args),
        policy=args.policy,
        policy_args=cast(dict[str, Any], args.policy_args),
        budget=dict(args.budget or {}),
        dependencies=dependencies([cm.ROOT / step.pinned_playbook, *paths]),
    )


def execute(calls: list[cm.ModelRoleConfig], stage: str) -> list[Path]:
    dirs = [cm.OUTPUT / "role/configs" / cm.role_name(c, None) for c in calls]
    if any(not (p / "result.yaml").exists() for p in dirs):
        cm.launch(
            calls, stage, workers=1 if calls[0].role == "grounder" else 4
        )
    for path in dirs:
        if not (path / "result.yaml").exists():
            raise ValueError(
                f"incomplete role call: {path}; no artifact freeze"
            )
    if cm.accounting()["unresolved"]:
        raise ValueError("unknown adaptation charge; no artifact freeze")
    return dirs


def make_step(
    role: str,
    model: cm.RoleModel,
    book: str,
    bench: str,
    *,
    upstream: str = "",
    **kwargs: Any,
) -> Step:
    return Step(
        role=role,
        step=0,
        bench_name=bench,
        seed=0,
        model_name=model.model_name,
        toolset="core",
        reasoning_effort=model.reasoning_effort,
        num_requests=3,
        max_dollar_budget=0.25 if model.model_name == cm.TERRA else 0.02,
        playbook_sha256=Playbook.load(cm.ROOT / book).sha256(),
        upstream_sha256=upstream,
        pinned_playbook=book,
        render_version=3,
        curator_contract=3,
        show_definitions=True,
        **kwargs,
    )


def proposals(dirs: list[Path]) -> str:
    blocks: list[str] = []
    for k, directory in enumerate(dirs):
        delta = load_delta(directory)
        if delta is None or not delta.operations:
            continue
        lines = [
            f"- section: {op.section}\n  content: {op.content}"
            for op in delta.operations
        ]
        blocks.append(f"[Sample {k}]\n" + "\n".join(lines))
    return "\n\n---\n\n".join(blocks) if blocks else "(no proposals)"


def build(recipe: cm.Recipe, *, stage: str = "adaptation") -> dict[str, Any]:
    manifest = f"artifacts/{recipe.key()}.json"
    if (cm.CAMPAIGN / manifest).exists():
        existing = cm.read(manifest)
        cm.verify_hashes(existing["dependencies"])
        return existing
    cm.activate(stage)
    reg = cm.read("registration.json")
    source_dirs: dict[str, Path] = {}
    source_paths: list[Path] = []
    for bench in reg["panels"]["source"]:
        c = cm.proof_config(bench, "medium", reg["incumbent"], "prover")
        directory = cm.OUTPUT / "proof/configs" / cm.proof_name(c, None)
        cm.observations([c])
        source_dirs[bench] = directory
        source_paths.extend(
            [directory / "cache.yaml", directory / "result.yaml"]
        )
    cells: set[str] = set()
    log: list[dict[str, Any]] = []
    pb = Playbook.load(cm.INCUMBENT)
    # Keep explicit ancestry for audit inputs and preparation-cost accounting.
    provenance: dict[str, Any] = {
        b.id: {"origin": "incumbent", "playbook": cm.INCUMBENT_SHA}
        for b in pb.bullets
    }
    if recipe.auditor is not None:
        base = build(cm.Recipe(recipe.reflector, recipe.curator), stage=stage)
        pb = Playbook.load(cm.ROOT / base["playbook"])
        cells.update(base["role_cells"])
        provenance = base["provenance"]
        log.extend(base["log"])
    else:
        reflection_calls: list[cm.ModelRoleConfig] = []
        for bench, directory in source_dirs.items():
            trajectory = extract_trajectory(directory, bench)
            step = make_step(
                "reflector",
                recipe.reflector,
                reg["incumbent"],
                bench,
                upstream=sha(trajectory),
                trajectory_override=trajectory,
                generator_dir=str(directory.relative_to(cm.ROOT)),
            )
            reflection_calls.append(call_config(step, source_paths))
        refl_dirs = execute(reflection_calls, stage)
        cells.update(cm.role_name(c, None) for c in reflection_calls)
        benches = list(source_dirs)
        deduper = EmbeddingDeduper(
            cache_file=cm.CAMPAIGN / "embeddings.cache.h5"
        )
        with deduper:
            os.environ["OMPHALOS_CAMPAIGN_CELL"] = "embedding-" + recipe.key()
            for start in (0, 4):
                book = put(pb)
                curator_calls: list[cm.ModelRoleConfig] = []
                for i in range(start, start + 4):
                    bench, refl_dir = benches[i], refl_dirs[i]
                    refl = load_reflection(refl_dir)
                    trajectory = extract_trajectory(source_dirs[bench], bench)
                    upstream = (
                        reflection_digest(refl)
                        if refl is not None
                        else trajectory
                    )
                    step = make_step(
                        "curator",
                        recipe.curator,
                        book,
                        bench,
                        upstream=sha(upstream),
                        generator_dir=str(
                            source_dirs[bench].relative_to(cm.ROOT)
                        ),
                        reflector_dir=str(refl_dir.relative_to(cm.ROOT)),
                        reflector="on" if refl is not None else "off",
                        trajectory_override=trajectory,
                        progress=f"Step {i + 1}/8; batch {start // 4 + 1}/2; playbook {pb.token_estimate()}/4000 tokens.",
                    )
                    curator_calls.append(
                        call_config(
                            step, [*source_paths, refl_dir / "result.yaml"]
                        )
                    )
                cur_dirs = execute(curator_calls, stage)
                cells.update(cm.role_name(c, None) for c in curator_calls)
                step = make_step(
                    "reducer",
                    recipe.curator,
                    book,
                    benches[start],
                    upstream=sha(proposals(cur_dirs)),
                    generator_dir="|".join(
                        str(p.relative_to(cm.ROOT)) for p in cur_dirs
                    ),
                    progress=f"Batch {start // 4 + 1}/2; playbook {pb.token_estimate()}/4000 tokens.",
                )
                reducer = call_config(
                    step, [p / "result.yaml" for p in cur_dirs]
                )
                reduced_dir = execute([reducer], stage)[0]
                cells.add(cm.role_name(reducer, None))
                for i in range(start, start + 4):
                    reflection = load_reflection(refl_dirs[i])
                    pb = merge(
                        pb,
                        [],
                        reflection.bullet_tags if reflection else [],
                        deduper=deduper,
                    ).playbook
                reduced = load_delta(reduced_dir)
                # As in v3, a failed reducer falls back to member deltas.
                ops = (
                    reduced.operations
                    if reduced is not None
                    else [
                        op
                        for p in cur_dirs
                        for d in [load_delta(p)]
                        if d is not None
                        for op in d.operations
                    ]
                )
                os.environ["OMPHALOS_CAMPAIGN_CELL"] = (
                    "embedding-" + recipe.key()
                )
                merged = merge(
                    pb,
                    ops,
                    [],
                    deduper=deduper,
                    dedup_counts_helpful=False,
                    max_tokens=4000,
                )
                pb = merged.playbook
                for bid in merged.added:
                    provenance[bid] = dict(
                        origin="reducer",
                        source=benches[start : start + 4],
                        role_cell=cm.role_name(reducer, None),
                    )
                log.append(
                    dict(
                        batch=start // 4,
                        added=merged.added,
                        dropped=merged.dropped,
                        warnings=merged.warnings,
                        reflector_failed=[
                            load_reflection(p) is None
                            for p in refl_dirs[start : start + 4]
                        ],
                        curator_failed=[
                            load_delta(p) is None for p in cur_dirs
                        ],
                        reducer_failed=reduced is None,
                    )
                )
            # Existing v3 also refines at the end of an epoch.
            refined = refine(pb, deduper, prune_harmful=True, max_tokens=4000)
            pb = refined.playbook
            log.append(
                dict(
                    refined=dict(
                        pruned=[b.id for b in refined.pruned],
                        merged=refined.merged,
                        compacted=[b.id for b in refined.compacted],
                    )
                )
            )
        cells.add("embedding-" + recipe.key())
    if recipe.auditor is not None:
        preaudit = put(pb)
        evidence = render_digest(
            collect_failures(source_dirs), attempts=len(source_dirs)
        )
        import json

        prov = json.dumps(provenance, sort_keys=True)
        step = make_step(
            "auditor",
            recipe.auditor,
            preaudit,
            "final",
            evidence=evidence,
            known_guidance=known_guidance(),
            provenance=prov,
            audit_max_additions=6,
        )
        audit_call = call_config(step, source_paths)
        audit_dir = execute([audit_call], stage)[0]
        cells.add(cm.role_name(audit_call, None))
        audit = load_audit(audit_dir)
        if audit is None:
            log.append(dict(audit_failed=True, preaudit=preaudit))
        else:
            names = checkable_references(
                n for op in audit.additions for n in op.references
            )
            missing: set[str] = set()
            checks: list[dict[str, Any]] = []
            if names:
                train = cm.mf.load_partition("benchmarks/trainX.txt")
                environments = "|".join(
                    "@".join(train[b]) for b in source_dirs
                )
                step = make_step(
                    "grounder",
                    cm.RoleModel(),
                    preaudit,
                    "final",
                    references="\n".join(names),
                    environments=environments,
                )
                grounding = call_config(step, source_paths)
                ground_dir = execute([grounding], stage)[0]
                cells.add(cm.role_name(grounding, None))
                results = load_grounding(ground_dir)
                if results is None:
                    raise ValueError(
                        "audit grounding missing; artifact incomplete"
                    )
                missing = {r.name for r in results if r.verdict == "missing"}
                checks = [asdict(r) for r in results]
            additions = [
                op
                for op in audit.additions
                if not (set(op.references) & missing)
            ]
            applied = apply_audit(
                pb, audit.decisions, additions, max_tokens=4000
            )
            pb = applied.playbook
            for bid in applied.added:
                provenance[bid] = dict(
                    origin="audit",
                    source=list(source_dirs),
                    role_cell=cm.role_name(audit_call, None),
                )
            log.append(
                dict(
                    preaudit=preaudit,
                    audit_failed=False,
                    grounding=checks,
                    audit=asdict(audit),
                    warnings=applied.warnings,
                )
            )
    path = put(pb)
    deps = dependencies(
        [
            cm.ROOT / path,
            *source_paths,
            *[
                cm.OUTPUT / "role/configs" / c / "result.yaml"
                for c in cells
                if c.startswith("role-")
            ],
        ]
    )
    data = dict(
        recipe=asdict(recipe),
        playbook=path,
        sha256=pb.sha256(),
        role_cells=sorted(cells),
        dependencies=deps,
        provenance=provenance,
        log=log,
    )
    cm.save(manifest, data)
    return data
