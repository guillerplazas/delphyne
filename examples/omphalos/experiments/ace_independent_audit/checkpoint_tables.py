"""Tables and standalone figures for the completed checkpoint only."""

from typing import Any

from .common import REPORT, read
from .figures import COLORS, export, plt
from .reporting import ARM_NAMES
from .tables import csv_table, interval


def run() -> None:
    data = read(REPORT / "checkpoint_results.json")
    rows: list[dict[str, Any]] = []
    text = [
        "## Completed forty-problem replicates",
        "",
        "These are individual complete replicates, not the registered pooled",
        "two-replicate comparison. Each cost includes all forty attempts.",
        "Positive savings mean lower cost than the matching non-ACE control.",
        "Online rows exclude their separately reported learning fees.",
        "",
        "| Partition / arm / replicate | Solves | Cost | Cost / solve | Requests | Saving | 90% interval |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key, m in sorted(data["complete_replicates"].items()):
        stage, arm, replicate = key.split("/")
        comparison = data["completed_replicate_comparisons"].get(key)
        pair = comparison["theorem"] if comparison else None
        row = dict(
            partition=stage + "X",
            arm=arm,
            description=ARM_NAMES[arm],
            replicate=int(replicate.removeprefix("replicate")),
            n=m["n"],
            solves=m["solves"],
            cost=m["cost"],
            cost_per_solve=m["cost_per_solve"],
            requests=m["requests"],
            failed_cost=m["failed_cost"],
            baseline=comparison["baseline"] if comparison else "",
            saving=pair["saving"] if pair else "",
            saving_ci90_low=pair["saving_ci90"][0] if pair else "",
            saving_ci90_high=pair["saving_ci90"][1] if pair else "",
            family_ci90_low=comparison["family"]["saving_ci90"][0]
            if comparison
            else "",
            family_ci90_high=comparison["family"]["saving_ci90"][1]
            if comparison
            else "",
            sign_flip_p=pair["two_sided_sign_flip_p"] if pair else "",
        )
        rows.append(row)
        saving = f"{100 * pair['saving']:+.1f}%" if pair else "—"
        ci = interval(pair["saving_ci90"]) if pair else "—"
        text.append(
            f"| {key} | {m['solves']}/40 | ${m['cost']:.5f}"
            f" | ${m['cost_per_solve']:.5f} | {m['requests']}"
            f" | {saving} | {ci} |"
        )
    text += [
        "",
        "Intervals cluster by theorem; the CSV also reports broader",
        "proof-method-family intervals. Neither an interval nor a replicate's",
        "solve loss is used as an extra acceptance veto. R1 replicate zero",
        "has no complete matching control at this checkpoint.",
        "",
    ]
    csv_table("checkpoint_replicates.csv", rows)
    (REPORT / "checkpoint_tables.md").write_text("\n".join(text))
    budget = read(REPORT / "checkpoint_budget_results.json")
    budget_rows: list[dict[str, Any]] = []
    for key, m in sorted(budget["complete_replicates"].items()):
        stage, arm, replicate, cap = key.split("/")
        pair = budget["same_cap_comparisons"].get(key)
        budget_rows.append(
            dict(
                partition=stage + "X",
                arm=arm,
                replicate=int(replicate.removeprefix("replicate")),
                cap=float(cap.removeprefix("cap")),
                **m,
                saving_vs_same_cap=pair["theorem"]["saving"] if pair else "",
                solve_difference_vs_same_cap=(
                    pair["theorem"]["arm_solves"]
                    - pair["theorem"]["baseline_solves"]
                )
                if pair
                else "",
            )
        )
    csv_table("checkpoint_budget_replicates.csv", budget_rows)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
    panels = [
        (
            "validation",
            0,
            ["A0", "A1", "A2", "B0", "B1", "B2"],
            "validationX · completed replicate 0",
        ),
        (
            "train",
            1,
            ["A0", "online_A2", "B0", "online_B1", "online_B2"],
            "trainX · completed online order 1",
        ),
    ]
    for ax, (stage, replicate, arms, title) in zip(axes, panels, strict=True):
        for i, arm in enumerate(arms):
            m = data["complete_replicates"][
                f"{stage}/{arm}/replicate{replicate}"
            ]
            ax.barh(i, m["cost"], color=COLORS[arm.removeprefix("online_")])
            ax.text(
                m["cost"] + 0.02,
                i,
                f"{m['solves']}/40 solved",
                va="center",
                fontsize=9,
            )
        maximum = max(
            data["complete_replicates"][f"{stage}/{a}/replicate{replicate}"][
                "cost"
            ]
            for a in arms
        )
        ax.set(
            title=title,
            yticks=list(range(len(arms))),
            yticklabels=arms,
            xlabel="All-attempt solver inference cost (USD)",
            xlim=(0, maximum * 1.48),
        )
        ax.invert_yaxis()
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(
        "User-requested checkpoint · one complete replicate per panel"
    )
    fig.tight_layout()
    export(fig, "checkpoint_complete_replicates")


if __name__ == "__main__":
    run()
