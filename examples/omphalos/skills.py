"""
Rocq skill-pack index and loader for the agentic baseline.

The skill pack at `rocq_skills_data/` was designed as a Claude Code
plugin, but only a subset of its references is relevant to a per-proof
LLM running through pytanque. This module curates that subset and
exposes two pure-Python entry points used by `prove_agentic.py`:

- `list_skills()` — name → one-line description, for the system prompt.
- `read_skill(name)` — full markdown content, returned through the
  `ReadSkill` tool when the LLM requests it.

The MCP / cycle-engine / subagent-workflows references are *not*
exposed: they describe a Claude-Code-plugin runtime that we are not
using, and would only add noise to the agent's context. The
admitted-filling / proof-golfing-patterns / axiom-elimination
references are excluded too: they are about transforming *existing*
proofs, which never comes up when proving a miniF2F goal from scratch.

Pure Python — no Delphyne imports — so callers can wrap these in
`dp.compute(...)` cleanly.
"""

from __future__ import annotations

from pathlib import Path


_SKILLS_ROOT = (
    Path(__file__).resolve().parent
    / "rocq_skills_data"
    / "plugins"
    / "rocq"
    / "skills"
    / "rocq"
)
_REFERENCES_DIR = _SKILLS_ROOT / "references"


SKILL_WHITELIST: tuple[str, ...] = (
    "rocq-phrasebook",
    "proof-templates",
    "tactics-reference",
    "tactic-patterns",
    "compilation-errors",
    "compiler-guided-repair",
    "coq-stdlib-guide",
)


def list_skills() -> dict[str, str]:
    """
    Return `{skill_name: one-line description}` for every whitelisted
    reference. The description is the first non-empty, non-heading line
    of the file (truncated). Used to render the available-skills table
    in the agentic system prompt.
    """
    return {
        name: _description(_REFERENCES_DIR / f"{name}.md")
        for name in SKILL_WHITELIST
    }


def read_skill(name: str) -> str:
    """
    Return the full markdown content of a whitelisted skill, or a clear
    error string if the name is unknown or the file is missing. The
    return value is shown verbatim to the LLM as the `ReadSkill` tool
    result, so error strings should be self-explanatory.
    """
    if name not in SKILL_WHITELIST:
        available = ", ".join(SKILL_WHITELIST)
        return (
            f"Skill {name!r} is not available. "
            f"Available skills: {available}."
        )
    path = _REFERENCES_DIR / f"{name}.md"
    if not path.is_file():
        return f"Skill {name!r} is missing on disk at {path}."
    return path.read_text()


def _description(path: Path) -> str:
    if not path.is_file():
        return "(missing on disk)"
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        return line[:200]
    return ""
