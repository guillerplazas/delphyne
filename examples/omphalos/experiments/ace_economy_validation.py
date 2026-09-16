"""Validation-only continuation after Guille's September 16 scope correction.

The original sealed campaign included a test plan, now revoked by "Never
touch testX". Never call its mixed-scope verifier, inspect its old seal, or
load another partition. This amendment seals only explicitly allowed code,
the unchanged book, validation inputs and registered validation manifests.
It does not retrospectively replace the original preregistration. The
measured proof implementation and four development panels are unchanged.
No new main-campaign dispatch, held-out confirmation or default promotion.

Both harnesses: `python -m experiments.ace_economy_validation prepare`,
then use the validation-only report and replay tools. A stopped historical
coordinator is retired after its supervised validation workers finish.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

import delphyne as dp

from experiments import ace_economy_experiment as original
from runtime.paths import OMPHALOS_ROOT as ROOT

NAME = original.NAME
CAMPAIGN = original.CAMPAIGN
OUTPUT = original.OUTPUT
BATCHES = ("baseline", "budget", "session", "views")
read = original.read
save = original.save
name = original.name
directory = original.directory
accounting = original.accounting
activate = original.activate
context = original.context


def partition(stage: str = "validation") -> dict[str, str]:
    if stage != "validation":
        raise ValueError("Only validationX is authorized")
    return original.partition("validation")


@dataclass(frozen=True)
class Config(original.Config):
    def __post_init__(self) -> None:
        if self.stage != "validation":
            raise ValueError("Only validationX is authorized")

    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        return super().instantiate(context)


def configs(batch: str) -> list[Config]:
    if batch not in BATCHES:
        raise ValueError("Unregistered validation batch")
    return [Config(**v) for v in read(f"manifests/{batch}.json")]


def cell_result(config: Config) -> dict[str, Any] | None:
    if config.stage != "validation":
        raise ValueError("Only validationX is authorized")
    return original.cell_result(config)


def source_paths() -> list[Path]:
    paths = [
        Path(__file__),
        ROOT / "delphyne.yaml",
        ROOT / "experiments/ace_economy_experiment.py",
        ROOT / "experiments/common/omphalos_launch.py",
        ROOT / "experiments/common/ace_learning_io.py",
        ROOT / "tools/reports/ace_economy_results.py",
        ROOT / "tests/test_ace_economy.py",
        ROOT / "tests/test_economy_scope.py",
        ROOT / "benchmarks/validationX.txt",
        CAMPAIGN / "book.yaml",
        CAMPAIGN / "runtime.json",
        CAMPAIGN / "validation_scope.json",
    ]
    paths.extend(ROOT.glob("prove_*.py"))
    for folder, pattern in (
        ("ace", "*.py"),
        ("runtime", "*.py"),
        ("prompts", "*.jinja"),
        ("demos", "*.yaml"),
    ):
        paths.extend((ROOT / folder).rglob(pattern))
    paths.extend(ROOT / p for p in partition().values())
    paths.extend(CAMPAIGN / f"manifests/{b}.json" for b in BATCHES)
    return sorted(set(paths))


def prepare() -> None:
    if (CAMPAIGN / "validation_seal.json").exists():
        verify()
        return
    if original.sha(CAMPAIGN / "book.yaml") != original.BOOK_SHA:
        raise ValueError("Frozen reference book changed")
    for batch in BATCHES:
        configs(batch)
    save(
        "validation_scope.json",
        dict(
            created=datetime.now(timezone.utc).isoformat(),
            protocol=__doc__,
            latest_instruction="Never touch testX",
            authorized_partition="validationX",
            revoked="All test plans in both September 16 campaigns",
            original_test_access="Partition list and statement hashes only; before correction",
            test_experiments_launched=0,
            original_seal="Preserved, not opened or verified after correction",
            new_seal="Prospective validation-only integrity snapshot; exact cache replay checks measured behavior",
            main_batches=list(BATCHES),
            expected_main_cells=400,
            combined_api_ceiling=50,
            default_promoted=False,
        ),
    )
    save(
        "validation_seal.json",
        {str(p.relative_to(ROOT)): original.sha(p) for p in source_paths()},
    )


def verify() -> None:
    expected = {str(p.relative_to(ROOT)) for p in source_paths()}
    sealed = read("validation_seal.json")
    # Reject unexpected paths BEFORE attempting to open or hash them.
    if set(sealed) != expected:
        raise ValueError("Validation seal contains an unauthorized path")
    for path, digest in sealed.items():
        if original.sha(ROOT / path) != digest:
            raise ValueError("Validation source/input drift: " + path)


def finalize_views() -> None:
    """Record finished workers after retiring the obsolete coordinator."""
    verify()
    charges = accounting()
    if charges["unresolved"] or charges["billing_issues"]:
        raise ValueError("Wait for validation workers and billing to settle")
    jobs = configs("views")
    for job in jobs:
        cell_result(job)
    save(
        "batches/views.json",
        dict(
            exit_code=None,
            coordinator="Stopped to prevent revoked mixed-scope verification; workers completed normally",
            states={
                name(job, None): original.ol.ground_truth(directory(job))
                for job in jobs
            },
        ),
    )


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "prepare":
        prepare()
    elif action == "verify":
        verify()
    elif action == "finalize-views":
        finalize_views()
    else:
        raise SystemExit("prepare | verify | finalize-views")
