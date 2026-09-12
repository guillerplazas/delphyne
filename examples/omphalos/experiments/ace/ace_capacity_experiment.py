"""Registered ACE capacity follow-up, approved 2026-09-12.

Seed 0 only. Complete the 40-problem validation crossover with 64 new
episodes and 176 paid references. Purchase 200 matched creation-role jobs
and 80 episodes on a fixed eight-problem trainX diagnostic panel. Continue
32 of those diagnostic cells under money-only then broader search limits;
never repurchase prefixes or restart already solved cells.

Primary: the Terra-minus-Luna difference in ACE benefit using the SAME
Luna book on all 40 validation problems; 5 percentage points is meaningful.
Family-cluster 90% intervals and two-sided p<.10. All diagnostic-panel
results are exploratory. Coverage, actual/uncached costs, and stopping
causes must be reported together. No incomplete panel receives a verdict.

Only the remaining $36.11492508 of the existing $75 ledger is authorized.
testX and protected challenge data remain closed. Both harnesses run:
 prepare | seal | campaign | status | run-batch <manifest> run --wait
"""

# ruff: noqa: E402 -- install the data guard before experiment imports
from runtime.development_only import install

install()

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
import fcntl
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time
from typing import Any

import delphyne as dp
from ace.ace_playbook import Playbook
from ace.ace_verified_snippets import (
    SnippetBinding,
    SnippetWitness,
    preserve_verified_snippet,
    protect_reduction,
    replace_book_snippet,
)
from experiments.ace import ace_attribution_experiment as old
import experiments.common.omphalos_launch as ol
from runtime.campaign_budget import Ledger
from runtime.runtime_profiles import RuntimeProfile
from tools.reports.ace_attribution_report import args_of

ROOT = old.ROOT
CAMPAIGN = ROOT / "experiments/campaigns/ace_capacity_20260912"
OUTPUT = ROOT / "experiments/output/ace_capacity_20260912"
LEDGER = old.CAMPAIGN / "ledger.sqlite3"
PRIOR_SPEND = 38.88507492
REMAINING = 36.11492508
ALLOCATIONS = {
    "cross": 10.0,
    "creation": 4.0,
    "mechanisms": 12.0,
    "headroom": 10.11492508,
}
PANEL = (
    "mathd_numbertheory_48",
    "imo_1967_p3",
    "mathd_algebra_28",
    "amc12b_2002_p11",
    "amc12a_2020_p13",
    "mathd_numbertheory_629",
    "algebra_amgm_sum1toneqn_prod1tonleq1",
    "aime_1988_p8",
)
PROFILES = {
    "A": ("none", 1),
    "B": ("terra", 1),
    "C": ("none", 2),
    "D": ("terra", 2),
    "E": ("terra-fixed", 2),
}


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != content:
            raise ValueError(f"Immutable artifact changed: {name}")
    else:
        path.write_text(content)


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def context() -> dp.ExecutionContext:
    ctx = old.context()
    return replace(ctx, modules=(*ctx.modules, "prove_capacity"))


def register_budget() -> None:
    """Allocate unused existing money atomically; retain the single ceiling."""
    ledger = Ledger(LEDGER)
    with ledger.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        ceiling, allocations = json.loads(
            db.execute("SELECT config FROM settings").fetchone()[0]
        )
        if any(k.startswith("capacity-") for k in allocations):
            assert all("capacity-" + k in allocations for k in ALLOCATIONS)
            return
        if db.execute(
            "SELECT 1 FROM receipts WHERE status!='settled'"
        ).fetchone():
            raise ValueError("Unresolved prior liability")
        spent = dict(
            db.execute(
                "SELECT stage,SUM(charged) FROM receipts GROUP BY stage"
            )
        )
        assert abs(sum(spent.values()) - PRIOR_SPEND) < 1e-8
        assert ceiling == 75
        available = {k: v - spent.get(k, 0) for k, v in allocations.items()}
        assert abs(sum(available.values()) - REMAINING) < 1e-8
        for stage, amount in ALLOCATIONS.items():
            target = "capacity-" + stage
            allocations[target] = amount
            left = amount
            for source in sorted(available):
                take = min(left, max(0.0, available[source]))
                if take <= 1e-9:
                    continue
                available[source] -= take
                allocations[source] -= take
                left -= take
                db.execute(
                    "INSERT INTO transfers VALUES (?,?,?,?,?)",
                    (
                        time.time(),
                        source,
                        target,
                        take,
                        "Approved capacity follow-up; same $75 total ceiling",
                    ),
                )
            assert abs(left) < 1e-8
        db.execute(
            "UPDATE settings SET config=?",
            (json.dumps([ceiling, allocations], sort_keys=True),),
        )


def activate(stage: str) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(LEDGER)
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = "capacity-" + stage
    os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(CAMPAIGN / "events.jsonl")


def book(which: str) -> tuple[str, str]:
    if which == "none":
        return "", ""
    if which == "luna":
        return old.BOOK, old.BOOK_SHA
    if which == "terra":
        raw = old.read("terra_book.json")
    elif which == "terra-fixed":
        raw = read("fixed_book.json")
    else:
        raise ValueError(which)
    return raw["file"], raw["sha256"]


@dataclass
class ProofConfig:
    theorem: str
    partition: str
    model: str
    book: str
    profile: str
    feedback_version: int = 1
    level: int = 0
    seed: int = 0

    def identifier(self) -> str:
        return f"{self.theorem}__{self.profile}-level{self.level}__{self.model}__seed{self.seed}"

    def directory(self) -> Path:
        group = (
            "cross"
            if self.profile == "cross"
            else "mechanisms"
            if self.level == 0
            else f"headroom{self.level}"
        )
        return OUTPUT / group / "configs" / self.identifier()

    def snapshots(self) -> Path:
        return CAMPAIGN / "transport" / self.identifier()

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if self.seed != 0 or self.model not in (old.LUNA, old.TERRA):
            raise ValueError("Unregistered model or seed")
        problem = old.partition(self.partition).get(self.theorem)
        if not problem:
            raise ValueError("Problem outside the development partition")
        if self.profile == "cross":
            if self.partition != "validation" or self.theorem in old.panel(
                "validation"
            ):
                raise ValueError("Unregistered crossover cell")
            assert (self.book, self.feedback_version, self.level) == (
                "terra" if self.model == old.LUNA else "luna",
                1,
                0,
            )
        else:
            assert self.partition == "training" and self.theorem in PANEL
            assert (self.book, self.feedback_version) == PROFILES[self.profile]
            assert self.level in (0, 1, 2)
            if self.level:
                assert self.profile in ("C", "E")
        stage = (
            "cross"
            if self.profile == "cross"
            else "headroom"
            if self.level
            else "mechanisms"
        )
        os.environ["OMPHALOS_CAMPAIGN_STAGE"] = "capacity-" + stage
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = self.identifier()
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
        filename, sha = book(self.book)
        rendered = ""
        if filename:
            pb = Playbook.load(ROOT / filename)
            if pb.sha256() != sha:
                raise ValueError("Frozen playbook drift")
            rendered = pb.render_prompt()
        cap = (0.1 if self.model == old.LUNA else 1.0) * (
            2 if self.level else 1
        )
        seconds, turns = (600, 128) if self.level == 2 else (300, 64)
        prefix_cache = ""
        if self.level:
            parent = replace(self, level=self.level - 1)
            source = parent.directory()
            carried = CAMPAIGN / "carried" / f"{parent.identifier()}.json"
            if carried.exists():
                source = ROOT / json.loads(carried.read_text())["source"]
            prefix_cache = str(source / "cache.yaml")
            if not Path(prefix_cache).is_file():
                raise ValueError("Missing continuation prefix")
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args=dict(
                problem_file=problem,
                theorem_name=self.theorem,
                playbook=rendered,
                claims=[],
                turn_budget=turns,
                prompt_turn_budget=64,
                limits=dict(seconds=60, rpc_calls=512, view_bytes=8192),
                verifier_seconds=seconds,
                admission=False,
                focused=True,
                restart=False,
                feedback_version=self.feedback_version,
            ),
            policy="prove_capacity_policy",
            policy_args=dict(
                model_name=self.model,
                snapshot_directory=str(self.snapshots()),
                dollar_limit=cap,
                verifier_seconds=seconds,
                turn_budget=turns,
                prefix_cache=prefix_cache,
            ),
            budget=dict(price=cap, num_requests=turns, rocq_seconds=seconds),
        )


@dataclass
class RoleConfig:
    source: str
    model: str
    role: str
    input_sha256: str
    seed: int = 0

    def identifier(self) -> str:
        return f"{Path(self.source).parent.parent.name}__{Path(self.source).name}__{self.model}__seed0"

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        assert self.seed == 0 and self.model in (old.LUNA, old.TERRA)
        assert self.role in ("reflector", "curator", "reducer")
        original = args_of(ROOT / self.source)
        if old.fingerprint(original["args"]) != self.input_sha256:
            raise ValueError("Frozen creation input drift")
        if original["args"].get("problem_file"):
            assert (
                original["args"]["problem_file"]
                in old.partition("training").values()
            )
        os.environ["OMPHALOS_CAMPAIGN_STAGE"] = "capacity-creation"
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = self.identifier()
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "0"
        return dp.RunStrategyArgs(
            strategy=original["strategy"],
            args=original["args"],
            policy="capacity_role_policy",
            policy_args=original["policy_args"]
            | dict(
                model_name=self.model,
                reasoning_effort="medium",
                max_requests=3,
                snapshot_directory=str(
                    CAMPAIGN / "transport" / self.identifier()
                ),
                dollar_limit=0.02 if self.model == old.LUNA else 0.2,
            ),
            budget=dict(
                num_requests=3, price=0.02 if self.model == old.LUNA else 0.2
            ),
        )


def prepare() -> None:
    assert (
        len(old.partition("training"))
        == len(old.partition("validation"))
        == 40
    )
    assert (
        set(PANEL) <= set(old.partition("training")) and len(set(PANEL)) == 8
    )
    save("runtime.json", old.read("runtime.json"))
    save(
        "protocol.json",
        dict(
            authorization="Guille: Implement the plan; 2026-09-12",
            prior_spend=PRIOR_SPEND,
            remaining=REMAINING,
            total_ceiling=75,
            allocations=ALLOCATIONS,
            seed=0,
            trainX_cells=40,
            validationX_cells=40,
            diagnostic_panel=PANEL,
            profiles=PROFILES,
            new_crossover_episodes=64,
            reused_crossover_episodes=176,
            creation_jobs=200,
            new_diagnostic_episodes=80,
            continuation_cells=32,
            continuation_levels=[
                dict(price_multiplier=1, verifier_seconds=300, requests=64),
                dict(price_multiplier=2, verifier_seconds=300, requests=64),
                dict(price_multiplier=2, verifier_seconds=600, requests=128),
            ],
            primary="(Terra with Luna book - Terra no book) - (Luna with Luna book - Luna no book), validationX",
            meaningful_effect=0.05,
            alpha=0.1,
            confidence=0.9,
            diagnostics="Exploratory, mechanism-selected training panel; not representative coverage",
            secondary="Within-solver book-author effects; Holm-adjust the two author contrasts",
            pricing="Actual, uncached, and Luna-rate normalized; report cached-input shares",
            defaults_changed=False,
            extra_seeds=False,
        ),
    )
    raw, _ = book("terra")
    witness = SnippetWitness(
        "terra-step00-square",
        old.partition("training")["mathd_algebra_28"],
        "mathd_algebra_28",
        "experiments/output/ace_adaptation_attribution-terra-20260912/configs/step00_generator_mathd_algebra_28",
        "intros c f Hf [x Hx]. rewrite Hf in Hx.",
        "assert (hs : 0 <= (a * x + b) * (a * x + b)) by apply Rle_0_sqr",
        {"a": "4", "b": "5"},
        ". nra.",
    )
    invalid = "have hs : 0 <= (a * x + b) * (a * x + b) := Rle_0_sqr _"
    fixed_path = CAMPAIGN / "terra_playbook_source_verified.yaml"
    if not (CAMPAIGN / "fixed_book.json").exists():
        verdict = preserve_verified_snippet(witness, invalid)
        assert verdict.decision == "source_preserved"
        repaired = replace_book_snippet(
            Playbook.load(ROOT / raw), "rocq-00001", invalid, verdict
        )
        repaired.save(fixed_path)
        save("snippet_witness.json", asdict(witness))
        save("snippet_verification.json", asdict(verdict))
        save(
            "fixed_book.json",
            dict(
                file=str(fixed_path.relative_to(ROOT)),
                sha256=repaired.sha256(),
                source=raw,
                change="Only the verified syntax replacement in rocq-00001",
            ),
        )
    cross = [
        ProofConfig(
            n, "validation", m, "terra" if m == old.LUNA else "luna", "cross"
        )
        for n in old.partition("validation")
        if n not in old.panel("validation")
        for m in (old.LUNA, old.TERRA)
    ]
    mechanisms = [
        ProofConfig(n, "training", m, b, p, v)
        for n in PANEL
        for m in (old.LUNA, old.TERRA)
        for p, (b, v) in PROFILES.items()
    ]
    roles: list[RoleConfig] = []
    for source_model, root in (
        ("luna", ROOT / "experiments/output/ace_adaptation_x3-offline"),
        ("terra", old.ADAPT_OUTPUT),
    ):
        for role in (
            ("reflector", "curator", "reducer")
            if source_model == "luna"
            else ("reducer",)
        ):
            sources = sorted((root / "configs").glob(f"*_{role}_*"))
            assert len(sources) == (10 if role == "reducer" else 40)
            for source in sources:
                original = args_of(source)
                for model in (old.LUNA, old.TERRA):
                    roles.append(
                        RoleConfig(
                            str(source.relative_to(ROOT)),
                            model,
                            role,
                            old.fingerprint(original["args"]),
                        )
                    )
    assert (len(cross), len(mechanisms), len(roles)) == (64, 80, 200)
    for group, configs in (
        ("cross", cross),
        ("creation", roles),
        ("mechanisms", mechanisms),
    ):
        random.Random(20260912).shuffle(configs)
        save(f"planned_{group}.json", [asdict(c) for c in configs])
    save("families.json", old.family_map())
    references: list[dict[str, Any]] = []
    for ref in old.read("references.json")["validation"]:
        source = ROOT / ref["source"] / "configs" / ref["name"]
        references.append(
            dict(
                theorem=ref["theorem"],
                model=old.LUNA,
                book="luna",
                source=str(source.relative_to(ROOT)),
            )
        )
    for arm, which in (
        ("luna-none", "none"),
        ("terra-none", "none"),
        ("terra-ace", "terra"),
        ("luna-terra-book", "terra"),
        ("terra-luna-book", "luna"),
    ):
        from tools.reports.ace_attribution_report import directory_for

        for theorem in (
            old.panel("validation")
            if arm.endswith("-book")
            else old.partition("validation")
        ):
            cfg = old.proof("validation", arm, theorem)
            references.append(
                dict(
                    theorem=theorem,
                    model=cfg.model_name,
                    book=which,
                    source=str(directory_for(cfg).relative_to(ROOT)),
                )
            )
    assert len(references) == 176
    for ref in references:
        source = ROOT / ref["source"]
        ref["hashes"] = {
            f: old.digest(source / f) for f in ("cache.yaml", "result.yaml")
        }
    save("references.json", references)
    if not (CAMPAIGN / "reduction_protection.json").exists():
        delta = old.adapt.load_delta(
            old.ADAPT_OUTPUT / "configs/step00_reducer_mathd_algebra_28"
        )
        assert delta is not None
        protected, verdicts = protect_reduction(
            delta,
            {witness.identifier: witness},
            (SnippetBinding(0, invalid, witness.identifier),),
        )
        save(
            "reduction_protection.json",
            dict(
                before=asdict(delta),
                after=asdict(protected),
                verdicts=[asdict(v) for v in verdicts],
                scope="Only explicitly bound executable snippets carry a verification claim",
            ),
        )
    register_budget()


def seal() -> None:
    if not read("preflight.json")["passed"]:
        raise ValueError("Offline checks must pass before sealing")
    paths = [p for p in (ROOT / "runtime").glob("*.py")]
    paths.extend((ROOT / "ace").glob("*.py"))
    paths.extend(ROOT.glob("prove*.py"))
    paths.extend((ROOT / "prompts").rglob("*.jinja"))
    paths.extend(context().demo_files)
    paths.extend(
        ROOT / p
        for p in read("prior_source_manifest.json")["all_original_files"]
    )
    paths.extend(
        ROOT / ref["source"] / f
        for ref in read("references.json")
        for f in ("cache.yaml", "result.yaml")
    )
    paths.extend(
        ROOT / row["source"] / "result.yaml"
        for row in read("planned_creation.json")
    )
    paths.extend(
        [
            Path(__file__),
            ROOT / "delphyne.yaml",
            ROOT / old.BOOK,
            old.CAMPAIGN / "terra_playbook.yaml",
        ]
    )
    paths.extend(
        CAMPAIGN / n
        for n in (
            "protocol.json",
            "runtime.json",
            "fixed_book.json",
            "terra_playbook_source_verified.yaml",
            "planned_cross.json",
            "planned_creation.json",
            "planned_mechanisms.json",
            "preflight.json",
            "references.json",
        )
    )
    save("seal.json", {str(p.relative_to(ROOT)): old.digest(p) for p in paths})


def verify() -> None:
    for path, sha in read("seal.json").items():
        if old.digest(ROOT / path) != sha:
            raise ValueError(f"Sealed follow-up source drift: {path}")


def accounting() -> dict[str, Any]:
    all_data = old.accounting()
    by_stage: dict[str, float] = defaultdict(float)
    cells: dict[str, float] = defaultdict(float)
    with Ledger(LEDGER).connect() as db:
        rows = db.execute(
            "SELECT stage,cell,charged,status FROM receipts WHERE stage LIKE 'capacity-%'"
        ).fetchall()
    unresolved = 0
    for stage, cell, charged, status in rows:
        if charged is None or status != "settled":
            unresolved += 1
        else:
            by_stage[stage] += charged
            cells[cell] += charged
    return dict(
        new_spend=sum(by_stage.values()),
        stages=dict(by_stage),
        cells=dict(cells),
        requests=len(rows),
        unresolved=unresolved,
        total_spend=all_data["total"],
        remaining=75 - all_data["ledger"]["liability"],
        ledger=all_data["ledger"],
    )


def launch(
    configs: Sequence[ProofConfig] | Sequence[RoleConfig], group: str
) -> None:
    if not configs:
        return
    verify()
    if accounting()["unresolved"]:
        raise ValueError("Unresolved liability; no further dispatch")
    kind = "role" if isinstance(configs[0], RoleConfig) else "proof"
    stage = "headroom" if group.startswith("headroom") else group
    payload: dict[str, Any] = dict(
        kind=kind,
        stage=stage,
        output=str((OUTPUT / group).relative_to(ROOT)),
        configs=[asdict(c) for c in configs],
    )
    ident = old.fingerprint(payload)[:24]
    filename = f"batches/{ident}.json"
    save(filename, payload)
    if (CAMPAIGN / f"batches/{ident}.complete.json").exists():
        return
    command = [
        sys.executable,
        "-m",
        "experiments.ace.ace_capacity_experiment",
        "run-batch",
        filename,
        "run",
        "--max_workers=24",
        "--wait",
    ]
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode:
        raise RuntimeError(
            f"Batch {ident} exited {result.returncode}; inspect before retry"
        )
    statuses = {
        c.identifier(): ol.ground_truth(
            ROOT / payload["output"] / "configs" / c.identifier()
        )
        for c in configs
    }
    if any(s not in ("done", "failed") for s in statuses.values()):
        raise ValueError("Missing cells; no verdict")
    for name in statuses:
        for p in (ROOT / payload["output"] / "configs" / name).glob(
            "exception*.txt"
        ):
            if "CampaignExhausted" in p.read_text():
                raise ValueError("Administrative censoring; no verdict")
    if accounting()["unresolved"]:
        raise ValueError("Unresolved billing liability")
    save(f"batches/{ident}.complete.json", statuses)


def forward_unused(source: str, target: str) -> None:
    ledger = Ledger(LEDGER)
    summary = ledger.summary()
    key = "capacity-" + source
    used = sum(r["dollars"] for r in summary["groups"] if r["stage"] == key)
    unused = summary["allocations"][key] - used
    if unused > 1e-8:
        ledger.transfer(
            key,
            "capacity-" + target,
            unused,
            "Completed follow-up stage; unchanged total ceiling",
        )


def campaign() -> None:
    verify()
    with (CAMPAIGN / "campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        launch([ProofConfig(**r) for r in read("planned_cross.json")], "cross")
        forward_unused("cross", "creation")
        launch(
            [RoleConfig(**r) for r in read("planned_creation.json")],
            "creation",
        )
        forward_unused("creation", "mechanisms")
        base = [ProofConfig(**r) for r in read("planned_mechanisms.json")]
        launch(base, "mechanisms")
        forward_unused("mechanisms", "headroom")
        from tools.analysis.cell_records import (  # pyright: ignore[reportPrivateUsage]
            _result_head,  # pyright: ignore[reportPrivateUsage]
            _field,  # pyright: ignore[reportPrivateUsage]
        )

        for level in (1, 2):
            configs: list[ProofConfig] = []
            for cfg in base:
                if cfg.profile not in ("C", "E"):
                    continue
                parent = replace(cfg, level=level - 1)
                child = replace(cfg, level=level)
                source = parent.directory()
                inherited = (
                    CAMPAIGN / "carried" / f"{parent.identifier()}.json"
                )
                if inherited.exists():
                    source = ROOT / json.loads(inherited.read_text())["source"]
                state = ol.ground_truth(source)
                solved = (
                    state == "done"
                    and _field(_result_head(source / "result.yaml"), "success")
                    == "true"
                )
                if solved:
                    save(
                        f"carried/{child.identifier()}.json",
                        dict(
                            source=str(source.relative_to(ROOT)),
                            reason="Already solved; no restart or charge",
                        ),
                    )
                    continue
                if state == "failed":
                    save(
                        f"carried/{child.identifier()}.json",
                        dict(
                            source=str(source.relative_to(ROOT)),
                            reason="Platform-failed parent retained in denominator",
                        ),
                    )
                    continue
                if not child.snapshots().exists():
                    shutil.copytree(parent.snapshots(), child.snapshots())
                configs.append(child)
            launch(configs, f"headroom{level}")
        save("final_accounting.json", accounting())


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    if command == "prepare":
        prepare()
    elif command == "seal":
        seal()
    elif command == "campaign":
        campaign()
    elif command == "status":
        print(json.dumps(accounting(), indent=2))
    elif command == "run-batch":
        verify()
        filename = sys.argv[2]
        if not filename.startswith("batches/") or ".." in filename:
            raise ValueError("Invalid manifest")
        batch = read(filename)
        if filename != f"batches/{old.fingerprint(batch)[:24]}.json":
            raise ValueError("Manifest drift")
        activate(batch["stage"])
        cls = RoleConfig if batch["kind"] == "role" else ProofConfig
        configs = [cls(**raw) for raw in batch["configs"]]
        sys.argv[:] = [sys.argv[0], *sys.argv[3:]]
        ol.OmphalosExperiment(
            config_class=cls,
            context=context(),
            configs=configs,
            output_dir=batch["output"],
            config_naming=lambda c, _: c.identifier(),
            attempts=1,
            wait_for_slots=True,
            needs_rocq=batch["kind"] == "proof",
        ).run_cli()
    else:
        raise ValueError(command)


if __name__ == "__main__":
    main()
