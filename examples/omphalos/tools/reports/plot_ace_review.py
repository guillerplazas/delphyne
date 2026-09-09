"""Render frozen ACE results as a thesis-ready PNG/PDF effect figure.

Run after final_report.json exists. Reads aggregate results only; no model
calls or proof inspection. Both agent harnesses use this same command.
"""

from runtime.paths import OMPHALOS_ROOT

# pyright: strict
# Matplotlib's style keyword arguments have incomplete library annotations.
# pyright: reportUnknownMemberType=false

import io
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MultipleLocator  # noqa: E402

CAMPAIGN = OMPHALOS_ROOT / "experiments/campaigns/ace_review_20260908"


def main() -> None:
    report = json.loads((CAMPAIGN / "final_report.json").read_text())
    selection = report["selection"]
    labels = [
        "Development: x3",
        "Development: repair seed 0",
        "Development: repair seed 1",
        f"Confirmation: {selection['arm']}",
    ]
    results = [
        *(
            selection["comparisons"][arm]
            for arm in ("x3", "repair0", "repair1")
        ),
        report["primary"],
    ]
    positions = [4, 3, 2, 0]
    plt.rcParams.update({"font.size": 10, "font.family": "DejaVu Sans"})
    fig, ax = plt.subplots(figsize=(9.4, 4.9))
    for label, result, y in zip(labels, results, positions):
        effect = 100 * float(result["effect"])
        low, high = (100 * float(x) for x in result["effect_ci95"])
        color = "#186b72" if label.startswith("Confirmation") else "#677589"
        ax.plot(
            [low, high],
            [y, y],
            color=color,
            marker="|",
            markersize=10,
            linewidth=1.8,
        )
        ax.plot(effect, y, "o", color=color, markersize=6)
        ax.text(
            1.03,
            y,
            f"{result['p_two_sided']:.3g}",
            transform=ax.get_yaxis_transform(),
            va="center",
        )
    ax.text(1.03, 4.7, "Exact p", transform=ax.get_yaxis_transform())
    ax.axvline(0, color="#666666", linewidth=1)
    ax.axvline(5, color="#b76d00", linestyle="--", linewidth=1.2)
    ax.axhline(1, color="#dddddd", linewidth=1)
    ax.set_yticks(positions, labels)
    ax.set_ylim(-0.7, 4.8)
    ax.set_xlabel("ACE − baseline solve rate (percentage points)")
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.grid(axis="x", color="#eeeeee")
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.suptitle("Verified proofs within the $0.10 cost ceiling", y=0.97)
    fig.text(
        0.03,
        0.11,
        "Bars: descriptive 95% family bootstrap intervals. Dashed line: +5-point target.\n"
        "Development: 40 theorems × 2 replicates; confirmation: 88 × 2.\n"
        "Only confirmation tests the registered claim; repeated seeds remain clustered.",
        fontsize=9,
        va="center",
    )
    fig.tight_layout(rect=(0.01, 0.19, 0.94, 0.95))
    for extension in ("png", "pdf"):
        stream = io.BytesIO()
        metadata = (
            {"Software": "Omphalos ACE review"}
            if extension == "png"
            else {
                "Creator": "Omphalos ACE review",
                "CreationDate": None,
                "ModDate": None,
                "Producer": None,
            }
        )
        fig.savefig(stream, format=extension, dpi=180, metadata=metadata)
        content = stream.getvalue()
        path = CAMPAIGN / f"effect_comparison.{extension}"
        if path.exists():
            if path.read_bytes() != content:
                raise ValueError(f"refusing to change frozen figure: {path}")
        else:
            with path.open("xb") as out:
                out.write(content)
    plt.close(fig)


if __name__ == "__main__":
    main()
