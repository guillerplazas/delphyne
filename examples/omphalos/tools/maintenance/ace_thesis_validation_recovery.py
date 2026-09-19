"""Stage adapter for the already sealed thesis recovery implementation.

The round-1 recovery source remains intact. This adapter supplies a scoped
campaign view to its unchanged recovery protocol, mapping only round-1
operation names to validation names. It never rewrites a request or retries
the rejected cell. The real Job still supplies the original validation
stage, input hash, cap and ledger identity.

Both harnesses use this module with prepare, checkpoints, reconcile,
run run --max_workers=24 --wait, and finalize, as for the original helper.
"""

from copy import deepcopy
from pathlib import Path
from typing import Any, override

import delphyne as dp

from experiments.ace_thesis import campaign as campaign
from tools.maintenance import ace_thesis_recovery as protocol


class ScopedPath:
    """Map the protocol's two relative archive names, keeping real Paths."""

    def __truediv__(self, path: str) -> Path:
        if path not in (
            "interrupted_round1/configs",
            "resume_round1/configs",
            "resume_round1",
        ):
            raise ValueError("Unexpected recovery archive path: " + path)
        return campaign.OUTPUT / path.replace("round1", "validation")


def filename(path: str) -> str:
    return path.replace("operations/round1_", "operations/validation_")


class CampaignView:
    """Narrow adapter; all actual execution/accounting belongs to campaign."""

    OUTPUT = ScopedPath()
    ALLOCATIONS = {"round1": campaign.ALLOCATIONS["validation"]}

    def __getattr__(self, name: str) -> Any:
        return getattr(campaign, name)

    @staticmethod
    def jobs(batch: str) -> list[campaign.Job]:
        if batch != "round1":
            raise ValueError("Unexpected recovery batch")
        return campaign.jobs("validation")

    @staticmethod
    def read(path: str) -> Any:
        return campaign.read(filename(path))

    @staticmethod
    def accounting() -> dict[str, Any]:
        account = deepcopy(campaign.accounting())
        # The legacy runner's quota calculation asks for stage round1.
        # Preserve all amounts and restore stage names before any export.
        for group in account["ledger"]["groups"]:
            if group["stage"] == "round1":
                group["stage"] = "original_round1"
            elif group["stage"] == "validation":
                group["stage"] = "round1"
        return account

    @staticmethod
    def save(path: str, value: Any) -> None:
        data: dict[str, Any] = deepcopy(value)
        for key in ("accounting", "accounting_before"):
            if key not in data:
                continue
            for group in data[key]["ledger"]["groups"]:
                if group["stage"] == "round1":
                    group["stage"] = "validation"
                elif group["stage"] == "original_round1":
                    group["stage"] = "round1"
        if path == "operations/validation_incident.json":
            data["stage_adapter"] = __doc__
            data["stage"] = "validation"
        if path.endswith("recovery_seal.json"):
            data.update(
                {
                    str(
                        Path(__file__).relative_to(campaign.ROOT)
                    ): campaign.sha(Path(__file__)),
                    "tests/test_thesis_validation_recovery.py": campaign.sha(
                        campaign.ROOT
                        / "tests/test_thesis_validation_recovery.py"
                    ),
                }
            )
        campaign.save(filename(path), data)


class ValidationResumeJob(protocol.ResumeJob):
    @override
    def instantiate(self, context: object) -> dp.RunStrategyArgs:
        # Spawned workers may import the base protocol in a fresh process.
        configure()
        return super().instantiate(context)


def configure() -> None:
    # This affects only the imported operational protocol, never the frozen
    # experiment module or Job methods. Every process configures its view.
    setattr(protocol, "c", CampaignView())
    protocol.INCIDENT = "operations/validation_incident.json"
    protocol.ResumeJob = ValidationResumeJob


def main() -> None:
    configure()
    protocol.main()


if __name__ == "__main__":
    main()
