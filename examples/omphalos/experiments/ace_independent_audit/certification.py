"""Independent receipt reconstruction and predict-before-update checks."""

from collections import Counter
from datetime import date, datetime
import gzip
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ace.ace_playbook import Playbook

from .accounting import price
from . import campaign as c
from .common import CAMPAIGN, OUTPUT, REPORT, allowed, read, save, sha
from .cost_bounds import receipt_interval
from .economics import ledger_rows


def chronology(*, final: bool) -> dict[str, Any]:
    protocol = read(CAMPAIGN / "online_protocol.json")
    receipts = ledger_rows()
    result: list[dict[str, Any]] = []
    for order in (0, 1):
        previous = {a: dict(next_id=1, bullets=[]) for a in ("A2", "B1", "B2")}
        names = protocol["independent_orders"][order]
        for step, theorem in enumerate(names):
            batch = f"online-o{order}-s{step:02d}"
            event_path = CAMPAIGN / "online_events" / f"{batch}.json"
            if not event_path.exists():
                if final:
                    raise ValueError("Online curriculum is not complete")
                break
            event = read(event_path)
            scores = CAMPAIGN / "online_scores" / f"{batch}.json"
            if (
                event["theorem"] != theorem
                or sha(scores) != event["score_sha"]
            ):
                raise ValueError("Online score commitment changed")
            jobs = [
                c.Job(**v)
                for v in read(CAMPAIGN / "batches" / f"{batch}.json")
            ]
            completed: list[float] = []
            for job in jobs:
                folder = OUTPUT / batch / "configs" / c.name(job, None)
                receipt = read(folder / "completed.json")
                if any(
                    receipt[key] != sha(folder / filename)
                    for key, filename in (
                        ("cache_sha", "cache.yaml"),
                        ("result_sha", "result.yaml"),
                    )
                ):
                    raise ValueError("Online completed result changed")
                completed.append(
                    datetime.fromisoformat(receipt["completed_at"]).timestamp()
                )
                if job.arm.startswith("online_"):
                    arm = job.arm.removeprefix("online_")
                    before = read(CAMPAIGN / job.book_file)
                    if before["playbook"] != previous[arm]:
                        raise ValueError(
                            "Online book is not the preceding update"
                        )
                    if (
                        before["training_theorems"] != names[:step]
                        or theorem in before["training_theorems"]
                    ):
                        raise ValueError(
                            "Current/future task entered the online book"
                        )
                    if (
                        job.book_sha != sha(CAMPAIGN / job.book_file)
                        or job.book_sha != event["before"][arm]
                    ):
                        raise ValueError("Online pre-update book hash differs")
                    if (
                        step == 0
                        and before["text"] != Playbook().render_prompt()
                    ):
                        raise ValueError(
                            "Cold online curriculum did not start empty"
                        )
                    evidence_file = (
                        f"{batch}__{arm}"
                        + ("_teacher" if arm == "B2" else "")
                        + ".json"
                    )
                    evidence = read(CAMPAIGN / "evidence" / evidence_file)
                    if (
                        evidence["theorem"] != theorem
                        or evidence["result_sha"] != receipt["result_sha"]
                        or evidence["cache_sha"] != receipt["cache_sha"]
                    ):
                        raise ValueError(
                            "Learning evidence differs from scored trajectory"
                        )
                    for role in ("reflect", "curate"):
                        source = read(
                            CAMPAIGN
                            / "role_inputs"
                            / f"{batch}__{arm}__{role}.json"
                        )
                        if json.loads(source["evidence"]) != evidence:
                            raise ValueError(
                                "Online learning role used different evidence"
                            )
            learned = [
                r for r in receipts if r["cell"].startswith(batch + "__")
            ]
            if len(learned) < 6 or any(
                r["status"] != "settled" for r in learned
            ):
                raise ValueError("Online update has incomplete paid receipts")
            first_update = min(r["created"] for r in learned)
            if first_update < max(completed):
                raise ValueError(
                    "Learning started before every current score completed"
                )
            previous = event["after"]
            result.append(
                dict(
                    order=order,
                    step=step,
                    theorem=theorem,
                    score_sha=event["score_sha"],
                    latest_solver_completion=max(completed),
                    first_learning_request=first_update,
                    passed=True,
                )
            )
    output = dict(
        steps=len(result),
        curricula=2,
        cells=5 * len(result),
        events=result,
        checks="Cold empty books; exact preceding state; current and future task absent from training prefix; completed solver hashes committed before learning; roles consume exactly the scored trajectory.",
    )
    if final:
        if len(result) != 80:
            raise ValueError("Expected eighty online updates")
        save(REPORT / "online_chronology.json", output)
    return output


def receipt_audit(destination: Path | None = None) -> dict[str, Any]:
    rows = ledger_rows()
    models: Counter[str] = Counter()
    phases: Counter[str] = Counter()
    cost = 0.0
    rejected = 0
    bounded: list[dict[str, Any]] = []
    for row in rows:
        if row["status"] == "bounded_charge":
            lo, hi = receipt_interval(row)
            if row["stage"] != "solver" or row["model"] != "gpt-5.6-luna":
                raise ValueError("Unexpected bounded request role/model")
            bounded.append(
                dict(
                    receipt=row["id"], cell=row["cell"], cost_interval=[lo, hi]
                )
            )
            continue
        if row["status"] != "settled" or row["charged"] is None:
            raise ValueError("Unresolved receipt: " + row["id"])
        path = CAMPAIGN / "responses" / row["cell"] / (row["id"] + ".json.gz")
        with gzip.open(path, "rt") as stream:
            raw = json.load(stream)
        if raw["receipt"] != row["id"] or raw["cell"] != row["cell"]:
            raise ValueError("Response identity differs from ledger")
        if raw.get("exception"):
            if not raw["exception"]["rejected"] or row["charged"] != 0:
                raise ValueError("Unreconciled exception charge")
            rejected += 1
            continue
        response = raw["response"]
        ledger_usage = json.loads(row["usage"])
        if ledger_usage["response_id"] != response["id"]:
            raise ValueError("Provider response identity mismatch")
        day = date.fromisoformat(raw["started"][:10])
        actual = price(
            response["usage"],
            response["model"],
            on=day,
            tier=response["service_tier"],
            regional=urlparse(str(raw["endpoint"])).hostname
            != "api.openai.com",
        )
        if abs(actual["price"] - row["charged"]) > 1e-10:
            raise ValueError("Raw provider usage differs from settled tariff")
        if row["stage"] == "solver" and response["model"] != "gpt-5.6-luna":
            raise ValueError("Non-Luna benchmark solver")
        models[response["model"]] += 1
        phases[row["stage"]] += 1
        cost += actual["price"]
    output = dict(
        receipts=len(rows),
        paid_cost=cost,
        rejected_zero_charge=rejected,
        models=dict(models),
        phases=dict(phases),
        passed=True,
        note="Recomputed from every persisted raw provider response, including cache writes, context premiums, service tier and regional endpoint. All benchmark solver responses are Luna.",
    )
    if bounded:
        upper = cost + sum(r["cost_interval"][1] for r in bounded)
        output.update(
            paid_cost=upper,
            paid_cost_interval=[cost, upper],
            observed_paid_cost=cost,
            cost_is_exact=False,
            bounded_receipts=bounded,
            settled_receipts=len(rows) - len(bounded),
            note="Every returned provider response is independently repriced. One explicitly approved timeout has no returned usage: its reservation is independently recomputed and fully retained, with its invoice interval exposed. paid_cost is upper liability, not an exact invoice. Model/phase counts cover returned non-rejected responses; the bounded request is separately identified and is also Luna.",
        )
    save(destination or REPORT / "receipt_certification.json", output)
    return output


def learning_scope(destination: Path | None = None) -> dict[str, Any]:
    names = {t for t, (stage, _) in allowed().items() if stage == "train"}
    inputs = list((CAMPAIGN / "role_inputs").glob("*.json"))
    checked = 0
    for path in inputs:
        value = read(path)
        if "evidence" not in value:
            raise ValueError("Learning input without explicit evidence")
        evidence = json.loads(value["evidence"])
        trajectories = evidence.get("trajectories", [evidence])
        for trajectory in trajectories:
            if trajectory["theorem"] not in names:
                raise ValueError("Learning accessed a non-training problem")
            checked += 1
    diagnostic_sources = 0
    diagnostic_protocol = CAMPAIGN / "learning_cache_protocol.json"
    if diagnostic_protocol.exists():
        from .learning_cache import one_shot_payload

        for source in read(diagnostic_protocol)["sources"]:
            path = CAMPAIGN / source["response_file"]
            if sha(path) != source["response_sha"]:
                raise ValueError("Author diagnostic source changed")
            with gzip.open(path, "rt") as stream:
                original = json.load(stream)
            identity = "learning_cache__" + source["cell"]
            responses = list(
                (CAMPAIGN / "responses" / identity).glob("*.json.gz")
            )
            if len(responses) != 1:
                raise ValueError("Expected one author diagnostic request")
            with gzip.open(responses[0], "rt") as stream:
                diagnostic = json.load(stream)
            if diagnostic["payload"] != one_shot_payload(original["payload"]):
                raise ValueError("Author diagnostic changed source content")
            # This exact role input is already included in the scope walk.
            if (
                CAMPAIGN / "role_inputs" / (source["cell"] + ".json")
                not in inputs
            ):
                raise ValueError("Diagnostic source was not scope checked")
            diagnostic_sources += 1
    result = dict(
        role_inputs=len(inputs),
        source_references=checked,
        author_diagnostic_sources=diagnostic_sources,
        passed=True,
        allowed="Only the forty trainX theorem identifiers; validationX is used for frozen scoring, never these learning roles. Author cache diagnostics preserve the exact previously scope-checked source content.",
    )
    save(destination or REPORT / "learning_scope_certification.json", result)
    return result


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["partial-chronology"]:
        value = chronology(final=False)
        print(json.dumps({k: v for k, v in value.items() if k != "events"}))
    elif sys.argv[1:] == ["finalize"]:
        print(json.dumps(receipt_audit()))
        print(json.dumps(learning_scope()))
        print(
            json.dumps(
                {
                    k: v
                    for k, v in chronology(final=True).items()
                    if k != "events"
                }
            )
        )
    else:
        raise SystemExit("Use partial-chronology or finalize")
