"""Immutable inputs and accounting for the approved ACE model suite.

Both harnesses use experiments.ace.ace_models_experiment. No provider
requests are made by registration, scoring, status, or dry-run commands.
"""

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any, Literal

import yaml

import delphyne as dp
from delphyne.utils.typing import pydantic_load

from ace.ace_playbook import Playbook
from experiments.ace.ace_bounded_experiment import (
    BoundedConfig,
    INCUMBENT,
    INCUMBENT_SHA,
    digest,
)
import experiments.common.miniF2F_bench as mf
from runtime.campaign_budget import Ledger
from runtime.model_registry import OmphalosReasoningEffort, price_tokens
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile
from tools.analysis.cell_records import cells_of_run
from tools.analysis.paired_evaluation import Observation
from tools.reports.grounded_report import families, write_new

CAMPAIGN = ROOT / "experiments/campaigns/ace_models_20260910"
OUTPUT = ROOT / "experiments/output/ace_models_20260910"
ALLOCATIONS = dict(
    prover=3.0,
    adaptation=5.0,
    screening=5.0,
    selection=4.0,
    benchmark=9.0,
    upper=2.0,
    retry=2.0,
)
EFFORTS: tuple[OmphalosReasoningEffort, ...] = (
    "low",
    "medium",
    "high",
    "xhigh",
)
ROLES = ("reflector", "curator", "auditor")
LUNA = "gpt-5.6-luna"
TERRA = "gpt-5.6-terra"


def fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True).encode()
    ).hexdigest()


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, data: object) -> None:
    path = CAMPAIGN / name
    path.parent.mkdir(parents=True, exist_ok=True)
    write_new(path, data)


@dataclass(frozen=True)
class RoleModel:
    model_name: str = LUNA
    reasoning_effort: OmphalosReasoningEffort = "medium"

    def __post_init__(self) -> None:
        if self.model_name not in (LUNA, TERRA):
            raise ValueError("only the registered Luna/Terra models")
        if self.reasoning_effort not in (*EFFORTS, "max"):
            raise ValueError("unregistered reasoning effort")
        if self.model_name == TERRA and self.reasoning_effort == "max":
            raise ValueError("Terra max is excluded")

    def label(self) -> str:
        return self.model_name.rsplit("-", 1)[1] + "-" + self.reasoning_effort


@dataclass(frozen=True)
class Recipe:
    reflector: RoleModel = RoleModel()
    curator: RoleModel = RoleModel()
    auditor: RoleModel | None = None

    def model_for(self, role: str) -> RoleModel:
        if role == "reducer":
            return self.curator
        if role not in ROLES:
            raise ValueError(role)
        result = getattr(self, role)
        if result is None:
            raise ValueError("auditing is off")
        return result

    def key(self) -> str:
        return fingerprint(asdict(self))[:16]


@dataclass
class ModelProofConfig(BoundedConfig):
    phase: str = "prover"

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        validate_proof(self)
        result = super().instantiate(context)
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = proof_name(self, None)
        return result


def proof_name(c: ModelProofConfig, _: object) -> str:
    return f"{c.bench_name}__{c.phase}-{c.arm_label}__{c.model_name}__seed{c.seed}"


def validate_proof(c: ModelProofConfig) -> None:
    reg = read("registration.json")
    panels = reg["panels"]
    allowed = {
        "prover": panels["source"] + panels["screen"],
        "selection": panels["selection"],
        "training": reg["train"],
        "validation": reg["validation"],
    }
    if c.phase not in allowed or c.bench_name not in allowed[c.phase]:
        raise ValueError("proof outside the registered phase panel")
    expected = mf.load_partition(
        "benchmarks/validationX.txt"
        if c.phase == "validation"
        else "benchmarks/trainX.txt"
    )[c.bench_name][0]
    if c.problem_file != expected:
        raise ValueError("statement substitution is prohibited")
    if (
        c.model_name != LUNA
        or not c.money
        or not c.focused
        or c.admission
        or c.restart
        or c.polished
        or c.num_requests != 64
        or c.max_dollar_budget != 0.10
        or c.output_limit != 32768
        or c.operation_seconds != 60
        or c.verifier_seconds != 300
        or c.view_bytes != 8192
    ):
        raise ValueError("unregistered change to flagship controls")
    if c.reasoning_effort not in (*EFFORTS, "max"):
        raise ValueError("unregistered prover effort")
    if c.phase in ("training", "validation"):
        if not (CAMPAIGN / "frozen.json").exists():
            raise ValueError("benchmark requires a frozen winner")
        if asdict(c) not in read("benchmark_manifest.json"):
            raise ValueError("cell is not in the frozen benchmark manifest")
    elif c.seed != 0:
        raise ValueError("extra development replicate prohibited")
    if (
        c.reasoning_effort == "max"
        and not read("prover_upper_gate.json")["open_max"]
    ):
        raise ValueError("max requires its registered signal")


@dataclass
class ModelRoleConfig:
    role: str
    model_name: str
    reasoning_effort: OmphalosReasoningEffort
    strategy: str
    strategy_args: dict[str, Any]
    policy: str
    policy_args: dict[str, Any]
    budget: dict[str, float]
    dependencies: dict[str, str]
    phase: str = "adaptation"

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        verify_hashes(self.dependencies)
        if self.role != "grounder":
            if (
                self.policy_args.get("model_name") != self.model_name
                or self.policy_args.get("reasoning_effort")
                != self.reasoning_effort
            ):
                raise ValueError(
                    "role routing disagrees with registered identity"
                )
            RoleModel(self.model_name, self.reasoning_effort)
            if self.reasoning_effort == "max":
                gate_role = "curator" if self.role == "reducer" else self.role
                if not read(f"{gate_role}_upper_gate.json")["open_max"]:
                    raise ValueError("role max requires its registered signal")
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = role_name(self, None)
        # The offline roles retain their historical soft per-role stop;
        # the campaign ledger independently reserves every HTTP request.
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "0"
        return dp.RunStrategyArgs(
            strategy=self.strategy,
            args=self.strategy_args,
            policy=self.policy,
            policy_args=self.policy_args,
            budget=self.budget,
        )


def role_name(c: ModelRoleConfig, _: object) -> str:
    return "role-" + c.role + "-" + fingerprint(asdict(c))[:24]


def verify_hashes(expected: dict[str, str]) -> None:
    for path, sha in expected.items():
        if digest(ROOT / path) != sha:
            raise ValueError(f"frozen input drift: {path}")


def source_hashes() -> dict[str, str]:
    paths: set[Path] = {ROOT / "delphyne.yaml"}
    for pattern in (
        "prove_*.py",
        "runtime/*.py",
        "ace/*.py",
        "prompts/**/*.jinja",
        "demos/*.demo.yaml",
        "experiments/common/*.py",
        "experiments/ace/ace_models*.py",
        "experiments/ace/ace_adaptation.py",
        "experiments/ace/ace_bounded_experiment.py",
        "tools/analysis/*.py",
    ):
        paths.update(ROOT.glob(pattern))
    paths.update(
        ROOT / f"benchmarks/{p}X.txt" for p in ("train", "validation")
    )
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}


def execution_hashes() -> dict[str, str]:
    """Original registration plus the recorded scheduling-only amendment."""
    expected = dict(read("registration.json")["execution_hashes"])
    path = CAMPAIGN / "scheduling_amendment.json"
    if path.exists():
        amendment = read("scheduling_amendment.json")
        if amendment["registration_sha256"] != digest(
            CAMPAIGN / "registration.json"
        ):
            raise ValueError("amendment belongs to another registration")
        allowed = {
            "experiments/common/ace_model_campaign.py",
            "experiments/ace/ace_models_experiment.py",
        }
        for name, change in amendment["changes"].items():
            if name not in allowed or expected[name] != change["before"]:
                raise ValueError("amendment changed a treatment or dependency")
            expected[name] = change["after"]
    return expected


def choose_panels(
    problems: dict[str, tuple[str, str]],
) -> dict[str, list[str]]:
    """Allocate whole families, with exact 4/4 source and screen quotas."""
    fs = families(problems)
    groups: dict[str, list[str]] = defaultdict(list)
    for bench, family in fs.items():
        groups[family].append(bench)
    rng = random.Random(20260910)
    panels: dict[str, list[str]] = dict(source=[], screen=[], selection=[])
    for competition in (True, False):
        blocks = [
            sorted(g)
            for g in groups.values()
            if all(
                n.startswith(("imo_", "aime_", "amc")) == competition
                for n in g
            )
        ]
        blocks.sort()
        rng.shuffle(blocks)
        for panel in ("source", "screen"):
            chosen: list[list[str]] = []

            # Finite subset search; never split a duplicate family.
            def take(i: int, remaining: int) -> bool:
                if remaining == 0:
                    return True
                for j in range(i, len(blocks)):
                    block = blocks[j]
                    if len(block) <= remaining:
                        chosen.append(block)
                        if take(j + 1, remaining - len(block)):
                            return True
                        chosen.pop()
                return False

            if not take(0, 4):
                raise ValueError("cannot form family-preserving 4/4 panels")
            for block in chosen:
                panels[panel].extend(block)
                blocks.remove(block)
        panels["selection"].extend(n for block in blocks for n in block)
    if sorted(n for panel in panels.values() for n in panel) != sorted(
        problems
    ):
        raise ValueError("panel allocation did not cover trainX exactly")
    if list(map(len, panels.values())) != [8, 8, 24]:
        raise ValueError("unexpected panel sizes")
    return panels


def prepare() -> None:
    if (CAMPAIGN / "registration.json").exists():
        verify_hashes(execution_hashes())
        return
    train = dict(mf.load_partition("benchmarks/trainX.txt"))
    validation = dict(mf.load_partition("benchmarks/validationX.txt"))
    profile = ROOT / "experiments/campaigns/ace_review_20260908/runtime.json"
    artifact = (
        ROOT / "experiments/campaigns/ace_bounded_20260908/artifact_v2.json"
    )
    if Playbook.load(INCUMBENT).sha256() != INCUMBENT_SHA:
        raise ValueError("incumbent changed")
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    save("runtime.json", json.loads(profile.read_text()))
    save(
        "registration.json",
        dict(
            ceiling=30,
            allocations=ALLOCATIONS,
            panels=choose_panels(train),
            families=families(train | validation),
            train=list(train),
            validation=list(validation),
            artifact=str(artifact.relative_to(ROOT)),
            artifact_sha256=digest(artifact),
            incumbent=str(INCUMBENT.relative_to(ROOT)),
            incumbent_sha256=INCUMBENT_SHA,
            execution_hashes=source_hashes(),
            runtime_sha256=digest(CAMPAIGN / "runtime.json"),
            statement_hashes={
                p: digest(ROOT / p) for p, _ in (train | validation).values()
            },
            inference_cost_ratio=1.20,
            cost_per_solve_ratio=1.0,
            selection_min_gain=2,
            final_min_gain=4,
            alpha=0.10,
            confidence=0.90,
            max_proof_cells=728,
            max_infrastructure_retries=4,
            expected_api_dollars=[15, 25],
            upper_gate="xhigh minus high >=2 qualified solves on existing panel; both cost gates",
            selection_rule="solves descending; inference cost; preparation cost; incumbent; lower effort",
            exposure="trainX and validationX development only; no protected outcomes",
            authorization="Guille: Implement the plan; $30 ceiling, 2026-09-10",
        ),
    )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(30, ALLOCATIONS)


def activate(stage: str) -> None:
    reg = read("registration.json")
    verify_hashes(
        execution_hashes()
        | reg["statement_hashes"]
        | {
            reg["artifact"]: reg["artifact_sha256"],
            str((CAMPAIGN / "runtime.json").relative_to(ROOT)): reg[
                "runtime_sha256"
            ],
        }
    )
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    Ledger(CAMPAIGN / "ledger.sqlite3").create(30, ALLOCATIONS)
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(CAMPAIGN / "ledger.sqlite3")
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = stage
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")


def proof_config(
    bench: str,
    effort: OmphalosReasoningEffort,
    playbook: str,
    phase: str,
    *,
    seed: int = 0,
    label: str = "",
) -> ModelProofConfig:
    reg = read("registration.json")
    allowed = reg["validation"] if phase == "validation" else reg["train"]
    if bench not in allowed:
        raise ValueError("problem outside the registered phase")
    files = mf.load_partition(
        "benchmarks/validationX.txt"
        if phase == "validation"
        else "benchmarks/trainX.txt"
    )
    pb = Playbook.load(ROOT / playbook)
    if pb.sha256() == INCUMBENT_SHA:
        playbook = str(INCUMBENT.relative_to(ROOT))
    return ModelProofConfig(
        bench_name=bench,
        problem_file=files[bench][0],
        model_name=LUNA,
        seed=seed,
        num_requests=64,
        temperature=None,
        toolset="core",
        reasoning_effort=effort,
        max_dollar_budget=0.10,
        artifact=reg["artifact"],
        artifact_sha256=reg["artifact_sha256"],
        money=True,
        focused=True,
        admission=False,
        restart=False,
        phase=phase,
        arm_label=label or f"{effort}-{pb.sha256()[:16]}",
        playbook_file=playbook,
        playbook_sha256=pb.sha256(),
    )


def launch(
    configs: list[ModelProofConfig] | list[ModelRoleConfig],
    stage: str,
    *,
    workers: int = 24,
) -> Path:
    """Launch an immutable batch through the shared, supervised CLI."""
    if not configs:
        raise ValueError("empty batch")
    kind: Literal["proof", "role"] = (
        "proof" if isinstance(configs[0], ModelProofConfig) else "role"
    )
    payload = dict(
        batch_protocol=2,
        kind=kind,
        stage=stage,
        configs=[asdict(c) for c in configs],
    )
    batch = fingerprint(payload)[:24]
    save(f"batches/{batch}.json", payload)
    log = CAMPAIGN / "logs" / f"{batch}.log"
    log.parent.mkdir(exist_ok=True)
    print(f"{stage}: {len(configs)} {kind} cells, batch {batch}", flush=True)
    with log.open("a") as stream:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "experiments.ace.ace_models_experiment",
                f"--batch={batch}",
                "run",
                f"--max_workers={workers}",
                "--wait",
            ],
            cwd=ROOT,
            stdout=stream,
            stderr=subprocess.STDOUT,
        )
    if result.returncode:
        raise RuntimeError(f"batch {batch} failed; inspect {log}")
    failed: list[str] = []
    for c in configs:
        name = (
            proof_name(c, None)
            if isinstance(c, ModelProofConfig)
            else role_name(c, None)
        )
        directory = OUTPUT / kind / "configs" / name
        if (
            not (directory / "result.yaml").exists()
            and (directory / "exception.txt").exists()
        ):
            error = (directory / "exception.txt").read_text()
            if any(
                token in error
                for token in (
                    "CampaignExhausted",
                    "AuthenticationError",
                    "PermissionDeniedError",
                )
            ):
                raise ValueError(f"non-retryable batch failure: {directory}")
            if any(
                token in error
                for token in (
                    "Timeout",
                    "ConnectionError",
                    "BrokenProcessPool",
                    "RateLimitError",
                )
            ):
                failed.append(name)
    if failed:
        if accounting()["unresolved"]:
            raise ValueError(
                "unknown liability must be reconciled before retry"
            )
        prior = sorted((CAMPAIGN / "retries").glob("*.json"))
        used = sum(len(json.loads(p.read_text())["names"]) for p in prior)
        if used + len(failed) > 4:
            raise ValueError(
                "registered infrastructure retry allowance exhausted"
            )
        retry_id = str(len(prior))
        save(
            f"retries/{retry_id}.json",
            dict(
                batch=batch,
                names=failed,
                reason="Recognized transient infrastructure failure; same cells and settings",
            ),
        )
        with log.open("a") as stream:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "experiments.ace.ace_models_experiment",
                    f"--batch={batch}",
                    f"--retry-manifest={retry_id}",
                    "run",
                    f"--max_workers={workers}",
                    "--wait",
                ],
                cwd=ROOT,
                stdout=stream,
                stderr=subprocess.STDOUT,
            )
        if result.returncode:
            raise RuntimeError(f"registered retry failed; inspect {log}")
    audit_requests(configs)
    return OUTPUT / kind


def audit_requests(
    configs: list[ModelProofConfig] | list[ModelRoleConfig],
) -> None:
    """Check the cached, fully defaulted requests, not just config labels."""
    for c in configs:
        proof = isinstance(c, ModelProofConfig)
        name = proof_name(c, None) if proof else role_name(c, None)
        path = (
            OUTPUT
            / ("proof" if proof else "role")
            / "configs"
            / name
            / "cache.yaml"
        )
        if not path.exists():
            continue
        rows: Any = yaml.load(path.read_text(), Loader=yaml.CSafeLoader) or []
        for entry in rows:
            options = entry["input"]["request"].get("options", {})
            model = options.get("model", "")
            if model == "__compute__" or not model:
                continue
            if (
                model != c.model_name
                or options.get("reasoning_effort") != c.reasoning_effort
            ):
                raise ValueError(
                    f"actual request model/effort mismatch: {name}"
                )
            if options.get("max_completion_tokens") != 32768:
                raise ValueError(f"actual output reservation changed: {name}")


def accounting() -> dict[str, Any]:
    ledger = Ledger(CAMPAIGN / "ledger.sqlite3")
    with ledger.connect() as db:
        rows = db.execute(
            "SELECT id,model,created,charged,reserved,status,usage,cell FROM receipts"
        ).fetchall()
    costs: dict[str, float] = defaultdict(float)
    unresolved: list[str] = []
    for key, model, created, charged, _reserved, _status, usage, cell in rows:
        if charged is None:
            unresolved.append(key)
            continue
        values = json.loads(usage or "{}")
        if "input_tokens" in values:
            value = price_tokens(
                model,
                values["input_tokens"],
                values.get("input_tokens_details", {}).get("cached_tokens", 0),
                values.get("output_tokens", 0),
                on=datetime.fromtimestamp(created, timezone.utc).date(),
            )
            if abs(value - charged) > 1e-8:
                raise ValueError(f"receipt/token mismatch: {key}")
        elif model == "text-embedding-3-small" and "total_tokens" in values:
            if abs(values["total_tokens"] * 0.02e-6 - charged) > 1e-9:
                raise ValueError(f"embedding receipt mismatch: {key}")
        elif charged:
            raise ValueError(f"charged receipt without usage: {key}")
        costs[cell] += charged
    return dict(
        costs=dict(costs),
        unresolved=unresolved,
        receipts=len(rows),
        campaign=ledger.summary(),
    )


def observations(
    configs: list[ModelProofConfig],
) -> dict[tuple[str, str], Observation]:
    acct = accounting()
    if acct["unresolved"]:
        raise ValueError("unresolved billing; no comparative verdict")
    records = {r.name: r for r in cells_of_run(OUTPUT / "proof")}
    result: dict[tuple[str, str], Observation] = {}
    for c in configs:
        name = proof_name(c, None)
        if name not in records:
            raise ValueError(f"missing expected cell: {name}")
        r = records[name]
        for error in (OUTPUT / "proof/configs" / name).glob("exception*.txt"):
            if "CampaignExhausted" in error.read_text():
                raise ValueError("administratively censored panel; no verdict")
        if r.requests and name not in acct["costs"]:
            raise ValueError(f"missing receipt: {name}")
        cost = acct["costs"].get(name, 0.0)
        previous = sum(
            cache_cost(p, c.model_name)
            for p in (OUTPUT / "proof/configs" / name / "attempts").glob(
                "*/cache.yaml"
            )
        )
        if abs(cost - r.cost - previous) > 1e-7:
            raise ValueError(f"cache/receipt discrepancy: {name}")
        if r.cell in result:
            raise ValueError("duplicate theorem/replicate in arm")
        result[r.cell] = Observation(r.solved, cost, r.platform_failed)
    return result


def cache_cost(path: Path, model: str) -> float:
    rows: Any = yaml.load(path.read_text(), Loader=yaml.CSafeLoader) or []
    total = 0.0
    for row in rows:
        options = row["input"]["request"].get("options", {})
        if options.get("model") != model:
            continue
        output: Any = row.get("output") or {}
        values: Any = output.get("budget", {}).get("values", {})
        total += price_tokens(
            model,
            int(values.get("input_tokens", 0)),
            int(values.get("cached_input_tokens", 0)),
            int(values.get("output_tokens", 0)),
        )
    return total


def metrics(obs: dict[tuple[str, str], Observation]) -> dict[str, Any]:
    solves = sum(
        o.solved and not o.failed and o.cost <= 0.10 + 1e-12
        for o in obs.values()
    )
    cost = sum(o.cost for o in obs.values())
    return dict(
        cells=len(obs),
        solves=solves,
        cost=cost,
        cost_per_solve=cost / solves if solves else None,
    )


def eligible(
    candidate: dict[str, Any], control: dict[str, Any], gain: int = 0
) -> bool:
    if candidate["cells"] != control["cells"] or not candidate["cells"]:
        raise ValueError("cost gates require the same complete panel")
    return bool(
        candidate["solves"] >= control["solves"] + gain
        and candidate["cost"] <= 1.20 * control["cost"] + 1e-12
        and candidate["solves"] > 0
        and (
            not control["solves"]
            or candidate["cost"] * control["solves"]
            <= control["cost"] * candidate["solves"] + 1e-12
        )
    )


def load_configs(
    payload: dict[str, Any],
) -> list[ModelProofConfig] | list[ModelRoleConfig]:
    if payload["kind"] == "proof":
        return [pydantic_load(ModelProofConfig, c) for c in payload["configs"]]
    return [pydantic_load(ModelRoleConfig, c) for c in payload["configs"]]
