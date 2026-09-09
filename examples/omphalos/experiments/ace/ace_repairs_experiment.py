"""
Repair bullets: extend a frozen playbook with advice mined from the
verifier's accepted repairs (`ace_repairs`), and freeze the result
with its trigger table.

Steps, each recorded as a config of an `OmphalosExperiment` (cached,
resumable, replayable):

1. Mine the repairs of the adaptation-pool runs (`--pool`, default the
   trainX baseline plus the x5 chain's generator cells — trainX only)
   and render the ranked digest.
2. One call to a stronger model (`prove_ace.WriteRepairBullets`,
   default gpt-5.6-terra): at most `--max_new` bullets for classes the
   playbook leaves bare, each with `references` and a trigger.
3. The grounding gate (`prove_ace.ground_references`, `Locate` in one
   environment per import signature of trainX): an addition naming an
   object Rocq does not know is refused.
4. Deterministic append (`ace_playbook.merge`, size guard), freeze
   `experiments/playbooks/<out>` with a provenance sidecar, and freeze
   `<out stem>.triggers.yaml` = the base playbook's frozen trigger rows
   plus the new bullets' own triggers (goal-gated coverage over the
   pool recorded in its sidecar).

Usage:
    python -m experiments.ace.ace_repairs_experiment \\
        --playbook=ace_x5_offline.yaml --out=ace_x6_repairs.yaml \\
        [--model=gpt-5.6-terra] [--effort=medium] [--max_new=8]
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import datetime as dt
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

import delphyne as dp
import delphyne.stdlib.answer_loaders as al

import experiments.common.minif2f_x as x  # noqa: E402
import experiments.common.omphalos_launch as ol  # noqa: E402
from ace.ace_evidence import (  # noqa: E402
    checkable_references,
    known_guidance,
    representative_files,
)
from ace.ace_playbook import Playbook, merge  # noqa: E402
from ace.ace_repairs import Repair, mine_run, render_repairs  # noqa: E402
from ace.ace_triggers import (  # noqa: E402
    TriggerError,
    TriggerSpec,
    TriggerTable,
    coverage,
    render_playbook_for_assignment,
    render_taxonomy,
)
from prove_ace import (  # noqa: E402
    GroundingResult,
    RepairAddition,
    RepairBullets,
)

_OMPHALOS_DIR = OMPHALOS_ROOT

PLAYBOOKS_DIR = _OMPHALOS_DIR / "experiments" / "playbooks"
DEFAULT_MODEL = "gpt-5.6-terra"
DEFAULT_EFFORT = "medium"
WRITER_DOLLAR_CAP = 0.50
MAX_PATTERNS = 3
PLAYBOOK_MAX_TOKENS = 4000


@dataclass
class RepairWriterConfig:
    """The one-shot writer call; digest and guidance pinned into identity."""

    playbook_file: str
    playbook_sha256: str
    model_name: str
    reasoning_effort: str
    repairs: str
    classes: str
    known_guidance: str
    max_new_bullets: int = 8
    max_patterns: int = MAX_PATTERNS
    max_dollar_budget: float = WRITER_DOLLAR_CAP
    api: str = "responses"
    temperature: float | None = None
    num_requests: int = 3
    role: str = "writer"
    references: str = ""
    environments: str = ""

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        budget = {
            dp.NUM_REQUESTS: float(self.num_requests),
            dp.DOLLAR_PRICE: self.max_dollar_budget,
        }
        if self.role == "grounder":
            names = [n for n in self.references.split("\n") if n]
            envs = [
                (file, theorem)
                for file, _, theorem in (
                    spec.partition("@")
                    for spec in self.environments.split("|")
                    if spec
                )
            ]
            assert names and envs, "grounder scheduled with nothing to check"
            return dp.RunStrategyArgs(
                strategy="ground_references",
                args={"names": names, "environments": envs},
                policy="ground_references_policy",
                policy_args={},
                budget=budget,
            )
        pb = Playbook.load(_OMPHALOS_DIR / self.playbook_file)
        assert pb.sha256() == self.playbook_sha256, (
            f"{self.playbook_file} drifted from the hash this config"
            " was created with"
        )
        return dp.RunStrategyArgs(
            strategy="write_repair_bullets",
            args={
                "playbook": render_playbook_for_assignment(pb),
                "repairs": self.repairs,
                "classes": self.classes,
                "known_guidance": self.known_guidance,
                "max_new_bullets": self.max_new_bullets,
                "max_patterns": self.max_patterns,
            },
            policy="write_repair_bullets_policy",
            policy_args={
                "model_name": self.model_name,
                "temperature": self.temperature,
                "api": self.api,
                "reasoning_effort": self.reasoning_effort,
                "max_requests": self.num_requests,
            },
            budget=budget,
        )


def config_name(cfg: RepairWriterConfig, _uid: object) -> str:
    stem = Path(cfg.playbook_file).stem
    if cfg.role == "grounder":
        return f"ground_{stem}_{cfg.playbook_sha256[:8]}"
    return (
        f"write_{stem}_{cfg.playbook_sha256[:8]}"
        f"__{cfg.model_name}_{cfg.reasoning_effort}"
    )


def _take_flag(name: str, default: str) -> str:
    prefix = f"--{name}="
    value = default
    for arg in list(sys.argv[1:]):
        if arg.startswith(prefix):
            value = arg[len(prefix) :]
            sys.argv.remove(arg)
    return value


def _run(cfg: RepairWriterConfig, output_dir: str, needs_rocq: bool) -> Path:
    exp = ol.OmphalosExperiment(
        config_class=RepairWriterConfig,
        context=dp.workspace_execution_context(__file__),
        configs=[cfg],
        output_dir=output_dir,
        config_naming=config_name,
        needs_rocq=needs_rocq,
        wait_for_slots=True,
    ).load()
    exp.resume(max_workers=1)
    return _OMPHALOS_DIR / output_dir / "configs" / config_name(cfg, None)


def main() -> int:
    playbook_name = _take_flag("playbook", "ace_x5_offline.yaml")
    out_name = _take_flag("out", "ace_x6_repairs.yaml")
    model = _take_flag("model", DEFAULT_MODEL)
    effort = _take_flag("effort", DEFAULT_EFFORT)
    max_new = int(_take_flag("max_new", "8"))
    pool_spec = _take_flag(
        "pool", "x_train_agentic,ace_adaptation_x5-offline:_generator_"
    )

    base_path = PLAYBOOKS_DIR / playbook_name
    base_triggers = PLAYBOOKS_DIR / f"{base_path.stem}.triggers.yaml"
    assert base_path.exists(), f"{base_path} is not a frozen playbook"
    assert base_triggers.exists(), f"{base_triggers}: no trigger table"
    pb = Playbook.load(base_path)
    base_table = TriggerTable.load(base_triggers)
    assert base_table.playbook_sha256 == pb.sha256()
    out_path = PLAYBOOKS_DIR / out_name
    out_stem = out_path.stem

    # 1. mine
    repairs: list[Repair] = []
    pool_runs: list[str] = []
    cells = 0
    for spec in pool_spec.split(","):
        name, _, only = spec.partition(":")
        run = _OMPHALOS_DIR / "experiments" / "output" / name
        assert run.is_dir(), f"{run}: not a run"
        found = mine_run(run, only=only or None)
        repairs.extend(found)
        cells += len(
            [
                c
                for c in run.glob("configs/*/cache.yaml")
                if not only or only in c.parent.name
            ]
        )
        pool_runs.append(spec)
    digest = render_repairs(
        repairs, cells=cells, max_groups=16, max_examples=3
    )
    assert digest, "no repairs mined"
    print(f"mined {len(repairs)} repairs from {cells} cells:")
    print(digest)
    print()

    # 2. write
    output_dir = f"experiments/output/ace_repairs_{out_stem}"
    cfg = RepairWriterConfig(
        playbook_file=f"experiments/playbooks/{playbook_name}",
        playbook_sha256=pb.sha256(),
        model_name=model,
        reasoning_effort=effort,
        repairs=digest,
        classes=render_taxonomy(),
        known_guidance=known_guidance(),
        max_new_bullets=max_new,
    )
    writer_dir = _run(cfg, output_dir, needs_rocq=False)
    values = al.load_success_values_from_command_file(
        writer_dir / "result.yaml", RepairBullets
    )
    if not values:
        print("the writer produced nothing usable; nothing frozen")
        return 2
    written = cast(RepairBullets, values[0])
    print(f"writer proposed {len(written.additions)} bullet(s)")

    # 3. ground
    ops = [a.as_add_op() for a in written.additions]
    names = checkable_references(n for op in ops for n in op.references)
    results: list[GroundingResult] = []
    if names:
        envs = representative_files(x.TRAINX_PROBLEMS)
        gcfg = RepairWriterConfig(
            playbook_file=cfg.playbook_file,
            playbook_sha256=cfg.playbook_sha256,
            model_name=model,
            reasoning_effort=effort,
            repairs="",
            classes="",
            known_guidance="",
            role="grounder",
            references="\n".join(names),
            environments="|".join(f"{f}@{t}" for f, t in envs),
        )
        gdir = _run(gcfg, output_dir, needs_rocq=True)
        gvals = al.load_success_values_from_command_file(
            gdir / "result.yaml", list[GroundingResult]
        )
        if gvals:
            results = list(cast(list[GroundingResult], gvals[0]))
        else:
            print("grounder produced nothing; every addition kept")
    missing = {r.name for r in results if r.verdict == "missing"}
    kept_additions: list[RepairAddition] = []
    refused: list[dict[str, Any]] = []
    for add in written.additions:
        bad = sorted(
            n for n in checkable_references(add.references) if n in missing
        )
        if bad:
            refused.append({"content": add.content, "missing": bad})
            continue
        kept_additions.append(add)
    print(
        f"grounding: {len(names)} name(s) checked, {len(missing)} missing,"
        f" {len(refused)} addition(s) refused"
    )

    # 4. merge, freeze playbook + triggers
    before_ids = {b.id for b in pb.bullets}
    out = merge(
        pb,
        [a.as_add_op() for a in kept_additions],
        [],
        max_tokens=PLAYBOOK_MAX_TOKENS,
    )
    new_pb = out.playbook
    new_bullets = [b for b in new_pb.bullets if b.id not in before_ids]
    print(
        f"merged: {len(out.added)} added, {len(out.deduped)} folded,"
        f" {len(out.dropped)} refused by the size guard ->"
        f" {len(new_pb.bullets)} bullets, ~{new_pb.token_estimate()} tokens"
    )
    if out_path.exists():
        existing = Playbook.load(out_path)
        assert existing.sha256() == new_pb.sha256(), (
            f"refusing to overwrite {out_path.name}: sha"
            f" {existing.sha256()[:8]} -> {new_pb.sha256()[:8]}"
        )
    else:
        new_pb.save(out_path)
    # Triggers: base rows verbatim, new rows from the writer.
    specs = [
        TriggerSpec(
            e.bullet_id,
            classes=list(e.classes),
            names=list(e.names),
            patterns=list(e.patterns),
            goal_patterns=list(e.goal_patterns),
        )
        for e in base_table.entries
    ]
    added_by_content = {" ".join(b.content.split()): b.id for b in new_bullets}
    for add in kept_additions:
        bid = added_by_content.get(" ".join(add.content.split()))
        if bid is None:
            continue  # folded into an existing bullet by dedup
        specs.append(
            TriggerSpec(
                bid,
                classes=list(add.classes),
                names=list(add.names),
                patterns=list(add.patterns),
                goal_patterns=list(add.goal_patterns),
            )
        )
    try:
        table = TriggerTable.build(new_pb, specs)
    except TriggerError as e:
        print(f"REFUSED trigger table: {e}")
        return 3
    tpath = PLAYBOOKS_DIR / f"{out_stem}.triggers.yaml"
    text = table.dumps()
    if tpath.exists():
        assert tpath.read_text() == text, f"refusing to overwrite {tpath}"
    else:
        tpath.write_text(text)
    pool_paths = [
        _OMPHALOS_DIR / "experiments" / "output" / s.partition(":")[0]
        for s in pool_runs
    ]
    cov = coverage(table, pool_paths)
    print(cov.render())
    prov: dict[str, Any] = {
        "base_playbook": playbook_name,
        "base_sha256": pb.sha256(),
        "sha256": new_pb.sha256(),
        "triggers_sha256": table.sha256(),
        "model": model,
        "reasoning_effort": effort,
        "pool": pool_runs,
        "repairs_mined": len(repairs),
        "writer_config": str(writer_dir.relative_to(_OMPHALOS_DIR)),
        "writer_reasoning": written.reasoning,
        "proposed": len(written.additions),
        "ungrounded": refused,
        "grounding_missing": sorted(missing),
        "added": out.added,
        "folded": [list(d) for d in out.deduped],
        "size_refused": out.dropped,
        "rationales": {
            bid: a.rationale.strip()
            for a in kept_additions
            if (bid := added_by_content.get(" ".join(a.content.split())))
        },
        "frozen": dt.date.today().isoformat(),
        "selection_rule": "goal-gated (ace_triggers.score)",
        "coverage": cov.as_dict(),
    }
    (PLAYBOOKS_DIR / f"{out_stem}.provenance.yaml").write_text(
        yaml.safe_dump(prov, sort_keys=False, allow_unicode=True)
    )
    (PLAYBOOKS_DIR / f"{out_stem}.triggers.provenance.yaml").write_text(
        yaml.safe_dump(
            {
                "playbook": out_name,
                "playbook_sha256": new_pb.sha256(),
                "triggers_sha256": table.sha256(),
                "base_triggers": base_triggers.name,
                "frozen": dt.date.today().isoformat(),
                "selection_rule": "goal-gated (ace_triggers.score)",
                "coverage": cov.as_dict(),
            },
            sort_keys=False,
            allow_unicode=True,
        )
    )
    print(
        f"frozen {out_path.name} ({new_pb.sha256()[:8]}) and"
        f" {tpath.name} ({table.sha256()[:8]})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
