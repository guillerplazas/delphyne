"""
Byte-for-byte parity of the Rocq bridge against archived compute calls.

`cache_mode: replay` proves that the *prompts* of an archived run are
unchanged, but it never re-executes the bridge: every `dp.compute`
call is cached as a `__compute__` request and served from `cache.yaml`.
This tool closes that gap. For every archived compute entry of the
selected configs it re-executes `pytanque_utils.<fun>(**args)` through
the current bridge, serialises the result exactly as `Compute` does
(`dump_yaml` of the function's declared return type) and compares it
with the archived output.

Mismatches are classified so the expected ones can be told apart from
regressions:

- `identical` — the archived bytes;
- `path` — the only difference is an embedded augmented-file path
  (those paths were random per call in the archive: never stable);
- `timeout` — a `Timeout!` / deadline verdict differs (wall-clock
  bound; the archive's own re-runs disagree here too);
- `crash` — the archived STDIO `pet` died mid-call ("No response from
  pet process"); the bounded server now reports Rocq's own error;
- `transport` — the new bridge reports a transport failure where the
  archived cell recorded a crash (`exception.txt`) or a runaway state;
- `other` — anything else: a regression until explained. Non-zero exit.

It also reports per-call wall-clock, so the same run doubles as the
before/after timing benchmark (`OMPHALOS_PET_MODE=stdio` vs `socket`).

Usage:
    python tools/bridge_parity.py --run x_validation_agentic --config NAME
    python tools/bridge_parity.py --run x_validation_agentic --limit 3
    python tools/bridge_parity.py --run x_validation_agentic --funs query,check_assisted
"""

# pyright: strict

import argparse
import os
import re
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytanque_utils as pt  # noqa: E402
import rocq_server  # noqa: E402

import delphyne.core.inspect as insp  # noqa: E402
from delphyne.utils.yaml import dump_yaml  # noqa: E402

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent

BRIDGE_FUNS = (
    "check",
    "check_assisted",
    "query",
    "inspect_at",
    "try_automation",
    "try_tactics",
)

_AUG_PATH_RE = re.compile(r"/[^\s'\"]*omphalos_aug_[0-9a-f]+/[^\s'\"]*\.v")
_STABLE_PATH_RE = re.compile(
    r"/[^\s'\"]*/\.rocq_cache/aug/[0-9a-f]+/[^\s'\"]*\.v"
)


@dataclass
class Outcome:
    config: str
    fun: str
    seconds: float
    verdict: str  # identical | path | timeout | crash | transport | other
    detail: str = ""


def _loader() -> Any:
    return getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def _compute_entries(
    cache_file: Path,
) -> list[tuple[str, dict[str, Any], str]]:
    """`(fun, args, archived_output)` for every bridge compute entry."""
    raw: Any = yaml.load(cache_file.read_text(), Loader=_loader())
    out: list[tuple[str, dict[str, Any], str]] = []
    for e in cast(list[dict[str, Any]], raw):
        req = cast(dict[str, Any], e["input"]["request"])
        if cast(dict[str, Any], req.get("options", {})).get("model") != (
            "__compute__"
        ):
            continue
        chat = cast(list[dict[str, Any]], req["chat"])
        q = cast(dict[str, Any], yaml.safe_load(chat[0]["content"]))
        fun = str(q["fun"])
        if fun not in BRIDGE_FUNS:
            continue
        outputs = cast(list[dict[str, Any]], e["output"]["outputs"])
        out.append(
            (fun, cast(dict[str, Any], q["args"]), str(outputs[0]["content"]))
        )
    return out


def _normalise_paths(text: str) -> str:
    text = _AUG_PATH_RE.sub("<AUG>", text)
    return _STABLE_PATH_RE.sub("<AUG>", text)


def _classify(
    archived: str, fresh: str, had_exception: bool
) -> tuple[str, str]:
    if archived == fresh:
        return "identical", ""
    if _normalise_paths(archived) == _normalise_paths(fresh):
        return "path", "augmented path differs"
    if "Timeout" in archived or "Timeout" in fresh or "Deadline" in fresh:
        return "timeout", "timeout verdict differs"
    if "No response from pet process" in archived:
        # The archived STDIO `pet` died mid-call (OOM / stack overflow)
        # and the bridge recorded a dead pipe; the bounded server now
        # reports Rocq's own error or a transport failure instead.
        return "crash", "archived pet process died; new verdict is explicit"
    if "transport failure" in fresh or pt.GOALS_OVERFLOW_MARKER in fresh:
        kind = "archived cell crashed" if had_exception else "runaway state"
        return "transport", kind
    # First differing line, for the report.
    a_lines, f_lines = archived.splitlines(), fresh.splitlines()
    for i, (a, b) in enumerate(zip(a_lines, f_lines)):
        if a != b:
            return "other", f"line {i + 1}: {a[:80]!r} != {b[:80]!r}"
    return "other", f"length {len(a_lines)} vs {len(f_lines)} lines"


def run_config(config_dir: Path, funs: tuple[str, ...]) -> list[Outcome]:
    entries = _compute_entries(config_dir / "cache.yaml")
    had_exception = (config_dir / "exception.txt").exists()
    outcomes: list[Outcome] = []
    for fun, args, archived in entries:
        if fun not in funs:
            continue
        f = getattr(pt, fun)
        ret_type = insp.function_return_type(f)
        t0 = time.perf_counter()
        fresh = dump_yaml(ret_type, f(**args))
        dt = time.perf_counter() - t0
        verdict, detail = _classify(archived, fresh, had_exception)
        outcomes.append(Outcome(config_dir.name, fun, dt, verdict, detail))
    return outcomes


def main() -> int:
    # Parity must *re-execute* every archived call: a repeat served
    # from the check-result memo would mask a transport regression.
    # An explicit OMPHALOS_CHECK_MEMO=1 still allows memo-on parity.
    os.environ.setdefault("OMPHALOS_CHECK_MEMO", "0")
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--run", required=True, help="experiments/output/<run>")
    ap.add_argument(
        "--config",
        action="append",
        default=[],
        help="config dir name (repeatable)",
    )
    ap.add_argument("--limit", type=int, default=None, help="first N configs")
    ap.add_argument("--funs", default=",".join(BRIDGE_FUNS))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    funs = tuple(s.strip() for s in str(args.funs).split(","))
    run_dir = _OMPHALOS_DIR / "experiments" / "output" / str(args.run)
    configs = sorted(p for p in (run_dir / "configs").iterdir() if p.is_dir())
    if args.config:
        wanted = set(cast(list[str], args.config))
        configs = [c for c in configs if c.name in wanted]
    if args.limit is not None:
        configs = configs[: int(args.limit)]
    print(
        f"bridge parity: run={args.run} configs={len(configs)} "
        f"mode={rocq_server.pet_mode()} funs={','.join(funs)}"
    )
    all_out: list[Outcome] = []
    for i, c in enumerate(configs, 1):
        t0 = time.perf_counter()
        out = run_config(c, funs)
        all_out.extend(out)
        counts = {
            v: sum(1 for o in out if o.verdict == v)
            for v in (
                "identical",
                "path",
                "timeout",
                "crash",
                "transport",
                "other",
            )
        }
        print(
            f"  [{i}/{len(configs)}] {c.name}: {len(out)} calls in "
            f"{time.perf_counter() - t0:.1f}s  {counts}",
            flush=True,
        )
        if args.verbose:
            for o in out:
                if o.verdict != "identical":
                    print(f"      {o.fun:15s} {o.verdict:9s} {o.detail}")
    if not all_out:
        print("no bridge calls found")
        return 0
    secs = [o.seconds for o in all_out]
    print(
        f"\n{len(all_out)} calls: median {statistics.median(secs) * 1000:.0f} ms, "
        f"p95 {sorted(secs)[int(0.95 * (len(secs) - 1))]:.2f} s, "
        f"max {max(secs):.1f} s, total {sum(secs):.1f} s"
    )
    for v in ("identical", "path", "timeout", "crash", "transport", "other"):
        n = sum(1 for o in all_out if o.verdict == v)
        if n:
            print(f"  {v:9s} {n}")
    others = [o for o in all_out if o.verdict == "other"]
    for o in others[:20]:
        print(f"  OTHER {o.config} {o.fun}: {o.detail}")
    st = rocq_server.MANAGER.stats()
    print(f"server: {st}")
    return 1 if others else 0


if __name__ == "__main__":
    raise SystemExit(main())
