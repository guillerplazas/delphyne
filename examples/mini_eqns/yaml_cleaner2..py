#!/usr/bin/env python
"""
clean_ex_01_yaml.py
    • strips usage/budget fields
    • collapses few‑shot payloads under *answers*, *examples*, or any key
      that holds a list of {answer: …} or {role/content: …} mappings.
"""

from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

HERE   = Path(__file__).resolve().parent
TARGET = HERE / "experiments_baseline" / "ex_01.yaml"

USAGE_KEYS            = {"spent_budget", "budget", "usage_info"}
METADATA_USAGE_SUBKEY = "usage"

DICT = (dict, CommentedMap)
LIST = (list, CommentedSeq)

# ---------------------------------------------------------------------------
# Helper: recognise a few‑shot list
# ---------------------------------------------------------------------------

def is_fewshot_list(lst):
    """Return True iff lst is a list of mappings each recording an example."""
    if not isinstance(lst, LIST) or not lst:
        return False
    for item in lst:
        if not isinstance(item, DICT):
            return False
        if "answer" in item:
            continue
        if {"role", "content"}.issubset(item):
            continue
        # Something else → not a demo list
        return False
    return True

# ---------------------------------------------------------------------------
# Pass 1 – remove usage/budget
# ---------------------------------------------------------------------------

def drop_usage(node):
    if isinstance(node, DICT):
        for k in list(node.keys()):
            if k in USAGE_KEYS:
                del node[k]
                continue
            if k == "metadata" and isinstance(node[k], DICT):
                node[k].pop(METADATA_USAGE_SUBKEY, None)
                drop_usage(node[k])
            else:
                drop_usage(node[k])

    elif isinstance(node, LIST):
        for item in node:
            drop_usage(item)

# ---------------------------------------------------------------------------
# Pass 2 – scrub few‑shot demos
# ---------------------------------------------------------------------------

def scrub_examples(node):
    if isinstance(node, DICT):
        for k, v in list(node.items()):
            if is_fewshot_list(v):
                node[k] = f"few‑shot examples ({len(v)})"
            else:
                scrub_examples(v)

    elif isinstance(node, LIST):
        for item in node:
            scrub_examples(item)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not TARGET.exists():
        raise FileNotFoundError(TARGET)

    yaml_rt = YAML(typ="rt")
    yaml_rt.preserve_quotes = True
    yaml_rt.width = 4096

    with TARGET.open("r", encoding="utf-8") as f:
        docs = list(yaml_rt.load_all(f))

    for doc in docs:
        drop_usage(doc)
        scrub_examples(doc)

    out_path = TARGET.with_name(TARGET.stem + "_clean.yaml")
    with out_path.open("w", encoding="utf-8") as f:
        yaml_rt.dump_all(docs, f)

    print(f"Cleaned YAML written to: {out_path}")

if __name__ == "__main__":
    main()
