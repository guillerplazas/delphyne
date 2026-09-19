"""Standalone figure; both harnesses run `python PATH/TO/plot.py`.

Reads the adjacent campaign's immutable analysis and historical comparison
exports. No requests, model fitting, outcome selection or protected data.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def main() -> None:
    campaign = Path(__file__).resolve().parents[2]
    history = json.loads(
        (campaign / "audit/corrected_comparisons.json").read_text()
    )
    fresh = json.loads((campaign / "analysis/results.json").read_text())[
        "comparisons"
    ]
    rows = [
        (
            "Historical X3, draw 0",
            history["historical_none__vs__historical_x3_seed0"],
            "#667085",
        ),
        (
            "Historical X3, draw 1*",
            history["historical_none__vs__historical_x3_seed1"],
            "#667085",
        ),
        (
            "Previous thesis, 8192",
            history["previous_nonace_matched__vs__previous_ace_historical"],
            "#667085",
        ),
        (
            "Controlled matrix, 32768",
            fresh["none_32768__vs__x3_32768"],
            "#006d77",
        ),
        (
            "Controlled matrix, 8192",
            fresh["none_8192__vs__x3_8192"],
            "#006d77",
        ),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    for i, (label, comparison, color) in enumerate(rows):
        value = comparison["qualified"]
        y = len(rows) - 1 - i
        saving = 100 * (1 - value["cost_ratio"])
        lower, upper = [
            100 * (1 - r) for r in reversed(value["cost_ratio_ci90"])
        ]
        axes[0].errorbar(
            saving,
            y,
            xerr=[[saving - lower], [upper - saving]],
            fmt="o",
            color=color,
            capsize=4,
        )
        gain = 100 * value["effect"]
        lower, upper = [100 * v for v in value["effect_ci90"]]
        axes[1].errorbar(
            gain,
            y,
            xerr=[[gain - lower], [upper - gain]],
            fmt="o",
            color=color,
            capsize=4,
        )
    axes[0].set_yticks(range(len(rows)), [r[0] for r in reversed(rows)])
    axes[0].set_xlabel("All-attempt cost reduction (%)")
    axes[1].set_xlabel("Qualified coverage gain (percentage points)")
    for ax in axes:
        ax.axvline(0, color="#98a2b3", linewidth=1)
        ax.axvline(10, color="#c77700", linestyle="--", linewidth=1)
        ax.grid(axis="y", alpha=0.15)
        ax.set_ylim(-0.6, len(rows) - 0.4)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    fig.suptitle(
        "Original X3: observed effects and 90% theorem-clustered intervals",
        fontsize=13,
    )
    fig.text(
        0.02,
        0.025,
        "Cache-write-inclusive tariff; provider caching enabled. Dashed lines: 10% / 10-point targets.\n*Historical draws share one empty-context control. ValidationX is reused development data.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.13, 1, 0.95))
    destination = Path(__file__).parent
    for suffix in ("png", "pdf"):
        fig.savefig(destination / ("x3_effects." + suffix), dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
