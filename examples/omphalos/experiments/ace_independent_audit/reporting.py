"""Final-only report inputs, keeping paid supplements explicitly identified."""

from typing import Any

from .common import REPORT, read

ARM_NAMES = {
    "A0": "Ordinary assisted",
    "A1": "Historical X5",
    "A2": "Full Sol book",
    "S1": "Full Luna book",
    "P1": "Short Sol pilot book",
    "O1": "Adaptive then frozen",
    "R1": "Three verified rule repairs",
    "B0": "Ordinary plain",
    "B1": "Plain-source Sol book",
    "B2": "Teacher-evidence Sol book",
    "online_A2": "Online assisted",
    "online_B1": "Online plain",
    "online_B2": "Online teacher",
}
ORDER = tuple(ARM_NAMES)


def inputs(*, reviewed: bool = True) -> dict[str, Any]:
    certificate = read(REPORT / "study_certification.json")
    if not certificate["passed"] or certificate["solver_cells"] != 2044:
        raise ValueError("The complete study is not certified")
    data = read(REPORT / "fresh_results.json")
    rows = read(REPORT / "fresh_cells.json")
    if data["cells"] != 1520 or len(rows) != 1520:
        raise ValueError("The registered main study is incomplete")
    rules = read(REPORT / "rule_repair_results.json")
    adaptive = read(REPORT / "adaptive_frozen_results.json")
    data["metrics"]["train/R1"] = rules["metrics"]
    for baseline, comparison in rules["comparisons"].items():
        key = "train/R1" + ("" if baseline == "A0" else "_vs_" + baseline)
        data["comparisons"][key] = dict(comparison, baseline=baseline)
    for stage, value in adaptive["metrics"].items():
        data["metrics"][stage + "/O1"] = value
    for key, comparison in adaptive["comparisons"].items():
        stage, baseline = key.split("/")
        name = stage + "/O1"
        if baseline != "A0":
            name += "_vs_" + baseline
        data["comparisons"][name] = dict(comparison, baseline=baseline)
    rows += read(REPORT / "rule_repair_cells.json")
    rows += read(REPORT / "adaptive_frozen_cells.json")
    if len(rows) != 1760 or len({r["cell"] for r in rows}) != 1760:
        raise ValueError("Main and supplemental serving cells differ")
    data["rows"] = rows
    data["serving_cells"] = len(rows)
    review_path = REPORT / "statistical_review.json"
    if reviewed and review_path.exists():
        review = read(review_path)["comparisons"]
        for key, comparison in data["comparisons"].items():
            for level in ("theorem", "family"):
                comparison[level] = review[f"serving/{key}/{level}"]
    return data


def group_order(key: str) -> tuple[int, int]:
    stage, arm = key.split("/")
    return (0 if stage == "train" else 1, ORDER.index(arm))
