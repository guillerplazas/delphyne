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
- `--injection=full|top<k>|triggered` — injection mode (default
  `full`). `triggered` is hint on error (2026-09-05): no playbook in
  the prompt, bullets attached to matching verifier rejections; it
  needs `--triggers=<file under experiments/playbooks/>` (default
  `<playbook stem>.triggers.yaml`) and takes `--max_hints=K`
  (default 3). Such cells are `ACETriggeredConfig`s in a
  `acet_x_<part>_<stem>_k<K>_agentic` directory.
- `--render_version=N` — override the provenance render version
  (deliberate ablations only; a warning is printed when it is lower
  than the version the playbook was adapted under).
- `--seeds=0,1` — which seeds to register (default both); a
  seed-0-first protocol registers seed 0, reads it, then adds seed 1
  to the same directory (the launcher only adds new cells).

History (2026-08-26 audit): the previous `_flag` helper removed the
flag from `sys.argv` on its first read, so the *second* call — inside
`ace_x_configs` — silently fell back to the default `ace_x_offline.yaml`;
both "v3" evaluation directories of 2026-08-25/26 therefore evaluated
the v2 playbook, and `render_version` was hard-coded to 2 regardless of
the playbook. Parsing once, taking the render version from provenance,
suffixing the directory with `_rv{N}` and refusing a directory that
holds cells of another playbook (`announce`) close all three holes.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict

import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml

import experiments.common.minif2f_x as x
from experiments.common.ace_bench import (
    ACEAgenticConfig,
    ACETriggeredConfig,
    ace_config_name,
    acet_config_name,
)


from ace.ace_playbook import Playbook  # noqa: E402
from ace.ace_triggers import (  # noqa: E402
    DEFAULT_MAX_HINTS,
    DEFAULT_SELECTION_RULE,
    TriggerTable,
)

_OMPHALOS_DIR = OMPHALOS_ROOT
PLAYBOOKS_DIR = _OMPHALOS_DIR / "experiments" / "playbooks"

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
    triggers_file: str = ""
    """Relative path of the frozen trigger table (`triggered` only)."""
    triggers_sha256: str = ""
    max_hints: int = DEFAULT_MAX_HINTS
    selection_rule: int = DEFAULT_SELECTION_RULE
    seeds: tuple[int, ...] = (0, 1)

    @property
    def sha8(self) -> str:
        return self.sha256[:8]

    @property
    def triggered(self) -> bool:
        return self.injection == "triggered"

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


def _parse_seeds(raw: str | None) -> tuple[int, ...]:
    if raw is None:
        return (0, 1)
    seeds = tuple(int(x) for x in raw.split(",") if x.strip())
    assert seeds and len(set(seeds)) == len(seeds), f"--seeds={raw!r}"
    return seeds


def _parse_selection() -> EvalSelection:
    name = _take_flag("playbook") or DEFAULT_PLAYBOOK
    injection = _take_flag("injection") or "full"
    override = _take_flag("render_version")
    triggers_flag = _take_flag("triggers")
    max_hints_flag = _take_flag("max_hints")
    rule_flag = _take_flag("selection_rule")
    seeds = _parse_seeds(_take_flag("seeds"))
    path = PLAYBOOKS_DIR / name
    assert path.exists(), f"{path} is not a frozen playbook"
    assert injection in ("full", "triggered") or injection.startswith("top"), (
        injection
    )
    triggers_file = ""
    triggers_sha = ""
    max_hints = DEFAULT_MAX_HINTS
    rule = DEFAULT_SELECTION_RULE
    if injection == "triggered":
        tname = triggers_flag or f"{Path(name).stem}.triggers.yaml"
        tpath = PLAYBOOKS_DIR / tname
        assert tpath.exists(), f"{tpath} is not a frozen trigger table"
        table = TriggerTable.load(tpath)
        pb_sha = Playbook.load(path).sha256()
        assert table.playbook_sha256 == pb_sha, (
            f"{tname} was built for playbook {table.playbook_sha256[:8]},"
            f" not {name} ({pb_sha[:8]})"
        )
        triggers_file = f"experiments/playbooks/{tname}"
        triggers_sha = table.sha256()
        if max_hints_flag is not None:
            max_hints = int(max_hints_flag)
            assert max_hints >= 1, max_hints
        if rule_flag is not None:
            rule = int(rule_flag)
            assert rule in (1, 2), rule
    else:
        assert (
            triggers_flag is None
            and max_hints_flag is None
            and rule_flag is None
        ), (
            "--triggers / --max_hints / --selection_rule only apply to"
            " --injection=triggered"
        )
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
        triggers_file=triggers_file,
        triggers_sha256=triggers_sha,
        max_hints=max_hints,
        selection_rule=rule,
        seeds=seeds,
    )


SELECTION: EvalSelection = _parse_selection()
"""Parsed once, at import, before `fire` reads `sys.argv`."""


def selected_playbook() -> tuple[str, str]:
    """`(relative playbook file, sha256)` — the parsed selection."""
    return SELECTION.playbook_file, SELECTION.sha256


def selected_injection() -> str:
    return SELECTION.injection


def selected_seeds() -> tuple[int, ...]:
    return SELECTION.seeds


def config_class(
    sel: EvalSelection = SELECTION,
) -> type[ACEAgenticConfig]:
    """The exact config class of the arm (the launcher loads state
    with it, so a triggered arm must not be read as a full one)."""
    return ACETriggeredConfig if sel.triggered else ACEAgenticConfig


def config_naming(
    sel: EvalSelection = SELECTION,
) -> Callable[[Any, Any], str]:
    return acet_config_name if sel.triggered else ace_config_name


def arm_output_dir(part: str, sel: EvalSelection = SELECTION) -> str:
    """
    Per-arm experiment directory: one `Experiment` state file per arm
    (arms evaluate concurrently), named by playbook stem, injection
    and render version. The pre-2026-08-26 directories without the
    `_rv{N}` suffix hold the mis-run cells and are never written again.
    """
    if sel.triggered:
        # Outside the `ace_x_*_agentic` glob of the frozen-playbook
        # report tools on purpose (see `ace_bench.ACET_ARM_RE`).
        rule = (
            ""
            if sel.selection_rule == DEFAULT_SELECTION_RULE
            else f"_r{sel.selection_rule}"
        )
        return (
            f"experiments/output/acet_x_{part}_{sel.stem}"
            f"_k{sel.max_hints}{rule}_agentic"
        )
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
    common: dict[str, Any] = dict(
        model_name=x.X_MODEL,
        temperature=None,
        toolset=x.X_TOOLSET,
        num_requests=x.X_NUM_REQUESTS,
        loop=False,
        max_dollar_budget=x.X_DOLLAR_CAP,
        reasoning_effort=x.X_EFFORT,
        playbook_file=sel.playbook_file,
        playbook_sha256=sel.sha256,
        injection=sel.injection,
        render_version=sel.render_version,
        show_definitions=True,
    )
    if sel.triggered:
        return [
            ACETriggeredConfig(
                bench_name=name,
                seed=seed,
                triggers_file=sel.triggers_file,
                triggers_sha256=sel.triggers_sha256,
                max_hints=sel.max_hints,
                selection_rule=sel.selection_rule,
                **common,
            )
            for seed in seeds
            for name in problems
        ]
    return [
        ACEAgenticConfig(bench_name=name, seed=seed, **common)
        for seed in seeds
        for name in problems
    ]


def announce(output_dir: str, sel: EvalSelection = SELECTION) -> None:
    """
    Print the resolved arm and refuse to touch a directory whose
    recorded cells pin another playbook / render version / injection.
    """
    trig = (
        f" triggers={sel.triggers_file} tsha={sel.triggers_sha256[:8]}"
        f" max_hints={sel.max_hints} selection_rule={sel.selection_rule}"
        if sel.triggered
        else ""
    )
    print(
        f"ACE eval arm: playbook={sel.playbook_file} sha={sel.sha8} "
        f"render_version={sel.render_version} ({sel.render_source}) "
        f"injection={sel.injection}{trig} seeds={list(sel.seeds)} "
        f"output_dir={output_dir}",
        flush=True,
    )
    state = _OMPHALOS_DIR / output_dir / "experiment.yaml"
    if not state.exists():
        return
    raw: Any = yaml.safe_load(state.read_text())
    state_map = cast(dict[str, Any], raw or {})
    configs = cast(dict[str, dict[str, Any]], state_map.get("configs", {}))
    offending: dict[tuple[str, int, str, str, int], int] = {}
    mine = (
        sel.sha8,
        sel.render_version,
        sel.injection,
        sel.triggers_sha256[:8],
        sel.selection_rule if sel.triggered else DEFAULT_SELECTION_RULE,
    )
    for info in configs.values():
        params = cast(dict[str, Any], info.get("params", {}))
        key = (
            str(params.get("playbook_sha256", ""))[:8],
            int(params.get("render_version", 1)),
            str(params.get("injection", "full")),
            str(params.get("triggers_sha256", ""))[:8],
            int(params.get("selection_rule", DEFAULT_SELECTION_RULE)),
        )
        if key != mine:
            offending[key] = offending.get(key, 0) + 1
    if offending:
        rows = ", ".join(
            f"sha={s} rv={r} injection={i} tsha={t} rule={u} ×{n}"
            for (s, r, i, t, u), n in sorted(offending.items())
        )
        print(
            f"REFUSING: {output_dir} already holds cells of another arm "
            f"({rows}); one arm per directory.",
            file=sys.stderr,
        )
        raise SystemExit(3)
