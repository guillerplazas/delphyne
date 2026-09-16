"""ACE cost target and advisor controls, registered before paid dispatch.

Authorization: Guille, 2026-09-16, $50 NEW experimental API ceiling. Only
validationX and testX. No new adaptation or training; reuse the frozen v2
book af399ace... from ace_revision_20260913 without repairing it in place.

Objective 1: contemporary paired empty-book agentic versus v2 ACE, same
Luna-medium model, core tools, focused verifier, definitions, 64 requests,
300 verifier seconds, $.10 cap and 32768-token output reservation. Only
the playbook differs. 40 validationX theorems x 2 replicates x 2 arms =
160 fresh cells. Then exactly one testX replicate per headline arm (80
cells). These reused partitions are not newly unseen held-out evidence.

Objective 2: three separate advisor interventions against that same ACE:
budget (.20 instead of .10); session (one reset after >=8 interactions and
>=24000 visible history chars, retaining last two groups and last checked
proposal); views (4096 instead of 8192 bytes for tool/feedback displays).
Each gets 40 validationX theorems x 2 replicates = 80 fresh cells. No
combination, extra seeds or sweeps. Study static instructions, schemas,
skills and output lengths offline. Full generated proofs remain uncut.

Primary goal: >=10% total inference saving, no fewer qualified solves on
either validation replicate, and no lower overall test coverage. Report
cost/solve, paired cost differences, two-sided p<.10 and family-clustered
90% CIs; observed preservation does not establish statistical equivalence.
Practical treatment selection: either the savings criterion above, or
>=2 extra validation solves, no per-replicate loss and cost/solve <=1.25
reference. Choose highest coverage, then lower cost. At most one treatment
gets testX (40 more cells), with all choices frozen before test outcomes.
All individual interventions remain exploratory; no default promotion.

Budget is a ceiling, not a target. Worst-case nominal remaining batch
liability plus $16 reserved for test must fit $50 before advisor dispatch.
The shared ledger reserves each HTTP upper bound, includes retries and
retains unknown charges. One supervised attempt; no automatic paid reruns.
Every expected cell is required. Infrastructure failures stay denominator;
missing/administratively censored cells or unresolved billing forbid verdicts.
Preparation is reported separately (historical X3 >=$.91692376 plus v2
$.45092992, embeddings excluded). Report uncached same-token sensitivity.
Both harnesses run this module; long paid batches use tmux.
"""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys
from typing import Any

import delphyne as dp
import yaml

from ace.ace_playbook import Playbook
from experiments.common import omphalos_launch as ol
from experiments.common.ace_learning_io import accounting as ledger_accounting
from runtime.campaign_budget import Ledger
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile

NAME = "ace_economy_20260916"
CAMPAIGN = ROOT / "experiments/campaigns" / NAME
OUTPUT = ROOT / "experiments/output" / NAME
PRIOR = ROOT / "experiments/campaigns/ace_revision_20260913"
BOOK_SHA = "af399ace24aab264c2305deab106774d7c93dab58b1a2b42e7e7b81db3817498"
ARMS = ("agentic", "ace", "budget", "session", "views")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    encoded = json.dumps(value, sort_keys=True, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_text() != encoded:
            raise ValueError("Immutable artifact changed: " + name)
    else:
        path.write_text(encoded)


def partition(stage: str) -> dict[str, str]:
    if stage not in ("validation", "test"):
        raise ValueError("Only validationX and testX are authorized")
    rows = [
        s.strip()
        for s in (ROOT / "benchmarks" / f"{stage}X.txt")
        .read_text()
        .splitlines()
        if s.strip() and not s.startswith("#")
    ]
    result = {Path(s).stem: s for s in rows}
    if len(result) != 40 or len(rows) != 40:
        raise ValueError("Partition must contain exactly 40 unique theorems")
    return result


def families(stage: str) -> dict[str, str]:
    from runtime.pytanque_utils import parse_problem

    problems = partition(stage)
    parent = {n: n for n in problems}

    def find(n: str) -> str:
        while parent[n] != n:
            n = parent[n]
        return n

    templates: dict[str, str] = {}
    for name, file in sorted(problems.items()):
        statement = re.sub(
            r"\b\d+\b",
            "NUMBER",
            " ".join(parse_problem(file, True).theorem_statement.split()),
        )
        keys = [statement]
        if name.startswith(("imo_", "aime_", "amc")):
            keys.append(re.sub(r"(_p\d+)_\d+$", r"\1", name))
        for key in keys:
            if key in templates:
                parent[find(name)] = find(templates[key])
            else:
                templates[key] = name
    return {n: find(n) for n in problems}


def context() -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    return replace(ctx, modules=(*ctx.modules, "prove_economy"))


@dataclass(frozen=True)
class Config:
    stage: str
    arm: str
    bench_name: str
    seed: int

    @property
    def cap(self) -> float:
        return 0.20 if self.arm == "budget" else 0.10

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        if self.arm not in ARMS or self.seed not in (
            (0, 1) if self.stage == "validation" else (0,)
        ):
            raise ValueError("Unregistered arm or replicate")
        problems = partition(self.stage)
        if self.bench_name not in problems:
            raise ValueError("Theorem is outside the authorized partition")
        if (
            self.stage == "test"
            and self.arm not in read("selection.json")["test_arms"]
        ):
            raise ValueError("Test arm was not frozen")
        book = CAMPAIGN / "book.yaml"
        if sha(book) != BOOK_SHA:
            raise ValueError("Frozen v2 book changed")
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        return dp.RunStrategyArgs(
            strategy="prove_theorem_grounded",
            args=dict(
                problem_file=problems[self.bench_name],
                theorem_name=self.bench_name,
                playbook=""
                if self.arm == "agentic"
                else Playbook.load(book).render_prompt(),
                claims=[],
                turn_budget=64,
                limits=dict(
                    seconds=60,
                    rpc_calls=512,
                    view_bytes=4096 if self.arm == "views" else 8192,
                ),
                verifier_seconds=300,
                admission=False,
                focused=True,
                restart=False,
            ),
            policy="economy_proof_policy",
            policy_args=dict(
                snapshot_directory=str(
                    CAMPAIGN / "transport" / name(self, None)
                ),
                pause_file=str(CAMPAIGN / "PAUSED"),
                dollar_cap=self.cap,
                split_session=self.arm == "session",
            ),
            budget=dict(price=self.cap, num_requests=64, rocq_seconds=300),
        )


def name(config: Config, _: object) -> str:
    return (
        f"{config.stage}__{config.arm}__{config.bench_name}__seed{config.seed}"
    )


def directory(config: Config) -> Path:
    return OUTPUT / config.stage / "configs" / name(config, None)


def configs(key: str) -> list[Config]:
    return [Config(**v) for v in read(f"manifests/{key}.json")]


def accounting() -> dict[str, Any]:
    return ledger_accounting(CAMPAIGN)


def activate(*, events: bool = True) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ.update(
        OMPHALOS_CAMPAIGN_LEDGER=str(CAMPAIGN / "ledger.sqlite3"),
        OMPHALOS_CAMPAIGN_STAGE="experiments",
        OMPHALOS_ESTIMATE_DOLLARS="1",
    )
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )
    else:
        os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)


def source_paths() -> list[Path]:
    paths = [
        ROOT / "delphyne.yaml",
        Path(__file__),
        ROOT / "prove_economy.py",
        ROOT / "tools/reports/ace_economy_results.py",
        ROOT / "tests/test_ace_economy.py",
        ROOT / "runtime/runtime_profiles.py",
        ROOT / "experiments/common/omphalos_launch.py",
        ROOT / "experiments/common/ace_learning_io.py",
        CAMPAIGN / "book.yaml",
        CAMPAIGN / "runtime.json",
        CAMPAIGN / "protocol.json",
    ]
    paths.extend(ROOT.glob("prove_*.py"))
    for folder, pattern in (
        ("ace", "*.py"),
        ("runtime", "*.py"),
        ("prompts", "*.jinja"),
        ("demos", "*.yaml"),
    ):
        paths.extend((ROOT / folder).rglob(pattern))
    for stage in ("validation", "test"):
        paths.append(ROOT / "benchmarks" / f"{stage}X.txt")
        paths.extend(ROOT / p for p in partition(stage).values())
    return sorted(set(paths))


def prepare() -> None:
    if (CAMPAIGN / "seal.json").exists():
        verify()
        return
    if sha(PRIOR / "book.yaml") != BOOK_SHA:
        raise ValueError("Reference book mismatch")
    save(
        "authorization.json",
        dict(
            date="2026-09-16",
            ceiling_usd=50,
            partitions=["validationX", "testX"],
            previous_testX_closure="Explicitly superseded for this campaign by the current user instruction",
            commits_authorized=True,
            no_new_adaptation=True,
        ),
    )
    (CAMPAIGN / "book.yaml").write_bytes((PRIOR / "book.yaml").read_bytes())
    save("runtime.json", json.loads((PRIOR / "runtime.json").read_text()))
    save(
        "protocol.json",
        dict(
            protocol=__doc__,
            arms=list(ARMS),
            validation_replicates=[0, 1],
            test_replicates=[0],
            max_cells=520,
            model="gpt-5.6-luna",
            reasoning_effort="medium",
            book_sha256=BOOK_SHA,
            initial_preparation_lower_bound=0.91692376,
            v2_preparation=0.45092992,
            known_book_limit="v2 retains the previously documented closed-cast recipe defect; no new book repair is mixed into this comparison",
            created=datetime.now(timezone.utc).isoformat(),
            git_head=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
        ),
    )
    Ledger(CAMPAIGN / "ledger.sqlite3").create(50, {"experiments": 50})
    save(
        "seal.json", {str(p.relative_to(ROOT)): sha(p) for p in source_paths()}
    )


def verify() -> None:
    for file, digest in read("seal.json").items():
        if sha(ROOT / file) != digest:
            raise ValueError("Source/input drift: " + file)


def cell_result(config: Config) -> dict[str, Any] | None:
    folder = directory(config)
    state = ol.ground_truth(folder)
    if state not in ("done", "failed"):
        raise ValueError("Missing required cell: " + name(config, None))
    raw: dict[str, Any] = (
        yaml.safe_load((folder / "result.yaml").read_text())
        if (folder / "result.yaml").exists()
        else {}
    )
    diagnostics = (
        str(raw.get("diagnostics", ""))
        + str(raw.get("outcome", {}).get("diagnostics", ""))
        + "".join(p.read_text() for p in folder.glob("exception*.txt"))
    )
    if any(
        tag in diagnostics for tag in ("CampaignExhausted", "CampaignPaused")
    ):
        raise ValueError("Administrative censoring: " + name(config, None))
    return raw.get("outcome", {}).get("result") if state == "done" else None


def launch(key: str, jobs: list[Config]) -> None:
    verify()
    if (CAMPAIGN / f"batches/{key}.json").exists():
        return
    state = accounting()
    if state["unresolved"] or state["billing_issues"]:
        raise ValueError("Reconcile billing before dispatch")
    needed = sum(
        c.cap
        for c in jobs
        if ol.ground_truth(directory(c)) not in ("done", "failed")
    )
    reserve = 16 if key != "test" else 0
    if state["ledger"]["liability"] + needed + reserve > 50 + 1e-8:
        raise ValueError(
            "Full batch and test reserve exceed remaining ceiling"
        )
    save(f"manifests/{key}.json", [asdict(c) for c in jobs])
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.ace_economy_experiment",
            "run-batch",
            key,
            "run",
            "--max_workers=24",
            "--wait",
        ],
        cwd=ROOT,
        check=False,
    )
    for c in jobs:
        cell_result(c)
    verify()
    save(
        f"batches/{key}.json",
        dict(
            exit_code=completed.returncode,
            states={
                name(c, None): ol.ground_truth(directory(c)) for c in jobs
            },
        ),
    )


def jobs_for(stage: str, arms: tuple[str, ...]) -> list[Config]:
    jobs = [
        Config(stage, arm, n, seed)
        for seed in ((0, 1) if stage == "validation" else (0,))
        for n in partition(stage)
        for arm in arms
    ]
    random.Random(202609160 if stage == "validation" else 202609161).shuffle(
        jobs
    )
    return jobs


def run_batch(key: str) -> None:
    verify()
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher lacks credential")
    jobs = configs(key)
    activate()
    ol.OmphalosExperiment(
        config_class=Config,
        configs=jobs,
        context=context(),
        output_dir=str((OUTPUT / jobs[0].stage).relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "prepare | baseline | advisors | select | test | report | replay | status"
        )
    action = sys.argv.pop(1)
    if action == "prepare":
        prepare()
    elif action == "run-batch":
        run_batch(sys.argv.pop(1))
    elif action == "baseline":
        launch("baseline", jobs_for("validation", ("agentic", "ace")))
    elif action == "advisors":
        if not (CAMPAIGN / "batches/baseline.json").exists():
            raise ValueError("Complete primary assessment first")
        for arm in ("budget", "session", "views"):
            launch(arm, jobs_for("validation", (arm,)))
    elif action == "test":
        launch(
            "test",
            jobs_for("test", tuple(read("selection.json")["test_arms"])),
        )
    elif action == "status":
        print(json.dumps(accounting()["ledger"], indent=2))
    elif action in ("select", "report", "replay"):
        from tools.reports import ace_economy_results as reports

        getattr(reports, action)()
    else:
        raise SystemExit("Unknown action")


if __name__ == "__main__":
    main()
