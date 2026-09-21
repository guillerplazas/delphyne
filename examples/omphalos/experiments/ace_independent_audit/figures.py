"""Standalone research figures; all coordinates come from audited artifacts."""

from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as _pyplot
import numpy as np

from .common import CAMPAIGN, REPORT, read
from .cost_bounds import interval as cost_interval
from .reporting import inputs

# Matplotlib's dynamic keyword/style interface has incomplete strict stubs.
plt: Any = _pyplot
DEST = REPORT / "figures"
COLORS = {
    "A0": "#222222",
    "A1": "#777777",
    "A2": "#0072B2",
    "S1": "#56B4E9",
    "P1": "#009E73",
    "O1": "#882255",
    "R1": "#44AA99",
    "B0": "#A64B00",
    "B1": "#E69F00",
    "B2": "#CC79A7",
}


def export(figure: Any, name: str) -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    figure.savefig(DEST / (name + ".png"), dpi=200, bbox_inches="tight")
    figure.savefig(DEST / (name + ".pdf"), bbox_inches="tight")
    figure.savefig(DEST / (name + ".svg"), bbox_inches="tight")
    plt.close(figure)


def historical() -> None:
    data = read(CAMPAIGN / "input_output_mechanisms.json")
    keys = [
        "x_validation_agentic",
        "ace_x_validation_ace_x3_offline_rv2_agentic",
        "ace_x_validation_ace_x3_noreflect_rv3_agentic",
        "ace_x_validation_ace_x5_offline_rv2_agentic",
    ]
    labels = ["Ordinary", "X3 rv2", "X3 no reflection", "X5 rv2"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = np.arange(len(keys))
    inp = [data[k]["input_cost"] for k in keys]
    out = [data[k]["output_cost"] for k in keys]
    ax.bar(x, inp, label="Billed input", color="#0072B2")
    ax.bar(x, out, bottom=inp, label="Output", color="#E69F00")
    for i, key in enumerate(keys):
        ax.text(
            i,
            data[key]["cost"] + 0.04,
            f"{data[key]['solves']}/80 solved",
            ha="center",
            fontsize=9,
        )
    ax.set(
        xticks=x,
        xticklabels=labels,
        ylabel="All-attempt inference cost (USD)",
        title="Historical original-agentic validationX · 80 attempts",
    )
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, max(data[k]["cost"] for k in keys) * 1.18)
    export(fig, "historical_cost_components")


def authors() -> None:
    data = read(CAMPAIGN / "author_selection.json")["metrics"]
    labels: list[str] = []
    costs: list[float] = []
    solves: list[int] = []
    for model in ("luna", "terra", "sol", "astra"):
        for effort in ("medium", "high"):
            value = data[f"ladder_v2_{model}_{effort}"]
            labels.append(model.title() + " " + effort)
            costs.append(value["cost"])
            solves.append(value["solves"])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(labels))
    ax.barh(
        x,
        costs,
        color=[
            "#009E73" if label == "Sol medium" else "#0072B2"
            for label in labels
        ],
    )
    for i, (cost, solved) in enumerate(zip(costs, solves, strict=True)):
        ax.text(
            cost + 0.004, i, f"{solved}/12 solved", va="center", fontsize=9
        )
    control = data["author_none"]
    ax.axvline(
        control["cost"],
        color="#222222",
        ls="--",
        label=f"No playbook: {control['solves']}/12 solved",
    )
    ax.set(
        yticks=x,
        yticklabels=labels,
        xlabel="Luna inference cost on the fixed 12-problem trainX pilot (USD)",
        title="Scale the author; keep the solver fixed · exploratory selection",
    )
    ax.invert_yaxis()
    ax.set_xlim(0, max(costs + [control["cost"]]) * 1.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    export(fig, "author_pilot")


def fresh() -> None:
    data = inputs()
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.6), sharey=True)
    offsets = {
        "A0": (8, 8),
        "A1": (6, 8),
        "A2": (8, -5),
        "S1": (-26, -16),
        "P1": (6, 9),
        "O1": (6, 8),
        "R1": (6, -14),
        "B0": (8, 8),
        "B1": (6, 8),
        "B2": (8, 8),
    }
    for ax, stage in zip(axs, ("train", "validation"), strict=True):
        for arm, color in COLORS.items():
            if f"{stage}/{arm}" not in data["metrics"]:
                continue
            m = data["metrics"][f"{stage}/{arm}"]
            x, y = m["cost"] / 2, m["solves"] / 2
            lo, hi = cost_interval(m)
            if lo != hi:
                ax.errorbar(
                    x,
                    y,
                    xerr=[[x - lo / 2], [0]],
                    fmt="none",
                    ecolor=color,
                    capsize=4,
                )
            ax.scatter(
                x,
                y,
                s=60,
                marker="s"
                if arm.startswith("B")
                else "^"
                if arm == "R1"
                else "o",
                color=color,
            )
            ax.annotate(
                arm,
                (x, y),
                xytext=offsets[arm],
                textcoords="offset points",
                color=color,
            )
        ax.set(
            xlabel="All-attempt cost per 40 problems (USD)",
            title="trainX: familiar"
            if stage == "train"
            else "validationX: development transfer",
        )
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.16)
    axs[0].set_ylabel("Solved per 40 problems (mean of two replicates)")
    fig.suptitle("Frozen playbooks · Luna solver · preparation cost excluded")
    bounded = any("cost_interval" in m for m in data["metrics"].values())
    if bounded:
        fig.text(
            0.5,
            0.01,
            "B1 trainX: horizontal bar spans the timeout invoice bound; point uses full retained liability.",
            ha="center",
            fontsize=8,
        )
    fig.tight_layout(rect=(0, 0.05 if bounded else 0, 1, 1))
    export(fig, "fresh_frontier")

    fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.8), sharey=True)
    arms = ["A1", "A2", "S1", "P1", "O1", "R1", "B1", "B2"]
    for ax, stage in zip(axs, ("train", "validation"), strict=True):
        for i, arm in enumerate(arms):
            if f"{stage}/{arm}" not in data["comparisons"]:
                continue
            result = data["comparisons"][f"{stage}/{arm}"]["theorem"]
            x = 100 * result["saving"]
            lo, hi = [100 * v for v in result["saving_ci90"]]
            ax.plot([lo, hi], [i, i], color=COLORS[arm], lw=2)
            ax.scatter(
                [x],
                [i],
                color=COLORS[arm],
                marker="o" if result["practical_target"] else "x",
                s=55,
            )
            if "saving_interval" in result:
                ax.plot(
                    [100 * v for v in result["saving_interval"]],
                    [i, i],
                    color="#222222",
                    lw=4,
                )
        ax.axvline(0, color="#555555", lw=0.8)
        ax.axvline(10, color="#009E73", ls="--", lw=1)
        ax.set(
            yticks=np.arange(len(arms)),
            yticklabels=arms,
            xlabel="Inference cost saving versus matched non-ACE (%)",
            title=stage + "X",
        )
        ax.spines[["top", "right"]].set_visible(False)
    axs[0].invert_yaxis()
    fig.suptitle(
        "Paired 90% theorem-cluster intervals · circle meets practical cost/coverage target"
    )
    if bounded:
        fig.text(
            0.5,
            0.01,
            "B1 trainX: dark segment is invoice uncertainty; its wider interval envelopes both billing endpoints.",
            ha="center",
            fontsize=8,
        )
    fig.tight_layout(rect=(0, 0.05 if bounded else 0, 1, 1))
    export(fig, "fresh_paired_savings")


def online() -> None:
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.6))
    economics = read(REPORT / "final_economics.json")
    arms = ["A0", "online_A2", "B0", "online_B1", "online_B2"]
    costs = {a: np.zeros(40) for a in arms}
    solves = {a: np.zeros(40) for a in arms}
    for order in (0, 1):
        for step in range(40):
            event = read(
                CAMPAIGN
                / "online_scores"
                / f"online-o{order}-s{step:02d}.json"
            )
            for row in event["scores"]:
                costs[row["arm"]][step] += row["cost"]["price"] / 2
                solves[row["arm"]][step] += row["solved"] / 2
    for arm in arms:
        name = arm.removeprefix("online_")
        for ax, values in zip(axs, (costs, solves), strict=True):
            ax.plot(
                np.arange(1, 41),
                values[arm].cumsum(),
                label=name,
                color=COLORS[name],
            )
    axs[0].set_ylabel("Cumulative inference cost (USD)")
    axs[1].set_ylabel("Cumulative solved problems")
    for ax in axs:
        ax.set_xlabel("Position in curriculum (mean of two orders)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False)
    fig.suptitle(
        "Online: solve before updating · inference shown separately from learning"
    )
    fig.tight_layout()
    export(fig, "online_inference")
    fig, ax = plt.subplots(figsize=(6.5, 4))
    names = ["A2", "B1", "B2"]
    inference = [economics["online"][a]["inference"]["cost"] for a in names]
    learning = [economics["online"][a]["learning"]["cost"] for a in names]
    ax.bar(names, inference, label="Inference", color="#0072B2")
    ax.bar(
        names,
        learning,
        bottom=inference,
        label="Online updates",
        color="#E69F00",
    )
    ax.set(
        ylabel="Operational cost of 80 online attempts (USD)",
        title="Online learning is part of the operating bill",
    )
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    export(fig, "online_operating_cost")


def budget() -> None:
    data = read(REPORT / "budget_replay_results.json")
    if data["scenarios"] != 4560:
        raise ValueError("Budget replay is not complete")
    fig, axs = plt.subplots(2, 2, figsize=(11, 8))
    for column, stage in enumerate(("train", "validation")):
        for row, arms in enumerate(
            (
                ("A0", "A1", "A2", "S1", "P1", "O1", "R1"),
                ("B0", "B1", "B2"),
            )
        ):
            ax = axs[row, column]
            for arm in arms:
                points = [
                    data["metrics"][f"{stage}/{arm}/{cap:g}"]
                    for cap in (0.05, 0.075, 0.09, 0.10)
                    if f"{stage}/{arm}/{cap:g}" in data["metrics"]
                ]
                if not points:
                    continue
                ax.plot(
                    [p["cost"] / 2 for p in points],
                    [p["solves"] / 2 for p in points],
                    marker="o",
                    markersize=4,
                    lw=2 if arm in ("A0", "B0") else 1,
                    ls="--" if arm == "R1" else "-",
                    label=arm,
                    color=COLORS[arm],
                )
                ax.scatter(
                    points[-1]["cost"] / 2,
                    points[-1]["solves"] / 2,
                    facecolors="none",
                    edgecolors=COLORS[arm],
                    s=65,
                )
                for point in points:
                    lo, hi = cost_interval(point)
                    if lo != hi:
                        ax.errorbar(
                            hi / 2,
                            point["solves"] / 2,
                            xerr=[[(hi - lo) / 2], [0]],
                            fmt="none",
                            ecolor=COLORS[arm],
                            capsize=3,
                        )
            ax.set(
                title=stage + "X · " + ("assisted" if row == 0 else "plain"),
                xlabel="All-attempt inference cost per 40 (USD)",
                ylabel="Solved per 40 (mean of two replicates)",
            )
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(alpha=0.16)
            ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.suptitle(
        "Budget frontier · $0.05 / $0.075 / $0.09 / $0.10 stopping allowances\n"
        "Observed trajectories, exact controller replay; ring marks $0.10"
    )
    bounded = any("cost_interval" in m for m in data["metrics"].values())
    if bounded:
        fig.text(
            0.5,
            0.01,
            "B1 trainX bars span retained invoice bounds, not sampling uncertainty; points use upper liability.",
            ha="center",
            fontsize=8,
        )
    fig.tight_layout(rect=(0, 0.035 if bounded else 0, 1, 1))
    export(fig, "budget_frontier")


def goal_flood() -> None:
    data = read(REPORT / "goal_flood_timing.json")
    rows = data["requests"]
    fig, axs = plt.subplots(2, 1, figsize=(8, 6.2), sharex=True)
    axs[0].plot(
        [r["request"] for r in rows],
        [r["input_tokens"] / 1000 for r in rows],
        marker="o",
        markersize=3,
        color=COLORS["A2"],
    )
    axs[0].annotate(
        "192-goal feedback enters next request",
        xy=(15, rows[14]["input_tokens"] / 1000),
        xytext=(2, 175),
        arrowprops=dict(arrowstyle="->", color="#555555"),
        fontsize=9,
    )
    axs[0].set_ylabel("Input tokens (thousands)")
    observed = rows[:-1]
    axs[1].bar(
        [r["request"] for r in observed],
        [r["after_response_to_next_dispatch_seconds"] for r in observed],
        color=[
            COLORS["A2"] if r["request"] == 14 else "#999999" for r in observed
        ],
    )
    axs[1].set_yscale("log")
    axs[1].annotate(
        "973 seconds outside the API",
        xy=(14, rows[13]["after_response_to_next_dispatch_seconds"]),
        xytext=(2, 350),
        arrowprops=dict(arrowstyle="->", color="#555555"),
        fontsize=9,
    )
    axs[1].set(
        xlabel="Model request number",
        ylabel="Seconds until next request\n(log scale; API time excluded)",
        xticks=[1, 5, 10, 15, 20, 25, 29],
    )
    for ax in axs:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.16)
        ax.set_xlim(0.5, 29.5)
    fig.suptitle(
        "One goal flood increases both local work and prompt size\n"
        "P1 · amc12a_2020_p21 · validationX replicate0 · unsolved at $0.1025"
    )
    fig.tight_layout()
    export(fig, "goal_flood_trace")


def validation_completed() -> None:
    """Seven fully returned panels, kept separate from the final study plot."""
    data = read(REPORT / "validation_diagnosis.json")
    repetitions = read(REPORT / "output_repetition_diagnosis.json")
    arms = ["A0", "A1", "A2", "P1", "B0", "B1", "B2"]
    if any(data["metrics"][arm]["n"] != 80 for arm in arms):
        raise ValueError("A displayed validation panel is incomplete")
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.8))
    offsets = {
        "A0": (-35, 8),
        "A1": (6, 3),
        "A2": (7, 7),
        "P1": (-30, 6),
        "B0": (-30, -15),
        "B1": (6, 4),
        "B2": (-30, 7),
    }
    for arm in arms:
        m = data["metrics"][arm]
        x, y = m["cost"] / 2, m["solves"] / 2
        axs[0].scatter(
            x,
            y,
            color=COLORS[arm],
            s=60,
            marker="s" if arm.startswith("B") else "o",
        )
        axs[0].annotate(
            arm,
            (x, y),
            xytext=offsets[arm],
            textcoords="offset points",
            color=COLORS[arm],
            fontsize=10,
        )
    axs[0].set(
        xlabel="All-attempt inference cost per 40 (USD)",
        ylabel="Solved per 40 (mean of two replicates)",
        title="Cost and coverage · seven complete panels",
        ylim=(23.8, 29.2),
    )
    axs[0].grid(alpha=0.16)
    costs = [data["metrics"][a]["cost"] for a in arms]
    capped = [repetitions["arms"][a]["capped_charge"] for a in arms]
    other = [cost - cap for cost, cap in zip(costs, capped, strict=True)]
    axs[1].bar(arms, other, color="#8fa8bb", label="Other replies")
    axs[1].bar(
        arms,
        capped,
        bottom=other,
        color="#D55E00",
        label="Replies hitting output limit",
    )
    for i, arm in enumerate(arms):
        n = repetitions["arms"][arm]["capped_calls"]
        axs[1].text(
            i, costs[i] + 0.035, f"{n} capped", ha="center", fontsize=8
        )
    axs[1].set(
        ylabel="Total inference cost over 80 attempts (USD)",
        title="Capped replies explain much of B1's excess",
        ylim=(0, 2.9),
    )
    axs[1].legend(frameon=False, fontsize=8, loc="upper left")
    for ax in axs:
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(
        "validationX · Luna fixed · seven-arm diagnostic subset · preparation excluded"
    )
    fig.tight_layout()
    export(fig, "completed_validation_diagnosis")


def run(final: bool) -> None:
    plt.rcParams.update({"font.size": 10, "svg.fonttype": "none"})
    historical()
    authors()
    if final:
        fresh()
        online()
        budget()
        goal_flood()
        validation_completed()
    (DEST / "README.md").write_text(
        "# Figure provenance\n\nEach figure is supplied as PNG, SVG, and standalone PDF. Reproduce with `python -m experiments.ace_independent_audit.figures final` from `examples/omphalos`. The plotting code reads only this investigation's audited data files. Historical tariffs are normalized to 2026-09-19; fresh costs are reconciled receipts. Error bars cluster the two replicates by theorem; the accompanying JSON also reports broader proof-method-family sensitivity.\n"
    )


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["validation-completed"]:
        validation_completed()
    else:
        run(final=sys.argv[1:] == ["final"])
