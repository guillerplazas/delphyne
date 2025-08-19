"""
Inspired by paper experiments
"""

"""code2inv.py - DATA PLUMBING -> 
    1. removing duplicates or wrongs
    2. loads them in python dict
    3. writtes them in "selected" (mlw)
_ _ _ _ _ _ _
    load_blacklist() – read names to skip.

load_selected_benchmarks() – load the exact curated set.

load_all_benchmarks() – load everything except black-listed.

generate_selected() – physically copy the curated set into a selected/ subfolder.

Execution (python file.py) simply prints how many usable (non-blacklisted) benchmarks it can see.

"""
# code2inv.py - DATA PLUMBING

from pathlib import Path
from typing import List
import checker as ch


# ---------------------------------------------------------------------------
#  Paths
# ---------------------------------------------------------------------------

HERE              = Path(__file__).resolve().parent          # this file's dir
BENCHMARKS_TXT    = (HERE / "benchmark" / "htps.txt").resolve()
# If you want to re-export the parsed equations somewhere:
OUTPUT_FOLDER     = HERE / "out_equations"  

def _parse_line(line: str) -> ch.Eq:
    """
    Convert a single 'lhs = rhs' string into an (lhs, rhs) tuple.
    Raises ValueError if the '=' sign is missing.
    """
    if "=" not in line:
        raise ValueError(f"Bad equation line: {line!r}")
    lhs, rhs = line.split("=", maxsplit=1)
    return lhs.strip(), rhs.strip()    

def load_equations(txt_path: Path | None = None) -> List[ch.Eq]:
    """
    Read *all* equations from the text file and return a list of (lhs, rhs) pairs.
    Blank lines are ignored; leading/trailing spaces are trimmed.
    """
    path = txt_path or BENCHMARKS_TXT
    with path.open() as fh:
        eqs = [_parse_line(ln) for ln in fh if ln.strip()]
    return eqs

def export_equations(dest: Path | None = None) -> None:
    """
    Re-write each parsed equation as '<idx>.txt' into OUTPUT_FOLDER
    (useful for quickly eyeballing or feeding into other tooling).
    """
    dest = dest or OUTPUT_FOLDER
    dest.mkdir(parents=True, exist_ok=True)

    for idx, (lhs, rhs) in enumerate(load_equations(), start=1):
        out_file = dest / f"{idx:03d}.txt"
        out_file.write_text(f"{lhs} = {rhs}\n")

if __name__ == "__main__":
    all_eq = load_equations()
    print(f"Loaded {len(all_eq)} equations from {BENCHMARKS_TXT}")
    # Uncomment to generate individual files:
    export_equations()