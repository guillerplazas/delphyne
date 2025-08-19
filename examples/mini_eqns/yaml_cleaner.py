#!/usr/bin/env python
"""
clean_delphyne_yaml.py  –  strip usage/budget fields from Delphyne YAML outputs
while *preserving original formatting* (flow lists, comments, etc.).

Requires:  pip install ruamel.yaml

Usage (same as before):
    python clean_delphyne_yaml.py REL_PATH_FROM_RESULT_DIR
"""

from pathlib import Path
import argparse
import sys
from typing import Any, Union

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
DEFAULT_RESULT_DIR = HERE / "experiments_baseline/ex_01.yaml"      # adjust if needed

USAGE_KEYS = {"spent_budget", "budget", "usage_info"}   # top‑level resource keys
METADATA_USAGE_KEY = "usage"                            # nested metadata.usage


# ---------------------------------------------------------------------------
# Cleaning logic
# ---------------------------------------------------------------------------

Mapping = CommentedMap
Sequence = CommentedSeq
YNode    = Union[Mapping, Sequence, Any]


def remove_usage_fields(node: YNode) -> None:
    """
    Recursively delete usage/budget fields **in‑place** from a ruamel structure.
    """
    if isinstance(node, Mapping):
        # work on a static list of keys to avoid runtime size change issues
        for k in list(node.keys()):
            if k in USAGE_KEYS:
                del node[k]
                continue

            # special case: metadata.usage
            if k == "metadata" and isinstance(node[k], Mapping):
                node[k].pop(METADATA_USAGE_KEY, None)
                remove_usage_fields(node[k])
                continue

            remove_usage_fields(node[k])

    elif isinstance(node, Sequence):
        for item in node:
            remove_usage_fields(item)
    # scalars → nothing to do


# ---------------------------------------------------------------------------
# Main helpers
# ---------------------------------------------------------------------------

def clean_file(src: Path, suffix: str = "_clean") -> Path:
    """
    Round‑trip load, clean, and dump YAML while preserving formatting.
    """
    if not src.is_file():
        raise FileNotFoundError(src)

    # Round‑trip YAML loader/dumper
    ryaml = YAML(typ='rt')          # 'rt' = round‑trip
    ryaml.preserve_quotes = True    # keep quotes as in source
    ryaml.width = 4096              # long line width so flow lists stay inline
    ryaml.sort_base_mapping_type_on_output = False  # keep original order

    with src.open("r", encoding="utf-8") as f:
        docs = list(ryaml.load_all(f))

    for doc in docs:
        remove_usage_fields(doc)

    # create output path
    if src.suffix in {".yaml", ".yml"}:
        dst = src.with_name(src.stem + suffix + ".yaml")
    else:
        dst = src.with_name(src.name + suffix + ".yaml")

    with dst.open("w", encoding="utf-8") as f:
        ryaml.dump_all(docs, f)

    return dst


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    """
    parser = argparse.ArgumentParser(
        description="Clean Delphyne YAML output, preserving formatting.")
    parser.add_argument("rel_path",
                        help="Relative path (from --root) to YAML file.")
    parser.add_argument("--root", type=Path, default=DEFAULT_RESULT_DIR,
                        help=f"Base directory (default: {DEFAULT_RESULT_DIR})")
    parser.add_argument("--suffix", default="_clean",
                        help="Suffix inserted before .yaml (default: _clean)")
    args = parser.parse_args(argv)

    target = (args.root / args.rel_path).resolve()
    """
    target = HERE / "experiments_baseline" / "ex_01.yaml"
    try:
        out = clean_file(target)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Cleaned YAML written to: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
