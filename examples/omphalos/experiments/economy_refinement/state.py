"""Resolve audited administrative continuations without changing raw archives."""

from pathlib import Path
from typing import Any

import yaml

from experiments import ace_economy_refinement_experiment as c


def directory(job: c.Config) -> Path:
    amendment = c.CAMPAIGN / "operations/incident01.json"
    if not amendment.exists():
        return c.directory(job)
    incident = c.read("operations/incident01.json")
    ident = c.name(job, None)
    resumed = incident["interrupted_cells"]
    if incident["rejected_cell"] in resumed:
        raise ValueError("A provider-rejected request cannot be resumed")
    if ident not in resumed:
        return c.directory(job)
    if job.batch != "final00" or job.stage != "validation":
        raise ValueError("Unexpected continuation scope")
    return c.OUTPUT / "resume01/configs" / ident


def cell_result(job: c.Config) -> dict[str, Any] | None:
    folder = directory(job)
    if folder == c.directory(job):
        return c.cell_result(job)
    status = c.ol.ground_truth(folder)
    if status not in ("done", "failed"):
        raise ValueError("Missing administrative continuation")
    diagnostics = "".join(p.read_text() for p in folder.glob("exception*.txt"))
    if "CampaignExhausted" in diagnostics or "CampaignPaused" in diagnostics:
        raise ValueError("Continuation remains administratively censored")
    if status == "failed":
        return None
    raw: dict[str, Any] = yaml.safe_load((folder / "result.yaml").read_text())
    return raw["outcome"]["result"]


def terminal_file(job: c.Config) -> Path:
    folder = directory(job)
    result = folder / "result.yaml"
    if result.exists():
        return result
    failure = folder / "exception.txt"
    if failure.exists():
        return failure
    raise ValueError("Cell has no terminal artifact")


def archive_files(job: c.Config) -> list[Path]:
    folders = {directory(job), c.directory(job)}
    return sorted(
        folder / filename
        for folder in folders
        for filename in ("result.yaml", "cache.yaml", "exception.txt")
        if (folder / filename).exists()
    )
