"""
Shared construction of ACE evaluation cells on the X partitions.

An evaluation cell is the canonical luna configuration
(`minif2f_x.XAgenticConfig`'s knobs) plus a frozen playbook, rendered
with the render version the playbook was *adapted* under (from its
`.provenance.yaml` sidecar), definitions shown, and is paired against
the baseline cell of the same problem and seed in
`experiments/output/x_{validation,test}_agentic`.

Flags, parsed ONCE at import into `SELECTION` (and stripped from
`sys.argv` before `fire` sees them):

- `--playbook=<file under experiments/playbooks/>` — the frozen
  playbook; its sha256 is part of the config identity and of the
  directory name.
- `--injection=full|top<k>` — injection mode (default `full`).
- `--render_version=N` — override the provenance render version
  (deliberate ablations only; a warning is printed when it is lower
  than the version the playbook was adapted under).

History (2026-08-26 audit): the previous `_flag` helper removed the
flag from `sys.argv` on its first read, so the *second* call — inside
`ace_x_configs` — silently fell back to the default `ace_x_offline.yaml`;
both "v3" evaluation directories of 2026-08-25/26 therefore evaluated
the v2 playbook, and `render_version` was hard-coded to 2 regardless of
the playbook. Parsing once, taking the render version from provenance,
suffixing the directory with `_rv{N}` and refusing a directory that
holds cells of another playbook (`announce`) close all three holes.
"""

# pyright: strict

import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml

import minif2f_x as x
from ace_bench import ACEAgenticConfig

_OMPHALOS_DIR = Path(__file__).resolve().parent.parent
PLAYBOOKS_DIR = _OMPHALOS_DIR / "experiments" / "playbooks"

if str(_OMPHALOS_DIR) not in sys.path:
    sys.path.insert(0, str(_OMPHALOS_DIR))

from ace_playbook import Playbook  # noqa: E402

DEFAULT_PLAYBOOK = "ace_x_offline.yaml"
FALLBACK_RENDER_VERSION = 2
"""Render version for playbooks without a provenance sidecar (v1/v2
files frozen before sidecars existed were all evaluated at 2)."""

RenderSource = Literal["provenance", "override", "fallback"]


@dataclass(frozen=True)
class EvalSelection:
    playbook_name: str
    playbook_file: str
    """Relative path (`experiments/playbooks/<name>`), the config field."""
    sha256: str
    injection: str
    render_version: int
    render_source: RenderSource

    @property
    def sha8(self) -> str:
        return self.sha256[:8]

    @property
    def stem(self) -> str:
        return Path(self.playbook_name).stem


def _take_flag(name: str) -> str | None:
    """Remove every `--<name>=` occurrence from argv; return the last."""
    prefix = f"--{name}="
    value: str | None = None
    for arg in list(sys.argv[1:]):
        if arg.startswith(prefix):
            value = arg[len(prefix) :]
            sys.argv.remove(arg)
    return value


def provenance(playbook_name: str) -> dict[str, Any]:
    """The frozen playbook's `.provenance.yaml` sidecar, or `{}`."""
    path = PLAYBOOKS_DIR / f"{Path(playbook_name).stem}.provenance.yaml"
    if not path.exists():
        return {}
    raw: Any = yaml.safe_load(path.read_text())
    return cast(dict[str, Any], raw or {})


def _parse_selection() -> EvalSelection:
    name = _take_flag("playbook") or DEFAULT_PLAYBOOK
    injection = _take_flag("injection") or "full"
    override = _take_flag("render_version")
    path = PLAYBOOKS_DIR / name
    assert path.exists(), f"{path} is not a frozen playbook"
    assert injection == "full" or injection.startswith("top"), injection
    prov = provenance(name)
    prov_rv = prov.get("render_version")
    if override is not None:
        rv, source = int(override), cast(RenderSource, "override")
    elif prov_rv is not None:
        rv, source = int(prov_rv), cast(RenderSource, "provenance")
    else:
        rv, source = FALLBACK_RENDER_VERSION, cast(RenderSource, "fallback")
    assert rv in (1, 2, 3), f"render_version {rv} is not one of 1, 2, 3"
    if prov_rv is not None and rv < int(prov_rv):
        print(
            f"WARNING: evaluating {name} (adapted at render_version "
            f"{prov_rv}) at render_version {rv} — a deliberate ablation "
            "of the prompt the playbook was adapted under.",
            file=sys.stderr,
        )
    return EvalSelection(
        playbook_name=name,
        playbook_file=f"experiments/playbooks/{name}",
        sha256=Playbook.load(path).sha256(),
        injection=injection,
        render_version=rv,
        render_source=source,
    )


SELECTION: EvalSelection = _parse_selection()
"""Parsed once, at import, before `fire` reads `sys.argv`."""


def selected_playbook() -> tuple[str, str]:
    """`(relative playbook file, sha256)` — the parsed selection."""
    return SELECTION.playbook_file, SELECTION.sha256


def selected_injection() -> str:
    return SELECTION.injection


def arm_output_dir(part: str, sel: EvalSelection = SELECTION) -> str:
    """
    Per-arm experiment directory: one `Experiment` state file per arm
    (arms evaluate concurrently), named by playbook stem, injection
    and render version. The pre-2026-08-26 directories without the
    `_rv{N}` suffix hold the mis-run cells and are never written again.
    """
    suffix = "" if sel.injection == "full" else f"_{sel.injection}"
    return (
        f"experiments/output/ace_x_{part}_{sel.stem}{suffix}"
        f"_rv{sel.render_version}_agentic"
    )


def ace_x_configs(
    problems: Mapping[str, tuple[str, str]],
    seeds: Sequence[int],
    sel: EvalSelection = SELECTION,
) -> list[ACEAgenticConfig]:
    return [
        ACEAgenticConfig(
            bench_name=name,
            model_name=x.X_MODEL,
            temperature=None,
            toolset=x.X_TOOLSET,
            num_requests=x.X_NUM_REQUESTS,
            loop=False,
            seed=seed,
            max_dollar_budget=x.X_DOLLAR_CAP,
            reasoning_effort=x.X_EFFORT,
            playbook_file=sel.playbook_file,
            playbook_sha256=sel.sha256,
            injection=sel.injection,
            render_version=sel.render_version,
            show_definitions=True,
        )
        for seed in seeds
        for name in problems
    ]


def announce(output_dir: str, sel: EvalSelection = SELECTION) -> None:
    """
    Print the resolved arm and refuse to touch a directory whose
    recorded cells pin another playbook / render version / injection.
    """
    print(
        f"ACE eval arm: playbook={sel.playbook_file} sha={sel.sha8} "
        f"render_version={sel.render_version} ({sel.render_source}) "
        f"injection={sel.injection} output_dir={output_dir}",
        flush=True,
    )
    state = _OMPHALOS_DIR / output_dir / "experiment.yaml"
    if not state.exists():
        return
    raw: Any = yaml.safe_load(state.read_text())
    state_map = cast(dict[str, Any], raw or {})
    configs = cast(dict[str, dict[str, Any]], state_map.get("configs", {}))
    offending: dict[tuple[str, int, str], int] = {}
    for info in configs.values():
        params = cast(dict[str, Any], info.get("params", {}))
        key = (
            str(params.get("playbook_sha256", ""))[:8],
            int(params.get("render_version", 1)),
            str(params.get("injection", "full")),
        )
        if key != (sel.sha8, sel.render_version, sel.injection):
            offending[key] = offending.get(key, 0) + 1
    if offending:
        rows = ", ".join(
            f"sha={s} rv={r} injection={i} ×{n}"
            for (s, r, i), n in sorted(offending.items())
        )
        print(
            f"REFUSING: {output_dir} already holds cells of another arm "
            f"({rows}); one arm per directory.",
            file=sys.stderr,
        )
        raise SystemExit(3)
