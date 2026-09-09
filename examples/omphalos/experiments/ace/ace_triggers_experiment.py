"""
Build and freeze the trigger table of a frozen playbook (hint on error).

One LLM call (`prove_ace.AssignTriggers`) per playbook: the assigner
sees the bullets with ids, the failure taxonomy it may use and the
digest of what the verifier rejected on the adaptation pool, and
answers with a trigger per bullet (`ace_triggers`). The answer is
validated (`TriggerTable.build`: ids exist, classes are known, every
regex compiles) and replayed over the recorded trainX verdicts
(`ace_triggers.coverage`) so the table says, before anything is paid,
which bullets would have fired where and which never fire. Then it is
frozen as `experiments/playbooks/<stem>.triggers.yaml` (self-contained:
bullet contents and the playbook sha inside) with a provenance sidecar.

Runs as an `OmphalosExperiment` of one config so the call is cached,
resumable and replayable like every other role call; the stronger
model is the default because this is the one ACE step where a better
model costs a few cents once (HINTS #49's economics).

Usage:
    python -m experiments.ace.ace_triggers_experiment \\
        --playbook=ace_x5_offline.yaml [--model=gpt-5.6-terra] \\
        [--effort=medium] [--pool=x_train_agentic]
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import datetime as dt
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

import delphyne as dp
import delphyne.stdlib.answer_loaders as al

import experiments.common.omphalos_launch as ol  # noqa: E402
from ace.ace_evidence import FailedVerdict, render_digest  # noqa: E402
from ace.ace_playbook import Playbook  # noqa: E402
from ace.ace_triggers import (  # noqa: E402
    TriggerAssignment,
    TriggerError,
    TriggerTable,
    coverage,
    render_playbook_for_assignment,
    render_taxonomy,
)
from tools.analysis.failure_analysis import FINE_TAXONOMY, TAXONOMY, load_run  # noqa: E402
from tools.analysis.failure_analysis import refine_class  # noqa: E402

_OMPHALOS_DIR = OMPHALOS_ROOT

PLAYBOOKS_DIR = _OMPHALOS_DIR / "experiments" / "playbooks"
DEFAULT_MODEL = "gpt-5.6-terra"
DEFAULT_EFFORT = "medium"
DEFAULT_POOL = "x_train_agentic"
ASSIGN_DOLLAR_CAP = 0.50
"""Per-call cap: one terra call over ~6k input tokens costs cents; the
cap is a runaway guard for the retry loop, not a budget."""
MAX_PATTERNS = 3


@dataclass
class TriggerAssignConfig:
    """
    The one-shot assigner call. `evidence` and `classes` are pinned
    into the identity (like the curators' `evidence`), so the config
    can never run against a different digest than it was created for.
    """

    playbook_file: str
    playbook_sha256: str
    model_name: str
    reasoning_effort: str
    classes: str
    evidence: str
    max_patterns: int = MAX_PATTERNS
    max_dollar_budget: float = ASSIGN_DOLLAR_CAP
    api: str = "responses"
    temperature: float | None = None
    num_requests: int = 3

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        pb = Playbook.load(_OMPHALOS_DIR / self.playbook_file)
        assert pb.sha256() == self.playbook_sha256, (
            f"{self.playbook_file} drifted from the hash this config"
            " was created with"
        )
        return dp.RunStrategyArgs(
            strategy="assign_triggers",
            args={
                "playbook": render_playbook_for_assignment(pb),
                "classes": self.classes,
                "evidence": self.evidence,
                "max_patterns": self.max_patterns,
            },
            policy="assign_triggers_policy",
            policy_args={
                "model_name": self.model_name,
                "temperature": self.temperature,
                "api": self.api,
                "reasoning_effort": self.reasoning_effort,
                "max_requests": self.num_requests,
            },
            budget={
                dp.NUM_REQUESTS: float(self.num_requests),
                dp.DOLLAR_PRICE: self.max_dollar_budget,
            },
        )


def config_name(cfg: TriggerAssignConfig, _uid: object) -> str:
    stem = Path(cfg.playbook_file).stem
    return (
        f"assign_{stem}_{cfg.playbook_sha256[:8]}"
        f"__{cfg.model_name}_{cfg.reasoning_effort}"
    )


def pool_digest(runs: Sequence[Path]) -> str:
    """
    The pool's failure digest with the fine classes (`refine_class`),
    which the adaptation-time digest deliberately lacks: the assigner
    may key a bullet on `ring-failure` or `unify-failure`.
    """
    verdicts: list[FailedVerdict] = []
    cells = 0
    for run in runs:
        seen: set[str] = set()
        for v in load_run(run):
            seen.add(v.config)
            if v.success or not v.error_message:
                continue
            verdicts.append(
                FailedVerdict(
                    v.bench,
                    refine_class(v.error_message),
                    v.failing_tactic or "",
                    v.error_message,
                )
            )
        cells += len(seen)
    blurbs = {c.label: c.blurb for c in TAXONOMY + FINE_TAXONOMY}
    return render_digest(
        verdicts, attempts=cells, max_classes=14, max_items=12, blurbs=blurbs
    )


def _take_flag(name: str, default: str) -> str:
    prefix = f"--{name}="
    value = default
    for arg in list(sys.argv[1:]):
        if arg.startswith(prefix):
            value = arg[len(prefix) :]
            sys.argv.remove(arg)
    return value


def load_assignment(config_dir: Path) -> TriggerAssignment | None:
    values = al.load_success_values_from_command_file(
        config_dir / "result.yaml", TriggerAssignment
    )
    if not values:
        return None
    return cast(TriggerAssignment, values[0])


def main() -> int:
    playbook_name = _take_flag("playbook", "ace_x5_offline.yaml")
    model = _take_flag("model", DEFAULT_MODEL)
    effort = _take_flag("effort", DEFAULT_EFFORT)
    pool_names = [p for p in _take_flag("pool", DEFAULT_POOL).split(",") if p]
    workers = int(_take_flag("max_workers", "1"))

    path = PLAYBOOKS_DIR / playbook_name
    assert path.exists(), f"{path} is not a frozen playbook"
    pb = Playbook.load(path)
    stem = path.stem
    pools = [_OMPHALOS_DIR / "experiments" / "output" / n for n in pool_names]
    for pool in pools:
        assert (pool / "results_summary.csv").exists(), f"{pool}: no summary"
    evidence = pool_digest(pools)
    classes = render_taxonomy()
    cfg = TriggerAssignConfig(
        playbook_file=f"experiments/playbooks/{playbook_name}",
        playbook_sha256=pb.sha256(),
        model_name=model,
        reasoning_effort=effort,
        classes=classes,
        evidence=evidence,
    )
    output_dir = f"experiments/output/ace_triggers_{stem}"
    name = config_name(cfg, None)
    print(
        f"trigger assignment: playbook={playbook_name} sha={pb.sha256()[:8]}"
        f" model={model}/{effort} pool={','.join(pool_names)} -> {output_dir}"
        f"/configs/{name}",
        flush=True,
    )
    exp = ol.OmphalosExperiment(
        config_class=TriggerAssignConfig,
        context=dp.workspace_execution_context(__file__),
        configs=[cfg],
        output_dir=output_dir,
        config_naming=config_name,
        needs_rocq=False,
    ).load()
    exp.resume(max_workers=workers)
    config_dir = _OMPHALOS_DIR / output_dir / "configs" / name
    assignment = load_assignment(config_dir)
    if assignment is None:
        print("the assigner produced nothing usable; nothing frozen")
        return 2
    try:
        table = TriggerTable.build(pb, assignment.triggers)
    except TriggerError as e:
        print(f"REFUSED: {e}")
        return 3
    cov = coverage(table, pools)
    print(f"coverage on {','.join(pool_names)}:")
    print(cov.render())

    target = PLAYBOOKS_DIR / f"{stem}.triggers.yaml"
    text = table.dumps()
    if target.exists() and target.read_text() != text:
        old = TriggerTable.load(target)
        print(
            f"REFUSING to overwrite {target.name}: it holds a different"
            f" table ({old.sha256()[:8]} vs {table.sha256()[:8]}). Frozen"
            " tables are prepend-only like playbooks — rename the old one"
            " if a new table is wanted."
        )
        return 4
    target.write_text(text)
    prov: dict[str, Any] = {
        "playbook": playbook_name,
        "playbook_sha256": pb.sha256(),
        "triggers_sha256": table.sha256(),
        "model": model,
        "reasoning_effort": effort,
        "pool": pool_names,
        "config": f"{output_dir}/configs/{name}",
        "frozen": dt.date.today().isoformat(),
        "assigner_reasoning": assignment.reasoning,
        "rationales": {t.id: t.rationale.strip() for t in assignment.triggers},
        "coverage": cov.as_dict(),
    }
    (PLAYBOOKS_DIR / f"{stem}.triggers.provenance.yaml").write_text(
        yaml.safe_dump(prov, sort_keys=False, allow_unicode=True)
    )
    print(f"frozen {target.relative_to(_OMPHALOS_DIR)} ({table.sha256()[:8]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
