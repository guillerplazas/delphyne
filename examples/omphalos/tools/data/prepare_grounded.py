"""Build a bounded, trainX-only evidence pool from paid cached transitions.

No API calls. At most 24 local admission checks, stopping after eight
verified claims from distinct training theorems. Cache order proposes a
candidate only; fresh Rocq execution establishes whether it is evidence.
"""

from runtime.paths import OMPHALOS_ROOT

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from typing import Any, cast
import yaml

import ace.ace_grounded as ag  # noqa: E402
from ace.ace_evidence import import_signature, unknown_identifier  # noqa: E402
import runtime.pytanque_utils as pt  # noqa: E402

ROOT = OMPHALOS_ROOT

CAMPAIGN = ROOT / "experiments/campaigns/ace_bounded_20260908"


def candidates() -> list[ag.TrainingTransition]:
    allowed = {
        Path(s.strip()).stem: s.strip()
        for s in (ROOT / "benchmarks/trainX.txt").read_text().splitlines()
        if s.strip() and not s.startswith("#")
    }
    run = ROOT / "experiments/output/ace_review_calibration"
    manifest: Any = yaml.load(
        (run / "experiment.yaml").read_text(), Loader=yaml.CSafeLoader
    )
    out: list[ag.TrainingTransition] = []
    for name in sorted(manifest["configs"]):
        bench = name.split("__")[0]
        if (
            bench not in allowed
            or "__baseline-r64__" not in name
            or not name.endswith("__seed0")
        ):
            continue
        cache = run / "configs" / name / "cache.yaml"
        if not cache.exists():
            continue
        content = cache.read_bytes()
        raw: Any = yaml.load(content, Loader=yaml.CSafeLoader)
        attempts: list[tuple[list[str], dict[str, Any]]] = []
        solution: tuple[str, ...] = ()
        for entry in raw:
            chat = entry.get("input", {}).get("request", {}).get("chat", [])
            if not chat or not str(chat[-1].get("content", "")).startswith(
                ("fun: check_assisted", "fun: check\n")
            ):
                continue
            outputs: Any = (entry.get("output") or dict[str, Any]()).get(
                "outputs", []
            )
            if not outputs:
                continue
            call: Any = yaml.load(chat[-1]["content"], Loader=yaml.CSafeLoader)
            fb: Any = yaml.load(outputs[0]["content"], Loader=yaml.CSafeLoader)
            tactics = cast(list[str], call["args"].get("tactics", []))
            attempts.append((tactics, fb))
            if fb.get("success"):
                solution = tuple(fb.get("proof_so_far") or tactics)
        for (before, fb), (_, next_fb) in zip(attempts, attempts[1:]):
            index = (
                int(fb["failing_index"])
                if fb.get("failing_index") is not None
                else None
            )
            accepted = cast(list[str], next_fb.get("proof_so_far") or [])
            if fb.get("success") or index is None or len(accepted) <= index:
                continue
            prefix = before[:index]
            if accepted[:index] != prefix:
                continue
            failed = str(fb.get("failing_tactic") or "Qed.")
            correction = (str(accepted[index]),)
            if correction == (failed,):
                continue
            out.append(
                ag.TrainingTransition(
                    allowed[bench],
                    bench,
                    name,
                    hashlib.sha256(content).hexdigest(),
                    tuple(prefix),
                    failed,
                    str(fb.get("error_message") or ""),
                    tuple(fb.get("remaining_goals") or []),
                    correction,
                    solution,
                )
            )
    return out


def prepare() -> None:
    CAMPAIGN.mkdir(parents=True, exist_ok=True)
    target = CAMPAIGN / "evidence_v2.json"
    if target.exists():
        print("Existing frozen evidence:", target)
        return
    pool = candidates()

    # Prefer reference/type defects, then structural corrections; stable
    # identifiers break ties. No validation outcomes influence selection.
    def priority(e: ag.TrainingTransition) -> tuple[int, str, str]:
        kind = ag.decision_kind(
            pt.Feedback(False, 0, e.failed_action, e.error)
        )
        return (
            {"reference": 0, "bridge": 1, "structure": 2}[kind],
            e.theorem_name,
            e.failed_action,
        )

    checked: list[ag.ClaimVerdict] = []
    used: set[str] = set()
    # Round-robin prevents one abundant error class from filling the pool.
    groups = [
        [e for e in sorted(pool, key=priority) if priority(e)[0] == k]
        for k in range(3)
    ]
    interleaved = [
        g[i]
        for i in range(max(map(len, groups), default=0))
        for g in groups
        if i < len(g)
    ]
    for e in interleaved:
        if len(checked) >= 24 or len(used) >= 8:
            break
        if e.theorem_name in used:
            continue
        fb = pt.Feedback(False, 0, e.failed_action, e.error)
        kind = ag.decision_kind(fb)
        missing = unknown_identifier(e.error) or ""
        claim = ag.AdviceClaim(
            f"checked-{e.source_sha256[:8]}-{len(checked)}",
            kind,
            f"After {e.failed_action!r} produced {e.error[:200]!r}",
            (),
            e.correction,
            e,
            import_signature(ROOT / e.problem_file),
            missing,
        )
        verdict = ag.validate_claim(claim)
        checked.append(verdict)
        if verdict.status == "verified":
            used.add(e.theorem_name)
    state = ag.AdaptationState().admit(tuple(checked))
    data = {
        "source": "trainX/r64/seed0",
        "candidates": len(pool),
        "state": asdict(state),
    }
    with target.open("x") as file:
        json.dump(data, file, indent=2)
    print(
        json.dumps(
            {
                "candidates": len(pool),
                "checked": len(checked),
                "admitted": len(state.claims),
                "problems": sorted(used),
            }
        )
    )


if __name__ == "__main__":
    prepare()
