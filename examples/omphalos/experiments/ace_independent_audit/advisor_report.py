"""Export advisor figures from sealed full-panel results, without API calls.

Both harnesses: python -m experiments.ace_independent_audit.advisor_report
The narrative is maintained in report/ace_independent_audit/advisor/report.md.
Only completed eighty-attempt comparisons enter these figures; no pilot
artifact is opened. Existing study artifacts are read-only.
"""

from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as _pyplot

from .common import REPORT, ROOT, read, sha

plt: Any = _pyplot
DEST = REPORT / "advisor"


def inputs() -> dict[str, Any]:
    manifest = read(REPORT / "artifact_manifest.json")
    sealed = {row["path"]: row for row in manifest["review_files"]}
    names = (
        "budget_frontier.json",
        "statistical_review.json",
        "historical_matched_comparisons.json",
        "fresh_mechanisms.json",
        "final_economics.json",
        "study_certification.json",
    )
    sources: dict[str, str] = {}
    for name in names:
        path = REPORT / name
        actual = sha(path)
        if actual != sealed[str(path.relative_to(ROOT))]["sha256"]:
            raise ValueError(f"Sealed source changed: {name}")
        sources[name] = actual
    study = read(REPORT / "study_certification.json")
    if not study["passed"] or study["solver_cells"] != 2044:
        raise ValueError("Full-study completion certificate is required")
    frontier = read(REPORT / "budget_frontier.json")["rows"]
    points = {
        (row["stage"], row["arm"], row["stopping_allowance"]): row
        for row in frontier
    }
    reviewed = read(REPORT / "statistical_review.json")["comparisons"]
    historical = next(
        row
        for row in read(REPORT / "historical_matched_comparisons.json")
        if row["comparison"] == "economy/session_matched"
    )
    if not historical["same_contract_except_book"]:
        raise ValueError("Historical comparison must have matched contracts")
    same: list[dict[str, Any]] = []
    for label, key in (
        ("O1 / trainX", "serving/train/O1/theorem"),
        ("R1 / trainX", "budget/train/R1/0.09/theorem"),
        (
            "ACE + reset / validationX (historical)",
            "historical_matched/economy/session_matched/theorem",
        ),
    ):
        stats = reviewed[key]
        if not stats["complete"] or stats["n"] != 80:
            raise ValueError(f"Incomplete panel: {key}")
        same.append(dict(label=label, source_key=key, **stats))
    joint: list[dict[str, Any]] = []
    for stage, arm, baseline in (
        ("train", "O1", "A0"),
        ("validation", "O1", "A0"),
        ("train", "S1", "A0"),
    ):
        original = points[stage, baseline, 0.1]
        reduced = points[stage, baseline, 0.05]
        treatment = points[stage, arm, 0.05]
        for point in (original, reduced, treatment):
            if point["n"] != 80 or not point["invoice_exact"]:
                raise ValueError("Expected a complete, exactly billed panel")
        before = float(original["all_attempt_cost"])
        budget = float(reduced["all_attempt_cost"])
        after = float(treatment["all_attempt_cost"])
        budget_share = (before - budget) / before
        ace_share = (budget - after) / before
        total = (before - after) / before
        if abs(budget_share + ace_share - total) > 1e-12:
            raise ValueError("Cost decomposition does not reconcile")
        if total < 0.1:
            raise ValueError("Selected joint result misses the 10% target")
        joint.append(
            dict(
                stage=stage,
                arm=arm,
                baseline=baseline,
                original=original,
                reduced_baseline=reduced,
                treatment=treatment,
                budget_share_of_original=budget_share,
                additional_share_of_original=ace_share,
                joint_saving=total,
                ace_saving_vs_reduced_baseline=(budget - after) / budget,
            )
        )
    return dict(
        input_hashes=sources,
        source_manifest_sha256=sha(REPORT / "artifact_manifest.json"),
        same_budget=same,
        joint_budget=joint,
        historical_session_vs_ordinary=reviewed[
            "historical_matched/economy/session_vs_ordinary/theorem"
        ],
        paid_calls=0,
        scope="Completed full trainX/validationX panels from the independent campaign, plus one explicitly matched and independently audited historical reset comparison; no pilots",
        interpretation="Serving fees include failed attempts and exclude preparation. Budget results replay recorded responses and cache invoices, without new model samples. Components share the original baseline denominator; matched-budget ACE percentages use the reduced baseline instead.",
    )


def export(figure: Any, name: str) -> None:
    for extension in ("pdf", "svg", "png"):
        figure.savefig(
            DEST / f"{name}.{extension}", dpi=220, bbox_inches="tight"
        )
    plt.close(figure)


def same_budget(data: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(9.0, 2.7))
    for index, row in enumerate(data["same_budget"]):
        value = 100 * row["saving"]
        lo, hi = [100 * bound for bound in row["saving_ci90"]]
        color = "#176B87" if index < 2 else "#667085"
        ax.errorbar(
            value,
            index,
            xerr=[[value - lo], [hi - value]],
            fmt="o",
            color=color,
            capsize=5,
            markersize=7,
            linewidth=2,
        )
        ax.text(
            hi + 0.7,
            index,
            f"{value:.2f}%",
            va="center",
            fontsize=10,
            weight="bold",
            color=color,
        )
    ax.axvline(0, color="#D0D5DD", linewidth=1)
    ax.axvline(10, color="#B54708", ls="--", linewidth=1.3)
    ax.text(10.5, -0.62, "10% target", color="#B54708", fontsize=9)
    labels = [
        f"{row['label']}\n({row['baseline_solves']} → "
        f"{row['arm_solves']} solves)"
        for row in data["same_budget"]
    ]
    ax.set(
        yticks=range(3),
        yticklabels=labels,
        xlabel="Serving-cost reduction (%) · dots: estimates; bars: 90% intervals",
        xlim=(-15, 36),
        ylim=(2.55, -0.9),
    )
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", alpha=0.12)
    export(fig, "same_budget")


def budget_decomposition(data: dict[str, Any]) -> None:
    fig, ax = plt.subplots(figsize=(9.0, 2.7))
    labels: list[str] = []
    for index, row in enumerate(data["joint_budget"]):
        budget = 100 * row["budget_share_of_original"]
        extra = 100 * row["additional_share_of_original"]
        total = 100 * row["joint_saving"]
        ax.barh(
            index,
            budget,
            height=0.57,
            color="#98A2B3",
            label="Ordinary budget reduction" if index == 0 else None,
        )
        ax.barh(
            index,
            extra,
            left=budget,
            height=0.57,
            color="#176B87",
            label="Additional difference with ACE" if index == 0 else None,
        )
        ax.text(
            budget / 2,
            index,
            f"{budget:.2f}",
            va="center",
            ha="center",
            color="#101828",
            fontsize=9,
        )
        if extra > 1.5:
            ax.text(
                budget + extra / 2,
                index,
                f"{extra:.2f}",
                va="center",
                ha="center",
                color="white",
                fontsize=9,
            )
        ax.text(
            total + 0.5,
            index,
            f"{total:.2f}%",
            va="center",
            weight="bold",
            fontsize=10,
        )
        labels.append(
            f"{row['arm']} / {row['stage']}X  "
            f"({row['original']['solves']} → "
            f"{row['treatment']['solves']} solves)"
        )
    ax.axvline(10, color="#B54708", ls="--", linewidth=1.1)
    ax.set(
        yticks=range(len(data["joint_budget"])),
        yticklabels=labels,
        xlabel="Cost saved as a percentage of the original $0.10 baseline bill",
        xlim=(0, 29),
    )
    ax.invert_yaxis()
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.02),
        ncol=2,
        frameon=False,
        fontsize=9,
    )
    export(fig, "budget_decomposition")


def run() -> None:
    import json

    DEST.mkdir(parents=True, exist_ok=True)
    data = inputs()
    (DEST / "figure_data.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n"
    )
    same_budget(data)
    budget_decomposition(data)
    print(
        "Two advisor figures exported; source hashes and full panels checked."
    )


if __name__ == "__main__":
    run()
