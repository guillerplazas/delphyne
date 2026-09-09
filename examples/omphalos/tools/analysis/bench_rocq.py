"""
Per-call timing of the Rocq bridge, per transport mode (offline).

Replays the archived compute calls of one cell (default: a median
validationX cell) through `pytanque_utils` under each mode and
reports wall-clock per call, the prefix-memo hit count and the
server's resident size — the before/after benchmark of the 2026-08-26
transport change:

- `stdio`      — the archived transport: a fresh `pet` per call;
- `socket`     — private warm server, stable document, prefix memo;
- `socket-nomemo` — the same without the prefix memo, to price it.

Runs each mode in a fresh subprocess so the server and memo start
cold. Rocq only, no API calls.

Usage:
    python -m tools.analysis.bench_rocq [--run x_validation_agentic] [--config NAME]
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, cast

import yaml

_OMPHALOS_DIR = OMPHALOS_ROOT

DEFAULT_CONFIG = "imo_1960_p2__core-medium__gpt-5.6-luna__seed0"
MODES = ("stdio", "socket", "socket-nomemo")


def _worker(cache_file: str, nomemo: bool) -> None:
    """Child body: replay every bridge call of one cache, print JSON."""
    import runtime.pytanque_utils as pt
    import runtime.rocq_server as rs

    if nomemo:
        pt.PREFIX_MEMO_CAP = 0
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    raw: Any = yaml.load(Path(cache_file).read_text(), Loader=loader)  # type: ignore[reportUnknownMemberType]
    times: list[tuple[str, float]] = []
    for e in cast(list[dict[str, Any]], raw):
        req = cast(dict[str, Any], e["input"]["request"])
        if cast(dict[str, Any], req.get("options", {})).get("model") != (
            "__compute__"
        ):
            continue
        q = cast(dict[str, Any], yaml.safe_load(req["chat"][0]["content"]))
        fun = str(q["fun"])
        if fun not in (
            "check",
            "check_assisted",
            "query",
            "inspect_at",
            "try_automation",
            "try_tactics",
        ):
            continue
        t0 = time.perf_counter()
        getattr(pt, fun)(**cast(dict[str, Any], q["args"]))
        times.append((fun, time.perf_counter() - t0))
    st = rs.MANAGER.stats()
    print(
        json.dumps(
            {
                "calls": times,
                "memo": pt.prefix_memo_size(),
                "rss_mb": st.rss_mb,
                "recycles": st.recycles,
                "fallbacks": st.fallbacks,
            }
        )
    )


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--worker":
        _worker(sys.argv[2], sys.argv[3] == "1")
        return 0
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--run", default="x_validation_agentic")
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--modes", default=",".join(MODES))
    args = ap.parse_args()
    cache = (
        _OMPHALOS_DIR
        / "experiments"
        / "output"
        / str(args.run)
        / "configs"
        / str(args.config)
        / "cache.yaml"
    )
    assert cache.exists(), cache
    print(f"bench: {args.config}")
    rows: list[str] = []
    for mode in str(args.modes).split(","):
        env = dict(os.environ)
        env["OMPHALOS_PET_MODE"] = "stdio" if mode == "stdio" else "socket"
        t0 = time.perf_counter()
        res = subprocess.run(
            [
                sys.executable,
                "-m",
                "tools.analysis.bench_rocq",
                "--worker",
                str(cache),
                "1" if mode.endswith("nomemo") else "0",
            ],
            cwd=_OMPHALOS_DIR,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        wall = time.perf_counter() - t0
        if res.returncode != 0:
            print(res.stderr)
            return 1
        data = cast(
            dict[str, Any], json.loads(res.stdout.strip().splitlines()[-1])
        )
        calls = cast(list[list[Any]], data["calls"])
        secs = [float(c[1]) for c in calls]
        by_fun: dict[str, list[float]] = {}
        for fun, s in calls:
            by_fun.setdefault(str(fun), []).append(float(s))
        per_fun = " ".join(
            f"{f}:{statistics.median(v) * 1000:.0f}ms×{len(v)}"
            for f, v in sorted(by_fun.items())
        )
        rows.append(
            f"{mode:14s} {len(secs):3d} calls  median {statistics.median(secs) * 1000:6.0f} ms  "
            f"p95 {sorted(secs)[int(0.95 * (len(secs) - 1))]:6.2f} s  total {sum(secs):6.1f} s  "
            f"wall {wall:5.1f} s  memo={data['memo']} rss={data['rss_mb']}  [{per_fun}]"
        )
        print(rows[-1], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
