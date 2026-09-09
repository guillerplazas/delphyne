"""
Check the invariants that let two agent harnesses share one project.

Since 2026-09-08 omphalos is worked on from both Claude Code and Codex
CLI. Neither harness reads the other's files, so the shared state is
held together by three symlinks and one config file:

1. `AGENTS.md` is the canonical instruction file in each of the three
   scopes (repository root, `examples/omphalos`, `examples/omphalos/
   ladon`), and `CLAUDE.md` beside it is a symlink to it. Claude Code
   auto-loads `CLAUDE.md`, Codex auto-loads `AGENTS.md`, and both get
   the same bytes.
2. `memory/` holds the durable cross-session facts, and Claude Code's
   own memory directory is a symlink to it.
3. `.codex/config.toml` is the omphalos Codex profile, symlinked to
   `~/.codex/omphalos.config.toml` by `tools/codex_setup.py`.

Every one of those is a symlink, and the failure mode is silent: a
`cp -r`, an `rsync` without `-l`, or an editor that "saves a copy"
turns a link into a regular file, the two names drift apart, and the
next session on the other harness reads stale instructions without any
error. Hence this guard, in `make test-unit`. It makes no API calls and
does not need either CLI installed.
"""

import argparse
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

OMPHALOS = Path(__file__).resolve().parent.parent
REPO = OMPHALOS.parent.parent
HOME = Path.home()

# The three directories that carry an AGENTS.md / CLAUDE.md pair.
SCOPES: tuple[Path, ...] = (REPO, OMPHALOS, OMPHALOS / "ladon")

MEMORY = OMPHALOS / "memory"
CLAUDE_MEMORY = (
    HOME / ".claude" / "projects" / str(REPO).replace("/", "-") / "memory"
)
CODEX_PROFILE = OMPHALOS / ".codex" / "config.toml"
CODEX_PROFILE_LINK = HOME / ".codex" / "omphalos.config.toml"
GIT_EXCLUDE = REPO / ".git" / "info" / "exclude"

# A token-shaped literal: long, unbroken, not a filesystem path.
_SECRET_RE = re.compile(r"sk-[A-Za-z0-9]|[A-Za-z0-9_\-]{40,}")


@dataclass
class Report:
    """Accumulated outcome of the checks."""

    problems: list[str]
    notes: list[str]

    def fail(self, msg: str) -> None:
        self.problems.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def check_instruction_files(report: Report) -> None:
    """`AGENTS.md` real, `CLAUDE.md` a symlink pointing at it."""
    for scope in SCOPES:
        rel = scope.relative_to(REPO) if scope != REPO else Path(".")
        agents, claude = scope / "AGENTS.md", scope / "CLAUDE.md"
        if not agents.is_file() or agents.is_symlink():
            report.fail(f"{rel}: AGENTS.md is missing or is not a file")
            continue
        if not agents.read_text().strip():
            report.fail(f"{rel}: AGENTS.md is empty")
        if not claude.is_symlink():
            kind = "a regular file" if claude.exists() else "missing"
            report.fail(
                f"{rel}: CLAUDE.md is {kind}; it must be a symlink "
                f"(cd {scope} && rm -f CLAUDE.md && ln -s AGENTS.md "
                f"CLAUDE.md)"
            )
        elif claude.resolve() != agents.resolve():
            report.fail(
                f"{rel}: CLAUDE.md points at {claude.resolve()}, "
                f"not at its own AGENTS.md"
            )
        else:
            report.note(f"{rel}: AGENTS.md + CLAUDE.md symlink")


def check_memory(report: Report) -> None:
    """Memory lives in the tree; Claude Code reaches it by symlink."""
    index = MEMORY / "MEMORY.md"
    if not index.is_file() or not index.read_text().strip():
        report.fail(f"{index} is missing or empty")
        return
    skip = {"MEMORY.md", "README.md"}
    entries = len([f for f in MEMORY.glob("*.md") if f.name not in skip])
    report.note(f"memory/: index + {entries} entries")
    if not (HOME / ".claude").is_dir():
        report.note("~/.claude absent: Claude Code memory link not checked")
        return
    if not CLAUDE_MEMORY.is_symlink():
        kind = "a real directory" if CLAUDE_MEMORY.exists() else "missing"
        report.fail(
            f"Claude Code memory dir is {kind}; it must be a symlink "
            f"(rm -rf {CLAUDE_MEMORY} && ln -s {MEMORY} {CLAUDE_MEMORY})"
        )
    elif CLAUDE_MEMORY.resolve() != MEMORY.resolve():
        report.fail(
            f"Claude Code memory dir points at {CLAUDE_MEMORY.resolve()}, "
            f"not at {MEMORY}"
        )
    else:
        report.note("Claude Code memory dir -> memory/")


def check_codex_profile(report: Report) -> None:
    """The profile parses, holds no secret, and is installed."""
    if not CODEX_PROFILE.is_file():
        report.fail(f"{CODEX_PROFILE} is missing")
        return
    text = CODEX_PROFILE.read_text()
    try:
        tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        report.fail(f"{CODEX_PROFILE} does not parse as TOML: {exc}")
        return
    for lineno, line in enumerate(text.splitlines(), 1):
        value = line.split("=", 1)[1] if "=" in line else ""
        if "/" in value or line.lstrip().startswith("#"):
            continue
        if _SECRET_RE.search(value):
            report.fail(
                f".codex/config.toml:{lineno} looks like a credential; "
                f"keys are inherited from the shell, never stored"
            )
    report.note(".codex/config.toml: parses, no credential literal")
    if not (HOME / ".codex").is_dir():
        report.note("~/.codex absent: Codex profile link not checked")
        return
    if not CODEX_PROFILE_LINK.is_symlink():
        kind = "a real file" if CODEX_PROFILE_LINK.exists() else "missing"
        report.fail(f"{CODEX_PROFILE_LINK} is {kind}; run `make codex-setup`")
    elif CODEX_PROFILE_LINK.resolve() != CODEX_PROFILE.resolve():
        report.fail(
            f"{CODEX_PROFILE_LINK} points at "
            f"{CODEX_PROFILE_LINK.resolve()}, not at {CODEX_PROFILE}"
        )
    else:
        report.note("~/.codex/omphalos.config.toml -> .codex/config.toml")


def check_git_exclude(report: Report) -> None:
    """The local-only files stay out of `git status`."""
    if not GIT_EXCLUDE.is_file():
        report.note("no .git/info/exclude: exclusions not checked")
        return
    listed = {
        line.strip()
        for line in GIT_EXCLUDE.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    wanted = ("AGENTS.md", "examples/omphalos/memory/")
    missing = [entry for entry in wanted if entry not in listed]
    if missing:
        report.fail(
            f".git/info/exclude is missing {', '.join(missing)} "
            f"(local-only files would show up in git status)"
        )
    else:
        report.note(".git/info/exclude: local-only files excluded")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check the dual-harness invariants (AGENTS.md/CLAUDE.md "
            "symlinks, shared memory, Codex profile). No API calls."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="accepted for symmetry with the other guards; the tool "
        "never writes anything",
    )
    parser.parse_args()
    report = Report(problems=[], notes=[])
    check_instruction_files(report)
    check_memory(report)
    check_codex_profile(report)
    check_git_exclude(report)
    for note in report.notes:
        print(f"ok   {note}")
    for problem in report.problems:
        print(f"FAIL {problem}")
    if report.problems:
        print(f"\n{len(report.problems)} dual-harness invariant(s) broken.")
        return 1
    print("\nDual-harness invariants hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
