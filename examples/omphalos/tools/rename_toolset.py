"""
One-off migration: rename the `lean` toolset to `core` in archived
experiment output.

Why this exists. The toolset name is a *strategy argument*, so it ends
up in three places that outlive a run: the config directory name (via
each experiment's `config_naming` lambda), the `toolset` field stored in
`experiment.yaml` / `results_summary*.csv` / `result.yaml`, and the
`cache_file` paths recorded inside `result.yaml`. Renaming the literal
in `prove_agentic.py` without moving those makes every archived run
unreachable: `tools/report_chart_data.py` asserts the cache path exists,
and `tools/decision_audit.py` selects rows by the column value.

Why it is safe. The toolset name never reaches the model — the only
template branch (`ProposeProofScriptAgentic.system.jinja`) tests
`"probing"`, and tool sections render from `advertised_tools()`.
Archived `cache.yaml` files contain zero word-boundary `lean` (every
match is the word "cleanly" in the feedback prompt), so **no LLM cache
is touched and nothing needs re-running**. This script deliberately
never opens a `cache.yaml`.

Usage:
    python tools/rename_toolset.py            # dry run, prints a plan
    python tools/rename_toolset.py --apply
"""

# pyright: strict

import re
import sys
from pathlib import Path

OLD = "lean"
NEW = "core"

ROOTS = (Path("experiments/output"), Path("experiments/previous"))

# `lean` as a whole word: the CSV column value, the `toolset:` YAML
# field, and prose in NOTES/report files. Never matches "cleanly".
WORD = re.compile(rf"(?<![A-Za-z]){OLD}(?![A-Za-z])")

# `__lean` / `__lean-medium` as a config-name segment. The preceding
# underscore is a word character, so `WORD` alone would miss these.
SEGMENT = re.compile(rf"__{OLD}(?=__|-)")


def _rewrite(path: Path, apply: bool) -> bool:
    """Rewrite one text file in place. Returns True if it changed."""
    text = path.read_text()
    new = SEGMENT.sub(f"__{NEW}", WORD.sub(NEW, text))
    if new == text:
        return False
    if apply:
        path.write_text(new)
    return True


def main() -> None:
    apply = "--apply" in sys.argv[1:]

    # 1. Directories, deepest first so parents are renamed last.
    dirs = sorted(
        (d for root in ROOTS for d in root.rglob(f"*{OLD}*") if d.is_dir()),
        key=lambda d: len(d.parts),
        reverse=True,
    )
    renamed = 0
    for d in dirs:
        name = SEGMENT.sub(f"__{NEW}", WORD.sub(NEW, d.name))
        if name == d.name:
            continue
        target = d.with_name(name)
        assert not target.exists(), f"target already exists: {target}"
        print(f"  dir  {d} -> {name}")
        if apply:
            d.rename(target)
        renamed += 1

    # 2. Manifests, summaries, per-config results and notes. `cache.yaml`
    #    is excluded by name -- see the module docstring.
    patterns = (
        "*/experiment.yaml",
        "*/results_summary*.csv",
        "*/configs/*/result.yaml",
        "*/NOTES.txt",
        "README.txt",
        "decision_audit/report.md",
    )
    touched = 0
    for root in ROOTS:
        for pattern in patterns:
            for f in sorted(root.glob(pattern)):
                assert f.name != "cache.yaml"
                if _rewrite(f, apply):
                    touched += 1

    verb = "renamed" if apply else "would rename"
    print(f"\n{verb} {renamed} directories, {touched} files rewritten")
    if not apply:
        print("dry run -- pass --apply to perform the migration")


if __name__ == "__main__":
    main()
