#!/usr/bin/env python3
"""Build the categorized miniF2F-rocq layout for Omphalos.

Reads upstream `.v` files from a temporary `_upstream/{test,valid}/` checkout
inside this directory and merges in the
informal statement + informal proof from the HuggingFace JSONL files.
Writes `<split>/<category>/<name>.v` and emits `_CoqProject`.

Re-running is idempotent: it deletes and rebuilds `test/`, `valid/`, and
`_CoqProject` from scratch.
"""

from __future__ import annotations

import json
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM = ROOT / "_upstream"
HF_JSONL = {
    "test": "https://huggingface.co/datasets/LLM4Rocq/miniF2F-rocq/resolve/main/test.jsonl",
    "valid": "https://huggingface.co/datasets/LLM4Rocq/miniF2F-rocq/resolve/main/valid.jsonl",
}


def fetch_jsonl(url: str) -> list[dict]:
    """Fetch a stream of concatenated JSON objects (pretty-printed, not strict JSONL)."""
    print(f"  fetching {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "omphalos-miniF2F/1.0"})
    with urllib.request.urlopen(req) as resp:
        text = resp.read().decode("utf-8")
    decoder = json.JSONDecoder()
    records: list[dict] = []
    idx = 0
    n = len(text)
    while idx < n:
        while idx < n and text[idx] in " \t\r\n":
            idx += 1
        if idx >= n:
            break
        obj, end = decoder.raw_decode(text, idx)
        records.append(obj)
        idx = end
    return records


def categorize(name: str) -> str:
    """Map a problem name to a category subdirectory (relative path)."""
    if name.startswith(("aime_", "aimeI_", "aimeII_")):
        return "aime"
    if name.startswith(("amc12_", "amc12a_", "amc12b_")):
        return "amc"
    if name.startswith(("imo_", "imosl_")):
        return "imo"
    if name.startswith("algebra_"):
        return "algebra"
    if name.startswith("induction_"):
        return "induction"
    if name.startswith("numbertheory_"):
        return "numbertheory"
    if name.startswith("mathd_"):
        # mathd_algebra_478 -> mathd/algebra
        # mathd_numbertheory_x -> mathd/numbertheory
        rest = name[len("mathd_"):]
        # topic is the substring before the last underscore-and-id; usually
        # mathd_<topic>_<id>. Split on first underscore to get topic.
        topic = rest.split("_", 1)[0] if "_" in rest else rest
        return f"mathd/{topic}"
    return "others"


def sanitize_for_rocq_comment(text: str) -> str:
    """Make informal text safe to embed inside `(* ... *)`:
    - Rocq nests comments, so `(*` / `*)` markers in the prose would re-open or
      prematurely close the comment.
    - Rocq's lexer parses string literals `"..."` even inside comments, so an
      odd number of `"` raises "Unterminated string".
    Replace both with visually similar substitutes."""
    return (
        text.replace("(*", "( *")
            .replace("*)", "* )")
            .replace('"', "''")
    )


def wrap_paragraph(text: str, width: int = 88, indent: str = "   ") -> str:
    """Word-wrap text without breaking long tokens (LaTeX). Preserves blank lines."""
    if not text:
        return f"{indent}(none)"
    text = sanitize_for_rocq_comment(text)
    out_lines: list[str] = []
    for raw_line in text.splitlines():
        if not raw_line.strip():
            out_lines.append("")
            continue
        words = raw_line.split(" ")
        current = indent
        for word in words:
            if current == indent:
                current += word
            elif len(current) + 1 + len(word) <= width:
                current += " " + word
            else:
                out_lines.append(current)
                current = indent + word
        out_lines.append(current)
    return "\n".join(out_lines)


def comment_header(
    name: str,
    split: str,
    informal_statement: str | None,
    informal_proof: str | None,
) -> str:
    stmt = wrap_paragraph(informal_statement or "")
    proof = wrap_paragraph(informal_proof or "")
    return (
        "(* miniF2F problem: " + name + "\n"
        "   Split: " + split + "\n"
        "   Source: https://github.com/LLM4Rocq/miniF2F-rocq\n"
        "\n"
        "   Informal statement:\n"
        + stmt + "\n"
        "\n"
        "   Informal proof:\n"
        + proof + "\n"
        "*)\n\n"
    )


def main() -> int:
    if not UPSTREAM.exists():
        print(f"ERROR: {UPSTREAM} missing. From {ROOT}, run `git clone --depth 1 "
              f"https://github.com/LLM4Rocq/miniF2F-rocq _upstream` first. "
              "`_upstream/` is local-only and should not be committed.",
              file=sys.stderr)
        return 1

    # 1) Load HF JSONL -> name -> (informal_statement, informal_proof)
    print("Fetching HuggingFace JSONL files...")
    informal: dict[str, tuple[str, str]] = {}
    for split, url in HF_JSONL.items():
        for row in fetch_jsonl(url):
            informal[str(row["name"])] = (
                str(row.get("informal_statement") or ""),
                str(row.get("informal_proof") or ""),
            )
    print(f"  loaded informal data for {len(informal)} problems")

    # 2) Wipe existing tree, rebuild
    for split in ("test", "valid"):
        target = ROOT / split
        if target.exists():
            shutil.rmtree(target)

    coq_paths: list[str] = []
    counts: dict[str, int] = {}
    missing_informal: list[str] = []

    for split in ("test", "valid"):
        src_dir = UPSTREAM / split
        if not src_dir.is_dir():
            print(f"ERROR: missing {src_dir}", file=sys.stderr)
            return 1
        for v_file in sorted(src_dir.glob("*.v")):
            name = v_file.stem
            category = categorize(name)
            dest_dir = ROOT / split / category
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / v_file.name

            stmt, proof = informal.get(name, ("", ""))
            if not stmt and not proof:
                missing_informal.append(f"{split}/{name}")

            header = comment_header(name, split, stmt, proof)
            body = v_file.read_text(encoding="utf-8")
            # Many upstream files (~185/488) end with `Proof.` and no terminator,
            # which Rocq 9.0.1 rejects with "There are pending proofs". Append
            # `Admitted.` so each file is self-contained and the project builds.
            stripped = body.rstrip()
            if not (stripped.endswith("Admitted.") or stripped.endswith("Qed.")
                    or stripped.endswith("Defined.") or stripped.endswith("Abort.")):
                body = stripped + "\nAdmitted.\n"
            dest.write_text(header + body, encoding="utf-8")

            rel = dest.relative_to(ROOT).as_posix()
            coq_paths.append(rel)
            counts[f"{split}/{category}"] = counts.get(f"{split}/{category}", 0) + 1

    # 3) Write _CoqProject
    coq_project = ROOT / "_CoqProject"
    with coq_project.open("w", encoding="utf-8") as f:
        f.write("-Q . miniF2F\n")
        for p in coq_paths:
            f.write(p + "\n")

    # 4) Report
    print(f"\nWrote {len(coq_paths)} .v files.")
    print("Counts by split/category:")
    for key in sorted(counts):
        print(f"  {key:40s} {counts[key]:3d}")
    if missing_informal:
        print(f"\nWARNING: {len(missing_informal)} problems had no informal text "
              "in the HF dataset:")
        for m in missing_informal[:10]:
            print(f"  - {m}")
        if len(missing_informal) > 10:
            print(f"  ... and {len(missing_informal) - 10} more")

    print(f"\n_CoqProject written to {coq_project}")
    print("Next: run `rocq makefile -f _CoqProject -o Makefile` then `make -j`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
