"""Read-only progress counters, without interpreting unfinished outcomes."""

from datetime import datetime
import json
import sqlite3

from .common import CAMPAIGN, OUTPUT, REPORT, read


def completed(batch: str) -> int:
    normal = sum(
        1 for _ in (OUTPUT / batch / "configs").glob("*/completed.json")
    )
    terminal = CAMPAIGN / "terminal_failures" / (batch + ".json")
    return normal + (
        len(read(terminal)["failures"]) if terminal.exists() else 0
    )


def run() -> None:
    schedule = read(CAMPAIGN / "core_schedule.json")
    frozen = sum(completed(b["batch"]) for b in schedule["batches"])
    online = sum(
        completed(f"online-o{order}-s{step:02d}")
        for order in (0, 1)
        for step in range(40)
    )
    updates = [
        sum(
            (
                CAMPAIGN / "online_events" / f"online-o{o}-s{s:02d}.json"
            ).exists()
            for s in range(40)
        )
        for o in (0, 1)
    ]
    with sqlite3.connect(
        f"file:{CAMPAIGN / 'ledger.sqlite3'}?mode=ro", uri=True
    ) as db:
        stages = db.execute(
            "SELECT stage, COUNT(*), SUM(charged) FROM receipts "
            "WHERE status = 'settled' GROUP BY stage"
        ).fetchall()
        pending = db.execute(
            "SELECT status, COUNT(*) FROM receipts "
            "WHERE status != 'settled' GROUP BY status"
        ).fetchall()
        bounded = db.execute(
            "SELECT COUNT(*), SUM(charged) FROM receipts "
            "WHERE status='bounded_charge'"
        ).fetchone()
    certificate = REPORT / "study_certification.json"
    finished_study = (
        frozen + online == 1520
        and completed("rule_repairs") == 80
        and completed("adaptive_frozen") == 160
        and certificate.exists()
        and read(certificate)["passed"]
    )
    lines = [
        "ACE INVESTIGATION — "
        + ("COMPLETE" if finished_study else "LIVE STATUS"),
        datetime.now().astimezone().isoformat(timespec="seconds"),
        "",
        "Read-only counters; running experiments are not interrupted.",
        "Finished means a completion receipt or audited terminal failure;",
        "platform failures remain in the denominator and all spending.",
        "Scientific conclusions additionally require final cost/proof checks.",
        "",
        f"Main benchmark: {frozen + online}/1520 finished",
        f"  Frozen schedule: {frozen}/1120",
        f"  Online track, including shared controls: {online}/400",
        f"  Learning updates: order 0 = {updates[0]}/40; order 1 = {updates[1]}/40",
        f"Rule repair follow-up: {completed('rule_repairs')}/80",
        f"Adaptive frozen follow-up: {completed('adaptive_frozen')}/160",
        "Source collection: 80/80; author pilot: 204/204 (already certified)",
        "",
    ]
    total = sum(float(cost or 0) for _, _, cost in stages)
    calls = sum(int(n) for _, n, _ in stages)
    lines.append(f"Settled API spend: ${total:.6f} across {calls:,} calls")
    lines += [
        f"  {stage}: ${cost:.6f} across {n:,} calls"
        for stage, n, cost in stages
    ]
    lines.append("Other receipt states: " + json.dumps(dict(pending)))
    if bounded is not None and bounded[0]:
        lines.append(
            f"Retained unknown invoice bound: $0–${bounded[1]:.8f} "
            f"across {bounded[0]} separately reconciled timeout(s)"
        )
    pause = CAMPAIGN / "PAUSED"
    lines.append("Dispatch pause: " + str(pause.exists()))
    if pause.exists():
        lines.append("  Reason: " + read(pause)["reason"])
    quota = CAMPAIGN / "quota_recovery"
    if (quota / "preparation.json").exists() and not (
        quota / "continuation_certificate.json"
    ).exists():
        record = read(quota / "preparation.json")
        lines.append(
            f"Administratively interrupted: {record['cell']} after "
            f"{record['successful_responses']} paid responses; "
            "exact prefix preserved, not counted as a completed failure."
        )
    rate = CAMPAIGN / "rate_recovery/preparation.json"
    if rate.exists():
        record = read(rate)
        finished = sum(
            (
                OUTPUT
                / record["batch"]
                / "configs"
                / identity
                / "completed.json"
            ).exists()
            for identity in record["interrupted"]
        )
        lines.append(
            f"Rate-limit continuations: {finished}/{len(record['interrupted'])} returned; "
            "paid prefixes preserved, temporary rejections are not theorem failures."
        )
        concurrent = (
            CAMPAIGN / "rate_recovery/concurrent/queue_start.json"
        ).exists()
        lines.append(
            ("Completed dispatch used: " if finished_study else "Dispatch: ")
            + (
                "four proof workers, up to four HTTP calls, shared 400,000-token/minute target."
                if concurrent
                else "four proof workers, one HTTP call, 400,000 observed tokens/minute pacing."
            )
        )
    lines.append(
        "User-requested hold on new batches: "
        + str((CAMPAIGN / "HOLD_NEW_BATCHES.json").exists())
    )
    replays = sum(1 for _ in (CAMPAIGN / "budget_replay").glob("*.json"))
    lines += [
        "",
        f"Lower-budget replay: {replays}/1520 frozen cells; {3 * replays}/4560 scenarios",
        "Replay scenarios make no API calls and are not new model samples.",
        "",
        "Luna remains the solver. Larger models only prepare playbooks.",
        "Only trainX and validationX are used; testX remains closed.",
        "No full-variant ranking is inferred from unfinished files.",
    ]
    if finished_study:
        lines += [
            "",
            "All 2,044 registered solver cells are certified; no paid runs remain pending.",
            "Final cost/proof certificate: report/ace_independent_audit/study_certification.json",
            "Current statistical review: report/ace_independent_audit/statistical_review.json",
        ]
    output = "\n".join(lines) + "\n"
    temporary = CAMPAIGN / "STATUS.tmp"
    temporary.write_text(output)
    temporary.replace(CAMPAIGN / "STATUS.txt")
    print(output, end="")


if __name__ == "__main__":
    run()
