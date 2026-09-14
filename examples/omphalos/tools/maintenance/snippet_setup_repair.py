"""Preserve the zero-dispatch credential failure before a corrected launch.

This single-use migration is scoped to this campaign. It refuses any API
receipt or model cache. It preserves all 24 setup failures and the original
20-cell failure panel, which cannot measure the intervention's model effect.
No paid request is retried; the four reconciled request-retry reserve remains.
Both harnesses source ~/.config/omphalos/env.sh inside the tmux command.
"""

# ruff: noqa: E402
from runtime.snippet_scope import install

install()

import shutil

from experiments.snippet_experiment import CAMPAIGN, OUTPUT, accounting, save


def main() -> None:
    acct = accounting()
    if acct["new_total"] or acct["costs"] or acct["unresolved"]:
        raise ValueError("Repair requires zero API dispatches/liabilities")
    failures = list(OUTPUT.rglob("exception.txt"))
    if len(failures) != 24 or any(
        "Please set environment variable OPENAI_API_KEY." not in p.read_text()
        for p in failures
    ):
        raise ValueError("Unexpected failure; requires separate diagnosis")
    if list(OUTPUT.rglob("cache.yaml")) or (CAMPAIGN / "transport").exists():
        raise ValueError("Refuse to reset any model execution")
    archive = CAMPAIGN / "setup_failure_01"
    archive.mkdir(exist_ok=False)
    paths = [
        OUTPUT,
        *[
            CAMPAIGN / n
            for n in (
                "seal.json",
                "manifests",
                "batches",
                "replays",
                "reports",
                "writing_stop.json",
                "exposure_gate.json",
                "final_accounting.json",
                "receipts.csv",
                "RESULTS.md",
                "campaign.log",
            )
        ],
    ]
    moved: list[dict[str, str]] = []
    for path in paths:
        if path.exists():
            destination = archive / ("output" if path == OUTPUT else path.name)
            shutil.move(str(path), destination)
            moved.append(dict(source=str(path), preserved=str(destination)))
    save(
        "setup_repair.json",
        dict(
            reason="tmux server environment did not inherit the API credential",
            model_dispatches=0,
            paid_retries=0,
            failed_setup_jobs=24,
            failed_training_denominator=20,
            failed_training_solves=0,
            interpretation="Initial setup panel is preserved with its failures; no model-effect verdict. Corrected launch is a separately identified execution of the same registered cells.",
            treatment_change=False,
            budget_change=False,
            gate_change=False,
            moved=moved,
            amendment="Credential precheck added before launching any batch; source environment inside tmux. New source seal precedes first paid dispatch.",
        ),
    )


if __name__ == "__main__":
    main()
