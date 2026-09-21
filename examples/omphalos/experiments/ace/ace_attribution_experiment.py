"""Approved ACE attribution and complete Terra scaling study (2026-09-12).

Exactly one seed: 80 new Luna no-book cells, 160 Terra main cells, 40
Terra training generators, 16 swaps and 16 effort diagnostics = 312 proof
episodes. Reuse 80 parity-checked Luna flagship observations. Training has
40 reflectors, 40 curators, 10 reducers and embeddings; existing parse retry
contracts apply. No automatic extra controls, seeds, book selection or
promotion. Terra runs after Luna irrespective of the Luna effect size.

Primary: validationX ACE-minus-no-ACE qualified coverage within each model
and its model interaction. Luna cap $0.10, Terra $1.00; medium reasoning in
all main arms. Report cost/coverage jointly, family-cluster 90% intervals
and two-sided p<0.10, with historical-control and development-data limits.
TrainX is in-sample for frozen books. Cost curves are retrospective actual
cost qualification, not simulations of a smaller admission budget.

API ceiling $75, including failures/retries/embeddings; no incomplete or
administratively censored panel receives a verdict. testX and protected
challenge data are closed. Both harnesses use this CLI on i34-gpu01:
 prepare | preflight | seal | campaign | status | run-batch <manifest> ...
"""

# ruff: noqa: E402 -- data guard must precede experiment imports
from runtime.development_only import install

install()

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import csv
import fcntl
from functools import cache
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any
import uuid

import delphyne as dp
from ace.ace_playbook import Playbook
from ace.ace_dedup import EmbeddingDeduper
from ace.ace_store import PlaybookStore
from experiments.ace import ace_adaptation as adapt
from experiments.coverage_cycle_experiment import partition, family_map
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.model_registry import price_tokens
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile

CAMPAIGN = ROOT / "experiments/campaigns/ace_attribution_20260912"
OUTPUT = ROOT / "experiments/output/ace_attribution_20260912"
VARIANT = "attribution-terra-20260912"
ADAPT_OUTPUT = ROOT / f"experiments/output/ace_adaptation_{VARIANT}"
LUNA = "gpt-5.6-luna"
TERRA = "gpt-5.6-terra"
BOOK = "experiments/playbooks/ace_x3_offline.yaml"
BOOK_SHA = "1e4aec7dbbe80e7a320db17a7c18fe0859bfc00898837c297be248a05dbde067"
ALLOCATIONS = dict(
    luna=4.0, adaptation=16.0, terra=40.0, swaps=4.0, effort=6.0, retry=5.0
)
STAGES = ("training", "validation")
ARMS = ("luna-none", "luna-ace", "terra-none", "terra-ace")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True).encode()
    ).hexdigest()


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    """Create immutable campaign evidence, accepting identical resumes."""
    path = CAMPAIGN / name
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != content:
            raise ValueError(f"Immutable artifact changed: {name}")
        return
    with path.open("x") as f:
        f.write(content)


def context() -> dp.ExecutionContext:
    return dp.workspace_execution_context(__file__)


@cache
def panel(stage: str) -> list[str]:
    families = family_map()
    groups: list[list[str]] = [[], []]
    for name in partition(stage):
        groups[int(name.startswith("mathd_"))].append(name)
    chosen: list[str] = []
    seen: set[str] = set()
    for group in groups:
        ranked = sorted(group, key=lambda n: fingerprint([20260912, stage, n]))
        count = 0
        for name in ranked:
            if families[name] in seen:
                continue
            seen.add(families[name])
            chosen.append(name)
            count += 1
            if count == 4:
                break
        if count != 4:
            raise ValueError("Cannot construct balanced distinct-family panel")
    return chosen


@dataclass
class ProofConfig:
    bench_name: str
    problem_file: str
    partition: str
    arm: str
    model_name: str
    playbook_file: str = ""
    playbook_sha256: str = ""
    reasoning_effort: str = "medium"
    seed: int = 0

    @property
    def cap(self) -> float:
        return 0.10 if self.model_name == LUNA else 1.00

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        validate_proof(self)
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
        book = ""
        if self.playbook_file:
            pb = Playbook.load(ROOT / self.playbook_file)
            if pb.sha256() != self.playbook_sha256:
                raise ValueError("Playbook drift")
            book = pb.render_prompt()
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args=dict(
                problem_file=self.problem_file,
                theorem_name=self.bench_name,
                playbook=book,
                claims=[],
                turn_budget=64,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
                verifier_seconds=300,
                admission=False,
                focused=True,
                restart=False,
            ),
            policy="prove_theorem_grounded_policy",
            policy_args=dict(
                model_name=self.model_name,
                reasoning_effort=self.reasoning_effort,
            ),
            budget=dict(price=self.cap, num_requests=64, rocq_seconds=300),
        )


def name(c: ProofConfig, _: object) -> str:
    return (
        f"{c.bench_name}__{c.arm}-{c.reasoning_effort}"
        f"__{c.model_name}__seed{c.seed}"
    )


def proof(
    stage: str, arm: str, theorem: str, effort: str = "medium"
) -> ProofConfig:
    model = LUNA if arm.startswith("luna") else TERRA
    book, sha = "", ""
    if arm in ("luna-ace", "terra-luna-book"):
        book, sha = BOOK, BOOK_SHA
    elif arm in ("terra-ace", "luna-terra-book"):
        frozen = read("terra_book.json")
        book, sha = frozen["file"], frozen["sha256"]
    return ProofConfig(
        theorem,
        partition(stage)[theorem],
        stage,
        arm,
        model,
        book,
        sha,
        effort,
    )


def validate_proof(c: ProofConfig) -> None:
    if c.seed != 0 or c.model_name not in (LUNA, TERRA):
        raise ValueError("Unregistered model or seed")
    if c.problem_file != partition(c.partition).get(c.bench_name):
        raise ValueError("Problem outside authorized partition")
    if c.arm not in (*ARMS, "luna-terra-book", "terra-luna-book"):
        raise ValueError("Unregistered arm")
    expected_model = LUNA if c.arm.startswith("luna") else TERRA
    if c.model_name != expected_model:
        raise ValueError("Model/arm mismatch")
    if c.reasoning_effort != "medium":
        if not (
            c.arm == "terra-none"
            and c.partition == "training"
            and c.bench_name in panel("training")
            and c.reasoning_effort in ("low", "high")
        ):
            raise ValueError("Unregistered effort diagnostic")
    if c.arm.endswith("-book"):
        if c.partition != "validation" or c.bench_name not in panel(
            "validation"
        ):
            raise ValueError("Unregistered swap cell")
    if c.arm.endswith("-none"):
        if c.playbook_file or c.playbook_sha256:
            raise ValueError("No-ACE control contains a book")
    elif c.arm in ("luna-ace", "terra-luna-book"):
        if (c.playbook_file, c.playbook_sha256) != (BOOK, BOOK_SHA):
            raise ValueError("Incumbent substitution")
    else:
        frozen = read("terra_book.json")
        if (c.playbook_file, c.playbook_sha256) != (
            frozen["file"],
            frozen["sha256"],
        ):
            raise ValueError("Terra book substitution")


def prepare() -> None:
    source = ROOT / "experiments/campaigns/coverage_cycle_20260911"
    refs = json.loads((source / "references.json").read_text())
    assert set(refs) == set(STAGES)
    for stage, rows in refs.items():
        assert len(rows) == 40
        assert {r["theorem"] for r in rows} == set(partition(stage))
        assert all(
            r["seed"] == 0 and r["effective_config_matches"] for r in rows
        )
    save("references.json", refs)
    save("runtime.json", json.loads((source / "runtime.json").read_text()))
    planned = [
        dict(partition=s, arm=a, theorem=n, effort="medium", seed=0)
        for s in STAGES
        for a in ("luna-none", "terra-none", "terra-ace")
        for n in partition(s)
    ]
    planned += [
        dict(partition="validation", arm=a, theorem=n, effort="medium", seed=0)
        for a in ("luna-terra-book", "terra-luna-book")
        for n in panel("validation")
    ]
    planned += [
        dict(
            partition="training", arm="terra-none", theorem=n, effort=e, seed=0
        )
        for e in ("low", "high")
        for n in panel("training")
    ]
    assert len(planned) == 272
    save("planned_proofs.json", planned)
    save(
        "protocol.json",
        dict(
            authorization="Guille: Implement the plan; 2026-09-12; $75 ceiling",
            ceiling=75,
            allocations=ALLOCATIONS,
            new_inference_cells=272,
            adaptation_generators=40,
            new_proof_episodes=312,
            role_jobs=dict(reflector=40, curator=40, reducer=10),
            role_parse_retries=2,
            infrastructure_retries=4,
            reuse_cells=80,
            seed=0,
            primary_partition="validation",
            confidence=0.90,
            alpha=0.10,
            families=family_map(),
            effort_panel=panel("training"),
            swap_panel=panel("validation"),
            primary="within-model ACE qualified coverage and model interaction",
            inference_caps={LUNA: 0.10, TERRA: 1.0},
            effort_selection=False,
            default_changed=False,
            control_commit="23329b0983a7f62564d29529a50005cce63c409c",
            legacy_commit="3162a40c",
            ace_introduction_commit="7bbb556f1",
        ),
    )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(75, ALLOCATIONS)


def seal() -> None:
    if not read("preflight.json")["passed"]:
        raise ValueError("Reference parity must pass before sealing")
    paths = [ROOT / "delphyne.yaml", ROOT / BOOK]
    for folder, pattern in (
        ("runtime", "*.py"),
        ("ace", "*.py"),
        ("prompts", "*.jinja"),
    ):
        paths.extend((ROOT / folder).rglob(pattern))
    paths.extend(ROOT.glob("prove*.py"))
    paths.extend(context().demo_files)
    paths.extend(
        [
            Path(__file__),
            ROOT / "experiments/common/ace_pools.py",
            ROOT / "experiments/common/ace_bench.py",
            ROOT / "experiments/ace/ace_adaptation.py",
            ROOT / "experiments/coverage_cycle_experiment.py",
            ROOT / "experiments/common/omphalos_launch.py",
            ROOT / "experiments/common/miniF2F_bench.py",
            ROOT / "tools/reports/ace_attribution_report.py",
            ROOT / "tools/analysis/cell_records.py",
            ROOT / "tools/analysis/paired_evaluation.py",
        ]
    )
    paths.extend(
        CAMPAIGN / n
        for n in (
            "protocol.json",
            "planned_proofs.json",
            "references.json",
            "runtime.json",
            "preflight.json",
        )
    )
    for stage in STAGES:
        paths.append(
            ROOT
            / "benchmarks"
            / ("trainX.txt" if stage == "training" else "validationX.txt")
        )
        paths.extend(ROOT / p for p in partition(stage).values())
        for ref in read("references.json")[stage]:
            paths.extend(
                ROOT / ref["source"] / "configs" / ref["name"] / f
                for f in ("cache.yaml", "result.yaml")
            )
    save("seal.json", {str(p.relative_to(ROOT)): digest(p) for p in paths})


def verify() -> None:
    expected_files = dict(read("seal.json"))
    # Preserve the original seal. Explicit, recorded execution amendments
    # may fix an infrastructure dependency without rewriting preregistration.
    for amendment in sorted((CAMPAIGN / "amendments").glob("*.json")):
        update = json.loads(amendment.read_text())
        for p, change in update["files"].items():
            if p in expected_files:
                assert expected_files[p] == change["before"]
            expected_files[p] = change["after"]
    for p, expected in expected_files.items():
        if digest(ROOT / p) != expected:
            raise ValueError(f"Sealed source drift: {p}")


def activate(stage: str) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = stage
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")
    os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "0"
    os.environ["OMPHALOS_CAMPAIGN_CELL"] = "embeddings"


def accounting() -> dict[str, Any]:
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    costs: dict[str, float] = defaultdict(float)
    unresolved: list[str] = []
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,usage,cell,status FROM receipts"
        ).fetchall()
    for ident, model, created, charged, usage, cell, status in rows:
        if charged is None or status != "settled":
            unresolved.append(ident)
            continue
        u = json.loads(usage or "{}")
        if charged or "input_tokens" in u:
            if model.startswith("text-embedding"):
                actual = (
                    u.get("total_tokens", u.get("prompt_tokens", 0))
                    * 0.02
                    / 1e6
                )
            else:
                actual = price_tokens(
                    model,
                    u["input_tokens"],
                    u.get("input_tokens_details", {}).get("cached_tokens", 0),
                    u.get("output_tokens", 0),
                    on=datetime.fromtimestamp(created, timezone.utc).date(),
                )
            if abs(actual - charged) > 1e-8:
                raise ValueError(f"Receipt price mismatch: {ident}")
        costs[cell] += charged
    return dict(
        costs=dict(costs),
        total=sum(costs.values()),
        requests=len(rows),
        unresolved=unresolved,
        ledger=ledger.summary(),
    )


def export_receipts() -> None:
    with (
        Ledger(CAMPAIGN / "ledger.sqlite3").connect() as db,
        (CAMPAIGN / "receipts.csv").open("w") as f,
    ):
        cursor = db.execute("SELECT * FROM receipts ORDER BY created,id")
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow([d[0] for d in cursor.description])
        writer.writerows(cursor)


def transfer_unused(source: str, target: str) -> None:
    """Move only completed-stage slack, once; never increase authorization."""
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        if db.execute(
            "SELECT 1 FROM transfers WHERE source=? AND target=?",
            (source, target),
        ).fetchone():
            return
        _, allocation = json.loads(
            db.execute("SELECT config FROM settings").fetchone()[0]
        )
        if db.execute(
            "SELECT 1 FROM receipts WHERE stage=? AND status!='settled'",
            (source,),
        ).fetchone():
            raise ValueError("Cannot release unresolved stage liability")
        used = db.execute(
            "SELECT COALESCE(SUM(charged),0) FROM receipts WHERE stage=?",
            (source,),
        ).fetchone()[0]
    amount = allocation[source] - used
    if amount > 1e-8:
        ledger.transfer(
            source,
            target,
            amount,
            "Completed stage; forward unused allocation within the approved $75 ceiling",
        )


@dataclass
class TrainingConfig(adapt.ACEAdaptStepConfig):
    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if (
            self.variant != VARIANT
            or self.model_name != TERRA
            or self.seed != 0
            or self.reasoning_effort != "medium"
            or self.bench_name not in partition("training")
        ):
            raise ValueError("Unregistered training job")
        if self.role not in ("generator", "reflector", "curator", "reducer"):
            raise ValueError("Unexpected training role")
        if self.max_dollar_budget != (
            1.0 if self.role == "generator" else 0.20
        ):
            raise ValueError("Training cap drift")
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "0"
        args = super().instantiate(context)
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = training_name(self, None)
        return args


def training_name(c: TrainingConfig, _: object) -> str:
    return adapt._config_name(c, uuid.UUID(int=0))  # pyright: ignore[reportPrivateUsage]


class TerraVariant(adapt.AdaptVariant):
    def role_model(self, role: str) -> str:
        return TERRA


def training_variant() -> TerraVariant:
    original = adapt.VARIANTS["x3-offline"]
    values: dict[str, Any] = asdict(original) | dict(
        name=VARIANT,
        final_playbook="ace_attribution_terra_20260912.yaml",
        generator_cap=1.0,
        role_cap=0.20,
        campaign_runtime=str((CAMPAIGN / "runtime.json").relative_to(ROOT)),
    )
    return TerraVariant(**values)


def launch(
    configs: Sequence[ProofConfig | TrainingConfig],
    stage: str,
    output: Path,
    *,
    workers: int = 24,
    needs_rocq: bool = True,
) -> None:
    verify()
    if accounting()["unresolved"]:
        raise ValueError("Unresolved liability; no further dispatch")
    kind = "proof" if isinstance(configs[0], ProofConfig) else "training"
    payload = dict(
        kind=kind,
        stage=stage,
        output=str(output.relative_to(ROOT)),
        configs=[asdict(c) for c in configs],
        workers=workers,
        needs_rocq=needs_rocq,
    )
    ident = fingerprint(payload)[:24]
    filename = f"batches/{ident}.json"
    save(filename, payload)
    completed = CAMPAIGN / f"batches/{ident}.complete.json"
    if completed.exists():
        return
    command = [
        sys.executable,
        "-m",
        "experiments.ace.ace_attribution_experiment",
        "run-batch",
        filename,
        "run",
        f"--max_workers={workers}",
        "--wait",
    ]
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode:
        raise RuntimeError(
            f"Batch {ident} exited {result.returncode}; inspect before retry"
        )
    names = [
        name(c, None) if isinstance(c, ProofConfig) else training_name(c, None)
        for c in configs
    ]
    statuses = {n: ol.ground_truth(output / "configs" / n) for n in names}
    if any(s not in ("done", "failed") for s in statuses.values()):
        raise ValueError("Incomplete batch")
    for n in names:
        for p in (output / "configs" / n).glob("exception*.txt"):
            if "CampaignExhausted" in p.read_text():
                raise ValueError("Administrative censoring; no verdict")
    if accounting()["unresolved"]:
        raise ValueError("Unresolved liability after batch")
    save(f"batches/{ident}.complete.json", statuses)
    export_receipts()


class TrainingRunner(adapt.RoleRunner[adapt.ACEAdaptStepConfig]):
    def run(
        self,
        configs: Sequence[adapt.ACEAdaptStepConfig],
        max_workers: int,
        needs_rocq: bool = True,
    ) -> dict[str, str]:
        if not configs:
            return {}
        converted = [TrainingConfig(**asdict(c)) for c in configs]
        launch(
            converted,
            "adaptation",
            ADAPT_OUTPUT,
            workers=min(4, max_workers),
            needs_rocq=needs_rocq,
        )
        return {
            training_name(c, None): ol.ground_truth(
                ADAPT_OUTPUT / "configs" / training_name(c, None)
            )
            for c in converted
        }


def train_book() -> None:
    if (CAMPAIGN / "terra_book.json").exists():
        frozen = read("terra_book.json")
        assert (
            Playbook.load(ROOT / frozen["file"]).sha256() == frozen["sha256"]
        )
        return
    activate("adaptation")
    variant = training_variant()
    batches = adapt.plan(variant, 1, None)
    assert sum(len(b) for b in batches) == 40
    save("adaptation_plan.json", [[asdict(s) for s in b] for b in batches])
    store = PlaybookStore(VARIANT)
    runner = TrainingRunner(
        TrainingConfig,
        str(ADAPT_OUTPUT.relative_to(ROOT)),
        adapt._config_name,  # pyright: ignore[reportPrivateUsage]
    )
    with EmbeddingDeduper(store.dir / "embeddings.cache.h5") as deduper:
        pb, _ = adapt.execute(
            variant,
            batches,
            adapt._Roles(runner, None),  # pyright: ignore[reportPrivateUsage]
            deduper,
            max_workers=4,
        )
    file = CAMPAIGN / "terra_playbook.yaml"
    pb.save(file)
    save(
        "terra_book.json",
        dict(
            file=str(file.relative_to(ROOT)),
            sha256=pb.sha256(),
            recipe=asdict(variant),
            source_model=TERRA,
            steps=40,
            bullets=len(pb.bullets),
            tokens_estimate=pb.token_estimate(),
            training_output=str(ADAPT_OUTPUT.relative_to(ROOT)),
        ),
    )
    export_receipts()


def run_batch(filename: str) -> None:
    verify()
    if not filename.startswith("batches/") or ".." in filename:
        raise ValueError("Invalid manifest")
    batch = read(filename)
    if filename != f"batches/{fingerprint(batch)[:24]}.json":
        raise ValueError("Manifest drift")
    # Main inference is complete before swaps, and swaps before effort.
    # Carry its unused liability allowance forward so simultaneous request
    # reservations do not administratively censor these small panels.
    # Doing this at batch entry also supports a running coordinator that
    # was started before this recorded bookkeeping amendment.
    if batch["stage"] == "swaps":
        transfer_unused("terra", "swaps")
    elif batch["stage"] == "effort":
        transfer_unused("swaps", "effort")
    activate(batch["stage"])
    cls = ProofConfig if batch["kind"] == "proof" else TrainingConfig
    configs = [cls(**raw) for raw in batch["configs"]]

    def naming(cfg: ProofConfig | TrainingConfig, uid: uuid.UUID) -> str:
        return (
            name(cfg, uid)
            if isinstance(cfg, ProofConfig)
            else training_name(cfg, uid)
        )

    ol.OmphalosExperiment(
        config_class=cls,
        context=context(),
        configs=configs,
        output_dir=batch["output"],
        config_naming=naming,
        attempts=1,
        wait_for_slots=True,
        needs_rocq=batch["needs_rocq"],
    ).run_cli()


def campaign() -> None:
    verify()
    with (CAMPAIGN / "campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for stage in STAGES:
            launch(
                [proof(stage, "luna-none", n) for n in partition(stage)],
                "luna",
                OUTPUT / stage / "luna-none",
            )
        from tools.reports.ace_attribution_report import report

        if not (CAMPAIGN / "luna_report.json").exists():
            report("luna")
        transfer_unused("luna", "terra")
        train_book()
        transfer_unused("adaptation", "terra")
        for stage in STAGES:
            configs = [
                proof(stage, a, n)
                for a in ("terra-none", "terra-ace")
                for n in partition(stage)
            ]
            random.Random(20260912).shuffle(configs)
            launch(configs, "terra", OUTPUT / stage / "terra")
        swaps = [
            proof("validation", a, n)
            for a in ("luna-terra-book", "terra-luna-book")
            for n in panel("validation")
        ]
        random.Random(20260912).shuffle(swaps)
        launch(swaps, "swaps", OUTPUT / "swaps")
        efforts = [
            proof("training", "terra-none", n, e)
            for e in ("low", "high")
            for n in panel("training")
        ]
        random.Random(20260912).shuffle(efforts)
        launch(efforts, "effort", OUTPUT / "effort")
        report("complete")
        save("final_accounting.json", accounting())


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if command == "run-batch":
        filename = sys.argv[2]
        sys.argv[:] = [sys.argv[0], *sys.argv[3:]]
        run_batch(filename)
    elif command == "prepare":
        prepare()
    elif command == "preflight":
        from tools.reports.ace_attribution_report import preflight

        preflight()
    elif command == "seal":
        seal()
    elif command == "campaign":
        campaign()
    elif command == "status":
        print(json.dumps(accounting(), indent=2))
    else:
        raise ValueError(command)


if __name__ == "__main__":
    main()
