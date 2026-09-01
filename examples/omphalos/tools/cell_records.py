"""
Ground-truth cell records of an experiment directory (no CSV needed).

`results_summary.csv` is written by the stdlib launcher only when
every config is done, and lists done configs only — so the report
tooling that read it (a) saw nothing in a directory with one failed
cell and (b) silently dropped every platform-failed cell from every
pairing (2026-08-26 audit, finding A4). This module reads
`experiment.yaml` plus each config directory instead:

- a config with a complete `result.yaml` is a **done** cell (solved or
  not, with its token counts and repriced cost);
- a config with `exception.txt` and no result is a **failed** cell:
  scored UNSOLVED with `platform_failed=True`, its spend recovered
  from the cached requests when the cache survived;
- a `todo` config is not a cell.

Costs are recomputed from token counts at today's dated rate
(`model_registry.pricing_for`), never read from the archive.
"""

# pyright: strict

import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_OMPHALOS_DIR))
sys.path.insert(0, str(_OMPHALOS_DIR / "experiments"))
sys.path.insert(0, str(_OMPHALOS_DIR / "tools"))

from model_registry import pricing_for  # noqa: E402

import omphalos_launch as ol  # noqa: E402

_HEAD_BYTES = 65536
_NAME_RE = re.compile(
    r"^(?P<bench>.+?)__(?P<arm>.+?)__(?P<model>.+?)__seed(?P<seed>\d+)$"
)


@dataclass(frozen=True)
class CellRecord:
    name: str
    bench: str
    seed: str
    arm: str
    model: str
    params: dict[str, Any]
    status: Literal["done", "failed"]
    solved: bool
    input: int
    cached: int
    output: int
    requests: int
    cost: float
    platform_failed: bool

    @property
    def cell(self) -> tuple[str, str]:
        return (self.bench, self.seed)

    def as_dict(self) -> dict[str, Any]:
        return {
            "solved": self.solved,
            "cost": self.cost,
            "input": self.input,
            "cached": self.cached,
            "output": self.output,
            "requests": self.requests,
            "platformFailed": self.platform_failed,
        }


def _field(head: str, key: str) -> str | None:
    m = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", head, re.M)
    return m.group(1) if m else None


def _result_head(path: Path) -> str:
    with path.open("rb") as f:
        return f.read(_HEAD_BYTES).decode(errors="replace")


def _price(model: str, inp: int, cached: int, out: int) -> float:
    rates = pricing_for(model)
    return (
        (inp - cached) * rates.dollars_per_input_token
        + cached * rates.dollars_per_cached_input_token
        + out * rates.dollars_per_output_token
    )


def _done_record(
    name: str, m: "re.Match[str]", params: dict[str, Any], path: Path
) -> CellRecord:
    head = _result_head(path)
    spent_block = (
        head[head.find("spent_budget:") :] if "spent_budget:" in head else ""
    )
    success = (_field(head, "success") or "false").lower() == "true"
    inp = int(_field(spent_block, "input_tokens") or 0)
    cached = int(_field(spent_block, "cached_input_tokens") or 0)
    outp = int(_field(spent_block, "output_tokens") or 0)
    reqs = int(float(_field(spent_block, "num_completions") or 0))
    model = m.group("model")
    return CellRecord(
        name=name,
        bench=m.group("bench"),
        seed=m.group("seed"),
        arm=m.group("arm"),
        model=model,
        params=params,
        status="done",
        solved=success,
        input=inp,
        cached=cached,
        output=outp,
        requests=reqs,
        cost=_price(model, inp, cached, outp),
        platform_failed=False,
    )


def _failed_record(
    name: str, m: "re.Match[str]", params: dict[str, Any], config_dir: Path
) -> CellRecord:
    """A platform-failed cell: unsolved; spend from the surviving cache."""
    inp = cached = outp = reqs = 0
    cache = config_dir / "cache.yaml"
    model = m.group("model")
    if cache.exists():
        try:
            loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
            with cache.open() as f:
                raw: Any = yaml.load(f, Loader=loader)  # type: ignore[reportUnknownMemberType]
            for entry in cast(list[dict[str, Any]], raw or []):
                output = cast(dict[str, Any] | None, entry.get("output"))
                budget = cast(
                    dict[str, Any] | None,
                    output.get("budget") if output else None,
                )
                values = cast(
                    dict[str, Any], (budget or {}).get("values") or {}
                )
                if "price" not in values:
                    continue
                inp += int(values.get("input_tokens", 0))
                cached += int(values.get("cached_input_tokens", 0))
                outp += int(values.get("output_tokens", 0))
                reqs += 1
        except Exception:
            pass
    return CellRecord(
        name=name,
        bench=m.group("bench"),
        seed=m.group("seed"),
        arm=m.group("arm"),
        model=model,
        params=params,
        status="failed",
        solved=False,
        input=inp,
        cached=cached,
        output=outp,
        requests=reqs,
        cost=_price(model, inp, cached, outp),
        platform_failed=True,
    )


def cells_of_run(run: Path) -> Iterator[CellRecord]:
    state = run / "experiment.yaml"
    if not state.exists():
        return
    raw: Any = yaml.safe_load(state.read_text())
    state_map = cast(dict[str, Any], raw or {})
    configs = cast(dict[str, dict[str, Any]], state_map.get("configs", {}))
    for name, info in configs.items():
        m = _NAME_RE.match(name)
        if m is None:
            continue
        params = cast(dict[str, Any], info.get("params", {}))
        config_dir = run / "configs" / name
        truth = ol.ground_truth(config_dir)
        if truth == "done":
            yield _done_record(name, m, params, config_dir / "result.yaml")
        elif truth == "failed":
            yield _failed_record(name, m, params, config_dir)
