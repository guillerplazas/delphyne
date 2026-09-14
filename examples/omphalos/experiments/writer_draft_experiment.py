"""Draft-aware curator/reducer pilot, one bundled contender vs fresh v1.

Same eight trainX historical syntax drafts, source contexts, X3 book and caps.
Eight individual curator cases and two fixed four-source reducer batches per
arm/seed. Roles tested independently on identical draft packets, not a chained
adaptation: role differences are descriptive, not an isolated causal contrast.
Seed0: 20 jobs x $0.20 <= $4 (fresh controls $2), training ledger allocation.
Seed1: identical 20 jobs <= $4 (controls $2), followup allocation, gated below.
All prior $5.12989540 remains in the original $30 ledger; reserve $4.38640002
untouched. No generators, embeddings, proof panels, paid diagnostics or retries.

Primary: unique useful source corrections surviving deterministic merge per
role/batch. Each receipt needs exact real-Rocq replay, source relevance and
novelty against frozen book. Related source families/seeds are clustered;
reducer has only two independent batches, no statistical support/promotion.
Failures remain denominators; missing/admin-censored cells forbid verdict.
Seed1 only if all contender products complete, relevant checks occur in both
source batches, at least one useful retained edit, and at least one role/batch
beats its fresh control without correctness violations. Retain as exploratory
only if an advantage repeats in seed1, aggregate useful corrections increase,
and cost/useful correction is no worse (control zero: report cost directly).
Unchanged inherited receipts need no new checks. More calls alone is not a win.

Both harnesses: prepare, preflight, seal, campaign. Only run-batch dispatches,
through OmphalosExperiment; per-request upper-bound reservations unchanged.
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

from ace.ace_playbook import Playbook
from experiments import snippet_experiment as old
from experiments.common import omphalos_launch as ol
from prove_snippets import CheckedWriting
from prove_writer_drafts import DraftWriting, UnverifiedSnippetDraft
from runtime.campaign_budget import CampaignResponsesModel

ROOT = old.ROOT
CAMPAIGN = old.CAMPAIGN / "writer_pilot"
OUTPUT = old.OUTPUT / "writer_pilot"
PREFIX = "writer-drafts-v1__"
PRIOR_COST = 5.12989540


def read(name: str) -> Any:
    return json.loads((CAMPAIGN / name).read_text())


def save(name: str, value: Any) -> None:
    path = CAMPAIGN / name
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text() != content:
            raise ValueError("Frozen artifact changed: " + name)
    else:
        path.write_text(content)


def context() -> dp.ExecutionContext:
    ctx = old.context()
    return replace(
        ctx,
        modules=(*ctx.modules, "prove_writer_drafts"),
        demo_files=(*ctx.demo_files, ROOT / "demos/writer_drafts.demo.yaml"),
    )


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


def activate(seed: int, events: bool = True) -> None:
    old.activate("training" if seed == 0 else "followup", events=False)
    if events:
        os.environ["OMPHALOS_ADMISSION_EVENTS"] = str(
            CAMPAIGN / "events.jsonl"
        )


@dataclass
class Config:
    bench_name: str
    role: str
    arm: str
    seed: int
    writer_input: str
    input_sha256: str
    dollar_cap: float = 0.20

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        os.environ["OMPHALOS_CAMPAIGN_CELL"] = name(self, None)
        if old.sha(CAMPAIGN / self.writer_input) != self.input_sha256:
            raise ValueError("Input provenance drift")
        item = read(self.writer_input)
        if item["role"] != self.role or self.arm not in ("control", "draft"):
            raise ValueError("Unregistered writer")
        policy_args: dict[str, object] = dict(
            snapshot_directory=str(CAMPAIGN / "transport" / name(self, None)),
            dollar_cap=self.dollar_cap,
        )
        if self.arm == "control":
            # Identical candidate bytes reach both arms; v1 sees them as evidence.
            item.pop("drafts")
            policy_args["role"] = self.role
        return dp.RunStrategyArgs(
            strategy="write_rocq_drafts"
            if self.arm == "draft"
            else "write_checked_rocq_advice",
            args=item,
            policy="draft_writer_policy"
            if self.arm == "draft"
            else "snippet_policy",
            policy_args=policy_args,
            budget=dict(
                price=self.dollar_cap, num_requests=4, rocq_seconds=180
            ),
        )


def name(cfg: Config, _: object) -> str:
    return f"{PREFIX}{cfg.bench_name}__{cfg.role}-{cfg.arm}__seed{cfg.seed}"


def directory(cfg: Config) -> Path:
    return OUTPUT / f"seed{cfg.seed}" / "configs" / name(cfg, None)


def configs(seed: int) -> list[Config]:
    return [Config(**r) for r in read(f"manifests/seed{seed}.json")]


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
    diagnostics = json.dumps(
        raw.get("outcome", {}).get("diagnostics", [])
    ) + json.dumps(raw.get("diagnostics", []))
    diagnostics += "".join(p.read_text() for p in path.glob("exception*.txt"))
    if "CampaignExhausted" in diagnostics:
        raise ValueError("Administratively censored cell: " + name(cfg, None))
    return raw.get("outcome", {}).get("result") if state == "done" else None


def product(cfg: Config) -> CheckedWriting | None:
    out = cell_result(cfg)
    if not out or not out["success"] or len(out["values"]) != 1:
        return None
    if cfg.arm == "draft":
        return pydantic_load(DraftWriting, out["values"][0]).checked
    return pydantic_load(CheckedWriting, out["values"][0])


def prepare() -> None:
    acct = accounting()
    if (
        acct["new_total"]
        or abs(acct["prior_total"] - PRIOR_COST) > 1e-8
        or acct["unresolved"]
        or acct["billing_issues"]
    ):
        raise ValueError("Prior accounting must be reconciled")
    book = Playbook.load(ROOT / old.base.BOOK)
    packets = old.read("reducer_study/candidate_packets.json")["batches"]
    save("checkpoint.json", acct)
    save(
        "protocol.json",
        dict(
            authorization="Guille: reducer, curator or ACE elements most benefiting; please test",
            prior_cost=PRIOR_COST,
            ceiling=30,
            stage0=4,
            stage1=4,
            fresh_controls=4,
            maximum_cumulative=PRIOR_COST + 8,
            untouched_contingency=4.38640002,
            automatic_retries=False,
            source_generators=0,
            embeddings=0,
            paid_diagnostics=0,
            seeds=[0, 1],
            seed_semantics="independent fresh requests, repeated measurements; model seed not sent",
            cases_per_seed=dict(curator=16, reducer=4),
            cap_per_cell=0.20,
            prompts="one bundle: role instructions, explicit decisions, applicable writer demo; identical draft evidence in fresh control",
            book_sha256=book.sha256(),
            families=old.family_map(),
            alpha=0.10,
            confidence=0.90,
            primary="useful checked source corrections surviving merge per role and batch",
            expansion="all draft products complete; relevant executed checks in both batches; >=1 useful retained correction and advantage in >=1 matched role/batch; no invalid retained code",
            retention="advantage repeats in seed1; aggregate useful correction increase; cost per useful correction no worse, control zero reported directly",
            promotion=False,
            coverage_evaluation="none: writer utility is not theorem solve coverage",
            scope="trainX only; closed testX/protected evidence excluded; validationX remains reused development data",
        ),
    )
    # Pre-outcome rubric: repairs, not repetitions of already-correct advice.
    labels = {
        old.SOURCES[
            0
        ]: "Useful only if it gives an executable finite-sum normalization step advancing Hsum or the target; vague simplification already covered by rocq-00011 is redundant.",
        old.SOURCES[
            1
        ]: "Parenthesized change for the product hypothesis is an eligible local syntax correction, absent from current book; irrelevant new assertions are not useful.",
        old.SOURCES[
            2
        ]: "Correcting unparenthesized INR change syntax repairs erroneous rocq-00015 and is useful; merely repeating its cast guidance is redundant.",
        old.SOURCES[
            3
        ]: "Parenthesized change for the natural power bound is an eligible source correction; count at most one per source and deduplicate generic change advice within a batch.",
        old.SOURCES[
            4
        ]: "Square-to-product advice is already correct in rocq-00012; merely supplying another instantiation is redundant. A concrete missing focus/syntax repair can qualify only with explicit evidence.",
        old.SOURCES[
            5
        ]: "A syntactically valid finite-set equality assertion fixing the historical delimiter error is eligible even with open obligations; it is not evidence that the equality is true or the cardinal theorem solved.",
        old.SOURCES[
            6
        ]: "Square-to-product advice is already correct in rocq-00012; another instantiation is redundant unless it fixes a demonstrated missing focus/syntax issue.",
        old.SOURCES[
            7
        ]: "Closed nat computation is already covered by rocq-00004; bare computation is redundant. A missing parenthesized change/focus correction can qualify if specifically explained.",
    }
    save(
        "utility_rubric.json",
        dict(
            labels=labels,
            counting="one per source; within reducer collapse identical reusable tactic patterns; no credit for no-op/id tactic, unrelated assertions, mere receipt existence, or source-local success generalized to all contexts",
            review="manual source-blind-to-arm JSON review after exact Rocq replay; judgments and reasons exported",
        ),
    )
    cases: list[tuple[str, str, list[dict[str, Any]]]] = []
    for b, packet in enumerate(packets):
        cases += [
            (p["context"]["theorem_name"], "curator", [p]) for p in packet
        ]
        cases.append((f"batch{b}", "reducer", packet))
    for case, role, packet in cases:
        drafts = [
            UnverifiedSnippetDraft(
                **{
                    k: p[k]
                    for k in UnverifiedSnippetDraft.__dataclass_fields__
                }
            )
            for p in packet
        ]
        evidence = dict(
            unverified_candidates=[asdict(d) for d in drafts],
            status="unverified; historical rejected code is not a certificate",
            authoritative_terminals={
                p["context"]["theorem_name"]: old.read(
                    f"sources/{p['context']['theorem_name']}.json"
                )["terminal"]
                for p in packet
            },
        )
        save(
            f"inputs/{role}_{case}.json",
            dict(
                role=role,
                evidence=json.dumps(evidence),
                playbook=book.render_prompt(),
                contexts=[p["context"] for p in packet],
                drafts=[asdict(d) for d in drafts],
                receipts=[],
            ),
        )
    for seed in (0, 1):
        jobs: list[Config] = []
        for i, (case, role, _) in enumerate(cases):
            path = f"inputs/{role}_{case}.json"
            # Reverse arm ordering across case and seed to reduce a fixed cache/order bias.
            arms = (
                ("control", "draft")
                if (i + seed) % 2 == 0
                else ("draft", "control")
            )
            jobs.extend(
                Config(case, role, a, seed, path, old.sha(CAMPAIGN / path))
                for a in arms
            )
        save(f"manifests/seed{seed}.json", [asdict(j) for j in jobs])


def seal() -> None:
    if not read("offline_checks.json")["passed"]:
        raise ValueError("Offline checks required")
    paths = [
        ROOT / "prove_writer_drafts.py",
        Path(__file__),
        ROOT / "demos/writer_drafts.demo.yaml",
        ROOT / "tests/test_writer_drafts.py",
        ROOT / "tools/data/writer_draft_demos.py",
        ROOT / "tools/reports/writer_draft_results.py",
    ]
    paths += list(
        (ROOT / "prompts/ace/adaptation").glob("WriteRocqDraftAdvice.*")
    )
    paths += list(CAMPAIGN.glob("inputs/*.json")) + list(
        CAMPAIGN.glob("manifests/*.json")
    )
    paths += [
        CAMPAIGN / n
        for n in ("protocol.json", "utility_rubric.json", "checkpoint.json")
    ]
    # Pin all inherited implementation dependencies by their currently audited bytes.
    paths += [ROOT / p for p in old.read("seal.json")]
    save(
        "seal.json",
        dict(
            files={
                str(p.relative_to(ROOT)): old.sha(p)
                for p in sorted(set(paths))
            }
        ),
    )


def verify() -> None:
    for path, expected in read("seal.json")["files"].items():
        if old.sha(ROOT / path) != expected:
            raise ValueError("Source seal drift: " + path)
    a = accounting()
    if (
        a["unresolved"]
        or a["billing_issues"]
        or abs(a["prior_total"] - PRIOR_COST) > 1e-8
        or a["new_total"] > 8 + 1e-8
        or a["cumulative"] > 30 + 1e-8
    ):
        raise ValueError("Cumulative accounting or billing issue")


def run_batch(seed: int) -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Launcher environment lacks API credential")
    verify()
    if seed == 1 and not read("gate_seed0.json")["expand"]:
        raise ValueError("Seed1 gate not passed")
    activate(seed)
    ol.OmphalosExperiment(
        config_class=Config,
        configs=configs(seed),
        context=context(),
        output_dir=str((OUTPUT / f"seed{seed}").relative_to(ROOT)),
        config_naming=name,
        attempts=1,
        wait_for_slots=True,
    ).run_cli()


def launch(seed: int) -> None:
    if (CAMPAIGN / f"batches/seed{seed}.json").exists():
        return
    verify()
    ledger = accounting()["ledger"]
    stage = "training" if seed == 0 else "followup"
    used = sum(r["dollars"] for r in ledger["groups"] if r["stage"] == stage)
    needed = sum(
        c.dollar_cap
        for c in configs(seed)
        if ol.ground_truth(directory(c)) not in ("done", "failed")
    )
    if used + needed > ledger["allocations"][stage] + 1e-8:
        raise ValueError(
            "Whole remaining required batch does not fit allocation"
        )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "experiments.writer_draft_experiment",
            "run-batch",
            str(seed),
            "run",
            "--max_workers=8",
            "--wait",
        ],
        cwd=ROOT,
        check=False,
    )
    states = {
        name(c, None): ol.ground_truth(directory(c)) for c in configs(seed)
    }
    for cfg in configs(seed):
        cell_result(cfg)
    verify()
    save(
        f"batches/seed{seed}.json",
        dict(exit_code=result.returncode, states=states),
    )


def replay(seed: int) -> None:
    before = accounting()["receipts"]
    activate(seed, events=False)
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
    save(
        f"replays/seed{seed}.json",
        dict(passed=True, paid_requests=0, cells=rows),
    )


def main() -> None:
    command = sys.argv.pop(1)
    if command == "run-batch":
        run_batch(int(sys.argv.pop(1)))
    elif command == "prepare":
        prepare()
    elif command == "seal":
        seal()
    elif command == "campaign":
        launch(int(sys.argv.pop(1)))
    elif command == "replay":
        replay(int(sys.argv.pop(1)))
    else:
        raise ValueError(command)


if __name__ == "__main__":
    main()
