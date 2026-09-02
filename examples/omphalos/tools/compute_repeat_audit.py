"""
Audit repeated identical compute calls in archived experiment caches.

The stdlib compute cache keys entries by `(request, iter)` — the
occurrence index — so a byte-identical `check_assisted` request that an
agent repeats is *re-executed* and recorded again. This tool answers
the question an in-process check-result memo depends on: **do repeated
identical compute requests ever record different outputs?** If they
never do, returning the first recorded result for a repeated request is
provably neutral on the archive (`tools/bridge_parity.py` then proves
it live).

Usage:
    python tools/compute_repeat_audit.py [dir ...]

With no arguments, every `experiments/output/*/configs/*/cache.yaml`
is scanned. Exit code 0 iff no repeated request diverges.
"""

# pyright: strict

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

import yaml

OMPHALOS_DIR = Path(__file__).resolve().parent.parent
_LOADER: Any = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def _compute_entries(cache_file: Path) -> list[tuple[str, str]]:
    """`(request_content, output_repr)` for every `__compute__` entry."""
    try:
        with cache_file.open() as f:
            data: Any = yaml.load(f, Loader=_LOADER)
    except Exception as e:
        print(f"  UNREADABLE {cache_file}: {e}")
        return []
    out: list[tuple[str, str]] = []
    if not isinstance(data, list):
        return out
    for entry in cast(list[Any], data):
        if not isinstance(entry, dict):
            continue
        entry = cast(dict[str, Any], entry)
        req = entry.get("input", {}).get("request", {})
        if req.get("options", {}).get("model") != "__compute__":
            continue
        chat = req.get("chat", [])
        content = "".join(str(m.get("content", "")) for m in chat)
        out.append((content, repr(entry.get("output"))))
    return out


def audit_dir(exp_dir: Path) -> tuple[int, int, int, list[str]]:
    """`(calls, repeated_calls, divergent_groups, divergent_names)`."""
    calls = repeated = divergent = 0
    divergent_names: list[str] = []
    for cache_file in sorted(exp_dir.glob("configs/*/cache.yaml")):
        groups: dict[str, list[str]] = defaultdict(list)
        for content, output in _compute_entries(cache_file):
            groups[content].append(output)
        for content, outputs in groups.items():
            calls += len(outputs)
            if len(outputs) > 1:
                repeated += len(outputs) - 1
                if len(set(outputs)) > 1:
                    divergent += 1
                    fun = content.split("\n", 1)[0]
                    divergent_names.append(
                        f"{cache_file.parent.name}: {fun} "
                        f"({len(set(outputs))} distinct of {len(outputs)})"
                    )
    return calls, repeated, divergent, divergent_names


def main(argv: list[str]) -> int:
    if argv:
        dirs = [Path(a).resolve() for a in argv]
    else:
        dirs = sorted(
            d
            for d in (OMPHALOS_DIR / "experiments" / "output").iterdir()
            if d.is_dir() and (d / "configs").is_dir()
        )
    total_calls = total_repeated = total_divergent = 0
    for d in dirs:
        calls, repeated, divergent, names = audit_dir(d)
        if calls == 0:
            continue
        total_calls += calls
        total_repeated += repeated
        total_divergent += divergent
        flag = " DIVERGENT" if divergent else ""
        print(
            f"{d.name}: {calls} compute calls, {repeated} repeats, "
            f"{divergent} divergent group(s){flag}"
        )
        for n in names:
            print(f"  {n}")
    print(
        f"TOTAL: {total_calls} calls, {total_repeated} repeats, "
        f"{total_divergent} divergent group(s)"
    )
    return 1 if total_divergent else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
