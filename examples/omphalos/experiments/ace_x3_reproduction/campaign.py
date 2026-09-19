"""Fixed 2x2 X3 reproduction: 40 validation theorems x 2 replicates x 4 arms.

Authorized 2026-09-18: $20 additional within the original $50 thesis ceiling,
with $18 matrix and $2 infrastructure reserve. No training, selection, extra
seeds, unsuccessful-attempt replacement, cache warmup, or default promotion.
Provider caching remains enabled. The $0.10 controller uses legacy accounting
to reproduce historical admission; corrected tariff-qualified coverage is
reported separately. Censoring or unresolved billing prohibits a verdict.
"""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any

import delphyne as dp
import yaml

from experiments.ace_sanitized.scope import partition
from experiments.ace_thesis import campaign as old
from experiments.ace_thesis.design import families, schedule
from experiments.common import omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.runtime_profiles import RuntimeProfile

from .accounting import SOURCES

ROOT = old.ROOT
NAME = "ace_x3_reproduction_20260918"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
ARMS = ("none_32768", "x3_32768", "none_8192", "x3_8192")
sha = old.sha


def read(filename: str) -> Any:
    return json.loads((CAMPAIGN / filename).read_text())


def save(filename: str, value: Any) -> None:
    path = CAMPAIGN / filename
    encoded = json.dumps(value, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != encoded:
            raise ValueError("Immutable artifact changed: " + filename)
        return
    path.write_text(encoded)


def context() -> dp.ExecutionContext:
    ctx = old.context()
    return replace(
        ctx,
        modules=(*ctx.modules, "experiments.ace_x3_reproduction.transport"),
    )


@dataclass(frozen=True)
class Job:
    arm: str
    theorem: str
    seed: int

    def __post_init__(self) -> None:
        if self.arm not in ARMS or self.seed not in (0, 1):
            raise ValueError("Unregistered arm or replicate")
        if self.theorem not in partition("validation"):
            raise ValueError("Only validationX is authorized")

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ.update(
            OMPHALOS_CAMPAIGN_CELL=name(self, None),
            OMPHALOS_CAMPAIGN_STAGE="matrix",
        )
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args=dict(
                problem_file=partition("validation")[self.theorem],
                theorem_name=self.theorem,
                playbook=read("book.json")["text"]
                if self.arm.startswith("x3_")
                else "",
                claims=[],
                turn_budget=64,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
                verifier_seconds=300,
                admission=False,
                focused=True,
                restart=False,
            ),
            policy="reproduction_policy",
            policy_args=dict(
                snapshot_directory=str(
                    CAMPAIGN / "transport" / name(self, None)
                ),
                evidence_directory=str(
                    CAMPAIGN / "responses" / name(self, None)
                ),
                pause_file=str(CAMPAIGN / "PAUSED"),
                output_tokens=int(self.arm.rsplit("_", 1)[1]),
            ),
            budget=dict(price=0.10, num_requests=64, rocq_seconds=300),
        )


def name(job: Job, _: object) -> str:
    return f"{job.arm}__{job.theorem}__seed{job.seed}"


def directory(job: Job) -> Path:
    return OUTPUT / "configs" / name(job, None)


def jobs() -> list[Job]:
    values = [Job(**v) for v in read("manifest.json")]
    expected = [
        Job(arm, theorem, seed)
        for theorem, seed, arm in schedule(
            list(partition("validation")), list(ARMS)
        )
    ]
    if values != expected or len({name(j, None) for j in values}) != 320:
        raise ValueError("Registered 320-cell counterbalanced matrix changed")
    return values


def activate(*, events: bool = True) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ.update(
        OMPHALOS_CAMPAIGN_LEDGER=str(CAMPAIGN / "ledger.sqlite3"),
        OMPHALOS_ESTIMATE_DOLLARS="1",
    )
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )
    else:
        os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)


def prepare() -> None:
    from .audit import prior_accounting

    prior = prior_accounting()
    if prior["corrected"] + 20 > 50:
        raise ValueError("Additional authorization exceeds cumulative ceiling")
    save("prior_accounting.json", prior)
    save("book.json", old.read("artifacts/x3_render.json"))
    save("runtime.json", old.read("runtime.json"))
    if not (CAMPAIGN / "protocol.json").exists():
        save(
            "protocol.json",
            dict(
                protocol=__doc__,
                created=datetime.now(timezone.utc).isoformat(),
                ceiling=20,
                allocations=dict(matrix=18, recovery=2),
                cumulative_thesis_ceiling=50,
                prior_corrected=prior["corrected"],
                families=families("validation"),
                arms=ARMS,
                cells=320,
                order="Rotate per theorem; reverse arm order in replicate 1",
                physical_seeds=False,
                cache="Provider enabled, fresh local caches, no artificial warmup",
                sources=SOURCES,
                sources_checked="2026-09-18",
                diagnostics="Metadata-only comparison with preceding completed response",
                primary="X3 versus empty at each cap; coverage and all-attempt tariff cost",
                interaction="Paired cap-by-book difference-in-differences; family bootstrap 90% CI",
                coverage="Raw and corrected cost <= $0.10; no coverage-loss veto by seed",
                uncertainty="40 theorem clusters; 2 replicates are not 80 independent problems",
                stop="No adaptive extra arms, learning, seeds or unfavorable replacements",
            ),
        )
    save(
        "manifest.json",
        [
            asdict(Job(arm, theorem, seed))
            for theorem, seed, arm in schedule(
                list(partition("validation")), list(ARMS)
            )
        ],
    )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(20, dict(matrix=18, recovery=2))
    # Only the already guarded thesis seal, never a mixed historical seal.
    sources = dict(old.read("seal.json"))
    for filename in (
        "__init__.py",
        "campaign.py",
        "transport.py",
        "accounting.py",
    ):
        path = Path(__file__).parent / filename
        sources[str(path.relative_to(ROOT))] = sha(path)
    for filename in (
        "protocol.json",
        "runtime.json",
        "book.json",
        "manifest.json",
        "prior_accounting.json",
    ):
        path = CAMPAIGN / filename
        sources[str(path.relative_to(ROOT))] = sha(path)
    for relative, expected in sources.items():
        if sha(ROOT / relative) != expected:
            raise ValueError("Pre-existing sealed source drift: " + relative)
    save("seal.json", sources)
    verify_seal()
    print(json.dumps(dict(prepared=True, cells=len(jobs()), prior=prior)))


def verify_seal() -> None:
    for relative, expected in read("seal.json").items():
        if sha(ROOT / relative) != expected:
            raise ValueError("Sealed source drift: " + relative)
    jobs()


def cell_result(job: Job) -> dict[str, Any] | None:
    folder = directory(job)
    status = ol.ground_truth(folder)
    if status not in ("done", "failed"):
        raise ValueError("Missing required cell: " + name(job, None))
    raw: dict[str, Any] = (
        yaml.load(
            (folder / "result.yaml").read_text(), Loader=yaml.CSafeLoader
        )
        if (folder / "result.yaml").exists()
        else {}
    )
    diagnostics = str(raw.get("diagnostics", "")) + str(
        raw.get("outcome", {}).get("diagnostics", "")
    )
    diagnostics += "".join(
        p.read_text() for p in folder.glob("exception*.txt")
    )
    if any(s in diagnostics for s in ("CampaignExhausted", "CampaignPaused")):
        raise ValueError("Administrative censoring: " + name(job, None))
    return raw.get("outcome", {}).get("result") if status == "done" else None


def run() -> None:
    verify_seal()
    if (CAMPAIGN / "PAUSED").exists() or not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Paused or credential unavailable")
    summary = Ledger(CAMPAIGN / "ledger.sqlite3").summary()
    if any(r["status"] != "settled" for r in summary["groups"]):
        raise ValueError("Unresolved receipts require reconciliation")
    activate()
    # Reserve each actual HTTP attempt atomically, rather than pretending
    # that 320 x the legacy controller allowance is a predicted invoice.
    sys.argv = [sys.argv[0], "run", "--max_workers=24", "--wait"]
    ol.OmphalosExperiment(
        config_class=Job,
        configs=jobs(),
        context=context(),
        output_dir=str(OUTPUT.relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()
