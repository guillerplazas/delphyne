"""Export thesis figures from measured, versioned report data; no API calls.

Both harnesses: python -m tools.reports.ace_thesis_figures ANALYSIS_DIRECTORY.
The source and data hashes accompany the standalone PNG/PDF artifacts.
"""

# Matplotlib leaves plotting keyword arguments partially typed. Numerical
# analysis lives in the strictly checked report module, not this renderer.
# pyright: reportUnknownMemberType=false

import json
from pathlib import Path
import sys
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from experiments.ace_thesis import campaign as c
from tools.reports.ace_thesis_retrospective import report_directory

LABELS = {
    "nonace_ordinary": "Non-ACE · output 32768",
    "nonace_matched": "Non-ACE · output 8192",
    "ace_historical": "Historical ACE · output 8192",
    "ace_selected": "Selected ACE · output 8192",
}


def save(figure: Any, folder: Path, name: str) -> None:
    figure.savefig(folder / (name + ".png"), dpi=180, bbox_inches="tight")
    figure.savefig(folder / (name + ".pdf"), bbox_inches="tight")
    plt.close(figure)


def main(folder: Path) -> None:
    source = folder / "results.json"
    result = json.loads(source.read_text())
    panels = {
        key.split("/")[1]: value
        for key, value in result["totals"].items()
        if key.startswith("validation/")
    }
    if not panels or any(p["cells"] != 80 for p in panels.values()):
        raise ValueError("Figures require complete 80-cell validation panels")
    destination = folder / "figures"
    destination.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False})
    colors = ["#596579", "#3182bd", "#c17c28", "#248a64"]
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    keys = [key for key in LABELS if key in panels]
    for axis, field, label in zip(
        axes,
        ("coverage_percent", "cost"),
        ("Qualified coverage (%)", "All-attempt inference spend (USD)"),
    ):
        values = [panels[k][field] for k in keys]
        axis.barh(range(len(keys)), values, color=colors[: len(keys)])
        axis.set_yticks(range(len(keys)), [LABELS[k] for k in keys])
        axis.invert_yaxis()
        axis.set_xlabel(label)
        axis.spines["right"].set_visible(False)
        axis.set_xlim(0, max(values) * 1.2)
        for i, value in enumerate(values):
            text = (
                f"{value:.2f}% ({panels[keys[i]]['solved']}/80)"
                if field == "coverage_percent"
                else f"${value:.3f}"
            )
            axis.text(value, i, "  " + text, va="center", fontsize=9)
    axes[1].set_yticklabels([])
    figure.suptitle("Frozen benchmark on reused validationX development data")
    figure.tight_layout()
    save(figure, destination, "validation")

    pairs = result["comparisons"]
    figure, axis = plt.subplots(figsize=(9, 3.5))
    for i, pair in enumerate(pairs):
        point = pair["budget_reduction_percent"]
        lo, hi = pair["budget_reduction_ci90"]
        axis.plot([lo, hi], [i, i], color="#248a64", linewidth=2)
        axis.scatter([point], [i], color="#248a64", s=40)
    axis.axvline(0, color="#777777", linewidth=1)
    axis.axvline(10, color="#b34747", linestyle="--", label="10% target")
    axis.set_yticks(
        range(len(pairs)), ["vs " + LABELS[p["left"]] for p in pairs]
    )
    axis.invert_yaxis()
    axis.set_xlabel(
        "Selected ACE spending reduction (%) · 90% family intervals"
    )
    axis.set_title("Positive values mean lower measured inference spend")
    axis.legend(loc="best")
    figure.tight_layout()
    save(figure, destination, "cost_uncertainty")

    historical = report_directory() / "comparisons.json"
    history = json.loads(historical.read_text())
    figure, axis = plt.subplots(figsize=(9, 4.5))
    for i, pair in enumerate(history):
        low, high = [100 * (1 - x) for x in pair["cost_ratio_ci90"][::-1]]
        axis.plot([low, high], [i, i], color="#596579", linewidth=2)
        axis.scatter([pair["budget_reduction_percent"]], [i], color="#596579")
    axis.axvline(0, color="#777777", linewidth=1)
    axis.axvline(10, color="#b34747", linestyle="--", label="10% target")
    axis.set_yticks(
        range(len(history)), [p["label"].replace("_", " ") for p in history]
    )
    axis.invert_yaxis()
    axis.set_xlabel("ACE spending reduction (%) · 90% family intervals")
    axis.set_title(
        "Historical development comparisons · controls/cache caveats apply"
    )
    axis.legend(loc="best")
    figure.tight_layout()
    save(figure, destination, "historical")
    (destination / "provenance.json").write_text(
        json.dumps(
            dict(
                plotting_source_sha256=c.sha(Path(__file__)),
                report_sha256=c.sha(source),
                historical_sha256=c.sha(historical),
                note="Inference cost includes failed attempts; learning separate.",
            ),
            indent=2,
        )
        + "\n"
    )
    (destination / "plotting_source.py").write_text(Path(__file__).read_text())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
