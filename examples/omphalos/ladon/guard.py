"""
The frozen surface of a Ladon night, and the git mechanics around it.

autoresearch keeps its agent honest by construction — the metric, the
data and the split live in a file the agent may not touch. Omphalos
has more leak surfaces (the verifier, the partitions, the scoring
tools, the pricing table, paid outputs), so the guard is a diff
inspector rather than a single file: before an implement session the
orchestrator snapshots the tree, after it it derives a manifest of
everything that changed and refuses the arm if a frozen path moved.
The same manifest drives the patch that is saved on DISCARD/INSPECT,
the revert that leaves the tree clean for the next hint, and the
`git add -f` of a KEEP (new files under `examples/omphalos/` are
invisible to `git status`: the directory sits in `.git/info/exclude`).

Frozen (any change = violation): the partitions, the paired-statistics
and pricing tools and their tests, the four baseline scripts, the
frozen X registry (`minif2f_x.py`, `miniF2F_bench.py` — an arm adds a
knob by subclassing `ladon.bench.LadonConfig` in its own script), the
benchmark and vendored trees, the cached smoke suites, the local
knowledge files, the frozen playbooks, and Ladon itself. Block-frozen:
the pricing table in `model_registry.py`. Append-only: `Makefile`,
`.gitignore`. Outputs: every pre-existing directory under
`experiments/output/` must be untouched and a new one must carry the
night's arm name.
"""

# pyright: strict

import fnmatch
import hashlib
import os
import re
import subprocess
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

OMPHALOS = Path(__file__).resolve().parent.parent
REPO = OMPHALOS.parent.parent
REL = "examples/omphalos"

FROZEN_GLOBS: tuple[str, ...] = (
    "benchmarks/*.txt",
    "tools/decision_audit.py",
    "tools/ace_report.py",
    "tools/cell_records.py",
    "tools/reprice.py",
    "tools/make_partitions.py",
    "tools/make_pool.py",
    "tools/test_*.py",
    "experiments/minif2f_x.py",
    "experiments/miniF2F_bench.py",
    "experiments/x_ladon_experiment.py",
    "experiments/x_validation_experiment.py",
    "experiments/x_test_experiment.py",
    "experiments/x_train_experiment.py",
    "experiments/playbooks/*",
    "experiments/playbooks/*/*",
    "miniF2F/*",
    "rocq_skills_data/*",
    "commands/*",
    "pyrightconfig.json",
    "delphyne.yaml",
    "README.md",
    "PROGRESS.md",
    "HINTS.md",
    "LINKS.md",
    "CLAUDE.md",
    "master_arbeit_plan.md",
    "papers/*",
    "ladon/*",
)
FROZEN_EXCEPT: tuple[str, ...] = ("ladon/nights/*",)
APPEND_ONLY: tuple[str, ...] = ("Makefile", ".gitignore")
BLOCK_FROZEN: dict[str, tuple[str, str]] = {
    "model_registry.py": ("# fmt: off", "# fmt: on"),
}
VERIFIER_FILES: tuple[str, ...] = (
    "pytanque_utils.py",
    "rocq_server.py",
    "prove_agentic.py",
)
SNAPSHOT_EXCLUDE: frozenset[str] = frozenset(
    {
        ".rocq_cache",
        "experiments/output",
        "experiments/previous",
        "experiments/logs",
        "rocq_skills_data",
        "miniF2F",
        "commands/cache",
        "commands/previous/cache",
        "ladon/nights",
        "papers",
        "__pycache__",
        ".pytest_cache",
        ".git",
        ".agents",
        ".codex",
    }
)
OUTPUT_DIR = "experiments/output"
HASH_LIMIT = 4 * 2**20
ARM_DIR_RE = re.compile(
    r"^ladon_\d{4}-\d{2}-\d{2}(-[a-z0-9]+)?_h\d+_(agentic|smoke)$"
)
ARM_SCRIPT_RE = re.compile(
    r"^experiments/ladon_\d{4}-\d{2}-\d{2}(-[a-z0-9]+)?_h\d+_experiment\.py$"
)


def _glob_match(rel: str, pattern: str) -> bool:
    """`fnmatch` where `*` also crosses directory separators."""
    return fnmatch.fnmatchcase(rel, pattern) or fnmatch.fnmatchcase(
        rel, pattern.replace("/*", "/**")
    )


def is_frozen(rel: str) -> bool:
    if any(rel == p or rel.startswith(p.rstrip("*")) for p in FROZEN_EXCEPT):
        return False
    for pattern in FROZEN_GLOBS:
        base = pattern.rstrip("*")
        if pattern.endswith("/*") and rel.startswith(base):
            return True
        if _glob_match(rel, pattern):
            return True
    return False


#####
##### Snapshots
#####


@dataclass(frozen=True)
class FileStat:
    size: int
    mtime_ns: int
    sha: str


def _sha_of(path: Path, size: int) -> str:
    if size > HASH_LIMIT:
        return f"size:{size}"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _excluded(rel: str) -> bool:
    parts = rel.split("/")
    for i in range(1, len(parts) + 1):
        if "/".join(parts[:i]) in SNAPSHOT_EXCLUDE or parts[i - 1] in (
            "__pycache__",
            ".git",
        ):
            return True
    return False


def snapshot(root: Path = OMPHALOS) -> dict[str, FileStat]:
    out: dict[str, FileStat] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        rel_dir = "" if rel_dir == "." else rel_dir
        dirnames[:] = sorted(
            d
            for d in dirnames
            if not _excluded(f"{rel_dir}/{d}" if rel_dir else d)
        )
        for name in filenames:
            rel = f"{rel_dir}/{name}" if rel_dir else name
            path = Path(dirpath) / name
            try:
                st = path.stat()
            except OSError:
                continue
            if not path.is_file():
                continue
            out[rel] = FileStat(
                st.st_size, st.st_mtime_ns, _sha_of(path, st.st_size)
            )
    return out


def output_snapshot(root: Path = OMPHALOS) -> dict[str, str]:
    """`{dir name: stat of its experiment.yaml}` for every output dir."""
    out: dict[str, str] = {}
    base = root / OUTPUT_DIR
    if not base.exists():
        return out
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        state = d / "experiment.yaml"
        try:
            st = state.stat()
            out[d.name] = f"{st.st_size}:{st.st_mtime_ns}"
        except OSError:
            out[d.name] = "absent"
    return out


def block_hashes(root: Path = OMPHALOS) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel, (start, end) in BLOCK_FROZEN.items():
        path = root / rel
        if not path.exists():
            out[rel] = "missing"
            continue
        text = path.read_text()
        i, j = text.find(start), text.find(end)
        block = text[i:j] if 0 <= i < j else text
        out[rel] = hashlib.sha256(block.encode()).hexdigest()
    return out


@dataclass(frozen=True)
class Snapshot:
    files: dict[str, FileStat]
    outputs: dict[str, str]
    blocks: dict[str, str]
    head: str
    git_status: tuple[str, ...]


def take(root: Path = OMPHALOS) -> Snapshot:
    return Snapshot(
        files=snapshot(root),
        outputs=output_snapshot(root),
        blocks=block_hashes(root),
        head=head_sha(),
        git_status=tuple(git_status()),
    )


#####
##### git
#####


def git(*args: str, cwd: Path = REPO, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed ({proc.returncode}): "
            f"{proc.stderr.strip()}"
        )
    return proc.stdout


def head_sha() -> str:
    return git("rev-parse", "HEAD").strip()


def current_branch() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD").strip()


def git_status() -> list[str]:
    """`git status --porcelain -uall` lines (excluded files never show)."""
    return [
        ln
        for ln in git("status", "--porcelain=v1", "-uall").splitlines()
        if ln
    ]


def author() -> str:
    name = git("config", "user.name").strip()
    email = git("config", "user.email").strip()
    return f"{name} <{email}>"


def tracked(rel: str) -> bool:
    return bool(git("ls-files", "--", f"{REL}/{rel}").strip())


def repo_rel(rel: str) -> str:
    return f"{REL}/{rel}"


#####
##### Manifest
#####


@dataclass(frozen=True)
class Manifest:
    modified: tuple[str, ...]
    created: tuple[str, ...]
    deleted: tuple[str, ...]
    git_changes: tuple[str, ...]
    out_of_scope: tuple[str, ...]
    blocks_changed: tuple[str, ...]
    append_violations: tuple[str, ...]
    outputs_changed: tuple[str, ...]
    outputs_new: tuple[str, ...]
    head_changed: bool
    untracked_modified: tuple[str, ...] = ()
    untracked_deleted: tuple[str, ...] = ()

    @property
    def touched(self) -> tuple[str, ...]:
        return tuple(sorted({*self.modified, *self.created, *self.deleted}))

    @property
    def empty(self) -> bool:
        return not (
            self.touched
            or self.out_of_scope
            or self.outputs_new
            or self.outputs_changed
        )


def manifest(before: Snapshot, after: Snapshot) -> Manifest:
    modified = sorted(
        r
        for r, st in after.files.items()
        if r in before.files and before.files[r].sha != st.sha
    )
    created = sorted(r for r in after.files if r not in before.files)
    deleted = sorted(r for r in before.files if r not in after.files)
    git_changes = sorted(set(after.git_status) - set(before.git_status))
    out_of_scope = tuple(
        ln for ln in git_changes if not ln[3:].strip().startswith(REL + "/")
    )
    append_violations = tuple(
        rel for rel in APPEND_ONLY if rel in modified and _removes_lines(rel)
    )
    outputs_changed = tuple(
        sorted(
            n
            for n, st in after.outputs.items()
            if n in before.outputs and before.outputs[n] != st
        )
    )
    outputs_new = tuple(
        sorted(n for n in after.outputs if n not in before.outputs)
    )
    untracked_modified = tuple(r for r in modified if not tracked(r))
    untracked_deleted = tuple(r for r in deleted if not tracked(r))
    return Manifest(
        modified=tuple(modified),
        created=tuple(created),
        deleted=tuple(deleted),
        git_changes=tuple(git_changes),
        out_of_scope=out_of_scope,
        blocks_changed=tuple(
            sorted(
                r
                for r in after.blocks
                if after.blocks[r] != before.blocks.get(r)
            )
        ),
        append_violations=append_violations,
        outputs_changed=outputs_changed,
        outputs_new=outputs_new,
        head_changed=before.head != after.head,
        untracked_modified=untracked_modified,
        untracked_deleted=untracked_deleted,
    )


def _removes_lines(rel: str) -> bool:
    diff = git("diff", "HEAD", "--", repo_rel(rel))
    return any(
        ln.startswith("-") and not ln.startswith("---")
        for ln in diff.splitlines()
    )


def violations(
    m: Manifest,
    *,
    allowed_output: Callable[[str], bool],
    allowed_script: Callable[[str], bool],
) -> list[str]:
    out: list[str] = []
    for rel in m.touched:
        if is_frozen(rel):
            out.append(f"frozen path changed: {rel}")
        elif rel.startswith("experiments/") and rel.endswith("_experiment.py"):
            if rel in m.created and not allowed_script(rel):
                out.append(
                    f"experiment script outside the arm name rule: {rel}"
                )
    out += [f"block-frozen region changed: {r}" for r in m.blocks_changed]
    out += [f"append-only file lost lines: {r}" for r in m.append_violations]
    out += [
        f"pre-existing output directory changed: {n}"
        for n in m.outputs_changed
    ]
    out += [
        f"output directory outside the arm name rule: {n}"
        for n in m.outputs_new
        if not allowed_output(n)
    ]
    out += [f"change outside {REL}: {ln.strip()}" for ln in m.out_of_scope]
    out += [
        f"pre-existing untracked file modified (cannot be restored): {r}"
        for r in m.untracked_modified
    ]
    out += [
        f"untracked file deleted (cannot be restored): {r}"
        for r in m.untracked_deleted
    ]
    if m.head_changed:
        out.append("HEAD moved during the session (a commit was made)")
    return out


def verifier_touched(m: Manifest) -> bool:
    return any(rel in VERIFIER_FILES for rel in m.touched)


def touched_python(m: Manifest) -> list[str]:
    return [r for r in (*m.modified, *m.created) if r.endswith(".py")]


def fingerprint(m: Manifest, root: Path = OMPHALOS) -> str:
    """Content hash of every touched file plus the tracked diff."""
    h = hashlib.sha256()
    for rel in m.touched:
        path = root / rel
        h.update(rel.encode())
        if path.exists() and path.is_file():
            h.update(_sha_of(path, path.stat().st_size).encode())
        else:
            h.update(b"<absent>")
    tracked_paths = [
        repo_rel(r) for r in (*m.modified, *m.deleted) if tracked(r)
    ]
    if tracked_paths:
        h.update(git("diff", "HEAD", "--", *tracked_paths).encode())
    return h.hexdigest()


def save_patch(m: Manifest, path: Path, root: Path = OMPHALOS) -> None:
    parts: list[str] = []
    tracked_paths = [
        repo_rel(r) for r in (*m.modified, *m.deleted) if tracked(r)
    ]
    if tracked_paths:
        parts.append(git("diff", "HEAD", "--", *tracked_paths))
    for rel in (*m.created, *m.untracked_modified):
        p = root / rel
        if not p.is_file():
            continue
        proc = subprocess.run(
            ["git", "diff", "--no-index", "--", "/dev/null", str(p)],
            cwd=REPO,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
        )
        parts.append(proc.stdout)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts))


def revert(m: Manifest, root: Path = OMPHALOS) -> list[str]:
    """Restore tracked files, delete created ones; report what was done."""
    actions: list[str] = []
    tracked_paths = [
        repo_rel(r) for r in (*m.modified, *m.deleted) if tracked(r)
    ]
    if tracked_paths:
        git("checkout", "HEAD", "--", *tracked_paths)
        actions += [f"restored {p}" for p in tracked_paths]
    for rel in m.created:
        p = root / rel
        if p.is_file():
            p.unlink()
            actions.append(f"deleted {rel}")
            parent = p.parent
            while (
                parent != root
                and parent.is_dir()
                and not any(parent.iterdir())
            ):
                parent.rmdir()
                parent = parent.parent
    for ln in m.out_of_scope:
        path = ln[3:].strip()
        if ln.startswith("??"):
            fp = REPO / path
            if fp.is_file():
                fp.unlink()
                actions.append(f"deleted out-of-scope {path}")
        else:
            git("checkout", "HEAD", "--", path, check=False)
            actions.append(f"restored out-of-scope {path}")
    return actions


def commit_paths(m: Manifest) -> list[str]:
    return [
        repo_rel(r)
        for r in m.touched
        if not r.startswith(OUTPUT_DIR + "/")
        and not r.startswith("ladon/nights/")
    ]


def commit(
    m: Manifest, message: str, *, extra_paths: Iterable[str] = ()
) -> str:
    paths = commit_paths(m) + [repo_rel(r) for r in extra_paths]
    if not paths:
        raise RuntimeError("nothing to commit")
    git("add", "-f", "-A", "--", *paths)
    msg = REPO / ".git" / "LADON_COMMIT_MSG"
    msg.write_text(message)
    try:
        git("commit", "--author", author(), "-F", str(msg))
    finally:
        msg.unlink(missing_ok=True)
    return head_sha()


def staged_or_dirty(paths: Sequence[str]) -> list[str]:
    """Status lines for `paths` (repo-relative); empty = clean."""
    if not paths:
        return []
    return [
        ln
        for ln in git("status", "--porcelain=v1", "--", *paths).splitlines()
        if ln
    ]
