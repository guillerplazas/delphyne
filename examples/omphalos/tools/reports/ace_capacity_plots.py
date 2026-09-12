"""Standalone research figures from frozen capacity-study reports."""

from pathlib import Path
import json
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    campaign = root / "experiments/campaigns/ace_capacity_20260912"
    cross = json.loads((campaign / "crossover_report.json").read_text())
    mech = json.loads((campaign / "mechanism_report_v2.json").read_text())
    models = ("gpt-5.6-luna", "gpt-5.6-terra")
    books = ("none", "luna", "terra")
    colors = ("#52616b", "#2a9d8f", "#e9a23b")
    # Matplotlib leaves several public plotting keyword types unspecified.
    fig, raw_axes = plt.subplots(  # pyright: ignore[reportUnknownMemberType]
        2, 2, figsize=(12, 8.5), constrained_layout=True
    )
    axes: Any = raw_axes
    x = np.arange(2)
    for i, (book, color) in enumerate(zip(books, colors, strict=True)):
        values = [
            cross["groups"][f"{m}/{book}"]["qualified_solves"] / 40 * 100
            for m in models
        ]
        bars = axes[0, 0].bar(
            x + (i - 1) * 0.25,
            values,
            0.24,
            color=color,
            label={
                "none": "No book",
                "luna": "Luna book",
                "terra": "Terra book",
            }[book],
        )
        axes[0, 0].bar_label(
            bars, labels=[f"{round(v * 0.4)}/40" for v in values], padding=3
        )
    axes[0, 0].set(
        xticks=x,
        xticklabels=["Luna", "Terra"],
        ylim=(0, 100),
        ylabel="Qualified solves (%)",
        title="Validation crossover: 40 problems per arm",
    )
    axes[0, 0].legend(loc="lower right", fontsize=8)
    keys = [f"{m}/{b}" for m in models for b in books]
    x6 = np.arange(6)
    actual = [cross["groups"][k]["cost"] for k in keys]
    uncached = [cross["groups"][k]["uncached_cost"] for k in keys]
    axes[0, 1].bar(
        x6 - 0.18, actual, 0.35, label="Actual charged", color="#2a9d8f"
    )
    axes[0, 1].bar(
        x6 + 0.18, uncached, 0.35, label="Uncached repricing", color="#9fb5bc"
    )
    axes[0, 1].set(
        xticks=x6,
        xticklabels=[
            f"{m.rsplit('-', 1)[1]}\n{b}" for m in models for b in books
        ],
        yscale="log",
        ylabel="Total dollars, all 40 cells (log scale)",
        title="Price and cached-input sensitivity",
    )
    axes[0, 1].legend(fontsize=8)
    for mi, model in enumerate(models):
        for profile, style in (("C", "--"), ("E", "-")):
            groups = [
                mech[str(level)]["groups"][f"{model}/{profile}"]
                for level in (0, 1, 2)
            ]
            solves = [g["qualified_solves"] for g in groups]
            costs = [g["cost"] for g in groups]
            label = f"{model.rsplit('-', 1)[1].capitalize()} / {'no book' if profile == 'C' else 'corrected book'}"
            color = ("#2878b5", "#d36a27")[mi]
            axes[1, 0].plot(
                [0, 1, 2],
                solves,
                marker="o",
                linestyle=style,
                color=color,
                label=label,
            )
            axes[1, 1].plot(
                costs,
                solves,
                marker="o",
                linestyle=style,
                color=color,
                label=label,
            )
    axes[1, 0].set(
        xticks=[0, 1, 2],
        xticklabels=["Initial", "Money ×2", "+ requests/verifier ×2"],
        yticks=range(9),
        ylim=(-0.1, 8.2),
        ylabel="Qualified solves out of 8",
        title="Selected trainX panel: exact prefix continuations",
    )
    axes[1, 0].legend(fontsize=8, loc="upper left")
    axes[1, 1].set(
        xlabel="Cumulative path cost, all 8 cells ($)",
        ylabel="Qualified solves out of 8",
        ylim=(-0.1, 8.2),
        title="Coverage and cost of continuation",
    )
    for axis in axes.flat:
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    fig.suptitle(  # pyright: ignore[reportUnknownMemberType]
        "ACE capacity follow-up · seed 0 · development data\n"
        "Crossover includes historical controls; the 8-case panel is diagnostic",
        fontsize=13,
    )
    for ext in ("png", "pdf"):
        fig.savefig(  # pyright: ignore[reportUnknownMemberType]
            campaign / f"capacity_comparison.{ext}", dpi=180
        )
    plt.close(fig)


if __name__ == "__main__":
    main()
