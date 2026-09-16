"""Standalone scientific figures from the economics campaign's offline report.

Both harnesses: python -m tools.reports.ace_economy_figures. PNG and PDF
exports live beside the report; this command cannot launch experiments.
"""

# Matplotlib's variadic plotting keywords have incomplete third-party stubs.
# pyright: reportUnknownMemberType=false

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from experiments import ace_economy_validation as c  # noqa: E402

LABELS = dict(
    agentic="Non-ACE",
    ace="ACE v2",
    budget="$0.20 cap",
    session="One context reset",
    views="4 KiB displays",
)
COLORS = dict(
    agentic="#555555",
    ace="#1670b5",
    budget="#bb5524",
    session="#7550a0",
    views="#159575",
)


def main() -> None:
    c.verify()
    data = json.loads((c.CAMPAIGN / "analysis/results.json").read_text())
    totals = data["totals"]
    destination = c.CAMPAIGN / "figures"
    destination.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.7), layout="constrained")
    for arm, label in LABELS.items():
        value = totals[f"validation/{arm}"]
        cost = value["cost"] / value["cells"]
        quality = 100 * value["qualified"] / value["cells"]
        ax.scatter(cost, quality, color=COLORS[arm], s=55, zorder=3)
        offset = {
            "agentic": (-65, 4),
            "ace": (-55, -15),
            "budget": (7, 7),
            "session": (7, 7),
            "views": (7, -12),
        }[arm]
        ax.annotate(
            label,
            (cost, quality),
            xytext=offset,
            textcoords="offset points",
            fontsize=9,
        )
    reference = totals["validation/agentic"]
    ax.axvline(
        0.9 * reference["cost"] / reference["cells"],
        color="#779477",
        ls=":",
        lw=1,
    )
    ax.axhline(
        100 * reference["qualified"] / reference["cells"],
        color="#aaaaaa",
        ls=":",
        lw=1,
    )
    ax.set(
        title="validationX: 40 theorems, 2 replicates per arm",
        xlabel="Inference dollars per problem (all attempts)",
        ylabel="Qualified proofs (%)",
    )
    ax.margins(x=0.35, y=0.3)
    ax.grid(alpha=0.2)
    fig.suptitle(
        "Observed cost and proof quality; lower cost and higher coverage are preferable",
        fontsize=11,
    )
    for suffix in ("png", "pdf"):
        fig.savefig(destination / f"cost_quality.{suffix}", dpi=180)
    plt.close(fig)
    comparisons = [
        (key, value)
        for key, value in data["paired"].items()
        if value["complete"]
    ]
    fig, ax = plt.subplots(
        figsize=(9, max(3.5, 0.55 * len(comparisons) + 1.4)),
        layout="constrained",
    )
    labels: list[str] = []
    for i, (key, value) in enumerate(comparisons):
        stage, arms = key.split("/")
        reference, arm = arms.split("_vs_")
        lo, hi = value["cost_ratio_ci90"]
        ax.hlines(i, lo, hi, color=COLORS[arm], lw=2)
        ax.plot(value["cost_ratio"], i, "o", color=COLORS[arm])
        delta = value["solved_b"] - value["solved_a"]
        labels.append(
            f"{stage}X: {LABELS[arm]} / {LABELS[reference]} ({delta:+d} proofs)"
        )
    ax.axvline(1, color="#777777", lw=1)
    ax.axvline(0.9, color="#779477", ls="--", lw=1)
    ax.set(
        yticks=range(len(labels)),
        yticklabels=labels,
        xlabel="Total inference cost ratio (dashed line: 10% saving)",
        title="Paired cost estimates and 90% confidence intervals, clustered by theorem family",
    )
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.2)
    for suffix in ("png", "pdf"):
        fig.savefig(destination / f"paired_costs.{suffix}", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
