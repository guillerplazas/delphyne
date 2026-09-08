"""CPU-only concurrency sweep on a fixed, archived trainX workload.

No LLM calls. Replays 192 bridge calls at each concurrency, verifies
serialized outputs, and samples aggregate process-tree RSS. Select the
fastest setting with no changed outcomes and RSS <75% of initially
available memory. This measures bridge throughput, not API throughput.
An existing result/profile is immutable. For a later diagnostic sweep,
pass --output with a new directory. Per-chunk times distinguish a slow
chunk from process startup/shutdown overhead.
"""

# pyright: strict

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any

import psutil

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

import bridge_parity as bp  # noqa: E402
import omphalos_launch as ol  # noqa: E402
import pytanque_utils as pt  # noqa: E402
from runtime_profiles import resolve  # noqa: E402

import delphyne.core.inspect as insp  # noqa: E402
from delphyne.utils.yaml import dump_yaml  # noqa: E402

Entry = tuple[str, dict[str, Any], str]
DEST = ROOT / "experiments/campaigns/ace_review_20260908"


def replay(entries: list[Entry]) -> dict[str, Any]:
    bad: list[str] = []
    start = time.monotonic()
    for fun, args, archived in entries:
        f = getattr(pt, fun)
        fresh = dump_yaml(insp.function_return_type(f), f(**args))
        verdict, _ = bp._classify(archived, fresh, False)  # pyright: ignore[reportPrivateUsage]
        if verdict not in {"identical", "path"}:
            bad.append(verdict)
    return {"seconds": time.monotonic() - start, "changed": bad}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEST)
    args = parser.parse_args()
    destination: Path = args.output
    for filename in ("runtime_benchmark.json", "runtime.json"):
        if (destination / filename).exists():
            parser.error(
                f"refusing to overwrite {destination / filename}; "
                "use --output with a new directory"
            )
    os.environ["OMPHALOS_CHECK_MEMO"] = "0"
    os.environ["OMPHALOS_MAX_STREAMS"] = "32"
    entries: list[Entry] = []
    sources: list[str] = []
    for directory in sorted(
        (ROOT / "experiments/output/x_train_agentic/configs").iterdir()
    ):
        if not (directory / "cache.yaml").exists():
            continue
        calls = bp._compute_entries(directory / "cache.yaml")  # pyright: ignore[reportPrivateUsage]
        # Bounded archived calls only. All training problems are eligible;
        # outcome exclusions avoid benchmarking deliberate timeout waits.
        calls = [
            e
            for e in calls
            if not any(
                s in e[2]
                for s in ("Timeout", "transport failure", "No response")
            )
            and int(e[1].get("timeout", 0)) <= 10
        ]
        if calls:
            entries.extend(calls[:6])
            sources.append(directory.name)
        if len(entries) >= 192:
            break
    entries = entries[:192]
    if len(entries) < 192:
        raise ValueError("insufficient bounded training calls")
    chunks = [entries[i : i + 6] for i in range(0, len(entries), 6)]
    available = psutil.virtual_memory().available
    rows: list[dict[str, Any]] = []
    for workers in (8, 16, 24, 32):
        peak = [0]
        stop = threading.Event()

        def sample() -> None:
            while not stop.wait(0.2):
                rss = 0
                for proc in [
                    psutil.Process(),
                    *psutil.Process().children(recursive=True),
                ]:
                    try:
                        rss += proc.memory_info().rss
                    except psutil.Error:
                        pass
                peak[0] = max(peak[0], rss)

        thread = threading.Thread(target=sample, daemon=True)
        thread.start()
        start = time.monotonic()
        try:
            with ol.stream_slots(
                workers, 32, wait=True, note="ACE CPU benchmark"
            ):
                with ProcessPoolExecutor(
                    workers,
                    mp_context=mp.get_context("spawn"),
                    initializer=ol._worker_init,  # pyright: ignore[reportPrivateUsage]
                    initargs=(ol.WorkerSetupArgs("socket", 4096, str(ROOT)),),
                ) as pool:
                    results = list(pool.map(replay, chunks))
        finally:
            stop.set()
            thread.join()
        row = dict(
            workers=workers,
            seconds=time.monotonic() - start,
            peak_rss_bytes=peak[0],
            changed=sum(len(r["changed"]) for r in results),
            calls=len(entries),
            chunk_seconds=[r["seconds"] for r in results],
        )
        rows.append(row)
        print(json.dumps(row), flush=True)
    valid = [
        r
        for r in rows
        if not r["changed"] and r["peak_rss_bytes"] < available * 0.75
    ]
    if not valid:
        raise RuntimeError("no concurrency setting passed")
    selected = min(valid, key=lambda r: r["seconds"])["workers"]
    profile = resolve(selected)
    destination.mkdir(parents=True, exist_ok=True)

    def write_new(filename: str, content: str) -> None:
        # A simultaneous invocation must not replace a newly frozen file.
        with (destination / filename).open("x") as file:
            file.write(content)

    write_new(
        "runtime_benchmark.json",
        json.dumps(
            dict(
                available_bytes=available,
                workload_sha256=hashlib.sha256(
                    json.dumps(entries, sort_keys=True).encode()
                ).hexdigest(),
                sources=sources,
                rows=rows,
                selected=selected,
            ),
            indent=2,
        )
        + "\n",
    )
    write_new("runtime.json", json.dumps(asdict(profile), indent=2) + "\n")


if __name__ == "__main__":
    main()
