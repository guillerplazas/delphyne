"""Authorized Rocq snippet campaign; same cumulative $30, no closed data.

A = flagship + snippet tool/demos, fixed book. B = A + checked targeted book.
18 writer jobs <=$2; 20 trainX/arm <=$4; 40 validationX/arm <=$8;
one winner + fresh incumbent, 40 validationX each seed1 <=$8; reserve
$4.38640002. Prior settled cost $3.61359998 remains in the SAME $30 ledger.
No embeddings, source generators, automatic retries or paid diagnostics.

Training gates require actual tool exposure (A), completed checked writing
and new advice in dispatched prompts (B). B requires A as validation control.
Follow-up: >=1 extra solve at all-in cost ratio <=1.25 OR <=1 lost solve
at ratio <=.90; compare to incumbent, include B preparation once. Rank
coverage, all-in cost/solve, cost, then A. Final 80-cell gates scale to 2;
fresh seed1 must not be worse in both cost and coverage. No default promotion.
Report all three initial contrasts, Holm correction, family clusters,
two-sided p<.10 / 90% intervals. ValidationX is reused development data.
Missing/admin-censored required cells or unknown billing block verdicts.

Both harnesses: prepare, preflight, seal, campaign, report, status.
Only run-batch dispatches, through OmphalosExperiment and budget streams.
"""

# ruff: noqa: E402 -- scope before experiment imports
from runtime.snippet_scope import install

install()

from contextlib import redirect_stdout
from dataclasses import asdict, dataclass, replace
import csv
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from typing import Any
from unittest.mock import patch

import delphyne as dp
from delphyne.stdlib.commands.run_strategy import run_strategy
from delphyne.stdlib.tasks import run_command
from delphyne.utils.typing import pydantic_load
import yaml

from ace.ace_playbook import Playbook, merge
from ace.rocq_snippets import SnippetContext, context_for
from ace.terminal_evidence import extract_terminal_evidence
from experiments.ace import ace_attribution_experiment as base
from experiments.ace.ace_adaptation import extract_trajectory
from experiments import resource_completion_experiment as prior
from experiments.common import omphalos_launch as ol
from experiments.coverage_cycle_experiment import family_map, partition
from prove_snippets import CheckedWriting
from runtime.campaign_budget import CampaignResponsesModel, Ledger
from runtime.paths import OMPHALOS_ROOT as ROOT
from runtime.runtime_profiles import RuntimeProfile
from tools.analysis.paired_evaluation import (
    Observation,
    compare,
    cost_cluster_p,
)

CAMPAIGN = ROOT / "experiments/campaigns/ace_snippets_20260913"
OUTPUT = ROOT / "experiments/output/ace_snippets_20260913"
LEDGER = prior.CAMPAIGN / "ledger.sqlite3"
PRIOR_COST = 3.61359998
SOURCES = (
    "aime_1984_p1",
    "amc12_2000_p1",
    "amc12a_2020_p13",
    "amc12b_2004_p3",
    "imo_1968_p5_1",
    "mathd_algebra_224",
    "mathd_algebra_28",
    "mathd_numbertheory_629",
)
COMPARATORS = ("mathd_algebra_323", "amc12b_2002_p11", "mathd_numbertheory_42")


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != text:
            raise ValueError(f"Frozen artifact changed: {name}")
    else:
        with path.open("x") as stream:
            stream.write(text)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context() -> dp.ExecutionContext:
    ctx = dp.workspace_execution_context(__file__)
    return replace(
        ctx,
        modules=(*ctx.modules, "prove_snippets", "prove_evidence"),
        demo_files=(*ctx.demo_files, ROOT / "demos/snippets.demo.yaml"),
    )


def accounting() -> dict[str, Any]:
    all_costs = prior.accounting()
    own = {
        n: c
        for n, c in all_costs["costs"].items()
        if n.startswith("snippets-v1__")
    }
    return dict(
        cumulative=all_costs["total"],
        new_total=sum(own.values()),
        costs=own,
        prior_total=all_costs["total"] - sum(own.values()),
        tokens={n: t for n, t in all_costs["tokens"].items() if n in own},
        unresolved=all_costs["unresolved"],
        billing_issues=all_costs["billing_issues"],
        receipts=all_costs["receipts"],
        ledger=all_costs["ledger"],
        codex_session_cost=None,
    )


def activate(stage: str, events: bool = True) -> None:
    RuntimeProfile.load(CAMPAIGN / "runtime.json").activate()
    os.environ["OMPHALOS_CAMPAIGN_LEDGER"] = str(LEDGER)
    os.environ["OMPHALOS_CAMPAIGN_STAGE"] = (
        "training" if stage == "writing" else stage
    )
    os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "1"
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )
    else:
        os.environ.pop("OMPHALOS_ADMISSION_EVENTS", None)


@dataclass
class Config:
    bench_name: str
    stage: str
    arm: str
    seed: int = 0
    writer_input: str = ""
    role: str = ""
    dollar_cap: float = 0.10
    input_sha256: str = ""

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        policy_args: dict[str, object] = dict(
            snapshot_directory=str(CAMPAIGN / "transport" / name(self, None)),
            role="proof" if self.stage != "writing" else self.role,
            dollar_cap=self.dollar_cap,
        )
        if self.stage == "writing":
            if sha(CAMPAIGN / self.writer_input) != self.input_sha256:
                raise ValueError("Writer input/provenance drift")
            item = read(self.writer_input)
            if item["role"] != self.role or self.role not in (
                "reflector",
                "curator",
                "reducer",
            ):
                raise ValueError("Writer identity mismatch")
            return dp.RunStrategyArgs(
                strategy="write_checked_rocq_advice",
                args=item,
                policy="snippet_policy",
                policy_args=policy_args,
                budget=dict(
                    price=self.dollar_cap, num_requests=4, rocq_seconds=180
                ),
            )
        part = "training" if self.stage == "training" else "validation"
        if self.bench_name not in partition(part) or self.arm not in (
            "A",
            "B",
            "reference",
        ):
            raise ValueError("Unregistered proof")
        if self.seed != (1 if self.stage == "followup" else 0):
            raise ValueError("Unregistered seed")
        args = base.proof(part, "luna-ace", self.bench_name).instantiate(None)
        # The reference factory sets its own legacy name during construction.
        # Restore this campaign's logical cell before the policy is loaded.
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        args.policy, args.policy_args = "snippet_policy", policy_args
        if self.arm != "reference":
            args.args["snippet_tools"] = True
        if self.arm == "B":
            book = Playbook.load(CAMPAIGN / "book.yaml")
            if book.sha256() != read("book.json")["sha256"]:
                raise ValueError("Candidate book drift")
            args.args["playbook"] = book.render_prompt()
        return args


def name(cfg: Config, _: object) -> str:
    return (
        f"snippets-v1__{cfg.bench_name}__{cfg.stage}-{cfg.arm}__seed{cfg.seed}"
    )


def directory(cfg: Config) -> Path:
    return OUTPUT / cfg.stage / "configs" / name(cfg, None)


def cell_result(cfg: Config) -> dict[str, Any] | None:
    """Require a terminal cell; distinguish platform loss from censoring."""
    path = directory(cfg)
    state = ol.ground_truth(path)
    if state not in ("done", "failed"):
        raise ValueError("Missing required cell: " + name(cfg, None))
    raw: dict[str, Any] = {}
    result_file = path / "result.yaml"
    if result_file.exists():
        raw = yaml.load(result_file.read_text(), Loader=yaml.CSafeLoader)
    diagnostics = json.dumps(raw.get("outcome", {}).get("diagnostics", []))
    diagnostics += json.dumps(raw.get("diagnostics", []))
    diagnostics += "".join(p.read_text() for p in path.glob("exception*.txt"))
    if "CampaignExhausted" in diagnostics:
        raise ValueError("Administratively censored cell: " + name(cfg, None))
    return raw.get("outcome", {}).get("result") if state == "done" else None


def prepare() -> None:
    if accounting()["new_total"]:
        raise ValueError("Preparation must precede new payment")
    diags = base.read("complete_diagnostics.json")
    syntax = sorted(
        k.rsplit("/", 1)[-1]
        for k, v in diags.items()
        if k.startswith("training/luna-ace/")
        and any(c["category"] == "syntax-error" for c in v["checks"])
    )
    training = sorted([*syntax, *COMPARATORS])
    assert len(syntax) == 17 and len(set(training)) == 20
    refs = base.read("references.json")
    save(
        "references.json",
        {
            s: [
                r
                for r in rows
                if s == "validation" or r["theorem"] in training
            ]
            for s, rows in refs.items()
        },
    )
    save("runtime.json", prior.read("runtime.json"))
    save(
        "protocol.json",
        dict(
            authorization="Guille: Implement the plan (Rocq snippets)",
            version=1,
            prior_cost=PRIOR_COST,
            cumulative_ceiling=30,
            remaining=30 - PRIOR_COST,
            allocations=dict(
                writing=2,
                training=4,
                validation=8,
                followup=8,
                contingency=4.38640002,
            ),
            sources=list(SOURCES),
            training=training,
            validation=sorted(partition("validation")),
            families=family_map(),
            source_book=base.BOOK,
            source_book_sha256=base.BOOK_SHA,
            source_generators=0,
            embeddings=0,
            paid_diagnostics=0,
            writer_jobs=18,
            alpha=0.10,
            confidence=0.90,
            contrasts=["A/reference", "B/A", "B/reference"],
            writing_context_selection="initial, first four distinct syntax-failure prefixes, terminal prefix",
            writing_requests=4,
            writing_probes=3,
            writing_output_limit=8192,
            proof_requests=64,
            proof_probes=4,
            proof_output_limit=32768,
            retry_limit=4,
            retries_per_cell=1,
            automatic_retries=False,
            validation_gate="actual A snippet execution OR completed B book exposed in training; B requires A control",
            expansion_gate="gain>=1 and all-in ratio<=1.25 OR loss<=1 and all-in ratio<=.90",
            retention_gate="scaled 80-cell gate; fresh seed1 not worse in both cost and coverage",
            promotion=False,
            selection=["coverage", "all-in cost/solve", "all-in cost", "A"],
        ),
    )
    save("prior_checkpoint.json", accounting())
    for theorem in SOURCES:
        diag = diags["training/luna-ace/" + theorem]
        source = ROOT / diag["source"]
        terminal = extract_terminal_evidence(source, theorem)
        contexts: dict[str, SnippetContext] = {}
        prefixes: list[tuple[str, ...]] = [()]
        for c in diag["checks"]:
            prefix = tuple(c["verified_prefix"])
            if (
                c["category"] == "syntax-error"
                and prefix not in prefixes
                and len(prefixes) < 5
            ):
                prefixes.append(prefix)
        if diag["checks"]:
            prefixes.append(tuple(diag["checks"][-1]["verified_prefix"]))
        for prefix in prefixes:
            c = context_for(
                partition("training")[theorem],
                theorem,
                prefix,
                terminal.check_sha256,
            )
            contexts[c.identifier] = c
        save(
            f"sources/{theorem}.json",
            dict(
                contexts=[asdict(c) for c in contexts.values()],
                evidence=extract_trajectory(source, theorem)
                + "\n\nAUTHORITATIVE TERMINAL RECEIPT:\n"
                + terminal.render(),
                source=diag["source"],
                cache_sha256=sha(source / "cache.yaml"),
                result_sha256=sha(source / "result.yaml"),
                terminal=asdict(terminal),
            ),
        )
    print(
        "Prepared 60 historical references, 8 writer sources; no payment",
        flush=True,
    )


def preflight() -> None:
    activate("training", events=False)
    original = base.read("preflight.json")["cells"]
    permitted = {
        r["name"] for rows in read("references.json").values() for r in rows
    }
    rows: list[dict[str, Any]] = []
    before = accounting()["receipts"]
    for ref in original:
        if ref["name"] not in permitted:
            continue
        args = base.proof(
            ref["partition"], "luna-ace", ref["theorem"]
        ).instantiate(None)
        path = ROOT / ref["source"] / "configs" / ref["name"]
        args.cache_mode, args.cache_file = "replay", str(path / "cache.yaml")
        args.export_raw_trace = args.export_browsable_trace = (
            args.export_log
        ) = False
        args.budget["num_requests"] = ref["requests"]
        os.environ["OMPHALOS_ESTIMATE_DOLLARS"] = "0"
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
            or out.result.success != ref["success"]
            or out.result.spent_budget.get("num_completions", 0)
            != ref["requests"]
        ):
            raise ValueError((ref["name"], out.diagnostics))
        rows.append(
            dict(
                name=ref["name"],
                success=out.result.success,
                requests=ref["requests"],
                cache_sha256=sha(path / "cache.yaml"),
                result_sha256=sha(path / "result.yaml"),
            )
        )
        if len(rows) % 10 == 0:
            print(f"Historical prompt replay {len(rows)}/60", flush=True)
    assert len(rows) == 60 and accounting()["receipts"] == before
    save(
        "preflight.json",
        dict(
            passed=True,
            cells=rows,
            paid_requests=0,
            limitation="Observed-request replay; historical terminal admission is not reconstructed",
        ),
    )


def seal() -> None:
    assert (
        read("preflight.json")["passed"]
        and read("offline_checks.json")["passed"]
    )
    paths = [
        ROOT / "prove_grounded.py",
        ROOT / "prove_snippets.py",
        Path(__file__),
        ROOT / "demos/snippets.demo.yaml",
        ROOT / "tools/data/snippet_demos.py",
        ROOT / "tools/reports/snippet_checks.py",
        ROOT / "tests/test_snippet_tool.py",
        CAMPAIGN / "README.md",
        ROOT / base.BOOK,
    ]
    for folder in (
        "ace",
        "runtime",
        "prompts/grounded",
        "prompts/ace",
        "prompts/baselines",
    ):
        paths += [
            p
            for p in (ROOT / folder).rglob("*")
            if p.suffix in (".py", ".jinja")
        ]
    paths += list((CAMPAIGN / "sources").glob("*.json"))
    paths += [
        CAMPAIGN / n
        for n in (
            "protocol.json",
            "runtime.json",
            "references.json",
            "preflight.json",
            "offline_checks.json",
        )
    ]
    save(
        "seal.json",
        {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))},
    )


def verify() -> None:
    for path, digest in read("seal.json").items():
        if sha(ROOT / path) != digest:
            raise ValueError("Sealed input drift: " + path)
    acct = accounting()
    if (
        acct["unresolved"]
        or acct["billing_issues"]
        or abs(acct["prior_total"] - PRIOR_COST) > 1e-8
    ):
        raise ValueError("Unresolved or changed cumulative billing")


def allocate() -> None:
    verify()
    ledger = Ledger(LEDGER)
    target = dict(
        training=7.74751532,
        validation=9.86608466,
        followup=8.0,
        contingency=4.38640002,
    )
    # Existing atomic transfers retain the original ceiling and liabilities.
    current = accounting()["ledger"]["allocations"]
    if current["training"] > target["training"] + 1e-8:
        ledger.transfer(
            "training",
            "contingency",
            current["training"] - target["training"],
            "Authorized snippet campaign allocation",
        )
    current = accounting()["ledger"]["allocations"]
    if current["validation"] < target["validation"] - 1e-8:
        ledger.transfer(
            "contingency",
            "validation",
            target["validation"] - current["validation"],
            "Authorized snippet validation allocation",
        )
    current = accounting()["ledger"]["allocations"]
    assert all(abs(current[k] - v) < 1e-8 for k, v in target.items())
    save(
        "allocation.json",
        dict(allocations=target, cumulative_ceiling=30, prior_cost=PRIOR_COST),
    )


def configs(key: str) -> list[Config]:
    return [Config(**c) for c in read(f"manifests/{key}.json")]


def launch(key: str, batch: list[Config]) -> None:
    save(f"manifests/{key}.json", [asdict(c) for c in batch])
    if (CAMPAIGN / f"batches/{key}.json").exists():
        replay_batch(key)
        return
    verify()
    stage = "training" if batch[0].stage == "writing" else batch[0].stage
    ledger = accounting()["ledger"]
    used = sum(r["dollars"] for r in ledger["groups"] if r["stage"] == stage)
    needed = sum(
        c.dollar_cap
        for c in batch
        if ol.ground_truth(directory(c)) not in ("done", "failed")
    )
    if used + needed > ledger["allocations"][stage] + 1e-8:
        raise ValueError(
            "Whole remaining batch does not fit its reservation allocation"
        )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.snippet_experiment",
            "run-batch",
            key,
            "run",
            "--max_workers=24",
            "--wait",
        ],
        cwd=ROOT,
        check=False,
    )
    states = {name(c, None): ol.ground_truth(directory(c)) for c in batch}
    if any(s not in ("done", "failed") for s in states.values()):
        raise ValueError("Missing/administratively censored required cells")
    verify()
    save(
        f"batches/{key}.json", dict(exit_code=result.returncode, states=states)
    )
    replay_batch(key)


def run_batch(key: str) -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher environment lacks the API credential")
    verify()
    batch = configs(key)
    if len({c.stage for c in batch}) != 1:
        raise ValueError("Mixed launcher stages")
    activate(batch[0].stage)
    ol.OmphalosExperiment(
        config_class=Config,
        configs=batch,
        context=context(),
        output_dir=str((OUTPUT / batch[0].stage).relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def replay_batch(key: str) -> None:
    artifact = f"replays/{key}.json"
    if (CAMPAIGN / artifact).exists():
        return
    before = accounting()["receipts"]
    rows: list[dict[str, Any]] = []
    batch = configs(key)
    activate(batch[0].stage, events=False)
    for cfg in batch:
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
            # RunStrategy's Python values may retain tuples; YAML encodes
            # them as lists. Compare the same JSON/YAML representation.
            or json.loads(json.dumps(list(out.result.values)))
            != original["values"]
        ):
            raise ValueError(
                "Exact transport/controller replay mismatch: "
                + name(cfg, None)
            )
        rows.append(
            dict(
                cell=name(cfg, None),
                success=out.result.success,
                cache_sha256=sha(directory(cfg) / "cache.yaml"),
            )
        )
    assert before == accounting()["receipts"]
    save(artifact, dict(passed=True, paid_requests=0, cells=rows))


def product(cfg: Config) -> CheckedWriting | None:
    out = cell_result(cfg)
    if out is None or not out["success"] or len(out["values"]) != 1:
        return None
    return pydantic_load(CheckedWriting, out["values"][0])


def writing() -> bool:
    if (CAMPAIGN / "book.json").exists():
        return bool(read("book.json")["changed"])
    book = Playbook.load(ROOT / base.BOOK)
    for batch_no in range(2):
        names = SOURCES[batch_no * 4 : batch_no * 4 + 4]
        products: list[CheckedWriting] = []
        for role in ("reflector", "curator"):
            jobs: list[Config] = []
            for i, theorem in enumerate(names):
                source = read(f"sources/{theorem}.json")
                inherited = products[i] if role == "curator" else None
                kept = (
                    [
                        r
                        for r in inherited.receipts
                        if r.identifier in inherited.answer.retained_receipts
                    ]
                    if inherited
                    else []
                )
                bank = {
                    pydantic_load(SnippetContext, c).identifier: c
                    for c in source["contexts"]
                }
                for r in kept:
                    bank[r.context.identifier] = asdict(r.context)
                path = f"writing_inputs/{batch_no}_{role}_{theorem}.json"
                save(
                    path,
                    dict(
                        role=role,
                        evidence=source["evidence"]
                        if not inherited
                        else json.dumps(asdict(inherited.answer)),
                        playbook=book.render_prompt(),
                        contexts=list(bank.values()),
                        receipts=[asdict(r) for r in kept],
                    ),
                )
                jobs.append(
                    Config(
                        theorem,
                        "writing",
                        f"{batch_no}-{role}",
                        writer_input=path,
                        role=role,
                        input_sha256=sha(CAMPAIGN / path),
                    )
                )
            launch(f"writing_{batch_no}_{role}", jobs)
            results = [product(c) for c in jobs]
            if any(r is None for r in results):
                save(
                    "writing_stop.json",
                    dict(
                        batch=batch_no,
                        role=role,
                        reason="Required writer output absent; no B verdict",
                    ),
                )
                return False
            products = [r for r in results if r is not None]
        kept_bank = {
            r.identifier: r
            for p in products
            for r in p.receipts
            if r.identifier in p.answer.retained_receipts
        }
        contexts = {
            r.context.identifier: r.context for r in kept_bank.values()
        }
        for theorem in names:
            for raw in read(f"sources/{theorem}.json")["contexts"]:
                c = pydantic_load(SnippetContext, raw)
                contexts[c.identifier] = c
        path = f"writing_inputs/{batch_no}_reducer.json"
        save(
            path,
            dict(
                role="reducer",
                evidence=json.dumps([asdict(p.answer) for p in products]),
                playbook=book.render_prompt(),
                contexts=[asdict(c) for c in contexts.values()],
                receipts=[asdict(r) for r in kept_bank.values()],
            ),
        )
        job = Config(
            names[0],
            "writing",
            f"{batch_no}-reducer",
            writer_input=path,
            role="reducer",
            dollar_cap=0.2,
            input_sha256=sha(CAMPAIGN / path),
        )
        launch(f"writing_{batch_no}_reducer", [job])
        reduced = product(job)
        if reduced is None:
            save(
                "writing_stop.json",
                dict(
                    batch=batch_no,
                    role="reducer",
                    reason="Required reducer output absent; no B verdict",
                ),
            )
            return False
        merged = merge(
            book,
            reduced.delta.operations,
            (),
            max_tokens=4000,
            dedup_counts_helpful=False,
        )
        book = merged.playbook
        save(
            f"writing_batch_{batch_no}.json",
            dict(product=asdict(reduced), merge=asdict(merged)),
        )
    book.save(CAMPAIGN / "book.yaml")
    save(
        "book.json",
        dict(
            sha256=book.sha256(),
            file_sha256=sha(CAMPAIGN / "book.yaml"),
            changed=book.render_prompt()
            != Playbook.load(ROOT / base.BOOK).render_prompt(),
            preparation_cost=sum(
                c
                for n, c in accounting()["costs"].items()
                if "__writing-" in n
            ),
        ),
    )
    return bool(read("book.json")["changed"])


def observations(stage: str, arm: str) -> dict[tuple[str, str], Observation]:
    protocol = read("protocol.json")
    names = protocol["training" if stage == "training" else "validation"]
    seed = 1 if stage == "followup" else 0
    if arm == "reference" and stage != "followup":
        return {
            (r["theorem"], "0"): Observation(
                r["solved"], r["cost"], r["failed"]
            )
            for r in read("references.json")[stage]
        }
    costs = accounting()["costs"]
    rows: dict[tuple[str, str], Observation] = {}
    for theorem in names:
        cfg = Config(theorem, stage, arm, seed)
        result = cell_result(cfg)
        cost = costs.get(name(cfg, None), 0.0)
        rows[(theorem, str(seed))] = Observation(
            bool(result and result["success"]), cost, result is None
        )
    return rows


def events() -> list[dict[str, Any]]:
    path = CAMPAIGN / "events.jsonl"
    return (
        [json.loads(line) for line in path.read_text().splitlines()]
        if path.exists()
        else []
    )


def comparisons(stage: str, arms: list[str]) -> dict[str, Any]:
    reference = observations(stage, "reference")
    panels = {a: observations(stage, a) for a in arms}
    pairs = [("reference", a) for a in arms]
    if "A" in arms and "B" in arms:
        pairs.append(("A", "B"))
    panels["reference"] = reference
    reports: dict[str, Any] = {}
    for a, b in pairs:
        x, y = panels[a], panels[b]
        r = compare(x, y, list(x), families=read("protocol.json")["families"])
        r["paired_cost_p"] = cost_cluster_p(
            x, y, list(x), read("protocol.json")["families"]
        )
        prep = read("book.json")["preparation_cost"] if b == "B" else 0
        r["preparation_b"] = prep
        r["all_in_cost_b"] = r["cost_b"] + prep
        r["all_in_ratio"] = (
            (r["cost_b"] + prep) / r["cost_a"] if r["cost_a"] else None
        )
        r["all_in_cost_per_solve_b"] = (
            (r["cost_b"] + prep) / r["solved_b"] if r["solved_b"] else None
        )
        reports[b + "/" + a] = r
    save(f"reports/{stage}.json", reports)
    return reports


def select(reports: dict[str, Any]) -> str | None:
    eligible: list[str] = []
    for arm in ("A", "B"):
        r = reports.get(arm + "/reference")
        if r is None:
            continue
        gain, ratio = r["solved_b"] - r["solved_a"], r["all_in_ratio"]
        if ratio is not None and (
            gain >= 1 and ratio <= 1.25 or gain >= -1 and ratio <= 0.9
        ):
            eligible.append(arm)
    eligible.sort(
        key=lambda a: (
            -reports[a + "/reference"]["solved_b"],
            reports[a + "/reference"]["all_in_cost_per_solve_b"]
            or float("inf"),
            a,
        )
    )
    adjusted: dict[str, float] = {}
    value = 0.0
    keys = ("A/reference", "B/A", "B/reference")
    for i, (p, key) in enumerate(
        sorted((reports.get(k, {}).get("p_two_sided", 1.0), k) for k in keys)
    ):
        value = max(value, min(1.0, (3 - i) * p))
        adjusted[key] = value
    winner = eligible[0] if eligible else None
    save(
        "selection.json",
        dict(winner=winner, eligible=eligible, coverage_p_holm=adjusted),
    )
    return winner


def retain(winner: str, fresh: dict[str, Any]) -> None:
    a = observations("validation", "reference") | observations(
        "followup", "reference"
    )
    b = observations("validation", winner) | observations("followup", winner)
    combined = compare(
        a, b, list(a), families=read("protocol.json")["families"]
    )
    preparation = (
        read("book.json")["preparation_cost"] if winner == "B" else 0.0
    )
    ratio = (combined["cost_b"] + preparation) / combined["cost_a"]
    gain = combined["solved_b"] - combined["solved_a"]
    repeat = fresh[winner + "/reference"]
    repeat_dominated = (
        repeat["solved_b"] < repeat["solved_a"]
        and repeat["cost_b"] > repeat["cost_a"]
    )
    passed = (
        gain >= 2 and ratio <= 1.25 or gain >= -2 and ratio <= 0.90
    ) and not repeat_dominated
    save(
        "retention.json",
        dict(
            winner=winner,
            retained=passed,
            promoted=False,
            combined=combined,
            preparation_counted_once=preparation,
            all_in_ratio=ratio,
            fresh_dominated=repeat_dominated,
            interpretation="Exploratory after selection; repeated seeds share theorem-family clusters",
        ),
    )


def campaign() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher environment lacks the API credential")
    verify()
    with (CAMPAIGN / "campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        allocate()
        b = writing()
        arms = ["A", "B"] if b else ["A"]
        training = [
            Config(n, "training", a)
            for n in read("protocol.json")["training"]
            for a in arms
        ]
        random.Random(20260913).shuffle(training)
        launch("training", training)
        comparisons("training", arms)
        ev = events()
        a_exposed = any(
            e["kind"] == "snippet"
            and e["decision"] in ("rejected", "executed_open", "completed")
            and e.get("rpc_calls", 0) > 0
            and "__training-A__" in e.get("cell", "")
            for e in ev
        )
        # The new book is present in every B proof request; require a real
        # dispatched request (a settled receipt), not merely a rendered query.
        b_exposed = b and any(
            "__training-B__" in n for n in accounting()["costs"]
        )
        save("exposure_gate.json", dict(A=a_exposed, B=b_exposed))
        validation_arms = arms if b_exposed else (["A"] if a_exposed else [])
        if validation_arms:
            batch = [
                Config(n, "validation", a)
                for n in read("protocol.json")["validation"]
                for a in validation_arms
            ]
            random.Random(20260914).shuffle(batch)
            launch("validation", batch)
            winner = select(comparisons("validation", validation_arms))
            if winner:
                batch = [
                    Config(n, "followup", a, 1)
                    for n in read("protocol.json")["validation"]
                    for a in (winner, "reference")
                ]
                random.Random(20260915).shuffle(batch)
                launch("followup", batch)
                retain(winner, comparisons("followup", [winner]))
        save("final_accounting.json", accounting())
        export_receipts()
        report()


def export_receipts() -> None:
    with Ledger(LEDGER).connect() as db:
        cursor = db.execute(
            "SELECT * FROM receipts WHERE cell LIKE 'snippets-v1__%' ORDER BY created,id"
        )
        out = io.StringIO()
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow([d[0] for d in cursor.description])
        writer.writerows(cursor)
    (CAMPAIGN / "receipts.csv").write_text(out.getvalue())


def report() -> None:
    acct = accounting()
    text = (
        "# Rocq snippet campaign\n\nValidationX is reused development data. "
        "No incumbent default changed.\n\n"
        f"New experimental spending: ${acct['new_total']:.8f}; cumulative ${acct['cumulative']:.8f}/$30.\n\n"
    )
    for stage in ("training", "validation", "followup"):
        path = CAMPAIGN / f"reports/{stage}.json"
        if path.exists():
            text += f"## {stage}\n\n```json\n" + path.read_text() + "```\n\n"
    (CAMPAIGN / "RESULTS.md").write_text(text)
    print(text, flush=True)


def main() -> None:
    action, *rest = sys.argv[1:]
    if action == "run-batch":
        key, *arguments = rest
        sys.argv = [sys.argv[0], *arguments]
        run_batch(key)
    elif action == "status":
        print(json.dumps(accounting(), indent=2))
    elif action in ("prepare", "preflight", "seal", "campaign", "report"):
        globals()[action]()
    else:
        raise ValueError("Unknown snippet campaign action")


if __name__ == "__main__":
    main()
