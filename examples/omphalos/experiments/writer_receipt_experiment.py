"""Final isolated writer contender: known failed receipts may be dropped.

Ten trainX writer cells (8 curators, 2 reducers), seed0, $0.20/cell <=$2.
Reuse the ten fresh baseline and ten draft-v1 cells from the immediately prior
pilot: same input bytes, model, tariff, book, four turns, three probes and
controller. V2 changes receipt disposition/repair feedback only. Historical
cache/order limits remain; this is not a fresh-control or coverage experiment.
Prior cumulative $5.21023244; maximum new cumulative $7.21023244/$30. No
seed extension, retries, generators, embeddings, proof or diagnostic charges.

Retain as exploratory if all ten produce valid outputs, the reducer yields at
least one useful checked correction, useful retained corrections increase over
v1, and cost/useful correction is no worse. Otherwise reject promotion and
record the specific bottleneck. No statistical support or default promotion
from two source batches. Keep all failures; missing/admin cells forbid verdict.
Both harnesses use the same supervised launcher and cumulative ledger.
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

from contextlib import redirect_stdout
from dataclasses import asdict, dataclass, replace
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from delphyne.utils.typing import pydantic_load
import yaml

from experiments import writer_draft_experiment as prior
from experiments import snippet_experiment as old
from experiments.common import omphalos_launch as ol
from prove_snippets import CheckedWriting
from prove_writer_drafts import DraftWriting
from runtime.campaign_budget import CampaignResponsesModel

ROOT = prior.ROOT
CAMPAIGN = prior.CAMPAIGN / "receipt_repair"
OUTPUT = prior.OUTPUT / "receipt_repair"
PREFIX = "writer-receipts-v2__"
PRIOR_COST = 5.21023244


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != text:
            raise ValueError("Frozen artifact changed: " + name)
    else:
        path.write_text(text)


def context() -> dp.ExecutionContext:
    ctx = prior.context()
    return replace(ctx, modules=(*ctx.modules, "prove_writer_receipts"))


def accounting() -> dict[str, Any]:
    all_costs = old.prior.accounting()
    own = {n: v for n, v in all_costs["costs"].items() if n.startswith(PREFIX)}
    return dict(
        cumulative=all_costs["total"],
        new_total=sum(own.values()),
        prior_total=all_costs["total"] - sum(own.values()),
        costs=own,
        tokens={n: t for n, t in all_costs["tokens"].items() if n in own},
        unresolved=all_costs["unresolved"],
        billing_issues=all_costs["billing_issues"],
        ledger=all_costs["ledger"],
        receipts=all_costs["receipts"],
        codex_session_cost=None,
    )


def activate(seed: int = 0, events: bool = True) -> None:
    old.activate("followup", events=False)
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )


@dataclass
class Config:
    bench_name: str
    role: str
    writer_input: str
    input_sha256: str
    arm: str = "receipt"
    seed: int = 0
    dollar_cap: float = 0.20

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        if old.sha(CAMPAIGN / self.writer_input) != self.input_sha256:
            raise ValueError("Input provenance drift")
        return dp.RunStrategyArgs(
            strategy="write_rocq_receipts",
            args=read(self.writer_input),
            policy="draft_writer_policy",
            policy_args=dict(
                snapshot_directory=str(
                    CAMPAIGN / "transport" / name(self, None)
                ),
                dollar_cap=self.dollar_cap,
            ),
            budget=dict(
                price=self.dollar_cap, num_requests=4, rocq_seconds=180
            ),
        )


def name(cfg: Config, _: object) -> str:
    return f"{PREFIX}{cfg.bench_name}__{cfg.role}__seed{cfg.seed}"


def configs(seed: int = 0) -> list[Config]:
    if seed != 0:
        raise ValueError("Only seed0 registered")
    return [Config(**r) for r in read("manifest.json")]


def directory(cfg: Config) -> Path:
    return OUTPUT / "configs" / name(cfg, None)


def cell_result(cfg: Config) -> dict[str, Any] | None:
    path = directory(cfg)
    state = ol.ground_truth(path)
    if state not in ("done", "failed"):
        raise ValueError("Missing required cell: " + name(cfg, None))
    raw: dict[str, Any] = (
        yaml.safe_load((path / "result.yaml").read_text())
        if (path / "result.yaml").exists()
        else {}
    )
    diag = (
        json.dumps(raw.get("outcome", {}).get("diagnostics", []))
        + json.dumps(raw.get("diagnostics", []))
        + "".join(p.read_text() for p in path.glob("exception*.txt"))
    )
    if "CampaignExhausted" in diag:
        raise ValueError("Administratively censored cell: " + name(cfg, None))
    return raw.get("outcome", {}).get("result") if state == "done" else None


def product(cfg: Config) -> CheckedWriting | None:
    out = cell_result(cfg)
    return (
        pydantic_load(DraftWriting, out["values"][0]).checked
        if out and out["success"] and len(out["values"]) == 1
        else None
    )


def prepare() -> None:
    a = accounting()
    if (
        a["new_total"]
        or a["unresolved"]
        or a["billing_issues"]
        or abs(a["prior_total"] - PRIOR_COST) > 1e-8
    ):
        raise ValueError("Initial accounting drift")
    if prior.read("gate_seed0.json")["expand"]:
        raise ValueError(
            "This revision records the original failed expansion gate"
        )
    save("checkpoint.json", a)
    save(
        "protocol.json",
        dict(
            authorization="User's authorized writing-role test; second and final isolated contender after a demonstrated receipt contract defect",
            jobs=10,
            seeds=[0],
            cap_per_job=0.20,
            max_new_spend=2,
            prior_cumulative=PRIOR_COST,
            cumulative_ceiling=30,
            allocation="followup",
            reserve_untouched=4.38640002,
            reused_controls=10,
            reused_v1_contender=10,
            source_generators=0,
            embeddings=0,
            automatic_retries=False,
            paid_diagnostics=0,
            fresh_control_cost=0,
            adaptation_cost="all ten writer jobs included",
            primary="useful checked source corrections retained after deterministic merge",
            retention="all ten valid outputs; reducer >=1 useful correction; total useful > v1; cost/useful <= v1",
            expansion=False,
            default_promotion=False,
            statistical_support=False,
            comparison_limit="immediately preceding historical control; cache/order differences; two source batches, repeated sources clustered",
            scope="trainX only; keep testX/protected evidence closed",
        ),
    )
    save("utility_rubric.json", prior.read("utility_rubric.json"))
    jobs: list[Config] = []
    for cfg in prior.configs(0):
        if cfg.arm != "draft":
            continue
        save(cfg.writer_input, prior.read(cfg.writer_input))
        assert old.sha(CAMPAIGN / cfg.writer_input) == cfg.input_sha256
        jobs.append(
            Config(
                cfg.bench_name, cfg.role, cfg.writer_input, cfg.input_sha256
            )
        )
    save("manifest.json", [asdict(j) for j in jobs])


def seal() -> None:
    if not read("offline_checks.json")["passed"]:
        raise ValueError("Offline checks required")
    paths = [
        Path(__file__),
        ROOT / "prove_writer_receipts.py",
        ROOT / "tests/test_writer_receipts.py",
        ROOT / "tools/reports/writer_receipt_results.py",
    ]
    paths += list(
        (ROOT / "prompts/ace/adaptation").glob("WriteRocqReceiptAdvice.*")
    )
    paths += list(CAMPAIGN.glob("inputs/*.json")) + [
        CAMPAIGN / n
        for n in (
            "protocol.json",
            "manifest.json",
            "utility_rubric.json",
            "checkpoint.json",
            "offline_checks.json",
        )
    ]
    files = dict(prior.read("seal.json")["files"])
    files.update({str(p.relative_to(ROOT)): old.sha(p) for p in paths})
    save("seal.json", dict(files=files))


def verify() -> None:
    for p, expected in read("seal.json")["files"].items():
        if old.sha(ROOT / p) != expected:
            raise ValueError("Source seal drift: " + p)
    a = accounting()
    if (
        a["unresolved"]
        or a["billing_issues"]
        or abs(a["prior_total"] - PRIOR_COST) > 1e-8
        or a["new_total"] > 2 + 1e-8
        or a["cumulative"] > 30 + 1e-8
    ):
        raise ValueError("Accounting issue")


def run_batch() -> None:
    verify()
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher lacks credential")
    activate()
    ol.OmphalosExperiment(
        config_class=Config,
        configs=configs(),
        context=context(),
        output_dir=str(OUTPUT.relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def launch() -> None:
    verify()
    ledger = accounting()["ledger"]
    used = sum(
        r["dollars"] for r in ledger["groups"] if r["stage"] == "followup"
    )
    needed = sum(
        c.dollar_cap
        for c in configs()
        if ol.ground_truth(directory(c)) not in ("done", "failed")
    )
    if used + needed > ledger["allocations"]["followup"] + 1e-8:
        raise ValueError("Whole required panel does not fit allocation")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.writer_receipt_experiment",
            "run-batch",
            "run",
            "--max_workers=8",
            "--wait",
        ],
        cwd=ROOT,
        check=False,
    )
    for cfg in configs():
        cell_result(cfg)
    verify()
    save(
        "batch.json",
        dict(
            exit_code=result.returncode,
            states={
                name(c, None): ol.ground_truth(directory(c)) for c in configs()
            },
        ),
    )


def replay(seed: int = 0) -> None:
    before = accounting()["receipts"]
    activate(events=False)
    rows: list[dict[str, Any]] = []
    for cfg in configs(seed):
        original = cell_result(cfg)
        if original is None:
            rows.append(dict(cell=name(cfg, None), platform_failed=True))
            continue
        args = cfg.instantiate(None)
        args.cache_mode, args.cache_file = (
            "replay",
            str(directory(cfg) / "cache.yaml"),
        )
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        with (
            patch.object(
                CampaignResponsesModel,
                "_send_final_request",
                side_effect=AssertionError("HTTP forbidden"),
            ),
            redirect_stdout(io.StringIO()),
        ):
            out = run_command(
                run_strategy,
                args,
                ctx=replace(context(), cache_root=Path("/")),
                add_header=False,
            )
        if (
            out.result is None
            or out.result.success != original["success"]
            or out.result.spent_budget != original["spent_budget"]
            or json.loads(json.dumps(list(out.result.values)))
            != original["values"]
        ):
            raise ValueError("Exact replay mismatch: " + name(cfg, None))
        rows.append(
            dict(
                cell=name(cfg, None),
                passed=True,
                cache_sha256=old.sha(directory(cfg) / "cache.yaml"),
            )
        )
    assert before == accounting()["receipts"]
    save("replay.json", dict(passed=True, paid_requests=0, cells=rows))


if __name__ == "__main__":
    command = sys.argv.pop(1)
    {
        "prepare": prepare,
        "seal": seal,
        "campaign": launch,
        "run-batch": run_batch,
        "replay": replay,
    }[command]()
