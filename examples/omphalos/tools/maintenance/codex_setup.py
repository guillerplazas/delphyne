"""
Install the omphalos Codex profile for this machine.

The profile itself is checked into the tree at `.codex/config.toml`, so
it travels with the repository (i34-gpu01 and any future host get the
same settings, and a change to it is reviewable like any other file).
Codex, however, only reads profiles from `$CODEX_HOME`, so this script
puts a *symlink* at `~/.codex/omphalos.config.toml` — a copy would go
stale the first time the profile changes.

Use the profile with `codex -p omphalos` (interactive) or
`codex exec -p omphalos "..."` (one-shot). What it grants and why is
documented in the profile's own comments; the short version is
workspace writes plus network (experiments call the OpenAI API),
`OPENAI_API_KEY` passed through, the Anthropic credentials deliberately
withheld, and rocq-mcp registered.

`--check` verifies without writing anything; that same check runs as
part of `make agents-check` / `make test-unit`.
"""

import argparse
import shutil
import subprocess


from tools.maintenance.agents_check import (  # noqa: E402
    CODEX_PROFILE,
    CODEX_PROFILE_LINK,
    Report,
    check_codex_profile,
)


def codex_version() -> str | None:
    """The installed Codex CLI version, or `None` if it is absent."""
    binary = shutil.which("codex")
    if binary is None:
        return None
    try:
        out = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def install() -> int:
    """Point `~/.codex/omphalos.config.toml` at the tracked profile."""
    if not CODEX_PROFILE.is_file():
        print(f"missing profile: {CODEX_PROFILE}")
        return 1
    CODEX_PROFILE_LINK.parent.mkdir(parents=True, exist_ok=True)
    if CODEX_PROFILE_LINK.is_symlink() or CODEX_PROFILE_LINK.exists():
        if (
            CODEX_PROFILE_LINK.is_symlink()
            and CODEX_PROFILE_LINK.resolve() == CODEX_PROFILE.resolve()
        ):
            print(f"already installed: {CODEX_PROFILE_LINK}")
            return report_ready()
        if not CODEX_PROFILE_LINK.is_symlink():
            print(
                f"refusing to replace the regular file "
                f"{CODEX_PROFILE_LINK}; move it aside first"
            )
            return 1
        CODEX_PROFILE_LINK.unlink()
    CODEX_PROFILE_LINK.symlink_to(CODEX_PROFILE)
    print(f"linked {CODEX_PROFILE_LINK} -> {CODEX_PROFILE}")
    return report_ready()


def report_ready() -> int:
    """Print how to use the profile, and whether Codex is installed."""
    version = codex_version()
    if version is None:
        print(
            "codex is not on PATH: the profile is installed but unused "
            "until the CLI is (https://developers.openai.com/codex/cli)"
        )
    else:
        print(f"codex on PATH: {version}")
    print("start a session with:  codex -p omphalos")
    print('one-shot:              codex exec -p omphalos "..."')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Install the checked-in Codex profile as "
            "~/.codex/omphalos.config.toml. Makes no API calls."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the installation without writing anything",
    )
    args = parser.parse_args()
    if not args.check:
        return install()
    report = Report(problems=[], notes=[])
    check_codex_profile(report)
    for note in report.notes:
        print(f"ok   {note}")
    for problem in report.problems:
        print(f"FAIL {problem}")
    return 1 if report.problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
