"""Standalone numeric figures; both harnesses invoke this module offline."""

from pathlib import Path
from typing import Any, cast

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from experiments import ace_economy_refinement_experiment as c


def main() -> None:
    data = c.read("results.json")
    totals = data["totals"]
    colors = {"ace": "#7b3294", "agentic": "#00836b"}
    markers = {"": "o", "_reset": "^", "_compact": "s", "_reset_compact": "D"}
    labels = {
        "": "baseline",
        "_reset": "drop",
        "_compact": "compact",
        "_reset_compact": "both",
    }
    plt.rcParams.update(
        {"font.size": 10, "axes.spines.top": False, "axes.spines.right": False}
    )
    # Installed Matplotlib stubs leave array axes and rendering kwargs untyped.
    renderer = cast(Any, plt)
    fig, axes = renderer.subplots(
        1, 2, figsize=(12, 5.5), gridspec_kw={"width_ratios": [1.05, 1.35]}
    )
    left, right = axes
    offsets = {
        "agentic": ((10, 10), (-10, 12), (-12, -18), (-10, -18)),
        "ace": ((8, -20), (10, 12), (-12, 6), (10, 12)),
    }
    for agent in ("agentic", "ace"):
        for index, (suffix, marker) in enumerate(markers.items()):
            row = totals[agent + suffix]
            left.scatter(
                row["cost"],
                row["qualified"],
                color=colors[agent],
                marker=marker,
                s=75,
                zorder=3,
            )
            dx, dy = offsets[agent][index]
            left.annotate(
                ("A: " if agent == "ace" else "N: ") + labels[suffix],
                (row["cost"], row["qualified"]),
                xytext=(dx, dy),
                textcoords="offset points",
                ha="left" if dx > 0 else "right",
                color=colors[agent],
                fontsize=9,
                arrowprops=dict(
                    arrowstyle="-", color=colors[agent], alpha=0.4
                ),
            )
        points = sorted(
            (totals[label]["cost"], totals[label]["qualified"])
            for label in data["frontiers"][agent]
        )
        left.plot(
            [p[0] for p in points],
            [p[1] for p in points],
            color=colors[agent],
            ls=":",
            alpha=0.7,
        )
    count = next(iter(totals.values()))["cells"]
    left.set(
        xlabel="All-attempt charged cost ($)",
        ylabel=f"Qualified proofs / {count}",
        title="Each agent's observed cost / coverage frontier",
    )
    left.margins(x=0.27, y=0.25)
    left.grid(alpha=0.18)
    left.legend(
        handles=[
            Line2D(
                [0],
                [0],
                color=colors[a],
                marker="o",
                linestyle="",
                label=label,
            )
            for a, label in (("agentic", "Non-ACE (N)"), ("ace", "ACE (A)"))
        ],
        loc="best",
    )
    tick_labels: list[str] = []
    index = 0
    for agent in ("agentic", "ace"):
        for suffix in ("_reset", "_compact", "_reset_compact"):
            pair = data["comparisons"][f"{agent} -> {agent + suffix}"]
            low, high = pair["cost_ratio_ci90"]
            ratio = pair["cost_ratio"]
            right.hlines(index, low, high, color=colors[agent], linewidth=2)
            right.plot(
                ratio,
                index,
                markers[suffix],
                color=colors[agent],
                markersize=7,
            )
            delta = pair["solved_b"] - pair["solved_a"]
            tick_labels.append(
                f"{'ACE' if agent == 'ace' else 'Non-ACE'} {labels[suffix]} ({delta:+d} proofs)"
            )
            index += 1
    right.axvline(1, color="#444444", lw=1, label="Same cost")
    right.axvline(0.9, color="#aaaaaa", lw=1, ls="--", label="10% saving")
    right.set_yticks(range(index), tick_labels)
    right.invert_yaxis()
    right.set(
        xlabel="Cost ratio versus that agent's baseline",
        title="Independent refinements and combination",
    )
    right.grid(axis="x", alpha=0.18)
    right.legend(loc="best", fontsize=9)
    fig.suptitle(
        f"Session dropping and compact prompting — {data['matched_theorems']} validationX theorems, two replicates",
        fontsize=12,
    )
    fig.text(
        0.5,
        0.015,
        "Exploratory development data. 90% theorem-family bootstrap intervals. Costs include unsuccessful attempts.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.055, 1, 0.94))
    destination = c.CAMPAIGN / "analysis"
    destination.mkdir(exist_ok=True)
    fig.savefig(
        destination / "cost_coverage.png",
        dpi=180,
        metadata={"Software": "Omphalos economy refinement"},
    )
    fig.savefig(
        destination / "cost_coverage.pdf",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)
    c.save(
        "analysis/figure.json",
        dict(
            results_sha256=c.sha(c.CAMPAIGN / "results.json"),
            code_sha256=c.sha(Path(__file__)),
            files={
                p.name: c.sha(p)
                for p in (
                    destination / "cost_coverage.png",
                    destination / "cost_coverage.pdf",
                )
            },
        ),
    )


if __name__ == "__main__":
    main()
