"""Freeze the promising eight-source Sol book before any new validation.

160 cells compare this recipe against existing core A0 controls. The sole
solver-side change is learned context. Comparing it to full-curriculum A2
tests two complete preparation recipes, not training-set size in isolation:
the curriculum order and terminal refinement also differ.
"""

from dataclasses import replace

from . import campaign as c
from .common import CAMPAIGN, read, save, sha


def prepare() -> None:
    filename = "books/ladder_v2__sol_medium.json"
    selection = read(CAMPAIGN / "author_selection.json")
    if selection["selected"][0] != "sol_medium":
        raise ValueError(
            "This registered follow-up names the completed pilot winner"
        )
    save(
        CAMPAIGN / "pilot_book_protocol.json",
        dict(
            cells=160,
            arm="P1",
            book_sha=sha(CAMPAIGN / filename),
            controls="Core A0, same Luna solver contract; no additional controls",
            motivation="Completed train pilot11/12,$0.11395045 versus ordinary9/12,$0.26757794. Verify the actual promising short book on full development panels before replacing it with a larger40-source book.",
            panel="All40trainX and40validationX, two replicates each; frozen before validation",
            contrasts="P1 versusA0 isolates learned context. P1 versusA2 contrasts whole preparation recipes, including curriculum and refinement; not a one-factor training-size ablation.",
            interpretation="Exploratory reused development validation, no held-out claim or default promotion",
        ),
    )
    jobs = [
        replace(job, robust=True)
        for stage in ("train", "validation")
        for job in c.ordered_jobs(stage, [("P1", True, filename)])
    ]
    if len(jobs) != 160:
        raise ValueError("Short-book follow-up allocation changed")
    c.register("core_pilot_book", jobs)


if __name__ == "__main__":
    prepare()
